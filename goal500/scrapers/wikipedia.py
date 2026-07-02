"""
Módulo para extrair dados de gols de jogadores de futebol da Wikipedia.
"""

import re
from io import StringIO
from urllib.error import URLError
import pandas as pd
import requests


def wiki_url(path):
    """
    Constrói a URL completa da Wikipedia a partir de um caminho.
    """
    return f"https://en.wikipedia.org{path}"


def get_active_players():
    """
    Retorna uma lista de jogadores ativos com seus nomes e links para suas páginas na Wikipedia.
    """
    players = [
        ("Cristiano Ronaldo",
         "https://en.wikipedia.org/wiki/Cristiano_Ronaldo"),
        ("Lionel Messi", "https://en.wikipedia.org/wiki/Lionel_Messi"),
        ("Robert Lewandowski",
         "https://en.wikipedia.org/wiki/Robert_Lewandowski"),
        ("Neymar Jr", "https://en.wikipedia.org/wiki/Neymar"),
        ("Erling Haaland", "https://en.wikipedia.org/wiki/Erling_Haaland"),
        ("Kylian Mbappé", "https://en.wikipedia.org/wiki/Kylian_Mbapp%C3%A9"),
        ("Harry Kane", "https://en.wikipedia.org/wiki/Harry_Kane"),
        ("Luis Suárez", "https://en.wikipedia.org/wiki/Luis_Su%C3%A1rez"),
    ]
    return pd.DataFrame(players, columns=["name", "link"])


def _flatten_columns(table):
    """Achata cabeçalhos MultiIndex em strings simples e retorna a lista de colunas."""
    if isinstance(table.columns, pd.MultiIndex):
        table.columns = [
            ' '.join(str(item) for item in col if item and str(item).strip())
            for col in table.columns.values
        ]
    return [str(col) for col in table.columns]


def _pick_goal_column(cols):
    """
    Escolhe a coluna de gols que representa o TOTAL da linha.

    As tabelas da Wikipedia trazem várias colunas de "Goals" (liga, copa,
    continental...) e uma coluna final "Total Goals" com a soma da temporada/ano.
    É essa que queremos — daí preferirmos, na ordem: a última "Total Goals",
    senão a última coluna que contenha "Goals".
    """
    total_cols = [c for c in cols if "Total Goals" in c]
    if total_cols:
        return total_cols[-1]
    goal_cols = [c for c in cols if "Goals" in c]
    return goal_cols[-1] if goal_cols else None


def _parse_goals(value):
    """Converte a célula de gols em inteiro, ignorando marcadores de nota (ex.: '40[h]')."""
    match = re.search(r"\d+", str(value))
    return int(match.group()) if match else 0


def _extract_rows(table, key_col, goal_col, kind):
    """
    Extrai (year, total, type) das linhas de uma tabela.

    Só considera linhas cuja célula-chave (Season/Year) contenha um ano de 4
    dígitos — assim as linhas de subtotal ("Total", "Career total") são ignoradas.
    Para temporadas como "2002–03" usa-se o primeiro ano (2002).
    """
    rows = []
    for _, row in table.iterrows():
        year_match = re.search(r"(\d{4})", str(row[key_col]))
        if not year_match:
            continue
        rows.append({
            "year": year_match.group(1),
            "total": _parse_goals(row[goal_col]),
            "type": kind,
        })
    return rows


def extract_goals_by_year(url):
    """
    Extrai os gols por ano de um jogador a partir da sua página na Wikipedia (em inglês).

    Usa a tabela "Career statistics": a de clube (coluna "Season") e a de seleção
    (coluna "Year"), somando sempre a coluna "Total Goals" de cada linha. Os totais
    resultantes batem com a linha "Career total" da própria página.

    Returns:
        pd.DataFrame: DataFrame com as colunas 'year', 'total' e 'type'.
    """
    print(f"Extraindo dados de: {url}")
    headers = {"User-Agent": "goal500-python/0.1 (https://github.com/jtrecenti/goal500-python)"}
    try:
        response = requests.get(url, timeout=30, headers=headers)
        response.raise_for_status()
        # flavor='lxml' torna o parsing determinístico e evita depender de html5lib.
        tables = pd.read_html(StringIO(response.text), flavor="lxml")
    except (ValueError, URLError, requests.RequestException) as e:
        print(f"Erro ao obter/parsear a página: {e}")
        return pd.DataFrame(columns=["year", "total", "type"])

    club_data = []
    international_data = []
    club_done = False
    international_done = False

    for table in tables:
        cols = _flatten_columns(table)
        goal_col = _pick_goal_column(cols)
        if goal_col is None:
            continue

        # Tabela de clube: tem a coluna "Season".
        if not club_done and any("Season" in col for col in cols):
            season_col = next(col for col in cols if "Season" in col)
            club_data = _extract_rows(table, season_col, goal_col, "club")
            club_done = True

        # Tabela de seleção: tem a coluna "Year" (mas não "Season").
        elif not international_done and any("Year" in col for col in cols):
            year_col = next(col for col in cols if "Year" in col)
            international_data = _extract_rows(table, year_col, goal_col, "international")
            international_done = True

        if club_done and international_done:
            break

    return pd.DataFrame(club_data + international_data)


def get_player_stats():
    """
    Obtém estatísticas de gols por ano para todos os jogadores ativos.
    
    Returns:
        pd.DataFrame: DataFrame com as colunas 'name', 'year', 'total' e 'type'.
    """
    players = get_active_players()
    all_stats = []

    for _, player in players.iterrows():
        try:
            player_stats = extract_goals_by_year(player["link"])
            if not player_stats.empty:
                player_stats["name"] = player["name"]
                all_stats.append(player_stats)
        except ValueError as e:
            print(f"Erro de valor: {e}")
        except URLError as e:
            print(f"Erro de rede: {e}")

    if all_stats:
        return pd.concat(all_stats, ignore_index=True)
    return pd.DataFrame(columns=["name", "year", "total", "type"])


# Exemplo de uso
if __name__ == "__main__":
    stats = get_player_stats()
    print(stats)
