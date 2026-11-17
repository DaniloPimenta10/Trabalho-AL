import time, pandas as pd
URL = ("https://info.dengue.mat.br/api/alertcity?geocode={g}&disease=dengue" "&format=csv&ew_start=1&ew_end=53&ey_start={a}&ey_end={b}")

for g in geocodes: # 78 códigos do IBGE
    df = pd.read_csv(URL.format(g=g, a=2015, b=2025))
    df.to_csv(f"data/raw/{g}.csv", index=False)
    time.sleep(1)