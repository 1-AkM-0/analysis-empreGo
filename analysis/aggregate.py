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
    df["area"] = df["area"].apply(lambda area: area.title())

    df["qtd_tecnologias"] = df["stack"].apply(len)

    areas = df["area"].value_counts().sort_values(ascending=False)

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

    _, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(
        top3_plot["area"] + " - " + top3_plot["stack"],
        top3_plot["frequencia"],
        color="#2E86AB",
        edgecolor="#1A5276",
    )
    ax.set_xlabel("Menções em vagas", fontsize=11, fontweight="bold")
    ax.set_title(
        "Top 3 Tecnologias por Área de Estágio", fontsize=14, fontweight="bold", pad=20
    )
    ax.invert_yaxis()
    ax.bar_label(bars, padding=5, fontsize=9)
    plt.tight_layout()
    plt.savefig("../data/top3_clean.png", dpi=300, bbox_inches="tight")

    _, ax = plt.subplots(figsize=(10, 6))
    colors = ["#E74C3C" if area == "dados" else "#3498DB" for area in areas.index]
    bars = ax.barh(areas.index, areas.values, color=colors)
    ax.set_xlabel("Quantidade de vagas", fontsize=11, fontweight="bold")
    ax.set_title(
        "Vagas de estágio em tech por área (fev–abr 2026)",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    ax.bar_label(bars, padding=5, fontsize=10)
    plt.tight_layout()
    plt.savefig("../data/areas_destaque.png", dpi=300, bbox_inches="tight")


if __name__ == "__main__":
    main()
