import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
import sys
import os
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage

@tool("A tool to interact with the user and ask him questions")
def chat_tool():
    """
    Tool to give user acces to send results,Notes to the Agent
    """
    user_input = input("Please enter your question: ")

    return user_input


@tool("Create general repport from the user project description")
def general_repport():
    """
  give to this tool  the Job description and it will return a rapport of the client project architecture .
    """
    genai.configure(api_key="AIzaSyDPZ2G97ri3vLM3773usRxNw1A22Yi0c60")
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content(f"""
Act like a senior Azure cloud engineer and Create a cloud architecture for Cloud Azure for this project description : 
""")
    return response.text

