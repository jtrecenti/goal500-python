"""
Testes para o módulo de visualização.
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
import matplotlib.pyplot as plt

from goal500.visualization.plots import plot_cumulative_goals, create_animation


class TestVisualization(unittest.TestCase):
    """Testes para as funções de visualização."""
    
    def setUp(self):
        """Configura dados de teste."""
        # Criar dados de teste processados
        self.test_data = pd.DataFrame({
            "name": ["Jogador A", "Jogador A", "Jogador B", "Jogador B"],
            "year": [2020, 2021, 2020, 2021],
            "total": [10, 15, 20, 25],
            "type": ["club", "club", "club", "club"]
        })
        
        # DataFrame vazio
        self.empty_data = pd.DataFrame(columns=["name", "year", "total", "type"])
    
    @patch("goal500.visualization.plots.plt.savefig")
    @patch("goal500.visualization.plots.prepare_visualization_data")
    def test_plot_cumulative_goals(self, mock_prepare_data, mock_savefig):
        """Testa a função plot_cumulative_goals."""
        # Configurar mock para prepare_visualization_data
        mock_prepare_data.return_value = pd.DataFrame({
            "name": ["Jogador A", "Jogador A", "Jogador B", "Jogador B"],
            "year": [2020, 2021, 2020, 2021],
            "total": [10, 15, 20, 25],
            "years_active": [0, 1, 0, 1],
            "cumulative_goals": [10, 25, 20, 45],
            "player_label": ["Jogador A (25)", "Jogador A (25)", "Jogador B (45)", "Jogador B (45)"]
        })
        
        # Chamar a função com output_file
        result = plot_cumulative_goals(self.test_data, "test_plot.png")
        
        # Verificar se a função prepare_visualization_data foi chamada
        mock_prepare_data.assert_called_once()
        
        # Verificar se savefig foi chamado com o arquivo correto
        mock_savefig.assert_called_once()
        self.assertIn("test_plot.png", mock_savefig.call_args[0][0])
        
        # Verificar se a função retornou uma figura
        self.assertIsNotNone(result)
        
        # Testar com DataFrame vazio
        mock_prepare_data.return_value = pd.DataFrame()
        result_empty = plot_cumulative_goals(self.empty_data)
        self.assertIsNone(result_empty)
    
    @patch("goal500.visualization.plots.imageio.imread")
    @patch("goal500.visualization.plots.imageio.get_writer")
    @patch("goal500.visualization.plots.plt.savefig")
    @patch("goal500.visualization.plots.prepare_visualization_data")
    @patch("goal500.visualization.plots.os.makedirs")
    @patch("goal500.visualization.plots.os.remove")
    @patch("goal500.visualization.plots.os.rmdir")
    def test_create_animation(self, mock_rmdir, mock_remove, mock_makedirs, 
                             mock_prepare_data, mock_savefig, mock_get_writer, mock_imread):
        """Testa a função create_animation."""
        # Configurar mock para prepare_visualization_data
        mock_prepare_data.return_value = pd.DataFrame({
            "name": ["Jogador A", "Jogador A", "Jogador B", "Jogador B"],
            "year": [2020, 2021, 2020, 2021],
            "total": [10, 15, 20, 25],
            "years_active": [0, 1, 0, 1],
            "cumulative_goals": [10, 25, 20, 45],
            "player_label": ["Jogador A (25)", "Jogador A (25)", "Jogador B (45)", "Jogador B (45)"]
        })
        
        # Configurar mock para get_writer
        mock_writer = MagicMock()
        mock_get_writer.return_value.__enter__.return_value = mock_writer
        
        # Chamar a função
        result = create_animation(self.test_data, "test_animation.gif", fps=1, duration=1)
        
        # Verificar se a função prepare_visualization_data foi chamada
        mock_prepare_data.assert_called_once()
        
        # Verificar se os diretórios foram criados
        mock_makedirs.assert_called_once()
        
        # Verificar se savefig foi chamado para cada frame
        self.assertGreater(mock_savefig.call_count, 0)
        
        # Verificar se get_writer foi chamado com o arquivo correto
        mock_get_writer.assert_called_once()
        self.assertIn("test_animation.gif", mock_get_writer.call_args[0][0])
        
        # Verificar se os arquivos temporários foram removidos
        self.assertGreater(mock_remove.call_count, 0)
        mock_rmdir.assert_called_once()
        
        # Verificar se a função retornou o caminho do arquivo
        self.assertEqual(result, "test_animation.gif")
        
        # Testar com DataFrame vazio
        mock_prepare_data.return_value = pd.DataFrame()
        result_empty = create_animation(self.empty_data)
        self.assertIsNone(result_empty)


if __name__ == "__main__":
    unittest.main()
