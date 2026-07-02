"""
Gera os dados para a página estática interativa (docs/data.json).

A página HTML (docs/index.html) consome esse JSON e monta os gráficos
interativos no navegador, permitindo filtrar por jogador, tipo de gol
(clube/seleção) e eixo (anos ativos vs. ano-calendário).
"""

import json
import os
from datetime import date

import pandas as pd

from goal500.utils.data_processing import clean_data

# Ordem/paleta categórica validada (mesma usada no index.html).
# Cada modo tem sua própria versão dos mesmos 8 tons, ajustada à superfície.
PALETTE = [
    "#2a78d6",  # blue
    "#1baf7a",  # aqua
    "#eda100",  # yellow
    "#008300",  # green
    "#4a3aa7",  # violet
    "#e34948",  # red
    "#e87ba4",  # magenta
    "#eb6834",  # orange
]
PALETTE_DARK = [
    "#3987e5",  # blue
    "#199e70",  # aqua
    "#c98500",  # yellow
    "#008300",  # green
    "#9085e9",  # violet
    "#e66767",  # red
    "#d55181",  # magenta
    "#d95926",  # orange
]


def build_site_data(df):
    """
    Constrói o dicionário de dados consumido pela página estática.

    Para cada jogador retorna arrays alinhados por ano-calendário com os gols
    de clube e de seleção. O acumulado, os "anos ativos" e os totais por filtro
    são calculados no navegador, garantindo que os gráficos reajam aos filtros.

    Args:
        df (pd.DataFrame): DataFrame bruto com colunas name/year/total/type.

    Returns:
        dict: estrutura pronta para virar JSON.
    """
    clean = clean_data(df.copy())
    if clean.empty:
        return {"generated_at": date.today().isoformat(), "source": "Wikipedia", "players": []}

    clean["year"] = clean["year"].astype(int)
    # Soma gols por jogador/ano/tipo (o CSV pode ter várias linhas por temporada).
    grouped = (
        clean.groupby(["name", "year", "type"])["total"].sum().reset_index()
    )

    players = []
    # Mantém uma ordem estável: por total de gols na carreira (desc).
    totals = grouped.groupby("name")["total"].sum().sort_values(ascending=False)

    for idx, name in enumerate(totals.index):
        pdata = grouped[grouped["name"] == name]
        years = sorted(pdata["year"].unique().tolist())
        club = []
        international = []
        for y in years:
            sub = pdata[pdata["year"] == y]
            club.append(int(sub[sub["type"] == "club"]["total"].sum()))
            international.append(int(sub[sub["type"] == "international"]["total"].sum()))

        players.append({
            "name": name,
            "color": PALETTE[idx % len(PALETTE)],
            "color_dark": PALETTE_DARK[idx % len(PALETTE_DARK)],
            "years": years,
            "club": club,
            "international": international,
            "total_club": int(sum(club)),
            "total_international": int(sum(international)),
            "total": int(sum(club) + sum(international)),
            "first_year": years[0],
            "last_year": years[-1],
        })

    return {
        "generated_at": date.today().isoformat(),
        "source": "Wikipedia",
        "players": players,
    }


def write_site_data(df, output_file="docs/data.json"):
    """
    Escreve o JSON de dados da página estática.

    Args:
        df (pd.DataFrame): DataFrame bruto com os dados extraídos.
        output_file (str): caminho do arquivo JSON de saída.

    Returns:
        str: caminho do arquivo escrito.
    """
    data = build_site_data(df)
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    print(f"Dados do site salvos em: {output_file}")
    return output_file
