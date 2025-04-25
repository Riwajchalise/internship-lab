from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

# Configuration
SERVICE_ACCOUNT_FILE = 'service.json'  # Path to your service account JSON file
DELEGATED_ADMIN = 'riwaj@sentry.cy'   # The email of the super admin
CUSTOMER_ID = '01516j2u'              # Your Google Workspace customer ID without the leading 'C'
SCOPES = ['https://www.googleapis.com/auth/apps.alerts']

# Authenticate and create the service
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
delegated_creds = credentials.with_subject(DELEGATED_ADMIN)
service = build('alertcenter', 'v1beta1', credentials=delegated_creds)

def list_alerts():
    """List all alerts in the Google Workspace domain."""
    alerts = []
    page_token = None
    while True:
        # Call the Alert Center API
        response = service.alerts().list(
            customerId=CUSTOMER_ID,
            pageToken=page_token
        ).execute()

        # Append alerts to the list
        alerts.extend(response.get('alerts', []))

        # Check if there are more pages
        page_token = response.get('nextPageToken')
        if not page_token:
            break

    return alerts

def export_to_excel(alerts):
    """Export the alert data to an Excel file."""
    # Prepare the data for Excel
    sheet_data = [['Alert ID', 'Type', 'Source', 'Create Time', 'Start Time', 'End Time']]
    
    for alert in alerts:
        sheet_data.append([
            alert['alertId'],
            alert['type'],
            alert['source'],
            alert['createTime'],
            alert['startTime'],
            alert.get('endTime', 'N/A')
        ])
    
    # Create a DataFrame from the data
    df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])

    # Export to Excel
    df.to_excel('alerts_data.xlsx', index=False, engine='openpyxl')
    print("Data exported to alerts_data.xlsx successfully!")

# Fetch and display alerts
alerts = list_alerts()

# Export the data to Excel locally
export_to_excel(alerts)
