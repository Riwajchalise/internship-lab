from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

# Config
SERVICE_ACCOUNT_FILE = "service.json"
DELEGATED_ADMIN = "riwaj@sentry.cy"
SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.user.readonly",
    "https://www.googleapis.com/auth/admin.directory.rolemanagement.readonly"
]

# Auth
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
delegated_creds = credentials.with_subject(DELEGATED_ADMIN)

# Services
admin_service = build("admin", "directory_v1", credentials=delegated_creds)

def get_role_map():
    """Fetch all available admin roles and build a roleId → name map"""
    try:
        roles = admin_service.roles().list(customer="my_customer").execute()
        return {r["roleId"]: r["roleName"] for r in roles.get("items", [])}
    except Exception as e:
        print("❌ Error fetching roles:", e)
        return {}

def get_delegated_admins():
    """List users with delegated admin roles"""
    try:
        role_assignments = admin_service.roleAssignments().list(customer="my_customer").execute()
        role_map = get_role_map()
        results = []

        for assignment in role_assignments.get("items", []):
            if assignment.get("scopeType") == "CUSTOMER":
                role_id = assignment.get("roleId")
                user_id = assignment.get("assignedTo")

                try:
                    user = admin_service.users().get(userKey=user_id).execute()
                    results.append({
                        "Email": user["primaryEmail"],
                        "Full Name": f"{user.get('name', {}).get('givenName', '')} {user.get('name', {}).get('familyName', '')}".strip(),
                        "Role": role_map.get(role_id, f"Role ID {role_id}")
                    })
                except Exception as ue:
                    print(f"⚠️ Could not get user info for {user_id}: {ue}")
        
        return pd.DataFrame(results)

    except Exception as e:
        print("❌ Error fetching delegated admins:", e)
        return pd.DataFrame()

def export_to_excel(df, filename="delegated_admins.xlsx"):
    """Export DataFrame to Excel"""
    if df.empty:
        print("⚠️ No delegated admins to export.")
    else:
        df.to_excel(filename, index=False)
        print(f"✅ Exported {len(df)} delegated admins to {filename}")

# Run it
if __name__ == "__main__":
    df = get_delegated_admins()
    export_to_excel(df)
