from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

# Configuration
SERVICE_ACCOUNT_FILE = "service.json"
DELEGATED_ADMIN = "riwaj@sentry.cy"
SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.orgunit.readonly",
    "https://www.googleapis.com/auth/admin.directory.group.readonly"
]

# Authenticate
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
delegated_creds = credentials.with_subject(DELEGATED_ADMIN)
service = build("admin", "directory_v1", credentials=delegated_creds)


# --- List Organizational Units ---
def get_organizational_units():
    print("📂 Fetching Organizational Units...")

    try:
        response = service.orgunits().list(
            customerId="my_customer",
            type="all"
        ).execute()

        ou_list = response.get("organizationUnits", [])
        if not ou_list:
            print("⚠️ No organizational units found.")
            return pd.DataFrame([{
                "Name": "Top-Level OU",
                "Path": "/",
                "Description": "",
                "Parent Path": ""
            }])

        data = []
        for ou in ou_list:
            data.append({
                "Name": ou.get("name"),
                "Path": ou.get("orgUnitPath"),
                "Description": ou.get("description", ""),
                "Parent Path": ou.get("parentOrgUnitPath", "")
            })

        print(f"✅ Found {len(data)} OUs")
        return pd.DataFrame(data)

    except Exception as e:
        print("❌ Error fetching OUs:", str(e))
        return pd.DataFrame()


# --- List Groups ---
def get_groups():
    print("\n👥 Fetching Groups...")
    groups = []
    page_token = None

    try:
        while True:
            result = service.groups().list(
                customer="my_customer",
                maxResults=100,
                pageToken=page_token
            ).execute()

            groups.extend(result.get("groups", []))
            page_token = result.get("nextPageToken")
            if not page_token:
                break

        data = []
        for g in groups:
            data.append({
                "Name": g.get("name"),
                "Email": g.get("email"),
                "Description": g.get("description", ""),
                "Direct Members Count": g.get("directMembersCount", "N/A")
            })

        print(f"✅ Found {len(data)} Groups")
        return pd.DataFrame(data)

    except Exception as e:
        print("❌ Error fetching Groups:", str(e))
        return pd.DataFrame()


# --- Export to Excel ---
def export_to_excel():
    ous_df = get_organizational_units()
    groups_df = get_groups()

    with pd.ExcelWriter("workspace_data.xlsx", engine="openpyxl") as writer:
        ous_df.to_excel(writer, sheet_name="Organizational Units", index=False)
        groups_df.to_excel(writer, sheet_name="Groups", index=False)

    print("\n📁 Export complete: workspace_data.xlsx")


# --- Run ---
if __name__ == "__main__":
    export_to_excel()
