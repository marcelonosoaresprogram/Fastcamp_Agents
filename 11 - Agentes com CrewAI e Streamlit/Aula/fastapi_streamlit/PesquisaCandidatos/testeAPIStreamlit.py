# Importação das bibliotecas necessárias
import streamlit as st    # Framework para criação de aplicações web
import requests           # Para fazer requisições HTTP
import time               # Para medir o tempo de execução das operações
from sendmail import send_email  # Função personalizada para envio de e-mails

# Função que realiza a chamada à API de pesquisa de candidatos
def search_jobs(requirements):
    # URL da API
    url = 'http://127.0.0.1/research_candidates'
    
    # Cabeçalhos para a requisição HTTP
    headers = {
        'accept': 'application/json',        # Especifica que aceita respostas em formato JSON
        'Content-Type': 'application/json',  # Especifica que o corpo da requisição é JSON
    }
    
    # Preparação dos dados para a requisição
    data = {
        'job_requirements': f'{requirements}'  # Requisitos da vaga fornecidos pelo usuário
    }

    # Execução da chamada à API
    response = requests.post(url, headers=headers, json=data)
    
    # Verifica se a requisição foi bem-sucedida (código 200)
    if response.status_code == 200:
        return response.json()  # Retorna os dados da resposta em formato JSON
    else:
        return None  # Retorna None em caso de falha

def main():
    # Interface Streamlit - Título da página
    st.title('Pesquisa de Jobs')
    
    # Campo de texto para entrada dos requisitos da vaga
    requirements = st.text_input("Digite os requisitos do job:")
    
    # Inicialização das variáveis de estado para controlar os botões
    if 'button1_clicked' not in st.session_state:
        st.session_state.button1_clicked = False
    if 'button2_clicked' not in st.session_state:
        st.session_state.button2_clicked = False

    # Botão para iniciar a busca de candidatos
    if st.button('Buscar'):
        st.session_state.button1_clicked = True
        st.session_state.button2_clicked = False

    # Lógica executada quando o botão de busca é clicado
    if st.session_state.button1_clicked:
        # Inicia a medição do tempo de execução
        start_time = time.time()
        
        # Exibe um indicador de carregamento (spinner)
        with st.spinner('Buscando os melhores candidatos...'):
            # Exibe uma animação enquanto aguarda a resposta da API
            gif_path = "loading.gif"
            gif_placeholder = st.empty()
            gif_placeholder.image(gif_path)

            # Chama a função para buscar candidatos
            results = search_jobs(requirements)
            
            # Finaliza a medição do tempo de execução
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # Processa e exibe os resultados
            if results:
                # Remove a animação de carregamento
                gif_placeholder.empty()
                
                # Exibe uma mensagem de sucesso
                st.markdown("<h3 style='color:green;'>Busca Finalizada!</h1>", unsafe_allow_html=True)
                
                # Exibe os candidatos encontrados
                st.write('Top 5 Candidatos:')
                st.write(f"{results['result']['raw']}")
                
                # Exibe informações sobre o uso de tokens e desempenho
                st.write(f"Tokens Usados: {results['result']['token_usage']['total_tokens']}")
                st.write(f"Total de requisições: {results['result']['token_usage']['successful_requests']}")
                st.write(f"Tempo de execução: {elapsed_time:.2f} segundos")
            else:
                # Exibe uma mensagem de erro caso a busca falhe
                st.error("Não foi possível obter resultados.")
    
    # Campo para inserir o e-mail do destinatário
    email_input = st.text_input("Digite o e-mail do destinatário:", key="email")
    
    # Botão para enviar os resultados por e-mail
    if st.button('Enviar E-mail'):
        st.session_state.button2_clicked = True
        st.session_state.button1_clicked = False

    # Lógica executada quando o botão de envio de e-mail é clicado
    if st.session_state.button2_clicked:
        if email_input:
            # Chama a função para enviar o e-mail com os resultados
            send_email(email_input, results['result']['raw'])
            
            # Exibe uma mensagem de confirmação
            st.markdown("<h3 style='color:green;'>E-mail enviado!</h1>", unsafe_allow_html=True)

# Ponto de entrada para execução direta do script
if __name__ == "__main__":
    main()