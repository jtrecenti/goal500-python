"""
Testes para a interface de linha de comando.
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import sys

from goal500.cli import main


class TestCLI(unittest.TestCase):
    """Testes para a interface de linha de comando."""
    
    @patch("goal500.cli.get_player_stats")
    @patch("goal500.cli.sys.argv", ["goal500", "extract", "--output", "test_output.csv"])
    def test_extract_command(self, mock_get_player_stats):
        """Testa o comando extract."""
        # Configurar mock para get_player_stats
        mock_data = pd.DataFrame({
            "name": ["Jogador A", "Jogador B"],
            "year": [2020, 2021],
            "total": [10, 20],
            "type": ["club", "club"]
        })
        mock_get_player_stats.return_value = mock_data
        
        # Configurar mock para DataFrame.to_csv
        with patch.object(pd.DataFrame, "to_csv") as mock_to_csv:
            # Chamar a função
            main()
            
            # Verificar se get_player_stats foi chamado
            mock_get_player_stats.assert_called_once()
            
            # Verificar se to_csv foi chamado com o arquivo correto
            mock_to_csv.assert_called_once()
            self.assertEqual(mock_to_csv.call_args[0][0], "test_output.csv")
    
    @patch("goal500.cli.plot_cumulative_goals")
    @patch("goal500.cli.pd.read_csv")
    @patch("goal500.cli.sys.argv", ["goal500", "plot", "--input", "test_input.csv", "--output", "test_plot.png"])
    def test_plot_command(self, mock_read_csv, mock_plot):
        """Testa o comando plot."""
        # Configurar mock para read_csv
        mock_data = pd.DataFrame({
            "name": ["Jogador A", "Jogador B"],
            "year": [2020, 2021],
            "total": [10, 20],
            "type": ["club", "club"]
        })
        mock_read_csv.return_value = mock_data
        
        # Chamar a função
        main()
        
        # Verificar se read_csv foi chamado com o arquivo correto
        mock_read_csv.assert_called_once_with("test_input.csv")
        
        # Verificar se plot_cumulative_goals foi chamado com os parâmetros corretos
        mock_plot.assert_called_once()
        self.assertEqual(mock_plot.call_args[0][1], "test_plot.png")
    
    @patch("goal500.cli.create_animation")
    @patch("goal500.cli.pd.read_csv")
    @patch("goal500.cli.sys.argv", ["goal500", "animate", "--input", "test_input.csv", "--output", "test_animation.gif"])
    def test_animate_command(self, mock_read_csv, mock_animate):
        """Testa o comando animate."""
        # Configurar mock para read_csv
        mock_data = pd.DataFrame({
            "name": ["Jogador A", "Jogador B"],
            "year": [2020, 2021],
            "total": [10, 20],
            "type": ["club", "club"]
        })
        mock_read_csv.return_value = mock_data
        
        # Chamar a função
        main()
        
        # Verificar se read_csv foi chamado com o arquivo correto
        mock_read_csv.assert_called_once_with("test_input.csv")
        
        # Verificar se create_animation foi chamado com os parâmetros corretos
        mock_animate.assert_called_once()
        self.assertEqual(mock_animate.call_args[0][1], "test_animation.gif")
    
    @patch("goal500.cli.pd.read_csv")
    @patch("goal500.cli.sys.exit")
    @patch("goal500.cli.sys.argv", ["goal500", "plot", "--input", "nonexistent.csv"])
    def test_file_not_found(self, mock_exit, mock_read_csv):
        """Testa o comportamento quando o arquivo não é encontrado."""
        # Configurar mock para read_csv para lançar FileNotFoundError
        mock_read_csv.side_effect = FileNotFoundError()
        
        # Chamar a função
        main()
        
        # Verificar se sys.exit foi chamado com código 1
        mock_exit.assert_called_once_with(1)
    
    @patch("goal500.cli.argparse.ArgumentParser.print_help")
    @patch("goal500.cli.sys.argv", ["goal500"])
    def test_no_command(self, mock_print_help):
        """Testa o comportamento quando nenhum comando é fornecido."""
        # Chamar a função
        main()
        
        # Verificar se print_help foi chamado
        mock_print_help.assert_called_once()


if __name__ == "__main__":
    unittest.main()
