"""
Testes para o módulo de raspagem da Wikipedia.
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

from goal500.scrapers.wikipedia import get_active_players, wiki_url, extract_goals_by_year


class TestWikipedia(unittest.TestCase):
    """Testes para as funções de raspagem da Wikipedia."""
    
    def test_wiki_url(self):
        """Testa a função wiki_url."""
        self.assertEqual(wiki_url("/wiki/Test"), "https://en.wikipedia.org/wiki/Test")
        self.assertEqual(wiki_url(""), "https://en.wikipedia.org")
    
    def test_get_active_players(self):
        """Testa a função get_active_players."""
        players = get_active_players()
        
        # Verificar se é um DataFrame
        self.assertIsInstance(players, pd.DataFrame)
        
        # Verificar se tem as colunas corretas
        self.assertIn("name", players.columns)
        self.assertIn("link", players.columns)
        
        # Verificar se contém os jogadores esperados
        player_names = players["name"].tolist()
        self.assertIn("Cristiano Ronaldo", player_names)
        self.assertIn("Lionel Messi", player_names)
        self.assertIn("Kylian Mbappé", player_names)
        self.assertIn("Harry Kane", player_names)
        
        # Verificar se os links são válidos
        for link in players["link"]:
            self.assertTrue(link.startswith("https://en.wikipedia.org/wiki/"))
    
    @patch("goal500.scrapers.wikipedia.requests.get")
    def test_extract_goals_by_year_empty(self, mock_get):
        """Testa a função extract_goals_by_year com resposta vazia."""
        # Configurar o mock
        mock_response = MagicMock()
        mock_response.text = "<html><body></body></html>"
        mock_get.return_value = mock_response
        
        # Chamar a função
        result = extract_goals_by_year("https://en.wikipedia.org/wiki/Test")
        
        # Verificar o resultado
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)
        
        # Verificar se a função get foi chamada corretamente
        mock_get.assert_called_once_with("https://en.wikipedia.org/wiki/Test")


if __name__ == "__main__":
    unittest.main()
