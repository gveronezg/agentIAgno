from importENV import *
#######################
from agno.agent import Agent
from agno.tools.tavily import TavilyTools
from agno.models.openai import OpenAIChat
#######################
from agno.tools import tool # Decorator para definir custom tools
import re

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

agent = Agent(
    model=OpenAIChat(id="gpt-5-nano"),
    tools=[
        TavilyTools(),
        celsius_to_fahrenheit,
    ],
    debug_mode=True
)

agent.print_response("Use suas ferramentas para pesquisar a temperatura de hoje em Franca-SP em Fahrenheit.")