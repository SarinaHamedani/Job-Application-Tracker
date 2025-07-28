from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from gmail_fetcher import authenticate_gmail, search_emails

import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
import time

def get_llm_chain():
    prompt = PromptTemplate(
        input_variables=['emails'],
        template="""
            Analyze the following email and extract:
            - Whether it's related to a job application
            - If yes, extract: Company Name, Job Title, Status (Applied, Interview, Offer, Rejected), and Date

            Email:
            {email}
        """
    )
    
    return ChatOpenAI(model="gpt-4o-mini", temperature=0), prompt

def to_unix(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(time.mktime(dt.timetuple()))

if __name__=="__main__":
    start_date = "2025-07-01"
    end_date = "2025-07-28"
    
    query = f"after:{to_unix(start_date)} before:{to_unix(end_date)}"
    
    service = authenticate_gmail()
    emails = search_emails(service=service, query=query)
    
    llm, prompt = get_llm_chain()
    
    results = []
    for email in emails:
        analysis = llm.predict(prompt.format(email=email['body']))
        results.append({
            'Email Subject': email['subject'],
            'Date': email['date'],
            'Analysis': analysis.strip()
        })

    # Create DataFrame
    df = pd.DataFrame(results)
    df.to_csv("email_job_analysis.csv", index=False)
    
    print(df.head())