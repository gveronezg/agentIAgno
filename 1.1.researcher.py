from importENV import *
#######################
from agno.agent import Agent
from agno.tools.tavily import TavilyTools
from agno.models.groq import Groq

agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[TavilyTools()],
    debug_mode=True
)

agent.print_response("Use suas ferramentas para pesquisar a temperatura de hoje em Franca-SP.")