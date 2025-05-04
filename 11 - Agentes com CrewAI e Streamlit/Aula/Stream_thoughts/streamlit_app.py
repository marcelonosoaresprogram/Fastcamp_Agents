from crewai import Crew
from trip_agents import TripAgents, StreamToExpander
from trip_tasks import TripTasks
import streamlit as st
import datetime
import sys

# Configuração da página Streamlit com ícone de avião e layout amplo
st.set_page_config(page_icon="✈️", layout="wide")


def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    # Função para exibir um emoji como ícone de página no estilo Notion com tamanho personalizado
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )


class TripCrew:
    # Classe principal que orquestra todo o processo de planejamento de viagem usando agentes de IA

    def __init__(self, origin, cities, date_range, interests):
        # Inicializa a classe com as informações fornecidas pelo usuário
        # Armazena origem, destinos, intervalo de datas e interesses do usuário
        self.cities = cities
        self.origin = origin
        self.interests = interests.venv
        self.date_range = date_range
        self.output_placeholder = st.empty()

    def run(self):
        # Método principal que executa todo o fluxo de planejamento da viagem
        # Cria instâncias dos agentes e tarefas necessárias
        agents = TripAgents()
        tasks = TripTasks()

        # Inicializa os três agentes especializados que trabalharão no planejamento
        city_selector_agent = agents.city_selection_agent()  # Agente para selecionar a melhor cidade
        local_expert_agent = agents.local_expert()  # Agente especialista local na cidade selecionada
        travel_concierge_agent = agents.travel_concierge()  # Agente concierge que cria o itinerário detalhado

        # Cria as tarefas específicas para cada agente, passando os parâmetros necessários
        identify_task = tasks.identify_task(
            city_selector_agent,
            self.origin,
            self.cities,
            self.interests,
            self.date_range
        )

        gather_task = tasks.gather_task(
            local_expert_agent,
            self.origin,
            self.interests,
            self.date_range
        )

        plan_task = tasks.plan_task(
            travel_concierge_agent,
            self.origin,
            self.interests,
            self.date_range
        )

        crew = Crew(
            agents=[
                city_selector_agent, local_expert_agent, travel_concierge_agent
            ],
            tasks=[identify_task, gather_task, plan_task],
            verbose=True
        )

        result = crew.kickoff()
        self.output_placeholder.markdown(result)

        return result


if __name__ == "__main__":
    icon("🏖️ VacAIgent")

    st.subheader("Let AI agents plan your next vacation!",
                 divider="rainbow", anchor=False)

    import datetime

    today = datetime.datetime.now().date()
    next_year = today.year + 1
    jan_16_next_year = datetime.date(next_year, 1, 10)

    with st.sidebar:
        st.header("👇 Enter your trip details")
        with st.form("my_form"):
            location = st.text_input(
                "Where are you currently located?", placeholder="San Mateo, CA")
            cities = st.text_input(
                "City and country are you interested in vacationing at?", placeholder="Bali, Indonesia")
            date_range = st.date_input(
                "Date range you are interested in traveling?",
                # Define o intervalo de datas para a viagem com valor padrão de uma semana a partir da data atual até o próximo ano
                value=(today, jan_16_next_year + datetime.timedelta(days=6)),
                format="MM/DD/YYYY",
            )
            # Campo de entrada para os interesses e hobbies do usuário, que serão usados para personalizar as recomendações
            interests = st.text_area("High level interests and hobbies or extra details about your trip?",
                                     placeholder="2 adults who love swimming, dancing, hiking, and eating")

            # Botão para enviar o formulário e iniciar o processamento dos agentes
            submitted = st.form_submit_button("Submit")

        # Adiciona uma linha divisória na barra lateral
        st.divider()

        # Seção de créditos para o criador do framework CrewAI
        # Mostra uma referência ao autor original do código e criador da biblioteca
        st.sidebar.markdown(
        """
        Credits to [**@joaomdmoura**](https://twitter.com/joaomdmoura)
        for creating **crewAI** 🚀
        """,
            unsafe_allow_html=True
        )

        # Mensagem informativa com ícone indicando onde clicar para acessar o repositório
        st.sidebar.info("Click the logo to visit GitHub repo", icon="👇")
        
        # Link para o repositório GitHub do projeto CrewAI com logo
        st.sidebar.markdown(
            """
        <a href="https://github.com/joaomdmoura/crewAI" target="_blank">
            <img src="https://raw.githubusercontent.com/joaomdmoura/crewAI/main/docs/crewai_logo.png" alt="CrewAI Logo" style="width:100px;"/>
        </a>
        """,
            unsafe_allow_html=True
        )


# Bloco condicional que executa quando o formulário é enviado
if submitted:
    # Cria um componente de status que mostra o progresso dos agentes trabalhando
    with st.status("🤖 **Agents at work...**", state="running", expanded=True) as status:
        # Cria um container com altura fixa para mostrar o processo dos agentes em tempo real
        with st.container(height=500, border=False):
            # Redireciona a saída padrão (stdout) para o componente StreamToExpander
            # que formata e mostra o progresso dos agentes na interface
            sys.stdout = StreamToExpander(st)
            trip_crew = TripCrew(location, cities, date_range, interests)
            result = trip_crew.run()
        status.update(label="✅ Trip Plan Ready!",
                      state="complete", expanded=False)

    st.subheader("Here is your Trip Plan", anchor=False, divider="rainbow")
    st.markdown(result)
