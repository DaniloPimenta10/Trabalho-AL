import pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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

#[IA] Gemini - 25/11/2026 - Usada para criar o algoritmo responsável por calcular a matriz estocástica e fazer as verificações necessarias
def estimar_matriz_transicao(C: np.ndarray, alpha: float = 0.5) -> tuple[np.ndarray, np.ndarray, np.ndarray]: 
    
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
#[IA]

#[IA] Gemini - 27/11/2026 - 
def distribuicao_estacionaria_sistema(P: np.ndarray) -> np.ndarray:
    n = P.shape[0]
    A = P.T - np.eye(n)
    b = np.zeros(n)

    A[-1, :] = 1.0
    b[-1] = 1.0

    pi = np.linalg.solve(A, b)
    return pi


def impacto_suavizacao_l1(P: np.ndarray, P_laplace: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    pi = distribuicao_estacionaria_sistema(P)
    pi_laplace = distribuicao_estacionaria_sistema(P_laplace)
    norma_l1 = float(np.linalg.norm(pi - pi_laplace, ord=1))
    return pi, pi_laplace, norma_l1
#[IA]

#[IA] - Gemini - 27/11/2026 - Código para guardar as matrizes em csv, criar o mapa de calor e código principal
def salvar_matriz_csv(matriz: np.ndarray, caminho: pathlib.Path, fmt_int: bool = False) -> None:
    rotulos = ["nivel_1", "nivel_2", "nivel_3", "nivel_4"]
    df_mat = pd.DataFrame(matriz, index=rotulos, columns=rotulos)
    if fmt_int:
        df_mat.to_csv(caminho)
    else:
        df_mat.round(6).to_csv(caminho)


def plotar_heatmap_transicao(
    P: np.ndarray, ep: np.ndarray, titulo: str, caminho_saida: pathlib.Path
) -> None:
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(P, cmap="Greys", vmin=0.0, vmax=1.0)

    niveis = ["1 (Verde)", "2 (Amarelo)", "3 (Laranja)", "4 (Vermelho)"]
    ax.set_xticks(range(4), labels=niveis)
    ax.set_yticks(range(4), labels=niveis)
    ax.set_xlabel("Nível na semana t + 1")
    ax.set_ylabel("Nível na semana t")
    ax.set_title(titulo)

    # Anota cada célula com p_hat e erro-padrão
    for i in range(4):
        for j in range(4):
            cor_texto = "white" if P[i, j] > 0.5 else "black"
            texto = f"{P[i, j]:.4f}\n(±{ep[i, j]:.4f})"
            ax.text(j, i, texto, ha="center", va="center", color=cor_texto, fontsize=9)

    fig.colorbar(im, ax=ax, label="Probabilidade de transição")
    fig.tight_layout()
    fig.savefig(caminho_saida, dpi=300)
    plt.close(fig)


def executar_etapa2() -> None:
    raiz = pathlib.Path(__file__).resolve().parent.parent
    dir_raw = raiz / "data" / "raw"
    dir_tabelas = raiz / "results" / "tabelas"
    dir_figuras = raiz / "results" / "figuras"

    dir_tabelas.mkdir(parents=True, exist_ok=True)
    dir_figuras.mkdir(parents=True, exist_ok=True)

    # 1. Matrizes de contagem
    C_serra = calcular_matriz_contagens(dir_raw / "3205002.csv")
    C_linhares = calcular_matriz_contagens(dir_raw / "3203205.csv")

    C_es = np.zeros((4, 4), dtype=int)
    for arq_csv in sorted(dir_raw.glob("*.csv")):
        C_es += calcular_matriz_contagens(arq_csv)

    # Verificação obrigatória: soma de C igual às transições válidas da Etapa 1
    df_aud = pd.read_csv(dir_tabelas / "e1_auditoria.csv")
    trans_serra = int(df_aud.loc[df_aud["geocode"] == 3205002, "transicoes_validas"].iloc[0])
    trans_linhares = int(df_aud.loc[df_aud["geocode"] == 3203205, "transicoes_validas"].iloc[0])
    trans_es = int(df_aud["transicoes_validas"].sum())

    assert C_serra.sum() == trans_serra, "Divergência na soma de C (Serra)"
    assert C_linhares.sum() == trans_linhares, "Divergência na soma de C (Linhares)"
    assert C_es.sum() == trans_es, "Divergência na soma de C (ES agregado)"

    cenarios = [
        ("serra", "Serra (3205002)", C_serra),
        ("linhares", "Linhares (3203205)", C_linhares),
        ("es", "Espírito Santo (Agregado)", C_es),
    ]

    resumo_laplace = []

    for slug, nome, C in cenarios:
        P_hat, ep_hat, P_lap = estimar_matriz_transicao(C, alpha=0.5)

        # Verificação obrigatória: matrizes estocásticas com tolerância 1e-12
        verificar_estocastica(P_hat, tol=1e-12)
        verificar_estocastica(P_lap, tol=1e-12)

        # Distribuições estacionárias e impacto L1
        pi = distribuicao_estacionaria_sistema(P_hat)
        pi_lap = distribuicao_estacionaria_sistema(P_lap)
        diff_l1 = float(np.linalg.norm(pi - pi_lap, ord=1))

        # Salvar tabelas (no máximo 6 casas decimais, conforme Seção 10)
        salvar_matriz_csv(C, dir_tabelas / f"e2_C_{slug}.csv", fmt_int=True)
        salvar_matriz_csv(P_hat, dir_tabelas / f"e2_P_{slug}.csv")
        salvar_matriz_csv(ep_hat, dir_tabelas / f"e2_ep_{slug}.csv")
        salvar_matriz_csv(P_lap, dir_tabelas / f"e2_P_laplace_{slug}.csv")

        # Gerar mapa de calor em escala de cinza
        plotar_heatmap_transicao(
            P_hat,
            ep_hat,
            f"Matriz de Transição Estimada - {nome}",
            dir_figuras / f"e2_heatmap_P_{slug}.png",
        )

        resumo_laplace.append({
            "cenario": nome,
            "pi_1": round(pi[0], 6),
            "pi_2": round(pi[1], 6),
            "pi_3": round(pi[2], 6),
            "pi_4": round(pi[3], 6),
            "pi_lap_1": round(pi_lap[0], 6),
            "pi_lap_2": round(pi_lap[1], 6),
            "pi_lap_3": round(pi_lap[2], 6),
            "pi_lap_4": round(pi_lap[3], 6),
            "norma_l1": round(diff_l1, 6),
        })

    pd.DataFrame(resumo_laplace).to_csv(dir_tabelas / "e2_resumo_laplace.csv", index=False)


if __name__ == "__main__":
    executar_etapa2()
#[IA]