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

        # Verificar se a função get foi chamada com a URL correta
        mock_get.assert_called_once()
        self.assertEqual(mock_get.call_args.args[0], "https://en.wikipedia.org/wiki/Test")

    @patch("goal500.scrapers.wikipedia.requests.get")
    def test_extract_goals_by_year_parsing(self, mock_get):
        """
        Garante que a extração usa a coluna 'Total Goals' (não a de liga/competitiva)
        e ignora as linhas de subtotal ('Total', 'Career total').
        """
        html = """
        <table>
          <thead><tr>
            <th>Club</th><th>Season</th><th>League Goals</th><th>Total Goals</th>
          </tr></thead>
          <tbody>
            <tr><td>Clube X</td><td>2010-11</td><td>5</td><td>10</td></tr>
            <tr><td>Clube X</td><td>2011-12</td><td>7</td><td>12</td></tr>
            <tr><td>Clube X</td><td>Total</td><td>12</td><td>22</td></tr>
            <tr><td>Career total</td><td>Career total</td><td>12</td><td>22</td></tr>
          </tbody>
        </table>
        <table>
          <thead><tr>
            <th>National team</th><th>Year</th><th>Competitive Goals</th><th>Total Goals</th>
          </tr></thead>
          <tbody>
            <tr><td>Seleção Y</td><td>2012</td><td>2</td><td>4</td></tr>
            <tr><td>Total</td><td>Total</td><td>2</td><td>4</td></tr>
          </tbody>
        </table>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_get.return_value = mock_response

        result = extract_goals_by_year("https://en.wikipedia.org/wiki/Test")

        club = result[result["type"] == "club"]
        intl = result[result["type"] == "international"]

        # Clube: usa 'Total Goals' (10 + 12), não 'League Goals' (5 + 7).
        self.assertEqual(sorted(club["year"].tolist()), ["2010", "2011"])
        self.assertEqual(club["total"].astype(int).sum(), 22)

        # Seleção: usa 'Total Goals' (4), não 'Competitive Goals' (2).
        self.assertEqual(intl["year"].tolist(), ["2012"])
        self.assertEqual(int(intl["total"].iloc[0]), 4)

        # Linhas de subtotal foram ignoradas (2 de clube + 1 de seleção).
        self.assertEqual(len(result), 3)


if __name__ == "__main__":
    unittest.main()
