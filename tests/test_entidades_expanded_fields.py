"""
Testes unitários para expansão de campos de busca, ordenação e treeview em Entidades,
além da verificação de persistência de log de erro de exportação na pasta do executável.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from core.error_logger import obter_diretorio_executavel, salvar_log_erro_executavel
from entidades.models import EntidadeFiltro
from entidades.repository import MAPA_COLUNAS, EntidadeRepository
from entidades.view import MAPA_CAMPOS_BUSCA_UI, MAPA_ORDEM_UI
from savic.moderacao_repository import SavicModeracaoRepository
from savic.moderacao_service import SavicModeracaoService
from savic.moderacao_models import CoordenadorModeracaoDTO


class TestErrorLogger(unittest.TestCase):
    """Testa a geração e gravação de logs de erro na pasta do executável."""

    def test_obter_diretorio_executavel(self):
        diretorio = obter_diretorio_executavel()
        self.assertTrue(os.path.isdir(diretorio))

    def test_salvar_log_erro_executavel(self):
        nome_temp = "test_exportacao_erro_temp.log"
        try:
            caminho = salvar_log_erro_executavel(
                nome_arquivo=nome_temp,
                titulo="Teste Unitário de Exportação",
                erro=ValueError("Simulação de falha de teste"),
                contexto="Detalhes de teste de exportação"
            )
            self.assertTrue(os.path.exists(caminho))
            with open(caminho, "r", encoding="utf-8") as f:
                conteudo = f.read()
            self.assertIn("Simulação de falha de teste", conteudo)
            self.assertIn("Teste Unitário de Exportação", conteudo)
            self.assertIn("Detalhes de teste de exportação", conteudo)
        finally:
            pasta = obter_diretorio_executavel()
            caminho_temp = os.path.join(pasta, nome_temp)
            if os.path.exists(caminho_temp):
                try:
                    os.remove(caminho_temp)
                except Exception:
                    pass


class TestEntidadesExpandedFields(unittest.TestCase):
    """Testa o suporte a campos expandidos de busca e ordenação."""

    def test_mapa_campos_busca_ui_contem_campos_essenciais(self):
        campos_obrigatorios = [
            "Razão Social / Nome",
            "Nome Fantasia",
            "CPF / CNPJ",
            "RG / Inscrição Estadual",
            "Endereço / Logradouro",
            "Número",
            "Complemento",
            "Bairro",
            "Cidade",
            "UF / Estado",
            "CEP",
            "Código GeoApolo",
            "entcod",
            "Categoria(s)",
            "Cargo",
            "Diocese",
        ]
        for c in campos_obrigatorios:
            self.assertIn(c, MAPA_CAMPOS_BUSCA_UI)
            self.assertTrue(len(MAPA_CAMPOS_BUSCA_UI[c]) > 0)
        # Compatibilidade com termo anterior
        self.assertIn("Código Alvo", MAPA_CAMPOS_BUSCA_UI)
        self.assertIn("entcod", MAPA_ORDEM_UI)

    def test_mapa_colunas_repository(self):
        self.assertEqual(MAPA_COLUNAS["nome_fantasia"], "entnomefant")
        self.assertEqual(MAPA_COLUNAS["cpf"], "EntCpfCgc")
        self.assertEqual(MAPA_COLUNAS["rg_ie"], "EntRgIe")
        self.assertEqual(MAPA_COLUNAS["bairro"], "entbair")
        self.assertEqual(MAPA_COLUNAS["cidade"], "cidnomecomp")
        self.assertEqual(MAPA_COLUNAS["uf"], "ufsigla")
        self.assertEqual(MAPA_COLUNAS["categoria"], "categnome")
        self.assertEqual(MAPA_COLUNAS["diocese"], "USERNomeDiocese")

    def test_consultar_lista_com_busca_geoapolo(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.description = [("geoentcod",), ("entnome",), ("entnomefant",), ("EntCpfCgc",)]
        mock_cur.fetchall.return_value = [("00000001", "TESTE ENTIDADE", "TESTE FANTASIA", "12345678900")]

        repo = EntidadeRepository(mock_conn)
        filtro = EntidadeFiltro(
            base_dados="GeoApolo",
            campo_busca="nome_fantasia",
            texto_busca="FANTASIA",
            campo_ordenacao="nome_fantasia",
            ordem_asc=True,
            limite=50
        )
        res = repo.consultar_lista(filtro)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["geoentcod"], "00000001")
        # Verifica se o SQL utilizou o campo mapeado
        sql_executado = mock_cur.execute.call_args[0][0]
        self.assertIn("e.entnomefant LIKE ?", sql_executado)

    def test_consultar_lista_com_busca_cpf_sanitizado(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.description = [("geoentcod",), ("entnome",), ("EntCpfCgc",), ("status_sincronizacao",)]
        mock_cur.fetchall.return_value = [("48431", "BEATA ELENA GUERRA", "87454033504", "S")]

        repo = EntidadeRepository(mock_conn)
        filtro = EntidadeFiltro(
            base_dados="GeoApolo",
            campo_busca="cpf",
            texto_busca="87454033504",
            tipo_pesquisa="Especifica",
            limite=50
        )
        res = repo.consultar_lista(filtro)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["geoentcod"], "48431")
        sql_executado = mock_cur.execute.call_args[0][0]
        # Verifica se usa sanitização de documento para comparação resiliente
        self.assertIn("REPLACE", sql_executado)
        # Verifica que em busca específica não força atualizou_apolo = 'N'
        self.assertNotIn("e.atualizou_apolo = 'N'", sql_executado)

    @patch("entidades.view.EntidadeRepository")
    @patch("entidades.view.EntidadeService")
    def test_entidades_view_limpar_busca(self, mock_srv, mock_repo):
        import tkinter as tk
        from entidades.view import EntidadesView
        root = tk.Tk()
        root.withdraw()
        try:
            view = EntidadesView(root)
            view.entry_busca.insert(0, "87454033504")
            view.combo_campo.set("CPF / CNPJ")
            view.var_filtro_exportada.set("TODAS")
            
            with patch.object(view, "_carregar_dados") as mock_carregar:
                view._limpar_busca()
                self.assertEqual(view.entry_busca.get(), "")
                self.assertEqual(view.combo_campo.get(), "Razão Social / Nome")
                self.assertEqual(view.var_filtro_exportada.get(), "PENDENTES")
                self.assertTrue(mock_carregar.called)
        finally:
            root.destroy()


class TestSavicExportacaoResiliencia(unittest.TestCase):
    """Testa a resiliência e correção de métodos na moderação do SAVIC."""

    def test_assegurar_colunas_exportado_executa_sem_erro(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        repo = SavicModeracaoRepository(mock_conn)
        repo.assegurar_colunas_exportado()
        self.assertTrue(mock_cur.execute.called)
        self.assertTrue(mock_conn.commit.called)

    def test_exportar_entidades_selecionadas_aceita_conexao_dedicada(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        mock_repo = MagicMock()
        mock_repo._get_conn.return_value = mock_conn
        mock_repo.buscar_grupos_por_ids_coordenadores.return_value = []
        mock_repo.buscar_geoentcod_por_cpf.return_value = None

        service = SavicModeracaoService(repository=mock_repo)
        coord = CoordenadorModeracaoDTO(
            id_savic="10",
            coordenador="TESTE COORD",
            cpf="111.222.333-44",
            cidade="Curitiba",
            uf="PR",
        )

        with patch("savic.moderacao_service.geoapolo_configcod", return_value="00000999"):
            resultado = service.exportar_entidades_selecionadas(
                coordenadores=[coord],
                grupos=[],
                empresa_codigo="1.01",
                connection=mock_conn
            )
            self.assertTrue(resultado.sucesso)
            self.assertEqual(resultado.total_coordenadores_inseridos, 1)


if __name__ == "__main__":
    unittest.main()
