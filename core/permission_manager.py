"""
Gerenciador de Permissões e Perfis de Acesso - GeoAlvo / GeoApolo V5
Integração com tabelas:
- USER_geoapolo_usuarios
- USER_geoapolo_grupo
- USER_geoapolo_grupousuario
- USER_geoapolo_objetos
- USER_geoapolo_grupobjetos
"""

import logging
from typing import Dict, List, Optional, Set
import tkinter as tk
from tkinter import messagebox

logger = logging.getLogger(__name__)

# Mapeamento bidirecional de sinônimos / aliases de objetos entre botões Python e Delphi
ALIASES_OBJETOS: Dict[str, List[str]] = {
    # Barra de ferramentas principal (Panel Delphi <-> Frame Python)
    "pnlmenuprincipal": ["toolbar", "barra_ferramentas", "pnlmenuprincipal"],
    
    # Botões da Toolbar Python <-> SpeedButtons Delphi <-> Objeto de catálogo de botão
    "config_bd": ["btn_config_bd", "spbconfiguracoes"],
    "entidades": ["btn_entidades", "spbcadastroentidades"],
    "conciliacao_vindi": ["btn_conciliacao_vindi", "spbconciliavindi", "spbconciliacaovindi"],
    "nova_requisicao": ["btn_nova_requisicao", "spbrequisicao"],
    "troca_empresa": ["btn_troca_empresa", "spbtrocaempresa"],
    "usuarios": ["btn_usuarios", "spbusuarios"],
    "imprimir": ["btn_imprimir", "spbimprimir"],
    "consultas_imediatas": ["btn_consultas_imediatas", "spbconsulta"],
    "sair": ["btn_sair", "spbsair"],
}

# Constrói mapa reverso para lookup imediato em O(1)
MAPA_ALIAS_LOOKUP: Dict[str, List[str]] = {}
for chave_principal, lista_aliases in ALIASES_OBJETOS.items():
    ch_p = chave_principal.lower()
    lista_limpa = [ch_p] + [a.lower() for a in lista_aliases if a.lower() != ch_p]
    for item in lista_limpa:
        MAPA_ALIAS_LOOKUP[item] = lista_limpa

