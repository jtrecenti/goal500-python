"""
Testes para o módulo de geração dos dados da página estática (site.py).
"""

import json
import os
import tempfile
import unittest

import pandas as pd

from goal500.site import build_site_data, write_site_data


class TestSite(unittest.TestCase):
    """Testes para build_site_data e write_site_data."""

    def setUp(self):
        # Jogador A: 2 temporadas de clube + 1 de seleção.
        # Jogador B: 1 temporada de clube (com duas linhas no mesmo ano).
        self.test_data = pd.DataFrame({
            "name": ["Jogador A", "Jogador A", "Jogador A",
                     "Jogador B", "Jogador B"],
            "year": [2020, 2021, 2020, 2019, 2019],
            "total": [10, 15, 3, 5, 7],
            "type": ["club", "club", "international", "club", "club"],
        })
        self.empty_data = pd.DataFrame(columns=["name", "year", "total", "type"])

    def test_build_structure(self):
        """A estrutura de saída tem os campos esperados."""
        data = build_site_data(self.test_data)
        self.assertIn("players", data)
        self.assertIn("generated_at", data)
        self.assertEqual(data["source"], "Wikipedia")
        self.assertEqual(len(data["players"]), 2)

    def test_totals_and_ordering(self):
        """Totais são somados corretamente e ordenados por total (desc)."""
        data = build_site_data(self.test_data)
        players = {p["name"]: p for p in data["players"]}

        a = players["Jogador A"]
        self.assertEqual(a["total_club"], 25)          # 10 + 15
        self.assertEqual(a["total_international"], 3)
        self.assertEqual(a["total"], 28)
        self.assertEqual(a["first_year"], 2020)
        self.assertEqual(a["last_year"], 2021)

        b = players["Jogador B"]
        # Duas linhas do mesmo ano são somadas: 5 + 7 = 12.
        self.assertEqual(b["total_club"], 12)
        self.assertEqual(b["total_international"], 0)

        # Jogador A (28) deve vir antes de Jogador B (12).
        self.assertEqual(data["players"][0]["name"], "Jogador A")

    def test_aligned_arrays(self):
        """Os arrays club/international têm o mesmo tamanho de years."""
        data = build_site_data(self.test_data)
        for p in data["players"]:
            self.assertEqual(len(p["club"]), len(p["years"]))
            self.assertEqual(len(p["international"]), len(p["years"]))

    def test_colors_present(self):
        """Cada jogador tem cor para tema claro e escuro."""
        data = build_site_data(self.test_data)
        for p in data["players"]:
            self.assertTrue(p["color"].startswith("#"))
            self.assertTrue(p["color_dark"].startswith("#"))

    def test_empty(self):
        """DataFrame vazio produz lista de jogadores vazia."""
        data = build_site_data(self.empty_data)
        self.assertEqual(data["players"], [])

    def test_write_file(self):
        """write_site_data escreve um JSON válido no caminho indicado."""
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "sub", "data.json")
            write_site_data(self.test_data, out)
            self.assertTrue(os.path.exists(out))
            with open(out, encoding="utf-8") as fh:
                loaded = json.load(fh)
            self.assertEqual(len(loaded["players"]), 2)


if __name__ == "__main__":
    unittest.main()
