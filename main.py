__author__ = "Simon Melotte"

import os
import json
import csv
import requests
import argparse
import logging
from dotenv import load_dotenv

# Create a logger object
logger = logging.getLogger()

def delete_suppression(base_url, token, policy_id, suppression_id):
    url = f"https://{base_url}/code/api/v1/suppressions/{policy_id}/justifications/{suppression_id}"
    headers = {"content-type": "application/json; charset=UTF-8", "x-redlock-auth": token}
   
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
    except requests.exceptions.RequestException as err:
        logger.error(f"Exception in get_policies: {err}")
        return None

    logger.debug(f"Response status code: {response.status_code}")
    logger.debug(f"Response headers: {response.headers}")    
    logger.info(f"Suppressions: {suppression_id} has been deleted for the policy {policy_id}")


def get_suppressions(base_url, token):
    url = f"https://{base_url}/code/api/v1/suppressions"
    headers = {"content-type": "application/json; charset=UTF-8", "x-redlock-auth": token}
   
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
    except requests.exceptions.RequestException as err:
        logger.error(f"Exception in get_policies: {err}")
        return None

    response_json = response.json()

    logger.debug(f"Response status code: {response.status_code}")
    logger.debug(f"Response headers: {response.headers}")    
    return response_json


def get_compute_url(base_url, token):
    url = f"https://{base_url}/meta_info"
    headers = {"content-type": "application/json; charset=UTF-8", "Authorization": "Bearer " + token}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
    except requests.exceptions.RequestException as err:
        logger.error("Oops! An exception occurred in get_compute_url, ", err)
        return None

    response_json = response.json()
    return response_json.get("twistlockUrl", None)


def login_saas(base_url, access_key, secret_key):
    url = f"https://{base_url}/login"
    payload = json.dumps({"username": access_key, "password": secret_key})
    headers = {"content-type": "application/json; charset=UTF-8"}
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
    except Exception as e:
        logger.info(f"Error in login_saas: {e}")
        return None

    return response.json().get("token")


def login_compute(base_url, access_key, secret_key):
    url = f"{base_url}/api/v1/authenticate"

    payload = json.dumps({"username": access_key, "password": secret_key})
    headers = {"content-type": "application/json; charset=UTF-8"}
    response = requests.post(url, headers=headers, data=payload)
    return response.json()["token"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")
    parser.add_argument("-l", "--limit", help="Number of maximum suppression to be deleted", default=0)
    args = parser.parse_args()

    input_csv_file = 'processed_policies_output.csv'    
    if args.debug:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO
    limit = args.limit
    logging.basicConfig(
        level=logging_level, format="%(asctime)s - %(levelname)s - %(message)s", filename="app.log", filemode="a"
    )

    # Create a console handler
    console_handler = logging.StreamHandler()

    # Add the console handler to the logger
    logger.addHandler(console_handler)

    logger.info("======================= START =======================")
    logger.debug("======================= DEBUG MODE =======================")

    load_dotenv()

    url = os.environ.get("PRISMA_API_URL")
    identity = os.environ.get("PRISMA_ACCESS_KEY")
    secret = os.environ.get("PRISMA_SECRET_KEY")

    if not url or not identity or not secret:
        logger.error("PRISMA_API_URL, PRISMA_ACCESS_KEY, PRISMA_SECRET_KEY variables are not set.")
        return

    token = login_saas(url, identity, secret)
    # compute_url = get_compute_url(url, token)
    # compute_token = login_compute(compute_url, identity, secret)
    # logger.debug(f"Compute url: {compute_url}")

    if token is None:
        logger.error("Unable to authenticate.")
        return 

    try:
        limit = int(limit)  # Convert limit to an integer
    except ValueError:
        raise ValueError("Limit must be a valid integer.")

    # Get the list of suppressions before deletion
    suppressions = get_suppressions(url, token)

    # Count of suppressions before deletion
    count_before = len(suppressions)
    print(f"Number of suppressions before deletion: {count_before}")

    # Determine the suppressions to delete based on the limit
    if limit == 0:
        suppressions_to_delete = suppressions
    else:
        suppressions_to_delete = suppressions[:limit]

    # Loop through the selected suppressions and delete them
    for suppression in suppressions_to_delete:
        policy_id = suppression['policyId']
        suppression_id = suppression['id']
        delete_suppression(url, token, policy_id, suppression_id)

    # Get the list of suppressions after deletion
    suppressions_after = get_suppressions(url, token)

    # Count of suppressions after deletion
    count_after = len(suppressions_after)
    print(f"Number of suppressions after deletion: {count_after}")
    

    logger.info("======================= END =======================")


if __name__ == "__main__":
    main()
