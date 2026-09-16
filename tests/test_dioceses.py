"""
Testes Unitários para o Módulo de Gestão e Relacionamento de Dioceses CNBB com Entidades RCC.
GeoApolo V5
"""

import sqlite3
import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock

from dioceses.models import (
    EntidadeDioceseDTO,
    DioceseCNBBDTO,
    FiltroVinculoDioceseDTO,
    ResultadoOperacaoDiocese,
)
from dioceses.repository import DiocesesRepository
from dioceses.service import DiocesesService


class TestDiocesesModels(unittest.TestCase):
    """Testes dos DTOs e regras de apresentação de Dioceses e Entidades."""

    def test_entidade_dto_propriedades(self):
        ent_sem = EntidadeDioceseDTO(
            entcod="100",
            entnome="JOAO DA SILVA",
            cidcod="3550308",
            cidnomecomp="SAO PAULO",
            ufsigla="SP",
            user_diocese_id=None,
            user_nome_diocese=None,
            user_jana_sve="N",
        )
        self.assertFalse(ent_sem.tem_diocese)
        self.assertEqual(ent_sem.status_sve_formatado, "NÃO INCLUÍDA NA SVE")

        ent_com = EntidadeDioceseDTO(
            entcod="101",
            entnome="MARIA DOS SANTOS",
            cidcod="3550308",
            cidnomecomp="SAO PAULO",
            ufsigla="SP",
            user_diocese_id="DIO_SP",
            user_nome_diocese="ARQUIDIOCESE DE SAO PAULO",
            user_jana_sve="S",
        )
        self.assertTrue(ent_com.tem_diocese)
        self.assertEqual(ent_com.status_sve_formatado, "DISPONÍVEL NA SVE")

        ent_vazio = EntidadeDioceseDTO(entcod="102", entnome="TESTE", user_jana_sve=None)
        self.assertEqual(ent_vazio.status_sve_formatado, "NÃO INFORMADO")

    def test_diocese_dto_display(self):
        dio = DioceseCNBBDTO(
            id="10",
            nome="Diocese de Lorena",
            cidade="Lorena",
            ufsigla="SP",
            nome_estado="São Paulo",
        )
        self.assertIn("Diocese de Lorena", dio.display_completo)
        self.assertIn("(SP)", dio.display_completo)
        self.assertIn("Lorena", dio.display_completo)


