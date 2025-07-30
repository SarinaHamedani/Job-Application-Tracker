# 📬 Job Application Tracker

This project automatically fetches job-related emails from your Gmail account and analyzes them using the OpenAI API to track the status and responses of your job applications. It helps you stay organized by identifying follow-ups, interview invitations, and rejections.

---

## ✨ Features

- ✅ Authenticate with Gmail using OAuth 2.0  
- 🔍 Search and retrieve job-related emails within a specific time window  
- 🧠 Use OpenAI's GPT to summarize and classify email content  
- 🗂 Track and store application statuses for review  

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/job-application-tracker.git
cd job-application-tracker
```
### 2. Install dependencies
```
pip install -r requirements.txt
```
### 3. Set up Gmail API credentials
Visit the Google Cloud Console

Enable the Gmail API

Create OAuth 2.0 Client ID credentials (select "Desktop App" as application type)

Download the credentials.json file and place it in the root of this project directory

### 4. Run the script
python analyze_emails.py
You will be prompted to authenticate using your Google account in a browser window. After authentication, the application will retrieve your job-related emails and process them.

## 🧠 How It Works
Authentication: Uses the Google OAuth flow to access your Gmail inbox with read-only permissions.

Email Fetching: Builds a Gmail query to fetch emails matching a date range or subject keywords.

Parsing: Extracts the subject, date, and decoded body from the emails.

Analysis (optional): Passes the email content to OpenAI GPT to classify email status (e.g., "interview", "rejection", "offer").

## 🔧 Configuration
You can update the date range for fetching emails by modifying these variables in analyze_emails.py:

start_date = "2025-07-01"
end_date = "2025-08-01"

To use OpenAI for processing email content, make sure you have your API key set:

```
import openai
openai.api_key = "your-openai-api-key"
```
## 📂 Project Structure
```
job-application-tracker/
├── analyze_emails.py         # Main script to fetch and process emails
├── gmail_fetcher.py          # Gmail API authentication and utility functions
├── credentials.json          # OAuth2 credentials from Google (DO NOT SHARE)
├── requirements.txt          # Python package dependencies
└── README.md                 # Project documentation
```
## 📌 Requirements
Python 3.7 or higher

Gmail API credentials (OAuth 2.0)

Internet access during script execution

OpenAI API key (optional for LLM classification)

## 📄 License
This project is licensed under the MIT License.
See the LICENSE file for more details.

## 🙋‍♀️ Author
Sarina Hamedani