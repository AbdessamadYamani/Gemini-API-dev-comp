from langchain_community.llms import Ollama
from datetime import datetime
from crewai import Task
from settings import api_configs as config

class AllTasks():
	def __init__(self, openai_api_key):
		self.openai_api_key = openai_api_key
	def  analysing_user_answers(self, agent,context):
		
		description = f"""
Correct the answers of the user and give him score next continue the course with the prevouce task

"""
		return Task(
            description=description,
            expected_output="",
			output_file = rf".\collecter_et_analyser_donnees_psychographiques_de_diverses_sources_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            agent=agent,
			context=context
			)
	
	def  Teacher_task(self, agent):
		
		description = f"""
Explain to the user
"""
		return Task(
            description=description,
            expected_output="""
""",
            agent=agent,
			)
	
	

	def  verify_task(self, agent,context):
		
		description = f"""
Analyze the user's latest answer based on the current state:
	        1. Evaluate the correctness and completeness of the answer.
	        2. Provide feedback on the user's understanding.
	        3. Suggest whether to proceed to the next topic or provide additional explanation.
"""
		return Task(
            description=description,
            expected_output="""
The result should be in markdown format
""",
            agent=agent,context=context
			)

	def helper_task(self,agent,context):
	    return Task(
	        description=f"""
            Coordinate the learning process based on the current state:

            1. Summarize the current progress.
            2. Ensure smooth transition between topics.
            3. Provide context for the next interaction.
	        """,
	        agent=agent,context=context
	    )	
	