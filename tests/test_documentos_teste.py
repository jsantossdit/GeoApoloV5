import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

from entidades.documentos_teste import (
    eh_grupo_de_oracao,
    obter_proximo_documento_teste,
    consumir_documento_teste,
)
from entidades.service import EntidadeService


class TestDocumentosTeste(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cpf_csv = Path(self.temp_dir.name) / "cpfs_teste_200.csv"
        self.cnpj_csv = Path(self.temp_dir.name) / "cnpjs_teste_200.csv"

        # Criar CSVs de teste com cabeçalho e dados fictícios
        with open(self.cpf_csv, "w", encoding="utf-8") as f:
            f.write("CPF\n")
            f.write("85746096768\n")
            f.write("01234567890\n")

        with open(self.cnpj_csv, "w", encoding="utf-8") as f:
            f.write("CNPJ\n")
            f.write("11222333000181\n")
            f.write("99888777000166\n")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_eh_grupo_de_oracao_por_categoria(self):
        dados = {"categcodestr": "02.001.005", "geoentnome": "São José"}
        self.assertTrue(eh_grupo_de_oracao("10", dados, None))

    def test_eh_grupo_de_oracao_por_nome(self):
        dados = {"categcodestr": "01.001", "geoentnome": "GRUPO DE ORAÇÃO MARANATHA"}
        self.assertTrue(eh_grupo_de_oracao("11", dados, None))

    def test_eh_grupo_de_oracao_negativo(self):
        dados = {"categcodestr": "01.001", "geoentnome": "JOÃO DA SILVA"}
        mock_repo = MagicMock()
        mock_repo.listar_categorias_entidade.return_value = []
        mock_repo._get_cursor.return_value.fetchone.return_value = None
        self.assertFalse(eh_grupo_de_oracao("12", dados, mock_repo))

    def test_obter_e_consumir_documento_teste_cpf(self):
        with patch("entidades.documentos_teste.obter_caminho_arquivo_teste", return_value=self.cpf_csv):
            doc, path = obter_proximo_documento_teste("F")
            self.assertEqual(doc, "85746096768")
            self.assertEqual(path, self.cpf_csv)

            # Consumir o documento
            consumir_documento_teste(path, doc)

            # Próximo deve ser o segundo
            doc2, _ = obter_proximo_documento_teste("F")
            self.assertEqual(doc2, "01234567890")

    def test_obter_e_consumir_documento_teste_cnpj(self):
        with patch("entidades.documentos_teste.obter_caminho_arquivo_teste", return_value=self.cnpj_csv):
            doc, path = obter_proximo_documento_teste("J")
            self.assertEqual(doc, "11222333000181")
            self.assertEqual(path, self.cnpj_csv)

            consumir_documento_teste(path, doc)

            doc2, _ = obter_proximo_documento_teste("J")
            self.assertEqual(doc2, "99888777000166")

    def test_exportacao_grupo_oracao_atribui_e_consome_doc_com_sucesso(self):
        mock_repo = MagicMock()
        mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "500",
            "geoentnome": "GRUPO DE ORAÇÃO PENTECOSTES",
            "enttipofj": "F",
            "entobservacoes": "",
            "categcodestr": "02.001",
        }
        # Inicialmente sem documento
        mock_repo.obter_cpf_rg_documentos.return_value = ("", "")
        mock_repo.listar_categorias_entidade.return_value = [{"categcodestr": "02.001"}]
        mock_repo.listar_telefones_entidade.return_value = []
        mock_repo.carregar_contatos_entidade.return_value = []
        mock_repo.listar_webcontatos_entidade.return_value = []
        mock_repo.vincular_entcod.return_value = True

        service = EntidadeService(mock_repo)

        mock_api = MagicMock()
        mock_api.garantir_autenticacao.return_value = True
        mock_api.inserir_alterar_entidade.return_value = (True, '{"entcod": "999"}', {"entcod": "999"})
        mock_api.extrair_entcod_resposta.return_value = "999"

        with patch("entidades.documentos_teste.obter_caminho_arquivo_teste", return_value=self.cpf_csv):
            res = service.exportar_entidade_para_alvo(
                geoentcod="500",
                usuario_alvo="USU_ALVO",
                senha_alvo_plana="senha123",
                api_client=mock_api,
            )

            self.assertTrue(res.sucesso)
            # Verifica que salvou no repositório com o primeiro CPF do CSV (85746096768)
            mock_repo.salvar_documento_entidade.assert_called_once_with(
                "500", tipo="CPF/CNPJ", documento="85746096768", observacoes="TESTE AUTO"
            )
            # Verifica que o CSV agora tem apenas o cabeçalho e o segundo CPF
            with open(self.cpf_csv, "r", encoding="utf-8") as f:
                linhas = [l.strip() for l in f if l.strip()]
            self.assertEqual(linhas, ["CPF", "01234567890"])

    def test_exportacao_grupo_oracao_nao_consome_se_api_falhar(self):
        mock_repo = MagicMock()
        mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "501",
            "geoentnome": "GRUPO DE ORAÇÃO CENÁCULO",
            "enttipofj": "F",
            "entobservacoes": "",
            "categcodestr": "02.001",
        }
        mock_repo.obter_cpf_rg_documentos.return_value = ("", "")
        mock_repo.listar_categorias_entidade.return_value = [{"categcodestr": "02.001"}]
        mock_repo.listar_telefones_entidade.return_value = []
        mock_repo.carregar_contatos_entidade.return_value = []
        mock_repo.listar_webcontatos_entidade.return_value = []

        service = EntidadeService(mock_repo)

        mock_api = MagicMock()
        mock_api.garantir_autenticacao.return_value = True
        mock_api.inserir_alterar_entidade.return_value = (False, 'Erro de conexão com Alvo', {})
        mock_api.extrair_entcod_resposta.return_value = None

        with patch("entidades.documentos_teste.obter_caminho_arquivo_teste", return_value=self.cpf_csv):
            res = service.exportar_entidade_para_alvo(
                geoentcod="501",
                usuario_alvo="USU_ALVO",
                senha_alvo_plana="senha123",
                api_client=mock_api,
            )

            self.assertFalse(res.sucesso)
            # Como falhou a exportação na API, o CSV NÃO pode ter tido o CPF consumido
            with open(self.cpf_csv, "r", encoding="utf-8") as f:
                linhas = [l.strip() for l in f if l.strip()]
            self.assertEqual(linhas, ["CPF", "85746096768", "01234567890"])

    def test_contar_documentos_restantes_cpf_e_cnpj(self):
        from entidades.documentos_teste import contar_documentos_restantes

        with patch("entidades.documentos_teste.obter_caminho_arquivo_teste", return_value=self.cpf_csv):
            qtd, path, desc = contar_documentos_restantes("F")
            self.assertEqual(qtd, 2)
            self.assertEqual(path, self.cpf_csv)
            self.assertEqual(desc, "CPFs")

        with patch("entidades.documentos_teste.obter_caminho_arquivo_teste", return_value=self.cnpj_csv):
            qtd, path, desc = contar_documentos_restantes("J")
            self.assertEqual(qtd, 2)
            self.assertEqual(path, self.cnpj_csv)
            self.assertEqual(desc, "CNPJs")

    def test_verificar_alerta_poucos_documentos(self):
        from entidades.documentos_teste import verificar_alerta_poucos_documentos

        # Com 2 documentos no CSV e limite=5, deve alertar
        with patch("entidades.documentos_teste.obter_caminho_arquivo_teste", return_value=self.cpf_csv):
            alerta = verificar_alerta_poucos_documentos("F", limite=5)
            self.assertIsNotNone(alerta)
            self.assertIn("está quase no fim", alerta)
            self.assertIn("Restam apenas 2 registros disponíveis", alerta)

        # Com limite=1, não deve alertar pois temos 2 documentos
        with patch("entidades.documentos_teste.obter_caminho_arquivo_teste", return_value=self.cpf_csv):
            alerta = verificar_alerta_poucos_documentos("F", limite=1)
            self.assertIsNone(alerta)

    def test_comparar_cadastros_sugere_manter_sve_quando_cpf_preenchido_apenas_sve(self):
        from entidades.models import DecisaoLinha

        service = EntidadeService(None)
        sve_data = {
            "entcod": "123",
            "geoentcod": "500",
            "geoentnome": "GRUPO DE ORAÇÃO MARANATHA",
            "Documento": "85746096768",
        }
        alvo_data = {
            "entcod": "123",
            "entnome": "GRUPO DE ORAÇÃO MARANATHA",
            "EntCpfCgc": "",
        }

        difs = service.comparar_cadastros(sve_data, alvo_data, incluir_referencias=True)
        item_cpf = next((d for d in difs if d.rotulo == "CPF / CNPJ"), None)
        self.assertIsNotNone(item_cpf)
        self.assertTrue(item_cpf.eh_diferente)
        self.assertEqual(item_cpf.decisao, DecisaoLinha.MANTER_SVE)

    @patch("tkinter.messagebox.showwarning")
    @patch("tkinter.messagebox.askyesno", return_value=True)
    def test_acao_exportar_entidade_existente_sem_documento_consome_e_atualiza_grid(self, mock_ask, mock_warn):
        from entidades.view import EntidadesView

        mock_repo = MagicMock()
        # Entidade existente no Alvo com entcod="333" e Grupo de Oração
        mock_repo.obter_cpf_rg_documentos.return_value = ("", "")
        mock_repo.carregar_dados_comparacao.return_value = (
            {"geoentcod": "100", "entcod": "333", "geoentnome": "GRUPO DE ORAÇÃO TESTE", "Documento": ""},
            {"entcod": "333", "entnome": "GRUPO DE ORAÇÃO TESTE", "EntCpfCgc": ""},
        )
        mock_service = EntidadeService(mock_repo)

        # Mock de EntidadesView sem instanciar GUI real
        with patch.object(EntidadesView, "__init__", return_value=None):
            view = EntidadesView()
            view._repo = mock_repo
            view._service = mock_service
            view._api_client = MagicMock()
            view.tree = MagicMock()
            view.tree.selection.return_value = ["I001"]
            view.combo_base = MagicMock()
            view.combo_base.get.return_value = "GeoApolo"
            view._abrir_tela_comparacao = MagicMock()

            reg = {
                "geoentcod": "100",
                "entcod": "333",
                "geoentnome": "GRUPO DE ORAÇÃO TESTE",
                "enttipofj": "F",
                "categcodestr": "02.001",
                "entcpfcgc": "",
            }
            view._obter_registro_selecionado = MagicMock(return_value=reg)

            with patch("entidades.documentos_teste.obter_caminho_arquivo_teste", return_value=self.cpf_csv):
                view._acao_exportar()

                # Verifica que emitiu o alerta pois o CSV tem apenas 2 itens (<= 5)
                mock_warn.assert_called_once()
                alerta_msg = mock_warn.call_args[0][1]
                self.assertIn("está quase no fim", alerta_msg)

                # Verifica que consumiu o primeiro CPF (85746096768) do CSV
                with open(self.cpf_csv, "r", encoding="utf-8") as f:
                    linhas = [l.strip() for l in f if l.strip()]
                self.assertEqual(linhas, ["CPF", "01234567890"])

                # Verifica que salvou no repositório
                mock_repo.salvar_documento_entidade.assert_called_once_with(
                    "100", tipo="CPF/CNPJ", documento="85746096768", observacoes="TESTE AUTO"
                )

                # Verifica que atualizou a grid principal
                view.tree.set.assert_called_once_with("I001", "documento", "85746096768")

                # Verifica que abriu a tela de comparação com o novo documento no sve_data
                view._abrir_tela_comparacao.assert_called_once()
                sve_passado = view._abrir_tela_comparacao.call_args[1]["sve_data"]
                self.assertEqual(sve_passado["Documento"], "85746096768")


if __name__ == "__main__":
    unittest.main()
