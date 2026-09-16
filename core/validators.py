"""
Validadores e Formatadores de Documentos e Dados (CPF, CNPJ, E-mail, CEP, Telefone).
Desacoplados de qualquer framework de tela ou banco de dados.
"""

import re
from typing import Optional


def limpar_formatacao(texto: Optional[str]) -> str:
    """Remove caracteres não numéricos de uma string."""
    if not texto:
        return ""
    return re.sub(r"\D", "", str(texto))


def validar_cpf(cpf: Optional[str]) -> bool:
    """Valida número de CPF de acordo com as regras da Receita Federal (algoritmo mod 11)."""
    digitos = limpar_formatacao(cpf)
    if len(digitos) != 11:
        return False

    # Rejeita CPFs com todos os dígitos iguais (ex: 111.111.111-11)
    if len(set(digitos)) == 1:
        return False

    # Primeiro dígito verificador
    soma = sum(int(digitos[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    dig1 = 0 if resto == 10 else resto
    if int(digitos[9]) != dig1:
        return False

    # Segundo dígito verificador
    soma = sum(int(digitos[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    dig2 = 0 if resto == 10 else resto
    return int(digitos[10]) == dig2


def validar_cnpj(cnpj: Optional[str]) -> bool:
    """Valida número de CNPJ de acordo com as regras da Receita Federal (pesos 5,4,3,2...)."""
    digitos = limpar_formatacao(cnpj)
    if len(digitos) != 14:
        return False

    # Rejeita CNPJs com todos os dígitos iguais
    if len(set(digitos)) == 1:
        return False

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(digitos[i]) * pesos1[i] for i in range(12))
    resto = soma % 11
    dig1 = 0 if resto < 2 else (11 - resto)
    if int(digitos[12]) != dig1:
        return False

    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(digitos[i]) * pesos2[i] for i in range(13))
    resto = soma % 11
    dig2 = 0 if resto < 2 else (11 - resto)
    return int(digitos[13]) == dig2


def validar_email(email: Optional[str]) -> bool:
    """Valida endereço de e-mail através de expressão regular RFC-compatível."""
    if not email or not str(email).strip():
        return False
    padrao = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(padrao, str(email).strip()))


def validar_cep(cep: Optional[str]) -> bool:
    """Verifica se o CEP possui exatamente 8 dígitos numéricos."""
    digitos = limpar_formatacao(cep)
    return len(digitos) == 8


def formatar_cpf(cpf: Optional[str]) -> str:
    """Formata string de 11 dígitos para o padrão 000.000.000-00."""
    d = limpar_formatacao(cpf)
    if len(d) == 11:
        return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"
    return str(cpf or "")


def formatar_cnpj(cnpj: Optional[str]) -> str:
    """Formata string de 14 dígitos para o padrão 00.000.000/0000-00."""
    d = limpar_formatacao(cnpj)
    if len(d) == 14:
        return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"
    return str(cnpj or "")


def formatar_cep(cep: Optional[str]) -> str:
    """Formata string de 8 dígitos para o padrão 00000-000."""
    d = limpar_formatacao(cep)
    if len(d) == 8:
        return f"{d[:5]}-{d[5:]}"
    return str(cep or "")
