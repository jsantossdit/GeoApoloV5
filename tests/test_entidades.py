"""
Testes Unitários para o Módulo de Gestão de Entidades, FrmCadEntidade e Troca de Empresa.
GeoApolo V5
"""

import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from tkinter import ttk

from entidades.cadentidade_view import FrmCadEntidade
from entidades.view import EntidadesView
from entidades.models import ItemComparacao, DecisaoLinha
from geoalvo import definir_empresa_ativa


class TestTrocaEmpresaContexto(unittest.TestCase):
    """Testes para atualização de empresa ativa e contexto corporativo."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.empresa_ativa = "1.01"
        self.root.nome_empresa_ativa = "Matriz Inicial"

    def tearDown(self):
        try:
            from logon import sessao_usuario_atual
            sessao_usuario_atual.pop("codigo_empresa", None)
            sessao_usuario_atual.pop("empcod", None)
            sessao_usuario_atual.pop("nome_empresa", None)
        except Exception:
            pass
        self.root.destroy()

    def test_definir_empresa_ativa_atualiza_titulo_e_atributos(self):
        definir_empresa_ativa(self.root, "02", "Filial São Paulo")
        self.assertEqual(self.root.empresa_ativa, "02")
        self.assertEqual(self.root.nome_empresa_ativa, "Filial São Paulo")
        self.assertIn("02", self.root.title())
        self.assertIn("Filial São Paulo", self.root.title())

    def test_definir_empresa_ativa_atualiza_sessao_logon(self):
        from logon import sessao_usuario_atual
        definir_empresa_ativa(self.root, "03", "Filial Rio de Janeiro")
        self.assertEqual(sessao_usuario_atual.get("codigo_empresa"), "03")
        self.assertEqual(sessao_usuario_atual.get("nome_empresa"), "Filial Rio de Janeiro")


class TestFrmCadEntidade(unittest.TestCase):
    """Testes para o formulário FrmCadEntidade (unt_cadentidades)."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.registro_exemplo = {
            "geoentcod": "GEO100",
            "entcod": "ALV100",
            "geoentnome": "João da Silva",
            "entnome": "João da Silva",
            "geoentnomefantasia": "Silva Artes",
            "entcpfcgc": "12345678901",
            "EntCpfCgc": "12345678901",
            "entrgie": "MG123456",
            "geoentender": "Rua das Flores",
            "geoenderno": "123",
            "geoentendercomp": "Apto 101",
            "geoentbair": "Centro",
            "geoentcep": "37130000",
            "cidnomecomp": "Alfenas",
            "ufsigla": "MG",
            "enttipofj": "F",
            "USERFalecido": "Não",
            "entgenero": "MASCULINO",
            "entestcivil": "CASADO(A)",
            "entnomepai": "José da Silva",
            "entnomemae": "Maria da Silva",
            "USERValor_Contribuicao": "50.00",
            "USERGeraCarne": "Sim",
            "Entobservacoes": "Doador fiel de Alfenas",
        }

    def tearDown(self):
        self.root.destroy()

    def test_instanciacao_e_preenchimento_dados(self):
        form = FrmCadEntidade(self.root, registro=self.registro_exemplo, base_dados="GeoApolo")
        self.assertEqual(form.txt_geoentcod.get(), "GEO100")
        self.assertEqual(form.txt_entcod.get(), "ALV100")
        self.assertEqual(form.txt_nome.get(), "João da Silva")
        self.assertEqual(form.txt_cpf_cnpj.get(), "12345678901")
        self.assertEqual(form.txt_ender.get(), "Rua das Flores")
        self.assertEqual(form.txt_enderno.get(), "123")
        self.assertEqual(form.txt_cidade.get(), "Alfenas")
        self.assertEqual(form.txt_uf.get(), "MG")
        self.assertEqual(form.cbo_tipofj.get(), "F")
        self.assertEqual(form.cbo_falecido.get(), "Não")
        self.assertEqual(form.txt_nomepai.get(), "José da Silva")
        self.assertEqual(form.cbo_geracarne.get(), "Sim")
        self.assertIn("Doador fiel", form.txt_observacoes.get("1.0", tk.END))
        form.destroy()

    def test_coletar_dados_alterados(self):
        form = FrmCadEntidade(self.root, registro=self.registro_exemplo, base_dados="GeoApolo")
        form.txt_nome.delete(0, tk.END)
        form.txt_nome.insert(0, "João da Silva Alterado")
        form.txt_ender.delete(0, tk.END)
        form.txt_ender.insert(0, "Avenida Nova")

        dados = form._coletar_dados()
        self.assertEqual(dados["geoentnome"], "JOÃO DA SILVA ALTERADO")
        self.assertEqual(dados["geoentender"], "AVENIDA NOVA")
        form.destroy()

    def test_salvar_callback_executado(self):
        callback_mock = MagicMock()
        form = FrmCadEntidade(
            self.root,
            registro=self.registro_exemplo,
            base_dados="GeoApolo",
            on_salvar=callback_mock
        )
        with patch.object(form._service, "salvar_entidade") as mock_save:
            from entidades.models import ResultadoOperacao
            mock_save.return_value = ResultadoOperacao(sucesso=True, mensagem="OK")
            with patch("tkinter.messagebox.showinfo"):
                form.salvar()
                callback_mock.assert_called_once()

    def test_presenca_abas_categorias_contatos_documentos(self):
        """Valida que as 7 abas principais e o sub-notebook complementar estão presentes no Notebook."""
        form = FrmCadEntidade(self.root, registro=self.registro_exemplo, base_dados="GeoApolo")
        abas = [form.notebook.tab(i, "text").strip() for i in range(form.notebook.index("end"))]
        self.assertIn("Identificação / Principal", abas)
        self.assertIn("Complementar", abas)
        self.assertIn("Categorias", abas)
        self.assertIn("Contatos & Comunicação", abas)
        self.assertIn("Histórico Entidade", abas)
        self.assertIn("Documentos", abas)
        self.assertIn("Observações", abas)
        self.assertEqual(len(abas), 7)

        subabas = [form.sub_notebook.tab(i, "text").strip() for i in range(form.sub_notebook.index("end"))]
        self.assertIn("Dados Pessoais", subabas)
        self.assertIn("Financeiro", subabas)
        self.assertIn("Informações Complementares", subabas)
        form.destroy()

    def test_gerenciamento_categorias(self):
        """Testa inclusão, remoção e coleta de categorias na aba Categorias."""
        form = FrmCadEntidade(self.root, registro=self.registro_exemplo, base_dados="GeoApolo")
        with patch.object(form._service, "adicionar_categoria", return_value=True) as mock_add, \
             patch.object(form._service, "remover_categoria", return_value=True) as mock_rem:

            form.txt_categ_cod.insert(0, "02.001")
            form.txt_categ_nome.insert(0, "Doador Mensal")
            form._adicionar_categoria()
            mock_add.assert_called_once_with("GEO100", "02.001", base_dados="GeoApolo")

            itens = form.tree_categorias.get_children()
            self.assertTrue(len(itens) >= 1)
            vals = form.tree_categorias.item(itens[-1], "values")
            self.assertEqual(vals[0], "02.001")
            self.assertEqual(vals[1], "Doador Mensal")

            dados = form._coletar_dados()
            self.assertTrue(any(c["codigo"] == "02.001" for c in dados["categorias"]))

            # Remove categoria
            form.tree_categorias.selection_set(itens[-1])
            with patch("tkinter.messagebox.askyesno", return_value=True):
                form._remover_categoria()
                mock_rem.assert_called_once_with("GEO100", "02.001", base_dados="GeoApolo")

            dados_pos = form._coletar_dados()
            self.assertFalse(any(c["codigo"] == "02.001" for c in dados_pos["categorias"]))
        form.destroy()

    def test_gerenciamento_contatos(self):
        """Testa adição e remoção de telefones e contatos web na aba Contatos."""
        form = FrmCadEntidade(self.root, registro=self.registro_exemplo, base_dados="GeoApolo")
        with patch.object(form._service, "salvar_telefone", return_value=True) as mock_tel, \
             patch.object(form._service, "remover_telefone", return_value=True) as mock_rem_tel, \
             patch.object(form._service, "salvar_webcontato", return_value=True) as mock_web, \
             patch.object(form._service, "remover_webcontato", return_value=True) as mock_rem_web:

            # Telefone
            form.txt_ddd.insert(0, "35")
            form.txt_tel_num.insert(0, "998887766")
            form._adicionar_telefone()
            mock_tel.assert_called_once()

            itens_tel = form.tree_telefones.get_children()
            self.assertTrue(len(itens_tel) >= 1)
            vals_tel = form.tree_telefones.item(itens_tel[-1], "values")
            self.assertEqual(vals_tel[2], "35")
            self.assertEqual(vals_tel[3], "998887766")

            # Web / E-mail
            form.txt_web_email.insert(0, "doador@exemplo.com.br")
            form._adicionar_webcontato()
            mock_web.assert_called_once()

            itens_web = form.tree_webcontatos.get_children()
            self.assertTrue(len(itens_web) >= 1)
            vals_web = form.tree_webcontatos.item(itens_web[-1], "values")
            self.assertEqual(vals_web[1], "doador@exemplo.com.br")

            dados = form._coletar_dados()
            self.assertTrue(any(t["numero"] == "998887766" for t in dados["telefones"]))
            self.assertTrue(any(w["email"] == "doador@exemplo.com.br" for w in dados["webcontatos"]))
        form.destroy()

    def test_gerenciamento_documentos(self):
        """Testa adição, remoção e sincronização na aba Documentos."""
        form = FrmCadEntidade(self.root, registro=self.registro_exemplo, base_dados="GeoApolo")
        with patch.object(form._service, "salvar_documento", return_value=True) as mock_doc, \
             patch.object(form._service, "remover_documento", return_value=True) as mock_rem_doc:

            # Deve ter carregado o CPF e RG da entidade de exemplo
            itens_doc = form.tree_documentos.get_children()
            self.assertTrue(len(itens_doc) >= 1)

            # Adiciona novo documento
            form.cbo_doc_tipo.set("C.N.H.")
            form.txt_doc_num.insert(0, "123456789")
            form.txt_doc_obs.insert(0, "Detran MG")
            form._adicionar_documento()
            mock_doc.assert_called_once()

            dados = form._coletar_dados()
            self.assertTrue(any(d["documento"] == "123456789" for d in dados["documentos"]))
        form.destroy()


