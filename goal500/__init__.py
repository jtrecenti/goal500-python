"""
goal500 - Extrai dados de gols acumulados por ano de jogadores de futebol da Wikipedia
"""

from goal500.scrapers.wikipedia import get_player_stats
from goal500.visualization.plots import plot_cumulative_goals, create_animation

__version__ = "0.1.0"
__all__ = ["get_player_stats", "plot_cumulative_goals", "create_animation"]
