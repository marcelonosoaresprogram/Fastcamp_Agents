import json

import requests
import streamlit as st
from crewai import Agent, Task
from langchain.tools import tool
from unstructured.partition.html import partition_html


class BrowserTools():
  # Classe que fornece ferramentas para navegação e coleta de informações da web

  @tool("Scrape website content")
  def scrape_and_summarize_website(website):
    """Useful to scrape and summarize a website content"""
    # Ferramenta que coleta e resume o conteúdo de um site usando o serviço Browserless
    
    # Configura a URL do serviço Browserless com a chave de API armazenada nos segredos do Streamlit
    url = f"https://chrome.browserless.io/content?token={st.secrets['BROWSERLESS_API_KEY']}"
    
    # Prepara os dados para a requisição, especificando o site a ser visitado
    payload = json.dumps({"url": website})
    
    # Configura os cabeçalhos HTTP, desabilitando cache e definindo o tipo de conteúdo
    headers = {'cache-control': 'no-cache', 'content-type': 'application/json'}
    
    # Envia a requisição POST para o serviço Browserless para obter o conteúdo HTML do site
    response = requests.request("POST", url, headers=headers, data=payload)
    
    # Processa o HTML recebido usando a biblioteca unstructured para dividir em elementos
    elements = partition_html(text=response.text)
    
    # Concatena os elementos em um texto único com separadores de parágrafo
    content = "\n\n".join([str(el) for el in elements])
    
    # Divide o conteúdo em chunks de 8000 caracteres para processamento em partes
    content = [content[i:i + 8000] for i in range(0, len(content), 8000)]
    
    # Lista para armazenar os resumos de cada parte do conteúdo
    summaries = []
    
    # Para cada parte do conteúdo, cria um agente temporário para resumir
    for chunk in content:
      # Cria um agente especializado em pesquisa para resumir o conteúdo
      agent = Agent(
          role='Principal Researcher',
          goal=
          'Do amazing researches and summaries based on the content you are working with',
          backstory=
          "You're a Principal Researcher at a big company and you need to do a research about a given topic.",
          allow_delegation=False)
          
      # Cria uma tarefa para o agente analisar e resumir o conteúdo do chunk atual
      task = Task(
          agent=agent,
          description=
          f'Analyze and summarize the content bellow, make sure to include the most relevant information in the summary, return only the summary nothing else.\n\nCONTENT\n----------\n{chunk}'
      )
      
      # Executa a tarefa de resumo e armazena o resultado na lista de resumos
      summary = task.execute()
      summaries.append(summary)
      
    # Retorna todos os resumos combinados, separados por linhas em branco
    return "\n\n".join(summaries)