class TestEntidadesView(unittest.TestCase):
    """Testes para a grid de EntidadesView e novas regras de negócio."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.mock_repo = MagicMock()
        self.mock_service = MagicMock()

    def tearDown(self):
        self.root.destroy()

    @patch("entidades.view.EntidadeRepository")
    @patch("entidades.view.EntidadeService")
    def test_registros_pendentes_destacados_em_vermelho_na_base_geoapolo(self, mock_srv_cls, mock_repo_cls):
        mock_repo = mock_repo_cls.return_value
        mock_repo.consultar_lista.return_value = [
            {
                "geoentcod": "001",
                "entnome": "Doador Pendente",
                "atualizou_apolo": "N",
                "status_sincronizacao": "N",
            },
            {
                "geoentcod": "002",
                "entnome": "Doador Sincronizado",
                "atualizou_apolo": "S",
                "status_sincronizacao": "S",
            },
        ]

        view = EntidadesView(self.root)
        view.combo_base.set("GeoApolo")
        view._carregar_dados()

        items = view.tree.get_children()
        self.assertEqual(len(items), 2)

        tags_pendente = view.tree.item(items[0], "tags")
        tags_sinc = view.tree.item(items[1], "tags")

        # Registro pendente na base GeoApolo deve receber a tag 'pendente_geoapolo' (linha vermelha)
        self.assertIn("pendente_geoapolo", tags_pendente)
        self.assertNotIn("pendente_geoapolo", tags_sinc)
        view.destroy()

    @patch("entidades.view.EntidadeRepository")
    @patch("entidades.view.EntidadeService")
    def test_duplo_clique_abre_frmcadentidade(self, mock_srv_cls, mock_repo_cls):
        mock_repo = mock_repo_cls.return_value
        mock_repo.consultar_lista.return_value = [
            {"geoentcod": "010", "entnome": "Maria Santos", "atualizou_apolo": "N"}
        ]

        view = EntidadesView(self.root)
        view._carregar_dados()

        items = view.tree.get_children()
        view.tree.selection_set(items[0])

        with patch("entidades.cadentidade_view.FrmCadEntidade") as mock_cad:
            view._on_double_click(None)
            mock_cad.assert_called_once()
            args, kwargs = mock_cad.call_args
            self.assertEqual(kwargs["registro"]["geoentcod"], "010")

        view.destroy()

    @patch("entidades.view.EntidadeRepository")
    @patch("entidades.view.EntidadeService")
    def test_exportar_para_alvo_abre_comparador_centralizado(self, mock_srv_cls, mock_repo_cls):
        mock_repo = mock_repo_cls.return_value
        mock_srv = mock_srv_cls.return_value

        mock_repo.consultar_lista.return_value = [
            {
                "geoentcod": "020",
                "entcod": "020",
                "entnome": "Carlos Silva",
                "atualizou_apolo": "N",
                "entcpfcgc": "85746096768",
                "enttipofj": "F",
            }
        ]
        mock_repo.carregar_dados_comparacao.return_value = (
            {"geoentnome": "Carlos Silva SVE"},
            {"entnome": "Carlos Silva Alvo"},
        )
        difs_mock = [
            ItemComparacao(0, "Nome", "geoentnome", "entnome", "Carlos Silva SVE", "Carlos Silva Alvo")
        ]
        mock_srv.comparar_cadastros.return_value = difs_mock

        view = EntidadesView(self.root)
        view._carregar_dados()

        items = view.tree.get_children()
        view.tree.selection_set(items[0])

        with patch.object(view, "_abrir_tela_comparacao") as mock_abrir_comp:
            view._acao_exportar()
            mock_abrir_comp.assert_called_once()
            args, kwargs = mock_abrir_comp.call_args
            self.assertEqual(args[0], difs_mock)
            self.assertEqual(kwargs.get("geoentcod"), "020")

        view.destroy()

    def test_validacao_email_e_minusculo_em_webcontato(self):
        """Valida que o e-mail deve ter formato válido e ser salvo em minúsculo."""
        form = FrmCadEntidade(self.root, registro={"geoentcod": "NOVO"}, base_dados="GeoApolo")
        
        # Teste 1: E-mail inválido
        form.txt_web_email.delete(0, tk.END)
        form.txt_web_email.insert(0, "emailinvalido")
        with patch("tkinter.messagebox.showwarning") as mock_warn:
            form._adicionar_webcontato()
            mock_warn.assert_called()
            self.assertEqual(len(form.tree_webcontatos.get_children()), 0)

        # Teste 2: E-mail válido com maiúsculas
        form.txt_web_email.delete(0, tk.END)
        form.txt_web_email.insert(0, "USUARIO.TESTE@DOMINIO.COM.BR")
        with patch("tkinter.messagebox.showwarning") as mock_warn:
            form._adicionar_webcontato()
            mock_warn.assert_not_called()
            items = form.tree_webcontatos.get_children()
            self.assertEqual(len(items), 1)
            vals = form.tree_webcontatos.item(items[0], "values")
            self.assertEqual(vals[1], "usuario.teste@dominio.com.br")

        form.destroy()

    def test_sincronizacao_documentos_com_aba_principal(self):
        """Valida que ao salvar CPF ou RG na aba Documentos, reflete na aba Principal."""
        form = FrmCadEntidade(self.root, registro={"geoentcod": "NOVO"}, base_dados="GeoApolo")
        
        form.cbo_doc_tipo.set("CPF/CNPJ")
        form.txt_doc_num.delete(0, tk.END)
        form.txt_doc_num.insert(0, "98765432100")
        form._adicionar_documento()
        self.assertEqual(form.txt_cpf_cnpj.get(), "98765432100")

        form.cbo_doc_tipo.set("RG/IE")
        form.txt_doc_num.delete(0, tk.END)
        form.txt_doc_num.insert(0, "MG998877")
        form._adicionar_documento()
        self.assertEqual(form.txt_rg_ie.get(), "MG998877")

        form.destroy()


class TestAlvoAPIClientDelphi(unittest.TestCase):
    """Testes unitários para o cliente REST da API Alvo (Auth/Login, Riosoft-Token e Entidade/InserirAlterarEntidade)."""

    def setUp(self):
        from entidades.api_client import AlvoAPIClient
        self.client = AlvoAPIClient("https://alvo.rccbrasil.org.br/api")

    @patch("urllib.request.urlopen")
    def test_autenticar_sucesso(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'{"token": "JWT_TOKEN_12345"}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        sucesso = self.client.autenticar("JULIO", "senha123")
        self.assertTrue(sucesso)
        self.assertEqual(self.client.token, "JWT_TOKEN_12345")
        self.assertEqual(self.client.obter_token_valido(), "JWT_TOKEN_12345")

        req_chamada = mock_urlopen.call_args[0][0]
        self.assertIn("/Auth/Login", req_chamada.full_url)
        self.assertEqual(req_chamada.get_method(), "POST")

    @patch("urllib.request.urlopen")
    def test_autenticar_falha_http(self, mock_urlopen):
        import urllib.error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://alvo.rccbrasil.org.br/api/Auth/Login",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=MagicMock(read=MagicMock(return_value=b'{"erro": "Credenciais invalidas"}')),
        )

        sucesso = self.client.autenticar("JULIO", "senhaerrada")
        self.assertFalse(sucesso)
        self.assertIsNone(self.client.token)

    @patch("urllib.request.urlopen")
    def test_inserir_alterar_entidade_headers_e_payload(self, mock_urlopen):
        self.client.token = "TOKEN_VALIDO_ABC"
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'{"entcod": "54321", "mensagem": "Entidade criada"}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        payload = {"Operacao": "I", "Nome": "Paróquia São José"}
        sucesso, msg, dados = self.client.inserir_alterar_entidade(payload)

        self.assertTrue(sucesso)
        self.assertEqual(dados.get("entcod"), "54321")

        req = mock_urlopen.call_args[0][0]
        self.assertIn("/Entidade/InserirAlterarEntidade", req.full_url)
        self.assertEqual(req.headers.get("Riosoft-token"), "TOKEN_VALIDO_ABC")
        self.assertEqual(req.headers.get("Authorization"), "Bearer TOKEN_VALIDO_ABC")

    def test_extrair_entcod_resposta(self):
        from entidades.api_client import AlvoAPIClient
        self.assertEqual(AlvoAPIClient.extrair_entcod_resposta('{"entcod": 987}', {"entcod": 987}), "987")
        self.assertEqual(AlvoAPIClient.extrair_entcod_resposta('{"Codigo": "1234"}', {"Codigo": "1234"}), "1234")
        self.assertEqual(AlvoAPIClient.extrair_entcod_resposta('{"Entidade": {"entcod": "555"}}', {"Entidade": {"entcod": "555"}}), "555")
        self.assertEqual(AlvoAPIClient.extrair_entcod_resposta('9988'), "9988")
        # Extração a partir de mensagem de documento já existente na base Alvo
        msg1 = '{"Mensagem": "Atenção: O CPF 00000000000 já existe na Entidade 0017325."}'
        self.assertEqual(AlvoAPIClient.extrair_entcod_resposta(msg1, {"Mensagem": "Atenção: O CPF 00000000000 já existe na Entidade 0017325."}), "0017325")
        msg2 = '{"Mensagem": "Atenção: O CPF 85746096768 já existe na Entidade 0000003."}'
        self.assertEqual(AlvoAPIClient.extrair_entcod_resposta(msg2, {"Mensagem": "Atenção: O CPF 85746096768 já existe na Entidade 0000003."}), "0000003")


class TestExportacaoEntidadeService(unittest.TestCase):
    """Testes da montagem de payload TEntidade e orquestração de exportação no EntidadeService."""

    def setUp(self):
        self.mock_repo = MagicMock()
        from entidades.service import EntidadeService
        self.service = EntidadeService(self.mock_repo)

    def test_montar_payload_entidade_alvo_estrutura_completa(self):
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "100",
            "geoentnome": "Comunidade Nova Aliança",
            "geoentnomefantasia": "Nova Aliança",
            "tipotratcod": "01",
            "origcodestr": "ORIG01",
            "entdesdedata": "2020-01-01",
            "entdatacad": "2020-01-01",
            "entlograd": "RUA",
            "geoentender": "Rua das Flores",
            "entenderno": "120",
            "entendercomp": "Sala 2",
            "entbair": "Centro",
            "cidcod": "3550308",
            "entcep": "01001-000",
            "enttipofj": "J",
            "entcpfcgc": "12.345.678/0001-90",
            "entrgie": "123456789",
            "entcxapost": "1001",
            "georegcodestr": "REG01",
            "entconceito": "A",
            "tipocobcod": "COB01",
            "entdataanivfund": "1990-05-15",
            "cargocodestr": "CARG01",
            "entgenero": "O",
            "USERValor_Contribuicao": 50.0,
            "entobservacoes": "",
        }
        self.mock_repo.obter_cpf_rg_documentos.return_value = ("12.345.678/0001-90", "123456789")
        self.mock_repo.listar_categorias_entidade.return_value = [{"categcodestr": "01.001"}]
        self.mock_repo.listar_telefones_entidade.return_value = [
            {"geotipotelefone": "CEL", "geotelefoneddd": "11", "geotelefonenumero": "988887777"}
        ]
        self.mock_repo.carregar_contatos_entidade.return_value = []
        self.mock_repo.listar_webcontatos_entidade.return_value = [{"email": "contato@alianca.org.br"}]

        payload = self.service.montar_payload_entidade_alvo("100", operacao="I", modo="delphi")

        self.assertEqual(payload["Operacao"], "I")
        self.assertEqual(payload["CodigoAlternativo"], "100")
        self.assertEqual(payload["Nome"], "Comunidade Nova Aliança")
        self.assertEqual(payload["Natureza"], "Consumidor")
        self.assertEqual(payload["NumeroEnderecoParImpar"], "Par")
        self.assertEqual(payload["ValorContribuicao"], 50.0)

        # Categorias
        self.assertEqual(len(payload["Categorias"]), 1)
        self.assertEqual(payload["Categorias"][0]["Codigo"], "01.001")

        # Telefones
        self.assertEqual(len(payload["Telefones"]), 1)
        self.assertEqual(payload["Telefones"][0]["Numero"], "988887777")
        self.assertEqual(payload["Telefones"][0]["Principal"], "Sim")

        # Endereço
        self.assertEqual(len(payload["Enderecos"]), 1)
        self.assertEqual(payload["Enderecos"][0]["Cep"], "01001-000")

        # Emails
        self.assertEqual(len(payload["Emails"]), 1)
        self.assertEqual(payload["Emails"][0]["Email"], "contato@alianca.org.br")
        self.assertEqual(payload["Emails"][0]["Tipo"], "Pessoal")
        self.assertEqual(payload["Emails"][0]["entwebtipo"], "Pessoal")
        self.assertEqual(payload["Emails"][0]["Principal"], "Sim")
        self.assertEqual(payload["Emails"][0]["entwebemailprinc"], "Sim")

    def test_montar_payload_entidade_alvo_tipos_webcontato(self):
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "100",
            "geoentnome": "Comunidade Nova Aliança",
        }
        self.mock_repo.obter_cpf_rg_documentos.return_value = ("12.345.678/0001-90", "123456789")
        self.mock_repo.listar_categorias_entidade.return_value = []
        self.mock_repo.listar_telefones_entidade.return_value = []
        self.mock_repo.carregar_contatos_entidade.return_value = []
        self.mock_repo.listar_webcontatos_entidade.return_value = [
            {"email": "pessoal@teste.com", "tipo_contato": ""},
            {"email": "comercial@teste.com", "tipo_contato": "Comercial"},
            {"email": "financeiro@teste.com", "tipo_contato": "FINANCEIRO"},
            {"email": "outro@teste.com", "tipo_contato": "Recado"},
        ]
        payload = self.service.montar_payload_entidade_alvo("100", operacao="I", modo="delphi")
        self.assertEqual(len(payload["Emails"]), 4)
        self.assertEqual(payload["Emails"][0]["Tipo"], "Pessoal")
        self.assertEqual(payload["Emails"][0]["entwebtipo"], "Pessoal")
        self.assertEqual(payload["Emails"][0]["Principal"], "Sim")
        self.assertEqual(payload["Emails"][0]["entwebemailprinc"], "Sim")
        self.assertEqual(payload["Emails"][1]["Tipo"], "Comercial")
        self.assertEqual(payload["Emails"][1]["entwebtipo"], "Comercial")
        self.assertEqual(payload["Emails"][2]["Tipo"], "Financeiro")
        self.assertEqual(payload["Emails"][2]["entwebtipo"], "Financeiro")
        self.assertEqual(payload["Emails"][3]["Tipo"], "Pessoal")
        self.assertEqual(payload["Emails"][3]["entwebtipo"], "Pessoal")

    def test_exportar_entidade_para_alvo_sucesso(self):
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "200",
            "geoentnome": "Associação Esperança",
            "entobservacoes": "",
            "enttipofj": "F",
        }
        # CPF válido: 857.460.967-68
        self.mock_repo.obter_cpf_rg_documentos.return_value = ("85746096768", "")
        self.mock_repo.listar_categorias_entidade.return_value = []
        self.mock_repo.listar_telefones_entidade.return_value = []
        self.mock_repo.carregar_contatos_entidade.return_value = []
        self.mock_repo.listar_webcontatos_entidade.return_value = []
        self.mock_repo.vincular_entcod.return_value = True

        mock_api = MagicMock()
        mock_api.garantir_autenticacao.return_value = True
        mock_api.inserir_alterar_entidade.return_value = (True, '{"entcod": "777"}', {"entcod": "777"})
        mock_api.extrair_entcod_resposta.return_value = "777"

        res = self.service.exportar_entidade_para_alvo(
            geoentcod="200",
            usuario_alvo="USU_ALVO",
            senha_alvo_plana="senha123",
            api_client=mock_api,
        )

        self.assertTrue(res.sucesso)
        self.assertEqual(res.codigo, "777")
        self.mock_repo.vincular_entcod.assert_called_once_with("200", "777")

    def test_exportar_entidade_cpf_invalido_bloqueia_exportacao(self):
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "250",
            "geoentnome": "Entidade com CPF Inválido",
            "entobservacoes": "",
            "enttipofj": "F",
        }
        # CPF inválido com todos os dígitos iguais
        self.mock_repo.obter_cpf_rg_documentos.return_value = ("00000000000", "")
        mock_api = MagicMock()

        res = self.service.exportar_entidade_para_alvo(
            geoentcod="250",
            usuario_alvo="USU_ALVO",
            senha_alvo_plana="senha123",
            api_client=mock_api,
        )

        self.assertFalse(res.sucesso)
        self.assertIn("CPF", res.mensagem)
        self.assertIn("inválido", res.mensagem)
        # Garante que a API NÃO foi acionada
        mock_api.inserir_alterar_entidade.assert_not_called()

    def test_exportar_entidade_ja_existente_atualiza_user_geoapolo_entidade(self):
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "200",
            "geoentnome": "Doador Marcos Dione",
            "entobservacoes": "",
            "enttipofj": "F",
        }
        self.mock_repo.obter_cpf_rg_documentos.return_value = ("85746096768", "")
        self.mock_repo.listar_categorias_entidade.return_value = []
        self.mock_repo.listar_telefones_entidade.return_value = []
        self.mock_repo.carregar_contatos_entidade.return_value = []
        self.mock_repo.listar_webcontatos_entidade.return_value = []
        self.mock_repo.vincular_entcod.return_value = True

        from entidades.api_client import AlvoAPIClient
        mock_api = MagicMock()
        mock_api.garantir_autenticacao.return_value = True
        msg_erro_alvo = 'Atenção: O CPF 85746096768 já existe na Entidade 0000003.'
        mock_api.inserir_alterar_entidade.return_value = (
            False,
            f'Erro HTTP 412: {{"Mensagem": "{msg_erro_alvo}"}}',
            {"Mensagem": msg_erro_alvo}
        )
        mock_api.extrair_entcod_resposta.side_effect = AlvoAPIClient.extrair_entcod_resposta

        res = self.service.exportar_entidade_para_alvo(
            geoentcod="200",
            usuario_alvo="USU_ALVO",
            senha_alvo_plana="senha123",
            api_client=mock_api,
        )

        self.assertTrue(res.sucesso)
        self.assertEqual(res.codigo, "0000003")
        # Garante que o código extraído em variável foi gravado no campo entcod da tabela user_geoapolo_entidade
        self.mock_repo.vincular_entcod.assert_called_once_with("200", "0000003")
        self.assertIn("user_geoapolo_entidade", res.mensagem)
        self.assertIn("0000003", res.mensagem)

    def test_exportar_entidade_para_alvo_bloqueio_observacoes(self):
        self.mock_repo.carregar_dados_completos_entidade_geoapolo.return_value = {
            "geoentcod": "300",
            "geoentnome": "Entidade Pendente",
            "entobservacoes": "[PENDÊNCIAS] Pendente de conferência do estatuto",
        }
        res = self.service.exportar_entidade_para_alvo("300", "USU", "SENHA")
        self.assertFalse(res.sucesso)
        self.assertIn("pendências", res.mensagem.lower())


class TestEntidadesViewExportacao(unittest.TestCase):
    """Testes da interação e regras da tela de entidades para exportação."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    @patch("entidades.view.EntidadeRepository")
    @patch("entidades.view.EntidadeService")
    def test_acao_exportar_bloqueio_base_alvo(self, mock_srv_cls, mock_repo_cls):
        view = EntidadesView(self.root)
        view.combo_base.set("Alvo")
        reg = {"geoentcod": "01", "entnome": "Teste"}
        view._registros_atuais = [reg]
        item_id = view.tree.insert("", "end", text="0", values=("01", "Teste", "", "", "", "", "", "Alvo"))
        view.tree.selection_set(item_id)

        with patch("tkinter.messagebox.showerror") as mock_err:
            view._acao_exportar()
            mock_err.assert_called_once()
            self.assertIn("VOCÊ ESTÁ NA BASE ALVO", mock_err.call_args[0][1])

        view.destroy()

    @patch("entidades.view.EntidadeRepository")
    @patch("entidades.view.EntidadeService")
    def test_acao_exportar_bloqueio_observacoes(self, mock_srv_cls, mock_repo_cls):
        view = EntidadesView(self.root)
        view.combo_base.set("GeoApolo")
        reg = {
            "geoentcod": "01",
            "entnome": "Teste",
            "entcpfcgc": "85746096768",
            "enttipofj": "F",
            "entobservacoes": "[PENDÊNCIAS] Precisa revisar documentação",
        }
        view._registros_atuais = [reg]
        item_id = view.tree.insert("", "end", text="0", values=("01", "Teste", "", "", "", "", "", "GeoApolo"))
        view.tree.selection_set(item_id)

        with patch("tkinter.messagebox.showerror") as mock_err:
            view._acao_exportar()
            mock_err.assert_called_once()
            self.assertIn("PENDÊNCIAS", mock_err.call_args[0][1])

        view.destroy()

    @patch("entidades.view.EntidadeRepository")
    @patch("entidades.view.EntidadeService")
    def test_acao_exportar_permite_observacao_sem_pendencias(self, mock_srv_cls, mock_repo_cls):
        mock_repo = mock_repo_cls.return_value
        mock_repo.carregar_dados_comparacao.return_value = ({}, {})
        mock_srv = mock_srv_cls.return_value
        mock_srv.obter_ou_resolver_entcod_alvo.return_value = ""
        mock_srv.exportar_entidade_para_alvo.return_value = MagicMock(sucesso=True, mensagem="Sucesso")

        view = EntidadesView(self.root)
        view.combo_base.set("GeoApolo")
        reg = {
            "geoentcod": "01",
            "entnome": "Teste",
            "entcpfcgc": "85746096768",
            "enttipofj": "F",
            "entobservacoes": "[INFORMAÇÕES] Atualizado via SAVIC em 26/09/2026",
        }
        view._registros_atuais = [reg]
        item_id = view.tree.insert("", "end", text="0", values=("01", "Teste", "", "", "", "", "", "GeoApolo"))
        view.tree.selection_set(item_id)

        with patch("tkinter.messagebox.askyesno", return_value=True), \
             patch("configuracoes.alvo_api_config.validar_status_token", return_value=("SEM_TOKEN", "Sem token", False)), \
             patch.object(view, "_obter_credenciais_alvo_operador", return_value=("USU_TESTE", "SENHA_TESTE")), \
             patch("tkinter.messagebox.showinfo"), \
             patch("tkinter.messagebox.showerror") as mock_err:
            view._acao_exportar()
            for call in mock_err.call_args_list:
                self.assertNotIn("PENDÊNCIAS", call[0][1])

        view.destroy()

    @patch("entidades.view.EntidadeRepository")
    @patch("entidades.view.EntidadeService")
    def test_acao_exportar_confirmacao_e_envio_novo_registro(self, mock_srv_cls, mock_repo_cls):
        mock_repo = mock_repo_cls.return_value
        mock_repo.carregar_dados_comparacao.return_value = ({}, {})
        mock_srv = mock_srv_cls.return_value
        mock_srv.obter_ou_resolver_entcod_alvo.return_value = ""
        mock_srv.exportar_entidade_para_alvo.return_value = MagicMock(sucesso=True, mensagem="Sucesso")

        view = EntidadesView(self.root)
        view.combo_base.set("GeoApolo")
        reg = {
            "geoentcod": "50",
            "entcod": "",
            "entnome": "Nova Entidade",
            "entobservacoes": "",
            "entcpfcgc": "85746096768",
            "enttipofj": "F"
        }
        view._registros_atuais = [reg]
        item_id = view.tree.insert("", "end", text="0", values=("50", "Nova Entidade", "", "", "", "", "", "GeoApolo"))
        view.tree.selection_set(item_id)

        with patch("tkinter.messagebox.askyesno", return_value=True), \
             patch("configuracoes.alvo_api_config.validar_status_token", return_value=("SEM_TOKEN", "Sem token", False)), \
             patch.object(view, "_obter_credenciais_alvo_operador", return_value=("USU_TESTE", "SENHA_TESTE")), \
             patch("tkinter.messagebox.showinfo") as mock_info:
            view._acao_exportar()
            mock_srv.exportar_entidade_para_alvo.assert_called_once_with(
                geoentcod="50",
                usuario_alvo="USU_TESTE",
                senha_alvo_plana="SENHA_TESTE",
                api_client=view._api_client,
            )
            mock_info.assert_called_once()

        view.destroy()

    @patch("entidades.view.EntidadeRepository")
    @patch("entidades.view.EntidadeService")
    def test_acao_exportar_com_token_ativo_dispensa_login(self, mock_srv_cls, mock_repo_cls):
        mock_repo = mock_repo_cls.return_value
        mock_repo.carregar_dados_comparacao.return_value = ({}, {})
        mock_srv = mock_srv_cls.return_value
        mock_srv.obter_ou_resolver_entcod_alvo.return_value = ""
        mock_srv.exportar_entidade_para_alvo.return_value = MagicMock(sucesso=True, mensagem="Sucesso")

        view = EntidadesView(self.root)
        view.combo_base.set("GeoApolo")
        reg = {
            "geoentcod": "51",
            "entcod": "",
            "entnome": "Entidade Com Token",
            "entobservacoes": "",
            "entcpfcgc": "85746096768",
            "enttipofj": "F"
        }
        view._registros_atuais = [reg]
        item_id = view.tree.insert("", "end", text="0", values=("51", "Entidade Com Token", "", "", "", "", "", "GeoApolo"))
        view.tree.selection_set(item_id)

        with patch("tkinter.messagebox.askyesno", return_value=True), \
             patch("configuracoes.alvo_api_config.validar_status_token", return_value=("ATIVO", "Token ativo", True)), \
             patch.object(view, "_obter_credenciais_alvo_operador") as mock_cred, \
             patch("tkinter.messagebox.showinfo") as mock_info:
            view._acao_exportar()
            mock_cred.assert_not_called()
            mock_srv.exportar_entidade_para_alvo.assert_called_once_with(
                geoentcod="51",
                usuario_alvo="",
                senha_alvo_plana="",
                api_client=view._api_client,
            )
            mock_info.assert_called_once()

        view.destroy()

    @patch("entidades.view.EntidadeRepository")
    @patch("entidades.view.EntidadeService")
    def test_acao_exportar_bloqueio_cpf_invalido(self, mock_srv_cls, mock_repo_cls):
        view = EntidadesView(self.root)
        view.combo_base.set("GeoApolo")
        reg = {
            "geoentcod": "52",
            "entcod": "",
            "entnome": "Entidade CPF Invalido",
            "entobservacoes": "",
            "entcpfcgc": "00000000000",
            "enttipofj": "F"
        }
        view._registros_atuais = [reg]
        item_id = view.tree.insert("", "end", text="0", values=("52", "Entidade CPF Invalido", "", "", "", "", "", "GeoApolo"))
        view.tree.selection_set(item_id)

        with patch("tkinter.messagebox.showerror") as mock_err:
            view._acao_exportar()
            mock_err.assert_called_once()
            self.assertIn("CPF", mock_err.call_args[0][1])
            self.assertIn("inválido", mock_err.call_args[0][1])

        view.destroy()


