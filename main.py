import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

# === 🔧 CONFIGURATION ===
SERVICE_ACCOUNT_FILE = "service.json"
DELEGATED_ADMIN = "riwaj@sentry.cy"
SCOPES = ["https://www.googleapis.com/auth/admin.directory.user.readonly"]

# === 🔐 AUTHENTICATION ===
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)
delegated_credentials = credentials.with_subject(DELEGATED_ADMIN)

# === 🌐 BUILD API SERVICE ===
service = build("admin", "directory_v1", credentials=delegated_credentials)

# === 🔁 PAGINATE AND FETCH USERS ===
def list_all_users():
    users = []
    page_token = None

    while True:
        results = service.users().list(
            customer="my_customer",
            maxResults=100,
            orderBy="email",
            pageToken=page_token
        ).execute()

        users.extend(results.get("users", []))
        page_token = results.get("nextPageToken")

        if not page_token:
            break

    return users

# === 📤 EXPORT TO EXCEL ===
if __name__ == "__main__":
    try:
        all_users = list_all_users()
        user_data = []

        for user in all_users:
            user_data.append({
                "Email": user.get("primaryEmail", ""),
                "Full Name": user.get("name", {}).get("fullName", ""),
                "First Name": user.get("name", {}).get("givenName", ""),
                "Last Name": user.get("name", {}).get("familyName", ""),
                "Is Admin": user.get("isAdmin", False),
                "Creation Time": user.get("creationTime", "")
            })

        # Convert to DataFrame and export
        df = pd.DataFrame(user_data)
        df.to_excel("users.xlsx", index=False)

        print("✅ Users exported to users.xlsx successfully!")

    except Exception as e:
        print("❌ Error:", e)
