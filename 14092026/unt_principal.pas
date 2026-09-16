unit unt_principal;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.Imaging.jpeg, Vcl.ExtCtrls,Vcl.Menus,
    // Suas uses necessárias (mantidas limpas)
  Vcl.Buttons, unt_UIHelper, unt_PermissionManager, unt_fra_StatusBar,Vcl.StdCtrls,unt_logon,
  Registry,frmdashboardvindi;
type
  Tfrmprincipal = class(TForm)
    imgfundo: TImage;
    pnlmenuprincipal: TPanel;
    spbtrocaempresa: TSpeedButton;
    spbcadastroentidades: TSpeedButton;
    lblf10sair: TLabel;
    spbsair: TSpeedButton;

    spbconciliacaovindi: TSpeedButton;
    spbocorrenciasapolo: TSpeedButton;
    spbconsulta: TSpeedButton;
    mnuprincipal: TMainMenu;
    mnuconfig: TMenuItem;
    mnuconfigdatabase: TMenuItem;
    mnuconfigparametros: TMenuItem;
    mnucfgparsisgeoapolo: TMenuItem;
    mnuparversaogeoapolo: TMenuItem;
    mnuparamcodsistema: TMenuItem;
    mnupermissoesacesso: TMenuItem;
    mnuconfigadmusuario: TMenuItem;
    mnupermissoesgrupousuarios: TMenuItem;
    mnupermissoesgrupo: TMenuItem;
    mnuconfigtrocaempresa: TMenuItem;
    mnucadastro: TMenuItem;
    mnucadativofixoti: TMenuItem;
    mnucadativoimobilizado: TMenuItem;
    mnucadcategbens: TMenuItem;
    mnucadclassificacaoativo: TMenuItem;
    mnucadestacoes: TMenuItem;
    mnucadlocalizacaofisica: TMenuItem;
    mnucadstatushardsoft: TMenuItem;
    mnucadtipolicsoftware: TMenuItem;
    mnucad_centrocontrole: TMenuItem;
    mnucad_mancentrocontrole: TMenuItem;
    mnucad_crm: TMenuItem;
    mnucadeventoscongressos: TMenuItem;
    mnucadtipocampanha: TMenuItem;
    mnucadentidades: TMenuItem;
    mnucadentcategorias: TMenuItem;
    mnuentidades: TMenuItem;
    mnuimportaentidades: TMenuItem;
    mnucadtipotratamento: TMenuItem;
    mnucadfinanceiro: TMenuItem;
    mnucadfinclasserecdesp: TMenuItem;
    mnugacadcartoescredito: TMenuItem;
    mnucadfinsitcod: TMenuItem;
    mnucadfintipocob: TMenuItem;
    mnucadestoque: TMenuItem;
    mnucadcores: TMenuItem;
    mnucadmarcas: TMenuItem;
    mnucadprodutos: TMenuItem;
    MenuItem1: TMenuItem;
    mnucadepartamentos: TMenuItem;
    mnucadempresas: TMenuItem;
    mnucadusuarios: TMenuItem;
    mnugeoapolo: TMenuItem;
    mnugeoapoloativofixoti: TMenuItem;
    mnugeoapoloatualizaativofixoti: TMenuItem;
    mnugafinanceiro: TMenuItem;
    mnugafinctaspagar: TMenuItem;
    mnugafinctaspagarcartaocredito: TMenuItem;
    mnugactasareceber: TMenuItem;
    mnugafincprecdocfin: TMenuItem;
    mnugeosavic: TMenuItem;
    mnugaintegrasavicgo: TMenuItem;
    mnugaintegrasavic_moderago: TMenuItem;
    mnugeosavicvalidaorigem: TMenuItem;
    mnuimportaentidadesavicgeoapolo: TMenuItem;
    mnuapolo: TMenuItem;
    mnuapoalvoloja: TMenuItem;
    mnuapoauditoriacupons: TMenuItem;
    mnuapoalojatrocacncf: TMenuItem;
    mnuapolocontabilidade: TMenuItem;
    mnuapolocontabdebcredconta: TMenuItem;
    mnuapoctbdebxcredetalhe: TMenuItem;
    mnuapoloexcluilctocontabil: TMenuItem;
    mnuapoctbcorrigecupom: TMenuItem;
    mnuapolocrm: TMenuItem;
    mnuapolocrmadmcampanha: TMenuItem;
    mnuapocrmatualizacampanha: TMenuItem;
    mnuapoemailmktcamp: TMenuItem;
    mnuapotlmktcamp: TMenuItem;
    mnu_apolosolocorrencia: TMenuItem;
    mnucrmapolomatchcode: TMenuItem;
    mnuapo_crm_rcc: TMenuItem;
    mnuapo_crm_rcc_importa_trackemail: TMenuItem;
    mnuapo_ent_rcc_integracongressos: TMenuItem;
    mnuapo_ent_rcc_vinculaent_dio: TMenuItem;
    mnuapoloentidades: TMenuItem;
    mnuapoloentidaderelaccateg: TMenuItem;
    mnurelacionausuariocategentidade: TMenuItem;
    mnuapo_ent_rcc: TMenuItem;
    mnuapo_ent_rcc_reclassifica: TMenuItem;
    mnuapo_ent_rcc_relacent_dio: TMenuItem;
    mnuapolofinanceiro: TMenuItem;
    mnuapologeratitulorecapolo: TMenuItem;
    mnuapolofingerarecbanco: TMenuItem;
    mnuapolodebcredcontafin: TMenuItem;
    mnuapolofinacertasituacaotitulo: TMenuItem;
    mnuapo_fin_rcc: TMenuItem;
    mnuapoloconciliavindi: TMenuItem;
    mnuapo_fin_fotograv: TMenuItem;
    mnuapo_fin_fotograv_acertaretornoitau: TMenuItem;
    mnuapo_localidade: TMenuItem;
    mnuapolocorrigedistritocidades: TMenuItem;
    mnuapo_os: TMenuItem;
    mnuapo_os_fotograv: TMenuItem;
    mnuapo_os_fotograv_cmutilizados: TMenuItem;
    mnuapo_os_fotograv_apuracm_faturado: TMenuItem;
    mnuapo_os_fotograv_acertacmutilizado: TMenuItem;
    mnuapolousuarios: TMenuItem;
    mnuapolodesativausuario: TMenuItem;
    mnuapoloclonarpermissao: TMenuItem;
    mnuapolopermsctafin: TMenuItem;
    mnutilitarios: TMenuItem;
    mnuutilconsimediatas: TMenuItem;
    mnutilconsimediatascadconsulta: TMenuItem;
    mnuconsimediatasexec: TMenuItem;
    mnutlvalidalicenca: TMenuItem;
    mnuutlenviaemail: TMenuItem;
    mnusair: TMenuItem;
    mnudashboardvindi: TMenuItem;
    procedure FormCreate(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure mnusairClick(Sender: TObject);
    procedure spbsairClick(Sender: TObject);
    procedure spbcadastroentidadesClick(Sender: TObject);
    procedure mnuentidadesClick(Sender: TObject);
    procedure mnuconsimediatasexecClick(Sender: TObject);
    procedure spbconsultaClick(Sender: TObject);
    procedure mnuconfigdatabaseClick(Sender: TObject);
    procedure mnucfgparsisgeoapoloClick(Sender: TObject);
    procedure mnuparversaogeoapoloClick(Sender: TObject);
    procedure mnucadusuariosClick(Sender: TObject);
    procedure spbtrocaempresaClick(Sender: TObject);
    procedure mnuparamcodsistemaClick(Sender: TObject);
    procedure mnuconfigadmusuarioClick(Sender: TObject);
    procedure mnupermissoesgrupousuariosClick(Sender: TObject);
    procedure mnupermissoesgrupoClick(Sender: TObject);
    procedure mnuconfigtrocaempresaClick(Sender: TObject);
    procedure mnucadeventoscongressosClick(Sender: TObject);
    procedure mnucadtipocampanhaClick(Sender: TObject);
    procedure mnucadentcategoriasClick(Sender: TObject);
    procedure mnucadtipotratamentoClick(Sender: TObject);
    procedure mnutlvalidalicencaClick(Sender: TObject);
    procedure mnuapoloconciliavindiClick(Sender: TObject);
    procedure mnudashboardvindiClick(Sender: TObject);
    procedure mnucadepartamentosClick(Sender: TObject);
    procedure mnucadempresasClick(Sender: TObject);
    procedure mnuapoauditoriacuponsClick(Sender: TObject);
    procedure mnutilconsimediatascadconsultaClick(Sender: TObject);
    procedure mnucrmapolomatchcodeClick(Sender: TObject);
    procedure spbconciliacaovindiClick(Sender: TObject);
    procedure mnuapolodesativausuarioClick(Sender: TObject);
    procedure mnuapoloclonarpermissaoClick(Sender: TObject);
    procedure mnuapolopermsctafinClick(Sender: TObject);
    procedure mnuapolocontabdebcredcontaClick(Sender: TObject);
    procedure mnuapoctbdebxcredetalheClick(Sender: TObject);
    procedure mnuapoloexcluilctocontabilClick(Sender: TObject);
    procedure mnuapoloentidaderelaccategClick(Sender: TObject);
    procedure mnurelacionausuariocategentidadeClick(Sender: TObject);
    procedure mnuapo_ent_rcc_integracongressosClick(Sender: TObject);
  private
    { Private declarations }
    FJaInicializado: Boolean;   
  public
    { Public declarations } 
    registro:tregistry;
    nomeserversql,nomebancosql,ipserversql,senhasql,protocolo,usuariobancosql,nomeserver,nomebancomix,dirnovasversoes,versao,versaoatual:string;
    resp:word;
    codigo_empresa,nome_empresa,diraplinstalador,dirinstalacaolocal,servidor_ntp,porta_servidor_ntp,caminhosbackup:string;
    pathfoto,alturafoto,largurafoto,caminhoexclusao,libera_validacao,baseparacampanha,integraentidadesapolo, caminhodabasealvoloja:string;
    servidorapp,portacomunicacao,nomebancoapp,usuarioapp,senhaapp, controle, sql, token_alvo :string;
    //  Declare estas variáveis públicas no TfrmPrincipal:
    usucod_apolo : string;   // já existe no seu código
    //token_alvo   : string;   // NOVO - guarda o JWT entre chamadas
    senha_alvo   : string;   // NOVO - guarda a senha para relogin    
  end;

var
  frmprincipal: Tfrmprincipal;

implementation

{$R *.dfm}

uses unt_entidades, funcoes, unt_imediatas, unt_configsysv2,
  frmconfigbancos, unt_mannovasversoes, unt_logon_controller, unt_users,
  unt_selecionaempresa, unt_manconfigcod, unt_usersadm, unt_grupousuario,
  unt_confignetandsys, unt_configperfil, unt_cadeventos, unt_cadcategorias,
  unt_cadtipocampanha, unt_cadtipotratamento, unt_about, unt_conciliavindi,
  unt_repo_dashboardvindi, unt_intf_dashboardvindi, unt_secao, unt_cadempresas,
  unt_auditoriacuponsfiscais, unt_cadconsulta, unt_matchcode, unt_desligafunc,
  unt_clonarpermissao, unt_usuario_ctasfin, unt_debxcred, unt_debxcred_detalhe,
  unt_excluicontabil, unt_usuario_categoria_entidade, unt_categoriaentidade,
  unt_importainscritos_eventos;

procedure Tfrmprincipal.FormActivate(Sender: TObject);
begin
   if FJaInicializado then Exit;
      FJaInicializado := True;
  // mnupermissoesgrupo.Click ;
   TPermissionManager.ApplyPermissions(Self, frmlogon.codigousuario);
end;

procedure Tfrmprincipal.FormClose(Sender: TObject; var Action: TCloseAction);
begin
   Action := caFree;
   Application.Terminate;
end;

procedure Tfrmprincipal.FormCreate(Sender: TObject);
begin
   FJaInicializado := False;
end;

procedure Tfrmprincipal.mnuapoauditoriacuponsClick(Sender: TObject);
begin
   application.CreateForm(tfrmauditoriacupons, frmauditoriacupons);
   gravalog(frmlogon.CodigoUsuario,datetostr(date),'ACESSOU AUDITORIA DE CUPOS FISCAIS');
   frmauditoriacupons.ShowModal;
end;

procedure Tfrmprincipal.mnuapoctbdebxcredetalheClick(Sender: TObject);
begin
   application.CreateForm(tfrmdebcred_detalhe, frmdebcred_detalhe);
   gravalog(frmlogon.CodigoUsuario,datetostr(date),'ACESSOU DÉBITO X CRÉDITO CONTÁBIL DETALHADO');
   frmdebcred_detalhe.ShowModal;
end;

procedure Tfrmprincipal.mnuapoloclonarpermissaoClick(Sender: TObject);
begin
   application.CreateForm(tfrmclonarpermissao, frmclonarpermissao);
   gravalog(frmlogon.CodigoUsuario,datetostr(date),'ACESSOU CLONAGEM DE PERMISSÃO DE USUÁRIOS DO ALVO');
   frmclonarpermissao.ShowModal;
end;

procedure Tfrmprincipal.mnuapoloconciliavindiClick(Sender: TObject);
begin
   application.CreateForm(tfrmconciliavindi, frmconciliavindi);
   gravalog(frmlogon.CodigoUsuario,datetostr(date),'ACESSOU CONCILIAÇÃO VINDI RCC');
   frmconciliavindi.ShowModal;
end;

procedure Tfrmprincipal.mnuapolocontabdebcredcontaClick(Sender: TObject);
begin
   application.CreateForm(tfrmdebxcred, frmdebxcred);
   gravalog(frmlogon.CodigoUsuario,datetostr(date),'ACESSOU DÉBITO X CRÉDITO CONTÁBIL');
   frmdebxcred.ShowModal;
end;

procedure Tfrmprincipal.mnuapolodesativausuarioClick(Sender: TObject);
begin
   application.CreateForm(tfrmdesligafunc, frmdesligafunc);
   gravalog(frmlogon.CodigoUsuario,datetostr(date),'ACESSO DESLIGAMENTO DE USUÁRIOS DO ALVO');
   frmdesligafunc.ShowModal;
end;

procedure Tfrmprincipal.mnuapoloentidaderelaccategClick(Sender: TObject);
begin
   application.CreateForm(tfrmrelacentidades, frmrelacentidades);
   gravalog(frmlogon.codigousuario,datetostr(date),'ACESSOU RELACIONAMENTO DE USUÁRIOS COM CATEGORIAS');
   frmrelacentidades.showmodal;
end;

procedure Tfrmprincipal.mnuapoloexcluilctocontabilClick(Sender: TObject);
begin
   application.CreateForm(tfrmexcluicontablanc, frmexcluicontablanc);
   gravalog(frmlogon.CodigoUsuario, datetostr(date),'ACESSOU EXCLUSÃO DE LANÇAMENTOS CONTÁBEIS');
   frmexcluicontablanc.ShowModal;
end;

procedure Tfrmprincipal.mnuapolopermsctafinClick(Sender: TObject);
begin
   application.CreateForm(tfrmRelacContasFin_usuario, frmRelacContasFin_usuario);
   gravalog(frmlogon.CodigoUsuario,datetostr(date),'ACESSOU DE PERMISSÕES PARA CONTAS FINANCEIRAS');
   frmRelacContasFin_usuario.showmodal;
end;

procedure Tfrmprincipal.mnuapo_ent_rcc_integracongressosClick(Sender: TObject);
begin
   application.CreateForm(tfrmimportacadastroeventos, frmimportacadastroeventos);
   gravalog(frmlogon.CodigoUsuario,datetostr(date), 'ACESSOU IMPORTAÇÃO DE PARTICIPANTES EM EVENTOS');
   frmimportacadastroeventos.ShowModal;
end;

procedure Tfrmprincipal.mnucadempresasClick(Sender: TObject);
begin
   application.CreateForm(tfrmempresa, frmempresa);
   gravalog(frmlogon.CodigoUsuario,datetostr(date),'ACESSO MANUTENÇÃO DE CADASTRO DE EMPRESAS');
   frmempresa.showmodal;
end;

procedure Tfrmprincipal.mnucadentcategoriasClick(Sender: TObject);
begin
  application.createform(tfrmcadcategoria, frmcadcategoria);
  gravalog(frmlogon.codigousuario,datetostr(date),'ACESSOU CADASTRO DE CATEGORIAS DE ATIVO FIXO DE TI');
  frmcadcategoria.ShowModal;
end;

procedure Tfrmprincipal.mnucadepartamentosClick(Sender: TObject);
begin
   application.CreateForm(tfrmdepartamentos, frmdepartamentos);
   gravalog(frmlogon.CodigoUsuario,datetostr(date),'ACESSOU MANUTENÇÃO DE DEPARTAMENTOS/EMPRESAS');
   frmdepartamentos.showmodal;
end;

procedure Tfrmprincipal.mnucadeventoscongressosClick(Sender: TObject);
begin
   application.createform(tfrmcadeventos, frmcadeventos);
   gravalog(frmlogon.codigousuario,datetostr(date),'ACESSOU CADASTRO DE EVENTOS ');
   frmcadeventos.showmodal;
end;

procedure Tfrmprincipal.mnucadtipocampanhaClick(Sender: TObject);
begin
   application.createform(tFrmtipocampanha, frmtipocampanha);
   gravalog(frmlogon.codigousuario,datetostr(date),'ACESSOU CADASTRO DE TIPOS DE CAMPANHAS !!!');
   frmtipocampanha.ShowModal;
end;

procedure Tfrmprincipal.mnucadtipotratamentoClick(Sender: TObject);
begin
   application.createform(tfrmcadtipotratamento, frmcadtipotratamento);
   gravalog(frmlogon.codigousuario,datetostr(date),'ACESSOU CADASTRO DE TIPO DE TRATAMENTO ');
   frmcadtipotratamento.showmodal;
end;

procedure Tfrmprincipal.mnucadusuariosClick(Sender: TObject);
begin
   application.CreateForm(tfrmusuarios, frmusuarios);
   gravalog(usucod_apolo, datetostr(date),'ACESSOU  CADASTROS DE USUÁRIOS GEOAPOLO !!!');
   frmusuarios.ShowModal;
end;

procedure Tfrmprincipal.mnucfgparsisgeoapoloClick(Sender: TObject);
begin
   application.CreateForm(Tfrmconfig, frmconfig);
   gravalog(usucod_apolo, datetostr(date),'ACESSOU CONFIGURAÇÃO DO SISTEMA !!!');
   frmconfig.showmodal;
end;

procedure Tfrmprincipal.mnuconfigadmusuarioClick(Sender: TObject);
begin
   application.CreateForm(tfrmusuariosadm,frmusuariosadm);
   gravalog(frmlogon.codigousuario,datetostr(date),'ACESSOU FORMULÁRIO DE USUÁRIOS ADMINISTRATIVOS');
   frmusuariosadm.ShowModal;
end;

procedure Tfrmprincipal.mnuconfigdatabaseClick(Sender: TObject);
begin
   application.CreateForm(Tfrmconfigbanco, frmconfigbanco)    ;
   gravalog(usucod_apolo, datetostr(date),'ACESSOU CONFIGURAÇÃO DE BANCO DE DADOS !!!');
   frmconfigbanco.ShowModal;
end;

procedure Tfrmprincipal.mnuconfigtrocaempresaClick(Sender: TObject);
begin
   if not funcoes.FormEstaCriado(tfrmempresa) then
      begin
         application.createform(tfrmempresa, frmempresa);
         frmempresa.ShowModal;
      end
   else
      frmempresa.ShowModal;
end;

procedure Tfrmprincipal.mnuconsimediatasexecClick(Sender: TObject);
begin
   application.CreateForm(tfrmimediatas, frmimediatas);
   gravalog(usucod_apolo, datetostr(date),'ACESSOU  GERAÇÃO DE CONSULTAS IMEDIATAS !!!');
   frmimediatas.showmodal;
end;

procedure Tfrmprincipal.mnucrmapolomatchcodeClick(Sender: TObject);
begin
   application.Createform(tfrmmatchcode, frmmatchcode);
   gravalog(frmprincipal.usucod_apolo,datetostr(date),'ENTROU EM MATCHCODE DE ENTIDADES');
   frmmatchcode.ShowModal;
end;

procedure Tfrmprincipal.mnudashboardvindiClick(Sender: TObject);
var
  frm: TfrmDashboardVindi;
begin
   frm := TfrmDashboardVindi.Create(Application);
  try
    //frm.Connection :=  // ajuste para o nome real do seu datamodule
    frm.ShowModal;
  finally
    frm.Free;
  end;
end;

procedure Tfrmprincipal.mnuentidadesClick(Sender: TObject);
begin
   spbcadastroentidades.Click;
end;

procedure Tfrmprincipal.mnuparamcodsistemaClick(Sender: TObject);
begin
   application.Createform(tfrmmancodigosSistema, frmManCodigosSistema);
   gravalog(frmprincipal.usucod_apolo,datetostr(date),'ENTROU EM CONFIGURAÇÕES DE CÓDIGOS DO SISTEMA');
   frmmancodigossistema.ShowModal;
end;

procedure Tfrmprincipal.mnuparversaogeoapoloClick(Sender: TObject);
begin
   application.CreateForm(Tfrmcadnovasversoes, frmcadnovasversoes) ;
   gravalog(frmprincipal.usucod_apolo,datetostr(date),'LOGON EM MANUTENÇÃO DE NOVAS VERSÕES !!!');
   frmcadnovasversoes.showmodal;
end;

procedure Tfrmprincipal.mnupermissoesgrupoClick(Sender: TObject);
begin
   application.CreateForm(tfrmconfigperfil, frmconfigperfil);
   gravalog(frmlogon.codigousuario,datetostr(date),'ACESSOU CONFIGURAÇÃO DE PERFIL DE USUÁRIO ');
   frmconfigperfil.ShowModal;
end;

procedure Tfrmprincipal.mnupermissoesgrupousuariosClick(Sender: TObject);
begin
   application.createform(tfrmgrupousuarios, frmgrupousuarios);
   gravalog(frmprincipal.usucod_apolo, datetostr(date),'ACESSOU GERENCIAMENTO DE GRUPOS DE USUÁRIOS !!!');
   frmgrupousuarios.showmodal;
end;

procedure Tfrmprincipal.mnurelacionausuariocategentidadeClick(Sender: TObject);
begin
   application.CreateForm(tfrmusuario_categ_entidade,frmusuario_categ_entidade);
   gravalog(frmlogon.codigousuario,datetostr(date),'ACESSOU VINCULO DE USUÁRIOS COM ENTIDADES E CATEGORIAS');
   frmusuario_categ_entidade.ShowModal;
end;

procedure Tfrmprincipal.mnusairClick(Sender: TObject);
begin
   application.Terminate;
end;

procedure Tfrmprincipal.mnutilconsimediatascadconsultaClick(Sender: TObject);
begin
   application.CreateForm(tfrmcadconsulta, frmcadconsulta);
   gravalog(frmprincipal.usucod_apolo,datetostr(date),'LOGOU EM CADASTRO DE CONSULTAS IMEDIATAS !!!');
   frmcadconsulta.ShowModal;
end;

procedure Tfrmprincipal.mnutlvalidalicencaClick(Sender: TObject);
begin
   application.CreateForm(tfrmabout, frmabout);
   gravalog(frmprincipal.usucod_apolo,datetostr(date),'ACESSOU VALIDAÇÃO DE LICENÇA');
   frmabout.showmodal;
end;

procedure Tfrmprincipal.spbcadastroentidadesClick(Sender: TObject);
begin
   application.CreateForm(tfrmentidades, frmentidades);
   gravalog(frmprincipal.usucod_apolo,datetostr(date),'LOGOU EM CADASTRO E MANUTENÇÃO DE ENTIDADES !!!');
   frmentidades.ShowModal;
end;

procedure Tfrmprincipal.spbconciliacaovindiClick(Sender: TObject);
begin
   mnuapoloconciliavindi.click;
end;

procedure Tfrmprincipal.spbconsultaClick(Sender: TObject);
begin
   mnuconsimediatasexec.Click
end;

procedure Tfrmprincipal.spbsairClick(Sender: TObject);
begin
   mnusair.Click;
end;

procedure Tfrmprincipal.spbtrocaempresaClick(Sender: TObject);
begin
   application.CreateForm(tfrmempresa, frmempresa);
   gravalog(frmlogon.CodigoUsuario,datetostr(date),'ACESSOU SELEÇÃO DE EMPRESAS !!!!');
   frmempresa.ShowModal;
end;

end.