class TestEntidadesNovasFuncionalidades(unittest.TestCase):
    """Testes para sanitização de parâmetros, formatação de datas, consultas de cidades e instanciamento."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_sanitizadores_repository(self):
        from entidades.repository import (
            _sanitizar_inteiro,
            _sanitizar_float,
            _sanitizar_data,
            _sanitizar_str,
        )

        # Inteiro
        self.assertEqual(_sanitizar_inteiro("123"), 123)
        self.assertIsNone(_sanitizar_inteiro(""))
        self.assertIsNone(_sanitizar_inteiro(None))
        self.assertIsNone(_sanitizar_inteiro("abc"))
        self.assertEqual(_sanitizar_inteiro(42), 42)

        # Float / Decimal
        self.assertEqual(_sanitizar_float("12,34"), 12.34)
        self.assertEqual(_sanitizar_float("12.34"), 12.34)
        self.assertIsNone(_sanitizar_float(""))
        self.assertIsNone(_sanitizar_float(None))
        self.assertIsNone(_sanitizar_float("invalido"))
        self.assertEqual(_sanitizar_float(9.99), 9.99)

        # Data
        self.assertEqual(_sanitizar_data("25/12/2026"), "2026-12-25")
        self.assertEqual(_sanitizar_data("2026-12-25"), "2026-12-25")
        self.assertIsNone(_sanitizar_data(""))
        self.assertIsNone(_sanitizar_data("//"))
        self.assertIsNone(_sanitizar_data("  /  /    "))
        self.assertIsNone(_sanitizar_data(None))

        # String
        self.assertEqual(_sanitizar_str("  Teste  "), "Teste")
        self.assertEqual(_sanitizar_str(123), "123")
        self.assertIsNone(_sanitizar_str(None))
        self.assertIsNone(_sanitizar_str(""))

    def test_formatacao_e_conversao_datas_cadentidade(self):
        from entidades.cadentidade_view import formatar_data_br, converter_data_para_db

        # Formatação para visualização BR (DD/MM/AAAA)
        self.assertEqual(formatar_data_br("2026-09-21"), "21/09/2026")
        self.assertEqual(formatar_data_br("2026-09-21 15:30:00"), "21/09/2026")
        self.assertEqual(formatar_data_br("21/09/2026"), "21/09/2026")
        self.assertEqual(formatar_data_br(None), "")
        self.assertEqual(formatar_data_br(""), "")

        # Conversão para persistência no Banco (YYYY-MM-DD)
        self.assertEqual(converter_data_para_db("21/09/2026"), "2026-09-21")
        self.assertEqual(converter_data_para_db("2026-09-21"), "2026-09-21")
        self.assertIsNone(converter_data_para_db(""))
        self.assertIsNone(converter_data_para_db("//"))
        self.assertIsNone(converter_data_para_db("  /  /    "))
        self.assertIsNone(converter_data_para_db(None))

    @patch("entidades.repository.EntidadeRepository._get_cursor")
    def test_obter_cidade_por_codigo_e_nome_uf(self, mock_cursor_fn):
        from entidades.repository import EntidadeRepository
        from entidades.service import EntidadeService

        mock_cursor = MagicMock()
        mock_cursor_fn.return_value = mock_cursor

        # Mock retorno de fetchone para cidade
        mock_cursor.fetchone.return_value = ("9999", "São Paulo", "SP")
        mock_cursor.description = [("geocidcod",), ("cidnomecomp",), ("ufsigla",)]

        repo = EntidadeRepository()
        cidade = repo.obter_cidade_por_codigo("9999", base_dados="GeoApolo")
        self.assertIsNotNone(cidade)
        self.assertEqual(cidade.get("nome"), "São Paulo")
        self.assertEqual(cidade.get("uf"), "SP")

        # Teste via Service
        service = EntidadeService(repo)
        cidade_srv = service.obter_cidade_por_codigo("9999", base_dados="GeoApolo")
        self.assertIsNotNone(cidade_srv)
        self.assertEqual(cidade_srv.get("nome"), "São Paulo")

    @patch("entidades.cadentidade_view.FrmCadEntidade._inicializar_dependencias")
    def test_frm_cad_entidade_single_instance(self, mock_init_dep):
        reg = {"geoentcod": "100", "entnome": "Entidade Teste"}
        form1 = FrmCadEntidade(self.root, registro=reg)
        form2 = FrmCadEntidade(self.root, registro=reg)

        # Garante que a mesma instância seja retornada (Singleton / Single Instance)
        self.assertIs(form1, form2)

        form1.destroy()
        self.assertIsNone(FrmCadEntidade._instancia_ativa)

    @patch("entidades.cadentidade_view.FrmCadEntidade._inicializar_dependencias")
    def test_frm_cad_entidade_preenchimento_e_busca_cidade(self, mock_init_dep):
        reg = {
            "geoentcod": "101",
            "entnome": "Entidade Com Cidade",
            "cidcod": "3550308",
        }
        form = FrmCadEntidade(self.root, registro=reg)

        # Mock da busca de cidade por código
        with patch.object(form, "_buscar_cidade_por_codigo", return_value={"codigo": "3550308", "nome": "São Paulo", "uf": "SP"}):
            form._on_cidcod_action()
            self.assertEqual(form.txt_cidcod.get(), "3550308")

        form.destroy()

    @patch("entidades.cadentidade_view.FrmCadEntidade._inicializar_dependencias")
    def test_frm_cad_entidade_atualizar_codigo_alvo(self, mock_init_dep):
        reg = {"geoentcod": "105", "entcod": "", "entnome": "Entidade Teste"}
        form = FrmCadEntidade(self.root, registro=reg)
        self.assertEqual(form.txt_entcod.get(), "")
        
        form.atualizar_codigo_alvo("998877")
        self.assertEqual(form.txt_entcod.get(), "998877")
        self.assertEqual(form.registro.get("entcod"), "998877")
        form.destroy()

    @patch("entidades.view.EntidadeRepository")
    @patch("entidades.view.EntidadeService")
    def test_exibicao_cod_geo_e_cod_alvo_no_treeview(self, mock_srv, mock_repo):
        view = EntidadesView(self.root)
        self.assertIn("cod_geo", view.tree["columns"])
        self.assertIn("entcod", view.tree["columns"])
        self.assertIn("documento", view.tree["columns"])

        view._registros_atuais = [
            {
                "geoentcod": "001",
                "entcod": "002",
                "entnome": "Paróquia São José",
                "EntCpfCgc": "85746096768",
                "status_sincronizacao": "S",
            }
        ]
        # Simula o loop de inserção do grid
        view.tree.delete(*view.tree.get_children())
        reg = view._registros_atuais[0]
        view.tree.insert("", tk.END, text="0", values=(
            reg["geoentcod"], reg["entcod"], reg["entnome"], reg["EntCpfCgc"], "", "", "✔ Sim (Sincronizado)", ""
        ))
        item = view.tree.get_children()[0]
        vals = view.tree.item(item, "values")
        self.assertEqual(vals[0], "001")  # Cód. Geo
        self.assertEqual(vals[1], "002")  # Cód. Alvo
        self.assertEqual(vals[2], "Paróquia São José")
        self.assertEqual(vals[3], "85746096768")  # CPF / CNPJ
        view.destroy()

    def test_extrair_entcod_resposta_multiplos_formatos(self):
        from entidades.api_client import AlvoAPIClient
        # Formato 1: JSON direto com entcod
        self.assertEqual(AlvoAPIClient.extrair_entcod_resposta("", {"entcod": 4567}), "4567")
        # Formato 2: JSON direto com Codigo
        self.assertEqual(AlvoAPIClient.extrair_entcod_resposta("", {"Codigo": "8901"}), "8901")
        # Formato 3: JSON aninhado em Entidade
        self.assertEqual(AlvoAPIClient.extrair_entcod_resposta("", {"Entidade": {"entcod": "1122"}}), "1122")
        # Formato 4: Mensagem de duplicidade de CPF informando a Entidade existente
        msg = "Atenção: O CPF 12345678900 já existe na Entidade 0017325."
        self.assertEqual(AlvoAPIClient.extrair_entcod_resposta(msg, None), "0017325")

    def test_gerar_payload_sobreposicao_com_codigos(self):
        from entidades.service import EntidadeService
        from entidades.models import ItemComparacao, DecisaoLinha
        service = EntidadeService(None)
        item = ItemComparacao(0, "Nome", "geoentnome", "entnome", "Nome SVE", "Nome Alvo", DecisaoLinha.MANTER_SVE)
        payload = service.gerar_payload_sobreposicao([item], entcod="1234", geoentcod="5678")
        self.assertEqual(payload.get("Codigo"), "1234")
        self.assertEqual(payload.get("CodigoAlternativo"), "5678")
        self.assertEqual(payload.get("Nome"), "Nome SVE")

    def test_gerar_payload_sobreposicao_genero_normalizado(self):
        """Garante que a sobreposição gere Genero com no máximo 1 caractere ('M' ou 'F')."""
        from entidades.service import EntidadeService
        from entidades.models import ItemComparacao, DecisaoLinha
        service = EntidadeService(None)

        item_masc = ItemComparacao(0, "Gênero", "geoentgenero", "entgenero", "MASCULINO", "F", DecisaoLinha.MANTER_SVE)
        p_masc = service.gerar_payload_sobreposicao([item_masc], entcod="100")
        self.assertEqual(p_masc["Genero"], "M")
        self.assertEqual(p_masc["Entidade"]["Genero"], "M")

        item_fem = ItemComparacao(0, "Gênero", "geoentgenero", "entgenero", "M", "FEMININO", DecisaoLinha.MANTER_ALVO)
        p_fem = service.gerar_payload_sobreposicao([item_fem], entcod="100")
        self.assertEqual(p_fem["Genero"], "F")
        self.assertEqual(p_fem["Entidade"]["Genero"], "F")

    def test_sanitizacao_e_resolucao_tipolograd_e_grauescolaridade(self):
        from entidades.repository import _resolver_tipolograd, _resolver_grauescolaridade, _sanitizar_obs
        mock_cursor = MagicMock()
        
        # 1. tipolograd numérico ou texto com dígitos
        self.assertEqual(_resolver_tipolograd(mock_cursor, 1), 1)
        self.assertEqual(_resolver_tipolograd(mock_cursor, "6"), 6)
        self.assertIsNone(_resolver_tipolograd(mock_cursor, ""))
        self.assertIsNone(_resolver_tipolograd(mock_cursor, None))

        # 2. tipolograd textual buscando via cursor
        mock_cursor.fetchone.return_value = (1,)
        self.assertEqual(_resolver_tipolograd(mock_cursor, "RUA"), 1)

        # 3. grau de escolaridade
        self.assertEqual(_resolver_grauescolaridade(mock_cursor, "8 - SUPERIOR"), 8)
        self.assertEqual(_resolver_grauescolaridade(mock_cursor, "4"), 4)

        # 4. truncamento de observações em 200 caracteres
        texto_longo = "A" * 350
        self.assertEqual(len(_sanitizar_obs(texto_longo, 200)), 200)

    @patch("entidades.cadentidade_view.FrmCadEntidade._inicializar_dependencias")
    def test_cep_limite_10_caracteres_e_tooltips_botoes(self, mock_init):
        reg = {"geoentcod": "301", "entnome": "Entidade Teste", "entcep": "12345-67890EXTRA"}
        form = FrmCadEntidade(self.root, registro=reg)
        
        # Validação do campo CEP
        dados = form._coletar_dados()
        self.assertLessEqual(len(dados["geoentcep"]), 10)
        self.assertLessEqual(len(dados["entcep"]), 10)

        # Validação dos botões +
        self.assertEqual(form.btn_add_categ.cget("text"), "➕")
        self.assertEqual(form.btn_add_tel.cget("text"), "➕")
        self.assertEqual(form.btn_add_web.cget("text"), "➕")
        self.assertEqual(form.btn_add_doc.cget("text"), "➕")
        
        form.destroy()

    def test_obter_ultimas_doacoes_limite_padrao_1000(self):
        from entidades.service import EntidadeService
        mock_repo = MagicMock()
        service = EntidadeService(mock_repo)
        service.obter_ultimas_doacoes("9999")
        mock_repo.obter_ultimas_doacoes.assert_called_once_with("9999", limite=1000)


class TestFrmCadEntidadeNovasFuncionalidades(unittest.TestCase):
    """Testes para os novos recursos e refinamentos do formulário FrmCadEntidade."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_inclusao_preenche_dtcad_com_data_do_dia(self):
        from datetime import date
        reg_novo = {"geoentcod": "", "entnome": "Nova Entidade Inclusão"}
        form = FrmCadEntidade(self.root, registro=reg_novo, base_dados="GeoApolo")
        hoje_str = date.today().strftime("%d/%m/%Y")
        self.assertEqual(form.txt_dtcad.get(), hoje_str)
        form.destroy()

    def test_formatacao_moeda_real_e_dolar_e_sanitizacao(self):
        reg = {"geoentcod": "100", "entnome": "Teste Moeda", "USERValor_Contribuicao": "150.75"}
        form = FrmCadEntidade(self.root, registro=reg, base_dados="GeoApolo")
        
        # Testa formatação brasileira
        form._formatar_valor_real()
        self.assertIn("R$", form.txt_valorcontrib.get())
        self.assertIn("150,75", form.txt_valorcontrib.get())

        # Testa coleta com sanitização para float
        dados = form._coletar_dados()
        self.assertEqual(dados["USERValor_Contribuicao"], "150.75")
        self.assertEqual(dados["geovalorcontribuicao"], "150.75")

        # Testa formatação americana
        form._formatar_valor_dolar()
        self.assertIn("US$", form.txt_valorcontrib.get())
        self.assertIn("150.75", form.txt_valorcontrib.get())

        dados_us = form._coletar_dados()
        self.assertEqual(dados_us["USERValor_Contribuicao"], "150.75")
        self.assertEqual(dados_us["geomoedacontribuicao"], "USD")
        form.destroy()

    def test_tipo_cobranca_debito_preenche_dia_debito(self):
        reg = {
            "geoentcod": "101",
            "entnome": "Teste Débito",
            "tipocobcod": "05",
            "tipocobnome": "DÉBITO AUTOMÁTICO EM CONTA",
            "USERDia_Debito_CC": "",
        }
        form = FrmCadEntidade(self.root, registro=reg, base_dados="GeoApolo")
        self.assertEqual(form.txt_diadebito.get(), "10")
        form.destroy()

    def test_alerta_menor_de_18_anos(self):
        from datetime import date
        ano_menor = date.today().year - 15
        dt_menor = f"01/01/{ano_menor}"
        reg = {"geoentcod": "102", "entnome": "Menor de Idade", "entdataanivfund": dt_menor}
        form = FrmCadEntidade(self.root, registro=reg, base_dados="GeoApolo")
        
        # O alerta deve estar visível e empacotado
        self.assertIn("menor de 18 anos", form.lbl_alerta_menor.cget("text").lower())
        self.assertEqual(form.frame_alerta_menor.winfo_manager(), "pack")

        # Altera para maior de idade (> 18)
        ano_maior = date.today().year - 25
        form.txt_dtnasc.delete(0, tk.END)
        form.txt_dtnasc.insert(0, f"01/01/{ano_maior}")
        form._verificar_alerta_menor()
        self.assertNotEqual(form.frame_alerta_menor.winfo_manager(), "pack")
        form.destroy()

    def test_historico_carregamento_e_novo_registro(self):
        reg = {
            "geoentcod": "103",
            "entnome": "Teste Histórico",
            "enthist": "Histórico inicial legado",
        }
        form = FrmCadEntidade(self.root, registro=reg, base_dados="GeoApolo")
        self.assertIn("Histórico inicial legado", form.txt_historico.get("1.0", tk.END))

        # Adiciona novo histórico
        form.txt_novohistorico.insert("1.0", "Registro de teste inserido pelo operador")
        form._gravar_novo_historico()

        conteudo = form.txt_historico.get("1.0", tk.END)
        self.assertIn("Registro de teste inserido pelo operador", conteudo)
        self.assertIn("Histórico inicial legado", conteudo)
        self.assertEqual(form.txt_novohistorico.get("1.0", tk.END).strip(), "")

        dados = form._coletar_dados()
        self.assertIn("Registro de teste inserido pelo operador", dados["enthist"])
        form.destroy()

    def test_toggle_subabas_endereco_cobranca_e_entrega(self):
        reg = {"geoentcod": "104", "entnome": "Teste Endereços Secundários"}
        form = FrmCadEntidade(self.root, registro=reg, base_dados="GeoApolo")
        
        subabas_inicial = [form.sub_notebook.tab(i, "text").strip() for i in range(form.sub_notebook.index("end"))]
        self.assertNotIn("End. Cobrança", subabas_inicial)
        self.assertNotIn("End. Entrega", subabas_inicial)

        # Habilita cobrança
        form.var_end_cob_mesmo.set("Não")
        form._toggle_subtab_endcobranca()
        subabas_cob = [form.sub_notebook.tab(i, "text").strip() for i in range(form.sub_notebook.index("end"))]
        self.assertIn("End. Cobrança", subabas_cob)

        # Habilita entrega
        form.var_end_ent_mesmo.set("Não")
        form._toggle_subtab_endentrega()
        subabas_ent = [form.sub_notebook.tab(i, "text").strip() for i in range(form.sub_notebook.index("end"))]
        self.assertIn("End. Entrega", subabas_ent)

        # Desabilita cobrança
        form.var_end_cob_mesmo.set("Sim")
        form._toggle_subtab_endcobranca()
        subabas_fim = [form.sub_notebook.tab(i, "text").strip() for i in range(form.sub_notebook.index("end"))]
        self.assertNotIn("End. Cobrança", subabas_fim)
        self.assertIn("End. Entrega", subabas_fim)
        form.destroy()

    def test_dados_pessoais_maiusculo_e_filhos(self):
        reg = {
            "geoentcod": "105",
            "entnome": "Teste Pessoal",
            "entnomepai": "carlos alberto",
            "entnomemae": "mariana silva",
            "entmoracom": "pais e irmaos",
            "entpossuifilho": "Sim",
            "quantosfilhos": "3"
        }
        form = FrmCadEntidade(self.root, registro=reg, base_dados="GeoApolo")
        dados = form._coletar_dados()
        self.assertEqual(dados["entnomepai"], "CARLOS ALBERTO")
        self.assertEqual(dados["entnomemae"], "MARIANA SILVA")
        self.assertEqual(dados["entmoracom"], "PAIS E IRMAOS")
        self.assertEqual(dados["entpossuifilho"], "Sim")
        self.assertEqual(dados["quantosfilhos"], "3")
        form.destroy()

    def test_grupo_oracao_vigencia_mandato(self):
        reg = {
            "geoentcod": "106",
            "entnome": "Grupo de Oração São José",
            "chkgrupooracao": "S",
            "dtiniciovigencia": "01/02/2026",
            "dtfinalvigencia": "01/02/2028",
            "contatocod": "99",
            "contatonome": "Coordenador Bento",
        }
        form = FrmCadEntidade(self.root, registro=reg, base_dados="GeoApolo")
        self.assertTrue(form.var_grupooracao.get())
        self.assertEqual(form.txt_dtiniciovigencia.get(), "01/02/2026")
        self.assertEqual(form.txt_dtfinalvigencia.get(), "01/02/2028")
        self.assertEqual(form.txt_contato_cod.get(), "99")
        self.assertEqual(form.lbl_contato_nome.get(), "Coordenador Bento")

        dados = form._coletar_dados()
        self.assertEqual(dados["chkgrupooracao"], "S")
        self.assertEqual(dados["contatocod"], "99")
        self.assertEqual(dados["contatonome"], "Coordenador Bento")
        form.destroy()


