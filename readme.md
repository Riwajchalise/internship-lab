# 🔐 Google Workspace Audit Scripts

This repo contains Python scripts to help administrators audit their Google Workspace domain using Google's Admin SDK and Directory API. It includes utilities to extract information about organizational units, groups, admin roles, 2FA enrollment, and more.

---

## 📦 Prerequisites

Before running any script, make sure you have:

- A **service account** with:
  - Domain-wide delegation enabled
  - The necessary scopes authorized
- Installed required packages:
  ```bash
  pip install google-api-python-client google-auth pandas openpyxl dnspython
