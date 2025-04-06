"""
Testes para o módulo de processamento de dados.
"""

import unittest
import pandas as pd
import numpy as np

from goal500.utils.data_processing import clean_data, calculate_cumulative_goals, prepare_visualization_data


class TestDataProcessing(unittest.TestCase):
    """Testes para as funções de processamento de dados."""
    
    def setUp(self):
        """Configura dados de teste."""
        # Criar dados de teste
        self.test_data = pd.DataFrame({
            "name": ["Jogador A", "Jogador A", "Jogador B", "Jogador B"],
            "year": ["2020", "2021", "2020", "2021"],
            "total": ["10", "15", "20", "25"],
            "type": ["club", "club", "club", "club"]
        })
        
        # Dados com valores inválidos
        self.invalid_data = pd.DataFrame({
            "name": ["Jogador A", "Jogador A", "Jogador B", "Jogador B"],
            "year": ["2020", "invalid", "2020", "2021"],
            "total": ["10", "15", "invalid", "25"],
            "type": ["club", "club", "club", "club"]
        })
        
        # DataFrame vazio
        self.empty_data = pd.DataFrame(columns=["name", "year", "total", "type"])
    
    def test_clean_data(self):
        """Testa a função clean_data."""
        # Testar com dados válidos
        result = clean_data(self.test_data)
        
        # Verificar se os tipos de dados foram convertidos corretamente
        self.assertEqual(result["year"].dtype, np.float64)
        self.assertEqual(result["total"].dtype, np.float64)
        
        # Verificar se os valores foram convertidos corretamente
        self.assertEqual(result["year"].iloc[0], 2020)
        self.assertEqual(result["total"].iloc[0], 10)
        
        # Testar com dados inválidos
        result_invalid = clean_data(self.invalid_data)
        
        # Verificar se as linhas inválidas foram removidas
        self.assertEqual(len(result_invalid), 2)
        
        # Testar com DataFrame vazio
        result_empty = clean_data(self.empty_data)
        self.assertTrue(result_empty.empty)
    
    def test_calculate_cumulative_goals(self):
        """Testa a função calculate_cumulative_goals."""
        # Limpar dados de teste
        clean_test_data = clean_data(self.test_data)
        
        # Calcular gols acumulados
        result = calculate_cumulative_goals(clean_test_data)
        
        # Verificar se as colunas esperadas foram criadas
        self.assertIn("years_active", result.columns)
        self.assertIn("cumulative_goals", result.columns)
        self.assertIn("player_label", result.columns)
        
        # Verificar cálculos para Jogador A
        jogador_a = result[result["name"] == "Jogador A"]
        self.assertEqual(jogador_a["years_active"].iloc[0], 0)  # Primeiro ano
        self.assertEqual(jogador_a["years_active"].iloc[1], 1)  # Segundo ano
        self.assertEqual(jogador_a["cumulative_goals"].iloc[0], 10)  # Primeiros gols
        self.assertEqual(jogador_a["cumulative_goals"].iloc[1], 25)  # Gols acumulados
        self.assertEqual(jogador_a["player_label"].iloc[0], "Jogador A (25)")  # Rótulo com total
        
        # Verificar cálculos para Jogador B
        jogador_b = result[result["name"] == "Jogador B"]
        self.assertEqual(jogador_b["cumulative_goals"].iloc[1], 45)  # Gols acumulados
        self.assertEqual(jogador_b["player_label"].iloc[0], "Jogador B (45)")  # Rótulo com total
        
        # Testar com DataFrame vazio
        result_empty = calculate_cumulative_goals(self.empty_data)
        self.assertTrue(result_empty.empty)
    
    def test_prepare_visualization_data(self):
        """Testa a função prepare_visualization_data."""
        # Preparar dados para visualização
        result = prepare_visualization_data(self.test_data)
        
        # Verificar se as colunas esperadas foram criadas
        self.assertIn("years_active", result.columns)
        self.assertIn("cumulative_goals", result.columns)
        self.assertIn("player_label", result.columns)
        
        # Verificar se os dados foram processados corretamente
        self.assertEqual(len(result), 4)  # Mesmo número de linhas que o original
        
        # Testar com dados inválidos
        result_invalid = prepare_visualization_data(self.invalid_data)
        self.assertEqual(len(result_invalid), 2)  # Apenas linhas válidas
        
        # Testar com DataFrame vazio
        result_empty = prepare_visualization_data(self.empty_data)
        self.assertTrue(result_empty.empty)


if __name__ == "__main__":
    unittest.main()