class TestComparadorEntidadesAjustes(unittest.TestCase):
    """Testes unitários para as regras do comparador de divergências (CPF, datas, entcod e referências)."""

    def test_item_comparacao_normalizacao_cpf_e_entcod(self):
        from entidades.models import ItemComparacao

        # CPF com e sem máscara deve ser considerado idêntico
        item_cpf = ItemComparacao(
            indice_mapa=1,
            rotulo="CPF / CNPJ",
            campo_sve="EntCpfCgc",
            campo_alvo="EntCpfCgc",
            valor_sve="028.690.169-21",
            valor_alvo="02869016921",
        )
        self.assertFalse(item_cpf.eh_diferente)

        # CPF divergente deve ser detectado
        item_cpf_dif = ItemComparacao(
            indice_mapa=1,
            rotulo="CPF / CNPJ",
            campo_sve="EntCpfCgc",
            campo_alvo="EntCpfCgc",
            valor_sve="028.690.169-21",
            valor_alvo="11122233344",
        )
        self.assertTrue(item_cpf_dif.eh_diferente)

        # Código Alvo com e sem zeros à esquerda deve ser considerado idêntico
        item_entcod = ItemComparacao(
            indice_mapa=0,
            rotulo="Código Alvo (entcod)",
            campo_sve="entcod",
            campo_alvo="entcod",
            valor_sve="0007199",
            valor_alvo="7199",
        )
        self.assertFalse(item_entcod.eh_diferente)

    def test_comparar_cadastros_com_referencias_e_formatacao_datas(self):
        import datetime
        from entidades.service import EntidadeService, _formatar_data_br
        from entidades.models import DecisaoLinha

        mock_repo = MagicMock()
        service = EntidadeService(mock_repo)

        # Validação direta do formatador de data BR
        self.assertEqual(_formatar_data_br(datetime.date(1979, 2, 25)), "25/02/1979")
        self.assertEqual(_formatar_data_br("1979-02-25"), "25/02/1979")
        self.assertEqual(_formatar_data_br(datetime.datetime(1979, 2, 25, 14, 30)), "25/02/1979")

        sve = {
            "geoentcod": "23211",
            "entcod": "0007199",
            "geoentnome": "ADAUTON CARDOSO DOS SANTOS",
            "EntCpfCgc": "02869016921",
            "geoentdataanivfund": datetime.date(1979, 2, 25),
            "cidnomecomp": "BALNEARIO CAMBORIU",
        }
        alvo = {
            "entcod": "7199",
            "entnome": "ADAUTON CARDOSO DOS SANTOS",
            "EntCpfCgc": "028.690.169-21",
            "EntDataAnivFund": "1980-01-10",
            "cidnomecomp": "ARAPONGAS",
        }

        difs = service.comparar_cadastros(sve, alvo, incluir_referencias=True)

        rotulos = [d.rotulo for d in difs]
        # Garante que os campos de referência estão presentes no topo
        self.assertIn("Código Alvo (entcod)", rotulos)
        self.assertIn("Código Geo (geoentcod)", rotulos)
        self.assertIn("Nome", rotulos)
        self.assertIn("CPF / CNPJ", rotulos)

        # Referências idênticas
        d_entcod = next(d for d in difs if d.rotulo == "Código Alvo (entcod)")
        self.assertFalse(d_entcod.eh_diferente)
        self.assertEqual(d_entcod.decisao, DecisaoLinha.MANTER_ALVO)

        d_cpf = next(d for d in difs if d.rotulo == "CPF / CNPJ")
        self.assertFalse(d_cpf.eh_diferente)
        self.assertEqual(d_cpf.decisao, DecisaoLinha.MANTER_ALVO)

        # Data de Aniversário divergente formatada em padrão BR (DD/MM/AAAA)
        d_nasc = next(d for d in difs if d.rotulo == "Data Aniversário")
        self.assertEqual(d_nasc.valor_sve, "25/02/1979")
        self.assertEqual(d_nasc.valor_alvo, "10/01/1980")
        self.assertTrue(d_nasc.eh_diferente)

        # Cidade deve ser acusada como divergência real
        d_cid = next(d for d in difs if d.rotulo == "Cidade")
        self.assertTrue(d_cid.eh_diferente)
        self.assertEqual(d_cid.valor_sve, "BALNEARIO CAMBORIU")
        self.assertEqual(d_cid.valor_alvo, "ARAPONGAS")
        self.assertEqual(d_cid.decisao, DecisaoLinha.NENHUMA)


