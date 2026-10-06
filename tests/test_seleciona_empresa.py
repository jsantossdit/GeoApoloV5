import unittest
import tkinter as tk
from unittest.mock import MagicMock, patch

from seleciona_empresa import TelaSelecaoEmpresa


class TestTelaSelecaoEmpresa(unittest.TestCase):
    """Testes de regressão para TelaSelecaoEmpresa garantindo ausência de erros Tcl/Tk."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    @patch("entidades.database.obter_conexao_banco")
    def test_estrutura_widgets_hierarquia(self, mock_conn):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("1.01", "EMPRESA PADRAO RCC")]
        mock_conn.return_value.cursor.return_value = mock_cursor

        tela = TelaSelecaoEmpresa(parent=self.root)
        self.assertEqual(tela.tree_empresas._w, ".!toplevel.!frame2.!frame.!treeview")
        tela.cancelar()

    @patch("entidades.database.obter_conexao_banco")
    def test_tecla_return_nao_gera_bgerror_togglefocus(self, mock_conn):
        """Valida que teclar Return com foco no Treeview confirma sem disparar bgerror de ToggleFocus."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("1.01", "EMPRESA PADRAO RCC")]
        mock_conn.return_value.cursor.return_value = mock_cursor

        on_confirmar = MagicMock()
        tela = TelaSelecaoEmpresa(parent=self.root, on_confirmar=on_confirmar)

        # Configura captura de bgerror no Tcl
        self.root.tk.eval("""
            catch {unset ::captured_bgerror}
            proc bgerror {msg} {
                set ::captured_bgerror $msg
            }
        """)

        # Dispara o evento <Key-Return> no tree_empresas
        self.root.tk.eval(f"event generate {tela.tree_empresas._w} <Key-Return>")
        self.root.update()

        has_bgerror = self.root.tk.eval("info exists ::captured_bgerror") == "1"
        if has_bgerror:
            erro = self.root.tk.eval("set ::captured_bgerror")
            self.fail(f"Erro Tcl disparado indevidamente no evento Return: {erro}")

        on_confirmar.assert_called_once_with("1.01", "EMPRESA PADRAO RCC")

    @patch("entidades.database.obter_conexao_banco")
    def test_duplo_clique_nao_gera_erro(self, mock_conn):
        """Valida que duplo clique confirma a seleção sem erros."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("1.01", "EMPRESA PADRAO RCC")]
        mock_conn.return_value.cursor.return_value = mock_cursor

        on_confirmar = MagicMock()
        tela = TelaSelecaoEmpresa(parent=self.root, on_confirmar=on_confirmar)

        res = tela._on_tree_double_click()
        self.assertEqual(res, "break")
        on_confirmar.assert_called_once_with("1.01", "EMPRESA PADRAO RCC")

    @patch("entidades.database.obter_conexao_banco")
    def test_cancelamento_via_escape(self, mock_conn):
        """Valida que cancelamento via Escape ou F10 fecha a janela e retorna break."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("1.01", "EMPRESA PADRAO RCC")]
        mock_conn.return_value.cursor.return_value = mock_cursor

        on_cancelar = MagicMock()
        tela = TelaSelecaoEmpresa(parent=self.root, on_cancelar=on_cancelar)

        res = tela._ao_cancelar_evento()
        self.assertEqual(res, "break")
        on_cancelar.assert_called_once()

    def test_janela_pesquisa_parametro_return_sem_bgerror(self):
        """Valida que JanelaPesquisaParametro no evento Return fecha e retorna break sem bgerror."""
        from configuracoes.view import JanelaPesquisaParametro

        on_callback = MagicMock()
        buscar_mock = MagicMock(return_value=[{"codigo": "01", "descricao": "TESTE"}])

        dlg = JanelaPesquisaParametro(
            parent=self.root,
            titulo="Pesquisa Teste",
            col_codigo_nome="Cód",
            col_descr_nome="Descrição",
            buscar_func=buscar_mock,
            callback_selecao=on_callback,
        )
        try:
            dlg.grab_release()
        except Exception:
            pass
        dlg._filtrar()

        # Valida que o método _confirmar_selecao retorna break para cessar a propagação
        res = dlg._confirmar_selecao()
        self.assertEqual(res, "break")
        on_callback.assert_called_once_with("01", "TESTE")


if __name__ == "__main__":
    unittest.main()
