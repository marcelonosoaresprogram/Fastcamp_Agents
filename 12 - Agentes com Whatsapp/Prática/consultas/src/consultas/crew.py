from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import FileReadTool
from crewai.tools import BaseTool
import requests
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
 

file_read_tool = FileReadTool("C:\\Users\\drmar\\OneDrive\\Documentos\\code\\Fastcamp_Agents\\12\\Prática\\consultas\\src\\consultas\\abc.csv")
url = "http://127.0.0.1:3000/api/sendText"


class RequestTool(BaseTool):
    name: str = "request_tool"
    description: str = "A tool to make requests to a specific URL."

    def _run(self, text: str, chatId: str) -> str:
        full_chat_id = f"{chatId}@c.us"
        response = requests.post(
            url,
            json={"chatId": full_chat_id, "text": text, "session": "default"}
        )
        if response.status_code not in (200,201):
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")
        return response.text

request_tool = RequestTool()

@CrewBase
class Consultas():
    """Consultas crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def arquivo(self) -> Agent:
        return Agent(
            config=self.agents_config['arquivo'], # type: ignore[index]
            verbose=True,
            tools=[file_read_tool] # type: ignore[index]
        )

    @agent
    def mensagem(self) -> Agent:
        return Agent(
            config=self.agents_config['mensagem'], # type: ignore[index]
            verbose=True,
            tools=[request_tool] # type: ignore[index]
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def arquivo_task(self) -> Task:
        return Task(
            config=self.tasks_config['arquivo_task'], # type: ignore[index]
        )

    @task
    def mensagem_task(self) -> Task:
        return Task(
            config=self.tasks_config['mensagem_task'], # type: ignore[index]
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Consultas crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
