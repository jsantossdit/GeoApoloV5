"""
Módulo de Criptografia e Descriptografia compatível com o padrão Delphi (funcoes.pas / unt_criptografia_adapter.pas).
GeoApolo V5 / GeoAlvo
Clean Architecture: Suporta decodificação de senhas salvas no banco pelo sistema Delphi legado.
"""

from typing import List


def preenche_vetor() -> List[str]:
    """
    Recria o vetor de substituição exatamente como na unit funcoes.pas do Delphi:
    - k=65 (26): A-Z
    - k=97 (26): a-z
    - k=48 (10): 0-9
    - k=32 (16): pontuação inicial (espaço até /)
    - k=58 (7): pontuação intermediária (: até @)
    - k=91 (5): pontuação colchetes ([ até _)
    - k=123 (3): chaves e barra ({ até })
    Total: 93 elementos (índices 1 a 92 usados no laço Delphi)
    """
    alpha = [""] * 94
    k = 65
    for i in range(1, 27):
        alpha[i] = chr(k)
        k += 1
    k = 97
    for i in range(27, 53):
        alpha[i] = chr(k)
        k += 1
    k = 48
    for i in range(53, 63):
        alpha[i] = chr(k)
        k += 1
    k = 32
    for i in range(63, 79):
        alpha[i] = chr(k)
        k += 1
    k = 58
    for i in range(79, 86):
        alpha[i] = chr(k)
        k += 1
    k = 91
    for i in range(86, 91):
        alpha[i] = chr(k)
        k += 1
    k = 123
    for i in range(91, 94):
        alpha[i] = chr(k)
        k += 1
    return alpha


def criptografia(chave: int, recebetexto: str) -> str:
    """
    Criptografa o texto conforme rotina Delphi 'criptografia(chave, recebetexto)'.
    Chave padrão para senhas de usuários: 32.
    """
    if not recebetexto:
        return ""
    alpha = preenche_vetor()
    resultado = []
    for char in recebetexto:
        trocou = False
        for j in range(1, 93):
            if alpha[j] == char:
                ida = j + chave
                if ida <= 92:
                    resultado.append(alpha[ida])
                else:
                    ida = ida - 92
                    resultado.append(alpha[ida])
                trocou = True
                break
        if not trocou:
            resultado.append(char)
    return "".join(resultado)


def decriptografia(chave: int, senhacripto: str, senhaoriginal: str = "") -> str:
    """
    Descriptografa o texto cifrado conforme rotina Delphi 'decriptografia(chave, senhacripto, senhaoriginal)'.
    Chave padrão para senhas de usuários: 32.
    """
    if not senhacripto:
        return ""
    alpha = preenche_vetor()
    resultado = []
    for char in senhacripto:
        trocou = False
        for j in range(1, 93):
            if alpha[j] == char:
                y = j - chave
                if y <= 0:
                    y = y + 92
                    resultado.append(alpha[y])
                else:
                    resultado.append(alpha[y])
                trocou = True
                break
        if not trocou:
            resultado.append(char)
    return "".join(resultado)
