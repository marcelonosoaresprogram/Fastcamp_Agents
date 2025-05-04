# pip install crewai==0.22.5 streamlit==1.32.2

"""
Aplicação de Escrita de Blog com CrewAI e Streamlit

Este script implementa uma interface web para um sistema de escrita automática de blogs
usando a biblioteca CrewAI e Streamlit. O sistema utiliza dois agentes de IA especializados:
um escritor e um revisor, que trabalham juntos para criar um blog post de qualidade
com base no tópico fornecido pelo usuário.
"""

# Importação das bibliotecas necessárias
import streamlit as st  # Framework para criar aplicações web interativas

# Importações relacionadas ao CrewAI e LangChain
from dotenv import load_dotenv  # Para carregar variáveis de ambiente (API keys)
from crewai import Crew, Process, Agent, Task  # Framework para criar e gerenciar agentes
from langchain_core.callbacks import BaseCallbackHandler  # Para criar handlers de callback personalizados
from typing import TYPE_CHECKING, Any, Dict, Optional  # Para tipagem
from langchain_openai import ChatOpenAI  # Integração com a OpenAI

# Carrega variáveis de ambiente do arquivo .env (como OPENAI_API_KEY)
load_dotenv()
# Inicializa o modelo de linguagem da OpenAI
llm = ChatOpenAI()

# Define avatares para os diferentes agentes na interface
avators = {"Writer":"https://cdn-icons-png.flaticon.com/512/320/320336.png",
            "Reviewer":"https://cdn-icons-png.freepik.com/512/9408/9408201.png"}

class MyCustomHandler(BaseCallbackHandler):
    """
    Handler personalizado para processar callbacks dos agentes e atualizar a interface do Streamlit.
    Este handler captura as entradas e saídas das chains do LangChain e as exibe na interface.
    """
    
    def __init__(self, agent_name: str) -> None:
        """
        Inicializa o handler com o nome do agente.
        
        Args:
            agent_name: Nome do agente para identificar suas mensagens na interface.
        """
        self.agent_name = agent_name

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """
        Executado quando uma chain começa a processar.
        Captura o prompt inicial e o exibe na interface.
        
        Args:
            serialized: Informações serializadas sobre a chain
            inputs: Entradas para a chain (incluindo o prompt)
        """
        st.session_state.messages.append({"role": "assistant", "content": inputs['input']})
        st.chat_message("assistant").write(inputs['input'])
   
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """
        Executado quando uma chain termina de processar.
        Captura a saída gerada e a exibe na interface com o avatar apropriado.
        
        Args:
            outputs: Saídas da chain (texto gerado pelo agente)
        """
        st.session_state.messages.append({"role": self.agent_name, "content": outputs['output']})
        st.chat_message(self.agent_name, avatar=avators[self.agent_name]).write(outputs['output'])

# Definição do agente Writer (Escritor)
writer = Agent(
    role='Blog Post Writer',  # Função do agente
    backstory=
    '''You are a blog post writer who is capable of writing a travel blog.
    You generate one iteration of an article once at a time.
    You never provide review comments.
    You are open to reviewer's comments and willing to iterate its article based on these comments.
    ''', 
    goal="Write and iterate a decent blog post.",  # Objetivo principal do agente
    # tools=[]  # Ferramentas que o agente pode usar (opcional)
    llm=llm,  # Modelo de linguagem a ser utilizado
    callbacks=[MyCustomHandler("Writer")],  # Handler para processar callbacks e atualizar a UI
)

# Definição do agente Reviewer (Revisor)
reviewer = Agent(
    role='Blog Post Reviewer',  # Função do agente
    backstory=
    '''You are a professional article reviewer and very helpful for improving articles.
    You review articles and give change recommendations to make the article more aligned with user requests.
    You will give review comments upon reading entire article, so you will not generate anything when the article is not completely delivered. 
    You never generate blogs by itself.''', 
    goal="list builtins about what need to be improved of a specific blog post. Do not give comments on a summary or abstract of an article",  # Objetivo principal
    # tools=[]  # Ferramentas que o agente pode usar (opcional)
    llm=llm,  # Modelo de linguagem a ser utilizado
    callbacks=[MyCustomHandler("Reviewer")],  # Handler para processar callbacks e atualizar a UI
)

# Configuração da interface do Streamlit
st.title("💬 CrewAI Writing Studio") 

# Inicialização do estado da sessão para armazenar o histórico de mensagens
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "What blog post do you want us to write?"}]

# Exibição do histórico de mensagens na interface
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Campo de entrada para o usuário digitar o tema do blog
if prompt := st.chat_input():
    # Adiciona a entrada do usuário ao histórico de mensagens e a exibe
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Define a tarefa para o agente Writer: escrever o blog post sobre o tema fornecido
    task1 = Task(
      description=f"""Write a blog post of {prompt}. """,  # Descrição da tarefa com o tema do usuário
      agent=writer,  # Agente responsável pela tarefa
      expected_output="an article under 300 words."  # Saída esperada
    )

    # Define a tarefa para o agente Reviewer: revisar o blog post criado
    task2 = Task(
      description="""list review comments for improvement from the entire content of blog post to make it more viral on social media""",  # Descrição da tarefa
      agent=reviewer,  # Agente responsável pela tarefa
      expected_output="Builtin points about where need to be improved."  # Saída esperada
    )
    
    # Criação da crew (equipe) com processo hierárquico
    project_crew = Crew(
        tasks=[task1, task2],  # Lista de tarefas a serem executadas
        agents=[writer, reviewer],  # Agentes disponíveis na crew
        manager_llm=llm,  # Modelo de linguagem usado pelo gerenciador
        process=Process.hierarchical  # Processo hierárquico: as tarefas são executadas em sequência
    )
    
    # Inicia o processo da crew e obtém o resultado final
    final = project_crew.kickoff()

    # Formata e exibe o resultado final na interface
    result = f"## Here is the Final Result \n\n {final}"
    st.session_state.messages.append({"role": "assistant", "content": result})
    st.chat_message("assistant").write(result)