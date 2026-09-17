"""
Testes Unitários para o Módulo de Gestão e Importação de Eventos/Congressos.
GeoApolo V5
"""

import unittest
from unittest.mock import MagicMock
import tempfile
import os
from eventos.models import (
    InscricaoEventoDTO,
    ResultadoImportacaoDTO,
    EventoResumoDTO,
    EventoDTO,
    TipoEventoDTO,
    ResultadoEventoDTO,
)
import sqlite3
from eventos.importer import PlanilhaInscricoesReader, somente_digitos
from eventos.repository import EventosRepository
from eventos.service import EventosService


class TestEventosModule(unittest.TestCase):

    def setUp(self):
        self.mock_repo = MagicMock(spec=EventosRepository)
        self.service = EventosService(self.mock_repo)

    def test_somente_digitos(self):
        self.assertEqual(somente_digitos("123.456.789-00"), "12345678900")
        self.assertEqual(somente_digitos("SP 04571-010"), "04571010")
        self.assertEqual(somente_digitos(None), "")

    def test_dto_vinculado_apolo(self):
        item_sem_vinculo = InscricaoEventoDTO(
            evento_id="CONG2025",
            documento="12345678901",
            nome="Jose da Silva",
            ent_cod=None,
        )
        self.assertFalse(item_sem_vinculo.vinculado_apolo)

        item_vinculado = InscricaoEventoDTO(
            evento_id="CONG2025",
            documento="12345678901",
            nome="Jose da Silva",
            ent_cod="CLI0050",
        )
        self.assertTrue(item_vinculado.vinculado_apolo)

    def test_leitor_csv_com_ponto_e_virgula(self):
        csv_conteudo = (
            "CPF;Nome;Email;Telefone;Cidade;UF;Valor;Fatura\n"
            "123.456.789-00;Maria Oliveira;maria@teste.com;11999998888;São Paulo;SP;150,00;FAT1001\n"
            "987.654.321-99;João Santos;joao@teste.com;21988887777;Rio de Janeiro;RJ;200,50;FAT1002\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", encoding="utf-8") as f:
            f.write(csv_conteudo)
            temp_path = f.name

        try:
            inscricoes = PlanilhaInscricoesReader.ler_arquivo(temp_path, evento_id="EVT01")
            self.assertEqual(len(inscricoes), 2)
            self.assertEqual(inscricoes[0].documento, "12345678900")
            self.assertEqual(inscricoes[0].nome, "Maria Oliveira")
            self.assertEqual(inscricoes[0].cidade, "São Paulo")
            self.assertEqual(inscricoes[0].valor_venda, 150.0)
            self.assertEqual(inscricoes[1].documento, "98765432199")
            self.assertEqual(inscricoes[1].valor_venda, 200.50)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_cruzar_com_apolo(self):
        inscricoes = [
            InscricaoEventoDTO(
                evento_id="EVT01",
                documento="11122233344",
                nome="Participante 1",
            ),
            InscricaoEventoDTO(
                evento_id="EVT01",
                documento="",
                nome="Participante Sem Doc",
            ),
        ]

        def mock_buscar_vinculo(doc):
            if doc == "11122233344":
                return ("ENT001", True, "202508")
            return (None, False, "")

        self.mock_repo.buscar_vinculo_apolo.side_effect = mock_buscar_vinculo

        res = self.service.cruzar_com_apolo(inscricoes)
        self.assertEqual(res.total_linhas, 2)
        self.assertEqual(res.total_com_documento, 1)
        self.assertEqual(res.total_vinculados_apolo, 1)
        self.assertEqual(inscricoes[0].ent_cod, "ENT001")
        self.assertTrue(inscricoes[0].colabora_projetos)
        self.assertEqual(inscricoes[0].ano_mes_ultima_contribuicao, "202508")

    def test_salvar_inscricoes_evento(self):
        inscricoes = [
            InscricaoEventoDTO(
                evento_id="EVT01",
                documento="11122233344",
                nome="Participante 1",
                ent_cod="ENT001",
            )
        ]
        self.mock_repo.salvar_inscricoes.return_value = 1
        res = self.service.salvar_inscricoes("EVT01", inscricoes)
        self.assertTrue(res.sucesso)
        self.assertEqual(res.total_salvos, 1)
        self.mock_repo.salvar_inscricoes.assert_called_once_with("EVT01", inscricoes)

    def test_salvar_inscricoes_sem_evento_id(self):
        res = self.service.salvar_inscricoes("", [])
        self.assertFalse(res.sucesso)
        self.assertIn("obrigatório", res.mensagem)

    def test_evento_ja_importado_e_remover(self):
        self.mock_repo.evento_ja_importado.return_value = True
        self.mock_repo.remover_importacao_anterior.return_value = 50

        self.assertTrue(self.service.evento_ja_importado("EVT01"))
        self.assertEqual(self.service.remover_importacao_anterior("EVT01"), 50)
        self.mock_repo.remover_importacao_anterior.assert_called_once_with("EVT01")

    def test_listar_eventos(self):
        self.mock_repo.listar_eventos_cadastrados.return_value = [
            EventoResumoDTO("CONG2025", "Congresso Nacional", 1500)
        ]
        eventos = self.service.listar_eventos()
        self.assertEqual(len(eventos), 1)
        self.assertEqual(eventos[0].id, "CONG2025")
        self.assertEqual(eventos[0].total_inscritos, 1500)


