# Delete Suppressions from Prisma Cloud

## Setup Instructions

### Prerequisites

- Python 3.x
- AWS SES credentials for sending emails
- Prisma Cloud API credentials

### Installation

1. **Create Python Virtual Environment**:

```bash
python3 -m virtualenv venv && source venv/bin/activate  
```

2. **Install required packages**:

Install the dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

3. **Environment Variables**:

Create a `.env` file in the root directory of your project. You can copy the `.env.example` file and update it with your own credentials:

```bash
cp .env.example .env
```

Update the `.env` file with your Prisma Cloud API credentials and AWS SES credentials:

```ini
# Prisma Cloud API Credentials
PRISMA_API_URL=<your_prisma_cloud_api_url>
PRISMA_ACCESS_KEY=<your_prisma_access_key>
PRISMA_SECRET_KEY=<your_prisma_secret_key>
```

### Usage

Run the script as follows, if limit == 0, then delete all suppressions from Prisma Cloud tenant:

```bash
python main.py --limit 5
```