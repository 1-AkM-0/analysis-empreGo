import sqlite3
import json
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("../data/vagas.db")


def main():
    with sqlite3.connect("../data/vagas.db") as conn:
        df = pd.read_sql(
            "SELECT ai_response FROM jobs WHERE ai_response IS NOT NULL", conn
        )

    def safe_json(s):
        try:
            return json.loads(s)
        except (json.JSONDecodeError, TypeError):
            return {}

    df["ai_parsed"] = df["ai_response"].apply(safe_json)
    df["stack"] = df["ai_parsed"].apply(lambda x: x.get("stack", []))
    df["area"] = df["ai_parsed"].apply(lambda x: x.get("area", "nao_informado"))

    df = df[df["area"] != "nao_informado"]
    df = df[df["stack"].apply(len) > 0].reset_index(drop=True)

    df["qtd_tecnologias"] = df["stack"].apply(len)

    areas = df["area"].value_counts().sort_values(ascending=False)

    areas.plot(kind="barh", figsize=(10, 6), color="steelblue")
    plt.title("Vagas de estágio em tech por área (fev–abr 2026)")
    plt.xlabel("Quantidade de vagas")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig("../data/quantidade_vagas_area.png", dpi=150)
    plt.close()

    df["stack"] = df["stack"].apply(
        lambda lista: [t.upper() if len(t) <= 3 else t.title() for t in lista]
    )

    vagas_por_area = df["area"].value_counts()
    areas_validas = set(vagas_por_area[vagas_por_area >= 5].index)
    df_filtrado = df[df["area"].isin(areas_validas)].reset_index(drop=True)

    df_long = df_filtrado.explode("stack")

    TECHS_EXCLUIR = {"GIT", "Github"}
    df_long = df_long[~df_long["stack"].isin(TECHS_EXCLUIR)]

    counts = df_long.groupby(["area", "stack"]).size().reset_index(name="frequencia")

    top3_por_area = (
        (counts.sort_values("frequencia", ascending=False))
        .groupby("area")
        .head(3)
        .reset_index(drop=True)
    )

    top3_plot = top3_por_area.sort_values(
        ["area", "frequencia"], ascending=[True, False]
    ).reset_index(drop=True)

    total_vagas = vagas_por_area.to_dict()

    top3_plot["label"] = top3_plot.apply(
        lambda row: f"{row['area']} ({total_vagas[row['area']]} vagas): {row['stack']}",
        axis=1,
    )

    plt.figure(figsize=(10, 6))
    plt.barh(top3_plot["label"], top3_plot["frequencia"], color="steelblue")
    plt.xlabel("Número de vagas que mencionam a tecnologia")
    plt.title("Top 3 tecnologias mais pedidas por área")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig("../data/top3_por_area.png", dpi=150)


if __name__ == "__main__":
    main()
