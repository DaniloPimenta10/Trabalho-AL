# [IA] Gemini - 20/11/2026 - Usado para tirar duvidas do funcionamento das bibliotecas e corrigir erros pontuais
import hashlib
import os
import pathlib
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def grafico_serra(raiz):

    dados_serra = pd.read_csv(raiz / "data" / "raw" / "3205002.csv")
    df = (dados_serra.sort_values("SE", ascending=True).drop_duplicates(subset=["SE"], keep="first").reset_index(drop=True))
    df["data_dt"] = pd.to_datetime(df["data_iniSE"], errors="coerce")

    #[IA] Gemini - 23/11/2026 - Criação do gráfico de sequencia de níveis da Serra
    fig, ax = plt.subplots(figsize=(13, 4))
    ax.step(df["data_dt"], df["nivel"], where="post", linewidth=1.1, color="#1f4e78")

    ax.set_yticks([1, 2, 3, 4])
    ax.set_ylim(0.7, 4.3)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    ax.set_title("Sequência semanal dos níveis de alerta — Serra/ES (3205002), 2015–2025")
    ax.set_xlabel("Ano (data de início da SE)")
    ax.set_ylabel("Nível de alerta")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(raiz / "results" / "tabelas" / "e1_serra_niveis.png", dpi=300)
    plt.close(fig)
     #[IA]

#[IA] Gemini - 23/11/2026 - Criação do mapa de calor municipio x ano
def grafico_heatmap_nivel3(raiz: pathlib.Path, geocodes: list[str]):
    series_municipios = {}

    for geocode in geocodes:
        df = pd.read_csv(raiz / "data" / "raw" / f"{geocode}.csv")
        df = (
            df.sort_values("SE", ascending=True)
            .drop_duplicates(subset=["SE"], keep="first")
            .reset_index(drop=True)
        )
        df["ano"] = df["SE"] // 100
        df["nivel_ge_3"] = df["nivel"] >= 3

        fracao_anual = df.groupby("ano")["nivel_ge_3"].mean()
        series_municipios[geocode] = fracao_anual

    matriz = pd.DataFrame(series_municipios).T.sort_index(axis=0).sort_index(axis=1)

    fig, ax = plt.subplots(figsize=(10, 14))
    im = ax.imshow(matriz.values, cmap="Greys", aspect="auto", vmin=0, vmax=1)

    ax.set_xticks(range(len(matriz.columns)))
    ax.set_xticklabels(matriz.columns)
    ax.set_yticks(range(len(matriz.index)))
    ax.set_yticklabels(matriz.index, fontsize=7)

    cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("Fração de semanas com nível ≥ 3")

    ax.set_title("Fração anual de semanas em nível ≥ 3 por município (ES, 2015–2025)")
    ax.set_xlabel("Ano epidemiológico")
    ax.set_ylabel("Município (geocode)")

    plt.tight_layout()
    plt.savefig(raiz / "results" / "tabelas" / "e1_heatmap_nivel3.png", dpi=300)
    plt.close(fig)
#[IA]


# [IA] Gemini - 23/11/2026 - Gerar código para conferir o hash do MANIFEST.md
def calcular_sha256(caminho_arquivo: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(caminho_arquivo, "rb") as f:
        for bloco in iter(lambda: f.read(8192), b""):
            h.update(bloco)
    return h.hexdigest()
# [IA]

def criar_tabela():
    raiz = pathlib.Path(__file__).resolve().parent.parent
    caminho_manifest = raiz / "data" / "MANIFEST.txt"

    os.makedirs(raiz / "results", exist_ok=True)

    dir_tabelas = raiz / "results" / "tabelas"
    dir_figuras = raiz / "results" / "figuras"

    dir_tabelas.mkdir(parents=True, exist_ok=True)
    dir_figuras.mkdir(parents=True, exist_ok=True)


    linhas_auditoria = []
    hashes_ok = 0
    divergentes = []

    with open(caminho_manifest, "r", encoding="utf-8") as arquivo:
        next(arquivo, None)
        next(arquivo, None)

        for linha in arquivo:
            if not linha.strip():
                continue

            l = linha.strip().split(",")
            geocode = l[0].strip()
            hash_esperado = l[3].strip()

            caminho_csv = raiz / "data" / "raw" / f"{geocode}.csv"

            # [IA] Gemini - 23/11/2026 - Gerar código para conferir o hash do MANIFEST.md
            hash_atual = calcular_sha256(caminho_csv)
            if hash_atual == hash_esperado:
                hashes_ok += 1
            else:
                divergentes.append(geocode)
            # [IA]

            dados_municipio = pd.read_csv(caminho_csv)

            se_unicos = set(dados_municipio["SE"].dropna())
            semanas_observadas = len(se_unicos)
            total_linhas = len(dados_municipio["SE"].dropna())
            duplicatas = total_linhas - semanas_observadas

            datas = pd.to_datetime(dados_municipio["data_iniSE"], errors="coerce").dropna()
            semanas_esperadas = ((datas.max() - datas.min()).days // 7) + 1
            lacunas = semanas_esperadas - semanas_observadas

            df_ord = (
                dados_municipio.sort_values("SE", ascending=True)
                .drop_duplicates(subset=["SE"], keep="first")
                .reset_index(drop=True)
            )
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

            registro = {
                "geocode": geocode,
                "semanas_observadas": semanas_observadas,
                "semanas_esperadas": semanas_esperadas,
                "lacunas": lacunas,
                "duplicatas": duplicatas,
                "transicoes_validas": transicoes_validas,
                "versoes_modelo_presente": versoes_unicas,
            }

            contagem_niveis = df_ord["nivel"].value_counts(dropna=True).sort_index()
            for nv in [1, 2, 3, 4]:
                registro[f"semanas_nivel_{nv}"] = int(contagem_niveis.get(nv, 0))

            linhas_auditoria.append(registro)

    df_auditoria = pd.DataFrame(linhas_auditoria)
    df_auditoria.to_csv(raiz / "results" / "e1_auditoria.csv", index=False)

    grafico_serra(raiz)
    grafico_heatmap_nivel3(raiz, df_auditoria["geocode"].tolist())

    print(f"Hashes SHA-256 conferidos: {hashes_ok}/{len(linhas_auditoria)} válidos.")
    if divergentes:
        print("Divergências:", divergentes)


if __name__ == "__main__":
    criar_tabela()

#[IA]