class TestEventosCRUD(unittest.TestCase):
    """Testes de persistência de eventos e tipos de eventos em SQLite em memória."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        cur = self.conn.cursor()
        cur.executescript("""
            CREATE TABLE USER_geoapolo_tipo_eventos (
                tipoeventcod TEXT PRIMARY KEY,
                descricao_tipo_evento TEXT
            );

            CREATE TABLE USER_geoapolo_eventos (
                idevento TEXT PRIMARY KEY,
                descricao TEXT,
                data_inicial TEXT,
                data_final TEXT,
                tema_principal TEXT,
                tipoeventcod TEXT
            );
        """)
        self.conn.commit()
        self.repo = EventosRepository(self.conn)
        self.service = EventosService(self.repo)

    def tearDown(self):
        self.conn.close()

    def test_crud_tipos_evento(self):
        tipo1 = TipoEventoDTO("01", "Congresso Estadual")
        self.repo.salvar_tipo_evento(tipo1)

        tipos = self.repo.listar_tipos_evento()
        self.assertEqual(len(tipos), 1)
        self.assertEqual(tipos[0].tipo_event_cod, "01")
        self.assertEqual(tipos[0].descricao_tipo_evento, "Congresso Estadual")

        # Update
        tipo1_upd = TipoEventoDTO("01", "Congresso Nacional")
        self.repo.salvar_tipo_evento(tipo1_upd)
        tipos = self.repo.listar_tipos_evento()
        self.assertEqual(tipos[0].descricao_tipo_evento, "Congresso Nacional")

        # Excluir
        self.repo.excluir_tipo_evento("01")
        tipos = self.repo.listar_tipos_evento()
        self.assertEqual(len(tipos), 0)

    def test_crud_eventos(self):
        self.repo.salvar_tipo_evento(TipoEventoDTO("01", "Congresso"))

        evt = EventoDTO(
            id_evento="EVT01",
            descricao="Congresso Nacional 2026",
            data_inicial="2026-07-10",
            data_final="2026-07-14",
            tema_principal="Unidade e Missão",
            tipo_event_cod="01",
        )
        self.repo.salvar_evento(evt)

        recup = self.repo.obter_evento("EVT01")
        self.assertIsNotNone(recup)
        self.assertEqual(recup.id_evento, "EVT01")
        self.assertEqual(recup.descricao, "Congresso Nacional 2026")
        self.assertEqual(recup.tema_principal, "Unidade e Missão")
        self.assertEqual(recup.descricao_tipo_evento, "Congresso")

        # Listar com filtro
        filtrados = self.repo.listar_eventos_cadastrados_completos("Unidade")
        self.assertEqual(len(filtrados), 1)

        nao_encontrados = self.repo.listar_eventos_cadastrados_completos("Inexistente")
        self.assertEqual(len(nao_encontrados), 0)

        # Update
        evt.descricao = "Congresso Atualizado"
        self.repo.salvar_evento(evt)
        recup = self.repo.obter_evento("EVT01")
        self.assertEqual(recup.descricao, "Congresso Atualizado")

        # Excluir
        self.repo.excluir_evento("EVT01")
        self.assertIsNone(self.repo.obter_evento("EVT01"))

    def test_service_validacoes_evento(self):
        # Validação id vazio
        res = self.service.salvar_evento(EventoDTO("", "Sem ID"))
        self.assertFalse(res.sucesso)
        self.assertIn("obrigatório", res.mensagem)

        # Validação descricao vazia
        res = self.service.salvar_evento(EventoDTO("EVT99", ""))
        self.assertFalse(res.sucesso)
        self.assertIn("obrigatória", res.mensagem)

        # Salvar com sucesso
        res = self.service.salvar_evento(EventoDTO("EVT99", "Evento Válido"))
        self.assertTrue(res.sucesso)

        # Excluir com id vazio
        res = self.service.excluir_evento("")
        self.assertFalse(res.sucesso)

        # Excluir com sucesso
        res = self.service.excluir_evento("EVT99")
        self.assertTrue(res.sucesso)


if __name__ == "__main__":
    unittest.main()

