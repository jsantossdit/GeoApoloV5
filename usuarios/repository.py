"""
Repositório de dados para Gestão de Usuários, Grupos e Perfis de Acesso.
GeoApolo V5
Compatível com SQL Server nativo (WITH NOLOCK) e SQLite em memória.
"""

import sys
from pathlib import Path

# Garante que o diretório raiz esteja no sys.path
_raiz_projeto = str(Path(__file__).resolve().parent.parent)
if _raiz_projeto not in sys.path:
    sys.path.insert(0, _raiz_projeto)

from typing import List, Optional
try:
    from usuarios.models import (
        UsuarioDTO,
        DepartamentoDTO,
        SistemaDTO,
        GrupoUsuarioDTO,
        VinculoGrupoUsuarioDTO,
        ObjetoAcessoDTO,
        PerfilAcessoItemDTO,
    )
except (ImportError, ModuleNotFoundError):
    from models import (
        UsuarioDTO,
        DepartamentoDTO,
        SistemaDTO,
        GrupoUsuarioDTO,
        VinculoGrupoUsuarioDTO,
        ObjetoAcessoDTO,
        PerfilAcessoItemDTO,
    )


CATALOGO_OBJETOS_SISTEMA = [
    # Menu Principal e Barra de Ferramentas
    ("mnuprincipal", "Menu Principal", "Menu Principal"),
    ("pnlmenuprincipal", "Barra de Ferramentas Principal", "Barra de Ferramentas"),
    ("spbtrocaempresa", "Barra: Troca de Empresa <F2>", "Barra de Ferramentas"),
    ("spbcadastroentidades", "Barra: Cadastro de Entidades", "Barra de Ferramentas"),
    ("spbconciliacaovindi", "Barra: Conciliação Vindi (R$)", "Barra de Ferramentas"),
    ("spbocorrenciasapolo", "Barra: CRM Ocorrências & Chamados", "Barra de Ferramentas"),
    ("spbconsulta", "Barra: Consultas Imediatas <F4>", "Barra de Ferramentas"),
    ("spbsair", "Barra: Sair do Sistema <F10>", "Barra de Ferramentas"),
    ("lblf10sair", "Barra: Rótulo Atalho F10 Sair", "Barra de Ferramentas"),
    ("btn_config_bd", "Barra: Configurações do Banco", "Barra de Ferramentas"),
    ("btn_entidades", "Barra: Gestão de Entidades", "Barra de Ferramentas"),
    ("btn_conciliacao_vindi", "Barra: Conciliação Vindi (R$)", "Barra de Ferramentas"),
    ("btn_nova_requisicao", "Barra: Nova Requisição de Materiais", "Barra de Ferramentas"),
    ("btn_troca_empresa", "Barra: Troca de Empresa", "Barra de Ferramentas"),
    ("btn_usuarios", "Barra: Gestão de Usuários", "Barra de Ferramentas"),
    ("btn_imprimir", "Barra: Imprimir (Ctrl+P)", "Barra de Ferramentas"),
    ("btn_consultas_imediatas", "Barra: Consultas Imediatas (Funil)", "Barra de Ferramentas"),
    ("btn_sair", "Barra: Sair do Sistema", "Barra de Ferramentas"),

    # Menus de Configurações
    ("mnuconfig", "Menu: Configurações", "Configurações"),
    ("mnuconfigdatabase", "Submenu: Banco de Dados", "Configurações"),
    ("mnuconfigbdgeoalvo", "Banco de Dados GeoAlvo / Alvo", "Banco de Dados"),
    ("mnuconfigbdsavic", "Banco de Dados Savic", "Banco de Dados"),
    ("mnuconfigbdapp", "Banco de Dados Aplicativo RCC", "Banco de Dados"),
    ("mnucfgtokenalvo", "Integração API Alvo (Token & Validade)", "Configurações"),
    ("mnuconfigparametros", "Submenu: Parâmetros do Sistema", "Configurações"),
    ("mnucfgparsisgeoapolo", "Parâmetros do Sistema GeoApolo", "Configurações"),
    ("mnuparversaogeoapolo", "Manutenção de Versões do GeoApolo", "Configurações"),
    ("mnuparamcodsistema", "Manutenção de Códigos do Sistema", "Configurações"),
    ("mnupermissoesacesso", "Submenu: Permissões de Acesso", "Segurança"),
    ("mnuconfigadmusuario", "Administração de Usuários", "Segurança"),
    ("mnupermissoesgrupousuarios", "Permissões de Grupos e Usuários", "Segurança"),
    ("mnupermissoesgrupo", "Perfis de Acesso a Objetos", "Segurança"),
    ("mnuclonarpermissoes", "Clonar Permissões de Usuários", "Segurança"),
    ("mnucontasfinanceiras", "Permissão em Contas Financeiras", "Segurança"),
    ("mnudesligamentousuario", "Desativação / Desligamento de Usuários", "Segurança"),
    ("mnumatchcodeusuario", "Mesclagem / MatchCode de Usuários", "Segurança"),
    ("mnunomesamigaveis", "Dicionário de Nomes Amigáveis", "Segurança"),
    ("mnuconfigtrocaempresa", "Trocar de Empresa <F2>", "Configurações"),

    # Menus de Cadastros
    ("mnucadastro", "Menu: Cadastros", "Cadastros"),
    ("mnucadativofixoti", "Submenu: Ativo Fixo (TI)", "Ativo Fixo"),
    ("mnucadativoimobilizado", "Ativo Imobilizado", "Ativo Fixo"),
    ("mnucadcategbens", "Categoria de Bens", "Ativo Fixo"),
    ("mnucadclassificacaoativo", "Classificação de Ativos", "Ativo Fixo"),
    ("mnucadestacoes", "Estações de Trabalho", "Ativo Fixo"),
    ("mnucadlocalizacaofisica", "Localização Física", "Ativo Fixo"),
    ("mnucadstatushardsoft", "Status de Hardware e Software", "Ativo Fixo"),
    ("mnucadtipolicsoftware", "Tipos de Licenças de Software", "Ativo Fixo"),
    ("mnucad_centrocontrole", "Centros de Custos e Controle", "Cadastros"),
    ("mnucad_mancentrocontrole", "Manutenção de Centro de Controle", "Cadastros"),
    ("mnucad_crm", "Submenu: CRM", "CRM"),
    ("mnucad_crm_ocorrencias", "CRM - Ocorrências & Chamados", "CRM"),
    ("mnucadeventoscongressos", "Cadastro de Eventos", "CRM"),
    ("mnucad_crm_importa", "Importar Inscritos de Eventos", "CRM"),
    ("mnucadtipocampanha", "Cadastro de Tipos de Campanhas", "CRM"),
    ("mnucad_crm_tratamentos", "Cadastro de Tipos de Tratamento", "CRM"),
    ("mnucadentidades", "Submenu: Entidades", "Cadastros"),
    ("mnucadentcategorias", "Categorias de Entidades", "Cadastros"),
    ("mnuentidades", "Cadastro de Entidades", "Cadastros"),
    ("mnuimportaentidades", "Importar Entidades", "Cadastros"),
    ("mnucadtipotratamento", "Tipos de Tratamento de Entidades", "Cadastros"),
    ("mnucadfinanceiro", "Submenu: Cadastros Financeiros", "Financeiro"),
    ("mnucadfinclasserecdesp", "Plano de Classes de Receitas/Despesas", "Financeiro"),
    ("mnugacadcartoescredito", "Manutenção de Cartões de Crédito", "Financeiro"),
    ("mnucadfinsitcod", "Situação Financeira de Documentos", "Financeiro"),
    ("mnucadfintipocob", "Tipos de Cobrança", "Financeiro"),
    ("mnucadestoque", "Submenu: Cadastros de Estoque", "Estoque"),
    ("mnucadcores", "Cores", "Estoque"),
    ("mnucadmarcas", "Marcas", "Estoque"),
    ("mnucadprodutos", "Produtos", "Estoque"),
    ("mnucadalmoxarifados", "Almoxarifados", "Estoque"),
    ("mnucadlotes", "Controle de Lotes de Produtos", "Estoque"),
    ("MenuItem1", "Submenu: Geral (Cadastros)", "Cadastros"),
    ("mnucadepartamentos", "Departamentos", "Cadastros"),
    ("mnucadempresas", "Empresas", "Cadastros"),
    ("mnucadusuarios", "Usuários GeoApolo", "Segurança"),
    ("mnucorrigecidades", "Correção de Cidades e Distritos", "Cadastros"),
    ("mnurelacionadiocese", "Relacionamento de Dioceses e Entidades", "Cadastros"),

    # Menus de GeoAlvo / GeoApolo
    ("mnugeoapolo", "Menu: GeoAlvo", "GeoAlvo"),
    ("mnugeoapoloativofixoti", "Submenu: Ativo Fixo (Inventário)", "Ativo Fixo"),
    ("mnugeoapoloatualizaativofixoti", "Atualiza Inventário de TI", "Ativo Fixo"),
    ("mnugafinanceiro", "Submenu: Financeiro GeoAlvo", "Financeiro"),
    ("mnugafinctaspagar", "Submenu: Contas a Pagar", "Financeiro"),
    ("mnudocfinanceiropagar", "Documentos Financeiros a Pagar", "Financeiro"),
    ("mnugafinctaspagarcartaocredito", "Controle de Cartões de Crédito", "Financeiro"),
    ("mnugactasareceber", "Submenu: Contas a Receber", "Financeiro"),
    ("mnugafincprecdocfin", "Documentos Financeiros a Receber", "Financeiro"),
    ("gamenuestoque", "Submenu: Estoque GeoAlvo", "Estoque"),
    ("gamenureqs", "Submenu: Requisições de Materiais", "Estoque"),
    ("mnunovarequisicao", "Nova Requisição de Material", "Estoque"),
    ("mnuatendimentoreqs", "Atendimento de Requisições", "Estoque"),
    ("mnucancelamentoreqs", "Cancelamento de Requisições", "Estoque"),
    ("mnudevolucaoreqs", "Devolução de Requisições", "Estoque"),
    ("mnumovimentacaoestoque", "Movimentação de Estoque", "Estoque"),
    ("gamenuconsultas", "Submenu: Consultas de Estoque", "Estoque"),
    ("mnuconsfichaestoque", "Consulta Ficha de Estoque (Kardex)", "Estoque"),
    ("mnuconssaldoproduto", "Consulta Saldo de Produtos", "Estoque"),
    ("mnuconsrequisicoes", "Consulta Requisições de Materiais", "Estoque"),
    ("mnurelalmoxarifados", "Relatórios por Almoxarifado", "Estoque"),

    # Menus de Integração SAVIC x Alvo
    ("mnugeosavic", "Menu: Integrar SAVIC x Alvo", "Integração SAVIC"),
    ("mnugaintegrasavicgo", "Importar Grupos de Oração do SAVIC", "Integração SAVIC"),
    ("mnugaintegrasavic_moderago", "Moderação de Grupos de Oração Savic x Alvo", "Integração SAVIC"),
    ("mnugeosavicvalidaorigem", "Valida Entidades Alvo x Savic", "Integração SAVIC"),
    ("mnuimportaentidadesavicgeoapolo", "Importa Entidades Savic -> GeoAlvo", "Integração SAVIC"),

    # Menus de Alvo
    ("mnuapolo", "Menu: Alvo", "Alvo"),
    ("mnuapoalvoloja", "Submenu: Alvo Loja", "Alvo"),
    ("mnuapoauditoriacupons", "Auditoria de Cupons Fiscais", "Fiscal"),
    ("mnuapoalojatrocacncf", "Troca Cupom Fiscal por Consumidor Final", "Fiscal"),
    ("mnuapolocontabilidade", "Submenu: Contabilidade", "Contabilidade"),
    ("mnuapolocontabdebcredconta", "Débito x Crédito", "Contabilidade"),
    ("mnuapoctbdebxcredetalhe", "Débito x Crédito Detalhado", "Contabilidade"),
    ("mnuapoloexcluilctocontabil", "Excluir Lançamentos Contábeis", "Contabilidade"),
    ("mnuapoctbcorrigecupom", "Corrige Lançamentos Cupom Fiscal", "Contabilidade"),
    ("mnuapolocrm", "Submenu: CRM Alvo", "CRM"),
    ("mnuapolocrmadmcampanha", "Administração de Campanhas", "CRM"),
    ("mnuapocrmatualizacampanha", "Atualiza Valores de Campanhas", "CRM"),
    ("mnuapoemailmktcamp", "E-Mail Marketing de Campanhas", "CRM"),
    ("mnuapotlmktcamp", "TeleMarketing de Campanhas", "CRM"),
    ("mnu_apolosolocorrencia", "Soluções de Ocorrências", "CRM"),
    ("mnucrmapolomatchcode", "Mesclagem de Entidades", "CRM"),
    ("mnuapo_crm_rcc", "Submenu: CRM RCC", "CRM"),
    ("mnuapo_crm_rcc_importa_trackemail", "Importa Monitoramento Lembrete Doações", "CRM"),
    ("mnuapo_ent_rcc_integracongressos", "Integração Congressos ONLINE x Alvo x RdStation", "CRM"),
    ("mnuapo_ent_rcc_vinculaent_dio", "Vincula Entidade a Diocese", "Cadastros"),
    ("mnuapoloentidades", "Submenu: Entidades Alvo", "Cadastros"),
    ("mnuapoloentidaderelaccateg", "Relaciona Usuário com Categoria", "Cadastros"),
    ("mnurelacionausuariocategentidade", "Relaciona Usuários, Categorias e Entidades", "Cadastros"),
    ("mnuapo_ent_rcc", "Submenu: Entidades RCC", "Cadastros"),
    ("mnuapo_ent_rcc_reclassifica", "Reclassificação de Entidades", "Cadastros"),
    ("mnuapo_ent_rcc_relacent_dio", "Relaciona Entidade com Diocese", "Cadastros"),
    ("mnuapolofinanceiro", "Submenu: Financeiro Alvo", "Financeiro"),
    ("mnuapologeratitulorecapolo", "Gerar Títulos a Receber no Alvo", "Financeiro"),
    ("mnuapolofingerarecbanco", "Gerar Remessa para Bancos", "Financeiro"),
    ("mnuapolodebcredcontafin", "Débito x Crédito de Conta Financeira", "Financeiro"),
    ("mnuapolofinacertasituacaotitulo", "Atualiza Situação de Títulos", "Financeiro"),
    ("mnuapo_fin_rcc", "Submenu: Financeiro RCC", "Financeiro"),
    ("mnuapoloconciliavindi", "Conciliação Vindi Crédito Recorrente (RCC)", "Financeiro"),
    ("mnudashboardvindi", "Dashboard Vindi", "Financeiro"),
    ("mnudashboarddoacoes", "Dashboard de Doações & IA (1.01)", "Financeiro"),
    ("mnusincronizardashboard", "Sincronizar Dashboard com o Banco", "Financeiro"),
    ("mnuapo_fin_fotograv", "Submenu: Fotograv", "Financeiro"),
    ("mnuapo_fin_fotograv_acertaretornoitau", "Acerta Arquivo Retorno Receber do ITAU", "Financeiro"),
    ("mnuapo_localidade", "Submenu: Localidades", "Cadastros"),
    ("mnuapolocorrigedistritocidades", "Correção de Distritos / Cidades", "Cadastros"),
    ("mnuapo_os", "Submenu: Ordens de Serviço", "Serviços"),
    ("mnuapo_os_fotograv", "Submenu: OS Fotograv", "Serviços"),
    ("mnuapo_os_fotograv_cmutilizados", "Manutenção de CM Utilizados", "Serviços"),
    ("mnuapo_os_fotograv_apuracm_faturado", "Apura CM Faturado", "Serviços"),
    ("mnuapo_os_fotograv_acertacmutilizado", "Acerta CM Utilizado", "Serviços"),
    ("mnuapolousuarios", "Submenu: Usuários do Alvo", "Segurança"),
    ("mnuapolodesativausuario", "Desativa Usuários do Alvo", "Segurança"),
    ("mnuapoloclonarpermissao", "Clonar Permissão de Usuários", "Segurança"),
    ("mnuapolopermsctafin", "Permissão em Contas Financeiras", "Segurança"),

    # Menus de Utilitários e Consultas
    ("mnutilitarios", "Menu: Utilitários", "Utilitários"),
    ("mnucadconsultas", "Cadastro e Manutenção de Consultas", "Consultas"),
    ("mnuutilconsimediatas", "Consultas Imediatas <F4>", "Consultas"),
    ("mnutilconsimediatascadconsulta", "Cadastrar Consultas", "Consultas"),
    ("mnuconsimediatasexec", "Executar Consultas", "Consultas"),
    ("mnutlvalidalicenca", "Validação de Licenças", "Utilitários"),
    ("mnuutlenviaemail", "Enviar E-Mail via GeoAlvo / GeoApolo", "Utilitários"),

    # Menus de Relatórios
    ("mnurelatórios", "Menu: Relatórios", "Relatórios"),
    ("mnurelcentral", "Central de Relatórios", "Relatórios"),
    ("mnurellistagemgeral", "Listagem Geral de Entidades", "Relatórios"),
    ("mnurelentidadessinc", "Entidades Sincronizadas", "Relatórios"),
    ("mnurelentidadespend", "Entidades Pendentes de Sincronização", "Relatórios"),
    ("mnurelauditoria", "Auditoria e Ocorrências", "Relatórios"),

    # Menus de Ajuda e Saída
    ("mnuajuda", "Menu: Ajuda", "Ajuda"),
    ("mnusobre", "Sobre o GeoAlvo", "Ajuda"),
    ("mnusair", "Sair do Sistema", "Geral"),
]


