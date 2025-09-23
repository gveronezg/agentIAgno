from importENV import *  # Importa variáveis de ambiente, tokens e chaves
import os, glob, duckdb # Banco de dados relacional usado para armazenar os dados em formato de tabelas (CSV, Parquet, etc.)
from pathlib import Path
#######################
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage
from agno.playground import Playground, serve_playground_app
from agno.tools import tool
#######################
from agno.vectordb.chroma import ChromaDb # Banco vetorial (ChromaDB) usado para armazenar os dados em formato de vetores (embeddings) para busca semântica.

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

# --- Função utilitária para converter CSVs para Parquet ---
def csv_para_parquet(src_folder, dest_folder, encoding=None):
    os.makedirs(dest_folder, exist_ok=True)
    
    for arquivo in glob.glob(os.path.join(src_folder, "*.csv")):
        arquivo_path = Path(arquivo).resolve().as_posix()
        base = Path(arquivo).stem + ".parquet"
        destino = Path(dest_folder).resolve() / base

        if encoding:
            con.execute(f"""
                CREATE OR REPLACE TEMPORARY TABLE tmp_csv AS
                SELECT * FROM read_csv_auto('{arquivo_path}', header=True, encoding='{encoding}');
            """)
        else:
            con.execute(f"""
                CREATE OR REPLACE TEMPORARY TABLE tmp_csv AS
                SELECT * FROM read_csv_auto('{arquivo_path}', header=True);
            """)

        con.execute(f"""
            COPY tmp_csv TO '{destino.as_posix()}' (FORMAT PARQUET);
        """)

# --- Converter CSVs principais para Parquet ---
csv_para_parquet("dados/saidas", "tmp/parquet/saidas")
csv_para_parquet("dados/devolucoes", "tmp/parquet/devolucoes")
csv_para_parquet("dados/ajustes", "tmp/parquet/ajustes")

# --- Cancelamentos ISO-8859-1 para Parquet ---
csv_para_parquet("dados/cancelamentos", "tmp/parquet/cancelamentos", encoding="CP1252")

# --- Criar tabelas DuckDB a partir dos arquivos Parquet ---
con.execute("CREATE OR REPLACE TABLE saidas AS SELECT * FROM 'tmp/parquet/saidas/*.parquet'")
con.execute("CREATE OR REPLACE TABLE devolucoes AS SELECT * FROM 'tmp/parquet/devolucoes/*.parquet'")
con.execute("CREATE OR REPLACE TABLE ajustes AS SELECT * FROM 'tmp/parquet/ajustes/*.parquet'")
con.execute("CREATE OR REPLACE TABLE cancelamentos AS SELECT * FROM 'tmp/parquet/cancelamentos/*.parquet'")

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
    knowledge=None,     # CSVKnowledgeBase removido
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