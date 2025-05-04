# Importação das bibliotecas necessárias
import os
from fastapi import FastAPI  # Framework para criar APIs
from pydantic import BaseModel  # Para validação de dados
from crewai import Agent, Task, Crew, Process  # Biblioteca para criar agentes de IA
from crewai_tools import SerperDevTool  # Ferramenta de busca na web

# Inicialização da aplicação FastAPI
app = FastAPI()

# Configuração das chaves de API necessárias para os serviços
# Estas chaves devem ser substituídas por valores reais em produção
os.environ["OPENAI_API_KEY"] = 'xx'  # Chave para acessar a API da OpenAI
os.environ["SERPER_API_KEY"] = 'xx'  # Chave para o serviço de busca Serper
os.environ["CLAUDE_KEY"] = 'xx'      # Chave para a API do Claude (Anthropic)


# Definição do modelo de dados para a entrada da API
# Esta classe valida que a requisição contém o campo job_requirements
class JobRequirements(BaseModel):
    job_requirements: str  # String contendo os requisitos da vaga

# Configuração do agente de IA e suas ferramentas
search_tool = SerperDevTool()  # Inicializa a ferramenta de busca na web
researcher = Agent(
    role='Recrutador Senior de Dados',  # Define o papel do agente
    goal='Encontrar os melhores perfis de dados para trabalhar baseados nos requisitos da vaga',  # Objetivo do agente
    verbose=True,  # Ativa logs detalhados das ações do agente
    memory=True,   # Permite que o agente mantenha memória das interações
    model='gpt-4o-mini',  # Modelo de IA utilizado pelo agente
    backstory=(  # Contexto/história de fundo para o agente
        "Experiencia na area de dados e formação academica em Recursos Humanos e "
        "Especilista em Linkedin, tem dominio das principais taticas de busca de profissionais"
    ),
    tools=[search_tool]  # Ferramentas que o agente pode utilizar
)

# Definição do endpoint da API para pesquisa de candidatos
@app.post("/research_candidates")
async def research_candidates(req: JobRequirements):
    # Criação da tarefa que o agente deve realizar
    research_task = Task(
        description=(  # Descrição detalhada da tarefa para o agente
            f"Realizar pesquisas completas para encontrar candidatos em potencial para o cargo especificado "
            f"Utilize vários recursos e bancos de dados online para reunir uma lista abrangente de candidatos em potencial. "
            f"Garanta que o candidato atenda os requisitos da vaga. Requisitos da vaga: {req.job_requirements}"
        ),
        expected_output=""" Uma lista com top 5 candidatos potenciais separada por Bullet points, 
                            cada candidado deve conter informações de contato e breve descrição do perfil destacando a sua qualificação para a vaga 
                            trazer junto a url para encontrar o perfil do candidato""",  # Formato esperado da saída
        tools=[search_tool],  # Ferramentas disponíveis para esta tarefa
        agent=researcher,  # Agente que executará a tarefa
    )

    # Criação da equipe (crew) e execução da tarefa
    crew = Crew(
        agents=[researcher],  # Lista de agentes na equipe
        tasks=[research_task],  # Lista de tarefas a serem executadas
        process=Process.sequential  # Define que as tarefas serão executadas sequencialmente
    )

    # Inicia o processo e retorna o resultado
    result = crew.kickoff(inputs={'job_requirements': req.job_requirements})
    return {"result": result}  # Retorna o resultado em formato JSON

# Ponto de entrada para execução direta do script
if __name__ == "__main__":
    import uvicorn  # Servidor ASGI para Python
    print(">>>>>>>>>>>> version V0.0.1")  # Log para indicar a versão da aplicação
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Inicia o servidor na porta 8000
