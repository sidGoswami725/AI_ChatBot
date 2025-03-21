import os
import json
from google.oauth2 import service_account
from google.cloud import storage, bigquery  # or other services you need
from dotenv import load_dotenv

load_dotenv()

# Create credentials dictionary from environment variables
credentials_dict = {
    "type": "service_account",
    "project_id": os.getenv("GCP_PROJECT_ID"),
    "private_key_id": os.getenv("GCP_PRIVATE_KEY_ID"),
    "private_key": os.getenv("GCP_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("GCP_CLIENT_EMAIL"),
    "client_id": os.getenv("GCP_CLIENT_ID"),
    "auth_uri": os.getenv("GCP_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
    "token_uri": os.getenv("GCP_TOKEN_URI", "https://oauth2.googleapis.com/token"),
    "auth_provider_x509_cert_url": os.getenv("GCP_AUTH_PROVIDER_X509_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs"),
    "client_x509_cert_url": os.getenv("GCP_CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("GCP_UNIVERSE_DOMAIN", "googleapis.com")
}

# Create credentials object from the dictionary
credentials = service_account.Credentials.from_service_account_info(credentials_dict)

# Create clients for different services using these credentials
# storage_client = storage.Client(credentials=credentials, project=credentials_dict["project_id"])
# bigquery_client = bigquery.Client(credentials=credentials, project=credentials_dict["project_id"])

# Now you can use storage_client and bigquery_client to interact with Google Cloud services