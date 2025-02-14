from linkedin_api import Linkedin
from dotenv import load_dotenv
import os
import pandas as pd
import json
from pathlib import Path
import openai
import re
from datetime import datetime
from data_extraction import process_job_description

# Load environment variables
load_dotenv()

class JobSearch:
    def __init__(self):
        self.usrname = os.getenv("LINKEDIN_USERNAME")
        self.pwd = os.getenv("LINKEDIN_PASSWORD")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.api = Linkedin(self.usrname, self.pwd)
        openai.api_key = self.openai_api_key

    def search_jobs(self, search_param):
        """Search for jobs on LinkedIn"""
        try:
            return self.api.search_jobs(**search_param)
        except Exception as e:
            print(f"Error searching for jobs: {e}")
            return []
    
    def get_job_details_by_id(self, job_id):
        """Get job details by job ID"""
        try:
            return self.api.get_job(job_id)
        except Exception as e:
            print(f"Error getting job details: {e}")
            return {}

    def match_resume_with_job(self, job_desc, resume_text):
        """Uses OpenAI to calculate match percentage between job description and resume"""
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages = [
                    {"role": "system", "content": "You are a job matching AI. Your task is to analyze the similarity between a job description and a resume. Respond with a single integer between 0 and 100, representing the match percentage. Do not include a % symbol, explanation, or any other text."},
                    {"role": "user", "content": f"Evaluate the match percentage between this job description and resume:\n\nJob Description:\n{job_desc}\n\nResume:\n{resume_text}\n\nReturn only a number from 0 to 100."}
                ]
            )
            output = response.choices[0].message.content.strip()
            return int(output) if output.isdigit() else "Unknown"
        except Exception as e:
            print(f"Error calculating match percentage: {e}")
            return "Error"
    
    def filter_job_by_date(self, jobs, days=1):
        """Filter jobs by date posted (within the last 'days' days)"""
        current_time = datetime.now()
        filtered_jobs = []
        for job in jobs:
            listed_time = job.get('listedAt', 'N/A')
            if listed_time != 'N/A':
                listed_time = datetime.fromtimestamp(int(listed_time)/1000)
                if (current_time - listed_time).days <= days:
                    filtered_jobs.append(job)
        return filtered_jobs

def main():
    search_params = {
        "keywords": "Software Engineer",
        "location_name": "United States",
        "remote": ["2"],  # Remote jobs only
        "experience": ["2", "3"],  # Entry level and Associate
        "job_type": ["F", "C"],  # Full-time and Contract
        "limit": 2,
    }
    
    search_params2 = {
        "keywords": "Software Developer",
        "location_name": "United States",
        "experience": ["2", "3"],  # Entry level and Associate
        "job_type": ["F", "C"],  # Full-time and Contract
        "limit": 2,
    }
    
    search_params3 = {
        "keywords": "Backend",
        "location_name": "United States",
        "experience": ["2", "3"],  # Entry level and Associate
        "job_type": ["F", "C"],  # Full-time and Contract
        "limit": 2,
    }
    
    # resume_text = Path("main_project/resume.json").read_text()  # Load user's resume
    job_search = JobSearch()
    jobs = []
    jobs.extend(job_search.search_jobs(search_params))
    jobs.extend(job_search.search_jobs(search_params2))
    jobs.extend(job_search.search_jobs(search_params3))
    
    job_results = []

    for job in jobs:
        job_id = job["entityUrn"].split(":")[-1]
        details = job_search.get_job_details_by_id(job_id)
        
        # print(details)
        
        # Extract metadata directly from LinkedIn API
        job_title = details.get('title', 'N/A')
        company = details.get('companyDetails', {}).get('com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany', {}).get('companyResolutionResult', {}).get('name', 'N/A')
        
        # filter out unwanted company
        black_list = ["Revature", "BeaconFire Inc.", "BeaconFire Solution Inc.", "Canoical", "SynergisticIT"]
        if company in black_list:
            continue
        
        company_linkedin_url = details.get('companyDetails', {}).get('com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany', {}).get('companyResolutionResult', {}).get('url', 'N/A')
        location = details.get('formattedLocation', 'N/A')
        workplace_type = details.get('workplaceTypesResolutionResults', {}).get('urn:li:fs_workplaceType:2', {}).get('localizedName', 'N/A')
        job_desc = details.get('description', {}).get('text', '')
        listed_time = details.get('listedAt', 'N/A')
        
        # print(job_desc)

        # Convert Unix timestamp (milliseconds) to readable date
        if listed_time != 'N/A':
            listed_time = datetime.fromtimestamp(int(listed_time)/1000).strftime('%Y-%m-%d %H:%M')

        # Extract apply URL (Easy Apply or External)
        apply_method = details.get('applyMethod', {}).get('com.linkedin.voyager.jobs.OffsiteApply', {}) or details.get('applyMethod', {}).get('com.linkedin.voyager.jobs.ComplexOnsiteApply', {})
        apply_url = apply_method.get('companyApplyUrl', company_linkedin_url)
        
        job_state = details.get('jobState', 'N/A')
        
        ## Match resume with job description
        # match_percentage = job_search.match_resume_with_job(job_desc, resume_text)
        job_data = process_job_description(job_desc)
        
        print("job_data", job_data)

        # Store extracted job details
        job_results.append({
            "Listed Date": listed_time,
            "Job Title": job_title,
            "Company": company,
            "Location": location,
            "Workplace Type": workplace_type,
            "Skills": job_data.get("skills"),
            "Experience Level": job_data.get("experience_level"),
            "Salary": job_data.get("salary"),
            "Apply URL": apply_url,
            # "Job State": job_state,
            "Salary": job_data.get("salary"),
            # "Match Level (%)": match_percentage
        })
    
    # Convert to DataFrame and save results
    df = pd.DataFrame(job_results)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Save data
    json_path = output_dir / "job_data.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(job_results, f, indent=4, ensure_ascii=False)

    # Save to Excel with hyperlinks
    writer = pd.ExcelWriter(output_dir / "job_data.xlsx", engine='xlsxwriter')
    df.to_excel(writer, index=False)
    
    # Get the xlsxwriter workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    
    # Auto-adjust columns width
    for idx, col in enumerate(df.columns):
        # Get the maximum length in the column
        max_length = max(
            df[col].astype(str).apply(len).max(),  # max length of values
            len(str(col))  # length of column name
        )
        worksheet.set_column(idx, idx, max_length + 2)  # Add some padding
    
    # Add hyperlink format
    link_format = workbook.add_format({
        'font_color': 'blue',
        'underline': True,
    })
    
    # Find the Apply URL column index
    url_col = df.columns.get_loc('Apply URL')
    
    # Add hyperlinks to each row in the Apply URL column
    for row_num, url in enumerate(df['Apply URL'], start=1):
        if url != 'N/A':
            worksheet.write_url(row_num, url_col, url, link_format, url)
    
    writer.close()

    print(f"Data saved successfully to:\n- {json_path}\n- {output_dir / 'job_data.xlsx'}")

if __name__ == "__main__":
    main()
