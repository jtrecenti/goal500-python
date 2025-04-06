"""
Módulo para extrair dados de gols de jogadores de futebol da Wikipedia.
"""

import re
import requests
from bs4 import BeautifulSoup
import pandas as pd


def wiki_url(path):
    """
    Constrói a URL completa da Wikipedia a partir de um caminho.
    
    Args:
        path (str): Caminho relativo na Wikipedia.
        
    Returns:
        str: URL completa.
    """
    return f"https://en.wikipedia.org{path}"


def get_active_players():
    """
    Retorna uma lista de jogadores ativos com seus nomes e links para suas páginas na Wikipedia.
    
    Returns:
        pd.DataFrame: DataFrame com colunas 'name' e 'link'.
    """
    # Lista de jogadores e seus links na Wikipedia
    players = [
        # Jogadores do projeto original
        ("Cristiano Ronaldo", "https://en.wikipedia.org/wiki/Cristiano_Ronaldo"),
        ("Lionel Messi", "https://en.wikipedia.org/wiki/Lionel_Messi"),
        ("Robert Lewandowski", "https://en.wikipedia.org/wiki/Robert_Lewandowski"),
        ("Neymar Jr", "https://en.wikipedia.org/wiki/Neymar"),
        ("Erling Haaland", "https://en.wikipedia.org/wiki/Erling_Haaland"),
        # Jogadores adicionais
        ("Kylian Mbappé", "https://en.wikipedia.org/wiki/Kylian_Mbapp%C3%A9"),
        ("Harry Kane", "https://en.wikipedia.org/wiki/Harry_Kane"),
    ]
    
    return pd.DataFrame(players, columns=["name", "link"])


def extract_goals_by_year(url):
    """
    Extrai os gols por ano de um jogador a partir da sua página na Wikipedia.
    
    Args:
        url (str): URL da página do jogador na Wikipedia.
        
    Returns:
        pd.DataFrame: DataFrame com colunas 'year', 'total' e 'type'.
    """
    print(f"Extraindo dados de: {url}")
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extrair tabela de estatísticas de clubes
    club_data = []
    
    # Procurar tabelas com estatísticas de clubes
    club_tables = soup.find_all("table", class_="wikitable")
    
    for table in club_tables:
        # Verificar se é uma tabela de estatísticas
        header_row = table.find("tr")
        if not header_row:
            continue
            
        headers = [th.get_text(strip=True).lower() for th in header_row.find_all(["th", "td"])]
        
        # Verificar se a tabela contém estatísticas de gols
        if any(col in headers for col in ["goals", "total", "season"]):
            season_idx = next((i for i, h in enumerate(headers) if "season" in h), None)
            goals_idx = next((i for i, h in enumerate(headers) if h in ["goals", "total"]), None)
            
            if season_idx is not None and goals_idx is not None:
                for row in table.find_all("tr")[1:]:  # Pular o cabeçalho
                    cells = row.find_all(["td", "th"])
                    if len(cells) <= max(season_idx, goals_idx):
                        continue
                        
                    season_text = cells[season_idx].get_text(strip=True)
                    goals_text = cells[goals_idx].get_text(strip=True)
                    
                    # Extrair o ano da temporada
                    year_match = re.search(r"(\d{4})", season_text)
                    if year_match:
                        year = year_match.group(1)
                        
                        # Extrair o número de gols
                        goals_match = re.search(r"(\d+)", goals_text)
                        if goals_match:
                            goals = int(goals_match.group(1))
                            club_data.append({"year": year, "total": goals, "type": "club"})
    
    # Extrair tabela de estatísticas internacionais
    international_data = []
    
    # Procurar tabelas com estatísticas internacionais
    international_tables = soup.find_all("table", class_="wikitable")
    
    for table in international_tables:
        caption = table.find("caption")
        if caption and "international" in caption.get_text().lower():
            header_row = table.find("tr")
            if not header_row:
                continue
                
            headers = [th.get_text(strip=True).lower() for th in header_row.find_all(["th", "td"])]
            
            year_idx = next((i for i, h in enumerate(headers) if "year" in h), None)
            goals_idx = next((i for i, h in enumerate(headers) if h in ["goals", "total"]), None)
            
            if year_idx is not None and goals_idx is not None:
                for row in table.find_all("tr")[1:]:  # Pular o cabeçalho
                    cells = row.find_all(["td", "th"])
                    if len(cells) <= max(year_idx, goals_idx):
                        continue
                        
                    year_text = cells[year_idx].get_text(strip=True)
                    goals_text = cells[goals_idx].get_text(strip=True)
                    
                    # Extrair o ano
                    year_match = re.search(r"(\d{4})", year_text)
                    if year_match:
                        year = year_match.group(1)
                        
                        # Extrair o número de gols
                        goals_match = re.search(r"(\d+)", goals_text)
                        if goals_match:
                            goals = int(goals_match.group(1))
                            international_data.append({"year": year, "total": goals, "type": "international"})
    
    # Combinar dados de clubes e internacionais
    all_data = pd.DataFrame(club_data + international_data)
    
    # Se não encontrou dados nas tabelas, tentar extrair da seção de estatísticas de carreira
    if all_data.empty:
        career_stats_section = soup.find(id="Career_statistics") or soup.find(string=re.compile("Career statistics"))
        if career_stats_section:
            if isinstance(career_stats_section, str):
                career_stats_section = soup.find("span", string=career_stats_section).parent
                
            # Encontrar a tabela após a seção de estatísticas
            table = career_stats_section.find_next("table")
            if table:
                header_row = table.find("tr")
                if header_row:
                    headers = [th.get_text(strip=True).lower() for th in header_row.find_all(["th", "td"])]
                    
                    season_idx = next((i for i, h in enumerate(headers) if "season" in h), None)
                    goals_idx = next((i for i, h in enumerate(headers) if h in ["goals", "total"]), None)
                    
                    if season_idx is not None and goals_idx is not None:
                        for row in table.find_all("tr")[1:]:  # Pular o cabeçalho
                            cells = row.find_all(["td", "th"])
                            if len(cells) <= max(season_idx, goals_idx):
                                continue
                                
                            season_text = cells[season_idx].get_text(strip=True)
                            goals_text = cells[goals_idx].get_text(strip=True)
                            
                            # Extrair o ano da temporada
                            year_match = re.search(r"(\d{4})", season_text)
                            if year_match:
                                year = year_match.group(1)
                                
                                # Extrair o número de gols
                                goals_match = re.search(r"(\d+)", goals_text)
                                if goals_match:
                                    goals = int(goals_match.group(1))
                                    all_data = all_data.append({"year": year, "total": goals, "type": "club"}, ignore_index=True)
    
    return all_data


def get_player_stats():
    """
    Obtém estatísticas de gols por ano para todos os jogadores ativos.
    
    Returns:
        pd.DataFrame: DataFrame com colunas 'name', 'year', 'total' e 'type'.
    """
    players = get_active_players()
    
    all_stats = []
    
    for _, player in players.iterrows():
        try:
            player_stats = extract_goals_by_year(player["link"])
            if not player_stats.empty:
                player_stats["name"] = player["name"]
                all_stats.append(player_stats)
        except Exception as e:
            print(f"Erro ao extrair dados para {player['name']}: {e}")
    
    if all_stats:
        return pd.concat(all_stats, ignore_index=True)
    else:
        return pd.DataFrame(columns=["name", "year", "total", "type"])
