from importENV import *  # Importa variáveis de ambiente, tokens e chaves
import os
import duckdb
#######################
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage
from agno.playground import Playground, serve_playground_app
from agno.tools import tool
#######################
from agno.vectordb.chroma import ChromaDb

# --- Garantir diretórios ---
os.makedirs("tmp/chromadb", exist_ok=True)
os.makedirs("tmp", exist_ok=True)

# --- Configuração do Chroma local (VectorDB) ---
db_path = os.path.join(os.getcwd(), "tmp", "chromadb")
vector_db = ChromaDb(
    collection="csv_agent",
    path=db_path
)

# --- Configuração do DuckDB ---
duckdb_path = os.path.join("tmp", "datawarehouse.duckdb")
con = duckdb.connect(duckdb_path)

# Carregar tabelas (aqui CSV → mas em produção ideal é Parquet)
con.execute("CREATE OR REPLACE TABLE saidas AS SELECT * FROM read_csv_auto('dados/saidas/*.csv')")
con.execute("CREATE OR REPLACE TABLE devolucoes AS SELECT * FROM read_csv_auto('dados/devolucoes/*.csv')")
con.execute("CREATE OR REPLACE TABLE ajustes AS SELECT * FROM read_csv_auto('dados/ajustes/*.csv')")

# Arquivos ISO-8859-1 - cancelar, ler com pandas e importar para duckdb
import glob
import pandas as pd
caminhos_cancelamentos = glob.glob('dados/cancelamentos/*.csv')
df_cancelamentos = pd.concat(
    [pd.read_csv(arquivo, encoding='ISO-8859-1', sep=';') for arquivo in caminhos_cancelamentos],
    ignore_index=True
)
con.execute("CREATE OR REPLACE TABLE cancelamentos AS SELECT * FROM df_cancelamentos")

# --- Tool para consultas SQL ---
@tool
def run_query(query: str):
    """
    Executa consultas SQL no DuckDB.
    """
    try:
        result = con.execute(query).df()
        return result.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

# --- Banco de sessões ---
db = SqliteStorage(table_name="agent_session", db_file="tmp/agent.db")

# --- Definição do agente ---
agent = Agent(
    name="Agente de Dados",
    model=OpenAIChat(id="gpt-5-nano"),
    storage=db,
    tools=[run_query],  # adiciona a ferramenta SQL
    knowledge=None,     # removemos CSVKnowledgeBase
    add_history_to_messages=True,
    num_history_runs=3,
    debug_mode=True,
    instructions=(
        "Você é um agente que responde com base nos dados armazenados. "
        "Sempre use a ferramenta `run_query` para consultar os dados em DuckDB. "
        "Para buscas de similaridade ou semânticas, utilize o banco vetorial. "
        "Se a informação não estiver nos dados, responda apenas: "
        "'Não encontrei essa informação nos arquivos.'"
    )
)

# --- Playground ---
app = Playground(agents=[agent]).get_app()

# --- Inicializar servidor ---
if __name__ == "__main__":
    # (Opcional) Pré-processar vetorização e popular VectorDB aqui
    serve_playground_app("31_15set:app")