# Mapeamento de Rótulos de Menus para Códigos de Objetos Oficiais do Banco
LABEL_TO_OBJ_NAME: Dict[str, str] = {
    # Configurações
    "banco dados geoalvo/alvo": "mnuconfigbdgeoalvo",
    "banco de dados geoalvo / alvo": "mnuconfigbdgeoalvo",
    "banco dados savic": "mnuconfigbdsavic",
    "banco dados aplicativo rcc": "mnuconfigbdapp",
    "banco de dados": "mnuconfigdatabase",
    "integração api alvo (token & validade)": "mnucfgtokenalvo",
    "integracao api alvo (token & validade)": "mnucfgtokenalvo",
    "parâmetros geoapolo/alvo": "mnucfgparsisgeoapolo",
    "parametros geoapolo/alvo": "mnucfgparsisgeoapolo",
    "parâmetros do sistema geoapolo": "mnucfgparsisgeoapolo",
    "manutenção de versões do geoapolo": "mnuparversaogeoapolo",
    "manutencao de versoes do geoapolo": "mnuparversaogeoapolo",
    "manutenção de códigos do sistema": "mnuparamcodsistema",
    "manutencao de codigos do sistema": "mnuparamcodsistema",
    "parâmetros do sistema": "mnuconfigparametros",
    "parametros do sistema": "mnuconfigparametros",
    "administração de usuários": "mnuconfigadmusuario",
    "administracao de usuarios": "mnuconfigadmusuario",
    "permissões de grupos e usuários": "mnupermissoesgrupousuarios",
    "permissoes de grupos e usuarios": "mnupermissoesgrupousuarios",
    "permissões de grupos": "mnupermissoesgrupo",
    "perfis de acesso a objetos": "mnupermissoesgrupo",
    "permissoes de grupos": "mnupermissoesgrupo",
    "clonar permissões de usuários": "mnuclonarpermissoes",
    "clonar permissoes de usuarios": "mnuclonarpermissoes",
    "permissão em contas financeiras": "mnucontasfinanceiras",
    "permissao em contas financeiras": "mnucontasfinanceiras",
    "desativação / desligamento de usuários": "mnudesligamentousuario",
    "desativacao / desligamento de usuarios": "mnudesligamentousuario",
    "mesclagem / matchcode de usuários": "mnumatchcodeusuario",
    "mesclagem / matchcode de usuarios": "mnumatchcodeusuario",
    "dicionário de nomes amigáveis": "mnunomesamigaveis",
    "dicionario de nomes amigaveis": "mnunomesamigaveis",
    "permissões de acesso": "mnupermissoesacesso",
    "permissoes de acesso": "mnupermissoesacesso",
    "trocar de empresa <f2>": "mnuconfigtrocaempresa",
    "configurações": "mnuconfig",
    "configuracoes": "mnuconfig",

    # Cadastros
    "ativo imobilizado": "mnucadativoimobilizado",
    "categoria de bens": "mnucadcategbens",
    "classificação de ativos": "mnucadclassificacaoativo",
    "classificacao de ativos": "mnucadclassificacaoativo",
    "estações de trabalho": "mnucadestacoes",
    "estacoes de trabalho": "mnucadestacoes",
    "localização física": "mnucadlocalizacaofisica",
    "localizacao fisica": "mnucadlocalizacaofisica",
    "status de hardware/software": "mnucadstatushardsoft",
    "tipos de licenças de software": "mnucadtipolicsoftware",
    "tipos de licencas de software": "mnucadtipolicsoftware",
    "ativo fixo": "mnucadativofixoti",
    "centro de custos/controle": "mnucad_centrocontrole",
    "manutenção centro de controle": "mnucad_mancentrocontrole",
    "manutencao centro de controle": "mnucad_mancentrocontrole",
    "ocorrências & chamados": "mnucad_crm_ocorrencias",
    "ocorrencias & chamados": "mnucad_crm_ocorrencias",
    "cadastros de eventos": "mnucad_crm_eventos",
    "importar inscritos de eventos": "mnucad_crm_importa",
    "cadastros de tipos de campanhas": "mnucad_crm_campanhas",
    "cadastros de tipos de tratamento": "mnucad_crm_tratamentos",
    "crm": "mnucad_crm",
    "categorias": "mnucadentcategorias",
    "entidades": "mnuentidades",
    "importa entidades": "mnuimportaentidades",
    "tipos de tratamento": "mnucadtipotratamento",
    "plano de classes de receitas/despesas": "mnucadfinclasserecdesp",
    "manutenção de cartões de crédito": "mnugacadcartoescredito",
    "manutencao de cartoes de credito": "mnugacadcartoescredito",
    "situação financeira de documentos": "mnucadfinsitcod",
    "situacao financeira de documentos": "mnucadfinsitcod",
    "tipos de cobrança": "mnucadfintipocob",
    "tipos de cobranca": "mnucadfintipocob",
    "financeiro": "mnucadfinanceiro",
    "almoxarifados": "mnucadalmoxarifados",
    "cores": "mnucadcores",
    "grupos de produtos": "mnucadprodutos",
    "marcas": "mnucadmarcas",
    "produtos": "mnucadprodutos",
    "controle de lotes de produtos": "mnucadlotes",
    "estoque": "mnucadestoque",
    "departamentos": "mnucadepartamentos",
    "empresas": "mnucadempresas",
    "geral": "mnucadgeral",
    "usuários geoapolo": "mnucadusuarios",
    "usuarios geoapolo": "mnucadusuarios",
    "cadastros": "mnucadastro",

    # GeoAlvo
    "atualiza inventário de ti": "gamenuativofixo",
    "atualiza inventario de ti": "gamenuativofixo",
    "documentos": "mnudocfinanceiropagar",
    "documento financeiro": "gamenu_doc_fin_pagar",
    "controle de cartões de crédito": "mnugafinctaspagarcartaocredito",
    "controle de cartoes de credito": "mnugafinctaspagarcartaocredito",
    "contas a pagar": "mnugafinctaspagar",
    "documentos a receber": "mnugafincprecdocfin",
    "contas a receber": "mnugactasareceber",
    "importar grupos de oração do savic": "mnugaintegrasavicgo",
    "importar grupos de oracao do savic": "mnugaintegrasavicgo",
    "moderação de grupos de oração savic x alvo": "mnugaintegrasavic_moderago",
    "moderacao de grupos de oracao savic x alvo": "mnugaintegrasavic_moderago",
    "valida entidades alvo x savic": "mnugeosavicvalidaorigem",
    "importa entidades savic -> geoalvo": "mnuimportaentidadesavicgeoapolo",
    "integrar savic x alvo": "mnugeosavic",
    "nova requisição de material": "mnunovarequisicao",
    "nova requisicao de material": "mnunovarequisicao",
    "atendimento": "mnuatendimentoreqs",
    "atendimento de requisições": "mnuatendimentoreqs",
    "cancelamento": "mnucancelamentoreqs",
    "cancelamento de requisições": "mnucancelamentoreqs",
    "devolução": "mnudevolucaoreqs",
    "devolucao": "mnudevolucaoreqs",
    "requisições de materiais": "gamenureqs",
    "requisicoes de materiais": "gamenureqs",
    "movimentação de estoque": "mnumovimentacaoestoque",
    "movimentacao de estoque": "mnumovimentacaoestoque",
    "consulta ficha estoque": "mnuconsfichaestoque",
    "consulta saldo produto": "mnuconssaldoproduto",
    "consulta requisições de materiais": "mnuconsrequisicoes",
    "consulta requisicoes de materiais": "mnuconsrequisicoes",
    "relatórios por almoxarifado": "mnurelalmoxarifados",
    "relatorios por almoxarifado": "mnurelalmoxarifados",
    "consultas": "gamenuconsultas",
    "geoalvo": "mnugeoapolo",

    # Alvo
    "alvo": "mnuapolo",
    "auditoria de cupons fiscais": "mnuapoauditoriacupons",
    "troca cupom fiscal por consumidor final": "mnuapoalojatrocacncf",
    "troca cupom fiscal nomeado por consumidor final": "mnuapoalojatrocacncf",
    "alvo loja": "mnuapoalojatrocacncf",
    "débito x crédito": "mnuapolodebcredcontafin",
    "debito x credito": "mnuapolodebcredcontafin",
    "débito x crédito detalhado": "mnuapolodebcredcontafin",
    "debito x credito detalhado": "mnuapolodebcredcontafin",
    "exclui lançamentos contábeis": "mnuapoexcluilanccontabil",
    "exclui lancamentos contabeis": "mnuapoexcluilanccontabil",
    "corrige lançamentos de cupom fiscal": "mnuapocorrigecupomfiscal",
    "corrige lancamentos de cupom fiscal": "mnuapocorrigecupomfiscal",
    "contabilidade": "mnuapocontabilidade",
    "administração de campanhas": "mnucad_crm_campanhas",
    "administracao de campanhas": "mnucad_crm_campanhas",
    "atualiza valores de campanhas": "mnucad_crm_campanhas",
    "e-mail marketing de campanhas": "mnucad_crm_campanhas",
    "telemarketing de campanhas": "mnucad_crm_campanhas",
    "soluções de ocorrências": "mnucad_crm_ocorrencias",
    "solucoes de ocorrencias": "mnucad_crm_ocorrencias",
    "mesclagem de entidades": "mnumatchcodeusuario",
    "importar inscrições de eventos/congressos": "mnucad_crm_importa",
    "importar inscricoes de eventos/congressos": "mnucad_crm_importa",
    "importa monitoramento lembrete de doações": "mnucad_crm_eventos",
    "importa monitoramento lembrete de doacoes": "mnucad_crm_eventos",
    "integração congressos online x alvo x rdstation": "mnucad_crm_eventos",
    "integracao congressos online x alvo x rdstation": "mnucad_crm_eventos",
    "vincula entidade a diocese": "mnurelacionadiocese",
    "rcc": "mnuapo_fin_rcc",
    "relaciona usuário com categoria": "mnucadentcategorias",
    "relaciona usuario com categoria": "mnucadentcategorias",
    "relaciona usuários, categorias e entidades": "mnucadentcategorias",
    "relaciona usuarios, categorias e entidades": "mnucadentcategorias",
    "relaciona entidade com diocese": "mnurelacionadiocese",
    "gera títulos a receber no alvo": "mnuapologeratitulorecapolo",
    "gera titulos a receber no alvo": "mnuapologeratitulorecapolo",
    "gera remessa para bancos": "mnuapolofingerarecbanco",
    "débito x crédito de conta financeira": "mnuapolodebcredcontafin",
    "debito x credito de conta financeira": "mnuapolodebcredcontafin",
    "atualiza situação de títulos": "mnuapolofinacertasituacaotitulo",
    "atualiza situacao de titulos": "mnuapolofinacertasituacaotitulo",
    "conciliação vindi crédito recorrente (rcc)": "mnuapoloconciliavindi",
    "conciliação vindi crédito recorrente(rcc)": "mnuapoloconciliavindi",
    "conciliacao vindi credito recorrente (rcc)": "mnuapoloconciliavindi",
    "conciliacao vindi credito recorrente(rcc)": "mnuapoloconciliavindi",
    "conciliação vindi": "mnuconciliavindi",
    "conciliacao vindi": "mnuconciliavindi",
    "desativa usuários do alvo": "mnuapolodesativausuario",
    "desativa usuarios do alvo": "mnuapolodesativausuario",
    "clonar permissão de usuários": "mnuapoloclonarpermissao",
    "clonar permissao de usuarios": "mnuapoloclonarpermissao",
    "permissão em contas financeiras": "mnuapolopermsctafin",
    "permissao em contas financeiras": "mnuapolopermsctafin",
    "usuários do alvo": "mnuapolousuarios",
    "usuarios do alvo": "mnuapolousuarios",

    # Utilitários
    "cadastro de consultas imediatas": "mnucadconsultas",
    "consultas imediatas <f4>": "mnuconsultasimediatas",
    "validação de licenças": "mnutlvalidalicenca",
    "validacao de licencas": "mnutlvalidalicenca",
    "enviar e-mail via geoalvo f8": "mnuutlenviaemail",
    "utilitários": "mnutilitarios",
    "utilitarios": "mnutilitarios",

    # Relatórios
    "central de relatórios": "mnurelcentral",
    "central de relatorios": "mnurelcentral",
    "listagem geral de entidades": "mnurellistagemgeral",
    "entidades sincronizadas": "mnurelentidadessinc",
    "entidades pendentes de sincronização": "mnurelentidadespend",
    "entidades pendentes de sincronizacao": "mnurelentidadespend",
    "auditoria e ocorrências": "mnurelauditoria",
    "auditoria e ocorrencias": "mnurelauditoria",
    "relatórios": "mnurelatórios",
    "relatorios": "mnurelatórios",

    # Sair
    "sair": "mnusair",
}


