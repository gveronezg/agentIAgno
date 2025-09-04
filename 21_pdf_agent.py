from importENV import * # Importa variáveis de ambiente, tokens e chaves que você definiu no arquivo importENV.py
import os # Módulo nativo do Python para manipulação de arquivos, diretórios e variáveis de ambiente.
#######################
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage
from agno.playground import Playground, serve_playground_app
#######################
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.vectordb.chroma import ChromaDb

# --- Garantir diretório de persistência ---
os.makedirs("tmp/chromadb", exist_ok=True)

# --- Configuração do Vector DB ---
db_path = os.path.join(os.getcwd(), "tmp", "chromadb") # Gera o caminho absoluto para o banco Chroma (evita problemas no Windows).
vector_db = ChromaDb(
    collection="pdf_agent",
    path=db_path,   # Local físico onde o Chroma armazenará os arquivos (SQLite + índices).
)

# --- Configuração da Knowledge Base ---
knowledge = PDFKnowledgeBase(
    path="doc.pdf", # Arquivo PDF que será lido
    vector_db=vector_db,    # Banco vetorial (ChromaDB)
    reader=PDFReader(chunk=True),   # Le e processa o PDF em partes
)

# --- Banco de sessões ---
db = SqliteStorage(table_name="agent_session", db_file="tmp/agent.db")

# --- Definição do agente ---
agent = Agent(
    name="Agente de PDFs",
    model=OpenAIChat(id="gpt-5-nano"),
    storage=db,
    knowledge=knowledge,
    add_history_to_messages=True, # Adiciona histórico de mensagens ao prompt
    num_history_runs=3, # Numero de interações anteriores a considerar
    debug_mode=True,
    instructions=(
        "Você é um agente que responde **exclusivamente com base no PDF fornecido**. "
        "Sempre use a knowledge base para buscar informações antes de responder. "
        "Se a informação não estiver no PDF, responda apenas: "
        "'Não encontrei essa informação no documento.'"
    )
)

# --- Playground ---
app = Playground(agents=[agent]).get_app() # Cria a aplicação web que permite interagir com o agente e retorna o objeto FastAPI que será servido pelo Uvicorn.

# --- Inicializar servidor ---
if __name__ == "__main__": # Garante que esse bloco só execute quando o script for chamado diretamente (não quando importado).
    # --- Carregar a base logo na importação ---
    knowledge.load() # Carrega o PDF e popula o banco vetorial (ChromaDB)
    print(f"Base de conhecimento carregada em: {db_path}") # Informa onde o ChromaDB está armazenado.
    serve_playground_app("21_pdf_agent:app") # Inicia o servidor web (Uvicorn) e aponta para o app FastAPI criado acima.