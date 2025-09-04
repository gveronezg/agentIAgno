from importENV import * # Importa variáveis de ambiente, tokens e chaves que você definiu no arquivo importENV.py
import os # Módulo nativo do Python para manipulação de arquivos, diretórios e variáveis de ambiente.
#######################
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage
from agno.playground import Playground, serve_playground_app
#######################
from agno.knowledge.csv import CSVKnowledgeBase, CSVReader
from agno.vectordb.chroma import ChromaDb

# --- Garantir diretório de persistência ---
os.makedirs("tmp/chromadb", exist_ok=True)

# --- Configuração do Chroma local ---
db_path = os.path.join(os.getcwd(), "tmp", "chromadb")
vector_db = ChromaDb(
    collection="csv_agent",
    path=db_path
)

# --- Base de conhecimento com múltiplos CSVs ---
knowledge = CSVKnowledgeBase(
    path="dados/",  # lê TODOS os arquivos .csv da pasta
    vector_db=vector_db,
    reader=CSVReader()
)

# --- Banco de sessões ---
db = SqliteStorage(table_name="agent_session", db_file="tmp/agent.db")

# --- Definição do agente ---
agent = Agent(
    name="Agente de CSVs",
    model=OpenAIChat(id="gpt-5-nano"),
    storage=db,
    knowledge=knowledge,
    add_history_to_messages=True, # Adiciona histórico de mensagens ao prompt
    num_history_runs=3, # Numero de interações anteriores a considerar
    debug_mode=True,
    instructions=(
        "Você é um agente que responde **exclusivamente com base nos CSV fornecidos**. "
        "Sempre use a knowledge base para buscar informações antes de responder. "
        "Se a informação não estiver no CSV, responda apenas: "
        "'Não encontrei essa informação nos arquivos.'"
    )
)

# --- Playground ---
app = Playground(agents=[agent]).get_app() # Cria a aplicação web que permite interagir com o agente e retorna o objeto FastAPI que será servido pelo Uvicorn.

# --- Inicializar servidor ---
if __name__ == "__main__": # Garante que esse bloco só execute quando o script for chamado diretamente (não quando importado).
    # --- Carregar a base logo na importação ---
    knowledge.load() # Carrega o PDF e popula o banco vetorial (ChromaDB)
    serve_playground_app("21_pdf_agent:app") # Inicia o servidor web (Uvicorn) e aponta para o app FastAPI criado acima.