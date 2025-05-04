# Importação das bibliotecas necessárias
import requests  # Para fazer requisições HTTP
import json      # Para manipulação de dados JSON

# URL da API de pesquisa de candidatos
url = 'http://127.0.0.1/research_candidates'

# Cabeçalhos para a requisição HTTP
headers = {
    'accept': 'application/json',     # Especifica que aceita respostas em formato JSON
    'Content-Type': 'application/json', # Especifica que o corpo da requisição é JSON
}

# Dados de exemplo para pesquisa de candidatos
# Esta é a entrada para o endpoint da API que será processada pelo agente de IA
data = {
    'job_requirements': 'Data Engineer & Data Architect - Databricks Professional Certified - brasileiro que resida em Boituva.'
}

# Faz uma requisição POST para a API com os dados e cabeçalhos definidos
response = requests.post(url, headers=headers, json=data)

# Exibe o código de status da resposta HTTP
print(f"Status Code: {response.status_code}")

# Exibe a resposta formatada em JSON com indentação e suporte a caracteres especiais
print("Response JSON:")
print(json.dumps(response.json(), indent=4, ensure_ascii=False))

