import os
import pandas as pd
import pathlib

def criar_tabela():
    raiz = pathlib.Path(__file__).resolve().parent.parent
    caminhoManifest = raiz / "data" / "MANIFEST.txt"
    
    os.makedirs(raiz / "results", exist_ok=True)
    
    with open(caminhoManifest , "r" , encoding="utf-8") as arquivo:
        next(arquivo, None)
        next(arquivo, None)

    linhas_auditoria = []

    for linha in arquivo:
        if not linha.strip():
            continue
        
        l = linha.split(",")
        geocode = l[0].strip()

        dados_municipio = pd.read_csv( raiz / "data" / "raw" / f"{geocode}.csv")

        se_unicos = set((dados_municipio["SE"].dropna()))
        semanas_observadas = len(se_unicos)
        total_linhas = len(dados_municipio["SE"].dropna())
        duplicatas = total_linhas - se_unicos

        datas = pd.to_datetime(dados_municipio["data_iniSE"], errors="coerce").dropna()
        semanas_esperadas = ((datas.max() - datas.min()).days // 7) + 1

        lacunas = semanas_esperadas - semanas_observadas

        #falta colocar ainda transições válidas, número de semanas em cada nível e versões do modelo presente
        
        registro = {
            "geocode": geocode,
            "semanas_observadas": semanas_observadas,
            "semanas_esperadas": semanas_esperadas,
            "lacunas" : lacunas,
            "duplicatas": duplicatas,
            }




if __name__ == "__main__":
    criar_tabela()