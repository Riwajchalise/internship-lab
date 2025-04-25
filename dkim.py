<<<<<<< HEAD
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configuration
SERVICE_ACCOUNT_FILE = 'service.json'  # Path to your service account JSON file
DELEGATED_ADMIN = 'riwaj@sentry.cy'   # The email of the super admin
SCOPES = ['https://www.googleapis.com/auth/admin.directory.domain.readonly']

# Authenticate and create the service
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
delegated_creds = credentials.with_subject(DELEGATED_ADMIN)
service = build('admin', 'directory_v1', credentials=delegated_creds)

def get_dkim_settings():
    """Fetch the DKIM settings for the domain."""
    try:
        # Retrieve the domain settings
        domains = service.domains().list(customer='my_customer').execute()

        # Check for DKIM status in the domain settings
        for domain in domains['domains']:
            print(f"Domain: {domain['domainName']}")
            print(f"DKIM Status: {domain.get('dkimEnabled', 'Not Configured')}")
            print('-' * 40)

    except Exception as e:
        print(f"An error occurred: {e}")

# Run the function to get DKIM settings
get_dkim_settings()
=======
import dns.resolver

def get_dkim_record(domain, selector="google"):
    try:
        dkim_domain = f"{selector}._domainkey.{domain}"
        print(f"🔍 Looking up DKIM for: {dkim_domain}")
        
        answers = dns.resolver.resolve(dkim_domain, 'TXT')
        for rdata in answers:
            # Join fragments and decode
            txt_record = ''.join([part.decode() if isinstance(part, bytes) else part for part in rdata.strings])
            print("\n✅ DKIM TXT Record:")
            print(txt_record)
            return txt_record
    except Exception as e:
        print(f"❌ Failed to fetch DKIM for {domain}: {e}")
        return None

# Replace with your domain
domain = "sentry.cy"
get_dkim_record(domain)
>>>>>>> 3faed1f5eb29b5b2180cb5659997a7295b6a27ec