class GestorPermissoes:
    """Gerenciador de regras e permissões de acesso a objetos do sistema"""

    def __init__(self, usuario: str = "", is_admin: bool = False):
        self.usuario = usuario.strip()
        self.is_admin = is_admin or (self.usuario.upper() == "ADMIN")
        self.grupos: List[int] = []
        self.permissoes: Dict[str, bool] = {}  # nome_objeto_lower -> bool (True=A, False=N)

    def pode_acessar(self, identificador: str) -> bool:
        """Verifica se o usuário atual tem permissão para acessar o objeto/recurso.
        
        Regra restritiva ('zero-trust'):
        1. Se for ADMIN (flag is_admin ou login 'ADMIN'), o acesso é irrestrito e absoluto.
        2. Recursos essenciais de encerramento seguro do sistema ('sair', 'btn_sair', 'spbsair', 'mnusair', 'lblf10sair')
           são permitidos por padrão para segurança operacional, a menos que explicitamente negados.
        3. Se o usuário comum não possuir nenhum grupo cadastrado, não tem acesso aos recursos.
        4. Verifica o nome do objeto, rótulo amigável ou aliases:
           - Se encontrado no mapa de permissões: retorna True ('A') ou False ('N').
           - Se NÃO encontrado ou não liberado: retorna False (somente liberar o que estiver liberado).
        """
        if self.is_admin or (self.usuario and self.usuario.upper() == "ADMIN"):
            return True

        if not identificador:
            return False

        chave = identificador.strip().lower()

        # Encerramento seguro do sistema: permitido por padrão, salvo bloqueio explícito
        if chave in ("sair", "btn_sair", "spbsair", "mnusair", "lblf10sair"):
            if chave in self.permissoes:
                return self.permissoes[chave]
            return True

        # Se não possui grupos vinculados e não há permissões manuais carregadas, nega acesso por padrão
        if not self.grupos and not self.permissoes:
            return False

        # 1. Se o nome exato estiver diretamente no dicionário de permissões do usuário
        if chave in self.permissoes:
            return self.permissoes[chave]

        # 2. Se o rótulo amigável estiver mapeado para um objeto oficial
        obj_mapeado = LABEL_TO_OBJ_NAME.get(chave)
        if obj_mapeado and obj_mapeado in self.permissoes:
            return self.permissoes[obj_mapeado]

        # 3. Verifica através dos aliases registrados
        aliases = MAPA_ALIAS_LOOKUP.get(chave)
        if aliases:
            for alias in aliases:
                if alias in self.permissoes:
                    return self.permissoes[alias]

        # 4. Modelo restritivo: objeto não encontrado / não liberado -> Acesso Negado
        return False

    def esta_bloqueado_explicitamente(self, identificador: str) -> bool:
        """Verifica se um recurso foi explicitamente configurado com status Negado (False).
        Útil para contêineres de menu (cascatas): se não houver negação explícita, a cascata
        pode ser exibida caso possua comandos filhos visíveis e liberados."""
        if self.is_admin or (self.usuario and self.usuario.upper() == "ADMIN"):
            return False
        if not identificador:
            return False

        chave = identificador.strip().lower()

        if chave in self.permissoes:
            return not self.permissoes[chave]

        obj_mapeado = LABEL_TO_OBJ_NAME.get(chave)
        if obj_mapeado and obj_mapeado in self.permissoes:
            return not self.permissoes[obj_mapeado]

        aliases = MAPA_ALIAS_LOOKUP.get(chave)
        if aliases:
            for alias in aliases:
                if alias in self.permissoes:
                    return not self.permissoes[alias]

        return False

    def verificar_ou_alerta(self, identificador: str, parent=None, titulo: str = "Acesso Negado") -> bool:
        """Valida permissão e, se bloqueado, exibe aviso visual amigável ao usuário."""
        if not self.pode_acessar(identificador):
            msg = (
                "Acesso Bloqueado!\n\n"
                "Seu perfil de usuário não possui permissão para acessar esta opção.\n"
                "Entre em contato com o Administrador do Sistema."
            )
            messagebox.showwarning(titulo, msg, parent=parent)
            return False
        return True

    @classmethod
    def carregar_do_banco(cls, conn, usuario: str) -> "GestorPermissoes":
        """Carrega do banco de dados (SQL Server) os grupos e permissões do usuário."""
        usu_limpo = (usuario or "").strip()
        if not usu_limpo or usu_limpo.upper() == "ADMIN":
            logger.info("Usuário ADMIN detectado: permissões irrestritas concedidas.")
            return cls(usuario=usu_limpo, is_admin=True)

        gestor = cls(usuario=usu_limpo, is_admin=False)
        if not conn:
            logger.warning("Conexão nula fornecida ao carregar permissões para %s.", usu_limpo)
            return gestor

        try:
            cursor = conn.cursor()

            # 1. Carrega os grupos aos quais o usuário pertence (usucod ou login)
            sql_grupos = """
                SELECT DISTINCT gu.codigo_grupo 
                FROM USER_geoapolo_grupousuario gu WITH(NOLOCK)
                WHERE UPPER(gu.usucod) = ? 
                   OR UPPER(gu.usucod) IN (
                       SELECT UPPER(u.usucod) 
                       FROM USER_geoapolo_usuarios u WITH(NOLOCK) 
                       WHERE UPPER(u.login) = ?
                   )
            """
            cursor.execute(sql_grupos, [usu_limpo.upper(), usu_limpo.upper()])
            rows_grupos = cursor.fetchall()
            gestor.grupos = [r[0] for r in rows_grupos if r[0] is not None]

            if not gestor.grupos:
                logger.info("Usuário '%s' não possui grupos vinculados.", usu_limpo)
                return gestor

            # 2. Carrega as permissões de todos os grupos do usuário
            # ORDER BY uggo.statusacesso DESC garante que 'N' venha antes de 'A',
            # logo se o usuário pertencer a múltiplos grupos, 'A' sobrescreve por último!
            placeholders = ",".join("?" for _ in gestor.grupos)
            sql_permissoes = f"""
                SELECT ugo.nome_objeto, uggo.statusacesso
                FROM USER_geoapolo_grupobjetos uggo WITH(NOLOCK)
                INNER JOIN USER_geoapolo_objetos ugo WITH(NOLOCK) ON uggo.codigo_objeto = ugo.codigo_objeto
                WHERE uggo.codigo_grupo IN ({placeholders})
                ORDER BY uggo.statusacesso DESC
            """
            cursor.execute(sql_permissoes, gestor.grupos)
            rows_perm = cursor.fetchall()

            for r in rows_perm:
                nome_obj = str(r[0] or "").strip().lower()
                status = str(r[1] or "").strip().upper()
                # Status 'A' = Acesso Permitido, qualquer outro ('N', 'B', etc.) = Negado
                gestor.permissoes[nome_obj] = (status == "A")

            logger.info(
                "Permissões carregadas com sucesso para '%s': %d grupos, %d objetos configurados.",
                usu_limpo,
                len(gestor.grupos),
                len(gestor.permissoes),
            )

        except Exception as exc:
            logger.error("Erro ao carregar permissões do usuário '%s' do banco: %s", usu_limpo, exc)

        return gestor


def aplicar_permissoes_toolbar(toolbar_manager, gestor: GestorPermissoes) -> None:
    """Aplica o controle de acesso e visibilidade na barra de ferramentas do GeoAlvo."""
    if not toolbar_manager or not hasattr(toolbar_manager, "toolbar"):
        return

    # Se a barra como um todo estiver bloqueada (objeto pnlmenuprincipal no Delphi/Banco)
    if not gestor.pode_acessar("pnlmenuprincipal"):
        toolbar_manager.toolbar.pack_forget()
        return
    else:
        toolbar_manager.toolbar.pack(side=tk.TOP, fill=tk.X)

    # Delegar para a própria barra se possuir método especializado
    if hasattr(toolbar_manager, "aplicar_permissoes"):
        toolbar_manager.aplicar_permissoes(gestor)
