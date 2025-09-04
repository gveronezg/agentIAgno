from importENV import *
#######################
from agno.agent import Agent
from agno.tools.tavily import TavilyTools
from agno.models.openai import OpenAIChat
from agno.playground import Playground, serve_playground_app
from agno.tools import tool # Decorator para definir custom tools
import re
#######################
from agno.storage.sqlite import SqliteStorage

# Define a custom tool to convert Celsius to Fahrenheit
@tool
def celsius_to_fahrenheit(temperatura_celsius: str) -> float:
    """
    Converte temperatura de Celsius para Fahrenheit.
    Aceita string como '28', '28°C' ou 'temperatura é 28 graus'.
    Args:
        temperatura_celsius (float): Temperatura em graus Celsius.
    Returns:
        float: Temperatura convertida em graus Fahrenheit.
    """
    # Extrai número da string
    match = re.search(r"[-+]?\d*\.\d+|\d+", str(temperatura_celsius))
    # Se não encontrar número, levanta erro
    if not match:
        raise ValueError(f"Não consegui interpretar a temperatura: {temperatura_celsius}")
    # Converte para float e aplica fórmula
    celsius = float(match.group())
    return (celsius * 9/5) + 32

db = SqliteStorage(table_name="agent_session", db_file="tmp/agent.db") # Armazena o histórico das sessões em SQLite

agent = Agent(
    name="Agente do Tempo",
    model=OpenAIChat(id="gpt-5-nano"),
    tools=[
        TavilyTools(),
        celsius_to_fahrenheit,
    ],
    storage=db,
    add_history_to_messages=True, # Adiciona histórico de mensagens ao prompt
    num_history_runs=3, # Numero de interações anteriores a considerar
    debug_mode=True
)

app = Playground(agents=[
    agent
]).get_app()

if __name__ == "__main__":
    serve_playground_app("1_4_onPlayground:app", reload=True)