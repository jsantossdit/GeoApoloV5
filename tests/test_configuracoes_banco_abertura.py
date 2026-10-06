"""
Testes automatizados para abertura do formulário de configuração do banco de dados (GeoAlvo & SAVIC).
Valida que não ocorrem erros de ciclo mestre/transiente (_tkinter.TclError) ou duplicação de instâncias tk.Tk.
"""

import unittest
import tkinter as tk
from config_banco import DatabaseConfigForm, ConfigManager
from toolbar_geoalvo import ToolbarManager
from geoalvo import abrir_config_banco, abrir_config_banco_aba


class TestConfiguracaoBancoAbertura(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Cria a janela raiz padrão da aplicação para simular o ambiente ativo
        cls.root = tk.Tk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass

    def test_database_config_form_com_parent_explicito(self):
        """Valida que instanciar passando parent cria um Toplevel filho do root."""
        form = DatabaseConfigForm(parent=self.root, initial_tab="MSSQL")
        self.assertIsInstance(form.root, tk.Toplevel)
        self.assertEqual(form.parent, self.root)
        form.fechar()

    def test_database_config_form_sem_parent_usa_default_root(self):
        """Valida que instanciar sem parent quando _default_root já existe não cria segundo Tk."""
        form = DatabaseConfigForm(parent=None, initial_tab="MSSQL")
        self.assertIsInstance(form.root, tk.Toplevel)
        self.assertEqual(form.parent, self.root)
        form.fechar()

    def test_database_config_form_selecao_aba_savic(self):
        """Valida que passar initial_tab='MYSQL' seleciona a aba do SAVIC."""
        form = DatabaseConfigForm(parent=self.root, initial_tab="MYSQL")
        self.assertEqual(form.notebook.select(), str(form.tab_savic))
        form.fechar()

    def test_database_config_form_selecao_aba_geoalvo(self):
        """Valida que passar initial_tab='MSSQL' seleciona a aba do GeoAlvo."""
        form = DatabaseConfigForm(parent=self.root, initial_tab="MSSQL")
        self.assertEqual(form.notebook.select(), str(form.tab_geoalvo))
        form.fechar()

    def test_database_config_form_selecao_aba_aplicativo_rcc(self):
        """Valida que passar initial_tab='APLICATIVO' seleciona a aba do Aplicativo RCC."""
        form = DatabaseConfigForm(parent=self.root, initial_tab="APLICATIVO")
        self.assertEqual(form.notebook.select(), str(form.tab_app_rcc))
        form.fechar()

    def test_config_manager_aplicativo_rcc_settings_e_credentials(self):
        """Valida salvamento e leitura dos parâmetros do Aplicativo RCC."""
        cm = ConfigManager(app_name="test_app_rcc_geov5")
        cm.save_app_rcc_settings({"host": "10.0.0.99", "port": "3307", "database": "app_rcc_teste"})
        cm.save_app_rcc_credentials("usuario_teste", "senha_teste")

        loaded = cm.load_app_rcc_settings()
        self.assertEqual(loaded["host"], "10.0.0.99")
        self.assertEqual(loaded["port"], "3307")
        self.assertEqual(loaded["database"], "app_rcc_teste")

        creds = cm.get_app_rcc_credentials()
        self.assertEqual(creds["user"], "usuario_teste")
        self.assertEqual(creds["password"], "senha_teste")

    def test_toolbar_novos_botoes_requisicao_e_posicao_imprimir(self):
        """Valida que o botão dashboard e config foram removidos e nova requisição / imprimir estão corretos."""
        tb = ToolbarManager(self.root)
        self.assertNotIn("dashboard", tb.buttons)
        self.assertNotIn("config", tb.buttons)
        self.assertIn("nova_requisicao", tb.buttons)
        self.assertIn("imprimir", tb.buttons)
        self.assertIn("consultas_imediatas", tb.buttons)

        # Checa a ordem na configuração: imprimir deve vir imediatamente antes de consultas_imediatas
        nomes = [item.get("name") for item in tb.toolbar_config if item.get("name")]
        idx_imprimir = nomes.index("imprimir")
        idx_consultas = nomes.index("consultas_imediatas")
        self.assertEqual(idx_consultas, idx_imprimir + 1)

    def test_timeout_campo_carregado_e_alteracao(self):
        """Valida que o formulário de banco carrega o timeout atual e permite alteração."""
        form = DatabaseConfigForm(parent=self.root, initial_tab="MSSQL")
        # Garante que o campo de timeout foi inicializado e possui valor numérico
        val_inicial = form.geo_timeout_var.get()
        self.assertTrue(val_inicial.isdigit())
        self.assertGreaterEqual(int(val_inicial), 1)

        # Simula alteração do usuário
        form.geo_timeout_var.set("90")
        self.assertEqual(form.geo_timeout_var.get(), "90")
        form.fechar()

    def test_is_base_local_deteccao(self):
        """Valida a detecção de instâncias locais para aplicação de timeout expandido."""
        from entidades.database import is_base_local
        self.assertTrue(is_base_local("localhost"))
        self.assertTrue(is_base_local("127.0.0.1"))
        self.assertTrue(is_base_local("."))
        self.assertTrue(is_base_local("(local)"))
        self.assertTrue(is_base_local(r"localhost\SQLEXPRESS"))
        self.assertTrue(is_base_local(r".\SQLEXPRESS"))
        self.assertTrue(is_base_local("127.0.0.1,1433"))
        self.assertTrue(is_base_local(""))

        self.assertFalse(is_base_local("192.168.0.50"))
        self.assertFalse(is_base_local("servidor-remoto.empresa.local"))
        self.assertFalse(is_base_local("10.0.0.1"))

    def test_config_manager_salvar_e_carregar_timeout(self):
        """Valida a persistência e recuperação do timeout no ConfigManager."""
        cm = ConfigManager(app_name="test_timeout_geoalvo")
        cm.save_settings({
            "db_type": "SQL Server",
            "endereco": "localhost",
            "porta": "1433",
            "banco": "RCC_TEST",
            "timeout": 75
        })
        loaded = cm.load_settings()
        self.assertEqual(loaded.get("timeout"), 75)


if __name__ == "__main__":
    unittest.main()

