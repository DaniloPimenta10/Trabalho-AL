import pathlib
import numpy as np
import pandas as pd

#[IA] Gemini - 24/11/2026 - Usada para criar o algoritmo responsável por calcular a matriz de contagem
def calcular_matriz_contagens(caminho_csv: pathlib.Path) -> np.ndarray:
    df = pd.read_csv(caminho_csv)
    df_ord = (df.sort_values("SE", ascending=True).drop_duplicates(subset=["SE"], keep="first").reset_index(drop=True))
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
#[IA]

def estimar_matriz_transicao(
    C: np.ndarray, alpha: float = 0.5) -> tuple[np.ndarray, np.ndarray, np.ndarray]: 
    somas_linhas = C.sum(axis=1, keepdims=True)

    P_hat = np.divide(
        C,
        somas_linhas,
        out=np.zeros_like(C, dtype=float),
        where=somas_linhas > 0,
    )

    var_hat = np.divide(
        P_hat * (1.0 - P_hat),
        somas_linhas,
        out=np.zeros_like(P_hat),
        where=somas_linhas > 0,
    )
    ep_hat = np.sqrt(var_hat)

    P_laplace = (C + alpha) / (somas_linhas + 4.0 * alpha)

    return P_hat, ep_hat, P_laplace


def verificar_estocastica(P: np.ndarray, tol: float = 1e-12) -> None:
    if np.any(P < -tol):
        raise ValueError("Matriz possui entradas negativas.")
    somas = P.sum(axis=1)
    if not np.allclose(somas, 1.0, atol=tol):
        raise ValueError(f"Somas das linhas diferem de 1: {somas}")