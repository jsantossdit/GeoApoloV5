"""
Repositório de Banco de Dados para Inscrições de Eventos e Congressos.
GeoApolo V5
"""

import logging
from typing import List, Tuple, Optional
from entidades.database import obter_conexao_banco
from .models import InscricaoEventoDTO, EventoResumoDTO

logger = logging.getLogger(__name__)


class EventosRepository:
    """Acesso ao SQL Server para gerenciamento de congressistas e cruzamento com a base Apolo."""

    def __init__(self, connection=None):
        self._conn = connection

    def _get_cursor(self):
        if self._conn is None:
            self._conn = obter_conexao_banco()
        return self._conn.cursor()

    def commit(self):
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()

    def rollback(self):
        if self._conn and hasattr(self._conn, "rollback"):
            self._conn.rollback()

    def buscar_vinculo_apolo(self, documento: str) -> Tuple[Optional[str], bool, str]:
        """
        Localiza entidade pelo CPF/CNPJ e averigua se colabora com projetos e última contribuição.
        Retorna (entcod, colabora_projetos, anomes_ultima_contribuicao).
        """
        doc = str(documento or "").strip()
        if not doc:
            return None, False, ""

        cursor = self._get_cursor()

        # 1. Busca código da entidade
        sql_ent = """
            SELECT TOP 1 entcod
            FROM entidade WITH (NOLOCK)
            WHERE REPLACE(REPLACE(REPLACE(ISNULL(entcpf, ''), '.', ''), '-', ''), '/', '') = ?
               OR REPLACE(REPLACE(REPLACE(ISNULL(entcnpj, ''), '.', ''), '-', ''), '/', '') = ?
        """
        cursor.execute(sql_ent, [doc, doc])
        r_ent = cursor.fetchone()
        if not r_ent:
            return None, False, ""

        ent_cod = str(r_ent[0]).strip()

        # 2. Verifica se tem categoria de projetos
        sql_cat = """
            SELECT TOP 1 ec.categcodestr
            FROM ent_categ ec WITH (NOLOCK)
            WHERE ec.entcod = ?
        """
        cursor.execute(sql_cat, [ent_cod])
        r_cat = cursor.fetchone()
        tem_categ = r_cat is not None

        # 3. Busca última contribuição
        sql_contrib = """
            SELECT TOP 1 ISNULL(docfinanomes, '')
            FROM doc_fin WITH (NOLOCK)
            WHERE entcod = ?
            ORDER BY docfinanomes DESC
        """
        cursor.execute(sql_contrib, [ent_cod])
        r_contrib = cursor.fetchone()
        anomes = str(r_contrib[0]).strip() if r_contrib else ""

        colabora = tem_categ and bool(anomes)
        return ent_cod, colabora, anomes

    def evento_ja_importado(self, evento_id: str) -> bool:
        cursor = self._get_cursor()
        sql = "SELECT TOP 1 1 FROM congresso_rcc WITH (NOLOCK) WHERE idevento = ?"
        cursor.execute(sql, [evento_id])
        return cursor.fetchone() is not None

    def remover_importacao_anterior(self, evento_id: str) -> int:
        cursor = self._get_cursor()
        sql = "DELETE FROM congresso_rcc WHERE idevento = ?"
        cursor.execute(sql, [evento_id])
        afetados = cursor.rowcount if cursor.rowcount > 0 else 0
        self.commit()
        return afetados

    def salvar_inscricoes(self, evento_id: str, inscricoes: List[InscricaoEventoDTO]) -> int:
        if not inscricoes:
            return 0

        cursor = self._get_cursor()
        sql_ins = """
            INSERT INTO congresso_rcc (
                idevento, clientedocumento, clientenome, clienteemail, clientefones,
                fatura, statusinscricao, valorvenda, endereco, cidade, uf, cep,
                entcod, colaboraprojetos, anomesultimacontribuicao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        salvos = 0
        try:
            for item in inscricoes:
                cursor.execute(
                    sql_ins,
                    [
                        evento_id,
                        item.documento,
                        item.nome,
                        item.email,
                        item.telefone,
                        item.fatura,
                        item.status_inscricao,
                        item.valor_venda,
                        item.endereco,
                        item.cidade,
                        item.uf,
                        item.cep,
                        item.ent_cod,
                        1 if item.colabora_projetos else 0,
                        item.ano_mes_ultima_contribuicao,
                    ],
                )
                salvos += 1
            self.commit()
            return salvos
        except Exception as e:
            self.rollback()
            logger.exception("Erro ao salvar inscrições de eventos: %s", e)
            raise e

    def listar_inscricoes_evento(self, evento_id: str) -> List[InscricaoEventoDTO]:
        cursor = self._get_cursor()
        sql = """
            SELECT idevento, clientedocumento, clientenome, ISNULL(clienteemail, ''),
                   ISNULL(clientefones, ''), ISNULL(fatura, ''), ISNULL(statusinscricao, 'Aprovado'),
                   ISNULL(valorvenda, 0.0), ISNULL(endereco, ''), ISNULL(cidade, ''),
                   ISNULL(uf, ''), ISNULL(cep, ''), entcod, ISNULL(colaboraprojetos, 0),
                   ISNULL(anomesultimacontribuicao, '')
            FROM congresso_rcc WITH (NOLOCK)
            WHERE idevento = ?
            ORDER BY clientenome ASC
        """
        cursor.execute(sql, [evento_id])
        itens = []
        for r in cursor.fetchall():
            itens.append(
                InscricaoEventoDTO(
                    evento_id=str(r[0]).strip(),
                    documento=str(r[1]).strip(),
                    nome=str(r[2]).strip(),
                    email=str(r[3]).strip(),
                    telefone=str(r[4]).strip(),
                    fatura=str(r[5]).strip(),
                    status_inscricao=str(r[6]).strip(),
                    valor_venda=float(r[7]),
                    endereco=str(r[8]).strip(),
                    cidade=str(r[9]).strip(),
                    uf=str(r[10]).strip(),
                    cep=str(r[11]).strip(),
                    ent_cod=str(r[12]).strip() if r[12] else None,
                    colabora_projetos=bool(r[13]),
                    ano_mes_ultima_contribuicao=str(r[14]).strip(),
                )
            )
        return itens

    def listar_eventos_cadastrados(self) -> List[EventoResumoDTO]:
        cursor = self._get_cursor()
        sql = """
            SELECT idevento, COUNT(*) as total
            FROM congresso_rcc WITH (NOLOCK)
            GROUP BY idevento
            ORDER BY idevento DESC
        """
        cursor.execute(sql)
        return [
            EventoResumoDTO(id=str(r[0]).strip(), descricao=f"Evento {r[0]}", total_inscritos=int(r[1]))
            for r in cursor.fetchall()
        ]
