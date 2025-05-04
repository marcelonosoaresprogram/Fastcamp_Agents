import streamlit as st
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from openai import OpenAI
import tempfile
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env (incluindo OPENAI_API_KEY)
load_dotenv()

# Configura a página do Streamlit com título e layout
st.set_page_config(page_title="Assistente Médico com CrewAI", layout="centered")

# Inicializa as variáveis de estado da sessão para persistência entre recarregamentos
if 'anamnese_text' not in st.session_state:
    st.session_state['anamnese_text'] = ""  # Armazena a transcrição da anamnese
if 'analysis_result' not in st.session_state:
    st.session_state['analysis_result'] = ""  # Armazena o resultado da análise
if 'show_analysis' not in st.session_state:
    st.session_state['show_analysis'] = False  # Controla visualização dos resultados
if 'patient_name' not in st.session_state:
    st.session_state['patient_name'] = ""  # Nome do paciente
if 'patient_age' not in st.session_state:
    st.session_state['patient_age'] = ""  # Idade do paciente

# Inicializa os clientes da API OpenAI usando a API key do ambiente
try:
    # Cliente OpenAI para transcrição de áudio
    client = OpenAI()
    # Modelo de linguagem para os agentes
    llm = ChatOpenAI(temperature=0.7)
except Exception as e:
    st.error(f"❌ Erro ao configurar API: {e}")
    client = None
    llm = None

