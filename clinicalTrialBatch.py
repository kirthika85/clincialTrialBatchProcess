import streamlit as st
import pandas as pd
import requests
import json
from langchain.chat_models import ChatOpenAI

# Function to prompt LLM for ICD codes
def prompt_llm_for_icd_codes(llm, study_title):
    prompt = f"""
    Identify relevant ICD codes for the following clinical trial study title:

    **Study Title:**
    {study_title}

    List the ICD codes that are most relevant to this study.
    """
    try:
        result = llm.invoke(prompt).content
        icd_codes = result.strip('` \n').splitlines()
        
        # Extract the first ICD code and its first three letters
        if icd_codes:
            first_icd_code = icd_codes[0]
            first_three_letters = first_icd_code[:3]
            return first_three_letters
        else:
            return None
    except Exception as e:
        st.error(f"Error prompting LLM: {str(e)}")
        return None

# Sidebar for OpenAI API Key
with st.sidebar:
    openai_api_key = st.text_input("Enter OpenAI API Key")

# Load files
uploaded_files = st.file_uploader("Upload files", type=["xlsx", "xls", "csv"], accept_multiple_files=True)

if len(uploaded_files) >= 3 and openai_api_key:
    clinical_trial_file = uploaded_files[0]
    icd_codes_file = uploaded_files[1]
    patient_database_file = uploaded_files[2]
    
    # Load data
    clinical_trial_df = pd.read_excel(clinical_trial_file, engine='openpyxl', dtype=str)
    icd_codes_df = pd.read_excel(icd_codes_file, engine='openpyxl', dtype=str)
    patient_database_df = pd.read_excel(patient_database_file, engine='openpyxl', dtype=str)
    
    # Initialize LLM
    llm = ChatOpenAI(openai_api_key=openai_api_key, model="gpt-4", temperature=0.1)
    
    # Button to update Clinical Trials DataFrame with ICD codes
    if st.button("Update Clinical Trials with ICD Codes"):
        st.write("Updating Clinical Trials DataFrame...")
        
        # Add a new column for ICD codes
        clinical_trial_df['ICD Code'] = None
        
        # Iterate over each study title
        for index, row in clinical_trial_df.iterrows():
            study_title = row['Study Title']
            icd_prefix = prompt_llm_for_icd_codes(llm, study_title)
            if icd_prefix:
                clinical_trial_df.loc[index, 'ICD Code'] = icd_prefix
            else:
                st.write(f"No ICD code found for {study_title}.")
        
        # Display updated DataFrame
        st.write("### Updated Clinical Trials DataFrame:")
        st.dataframe(clinical_trial_df)
