import pathlib
import numpy as np
import pandas as pd


def calcular_matriz_contagens(caminho_csv: pathlib.Path) -> np.ndarray:
    df = pd.read_csv(caminho_csv)
    df_ord = (
        df.sort_values("SE", ascending=True)
        .drop_duplicates(subset=["SE"], keep="first")
        .reset_index(drop=True)
    )
    df_ord["data_dt"] = pd.to_datetime(df_ord["data_iniSE"], errors="coerce")

    C = np.zeros((4, 4), dtype=int)

    for idx in range(len(df_ord) - 1):
        d_atual = df_ord.loc[idx, "data_dt"]
        d_prox = df_ord.loc[idx + 1, "data_dt"]
        nv_atual = df_ord.loc[idx, "nivel"]
        nv_prox = df_ord.loc[idx + 1, "nivel"]

        if pd.notna(d_atual) and pd.notna(d_prox):
            if (d_prox - d_atual).days == 7 and pd.notna(nv_atual) and pd.notna(nv_prox):
                origem = int(nv_atual) - 1
                destino = int(nv_prox) - 1
                C[origem, destino] += 1

    return C