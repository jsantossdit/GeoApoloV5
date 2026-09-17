"""
Testes Unitários para o Módulo CRM (Campanhas, Tratamentos e Ocorrências).
GeoApolo V5
Clean Architecture: Testes de Models, Repositório SQLite em memória e Regras de Negócio do Service.
"""

import sqlite3
import unittest
from unittest.mock import MagicMock

from crm.models import (
    TipoCampanhaDTO,
    TipoTratamentoDTO,
    OcorrenciaDTO,
    MotivoOcorrenciaDTO,
    OrigemDTO,
    SolicitanteDTO,
    ResultadoCRM,
)
from crm.repository import CRMRepository
from crm.service import CRMService


class TestCRMModels(unittest.TestCase):
    """Testes dos DTOs e propriedades do modelo CRM."""

    def test_tipo_campanha_dto_properties(self):
        c1 = TipoCampanhaDTO("CAMP01", "Campanha Pascoa", "S", "S")
        self.assertTrue(c1.is_ativo)
        self.assertTrue(c1.is_gera_campanha)
        self.assertEqual(c1.display, "CAMP01 - Campanha Pascoa")

        c2 = TipoCampanhaDTO("CAMP02", "Campanha Inativa", "N", "N")
        self.assertFalse(c2.is_ativo)
        self.assertFalse(c2.is_gera_campanha)

    def test_tipo_tratamento_dto_display(self):
        t = TipoTratamentoDTO("01", "TEL", "Teleatendimento Receptivo")
        self.assertEqual(t.display, "TEL - Teleatendimento Receptivo")

    def test_ocorrencia_dto_status_properties(self):
        o_pen = OcorrenciaDTO(ocorcod="0001", ocorstat="Pendente")
        self.assertTrue(o_pen.is_pendente)
        self.assertFalse(o_pen.is_cancelado)

        o_canc = OcorrenciaDTO(ocorcod="0002", ocorstat="Cancelado")
        self.assertTrue(o_canc.is_cancelado)
        self.assertFalse(o_canc.is_pendente)

        o_res = OcorrenciaDTO(ocorcod="0003", ocorstat="Resolvido")
        self.assertTrue(o_res.is_resolvido)

        o_and = OcorrenciaDTO(ocorcod="0004", ocorstat="Em Andamento")
        self.assertTrue(o_and.is_em_andamento)

    def test_motivo_ocorrencia_is_area(self):
        m_area = MotivoOcorrenciaDTO("01", "Atendimento Geral", motocorgrupo="T")
        self.assertTrue(m_area.is_area)

        m_sub = MotivoOcorrenciaDTO("01.01", "Dúvida de Boleto", motocorgrupo="F")
        self.assertFalse(m_sub.is_area)


