from gmail_fetcher import authenticate_gmail, search_emails

import pandas as pd
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
import time

from openai import OpenAI

client = OpenAI()  # Assumes your OPENAI_API_KEY is set in the environment
VALID_STATUSES = {"Applied", "Interview", "Offer", "Rejected"}

def get_llm_chain(email_text):
    prompt = f"""
    You are an assistant that extracts job application information from emails.
    Analyze the email below. If it is related to a job application, extract the following structured data ONLY:

    | Company | Job Title | Status | Date |

    - Status must be exactly one of: Applied, Interview, Offer, Rejected
    - If it's not job-related, respond only with: NOT JOB-RELATED

    Email:
    {email_text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": "You are an assistant that analyzes job-related emails."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


def to_unix(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(time.mktime(dt.timetuple()))

if __name__=="__main__":
    start_date = "2025-07-05"
    end_date = "2025-07-10"
    
    query = f"after:{to_unix(start_date)} before:{to_unix(end_date)}"
    
    service = authenticate_gmail()
    emails = search_emails(service=service, query=query)
    
    
    results = []
    for email in emails[:5]:
        analysis = get_llm_chain(email['body'])
        
        if analysis.startswith("NOT JOB-RELATED"):
            continue
        
        try:
            lines = analysis.splitlines()
            # print(len(lines) >= 2 and "|" in lines[1])
            print(lines)
            if len(lines) >= 2 and "|" in lines[2]:
                data_row = [cell.strip() for cell in lines[2].split("|")[1:-1]]
                print(data_row)
                if len(data_row) == 4 and data_row[2] in VALID_STATUSES:
                    results.append({
                        "Company": data_row[0],
                        "Job Title": data_row[1],
                        "Status": data_row[2],
                        "Date": data_row[3],
                        "Email Subject": email["subject"]
                    })
        except Exception as e:
            print(f"Error parsing result:\n{analysis}\nError: {e}")
            continue

    df = pd.DataFrame(results)
    df.to_csv("filtered_job_emails.csv", index=False)
    print(df.head())
    
    print(df.head())