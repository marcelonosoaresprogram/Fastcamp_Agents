# Define a imagem base do Python 3.12.4
FROM python:3.12.4

# Define o diretório de trabalho no container
WORKDIR /code

# Copia o arquivo de requisitos para o diretório de trabalho
COPY ./requirements.txt /code/requirements.txt

# Instala as dependências do projeto
# --no-cache-dir: não mantém o cache dos pacotes para reduzir o tamanho da imagem
# --upgrade: garante que sejam instaladas as versões mais recentes
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copia a pasta 'app' para o diretório de trabalho do container
COPY ./app /code/app

# Define o comando que será executado quando o container iniciar
# Inicia a aplicação FastAPI na porta 80
CMD ["fastapi", "run", "app/main.py", "--port", "80"]