import pandas as pd
from dotenv import load_dotenv
import pdfplumber as plum
import os 
import sys
from transformers import BigBirdModel, BigBirdTokenizer
from linkedin_api import Linkedin
from pathlib import Path


pdf_path = "../your_resume/resume.pdf"
abs_path = os.path.abspath(pdf_path)

#check if file exists

if not os.path.exists(abs_path):
    print("File not found in LJS/mian_project/your_resume")
    sys.exit(1)

print("We found your resume")


resume=[] #cuurently has bad formatting(hard to read but maybe it doesnt effect the quality of llm response). 

with plum.open(pdf_path) as pdf:
    for page_number, page in enumerate(pdf.pages, start=1): 
        text = page.extract_text()
        if text:
          #  print(f"--- Page {page_number} ---")
          #  print("\n" + "-" * 50 + "\n")
            resume.append(text)
        else:
            print(f"--- Page {page_number} has no readable text ---")

env_path = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(env_path)

usrname=os.getenv("LINKEDIN_USERNAME")
pwd=os.getenv("LINKEDIN_PASSWORD")

if not usrname or not pwd:
    print("Please set your linkedin username and password in the .env file")
    sys.exit(1)

print("Logging in to Linkedin with provided credentials")

try:
    api=Linkedin(usrname,pwd)
except Exception as e:
    print("Invalid credentials: " + str(e))

    sys.exit(1)

print("User logged in, getting job postings")

job_results=api.search_jobs(experience=["2","3"],job_type=["F"],keywords="Software Engineer",limit=2)  # results are type list


print()

for job in job_results:
    job_detail=api.get_job(job["trackingUrn"].split(":")[-1])
    
    job["Description"]=job_detail["description"]["text"]
    
    for key, val in job.items():
        print("key: ", key, "value: ", val)

    print()

print("Obtained job postings and descriptions, calling LLM model to generate responses")

llm_model = BigBirdModel.from_pretrained('google/bigbird-roberta-base')
llm_tokenizer = BigBirdTokenizer.from_pretrained('google/bigbird-roberta-base')


prompt = "hi how are you."
llm_input = llm_tokenizer(text, return_tensors='pt', max_length=4096, truncation=True, padding='max_length')
llm_output = llm_model(**llm_input)

last_hidden_states = llm_output.last_hidden_state


print(last_hidden_states)