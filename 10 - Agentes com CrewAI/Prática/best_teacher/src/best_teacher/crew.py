# src/educational_content_team/crew.py

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

scrape = ScrapeWebsiteTool('https://www.example.com')

@CrewBase
class BestTeacher:
    """
    BestTeacher é a equipe de agentes responsável por criar conteúdos educativos
    completos, bem organizados e didáticos a partir de um tópico e um contexto
    fornecidos pelo usuário.

    Essa equipe executa uma sequência de tarefas usando 6 agentes especializados:
    1. Coordenador (admin)
    2. Coletor de URLs (url_collector)
    3. Extrator de conteúdo da web (content_scraper)
    4. Pesquisador (researcher)
    5. Aprimorador didático (enhancer)
    6. Editor final em Markdown (editor)
    """

    # Caminhos dos arquivos YAML de configuração de agentes e tarefas
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # =========================
    # DEFINIÇÃO DOS AGENTES
    # =========================

    @agent
    def admin(self) -> Agent:
        """Agente responsável por planejar e delegar as tarefas"""
        return Agent(config=self.agents_config['admin'], verbose=True,)

    @agent
    def url_collector(self) -> Agent:
        """Agente que busca URLs com conteúdo educacional usando SerperDevTool"""
        return Agent(
            config=self.agents_config['url_collector'], 
            verbose=True, 
            tools=[SerperDevTool()]
            )

    @agent
    def content_scraper(self) -> Agent:
        """Agente que extrai o conteúdo das URLs usando ScrapeWebsiteTool"""
        return Agent(config=self.agents_config['content_scraper'], verbose=True, tools= [scrape,])

    @agent
    def researcher(self) -> Agent:
        """Agente responsável por realizar uma pesquisa profunda sobre o tema"""
        return Agent(config=self.agents_config['researcher'], verbose=True)

    @agent
    def enhancer(self) -> Agent:
        """Agente que transforma o conteúdo em algo mais didático e estruturado"""
        return Agent(config=self.agents_config['enhancer'], verbose=True)

    @agent
    def editor(self) -> Agent:
        """Agente que revisa e gera o arquivo final em Markdown"""
        return Agent(config=self.agents_config['editor'], verbose=True)

    # =========================
    # DEFINIÇÃO DAS TAREFAS
    # =========================

    @task
    def assign_task(self) -> Task:
        """Tarefa do coordenador: planejar a execução"""
        return Task(config=self.tasks_config['assign_task'])

    @task
    def collect_urls(self) -> Task:
        """Tarefa de busca de URLs com conteúdo educacional"""
        return Task(config=self.tasks_config['collect_urls'])

    @task
    def scrape_content(self) -> Task:
        """Tarefa de extração do conteúdo das páginas encontradas"""
        return Task(config=self.tasks_config['scrape_content'])

    @task
    def research_task(self) -> Task:
        """Tarefa de pesquisa profunda sobre o tópico"""
        return Task(config=self.tasks_config['research_task'])

    @task
    def enhance_task(self) -> Task:
        """Tarefa de melhoria e organização didática do conteúdo"""
        return Task(config=self.tasks_config['enhance_task'])

    @task
    def finalize_task(self) -> Task:
        """Tarefa de edição final do conteúdo e exportação em Markdown"""
        return Task(
            config=self.tasks_config['finalize_task'],
            output_file='output/final_markdown.md'  # Caminho de saída do conteúdo final
        )

    # =========================
    # DEFINIÇÃO DA CREW
    # =========================

    @crew
    def crew(self) -> Crew:
        """
        Cria a equipe de agentes e define que o processo de execução será sequencial,
        ou seja, um agente executa sua tarefa e o próximo continua a partir daí.
        """
        return Crew(
            agents=self.agents,  # Agentes definidos acima com @agent
            tasks=self.tasks,    # Tarefas definidas acima com @task
            process=Process.sequential,  # Execução em ordem
            verbose=True,
            memory=True,
        )
