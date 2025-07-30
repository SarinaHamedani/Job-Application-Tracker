from gmail_fetcher import authenticate_gmail, search_emails

import pandas as pd
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
import time

from openai import OpenAI
import re

client = OpenAI()  # Assumes your OPENAI_API_KEY is set in the environment
VALID_STATUSES = {"Applied", "Interview", "Offer", "Rejected"}

def get_job_info(email_text, email_date):
    prompt = f"""
    You are an assistant that extracts job application information from emails.
    Analyze the email below. If it is related to a job application, extract the following structured data ONLY:

    | Company | Job Title | Status | Date |

    - Status must be exactly one of: Applied, Interview, Offer, Rejected
    - If it's not job-related, respond only with: NOT JOB-RELATED

    Email:
    {email_text}
    Date:
    {email_date}
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


def merge_jobs(emails_df):
    records = emails_df.to_dict(orient="records")

    prompt = f"""
    You are a helpful assistant that merges and reconciles job application records.

    You will receive a list of job application records extracted from emails. Each record contains:
    - Company Name
    - Job Title (may vary slightly across records referring to the same job)
    - Application Status (Applied, Interview, Offer, Rejected)
    - Date (YYYY-MM-DD format)

    Your task:
    1. Group records that refer to the same job using the Company Name and a similar Job Title (minor wording differences are allowed).
    2. For each group, determine the **latest status** by choosing the record with the most recent Date.
    3. Return Return the final deduplicated job list as a Markdown table ONLY:
    | Company | Job Title | Status | Date |
    |---------|-----------|--------|------|
    | ...     | ...       | ...    | ...  |
    Here are the job records:
    {records}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a data-cleaning assistant specializing in job application records."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

def to_unix(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(time.mktime(dt.timetuple()))

def convert_to_df(txt):
    results = []
    lines = txt.splitlines()
    # LLM always puts a line containing - only between the Column names row and the content
    lines.pop(1)
    if len(lines) >= 2 and "|" in lines[1]:
        data_row = [cell.strip() for cell in lines[1].split("|")[1:-1]]
        if len(data_row) == 4 and data_row[2] in VALID_STATUSES:
            results.append({
                "Company": data_row[0],
                "Job Title": data_row[1],
                "Status": data_row[2],
                "Date": data_row[3],
                "Email Subject": email["subject"]
            })
    return results
if __name__=="__main__":
    start_date = "2025-07-01"
    end_date = "2025-07-28"
    
    query = f"after:{to_unix(start_date)} before:{to_unix(end_date)}"
    
    service = authenticate_gmail()
    emails = search_emails(service=service, query=query)
    
    
    results = []
    for email in emails:
        analysis = get_job_info(email['body'], email['date'])
        
        if analysis.startswith("NOT JOB-RELATED"):
            continue
        
        try:
            results.extend(convert_to_df(analysis))
        except Exception as e:
            print(f"Error parsing result:\n{analysis}\nError: {e}")
            continue

    df = pd.DataFrame(results)
    
    if not df.empty:
        merged_output = merge_jobs(df)

        # Extract rows from the GPT output (skip header and separator lines)
        rows = []
        lines = merged_output.splitlines()
        job_lines = [
            line for line in lines
            if re.match(r'^\|\s*[^|]+\s*\|\s*[^|]+\s*\|\s*[^|]+\s*\|\s*[^|]+\s*\|$', line)
            and not re.match(r'^\|[-\s]+\|$', line)  # skip header separator row like |------|----|---|
        ]

        for line in job_lines:
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if len(cells) == 4:
                rows.append({
                    "Company": cells[0],
                    "Job Title": cells[1],
                    "Status": cells[2],
                    "Date": cells[3]
                })

        final_df = pd.DataFrame(rows)
        final_df = final_df[
            ~final_df["Company"].str.strip().str.lower().eq("company") & 
            ~final_df["Company"].str.contains(r'-{3,}')
        ]

        final_df.to_csv("filtered_job_emails.csv", index=False)
        print(final_df.head())
    else:
        print("No job-related emails found in the selected date range.")
        # print(df.head())