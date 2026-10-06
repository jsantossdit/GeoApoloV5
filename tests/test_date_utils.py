"""
Testes Unitários para Utilitários Corporativos de Data (core/date_utils.py).
Validação do padrão brasileiro DD/MM/AAAA, conversão ISO para banco de dados e tolerância de formatos.
"""

import unittest
from datetime import datetime, date
from core.date_utils import (
    formatar_data_br,
    converter_data_br_para_iso,
    parse_data_flexivel,
    validar_data_br,
)


class TestDateUtils(unittest.TestCase):
    def test_formatar_data_br_a_partir_de_objeto_date(self):
        d = date(2026, 9, 27)
        self.assertEqual(formatar_data_br(d), "27/09/2026")

    def test_formatar_data_br_a_partir_de_objeto_datetime(self):
        dt = datetime(2026, 9, 27, 14, 35, 10)
        self.assertEqual(formatar_data_br(dt), "27/09/2026")
        self.assertEqual(formatar_data_br(dt, incluir_hora=True), "27/09/2026 14:35")
        self.assertEqual(formatar_data_br(dt, incluir_segundos=True), "27/09/2026 14:35:10")

    def test_formatar_data_br_a_partir_de_string_iso(self):
        # Data pura
        self.assertEqual(formatar_data_br("2026-09-27"), "27/09/2026")
        # Data e hora com espaço
        self.assertEqual(formatar_data_br("2026-09-27 10:20:30"), "27/09/2026")
        self.assertEqual(formatar_data_br("2026-09-27 10:20:30", incluir_hora=True), "27/09/2026 10:20")
        # Formato ISO com T
        self.assertEqual(formatar_data_br("2026-09-27T10:20:30.000Z"), "27/09/2026")

    def test_formatar_data_br_quando_ja_estiver_em_br(self):
        self.assertEqual(formatar_data_br("27/09/2026"), "27/09/2026")
        self.assertEqual(formatar_data_br("27/09/2026 15:40:00", incluir_hora=True), "27/09/2026 15:40")

    def test_converter_data_br_para_iso(self):
        self.assertEqual(converter_data_br_para_iso("27/09/2026"), "2026-09-27")
        self.assertEqual(converter_data_br_para_iso("27/09/2026", fim_do_dia=True), "2026-09-27 23:59:59")
        # Já em ISO
        self.assertEqual(converter_data_br_para_iso("2026-09-27"), "2026-09-27")
        self.assertEqual(converter_data_br_para_iso("2026-09-27", fim_do_dia=True), "2026-09-27 23:59:59")
        # Vazio
        self.assertEqual(converter_data_br_para_iso(""), "")
        self.assertEqual(converter_data_br_para_iso(None), "")

    def test_parse_data_flexivel(self):
        d1 = parse_data_flexivel("27/09/2026")
        self.assertEqual(d1, date(2026, 9, 27))

        d2 = parse_data_flexivel("2026-09-27")
        self.assertEqual(d2, date(2026, 9, 27))

        d3 = parse_data_flexivel("27-09-2026")
        self.assertEqual(d3, date(2026, 9, 27))

        self.assertIsNone(parse_data_flexivel("invalido"))
        self.assertIsNone(parse_data_flexivel(""))

    def test_validar_data_br(self):
        self.assertTrue(validar_data_br("27/09/2026"))
        self.assertTrue(validar_data_br("29/02/2024"))  # Ano bissexto válido
        self.assertFalse(validar_data_br("29/02/2025"))  # Ano não bissexto inválido
        self.assertFalse(validar_data_br("32/01/2026"))
        self.assertFalse(validar_data_br("2026-09-27"))
        self.assertFalse(validar_data_br(""))


if __name__ == "__main__":
    unittest.main()
