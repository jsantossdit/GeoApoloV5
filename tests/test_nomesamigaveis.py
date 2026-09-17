"""
Testes Unitários para o Módulo de Dicionário de Nomes Amigáveis de Objetos.
GeoApolo V5
Clean Architecture: DTOs, Repositório SQLite em memória e Regras de Negócio do Service.
"""

import sqlite3
import unittest
from unittest.mock import MagicMock

from nomesamigaveis.models import ObjetoSistemaDTO, ResultadoNomesAmigaveisDTO
from nomesamigaveis.repository import NomesAmigaveisRepository
from nomesamigaveis.service import NomesAmigaveisService


class TestNomesAmigaveisModels(unittest.TestCase):
    """Testes dos DTOs de Nomes Amigáveis."""

    def test_objeto_sistema_dto_display(self):
        dto = ObjetoSistemaDTO(
            nome_objeto="frmprincipal.btnEmitirNFe",
            nome_amigavel="Emitir NF-e",
            categoria="Fiscal",
        )
        self.assertEqual(dto.categoria, "Fiscal")
        self.assertIn("[Fiscal]", dto.display)
        self.assertIn("Emitir NF-e", dto.display)

    def test_resultado_nomes_amigaveis_dto(self):
        res = ResultadoNomesAmigaveisDTO(sucesso=True, mensagem="OK", total_afetados=5)
        self.assertTrue(res.sucesso)
        self.assertEqual(res.total_afetados, 5)


class TestNomesAmigaveisRepository(unittest.TestCase):
    """Testes do Repositório com SQLite em memória."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE USER_geoapolo_objetos (
                nome_objeto VARCHAR(100) PRIMARY KEY,
                nome_amigavel VARCHAR(100),
                categoria VARCHAR(50)
            )
        """)
        self.conn.commit()
        self.repo = NomesAmigaveisRepository(connection=self.conn)

    def tearDown(self):
        self.conn.close()

    def test_salvar_e_listar_objetos(self):
        obj1 = ObjetoSistemaDTO("frmprincipal.btnCadastros", "Cadastros Gerais", "Cadastros")
        obj2 = ObjetoSistemaDTO("frmprincipal.btnFinanceiro", "Módulo Financeiro", "Financeiro")
        self.repo.salvar_objeto(obj1)
        self.repo.salvar_objeto(obj2)

        lista = self.repo.listar_objetos()
        self.assertEqual(len(lista), 2)

        # Filtro por categoria
        lista_cad = self.repo.listar_objetos(categoria="Cadastros")
        self.assertEqual(len(lista_cad), 1)
        self.assertEqual(lista_cad[0].nome_objeto, "frmprincipal.btnCadastros")

        # Filtro por texto
        lista_busca = self.repo.listar_objetos(filtro="Financeiro")
        self.assertEqual(len(lista_busca), 1)
        self.assertEqual(lista_busca[0].categoria, "Financeiro")

    def test_obter_objeto_e_atualizar(self):
        obj = ObjetoSistemaDTO("frmprincipal.btnSair", "btnSair", "Geral")
        self.repo.salvar_objeto(obj)

        self.repo.atualizar_nome_amigavel("frmprincipal.btnSair", "Sair do Sistema", "Sistema")
        rec = self.repo.obter_objeto("frmprincipal.btnSair")
        self.assertIsNotNone(rec)
        self.assertEqual(rec.nome_amigavel, "Sair do Sistema")
        self.assertEqual(rec.categoria, "Sistema")

    def test_listar_categorias(self):
        self.repo.salvar_objeto(ObjetoSistemaDTO("obj1", "ami1", "Vendas"))
        self.repo.salvar_objeto(ObjetoSistemaDTO("obj2", "ami2", "Estoque"))

        cats = self.repo.listar_categorias()
        self.assertIn("Vendas", cats)
        self.assertIn("Estoque", cats)


class TestNomesAmigaveisService(unittest.TestCase):
    """Testes de heurística e regras de negócio do NomesAmigaveisService."""

    def setUp(self):
        self.mock_repo = MagicMock(spec=NomesAmigaveisRepository)
        self.service = NomesAmigaveisService(self.mock_repo)

    def test_heuristica_sugestao_nomes(self):
        self.assertEqual(self.service.sugerir_nome_amigavel("frmprincipal.btnEmitirNFe"), "Emitir NF-e")
        self.assertEqual(self.service.sugerir_nome_amigavel("frmprincipal.mnuCadastros"), "Cadastros")
        self.assertEqual(self.service.sugerir_nome_amigavel("tbsheetFiscal"), "Fiscal")
        self.assertEqual(self.service.sugerir_nome_amigavel("pnlAtendimentoGeral"), "Atendimento Geral")
        self.assertEqual(self.service.sugerir_nome_amigavel("btnAuditoriaCupons"), "Auditoria Cupons")

    def test_salvar_objeto_validacoes(self):
        res_vazio = self.service.salvar_objeto(ObjetoSistemaDTO("", "Nome"))
        self.assertFalse(res_vazio.sucesso)
        self.assertIn("obrigatório", res_vazio.mensagem)

        # Sem nome amigável gera automaticamente
        res_sug = self.service.salvar_objeto(ObjetoSistemaDTO("frmprincipal.btnSalvar", ""))
        self.assertTrue(res_sug.sucesso)
        self.mock_repo.salvar_objeto.assert_called_once()

    def test_gerar_sugestoes_automaticas(self):
        self.mock_repo.listar_objetos.return_value = [
            # Não editado: nome amigável igual ao nome técnico
            ObjetoSistemaDTO("frmprincipal.btnRelatorios", "frmprincipal.btnRelatorios", "Geral"),
            # Já editado: não deve alterar
            ObjetoSistemaDTO("frmprincipal.btnConfig", "Configurações Avançadas", "Geral"),
        ]

        res = self.service.gerar_sugestoes_automaticas(apenas_nao_editados=True)
        self.assertTrue(res.sucesso)
        self.assertEqual(res.total_afetados, 1)
        self.mock_repo.atualizar_nome_amigavel.assert_called_once_with(
            "frmprincipal.btnRelatorios", "Relatorios", "Geral"
        )


if __name__ == "__main__":
    unittest.main()
