import os
import chardet

# Função para detectar a codificação de um arquivo
def detectar_codificacao(caminho_arquivo):
    with open(caminho_arquivo, 'rb') as f:
        rawdata = f.read(10000)  # lê os primeiros 10k bytes para detectar
        result = chardet.detect(rawdata)
        return result['encoding']

pastas = ['dados/saidas/', 'dados/devolucoes/', 'dados/cancelamentos/', 'dados/ajustes/']

for pasta in pastas:
    print(f"Codificação dos arquivos em {pasta}:")
    for arquivo in os.listdir(pasta):
        caminho_arquivo = os.path.join(pasta, arquivo)
        if os.path.isfile(caminho_arquivo) and arquivo.endswith('.csv'):
            codificacao = detectar_codificacao(caminho_arquivo)
            print(f"  {arquivo}: {codificacao}")
    print()
