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
            duplicatas = total_linhas - semanas_observadas   

            datas = pd.to_datetime(dados_municipio["data_iniSE"], errors="coerce").dropna()
            semanas_esperadas = ((datas.max() - datas.min()).days // 7) + 1

            lacunas = semanas_esperadas - semanas_observadas

            df_ord = (dados_municipio.sort_values("SE", ascending=True).drop_duplicates(subset=["SE"], keep="first").reset_index(drop=True))
            df_ord["data_dt"] = pd.to_datetime(df_ord["data_iniSE"], errors="coerce")

            transicoes_validas = 0

            for i in range(len(df_ord) - 1):
                d_atual = df_ord.loc[i, "data_dt"]
                d_prox = df_ord.loc[i + 1, "data_dt"]

                nivel_atual = df_ord.loc[i, "nivel"]
                nivel_prox = df_ord.loc[i + 1, "nivel"]

                if pd.notna(d_atual) and pd.notna(d_prox):
                    semanas_consecutivas = (d_prox - d_atual).days == 7
                    niveis_registrados = pd.notna(nivel_atual) and pd.notna(nivel_prox)

                    if semanas_consecutivas and niveis_registrados:
                        transicoes_validas += 1

            versoes_unicas = sorted(
                str(v).strip()
                for v in df_ord["versao_modelo"].dropna().unique()
                if str(v).strip()
            )
            versoes_str = " | ".join(versoes_unicas)
            
            registro = {
                "geocode": geocode,
                "semanas_observadas": semanas_observadas,
                "semanas_esperadas": semanas_esperadas,
                "lacunas" : lacunas,
                "duplicatas": duplicatas,
                "transicoes_validas": transicoes_validas,
                "versoes_modelo_presente": versoes_unicas
                }

            contagem_niveis = df_ord["nivel"].value_counts(dropna=True).sort_index()
            for nv in [1, 2, 3, 4]:
                registro[f"semanas_nivel_{nv}"] = int(contagem_niveis.get(nv, 0))

            linhas_auditoria.append(registro)
        
        df_auditoria = pd.DataFrame(linhas_auditoria)
        df_auditoria.to_csv(raiz / "results" / "e1_auditoria.csv", index=False)



if __name__ == "__main__":
    criar_tabela()