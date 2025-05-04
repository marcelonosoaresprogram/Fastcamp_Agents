from crewai import Agent
import re
import streamlit as st
from langchain_community.llms import OpenAI

from tools.browser_tools import BrowserTools
from tools.calculator_tools import CalculatorTools
from tools.search_tools import SearchTools

## Código de callback comentado que originalmente era usado para exibir o progresso dos agentes na interface
## Substituído posteriormente pelo StreamToExpander
# def streamlit_callback(step_output):
#     # This function will be called após cada etapa da execução do agente
#     st.markdown("---")
#     for step in step_output:
#         if isinstance(step, tuple) and len(step) == 2:
#             action, observation = step
#             if isinstance(action, dict) and "tool" in action and "tool_input" in action and "log" in action:
#                 st.markdown(f"# Action")
#                 st.markdown(f"**Tool:** {action['tool']}")
#                 st.markdown(f"**Tool Input** {action['tool_input']}")
#                 st.markdown(f"**Log:** {action['log']}")
#                 st.markdown(f"**Action:** {action['Action']}")
#                 st.markdown(
#                     f"**Action Input:** ```json\n{action['tool_input']}\n```")
#             elif isinstance(action, str):
#                 st.markdown(f"**Action:** {action}")
#             else:
#                 st.markdown(f"**Action:** {str(action)}")

#             st.markdown(f"**Observation**")
#             if isinstance(observation, str):
#                 observation_lines = observation.split('\n')
#                 for line in observation_lines:
#                     if line.startswith('Title: '):
#                         st.markdown(f"**Title:** {line[7:]}")
#                     elif line.startswith('Link: '):
#                         st.markdown(f"**Link:** {line[6:]}")
#                     elif line.startswith('Snippet: '):
#                         st.markdown(f"**Snippet:** {line[9:]}")
#                     elif line.startswith('-'):
#                         st.markdown(line)
#                     else:
#                         st.markdown(line)
#             else:
#                 st.markdown(str(observation))
#         else:
#             st.markdown(step)


class TripAgents():
    # Classe que define os diferentes agentes especializados usados no planejamento de viagem

    def city_selection_agent(self):
        # Cria um agente especializado em selecionar a melhor cidade para a viagem
        # Este agente analisa dados meteorológicos, temporadas e preços para escolher o destino ideal
        return Agent(
            role='City Selection Expert',
            goal='Select the best city based on weather, season, and prices',
            backstory='An expert in analyzing travel data to pick ideal destinations',
            tools=[
                SearchTools.search_internet,  # Ferramenta para buscar informações na internet
                BrowserTools.scrape_and_summarize_website,  # Ferramenta para coletar e resumir conteúdo de sites
            ],
            verbose=True,  # Exibe detalhes do processo de raciocínio do agente
            # step_callback=streamlit_callback,  # Callback comentado que não está sendo usado
        )

    def local_expert(self):
        # Cria um agente que atua como especialista local na cidade selecionada
        # Este agente fornece insights detalhados sobre atrações, cultura e dicas locais
        return Agent(
            role='Local Expert at this city',
            goal='Provide the BEST insights about the selected city',
            backstory="""A knowledgeable local guide with extensive information
        about the city, it's attractions and customs""",
            tools=[
                SearchTools.search_internet,  # Ferramenta para buscar informações na internet
                BrowserTools.scrape_and_summarize_website,  # Ferramenta para coletar e resumir conteúdo de sites
            ],
            verbose=True,
            # step_callback=streamlit_callback,
        )

    def travel_concierge(self):
        # Cria um agente concierge de viagens que elabora itinerários detalhados
        # Este agente cria planos diários, sugestões de orçamento e lista de itens para levar
        return Agent(
            role='Amazing Travel Concierge',
            goal="""Create the most amazing travel itineraries with budget and 
        packing suggestions for the city""",
            backstory="""Specialist in travel planning and logistics with 
        decades of experience""",
            tools=[
                SearchTools.search_internet,  # Ferramenta para buscar informações na internet
                BrowserTools.scrape_and_summarize_website,  # Ferramenta para coletar e resumir conteúdo de sites
                CalculatorTools.calculate,  # Ferramenta para realizar cálculos (útil para orçamentos)
            ],
            verbose=True,
            # step_callback=streamlit_callback,
        )

###########################################################################################
# Exibe o processo dos agentes no container do Streamlit                                   #
# Esta parte do código é adaptada de @AbubakrChan; obrigado!                              #
# https://github.com/AbubakrChan/crewai-UI-business-product-launch/blob/main/main.py#L210 #
###########################################################################################
class StreamToExpander:
    def __init__(self, expander):
        # Inicializa a classe com o expansor do Streamlit onde o conteúdo será exibido
        self.expander = expander
        self.buffer = []  # Buffer para acumular dados antes de exibir
        self.colors = ['red', 'green', 'blue', 'orange']  # Define a lista de cores para diferenciar agentes
        self.color_index = 0  # Inicializa o índice de cores

    def write(self, data):
        # Método que processa e formata a saída dos agentes para exibição no Streamlit
        # Filtra os códigos de escape ANSI usando uma expressão regular para limpar o texto
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)

        # Verifica se os dados contêm informações de 'task' para exibir notificações toast
        task_match_object = re.search(r'\"task\"\s*:\s*\"(.*?)\"', cleaned_data, re.IGNORECASE)
        task_match_input = re.search(r'task\s*:\s*([^\n]*)', cleaned_data, re.IGNORECASE)
        task_value = None
        if task_match_object:
            task_value = task_match_object.group(1)
        elif task_match_input:
            task_value = task_match_input.group(1).strip()

        # Se encontrou um valor de tarefa, exibe como uma notificação toast
        if task_value:
            st.toast(":robot_face: " + task_value)

        # Identifica frases específicas e aplica formatação colorida para melhorar a legibilidade
        # Usado para destacar visualmente as etapas do processo de cada agente
        if "Entering new CrewAgentExecutor chain" in cleaned_data:
            # Alterna as cores para diferenciar os agentes e suas cadeias de execução
            self.color_index = (self.color_index + 1) % len(self.colors)
            cleaned_data = cleaned_data.replace("Entering new CrewAgentExecutor chain", f":{self.colors[self.color_index]}[Entering new CrewAgentExecutor chain]")

        # Aplica cores específicas para os nomes dos agentes para facilitar identificação visual
        if "City Selection Expert" in cleaned_data:
            cleaned_data = cleaned_data.replace("City Selection Expert", f":{self.colors[self.color_index]}[City Selection Expert]")
        if "Local Expert at this city" in cleaned_data:
            cleaned_data = cleaned_data.replace("Local Expert at this city", f":{self.colors[self.color_index]}[Local Expert at this city]")
        if "Amazing Travel Concierge" in cleaned_data:
            cleaned_data = cleaned_data.replace("Amazing Travel Concierge", f":{self.colors[self.color_index]}[Amazing Travel Concierge]")
        if "Finished chain." in cleaned_data:
            cleaned_data = cleaned_data.replace("Finished chain.", f":{self.colors[self.color_index]}[Finished chain.]")

        # Adiciona os dados processados ao buffer
        self.buffer.append(cleaned_data)
        # Quando encontra uma quebra de linha, exibe todo o conteúdo do buffer e limpa-o
        if "\n" in data:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer = []
