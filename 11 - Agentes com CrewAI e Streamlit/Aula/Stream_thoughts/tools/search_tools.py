import json

import requests
import streamlit as st
from langchain.tools import tool


class SearchTools():
  # Classe que fornece ferramentas para buscar informações na internet

  @tool("Search the internet")
  def search_internet(query):
    """Useful to search the internet
    about a a given topic and return relevant results"""
    # Ferramenta que realiza pesquisas na internet usando a API Serper (alternativa à API do Google)
    
    # Define o número máximo de resultados a serem retornados
    top_result_to_return = 4
    
    # Configura a URL do serviço de busca Serper
    url = "https://google.serper.dev/search"
    
    # Prepara a consulta em formato JSON
    payload = json.dumps({"q": query})
    
    # Configura os cabeçalhos HTTP com a chave de API armazenada nos segredos do Streamlit
    headers = {
        'X-API-KEY': st.secrets['SERPER_API_KEY'],
        'content-type': 'application/json'
    }
    
    # Envia a requisição POST para a API Serper com a consulta
    response = requests.request("POST", url, headers=headers, data=payload)
    
    # Verifica se a resposta contém a chave 'organic' (resultados orgânicos)
    # Se não tiver, retorna uma mensagem de erro
    if 'organic' not in response.json():
      return "Sorry, I couldn't find anything about that, there could be an error with you serper api key."
    else:
      # Extrai os resultados orgânicos da resposta
      results = response.json()['organic']
      
      # Lista para armazenar as informações formatadas dos resultados
      string = []
      
      # Processa os primeiros N resultados (conforme definido em top_result_to_return)
      for result in results[:top_result_to_return]:
        try:
          # Formata cada resultado com título, link e snippet, separados por uma linha divisória
          string.append('\n'.join([
              f"Title: {result['title']}", 
              f"Link: {result['link']}",
              f"Snippet: {result['snippet']}", 
              "\n-----------------"
          ]))
        except KeyError:
          # Ignora resultados que não possuem todos os campos necessários
          next

      # Retorna todos os resultados formatados como uma única string
      return '\n'.join(string)
