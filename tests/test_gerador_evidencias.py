# -*- coding: utf-8 -*-
"""
Testes unitários para o gerador e executor de evidências de testes.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock

PASTA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PASTA_RAIZ not in sys.path:
    sys.path.insert(0, PASTA_RAIZ)

from executar_testes_com_evidencias import (
    CasoTesteEvidencia,
    ColetorEvidenciasTestResult,
    GeradorRelatorioEvidencias,
    executar_testes,
)


class TestGeradorEvidencias(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.destino = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_caso_teste_evidencia_para_dicionario(self):
        caso = CasoTesteEvidencia(
            test_id="modulo.Classe.test_exemplo",
            nome="test_exemplo",
            modulo="modulo",
            classe="Classe",
            docstring="Testa cenário de exemplo.",
        )
        caso.status = "SUCESSO"
        caso.tempo_execucao = 0.04567

        d = caso.para_dicionario()
        self.assertEqual(d["test_id"], "modulo.Classe.test_exemplo")
        self.assertEqual(d["nome"], "test_exemplo")
        self.assertEqual(d["status"], "SUCESSO")
        self.assertEqual(d["tempo_execucao"], 0.0457)
        self.assertEqual(d["docstring"], "Testa cenário de exemplo.")

    def test_coletor_evidencias_ciclo_de_vida(self):
        coletor = ColetorEvidenciasTestResult()

        # Mock de teste com sucesso
        mock_test_ok = MagicMock()
        mock_test_ok.id.return_value = "tests.test_mock.TestMock.test_ok"
        mock_test_ok._testMethodDoc = "Teste com sucesso"

        coletor.startTest(mock_test_ok)
        coletor.addSuccess(mock_test_ok)
        coletor.stopTest(mock_test_ok)

        # Mock de teste com falha
        mock_test_fail = MagicMock()
        mock_test_fail.id.return_value = "tests.test_mock.TestMock.test_fail"
        mock_test_fail._testMethodDoc = "Teste com falha"

        coletor.startTest(mock_test_fail)
        try:
            raise AssertionError("Valor divergente")
        except AssertionError as e:
            err = (AssertionError, e, sys.exc_info()[2])
            coletor.addFailure(mock_test_fail, err)
        coletor.stopTest(mock_test_fail)

        # Mock de teste com skip
        mock_test_skip = MagicMock()
        mock_test_skip.id.return_value = "tests.test_mock.TestMock.test_skip"
        mock_test_skip._testMethodDoc = "Teste ignorado"

        coletor.startTest(mock_test_skip)
        coletor.addSkip(mock_test_skip, "Ignorado por condicao")
        coletor.stopTest(mock_test_skip)

        metricas = coletor.consolidar_metricas()
        self.assertEqual(metricas["total"], 3)
        self.assertEqual(metricas["sucessos"], 1)
        self.assertEqual(metricas["falhas"], 1)
        self.assertEqual(metricas["erros"], 0)
        self.assertEqual(metricas["ignorados"], 1)
        self.assertAlmostEqual(metricas["taxa_sucesso"], 33.33, places=1)

    def test_gerar_arquivos_html_markdown_log(self):
        dados_exemplo = {
            "total": 2,
            "sucessos": 1,
            "falhas": 1,
            "erros": 0,
            "ignorados": 0,
            "taxa_sucesso": 50.0,
            "duracao_segundos": 1.25,
            "data_hora": "04/10/2026 02:00:00",
            "sistema_operacional": "Windows-10",
            "python_versao": "3.12.0",
            "arquitetura": "64bit",
            "evidencias": [
                {
                    "test_id": "tests.test_demo.TestDemo.test_sucesso",
                    "nome": "test_sucesso",
                    "modulo": "test_demo",
                    "classe": "TestDemo",
                    "docstring": "Verifica sucesso",
                    "status": "SUCESSO",
                    "tempo_execucao": 0.05,
                    "mensagem_erro": "",
                    "traceback_erro": "",
                },
                {
                    "test_id": "tests.test_demo.TestDemo.test_falha",
                    "nome": "test_falha",
                    "modulo": "test_demo",
                    "classe": "TestDemo",
                    "docstring": "Verifica falha",
                    "status": "FALHA",
                    "tempo_execucao": 0.08,
                    "mensagem_erro": "Comparacao invalida",
                    "traceback_erro": "Traceback:\n  File test_demo.py: AssertionError",
                },
            ],
        }

        # 1. HTML
        caminho_html = os.path.join(self.destino, "relatorio.html")
        GeradorRelatorioEvidencias.gerar_html(dados_exemplo, caminho_html)
        self.assertTrue(os.path.exists(caminho_html))
        with open(caminho_html, "r", encoding="utf-8") as f:
            conteudo_html = f.read()
        self.assertIn("Relatório de Evidências de Testes", conteudo_html)
        self.assertIn("test_sucesso", conteudo_html)
        self.assertIn("test_falha", conteudo_html)
        self.assertIn("50.0%", conteudo_html)
        self.assertIn("REPROVADO", conteudo_html)

        # 2. Markdown
        caminho_md = os.path.join(self.destino, "relatorio.md")
        GeradorRelatorioEvidencias.gerar_markdown(dados_exemplo, caminho_md)
        self.assertTrue(os.path.exists(caminho_md))
        with open(caminho_md, "r", encoding="utf-8") as f:
            conteudo_md = f.read()
        self.assertIn("# Relatório de Evidências de Testes", conteudo_md)
        self.assertIn("**Aprovados**", conteudo_md)
        self.assertIn("**Falhas**", conteudo_md)
        self.assertIn("Comparacao invalida", conteudo_md)

        # 3. Log
        caminho_log = os.path.join(self.destino, "relatorio.log")
        GeradorRelatorioEvidencias.gerar_log(dados_exemplo, caminho_log)
        self.assertTrue(os.path.exists(caminho_log))
        with open(caminho_log, "r", encoding="utf-8") as f:
            conteudo_log = f.read()
        self.assertIn("RELATORIO DE EVIDENCIAS DE TESTES", conteudo_log)
        self.assertIn("[SUCESSO] tests.test_demo.TestDemo.test_sucesso", conteudo_log)
        self.assertIn("[FALHA] tests.test_demo.TestDemo.test_falha", conteudo_log)

    def test_executar_testes_com_destino_customizado(self):
        # Executar apenas uma classe simples
        dados = executar_testes(
            alvo="tests.test_gerador_evidencias.TestGeradorEvidencias.test_caso_teste_evidencia_para_dicionario",
            pasta_destino=self.destino,
        )
        self.assertEqual(dados["total"], 1)
        self.assertEqual(dados["sucessos"], 1)
        self.assertEqual(dados["falhas"], 0)

        # Verificar se os arquivos foram criados na pasta de destino
        self.assertTrue(os.path.exists(os.path.join(self.destino, "ultima_evidencia_testes.html")))
        self.assertTrue(os.path.exists(os.path.join(self.destino, "RELATORIO_EVIDENCIAS_TESTES.md")))

        pasta_hist = os.path.join(self.destino, "evidencias_testes")
        self.assertTrue(os.path.isdir(pasta_hist))
        arquivos_hist = os.listdir(pasta_hist)
        self.assertTrue(any(f.endswith(".html") for f in arquivos_hist))
        self.assertTrue(any(f.endswith(".log") for f in arquivos_hist))


if __name__ == "__main__":
    unittest.main()
