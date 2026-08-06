# Google Sheets Integration Setup Guide
This guide walks you through connecting Invoice Buddy to your Google Sheets account using OAuth 2.0.

***NOTICE: This is for an integration which has yet to be completed. Work is still being done to fully integrate Google Sheets into Invoice Buddy.***

## Prerequisites
- A personal Gmail account (school/work accounts may have Google Cloud disabled)
- Internet access during initial setup
- Approximately 10–15 minutes


### Step 1: Create a Google Cloud Project
1. Go to Google Cloud Console
2. Sign in with your personal Gmail account
3. Click the project dropdown at the top → New Project
4. Name it (e.g., InvoiceBuddy)
5. Click Create

### Step 2: Enable Required APIs
Google requires you to enable each API your app will use. You need two APIs enabled:

1. Enable Google Sheets API
2. Navigate to APIs & Services → Library
3. Search for Google Sheets API
4. Click on it → Click Enable
Or visit directly: Enable Google Sheets API
5. Enable Google Drive API
6. In the same Library page, search for Google Drive API
7. Click on it → Click Enable
8. Or visit directly: Enable Google Drive API


### Step 3: Configure OAuth Consent Screen
1. Go to APIs & Services → OAuth consent screen
2. Select External → Click Create
3. Fill in required fields:
4. App name: InvoiceBuddy
5. User support email: Your email
6. Developer contact information: Your email
7. Click Save and Continue through each page
8. On the Scopes page, click Add or Remove Scopes
9. Search for and add these two scopes:
https://www.googleapis.com/auth/spreadsheets — See, edit, create, and delete your spreadsheets
https://www.googleapis.com/auth/drive — See, edit, create, and delete all your Google Drive files
10. Click Save and Continue through the remaining pages

### Step 4: Create OAuth Client Credentials
1. Go to APIs & Services → Credentials
2. Click + Create Credentials → OAuth client ID
3. Application type: Desktop app
4. Name: InvoiceBuddy Desktop
5. Click Create
6. Click Download JSON — this downloads your client_secrets.json file
7. Save this file somewhere safe — you'll need it for the first-time auth flow


### Step 5: First-Time Authentication
1. Launch Invoice Buddy
2. Go to Settings → Google Sheets Integration
3. When prompted, enter the path to your downloaded `client_secrets.json` file
4. Your default browser will open a Google sign-in page
5. Sign in with the same Gmail account you used for Google Cloud
6. Click **Continue** on the warning prompt (your app is unverified — this is normal for self-hosted apps)
7. Grant permission for Sheets and Drive access
8. You should see a success message in Invoice Buddy

---

## Step 6: Verify the Connection

After completing authentication, your token is saved automatically at:

~/.config/invoicebuddy/google_token.json


This token is refreshed automatically and does not require re-authentication.

---

## Troubleshooting

### "Google Sheets API has not been used in project..."

**Cause:** Google Sheets API is not enabled in your project.

**Fix:** Visit the URL provided in the error message and click **Enable**.

---

### "Google Drive API has not been used in project..."

**Cause:** Google Drive API is not enabled in your project.

**Fix:** Visit the URL provided in client_credentials, search for Google Drive API, and click **Enable**.

---

### "Error 401: invalid_client"

**Cause:** Your `client_secrets.json` file is missing, corrupt, or contains placeholder values.

**Fix:** Re-download the JSON file from Google Cloud Console → Credentials.

---

### "You do not have access to Google Cloud Platform"

**Cause:** You are using a school or work account that has Google Cloud disabled by the organization administrator.

**Fix:** Switch to a **personal Gmail account** and try again.

---

### "Insufficient authentication scopes"

**Cause:** Your token was created without both required scopes (Sheets + Drive).

**Fix:** Delete your saved token and re-authenticate:

bash rm ~/.config/invoicebuddy/google_token.json python src/connections/alphabet.py


---

### Token Revocation / Resetting Authentication

If you need to reset your Google authentication (switching accounts, revoking access, etc.):

1. Delete your local token file:
   ```bash
   rm ~/.config/invoicebuddy/google_token.json
(Optional) Revoke access from your Google account:
2. Go to Google Account Permissions
3. Find InvoiceBuddy → Click Remove Access
4. Re-run the authentication flow

### Data & Privacy
Invoice Buddy stores your OAuth token locally at ~/.config/invoicebuddy/google_token.json
Your client_secrets.json file is only needed during initial setup
Invoice Buddy never sees or stores your Google password
Authentication is handled entirely through Google's OAuth 2.0 protocol
You can revoke access at any time from your Google Account

### Need Help?
If you encounter issues not covered in this troubleshooting guide, please file an issue on GitHub or consult the Google OAuth 2.0 documentation.
