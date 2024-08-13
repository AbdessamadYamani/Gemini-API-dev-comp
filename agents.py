from langchain_openai import ChatOpenAI
from crewai import Agent
import os
import dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from settings import api_configs as config
dotenv.load_dotenv()
from tools.reading_from_user_form import DocClass
from tools.gradiant import RAGGradient
from tools.interactive_tool import chat_tool


class AllAgents():
	
    def __init__(self, openai_api_key):
        self.openai_api_key = openai_api_key

    def assistant_agent(self):
        return Agent(
            role='Assistant Agent',
            goal=(f"""Get infos of User from firebase to create a summary of the methodology that the Teacher Agent should follow to explain."""),
            backstory=("""Designed to assist the Digital Teacher Agent by gathering and summarizing user information from the Databse firebase.You helps in creating a tailored teaching approach based on the user's background, interests, and learning preferences. The Assistant Agent ensures that the teaching methodology is personalized, making the learning experience more effective and engaging."""),
            tools=[],
            allow_delegation=True,
            verbose=True,
            llm=config.llm
        )

    def teacher_agent(self):
        return Agent(
            role='Teacher Agent',
            goal=(f"""You should recreate the way of explaining based on the exercise scores."""),
            backstory=("""A senior teacher that can adapt its teaching methods according to the user's performance in exercises. This agent focuses on explaining complex subjects in a way that aligns with the user's understanding and progress. By dynamically adjusting its approach, the Teacher Agent ensures that the explanations are clear, comprehensive, and tailored to the user's needs."""),
            tools=[],
            allow_delegation=True,
            verbose=True,
            llm=config.llm,
        )

    def verified_agent(self):
        return Agent(
            role='Verified Agent',
            goal=(f"""Teacher assisstante"""),
            backstory=("""The Verified Agent analyzes the user's answers and deside if the user should continue or reset the course and correct the wnswers and give the score and provide the corrections"""),
            tools=[],
            allow_delegation=True,
            verbose=True,
            llm=config.llm,

        )
    def helper_agent(self):
        return Agent(
            role='helper Agent',
            goal=(f"""Help memories and coordonate between agents and the user"""),
            backstory=("""The Helper Agent assists the other agents in coordinating their efforts and ensuring a smooth user experience. This agent helps in managing the communication between the user and the other agents, providing additional support and guidance as needed. By acting as a liaison between the user and the other agents, the Helper Agent ensures that the user's needs are met and that the agents work together effectively.Also can remember what the teacher have explain """),
            tools=[],
            allow_delegation=True,
            verbose=True,
            llm=config.llm
        )

    def insight_agent(self):
        return Agent(
            role='Insight Agent',
            goal=(f"""Visualize the data using Python."""),
            backstory=("""The Insight Agent is responsible for visualizing user data to provide clear and actionable insights. Using Python's data visualization libraries, this agent presents information in an easily understandable format. The visualizations help in identifying trends, patterns, and areas for improvement, making it easier to understand the user's learning journey."""),
            tools=[],
            allow_delegation=True,
            verbose=True,
            llm=self.config.llm
        )