class UsuariosRepository:
    """Repositório de persistência e consultas para Usuários e Perfis de Acesso."""

    def __init__(self, connection):
        self.conn = connection
        self._is_sql_server = not hasattr(connection, "isolation_level")
        self._colunas_usuarios = self._obter_colunas("USER_geoapolo_usuarios")
        self._colunas_objetos = self._obter_colunas("USER_geoapolo_objetos")

    def _obter_colunas(self, nome_tabela: str) -> set:
        try:
            cur = self.conn.cursor()
            cur.execute(f"SELECT * FROM {nome_tabela} WHERE 1=0")
            if cur.description:
                return {desc[0].lower() for desc in cur.description}
        except Exception:
            pass
        return set()

    def _garantir_estrutura_tabela_objetos(self):
        """Garante que USER_geoapolo_objetos possua as colunas categoria e nome_amigavel."""
        colunas = self._obter_colunas("USER_geoapolo_objetos")
        if not colunas:
            return

        cur = self.conn.cursor()
        alterou = False

        if "nome_amigavel" not in colunas:
            try:
                cur.execute("ALTER TABLE USER_geoapolo_objetos ADD nome_amigavel VARCHAR(150) NULL")
                if "nome_oficial" in colunas:
                    cur.execute("UPDATE USER_geoapolo_objetos SET nome_amigavel = COALESCE(nome_oficial, nome_objeto) WHERE nome_amigavel IS NULL")
                else:
                    cur.execute("UPDATE USER_geoapolo_objetos SET nome_amigavel = nome_objeto WHERE nome_amigavel IS NULL")
                alterou = True
            except Exception as e:
                logger.warning(f"Não foi possível adicionar coluna nome_amigavel: {e}")

        if "categoria" not in colunas:
            try:
                cur.execute("ALTER TABLE USER_geoapolo_objetos ADD categoria VARCHAR(80) NULL")
                cur.execute("UPDATE USER_geoapolo_objetos SET categoria = 'Geral' WHERE categoria IS NULL")
                alterou = True
            except Exception as e:
                logger.warning(f"Não foi possível adicionar coluna categoria: {e}")

        if alterou:
            try:
                self.conn.commit()
            except Exception:
                pass
            self._colunas_objetos = self._obter_colunas("USER_geoapolo_objetos")

    def sincronizar_ou_inicializar_objetos(self, empresa: str = "1", apenas_se_vazia: bool = False) -> int:
        """
        Sincroniza e inicializa os objetos do sistema em bases novas ou existentes de forma incremental.
        - Se apenas_se_vazia=True, executa somente se USER_geoapolo_objetos estiver vazia.
        - Insere novos objetos do catálogo que ainda não existem em USER_geoapolo_objetos.
        - Atualiza objetos existentes com nomes genéricos (ex: TMainMenu, TPanel, TSpeedButton, etc.) para os nomes amigáveis oficiais.
        - Garante que todos os grupos de segurança existentes possuam vínculos em USER_geoapolo_grupobjetos
          (com status 'A' para administradores e 'N' para os demais).
        Retorna a quantidade de objetos modificados (inseridos + atualizados).
        """
        self._garantir_estrutura_tabela_objetos()
        cur = self.conn.cursor()
        nolock = self._nolock()

        colunas = self._obter_colunas("USER_geoapolo_objetos")
        if not colunas:
            return 0

        if apenas_se_vazia:
            try:
                cur.execute(f"SELECT COUNT(*) FROM USER_geoapolo_objetos {nolock}")
                qtd = cur.fetchone()[0]
                if qtd > 0:
                    return 0
            except Exception:
                return 0

        tem_categoria = "categoria" in colunas
        tem_amigavel = "nome_amigavel" in colunas
        tem_oficial = "nome_oficial" in colunas

        # Lista grupos existentes
        try:
            cur.execute(f"SELECT codigo_grupo FROM USER_geoapolo_grupo {nolock}")
            grupos = [str(r[0]).strip() for r in cur.fetchall() if r[0] is not None]
        except Exception:
            grupos = []

        # Carrega objetos existentes para mapeamento rápido
        cols_query = ["nome_objeto", "codigo_objeto"]
        if tem_amigavel:
            cols_query.append("nome_amigavel")
        if tem_categoria:
            cols_query.append("categoria")

        try:
            cur.execute(f"SELECT {', '.join(cols_query)} FROM USER_geoapolo_objetos {nolock}")
            objetos_existentes = {}
            for r in cur.fetchall():
                nome_obj_db = str(r[0]).strip().upper() if r[0] else ""
                if not nome_obj_db:
                    continue
                cod_obj_db = str(r[1]) if r[1] is not None else ""
                amigavel_db = str(r[2]).strip() if tem_amigavel and len(r) > 2 and r[2] is not None else ""
                cat_db = str(r[3]).strip() if tem_categoria and len(r) > 3 and r[3] is not None else ""
                objetos_existentes[nome_obj_db] = {
                    "codigo_objeto": cod_obj_db,
                    "nome_amigavel": amigavel_db,
                    "categoria": cat_db,
                }
        except Exception as e:
            logger.error(f"Erro ao carregar objetos existentes: {e}")
            objetos_existentes = {}

        # Carrega vínculos existentes em USER_geoapolo_grupobjetos
        vinculos_existentes = set()
        try:
            cur.execute(f"SELECT codigo_grupo, codigo_objeto FROM USER_geoapolo_grupobjetos {nolock}")
            for r in cur.fetchall():
                if r[0] is not None and r[1] is not None:
                    vinculos_existentes.add((str(r[0]).strip().upper(), str(r[1]).strip().upper()))
        except Exception:
            vinculos_existentes = set()

        from core.recursos import geoapolo_configcod

        inseridos = 0
        atualizados = 0

        # Nomes que indicam valor genérico gerado pelo Delphi ou padrão vazio
        classes_delphi_genericas = {
            "tmainmenu", "tpanel", "tspeedbutton", "tmenuitem", "tbutton",
            "ttoolbutton", "geral", ""
        }

        for nome_obj, nome_amigavel, cat in CATALOGO_OBJETOS_SISTEMA:
            key = nome_obj.strip().upper()
            try:
                if key in objetos_existentes:
                    info = objetos_existentes[key]
                    cod_objeto = info["codigo_objeto"]
                    amig_atual = info["nome_amigavel"]
                    cat_atual = info["categoria"]

                    # Atualiza se o nome amigavel ou a categoria forem genéricos
                    precisa_update = False
                    upd_amigavel = amig_atual
                    upd_cat = cat_atual

                    if tem_amigavel and (amig_atual.lower() in classes_delphi_genericas or amig_atual.lower() == key.lower()):
                        upd_amigavel = nome_amigavel
                        precisa_update = True

                    if tem_categoria and (cat_atual.lower() in classes_delphi_genericas or not cat_atual):
                        upd_cat = cat
                        precisa_update = True

                    if precisa_update:
                        upd_campos = []
                        upd_vals = []
                        if tem_amigavel:
                            upd_campos.append("nome_amigavel = ?")
                            upd_vals.append(upd_amigavel)
                        if tem_oficial:
                            upd_campos.append("nome_oficial = ?")
                            upd_vals.append(upd_amigavel)
                        if tem_categoria:
                            upd_campos.append("categoria = ?")
                            upd_vals.append(upd_cat)

                        if upd_campos:
                            upd_vals.append(cod_objeto)
                            sql_upd = f"UPDATE USER_geoapolo_objetos SET {', '.join(upd_campos)} WHERE codigo_objeto = ?"
                            cur.execute(sql_upd, upd_vals)
                            atualizados += 1
                            info["nome_amigavel"] = upd_amigavel
                            info["categoria"] = upd_cat
                else:
                    # Objeto novo: insere
                    try:
                        cod_objeto = geoapolo_configcod(empresa, "USER_geoapolo_objetos", "Sim", self.conn)
                    except Exception:
                        try:
                            cur.execute("SELECT COALESCE(MAX(CAST(codigo_objeto AS INT)), 0) + 1 FROM USER_geoapolo_objetos")
                            cod_objeto = str(cur.fetchone()[0])
                        except Exception:
                            cod_objeto = str(len(objetos_existentes) + inseridos + 1)

                    campos = ["codigo_objeto", "nome_objeto"]
                    valores = [cod_objeto, nome_obj]

                    if tem_amigavel:
                        campos.append("nome_amigavel")
                        valores.append(nome_amigavel)
                    if tem_oficial:
                        campos.append("nome_oficial")
                        valores.append(nome_amigavel)
                    if tem_categoria:
                        campos.append("categoria")
                        valores.append(cat)

                    cols_str = ", ".join(campos)
                    placeholders = ", ".join("?" for _ in campos)
                    cur.execute(f"INSERT INTO USER_geoapolo_objetos ({cols_str}) VALUES ({placeholders})", valores)
                    inseridos += 1
                    objetos_existentes[key] = {
                        "codigo_objeto": cod_objeto,
                        "nome_amigavel": nome_amigavel,
                        "categoria": cat,
                    }

                # Garante vínculos em USER_geoapolo_grupobjetos para os grupos existentes
                for grp in grupos:
                    vinc_key = (grp.strip().upper(), str(cod_objeto).strip().upper())
                    if vinc_key not in vinculos_existentes:
                        # Se for grupo de administradores ('1' ou 'ADMIN'), libera por padrão ('A'), senão bloqueia ('N')
                        status_inicial = "A" if grp.strip().upper() in ("1", "ADMIN") else "N"
                        cur.execute(
                            "INSERT INTO USER_geoapolo_grupobjetos (codigo_grupo, codigo_objeto, statusacesso) VALUES (?, ?, ?)",
                            [grp, cod_objeto, status_inicial]
                        )
                        vinculos_existentes.add(vinc_key)
            except Exception as e:
                logger.error(f"Erro ao sincronizar objeto '{nome_obj}': {e}")

        # Garante retroativamente que 100% dos pares (grupo, objeto) possuam registro em USER_geoapolo_grupobjetos
        try:
            cur.execute("""
                INSERT INTO USER_geoapolo_grupobjetos (codigo_grupo, codigo_objeto, statusacesso)
                SELECT g.codigo_grupo, o.codigo_objeto,
                       CASE WHEN UPPER(LTRIM(RTRIM(g.codigo_grupo))) IN ('1', 'ADMIN') THEN 'A' ELSE 'N' END
                FROM USER_geoapolo_grupo g
                CROSS JOIN USER_geoapolo_objetos o
                LEFT JOIN USER_geoapolo_grupobjetos go
                  ON go.codigo_grupo = g.codigo_grupo AND go.codigo_objeto = o.codigo_objeto
                WHERE go.codigo_objeto IS NULL
            """)
        except Exception as e:
            logger.debug(f"Aviso ao garantir vínculos cruzados grupobjetos: {e}")

        try:
            self.conn.commit()
        except Exception:
            pass
        return inseridos + atualizados

    def _nolock(self) -> str:
        return "WITH (NOLOCK)" if self._is_sql_server else ""

    def listar_usuarios(self, filtro_nome: str = "", apenas_ativos: bool = True) -> List[UsuarioDTO]:
        """Lista usuários cadastrados com suporte a filtro e status."""
        cur = self.conn.cursor()
        nolock = self._nolock()

        col_senha_alvo = "u.senha_alvo" if "senha_alvo" in self._colunas_usuarios else "'' AS senha_alvo"
        col_usucod_apolo = "u.usucod_apolo" if "usucod_apolo" in self._colunas_usuarios else "'' AS usucod_apolo"

        sql = f"""
            SELECT u.codigo_usuario, u.usucod, u.nome_completo, u.flagativo, u.login, u.email,
                   u.data_nascimento, u.codigo_departamento, d.nome_departamento, {col_usucod_apolo},
                   {col_senha_alvo}, u.senha
            FROM USER_geoapolo_usuarios u {nolock}
            LEFT JOIN USER_geoapolo_departamentos d {nolock} ON u.codigo_departamento = d.codigo_departamento
            WHERE 1=1
        """
        params = []
        if apenas_ativos:
            sql += " AND u.flagativo IN ('A', 'S')"
        if filtro_nome.strip():
            sql += " AND (u.nome_completo LIKE ? OR u.login LIKE ?)"
            termo = f"%{filtro_nome.strip()}%"
            params.extend([termo, termo])

        sql += " ORDER BY u.nome_completo ASC"

        cur.execute(sql, params)
        rows = cur.fetchall()
        usuarios = []
        for r in rows:
            usuarios.append(UsuarioDTO(
                codigo_usuario=str(r[0] or ""),
                usucod=str(r[1] or ""),
                nome_completo=str(r[2] or ""),
                flagativo=str(r[3] or "A"),
                login=str(r[4] or ""),
                email=str(r[5] or ""),
                data_nascimento=str(r[6]) if r[6] else None,
                codigo_departamento=str(r[7] or ""),
                nome_departamento=str(r[8] or ""),
                usucod_apolo=str(r[9] or ""),
                senha_alvo=str(r[10] or ""),
                senha=str(r[11] or ""),
            ))
        return usuarios

    def obter_usuario_por_usucod(self, usucod: str) -> Optional[UsuarioDTO]:
        """Localiza usuário pelo código identificador (usucod)."""
        cur = self.conn.cursor()
        nolock = self._nolock()

        col_senha_alvo = "u.senha_alvo" if "senha_alvo" in self._colunas_usuarios else "'' AS senha_alvo"
        col_usucod_apolo = "u.usucod_apolo" if "usucod_apolo" in self._colunas_usuarios else "'' AS usucod_apolo"

        sql = f"""
            SELECT u.codigo_usuario, u.usucod, u.nome_completo, u.flagativo, u.login, u.email,
                   u.data_nascimento, u.codigo_departamento, d.nome_departamento, {col_usucod_apolo},
                   {col_senha_alvo}, u.senha
            FROM USER_geoapolo_usuarios u {nolock}
            LEFT JOIN USER_geoapolo_departamentos d {nolock} ON u.codigo_departamento = d.codigo_departamento
            WHERE u.usucod = ?
        """
        cur.execute(sql, [usucod])
        r = cur.fetchone()
        if not r:
            return None
        return UsuarioDTO(
            codigo_usuario=str(r[0] or ""),
            usucod=str(r[1] or ""),
            nome_completo=str(r[2] or ""),
            flagativo=str(r[3] or "A"),
            login=str(r[4] or ""),
            email=str(r[5] or ""),
            data_nascimento=str(r[6]) if r[6] else None,
            codigo_departamento=str(r[7] or ""),
            nome_departamento=str(r[8] or ""),
            usucod_apolo=str(r[9] or ""),
            senha_alvo=str(r[10] or ""),
            senha=str(r[11] or ""),
        )

    def obter_usuario_por_login(self, login: str) -> Optional[UsuarioDTO]:
        """Localiza usuário pelo login único de acesso."""
        cur = self.conn.cursor()
        nolock = self._nolock()

        col_senha_alvo = "u.senha_alvo" if "senha_alvo" in self._colunas_usuarios else "'' AS senha_alvo"
        col_usucod_apolo = "u.usucod_apolo" if "usucod_apolo" in self._colunas_usuarios else "'' AS usucod_apolo"

        sql = f"""
            SELECT u.codigo_usuario, u.usucod, u.nome_completo, u.flagativo, u.login, u.email,
                   u.data_nascimento, u.codigo_departamento, d.nome_departamento, {col_usucod_apolo},
                   {col_senha_alvo}, u.senha
            FROM USER_geoapolo_usuarios u {nolock}
            LEFT JOIN USER_geoapolo_departamentos d {nolock} ON u.codigo_departamento = d.codigo_departamento
            WHERE u.login = ?
        """
        cur.execute(sql, [login])
        r = cur.fetchone()
        if not r:
            return None
        return UsuarioDTO(
            codigo_usuario=str(r[0] or ""),
            usucod=str(r[1] or ""),
            nome_completo=str(r[2] or ""),
            flagativo=str(r[3] or "A"),
            login=str(r[4] or ""),
            email=str(r[5] or ""),
            data_nascimento=str(r[6]) if r[6] else None,
            codigo_departamento=str(r[7] or ""),
            nome_departamento=str(r[8] or ""),
            usucod_apolo=str(r[9] or ""),
            senha_alvo=str(r[10] or ""),
            senha=str(r[11] or ""),
        )

    @staticmethod
    def _tratar_inteiro(valor) -> Optional[int]:
        if valor is None:
            return None
        v_str = str(valor).strip()
        if not v_str:
            return None
        try:
            return int(float(v_str))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _tratar_data(valor) -> Optional[str]:
        if valor is None:
            return None
        v_str = str(valor).strip()
        if not v_str or v_str == "None":
            return None
        return v_str

    def _proximo_codigo_usuario(self) -> int:
        """Gera o próximo código sequencial numérico para usuário via configcod ou MAX."""
        cur = self.conn.cursor()
        maior_na_tabela = 0
        try:
            cur.execute("SELECT COALESCE(MAX(CAST(codigo_usuario AS INT)), 0) FROM USER_geoapolo_usuarios")
            r = cur.fetchone()
            if r and r[0] is not None:
                maior_na_tabela = int(r[0])
        except Exception:
            pass

        try:
            from core.recursos import geoapolo_configcod
            cod_gen = int(geoapolo_configcod("1", "USER_geoapolo_usuarios", "Sim", self.conn))
            if cod_gen <= maior_na_tabela:
                cod_gen = maior_na_tabela + 1
                try:
                    cur.execute(
                        "UPDATE USER_geoapolo_configcod SET proximo_codigo = ?, ultimo_numero_utilizado = ? WHERE UPPER(geotabela) = 'USER_GEOAPOLO_USUARIOS'",
                        [cod_gen + 1, cod_gen]
                    )
                    self.conn.commit()
                except Exception:
                    pass
            return cod_gen
        except Exception:
            return maior_na_tabela + 1

    def salvar_usuario(self, u: UsuarioDTO) -> bool:
        """Insere ou atualiza os dados de um usuário."""
        cur = self.conn.cursor()
        existente = self.obter_usuario_por_usucod(u.usucod)

        cod_depto = self._tratar_inteiro(u.codigo_departamento)
        dt_nasc = self._tratar_data(u.data_nascimento)

        if existente:
            cod_usuario = self._tratar_inteiro(u.codigo_usuario) or self._tratar_inteiro(existente.codigo_usuario)
            campos_update = [
                ("nome_completo", u.nome_completo),
                ("flagativo", u.flagativo),
                ("login", u.login),
                ("email", u.email),
                ("data_nascimento", dt_nasc),
                ("codigo_departamento", cod_depto),
            ]
            if cod_usuario is not None:
                campos_update.append(("codigo_usuario", cod_usuario))
            if "usucod_apolo" in self._colunas_usuarios:
                campos_update.append(("usucod_apolo", u.usucod_apolo))
            if "senha_alvo" in self._colunas_usuarios:
                campos_update.append(("senha_alvo", u.senha_alvo))
            campos_update.append(("senha", u.senha))

            set_clause = ", ".join(f"{c[0]} = ?" for c in campos_update)
            params = [c[1] for c in campos_update] + [u.usucod]
            sql = f"UPDATE USER_geoapolo_usuarios SET {set_clause} WHERE usucod = ?"
            cur.execute(sql, params)
        else:
            cod_usuario = self._tratar_inteiro(u.codigo_usuario)
            if cod_usuario is None:
                cod_usuario = self._proximo_codigo_usuario()

            campos_insert = [
                ("codigo_usuario", cod_usuario),
                ("usucod", u.usucod),
                ("nome_completo", u.nome_completo),
                ("flagativo", u.flagativo),
                ("login", u.login),
                ("email", u.email),
                ("data_nascimento", dt_nasc),
                ("codigo_departamento", cod_depto),
            ]
            if "usucod_apolo" in self._colunas_usuarios:
                campos_insert.append(("usucod_apolo", u.usucod_apolo))
            if "senha_alvo" in self._colunas_usuarios:
                campos_insert.append(("senha_alvo", u.senha_alvo))
            campos_insert.append(("senha", u.senha))

            cols_str = ", ".join(c[0] for c in campos_insert)
            placeholders = ", ".join("?" for _ in campos_insert)
            params = [c[1] for c in campos_insert]
            sql = f"INSERT INTO USER_geoapolo_usuarios ({cols_str}) VALUES ({placeholders})"
            cur.execute(sql, params)

        self.conn.commit()
        return True

    def excluir_usuario(self, usucod: str) -> bool:
        """Remove o usuário e seus vínculos de sistemas e grupos."""
        cur = self.conn.cursor()
        cur.execute("DELETE FROM USER_geoapolo_usuariossistemas WHERE usucod = ?", [usucod])
        cur.execute("DELETE FROM USER_geoapolo_grupousuario WHERE usucod = ?", [usucod])
        cur.execute("DELETE FROM USER_geoapolo_usuarios WHERE usucod = ?", [usucod])
        self.conn.commit()
        return True

    def listar_departamentos(self, empcod: str = "") -> List[DepartamentoDTO]:
        """Lista departamentos ativos cadastrados."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT ugd.codigo_departamento, ugd.nome_departamento, ugd.empcod,
                   COALESCE(uge.empnome, '') AS empnome, ugd.flagativo
            FROM USER_geoapolo_departamentos ugd {nolock}
            LEFT JOIN USER_geoapolo_empresas uge {nolock} ON ugd.empcod = uge.empcod
            WHERE (ugd.flagativo IN ('A', 'S') OR ugd.flagativo IS NULL OR ugd.flagativo = '')
        """
        params = []
        if empcod.strip():
            sql += " AND ugd.empcod = ?"
            params.append(empcod.strip())
        sql += " ORDER BY ugd.nome_departamento ASC"

        cur.execute(sql, params)
        return [
            DepartamentoDTO(
                codigo_departamento=str(r[0]).strip(),
                nome_departamento=str(r[1] or "").strip(),
                empcod=str(r[2] or "").strip(),
                empnome=str(r[3] or "").strip(),
                flagativo=str(r[4] or "A").strip().upper(),
            )
            for r in cur.fetchall()
        ]

    def listar_sistemas(self) -> List[SistemaDTO]:
        """Lista todos os sistemas corporativos disponíveis."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        sql = f"SELECT codigo_sistema, descricao, COALESCE(sigla, '') FROM USER_geoapolo_sistemas {nolock} ORDER BY descricao ASC"
        cur.execute(sql)
        return [
            SistemaDTO(
                codigo_sistema=str(r[0]),
                descricao=str(r[1]),
                sigla=str(r[2] or ""),
            )
            for r in cur.fetchall()
        ]

    def listar_sistemas_usuario(self, usucod: str) -> List[SistemaDTO]:
        """Lista sistemas vinculados a um usuário específico."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT s.codigo_sistema, s.descricao, COALESCE(s.sigla, '')
            FROM USER_geoapolo_usuariossistemas us {nolock}
            INNER JOIN USER_geoapolo_sistemas s {nolock} ON us.codigo_sistema = s.codigo_sistema
            WHERE us.usucod = ?
            ORDER BY s.descricao ASC
        """
        cur.execute(sql, [usucod])
        return [
            SistemaDTO(
                codigo_sistema=str(r[0]),
                descricao=str(r[1]),
                sigla=str(r[2] or ""),
            )
            for r in cur.fetchall()
        ]

    def vincular_sistema_usuario(self, usucod: str, codigo_sistema: str) -> bool:
        """Associa um sistema ao usuário."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT 1 FROM USER_geoapolo_usuariossistemas WHERE usucod = ? AND codigo_sistema = ?",
            [usucod, codigo_sistema],
        )
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO USER_geoapolo_usuariossistemas (usucod, codigo_sistema) VALUES (?, ?)",
                [usucod, codigo_sistema],
            )
            self.conn.commit()
        return True

    def desvincular_sistema_usuario(self, usucod: str, codigo_sistema: str) -> bool:
        """Remove associação entre usuário e sistema."""
        cur = self.conn.cursor()
        cur.execute(
            "DELETE FROM USER_geoapolo_usuariossistemas WHERE usucod = ? AND codigo_sistema = ?",
            [usucod, codigo_sistema],
        )
        self.conn.commit()
        return True

    def listar_grupos(self) -> List[GrupoUsuarioDTO]:
        """Lista todos os grupos e quantidade de usuários participantes."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT g.codigo_grupo, g.descricao, COUNT(gu.usucod) AS total_usuarios
            FROM USER_geoapolo_grupo g {nolock}
            LEFT JOIN USER_geoapolo_grupousuario gu {nolock} ON g.codigo_grupo = gu.codigo_grupo
            GROUP BY g.codigo_grupo, g.descricao
            ORDER BY g.descricao ASC
        """
        cur.execute(sql)
        return [
            GrupoUsuarioDTO(
                codigo_grupo=str(r[0]),
                descricao=str(r[1]),
                total_usuarios=int(r[2] or 0),
            )
            for r in cur.fetchall()
        ]

    def obter_grupo(self, codigo_grupo: str) -> Optional[GrupoUsuarioDTO]:
        """Localiza um grupo pelo seu código."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        cur.execute(
            f"SELECT codigo_grupo, descricao FROM USER_geoapolo_grupo {nolock} WHERE codigo_grupo = ?",
            [codigo_grupo],
        )
        r = cur.fetchone()
        if not r:
            return None
        return GrupoUsuarioDTO(codigo_grupo=str(r[0]), descricao=str(r[1]))

    def salvar_grupo(self, codigo_grupo: str, descricao: str) -> bool:
        """Cria ou atualiza grupo de usuários."""
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM USER_geoapolo_grupo WHERE codigo_grupo = ?", [codigo_grupo])
        if cur.fetchone():
            cur.execute(
                "UPDATE USER_geoapolo_grupo SET descricao = ? WHERE codigo_grupo = ?",
                [descricao, codigo_grupo],
            )
        else:
            cur.execute(
                "INSERT INTO USER_geoapolo_grupo (codigo_grupo, descricao) VALUES (?, ?)",
                [codigo_grupo, descricao],
            )
        self.conn.commit()
        return True

    def excluir_grupo(self, codigo_grupo: str) -> bool:
        """Remove grupo e todos os seus vínculos de objetos e usuários."""
        cur = self.conn.cursor()
        cur.execute("DELETE FROM USER_geoapolo_grupobjetos WHERE codigo_grupo = ?", [codigo_grupo])
        cur.execute("DELETE FROM USER_geoapolo_grupousuario WHERE codigo_grupo = ?", [codigo_grupo])
        cur.execute("DELETE FROM USER_geoapolo_grupo WHERE codigo_grupo = ?", [codigo_grupo])
        self.conn.commit()
        return True

    def listar_usuarios_grupo(self, codigo_grupo: str) -> List[VinculoGrupoUsuarioDTO]:
        """Lista usuários pertencentes a um grupo de segurança."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT gu.codigo_grupo, g.descricao, u.usucod, u.login, u.nome_completo
            FROM USER_geoapolo_grupousuario gu {nolock}
            INNER JOIN USER_geoapolo_grupo g {nolock} ON gu.codigo_grupo = g.codigo_grupo
            INNER JOIN USER_geoapolo_usuarios u {nolock} ON gu.usucod = u.usucod
            WHERE gu.codigo_grupo = ?
            ORDER BY u.nome_completo ASC
        """
        cur.execute(sql, [codigo_grupo])
        return [
            VinculoGrupoUsuarioDTO(
                codigo_grupo=str(r[0]),
                nome_grupo=str(r[1]),
                usucod=str(r[2]),
                login=str(r[3]),
                nome_completo=str(r[4]),
            )
            for r in cur.fetchall()
        ]

    def vincular_usuario_grupo(self, codigo_grupo: str, usucod: str) -> bool:
        """Insere usuário no grupo de segurança."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT 1 FROM USER_geoapolo_grupousuario WHERE codigo_grupo = ? AND usucod = ?",
            [codigo_grupo, usucod],
        )
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO USER_geoapolo_grupousuario (codigo_grupo, usucod) VALUES (?, ?)",
                [codigo_grupo, usucod],
            )
            self.conn.commit()
        return True

    def desvincular_usuario_grupo(self, codigo_grupo: str, usucod: str) -> bool:
        """Remove usuário do grupo."""
        cur = self.conn.cursor()
        cur.execute(
            "DELETE FROM USER_geoapolo_grupousuario WHERE codigo_grupo = ? AND usucod = ?",
            [codigo_grupo, usucod],
        )
        self.conn.commit()
        return True

    def listar_objetos_perfil(self, codigo_grupo: str, categoria: str = "") -> List[PerfilAcessoItemDTO]:
        """Lista status de acesso a telas e recursos para um grupo."""
        self.sincronizar_ou_inicializar_objetos(apenas_se_vazia=True)
        cur = self.conn.cursor()
        nolock = self._nolock()

        colunas = self._obter_colunas("USER_geoapolo_objetos")
        if "categoria" in colunas:
            col_categoria = "COALESCE(o.categoria, 'Geral')"
            where_cat = " AND UPPER(COALESCE(o.categoria, 'Geral')) = UPPER(?)" if categoria.strip() else ""
            order_by = "o.categoria, "
        else:
            col_categoria = "'Geral'"
            where_cat = ""
            order_by = ""

        if "nome_amigavel" in colunas and "nome_oficial" in colunas:
            col_amigavel = "COALESCE(o.nome_amigavel, o.nome_oficial, o.nome_objeto)"
        elif "nome_amigavel" in colunas:
            col_amigavel = "COALESCE(o.nome_amigavel, o.nome_objeto)"
        elif "nome_oficial" in colunas:
            col_amigavel = "COALESCE(o.nome_oficial, o.nome_objeto)"
        else:
            col_amigavel = "o.nome_objeto"

        sql = f"""
            SELECT o.codigo_objeto, o.nome_objeto, {col_amigavel} AS nome_amigavel,
                   {col_categoria} AS categoria, COALESCE(go.statusacesso, 'N') AS statusacesso
            FROM USER_geoapolo_objetos o {nolock}
            LEFT JOIN USER_geoapolo_grupobjetos go {nolock}
              ON o.codigo_objeto = go.codigo_objeto AND go.codigo_grupo = ?
            WHERE 1=1 {where_cat}
            ORDER BY {order_by} {col_amigavel}
        """
        params = [codigo_grupo]
        if where_cat:
            params.append(categoria.strip())

        cur.execute(sql, params)
        return [
            PerfilAcessoItemDTO(
                codigo_objeto=str(r[0]),
                nome_objeto=str(r[1]),
                nome_amigavel=str(r[2]),
                categoria=str(r[3]),
                codigo_grupo=codigo_grupo,
                statusacesso=str(r[4]),
            )
            for r in cur.fetchall()
        ]

    def listar_categorias_objetos(self) -> List[str]:
        """Lista categorias distintas de objetos/menus."""
        self.sincronizar_ou_inicializar_objetos(apenas_se_vazia=True)
        cur = self.conn.cursor()
        nolock = self._nolock()
        colunas = self._obter_colunas("USER_geoapolo_objetos")

        if "categoria" not in colunas:
            return ["Geral"]

        sql = f"SELECT DISTINCT categoria FROM USER_geoapolo_objetos {nolock} WHERE categoria IS NOT NULL AND RTRIM(LTRIM(categoria)) <> '' ORDER BY categoria"
        cur.execute(sql)
        cats = [str(r[0]).strip() for r in cur.fetchall() if r[0]]
        return cats or ["Geral"]

    def atualizar_status_acesso(self, codigo_grupo: str, codigo_objeto: str, statusacesso: str) -> bool:
        """Atualiza a permissão de acesso (A = Liberado, N = Bloqueado)."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT 1 FROM USER_geoapolo_grupobjetos WHERE codigo_grupo = ? AND codigo_objeto = ?",
            [codigo_grupo, codigo_objeto],
        )
        if cur.fetchone():
            cur.execute(
                "UPDATE USER_geoapolo_grupobjetos SET statusacesso = ? WHERE codigo_grupo = ? AND codigo_objeto = ?",
                [statusacesso, codigo_grupo, codigo_objeto],
            )
        else:
            cur.execute(
                "INSERT INTO USER_geoapolo_grupobjetos (codigo_grupo, codigo_objeto, statusacesso) VALUES (?, ?, ?)",
                [codigo_grupo, codigo_objeto, statusacesso],
            )
        self.conn.commit()
        return True
