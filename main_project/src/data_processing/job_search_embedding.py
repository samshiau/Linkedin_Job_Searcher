import os

# Import lazy loader
from utils.lazy_module import LazyModule

# Lazy imports
json = LazyModule('json')
pd = LazyModule('pandas')
np = LazyModule('numpy')

# Third-party imports
OpenAI = LazyModule('openai')
load_dotenv = LazyModule('dotenv').load_dotenv
Linkedin = LazyModule('linkedin_api').Linkedin
cosine_similarity = LazyModule('sklearn.metrics.pairwise').cosine_similarity

# # Local application imports
# from pathlib import Path
# from dotenv import load_dotenv
# from openai import OpenAI
# from linkedin_api import Linkedin
# from sklearn.metrics.pairwise import cosine_similarity

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


    extracted_data = []

 
