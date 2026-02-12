import os, logging, glob, duckdb
from pathlib import Path
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage
from agno.playground import Playground, serve_playground_app
from agno.tools import tool
from dotenv import load_dotenv
load_dotenv()

# ----------------------------------------
# CONFIGURAÇÃO DE LOG
# ----------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------------------------
# GARANTIR DIRETÓRIOS TEMPORÁRIOS
# ----------------------------------------
# 'tmp' será usada para armazenar:
# - o banco DuckDB
# - os arquivos Parquet gerados temporariamente
os.makedirs("tmp", exist_ok=True)

# ----------------------------------------
# CONEXÃO COM DUCKDB
# ----------------------------------------
# Cria ou abre o banco de dados DuckDB no diretório tmp
duckdb_path = os.path.join("tmp", "datawarehouse.duckdb")
con = duckdb.connect(duckdb_path)
logger.info(f"DuckDB conectado em: {duckdb_path}")

# ----------------------------------------
# FUNÇÃO UTILITÁRIA: CSV → PARQUET
# ----------------------------------------
def csv_para_parquet(src_folder, dest_folder, encoding=None):
    """
    Lê todos os arquivos CSV de uma pasta, cria tabelas temporárias no DuckDB
    e salva cada CSV como arquivo Parquet no destino.
    """
    # Garantir que a pasta de destino exista
    os.makedirs(dest_folder, exist_ok=True)
    
    # Itera sobre todos os CSVs na pasta de origem
    for arquivo in glob.glob(os.path.join(src_folder, "*.csv")):
        arquivo_path = Path(arquivo).resolve().as_posix()  # Caminho absoluto
        base = Path(arquivo).stem + ".parquet"            # Nome do arquivo Parquet
        destino = Path(dest_folder).resolve() / base      # Caminho completo do Parquet

        # Criar tabela temporária no DuckDB lendo o CSV
        if encoding:
            # Caso precise de encoding especial (ex: CP1252)
            con.execute(f"""
                CREATE OR REPLACE TEMPORARY TABLE tmp_csv AS
                SELECT * FROM read_csv_auto('{arquivo_path}', header=True, encoding='{encoding}');
            """)
        else:
            # Encoding padrão
            con.execute(f"""
                CREATE OR REPLACE TEMPORARY TABLE tmp_csv AS
                SELECT * FROM read_csv_auto('{arquivo_path}', header=True);
            """)

        # Salvar o CSV convertido em Parquet
        con.execute(f"""
            COPY tmp_csv TO '{destino.as_posix()}' (FORMAT PARQUET);
        """)
        logger.info(f"Convertido para Parquet: {destino}")

    # Limpar a tabela temporária para não poluir a sessão DuckDB
    con.execute("DROP TABLE IF EXISTS tmp_csv")

# ----------------------------------------
# CONVERSÃO DE CSVs PARA PARQUET
# ----------------------------------------
# Cada conjunto de dados vai para sua pasta própria no tmp/parquet
csv_para_parquet("dados/tratados/ajustes", "tmp/parquet/ajustes")
csv_para_parquet("dados/tratados/saidas", "tmp/parquet/saidas")
csv_para_parquet("dados/tratados/devolucoes", "tmp/parquet/devolucoes")
csv_para_parquet("dados/tratados/cancelamentos", "tmp/parquet/cancelamentos")

# ----------------------------------------
# CRIAR TABELAS NO DUCKDB A PARTIR DOS PARQUET
# ----------------------------------------
# Cada tabela será permanente dentro do DuckDB
# e terá o mesmo nome do conjunto de dados
con.execute("""
    CREATE OR REPLACE TABLE ajustes AS 
    SELECT * FROM 'tmp/parquet/ajustes/*.parquet'
""")
logger.info("Tabela 'ajustes' criada com sucesso.")

con.execute("""
    CREATE OR REPLACE TABLE saidas AS 
    SELECT * FROM 'tmp/parquet/saidas/*.parquet'
""")
logger.info("Tabela 'saidas' criada com sucesso.")

con.execute("""
    CREATE OR REPLACE TABLE devolucoes AS 
    SELECT * FROM 'tmp/parquet/devolucoes/*.parquet'
""")
logger.info("Tabela 'devolucoes' criada com sucesso.")

con.execute("""
    CREATE OR REPLACE TABLE cancelamentos AS 
    SELECT * FROM 'tmp/parquet/cancelamentos/*.parquet'
""")
logger.info("Tabela 'cancelamentos' criada com sucesso.")

# ----------------------------------------
# VALIDAÇÃO (OPCIONAL)
# ----------------------------------------
# Podemos listar as tabelas e conferir as colunas
tabelas = con.execute("SHOW TABLES").fetchall()
logger.info(f"Tabelas disponíveis no DuckDB: {tabelas}")

for tabela in tabelas:
    nome = tabela[0]
    colunas = con.execute(f"DESCRIBE {nome}").fetchdf()
    logger.info(f"Colunas da tabela '{nome}':\n{colunas}")

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
    name="Agente de Dados da Oscar",
    model=OpenAIChat(id="gpt-5-nano"),
    storage=db,
    tools=[run_query],
    knowledge=None,
    add_history_to_messages=True,
    num_history_runs=3,
    debug_mode=True,
    instructions=(
        "Você é um agente que responde com base nos dados armazenados. "
        "Sempre use preferencialmente a ferramenta `run_query` para consultar os dados em DuckDB. "
        "Se a informação não estiver nos dados, responda apenas: "
        "'Não encontrei essa informação nos arquivos.'"
    )
)

# --- Playground ---
app = Playground(agents=[agent]).get_app()

# --- Inicializar servidor ---
if __name__ == "__main__":
    serve_playground_app("31_15set:app")