def transcribe_audio(audio_bytes):
    """
    Transcreve o áudio gravado para texto usando o modelo Whisper da OpenAI
    
    Args:
        audio_bytes: Bytes do áudio gravado
        
    Returns:
        String com o texto transcrito ou None em caso de erro
    """
    if not client:
        st.error("Cliente OpenAI não configurado. Verifique o arquivo .env.")
        return None
    
    # Cria um arquivo temporário para armazenar o áudio
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
        tmp_file.write(audio_bytes)
        tmp_file_path = tmp_file.name
    
    try:
        # Envia o áudio para transcrição via API da OpenAI
        with open(tmp_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        # Remove o arquivo temporário
        os.unlink(tmp_file_path)
        return transcript.text
    except Exception as e:
        st.error(f"Erro na transcrição: {e}")
        os.unlink(tmp_file_path)
        return None

def run_medical_crew(anamnese_text, patient_name, patient_age):
    """
    Executa o fluxo de trabalho dos agentes médicos usando CrewAI
    
    Args:
        anamnese_text: Texto da anamnese transcrita
        patient_name: Nome do paciente
        patient_age: Idade do paciente
        
    Returns:
        String com o resultado da análise dos agentes
    """
    if not llm:
        st.error("LLM não configurado. Verifique o arquivo .env.")
        return None
    
    # AGENTE 1: Especialista em organizar e estruturar informações da anamnese
    anamnese_organizer = Agent(
        role="Especialista em Anamnese Médica",
        goal="Organizar e estruturar informações da anamnese do paciente",
        backstory="Médico com vasta experiência em coleta e organização de informações de pacientes para facilitar diagnósticos precisos.",
        llm=llm,
        verbose=True
    )
    
    # AGENTE 2: Especialista em diagnóstico e recomendações de tratamento
    diagnostician = Agent(
        role="Especialista em Diagnóstico Médico",
        goal="Analisar sintomas, sugerir possíveis diagnósticos, exames e medicações",
        backstory="Médico especialista com amplo conhecimento em diferentes patologias, métodos diagnósticos e abordagens terapêuticas.",
        llm=llm,
        verbose=True
    )
    
    # TAREFA 1: Organizar as informações da anamnese em estrutura adequada
    organize_task = Task(
        description=f"""
        Com base na anamnese gravada pelo paciente {patient_name}, {patient_age} anos:
        "{anamnese_text}"
        
        1. Organize as informações nos seguintes tópicos:
           - Queixa principal
           - Sintomas relatados
           - Duração dos sintomas
           - Fatores de agravamento ou alívio
           - Histórico médico relevante (se mencionado)
        
        2. Identifique informações importantes que possam estar faltando
        3. Utilize apenas as informações disponíveis e faça o melhor possível com elas
        
        Estruture sua resposta de forma clara e objetiva.
        """,
        agent=anamnese_organizer,
        expected_output="Anamnese organizada por tópicos e observações importantes."
    )
    
    # TAREFA 2: Analisar os sintomas e sugerir diagnósticos e tratamentos
    diagnosis_task = Task(
        description="""
        Com base na anamnese organizada:
        
        1. Liste os principais sintomas identificados
        2. Sugira 2-3 possíveis diagnósticos em ordem de probabilidade, com breve justificativa
        3. Recomende exames específicos que ajudariam a confirmar os diagnósticos sugeridos
        4. Proponha uma abordagem terapêutica inicial adequada, incluindo medicamentos se apropriado
        
        Lembre-se de incluir um aviso sobre a importância de consultar um médico presencialmente.
        """,
        agent=diagnostician,
        expected_output="Análise dos sintomas, possíveis diagnósticos, recomendações de exames e tratamento."
    )
    
    # Configura e executa o fluxo de trabalho da crew
    crew = Crew(
        agents=[anamnese_organizer, diagnostician],
        tasks=[organize_task, diagnosis_task],
        verbose=True,
        process=Process.sequential  # Executa as tarefas em sequência, uma após a outra
    )
    
    # Executa o fluxo e retorna o resultado
    result = crew.kickoff()
    return str(result)

# ---------- INTERFACE DO USUÁRIO ---------- #

# Título e descrição da aplicação
st.title("🏥 Assistente Médico Digital")
st.write("Registre a anamnese do paciente via áudio e receba uma análise médica")

# Formulário para entrada de dados do paciente
col1, col2 = st.columns(2)

with col1:
    # Campo para nome do paciente
    patient_name = st.text_input("Nome do paciente:", value=st.session_state['patient_name'])
    if patient_name != st.session_state['patient_name']:
        st.session_state['patient_name'] = patient_name

with col2:
    # Campo para idade do paciente
    patient_age = st.text_input("Idade do paciente:", value=st.session_state['patient_age'])
    if patient_age != st.session_state['patient_age']:
        st.session_state['patient_age'] = patient_age

# Seção para gravação da anamnese
st.subheader("Anamnese")
st.write("Grave o relato dos sintomas e histórico médico relevante:")

# Componente de gravação de áudio do Streamlit
audio_input = st.audio_input("Gravar anamnese", key="audio_recorder")

# Se um áudio foi gravado, exibe-o e oferece opção para transcrição
if audio_input:
    st.audio(audio_input)
    if st.button("✅ Transcrever Áudio"):
        with st.spinner("Transcrevendo áudio..."):
            transcription = transcribe_audio(audio_input.getvalue())
            if transcription:
                st.session_state['anamnese_text'] = transcription
                st.success("Transcrição concluída!")
                st.write(f"**Texto transcrito:**\n{transcription}")

# Botão para iniciar análise (ativo apenas quando todos os dados necessários estão presentes)
if st.session_state['anamnese_text'] and st.session_state['patient_name'] and st.session_state['patient_age']:
    if st.button("🔍 Analisar Anamnese"):
        with st.spinner("Processando anamnese e gerando recomendações médicas..."):
            try:
                # Executa a análise com os agentes do CrewAI
                result = run_medical_crew(
                    st.session_state['anamnese_text'], 
                    st.session_state['patient_name'],
                    st.session_state['patient_age']
                )
                
                if result:
                    # Armazena e exibe o resultado
                    st.session_state['analysis_result'] = result
                    st.session_state['show_analysis'] = True
                    st.rerun()  # Atualiza a página para mostrar os resultados
            except Exception as e:
                st.error(f"Erro ao processar anamnese: {e}")

# Exibe os resultados da análise médica
if st.session_state['show_analysis'] and st.session_state['analysis_result']:
    st.subheader("🩺 Análise Médica")
    st.markdown(st.session_state['analysis_result'])
    st.warning("⚠️ Este é um assistente educacional e não substitui a consulta com um profissional de saúde real.")
    
    # Botão para iniciar uma nova consulta
    if st.button("🔄 Nova Consulta"):
        # Limpa os dados da consulta atual
        st.session_state['anamnese_text'] = ""
        st.session_state['analysis_result'] = ""
        st.session_state['show_analysis'] = False
        st.rerun()  # Atualiza a página para iniciar uma nova consulta
