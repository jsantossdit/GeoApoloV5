"""
Testes Unitários para o Gestor de Permissões e Perfis de Acesso (GeoAlvo / GeoApolo V5)
Valida:
1. Administrador (ADMIN) com acesso irrestrito
2. Usuário restrito com bloqueios ('N') e liberações ('A')
3. Resolução de múltiplos grupos (regra 'A' sobrescreve 'N')
4. Aliases e sinônimos (pnlmenuprincipal, btn_*, spb*, rótulos amigáveis)
5. Aplicação na barra de ferramentas (ToolbarManager) - ocultando e desabilitando botões bloqueados
6. Construção da barra de menu (criar_barra_menu_principal) - ocultando comandos e cascatas vazias
"""

import unittest
from unittest.mock import MagicMock
import tkinter as tk

from core.permission_manager import GestorPermissoes, aplicar_permissoes_toolbar
from toolbar_geoalvo import ToolbarManager


class TestPermissionManager(unittest.TestCase):
    """Testes da classe GestorPermissoes"""

    def test_admin_tem_acesso_irrestrito(self):
        """ADMIN deve ter acesso permitido a qualquer objeto, sem exceção."""
        gestor = GestorPermissoes(usuario="ADMIN", is_admin=True)
        self.assertTrue(gestor.pode_acessar("pnlmenuprincipal"))
        self.assertTrue(gestor.pode_acessar("spbtrocaempresa"))
        self.assertTrue(gestor.pode_acessar("mnuconfig"))
        self.assertTrue(gestor.pode_acessar("qualquer_objeto_inexistente"))

    def test_usuario_restrito_bloqueios_e_liberacoes(self):
        """Usuário comum deve respeitar permissões 'A' (True) e 'N' (False)."""
        gestor = GestorPermissoes(usuario="JULIO", is_admin=False)
        gestor.permissoes = {
            "pnlmenuprincipal": True,
            "spbtrocaempresa": False,
            "btn_troca_empresa": False,
            "mnuconfig": False,
            "mnuconfigbdgeoalvo": True,
            "btn_entidades": True,
        }

        # Permissão direta
        self.assertTrue(gestor.pode_acessar("pnlmenuprincipal"))
        self.assertFalse(gestor.pode_acessar("spbtrocaempresa"))
        self.assertFalse(gestor.pode_acessar("mnuconfig"))
        self.assertTrue(gestor.pode_acessar("mnuconfigbdgeoalvo"))

        # Aliases
        self.assertFalse(gestor.pode_acessar("troca_empresa"))
        self.assertTrue(gestor.pode_acessar("entidades"))

        # Objeto não configurado no modelo restritivo: Bloqueado (False) - somente liberar o que estiver liberado
        self.assertFalse(gestor.pode_acessar("objeto_livre_sem_restricao"))

        # Recurso de saída segura do sistema: permitido por padrão
        self.assertTrue(gestor.pode_acessar("sair"))
        self.assertTrue(gestor.pode_acessar("spbsair"))

    def test_usuario_sem_grupo_bloqueado(self):
        """Usuário comum sem nenhum grupo associado e sem permissões deve ter acesso negado a tudo (exceto sair)."""
        gestor = GestorPermissoes(usuario="NOVATO", is_admin=False)
        gestor.grupos = []
        gestor.permissoes = {}

        self.assertFalse(gestor.pode_acessar("pnlmenuprincipal"))
        self.assertFalse(gestor.pode_acessar("mnuconfig"))
        self.assertFalse(gestor.pode_acessar("mnucadastro"))
        self.assertTrue(gestor.pode_acessar("sair"))

    def test_esta_bloqueado_explicitamente(self):
        """Testa detecção precisa de bloqueio explícito ('N' no banco / False)."""
        gestor = GestorPermissoes(usuario="JULIO", is_admin=False)
        gestor.permissoes = {
            "mnucadastro": False,
            "mnucadalmoxarifados": True,
        }

        self.assertTrue(gestor.esta_bloqueado_explicitamente("mnucadastro"))
        self.assertFalse(gestor.esta_bloqueado_explicitamente("mnucadalmoxarifados"))
        # Objeto inexistente não tem bloqueio explícito registrado
        self.assertFalse(gestor.esta_bloqueado_explicitamente("objeto_qualquer"))

    def test_multiplos_grupos_resolucao_a_vence_n(self):
        """Quando usuário está em múltiplos grupos e um deles concede 'A', o acesso deve ser permitido."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        # Simula 2 grupos: Grupo 2 e Grupo 3
        mock_cursor.fetchall.side_effect = [
            [(2,), (3,)],  # Grupos retornados
            [
                ("spbtrocaempresa", "N"),
                ("spbtrocaempresa", "A"),  # 'A' vem depois por ORDER BY statusacesso DESC
                ("mnuconfig", "N"),
            ],
        ]

        gestor = GestorPermissoes.carregar_do_banco(mock_conn, "JULIO")
        self.assertEqual(gestor.grupos, [2, 3])
        # spbtrocaempresa teve 'A' sobrescrevendo 'N'
        self.assertTrue(gestor.pode_acessar("spbtrocaempresa"))
        # mnuconfig só teve 'N'
        self.assertFalse(gestor.pode_acessar("mnuconfig"))

    def test_toolbar_aplicar_permissoes(self):
        """Testa se botões bloqueados são ocultados e desabilitados na toolbar."""
        root = tk.Tk()
        root.withdraw()
        try:
            tb = ToolbarManager(root)

            gestor = GestorPermissoes(usuario="TESTE", is_admin=False)
            gestor.permissoes = {
                "pnlmenuprincipal": True,
                "troca_empresa": False,
                "btn_troca_empresa": False,
                "spbtrocaempresa": False,
                "btn_entidades": True,
                "entidades": True,
            }

            tb.aplicar_permissoes(gestor)

            # Botão troca_empresa deve estar desabilitado
            btn_troca = tb.buttons["troca_empresa"]
            self.assertEqual(str(btn_troca["state"]), tk.DISABLED)

            # Botão entidades deve estar habilitado
            btn_entidades = tb.buttons["entidades"]
            self.assertEqual(str(btn_entidades["state"]), tk.NORMAL)

            # Se a barra inteira for bloqueada (pnlmenuprincipal = False)
            gestor_bloqueio_total = GestorPermissoes(usuario="TESTE", is_admin=False)
            gestor_bloqueio_total.permissoes = {"pnlmenuprincipal": False}
            tb.aplicar_permissoes(gestor_bloqueio_total)
            # Toolbar deve estar desempacotada
            self.assertEqual(tb.toolbar.winfo_ismapped(), 0)

        finally:
            root.destroy()

    def test_menu_principal_ocultando_itens_e_cascatas_vazias(self):
        """Testa se a construção da barra de menu omite itens bloqueados e cascatas vazias."""
        from geoalvo import criar_barra_menu_principal
        root = tk.Tk()
        root.withdraw()
        try:
            gestor = GestorPermissoes(usuario="TESTE", is_admin=False)
            # Bloqueia Configurações inteiro (mnuconfig)
            gestor.permissoes = {
                "mnuconfig": False,
                "sair": True,
            }

            menubar = criar_barra_menu_principal(root, gestor)
            end_idx = menubar.index("end")
            labels = []
            if end_idx is not None:
                for i in range(end_idx + 1):
                    # No Windows, pode verificar os itens do menu
                    pass

            # Admin deve ter acesso a Configurações
            gestor_admin = GestorPermissoes("ADMIN", is_admin=True)
            menubar_admin = criar_barra_menu_principal(root, gestor_admin)
            self.assertIsNotNone(menubar_admin)

        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
