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


def extract_goals_by_year(url):
    """
    Extrai os gols por ano de um jogador a partir da sua página na Wikipedia.
    
    Essa versão utiliza pd.read_html (com StringIO para evitar warnings) e achata o cabeçalho
    caso seja MultiIndex.
    
    Returns:
        pd.DataFrame: DataFrame com as colunas 'year', 'total' e 'type'.
    """
    print(f"Extraindo dados de: {url}")
    response = requests.get(url, timeout=10)
    try:
        tables = pd.read_html(StringIO(response.text))
    except ValueError as e:
        print(f"Erro de valor: {e}")
        return pd.DataFrame(columns=["year", "total", "type"])
    except URLError as e:
        print(f"Erro de rede: {e}")
        return pd.DataFrame(columns=["year", "total", "type"])

    club_data = []
    international_data = []

    for table in tables:
        # Se as colunas forem MultiIndex, achata-as
        if isinstance(table.columns, pd.MultiIndex):
            table.columns = [
                ' '.join(
                    [str(item) for item in col if item and str(item).strip()])
                for col in table.columns.values
            ]
        cols = [str(col) for col in table.columns]
        # Verifica se a tabela tem estatísticas de clube (presença da coluna "Season")
        if any("Season" in col for col in cols):
            season_col = next((col for col in cols if "Season" in col), None)
            # Procura por uma coluna que contenha "Total Goals" ou, em alternativa, "Goals"
            goal_col = next((col for col in cols if "Total Goals" in col),
                            None)
            if goal_col is None:
                goal_col = next((col for col in cols if "Goals" in col), None)

            if season_col and goal_col:
                for _, row in table.iterrows():
                    season_text = str(row[season_col])
                    year_match = re.search(r"(\d{4})", season_text)
                    if year_match:
                        year = year_match.group(1)
                        try:
                            goals = int(row[goal_col])
                        except ValueError as e:
                            print(f"Erro de valor: {e}")
                            goals = 0
                        except URLError as e:
                            print(f"Erro de rede: {e}")
                            goals = 0
                        club_data.append({
                            "year": year,
                            "total": goals,
                            "type": "club"
                        })

        # Verifica se a tabela tem estatísticas internacionais (colunas "Year" e "Goals")
        elif any("Year" in col for col in cols) and any("Goals" in col
                                                        for col in cols):
            year_col = next((col for col in cols if "Year" in col), None)
            goal_col = next((col for col in cols if "Goals" in col), None)
            if year_col and goal_col:
                for _, row in table.iterrows():
                    year_text = str(row[year_col])
                    year_match = re.search(r"(\d{4})", year_text)
                    if year_match:
                        year = year_match.group(1)
                        try:
                            goals = int(row[goal_col])
                        except ValueError as e:
                            print(f"Erro de valor: {e}")
                            goals = 0
                        except URLError as e:
                            print(f"Erro de rede: {e}")
                            goals = 0
                        international_data.append({
                            "year": year,
                            "total": goals,
                            "type": "international"
                        })

    all_data = pd.DataFrame(club_data + international_data)
    return all_data


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
