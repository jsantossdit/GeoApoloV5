"""
Pacote de Serviços Centrais (Core) do GeoAlvo.
Validações de documentos, serviços de integração de CEP e e-mail.
"""

from core.validators import (
    validar_cpf,
    validar_cnpj,
    validar_email,
    validar_cep,
    limpar_formatacao,
    formatar_cpf,
    formatar_cnpj,
    formatar_cep,
)
from core.viacep import consultar_cep
from core.email_service import EmailService
from core.recursos import (
    obter_caminho_recurso,
    centralizar_janela,
    geoapolo_configcod,
    aplicar_icone_janela,
    configurar_navegacao_enter,
    vincular_maiusculo,
    habilitar_filtro_dinamico_combobox,
)
from core.criptografia import criptografia, decriptografia
from core.error_logger import salvar_log_erro_executavel, obter_diretorio_executavel
from core.date_utils import (
    aplicar_mascara_data,
    vincular_mascara_data,
    parse_data_flexivel,
    formatar_data_br,
    converter_data_br_para_iso,
    validar_data_br,
)
from core.permission_manager import (
    GestorPermissoes,
    aplicar_permissoes_toolbar,
)
from core.schema_checker import (
    verificar_sanidade_estoque_produtos,
    exibir_dialogo_sanidade_schema,
    aplicar_correcao_tabelas_faltantes,
)
from core.sessao import (
    obter_empresa_ativa,
    obter_nome_empresa_ativa,
    definir_empresa_ativa,
)


__all__ = [
    "validar_cpf",
    "validar_cnpj",
    "validar_email",
    "validar_cep",
    "limpar_formatacao",
    "formatar_cpf",
    "formatar_cnpj",
    "formatar_cep",
    "consultar_cep",
    "EmailService",
    "obter_caminho_recurso",
    "centralizar_janela",
    "geoapolo_configcod",
    "aplicar_icone_janela",
    "criptografia",
    "decriptografia",
    "salvar_log_erro_executavel",
    "obter_diretorio_executavel",
    "aplicar_mascara_data",
    "vincular_mascara_data",
    "parse_data_flexivel",
    "formatar_data_br",
    "converter_data_br_para_iso",
    "validar_data_br",
    "habilitar_filtro_dinamico_combobox",
    "GestorPermissoes",
    "aplicar_permissoes_toolbar",
    "verificar_sanidade_estoque_produtos",
    "exibir_dialogo_sanidade_schema",
    "aplicar_correcao_tabelas_faltantes",
    "obter_empresa_ativa",
    "obter_nome_empresa_ativa",
    "definir_empresa_ativa",
]

