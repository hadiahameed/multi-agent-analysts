from typing import List
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
import matplotlib.pyplot as plt
from crewai.tools import BaseTool


# Uncomment the following line to use an example of a custom tool
# from marketing_posts.tools.custom_tool import MyCustomTool

# Check our tools documentations for more information on how to use them
from crewai_tools import SerperDevTool, ScrapeWebsiteTool,FileReadTool,PDFSearchTool
from pydantic import BaseModel, Field

# llm = LLM(
#         model="ollama/llama3.2",
#         base_url="http://localhost:11434"
#     )

class Report(BaseModel):
	overview: List[str] = Field(..., description="Overview: context and information of the data sources")
	glossary: List[str] = Field(..., description="Glossary: Important fields in the UK data")
	trends: List[str] = Field(..., description="Important trends seen in the UK data")
	KPI: List[str] = Field(..., description="Important KPIs Related to Travel and Tourism returned from policy advisor")
	current_policy: List[str] = Field(..., description="UK's current policy that we seem to have based on current trends")
	recommednation: List[str] = Field(..., description="Policy recommendations from the policy advisor ways to improve the KPIs")

@CrewBase
class PolicyPostsCrew():
	"""PolicyPosts crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	print(tasks_config)

	@agent
	def lead_research_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['lead_research_analyst'],
			tools=[FileReadTool(), PDFSearchTool(), SerperDevTool(), ScrapeWebsiteTool()],
			verbose=True,
			memory=True
			#,LLM=llm
		)

	@agent
	def chief_policy_advisor(self) -> Agent:
		return Agent(
			config=self.agents_config['chief_policy_advisor'],
			tools=[SerperDevTool(), ScrapeWebsiteTool()],
			verbose=True,
			memory=True
			#,LLM=llm
		)
	
	
	@agent
	def presenter(self) -> Agent:
		return Agent(
			config=self.agents_config['presenter'],
			verbose=True,
			memory=True
			#,LLM=llm
		)


	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
			agent=self.lead_research_analyst(),
		)
	@task
	def policy_task(self) -> Task:
		return Task(
			config=self.tasks_config['policy_task'],
			agent=self.chief_policy_advisor(),
		)
	@task
	def insight_gathering_task(self) -> Task:
		return Task(
			config=self.tasks_config['insight_gathering_task'],
			agent=self.presenter(),
			output_json=Report
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the PolicyPosts crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			#process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
			#manager_agent=self.chief_policy_advisor()
		)