class TestCRMRepositorySQLite(unittest.TestCase):
    """Testes de integração do CRMRepository com SQLite em memória."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self._criar_schema()
        self._popular_dados()
        self.repo = CRMRepository(self.conn)

    def tearDown(self):
        self.conn.close()

    def _criar_schema(self):
        cur = self.conn.cursor()
        cur.executescript("""
            CREATE TABLE USER_geoapolo_tipocampanha (
                codigo_tipocampanha TEXT PRIMARY KEY,
                descricaotipocamp TEXT,
                ativo TEXT,
                geracampanha TEXT
            );

            CREATE TABLE USER_geoapolo_tipotratamento (
                tipotratcod TEXT PRIMARY KEY,
                abreviatura TEXT,
                descricao_tratamento TEXT
            );

            CREATE TABLE OCORRENCIA (
                OcorCod TEXT PRIMARY KEY,
                OcorStat TEXT,
                EntCod TEXT,
                ocorentnome TEXT,
                OcorRespSol TEXT,
                OcorData TEXT,
                MotOcorCodEstr TEXT,
                ocortexto TEXT,
                ocorresptexto TEXT,
                origcodestr TEXT,
                empcod TEXT,
                ocordatacanc TEXT,
                ocorrespcanc TEXT,
                ocormotcanc TEXT
            );

            CREATE TABLE MOTIVO_OCOR (
                MotOcorCodEstr TEXT PRIMARY KEY,
                MotOcorDescr TEXT,
                MotOcorGrupo TEXT,
                MotOcorResp1 TEXT,
                MotOcorResp2 TEXT,
                MotOcorResp3 TEXT
            );

            CREATE TABLE ORIGEM (
                OrigCodEstr TEXT PRIMARY KEY,
                OrigNome TEXT
            );

            CREATE TABLE ENTIDADE (
                entcod TEXT PRIMARY KEY,
                entnome TEXT,
                entstatdescr TEXT
            );

            CREATE TABLE ENT_CATEG (
                entcod TEXT,
                categcodestr TEXT
            );
        """)
        self.conn.commit()

    def _popular_dados(self):
        cur = self.conn.cursor()
        # Campanhas
        cur.execute("INSERT INTO USER_geoapolo_tipocampanha VALUES ('01', 'Campanha Aniversariantes', 'S', 'S')")
        cur.execute("INSERT INTO USER_geoapolo_tipocampanha VALUES ('02', 'Campanha Inativa', 'N', 'S')")

        # Tratamentos
        cur.execute("INSERT INTO USER_geoapolo_tipotratamento VALUES ('01', 'EMAIL', 'Contato por Email')")

        # Origem
        cur.execute("INSERT INTO ORIGEM VALUES ('01', 'Portal Web')")

        # Motivos
        cur.execute("INSERT INTO MOTIVO_OCOR VALUES ('01', 'Suporte Técnico', 'T', '', '', '')")
        cur.execute("INSERT INTO MOTIVO_OCOR VALUES ('01.01', 'Erro no Login', 'F', 'Carlos', 'Ana', '')")

        # Entidade
        cur.execute("INSERT INTO ENTIDADE VALUES ('CLI001', 'João da Silva', 'Ativo')")
        cur.execute("INSERT INTO ENT_CATEG VALUES ('CLI001', '03.001')")

        self.conn.commit()

    def test_crud_tipos_campanha(self):
        # Listar todos
        todos = self.repo.listar_tipos_campanha()
        self.assertEqual(len(todos), 2)

        # Listar apenas ativos
        ativos = self.repo.listar_tipos_campanha(apenas_ativos=True)
        self.assertEqual(len(ativos), 1)
        self.assertEqual(ativos[0].codigo_tipocampanha, "01")

        # Obter
        c = self.repo.obter_tipo_campanha("01")
        self.assertIsNotNone(c)
        self.assertEqual(c.descricaotipocamp, "Campanha Aniversariantes")

        # Salvar novo
        self.repo.salvar_tipo_campanha(TipoCampanhaDTO("03", "Campanha Natal", "S", "S"))
        c3 = self.repo.obter_tipo_campanha("03")
        self.assertIsNotNone(c3)
        self.assertEqual(c3.descricaotipocamp, "Campanha Natal")

        # Atualizar
        c3.descricaotipocamp = "Campanha Natal 2026"
        self.repo.salvar_tipo_campanha(c3)
        self.assertEqual(self.repo.obter_tipo_campanha("03").descricaotipocamp, "Campanha Natal 2026")

        # Excluir
        self.repo.excluir_tipo_campanha("03")
        self.assertIsNone(self.repo.obter_tipo_campanha("03"))

    def test_crud_tipos_tratamento(self):
        trats = self.repo.listar_tipos_tratamento()
        self.assertEqual(len(trats), 1)
        self.assertEqual(trats[0].abreviatura, "EMAIL")

        # Salvar novo
        self.repo.salvar_tipo_tratamento(TipoTratamentoDTO("02", "WHATS", "Atendimento WhatsApp"))
        t2 = self.repo.obter_tipo_tratamento("02")
        self.assertIsNotNone(t2)
        self.assertEqual(t2.descricao_tratamento, "Atendimento WhatsApp")

        # Excluir
        self.repo.excluir_tipo_tratamento("02")
        self.assertIsNone(self.repo.obter_tipo_tratamento("02"))

    def test_crud_ocorrencias(self):
        prox_cod = self.repo.proximo_codigo_ocorrencia()
        self.assertEqual(prox_cod, "0000001")

        dto = OcorrenciaDTO(
            ocorcod="0000001",
            ocorstat="Pendente",
            entcod="CLI001",
            ocorentnome="João da Silva",
            ocorrespsol="Carlos",
            ocordata="2026-09-17",
            motocorcodestr="01.01",
            ocortexto="Não consigo acessar o sistema",
            origcodestr="01",
            empcod="01",
        )
        self.repo.salvar_ocorrencia(dto)

        # Obter
        recup = self.repo.obter_ocorrencia("0000001")
        self.assertIsNotNone(recup)
        self.assertEqual(recup.ocorentnome, "João da Silva")
        self.assertEqual(recup.motocordescr, "Erro no Login")
        self.assertEqual(recup.orignome, "Portal Web")

        # Listar filtrando por status
        lista_pend = self.repo.listar_ocorrencias(status="Pendente")
        self.assertEqual(len(lista_pend), 1)
        lista_canc = self.repo.listar_ocorrencias(status="Cancelado")
        self.assertEqual(len(lista_canc), 0)

        # Atualizar Solução
        self.repo.atualizar_solucao("0000001", "Senha reiniciada", status="Resolvido", resp_sol="Carlos")
        recup_res = self.repo.obter_ocorrencia("0000001")
        self.assertEqual(recup_res.ocorstat, "Resolvido")
        self.assertEqual(recup_res.ocorresptexto, "Senha reiniciada")

        # Cancelar
        self.repo.cancelar_ocorrencia("0000001", "2026-09-17", "Admin", "Cancelado a pedido")
        recup_canc = self.repo.obter_ocorrencia("0000001")
        self.assertEqual(recup_canc.ocorstat, "Cancelado")
        self.assertEqual(recup_canc.ocormotcanc, "Cancelado a pedido")

    def test_auxiliares(self):
        areas = self.repo.listar_areas_disponiveis()
        self.assertEqual(len(areas), 1)
        self.assertEqual(areas[0].motocordescr, "Suporte Técnico")

        motivos = self.repo.listar_motivos_por_area("01")
        self.assertEqual(len(motivos), 1)
        self.assertEqual(motivos[0].motocorresp1, "Carlos")

        origens = self.repo.listar_origens()
        self.assertEqual(len(origens), 1)
        self.assertEqual(origens[0].orignome, "Portal Web")

        solicitantes = self.repo.listar_solicitantes("João")
        self.assertEqual(len(solicitantes), 1)
        self.assertEqual(solicitantes[0].entcod, "CLI001")


class TestCRMService(unittest.TestCase):
    """Testes de regras de negócio e validações do CRMService."""

    def setUp(self):
        self.mock_repo = MagicMock(spec=CRMRepository)
        self.service = CRMService(self.mock_repo)

    def test_salvar_tipo_campanha_validacoes(self):
        # Código vazio
        res = self.service.salvar_tipo_campanha(TipoCampanhaDTO("", "Campanha"))
        self.assertFalse(res.sucesso)
        self.assertIn("Código", res.mensagem)

        # Descrição vazia
        res = self.service.salvar_tipo_campanha(TipoCampanhaDTO("01", ""))
        self.assertFalse(res.sucesso)
        self.assertIn("Descrição", res.mensagem)

        # Sucesso com sanitização de flags
        dto = TipoCampanhaDTO("01", "Campanha Válida", ativo="x", geracampanha="s")
        res = self.service.salvar_tipo_campanha(dto)
        self.assertTrue(res.sucesso)
        self.assertEqual(dto.ativo, "N")
        self.assertEqual(dto.geracampanha, "S")
        self.mock_repo.salvar_tipo_campanha.assert_called_once_with(dto)

    def test_salvar_tipo_tratamento_validacoes(self):
        # Código vazio
        res = self.service.salvar_tipo_tratamento(TipoTratamentoDTO("", "TEL", "Telefone"))
        self.assertFalse(res.sucesso)

        # Abreviatura vazia
        res = self.service.salvar_tipo_tratamento(TipoTratamentoDTO("01", "", "Telefone"))
        self.assertFalse(res.sucesso)

        # Sucesso
        res = self.service.salvar_tipo_tratamento(TipoTratamentoDTO("01", "TEL", "Telefone"))
        self.assertTrue(res.sucesso)

    def test_salvar_ocorrencia_validacoes(self):
        # Sem solicitante
        res = self.service.salvar_ocorrencia(OcorrenciaDTO("", entcod="", motocorcodestr="01", ocortexto="Texto"))
        self.assertFalse(res.sucesso)
        self.assertIn("solicitante", res.mensagem.lower())

        # Sem motivo
        res = self.service.salvar_ocorrencia(OcorrenciaDTO("", entcod="01", motocorcodestr="", ocortexto="Texto"))
        self.assertFalse(res.sucesso)
        self.assertIn("motivo", res.mensagem.lower())

        # Sem texto
        res = self.service.salvar_ocorrencia(OcorrenciaDTO("", entcod="01", motocorcodestr="01.01", ocortexto=""))
        self.assertFalse(res.sucesso)
        self.assertIn("descrição", res.mensagem.lower())

        # Sucesso gerando código sequencial automático se ausente
        self.mock_repo.proximo_codigo_ocorrencia.return_value = "0000042"
        dto = OcorrenciaDTO("", entcod="CLI01", motocorcodestr="01.01", ocortexto="Solicito suporte")
        res = self.service.salvar_ocorrencia(dto)
        self.assertTrue(res.sucesso)
        self.assertEqual(dto.ocorcod, "0000042")
        self.assertEqual(dto.ocorstat, "Pendente")

    def test_cancelar_ocorrencia_validacoes(self):
        # Validação campos obrigatórios
        res = self.service.cancelar_ocorrencia("", "2026-09-17", "Admin", "Motivo")
        self.assertFalse(res.sucesso)

        res = self.service.cancelar_ocorrencia("0001", "", "Admin", "Motivo")
        self.assertFalse(res.sucesso)

        res = self.service.cancelar_ocorrencia("0001", "2026-09-17", "Admin", "")
        self.assertFalse(res.sucesso)

        # Ocorrência não encontrada
        self.mock_repo.obter_ocorrencia.return_value = None
        res = self.service.cancelar_ocorrencia("0001", "2026-09-17", "Admin", "Motivo")
        self.assertFalse(res.sucesso)
        self.assertIn("não foi localizada", res.mensagem)

        # Ocorrência já cancelada
        self.mock_repo.obter_ocorrencia.return_value = OcorrenciaDTO("0001", ocorstat="Cancelado")
        res = self.service.cancelar_ocorrencia("0001", "2026-09-17", "Admin", "Motivo")
        self.assertFalse(res.sucesso)
        self.assertIn("já se encontra cancelada", res.mensagem)

        # Sucesso
        self.mock_repo.obter_ocorrencia.return_value = OcorrenciaDTO("0001", ocorstat="Pendente")
        res = self.service.cancelar_ocorrencia("0001", "2026-09-17", "Admin", "Motivo")
        self.assertTrue(res.sucesso)


if __name__ == "__main__":
    unittest.main()
