unit unt_estacoes;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, Buttons, ExtCtrls, StdCtrls, ComCtrls, Grids, DBGrids, Mask,
  Vcl.Menus, Data.DB, Vcl.Imaging.jpeg;

type
  Tfrmestacoes = class(TForm)
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spblimpar: TSpeedButton;
    spbdeletar: TSpeedButton;
    spbabreos: TSpeedButton;
    spbsair: TSpeedButton;
    lblmsg1: TLabel;
    StatusBar1: TStatusBar;
    GroupBox7: TGroupBox;
    lblcampo: TLabel;
    lblordem: TLabel;
    lblprocurarpor: TLabeledEdit;
    cbocampo: TComboBox;
    cbordem: TComboBox;
    rdgcrescente: TRadioButton;
    rdgdecrescente: TRadioButton;
    PopupMenu1: TPopupMenu;
    mnugravaconfiguracoes: TMenuItem;
    opendialog: TOpenDialog;
    savedialog: TSaveDialog;
    cin: TPageControl;
    tabestacoes: TTabSheet;
    lbldtcadastro: TLabel;
    spbuscaestacao: TSpeedButton;
    spbuscasecao: TSpeedButton;
    lblobsestacao: TLabel;
    lblnomedepartamento: TLabel;
    spbbuscausuario: TSpeedButton;
    spbuscaentidade: TSpeedButton;
    spbuscalocalizacao: TSpeedButton;
    lblcodigoest: TLabeledEdit;
    lbldescricao: TLabeledEdit;
    cbodepartamentos: TComboBox;
    mskdtcadastro: TMaskEdit;
    lblcodigodepartamento: TLabeledEdit;
    gridestacoes: TDBGrid;
    memobservacoes: TMemo;
    lblcodigousuario: TLabeledEdit;
    lblnomeusuario: TLabeledEdit;
    lblservicetag: TLabeledEdit;
    lblentcod: TLabeledEdit;
    edtentnome: TEdit;
    lblmodelo: TLabeledEdit;
    lbllocalizacao: TLabeledEdit;
    edtlocalizacao: TEdit;
    tabhardware: TTabSheet;
    lblvalorhard: TLabel;
    lbldatacompra: TLabel;
    lbldtativacao: TLabel;
    lbldias: TLabel;
    lblstatush: TLabel;
    lblmsgclasshard: TLabel;
    lblmsg4: TLabel;
    lblcodigohard: TLabeledEdit;
    lbldescricaohard: TLabeledEdit;
    lblnotafiscal: TLabeledEdit;
    mskvalor: TMaskEdit;
    mskdtcompra: TMaskEdit;
    mskdtativacao: TMaskEdit;
    lbltmpgarantia: TLabeledEdit;
    cbostatush: TComboBox;
    cboclasseh: TComboBox;
    memobshard: TMemo;
    grphardware: TGroupBox;
    gridfichatecnica: TDBGrid;
    gridhardware: TDBGrid;
    pnlfichatecnicahardware: TPanel;
    tabsoftware: TTabSheet;
    lblvrsoft: TLabel;
    lblmsg5: TLabel;
    lbldtcompra: TLabel;
    lblstatusoft: TLabel;
    lblclassesoft: TLabel;
    lbltipolic: TLabel;
    lblobservacoes: TLabel;
    spbuscaentsoft: TSpeedButton;
    spbuscamarca: TSpeedButton;
    spbuscasoftware: TSpeedButton;
    lbldescricaosoft: TLabeledEdit;
    lblcodsoftware: TLabeledEdit;
    lblnfsoft: TLabeledEdit;
    mskvalorsoft: TMaskEdit;
    mskdtcomprasoft: TMaskEdit;
    mskdtativasoft: TMaskEdit;
    lblmarca: TLabeledEdit;
    lblversao: TLabeledEdit;
    lblchaveinst: TLabeledEdit;
    cbostatus_s: TComboBox;
    cboclasse: TComboBox;
    cbotipolic: TComboBox;
    memobs: TMemo;
    lblentcodsoft: TLabeledEdit;
    lblcodmarca: TLabeledEdit;
    edtnomefornecedor: TEdit;
    gridsoftware: TDBGrid;
    tblconfigrede: TTabSheet;
    GroupBox5: TGroupBox;
    spbuscalocalizacaofisica: TSpeedButton;
    lblportapatch: TLabeledEdit;
    lblpatchpanel: TLabeledEdit;
    lblrack: TLabeledEdit;
    lblenderecoip: TLabeledEdit;
    lblcodlocalizacaofisica: TLabeledEdit;
    chkatualizatimetric: TCheckBox;
    edtdescricaolocalizacao: TEdit;
    gridredes: TDBGrid;
    lblvlan: TLabeledEdit;
    lblswitch: TLabeledEdit;
    lblportaswitch: TLabeledEdit;
    btnresolveip: TBitBtn;
    tabdocumentacao: TTabSheet;
    GroupBox1: TGroupBox;
    spbcarregarquivo: TSpeedButton;
    spbsalvadocumento: TSpeedButton;
    lblajusteimagem: TLabel;
    pnlimage: TPanel;
    imgdocumento: TImage;
    lblarquivo: TLabeledEdit;
    lblnumdoc: TLabeledEdit;
    griddocumentacao: TDBGrid;
    cboajusteimagem: TComboBox;
    GroupBox2: TGroupBox;
    spbgravatela1: TSpeedButton;
    lblidfichatecnica: TLabeledEdit;
    lblidentificacao: TLabeledEdit;
    lblconteudo: TLabeledEdit;
    memoobsdetalhefichatech: TMemo;
    lblnomedamarca: TLabel;
    lblcodigomarca: TLabeledEdit;
    spbuscamarcahardware: TSpeedButton;
    procedure spbsairClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormActivate(Sender: TObject);
    procedure lbldescricaoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblipKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblrackKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblpatchpanelKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbsalvarClick(Sender: TObject);
    procedure dbgusuarioKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure mskdtcadastroKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblusuarioEnter(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure tabhardwareEnter(Sender: TObject);
    procedure cbofornecedoresEnter(Sender: TObject);
    procedure cbofornecedoresKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblnotafiscalKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure mskvalorKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure mskdtcompraKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure mskdtativacaoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cbocategoriaKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cbostatushKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cboclassehKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cboclassehEnter(Sender: TObject);
    procedure memobshardEnter(Sender: TObject);
    procedure memobshardKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblestacaoEnter(Sender: TObject);
    procedure mskdtativacaoEnter(Sender: TObject);
    procedure lblcodigohardKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spblocateClick(Sender: TObject);
    procedure dbgestacoesEnter(Sender: TObject);
    procedure cbofornsoftEnter(Sender: TObject);
    procedure cbofornsoftKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblnfsoftKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure mskvalorsoftKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure mskdtcomprasoftKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure mskdtativasoftEnter(Sender: TObject);
    procedure mskdtativasoftKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblmarcaEnter(Sender: TObject);
    procedure lblmarcaKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblversaoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblchaveinstEnter(Sender: TObject);
    procedure lblchaveinstKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cbotipolicKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cbocatsoftKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cbostatus_sKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cboclasseEnter(Sender: TObject);
    procedure cboclasseKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure memobsKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure memobsEnter(Sender: TObject);
    procedure gridsoftwareDblClick(Sender: TObject);
    procedure gridsoftwareKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure mskdtcomprasoftEnter(Sender: TObject);
    procedure gridhardwareDblClick(Sender: TObject);
    procedure gridhardwareKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure gridestacoesKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure tabestacoesEnter(Sender: TObject);
    procedure spbfindestClick(Sender: TObject);
    procedure dbgconsultaDblClick(Sender: TObject);
    procedure spbabreosClick(Sender: TObject);
    procedure spbdeletarClick(Sender: TObject);
    procedure lbltmpgarantiaEnter(Sender: TObject);
    procedure FormKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblnumserieKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblcodigoestKeyPress(Sender: TObject; var Key: Char);
    procedure edtcodsecaoKeyPress(Sender: TObject; var Key: Char);
    procedure lblipKeyPress(Sender: TObject; var Key: Char);
    procedure mskdtcadastroKeyPress(Sender: TObject; var Key: Char);
    procedure lblcodest2KeyPress(Sender: TObject; var Key: Char);
    procedure lblcodigohardKeyPress(Sender: TObject; var Key: Char);
    procedure edtcodfornKeyPress(Sender: TObject; var Key: Char);
    procedure mskvalorKeyPress(Sender: TObject; var Key: Char);
    procedure mskdtcompraKeyPress(Sender: TObject; var Key: Char);
    procedure mskdtativacaoKeyPress(Sender: TObject; var Key: Char);
    procedure lbltmpgarantiaKeyPress(Sender: TObject; var Key: Char);
    procedure lblcodestsoftKeyPress(Sender: TObject; var Key: Char);
    procedure lblcodsoftwareKeyPress(Sender: TObject; var Key: Char);
    procedure edtcodfornsKeyPress(Sender: TObject; var Key: Char);
    procedure mskvalorsoftKeyPress(Sender: TObject; var Key: Char);
    procedure mskdtcomprasoftKeyPress(Sender: TObject; var Key: Char);
    procedure mskdtativasoftKeyPress(Sender: TObject; var Key: Char);
    procedure mskvalorsoftEnter(Sender: TObject);
    procedure lblrespcctrlKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cbodepartamentosKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblenderecoipKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblportapatchEnter(Sender: TObject);
    procedure lblcodlocalizacaofisicaKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblcodigodepartamentoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure gridestacoesDblClick(Sender: TObject);
    procedure spbuscasecaoClick(Sender: TObject);
    procedure spbuscaestacaoClick(Sender: TObject);
    procedure lblcodigoestKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblcodigousuarioKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblcodigousuarioEnter(Sender: TObject);
    procedure spbbuscausuarioClick(Sender: TObject);
    procedure lblprocurarporKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure memobservacoesEnter(Sender: TObject);
    procedure mnugravaconfiguracoesClick(Sender: TObject);
    procedure lblentcodKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbuscaentidadeClick(Sender: TObject);
    procedure lbldescricaohardKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lbltmpgarantiaKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lbldescricaosoftKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblentcodsoftKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbuscamarcaClick(Sender: TObject);
    procedure lblcodmarcaEnter(Sender: TObject);
    procedure lblcodmarcaKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbuscaentsoftClick(Sender: TObject);
    procedure gridsoftwareCellClick(Column: TColumn);
    procedure lblversaoEnter(Sender: TObject);
    procedure lbllocalizacaoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbuscalocalizacaoClick(Sender: TObject);
    procedure spbuscalocalizacaofisicaClick(Sender: TObject);
    procedure edtentnomeEnter(Sender: TObject);
    procedure edtlocalizacaoEnter(Sender: TObject);
    procedure edtentnomeKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure tabsoftwareEnter(Sender: TObject);
    procedure tblconfigredeEnter(Sender: TObject);
    procedure GroupBox5Enter(Sender: TObject);
    procedure spbcarregarquivoClick(Sender: TObject);
    procedure spbsalvadocumentoClick(Sender: TObject);
    procedure tabdocumentacaoEnter(Sender: TObject);
    procedure griddocumentacaoDblClick(Sender: TObject);
    procedure SpeedButton1Click(Sender: TObject);
    procedure griddocumentacaoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblnumdocKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cboajusteimagemClick(Sender: TObject);
    procedure btnresolveipClick(Sender: TObject);
    procedure lblportapatchKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure edtdescricaolocalizacaoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblvlanKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblswitchKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblportaswitchKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure gridredesKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblservicetagKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblmodeloKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblnomeusuarioKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure edtlocalizacaoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure memobservacoesKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblnotafiscalEnter(Sender: TObject);
    procedure gridredesDblClick(Sender: TObject);
    procedure gridhardwareCellClick(Column: TColumn);
    procedure FormCreate(Sender: TObject);
    procedure cbodepartamentosEnter(Sender: TObject);
    procedure lblnomeusuarioEnter(Sender: TObject);
    procedure gridfichatecnicaDblClick(Sender: TObject);
    procedure spbgravatela1Click(Sender: TObject);
    procedure gridfichatecnicaKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cinEnter(Sender: TObject);
    procedure gridfichatecnicaDrawColumnCell(Sender: TObject; const Rect: TRect;
      DataCol: Integer; Column: TColumn; State: TGridDrawState);
    procedure gridhardwareDrawColumnCell(Sender: TObject; const Rect: TRect;
      DataCol: Integer; Column: TColumn; State: TGridDrawState);
    procedure gridestacoesDrawColumnCell(Sender: TObject; const Rect: TRect;
      DataCol: Integer; Column: TColumn; State: TGridDrawState);
    procedure gridsoftwareDrawColumnCell(Sender: TObject; const Rect: TRect;
      DataCol: Integer; Column: TColumn; State: TGridDrawState);
    procedure gridredesDrawColumnCell(Sender: TObject; const Rect: TRect;
      DataCol: Integer; Column: TColumn; State: TGridDrawState);
    procedure griddocumentacaoDrawColumnCell(Sender: TObject; const Rect: TRect;
      DataCol: Integer; Column: TColumn; State: TGridDrawState);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  frmestacoes: Tfrmestacoes;
  pasta,procurarporestacao,estacao,ipantigo,data,sql,vinculo,ip,destipolic,controleopen,controle2,controle,deondeveio:string;
  resp:word;
  i,codigousuario,codigoclasse,codigostatus,codigosoftware,tipolicenca,codigoestacao,codigoestacaovelha,codigohardware:integer;

function mostra_estacoes(tipo_consulta : string) : string; export;
function mostra_hardwaredaestacao(codigo_estacao:string) : string; export;
function mostra_fichatecnicahardware(codigo_hardware : string) : string; export;
function mostra_detalhefichatecnica(codigo_hardware : string; codigo_estacao: string): string; export;
function mostra_softwaredaestacao(codigo_estacao : string) : string; export;
function mostraredeestacao(codigo_estacao:string) : string; export;
function mostra_documentacao(codigo_estacao : string) : string; export;
function grava_estacao(parametro : string) : string; export;
function grava_hardware(parametro : string) : string; export;
function grava_softwarex(parametro : string) : string; export;
function grava_redes(parametro : string) : string; export;
function retorna_codigousuario(parametro: string; login : string) : string; export;
function retorna_codigodepartamento(descricao: string) : string; export;
function retorna_statushardsoft(idstatus : string) : string; export;
function retorna_codigoclasse(parametro : string) : string; export;
function retorna_tipolicenca(descricao : string) : string; export;
function retorna_nomeentidade(parametro : string) : string; export;
function retorna_descricaolocalizacaofisica(parametro : string) : string; export;
function retorna_nomedepartamento(codigo : string) : string; export;
function carrega_combo_departamentos:string; export;
function carrega_status(parametro : string) : string; export;
function carrega_combo_classes(tipo : string) : string; export;


implementation

uses funcoes, unt_dados, unt_consultav3, unt_logon, unt_principal,unt_model_estacao,
  unt_DAOEstacoes;

{$R *.dfm}

procedure Tfrmestacoes.spbsairClick(Sender: TObject);
begin
   close;
end;

procedure Tfrmestacoes.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
   action:=cafree;
end;


procedure Tfrmestacoes.FormCreate(Sender: TObject);
begin
   deondeveio:='';
end;

procedure Tfrmestacoes.FormActivate(Sender: TObject);
begin
   with modulo_dados, frmprincipal do
   begin
      {se tiver conexão com o banco apolo, carrega o combo com os centro de controle do apolo,
      caso contrário, o combo é carregado com as seções do geoapolo}
      // ROTINAS ABAIXO IRÃO PREENCHER TODOS OS COMBOS DE DADOS BÁSICOS DO SISTEMA
      statusbar1.Panels[1].text := configura_statusbar('a');
      statusbar1.Panels[3].Text:=  configura_statusbar('a');
      statusbar1.Panels[5].text := frmprincipal.nomeserversql;
      statusbar1.Refresh;
     carrega_combo_departamentos;
     // STATUS DE HARDWARE
     carrega_status('H');
     // STATUS DE SOFTWARE
     carrega_status('S');
     mostra_estacoes('');
     // CLASSIFICAÇÃO DE BENS HARDWARE
     carrega_combo_classes('HARDWARE');
     carrega_combo_classes('SOFTWARE');
     //
     carrega_config('SATFIESTACOES',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
     configura_grid('SATFIESTACOES',frmConsulta3,'gridestacoes',frmlogon.nomeusuario,gridestacoes,modulo_dados.dtsfdquerysql);
     //
     sql:='SELECT caminhodocti FROM USER_geoapolo_configuracoes';
     fdquerysql.Close;
     fdquerysql.SQL.Clear;
     fdquerysql.SQL.Text := sql;
     if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
        begin
           pasta:=fdquerysql.fieldbyname('caminhodocti').asstring;
        end;
     mskdtcadastro.Text := datetostr(date);
     controle:='INCLUSÃO';
     //
     if deondeveio = 'DOCUMENTACAO' then
        begin
           //cin.ActivePageIndex :=4;
           lblnumdoc.SetFocus;
           cin.Refresh;
        end
     else
        begin
           lblcodigoest.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_satfi_estacao','Sim');
           tabestacoes.setfocus;
           lblcodigoest.Refresh;
           lbldescricao.SetFocus;
           cin.refresh;
        end;
     //
     cin.ActivePageIndex:=0;
     cin.Refresh;
   end;
end;

procedure Tfrmestacoes.lbldescricaoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lblservicetag.SetFocus;
end;

procedure Tfrmestacoes.lbldescricaosoftKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lblentcodsoft.setfocus;
end;

procedure Tfrmestacoes.lblipKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lblrack.SetFocus;
end;

procedure Tfrmestacoes.lbllocalizacaoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f4 then
      spbuscalocalizacao.click;
   if (key = vk_return) or (key = vk_tab) then
      edtlocalizacao.setfocus;
end;

procedure Tfrmestacoes.lblrackKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lblpatchpanel.SetFocus;
end;

procedure Tfrmestacoes.lblpatchpanelKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lblportapatch.SetFocus;
end;

procedure Tfrmestacoes.lblprocurarporKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) and (cin.ActivePageIndex =0) then
      mostra_estacoes('ESPECIFICA');
end;

procedure Tfrmestacoes.spbsalvarClick(Sender: TObject);
var
  Estacao: TEstacao;
  Dao: TEstacaoDAO;
  DataCadastroValida: TDatetime;
  MascaraLimpa: string;
begin
  Estacao := TEstacao.Create;
  Dao := TEstacaoDAO.Create(modulo_dados.fdbanco);
  try
    Estacao.Codigo := lblcodigoest.Text;
    Estacao.Descricao := lbldescricao.Text;
    Estacao.EnderecoIP := lblenderecoip.Text;

    // Remove os espaços em branco para checar se a máscara está vazia
    MascaraLimpa := StringReplace(mskdtcadastro.Text, ' ', '', [rfReplaceAll]);

    if MascaraLimpa <> '//' then
    begin
      // TryStrToDate tenta converter sem quebrar a aplicação caso a data seja inválida (ex: 31/02)
      if TryStrToDate(mskdtcadastro.Text, DataCadastroValida) then
        Estacao.DataCadastro := DataCadastroValida
      else
      begin
        ShowMessage('A data de cadastro informada é inválida. Verifique e tente novamente.');
        Exit; // Interrompe o processo antes de ir pro banco
      end;
    end;

    try
      Dao.Inserir(Estacao);
      ShowMessage('Operação realizada com sucesso!');
    except
      on E: Exception do
        ShowMessage('Não foi possível salvar a estação. Detalhe: ' + E.Message);
    end;

  finally
    Estacao.Free;
    Dao.Free;
  end;
end;

procedure Tfrmestacoes.spbuscaentidadeClick(Sender: TObject);
var
   i:integer;
begin
   with modulo_dados do
   begin
      sql:='SELECT * FROM USER_geoapolo_entidade';
      fdquerysql6.close;
      fdquerysql6.sql.clear;
      fdquerysql6.sql.text := sql;
      if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            frmconsulta3.controle:='ENTIDADE_ESTACAO';
            with frmconsulta3 do
            begin
               cbocampo.clear; cbordem.clear;
               for i:= 0 to fdquerysql6.FieldCount -1 do
               begin
                  cbocampo.Items.add(fdquerysql6.Fields[i].DisplayName);
                  cbordem.Items.add(fdquerysql6.Fields[i].DisplayName);
               end;
               carrega_config('ENTIDADE_ESTACAO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
            end;
            dtsfdquerysql6.DataSet :=fdquerysql6;
            frmconsulta3.gridconsulta.DataSource := dtsfdquerysql6;
            frmconsulta3.ShowModal;
         end;
   end;
end;

procedure Tfrmestacoes.spbuscaentsoftClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      sql:='SELECT * FROM USER_geoapolo_entidade';
      fdquerysql6.close;
      fdquerysql6.sql.clear;
      fdquerysql6.sql.text := sql;
      if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            frmconsulta3.controle:='ENTIDADE_SOFTWARE';
            dtsfdquerysql6.DataSet :=fdquerysql6;
            frmconsulta3.gridconsulta.DataSource := dtsfdquerysql6;
            frmconsulta3.ShowModal;
         end;
   end;
end;

procedure Tfrmestacoes.spbuscaestacaoClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      sql:='SELECT ugse.codigo_estacao, ugse.descricao, ugd.nome_departamento';
      sql:=sql+' FROM USER_geoapolo_satfi_estacao ugse with(nolock)';
      sql:=sql+' INNER JOIN USER_geoapolo_departamentos ugd with(nolock) ON ugse.codigo_departamento = ugd.codigo_departamento';
      sql:=sql+' INNER JOIN USER_geoapolo_usuarios ugu with(nolock) ON ugd.codigo_departamento = ugu.codigo_departamento';
      sql:=sql+' WHERE ugse.usuario_responsavel = ugu.usucod';
      fdquerysql6.close;
      fdquerysql6.sql.clear;
      fdquerysql6.sql.text := sql;
      if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            with frmconsulta3 do
            begin
               cbocampo.clear; cbordem.clear;
               for i:= 0 to fdquerysql6.FieldCount -1 do
               begin
                  cbocampo.Items.add(fdquerysql6.Fields[i].DisplayName);
                  cbordem.Items.add(fdquerysql6.Fields[i].DisplayName);
               end;
            end;
            frmconsulta3.controle:='ESTACAO';
            dtsfdquerysql6.DataSet :=fdquerysql6;
            frmconsulta3.gridconsulta.DataSource := dtsfdquerysql6;
            frmconsulta3.ShowModal;
         end;
   end;
end;

procedure Tfrmestacoes.spbuscasecaoClick(Sender: TObject);
begin
   with frmprincipal, modulo_dados do
   begin
      {montar a consulta e colocar abaixo}
      sql:='SELECT ugd.codigo_departamento, ugd.nome_departamento';
      sql:=sql+' FROM USER_geoapolo_departamentos ugd with(nolock)';
      sql:=sql+' WHERE ugd.empcod = :empcod';
      sql:=sql+' AND ugd.flagativo = :flagativo';
      sql:=sql+' ORDER BY ugd.nome_departamento';
      fdquerysql6.close;
      fdquerysql6.sql.clear;
      fdquerysql6.sql.text := sql;
      fdquerysql6.parambyname('empcod').asstring := frmprincipal.codigo_empresa;
      fdquerysql6.parambyname('flagativo').asstring := 'A';
      if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            frmconsulta3.controle:='DEPARTAMENTO_ESTACAO';
            dtsfdquerysql6.DataSet :=fdquerysql6;
            frmconsulta3.gridconsulta.DataSource := dtsfdquerysql6;
            with frmconsulta3 do
            begin
               cbocampo.clear; cbordem.clear;
               for i:= 0 to fdquerysql6.FieldCount -1 do
               begin
                  cbocampo.Items.add(fdquerysql6.Fields[i].DisplayName);
                  cbordem.Items.add(fdquerysql6.Fields[i].DisplayName);
               end;
            end;
            frmconsulta3.lblprocurarpor.text :='%%';
//            frmconsulta3.lblprocurarpor.OnKeyUp(self;vk_return,shift);
            frmconsulta3.ShowModal;
         end;
   end;
end;

procedure Tfrmestacoes.SpeedButton1Click(Sender: TObject);
begin
   mostra_documentacao(lblcodigoest.text);
   griddocumentacao.refresh;
end;

procedure Tfrmestacoes.spbuscalocalizacaoClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      sql:='SELECT ugslf.*, ugd.nome_departamento as Departamento';
	    sql:=sql+' FROM USER_geoapolo_satfi_localizacao_fisica ugslf';
      sql:=sql+' INNER JOIN USER_geoapolo_departamentos ugd with(nolock) ON ugslf.codigo_departamento = ugd.codigo_departamento';
	    sql:=sql+' ORDER BY ugslf.codigo_localizacao ASC';
      fdquerysql6.close;
      fdquerysql6.sql.clear;
      fdquerysql6.sql.text := sql;
      if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            frmconsulta3.controle:='LOCALIZACAO_FISICA_ESTACAO';
            with frmconsulta3 do
            begin
               cbocampo.clear; cbordem.clear;
               for i:= 0 to fdquerysql6.FieldCount -1 do
               begin
                  cbocampo.Items.add(fdquerysql6.Fields[i].DisplayName);
                  cbordem.Items.add(fdquerysql6.Fields[i].DisplayName);
               end;
               carrega_config('LOCALIZACAO_FISICA_ESTACAO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
            end;
            dtsfdquerysql6.DataSet :=fdquerysql6;
            frmconsulta3.gridconsulta.DataSource := dtsfdquerysql6;
            frmconsulta3.ShowModal;
         end;
   end;
end;

procedure Tfrmestacoes.spbuscalocalizacaofisicaClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      sql:='SELECT ugslf.codigo_localizacao, ugslf.grupo, ugslf.localizacao, ugslf.codigo_departamento, ugd.nome_departamento';
      sql:=sql+' FROM USER_geoapolo_satfi_localizacao_fisica ugslf with(nolock)';
      sql:=sql+' INNER JOIN USER_geoapolo_departamentos ugd with(nolock) ON ugslf.codigo_departamento = ugd.codigo_departamento';
      sql:=sql+' WHERE ugd.empcod = :empcod';
      sql:=sql+' AND   ugd.flagativo = :flagativo';
      sql:=sql+' ORDER BY ugslf.codigo_localizacao ASC';
      fdquerysql6.close;
      fdquerysql6.sql.clear;
      fdquerysql6.sql.text := sql;
      fdquerysql6.parambyname('empcod').asstring :=frmprincipal.codigo_empresa;
      fdquerysql6.parambyname('flagativo').asstring := 'A';
      if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
         begin
           application.CreateForm(tfrmconsulta3, frmconsulta3);
           dtsfdquerysql6.DataSet :=fdquerysql6;
           frmconsulta3.gridconsulta.DataSource := dtsfdquerysql6;
           frmconsulta3.controle:='LOCALIZACAO_FISICA_REDE';
           with frmconsulta3 do
           begin
              cbocampo.clear; cbordem.clear;
              for i:= 0 to fdquerysql6.FieldCount -1 do
              begin
                 cbocampo.Items.add(fdquerysql6.Fields[i].DisplayName);
                 cbordem.Items.add(fdquerysql6.Fields[i].DisplayName);
              end;
              carrega_config('LOCALIZACAO_FISICA_REDE',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
           end;
           frmconsulta3.ShowModal;
         end;
   end;
end;

procedure Tfrmestacoes.spbuscamarcaClick(Sender: TObject);
var
   i:integer;
begin
   with modulo_dados do
   begin
      sql:='SELECT * FROM USER_geoapolo_produto_marcas ';
      fdquerysql.close;
      fdquerysql.sql.clear;
      fdquerysql.sql.text := sql;
      if executaracao(fdquerysql,fdbanco, true, dtsfdquerysql) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            frmconsulta3.controle:='MARCAS_ESTACOES';
            for i:= 0 to modulo_dados.fdquerysql.FieldCount -1 do
            begin
               cbocampo.Items.add(modulo_dados.fdquerysql.Fields[i].DisplayName);
               cbordem.items.add(modulo_dados.fdquerysql.Fields[i].DisplayName);
            end;
            dtsfdquerysql.DataSet :=fdquerysql;
            frmconsulta3.gridconsulta.DataSource := dtsfdquerysql;
            frmconsulta3.ShowModal;
         end;
   end;
end;

procedure Tfrmestacoes.dbgusuarioKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_delete then
      begin
         with modulo_dados do
         begin
            resp:=messagedlg('Confirma a remoção deste usuário como responsável desta estação ? ',mtconfirmation,[mbyes,mbno],0);
            if resp = idyes then
               begin
                  sql:='DELETE FROM USER_geoapolo_usuario_estacao WHERE codigo_usuario = :codigousuario ';
                  fdquerysql3.close;
                  fdquerysql3.sql.clear;
                  fdquerysql3.sql.text := sql;
                  fdquerysql3.parambyname('codigousuario').asstring := inttostr(codigousuario) ;
                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                     begin
                        messagedlg('Vinculo Removido com sucesso !!!',mtinformation,[mbok],0);
                     end;
               end
            else
               begin
               end;
         end;
      end;
end;

procedure Tfrmestacoes.mskdtcadastroKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      begin
         lblcodigousuario.SetFocus;
      end;
end;

procedure Tfrmestacoes.lblusuarioEnter(Sender: TObject);
begin
   with modulo_dados do
   begin
      if cbodepartamentos.Text = '' then
         begin
            messagedlg('É OBRIGATÓRIO VINCULAR UMA ESTAÇÃO A UM DEPARTAMENTO !!!',mterror,[mbok],0);
            cbodepartamentos.SetFocus;
            exit;
         end
      else if trim(cbodepartamentos.Text) <> '' then
         begin
            sql:='SELECT codigo_departamento FROM USER_geoapolo_departamentos ';
            sql:=sql+' WHERE descricao = :cbodepartamentos';
            sql:=sql+' AND empcod = :empcod';
            sql:=sql+' AND flagativo = :flagativo';
            fdquerysql.close;
            fdquerysql.sql.clear;
            fdquerysql.sql.text := sql;
            fdquerysql.parambyname('cbodepartamentos').asstring:=cbodepartamentos.Text;
            fdquerysql.parambyname('empcod').asstring := frmprincipal.codigo_empresa;
            fdquerysql.parambyname('flagativo').asstring := 'A';
            if executaracao(fdquerysql,fdbanco, true, dtsfdquerysql) then
               begin
               end
            else
               messagedlg('DEPARTAMENTO NÃO ENCONTRADO !!!',mterror,[mbok],0);
         end;
   end;
end;

procedure Tfrmestacoes.spblimparClick(Sender: TObject);
begin
   if cin.ActivePageIndex = 0 then
      begin
         lbldescricao.Clear; cbodepartamentos.ItemIndex :=-1;
         lblenderecoip.Clear;lblrack.Clear; lblportapatch.Clear; lblpatchpanel.Clear;
         lblnomeusuario.clear; memobservacoes.clear; lblcodigoest.clear; lblentcod.clear; lblcodigodepartamento.clear;
         edtentnome.clear; lblmodelo.clear; lblservicetag.clear; lbllocalizacao.clear; edtlocalizacao.clear; lblcodigousuario.Clear;
         if lblprocurarpor.text <> '' then
            mostra_estacoes('ESPECIFICA')
         else
            mostra_estacoes('');
      end
   else if cin.ActivePageIndex =1 then
      begin
         lblcodigohard.Clear; lbldescricaohard.Clear; lblnotafiscal.Clear; mskvalor.Clear;
         mskdtcompra.Clear; mskdtativacao.clear; lbltmpgarantia.Clear; cbostatush.ItemIndex := -1;
         cboclasseh.ItemIndex := -1;   memobshard.Clear;
         lbldescricaohard.setfocus;
      end
   else if cin.ActivePageIndex =2 then
      begin
         lblcodsoftware.clear; lbldescricaosoft.clear; lblentcodsoft.clear; edtnomefornecedor.clear;
         lblnfsoft.clear; mskvalorsoft.clear; lblversao.clear; lblchaveinst.clear; cbotipolic.itemindex:=-1;
         lblcodmarca.clear; lblmarca.clear; mskdtcompra.text :='  /  /    '; mskdtativasoft.text := '  /  /    ';
         cbostatus_s.itemindex:=-1; cboclasse.ItemIndex:=-1;
         lbldescricaosoft.setfocus;
      end
   else if cin.ActivePageIndex = 3 then
      begin
         lblrack.clear; lblpatchpanel.clear; lblportapatch.clear; lblcodlocalizacaofisica.clear;
         edtdescricaolocalizacao.clear; chkatualizatimetric.checked := false;
         lblenderecoip.setfocus;
      end;
end;

function mostra_estacoes(tipo_consulta : string) : string;
var
   i:integer;
begin
   with modulo_dados, frmestacoes do
   begin
      sql:='SELECT * FROM USER_geoapolo_satfiview_estacao';
      fdquerysql4.close;
      fdquerysql4.sql.text := sql;
      if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
         begin
         end;
      i:=0;
      cbocampo.clear; cbordem.clear;
      for i:= 0 to fdquerysql4.FieldCount -1 do
      begin
         cbocampo.Items.add(fdquerysql4.Fields[i].DisplayName);
         cbordem.Items.add(fdquerysql4.Fields[i].DisplayName);
      end;
      carrega_config('SATFIESTACOES',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);

      if tipo_consulta = 'ESPECIFICA' then
         begin
            sql:='SELECT * FROM USER_geoapolo_satfiview_estacao';
            if cbocampo.text = '' then
               begin
                  messagedlg('SELECIONE UM CAMPO PARA A PESQUISA E PARA A ORDENAÇÃO!!!',mterror,[mbok],0);
                  cbocampo.setfocus;
                  exit;
               end
            else
               begin
                  sql:=sql+' WHERE ';
                  sql:=sql+cbocampo.text+' like :lblprocurarpor';
               end;
            if cbordem.text = '' then
               sql:=sql+' ORDER BY estacao ASC'
            else
               sql:=sql+' ORDER BY '+cbordem.text+' ASC';
            //
            fdquerysql4.close;
            fdquerysql4.sql.clear;
            fdquerysql4.sql.text := sql;
            fdquerysql4.parambyname('lblprocurarpor').asstring :='%'+lblprocurarpor.text+'%';
            if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
               begin
                  dtsfdquerysql4.DataSet := fdquerysql4;
                  gridestacoes.DataSource := dtsfdquerysql4;
                  gridestacoes.refresh;
                  gridestacoes.SetFocus;
               end;
         end
      else if tipo_consulta = '' then
         begin
            sql:='SELECT * FROM USER_geoapolo_satfiview_estacao';
            if cbordem.text <> '' then
               sql:=sql+' ORDER BY '+cbordem.text+' ASC'
            else
               sql:=sql+' ORDER BY codigo_estacao ASC';
            //
            if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
               begin
                  //
                  dtsfdquerysql4.DataSet := fdquerysql4;
                  gridestacoes.DataSource := dtsfdquerysql4;
                  gridestacoes.refresh;
                  gridestacoes.SetFocus;
               end;
         end;
     configura_grid('SATFIESTACOES',frmestacoes,frmlogon.nomeusuario,'gridestacoes',gridestacoes,modulo_dados.dtsfdquerysql4);
   end;
end;

function grava_estacao(parametro : string) : string;
var
   datacadastro,codigousuario:string;
begin
    with modulo_dados, frmestacoes do
    begin
      if parametro = 'INCLUSÃO' then
         begin
            if trim(lbldescricao.Text) = '' then
               begin
                  messagedlg('NÃO É PERMITIDO O CADASTRAMENTO DE ESTAÇÕES COM DESCRIÇÃO EM BRANCO !!!',mterror,[mbok],0);
                  lbldescricao.SetFocus;
                  exit;
               end;
            //
            resp :=messagedlg('Confirma os dados desta estação ? (Y/N)',mtinformation,[mbyes,mbno],0);
            if resp = idyes then
               begin
                  codigousuario:=retorna_codigousuario('CÓDIGO',lblnomeusuario.text);
                  ip:=lblenderecoip.Text;
                  datacadastro:=mskdtcadastro.Text;
                  mskdtcadastro.Text := FormatDatetime('yyyy-mm-dd',strtodatetime(datacadastro));
                  sql:='INSERT INTO USER_geoapolo_satfi_estacao (codigo_estacao,descricao,codigo_departamento,data_cadastro, codigo_usuario, usuario_responsavel, tag_servico, geoentcod, modelo_estacao,codigo_localizacao)';
                  sql:=sql+' VALUES (:codigoestacao, :descricao, :codigodepartamento, :datacadastro, :codigousuario, :usuarioresponsavel, :tagservico, :modeloestacao, :codigolocalizacao)';
                  fdquerysql3.close;
                  fdquerysql3.sql.clear;
                  fdquerysql3.sql.text := sql;
                  fdquerysql3.parambyname('codigoestacao').asstring :=lblcodigoest.Text;
                  fdquerysql3.parambyname('descricao').asstring :=lbldescricao.Text;
                  fdquerysql3.parambyname('codigodepartamento').asstring :=lblcodigodepartamento.Text;
                  fdquerysql3.parambyname('datacadastro').asstring := datacadastro;
                  fdquerysql3.parambyname('codigousuario').asstring :=retorna_codigousuario('CÓDIGO',lblcodigousuario.Text);
                  fdquerysql3.parambyname('usuarioresponsavel').asstring := lblnomeusuario.Text;
                  fdquerysql3.parambyname('tagservico').asstring := lblservicetag.text ;
                  fdquerysql3.parambyname('modeloestacao').asstring := lblmodelo.text;
                  fdquerysql3.parambyname('codigolocalizacao').asstring := lbllocalizacao.text;
                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                     begin
                        messagedlg('Operação realizada com sucesso, A próxima fase é o Cadastramento de Hardware !!!',mtinformation,[mbok],0);
                        mostra_estacoes('');
                        cin.ActivePageIndex :=2;
                     end
                  else
                     begin
                        messagedlg('NÃO FOI POSSÍVEL CONFIRMAR ESTA OPERAÇÃO !!!',mterror,[mbok],0);
                        lbldescricao.SetFocus;
                     end;
               end
         end
      else if parametro = 'ALTERAÇÃO' then
         begin
            if trim(lbldescricao.Text) = '' then
               begin
                  messagedlg('NÃO É PERMITIDO O CADASTRAMENTO DE ESTAÇÕES COM DESCRIÇÃO EM BRANCO !!!',mterror,[mbok],0);
                  lbldescricao.SetFocus;
                  exit;
               end;
           resp:=messagedlg('Confirma '+controle+' desta estação ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
           if resp = idyes then
              begin
                  codigousuario:=retorna_codigousuario('CÓDIGO',lblnomeusuario.text);
                  datacadastro:= mskdtcadastro.Text;
                  datacadastro := formatdatetime('yyyy-mm-dd',strtodatetime(datacadastro));
                  sql:='UPDATE USER_geoapolo_satfi_estacao SET descricao = :descricao';
                  sql:=sql+', codigo_departamento = :codigodepartamento, codigo_usuario = :codigousuario, usuario_responsavel = :usuarioresponsavel, ';
                  sql:=sql+', tag_servico = :servicetag, data_cadastro = :datacadastro';
                  sql:=sql+' WHERE codigo_estacao = :codgoestacao';
                  fdquerysql3.close;
                  fdquerysql3.sql.clear;
                  fdquerysql3.sql.text := sql;
                  fdquerysql3.parambyname('codigodepartamento').asstring :=  lblcodigodepartamento.text;
                  fdquerysql3.parambyname('descricao').asstring := lbldescricao.text;
                  fdquerysql3.parambyname('codigo_usuario').asstring := lblcodigousuario.text;
                  fdquerysql3.parambyname('usuarioresponsavel').asstring := lblnomeusuario.text ;
                  fdquerysql3.parambyname('servicetag').asstring := lblservicetag.text;
                  fdquerysql3.parambyname('data_cadastro').asstring := mskdtcadastro.text;
                  fdquerysql3.parambyname('codigoestacao').asstring := lblcodigoest.text;
                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                     begin
                        messagedlg('Operação realizada com sucesso !!!',mtinformation,[mbok],0);
                        spblimpar.Click; controle:='INCLUSÃO';
                        mostra_estacoes('');
                        cin.ActivePageIndex :=0;
                        lblcodigoest.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_satfi_estacao','N');
                        lblcodigoest.Refresh;
                        lbldescricao.SetFocus;
                     end
                  else
                     begin
                        messagedlg('NÃO FOI POSSÍVEL CONFIRMAR ESTA OPERAÇÃO !!!',mterror,[mbok],0);
                        lbldescricao.SetFocus;
                     end;
              end;
         end;
   end;
end;

function grava_hardware(parametro : string) : string;
var
   datacompra,datativacao:string;
begin
   with modulo_dados, frmestacoes do
   begin
      if (lblcodigohard.text = '') or (lbldescricaohard.text = '') then
         begin
            messagedlg('CÓDIGO E DESCRIÇÃO DO HARDWARE SÃO CAMPOS OBRIGATÓRIOS !!!',mterror,[mbok],0);
            lbldescricaohard.setfocus;
         end;
      //
      if ((alltrim(mskdtcompra.text) = ' / /  ') or (trim(mskdtcompra.text)  = '')) then
         datacompra:='NULL'
      else
         begin
            datacompra:=alltrim(mskdtcompra.text);
            datacompra:=formatdatetime('yyyy-mm-dd',strtodate(mskdtcompra.Text));
         end;
      //
      if ((alltrim(mskdtativacao.text) = ' / /  ') or (mskdtativacao.text = ''))  then
         datativacao:='NULL'
      else
         begin
            datativacao:=alltrim(mskdtativacao.text);
            datativacao:=formatdatetime('yyyy-mm-dd',strtodatetime(mskdtativacao.Text));
         end;
      //
      if lbltmpgarantia.text = '' then
         lbltmpgarantia.Text := '360';
      //
      if memobshard.text = '' then
         memobshard.text := '...';
      //
      if mskvalor.text = '' then
         mskvalor.text :='0.00';
      //
      // ANTES DE INCLUIR OU ALTERAR O HARDWARE, VERIFICA SE O MESMO EXISTE PARA AQUELA ESTAÇÃO, EM EXISTINDO MUDA O CONTROLE
      // PARA ALTERAR, SE NÃO EXISTIR, COLOCA COMO INCLUSÃO
      if (codigoclasse = 0) and (cboclasse.Text <> '') then
         codigoclasse:=strtoint(retorna_codigoclasse(cboclasse.Text));

      sql:= 'SELECT ugsh.codigo_hardware FROM USER_geoapolo_satfi_hardware ugsh with(nolock) ';
      sql:=sql+' WHERE codigo_estacao = :codigoestacao';
      sql:=sql+' AND descricao = :descricaohardware';
      fdquerysql6.close;
      fdquerysql6.sql.clear;
      fdquerysql6.sql.text := sql;
      fdquerysql6.parambyname('codigoestacao').asstring := lblcodigoest.text;
      fdquerysql6.parambyname('descricaohardware').asstring := lbldescricaohard.Text;

      if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
         parametro:='ALTERAÇÃO'
      else
         parametro:='INCLUSÃO';
      //
      lblnotafiscal.text := buscatroca(lblnotafiscal.text,'.','');
      lblnotafiscal.text := buscatroca(lblnotafiscal.text,'-','');
      resp:=messagedlg('Confirma a '+parametro+' para este Hardware ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
      if resp = idyes then
         begin
            if parametro = 'INCLUSÃO' then
               begin
                  sql:='INSERT INTO USER_geoapolo_satfi_hardware (codigo_hardware,descricao,valor,data_compra,data_ativacao,tempo_garantia,';
                  sql:=sql+' codigo_status_h,codigo_estacao,codigoclasse,observacoes,nf)';
                  sql:=sql+' VALUES (:codigohardware, :descricao, :valor, :datacompra, :dataativacao, ';
                  sql:=sql+' :tempogarantia, :codigostatus, :codigoestacao,:codigoclasse, :observacoes, :nf)';
                  fdquerysql3.close;
                  fdquerysql3.sql.clear;
                  fdquerysql3.sql.text := sql;
                  fdquerysql3.parambyname('codigohardware').asstring :=lblcodigohard.text;
                  fdquerysql3.parambyname('descricao').asstring :=lbldescricaohard.text;
                  fdquerysql3.parambyname('valor').asstring := mskvalor.text;
                  fdquerysql3.parambyname('datacompra').asstring := datacompra;
                  fdquerysql3.parambyname('dataativacao').asstring := datativacao;
                  fdquerysql3.parambyname('tempogarantia').asstring :=lbltmpgarantia.text;
                  fdquerysql3.parambyname('codigostatus').asstring := inttostr(codigostatus);
                  fdquerysql3.parambyname('codigoestacao').asstring := lblcodigoest.text;
                  fdquerysql3.parambyname('codigoclasse').asstring := inttostr(codigoclasse);
                  fdquerysql3.parambyname('observacoes').asstring:=memobshard.text;
                  fdquerysql3.parambyname('nf').asstring:= lblnotafiscal.text;
               end
            else if parametro = 'ALTERAÇÃO' then
               begin
                  sql:='UPDATE USER_geoapolo_satfi_hardware SET descricao = :lbldescricaohard';
                  sql:=sql+', valor = :mskvalor';
                  if datacompra = 'NULL' then
                     sql:=sql+', data_compra = '+' null'
                  else
                     sql:=sql+', data_compra = :datacompra';
                  //
                  if datativacao = 'NULL' then
                     sql:=sql+', data_ativacao = '+' null'
                  else
                     sql:=sql+', data_ativacao = :datativacao';
                  //
                  sql:=sql+', tempo_garantia = :tempogarantia';
                  sql:=sql+', codigo_status_h = :codigostatus, codigoclasse = :codigoclasse ';
                  sql:=sql+', observacoes = :memobshard, nf = :nfnum';
                  sql:=sql+' WHERE codigo_hardware = :lblcodigohard';
                  sql:=sql+' AND   codigo_estacao = :codigoestacao';
               end;
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('lbldescricaohard').AsString :=lbldescricaohard.text;
            fdquerysql3.ParamByName('mskvalor').AsString :=mskvalor.text;
            fdquerysql3.ParamByName('datacompra').AsString := datacompra ;
            fdquerysql3.ParamByName('datativacao').AsString := datativacao;
            fdquerysql3.ParamByName('tempogarantia').AsString:= lbltmpgarantia.text;
            fdquerysql3.ParamByName('codigostatus').AsString := inttostr(codigostatus);
            fdquerysql3.ParamByName('codigoclasse').AsString :=  inttostr(codigoclasse);
            fdquerysql3.ParamByName('memobshard').AsString := memobshard.text;
            fdquerysql3.parambyname('nfnum').AsString := lblnotafiscal.text;
            fdquerysql3.ParamByName('lblcodigohard').AsString := lblcodigohard.Text;
            fdquerysql3.ParamByName('codigoestacao').AsString := lblcodigoest.text;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  messagedlg('Operação realizada com sucesso !!!',mtinformation,[mbok],0);
                  spblimpar.Click;
                  mostra_hardwaredaestacao(lblcodigoest.text);
                  lbldescricaohard.SetFocus;
               end
            else
               begin
                  messagedlg('NÃO FOI POSSÍVEL CONFIRMAR ESTA OPERAÇÃO !!!',mterror,[mbok],0);
                  lbldescricaohard.SetFocus;
               end;
         end
      else
         begin
             lbldescricaohard.setfocus;
         end;
   end;
end;

function grava_softwarex(parametro : string) : string;
var
   datacompra,datativacao,codigostatus:string;
begin
   with modulo_dados, frmestacoes do
   begin
      if (lblcodsoftware.text = '') or (lbldescricaosoft.text ='') then
         begin
            messagedlg('O CÓDIGO E DESCRIÇÃO DO SOFTWARE SÃO CAMPOS OBRIGATÓRIOS !!!',mterror,[mbok],0);
            lbldescricaosoft.setfocus;
            exit;
         end;
      //
      if (lblnfsoft.text = '') and (cbotipolic.text <> 'CONTRATO GPL/GNU') then
         begin
            messagedlg('É ALTAMENTE RECOMENDÁVEL INFORMAR A NOTA FISCAL DE COMPRA DO SOFTWARE !!!',mtwarning,[mbok],0);
            lblnfsoft.setfocus;
         end
      else if (lblnfsoft.text = '') and (cbotipolic.text = 'CONTRATO GPL/GNU') then
         begin
            lblnfsoft.text := '0';
         end;
      //
      if cbotipolic.text = '' then
         begin
            messagedlg('É ALTAMENTE RECOMENDÁVEL INFORMAR O TIPO DE LICENCIAMENTO DESTE SOFTWARE !!!',mtwarning,[mbok],0);
            cbotipolic.setfocus;
            exit;
         end
      else
         begin
            if tipolicenca = 0 then
               tipolicenca:=strtoint(retorna_tipolicenca(cbotipolic.text));
         end;
      //
      if cboclasse.text = '' then
         begin
            messagedlg('É ALTAMENTE RECOMENDÁVEL CLASSIFICAR ESTE SOFTWARE !!!',mtwarning,[mbok],0);
            cbotipolic.setfocus;
            exit;
         end
      else
         begin
            if codigoclasse = 0 then
               codigoclasse:=strtoint(retorna_codigoclasse(cboclasse.text));
         end;
      if (mskdtcomprasoft.text = '  /  /    ') then
         datacompra:='NULL'
      else
         begin
            datacompra:=mskdtcomprasoft.text;
            datacompra:=formatdatetime('yyyy-mm-dd',strtodatetime(mskdtcomprasoft.Text));
         end;
      //
      if (mskdtativacao.text = '  /  /    ') then
         datativacao:='NULL'
      else
         begin
            datativacao:=mskdtativasoft.text;
            datativacao:=formatdatetime('yyyy-mm-dd',strtodatetime(datativacao));
         end;
      //
      if (mskdtcomprasoft.text  = '  /  /    ') and (datacompra = '') then
         datacompra:='NULL';
      //
      if (mskdtativacao.text = '  /  /    ') and (datativacao = '') then
         datativacao:=' NULL';
      //
      if mskvalorsoft.text = '' then
         mskvalorsoft.text :='0.00';
      //
      if lblnfsoft.Text = '' then
         lblnfsoft.Text := '0';

      mskvalorsoft.Text := buscatroca(mskvalorsoft.Text,',','.');
      //
      //lblnfsoft.text := buscatroca(lblnotafiscal.text,'.','');
      //lblnfsoft.text := buscatroca(lblnotafiscal.text,'-','');
      sql:= 'SELECT ugss.codigo_software'   ;
      sql:=sql+' FROM USER_geoapolo_satfi_software ugss with(nolock)';
      sql:=sql+' WHERE ugss.codigo_estacao = :lblcodigoest';
      sql:=sql+' AND descricao = :lbldescricaosoft' ;
      fdquerysql6.Close;
      fdquerysql6.SQL.Clear;
      fdquerysql6.SQL.Text := sql;
      fdquerysql6.ParamByName('lblcodigoest').AsString := lblcodigoest.Text;
      fdquerysql6.ParamByName('lbldescricaosoft').AsString:= lbldescricaosoft.Text;
      if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
         parametro:='ALTERAÇÃO'
      else
         parametro:='INCLUSÃO';
      // valida codigo do software
      if codigosoftware = 0 then
         begin
           lblcodsoftware.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_satfi_software','Sim');
           codigosoftware:=strtoint(lblcodsoftware.Text);
         end;
      resp:=messagedlg('Confirma a '+parametro+' para este Software (Y/N) ?',mtconfirmation, [mbyes,mbno],0);
      if resp = idyes then
         begin
            codigostatus:=retorna_statushardsoft('S');
            if parametro = 'INCLUSÃO' then
               begin
                  sql:='INSERT INTO USER_geoapolo_satfi_software (codigo_software,descricao,nfsoft,valor,data_compra,';
                  sql:=sql+' codigo_status, codigoclasse, codigo_tipo_lic,codigo_estacao, geoentcod, service_pack, chave_produto,';
                  sql:=sql+' codigo_marca, data_ativacao)';
                  sql:=sql+' VALUES (:codigosoftware, :lbldescricaosoft, :lblnfsoft, :mskvalorsoft, :mskdtcomprasoft, :mskvalorsoft,';
                  sql:=sql+' :mskdtcomprasoft, :datacompra, :codigostatus, :codigoclasse, :tipolicenca, :codigoestacao, :lblentcodsoft,';
                  sql:=sql+' :lblversao, :lblchaveinst, :lblcodmarca, :datativacao)';
               end
            else if parametro = 'ALTERAÇÃO' then
               begin
                  sql:='UPDATE USER_geoapolo_satfi_software SET descricao = :lbldescricaosoft';
                  sql:=sql+', nf = :nfnum, valor = :mskvalorsoft';
                  if (mskdtcomprasoft.text  = '  /  /    ') and (datacompra = '') then
                    sql:=sql+', data_compra = '+'NULL'
                  else
                     sql:=sql+', data_compra = :datacompra'; //+datacompra;
                  //
                  sql:=sql+', codigo_status = :codigostatus';
                  sql:=sql+', codigo_tipo_lic = :tipolicenca';
                  sql:=sql+', geoentcod = :geoentcod';
                  sql:=sql+', service_pack = :lblversao';
                  sql:=sql+', chave_produto = :lblchaveinst';
                  sql:=sql+', codigo_marca = :codigomarca';
                  sql:=sql+', codigoclasse = :codigoclasse';
                  if (mskdtativacao.text = '  /  /    ') and (datativacao = '') then
                     sql:=sql+', data_ativacao = '+'NULL'
                  else
                     sql:=sql+', data_ativacao = :datativacao';
                  //
                  sql:=sql+' WHERE codigo_software = :codigosoftware';
                  sql:=sql+' AND codigo_estacao = :lblcodigoest';
               end;
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('lbldescricaosoft').AsString := lbldescricaosoft.Text;
            fdquerysql3.ParamByName('nfnum').AsString := lblnotafiscal.Text;
            fdquerysql3.ParamByName('mskvalor').AsString := mskvalorsoft.Text;
            fdquerysql3.ParamByName('datacompra').AsString := datacompra;
            fdquerysql3.ParamByName('codigostatus').AsString := codigostatus;
            fdquerysql3.ParamByName('tipolicenca').AsString := inttostr(tipolicenca);
            fdquerysql3.ParamByName('geoentcod').AsString :=lblentcodsoft.text;
            fdquerysql3.ParamByName('service_pac').AsString :=  lblversao.text;
            fdquerysql3.ParamByName('lblchaveinst').AsString := lblchaveinst.text;
            fdquerysql3.ParamByName('codigo_marca').AsString := lblcodmarca.text;
            fdquerysql3.ParamByName('codigoclasse').AsString := inttostr(codigoclasse);
            fdquerysql3.ParamByName('data_ativacao').AsString := datativacao;
            fdquerysql3.ParamByName('codigosoftware').AsString := inttostr(codigosoftware);
            fdquerysql3.ParamByName('lblcodigoest').AsString := lblcodigoest.text;

            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  messagedlg('Operação realizada com sucesso !!!',mtinformation,[mbok],0);
                  spblimpar.Click;
                  mostra_softwaredaestacao(lblcodigoest.text);
                  if parametro = 'INCLUSÃO' then
                     lblcodsoftware.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_satfi_software','Sim');
                  lblcodsoftware.Refresh;
                  lbldescricaosoft.SetFocus;
               end
            else
               begin
                  lbldescricaosoft.setfocus;
                  exit;
               end;
         end
      else
         lbldescricaosoft.setfocus;
   end;
end;

function grava_redes(parametro : string) : string;
begin
   with modulo_dados, frmestacoes do
   begin
      if lblenderecoip.text = '' then
         begin
            messagedlg('O CAMPO ENDEREÇO DE IP É DE PREENCHIMENTO OBRIGATÓRIO !!!',mterror,[mbok],0);
            lblenderecoip.setfocus;
            exit;
         end;
      //
      sql:= 'SELECT ugser.codigo_estacao FROM USER_geoapolo_satfi_estacao_rede ugser with(nolock) WHERE codigo_estacao = '+quotedstr(lblcodigoest.Text);
      sql:=sql+' OR switch = :lblswitch OR porta_switch = :lblportaswitch';
      fdquerysql6.Close;
      fdquerysql6.SQL.Clear;
      fdquerysql6.SQL.Text := sql;
      fdquerysql6.ParamByName('lblswitch').AsString :=lblswitch.Text;
      fdquerysql6.ParamByName('lblportaswitch').AsString :=lblportaswitch.Text;
      if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
         parametro:='ALTERAÇÃO'
      else
         parametro:='INCLUSÃO';
      //
      resp:=messagedlg('Confirma a '+parametro+' para estes dados de rede ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
      if resp = idyes then
         begin
            if parametro = 'INCLUSÃO' then
               begin
                  sql:='INSERT INTO USER_geoapolo_satfi_estacao_rede (codigo_estacao,rack,patchpanel,porta_patchpanel,vlan,switch,porta_switch,enderecoip,codigo_localizacaofisica)';
                  sql:=sql+' VALUES (:lblcodigoest, :lblrack, :lblpatchpanel, :lblportapatch, :lblvlan, :lblswitch, :lblportaswitch, :lblenderecoip, :lbllocalizacaofisica) ';
               end
            else if parametro = 'ALTERAÇÃO' then
               begin
                  sql:='SELECT * FROM USER_geoapolo_satfi_estacao_rede WHERE codigo_estacao = :codigoestacao AND enderecoip = :enderecoip';
                  fdquerysql.Close;
                  fdquerysql.SQL.Clear;
                  fdquerysql.SQL.Text := sql;
                  fdquerysql.ParamByName('codigoestacao').AsString :=lblcodigoest.text;
                  fdquerysql.ParamByName('enderecoip').AsString := lblenderecoip.Text;
                  if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
                     begin
                        sql:='UPDATE USER_geoapolo_satfi_estacao_rede SET rack = :lblrack, patchpanel= :lblpatchpanel';
                        sql:=sql+', porta_patchpanel = :lblportapatchpanel, vlan = :lblvlan, switch = :lblswitch';
                        sql:=sql+', porta_switch = :lblportaswitch, enderecoip = :enderecoip';
                        sql:=sql+', codigo_localizacaofisica = :lbllocalizacaofisica WHERE codigo_estacao = lblcodigoest';
                     end
                  else
                     begin
                        sql:='INSERT INTO USER_geoapolo_satfi_estacao_rede (codigo_estacao,rack,patchpanel,porta_patchpanel,vlan,switch,porta_switch,enderecoip,codigo_localizacaofisica)';
                        sql:=sql+' VALUES (:lblcodigoest, :lblrack, :lblpatchpanel, :lblportapatch, :lblvlan, :lblswitch, :lblportaswitch, :lblenderecoip, :lblcodlocalizacaofisica)';
                     end;
               end;
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('lblcodigoest').AsString := lblcodigoest.Text;
            fdquerysql3.ParamByName('lblrack').AsString := lblrack.text;
            fdquerysql3.ParamByName('lblpatchpanel').AsString :=lblpatchpanel.text;
            fdquerysql3.ParamByName('lblportapatch').AsString := lblportapatch.text;
            fdquerysql3.ParamByName('lblvlan').AsString := lblvlan.text;
            fdquerysql3.ParamByName('lblswitch').AsString := lblswitch.text;
            fdquerysql3.ParamByName('lblportaswitch').AsString := lblportaswitch.text;
            fdquerysql3.ParamByName('lblenderecoip').AsString := lblenderecoip.text;
            fdquerysql3.ParamByName('lbllocalizacaofisica').AsString :=lblcodlocalizacaofisica.text;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  if chkatualizatimetric.Checked then
                     begin
                        sql:='UPDATE geo2_timet_ips SET ip = :lblenderecoip, descricao = :lbldescricao';
                        sql:=sql+' WHERE ip = :ipantigo'+quotedstr(ipantigo);
                        fdquerysql3.Close;
                        fdquerysql3.SQL.Clear;
                        fdquerysql3.SQL.Text := sql;
                        fdquerysql3.ParamByName('lblenderecoip').AsString :=lblenderecoip.text;
                        fdquerysql3.ParamByName('lbldescricao').AsString :=lbldescricao.text;
                        if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                           begin
                           end;
                     end;
                  messagedlg('Operação realizada com Sucesso !!!',mtinformation,[mbok],0);
                  mostraredeestacao(lblcodigoest.Text);
                  spblimpar.click;
                  lblrack.setfocus;
               end
            else
               begin
                  messagedlg('PROBLEMAS AO INSERIR DADOS DE REDE PARA ESTA ESTAÇÃO !!!',mterror,[mbok],0);
                  lblrack.setfocus;
               end;
         end
      else
         begin
            lblrack.setfocus;
            exit;
         end;
   end;
end;

function carrega_combo_departamentos:string;
begin
   with modulo_dados, frmestacoes do
   begin
      //DEPARTAMENTOS
      cbodepartamentos.clear;
      sql:='SELECT nome_departamento FROM USER_geoapolo_departamentos';
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := sql;
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
            fdquerysql.First;
            while not fdquerysql.eof do
            begin
               cbodepartamentos.Items.add(fdquerysql.fieldbyname('nome_departamento').asstring);
               fdquerysql.Next;
            end;
         end
      else
         begin
            messagedlg('TABELA DE DEPARTAMENTOS VAZIA, CADASTRE OS DEPARTAMENTOS !!!',mterror,[mbok],0);
            frmestacoes.Close;
         end;
   end;
end;

function carrega_status(parametro : string) : string;
begin
   with modulo_dados, frmestacoes do
   begin
      sql:='SELECT descricao FROM USER_geoapolo_satfi_status_hardsoft WHERE idhardsoft = :parametro';
      fdquerysql.close;
      fdquerysql.sql.clear;
      fdquerysql.SQL.Text := sql;
      fdquerysql.ParamByName('parametro').AsString := parametro;

      if executaracao(fdquerysql,fdbanco, true, dtsfdquerysql) then
         begin
            if parametro = 'H' then
               begin
                  cbostatush.clear;
                  fdquerysql.First;
                  while not fdquerysql.Eof do
                  begin
                     cbostatush.Items.Add(fdquerysql.fieldbyname('descricao').asstring);
                     fdquerysql.Next;
                  end;
               end
            else if parametro = 'S' then
               begin
                  cbostatus_s.clear;
                  fdquerysql.First;
                  while not fdquerysql.Eof do
                  begin
                     cbostatus_s.Items.Add(fdquerysql.fieldbyname('descricao').asstring);
                     fdquerysql.Next;
                  end;
               end;
         end
      else
         begin
            messagedlg('TABELA DE STATUS DE HARDWARE ESTÁ VAZIA, FAVOR CADASTRAR !!!',mterror,[mbok],0);
            frmestacoes.Close;
         end;
   end;
end;

function carrega_combo_classes(tipo : string) : string;
begin
   with modulo_dados, frmestacoes do
   begin
      if tipo = 'SOFTWARE' then
         begin
            sql:='SELECT sca.descricao';
            sql:=sql+' FROM USER_geoapolo_satfi_classificacaoativo sca with(nolock)';
            sql:=sql+' INNER JOIN  USER_geoapolo_satfi_categorias ugsc with(nolock) ON sca.codigo_categoria = ugsc.codigo_categoria';
            sql:=sql+' WHERE ugsc.descricao = :tipo';
            sql:=sql+' ORDER BY sca.descricao ASC';
            fdquerysql.Close;
            fdquerysql.SQL.Clear;
            fdquerysql.SQL.Text := sql;
            fdquerysql.ParamByName('tipo').AsString := tipo;
            if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
               begin
                  cboclasse.clear;
               end;
         end
      else if tipo = 'HARDWARE' then
         begin
            sql:='SELECT sca.descricao';
            sql:=sql+' FROM USER_geoapolo_satfi_classificacaoativo sca with(nolock)';
            sql:=sql+' INNER JOIN  USER_geoapolo_satfi_categorias ugsc with(nolock) ON sca.codigo_categoria = ugsc.codigo_categoria';
            sql:=sql+' WHERE ugsc.descricao = :tipo';
            sql:=sql+' ORDER BY sca.descricao ASC';
            fdquerysql.Close;
            fdquerysql.SQL.Clear;
            fdquerysql.SQL.Text := sql;
            fdquerysql.ParamByName('tipo').AsString := tipo;
            if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
               begin
                  cboclasseh.clear;
               end;
         end;
      fdquerysql.first;
      while not fdquerysql.Eof do
      begin
         if tipo = 'SOFTWARE' then
            cboclasse.items.add(fdquerysql.fieldbyname('descricao').asstring)
         else if tipo = 'HARDWARE' then
            cboclasseh.items.add(fdquerysql.fieldbyname('descricao').asstring);
         fdquerysql.next;
      end;
   end;
end;

procedure Tfrmestacoes.tabhardwareEnter(Sender: TObject);
begin
   controle2:='INCLUSÃO';
   codigoestacaovelha:=codigoestacao;
   lblcodigohard.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_satfi_hardware','S');
   lblcodigohard.Refresh;
   mostra_hardwaredaestacao(lblcodigoest.text);
   carrega_config('SATFIHARDWARE',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
   configura_grid('SATFIHARDWARE',frmestacoes,frmlogon.nomeusuario,'gridhardware',gridhardware,modulo_dados.dtsfdquerysql5);
   configura_grid('SATFIFICHAHARDWARE',frmestacoes,frmlogon.nomeusuario,'gridfichatecnica',gridfichatecnica,modulo_dados.dtsfdquerysql6);
//   configura_grid('SATFIFICHAHR',frmestacoes,frmlogon.nomeusuario,'griddetalhefichatecnica',griddetalhefichatecnica,modulo_dados.dtsquerysql9);
end;

procedure Tfrmestacoes.cbofornecedoresEnter(Sender: TObject);
begin
   if trim(lbldescricaohard.Text) = '' then
      begin
         messagedlg('NÃO É PERMITIDO CADASTRAR UM HARDWARE SEM UMA DESCRIÇÃO DO MESMO !!!',mterror,[mbok],0);
         lbldescricaohard.SetFocus;
      end;
end;

procedure Tfrmestacoes.cbofornecedoresKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) and (key = vk_return) then
      lblnotafiscal.SetFocus;
end;

procedure Tfrmestacoes.lblnomeusuarioEnter(Sender: TObject);
begin
   with modulo_dados, frmestacoes do
   begin
     if (lblcodigousuario.Text <> '') and (lblnomeusuario.Text = '') then
        begin
          lblnomeusuario.Text := retorna_codigousuario('NOME',lblcodigousuario.Text);
          lblnomeusuario.Refresh;
        end;

   end;
end;

procedure Tfrmestacoes.lblnomeusuarioKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lblentcod.SetFocus;
end;

procedure Tfrmestacoes.lblnotafiscalEnter(Sender: TObject);
begin
   with modulo_dados do
   begin
      sql:='SELECT codigoclasse FROM USER_geoapolo_satfi_classificacaoativo WHERE descricao =:cboclassehardware';
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := sql;
      fdquerysql.ParamByName('cboclassehardware').AsString := cboclasseh.Text;
      if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
         codigoclasse:=fdquerysql.fieldbyname('codigoclasse').asinteger;
   end;
end;

procedure Tfrmestacoes.lblnotafiscalKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      mskvalor.SetFocus;
end;

procedure Tfrmestacoes.mskvalorKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lbltmpgarantia.setfocus;
end;

procedure Tfrmestacoes.mskdtcompraKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      mskdtativacao.SetFocus;
end;

procedure Tfrmestacoes.mskdtativacaoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      cboclasseh.setfocus;
end;

procedure Tfrmestacoes.btnresolveipClick(Sender: TObject);
begin
   lblenderecoip.Text := GetLocalIP;
   lblenderecoip.Refresh;
end;

procedure Tfrmestacoes.cboajusteimagemClick(Sender: TObject);
begin
   if cboajusteimagem.text = 'Ajustar' then
      imgdocumento.Stretch := true;
   if cboajusteimagem.text = 'Não Ajustar' then
      imgdocumento.Stretch :=false;
end;

procedure Tfrmestacoes.cbocategoriaKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_return then
      cbostatush.SetFocus;
end;

procedure Tfrmestacoes.cbostatushKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      spbsalvar.click;
end;

procedure Tfrmestacoes.cboclassehKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lblnotafiscal.setfocus;
end;

procedure Tfrmestacoes.cboclassehEnter(Sender: TObject);
begin
   if mskdtativacao.Text = '  /  /    ' then
      mskdtativacao.Text := datetostr(date);
end;

procedure Tfrmestacoes.memobshardEnter(Sender: TObject);
begin
  with modulo_dados do
   begin
      sql:='SELECT codigo_status FROM USER_geoapolo_satfi_status_hardsoft WHERE descricao =:cbostatush';
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := sql;
      fdquerysql.ParamByName('cbostatush').AsString := cbostatush.Text;

      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         codigostatus:=fdquerysql.fieldbyname('codigo_status').asinteger;
   end;
end;

procedure Tfrmestacoes.memobshardKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_escape then
      begin
         memobshard.Text:=buscatroca(memobshard.Text,':','');
         memobshard.Text:=buscatroca(memobshard.Text,'''','');
         spbsalvar.Click;
      end;
end;

procedure Tfrmestacoes.lblestacaoEnter(Sender: TObject);
begin
   with modulo_dados do
   begin
     { sql:='SELECT * FROM USER_geoapolo_satfi_estacao WHERE codigo_estacao = '+lblcodest.Text+';';
      executaracao(sql,querysql);
      if querysql.RecordCount > 0 then
         begin
            if controle2 <> 'ALTERAÇÃO' then
               begin
                  sql:='SELECT codigo_estacao, descricao FROM USER_geoapolo_satfi_estacao WHERE codigo_estacao = ';
                  executaracao(sql,querysql);
                  if querysql.RecordCount > 0 then
                     begin
                        lbldescricao.Text := querysql.fieldbyname('descricao').asstring;
                        lbldescricaohard.SetFocus;
                     end
                  else
                     begin
                        messagedlg('ESTAÇÃO NÃO ESTÁ CADASTRADA, OU  POSSUI OUTRO CÓDIGO, FAVOR VERIFICAR !!!',mtinformation,[mbok],0);

                     end;
               end
            else if controle2 = 'ALTERAÇÃO' then
               begin
                   resp:=messagedlg('VOCÊ ESTÁ TRANSFERINDO ESTE HARDWARE PARA ESTA ESTAÇÃO ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
                   if resp = idyes then
                      begin
                      end
                   else
                      begin
                      end;
               end;
         end; }
   end;
end;

procedure Tfrmestacoes.mskdtativacaoEnter(Sender: TObject);
begin
   if mskdtcompra.Text <> '  /  /    ' then
      begin
         if not strisdate(mskdtcompra.Text) then
            begin
               messagedlg('FORMATO DE DATA INVÁLIDO !!!',mterror,[mbok],0);
               mskdtcompra.Clear; mskdtcompra.SetFocus;
               exit;
            end;
         //
         if strtodate(mskdtcompra.Text) > date then
            begin
               messagedlg('NÃO É PERMITIDO LANÇAR COMPRAS COM DATAS FUTURAS !!!',mterror,[mbok],0);
               mskdtcompra.Clear; mskdtcompra.SetFocus;
               exit;
            end;
      end;
end;

procedure Tfrmestacoes.lblcodigohardKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lbldescricaohard.SetFocus;
end;

procedure Tfrmestacoes.lblcodigodepartamentoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
  if (key = vk_return) or (key = vk_tab) then
     cbodepartamentos.setfocus;
  if key = VK_F4 then
     spbuscasecao.click;
end;

procedure Tfrmestacoes.lblcodigousuarioEnter(Sender: TObject);
begin
   if cbodepartamentos.text <> '' then
      lblcodigodepartamento.text := retorna_codigodepartamento(cbodepartamentos.text);
end;

function retorna_codigodepartamento(descricao: string) : string;
begin
   with modulo_dados, frmestacoes do
   begin
      sql:='SELECT codigo_departamento FROM USER_geoapolo_departamentos WHERE nome_departamento = :nomedepartamento';
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := sql;
      fdquerysql.ParamByName('nomedepartamento').AsString := descricao;
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         result:= fdquerysql.fieldbyname('codigo_departamento').asstring
      else
         result:='0';
   end;
end;

function retorna_tipolicenca(descricao : string) : string;
begin
 {  with modulo_dados, frmestacoes do
   begin
      sql:='SELECT codigo_tipo_lic FROM USER_geoapolo_satfi_tipo_licenca ugstl with(nolock) ';
      sql:=sql+' WHERE descricao = '+quotedstr(cbotipolic.text)+';';
      executaracao(sql,querysql);
      if querysql.RecordCount > 0 then
         Result:=querysql.fieldbyname('codigo_tipo_lic').Asstring
      else
         result:='0';
   end; }
end;

procedure Tfrmestacoes.lblcodigousuarioKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = VK_F4 then
      spbbuscausuario.click;
   if (key = vk_return) or (key = vk_tab) then
      lblnomeusuario.setfocus;
end;

procedure Tfrmestacoes.lblcodmarcaEnter(Sender: TObject);
begin
   if trim(cbotipolic.Text) = '' then
      begin
         messagedlg('CAMPO OBRIGATÓRIO, INFORME O TIPO DE LICENÇA POR FAVOR !!! ',mterror,[mbok],0);
         cbotipolic.SetFocus;
         exit;
      end
   else
      tipolicenca:=strtoint(retorna_tipolicenca(cbotipolic.text));
   //
end;

procedure Tfrmestacoes.lblcodmarcaKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lblmarca.setfocus;
   if key = VK_F4 then
      spbuscamarca.click;
end;

procedure Tfrmestacoes.spblocateClick(Sender: TObject);
begin
 {  with modulo_dados do
   begin
     sql:='SELECT * FROM USER_geoapolo_satfiview_localizaestacao';
     executaracao(sql,querysql9);
     if querysql9.RecordCount > 0 then
        begin
           application.CreateForm(tfrmconsulta3,frmconsulta3);
           dtsquerysql9.DataSet := querysql9;
           frmconsulta3.gridconsulta.DataSource := dtsquerysql9;
           frmconsulta3.controle:='ESTACAOHARDWARE';
           frmconsulta3.ShowModal;
        end;
   end; }
end;

procedure Tfrmestacoes.dbgestacoesEnter(Sender: TObject);
begin
   if trim(mskdtcadastro.Text) <> '' then
      begin
         if strtodate(mskdtcadastro.Text) > date then
            begin
               messagedlg('NÃO É PERMITIDO LANÇAMENTO DE CADASTRO COM DATA FUTURA !!!',mterror,[mbok],0);
               mskdtcadastro.Clear; mskdtcadastro.SetFocus;
            end;
      end;
end;

procedure Tfrmestacoes.cbofornsoftEnter(Sender: TObject);
begin
   if trim(lbldescricaosoft.Text) = '' then
      begin
         messagedlg('NÃO É PERMITIDO CADASTRAR SOFTWARE SEM DESCRIÇÃO !!!',mterror,[mbok],0);
         lbldescricaosoft.SetFocus;
         exit;
      end;
end;

procedure Tfrmestacoes.cbofornsoftKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_return then
      lblnfsoft.SetFocus;
end;

procedure Tfrmestacoes.lblnfsoftKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      mskvalorsoft.SetFocus;
end;

procedure Tfrmestacoes.mskvalorsoftKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lblversao.setfocus;
end;

procedure Tfrmestacoes.mskdtcomprasoftKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      mskdtativasoft.SetFocus;
end;

procedure Tfrmestacoes.mskdtativasoftEnter(Sender: TObject);
begin
   if mskdtcomprasoft.Text <> '  /  /    ' then
      begin
         if strtodate(mskdtcomprasoft.Text) > date then
            begin
               messagedlg('NÃO É PERMITIDO DATA DE COMPRA MAIOR QUE A DATA DO SISTEMA, FAVOR VERIFICAR !!!',mterror,[mbok],0);
               mskdtcomprasoft.SetFocus;
               exit;
            end;
      end;
end;

procedure Tfrmestacoes.mskdtativasoftKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      cbostatus_s.SetFocus;
end;

procedure Tfrmestacoes.lblmarcaEnter(Sender: TObject);
begin
   if mskdtativasoft.Text <> '  /  /    ' then
      begin
         if strtodate(mskdtativasoft.Text) > date then
            begin
               messagedlg('NÃO É PERMITIDO DATA DE ATIVAÇÃO MAIOR QUE A DATA DO SISTEMA, FAVOR VERIFICAR !!!',mterror,[mbok],0);
               mskdtativasoft.SetFocus;
               exit;
            end;
      end
   else if mskdtativasoft.Text = '  /  /    ' then
      mskdtativasoft.Text := datetostr(date);

end;

procedure Tfrmestacoes.lblmarcaKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      mskdtcomprasoft.SetFocus;
end;

procedure Tfrmestacoes.lblmodeloKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      lblcodigodepartamento.SetFocus;
end;

procedure Tfrmestacoes.lblversaoEnter(Sender: TObject);
begin
  if trim(mskvalorsoft.Text) <> '' then
     mskvalorsoft.Text := buscatroca(mskvalorsoft.Text,',','.')
   else
      mskvalorsoft.Text := '0';

end;

procedure Tfrmestacoes.lblversaoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lblchaveinst.SetFocus;
end;

procedure Tfrmestacoes.lblvlanKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      lblswitch.SetFocus;
end;

procedure Tfrmestacoes.lblchaveinstEnter(Sender: TObject);
begin
   if trim(lblversao.Text) = '' then
      begin
         messagedlg('PARA INFORMAR A VERSÃO VERIFIQUE NOS DOCUMENTOS DO SOFTWARE OU NO MENU AJUDA PARA INFORMAR-SE DO NÚMERO !!!',mtinformation,[mbok],0);
         lblversao.SetFocus;
         exit;
      end;
end;

procedure Tfrmestacoes.lblchaveinstKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      cbotipolic.SetFocus;
end;

procedure Tfrmestacoes.cbotipolicKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      begin
         if cbotipolic.text = 'OPEN' then
            controleopen:='OPEN';
         lblcodmarca.setfocus;
      end;
end;

procedure Tfrmestacoes.cinEnter(Sender: TObject);
begin
   cin.ActivePageIndex:=0;
end;

procedure Tfrmestacoes.cbocatsoftKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_return then
      cbostatus_s.SetFocus;
end;

procedure Tfrmestacoes.cbostatus_sKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      cboclasse.SetFocus;
end;

procedure Tfrmestacoes.cboclasseEnter(Sender: TObject);
begin
   if trim(cbostatus_s.Text) = '' then
      begin
         messagedlg('POR FAVOR DEFINA UM STATUS PARA ESTE SOFTWARE !!!',mtinformation,[mbok],0);
         cbostatus_s.SetFocus;
         exit;
      end
   else
      codigostatus:=strtoint(retorna_statushardsoft(cbostatus_s.Text));
end;

function retorna_statushardsoft(idstatus : string) : string;
begin
{   with modulo_dados, frmestacoes do
   begin
      sql:='SELECT * FROM USER_geoapolo_satfi_status_hardsoft WHERE idhardsoft = '+quotedstr(idstatus);
      executaracao(sql,querysql);
      if querysql.RecordCount > 0 then
         result:=querysql.fieldbyname('codigo_status').asstring
      else
         result:='0';
   end;}
end;

procedure Tfrmestacoes.cboclasseKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      memobs.SetFocus;
end;

procedure Tfrmestacoes.memobsKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_escape then
      spbsalvar.Click;
end;

procedure Tfrmestacoes.mnugravaconfiguracoesClick(Sender: TObject);
begin
   if cin.ActivePageIndex = 0 then
      begin
         grava_configuracoes_grids(frmestacoes,'SATFIESTACOES',gridestacoes,'gridestacoes',frmlogon.nomeusuario,modulo_dados.dtsfdquerysql4);
         grava_config_telabusca('SATFIESTACOES',cbocampo.Text,cbordem.Text,'A',frmestacoes);
      end
   else if cin.ActivePageIndex = 1 then
      begin
         grava_configuracoes_grids(frmestacoes,'SATFIHARDWARE',gridhardware,'gridhardware',frmlogon.nomeusuario,modulo_dados.dtsfdquerysql5);
         grava_configuracoes_grids(frmestacoes,'SATFIFICHAHARDWARE',gridfichatecnica,'gridfichatecnica',frmlogon.nomeusuario,modulo_dados.dtsfdquerysql6);
         grava_config_telabusca('SATFIHARDWARE',cbocampo.Text,cbordem.Text,'A',frmestacoes);
      end
   else if cin.ActivePageIndex = 2 then
      begin
         grava_configuracoes_grids(frmestacoes,'SATFISOFTWARE',gridsoftware,'gridsoftware',frmlogon.nomeusuario,modulo_dados.dtsfdquerysql7);
         grava_config_telabusca('SATFISOFTWARE',cbocampo.Text,cbordem.Text,'A',frmestacoes);
      end
   else if cin.ActivePageIndex = 3 then
      begin
         grava_configuracoes_grids(frmestacoes,'SATFIREDES',gridredes,'gridredes',frmlogon.nomeusuario,modulo_dados.dtsfdquerysql8);
         grava_config_telabusca('SATFIREDES',cbocampo.Text,cbordem.Text,'A',frmestacoes);
      end
   else if cin.ActivePageIndex = 4 then
      begin
         grava_configuracoes_grids(frmestacoes,'SATFIDOCESTACAO',griddocumentacao,'griddocumentacao',frmlogon.nomeusuario,modulo_dados.dtsfdquerysql9);
         grava_config_telabusca('SATFIDOCESTACAO',cbocampo.Text,cbordem.Text,'A',frmestacoes);
      end;
end;

procedure Tfrmestacoes.memobsEnter(Sender: TObject);
begin
   if trim(cboclasse.Text) = '' then
      begin
         messagedlg('VOCÊ NÃO CLASSIFICOU ESTE SOFTWARE, PODERIA FAZÊ-LO POR FAVOR !!!',mtinformation,[mbok],0);
         cboclasse.SetFocus;
         exit;
      end;
   codigoclasse:=strtoint(retorna_codigoclasse(cboclasse.text));
end;

function retorna_codigoclasse(parametro : string) : string;
begin
{   with modulo_dados, frmestacoes do
   begin
      sql:='SELECT codigoclasse FROM USER_geoapolo_satfi_classificacaoativo WHERE descricao = '+quotedstr(parametro);
      executaracao(sql,querysql);
      if querysql.RecordCount > 0 then
         result:=querysql.fieldbyname('codigoclasse').asstring
      else
         result:='0';
   end;}
end;

function retorna_nomeentidade(parametro : string) : string;
begin
{   with modulo_dados, frmestacoes do
   begin
      sql:='SELECT geoentnome FROM USER_geoapolo_entidade WHERE geoentcod = '+quotedstr(parametro);
      executaracao(sql,querysql);
      if querysql.RecordCount > 0 then
         result:=querysql.fieldbyname('geoentnome').asstring
      else
         result:='';
   end;}
end;

function retorna_descricaolocalizacaofisica(parametro : string) : string;
begin
{   with modulo_dados, frmestacoes do
   begin
      sql:='SELECT localizacao FROM USER_geoapolo_satfi_localizacao_fisica WHERE codigo_localizacao = '+quotedstr(parametro);
      executaracao(sql,querysql);
      if querysql.RecordCount > 0 then
         result:=querysql.fieldbyname('localizacao').asstring
      else
         result:='';
   end;}
end;

procedure Tfrmestacoes.memobservacoesEnter(Sender: TObject);
begin
   if (lblnomeusuario.text <> '') and ((lblcodigousuario.text = '0') or (lblcodigousuario.text = '')) then
      lblcodigousuario.text := retorna_codigousuario('CÓDIGO',lblnomeusuario.text);
   //
   lblcodigousuario.refresh;
end;

procedure Tfrmestacoes.memobservacoesKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_escape) then
      spbsalvar.Click;
end;

procedure Tfrmestacoes.gridsoftwareCellClick(Column: TColumn);
begin
//   mostra_fichatecnica_software(modulo_dados.querysql7.fieldbyname('codigo_software').asstring, modulo_dados.querysql7.fieldbyname('codigo_estacao').asstring);
end;

procedure Tfrmestacoes.gridsoftwareDblClick(Sender: TObject);
var
   dataativacao,datacompra:string;
begin
   with modulo_dados do
   begin
      lblcodsoftware.text := fdquerysql7.fieldbyname('codigo_software').asstring;
      codigosoftware:=strtoint(lblcodsoftware.text);
      lbldescricaosoft.text := fdquerysql7.fieldbyname('descricao').asstring;
      lblentcodsoft.text := fdquerysql7.fieldbyname('entcod').asstring;
      edtnomefornecedor.text := fdquerysql7.fieldbyname('geoentnome').asstring;
      lblnfsoft.text := fdquerysql7.fieldbyname('nf').asstring;
      mskvalorsoft.text := formatfloat('###,###,##0.00',fdquerysql7.fieldbyname('valor').asfloat);
      lblversao.text := fdquerysql7.fieldbyname('service_pack').asstring;
      lblchaveinst.text := fdquerysql7.fieldbyname('chave_produto').asstring;
      buscanacombo(fdquerysql7.fieldbyname('tipo_licenca').asstring,frmestacoes,cbotipolic);
      lblcodmarca.text := fdquerysql7.fieldbyname('codigo_marca').asstring;
      lblmarca.text := fdquerysql7.fieldbyname('descricao_marca').asstring;
      //mskdtcompra.EditMask := '';
      datacompra:=   fdquerysql7.fieldbyname('data_compra').asstring;
      mskdtcompra.text := copy(datacompra,9,2)+'/'+copy(datacompra,6,2)+'/'+copy(datacompra,1,4);
      mskdtcompra.Refresh;
      //mskdtcompra.Text :=   copy(mskdtcompra.Text,9,2)+'/'+copy(mskdtcompra.Text,6,2)+'/'+copy(mskdtcompra.Text,1,4);
      //mskdtativasoft.EditMask := '';
      dataativacao:=  fdquerysql7.fieldbyname('data_ativacao').AsString;
      mskdtativasoft.text :=  copy(dataativacao,9,2)+'/'+copy(dataativacao,6,2)+'/'+copy(dataativacao,1,4);
      mskdtativasoft.Refresh;
      //mskdtativasoft.Text := copy(mskdtativasoft.Text,9,2)+'/'+copy(mskdtativasoft.Text,6,2)+'/'+copy(mskdtativasoft.Text,1,4);
      mskdtativasoft.Refresh;
      buscanacombo(fdquerysql7.fieldbyname('status').asstring,frmestacoes,cbostatus_s);
      buscanacombo(fdquerysql7.fieldbyname('classe').asstring,frmestacoes,cboclasse);
      lbldescricaosoft.setfocus;
      controle:='ALTERAÇÃO';
   end;
end;

procedure Tfrmestacoes.gridsoftwareDrawColumnCell(Sender: TObject;
  const Rect: TRect; DataCol: Integer; Column: TColumn; State: TGridDrawState);
var
  displaytext :string;
begin
  if Column.Field is TMemoField then
  begin
    // Limitar o texto exibido
    DisplayText := Copy(Column.Field.AsString, 1, 50) + '...';
    // Desenha o texto no grid
    gridsoftware.Canvas.FillRect(Rect);
    gridsoftware.Canvas.TextRect(Rect, Rect.Left + 2, Rect.Top + 2, DisplayText);
  end;
end;

procedure Tfrmestacoes.gridsoftwareKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   with modulo_dados do
   begin
      if key = vk_delete then
         begin
            resp:=messagedlg('Confirma a Exclusão deste Software para esta Estação ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
            if resp = idyes then
               begin
                  sql:='DELETE FROM USER_geoapolo_satfi_software WHERE codigo_software = :codigosoftware';
                  sql:=sql+' AND codigo_estacao = :lblcodigoest';
                  fdquerysql3.Close;
                  fdquerysql3.SQL.Clear;
                  fdquerysql3.SQL.Text := sql;
                  fdquerysql3.ParamByName('codigosoftware').AsString := fdquerysql7.fieldbyname('codigo_software').asstring ;
                  fdquerysql3.ParamByName('codigo_estacao').AsString := lblcodigoest.Text;

                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                     begin
                        messagedlg('SOFTWARE EXCLUÍDO COM SUCESSO !!!',mtinformation,[mbok],0);
                        mostra_softwaredaestacao(lblcodigoest.text);
                        spblimpar.Click;
                     end
                  else
                     begin
                        messagedlg('OCORREU ERRO AO TENTAR EXCLUIR ESTE SOFTWARE, VERIFIQUE INTEGRIDADE DOS DADOS !!!',mterror,[mbok],0);
                        exit;
                     end;
               end
            else
               begin
                  lbldescricaosoft.SetFocus;
                  exit;
               end;
         end;
   end;
end;

procedure Tfrmestacoes.GroupBox5Enter(Sender: TObject);
begin
   mostraredeestacao(lblcodigoest.text);
end;

procedure Tfrmestacoes.mskdtcomprasoftEnter(Sender: TObject);
begin
   if trim(mskvalorsoft.Text) <> '' then
      mskvalorsoft.Text := buscatroca(mskvalorsoft.Text,',','.')
   else
      mskvalorsoft.Text := '0';
end;

procedure Tfrmestacoes.gridhardwareCellClick(Column: TColumn);
begin
   if modulo_dados.fdquerysql5.fieldbyname('codigo_hardware').asstring <> '' then
      mostra_fichatecnicahardware(modulo_dados.fdquerysql5.fieldbyname('codigo_hardware').asstring);
   if modulo_dados.fdquerysql6.fieldbyname('codigo_hardware').asstring <> '' then
      mostra_detalhefichatecnica(modulo_dados.fdquerysql6.fieldbyname('codigo_hardware').asstring,lblcodigoest.text);
end;

procedure Tfrmestacoes.gridhardwareDblClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      lblcodigohard.Text := fdquerysql5.fieldbyname('codigo_hardware').AsString;
      lbldescricaohard.Text := fdquerysql5.fieldbyname('descricao').asstring;
      mskdtcompra.Text := fdquerysql5.fieldbyname('data_compra').asstring;
      mskdtativacao.Text := fdquerysql5.fieldbyname('data_ativacao').asstring;
      buscanacombo(fdquerysql5.fieldbyname('classificacao').asstring,frmestacoes,cboclasseh);
      lblnotafiscal.Text := fdquerysql5.fieldbyname('nf').asstring;
      mskvalor.Text := fdquerysql5.fieldbyname('valor').asstring;
      lbltmpgarantia.Text := fdquerysql5.fieldbyname('tempo_garantia').asstring;
      buscanacombo(uppercase(fdquerysql5.fieldbyname('status_hardware').asstring),frmestacoes,cbostatush);
      codigostatus:=fdquerysql5.fieldbyname('codigo_status_h').asinteger;
      memobshard.Lines.Add(fdquerysql5.fieldbyname('observacoes').asstring);
      //lblmodelo.Text := querysql5.fieldbyname('modelo').asstring;
      //lblnumserie.Text := querysql5.fieldbyname('numero_serie').asstring;
      codigoclasse:=fdquerysql5.fieldbyname('codigoclasse').asinteger;
      controle2:='ALTERAÇÃO';
   end;
end;

procedure Tfrmestacoes.gridhardwareDrawColumnCell(Sender: TObject;
  const Rect: TRect; DataCol: Integer; Column: TColumn; State: TGridDrawState);
var
  displaytext :string;
begin
  if Column.Field is TMemoField then
  begin
    // Limitar o texto exibido
    DisplayText := Copy(Column.Field.AsString, 1, 50) + '...';
    // Desenha o texto no grid
    gridhardware.Canvas.FillRect(Rect);
    gridhardware.Canvas.TextRect(Rect, Rect.Left + 2, Rect.Top + 2, DisplayText);
  end;
end;

procedure Tfrmestacoes.gridhardwareKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   with modulo_dados do
   begin
      if key = vk_delete then
         begin
            if trim(lblcodigohard.Text) = '' then
               begin
                  messagedlg('PARA EXCLUIR UM HARDWARE, PRIMEIRO DÊ UM DUPLO CLICK PARA SELECIONÁ-LO !!!',mtinformation,[mbok],0);
                  gridhardware.SetFocus;
                  exit;
               end
            else
               begin
                  resp:=messagedlg('Confirma a Exclusão deste Hardware e sua respectiva ficha técnica ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
                  if resp = idyes then
                     begin
                        sql:='DELETE FROM USER_geoapolo_satfi_hardware_fichatecnica WHERE codigo_hardware = :codigohardware';
                        fdquerysql3.Close;
                        fdquerysql3.SQL.Clear;
                        fdquerysql3.SQL.Text := sql;
                        fdquerysql3.ParamByName('codigohardware').AsString:= fdquerysql5.FieldByName('codigo_hardware').AsString;
                        if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                           begin
                              sql:='DELETE FROM USER_geoapolo_satfi_hardware WHERE codigo_hardware = :codigohardware';
                              fdquerysql3.Close;
                              fdquerysql3.SQL.Clear;
                              fdquerysql3.SQL.Text := fdquerysql5.fieldbyname('codigo_hardware').asstring;
                              if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                                 begin
                                    messagedlg('Operação executada com Sucesso !!!',mtinformation,[mbok],0);
                                    mostra_hardwaredaestacao(lblcodigoest.text);
                                    spblimpar.Click;
                                 end
                              else
                                 begin
                                    lblcodigohard.SetFocus;
                                    exit;
                                 end;
                           end
                        else
                           begin
                             messagedlg('PROBLEMAS AO EXCLUIR A FICHA TÉCNICA DESTE HARDWARE !!!',mterror,[mbok],0);
                             lbldescricaohard.SetFocus;
                           end;
                     end
                  else
                     begin
                        gridhardware.SetFocus;
                        exit;
                     end;
               end;
         end;
   end;
end;

procedure Tfrmestacoes.gridredesDblClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      controle:='ALTERAÇÃO';
      lblrack.Text := fdquerysql8.FieldByName('rack').AsString;
      lblpatchpanel.Text := fdquerysql8.FieldByName('patchpanel').AsString;
      lblenderecoip.Text := fdquerysql8.FieldByName('enderecoip').AsString;
      lbllocalizacao.Text := fdquerysql8.FieldByName('localizacao').AsString;
      tblconfigrede.Refresh;
      lblrack.SetFocus;
   end;
end;

procedure Tfrmestacoes.gridredesDrawColumnCell(Sender: TObject;
  const Rect: TRect; DataCol: Integer; Column: TColumn; State: TGridDrawState);
var
  displaytext :string;
begin
  if Column.Field is TMemoField then
  begin
    // Limitar o texto exibido
    DisplayText := Copy(Column.Field.AsString, 1, 50) + '...';
    // Desenha o texto no grid
    gridredes.Canvas.FillRect(Rect);
    gridredes.Canvas.TextRect(Rect, Rect.Left + 2, Rect.Top + 2, DisplayText);
  end;
end;

procedure Tfrmestacoes.gridredesKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   with modulo_dados do
   begin
     if key = vk_delete then
        begin
          resp:=messagedlg('Confirma a Exclusão desta configuração de rede ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
          if resp = idyes  then
             begin
                sql:='DELETE FROM USER_geoapolo_satfi_estacao_rede WHERE codigo_estacao = :codigoestacao';
                sql:=sql+' AND rack = :rack ';
                sql:=sql+' AND enderecoip = :enderecoip';
                fdquerysql3.Close;
                fdquerysql3.SQL.Clear;
                fdquerysql3.SQL.Text := sql;
                fdquerysql3.ParamByName('codigoestacao').AsString := lblcodigoest.Text;
                fdquerysql3.ParamByName('rack').AsString := fdquerysql8.FieldByName('rack').AsString;
                fdquerysql3.parambyname('enderecoip').asstring := fdquerysql8.FieldByName('enderecoip').AsString;
                if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                   begin
                     messagedlg('Configuração Removida com sucesso !!!',mtinformation,[mbok],0);
                     mostraredeestacao(lblcodigoest.Text);
                     lblrack.SetFocus;
                   end;
             end
          else
             mostraredeestacao(lblcodigoest.Text);
        end;
   end;
end;

procedure Tfrmestacoes.griddocumentacaoDblClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      lblarquivo.text := fdquerysql10.fieldbyname('caminho_arquivo').asstring;
      if not FileExists(fdquerysql10.fieldbyname('caminho_arquivo').asstring) then
         begin
            resp:=messagedlg('Documento não foi encontrado, deseja remover registro ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
            if resp = idyes then
               begin
                  sql:='DELETE FROM USER_geoapolo_satfi_estacoes_documentacao WHERE codigo_estacao = :codigoestacao';
                  sql:=sql+' AND caminho_arquivo = :caminhodoarquivo';
                  fdquerysql3.Close;
                  fdquerysql3.SQL.Clear;
                  fdquerysql3.SQL.Text := sql;
                  fdquerysql3.parambyname('codigoestacao').AsString := fdquerysql10.fieldbyname('codigo_estacao').asstring;
                  fdquerysql3.ParamByName('caminhodoarquivo').AsString := fdquerysql10.fieldbyname('caminho_arquivo').asstring;

                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                     begin
                        messagedlg('DOCUMENTO REMOVIDO COM SUCESSO !!!',mtinformation,[mbok],0);
                        mostra_documentacao(lblcodigoest.text);
                        lblarquivo.setfocus;
                     end;
               end;
            exit;
         end
      else
         imgdocumento.picture.loadfromfile(modulo_dados.fdquerysql10.fieldbyname('caminho_arquivo').asstring);
      lblarquivo.refresh; imgdocumento.Refresh;
   end;
end;

procedure Tfrmestacoes.griddocumentacaoDrawColumnCell(Sender: TObject;
  const Rect: TRect; DataCol: Integer; Column: TColumn; State: TGridDrawState);
var
  displaytext :string;
begin
  if Column.Field is TMemoField then
  begin
    // Limitar o texto exibido
    DisplayText := Copy(Column.Field.AsString, 1, 50) + '...';
    // Desenha o texto no grid
    griddocumentacao.Canvas.FillRect(Rect);
    griddocumentacao.Canvas.TextRect(Rect, Rect.Left + 2, Rect.Top + 2, DisplayText);
  end;
end;

procedure Tfrmestacoes.griddocumentacaoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   with modulo_dados do
   begin
      if key = VK_DELETE then
         begin
            resp:=messagedlg('Confirma a remoção deste documento ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
            if resp = idyes  then
               begin
                  deletefile(fdquerysql10.fieldbyname('caminho_arquivo').asstring);
                  if not FileExists(fdquerysql10.fieldbyname('caminho_arquivo').asstring) then
                     begin
                        sql:='DELETE FROM USER_geoapolo_satfi_estacoes_documentacao WHERE codigo_estacao = :codigoestacao ';
                        sql:=sql+' AND caminho_arquivo = :caminhodoarquivo';
                        fdquerysql3.Close;
                        fdquerysql3.sql.clear;
                        fdquerysql3.sql.Text := sql;
                        fdquerysql3.parambyname('codigoestacao').asstring :=fdquerysql10.fieldbyname('codigo_estacao').asstring;
                        fdquerysql3.parambyname('caminhodoarquivo').asstring := fdquerysql10.fieldbyname('caminho_arquivo').asstring;
                        if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                           begin
                              messagedlg('DOCUMENTO REMOVIDO COM SUCESSO !!!',mtinformation,[mbok],0);
                              mostra_documentacao(lblcodigoest.text);
                              lblarquivo.setfocus;
                           end;
                     end
                  else
                     begin
                        messagedlg('PROBLEMAS AO TENTAR REMOVER O DOCUMENTO !!!',mterror,[mbok],0);
                        lblarquivo.setfocus;
                        exit;
                     end;
               end
            else
               begin
                  lblarquivo.setfocus;
               end;
         end;
   end;
end;

procedure Tfrmestacoes.gridestacoesDblClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      controle:='ALTERAÇÃO';
      lblcodigoest.text := fdquerysql4.fieldbyname('codigo_estacao').asstring;
      lbldescricao.text := fdquerysql4.fieldbyname('estacao').asstring;
      lblservicetag.text := fdquerysql4.fieldbyname('tag_servico').asstring;
      lblmodelo.text := fdquerysql4.fieldbyname('modelo_estacao').asstring;
      lblcodigodepartamento.text := fdquerysql4.fieldbyname('codigo_departamento').asstring;
      buscanacombo(fdquerysql4.fieldbyname('nome_departamento').asstring,frmestacoes,cbodepartamentos);
      mskdtcadastro.text:= formatdatetime('dd/mm/yyyy', fdquerysql4.FieldByName('data_cadastro').Asdatetime);
      lblcodigousuario.text := fdquerysql4.FieldByName('codigo_usuario').Text;
      lblnomeusuario.text := fdquerysql4.fieldbyname('usuario_responsavel').asstring;
      lblentcod.text := fdquerysql4.fieldbyname('geoentcod').asstring;
      edtentnome.text := fdquerysql4.fieldbyname('fornecedor').asstring;
      lblenderecoip.text := fdquerysql4.fieldbyname('enderecoip').asstring;
      ipantigo:=lblenderecoip.text; estacao:=lbldescricao.text;
      lbllocalizacao.text := fdquerysql4.fieldbyname('codigo_localizacao').asstring;
      edtlocalizacao.text := fdquerysql4.fieldbyname('localizacao').asstring;
      memobservacoes.clear;
      memobservacoes.lines.add(fdquerysql4.fieldbyname('info_compl').asstring);
      {mostra_hardwaredaestacao(lblcodigoest.text);
      mostraredeestacao(lblcodigoest.Text);
      mostra_softwaredaestacao(lblcodigoest.Text);
      mostra_documentacao(lblcodigoest.text);}
      lblcodigoest.SetFocus;
      memobservacoes.refresh;
   end;
end;

procedure Tfrmestacoes.gridestacoesDrawColumnCell(Sender: TObject;
  const Rect: TRect; DataCol: Integer; Column: TColumn; State: TGridDrawState);
var
  displaytext :string;
begin
  if Column.Field is TMemoField then
  begin
    // Limitar o texto exibido
    DisplayText := Copy(Column.Field.AsString, 1, 50) + '...';
    // Desenha o texto no grid
    gridestacoes.Canvas.FillRect(Rect);
    gridestacoes.Canvas.TextRect(Rect, Rect.Left + 2, Rect.Top + 2, DisplayText);
  end;

end;

function retorna_codigousuario(parametro: string; login : string) : string;
begin
   with frmestacoes, modulo_dados do
   begin
      if parametro = 'CÓDIGO' then
         begin
            sql:='SELECT codigo_usuario FROM USER_geoapolo_usuarios ugu with(nolock) ';
            sql:=sql+' WHERE ugu.login = '+quotedstr(login);
            sql:=sql+' AND ugu.flagativo = '+quotedstr('A');
         end
      else if parametro = 'NOME' then
         begin
             sql:='SELECT nome_completo FROM USER_geoapolo_usuarios WHERE codigo_usuario = :codigousuario  AND flagativo = :flagativo';
         end;
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := sql;
      fdquerysql.ParamByName('codigousuario').AsString := login;
      fdquerysql.ParamByName('flagativo').AsString := 'A';
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
           if parametro = 'CÓDIGO' then
              begin
                 result:=fdquerysql.fieldbyname('codigo_usuario').asstring
              end
           else if parametro = 'NOME' then
              begin
                result:=fdquerysql.FieldByName('nome_completo').AsString;
              end;
         end
      else
         result:='0';
   end;
end;

procedure Tfrmestacoes.gridestacoesKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   with modulo_dados do
   begin
      if key = vk_delete then
         begin
            messagedlg('LEMBRE-SE QUE PARA EXCLUIR UMA ESTAÇÃO, ELA NÃO PODERÁ TER NENHUM HARDWARE OU SOFTWARE ASSOCIADO !!!',mtwarning,[mbok],0);
            resp:=messagedlg('Confirma a Exclusão desta estação ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
            if resp = idyes then
               begin
                  sql:='SELECT codigo_estacao FROM USER_geoapolo_satfi_hardware ';
                  sql:=sql+' WHERE codigo_estacao = :codigoestacao';
                  fdquerysql.Close;
                  fdquerysql.SQL.Clear;
                  fdquerysql.SQL.Text := sql;
                  fdquerysql.ParamByName('codigoestacao').AsString := lblcodigoest.Text;
                  if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
                     begin
                        messagedlg('ESTA ESTAÇÃO POSSUI HARDWARE VINCULADO A ELA, EXCLUSÃO IMPOSSÍVEL !!!',mtinformation,[mbok],0);
                        lbldescricao.SetFocus;
                        exit;
                     end
                  else
                     begin
                        sql:='SELECT codigo_estacao FROM USER_geoapolo_satfi_software ';
                        sql:=sql+' WHERE codigo_estacao = :codigoestacao';
                        fdquerysql.Close;
                        fdquerysql.SQL.Clear;
                        fdquerysql.SQL.Text := sql;
                        fdquerysql.ParamByName('codigoestacao').AsString := lblcodigoest.Text;
                        if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
                           begin
                              messagedlg('ESTA ESTAÇÃO POSSUI HARDWARE VINCULADO A ELA, EXCLUSÃO IMPOSSÍVEL !!!',mtinformation,[mbok],0);
                              lbldescricao.SetFocus;
                              exit;
                           end
                        else
                           begin
                               sql:='DELETE FROM USER_geoapolo_satfi_estacao ';
                               sql:=sql+' WHERE codigo_estacao = :codigoestacao';
                               fdquerysql3.Close;
                               fdquerysql3.SQL.Clear;
                               fdquerysql3.SQL.Text := sql;
                               fdquerysql3.ParamByName('codigoestacao').AsString := lblcodigoest.Text;
                               if executaracao(fdquerysql3,fdbanco, true, dtsfdquerysql3) then
                                  begin
                                     messagedlg('ESTAÇÃO EXCLUÍDA COM SUCESSO !!!',mtinformation,[mbok],0);
                                     spblimpar.click;
                                     exit;
                                  end
                               else
                                  begin
                                     messagedlg('PROBLEMAS AO TENTAR EXCLUIR ESTA ESTAÇÃO !!!',mterror,[mbok],0);
                                     lbldescricao.SetFocus;
                                     exit;
                                  end;
                           end;
                     end;
               end
            else
               begin
                  lbldescricao.SetFocus;
                  exit;
               end;
         end;
   end;
end;

procedure Tfrmestacoes.gridfichatecnicaDblClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      pnlfichatecnicahardware.Visible := true;
      pnlfichatecnicahardware.Top:= 74;
      pnlfichatecnicahardware.left:=193;
      lblidfichatecnica.Text:= fdquerysql6.FieldByName('idfichatecnica').AsString;
      lblidentificacao.text := fdquerysql6.FieldByName('identificacao').AsString;
      lblconteudo.text:= fdquerysql6.FieldByName('conteudo').AsString;
      memoobsdetalhefichatech.Lines.text := fdquerysql6.FieldByName('observacoes').Text;
   end;
end;

procedure Tfrmestacoes.gridfichatecnicaDrawColumnCell(Sender: TObject;
  const Rect: TRect; DataCol: Integer; Column: TColumn; State: TGridDrawState);
var
  displaytext :string;
begin
  if Column.Field is TMemoField then
  begin
    // Limitar o texto exibido
    DisplayText := Copy(Column.Field.AsString, 1, 50) + '...';
    // Desenha o texto no grid
    gridfichatecnica.Canvas.FillRect(Rect);
    gridfichatecnica.Canvas.TextRect(Rect, Rect.Left + 2, Rect.Top + 2, DisplayText);
  end;
end;

procedure Tfrmestacoes.gridfichatecnicaKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   with modulo_dados do
   begin
     if key = vk_delete then
        begin
           resp:=messagedlg('Confirma a Remoção deste Item da Ficha Técnica de Hardware ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
           if resp = idyes then
              begin
                 sql:='DELETE FROM USER_geoapolo_satfi_hardware_fichatecnica WHERE  idfichatecnica = :idfichatecnica ';
                 sql:=sql+' AND codigo_hardware = :codigohardware';
                 fdquerysql3.close;
                 fdquerysql3.sql.Clear;
                 fdquerysql3.sql.Text := sql;
                 fdquerysql3.parambyname('idfichatecnica').asstring:= fdquerysql6.FieldByName('idfichatecnica').AsString;
                 fdquerysql3.parambyname('codigohardware').asstring :=fdquerysql6.FieldByName('codigo_hardware').AsString;
                 if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                    begin
                      mostra_fichatecnicahardware(fdquerysql5.FieldByName('codigo_hardware').AsString);
                      gridfichatecnica.Refresh;
                    end;
              end
           else
              gridfichatecnica.SetFocus;
        end;
   end;
end;

procedure Tfrmestacoes.tabdocumentacaoEnter(Sender: TObject);
begin
 {  carrega_config('SATFIDOCESTACAO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
   configura_grid('SATFIDOCESTACAO',frmestacoes,frmlogon.nomeusuario,'griddocumentacao',griddocumentacao,modulo_dados.dtsquerysql10);
   lblarquivo.SetFocus; }
end;

procedure Tfrmestacoes.tabestacoesEnter(Sender: TObject);
begin
   if (lblprocurarpor.text <> '') and (lblprocurarpor.text <> null) then
      mostra_estacoes('ESPECIFICA')
   else
      mostra_estacoes('');

   lbldescricao.SetFocus;
end;

procedure Tfrmestacoes.lbldescricaohardKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      mskdtcompra.setfocus;
end;

procedure Tfrmestacoes.spbfindestClick(Sender: TObject);
begin
   with modulo_dados do
   begin
     sql:='SELECT * FROM USER_geoapolo_satfiview_localizaestacao';
     if executaracao(fdquerysql4,fdbanco, true, dtsfdquerysql4) then
        begin
           application.CreateForm(tfrmconsulta3,frmconsulta3);
           dtsfdquerysql4.DataSet := fdquerysql4;
           frmconsulta3.gridCONSULTA.DataSource := dtsfdquerysql4;
           frmconsulta3.controle:='ESTAÇÃOSOFTWARE';
           frmconsulta3.ShowModal;
        end;
   end;
end;

procedure Tfrmestacoes.spbgravatela1Click(Sender: TObject);
begin
{   with modulo_dados do
   begin
     resp:=messagedlg('Confirma a alteração desta ficha técnica do hardware ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
     if resp = idyes then
        begin
           sql:='UPDATE USER_geoapolo_satfi_hardware_fichatecnica SET identificacao = '+quotedstr(lblidentificacao.Text);
           sql:=sql+', conteudo = '+quotedstr(lblconteudo.Text)+', observacoes = '+quotedstr(memoobsdetalhefichatech.Text);
           sql:=sql+' WHERE codigo_hardware = '+quotedstr(lblcodigohard.Text);
           sql:=sql+' AND idfichatecnica = '+quotedstr(lblidfichatecnica.Text);
           executaracao(sql,querysql3);
           if querysql3.RowsAffected > 0 then
              begin
                 pnlfichatecnicahardware.Left:=-1;
                 pnlfichatecnicahardware.Visible :=false;
                 gridhardware.SetFocus;
              end;
        end
     else
        begin
           pnlfichatecnicahardware.Left:=-1;
           pnlfichatecnicahardware.Visible :=false;
           gridhardware.SetFocus;
        end;
   end;    }
end;

procedure Tfrmestacoes.dbgconsultaDblClick(Sender: TObject);
begin
 {  with modulo_dados do
   begin
      lblcodigoest.Text := querysql4.fieldbyname('codigo_estacao').asstring;
      lbldescricao.Text := querysql4.fieldbyname('descricao').asstring;
      lblcodigoest.Refresh; lbldescricao.Refresh; lbldescricaosoft.Refresh;
      cin.ActivePageIndex := 0;
      cbodepartamentos.SetFocus;
      controle2:='ALTERAÇÃO';
   end;    }
end;

procedure Tfrmestacoes.spbabreosClick(Sender: TObject);
begin
   messagedlg('PARA LOCALIZAR ALGUM ITEM DESTA OPÇÃO CONSULTE OS GRIDS ABAIXO !!!',mtinformation,[mbok],0);
end;

procedure Tfrmestacoes.spbsalvadocumentoClick(Sender: TObject);
var
   arquivo:string;
begin
   with modulo_dados do
   begin
      if lblcodigoest.text = '' then
         begin
            messagedlg('É OBRIGATÓRIO INFORMAR PARA QUAL ESTAÇÃO DESEJA INSERIR O DOCUMENTO ',mterror,[mbok],0);
            lblarquivo.setfocus;
         end;
      resp:=messagedlg('Confirma a Inserção deste documento para a estação selecionada ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
      if resp = idyes then
         begin
            if lblnumdoc.text = '' then
               arquivo:=pasta+'\EST-'+lblcodigoest.text+'-'+lbldescricao.Text+'\DOC-'+geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_satfi_estacoes_documentacao','S')+ExtractFileExt(lblarquivo.text)
            else
               arquivo:=pasta+'\EST-'+lblcodigoest.text+'-'+lbldescricao.Text+'\DOC-'+lblnumdoc.Text+ExtractFileExt(lblarquivo.text);
            //
            if not DirectoryExists(pasta+'\EST-'+lblcodigoest.text+'-'+lbldescricao.Text) then
               begin
                  ForceDirectories(pasta+'\EST-'+lblcodigoest.text+'-'+lbldescricao.Text);
               end;
            if ExtractFileExt(lblarquivo.text) = '.jpg' then
               begin
                  imgdocumento.picture.SaveToFile(arquivo);
               end
            else
               begin
                  copyfile(StrToPChar(lblarquivo.Text),strtopchar(arquivo),true);
               end;
            //
            if not FileExists(arquivo) then
              begin
                 messagedlg('O ARQUIVO NÃO FOI SALVO',mterror,[mbok],0);
                 exit;
              end
            else
               begin
                {  sql:='INSERT INTO USER_geoapolo_satfi_estacoes_documentacao(codigo_estacao,caminho_arquivo)';
                  sql:=sql+' VALUES ('+quotedstr(lblcodigoest.text)+', '+quotedstr(arquivo)+')';
                  executaracao(sql,querysql3);
                  if querysql3.RowsAffected > 0 then
                     begin
                        lblarquivo.clear; lblnumdoc.clear;
                        imgdocumento.picture:=nil;
                        mostra_documentacao(lblcodigoest.text);
                     end; }
               end;
         end
      else
         lblarquivo.setfocus;
   end;
end;

function mostra_documentacao(codigo_estacao : string) : string;
begin
 {  with frmestacoes,modulo_dados do
   begin
      sql:='SELECT sed.codigo_estacao, se.descricao, sed.caminho_arquivo';
      sql:=sql+' FROM USER_geoapolo_satfi_estacao se ';
      sql:=sql+' INNER JOIN USER_geoapolo_satfi_estacoes_documentacao sed ON se.codigo_estacao = sed.codigo_estacao';
      sql:=sql+' WHERE sed.codigo_estacao = '+quotedstr(codigo_estacao);
      executaracao(sql,querysql10);
      if querysql10.RecordCount > 0 then
         begin
            dtsquerysql10.DataSet := querysql10;
            griddocumentacao.DataSource:= dtsquerysql10;
            griddocumentacao.refresh;
         end;
   end;  }
end;

procedure Tfrmestacoes.spbbuscausuarioClick(Sender: TObject);
begin
 {  with modulo_dados do
   begin
      sql:='SELECT ugu.nome_completo, ugd.nome_departamento, ugu.usucod,ugu.login,ugu.codigo_usuario';
	    sql:=sql+' FROM USER_geoapolo_usuarios ugu with(nolock) ';
      sql:=sql+' INNER JOIN USER_geoapolo_departamentos ugd with(nolock) ON ugu.codigo_departamento = ugd.codigo_departamento AND ugd.flagativo = '+quotedstr('A');
      sql:=sql+' WHERE ugu.flagativo = '+quotedstr('A');
	    sql:=sql+' ORDER BY ugd.nome_departamento ASC';
      executaracao(sql,querysql6);
      if querysql6.RecordCount > 0 then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            dtsquerysql6.DataSet :=querysql6;
            frmconsulta3.gridconsulta.DataSource := dtsquerysql6;
            with frmconsulta3 do
            begin
               cbocampo.clear; cbordem.clear;
               for i:= 0 to querysql6.FieldCount -1 do
               begin
                  cbocampo.Items.add(querysql6.Fields[i].DisplayName);
                  cbordem.Items.add(querysql6.Fields[i].DisplayName);
               end;
            end;
            frmconsulta3.controle:='USUARIO_ESTACAO';
            frmconsulta3.ShowModal;
         end;
   end;   }
end;

procedure Tfrmestacoes.spbcarregarquivoClick(Sender: TObject);
begin
   opendialog.execute;
   if lowercase(extractfileext(opendialog.filename)) = '.jpg' then
      imgdocumento.Picture.LoadFromFile(opendialog.FileName);
   //
   deondeveio:='DOCUMENTACAO';
   lblarquivo.text :=opendialog.filename;
   lblarquivo.refresh;
   lblnumdoc.SetFocus;
end;

procedure Tfrmestacoes.spbdeletarClick(Sender: TObject);
begin
   messagedlg('AS OPÇÕES QUE PERMITEM EXCLUSÃO DE ITEM, ESTÃO HABILITADAS PRESSIONANDO DELETE SOBRE O ITEM DESEJADO NO GRID !!!',mtinformation,[mbok],0);
end;

procedure Tfrmestacoes.lbltmpgarantiaEnter(Sender: TObject);
begin
   if trim(mskvalor.Text) <> '' then
      mskvalor.Text := buscatroca(mskvalor.Text,',','.')
   else
      mskvalor.Text := '0';
end;

procedure Tfrmestacoes.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f10 then
      spbsair.Click;
end;

procedure Tfrmestacoes.lblnumdocKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      spbsalvadocumento.click;
end;

procedure Tfrmestacoes.lblnumserieKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      cbostatush.SetFocus;
end;

procedure Tfrmestacoes.tabsoftwareEnter(Sender: TObject);
begin
 {  with modulo_dados do
   begin
     // TIPO DE LICENÇA DE SOFTWARE
     sql:='SELECT descricao FROM USER_geoapolo_satfi_tipo_licenca';
     executaracao(sql,querysql);
     if querysql.recordcount > 0 then
        begin
           cbotipolic.Clear; querysql.first;
           while not querysql.eof do
           begin
              cbotipolic.items.add(querysql.fieldbyname('descricao').asstring);
              querysql.next;
           end;
        end
     else
        begin
           messagedlg('TABELA DE TIPO DE LICENÇA ESTÁ VAZIA, FAVOR CADASTRAR !!!',mterror,[mbok],0);
           frmestacoes.close;
        end;
   end;   }
   carrega_combo_classes('SOFTWARE');
   mostra_softwaredaestacao(lblcodigoest.text);
   lblcodsoftware.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_satfi_software','Sim');
   lblcodsoftware.Refresh;
   carrega_config('SATFISOFTWARE',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
  // configura_grid('SATFISOFTWARE',frmestacoes,frmlogon.nomeusuario,'gridsoftware',gridsoftware,modulo_dados.dtsquerysql7);
end;

procedure Tfrmestacoes.tblconfigredeEnter(Sender: TObject);
begin
  mostraredeestacao(lblcodigoest.text);
  if controle <> 'ALTERAÇÃO' then
     lblenderecoip.Text := GetLocalIP;
  lblenderecoip.Refresh;
  carrega_config('SATFIREDES',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
  configura_grid('SATFIREDES',frmestacoes,frmlogon.nomeusuario,'gridredes',gridredes,modulo_dados.dtsfdquerysql8);
end;

procedure Tfrmestacoes.lblcodigoestKeyPress(Sender: TObject;
  var Key: Char);
begin
{  // SÓ ENTRA NUMERO
  If not( key in['0'..'9',#8] ) then
    begin
       beep;
       key:=#0;
    end;}
end;

procedure Tfrmestacoes.lblcodigoestKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f4 then
      spbuscaestacao.click;
   if (key = vk_tab) or (key = vk_return) then
      lbldescricao.setfocus;
end;

procedure Tfrmestacoes.edtcodsecaoKeyPress(Sender: TObject; var Key: Char);
begin
  // SÓ ENTRA NUMERO
  If not( key in['0'..'9',#8] ) then
    begin
       beep;
       key:=#0;
    end;
end;

procedure Tfrmestacoes.edtdescricaolocalizacaoKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      lblvlan.SetFocus;
end;

procedure Tfrmestacoes.edtentnomeEnter(Sender: TObject);
begin
   if lblentcod.text <> '' then
      edtentnome.text := retorna_nomeentidade(lblentcod.Text);
   edtentnome.refresh;
end;

procedure Tfrmestacoes.edtentnomeKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lbllocalizacao.setfocus;
end;

procedure Tfrmestacoes.edtlocalizacaoEnter(Sender: TObject);
begin
   if (lbllocalizacao.text <> '') and (edtlocalizacao.text = '') then
      edtlocalizacao.Text:=retorna_descricaolocalizacaofisica(lbllocalizacao.text);
end;

procedure Tfrmestacoes.edtlocalizacaoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      memobservacoes.SetFocus;
end;

procedure Tfrmestacoes.lblipKeyPress(Sender: TObject; var Key: Char);
begin
  // SÓ ENTRA NUMERO
{  If not( key in['0'..'9',#8] ) then
    begin
       beep;
       key:=#0;
    end;}
end;

procedure Tfrmestacoes.mskdtcadastroKeyPress(Sender: TObject;
  var Key: Char);
begin
  // SÓ ENTRA NUMERO
  If not( key in['0'..'9',#8] ) then
    begin
       beep;
       key:=#0;
    end;
end;

procedure Tfrmestacoes.lblcodest2KeyPress(Sender: TObject; var Key: Char);
begin
  // SÓ ENTRA NUMERO
  If not( key in['0'..'9',#8] ) then
    begin
       beep;
       key:=#0;
    end;
end;

procedure Tfrmestacoes.lblcodigohardKeyPress(Sender: TObject;
  var Key: Char);
begin
  // SÓ ENTRA NUMERO
  If not( key in['0'..'9',#8] ) then
    begin
       beep;
       key:=#0;
    end;
end;

procedure Tfrmestacoes.edtcodfornKeyPress(Sender: TObject; var Key: Char);
begin
  // SÓ ENTRA NUMERO
  If not( key in['0'..'9',#8] ) then
    begin
       beep;
       key:=#0;
    end;
end;

procedure Tfrmestacoes.mskvalorKeyPress(Sender: TObject; var Key: Char);
begin
  // SÓ ENTRA NUMERO
{  If not( key in['0'..'9',#8] ) then
    begin
       beep;
       key:=#0;
    end;}
end;

procedure Tfrmestacoes.mskdtcompraKeyPress(Sender: TObject; var Key: Char);
begin
  // SÓ ENTRA NUMERO
  If not( key in['0'..'9',#8] ) then
    begin
       beep;
       key:=#0;
    end;
end;

procedure Tfrmestacoes.mskdtativacaoKeyPress(Sender: TObject;
  var Key: Char);
begin
  // SÓ ENTRA NUMERO
  If not( key in['0'..'9',#8] ) then
    begin
       beep;
       key:=#0;
    end;
end;

procedure Tfrmestacoes.lbltmpgarantiaKeyPress(Sender: TObject;
  var Key: Char);
begin
  // SÓ ENTRA NUMERO
  If not( key in['0'..'9',#8] ) then
    begin
       beep;
       key:=#0;
    end;
end;

procedure Tfrmestacoes.lbltmpgarantiaKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      cbostatush.setfocus;
end;

procedure Tfrmestacoes.lblcodestsoftKeyPress(Sender: TObject;
  var Key: Char);
begin
  // SÓ ENTRA NUMERO
  If not( key in['0'..'9',#8] ) then
    begin
       beep;
       key:=#0;
    end;
end;

procedure Tfrmestacoes.lblcodsoftwareKeyPress(Sender: TObject;
  var Key: Char);
begin
  // SÓ ENTRA NUMERO
  If not( key in['0'..'9',#8] ) then
    begin
       beep;
       key:=#0;
    end;
end;

procedure Tfrmestacoes.edtcodfornsKeyPress(Sender: TObject; var Key: Char);
begin
  // SÓ ENTRA NUMERO
  If not( key in['0'..'9',#8] ) then
    begin
       beep;
       key:=#0;
    end;
end;

procedure Tfrmestacoes.mskvalorsoftKeyPress(Sender: TObject;
  var Key: Char);
begin
  // SÓ ENTRA NUMERO
{  If not( key in['0'..'9',#8] ) then
    begin
       beep;
       key:=#0;
    end;}
end;

procedure Tfrmestacoes.mskdtcomprasoftKeyPress(Sender: TObject;
  var Key: Char);
begin
  // SÓ ENTRA NUMERO
  If not( key in['0'..'9',#8] ) then
    begin
       beep;
       key:=#0;
    end;
end;

procedure Tfrmestacoes.mskdtativasoftKeyPress(Sender: TObject;
  var Key: Char);
begin
  // SÓ ENTRA NUMERO
  If not( key in['0'..'9',#8] ) then
    begin
       beep;
       key:=#0;
    end;
end;

procedure Tfrmestacoes.mskvalorsoftEnter(Sender: TObject);
begin
   if trim(lblnfsoft.Text) = '' then
      lblnfsoft.Text :='0';
end;

procedure Tfrmestacoes.lblrespcctrlKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      lblrack.SetFocus;
end;

procedure Tfrmestacoes.lblservicetagKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      lblmodelo.setfocus;
end;

procedure Tfrmestacoes.lblswitchKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      lblportaswitch.SetFocus;
end;

procedure Tfrmestacoes.cbodepartamentosEnter(Sender: TObject);
begin
   with modulo_dados do
   begin
     if lblcodigodepartamento.Text <> '' then
        begin
           buscanacombo(retorna_nomedepartamento(lblcodigodepartamento.Text),frmestacoes,cbodepartamentos);
           cbodepartamentos.Refresh;
           mskdtcadastro.SetFocus;
        end;
   end;
end;

function retorna_nomedepartamento(codigo : string) : string;
begin
 {  with modulo_dados, frmestacoes do
   begin
     sql:='SELECT nome_departamento FROM USER_geoapolo_departamentos WHERE codigo_departamento = '+quotedstr(codigo);
     executaracao(sql,querysql10);
     if querysql10.RecordCount > 0 then
        begin
          result := querysql10.FieldByName('nome_departamento').AsString;
        end;
   end;  }
end;

procedure Tfrmestacoes.cbodepartamentosKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      mskdtcadastro.SetFocus;
end;

procedure Tfrmestacoes.lblenderecoipKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      spbsalvar.Click;
end;

procedure Tfrmestacoes.lblentcodKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = VK_F4 then
      spbuscaentidade.click;
   if (key = vk_return) or (key = vk_tab) then
      edtentnome.setfocus;
end;

procedure Tfrmestacoes.lblentcodsoftKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lblnfsoft.setfocus;
   if key = vk_f4 then
      spbuscaentsoft.click;
end;

procedure Tfrmestacoes.lblportapatchEnter(Sender: TObject);
begin
   if lblenderecoip.Text = '' then
      begin
         messagedlg('O CAMPO DE ENDEREÇO IP É IMPORTANTE PARA ESTE CADASTRO !!!!', mtwarning,[mbok],0);
         exit;
      end;
end;

procedure Tfrmestacoes.lblportapatchKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lblcodlocalizacaofisica.SetFocus;
end;

procedure Tfrmestacoes.lblportaswitchKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      lblenderecoip.SetFocus;
end;

procedure Tfrmestacoes.lblcodlocalizacaofisicaKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      begin
         edtdescricaolocalizacao.SetFocus;
      end;
   if key = vk_f4 then
      spbuscalocalizacaofisica.Click;
end;

function mostra_hardwaredaestacao(codigo_estacao:string) : string;
begin
 {  with modulo_dados, frmestacoes do
   begin
      sql:='SELECT ugsh.descricao, ugsh.valor, ugsh.data_compra, ugsh.data_ativacao, ugsh.tempo_garantia, ugsh.data_ultimamanutencao,';
      sql:=sql+'  ugsshs.descricao as Status_hardware, ugse.descricao Estacao, ugsca.descricao as Classificacao, ugsh.observacoes,';
      sql:=sql+'   ugsh.nf, ugsh.codigo_hardware, ugsh.codigo_status_h, ugsh.codigoclasse';
      sql:=sql+' FROM user_geoapolo_satfi_hardware ugsh';
      sql:=sql+' INNER JOIN USER_geoapolo_satfi_status_hardsoft ugsshs with(nolock) ON ugsh.codigo_status_h = ugsshs.codigo_status';
      sql:=sql+' INNER JOIN USER_geoapolo_satfi_estacao ugse with(nolock) ON ugsh.codigo_estacao = ugse.codigo_estacao';
      sql:=sql+' INNER JOIN USER_geoapolo_satfi_classificacaoativo ugsca with(nolock) ON ugsh.codigoclasse = ugsca.codigoclasse';
      sql:=sql+' WHERE ugsh.codigo_estacao = '+quotedstr(codigo_estacao);
      executaracao(sql,querysql5);
      if querysql5.RecordCount > 0 then
         begin
            cbocampo.clear; cbordem.clear;
            for i:= 0 to querysql5.FieldCount -1 do
            begin
               cbocampo.Items.add(querysql5.Fields[i].DisplayName);
               cbordem.Items.add(querysql5.Fields[i].DisplayName);
            end;
            dtsquerysql5.DataSet := querysql5;
            gridhardware.DataSource:=dtsquerysql5;
            gridhardware.refresh;
         end;
   end;}
end;

function mostra_fichatecnicahardware(codigo_hardware : string) : string;
begin
{   with modulo_dados, frmestacoes do
   begin
      sql:='SELECT * FROM USER_geoapolo_satfi_hardware_fichatecnica ';
      sql:=sql+' WHERE codigo_hardware = '+codigo_hardware;
      executaracao(sql,querysql6);
      if querysql6.RecordCount > 0 then
         begin
            dtsquerysql6.DataSet := querysql6;
            gridfichatecnica.DataSource:=dtsquerysql6;
            gridfichatecnica.refresh;
         end;
   end;    }
end;

function mostraredeestacao(codigo_estacao:string) : string;
begin
  { with modulo_dados, frmestacoes do
   begin
      sql:='SELECT ugser.rack, ugser.patchpanel, ugser.enderecoip, ugser.porta_patchpanel, ugslf.localizacao';
	    sql:=sql+' FROM USER_geoapolo_satfi_estacao_rede ugser with(nolock)';
	    sql:=sql+' LEFT JOIN USER_geoapolo_satfi_localizacao_fisica ugslf ON ugser.codigo_localizacaofisica = ugslf.codigo_localizacao';
      sql:=sql+' WHERE ugser.codigo_estacao = '+quotedstr(codigo_estacao);
      executaracao(sql,querysql8);
      if querysql8.RecordCount > 0 then
         begin
            cbocampo.clear; cbordem.clear;
            for i:= 0 to querysql8.FieldCount -1 do
            begin
               cbocampo.Items.add(querysql8.Fields[i].DisplayName);
               cbordem.Items.add(querysql8.Fields[i].DisplayName);
            end;
            dtsquerysql8.DataSet := querysql8;
            gridredes.DataSource := dtsquerysql8;
            gridredes.refresh;
         end;
   end;  }
end;

function mostra_detalhefichatecnica(codigo_hardware : string; codigo_estacao: string): string;
begin
  { with modulo_dados, frmestacoes do
   begin
      sql:='SELECT ugsf.conteudo, ugpm.descricao_marca, ugsf.identificacao, ugsf.codigo_marca';
	    sql:=sql+' FROM user_geoapolo_satfi_hardware ugsh';
	    sql:=sql+' INNER JOIN USER_geoapolo_satfi_hardware_fichatecnica ugsf with(nolock) ON ugsh.codigo_hardware = ugsf.codigo_hardware';
      sql:=sql+' LEFT JOIN USER_geoapolo_produto_marcas ugpm with(nolock) ON ugsf.codigo_marca = ugpm.codigo_marca';
	    sql:=sql+' WHERE ugsh.codigo_estacao = '+quotedstr(codigo_estacao);
	    sql:=sql+' AND   ugsh.codigo_hardware = '+quotedstr(codigo_hardware);
      executaracao(sql,querysql9);
      if querysql9.RecordCount > 0 then
         begin
            dtsquerysql9.dataset:= querysql9;
            {griddetalhefichatecnica.columns[0].FieldName:=querysql9.fieldbyname('identificacao').asstring;
            griddetalhefichatecnica.columns[1].FieldName:=querysql9.fieldbyname('conteudo').asstring;
//            griddetalhefichatecnica.Refresh;
           dimensionargrid(griddetalhefichatecnica,frmestacoes);
         end;
   end;}
end;

function mostra_softwaredaestacao(codigo_estacao : string) : string;
var
   sql2:string;
begin
   with modulo_dados, frmestacoes do
   begin
      sql2:='SELECT se.descricao, stl.descricao tipo_licenca, se.nf, se.valor,';
      sql2:=sql2+' se.data_compra, se.data_ativacao, sest.descricao estacao, sest.usuario_responsavel,se.geoentcod entcod,';
      sql2:=sql2+' se.codigo_tipo_lic, ssh.descricao status, sc.descricao classe, se.observacoes, se.codigo_software, ';
      sql2:=sql2+' se.codigo_estacao, se.codigo_marca, se.service_pack, se.chave_produto, se.tamanho_estimado';
      sql2:=sql2+', ge.geoentnome, gpm.descricao_marca ';
      sql2:=sql2+' FROM USER_geoapolo_satfi_software se INNER JOIN USER_geoapolo_satfi_estacao sest ON se.codigo_estacao = sest.codigo_estacao';
      sql2:=sql2+' LEFT JOIN USER_geoapolo_satfi_tipo_licenca stl ON se.codigo_tipo_lic = stl.codigo_tipo_lic';
      sql2:=sql2+' LEFT JOIN USER_geoapolo_satfi_status_hardsoft ssh ON se.codigo_status = ssh.codigo_status';
      sql2:=sql2+' LEFT JOIN USER_geoapolo_entidade ge ON se.geoentcod = ge.geoentcod';
      sql2:=sql2+' LEFT JOIN USER_geoapolo_produto_marcas gpm ON gpm.codigo_marca = se.codigo_marca';
      sql2:=sql2+' INNER JOIN USER_geoapolo_satfi_classificacaoativo sc ON se.codigoclasse = sc.codigoclasse';
      sql2:=sql2+' WHERE se.codigo_estacao = '+quotedstr(codigo_estacao);

      {

	  SELECT ugse.descricao, ugstl.descricao as tipo_licenca, ugse.nf, ugse.valor, ugss.data_compra, ugss.data_ativacao,
	         ugse.descricao as Estacao, ugse.usuario_responsavel, ugss.geoentcod as entcod, ugss.codigo_tipo_lic, ugsshs.descricao as status_software,
			 ugsca.descricao as Classe

	  FROM USER_geoapolo_satfi_software ugss with(nolock)
	  INNER JOIN USER_geoapolo_satfi_estacao ugse with(nolock) ON ugss.codigo_estacao = ugse.codigo_estacao
	  LEFT JOIN USER_geoapolo_satfi_tipo_licenca ugstl with(nolock) ON ugss.codigo_tipo_lic = ugstl.codigo_tipo_lic
	  LEFT JOIN USER_geoapolo_satfi_status_hardsoft ugsshs with(nolock) ON ugss.codigo_status = ugsshs.codigo_status
	  LEFT JOIN USER_geoapolo_entidade uge with(nolock) ON ugss.geoentcod = uge.geoentcod
	  LEFT JOIN USER_geoapolo_produto_marcas ugpm with(nolock) ON ugss.codigo_marca = ugpm.codigo_marca
	  INNER JOIN USER_geoapolo_satfi_classificacaoativo ugsca with(nolock) ON ugss.codigoclasse = ugsca.codigoclasse
	  WHERE ugss.codigo_estacao =

       }
   {   executaracao(sql2,querysql7);
      if querysql7.RecordCount > 0 then
         begin
            cbocampo.clear; cbordem.clear;
            for i:= 0 to querysql7.FieldCount -1 do
            begin
               cbocampo.Items.add(querysql7.Fields[i].DisplayName);
               cbordem.Items.add(querysql7.Fields[i].DisplayName);
            end;
            dtsquerysql7.DataSet := querysql7;
            gridsoftware.DataSource := dtsquerysql7;
            gridsoftware.refresh;
         end; }
   end;
end;

end.
