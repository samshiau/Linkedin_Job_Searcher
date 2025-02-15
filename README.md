🚧 Work in Progress 🚧

2/10/2025
Completed pdf reading and job details retrieval. <br>
\*\*Currently resolving sentencepiece version issue with python 3.13.1

![image](https://github.com/user-attachments/assets/d487eef5-a1b1-48be-bafa-a1dee3721bb2)

# Project Setup Guide

## 1. Python Environment Setup

Make sure you have Python 3.11+ installed, then:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

## 2. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# Install spaCy language model
python -m spacy download en_core_web_sm
```

## 3. Environment Variables

Create a `.env` file in the root directory:

```env
LINKEDIN_USERNAME=your_email
LINKEDIN_PASSWORD=your_password
OPENAI_API_KEY=your_openai_key
```

## 4. Running the Project

```bash
# From the project root directory
python src/data_processing/job_search.py
```

## Dependencies

- Python 3.11+
- numpy>=1.26.0
- spacy>=3.7.2
- xlsxwriter>=3.1.0
- python-dotenv
- pandas