class TestDiocesesRepositorySQLite(unittest.TestCase):
    """Testes do Repositório com banco em memória simulando SQL Server."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self._criar_schema()
        self._popular_dados()
        self.repo = DiocesesRepository(self.conn)

    def tearDown(self):
        self.conn.close()

    def _criar_schema(self):
        cur = self.conn.cursor()
        cur.executescript("""
            CREATE TABLE entidade (
                entcod TEXT PRIMARY KEY,
                entnome TEXT,
                cidcod TEXT,
                entdesdedata TEXT
            );

            CREATE TABLE ent_categ (
                entcod TEXT,
                categcodestr TEXT
            );

            CREATE TABLE cidade (
                cidcod TEXT PRIMARY KEY,
                cidnomecomp TEXT,
                ufsigla TEXT
            );

            CREATE TABLE u_entidade (
                entcod TEXT PRIMARY KEY,
                USERDiocese_id TEXT,
                USERNomeDiocese TEXT,
                USERJanaSVE TEXT
            );

            CREATE TABLE USEREstado_CNBB (
                USERid TEXT PRIMARY KEY,
                usersigla TEXT,
                usernome_estado TEXT
            );

            CREATE TABLE USERdioceses_CNBB (
                id TEXT PRIMARY KEY,
                estado_id TEXT,
                nome TEXT
            );

            CREATE TABLE USERcidades_CNBB (
                id TEXT PRIMARY KEY,
                diocese_id TEXT,
                estado_id TEXT,
                descricao TEXT
            );
        """)
        self.conn.commit()

    def _popular_dados(self):
        cur = self.conn.cursor()
        # Cidades
        cur.execute("INSERT INTO cidade VALUES ('001', 'LORENA', 'SP')")
        cur.execute("INSERT INTO cidade VALUES ('002', 'APARECIDA', 'SP')")
        cur.execute("INSERT INTO cidade VALUES ('003', 'RIO DE JANEIRO', 'RJ')")

        # Entidades RCC
        cur.execute("INSERT INTO entidade VALUES ('E001', 'COORDENADOR RCC 1', '001', '2026-01-15')")
        cur.execute("INSERT INTO ent_categ VALUES ('E001', '02.001.001')")

        cur.execute("INSERT INTO entidade VALUES ('E002', 'LIDER GRUPO ORAÇÃO', '001', '2026-02-20')")
        cur.execute("INSERT INTO ent_categ VALUES ('E002', '03.001.002')")

        cur.execute("INSERT INTO entidade VALUES ('E003', 'MEMBRO CADASTRADO', '002', '2026-03-10')")
        cur.execute("INSERT INTO ent_categ VALUES ('E003', '03.005.000')")

        # Entidade não RCC (não deve aparecer)
        cur.execute("INSERT INTO entidade VALUES ('E999', 'FORNECEDOR DIVERSO', '001', '2026-01-01')")
        cur.execute("INSERT INTO ent_categ VALUES ('E999', '01.001.001')")

        # Vínculos pré-existentes
        cur.execute("INSERT INTO u_entidade VALUES ('E002', 'D10', 'DIOCESE DE LORENA', 'S')")

        # Estados CNBB
        cur.execute("INSERT INTO USEREstado_CNBB VALUES ('EST_SP', 'SP', 'Sao Paulo')")
        cur.execute("INSERT INTO USEREstado_CNBB VALUES ('EST_RJ', 'RJ', 'Rio de Janeiro')")

        # Dioceses CNBB
        cur.execute("INSERT INTO USERdioceses_CNBB VALUES ('D10', 'EST_SP', 'Diocese de Lorena')")
        cur.execute("INSERT INTO USERdioceses_CNBB VALUES ('D20', 'EST_SP', 'Arquidiocese de Aparecida')")

        # Cidades CNBB
        cur.execute("INSERT INTO USERcidades_CNBB VALUES ('C1', 'D10', 'EST_SP', 'LORENA')")
        cur.execute("INSERT INTO USERcidades_CNBB VALUES ('C2', 'D20', 'EST_SP', 'APARECIDA')")

        self.conn.commit()

    def test_listar_entidades_sem_diocese(self):
        filtro = FiltroVinculoDioceseDTO(
            data_inicial=date(2026, 1, 1),
            data_final=date(2026, 12, 31),
            apenas_sem_diocese=True,
        )
        res = self.repo.listar_entidades(filtro)
        # E001 e E003 não possuem diocese. E002 possui. E999 não é categoria RCC.
        codigos = [e.entcod for e in res]
        self.assertIn("E001", codigos)
        self.assertIn("E003", codigos)
        self.assertNotIn("E002", codigos)
        self.assertNotIn("E999", codigos)

    def test_listar_todas_entidades_periodo(self):
        filtro = FiltroVinculoDioceseDTO(
            data_inicial=date(2026, 1, 1),
            data_final=date(2026, 12, 31),
            apenas_sem_diocese=False,
        )
        res = self.repo.listar_entidades(filtro)
        codigos = [e.entcod for e in res]
        self.assertIn("E001", codigos)
        self.assertIn("E002", codigos)
        self.assertIn("E003", codigos)
        self.assertNotIn("E999", codigos)

    def test_obter_entidade(self):
        ent = self.repo.obter_entidade("E002")
        self.assertIsNotNone(ent)
        self.assertEqual(ent.entnome, "LIDER GRUPO ORAÇÃO")
        self.assertEqual(ent.user_diocese_id, "D10")
        self.assertEqual(ent.user_nome_diocese, "DIOCESE DE LORENA")
        self.assertEqual(ent.user_jana_sve, "S")

    def test_vincular_diocese_insert(self):
        # E001 não está em u_entidade ainda
        sucesso = self.repo.vincular_diocese("E001", "D10", "Diocese de Lorena")
        self.assertTrue(sucesso)

        ent = self.repo.obter_entidade("E001")
        self.assertEqual(ent.user_diocese_id, "D10")
        self.assertEqual(ent.user_nome_diocese, "Diocese de Lorena")

    def test_vincular_diocese_update(self):
        # E002 já está em u_entidade com D10; trocar para D20
        sucesso = self.repo.vincular_diocese("E002", "D20", "Arquidiocese de Aparecida")
        self.assertTrue(sucesso)

        ent = self.repo.obter_entidade("E002")
        self.assertEqual(ent.user_diocese_id, "D20")
        self.assertEqual(ent.user_nome_diocese, "Arquidiocese de Aparecida")

    def test_desvincular_diocese(self):
        sucesso = self.repo.desvincular_diocese("E002")
        self.assertTrue(sucesso)

        ent = self.repo.obter_entidade("E002")
        self.assertIsNone(ent.user_diocese_id)
        self.assertIsNone(ent.user_nome_diocese)

    def test_sugerir_diocese_por_cidade(self):
        dio = self.repo.sugerir_diocese_por_cidade("LORENA", "SP")
        self.assertIsNotNone(dio)
        self.assertEqual(dio.id, "D10")
        self.assertEqual(dio.nome, "Diocese de Lorena")

        dio_aparecida = self.repo.sugerir_diocese_por_cidade("APARECIDA", "SP")
        self.assertIsNotNone(dio_aparecida)
        self.assertEqual(dio_aparecida.id, "D20")

        dio_inexistente = self.repo.sugerir_diocese_por_cidade("CIDADE DESCONHECIDA", "XX")
        self.assertIsNone(dio_inexistente)

    def test_listar_dioceses(self):
        dios = self.repo.listar_dioceses(uf="SP")
        self.assertEqual(len(dios), 2)
        nomes = [d.nome for d in dios]
        self.assertIn("Diocese de Lorena", nomes)
        self.assertIn("Arquidiocese de Aparecida", nomes)


class TestDiocesesService(unittest.TestCase):
    """Testes das regras de negócio do DiocesesService."""

    def setUp(self):
        self.mock_repo = MagicMock(spec=DiocesesRepository)
        self.service = DiocesesService(self.mock_repo)

    def test_validacao_periodo_invalido(self):
        dt_ini = date(2026, 12, 31)
        dt_fim = date(2026, 1, 1)
        filtro = FiltroVinculoDioceseDTO(data_inicial=dt_ini, data_final=dt_fim)

        with self.assertRaises(ValueError):
            self.service.listar_entidades(filtro)

    def test_vincular_com_sucesso(self):
        self.mock_repo.vincular_diocese.return_value = True
        res = self.service.vincular("E123", "D10", "Diocese Teste")

        self.assertTrue(res.sucesso)
        self.assertIn("vinculada com sucesso", res.mensagem)
        self.mock_repo.vincular_diocese.assert_called_once_with(
            entcod="E123",
            diocese_id="D10",
            nome_diocese="Diocese Teste"
        )

    def test_vincular_sem_entcod(self):
        res = self.service.vincular("", "D10", "Diocese Teste")
        self.assertFalse(res.sucesso)
        self.assertIn("deve ser informado", res.mensagem)
        self.mock_repo.vincular_diocese.assert_not_called()

    def test_desvincular_chama_repository(self):
        self.mock_repo.desvincular_diocese.return_value = True
        res = self.service.desvincular("E123")

        self.assertTrue(res.sucesso)
        self.assertIn("desvinculada com sucesso", res.mensagem)
        self.mock_repo.desvincular_diocese.assert_called_once_with("E123")

    def test_sugerir_diocese(self):
        dio_esperada = DioceseCNBBDTO(id="D1", nome="Diocese Teste", cidade="Cidade T", ufsigla="SP")
        self.mock_repo.sugerir_diocese_por_cidade.return_value = dio_esperada

        res = self.service.sugerir_diocese("Cidade T", "SP")
        self.assertEqual(res, dio_esperada)
        self.mock_repo.sugerir_diocese_por_cidade.assert_called_once_with(cidade="Cidade T", uf="SP")


if __name__ == "__main__":
    unittest.main()
