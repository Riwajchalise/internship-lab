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
    """Get mapping of roleId → roleName"""
    roles = admin_service.roles().list(customer="my_customer").execute()
    return {r["roleId"]: r["roleName"] for r in roles.get("items", [])}

def get_admins():
    """List admin users and their roles"""
    role_assignments = admin_service.roleAssignments().list(customer="my_customer").execute()
    role_map = get_role_map()
    admins = []

    for assignment in role_assignments.get("items", []):
        if assignment.get("scopeType") == "CUSTOMER":
            role_id = assignment.get("roleId")
            user_id = assignment.get("assignedTo")

            try:
                user = admin_service.users().get(userKey=user_id).execute()
                admins.append({
                    "Email": user["primaryEmail"],
                    "Full Name": f"{user.get('name', {}).get('givenName', '')} {user.get('name', {}).get('familyName', '')}".strip(),
                    "2FA Enrolled": user.get("isEnrolledIn2Sv", False),
                    "2FA Enforced": user.get("isEnforcedIn2Sv", False),
                    "Role": role_map.get(role_id, f"Role ID {role_id}")
                })
            except Exception as e:
                print(f"⚠️ Failed to fetch user {user_id}: {e}")
    return pd.DataFrame(admins)

def filter_admins_without_2fa(df):
    """Filter users with no 2FA enrollment"""
    return df[df["2FA Enrolled"] == False]

def export_to_excel(df, filename="admins_without_2fa.xlsx"):
    if df.empty:
        print("✅ All admin users have 2FA enabled.")
    else:
        df.to_excel(filename, index=False)
        print(f"⚠️ Exported {len(df)} admin users without 2FA to {filename}")

# Main
if __name__ == "__main__":
    df_admins = get_admins()
    df_no_2fa = filter_admins_without_2fa(df_admins)
    export_to_excel(df_no_2fa)
