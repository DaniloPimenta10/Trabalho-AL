# [IA] Gemini 18-11-2026 Criação da estrutura base do script para baixar os CSVs da API do InfoDengue, calcular o hash SHA-256 e gerar o arquivo de manifesto exigido pelo edital.
import os
import time
import hashlib
import datetime
import requests
import pandas as pd

def calcular_sha256(caminho_arquivo):
    """Calcula o hash SHA-256 de um arquivo."""
    sha256_hash = hashlib.sha256()
    with open(caminho_arquivo, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def baixar_dados_dengue():
    os.makedirs("data/raw", exist_ok=True)
    
    url_ibge = "servicodados.ibge.gov.br/api/v1/localidades/estados/32/municipios"
    res = requests.get(f"https://{url_ibge}")
    municipios = res.json()
    geocodes = [m["id"] for m in municipios]
    
    manifesto_linhas = []
    manifesto_linhas.append(f"Data e Hora do Download: {datetime.datetime.now()}\n")
    manifesto_linhas.append("geocode,url,num_linhas,sha256\n")
    
    base_url = "https://info.dengue.mat.br/api/alertcity?geocode={g}&disease=dengue&format=csv&ew_start=1&ew_end=53&ey_start=2015&ey_end=2025"
    
    for g in geocodes:
        url_consulta = base_url.format(g=g)
        try:
            df = pd.read_csv(url_consulta)
            caminho_csv = f"data/raw/{g}.csv"
            df.to_csv(caminho_csv, index=False)
            
            num_linhas = len(df)
            file_hash = calcular_sha256(caminho_csv)
            manifesto_linhas.append(f"{g},{url_consulta},{num_linhas},{file_hash}\n")
        except Exception as e:
            print(f"Erro ao baixar o município {g}: {e}")
            
        time.sleep(1)
        
    with open("data/MANIFEST.txt", "w", encoding="utf-8") as f:
        f.writelines(manifesto_linhas)

if __name__ == "__main__":
    baixar_dados_dengue()
# [IA]