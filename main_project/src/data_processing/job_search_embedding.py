import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from linkedin_api import Linkedin
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables
load_dotenv()

# OpenAI API Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


'''
    This class is used to search for jobs on LinkedIn and match them with resume using embedding.
    It uses OpenAI API to generate embeddings for the resume and job description.
    It then calculates the cosine similarity between the resume and job description embeddings.
    It then returns the jobs that have the highest similarity to the resume.
'''
class JobSearch:
    def __init__(self):
        self.usrname = os.getenv("LINKEDIN_USERNAME")
        self.pwd = os.getenv("LINKEDIN_PASSWORD")
        self.api = Linkedin(self.usrname, self.pwd)

    def search_jobs(self, search_param):
        """Search for jobs on LinkedIn"""
        try:
            jobs = self.api.search_jobs(**search_param)
            return jobs
        except Exception as e:
            print(f"Error searching for jobs: {e}")
            return []

    def get_job_details_by_id(self, job_id):
        """Get job details by job ID"""
        try:
            job_details = self.api.get_job(job_id)
            return job_details
        except Exception as e:
            print(f"Error getting job details: {e}")
            return {}

def get_openai_embedding(text):
    """Generates an embedding for a given text using OpenAI API"""
    try:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

def calculate_similarity(resume_embedding, job_embedding):
    """Calculates cosine similarity between resume and job description embeddings"""
    if resume_embedding is None or job_embedding is None:
        return 0.0
    return cosine_similarity([resume_embedding], [job_embedding])[0][0]

def main():
    search_params = {
        "keywords": "Software Engineer",
        "location_name": "United States",
        "remote": ["2"],  # Remote jobs only
        "experience": ["2", "3"],  # Entry level and Associate
        "job_type": ["F", "C"],  # Full-time and Contract
        "limit": 3,
    }

    # Load and format resume text
    resume_path = Path("main_project/resume.json")
    with open(resume_path, "r", encoding="utf-8") as f:
        resume_data = json.load(f)
        # Convert JSON to string format
        resume_text = f"""
        Experience: {resume_data.get('experience', '')}
        Education: {resume_data.get('education', '')}
        Skills: {resume_data.get('skills', '')}
        """

    # Generate embedding for the resume
    resume_embedding = get_openai_embedding(resume_text)

    job_search = JobSearch()
    jobs = job_search.search_jobs(search_params)

    extracted_data = []

    for job in jobs:
        job_id = job["entityUrn"].split(":")[-1]
        details = job_search.get_job_details_by_id(job_id)

        title = details.get("title", "N/A")
        company = details.get("companyDetails", {}).get("com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany", {}).get("companyResolutionResult", {}).get("name", "N/A")
        location = details.get("formattedLocation", "N/A")
        workplace_type = details.get("workplaceTypesResolutionResults", {}).get("urn:li:fs_workplaceType:2", {}).get("localizedName", "N/A")
        apply_method = details.get("applyMethod", {}).get("com.linkedin.voyager.jobs.OffsiteApply", {}) or details.get("applyMethod", {}).get("com.linkedin.voyager.jobs.ComplexOnsiteApply", {})
        apply_url = apply_method.get("companyApplyUrl") or apply_method.get("easyApplyUrl", "N/A")
        description = details.get("description", {}).get("text", "")
        print(description)

        # Generate embedding for job description
        job_embedding = get_openai_embedding(description)

        # Compute similarity
        match_percentage = calculate_similarity(resume_embedding, job_embedding) * 100

        # Store data
        extracted_data.append({
            "Match %": round(match_percentage, 2),
            "Title": title,
            "Company": company,
            "Location": location,
            "Workplace Type": workplace_type,
            "Apply URL": apply_url
        })

    # Convert to DataFrame
    df = pd.DataFrame(extracted_data)

    # Save to Excel
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    excel_path = output_dir / "job_matches.xlsx"
    df.to_excel(excel_path, index=False)

    print(f"Data saved successfully to {excel_path}")

if __name__ == "__main__":
    main()
