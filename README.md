# 🤖 agentIAgno: Inteligência Artificial para Auditoria de Varejo

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Agno](https://img.shields.io/badge/Framework-Agno%20(Phidata)-orange.svg)](https://www.agno.com/)
[![DuckDB](https://img.shields.io/badge/Database-DuckDB-yellow.svg)](https://duckdb.org/)
[![Status](https://img.shields.io/badge/Status-Desenvolvimento-green.svg)]()

**agentIAgno** é um ecossistema de agentes inteligentes projetado para transformar a auditoria de varejo. Utilizando o framework **Agno**, o projeto automatiza a análise de grandes volumes de dados transacionais, identificando padrões de fraude, anomalias de estoque e inconsistências sistêmicas com precisão e velocidade.

---

## 🎯 Proposta de Valor

No cenário de varejo moderno, auditores levam dias para analisar manualmente centenas de SKUs. O **agentIAgno** reduz esse tempo para segundos, cruzando dados de:
- **Cancelamentos**
- **Ajustes de Estoque**
- **Devoluções**
- **Saídas de Mercadoria**

O sistema é capaz de detectar padrões complexos, como o "Loop de SKU" (Cancelamento -> Ajuste -> Devolução), onde o mesmo produto transita entre tabelas de forma suspeita para burlar controles de auditoria.

## ✨ Funcionalidades Principais

- **🔍 Agentes Especialistas:**
  - **Analistas de Dados:** Realizam consultas complexas via SQL natural em DuckDB.
  - **Pesquisadores:** Buscam informações externas via Tavily e Groq.
  - **Agentes de Documentos:** Processam PDFs e CSVs para extração de conhecimento específico.
- **⚡ Performance de Data Warehouse:** Conversão automática de CSVs brutos para **Parquet** e processamento via **DuckDB** para alta performance em milhões de linhas.
- **🧠 Conhecimento Vetorial:** Implementação de RAG (Retrieval-Augmented Generation) com **ChromaDB** para análise inteligente de documentos técnicos e normativos.
- **🌐 Playground Interativo:** Interface via FastAPI para interação direta com os agentes em tempo real.

## 🛠️ Stack Tecnológica

- **Orquestração de IA:** [Agno](https://www.agno.com/) (Phidata)
- **Modelos de Linguagem:** OpenAI (GPT-4o/5-nano), Groq (Llama-3.3)
- **Processamento de Dados:** DuckDB, Pandas, Parquet
- **Banco Vetorial:** ChromaDB
- **Infraestrutura:** FastAPI, Uvicorn, Python-dotenv
- **Gerenciamento de Pacotes:** `uv`

## 🚀 Como Começar

### Pré-requisitos
- Python 3.13 ou superior
- Recomendado o uso do [uv](https://github.com/astral-sh/uv) para gerenciamento de projeto.

### Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/agentIAgno.git
   cd agentIAgno
   ```

2. Configure as variáveis de ambiente:
   Crie um arquivo `.env` na raiz do projeto com suas chaves:
   ```env
   OPENAI_API_KEY=sua_chave_aqui
   GROQ_API_KEY=sua_chave_aqui
   TAVILY_API_KEY=sua_chave_aqui
   ```

3. Instale as dependências:
   ```bash
   uv sync
   ```

### Execução

O projeto possui diversos módulos experimentais numerados. Para rodar o agente de análise de dados principal:

```bash
uv run python 31_15set.py
```

Isso iniciará o **Agno Playground**. Acesse o link fornecido no terminal para interagir com o agente através da interface web.

## 📂 Estrutura do Projeto

- `00_llm_call.py`: Teste básico de conexão com LLMs.
- `11_researcher.py`: Agente de pesquisa web (Tools).
- `21_pdf_agent.py`: Agente especializado em análise de documentos RAG.
- `31_15set.py`: Core do sistema - Integração DuckDB + Data Warehouse + Multi-agentes.
- `dados/`: Diretório contendo os datasets de auditoria.
- `tmp/`: Banco de dados local e caches de processamento.

---

## 📋 RoadMap

- [ ] Implementação de lógica de "Agente que chama Agente" (Multi-Agent Crew).
- [ ] Integração com MongoDB para persistência de logs de auditoria em alta escala.
- [ ] Dashboards automatizados de visualização de anomalias detectadas.
- [ ] Refinamento dos pesos de detecção de fraude (Z-Score analítico).

---

*Desenvolvido para revolucionar a eficiência na auditoria inteligente.*