class TestAjustesRgIeECidadeSobreposicao(unittest.TestCase):
    """Testes para garantir persistência de RG/IE e envio de CodigoCidade na sobreposição da API Alvo."""

    def test_gerar_payload_sobreposicao_cidade_envia_codigo_cidade_sve(self):
        from entidades.models import ItemComparacao, DecisaoLinha
        from entidades.service import EntidadeService

        mock_repo = MagicMock()
        service = EntidadeService(mock_repo)

        item_cid = ItemComparacao(
            indice_mapa=11,
            rotulo="Cidade",
            campo_sve="cidnomecomp",
            campo_alvo="cidnomecomp",
            valor_sve="BALNEARIO CAMBORIU",
            valor_alvo="ARAPONGAS",
            decisao=DecisaoLinha.MANTER_SVE,
        )
        sve_data = {"cidcodapolo": "00075493", "ufsigla": "SC"}
        alvo_data = {"cidcod": "00053902", "ufsigla": "PR"}

        payload = service.gerar_payload_sobreposicao(
            [item_cid],
            entcod="0007199",
            geoentcod="23211",
            sve_data=sve_data,
            alvo_data=alvo_data,
        )

        self.assertEqual(payload["Entidade"]["CodigoCidade"], "00075493")
        self.assertEqual(payload["CodigoCidade"], "00075493")
        self.assertEqual(payload["Entidade"]["Cidade"], "BALNEARIO CAMBORIU")

    def test_gerar_payload_sobreposicao_cidade_envia_codigo_cidade_alvo(self):
        from entidades.models import ItemComparacao, DecisaoLinha
        from entidades.service import EntidadeService

        mock_repo = MagicMock()
        service = EntidadeService(mock_repo)

        item_cid = ItemComparacao(
            indice_mapa=11,
            rotulo="Cidade",
            campo_sve="cidnomecomp",
            campo_alvo="cidnomecomp",
            valor_sve="BALNEARIO CAMBORIU",
            valor_alvo="ARAPONGAS",
            decisao=DecisaoLinha.MANTER_ALVO,
        )
        sve_data = {"cidcodapolo": "00075493", "ufsigla": "SC"}
        alvo_data = {"cidcod": "00053902", "ufsigla": "PR"}

        payload = service.gerar_payload_sobreposicao(
            [item_cid],
            entcod="0007199",
            geoentcod="23211",
            sve_data=sve_data,
            alvo_data=alvo_data,
        )

        self.assertEqual(payload["Entidade"]["CodigoCidade"], "00053902")
        self.assertEqual(payload["CodigoCidade"], "00053902")
        self.assertEqual(payload["Entidade"]["Cidade"], "ARAPONGAS")

    def test_aplicar_sobreposicao_alvo_local(self):
        from entidades.repository import EntidadeRepository

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        repo = EntidadeRepository(mock_conn)
        sucesso = repo.aplicar_sobreposicao_alvo_local(
            "0007199",
            {"CodigoCidade": "00075493", "Endereco": "Rua 1000", "Cep": "88330-000"}
        )

        self.assertTrue(sucesso)
        mock_cursor.execute.assert_any_call(
            "UPDATE entidade SET cidcod = ?, entender = ?, entcep = ? WHERE entcod = ?",
            ("00075493", "Rua 1000", "88330-000", "0007199")
        )

    def test_gravar_entidade_geoapolo_sincroniza_rg_e_cpf_documentos(self):
        from entidades.repository import EntidadeRepository

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # Simula que documento ainda não existia

        repo = EntidadeRepository(mock_conn)
        dados = {
            "geoentcod": "23211",
            "geoentnome": "ADAUTON CARDOSO",
            "geoentrgie": "59181211",
            "entcpfcgc": "02869016921",
        }
        repo.gravar_entidade_geoapolo(dados, modo_inclusao=False)

        # Verifica chamadas ao cursor para sincronizar USER_geoapolo_entidade_documentos
        chamadas_sql = [call[0][0] for call in mock_cursor.execute.call_args_list]
        tem_update_principal = any("UPDATE USER_geoapolo_entidade" in s for s in chamadas_sql)
        tem_insert_doc = any("INSERT INTO USER_geoapolo_entidade_documentos" in s for s in chamadas_sql)
        self.assertTrue(tem_update_principal)
        self.assertTrue(tem_insert_doc)

    def test_gravar_entidade_alvo_atualiza_rg_ie_e_cpf(self):
        from entidades.repository import EntidadeRepository

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        repo = EntidadeRepository(mock_conn)
        dados = {
            "entcod": "0007199",
            "entnome": "ADAUTON CARDOSO",
            "entrgie": "59181211",
            "EntCpfCgc": "02869016921",
        }
        repo.gravar_entidade_alvo(dados)

        chamadas_sql = [call[0][0] for call in mock_cursor.execute.call_args_list]
        update_entidade = next(s for s in chamadas_sql if "UPDATE entidade SET" in s)
        self.assertIn("entrgie = ?", update_entidade)
        self.assertIn("EntCpfCgc = ?", update_entidade)
