import streamlit as st
import os
import json
import tempfile
from typing import List
from crewai.tools import tool
from contextlib import redirect_stdout
import gc
from crew import PolicyPostsCrew
import sys
import base64
import time
import yaml
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Crew, Process, Task, LLM
from crewai_tools import ScrapeWebsiteTool,FileReadTool
import pandas as pd
from pydantic import BaseModel, Field


@st.cache_resource
def load_llm():

    llm = LLM(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

    # llm = LLM(
    #     model="ollama/llama3.2",
    #     base_url="http://localhost:11434"
    # )
    return llm

st.markdown("""
    # UK travel trend report re-written by AI agents
""", unsafe_allow_html=True)


if "messages" not in st.session_state:
    st.session_state.messages = []  # Chat history

if "response" not in st.session_state:
    st.session_state.response = None

if "crew" not in st.session_state:
    st.session_state.crew = None      # Store the Crew object

def reset_chat():
    st.session_state.messages = []
    gc.collect()

def start_analysis():
    with st.spinner('The agents are analyzing the data.'):
        try:
            inputs = {
            "file_paths": ['data/data_number_of_visits_aborad_by_area.txt', 'data/data_number_visits.txt', 'data/notes.txt', 'data/data_number_of_visits_abroad_by_area_purpose_air.txt', 'data/contents.txt', 'data/data_spending_abroad_area_purpose_visit.txt', 'data/data_number_of_visits_abroad_by_area_purpose_sea.txt', 'data/definitions.txt', 'data/data_number_of_visits_abroad_by_area_purpose_all_modes.txt', 'data/data_nights_spent_abroad.txt', 'data/data_number_of_visits_abroad_by_destination.txt', 
                           'data/data_spending_abroad.txt', 'data/context.txt', 'data/data_spending_by_destination.txt',
                           'data/Expedia_sample_report_2024.pdf','data/Expedia_sample_report_2025.pdf'],
            'customer_domain': 'travel',
            'project_description': """
            Develop a report on outlining changes to UK's travel and tourism statistics from July 2024. Advise on policy change to improving our travel and tourism statistics: changes from July 2024.

            Customer Domain: Travel and Tourism
            Project Overview: Creating a comprehensive policy report to improve travel and tourism statistics for the UK.
            """
            }
            st.session_state.crew = PolicyPostsCrew().crew()
            #st.session_state.response = st.session_state.crew.kickoff(inputs=inputs)
            output_file = "agents_output.txt"
            with open(output_file, "a") as f:
                with redirect_stdout(f):  # Redirect all print output to the file
                    # Run the agent and capture its final response
                    st.session_state.response = st.session_state.crew.kickoff(inputs=inputs)
        except:
            st.error(f"An error occurred during analysis: {str(e)}")

                    


# ===========================
#   Sidebar
# ===========================
with st.sidebar:

    st.divider()
    st.button("Generate Report 🚀", type="primary", on_click=start_analysis)
    
    st.markdown(f"[Datasource - Estimates of overseas residents’ visits and spending collected by Office for National Statistics](https://www.ons.gov.uk/peoplepopulationandcommunity/leisureandtourism/datasets/estimatesofoverseasresidentsvisitsandspendingintheuk)", unsafe_allow_html=True)
    st.markdown(f"[Expedia Sample Report 2024](https://partner.expediagroup.com/en-us/resources/research-insights/unpack-24-travel-trends-2024)", unsafe_allow_html=True)
    st.markdown(f"[Expedia Sample Report 2025](https://www.expedia.ca/unpack-travel-trends/)", unsafe_allow_html=True)
    # st.button("Clear Chat", on_click=reset_chat)

# ===========================
#   Main Chat Interface
# ===========================

# Main content area
if st.session_state.response:
    with st.spinner('Generating content... This may take a moment.'):
        try:
            result = st.session_state.response
            st.markdown("### Generated Analysis")
            result_dict = json.loads(result.raw)
            # Check if the result is a dictionary
            if isinstance(result_dict , dict):
                for key, value in result_dict.items():
                    st.markdown(f"#### {key.capitalize()}")
                    
                    # Handle different data types for values
                    if isinstance(value, list):
                        for item in value:
                            st.markdown(f"- {item}")
                    else:
                        st.markdown(value)
            
            # Add download button
            st.download_button(
                label="Download Content",
                data=result.raw,
                file_name=f"UK_report.md",
                mime="text/markdown"
            )
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Built with CrewAI, Streamlit")