class TestInclusaoEntidades(unittest.TestCase):
    """Testes específicos para inclusão de novas entidades e acionamento via Insert/Novo."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_gravar_entidade_geoapolo_modo_inclusao_completo(self):
        from entidades.repository import EntidadeRepository

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        repo = EntidadeRepository(mock_conn)
        dados = {
            "geoentcod": "00000999",
            "geoentnome": "NOVA ENTIDADE DE TESTE",
            "geoentrgie": "12345678",
            "entcpfcgc": "11122233344",
            "geoentender": "RUA TESTE",
            "geoenderno": "100",
            "geoentbair": "BAIRRO TESTE",
            "geocidcod": "001",
            "geodia_contribuicao": 15,
            "geovalorcontribuicao": 100.50,
            "geogerarcarne": "Sim",
            "georecebelembrete": "Sim",
        }
        res = repo.gravar_entidade_geoapolo(dados, modo_inclusao=True)
        self.assertTrue(res)

        chamadas_sql = [call[0][0] for call in mock_cursor.execute.call_args_list]
        tem_insert_principal = any("INSERT INTO USER_geoapolo_entidade" in s for s in chamadas_sql)
        tem_sync_doc = any("INSERT INTO USER_geoapolo_entidade_documentos" in s for s in chamadas_sql)
        self.assertTrue(tem_insert_principal)
        self.assertTrue(tem_sync_doc)

    def test_entidades_view_novo_registro_acao(self):
        with patch("entidades.view.obter_conexao_banco", return_value=None):
            view = EntidadesView(self.root)
            with patch("entidades.cadentidade_view.FrmCadEntidade") as mock_cad:
                view._novo_registro()
                mock_cad.assert_called_once()
                kwargs = mock_cad.call_args[1]
                self.assertTrue(kwargs.get("modo_inclusao"))
                self.assertIsNone(kwargs.get("registro"))
            view.destroy()


if __name__ == "__main__":
    unittest.main()

