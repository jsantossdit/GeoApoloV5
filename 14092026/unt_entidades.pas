unit unt_entidades;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, ComCtrls, StdCtrls, Buttons, ExtCtrls, Grids, DBGrids, Menus, Data.DB,
  IdBaseComponent, IdComponent, IdTCPConnection, IdTCPClient, IdHTTP, System.UITypes,
  IdIOHandler, IdIOHandlerSocket, IdIOHandlerStack, IdSSL, IdSSLOpenSSL,
  System.JSON, FireDAC.Comp.Client, FireDAC.Stan.Param, System.IOUtils, DateUtils,
  uIntegradorGeoApolo, FireDAC.Stan.Option, Vcl.Mask, Clipbrd, System.RegularExpressions, unt_AlvoEntidade, System.StrUtils;

type
  Tfrmentidades = class(TForm)
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spbligacoes: TSpeedButton;
    spbsair: TSpeedButton;
    spblimpar: TSpeedButton;
    lblsair: TLabel;
    spbexcluir: TSpeedButton;
    spbexportarlote: TSpeedButton;
    spbfiltroavancado: TSpeedButton;
    spbnovo: TSpeedButton;
    StatusBar1: TStatusBar;
    GroupBox1: TGroupBox;
    GroupBox7: TGroupBox;
    lblcampo: TLabel;
    lblordem: TLabel;
    lblprocurarpor: TLabeledEdit;
    cbocampo: TComboBox;
    cbordem: TComboBox;
    rdgcrescente: TRadioButton;
    rdgdecrescente: TRadioButton;
    gridentidades: TDBGrid;
    PopupMenu1: TPopupMenu;
    mnugravaconfiguracoes: TMenuItem;
    cbobuscabanco: TComboBox;
    lblbuscaem: TLabel;
    spbexportaentidades: TSpeedButton;
    pnlconfereentidade: TPanel;
    spbatualizaentidadeapolo: TBitBtn;
    memobaseapolo: TMemo;
    lblmensagemgeoapolo: TLabel;
    lblmensagemapolo: TLabel;
    memoplataformasve: TMemo;
    btnignorar: TBitBtn;
    lblentidadeslistadas: TLabel;
    lblnentidadeslistadas: TLabel;
    lbljafoi: TLabel;
    lbltemobservacoes1: TLabel;
    shpobsmoderar: TShape;
    Panel1: TPanel;
    spbjaexportada: TSpeedButton;
    Panel2: TPanel;
    Label1: TLabel;
    spbsobrepoealvo: TBitBtn;
    btnignoraralvo: TBitBtn;
    StringGrid1: TStringGrid;
    pnlFiltroAvancado: TPanel;
    pnlFiltroTopo: TPanel;
    lblFiltroTitulo: TLabel;
    lblFiltroConector: TLabel;
    lblFiltroCampo: TLabel;
    lblFiltroOperador: TLabel;
    lblFiltroValor: TLabel;
    btnFecharFiltroAvancado: TButton;
    cboFiltroConector: TComboBox;
    cboFiltroCampo: TComboBox;
    cboFiltroOperador: TComboBox;
    edtFiltroValor: TEdit;
    btnAdicionarCondicao: TButton;
    btnRemoverCondicao: TButton;
    btnLimparCondicoes: TButton;
    gridCondicoes: TStringGrid;
    pnlFiltroRodape: TPanel;
    btnAtalhoGOPendentes: TButton;
    btnRestaurarFiltroPadrao: TButton;
    btnAplicarFiltroAvancado: TButton;
    procedure FormActivate(Sender: TObject);
    procedure spbsairClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure mnugravaconfiguracoesClick(Sender: TObject);
    procedure gridentidadesDblClick(Sender: TObject);
    procedure gridentidadesKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure cbocampoChange(Sender: TObject);
    procedure cbobuscabancoClick(Sender: TObject);
    procedure FormShow(Sender: TObject);
    procedure gridentidadesDrawColumnCell(Sender: TObject; const Rect: TRect;
      DataCol: Integer; Column: TColumn; State: TGridDrawState);
    procedure btnignorarClick(Sender: TObject);
    procedure rdgcrescenteClick(Sender: TObject);
    procedure rdgdecrescenteClick(Sender: TObject);
    procedure StringGrid1SelectCell(Sender: TObject; ACol, ARow: Integer;
      var CanSelect: Boolean);
    procedure StringGrid1DrawCell(Sender: TObject; ACol, ARow: Integer;
      Rect: TRect; State: TGridDrawState);
    procedure spbsobrepoealvoClick(Sender: TObject);
    procedure lblprocurarporKeyPress(Sender: TObject; var Key: Char);
    procedure spbexportaentidadesClick(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure spbexportarloteClick(Sender: TObject);
    procedure spbfiltroavancadoClick(Sender: TObject);
    procedure spbnovoClick(Sender: TObject);
    procedure btnFecharFiltroAvancadoClick(Sender: TObject);
    procedure btnAdicionarCondicaoClick(Sender: TObject);
    procedure btnRemoverCondicaoClick(Sender: TObject);
    procedure btnLimparCondicoesClick(Sender: TObject);
    procedure btnAtalhoGOPendentesClick(Sender: TObject);
    procedure btnRestaurarFiltroPadraoClick(Sender: TObject);
    procedure btnAplicarFiltroAvancadoClick(Sender: TObject);
  private
    FCarregandoEntidades: Boolean;
    FJaAtivou: Boolean;
    procedure ConfigurarGrid;
    procedure MontarTelaComparacao(QuerySVE, QueryBanco: TFDQuery);
    procedure SelectCell(Sender: TObject; ACol, ARow: Integer; var CanSelect: Boolean);
    procedure ConfigurarGridCompleto(const NomeBase: string);
    function DeterminarTipoTratamento(const AGenero, AEstadoCivil: string): string;
    function ObterCodigoTipoTratamento(const AAbreviatura: string): string;
    function ObterCodigoRegiaoPorUF(const AUF: string): string;
    function GarantirAutenticacaoAlvo(AAPI: TAlvoAPI): Boolean;
    function GarantirContatoIntegradoAlvo(const AGeoEntCod: string; API: TAlvoAPI; out AEntCodContato: string; out AErro: string): Boolean;
    function MontarEntidadeParaEnvio(const AGeoEntCod: string; out AEntidade: TEntidade; out ATratCod: string): Boolean;
    procedure AtualizarEntidadeExportada(const AGeoEntCod, ANovoEntCod, ATratCod: string);
    procedure InicializarFiltroAvancado;
    procedure AplicarFiltroAvancadoSQL(const AWhereClause: string);
  public
    filhossimnao, wordem, integraentidadeapolo, falecido, sexo, logradouro,
    codgrauescolar, grauescolaridade, vgeoentcod, ventcod: string;
    vordem: string;
  end;

// =============================================================================
// TIPOS E CONSTANTES — Comparação lado a lado SVE x Alvo
// =============================================================================
type
  TDecisaoLinha = (dlNenhuma, dlManterSVE, dlManterAlvo);

  TMapaCampo = record
    LabelExibicao: string;
    CampoSVE     : string;
    CampoAlvo    : string;
  end;

const
  TOTAL_CAMPOS_MAPA = 14;
  MapaCampos: array[0..TOTAL_CAMPOS_MAPA - 1] of TMapaCampo = (
    (LabelExibicao: 'Nome';             CampoSVE: 'geoentnome';         CampoAlvo: 'entnome'),
    (LabelExibicao: 'CPF / CNPJ';       CampoSVE: 'Documento';          CampoAlvo: 'EntCpfCgc'),
    (LabelExibicao: 'RG / IE';          CampoSVE: 'EntRgIe';            CampoAlvo: 'EntRgIe'),
    (LabelExibicao: 'Logradouro';       CampoSVE: 'tipolograd';         CampoAlvo: 'EntLograd'),
    (LabelExibicao: 'Endereço';         CampoSVE: 'geoentender';        CampoAlvo: 'entender'),
    (LabelExibicao: 'Número';           CampoSVE: 'geoenderno';         CampoAlvo: 'entenderno'),
    (LabelExibicao: 'Complemento';      CampoSVE: 'geoentendercomp';    CampoAlvo: 'EntEnderComp'),
    (LabelExibicao: 'Bairro';           CampoSVE: 'geoentbair';         CampoAlvo: 'entbair'),
    (LabelExibicao: 'CEP';              CampoSVE: 'geoentcep';          CampoAlvo: 'entcep'),
    (LabelExibicao: 'Cidade';           CampoSVE: 'cidnomecomp';        CampoAlvo: 'cidnomecomp'),
    (LabelExibicao: 'Estado';           CampoSVE: 'ufsigla';            CampoAlvo: 'ufsigla'),
    (LabelExibicao: 'E-mail';           CampoSVE: 'Email';              CampoAlvo: 'Email'),
    (LabelExibicao: 'Telefone';         CampoSVE: 'Telefone';           CampoAlvo: 'Telefone'),
    (LabelExibicao: 'Data Aniversário'; CampoSVE: 'geoentdataanivfund'; CampoAlvo: 'EntDataAnivFund')
  );

var
  frmentidades: Tfrmentidades;
  sql: string;
  campos: array[0..29] of string;
  numerocategorias: integer;

  GDecisoes        : array[0..TOTAL_CAMPOS_MAPA - 1] of TDecisaoLinha;
  GLinhasDiferentes: array[0..TOTAL_CAMPOS_MAPA - 1] of Integer;
  GTotalDiferentes : Integer;

function carrega_lista_entidades(basededados: string; tipo_pesquisa: string; filtro: string): string; export;
function verifica_integracao_entidades(empcod: string): string; export;
function retorna_ativ_econ(ativeconcodestr: string): string; export;
function importa_entidade(integracao: string): string; export;
function match_code_com_apolo(geoentcod: string; base_dados: string): string; export;
function atualiza_entcod_alvo_via_cpf(const vcodigogeoentidade: string): string; export;
function match_code_com_alvo(geoentcod: string; base_dados: string): string; export;
function ExtrairConjunto(const Texto: string; Indice: Integer): string; export;

implementation

uses funcoes, unt_dados, unt_logon, unt_cadentidades, unt_principal,
  unt_selecionaempresa, unt_statusbarclock;

{$R *.dfm}

// =============================================================================
// SolicitarSenhaMascarada
// Exibe um dialogo simples (criado em runtime) com campo de senha mascarado
// (PasswordChar), usado para coletar a senha do usuario alvo sem exibi-la.
// =============================================================================
function SolicitarSenhaMascarada(const ATitulo, APrompt: string;
  out ASenha: string): Boolean;
var
  FormSenha : TForm;
  lblProm   : TLabel;
  edtSenha  : TEdit;
  btnOK     : TButton;
  btnCancel : TButton;
begin
  Result := False;
  ASenha := '';
  FormSenha := TForm.CreateNew(Application);
  try
    FormSenha.Caption     := ATitulo;
    FormSenha.ClientWidth  := 340;
    FormSenha.ClientHeight := 120;
    FormSenha.Position    := poScreenCenter;
    FormSenha.BorderStyle := bsDialog;
    FormSenha.BorderIcons := [biSystemMenu];
    FormSenha.KeyPreview  := True;

    lblProm := TLabel.Create(FormSenha);
    lblProm.Parent   := FormSenha;
    lblProm.Left     := 16;
    lblProm.Top      := 12;
    lblProm.Width    := 308;
    lblProm.WordWrap := True;
    lblProm.Caption  := APrompt;

    edtSenha := TEdit.Create(FormSenha);
    edtSenha.Parent       := FormSenha;
    edtSenha.Left         := 16;
    edtSenha.Top          := 44;
    edtSenha.Width        := 308;
    edtSenha.PasswordChar := '*';

    btnOK := TButton.Create(FormSenha);
    btnOK.Parent      := FormSenha;
    btnOK.Caption     := 'OK';
    btnOK.Left        := 168;
    btnOK.Top         := 80;
    btnOK.Width       := 75;
    btnOK.ModalResult := mrOk;
    btnOK.Default     := True;

    btnCancel := TButton.Create(FormSenha);
    btnCancel.Parent      := FormSenha;
    btnCancel.Caption     := 'Cancelar';
    btnCancel.Left        := 249;
    btnCancel.Top         := 80;
    btnCancel.Width       := 75;
    btnCancel.ModalResult := mrCancel;
    btnCancel.Cancel      := True;

    FormSenha.ActiveControl := edtSenha;

    if FormSenha.ShowModal = mrOk then
    begin
      ASenha := edtSenha.Text;
      Result := Trim(ASenha) <> '';
    end;
  finally
    FormSenha.Free;
  end;
end;

// =============================================================================
// btnignorarClick
// =============================================================================
procedure Tfrmentidades.btnignorarClick(Sender: TObject);
var
  vocorcod: string;
begin
  with modulo_dados do
  begin
    resp := messagedlg('Confirma a não atualização deste registro no Alvo (Y/N)',
                       mtconfirmation, [mbyes, mbno], 0);
    if resp = idyes then
    begin
      sql := 'UPDATE USER_geoapolo_Entidade SET atualizou_apolo = :atualizouapolo' +
             ', usucod_atualizou_apolo = :usucodapolo' +
             ' WHERE geoentcod = :geoentcod';
      fdquerysql3.Close;
      fdquerysql3.SQL.Clear;
      fdquerysql3.SQL.Text := sql;
      fdquerysql3.ParamByName('atualizouapolo').AsString := QuotedStr('S');
      fdquerysql3.ParamByName('usucodapolo').AsString    := frmprincipal.usucod_apolo;
      fdquerysql3.ParamByName('geoentcod').AsString      := fdqueryentidade.FieldByName('geoentcod').AsString;
      if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
      begin
        fdquerysql11.Close;
        fdquerysql11.SQL.Clear;
        fdquerysql11.SQL.Text := 'SELECT ocorcod FROM user_geoapolo_entidade WHERE geoentcod = :geoentcod';
        fdquerysql11.ParamByName('geoentcod').AsString := fdqueryentidade.FieldByName('geoentcod').AsString;
        if executaracao(fdquerysql11, fdbanco, true, dtsfdquerysql11) then
          vocorcod := fdquerysql11.FieldByName('ocorcod').AsString;

        sql := 'DECLARE @vocorcod1 varchar(7)' +
               ' exec User_geraocorrencia_projetosv2 ' + frmprincipal.codigo_empresa +
               ', ' + 'F' + ', ' + 'INDIVIDUAL' +
               ', ' + '' + ', ' + '' +
               ', ' + vocorcod + ', ' + '' +
               ', ' + frmlogon.codigousuario +
               ', ' + 'FOI IGNORADA A ATUALIZAÇÃO DE CADASTRO POR ESTAR ATUALIZADO' +
               ', ' + '0000012' + ', ' + '' +
               ', NULL, NULL, ' + '';
        fdcomando.CommandText.Text  := sql;
        try
          fdcomando.Execute;
        except
          on e: exception do ShowMessage(e.Message);
        end;
        gravalog(frmlogon.codigousuario, datetostr(date),
                 'NÃO ATUALIZOU A ENTIDADE ' + campos[0] + ' NO ALVO');
        carrega_lista_entidades(cbobuscabanco.Text, 'Consulta', '');
      end;
    end;
    carrega_lista_entidades(cbobuscabanco.Text, 'Consulta', '');
    pnlconfereentidade.Visible  := False;
    memoplataformasve.Visible   := True;
    memobaseapolo.Visible       := True;
    StringGrid1.Visible         := False;
  end;
end;

// =============================================================================
// cbobuscabancoClick
// =============================================================================
procedure Tfrmentidades.cbobuscabancoClick(Sender: TObject);
begin
  setcursorsql('sql');
  FCarregandoEntidades := False;
  carrega_lista_entidades(cbobuscabanco.Text, 'Consulta', '');
  setcursorsql('');
  ConfigurarGridCompleto(cbobuscabanco.Text);
end;

procedure Tfrmentidades.cbocampoChange(Sender: TObject);
begin
  funcoes.setcursorsql('sql');
  buscanacombo(cbocampo.Text, frmentidades, cbordem);
  cbordem.Refresh;
end;

// =============================================================================
// FormActivate
// =============================================================================
procedure Tfrmentidades.FormActivate(Sender: TObject);
var
  Integrador: TIntegradorGeoApolo;
begin
  setcursorsql('sql');
  with modulo_dados do
  begin
    Integrador := TIntegradorGeoApolo.Create(fdquerysql, fdquerysql2, fdquerysql3);
    try
      Integrador.SincronizaOrigens(cbobuscabanco.Text, integraentidadeapolo);
    finally
      Integrador.Free;
    end;
    lblprocurarpor.SetFocus;
    carrega_lista_entidades('GeoApolo', 'Consulta', '');
    ConfigurarGridCompleto('GeoApolo');
    carrega_config('entidades_geoapolo', frmentidades, cbocampo, cbordem,
                   rdgcrescente, rdgdecrescente);
    funcoes.AjustaLarguraColunas(gridentidades);
    cbobuscabanco.Refresh;
  end;
end;

// =============================================================================
// verifica_integracao_entidades
// =============================================================================
function verifica_integracao_entidades(empcod: string): string;
begin
  setcursorsql('sql');
  with modulo_dados, frmentidades do
  begin
    fdquerysql.Close;
    fdquerysql.SQL.Clear;
    fdquerysql.SQL.Add('SELECT integra_entidades_apolo FROM USER_geoapolo_configuracoes WHERE empcod = :empcod');
    fdquerysql.ParamByName('empcod').AsString := empcod;
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
      Result := fdquerysql.FieldByName('integra_entidades_apolo').AsString
    else
       begin
          setcursorsql('sql');
          messagedlg('NÃO EXISTEM PARÂMETROS CONFIGURADOS PARA ESTA EMPRESA, VERIFIQUE !!!', mterror, [mbok], 0);
      Exit;
    end;
  end;
end;

// =============================================================================
// match_code_com_alvo
// =============================================================================
function match_code_com_alvo(geoentcod: string; base_dados: string): string;
begin
  setcursorsql('sql');
  with frmentidades, modulo_dados do
  begin
    setcursorsql('sql');
    ConfigurarGrid;
    if base_dados = 'GeoApolo' then
    begin
      setcursorsql('sql');
      fdquerysql22.Close;
      fdquerysql22.SQL.Clear;
      fdquerysql22.SQL.Text := 'SELECT * FROM entidades_geoapolo WHERE geoentcod = :geoentcod';
      fdquerysql22.ParamByName('geoentcod').AsString := geoentcod;
      if executaracao(fdquerysql22, fdbanco, true, dtsfdquerysql22) then
        dtsfdquerysql22.Dataset := fdquerysql22;
    end
    else if base_dados = 'Alvo' then
    begin
      setcursorsql('sql');
      fdquerysql23.Close;
      fdquerysql23.SQL.Clear;
      fdquerysql23.SQL.Text := 'SELECT * FROM entidades_apolo WHERE entcod = :geoentcod';
      fdquerysql23.ParamByName('geoentcod').AsString := geoentcod;
      if executaracao(fdquerysql23, fdbanco, true, dtsfdquerysql23) then
        dtsfdquerysql23.DataSet := fdquerysql23;
    end;
    if fdquerysql22.Active and fdquerysql23.Active then
      MontarTelaComparacao(fdquerysql22, fdquerysql23);
  end;
end;

// =============================================================================
// match_code_com_apolo
// =============================================================================
function match_code_com_apolo(geoentcod: string; base_dados: string): string;
var
  cabecalho: array[0..29] of string;
  ponteiro: integer;
  cpfgeoapolo, datanascimento: string;
begin
  setcursorsql('sql');
  with frmentidades, modulo_dados do
  begin
    setcursorsql('sql');
    cabecalho[0]  := 'Código Apolo:';
    cabecalho[1]  := 'Tratamento: ';
    cabecalho[2]  := 'Nome: ';
    cabecalho[3]  := 'Logradouro: ';
    cabecalho[4]  := 'Endereço: ';
    cabecalho[5]  := 'Complem.';
    cabecalho[6]  := 'Número: ';
    cabecalho[7]  := 'Bairro: ';
    cabecalho[8]  := 'Cep: ';
    cabecalho[9]  := 'Cód.Cidade: ';
    cabecalho[10] := 'Cidade: ';
    cabecalho[11] := 'Estado: ';
    cabecalho[12] := 'Tipo Pessoa: ';
    cabecalho[13] := 'RG / IE: ';
    cabecalho[14] := 'CPF / CNPJ:';
    cabecalho[15] := 'Data Aniv.: ';
    cabecalho[16] := 'Gênero: ';
    cabecalho[17] := 'Id.Diocese: ';
    cabecalho[18] := 'Diocese: ';
    cabecalho[19] := 'Tipo Cobrança: ';
    cabecalho[20] := 'Nome Tipo Cob: ';
    cabecalho[21] := 'Dia Contribuição';
    cabecalho[22] := 'Valor Contribuição: ';
    cabecalho[23] := 'Número Bco: ';
    cabecalho[24] := 'Número Agência: ';
    cabecalho[25] := 'Nome Agência: ';
    cabecalho[26] := 'Conta Bancária: ';
    cabecalho[27] := 'Nome Banco: ';
    cabecalho[28] := 'E-Mails: ';
    cabecalho[29] := 'Telefones: ';

    if base_dados = 'GeoApolo' then
    begin
       setcursorsql('sql');
       sql := 'SELECT uge.geoentcod, uge.entcod, uge.geoentnome, uge.geotipentcod,' +
             ' uge.geoentsit, uge.geoentdatcad, uge.geopescod, uge.geotabentcod,' +
             ' uge.geousucod, uge.geocidcod, uge.geousumod, uge.geodatmod,' +
             ' uge.geoentobs, uge.geoentdataalt, uge.geoentdatainativ, uge.geoentdatreab,' +
             ' (SELECT dbo.fnGeoEntidadeEmail(uge.geoentcod,3)) AS Email,' +
             ' (SELECT dbo.fnGeoPessoaTelefone(uge.geoentcod,3)) AS Telefone,' +
             ' (SELECT dbo.fnGeoPessoaEndereco(uge.geoentcod,3)) AS Endereco,' +
             ' (SELECT dbo.fnGeoPessoaCidade(uge.geoentcod,3)) AS Cidade,' +
             ' uged.geonumerodocumento AS Documento' +
             ' FROM USER_geoapolo_entidade uge WITH(NOLOCK)' +
             ' LEFT JOIN USER_geoapolo_entidade_documentos uged WITH(NOLOCK)' +
             '   ON uge.geoentcod = uged.geoentcod AND uged.geotipodocumento = ''CPF/CNPJ''' +
             ' WHERE uge.geoentcod = ' + QuotedStr(geoentcod);
    end
    else if base_dados = 'Alvo' then
    begin
      setcursorsql('sql');
      sql := 'SELECT e.entcod, e.tipotratcod, e.entnome, e.EntLograd, e.entender, e.EntEnderComp, e.entenderno,' +
             ' e.entbair, e.entcep, e.cidcod, cid.cidnomecomp, cid.ufsigla, e.EntTipoFJ, e.EntRgIe, e.EntCpfCgc,' +
             ' e.EntDataAnivFund, e.EntGenero, e1.USERDiocese_id, e1.USERNomeDiocese, e.tipocobcod, tc.tipocobnome,' +
             ' e1.USERDia_Debito_CC, e1.USERValor_Contribuicao,' +
             ' e.bconum, bco.bconome, e.agnum, ag.agnome as agnome, e.entbcoagccornum,' +
             ' (SELECT dbo.fnEntidadeEmail(e.entcod,3)) as Email,' +
             ' (SELECT dbo.fnPessoaTelefone(e.entcod, 3)) as Telefone' +
             ' FROM entidade e WITH(NOLOCK)' +
             ' INNER JOIN cidade cid WITH(NOLOCK) ON e.cidcod = cid.CidCod' +
             ' INNER JOIN u_entidade e1 WITH(NOLOCK) ON e.entcod = e1.EntCod' +
             ' INNER JOIN tipo_cobranca tc WITH(NOLOCK) ON e.tipocobcod = tc.tipocobcod' +
             ' LEFT JOIN banco bco WITH(NOLOCK) ON e.bconum = bco.bconum' +
             ' LEFT JOIN ag_bancaria ag WITH(NOLOCK) ON e.agnum = ag.agnum AND ag.bconum = bco.BcoNum' +
             ' WHERE e.entcod = ' + QuotedStr(geoentcod);
    end;

    fdquerysql17.Close;
    fdquerysql17.SQL.Clear;
    fdquerysql17.SQL.Text := sql;
    if executaracao(fdquerysql17, fdbanco, true, dtsfdquerysql17) then
    begin
       setcursorsql('sql');
       fdquerysql17.First;
       while not fdquerysql17.EOF do
       begin
          setcursorsql('sql');
          for ponteiro := 0 to 29 do
          begin
            if base_dados = 'GeoApolo' then
            begin
              setcursorsql('sql');
              if ponteiro = 15 then
              begin
                 setcursorsql('sql');
                 datanascimento := FormatDateTime('dd/MM/yyyy', ConvertISODate(fdquerysql17.Fields[ponteiro].AsString));
              if datanascimento = '01/01/1970' then
                datanascimento := 'Data Aniv: Não preenchido';
              memoplataformasve.Lines.Add(cabecalho[ponteiro] + ' ' + datanascimento);
              end
            else
               memoplataformasve.Lines.Add(cabecalho[ponteiro] + ' ' +
               fdquerysql17.Fields[ponteiro].AsString);
               campos[ponteiro] := fdquerysql17.Fields[ponteiro].AsString;
               cpfgeoapolo := fdquerysql17.FieldByName('geonumerodocumento').AsString;
            end
          else if base_dados = 'Alvo' then
            memobaseapolo.Lines.Add(cabecalho[ponteiro] + ' ' +
              fdquerysql17.Fields[ponteiro].AsString);
        end;
        fdquerysql17.Next;
      end;
    end;
  end;
end;

// =============================================================================
// ExtrairEntCodResposta: parser robusto para capturar código do Alvo
// =============================================================================
function ExtrairEntCodResposta(const AMsg: string): string;
var
  jVal: TJSONValue;
  jObj, jEnt: TJSONObject;
  vStr: string;
  Match: TMatch;
begin
  Result := '';
  if Trim(AMsg) = '' then Exit;

  try
    jVal := TJSONObject.ParseJSONValue(AMsg);
    if (jVal <> nil) and (jVal is TJSONObject) then
    begin
      jObj := TJSONObject(jVal);
      try
        if jObj.TryGetValue<string>('entcod', vStr) and (Trim(vStr) <> '') then Exit(Trim(vStr));
        if jObj.TryGetValue<string>('EntCod', vStr) and (Trim(vStr) <> '') then Exit(Trim(vStr));
        if jObj.TryGetValue<string>('codigo', vStr) and (Trim(vStr) <> '') then Exit(Trim(vStr));
        if jObj.TryGetValue<string>('Codigo', vStr) and (Trim(vStr) <> '') then Exit(Trim(vStr));
        if jObj.TryGetValue<string>('id', vStr) and (Trim(vStr) <> '') then Exit(Trim(vStr));
        if jObj.TryGetValue<string>('Id', vStr) and (Trim(vStr) <> '') then Exit(Trim(vStr));

        if jObj.TryGetValue<TJSONObject>('Entidade', jEnt) or jObj.TryGetValue<TJSONObject>('entidade', jEnt) then
        begin
          if jEnt.TryGetValue<string>('entcod', vStr) and (Trim(vStr) <> '') then Exit(Trim(vStr));
          if jEnt.TryGetValue<string>('EntCod', vStr) and (Trim(vStr) <> '') then Exit(Trim(vStr));
          if jEnt.TryGetValue<string>('codigo', vStr) and (Trim(vStr) <> '') then Exit(Trim(vStr));
          if jEnt.TryGetValue<string>('Codigo', vStr) and (Trim(vStr) <> '') then Exit(Trim(vStr));
          if jEnt.TryGetValue<string>('id', vStr) and (Trim(vStr) <> '') then Exit(Trim(vStr));
        end;
      finally
        jVal.Free;
      end;
    end;
  except
  end;

  try
    Match := TRegEx.Match(AMsg, '(?:entidade|código|codigo|cód|cod)\s*(?:n[ºo°\.]*)?\s*:?\s*(\d+)', [roIgnoreCase]);
    if Match.Success and (Match.Groups.Count > 1) then
      Exit(Match.Groups[1].Value);

    Match := TRegEx.Match(AMsg, '"(?:entcod|codigo|id)"\s*:\s*"?(\d+)"?', [roIgnoreCase]);
    if Match.Success and (Match.Groups.Count > 1) then
      Exit(Match.Groups[1].Value);
  except
  end;
end;

// =============================================================================
// Helper: DeterminarTipoTratamento
// Regra:
//   M -> 'Sr.'
//   F -> se estado civil preenchido e Casada / União Estável -> 'Sra.', senão -> 'Srta.'
// =============================================================================
function Tfrmentidades.DeterminarTipoTratamento(const AGenero, AEstadoCivil: string): string;
var
  g, ec: string;
begin
  g  := UpperCase(Trim(AGenero));
  ec := UpperCase(Trim(AEstadoCivil));

  if (g = 'M') or (Pos('MASC', g) = 1) then
    Result := 'Sr.'
  else if (g = 'F') or (Pos('FEM', g) = 1) then
  begin
    if (ec <> '') and ((Pos('CASAD', ec) > 0) or (Pos('UNI', ec) > 0) or (Pos('ESTAVEL', ec) > 0) or (Pos('ESTÁVEL', ec) > 0)) then
      Result := 'Sra.'
    else
      Result := 'Srta.';
  end
  else
    Result := '';
end;

// =============================================================================
// Helper: ObterCodigoTipoTratamento
// Busca o código na tabela USER_geoapolo_tipotratamento
// =============================================================================
function Tfrmentidades.ObterCodigoTipoTratamento(const AAbreviatura: string): string;
var
  Qry: TFDQuery;
  vAbrev: string;
begin
  vAbrev := Trim(AAbreviatura);
  Result := vAbrev;
  if vAbrev = '' then Exit;

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := modulo_dados.fdbanco;
    Qry.SQL.Text :=
      'SELECT TOP 1 abreviatura, tipotratcod FROM USER_geoapolo_tipotratamento WITH (NOLOCK) ' +
      'WHERE UPPER(abreviatura) = UPPER(:abrev) OR UPPER(descricao_tratamento) LIKE UPPER(:abrev2)';
    Qry.ParamByName('abrev').AsString  := vAbrev;
    Qry.ParamByName('abrev2').AsString := '%' + vAbrev + '%';
    Qry.Open;
    if not Qry.IsEmpty then
    begin
      if Trim(Qry.FieldByName('abreviatura').AsString) <> '' then
        Result := Trim(Qry.FieldByName('abreviatura').AsString)
      else
        Result := Trim(Qry.FieldByName('tipotratcod').AsString);
    end;
  except
    Result := vAbrev;
  end;
  Qry.Free;
end;

// =============================================================================
// Helper: ObterCodigoRegiaoPorUF
// Mapeia a sigla do estado (UF) para a respectiva região conforme regras:
//   - RS, SC, PR -> Região Sul (código '1')
//   - SP, MG, RJ, ES -> Região Sudeste (código '5')
//   - MS, MT, GO, TO, DF -> Região Centro-Oeste (código '3')
//   - AM, RO, PA, AC, AP, RR -> Região Norte (código '4')
//   - AL, BA, CE, MA, PB, PE, PI, RN, SE -> Região Nordeste (código '2')
// =============================================================================
function Tfrmentidades.ObterCodigoRegiaoPorUF(const AUF: string): string;
var
  U, NomeBusca, FallbackCod: string;
  Qry: TFDQuery;
begin
  Result := '';
  U := UpperCase(Trim(AUF));
  if U = '' then Exit;

  // Sul: RS, SC, PR
  if (U = 'RS') or (U = 'SC') or (U = 'PR') then
  begin
    NomeBusca := 'SUL';
    FallbackCod := '1';
  end
  // Sudeste: SP, MG, RJ, ES
  else if (U = 'SP') or (U = 'MG') or (U = 'RJ') or (U = 'ES') then
  begin
    NomeBusca := 'SUDESTE';
    FallbackCod := '5';
  end
  // Centro-Oeste: MS, MT, GO, TO, DF
  else if (U = 'MS') or (U = 'MT') or (U = 'GO') or (U = 'TO') or (U = 'DF') then
  begin
    NomeBusca := 'CENTRO';
    FallbackCod := '3';
  end
  // Norte: AM, RO, PA, AC, AP, RR
  else if (U = 'AM') or (U = 'RO') or (U = 'PA') or (U = 'AC') or (U = 'AP') or (U = 'RR') then
  begin
    NomeBusca := 'NORTE';
    FallbackCod := '4';
  end
  // Nordeste: AL, BA, CE, MA, PB, PE, PI, RN, SE
  else if (U = 'AL') or (U = 'BA') or (U = 'CE') or (U = 'MA') or (U = 'PB') or
          (U = 'PE') or (U = 'PI') or (U = 'RN') or (U = 'SE') then
  begin
    NomeBusca := 'NORDESTE';
    FallbackCod := '2';
  end
  else
    Exit;

  Result := FallbackCod;
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := modulo_dados.fdbanco;
    if NomeBusca = 'NORTE' then
      Qry.SQL.Text := 'SELECT TOP 1 RegCodEstr FROM REGIAO WITH (NOLOCK) WHERE RegNome LIKE ''%NORTE%'' AND RegNome NOT LIKE ''%NORDESTE%'''
    else if NomeBusca = 'CENTRO' then
      Qry.SQL.Text := 'SELECT TOP 1 RegCodEstr FROM REGIAO WITH (NOLOCK) WHERE RegNome LIKE ''%CENTRO%'''
    else
      Qry.SQL.Text := 'SELECT TOP 1 RegCodEstr FROM REGIAO WITH (NOLOCK) WHERE RegNome LIKE ''%' + NomeBusca + '%''';
    Qry.Open;
    if not Qry.IsEmpty and (Trim(Qry.Fields[0].AsString) <> '') then
      Result := Trim(Qry.Fields[0].AsString);
  except
    // Mantém FallbackCod
  end;
  Qry.Free;
end;

// =============================================================================
// Helper: GarantirAutenticacaoAlvo
// =============================================================================
function Tfrmentidades.GarantirAutenticacaoAlvo(AAPI: TAlvoAPI): Boolean;
var
  vusucodapolo, vsenhaalvoplano, vsenhaalvocriptografada, senhaalvo: string;
  Qry: TFDQuery;
begin
  Result := False;
  if not Assigned(AAPI) then Exit;

  if Trim(frmprincipal.token_alvo) <> '' then
  begin
    AAPI.Token := frmprincipal.token_alvo;
    Exit(True);
  end;

  if Trim(frmprincipal.usucod_apolo) = '' then
  begin
    Qry := TFDQuery.Create(nil);
    try
      Qry.Connection := modulo_dados.fdbanco;
      Qry.SQL.Text := 'SELECT usucod_apolo, senha_alvo FROM USER_geoapolo_usuarios WITH (NOLOCK) WHERE usucod = :codigousuario';
      Qry.ParamByName('codigousuario').AsString := frmlogon.codigousuario;
      Qry.Open;
      if not Qry.IsEmpty and (Trim(Qry.FieldByName('usucod_apolo').AsString) <> '') and (Trim(Qry.FieldByName('senha_alvo').AsString) <> '') then
      begin
        frmprincipal.usucod_apolo := Qry.FieldByName('usucod_apolo').AsString;
        frmprincipal.senha_alvo   := Qry.FieldByName('senha_alvo').AsString;
      end;
    finally
      Qry.Free;
    end;
  end;

  if Trim(frmprincipal.usucod_apolo) = '' then
  begin
    vusucodapolo := UpperCase(InputBox('Usuário Alvo', 'Informe o usuário de acesso ao Alvo:', ''));
    if Trim(vusucodapolo) = '' then
    begin
      MessageDlg('Operação cancelada. Usuário alvo não foi informado.', mtWarning, [mbOK], 0);
      Exit(False);
    end;

    if not SolicitarSenhaMascarada('Senha do Usuário Alvo', 'Informe a senha do usuário alvo (' + vusucodapolo + '):', vsenhaalvoplano) then
    begin
      MessageDlg('Operação cancelada. Senha alvo não foi informada.', mtWarning, [mbOK], 0);
      Exit(False);
    end;

    vsenhaalvocriptografada := funcoes.criptografia(35, vsenhaalvoplano);
    Qry := TFDQuery.Create(nil);
    try
      Qry.Connection := modulo_dados.fdbanco;
      Qry.SQL.Text := 'UPDATE USER_geoapolo_usuarios SET usucod_apolo = :usucodapolo, senha_alvo = :senhaalvo WHERE usucod = :codigousuario';
      Qry.ParamByName('usucodapolo').AsString   := vusucodapolo;
      Qry.ParamByName('senhaalvo').AsString     := vsenhaalvocriptografada;
      Qry.ParamByName('codigousuario').AsString := frmlogon.codigousuario;
      Qry.ExecSQL;
    finally
      Qry.Free;
    end;

    frmprincipal.usucod_apolo := vusucodapolo;
    frmprincipal.senha_alvo   := vsenhaalvocriptografada;
  end;

  senhaalvo := funcoes.decriptografia(35, frmprincipal.senha_alvo, frmprincipal.senhaapp);
  if not AAPI.Login(frmprincipal.usucod_apolo, senhaalvo) then
  begin
    MessageDlg('Falha ao autenticar na API do Alvo!', mtError, [mbOK], 0);
    Exit(False);
  end;

  frmprincipal.token_alvo := AAPI.Token;
  Result := True;
end;

// =============================================================================
// Helper: GarantirContatoIntegradoAlvo
// Verifica se a entidade possui contato vinculado em USER_geoapolo_entidade_contato.
// Se possuir:
// 1. Busca dados do contato no GeoAlvo.
// 2. Pelo CPF, verifica se já existe no Alvo (via banco de dados ou entcod local).
// 3. Se já existir, traz o entcod do Alvo e vincula.
// 4. Se não encontrar, faz primeiro a integração do contato e vincula o código.
// =============================================================================
function Tfrmentidades.GarantirContatoIntegradoAlvo(const AGeoEntCod: string; API: TAlvoAPI; out AEntCodContato: string; out AErro: string): Boolean;
var
  Qry: TFDQuery;
  vGeoContato, vEntCodAlvo, vDocCPF, vDigitosCPF, vMsg, vTrat: string;
  EntContato: TEntidade;
begin
  Result := True;
  AErro := '';
  AEntCodContato := '';
  if Trim(AGeoEntCod) = '' then Exit;

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := modulo_dados.fdbanco;

    // 1. Verifica se a entidade tem contato vinculado
    Qry.SQL.Text :=
      'SELECT TOP 1 econt.EntCodContato, econt.entCod, uge.entcod AS uge_entcod ' +
      'FROM USER_geoapolo_entidade_contato econt WITH (NOLOCK) ' +
      'LEFT JOIN USER_geoapolo_entidade uge WITH (NOLOCK) ON econt.EntCodContato = uge.geoentcod ' +
      'WHERE econt.geoentcod = :geoentcod';
    Qry.ParamByName('geoentcod').AsString := AGeoEntCod;
    Qry.Open;

    if Qry.IsEmpty then
      Exit(True);

    vGeoContato := Trim(Qry.FieldByName('EntCodContato').AsString);
    if vGeoContato = '' then
      Exit(True);

    vEntCodAlvo := Trim(Qry.FieldByName('entCod').AsString);
    if vEntCodAlvo = '' then
      vEntCodAlvo := Trim(Qry.FieldByName('uge_entcod').AsString);

    // 2. Se ainda não possui entcod vinculado, busca no Alvo pelo CPF
    if vEntCodAlvo = '' then
    begin
      Qry.Close;
      Qry.SQL.Text :=
        'SELECT geonumerodocumento FROM USER_geoapolo_entidade_documentos WITH (NOLOCK) ' +
        'WHERE geoentcod = :geoentcod AND geotipodocumento LIKE ''%CPF%''';
      Qry.ParamByName('geoentcod').AsString := vGeoContato;
      Qry.Open;

      if not Qry.IsEmpty then
      begin
        vDocCPF := Trim(Qry.FieldByName('geonumerodocumento').AsString);
        vDigitosCPF := TRegEx.Replace(vDocCPF, '\D', '');

        if vDigitosCPF <> '' then
        begin
          Qry.Close;
          Qry.SQL.Text :=
            'SELECT TOP 1 entcod FROM entidades_apolo WITH (NOLOCK) ' +
            'WHERE entcpfcgc = :cpf ' +
            '   OR REPLACE(REPLACE(REPLACE(ISNULL(entcpfcgc,''''), ''.'', ''''), ''-'', ''''), ''/'', '''') = :cpf_digitos';
          Qry.ParamByName('cpf').AsString := vDocCPF;
          Qry.ParamByName('cpf_digitos').AsString := vDigitosCPF;
          Qry.Open;

          if not Qry.IsEmpty then
            vEntCodAlvo := Trim(Qry.FieldByName('entcod').AsString);
        end;
      end;
    end;

    // 3. Se já encontrou no Alvo, vincula localmente
    if vEntCodAlvo <> '' then
    begin
      Qry.Close;
      Qry.SQL.Text := 'UPDATE USER_geoapolo_entidade SET entcod = :entcod WHERE geoentcod = :geoentcod';
      Qry.ParamByName('entcod').AsString := vEntCodAlvo;
      Qry.ParamByName('geoentcod').AsString := vGeoContato;
      Qry.ExecSQL;

      Qry.Close;
      Qry.SQL.Text := 'UPDATE USER_geoapolo_entidade_contato SET entCod = :entcod WHERE geoentcod = :geoentcod AND EntCodContato = :geocontato';
      Qry.ParamByName('entcod').AsString := vEntCodAlvo;
      Qry.ParamByName('geoentcod').AsString := AGeoEntCod;
      Qry.ParamByName('geocontato').AsString := vGeoContato;
      Qry.ExecSQL;

      AEntCodContato := vEntCodAlvo;
      Exit(True);
    end;

    // 4. Não encontrou no Alvo: integra primeiro o contato no Alvo
    if not Self.MontarEntidadeParaEnvio(vGeoContato, EntContato, vTrat) then
    begin
      AErro := 'Não foi possível carregar os dados do contato vinculado (' + vGeoContato + ') para integração prévia.';
      Exit(False);
    end;

    EntContato.Operacao := 'I';
    EntContato.Codigo := '';

    if not API.InserirAlterarEntidade(EntContato, vMsg) then
    begin
      vEntCodAlvo := ExtrairEntCodResposta(vMsg);
      if vEntCodAlvo = '' then
      begin
        AErro := 'Falha ao integrar o contato vinculado (' + vGeoContato + ') no Alvo: ' + #13#10 + vMsg;
        Exit(False);
      end;
    end
    else
    begin
      vEntCodAlvo := ExtrairEntCodResposta(vMsg);
    end;

    if vEntCodAlvo <> '' then
    begin
      Self.AtualizarEntidadeExportada(vGeoContato, vEntCodAlvo, vTrat);

      Qry.Close;
      Qry.SQL.Text := 'UPDATE USER_geoapolo_entidade_contato SET entCod = :entcod WHERE geoentcod = :geoentcod AND EntCodContato = :geocontato';
      Qry.ParamByName('entcod').AsString := vEntCodAlvo;
      Qry.ParamByName('geoentcod').AsString := AGeoEntCod;
      Qry.ParamByName('geocontato').AsString := vGeoContato;
      Qry.ExecSQL;

      AEntCodContato := vEntCodAlvo;
      Exit(True);
    end
    else
    begin
      AErro := 'Contato vinculado (' + vGeoContato + ') integrado, mas o código retornado pelo Alvo não foi identificado.';
      Exit(False);
    end;

  finally
    Qry.Free;
  end;
end;

// =============================================================================
// Helper: MontarEntidadeParaEnvio
// Popula a estrutura TEntidade com todos os dados da entidade selecionada
// =============================================================================
function Tfrmentidades.MontarEntidadeParaEnvio(const AGeoEntCod: string; out AEntidade: TEntidade; out ATratCod: string): Boolean;
var
  vDocCPFCNPJ, vDocRGIE, vTipoWeb, vTratAbrev, vUF: string;
  vGenero, vEstCivil: string;
  i, a, numerocategorias: Integer;
  bTemGOCoord, bTemLoja: Boolean;

  function GetVal(ADataSet: TDataSet; const Names: array of string): string;
  var
    k: Integer;
    Fld: TField;
  begin
    Result := '';
    for k := Low(Names) to High(Names) do
    begin
      Fld := ADataSet.FindField(Names[k]);
      if (Fld <> nil) and (not Fld.IsNull) then
      begin
        Result := Trim(Fld.AsString);
        Exit;
      end;
    end;
  end;

begin
  Result := False;
  AEntidade := Default(TEntidade);
  ATratCod  := '';

  with modulo_dados do
  begin
    vDocCPFCNPJ := '';
    vDocRGIE    := '';
    fdquerysql18.Close;
    fdquerysql18.SQL.Clear;
    fdquerysql18.SQL.Text :=
      'SELECT geotipodocumento, geonumerodocumento ' +
      'FROM USER_geoapolo_entidade_documentos WITH (NOLOCK) ' +
      'WHERE geoentcod = :geoentcod';
    fdquerysql18.ParamByName('geoentcod').AsString := AGeoEntCod;
    if executaracao(fdquerysql18, fdbanco, true, dtsfdquerysql18) then
    begin
      fdquerysql18.First;
      while not fdquerysql18.EOF do
      begin
        if Pos('CPF', UpperCase(fdquerysql18.FieldByName('geotipodocumento').AsString)) > 0 then
          vDocCPFCNPJ := Trim(fdquerysql18.FieldByName('geonumerodocumento').AsString)
        else if Pos('RG', UpperCase(fdquerysql18.FieldByName('geotipodocumento').AsString)) > 0 then
          vDocRGIE := Trim(fdquerysql18.FieldByName('geonumerodocumento').AsString);
        fdquerysql18.Next;
      end;
    end;

    // Regra de Tipo de Tratamento:
    // M -> Sr.
    // F -> Casada / União Estável -> Sra., senão -> Srta.
    vGenero   := GetVal(fdqueryentidade, ['geoentgenero', 'entgenero']);
    vEstCivil := GetVal(fdqueryentidade, ['geoentestcivil', 'entestcivil', 'EntEstCivil']);

    vTratAbrev := Self.DeterminarTipoTratamento(vGenero, vEstCivil);
    if vTratAbrev <> '' then
      ATratCod := Self.ObterCodigoTipoTratamento(vTratAbrev)
    else
      ATratCod := GetVal(fdqueryentidade, ['tipotratcod', 'geotipotratcod']);

    AEntidade.Operacao               := 'I';
    AEntidade.Codigo                 := '';
    AEntidade.CodigoAlternativo      := AGeoEntCod;
    AEntidade.CodigoTipoTratamento   := ATratCod;
    AEntidade.Nome                   := GetVal(fdqueryentidade, ['geoentnome', 'entnome']);
    AEntidade.NomeFantasia           := GetVal(fdqueryentidade, ['geoentnomefantasia', 'entnomefant']);
    AEntidade.CodigoAtivEconomica    := 'null';
    AEntidade.CodigoOrigem           := GetVal(fdqueryentidade, ['geo_origcodestr', 'origcodestr']);
    AEntidade.EntidadeDesde          := GetVal(fdqueryentidade, ['geoentdesdedata', 'entdesdedata', 'EntDesdeData']);
    AEntidade.DataCadastro           := GetVal(fdqueryentidade, ['geoentdatacad', 'entdatacad', 'EntDataCad']);
    AEntidade.CodigoTipoLograd       := GetVal(fdqueryentidade, ['tipologradabrev', 'entlograd', 'tipolograd']);
    AEntidade.Endereco               := GetVal(fdqueryentidade, ['geoentender', 'entender']);
    AEntidade.NumeroEndereco         := GetVal(fdqueryentidade, ['geoenderno', 'entenderno']);
    AEntidade.NumeroEnderecoParImpar := funcoes.parouimpar(AEntidade.NumeroEndereco);
    AEntidade.ComplementoEndereco    := GetVal(fdqueryentidade, ['geoentendercomp', 'entendercomp']);
    AEntidade.Bairro                 := GetVal(fdqueryentidade, ['geoentbair', 'entbair']);
    AEntidade.CodigoCidade           := GetVal(fdqueryentidade, ['geocidcod', 'cidcod']);
    AEntidade.Cep                    := GetVal(fdqueryentidade, ['geoentcep', 'entcep']);
    AEntidade.Tipo                   := GetVal(fdqueryentidade, ['geotipofj', 'enttipofj']);
    AEntidade.CPFCNPJ                := vDocCPFCNPJ;
    AEntidade.RGIE                   := vDocRGIE;
    AEntidade.OrgaoExpedidor         := '';
    AEntidade.Agropecuarista         := 'Não';
    AEntidade.InscricaoAgropecuarista:= 'null';
    AEntidade.CaixaPostal            := GetVal(fdqueryentidade, ['geoentcxapost', 'entcxapost']);
    AEntidade.CodigoRegiao           := GetVal(fdqueryentidade, ['georegcodestr', 'regcodestr']);

    // Mapeamento da região conforme a UF do estado
    vUF := GetVal(fdqueryentidade, ['ufsigla']);
    if (vUF = '') and (AEntidade.CodigoCidade <> '') then
    begin
      fdquerysql18.Close; fdquerysql18.SQL.Clear;
      fdquerysql18.SQL.Text := 'SELECT TOP 1 ufsigla FROM user_geoapolo_cidades WITH (NOLOCK) WHERE geocidcod = :cid';
      fdquerysql18.ParamByName('cid').AsString := AEntidade.CodigoCidade;
      try
        if executaracao(fdquerysql18, fdbanco, true, dtsfdquerysql18) and (not fdquerysql18.IsEmpty) then
          vUF := Trim(fdquerysql18.FieldByName('ufsigla').AsString);
      finally
        fdquerysql18.Close;
      end;
    end;
    if vUF <> '' then
      AEntidade.CodigoRegiao := Self.ObterCodigoRegiaoPorUF(vUF);

    AEntidade.Conceito               := GetVal(fdqueryentidade, ['geoentconceito', 'entconceito']);
    AEntidade.CodigoCondPag          := 'null';
    AEntidade.AlteraCondicaoPagamento:= 'Sim';
    AEntidade.CodigoTipoCobranca     := GetVal(fdqueryentidade, ['geotipocobcod', 'tipocobcod', 'TipoCobCod']);
    if Trim(AEntidade.CodigoTipoCobranca) = '' then
      AEntidade.CodigoTipoCobranca   := '0000027';

    if (fdqueryentidade.FindField('entdataanivfund') <> nil) and (not fdqueryentidade.FieldByName('entdataanivfund').IsNull) then
      AEntidade.DataFundacao := DateTimeToISO8601(fdqueryentidade.FieldByName('entdataanivfund').AsDateTime)
    else if (fdqueryentidade.FindField('geoentdataanivfund') <> nil) and (not fdqueryentidade.FieldByName('geoentdataanivfund').IsNull) then
      AEntidade.DataFundacao := DateTimeToISO8601(fdqueryentidade.FieldByName('geoentdataanivfund').AsDateTime)
    else
      AEntidade.DataFundacao := '';

    AEntidade.CodigoCargo            := GetVal(fdqueryentidade, ['geocargocodestr', 'cargocodestr']);
    AEntidade.Genero                 := vGenero;
    AEntidade.CodigoStatus           := 'Ativo';
    AEntidade.CaracteristicaImovel   := 0;
    AEntidade.Natureza               := 'Consumidor';
    AEntidade.ComunicacaoEtiqueta    := 'Sim';
    AEntidade.ComunicacaoEmail       := 'Sim';
    AEntidade.ComunicacaoMalaDireta  := 'Não';
    AEntidade.ComunicacaoTelemarketing := 'Não';
    AEntidade.NumeroBanco            := '';
    AEntidade.NumeroAgBancaria       := '';
    AEntidade.NumeroContaCorrente    := '';
    if fdqueryentidade.FindField('USERValor_Contribuicao') <> nil then
      AEntidade.ValorContribuicao    := fdqueryentidade.FieldByName('USERValor_Contribuicao').AsFloat
    else
      AEntidade.ValorContribuicao    := 0.0;

    // Categorias
    if fdqueryentidade.FindField('categcodestr') <> nil then
    begin
      numerocategorias := funcoes.ContarVirgulas(fdqueryentidade.FieldByName('categcodestr').AsString);
      SetLength(AEntidade.Categorias, numerocategorias + 1);
      for a := 0 to numerocategorias do
      begin
        AEntidade.Categorias[a].Operacao         := 'I';
        AEntidade.Categorias[a].Codigo           := ExtrairConjunto(fdqueryentidade.FieldByName('categcodestr').AsString, a);
        AEntidade.Categorias[a].AtivaTabelaPreco := 'Sim';
      end;
    end
    else
      SetLength(AEntidade.Categorias, 0);

    // Se possui categoria de Grupo de Oração ou Coordenador (02.001...), adiciona também 08.009 (Loja)
    bTemGOCoord := False;
    bTemLoja    := False;
    for a := 0 to High(AEntidade.Categorias) do
    begin
      if Pos('02.001', AEntidade.Categorias[a].Codigo) = 1 then
        bTemGOCoord := True;
      if Trim(AEntidade.Categorias[a].Codigo) = '08.009' then
        bTemLoja := True;
    end;
    if bTemGOCoord and (not bTemLoja) then
    begin
      SetLength(AEntidade.Categorias, Length(AEntidade.Categorias) + 1);
      AEntidade.Categorias[High(AEntidade.Categorias)].Operacao         := 'I';
      AEntidade.Categorias[High(AEntidade.Categorias)].Codigo           := '08.009';
      AEntidade.Categorias[High(AEntidade.Categorias)].AtivaTabelaPreco := 'Sim';
    end;

    // Telefones
    fdquerysql1.Close; fdquerysql1.SQL.Clear;
    fdquerysql1.SQL.Text := 'SELECT * FROM USER_geoapolo_entidade_comunicacao WITH (NOLOCK) WHERE geoentcod = :geoentcod';
    fdquerysql1.ParamByName('geoentcod').AsString := AGeoEntCod;
    if executaracao(fdquerysql1, fdbanco, true, dtsfdquerysql1) then
    begin
      i := 0; fdquerysql1.First;
      while not fdquerysql1.EOF do
      begin
        SetLength(AEntidade.Telefones, i + 1);
        AEntidade.Telefones[i].Operacao    := 'I';
        AEntidade.Telefones[i].Sequencia   := i + 1;
        AEntidade.Telefones[i].Tipo        := fdquerysql1.FieldByName('geotipotelefone').AsString;
        AEntidade.Telefones[i].DDI         := '55';
        AEntidade.Telefones[i].DDD         := fdquerysql1.FieldByName('geotelefoneddd').AsString;
        AEntidade.Telefones[i].Numero      := fdquerysql1.FieldByName('geotelefonenumero').AsString;
        AEntidade.Telefones[i].NumeroRamal := '';
        AEntidade.Telefones[i].Principal   := IfThen(i = 0, 'Sim', 'Não');
        AEntidade.Telefones[i].Descricao   := '';
        AEntidade.Telefones[i].NFe         := 'Não';
        AEntidade.Telefones[i].NFSe        := 'Não';
        Inc(i); fdquerysql1.Next;
      end;
    end
    else
      SetLength(AEntidade.Telefones, 0);

    // Endereço
    SetLength(AEntidade.Enderecos, 1);
    AEntidade.Enderecos[0].Operacao                  := 'I';
    AEntidade.Enderecos[0].Sequencia                 := 1;
    AEntidade.Enderecos[0].CodigoEntidade            := AEntidade.CodigoAlternativo;
    AEntidade.Enderecos[0].CodigoEntidadeRelacionada := '';
    AEntidade.Enderecos[0].EnderecoEntrega           := 'Sim';
    AEntidade.Enderecos[0].EnderecoCobranca          := 'Não';
    AEntidade.Enderecos[0].EnderecoFaturamento       := 'Não';
    AEntidade.Enderecos[0].EnderecoColeta            := 'Não';
    AEntidade.Enderecos[0].Nome                      := AEntidade.Nome;
    AEntidade.Enderecos[0].Logradouro                := AEntidade.CodigoTipoLograd;
    AEntidade.Enderecos[0].Endereco                  := AEntidade.Endereco;
    AEntidade.Enderecos[0].NumeroEndereco            := AEntidade.NumeroEndereco;
    AEntidade.Enderecos[0].NumeroEnderecoParImpar    := '';
    AEntidade.Enderecos[0].ComplementoEndereco       := AEntidade.ComplementoEndereco;
    AEntidade.Enderecos[0].Bairro                    := AEntidade.Bairro;
    AEntidade.Enderecos[0].CodigoCidade              := AEntidade.CodigoCidade;
    AEntidade.Enderecos[0].Cep                       := AEntidade.Cep;
    AEntidade.Enderecos[0].TipoFisicaJuridica        := AEntidade.Tipo;
    AEntidade.Enderecos[0].CPFCNPJ                   := AEntidade.CPFCNPJ;
    AEntidade.Enderecos[0].RGIE                      := AEntidade.RGIE;
    AEntidade.Enderecos[0].OrgaoExpedidor            := AEntidade.OrgaoExpedidor;
    AEntidade.Enderecos[0].CaixaPostal               := '';
    AEntidade.Enderecos[0].Email                     := '';
    AEntidade.Enderecos[0].PaginaWeb                 := '';
    AEntidade.Enderecos[0].NomeContato               := '';
    AEntidade.Enderecos[0].TextoLivre                := '';
    AEntidade.Enderecos[0].DataValidadeInicial       := Now;
    AEntidade.Enderecos[0].DataValidadeFinal         := IncYear(Now, 100);
    AEntidade.Enderecos[0].EnderecoCertificado       := 'Não';

    // Contatos
    SetLength(AEntidade.Contatos, 0);
    fdquerysql3.Close; fdquerysql3.SQL.Clear;
    fdquerysql3.SQL.Text :=
      'SELECT econt.EntCodContato, econt.entCod, uge.entcod AS uge_entcod, uge.geoentnome, uge.tipolograd, uge.geoentender, ' +
      ' uge.geoenderno, uge.geoentendercomp, uge.geoentbair, uge.geocidcod, uge.geoentcep, ' +
      ' uge.geotipofj, econt.EntContatoCelular, econt.EntContatoTelefone' +
      ' FROM USER_geoapolo_entidade_contato econt WITH(NOLOCK)' +
      ' INNER JOIN USER_geoapolo_entidade uge WITH(NOLOCK) ON econt.EntCodContato = uge.geoentcod' +
      ' WHERE econt.geoentcod = :geoentcod';
    fdquerysql3.ParamByName('geoentcod').AsString := AGeoEntCod;
    if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
    begin
      fdquerysql3.First;
      if not fdquerysql3.EOF then
      begin
        SetLength(AEntidade.Contatos, 1);
        AEntidade.Contatos[0].Operacao       := 'I';
        AEntidade.Contatos[0].Codigo         := Trim(fdquerysql3.FieldByName('entCod').AsString);
        if AEntidade.Contatos[0].Codigo = '' then
          AEntidade.Contatos[0].Codigo       := Trim(fdquerysql3.FieldByName('uge_entcod').AsString);
        if AEntidade.Contatos[0].Codigo = '' then
          AEntidade.Contatos[0].Codigo       := Trim(fdquerysql3.FieldByName('EntCodContato').AsString);
        AEntidade.Contatos[0].Nome           := fdquerysql3.FieldByName('geoentnome').AsString;
        AEntidade.Contatos[0].Endereco       := fdquerysql3.FieldByName('geoentender').AsString;
        AEntidade.Contatos[0].NumeroEndereco := fdquerysql3.FieldByName('geoenderno').AsString;
        AEntidade.Contatos[0].Bairro         := fdquerysql3.FieldByName('geoentbair').AsString;
        AEntidade.Contatos[0].CodigoCidade   := fdquerysql3.FieldByName('geocidcod').AsString;
        AEntidade.Contatos[0].Cep            := fdquerysql3.FieldByName('geoentcep').AsString;
        AEntidade.Contatos[0].TipoFisicaJuridica := fdquerysql3.FieldByName('geotipofj').AsString;
        AEntidade.Contatos[0].Principal      := 'Sim';
        AEntidade.Contatos[0].CodigoStatus   := 'Ativo';
        SetLength(AEntidade.Contatos[0].Telefones, 1);
        AEntidade.Contatos[0].Telefones[0].Operacao  := 'I';
        AEntidade.Contatos[0].Telefones[0].Sequencia := 1;
        AEntidade.Contatos[0].Telefones[0].Numero    := fdquerysql3.FieldByName('EntContatoCelular').AsString;
        AEntidade.Contatos[0].Telefones[0].Principal := 'Sim';
      end;
    end;

    // Emails e Web
    SetLength(AEntidade.Emails, 0);
    fdquerysql3.Close; fdquerysql3.SQL.Clear;
    fdquerysql3.SQL.Text := 'SELECT * FROM USER_geoapolo_entidade_webcontato WITH (NOLOCK) WHERE geoentcod = :geoentcod';
    fdquerysql3.ParamByName('geoentcod').AsString := AGeoEntCod;
    if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
    begin
      i := 0; fdquerysql3.First;
      while not fdquerysql3.EOF do
      begin
        SetLength(AEntidade.Emails, i + 1);
        AEntidade.Emails[i].Operacao  := 'I';
        AEntidade.Emails[i].Sequencia := i + 1;
        vTipoWeb := '';
        if fdquerysql3.FindField('tipo_contato') <> nil then
          vTipoWeb := Trim(fdquerysql3.FieldByName('tipo_contato').AsString)
        else if fdquerysql3.FindField('entwebtipo') <> nil then
          vTipoWeb := Trim(fdquerysql3.FieldByName('entwebtipo').AsString);

        if (UpperCase(vTipoWeb) = 'COMERCIAL') or (UpperCase(vTipoWeb) = 'COM') or (Pos('COM', UpperCase(vTipoWeb)) = 1) then
          vTipoWeb := 'Comercial'
        else if (UpperCase(vTipoWeb) = 'FINANCEIRO') or (UpperCase(vTipoWeb) = 'FIN') or (Pos('FIN', UpperCase(vTipoWeb)) = 1) then
          vTipoWeb := 'Financeiro'
        else
          vTipoWeb := 'Pessoal';

        AEntidade.Emails[i].Tipo      := vTipoWeb;
        AEntidade.Emails[i].Email     := fdquerysql3.FieldByName('email').AsString;
        AEntidade.Emails[i].Principal := 'Sim';
        AEntidade.Emails[i].NFe       := 'Não';
        AEntidade.Emails[i].NFSe      := 'Não';
        AEntidade.Emails[i].Descricao := '';
        if fdquerysql3.FindField('website') <> nil then
          AEntidade.Emails[i].Url     := fdquerysql3.FieldByName('website').AsString
        else
          AEntidade.Emails[i].Url     := '';
        Inc(i); fdquerysql3.Next;
      end;
    end;
  end;

  Result := True;
end;

// =============================================================================
// Helper: AtualizarEntidadeExportada
// =============================================================================
procedure Tfrmentidades.AtualizarEntidadeExportada(const AGeoEntCod, ANovoEntCod, ATratCod: string);
var
  Qry: TFDQuery;
  vUsuCodApolo: string;
begin
  vUsuCodApolo := frmprincipal.usucod_apolo;
  if Trim(vUsuCodApolo) = '' then
    vUsuCodApolo := frmlogon.codigousuario;

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := modulo_dados.fdbanco;
    Qry.SQL.Text :=
      'UPDATE USER_geoapolo_entidade SET ' +
      '  entcod = CASE WHEN :entcod <> '''' THEN :entcod2 ELSE entcod END, ' +
      '  atualizou_apolo = ''S'', ' +
      '  usucod_atualizou_apolo = :usucod, ' +
      '  data_atualizou_apolo = GETDATE(), ' +
      '  geotipotratcod = CASE WHEN :tratcod <> '''' THEN :tratcod2 ELSE geotipotratcod END ' +
      'WHERE geoentcod = :geoentcod';
    Qry.ParamByName('entcod').AsString    := Trim(ANovoEntCod);
    Qry.ParamByName('entcod2').AsString   := Trim(ANovoEntCod);
    Qry.ParamByName('usucod').AsString    := vUsuCodApolo;
    Qry.ParamByName('tratcod').AsString   := Trim(ATratCod);
    Qry.ParamByName('tratcod2').AsString  := Trim(ATratCod);
    Qry.ParamByName('geoentcod').AsString := AGeoEntCod;
    Qry.ExecSQL;

    // Atualiza dataset em memória se o registro corrente for ele
    if modulo_dados.fdqueryentidade.Active and
       (modulo_dados.fdqueryentidade.FieldByName('geoentcod').AsString = AGeoEntCod) then
    begin
      try
        modulo_dados.fdqueryentidade.Edit;
        if Trim(ANovoEntCod) <> '' then
          modulo_dados.fdqueryentidade.FieldByName('entcod').AsString := ANovoEntCod;
        if modulo_dados.fdqueryentidade.FindField('atualizou_apolo') <> nil then
          modulo_dados.fdqueryentidade.FieldByName('atualizou_apolo').AsString := 'S';
        if (Trim(ATratCod) <> '') and (modulo_dados.fdqueryentidade.FindField('tipotratcod') <> nil) then
          modulo_dados.fdqueryentidade.FieldByName('tipotratcod').AsString := ATratCod;
        modulo_dados.fdqueryentidade.Post;
      except
      end;
    end;
  finally
    Qry.Free;
  end;
end;

// =============================================================================
// spbexportaentidadesClick — Exportação de entidade individual para o Alvo
// =============================================================================
procedure Tfrmentidades.spbexportaentidadesClick(Sender: TObject);
var
  Entidade: TEntidade;
  API: TAlvoAPI;
  vMensagem, vNovoEntCod, vTratCod: string;
  vEntCodContato, vErroContato: string;
begin
  Screen.Cursor := crSQLWait;
  try
    with frmentidades, modulo_dados do
    begin
      memobaseapolo.Clear;
      memoplataformasve.Clear;

      if cbobuscabanco.Text = 'GeoApolo' then
      begin
        if Pos('[PEND', UpperCase(fdqueryentidade.FieldByName('entobservacoes').AsString)) > 0 then
        begin
          MessageDlg('A exportação para o Alvo foi interrompida pois esta entidade possui [PENDÊNCIAS] registradas!', mtWarning, [mbOK], 0);
          Exit;
        end;

        if (fdqueryentidade.FieldByName('entcod').AsString = null) or (Trim(fdqueryentidade.FieldByName('entcod').AsString) = '') then
        begin
          ventcod := '';
          sql := 'SELECT geonumerodocumento FROM USER_geoapolo_entidade_documentos' +
                 ' WHERE geoentcod = :geoentcod' +
                 ' AND geotipodocumento like ' + QuotedStr('%CPF/CNPJ%');
          fdquerysql18.Close; fdquerysql18.SQL.Clear;
          fdquerysql18.SQL.Text := sql;
          fdquerysql18.ParamByName('geoentcod').AsString := fdqueryentidade.FieldByName('geoentcod').AsString;
          if executaracao(fdquerysql18, fdbanco, true, dtsfdquerysql18) then
          begin
            fdquerysql1.Close; fdquerysql1.SQL.Clear;
            fdquerysql1.SQL.Text := 'SELECT entcod FROM entidades_geoapolo WHERE entcpfcgc = :geonumerodocumento';
            fdquerysql1.ParamByName('geonumerodocumento').AsString := fdquerysql18.FieldByName('geonumerodocumento').AsString;
            if executaracao(fdquerysql1, fdbanco, true, dtsfdquerysql1) then
            begin
              ventcod := Trim(fdquerysql1.FieldByName('entcod').AsString);
              if ventcod <> '' then
              begin
                fdquerysql3.Close; fdquerysql3.SQL.Clear;
                fdquerysql3.SQL.Text := 'UPDATE USER_geoapolo_entidade SET entcod = :entcod WHERE geoentcod = :geoentcod';
                fdquerysql3.ParamByName('entcod').AsString    := ventcod;
                fdquerysql3.ParamByName('geoentcod').AsString := fdqueryentidade.FieldByName('geoentcod').AsString;
                executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3);
              end;
            end;
          end;
        end
        else
          ventcod := Trim(fdqueryentidade.FieldByName('entcod').AsString);

        vgeoentcod := fdqueryentidade.FieldByName('geoentcod').AsString;

        // Se já possui código no Alvo, abre tela de comparação lado a lado
        if Trim(ventcod) <> '' then
        begin
          panel2.Visible := True; panel2.Top := 85; panel2.Left := 24; panel2.BringToFront; panel2.Refresh;
          StringGrid1.Visible := True; StringGrid1.BringToFront;

          fdquerysql22.Close; fdquerysql22.SQL.Clear;
          fdquerysql22.SQL.Text := 'SELECT * FROM entidades_geoapolo WHERE geoentcod = :geoentcod';
          fdquerysql22.ParamByName('geoentcod').AsString := vgeoentcod;
          executaracao(fdquerysql22, fdbanco, true, dtsfdquerysql22);

          fdquerysql23.Close; fdquerysql23.SQL.Clear;
          fdquerysql23.SQL.Text := 'SELECT * FROM entidades_apolo WHERE entcod = :entcod';
          fdquerysql23.ParamByName('entcod').AsString := ventcod;
          executaracao(fdquerysql23, fdbanco, true, dtsfdquerysql23);

          MontarTelaComparacao(fdquerysql22, fdquerysql23);
          Exit;
        end
        else
        begin
          resp := MessageDlg('Confirma a exportação desta entidade para o Alvo ? (Y/N)', mtConfirmation, [mbYes, mbNo], 0);
          if resp = idYes then
          begin
            API := TAlvoAPI.Create('https://alvo.rccbrasil.org.br/api/');
            try
              if not Self.GarantirAutenticacaoAlvo(API) then
                Exit;

              if not Self.GarantirContatoIntegradoAlvo(vgeoentcod, API, vEntCodContato, vErroContato) then
              begin
                MessageDlg(vErroContato, mtError, [mbOK], 0);
                Exit;
              end;

              if not Self.MontarEntidadeParaEnvio(vgeoentcod, Entidade, vTratCod) then
              begin
                MessageDlg('Erro ao montar os dados da entidade para exportação.', mtError, [mbOK], 0);
                Exit;
              end;
              if (vEntCodContato <> '') and (Length(Entidade.Contatos) > 0) then
                Entidade.Contatos[0].Codigo := vEntCodContato;

              if Entidade.ValorContribuicao = 0.0 then
              begin
                if MessageDlg('Atenção: O Valor de Contribuição desta entidade é R$ 0,00 para sua conferência.' + #13#10 +
                              'Deseja realmente continuar com a exportação?', mtWarning, [mbYes, mbNo], 0) <> idYes then
                  Exit;
              end;

              if API.InserirAlterarEntidade(Entidade, vMensagem) then
              begin
                vNovoEntCod := ExtrairEntCodResposta(vMensagem);
                if vNovoEntCod <> '' then
                  ventcod := vNovoEntCod;

                Self.AtualizarEntidadeExportada(vgeoentcod, ventcod, vTratCod);
                MessageDlg('Entidade exportada com sucesso!' + #13#10 + vMensagem, mtInformation, [mbOK], 0);
              end
              else
              begin
                TFile.WriteAllText('c:\temp\dump_erro_export.json', vMensagem);
                MessageDlg('Erro ao exportar: ' + #13#10 + vMensagem, mtError, [mbOK], 0);
              end;
            finally
              API.Free;
            end;
          end;
        end;
      end
      else if cbobuscabanco.Text = 'Alvo' then
      begin
        MessageDlg('VOCÊ ESTÁ NA BASE ALVO E NÃO SERÁ PERMITIDA A EXPORTAÇÃO DA ENTIDADE !!!', mtError, [mbOK], 0);
        Exit;
      end;
    end;
  finally
    Screen.Cursor := crDefault;
  end;
end;

// =============================================================================
// consumirapi
// =============================================================================
function consumirapi(url: string): string;
var
  IdHTTP1   : TIdHTTP;
  SSLHandler: TIdSSLIOHandlerSocketOpenSSL;
begin
  IdHTTP1    := TIdHTTP.Create(nil);
  SSLHandler := TIdSSLIOHandlerSocketOpenSSL.Create(nil);
  try
    SSLHandler.SSLOptions.Method := sslvTLSv1_2;
    SSLHandler.SSLOptions.Mode   := sslmClient;
    IdHTTP1.IOHandler        := SSLHandler;
    IdHTTP1.HandleRedirects  := True;
    Result := IdHTTP1.Get(url);
    ShowMessage(Result);
  finally
    IdHTTP1.Free;
    SSLHandler.Free;
  end;
end;

procedure Tfrmentidades.spbsairClick(Sender: TObject);
begin
  Close;
  frmprincipal.Show;
end;

// =============================================================================
// spbsobrepoealvoClick - Atualiza a entidade existente no Alvo via API REST
// =============================================================================
procedure Tfrmentidades.spbsobrepoealvoClick(Sender: TObject);
var
  API: TAlvoAPI;
  Entidade: TEntidade;
  vMensagem, vTratCod, vGeoEntCod, vEntCod: string;
  vEntCodContato, vErroContato: string;
  i, idxCampo: Integer;
  valDecidido: string;
begin
  resp := MessageDlg('Confirma a sobreposição e envio destes dados para o Alvo ? (Sim / Não)',
                     mtConfirmation, [mbYes, mbNo], 0);
  if resp <> idYes then
    Exit;

  with modulo_dados do
  begin
    vGeoEntCod := Trim(fdqueryentidade.FieldByName('geoentcod').AsString);
    vEntCod    := Trim(ventcod);
    if vEntCod = '' then
      vEntCod  := Trim(fdqueryentidade.FieldByName('entcod').AsString);

    if vGeoEntCod = '' then
    begin
      MessageDlg('Código da entidade GeoApolo não identificado.', mtError, [mbOK], 0);
      Exit;
    end;

    Screen.Cursor := crSQLWait;
    API := TAlvoAPI.Create('https://alvo.rccbrasil.org.br/api/');
    try
      if not Self.GarantirAutenticacaoAlvo(API) then
        Exit;

      if not Self.GarantirContatoIntegradoAlvo(vGeoEntCod, API, vEntCodContato, vErroContato) then
      begin
        MessageDlg(vErroContato, mtError, [mbOK], 0);
        Exit;
      end;

      if not Self.MontarEntidadeParaEnvio(vGeoEntCod, Entidade, vTratCod) then
      begin
        MessageDlg('Não foi possível montar os dados da entidade para envio.', mtError, [mbOK], 0);
        Exit;
      end;
      if (vEntCodContato <> '') and (Length(Entidade.Contatos) > 0) then
        Entidade.Contatos[0].Codigo := vEntCodContato;

      if Entidade.ValorContribuicao = 0.0 then
      begin
        if MessageDlg('Atenção: O Valor de Contribuição desta entidade é R$ 0,00 para sua conferência.' + #13#10 +
                      'Deseja realmente continuar com a alteração no Alvo?', mtWarning, [mbYes, mbNo], 0) <> idYes then
          Exit;
      end;

      Entidade.Operacao := 'A'; // Alteração no Alvo
      Entidade.Codigo   := vEntCod;

    // Aplica as decisões tomadas na tela de comparação
    for i := 0 to GTotalDiferentes - 1 do
    begin
      idxCampo := GLinhasDiferentes[i];
      if (idxCampo < 0) or (idxCampo >= TOTAL_CAMPOS_MAPA) then
        Continue;

      // Se o usuário escolheu manter o valor do Alvo:
      if GDecisoes[i] = dlManterAlvo then
        valDecidido := StringGrid1.Cells[2, i + 1]
      else // Usar SVE (GeoApolo)
        valDecidido := StringGrid1.Cells[1, i + 1];

      case idxCampo of
        0: Entidade.Nome := valDecidido;
        1: Entidade.CPFCNPJ := valDecidido;
        2: Entidade.RGIE := valDecidido;
        3: Entidade.CodigoTipoLograd := valDecidido;
        4:
        begin
          Entidade.Endereco := valDecidido;
          if Length(Entidade.Enderecos) > 0 then
            Entidade.Enderecos[0].Endereco := valDecidido;
        end;
        5:
        begin
          Entidade.NumeroEndereco := valDecidido;
          if Length(Entidade.Enderecos) > 0 then
            Entidade.Enderecos[0].NumeroEndereco := valDecidido;
        end;
        6:
        begin
          Entidade.ComplementoEndereco := valDecidido;
          if Length(Entidade.Enderecos) > 0 then
            Entidade.Enderecos[0].ComplementoEndereco := valDecidido;
        end;
        7:
        begin
          Entidade.Bairro := valDecidido;
          if Length(Entidade.Enderecos) > 0 then
            Entidade.Enderecos[0].Bairro := valDecidido;
        end;
        8:
        begin
          Entidade.Cep := valDecidido;
          if Length(Entidade.Enderecos) > 0 then
            Entidade.Enderecos[0].Cep := valDecidido;
        end;
        9:
        begin
          Entidade.CodigoCidade := valDecidido;
          if Length(Entidade.Enderecos) > 0 then
            Entidade.Enderecos[0].CodigoCidade := valDecidido;
        end;
        13: Entidade.DataFundacao := valDecidido;
      end;
    end;

      if API.InserirAlterarEntidade(Entidade, vMensagem) then
      begin
        Self.AtualizarEntidadeExportada(vGeoEntCod, vEntCod, vTratCod);
        MessageDlg('Dados atualizados com sucesso no Alvo!' + #13#10 + vMensagem, mtInformation, [mbOK], 0);
        panel2.Visible := False;
      end
      else
      begin
        TFile.WriteAllText('c:\temp\dump_erro_sobrepoe_alvo.json', vMensagem);
        MessageDlg('Erro ao atualizar dados no Alvo: ' + #13#10 + vMensagem, mtError, [mbOK], 0);
      end;
    finally
      API.Free;
      Screen.Cursor := crDefault;
    end;
  end;
end;

// =============================================================================
// StringGrid1DrawCell
// =============================================================================
procedure Tfrmentidades.StringGrid1DrawCell(Sender: TObject; ACol, ARow: Integer;
  Rect: TRect; State: TGridDrawState);
var
  CellText : string;
  CellColor: TColor;
  TextRect_: TRect;
begin
  CellText := StringGrid1.Cells[ACol, ARow];

  if ARow = 0 then
  begin
    StringGrid1.Canvas.Brush.Color := $00DCDCDC;
    StringGrid1.Canvas.Font.Style  := [fsBold];
    StringGrid1.Canvas.Font.Size   := 10;
    StringGrid1.Canvas.Font.Color  := clBlack;
    StringGrid1.Canvas.FillRect(Rect);
    TextRect_ := Rect;
    InflateRect(TextRect_, -4, 0);
    DrawText(StringGrid1.Canvas.Handle, PChar(CellText), Length(CellText),
             TextRect_, DT_VCENTER or DT_SINGLELINE or DT_LEFT);
    Exit;
  end;

  if (ARow - 1) >= GTotalDiferentes then
  begin
    StringGrid1.Canvas.Brush.Color := clWindow;
    StringGrid1.Canvas.FillRect(Rect);
    Exit;
  end;

  StringGrid1.Canvas.Font.Style := [];
  StringGrid1.Canvas.Font.Size  := 10;
  StringGrid1.Canvas.Font.Color := clBlack;

  case GDecisoes[ARow - 1] of
    dlNenhuma   : CellColor := $00FFF3CD;
    dlManterSVE : CellColor := $00D4EDDA;
    dlManterAlvo: CellColor := $00CCE5FF;
  end;

  if ACol = 3 then
    case GDecisoes[ARow - 1] of
      dlNenhuma   : CellColor := $00FFE69C;
      dlManterSVE : CellColor := $00A8D5B5;
      dlManterAlvo: CellColor := $009FCCEE;
    end;

  if ACol = 0 then
    StringGrid1.Canvas.Font.Style := [fsItalic];

  StringGrid1.Canvas.Brush.Color := CellColor;
  StringGrid1.Canvas.FillRect(Rect);
  TextRect_ := Rect;
  InflateRect(TextRect_, -4, 0);
  DrawText(StringGrid1.Canvas.Handle, PChar(CellText), Length(CellText),
           TextRect_, DT_VCENTER or DT_SINGLELINE or DT_LEFT);
end;

// =============================================================================
// StringGrid1SelectCell
// =============================================================================
procedure Tfrmentidades.StringGrid1SelectCell(Sender: TObject; ACol, ARow: Integer;
  var CanSelect: Boolean);
var
  Pendentes, i: Integer;
begin
  if (ARow < 1) or not (ACol in [1, 2]) then Exit;
  if (ARow - 1) >= GTotalDiferentes then Exit;

  if ACol = 1 then
  begin
    GDecisoes[ARow - 1] := dlManterSVE;
    StringGrid1.Cells[3, ARow] := '◀ Usar SVE';
  end
  else
  begin
    GDecisoes[ARow - 1] := dlManterAlvo;
    StringGrid1.Cells[3, ARow] := 'Manter Alvo ▶';
  end;

  Pendentes := 0;
  for i := 0 to GTotalDiferentes - 1 do
    if GDecisoes[i] = dlNenhuma then Inc(Pendentes);

  if Pendentes = 0 then
  begin
    lblmensagemgeoapolo.Caption    := Format('✔ %d diferença(s) — todas decididas. Clique em Aplicar.',
                                             [GTotalDiferentes]);
    lblmensagemgeoapolo.Font.Color := clGreen;
    spbatualizaentidadeapolo.Enabled := True;
  end
  else
  begin
    lblmensagemgeoapolo.Caption    := Format('⚠ %d diferença(s) — %d pendente(s)',
                                             [GTotalDiferentes, Pendentes]);
    lblmensagemgeoapolo.Font.Color := clRed;
    spbatualizaentidadeapolo.Enabled := False;
  end;
  StringGrid1.Repaint;
end;

procedure Tfrmentidades.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Action := caFree;
end;

procedure Tfrmentidades.FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F10 then spbsair.Click;
  if Key = VK_INSERT then spbnovo.Click;
end;

// =============================================================================
// FormShow
// =============================================================================
procedure Tfrmentidades.FormShow(Sender: TObject);
begin
  InicializarFiltroAvancado;
  with modulo_dados do
  begin
    try
      integraentidadeapolo := verifica_integracao_entidades(frmprincipal.codigo_empresa);
      if ((integraentidadeapolo = 'Não Integra') or (integraentidadeapolo = 'Mescla')) and
         (cbobuscabanco.Text = 'GeoApolo') then
      begin
        carrega_lista_entidades('GeoApolo', 'Consulta', '');
        ConfigurarGridCompleto('GeoApolo');
      end
      else if ((integraentidadeapolo = 'Integra') or (integraentidadeapolo = 'Mescla')) and
              (cbobuscabanco.Text = 'Alvo') then
        cbobuscabanco.Items.Add('Alvo');

      StatusBar1.Panels[1].Text := configura_statusbar('s');
      StatusBar1.Panels[3].Text := configura_statusbar('s');
      StatusBar1.Panels[5].Text := frmprincipal.nomeserversql;
    except
      on E: Exception do
        ShowMessage('Erro ao inicializar formulário: ' + E.Message);
    end;
  end;
end;

// =============================================================================
// mnugravaconfiguracoesClick
// =============================================================================
procedure Tfrmentidades.mnugravaconfiguracoesClick(Sender: TObject);
begin
  if cbobuscabanco.Text = 'Alvo' then
  begin
    grava_configuracoes_grids(frmentidades, 'entidades_apolo', gridentidades,
      'gridentidades', frmlogon.nomeusuario, modulo_dados.dtsfdqueryentidade);
    grava_config_telabusca('entidades_apolo', cbocampo.Text, cbordem.Text,
      Copy(Trim(vordem), 1, 1), frmentidades);
  end
  else if cbobuscabanco.Text = 'GeoApolo' then
  begin
    grava_configuracoes_grids(frmentidades, 'entidades_geoapolo', gridentidades,
      'gridentidades', frmlogon.nomeusuario, modulo_dados.dtsfdqueryentidade);
    grava_config_telabusca('entidades_geoapolo', cbocampo.Text, cbordem.Text,
      Copy(Trim(vordem), 1, 1), frmentidades);
  end;
end;

procedure Tfrmentidades.rdgcrescenteClick(Sender: TObject);
begin
  if rdgcrescente.Checked then
  begin
    vordem := ' ASC';
    rdgdecrescente.Checked := False;
  end;
end;

procedure Tfrmentidades.rdgdecrescenteClick(Sender: TObject);
begin
  if rdgdecrescente.Checked then
  begin
    vordem := ' DESC';
    rdgcrescente.Checked := False;
    rdgcrescente.Refresh;
  end;
end;

// =============================================================================
// carrega_lista_entidades — VERSÃO CORRIGIDA
//
// CORREÇÕES APLICADAS:
//   FIX 1: FetchOptions configurado para busca sob demanda (fmOnDemand)
//   FIX 2: CommandTimeout = 180 para esta query pesada
//   FIX 3: Campo padrão 'entnome' quando cbocampo está vazio
//   FIX 4: AG_BANCARIA com WITH(NOLOCK) — estava sem hint
//   FIX 5: ENT_CATEG e CATEGORIA com WITH(NOLOCK) dentro do OUTER APPLY
//   FIX 6: USER_geoapolo_entcateg e USER_geoapolo_categoria com WITH(NOLOCK)
//   FIX 7: Verificação da view com try/finally + IsEmpty (não usa executaracao)
//   FIX 8: Parâmetro :procurarpor só atribuído quando realmente existe na query
// =============================================================================
function carrega_lista_entidades(basededados: string; tipo_pesquisa: string; filtro: string): string;
var
  sqlview: string;
  i: integer;
  vCampoBusca: string;
begin
  with frmentidades, modulo_dados do
  begin
    if FCarregandoEntidades then Exit;
    FCarregandoEntidades := True;
    try
      if rdgcrescente.Checked then
      begin
        vordem := ' ASC';
        rdgdecrescente.Checked := False;
      end
      else if rdgdecrescente.Checked then
      begin
        vordem := ' DESC';
        rdgcrescente.Checked := False;
      end;

      // Fecha dataset antes de qualquer operação para liberar locks
      if fdqueryentidade.Active then
        fdqueryentidade.Close;

      // FIX 1: busca sob demanda — não carrega tudo antes de exibir
      fdqueryentidade.FetchOptions.Mode       := fmOnDemand;
      fdqueryentidade.FetchOptions.RowsetSize := 50;
      fdqueryentidade.FetchOptions.RecsMax    := -1;

      // FIX 2: timeout maior para queries pesadas
      //fdqueryentidade.CommandTimeout := 180;
      fdbanco.Params.Values['CommandTimeout'] := '360';

      // FIX 3: campo padrão quando cbocampo está vazio
      if Trim(cbocampo.Text) = '' then
        vCampoBusca := 'entnome'
      else
        vCampoBusca := cbocampo.Text;

      // ===================================================================
      // BASE ALVO
      // ===================================================================
      if ((frmentidades.integraentidadeapolo = 'Integra') or (frmentidades.integraentidadeapolo = 'Mescla')) and  (cbobuscabanco.Text = 'Alvo') then
      begin
        if tipo_pesquisa = 'Consulta' then
        begin
          // Definição da view — usada apenas para (re)criação se necessário
          sqlview :=
            'SELECT e.entcod, e.tipotratcod, e.entnome, e.EntNomeFant, e.EntDesdeData, e.EntDataCad,' +
            ' e.EntLograd, e.entender, e.entenderno, e.entbair, e.entendercomp,' +
            ' cid.cidcod, cid.cidnomecomp, cid.ufsigla, e.EntCep, e.EntTipoFJ, e.EntCxaPost,' +
            ' e.RegCodEstr, r.regnome, e.EntConceito, e.EntDataAnivFund, e.CargoCodEstr, car.cargonome,' +
            ' e.EntGenero, e.EntLocCobrancaOMesmo, e.EntLocEntregaOMesmo, e.EntEstCivil,' +
            ' e.EntNomePai, e.EntNomeMae, e.EntPossuiFilho, e.EntMoraCom,' +
            ' e.EntGrauEscol, e.AtivEconCodEstr, ae.ativeconnome, e.OrigCodEstr, o.orignome,' +
            ' categorias_alvo.categcodestr, categorias_alvo.categorias as CategNome,' +
            ' e.TipoCobCod, tc.tipocobnome, e.bconum, bco.bconome,' +
            ' e.AgNum, ag.AgNome as AgNome, e.EntBcoAgCCorNum,' +
            ' ue.USERDia_Debito_CC, ue.USERGeraCarne, ue.USERDiocese_id,' +
            ' ue.USERNomeDiocese, ue.USERrecebelembretedoacao,' +
            ' e1.entvalcontrib as USERValor_Contribuicao,' +
            ' e.EntCpfCgc, e.EntRgIe, e.entendernopi, ue.UserFalecido,' +
            ' uge.geoobservacoes as Entobservacoes,' +
            ' uge.geoentcod, uge.atualizou_apolo, uge.usucod_atualizou_apolo, e.enttransporteomesmo' +
            ' FROM entidade e WITH(NOLOCK)' +
            ' INNER JOIN entidade1 e1 WITH(NOLOCK) ON e.entcod = e1.entcod' +
            ' INNER JOIN cidade cid WITH(NOLOCK) ON e.cidcod = cid.cidcod' +
            ' LEFT JOIN REGIAO reg WITH(NOLOCK) ON e.RegCodEstr = reg.RegCodEstr' +
            ' LEFT JOIN cargo car WITH(NOLOCK) ON e.CargoCodEstr = car.CargoCodEstr' +
            ' LEFT JOIN origem o WITH(NOLOCK) ON e.OrigCodEstr = o.OrigCodEstr' +
            ' LEFT JOIN ativ_economica ae WITH(NOLOCK) ON e.ativeconcodestr = ae.ativeconcodestr' +
            // FIX 5: WITH(NOLOCK) dentro do OUTER APPLY
            ' OUTER APPLY (' +
            '   SELECT STRING_AGG(cat.categnome, ' + QuotedStr(',') + ') AS categorias,' +
            '          STRING_AGG(ec.categcodestr, ' + QuotedStr(',') + ') AS categcodestr' +
            '   FROM ENT_CATEG ec WITH(NOLOCK)' +
            '   INNER JOIN CATEGORIA cat WITH(NOLOCK) ON ec.categcodestr = cat.categcodestr' +
            '   WHERE ec.entcod = e.entcod' +
            ' ) as categorias_alvo' +
            ' LEFT JOIN tipo_cobranca tc WITH(NOLOCK) ON e.TipoCobCod = tc.TipoCobCod' +
            ' LEFT JOIN banco bco WITH(NOLOCK) ON e.bconum = bco.BcoNum' +
            // FIX 4: AG_BANCARIA com WITH(NOLOCK)
            ' LEFT JOIN AG_BANCARIA ag WITH(NOLOCK) ON e.agnum = ag.AgNum AND bco.bconum = ag.bconum' +
            ' INNER JOIN u_entidade ue WITH(NOLOCK) ON e.entcod = ue.EntCod' +
            ' LEFT JOIN user_geoapolo_entidade uge WITH(NOLOCK) ON e.entcod = uge.entcod' +
            ' LEFT JOIN regiao r WITH(NOLOCK) ON e.regcodestr = r.regcodestr';

          // FIX 7: verificação segura da view
          fdquerysql18.Close;
          fdquerysql18.sql.clear;
          fdquerysql18.sql.Text := 'SELECT name FROM sys.views WHERE name = :pview ';
          fdquerysql18.parambyname('pview').asstring :=  'entidades_apolo';

          try
            fdquerysql18.Open;
            if fdquerysql18.IsEmpty then
              cria_view(sqlview, 'entidades_apolo', 'Apolo', frmentidades);
          finally
            fdquerysql18.Close;
          end;

          // Consulta final usando a view
          sqlview :=
            'SELECT TOP 50 * FROM entidades_apolo e WITH(NOLOCK)' +
            ' WHERE e.' + vCampoBusca + ' LIKE :procurarpor' +
            ' AND SUBSTRING(e.categcodestr, 1, 2) IN (' + QuotedStr('02') + ', ' + QuotedStr('03') + ')' +
            ' ORDER BY e.entnome ASC';
        end
        else if tipo_pesquisa = 'Especifica' then
        begin
          if cbordem.Items.Count = 0 then
            cbordem.Items.Add('entnome');

          if SameText(vCampoBusca, 'categcodestr') or SameText(vCampoBusca, 'geocategcodestr') then
            sqlview :=
              'SELECT * FROM entidades_apolo e WITH(NOLOCK)' +
              ' WHERE EXISTS (SELECT 1 FROM ENT_CATEG ec WITH (NOLOCK) WHERE ec.entcod = e.entcod AND ec.categcodestr = :procurarpor_exato)' +
              ' AND SUBSTRING(e.categcodestr, 1, 2) IN (' + QuotedStr('02') + ', ' + QuotedStr('03') + ')' +
              ' ORDER BY e.' + cbordem.Text
          else
            sqlview :=
              'SELECT * FROM entidades_apolo e WITH(NOLOCK)' +
              ' WHERE e.' + vCampoBusca + ' LIKE :procurarpor' +
              ' AND SUBSTRING(e.categcodestr, 1, 2) IN (' + QuotedStr('02') + ', ' + QuotedStr('03') + ')' +
              ' ORDER BY e.' + cbordem.Text;
          if rdgcrescente.Checked then sqlview := sqlview + ' ASC'
          else if rdgdecrescente.Checked then sqlview := sqlview + ' DESC';
        end;

        fdqueryentidade.SQL.Clear;
        fdqueryentidade.SQL.Text := sqlview;
        // FIX 8: parâmetro sempre presente nas queries do Alvo
        if (SameText(vCampoBusca, 'categcodestr') or SameText(vCampoBusca, 'geocategcodestr')) then
          fdqueryentidade.ParamByName('procurarpor_exato').AsString := Trim(lblprocurarpor.Text)
        else
          fdqueryentidade.ParamByName('procurarpor').AsString := '%' + lblprocurarpor.Text + '%';

        if executaracao(fdqueryentidade, fdbanco, True, dtsfdqueryentidade) then
        begin
          gridentidades.DataSource := dtsfdqueryentidade;
          cbocampo.Items.Clear; cbordem.Items.Clear;
          for i := 0 to fdqueryentidade.Fields.Count - 1 do
          begin
            cbocampo.Items.Add(fdqueryentidade.Fields[i].FieldName);
            cbordem.Items.Add(fdqueryentidade.Fields[i].FieldName);
          end;
          carrega_config('entidades_apolo', frmentidades, cbocampo, cbordem,
                         rdgcrescente, rdgdecrescente);
          funcoes.AjustaLarguraColunas(gridentidades);
          configura_grid('entidades_apolo', frmentidades, frmlogon.codigousuario,
                         'gridentidades', gridentidades, modulo_dados.dtsfdqueryentidade);
          lblnentidadeslistadas.Caption := IntToStr(fdqueryentidade.RecordCount);
          lblnentidadeslistadas.Refresh;
          cbobuscabanco.Refresh;
          gridentidades.Refresh;
        end;
        gridentidades.SetFocus;
      end

      // ===================================================================
      // BASE GEOAPOLO
      // ===================================================================
      else if ((frmentidades.integraentidadeapolo = 'Não Integra') or (frmentidades.integraentidadeapolo = 'Mescla')) and (cbobuscabanco.Text = 'GeoApolo') then
      begin
        sql :=
          'SELECT uge.entcod, uge.geotipotratcod as tipotratcod,' +
          ' uge.geoentnome as entnome, uge.geoentnomefantasia as entnomefant,' +
          ' uge.geoentdesdedata as EntDesdeData, uge.geoentdatacad as entdatacad,' +
          ' ugtl.tipologradabrev as entlograd,' +
          ' uge.geoentender as entender, uge.geoenderno as entenderno,' +
          ' uge.geoenderno as ententnopi, uge.geoentbair as entbair,' +
          ' uge.geoentendercomp as entendercomp, cid.geocidcod as cidcod,' +
          ' cid.cidnomecomp, cid.ufsigla, uge.geoentcep as entcep,' +
          ' uge.geotipofj as enttipofj, uge.geoentcxapost as entcxapost,' +
          ' uge.georegcodestr as regcodestr, ugrp.geo_regnome as regnome,' +
          ' uge.geoentconceito as entconceito, uge.geoentdataanivfund as entdataanivfund,' +
          ' uge.geocargocodestr as cargocodestr, car.geocargonome as cargonome,' +
          ' uge.geoentgenero as entgenero,' +
          ' uge.geoentloccobrancaomesmo as entloccobrancaomesmo,' +
          ' uge.geoentlocentregaomesmo as EntLocEntregaOMesmo,' +
          ' uge.geoenttransporteomesmo as EntTransporteOMesmo,' +
          ' uge.geoentestcivil as EntEstCivil,' +
          ' uge.geoentnomepai as EntNomePai, uge.geoentnomemae as EntNomeMae,' +
          ' uge.geoentpossuifilho as EntPossuiFilho, uge.geoentmoracom as EntMoraCom,' +
          ' ggrau.grau_escolaridade as EntGrauEscol,' +
          ' gae.AtivEconcodestr, ugate.ativeconnome,' +
          ' ugoe.geo_origcodestr as OrigCodEstr, ugo.geo_orignome as OrigNome,' +
          ' categorias_apolo.categcodestr as Categcodestr, categorias_apolo.categnome,' +
          ' uge.geotipocobcod as TipoCobCod, ugtc.geotipocobnome as TipoCobNome,' +
          ' uge.geobconum as bconum, ugb.geobconome as bconome,' +
          ' uge.geoagnum as agnum, ugab.geoagnome as AgNome,' +
          ' uge.geoconta as EntBcoAgCCorNum,' +
          ' uge.geodia_contribuicao as USERDia_Debito_CC,' +
          ' uge.geogerarcarne as USERgeraCarne,' +
          ' uge.geodioceseid as UserDiocese_id, udc.nome as USERNomeDiocese,' +
          ' uge.georecebelembrete as USERrecebelembretedoacao,' +
          ' uge.geovalorcontribuicao as USERValor_Contribuicao,' +
          ' MAX(CASE WHEN uged.geotipodocumento = ' + QuotedStr('CPF/CNPJ') +
          '   THEN uged.geonumerodocumento END) AS EntCpfCgc,' +
          ' MAX(CASE WHEN uged.geotipodocumento = ' + QuotedStr('RG/IE') +
          '   THEN uged.geonumerodocumento END) AS EntRgIe,' +
          ' uge.geoentcod, uge.geofalecido as USERFalecido,' +
          ' uge.geoobservacoes as Entobservacoes,' +
          ' uge.usucod_atualizou_apolo as atualizou_apolo' +
          ' FROM user_geoapolo_entidade uge WITH(NOLOCK)' +
          ' LEFT JOIN USER_geoapolo_tipologradouro ugtl WITH(NOLOCK) ON uge.tipolograd = ugtl.tipolograd' +
          ' INNER JOIN user_geoapolo_cidades cid WITH(NOLOCK) ON uge.geocidcod = cid.geoCidCod' +
          ' LEFT JOIN USER_geoapolo_cargos car WITH(NOLOCK) ON uge.geocargocodestr = car.geocargocodestr' +
          ' LEFT JOIN USER_geoapolo_grauescolaridade ggrau WITH(NOLOCK) ON uge.codigo_grauescolaridade = ggrau.codigo_grauescolaridade' +
          ' LEFT JOIN USER_geoapolo_entidade_ativecon gae WITH(NOLOCK) ON uge.geoentcod = gae.geoentcod' +
          ' LEFT JOIN USER_geoapolo_atividade_economica ugate WITH(NOLOCK) ON gae.ativeconcodestr = ugate.ativeconcodestr' +
          ' LEFT JOIN USER_geoapolo_origens_entidade ugoe WITH(NOLOCK) ON uge.geoentcod = ugoe.geoentcod' +
          ' INNER JOIN USER_geoapolo_origens ugo WITH(NOLOCK) ON ugoe.geo_origcodestr = ugo.geo_origcodestr' +
          // FIX 6: WITH(NOLOCK) dentro do OUTER APPLY GeoApolo
          ' OUTER APPLY (' +
          '   SELECT STRING_AGG(gcat.geocategnome, ' + QuotedStr(', ') + ') AS categnome,' +
          '          STRING_AGG(ugec.geocategcodestr, ' + QuotedStr(',') + ') AS categcodestr' +
          '   FROM USER_geoapolo_entcateg ugec WITH(NOLOCK)' +
          '   INNER JOIN USER_geoapolo_categoria gcat WITH(NOLOCK) ON ugec.geocategcodestr = gcat.geocategcodestr' +
          '   WHERE ugec.geoentcod = uge.geoentcod' +
          ' ) as categorias_apolo' +
          ' LEFT JOIN USER_geoapolo_tipo_cobranca ugtc WITH(NOLOCK) ON uge.geotipocobcod = ugtc.geotipocobcod' +
          ' LEFT JOIN USER_geoapolo_bancos ugb WITH(NOLOCK) ON uge.geobconum = ugb.geobconum' +
          ' LEFT JOIN USER_geoapolo_agbancaria ugab WITH(NOLOCK) ON uge.geoagnum = ugab.geoagnum AND ugab.geobconum = ugb.geobconum' +
          ' LEFT JOIN USERdioceses_CNBB udc WITH(NOLOCK) ON uge.geodioceseid = udc.id AND udc.estado_id = (SELECT uecnbb.USERiD FROM USEREstado_CNBB uecnbb WITH(NOLOCK) WHERE uecnbb.USERsigla = cid.ufsigla)' +
          ' LEFT JOIN USER_geoapolo_entidade_documentos uged WITH(NOLOCK) ON uge.geoentcod = uged.geoentcod' +
          ' LEFT JOIN USER_geoapolo_regiao_pais ugrp WITH(NOLOCK) ON uge.georegcodestr = ugrp.geo_regnome' +
          ' GROUP BY' +
          '   uge.entcod, uge.geotipotratcod, uge.geoentnome, uge.geoentnomefantasia,' +
          '   uge.geoentdesdedata, uge.geoentdatacad, ugtl.tipologradabrev,' +
          '   uge.geoentender, uge.geoenderno, uge.geoentbair, uge.geoentendercomp,' +
          '   cid.geocidcod, cid.cidnomecomp, cid.ufsigla, uge.geoentcep,' +
          '   uge.geotipofj, uge.geoentcxapost, uge.georegcodestr, uge.geoentconceito,' +
          '   uge.geoentdataanivfund, uge.geocargocodestr, car.geocargonome,' +
          '   uge.geoentgenero, uge.geoentloccobrancaomesmo, uge.geoentlocentregaomesmo,' +
          '   uge.geoenttransporteomesmo, uge.geoentestcivil, uge.geoentnomepai,' +
          '   uge.geoentnomemae, uge.geoentpossuifilho, uge.geoentmoracom,' +
          '   ggrau.grau_escolaridade, gae.ativeconcodestr, ugoe.geo_origcodestr,' +
          '   ugo.geo_orignome, categorias_apolo.categcodestr, categorias_apolo.categnome,' +
          '   uge.cidcodapolo, uge.geotipocobcod, ugtc.geotipocobnome,' +
          '   uge.geobconum, ugb.geobconome, uge.geoagnum, ugab.geoagnome,' +
          '   uge.geoconta, uge.geodia_contribuicao, uge.geogerarcarne,' +
          '   uge.geodioceseid, udc.nome, uge.georecebelembrete, uge.geovalorcontribuicao,' +
          '   uge.geoobservacoes, uge.tipolograd, uge.geoentcod, uge.geofalecido,' +
          '   uge.usucod_atualizou_apolo, ugate.ativeconnome, ugrp.geo_regnome';
        // FIX 7: verificação segura da view GeoApolo
        fdquerysql18.Close;
        fdquerysql8.sql.clear;
        fdquerysql18.SQL.Text := 'SELECT name FROM sys.views WHERE name = :nomedaview';
        fdquerysql18.parambyname('nomedaview').asstring := 'entidades_geoapolo';
        try
          if not executaracao(fdquerysql18, fdbanco, true, dtsfdquerysql18) then
            cria_view(sql, 'entidades_geoapolo', 'GeoApolo', frmentidades);
        finally
          fdquerysql18.Close;
        end;

        if tipo_pesquisa = 'Consulta' then
        begin
          if filtro = 'JAEXPORTADA' then
            begin
              sqlview :=
                'SELECT * FROM entidades_geoapolo e WITH(NOLOCK)' +
                ' INNER JOIN USER_geoapolo_entidade_documentos uged WITH(NOLOCK)' +
                '   ON e.entcpfcgc = uged.geonumerodocumento AND uged.geotipodocumento = ' + QuotedStr('CPF/CNPJ') +
                ' INNER JOIN user_geoapolo_entidade ue WITH(NOLOCK) ON e.entcpfcgc = ue.entcpfcgc' +
                ' WHERE ue.atualizou_apolo = ' + QuotedStr('S');
            end
          else
          begin
              sqlview :=
                'SELECT * FROM entidades_geoapolo e WITH(NOLOCK)' +
               ' INNER JOIN USER_geoapolo_entidade_documentos uged WITH(NOLOCK)' +
                '   ON e.entcpfcgc = uged.geonumerodocumento AND uged.geotipodocumento = ' + QuotedStr('CPF/CNPJ') +
                ' INNER JOIN user_geoapolo_entidade ue WITH(NOLOCK) ON e.geoentcod = ue.geoentcod' +
                ' WHERE ue.atualizou_apolo = ' + QuotedStr('N');
            end;
            sqlview := sqlview +
              ' ORDER BY CASE WHEN ue.atualizou_apolo = ' + QuotedStr('N') +
              ' AND e.Entobservacoes IS NULL THEN 0 ELSE 1 END';
          end
        else if tipo_pesquisa = 'Especifica' then
        begin
          if cbordem.Items.Count = 0 then
            begin
              cbordem.Items.Add('geoentnome');
              cbordem.ItemIndex := 0;
            end;
          if SameText(vCampoBusca, 'categcodestr') or SameText(vCampoBusca, 'geocategcodestr') then
            sqlview :=
              'SELECT * FROM entidades_geoapolo e WITH(NOLOCK)' +
              ' INNER JOIN user_geoapolo_entidade ue WITH(NOLOCK) ON e.geoentcod = ue.geoentcod' +
              ' WHERE EXISTS (SELECT 1 FROM USER_geoapolo_entcateg uec WITH (NOLOCK) WHERE uec.geoentcod = e.geoentcod AND uec.geocategcodestr = :procurarpor_exato)' +
              ' ORDER BY CASE WHEN ue.atualizou_apolo = ' + QuotedStr('N') +
              ' AND e.Entobservacoes IS NULL THEN 0 ELSE 1 END'
          else
            sqlview :=
              'SELECT * FROM entidades_geoapolo e WITH(NOLOCK)' +
              ' INNER JOIN user_geoapolo_entidade ue WITH(NOLOCK) ON e.geoentcod = ue.geoentcod' +
              ' WHERE e.' + vCampoBusca + ' LIKE :procurarpor' +
              ' ORDER BY CASE WHEN ue.atualizou_apolo = ' + QuotedStr('N') +
              ' AND e.Entobservacoes IS NULL THEN 0 ELSE 1 END';
        end;

        fdqueryentidade.SQL.Clear;
        fdqueryentidade.SQL.Text := sqlview;

        // FIX 8: parâmetro só atribuído quando existe na query
        if tipo_pesquisa = 'Especifica' then
        begin
          if (SameText(vCampoBusca, 'categcodestr') or SameText(vCampoBusca, 'geocategcodestr')) then
            fdqueryentidade.ParamByName('procurarpor_exato').AsString := Trim(lblprocurarpor.Text)
          else
            fdqueryentidade.ParamByName('procurarpor').AsString := '%' + lblprocurarpor.Text + '%';
        end;

        if executaracao(fdqueryentidade, fdbanco, True, dtsfdqueryentidade) then
        begin
          dtsfdqueryentidade.DataSet := fdqueryentidade;
          gridentidades.DataSource   := dtsfdqueryentidade;
          cbocampo.Items.Clear; cbordem.Items.Clear;
          for i := 0 to fdqueryentidade.Fields.Count - 1 do
          begin
            cbocampo.Items.Add(fdqueryentidade.Fields[i].FieldName);
            cbordem.Items.Add(fdqueryentidade.Fields[i].FieldName);
          end;
          carrega_config('entidades_geoapolo', frmentidades, cbocampo, cbordem,
                         rdgcrescente, rdgdecrescente);
          funcoes.AjustaLarguraColunas(gridentidades);
          configura_grid('entidades_geoapolo', frmentidades, frmlogon.codigousuario,
                         'gridentidades', gridentidades, modulo_dados.dtsfdqueryentidade);
          lblnentidadeslistadas.Caption := IntToStr(fdqueryentidade.RecordCount);
          lblnentidadeslistadas.Refresh;
        end;
        gridentidades.Refresh;
        gridentidades.SetFocus;
      end;

    except
      on E: Exception do
      begin
        FCarregandoEntidades := False;
        ShowMessage('Erro ao carregar entidades: ' + E.Message);
        Exit;
      end;
    end;
    FCarregandoEntidades := False;
  end;
end;

// =============================================================================
// gridentidadesDblClick — CORRIGIDO: Show antes de preencher campos
// =============================================================================
procedure Tfrmentidades.gridentidadesDblClick(Sender: TObject);
var
  vrecebelembrete, vgeracarne, vestadocivil, vfalecido, ventgenero, vtipofj: string;
begin
  with modulo_dados do
  begin
    application.CreateForm(TfrmCadEntidade, frmcadentidade);
    frmcadentidade.controle := 'ALTERAÇÃO';
    // CORREÇÃO: Show ANTES de preencher campos para evitar
    // "Cannot focus an invisible window"
    frmcadentidade.Show;

    with frmcadentidade do
    begin
      Caption := Format('Manutenção de Entidade: [Geo: %s | Alvo: %s] %s',
        [fdqueryentidade.FieldByName('geoentcod').AsString,
         fdqueryentidade.FieldByName('entcod').AsString,
         fdqueryentidade.FieldByName('entnome').AsString]);

      lblentcod.Text := fdqueryentidade.FieldByName('geoentcod').AsString;
      StatusBar1.Panels[1].Text := Format('Geo: %s | Alvo: %s',
        [fdqueryentidade.FieldByName('geoentcod').AsString,
         fdqueryentidade.FieldByName('entcod').AsString]);

      cin1.ActivePageIndex := 0;
      lbltipotrat.Text         := fdqueryentidade.FieldByName('tipotratcod').AsString;
      lblentnome.Text          := fdqueryentidade.FieldByName('entnome').AsString;
      lblentnomefantasia.Text  := fdqueryentidade.FieldByName('entnomefant').AsString;
      mskcep.Text              := fdqueryentidade.FieldByName('entcep').AsString;
      lbllogradouro.Text       := fdqueryentidade.FieldByName('entlograd').AsString;
      lblentender.Text         := fdqueryentidade.FieldByName('entender').AsString;
      lblentenderno.Text       := fdqueryentidade.FieldByName('entenderno').AsString;
      lblentendercompl.Text    := fdqueryentidade.FieldByName('entendercomp').AsString;
      lblentbair.Text          := fdqueryentidade.FieldByName('entbair').AsString;
      lblcidcod.Text           := fdqueryentidade.FieldByName('cidcod').AsString;
      lblnomecidade.Caption    := fdqueryentidade.FieldByName('cidnomecomp').AsString;
      lbluf.Text               := fdqueryentidade.FieldByName('ufsigla').AsString;
      lblcaixapostal.Text      := fdqueryentidade.FieldByName('EntCxaPost').AsString;

      ventgenero := fdqueryentidade.FieldByName('entgenero').AsString;
      if ventgenero = 'M' then ventgenero := 'MASCULINO'
      else if ventgenero = 'F' then ventgenero := 'FEMININO'
      else if ventgenero = 'N' then ventgenero := 'NENHUM';
      buscanacombo(ventgenero, frmcadentidade, cbosexo);

      vfalecido := fdqueryentidade.FieldByName('USERFalecido').AsString;
      if vfalecido = 'N' then vfalecido := 'Não' else vfalecido := 'Sim';
      buscanacombo(vfalecido, frmcadentidade, cbofalecido);

      vtipofj := fdqueryentidade.FieldByName('enttipofj').AsString;
      buscanacombo(vtipofj, frmcadentidade, cbotipofj);

      vestadocivil := fdqueryentidade.FieldByName('entestcivil').AsString;
      buscanacombo(vestadocivil, frmcadentidade, cboestadocivil);

      mskdtnascimento.Text := fdqueryentidade.FieldByName('entdataanivfund').AsString;
      mskdtcadastro.Text   := fdqueryentidade.FieldByName('entdesdedata').AsString;

      if cboescolaridade.ItemIndex = -1 then carrega_combo_grauescolar;
      buscanacombo(fdqueryentidade.FieldByName('EntGrauEscol').AsString, frmcadentidade, cboescolaridade);

      lblcargocodestr.Text := fdqueryentidade.FieldByName('cargocodestr').AsString;
      lblnomecargo.Caption := fdqueryentidade.FieldByName('cargonome').AsString;

      cin1.ActivePageIndex := 1;
      cin2.ActivePageIndex := 0;
      lblnomedopai.Text := fdqueryentidade.FieldByName('entnomepai').AsString;
      lblnomedamae.Text := fdqueryentidade.FieldByName('entnomemae').AsString;
      lblresidecom.Text := fdqueryentidade.FieldByName('entmoracom').AsString;
      if fdqueryentidade.FieldByName('entpossuifilho').AsString = 'Sim' then
        rdgfilhos_sim.Checked := True
      else
        rdgfilhosnao.Checked := True;

      cin2.ActivePageIndex := 1;
      lbltipocobcod.Text          := fdqueryentidade.FieldByName('tipocobcod').AsString;
      lbltipocobnome.Caption      := fdqueryentidade.FieldByName('tipocobnome').AsString;
      lbltipocobnome.Refresh;
      lblbconum.Text              := fdqueryentidade.FieldByName('bconum').AsString;
      lblnomebanco.Caption        := fdqueryentidade.FieldByName('bconome').AsString;
      lblagnum.Text               := fdqueryentidade.FieldByName('agnum').AsString;
      lblnomeagencia.Caption      := fdqueryentidade.FieldByName('agnome').AsString;
      lblgeocontacorrente.Text    := fdqueryentidade.FieldByName('EntBcoAgCCorNum').AsString;
      lbldiadebitoautomatico.Text := fdqueryentidade.FieldByName('USERDia_Debito_CC').AsString;

      if fdqueryentidade.FieldByName('USERValor_Contribuicao').IsNull or
         (Trim(fdqueryentidade.FieldByName('USERValor_Contribuicao').AsString) = '') or
         (fdqueryentidade.FieldByName('USERValor_Contribuicao').AsString = '0') then
        lblvalorcontribuicao.Text := '25'
      else
        lblvalorcontribuicao.Text := fdqueryentidade.FieldByName('USERValor_Contribuicao').AsString;

      vgeracarne := fdqueryentidade.FieldByName('USERGeraCarne').AsString;
      buscanacombo(UpperCase(vgeracarne), frmcadentidade, cbogeracarne);
      lbldioceseid.Text      := fdqueryentidade.FieldByName('USERDiocese_id').AsString;
      lbldiocesenome.Caption := fdqueryentidade.FieldByName('USERNomeDiocese').AsString;
      vrecebelembrete := fdqueryentidade.FieldByName('USERRecebelembretedoacao').AsString;
      buscanacombo(UpperCase(vrecebelembrete), frmcadentidade, cborecebelembrete);

      cin2.ActivePageIndex := 2;
      lblativecodestr.Text               := fdqueryentidade.FieldByName('ativeconcodestr').AsString;
      lblnomeatividade_economica.Caption := fdqueryentidade.FieldByName('ativeconnome').AsString;
      lblorigcodestr.Text                := fdqueryentidade.FieldByName('origcodestr').AsString;
      lblnomeorigem.Caption              := fdqueryentidade.FieldByName('orignome').AsString;
      lblregiao.Text                     := fdqueryentidade.FieldByName('regcodestr').AsString;
      lblnomeregiao.Caption              := fdqueryentidade.FieldByName('regnome').AsString;
      lblconceito.Text                   := fdqueryentidade.FieldByName('entconceito').AsString;
      vgeoentcod := fdqueryentidade.FieldByName('geoentcod').AsString;

      cin1.ActivePageIndex := 3;
      lblentcontatocod.Text := '';
      carrega_tipologradouro_contato;

      mostra_telefones_entidade(lblentcod.Text, frmentidades.integraentidadeapolo);
      mostra_entidade_contatoweb(lblentcod.Text, frmentidades.integraentidadeapolo);
      mostra_entidade_categoria(lblentcod.Text, frmentidades.integraentidadeapolo);

      cin1.ActivePageIndex := 4;
      mostra_entidade_documentos(lblentcod.Text, frmentidades.integraentidadeapolo);

      memobservacoes.Lines.Clear;
      memobservacoes.Lines.Add(fdqueryentidade.FieldByName('Entobservacoes').AsString);
      tabobservacoes.Refresh;

      cin1.ActivePageIndex := 0;
      cin2.ActivePageIndex := 0;
    end;
  end;
end;

// =============================================================================
// atualiza_entcod_alvo_via_cpf
// =============================================================================
function atualiza_entcod_alvo_via_cpf(const vcodigogeoentidade: string): string;
var
  ventcodalvo: string;
begin
  Result := '';
  with frmentidades, modulo_dados do
  begin
    fdquerysql19.Close;
    fdquerysql19.SQL.Clear;
    fdquerysql19.SQL.Text :=
      'SELECT geonumerodocumento FROM USER_geoapolo_entidade_documentos' +
      ' WHERE geoentcod = :geoentcod AND geotipodocumento = :geotipodocumento';
    fdquerysql19.ParamByName('geoentcod').AsString       := vcodigogeoentidade;
    fdquerysql19.ParamByName('geotipodocumento').AsString := 'CPF/CNPJ';
    fdquerysql19.Open;
    if not fdquerysql19.IsEmpty then
    begin
      fdquerysql20.Close;
      fdquerysql20.SQL.Text := 'SELECT TOP 1 entcod FROM entidades_apolo WITH (NOLOCK) WHERE entcpfcgc = :cpf';
      fdquerysql20.ParamByName('cpf').AsString := fdquerysql19.FieldByName('geonumerodocumento').AsString;
      fdquerysql20.Open;
      if not fdquerysql20.IsEmpty then
      begin
        ventcodalvo := fdquerysql20.FieldByName('entcod').AsString;
        fdquerysql3.Close;
        fdquerysql3.SQL.Text :=
          'UPDATE USER_geoapolo_entidade SET entcod = :entcod WHERE geoentcod = :geoentcod';
        fdquerysql3.ParamByName('entcod').AsString    := ventcodalvo;
        fdquerysql3.ParamByName('geoentcod').AsString := vcodigogeoentidade;
        fdquerysql3.ExecSQL;
        if fdquerysql3.RowsAffected > 0 then
          Result := ventcodalvo;
      end;
    end;
  end;
end;

// =============================================================================
// gridentidadesDrawColumnCell
// =============================================================================
procedure Tfrmentidades.gridentidadesDrawColumnCell(Sender: TObject;
  const Rect: TRect; DataCol: Integer; Column: TColumn; State: TGridDrawState);
begin
  with modulo_dados do
  begin
    if ((integraentidadeapolo = 'Não Integra') or (integraentidadeapolo = 'Mescla')) and
       (cbobuscabanco.Text = 'GeoApolo') then
    begin
      if (fdqueryentidade.FieldByName('entcod').AsString <> '') and
         (fdqueryentidade.FieldByName('atualizou_apolo').AsString = 'S') and
         (fdqueryentidade.FieldByName('usucod_atualizou_apolo').AsString <> '') then
      begin
        gridentidades.Canvas.Brush.Color := clYellow;
        gridentidades.Canvas.FillRect(Rect);
        gridentidades.DefaultDrawDataCell(Rect, Column.Field, State);
      end
      else if not fdqueryentidade.FieldByName('geoobservacoes').IsNull and
              (Trim(fdqueryentidade.FieldByName('geoobservacoes').AsString) <> '') then
      begin
        gridentidades.Canvas.Brush.Color := clRed;
        gridentidades.Canvas.FillRect(Rect);
        gridentidades.DefaultDrawDataCell(Rect, Column.Field, State);
      end;
    end;
  end;
end;

// =============================================================================
// importa_entidade — mantido igual ao original
// =============================================================================
function importa_entidade(integracao: string): string;
var
  tratalogradouro, entcodcontato: string;
  FormatSettings: TFormatSettings;
begin
  with modulo_dados, frmentidades, frmcadentidade do
  begin
    FormatSettings := TFormatSettings.Create;
    FormatSettings.DateSeparator   := '-';
    FormatSettings.ShortDateFormat := 'dd/mm/yyyy';

    if integracao = 'GeoApolo' then
    begin
      lblentcod.Text := fdqueryentidade.FieldByName('entcod').AsString;
      lbllogradouro.Clear; lbllogradouroentrega.Clear; lbllogradourocobranca.Clear;
      lbltipotrat.Text  := fdqueryentidade.FieldByName('tipotratcod').AsString;
      entcodapolo       := atualiza_entcod_alvo_via_cpf(lblentcod.Text);
      lblentnome.Text   := fdqueryentidade.FieldByName('entnome').AsString;
      lblentnomefantasia.Text := fdqueryentidade.FieldByName('entnomefant').AsString;
      logradouro := fdqueryentidade.FieldByName('entlograd').AsString;
      if logradouro <> '' then
        lbllogradouro.Text := logradouro
      else
      begin
        tratalogradouro := Copy(fdqueryentidade.FieldByName('entender').AsString, 1, 3);
        if tratalogradouro = 'RUA' then logradouro := 'R.'
        else if logradouro = 'AVE' then logradouro := 'Av.'
        else if logradouro = 'TRA' then logradouro := 'Tv.'
        else if logradouro = 'PRA' then logradouro := 'Pç.';
      end;
      lbllogradouro.Text      := logradouro;
      lblentender.Text        := fdqueryentidade.FieldByName('entender').AsString;
      lblentenderno.Text      := fdqueryentidade.FieldByName('entenderno').AsString;
      lblentendercompl.Text   := fdqueryentidade.FieldByName('EntEnderComp').AsString;
      lblentbair.Text         := fdqueryentidade.FieldByName('EntBair').AsString;
      mskcep.Text             := fdqueryentidade.FieldByName('Entcep').AsString;
      lblcidcod.Text          := fdqueryentidade.FieldByName('cidcod').AsString;
      retorna_cidade_estado(lblcidcod.Text, frmentidades.integraentidadeapolo);
      lblcaixapostal.Text     := fdqueryentidade.FieldByName('entcxapost').AsString;
      sexo := fdqueryentidade.FieldByName('EntGenero').AsString;
      if sexo = 'F' then
      begin
        if lbltipotrat.Text = '' then lbltipotrat.Text := 'Sra.';
        sexo := 'FEMININO';
      end
      else if sexo = 'M' then
      begin
        if lbltipotrat.Text = '' then lbltipotrat.Text := 'Sr.';
        sexo := 'MASCULINO';
      end;
      buscanacombo(sexo, frmcadentidade, cbosexo);
      buscanacombo(fdqueryentidade.FieldByName('EntTipoFJ').AsString, frmcadentidade, cbotipofj);
      buscanacombo(fdqueryentidade.FieldByName('EntEstCivil').AsString, frmcadentidade, cboestadocivil);
      falecido := fdqueryentidade.FieldByName('USERFalecido').AsString;
      if (falecido = 'Não') or (falecido = '') then falecido := 'Não' else falecido := 'Sim';
      buscanacombo(falecido, frmcadentidade, cbofalecido);
      carrega_combo_grauescolar;
      grauescolaridade := fdqueryentidade.FieldByName('EntGrauEscol').AsString;
      buscanacombo(grauescolaridade, frmcadentidade, cboescolaridade);
      lblcargocodestr.Text  := fdqueryentidade.FieldByName('cargocodestr').AsString;
      mskdtnascimento.EditMask := '';
      if (fdqueryentidade.FieldByName('entdataanivfund').AsString = '01/01/1970') or
         (fdqueryentidade.FieldByName('entdataanivfund').AsString = '') then
        mskdtnascimento.Text := '  /  /    '
      else
        mskdtnascimento.Text :=
          Copy(fdqueryentidade.FieldByName('entdataanivfund').AsString, 9, 2) + '/' +
          Copy(fdqueryentidade.FieldByName('entdataanivfund').AsString, 6, 2) + '/' +
          Copy(fdqueryentidade.FieldByName('entdataanivfund').AsString, 1, 4);
      mskdtcadastro.EditMask := '';
      if (fdqueryentidade.FieldByName('entdatacad').AsString = '01/01/1970') or
         (fdqueryentidade.FieldByName('entdatacad').AsString = '') then
        mskdtcadastro.Text := '  /  /    '
      else
        mskdtcadastro.Text := FormatDateTime('dd/mm/yyyy',
          StrToDate(fdqueryentidade.FieldByName('entdatacad').AsString));

      cin1.ActivePageIndex := 1; cin2.ActivePageIndex := 0;
      lblnomedopai.Text := fdqueryentidade.FieldByName('EntNomePai').AsString;
      lblnomedamae.Text := fdqueryentidade.FieldByName('EntNomeMae').AsString;
      lblresidecom.Text := fdqueryentidade.FieldByName('EntMoraCom').AsString;
      if fdqueryentidade.FieldByName('EntPossuiFilho').AsString = 'Sim' then
      begin
        filhossimnao := 'Sim';
        lblquantosfilhos.Visible := True;
        lblquantosfilhos.Text := fdqueryentidade.FieldByName('numerofilhos').AsString;
      end
      else if fdqueryentidade.FieldByName('EntPossuiFilho').AsString = 'Não' then
        filhossimnao := 'Não';

      cin2.ActivePageIndex := 1;
      lbltipocobcod.Text      := fdqueryentidade.FieldByName('tipocobcod').AsString;
      lbltipocobnome.Caption  := fdqueryentidade.FieldByName('tipocobnome').AsString;
      lblbconum.Text          := fdqueryentidade.FieldByName('bconum').AsString;
      lblnomebanco.Caption    := fdqueryentidade.FieldByName('bconome').AsString;
      lblagnum.Text           := fdqueryentidade.FieldByName('agnum').AsString;
      lblnomeagencia.Caption  := fdqueryentidade.FieldByName('agnome').AsString;
      lblgeocontacorrente.Text := fdqueryentidade.FieldByName('EntBcoAgCCorNum').AsString;
      lbldiadebitoautomatico.Text := fdqueryentidade.FieldByName('USERDia_Debito_CC').AsString;
      lblvalorcontribuicao.Text   := fdqueryentidade.FieldByName('USERValor_Contribuicao').AsString;
      buscanacombo('SIM', frmcadentidade, cbogeracarne); cbogeracarne.Refresh;
      lbldioceseid.Text      := fdqueryentidade.FieldByName('USERDiocese_id').AsString;
      lbldiocesenome.Caption := fdqueryentidade.FieldByName('USERNomeDiocese').AsString;
      buscanacombo('SIM', frmcadentidade, cborecebelembrete); cborecebelembrete.Refresh;

      cin2.ActivePageIndex := 2;
      lblativecodestr.Text               := fdqueryentidade.FieldByName('ativeconcodestr').AsString;
      lblnomeatividade_economica.Caption := retorna_ativ_econ(lblativecodestr.Text);
      lblorigcodestr.Text                := fdqueryentidade.FieldByName('origcodestr').AsString;
      lblnomeorigem.Caption              := fdqueryentidade.FieldByName('orignome').AsString;
      lblorigcodestr.Refresh; lblnomeorigem.Refresh;
      lblregiao.Text := fdqueryentidade.FieldByName('regcodestr').AsString;
      if lblregiao.Text <> '' then
        lblnomeregiao.Caption := retorna_regiaopais(lblregiao.Text);
      lblconceito.Text := fdqueryentidade.FieldByName('entconceito').AsString;
      lblregiao.Refresh; lblconceito.Refresh; lblnomeregiao.Refresh;

      cin1.ActivePageIndex := 3;
      fdquerysql.Close; fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text :=
        'SELECT entcodcontato FROM USER_geoapolo_entidade_contato WHERE geoentcod = ' +
        QuotedStr(lblentcod.Text);
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
        entcodcontato := fdquerysql.FieldByName('entcodcontato').AsString;

      fdquerysql4.Close; fdquerysql4.SQL.Clear;
      fdquerysql4.SQL.Text :=
        'SELECT econt.EntCodContato, econt.tipotratcod, uge.geoentnome, uge.tipolograd,' +
        ' uge.geoentender, uge.geoentendercomp, uge.geoentendernopi, uge.geoentbair,' +
        ' uge.geoentcep, econt.CidCod, cid.cidnomecomp, cid.ufsigla,' +
        ' econt.data_vigencia_inicial, econt.data_vigencia_final, econt.EntContatoCelular,' +
        ' econt.EntContatoTelefone, econt.CargoCodEstr, ugc.geocargonome' +
        ' FROM USER_geoapolo_entidade_contato econt' +
        ' INNER JOIN user_geoapolo_entidade uge WITH(NOLOCK) ON econt.EntCodContato = uge.geoentcod' +
        ' INNER JOIN user_geoapolo_cidades cid WITH(NOLOCK) ON econt.CidCod = cid.geocidcod' +
        ' LEFT JOIN USER_geoapolo_cargos ugc WITH(NOLOCK) ON econt.usercargocodestr = ugc.geocargocodestr' +
        ' WHERE econt.EntCodContato = ' + QuotedStr(entcodcontato);
      if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
      begin
        lblentcontatocod.Text    := fdquerysql14.FieldByName('EntCodContato').AsString;
        lbltipotratamento.Caption := fdquerysql14.FieldByName('tipotratcod').AsString;
        lblentcontatonome.Caption := fdquerysql14.FieldByName('entnome').AsString;
        mskcepcontato.Text       := fdquerysql14.FieldByName('entcep').AsString;
        buscanacombo(fdquerysql14.FieldByName('tipolograd').AsString, frmcadentidade, cbologradourocontato);
        lblenderecocontato.Text  := fdquerysql14.FieldByName('entender').AsString;
        lblnumerocontato.Text    := fdquerysql14.FieldByName('entendernopi').AsString;
        lblcomplendercontato.Text := fdquerysql14.FieldByName('entendercomp').AsString;
        lblbairrocontato.Text    := fdquerysql14.FieldByName('entbair').AsString;
        lblcargocontato.Text     := fdquerysql14.FieldByName('CargoCodEstr').AsString;
        lblcargocontatonome.Caption := fdquerysql14.FieldByName('cargonome').AsString;
        if not fdQuerySQL14.FieldByName('data_vigencia_inicial').IsNull then
          mskdtiniciovigencia.Text := FormatDateTime('dd/MM/yyyy',
            fdquerysql14.FieldByName('data_vigencia_inicial').AsDateTime)
        else
          mskdtiniciovigencia.Text := '';
        if not fdquerysql14.FieldByName('data_vigencia_final').IsNull then
          mskdtfinalvigencia.Text := FormatDateTime('dd/MM/yyyy',
            fdquerysql14.FieldByName('data_vigencia_final').AsDateTime)
        else
          mskdtfinalvigencia.Text := '';
      end;

      mostra_telefones_entidade(lblentcod.Text, frmentidades.integraentidadeapolo);
      mostra_entidade_contatoweb(lblentcod.Text, frmentidades.integraentidadeapolo);
      mostra_entidade_categoria(lblentcod.Text, frmentidades.integraentidadeapolo);
      cin1.ActivePageIndex := 4;
      mostra_entidade_documentos(lblentcod.Text, frmentidades.integraentidadeapolo);
      memobservacoes.Lines.Add(fdqueryentidade.FieldByName('geobservacoes').AsString);
      frmcadentidade.tabobservacoes.Refresh;
      cin1.ActivePageIndex := 0;
    end
    else if integracao = 'Alvo' then
    begin
      lblentcod.Text          := fdqueryentidade.FieldByName('entcod').AsString;
      lbllogradouro.Clear; lbllogradouroentrega.Clear; lbllogradourocobranca.Clear;
      lbltipotrat.Text        := fdqueryentidade.FieldByName('tipotratcod').AsString;
      lblentnome.Text         := fdqueryentidade.FieldByName('entnome').AsString;
      lblentnomefantasia.Text := fdqueryentidade.FieldByName('entnomefant').AsString;
      logradouro              := fdqueryentidade.FieldByName('entlograd').AsString;
      lbllogradouro.Text      := logradouro;
      lblentender.Text        := fdqueryentidade.FieldByName('entender').AsString;
      lblentenderno.Text      := fdqueryentidade.FieldByName('entenderno').AsString;
      lblentendercompl.Text   := fdqueryentidade.FieldByName('entendercomp').AsString;
      lblentbair.Text         := fdqueryentidade.FieldByName('entbair').AsString;
      mskcep.Text             := fdqueryentidade.FieldByName('entcep').AsString;
      lblcidcod.Text          := fdqueryentidade.FieldByName('cidcod').AsString;
      retorna_cidade_estado(lblcidcod.Text, frmentidades.integraentidadeapolo);
      lblcaixapostal.Text     := fdquerysql4.FieldByName('entcxapost').AsString;
      sexo := fdqueryentidade.FieldByName('entgenero').AsString;
      if sexo = 'F' then sexo := 'FEMININO'
      else if sexo = 'M' then sexo := 'MASCULINO';
      buscanacombo(sexo, frmcadentidade, cbosexo);
      lbllocaldereferencia.Text := fdqueryentidade.FieldByName('localreferencia_ender').AsString;
      buscanacombo(fdqueryentidade.FieldByName('tipofj').AsString, frmcadentidade, cbotipofj);
      buscanacombo(fdqueryentidade.FieldByName('entestcivil').AsString, frmcadentidade, cboestadocivil);
      falecido := fdqueryentidade.FieldByName('falecido').AsString;
      if falecido = 'S' then falecido := 'Sim' else if falecido = 'N' then falecido := 'Não';
      buscanacombo(falecido, frmcadentidade, cbofalecido);
      carrega_combo_grauescolar;
      if fdqueryentidade.FieldByName('entgrauescol').AsString = '' then
        codgrauescolar := '0'
      else
        codgrauescolar := fdqueryentidade.FieldByName('entgrauescol').AsString;
      fdquerysql11.Close; fdquerysql11.SQL.Clear;
      fdquerysql11.SQL.Text :=
        'SELECT grau_escolaridade FROM USER_geoapolo_grauescolaridade' +
        ' WHERE codigo_grauescolaridade = ' + codgrauescolar;
      if executaracao(fdquerysql11, fdbanco, true, dtsfdquerysql11) then
      begin
        grauescolaridade := modulo_dados.fdquerysql1.FieldByName('grau_escolaridade').AsString;
        buscanacombo(grauescolaridade, frmcadentidade, cboescolaridade);
      end;
      lblcargocodestr.Text    := fdqueryentidade.FieldByName('cargocodestr').AsString;
      mskdtnascimento.Text    := fdqueryentidade.FieldByName('entdataanivfund').AsString;
      mskdtcadastro.Text      := fdqueryentidade.FieldByName('entdatacad').AsString;

      cin1.ActivePageIndex := 1; cin2.ActivePageIndex := 0;
      lblnomedopai.Text := fdqueryentidade.FieldByName('entnomepai').AsString;
      lblnomedamae.Text := fdqueryentidade.FieldByName('entnomemae').AsString;
      lblresidecom.Text := fdqueryentidade.FieldByName('entmoracom').AsString;
      if fdqueryentidade.FieldByName('entpossuifilho').AsString = 'Sim' then
      begin
        filhossimnao := 'Sim';
        lblquantosfilhos.Visible := True;
        lblquantosfilhos.Text := fdqueryentidade.FieldByName('numerofilhos').AsString;
      end
      else if fdqueryentidade.FieldByName('entpossuifilho').AsString = 'Não' then
        filhossimnao := 'Não';

      cin2.ActivePageIndex := 2;
      lblativecodestr.Text               := fdquerysql.FieldByName('ativeconcodestr').AsString;
      lblnomeatividade_economica.Caption := fdquerysql.FieldByName('ativeconnome').AsString;
      lblativecodestr.Refresh; lblnomeatividade_economica.Refresh;
      lblorigcodestr.Text  := fdqueryentidade.FieldByName('origcodestr').AsString;
      lblnomeorigem.Caption := fdqueryentidade.FieldByName('orignome').AsString;
      lblorigcodestr.Refresh; lblnomeorigem.Refresh;
      lblregiao.Text        := fdqueryentidade.FieldByName('regcodestr').AsString;
      lblnomeregiao.Caption := retorna_regiaopais(lblregiao.Text);
      lblconceito.Text      := fdqueryentidade.FieldByName('entconceito').AsString;
      lblregiao.Refresh; lblconceito.Refresh; lblnomeregiao.Refresh;

      cin1.ActivePageIndex := 3;
      mostra_telefones_entidade(lblentcod.Text, frmentidades.integraentidadeapolo);
      mostra_entidade_contatoweb(lblentcod.Text, frmentidades.integraentidadeapolo);
      mostra_entidade_categoria(lblentcod.Text, frmentidades.integraentidadeapolo);

      fdquerysql.Close; fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text :=
        'SELECT ect.entcod, ect.entcodcontato, ect.tipotratcod, ect.cargocodestr,' +
        ' ect.tipologradabrev, ect.entcontatoender, ect.entcontatoenderno, ect.entcontatoendercomp,' +
        ' ect.entcontatobair, ect.entcontatocep, ect.cidcod, cid.cidnomecomp' +
        ' FROM ent_contato ect WITH(NOLOCK)' +
        ' INNER JOIN cidade cid WITH(NOLOCK) ON ect.cidcod = cid.cidcod' +
        ' WHERE ect.entcod = ' + QuotedStr(lblentcod.Text);
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
        lblentcontatocod.Text := '';

      cin1.ActivePageIndex := 4;
      memobservacoes.Lines.Add('');
      mostra_entidade_documentos(lblentcod.Text, frmentidades.integraentidadeapolo);
      cin1.ActivePageIndex := 0; cin1.Refresh;
    end;
  end;
end;

// =============================================================================
// retorna_ativ_econ
// =============================================================================
function retorna_ativ_econ(ativeconcodestr: string): string;
begin
  with modulo_dados, frmcadentidade do
  begin
    fdquerysql.Close;
    fdquerysql.SQL.Clear;
    fdquerysql.SQL.Text :=
      'SELECT ae.AtivEconCodEstr, ae.AtivEconNome FROM ATIV_ECONOMICA ae WITH(NOLOCK)' +
      ' WHERE ae.AtivEconCodEstr = ' + QuotedStr(ativeconcodestr);
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
    begin
      lblativecodestr.Text               := ativeconcodestr;
      lblnomeatividade_economica.Caption := fdquerysql.FieldByName('ativeconnome').AsString;
      lblativecodestr.Refresh; lblnomeatividade_economica.Refresh;
    end;
  end;
end;

// =============================================================================
// gridentidadesKeyUp
// =============================================================================
procedure Tfrmentidades.gridentidadesKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  with modulo_dados do
  begin
    if Key = VK_INSERT then
    begin
      spbnovo.Click;
    end;

    if Key = VK_DELETE then
    begin
      if integraentidadeapolo = 'N' then
      begin
        resp := messagedlg('Confirma a Exclusão desta Entidade ? (Y/N)',
                           mtconfirmation, [mbyes, mbno], 0);
        if resp = idyes then
        begin
          fdquerysql3.Close; fdquerysql3.SQL.Clear;
          fdquerysql3.SQL.Text :=
            'DELETE FROM USER_geoapolo_entidade_webcontato WHERE geoentcod = :geoentcod';
          fdquerysql3.ParamByName('geoentcod').AsString := fdquerysql4.FieldByName('geoentcod').AsString;
          executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3);

          fdquerysql3.Close; fdquerysql3.SQL.Clear;
          fdquerysql3.SQL.Text :=
            'DELETE FROM USER_geoapolo_entidade_comunicacao WHERE geoentcod = :geoentcod';
          fdquerysql3.ParamByName('geoentcod').AsString := fdquerysql4.FieldByName('geoentcod').AsString;
          executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3);

          fdquerysql3.Close; fdquerysql3.SQL.Clear;
          fdquerysql3.SQL.Text :=
            'DELETE FROM USER_geoapolo_entidade_documentos WHERE geoentcod = :geoentcod';
          fdquerysql3.ParamByName('geoentcod').AsString := fdquerysql4.FieldByName('geoentcod').AsString;
          executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3);

          fdquerysql3.Close; fdquerysql3.SQL.Clear;
          fdquerysql3.SQL.Text :=
            'DELETE FROM USER_geoapolo_entcateg WHERE geoentcod = :geoentcod';
          fdquerysql3.ParamByName('geoentcod').AsString := fdquerysql4.FieldByName('geoentcod').AsString;
          executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3);

          fdquerysql3.Close; fdquerysql3.SQL.Clear;
          fdquerysql3.SQL.Text :=
            'DELETE FROM USER_geoapolo_entidade WHERE geoentcod = :geoentcod';
          fdquerysql3.ParamByName('geoentcod').AsString := fdquerysql4.FieldByName('geoentcod').AsString;
          if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
          begin
            messagedlg('ENTIDADE REMOVIDA COM SUCESSO !!!', mtinformation, [mbok], 0);
            carrega_lista_entidades('GEOAPOLO', '', '');
            gridentidades.Refresh;
          end
          else
          begin
            messagedlg('EXISTE VINCULOS DESTA ENTIDADE DENTRO DO SISTEMA, DELEÇÃO NÃO SERÁ PERMITIDA!!!',
                       mtwarning, [mbok], 0);
            gridentidades.Refresh;
          end;
        end;
      end
      else if integraentidadeapolo = 'I' then
      begin
        messagedlg('PARA REMOVER ENTIDADES DA BASE APOLO, UTILIZE O APOLO OU ALVO ERP',
                   mtwarning, [mbok], 0);
        Exit;
      end;
    end;
  end;
end;

procedure Tfrmentidades.lblprocurarporKeyPress(Sender: TObject; var Key: Char);
begin
  if (Key = #13) or (Key = #$F3) then
  begin
    if Trim(lblprocurarpor.Text) <> '' then
      carrega_lista_entidades(cbobuscabanco.Text, 'Especifica', '')
    else
      carrega_lista_entidades(cbobuscabanco.Text, 'Consulta', '');
  end;
end;

procedure Tfrmentidades.spblimparClick(Sender: TObject);
begin
  lblprocurarpor.Clear;
  if cbocampo.Items.Count > 0 then
    cbocampo.ItemIndex := 0;
  if cbordem.Items.Count > 0 then
    cbordem.ItemIndex := 0;
  rdgcrescente.Checked := True;
  carrega_lista_entidades(cbobuscabanco.Text, 'Consulta', '');
  if lblprocurarpor.CanFocus then
    lblprocurarpor.SetFocus;
end;

// =============================================================================
// ConfigurarGrid
// =============================================================================
procedure Tfrmentidades.ConfigurarGrid;
begin
  with StringGrid1 do
  begin
    Align            := alNone;
    Font.Name        := 'Segoe UI';
    Font.Size        := 10;
    ColCount         := 4;
    FixedCols        := 0;
    FixedRows        := 1;
    DefaultRowHeight := 26;
    ScrollBars       := ssVertical;
    Options          := Options + [goFixedVertLine, goFixedHorzLine,
                                   goVertLine, goHorzLine] - [goEditing];
    ColWidths[0] := 150;
    ColWidths[1] := 200;
    ColWidths[2] := 200;
    ColWidths[3] := 140;
    Left   := memoplataformasve.Left;
    Top    := memoplataformasve.Top;
    Width  := memobaseapolo.Left + memobaseapolo.Width - memoplataformasve.Left;
    Height := memoplataformasve.Height;
  end;
  memoplataformasve.Visible := False;
  memobaseapolo.Visible     := False;
  StringGrid1.Visible       := True;
  StringGrid1.BringToFront;
end;

// =============================================================================
// MontarTelaComparacao
// =============================================================================
procedure Tfrmentidades.MontarTelaComparacao(QuerySVE, QueryBanco: TFDQuery);
var
  i, Row: Integer;
  ValSVE, ValAlvo: string;
begin
  GTotalDiferentes := 0;
  StringGrid1.Cells[0, 0] := 'Campo';
  StringGrid1.Cells[1, 0] := 'SVE  (clique para usar)';
  StringGrid1.Cells[2, 0] := 'Alvo  (clique para manter)';
  StringGrid1.Cells[3, 0] := 'Decisão';

  for i := 0 to TOTAL_CAMPOS_MAPA - 1 do
  begin
    ValSVE := ''; ValAlvo := '';
    if QuerySVE.FindField(MapaCampos[i].CampoSVE) <> nil then
      ValSVE := Trim(QuerySVE.FieldByName(MapaCampos[i].CampoSVE).AsString);
    if QueryBanco.FindField(MapaCampos[i].CampoAlvo) <> nil then
      ValAlvo := Trim(QueryBanco.FieldByName(MapaCampos[i].CampoAlvo).AsString);
    if not SameText(ValSVE, ValAlvo) then
    begin
      GLinhasDiferentes[GTotalDiferentes] := i;
      Inc(GTotalDiferentes);
    end;
  end;

  if GTotalDiferentes = 0 then
  begin
    lblmensagemgeoapolo.Caption    := '✔ Cadastros idênticos — nenhuma diferença encontrada.';
    lblmensagemgeoapolo.Font.Color := clGreen;
    StringGrid1.RowCount           := 2;
    StringGrid1.Cells[0, 1]        := '(cadastros idênticos, nenhuma ação necessária)';
    StringGrid1.Cells[1, 1] := ''; StringGrid1.Cells[2, 1] := ''; StringGrid1.Cells[3, 1] := '';
    spbatualizaentidadeapolo.Enabled := False;
    StringGrid1.Repaint;
    Exit;
  end;

  StringGrid1.RowCount := GTotalDiferentes + 1;
  for i := 0 to GTotalDiferentes - 1 do GDecisoes[i] := dlNenhuma;

  Row := 1;
  for i := 0 to GTotalDiferentes - 1 do
  begin
    ValSVE := ''; ValAlvo := '';
    if QuerySVE.FindField(MapaCampos[GLinhasDiferentes[i]].CampoSVE) <> nil then
      ValSVE := Trim(QuerySVE.FieldByName(MapaCampos[GLinhasDiferentes[i]].CampoSVE).AsString);
    if QueryBanco.FindField(MapaCampos[GLinhasDiferentes[i]].CampoAlvo) <> nil then
      ValAlvo := Trim(QueryBanco.FieldByName(MapaCampos[GLinhasDiferentes[i]].CampoAlvo).AsString);
    StringGrid1.Cells[0, Row] := MapaCampos[GLinhasDiferentes[i]].LabelExibicao;
    StringGrid1.Cells[1, Row] := ValSVE;
    StringGrid1.Cells[2, Row] := ValAlvo;
    StringGrid1.Cells[3, Row] := '— clique num valor —';
    Inc(Row);
  end;

  lblmensagemgeoapolo.Caption :=
    Format('⚠ %d diferença(s) encontrada(s) — %d pendente(s)', [GTotalDiferentes, GTotalDiferentes]);
  lblmensagemgeoapolo.Font.Color   := clRed;
  spbatualizaentidadeapolo.Enabled := False;
  spbatualizaentidadeapolo.Caption := '✔ Aplicar Selecionados';
  StringGrid1.Repaint;
end;

procedure Tfrmentidades.SelectCell(Sender: TObject; ACol, ARow: Integer; var CanSelect: Boolean);
begin
  // Intencionalmente vazia — ver StringGrid1SelectCell
end;

// =============================================================================
// ExtrairConjunto
// =============================================================================
function ExtrairConjunto(const Texto: string; Indice: Integer): string;
var
  Lista: TStringList;
begin
  Result := '';
  Lista := TStringList.Create;
  try
    Lista.CommaText := Texto;
    if (Indice >= 0) and (Indice < Lista.Count) then
      Result := Lista[Indice];
  finally
    Lista.Free;
  end;
end;

// =============================================================================
// ConfigurarGridCompleto
// =============================================================================
procedure Tfrmentidades.ConfigurarGridCompleto(const NomeBase: string);
var
  NomeModulo, NomeConfig: string;
begin
  with modulo_dados do
  begin
    if NomeBase = 'GeoApolo' then
      begin
        NomeModulo := 'entidades_geoapolo';
        NomeConfig := 'GEOENTIDADESGEOAPOLO';
      end
    else if NomeBase = 'Alvo' then
      begin
        NomeModulo := 'entidades_apolo';
        NomeConfig := 'GEOENTIDADESAPOLO';
      end
    else
      Exit;

    if not Assigned(fdqueryentidade) then Exit;
    if not fdqueryentidade.Active then Exit;
    if fdqueryentidade.RecordCount = 0 then Exit;

    try
      carrega_config(NomeConfig, frmentidades, cbocampo, cbordem, rdgcrescente, rdgdecrescente);
      configura_grid(NomeModulo, frmentidades, frmlogon.codigousuario, 'gridentidades',
                     gridentidades, modulo_dados.dtsfdqueryentidade);
      gridentidades.Refresh;
    except
      on E: Exception do
        ShowMessage('Erro ao configurar grid: ' + E.Message);
    end;
  end;
end;

// =============================================================================
// spbexportarloteClick - Exportação em lote para o Alvo
// =============================================================================
procedure Tfrmentidades.spbexportarloteClick(Sender: TObject);
var
  API: TAlvoAPI;
  Entidade: TEntidade;
  vMensagem, vNovoEntCod, vTratCod, vGeoEntCod, vEntCod, vNomeEntidade: string;
  vEntCodContato, vErroContato, vLogFileName, vLogPath, vMsgConfirm: string;
  LogErros: TStringList;
  TotalRegs, Sucessos, Falhas, Pendencias, TotalZerados: Integer;
  vBk: TBookmark;
begin
  if cbobuscabanco.Text <> 'GeoApolo' then
  begin
    MessageDlg('A exportação em lote só é permitida na base GeoApolo.', mtWarning, [mbOK], 0);
    Exit;
  end;

  if not modulo_dados.fdqueryentidade.Active or (modulo_dados.fdqueryentidade.RecordCount = 0) then
  begin
    MessageDlg('Não há entidades filtradas na lista para exportar.', mtWarning, [mbOK], 0);
    Exit;
  end;

  TotalRegs := modulo_dados.fdqueryentidade.RecordCount;
  TotalZerados := 0;
  vBk := modulo_dados.fdqueryentidade.GetBookmark;
  try
    modulo_dados.fdqueryentidade.First;
    while not modulo_dados.fdqueryentidade.Eof do
    begin
      if (modulo_dados.fdqueryentidade.FindField('USERValor_Contribuicao') = nil) or
         (modulo_dados.fdqueryentidade.FieldByName('USERValor_Contribuicao').AsFloat = 0.0) then
        Inc(TotalZerados);
      modulo_dados.fdqueryentidade.Next;
    end;
  finally
    if modulo_dados.fdqueryentidade.BookmarkValid(vBk) then
    begin
      modulo_dados.fdqueryentidade.GotoBookmark(vBk);
      modulo_dados.fdqueryentidade.FreeBookmark(vBk);
    end;
  end;

  vMsgConfirm := Format('Deseja exportar todas as %d Entidades abaixo para o Alvo ?', [TotalRegs]);
  if TotalZerados > 0 then
    vMsgConfirm := vMsgConfirm + #13#10 + #13#10 +
      Format('ATENÇÃO: Existem %d entidades com Valor de Contribuição igual a R$ 0,00 para sua conferência.', [TotalZerados]) + #13#10 +
      'Deseja prosseguir com a exportação?';

  if MessageDlg(vMsgConfirm, mtConfirmation, [mbYes, mbNo], 0) <> mrYes then
    Exit;

  Screen.Cursor := crHourGlass;
  LogErros := TStringList.Create;
  API := TAlvoAPI.Create('https://alvo.rccbrasil.org.br/api/');
  try
    if not Self.GarantirAutenticacaoAlvo(API) then
      Exit;

    Sucessos   := 0;
    Falhas     := 0;
    Pendencias := 0;

    LogErros.Add('======================================================================');
    LogErros.Add('LOG DE EXPORTAÇÃO EM LOTE PARA O ALVO - GEOAPOLO');
    LogErros.Add('Data/Hora: ' + FormatDateTime('dd/mm/yyyy hh:nn:ss', Now));
    LogErros.Add(Format('Total de Registros a Processar: %d', [TotalRegs]));
    LogErros.Add('======================================================================');
    LogErros.Add('');

    modulo_dados.fdqueryentidade.First;
    while not modulo_dados.fdqueryentidade.Eof do
    begin
      vGeoEntCod    := modulo_dados.fdqueryentidade.FieldByName('geoentcod').AsString;
      vNomeEntidade := modulo_dados.fdqueryentidade.FieldByName('entnome').AsString;
      vEntCod       := Trim(modulo_dados.fdqueryentidade.FieldByName('entcod').AsString);

      // 1. Verifica se tem pendências moderadas
      if Pos('[PEND', UpperCase(modulo_dados.fdqueryentidade.FieldByName('entobservacoes').AsString)) > 0 then
      begin
        Inc(Pendencias);
        LogErros.Add(Format('[IGNORADA - PENDÊNCIAS] GeoCod: %s | Nome: %s | Motivo: Possui [PENDÊNCIAS] registradas no cadastro.',
                            [vGeoEntCod, vNomeEntidade]));
        modulo_dados.fdqueryentidade.Next;
        Application.ProcessMessages;
        Continue;
      end;

      // 2. Se entcod vazio, tenta achar via CPF
      if vEntCod = '' then
      begin
        with modulo_dados do
        begin
          fdquerysql18.Close; fdquerysql18.SQL.Clear;
          fdquerysql18.SQL.Text :=
            'SELECT geonumerodocumento FROM USER_geoapolo_entidade_documentos WITH (NOLOCK) ' +
            ' WHERE geoentcod = :geoentcod AND geotipodocumento LIKE ''%CPF/CNPJ%''';
          fdquerysql18.ParamByName('geoentcod').AsString := vGeoEntCod;
          if executaracao(fdquerysql18, fdbanco, true, dtsfdquerysql18) and (not fdquerysql18.IsEmpty) then
          begin
            fdquerysql1.Close; fdquerysql1.SQL.Clear;
            fdquerysql1.SQL.Text := 'SELECT entcod FROM entidades_geoapolo WHERE entcpfcgc = :geonumerodocumento';
            fdquerysql1.ParamByName('geonumerodocumento').AsString := fdquerysql18.FieldByName('geonumerodocumento').AsString;
            if executaracao(fdquerysql1, fdbanco, true, dtsfdquerysql1) and (not fdquerysql1.IsEmpty) then
              vEntCod := Trim(fdquerysql1.FieldByName('entcod').AsString);
          end;
        end;
      end;

      // 2.5. Garante contato integrado no Alvo (busca CPF ou integra primeiro)
      if not Self.GarantirContatoIntegradoAlvo(vGeoEntCod, API, vEntCodContato, vErroContato) then
      begin
        Inc(Falhas);
        LogErros.Add(Format('[FALHA - CONTATO] GeoCod: %s | Nome: %s | Motivo: %s',
                            [vGeoEntCod, vNomeEntidade, vErroContato]));
        modulo_dados.fdqueryentidade.Next;
        Application.ProcessMessages;
        Continue;
      end;

      // 3. Monta dados da entidade
      if not Self.MontarEntidadeParaEnvio(vGeoEntCod, Entidade, vTratCod) then
      begin
        Inc(Falhas);
        LogErros.Add(Format('[FALHA - MONTAGEM] GeoCod: %s | Nome: %s | Motivo: Erro ao carregar dependências da entidade.',
                            [vGeoEntCod, vNomeEntidade]));
        modulo_dados.fdqueryentidade.Next;
        Application.ProcessMessages;
        Continue;
      end;
      if (vEntCodContato <> '') and (Length(Entidade.Contatos) > 0) then
        Entidade.Contatos[0].Codigo := vEntCodContato;

      if vEntCod <> '' then
      begin
        Entidade.Operacao := 'A';
        Entidade.Codigo   := vEntCod;
      end
      else
      begin
        Entidade.Operacao := 'I';
        Entidade.Codigo   := '';
      end;

      // 4. Chamada da API REST Alvo
      if API.InserirAlterarEntidade(Entidade, vMensagem) then
      begin
        vNovoEntCod := ExtrairEntCodResposta(vMensagem);
        if vNovoEntCod <> '' then
          vEntCod := vNovoEntCod;

        Self.AtualizarEntidadeExportada(vGeoEntCod, vEntCod, vTratCod);
        Inc(Sucessos);
      end
      else
      begin
        Inc(Falhas);
        LogErros.Add(Format('[ERRO - API ALVO] GeoCod: %s | Nome: %s | Detalhes: %s',
                            [vGeoEntCod, vNomeEntidade, vMensagem]));
      end;

      // Move cursor no grid e atualiza interface sem abrir janelas modais
      modulo_dados.fdqueryentidade.Next;
      Application.ProcessMessages;
    end;

    // 5. Finalização e Log
    if (Falhas > 0) or (Pendencias > 0) then
    begin
      vLogPath := ExtractFilePath(Application.ExeName);
      if not DirectoryExists(vLogPath) then
        vLogPath := ExtractFilePath(ParamStr(0));
      vLogFileName := vLogPath + 'log_exportacao_alvo_' + FormatDateTime('yyyymmdd_hhnnss', Now) + '.txt';

      LogErros.Add('');
      LogErros.Add(Format('Resumo: Sucessos = %d, Falhas = %d, Ignoradas (Pendências) = %d', [Sucessos, Falhas, Pendencias]));
      try
        LogErros.SaveToFile(vLogFileName);
      except
        vLogFileName := 'c:\temp\log_exportacao_alvo_' + FormatDateTime('yyyymmdd_hhnnss', Now) + '.txt';
        LogErros.SaveToFile(vLogFileName);
      end;

      MessageDlg(Format('Exportação em lote finalizada!' + #13#10 +
                        'Sucessos: %d' + #13#10 +
                        'Falhas: %d' + #13#10 +
                        'Ignoradas (Pendências): %d' + #13#10#13#10 +
                        'O arquivo com o detalhamento dos erros foi gravado em:' + #13#10 + '%s',
                        [Sucessos, Falhas, Pendencias, vLogFileName]),
                 mtWarning, [mbOK], 0);
    end
    else
    begin
      MessageDlg(Format('Exportação em lote de todas as %d entidades concluída com 100%% de sucesso!', [Sucessos]),
                 mtInformation, [mbOK], 0);
    end;

  finally
    LogErros.Free;
    API.Free;
    Screen.Cursor := crDefault;
  end;
end;

// =============================================================================
// Filtro Avançado Multi-Campos
// =============================================================================
procedure Tfrmentidades.InicializarFiltroAvancado;
begin
  if not Assigned(gridCondicoes) then Exit;
  gridCondicoes.ColCount := 4;
  gridCondicoes.RowCount := 1;
  gridCondicoes.Cells[0, 0] := 'Conector';
  gridCondicoes.Cells[1, 0] := 'Campo';
  gridCondicoes.Cells[2, 0] := 'Operador';
  gridCondicoes.Cells[3, 0] := 'Valor';
  gridCondicoes.ColWidths[0] := 65;
  gridCondicoes.ColWidths[1] := 200;
  gridCondicoes.ColWidths[2] := 140;
  gridCondicoes.ColWidths[3] := 450;
  if cboFiltroConector.Items.Count > 0 then cboFiltroConector.ItemIndex := 0;
  if cboFiltroCampo.Items.Count > 0 then cboFiltroCampo.ItemIndex := 0;
  if cboFiltroOperador.Items.Count > 0 then cboFiltroOperador.ItemIndex := 0;
  edtFiltroValor.Clear;
end;

procedure Tfrmentidades.spbfiltroavancadoClick(Sender: TObject);
begin
  pnlFiltroAvancado.Visible := not pnlFiltroAvancado.Visible;
  if pnlFiltroAvancado.Visible then
  begin
    pnlFiltroAvancado.BringToFront;
    if gridCondicoes.RowCount <= 1 then
      InicializarFiltroAvancado;
  end;
end;

procedure Tfrmentidades.spbnovoClick(Sender: TObject);
begin
  Application.CreateForm(TfrmCadEntidade, frmcadentidade);
  frmcadentidade.controle := 'INCLUSÃO';
  if (integraentidadeapolo = 'Mescla') or (integraentidadeapolo = 'Não Integra') then
    frmcadentidade.lblentcod.Text := geoapolo_configcod(frmprincipal.codigo_empresa, 'USER_geoapolo_entidade', 'Sim')
  else if integraentidadeapolo = 'Integra' then
    frmcadentidade.lblentcod.Text := entcod_apolo_busca('S', frmcadentidade);
  frmcadentidade.ShowModal;
  if cbobuscabanco.Text <> '' then
    carrega_lista_entidades(cbobuscabanco.Text, 'Consulta', '');
end;

procedure Tfrmentidades.btnFecharFiltroAvancadoClick(Sender: TObject);
begin
  pnlFiltroAvancado.Visible := False;
end;

procedure Tfrmentidades.btnAdicionarCondicaoClick(Sender: TObject);
var
  R: Integer;
begin
  if cboFiltroCampo.ItemIndex < 0 then
  begin
    MessageDlg('Selecione um campo para o filtro.', mtWarning, [mbOK], 0);
    Exit;
  end;
  if cboFiltroOperador.ItemIndex < 0 then
  begin
    MessageDlg('Selecione um operador.', mtWarning, [mbOK], 0);
    Exit;
  end;
  if (cboFiltroOperador.ItemIndex < 6) and (Trim(edtFiltroValor.Text) = '') then
  begin
    MessageDlg('Informe o valor para a condição.', mtWarning, [mbOK], 0);
    edtFiltroValor.SetFocus;
    Exit;
  end;

  R := gridCondicoes.RowCount;
  gridCondicoes.RowCount := R + 1;
  if R = 1 then
    gridCondicoes.Cells[0, R] := 'ONDE'
  else
    gridCondicoes.Cells[0, R] := cboFiltroConector.Text;

  gridCondicoes.Cells[1, R] := cboFiltroCampo.Text;
  gridCondicoes.Cells[2, R] := cboFiltroOperador.Text;
  gridCondicoes.Cells[3, R] := edtFiltroValor.Text;

  edtFiltroValor.Clear;
  edtFiltroValor.SetFocus;
end;

procedure Tfrmentidades.btnRemoverCondicaoClick(Sender: TObject);
var
  i, SelRow: Integer;
begin
  SelRow := gridCondicoes.Row;
  if (SelRow <= 0) or (gridCondicoes.RowCount <= 1) then Exit;

  for i := SelRow to gridCondicoes.RowCount - 2 do
  begin
    gridCondicoes.Cells[0, i] := gridCondicoes.Cells[0, i + 1];
    gridCondicoes.Cells[1, i] := gridCondicoes.Cells[1, i + 1];
    gridCondicoes.Cells[2, i] := gridCondicoes.Cells[2, i + 1];
    gridCondicoes.Cells[3, i] := gridCondicoes.Cells[3, i + 1];
  end;
  gridCondicoes.RowCount := gridCondicoes.RowCount - 1;
  if gridCondicoes.RowCount > 1 then
    gridCondicoes.Cells[0, 1] := 'ONDE';
end;

procedure Tfrmentidades.btnLimparCondicoesClick(Sender: TObject);
begin
  InicializarFiltroAvancado;
end;

procedure Tfrmentidades.btnAtalhoGOPendentesClick(Sender: TObject);
begin
  InicializarFiltroAvancado;
  gridCondicoes.RowCount := 4;

  gridCondicoes.Cells[0, 1] := 'ONDE';
  gridCondicoes.Cells[1, 1] := 'Categoria (Nome)';
  gridCondicoes.Cells[2, 1] := 'Contém';
  gridCondicoes.Cells[3, 1] := 'GRUPO DE ORAÇÃO';

  gridCondicoes.Cells[0, 2] := 'E';
  gridCondicoes.Cells[1, 2] := 'Status Exportação Alvo (atualizou_apolo)';
  gridCondicoes.Cells[2, 2] := 'Diferente de';
  gridCondicoes.Cells[3, 2] := 'S';

  gridCondicoes.Cells[0, 3] := 'E';
  gridCondicoes.Cells[1, 3] := 'Código Alvo (entcod)';
  gridCondicoes.Cells[2, 3] := 'Está Vazio / Nulo';
  gridCondicoes.Cells[3, 3] := '';

  btnAplicarFiltroAvancadoClick(Sender);
end;

procedure Tfrmentidades.btnRestaurarFiltroPadraoClick(Sender: TObject);
begin
  pnlFiltroAvancado.Visible := False;
  carrega_lista_entidades('GeoApolo', 'Consulta', '');
  ConfigurarGridCompleto('GeoApolo');
end;

procedure Tfrmentidades.btnAplicarFiltroAvancadoClick(Sender: TObject);
var
  i: Integer;
  sWhere, sCond, sConector, sCampo, sOp, sVal, sColSQL: string;
begin
  if gridCondicoes.RowCount <= 1 then
  begin
    MessageDlg('Nenhuma condição foi adicionada para o filtro.', mtWarning, [mbOK], 0);
    Exit;
  end;

  sWhere := '';
  for i := 1 to gridCondicoes.RowCount - 1 do
  begin
    sConector := UpperCase(Trim(gridCondicoes.Cells[0, i]));
    sCampo    := Trim(gridCondicoes.Cells[1, i]);
    sOp       := Trim(gridCondicoes.Cells[2, i]);
    sVal      := Trim(gridCondicoes.Cells[3, i]);

    if SameText(sCampo, 'Categoria (Nome)') then
      sColSQL := 'e.categnome'
    else if SameText(sCampo, 'Categoria (Código)') then
      sColSQL := 'e.categcodestr'
    else if SameText(sCampo, 'Código Alvo (entcod)') then
      sColSQL := 'e.entcod'
    else if SameText(sCampo, 'Status Exportação Alvo (atualizou_apolo)') then
      sColSQL := 'ue.atualizou_apolo'
    else if SameText(sCampo, 'Nome da Entidade') then
      sColSQL := 'e.entnome'
    else if SameText(sCampo, 'Nome Fantasia') then
      sColSQL := 'e.entnomefant'
    else if SameText(sCampo, 'CPF / CNPJ') then
      sColSQL := 'e.entcpfcgc'
    else if SameText(sCampo, 'RG / IE') then
      sColSQL := 'e.entrgie'
    else if SameText(sCampo, 'Cidade') then
      sColSQL := 'e.cidnomecomp'
    else if SameText(sCampo, 'Estado (UF)') then
      sColSQL := 'e.ufsigla'
    else if SameText(sCampo, 'Bairro') then
      sColSQL := 'e.entbair'
    else if SameText(sCampo, 'CEP') then
      sColSQL := 'e.entcep'
    else if SameText(sCampo, 'Gênero') then
      sColSQL := 'e.entgenero'
    else if SameText(sCampo, 'Estado Civil') then
      sColSQL := 'e.entestcivil'
    else if SameText(sCampo, 'Observações') then
      sColSQL := 'e.entobservacoes'
    else
      sColSQL := 'e.entnome';

    if SameText(sCampo, 'Categoria (Código)') then
    begin
      if SameText(sOp, 'Diferente de') then
        sCond := 'NOT EXISTS (SELECT 1 FROM USER_geoapolo_entcateg uec WITH (NOLOCK) WHERE uec.geoentcod = e.geoentcod AND uec.geocategcodestr = ' + QuotedStr(sVal) + ')'
      else if SameText(sOp, 'Está Vazio / Nulo') then
        sCond := 'NOT EXISTS (SELECT 1 FROM USER_geoapolo_entcateg uec WITH (NOLOCK) WHERE uec.geoentcod = e.geoentcod)'
      else if SameText(sOp, 'Não Está Vazio') then
        sCond := 'EXISTS (SELECT 1 FROM USER_geoapolo_entcateg uec WITH (NOLOCK) WHERE uec.geoentcod = e.geoentcod)'
      else
        // Filtro exato na categoria selecionada sem trazer níveis abaixo
        sCond := 'EXISTS (SELECT 1 FROM USER_geoapolo_entcateg uec WITH (NOLOCK) WHERE uec.geoentcod = e.geoentcod AND uec.geocategcodestr = ' + QuotedStr(sVal) + ')';
    end
    else
    begin
      if SameText(sOp, 'Contém') then
        sCond := sColSQL + ' LIKE ' + QuotedStr('%' + sVal + '%')
      else if SameText(sOp, 'Não Contém') then
        sCond := '(' + sColSQL + ' NOT LIKE ' + QuotedStr('%' + sVal + '%') + ' OR ' + sColSQL + ' IS NULL)'
      else if SameText(sOp, 'Igual a') then
        sCond := sColSQL + ' = ' + QuotedStr(sVal)
      else if SameText(sOp, 'Diferente de') then
        sCond := '(' + sColSQL + ' <> ' + QuotedStr(sVal) + ' OR ' + sColSQL + ' IS NULL)'
      else if SameText(sOp, 'Começa com') then
        sCond := sColSQL + ' LIKE ' + QuotedStr(sVal + '%')
      else if SameText(sOp, 'Termina com') then
        sCond := sColSQL + ' LIKE ' + QuotedStr('%' + sVal)
      else if SameText(sOp, 'Está Vazio / Nulo') then
        sCond := '(' + sColSQL + ' IS NULL OR RTRIM(LTRIM(' + sColSQL + ')) = '''')'
      else if SameText(sOp, 'Não Está Vazio') then
        sCond := '(' + sColSQL + ' IS NOT NULL AND RTRIM(LTRIM(' + sColSQL + ')) <> '''')'
      else
        sCond := sColSQL + ' LIKE ' + QuotedStr('%' + sVal + '%');
    end;

    if sWhere = '' then
      sWhere := '(' + sCond + ')'
    else
    begin
      if (sConector = 'OU') or (sConector = 'OR') then
        sWhere := sWhere + ' OR (' + sCond + ')'
      else
        sWhere := sWhere + ' AND (' + sCond + ')';
    end;
  end;

  Self.AplicarFiltroAvancadoSQL(sWhere);
  ConfigurarGridCompleto('GeoApolo');
end;

// =============================================================================
// AplicarFiltroAvancadoSQL
// Executa a query com a cláusula WHERE montada pelas condições do filtro
// =============================================================================
procedure Tfrmentidades.AplicarFiltroAvancadoSQL(const AWhereClause: string);
var
  sqlview: string;
begin
  if cbobuscabanco.Text <> 'GeoApolo' then
  begin
    MessageDlg('O filtro avançado multi-campos está disponível para a base GeoApolo.', mtInformation, [mbOK], 0);
    Exit;
  end;

  Screen.Cursor := crSQLWait;
  try
    sqlview :=
      'SELECT * FROM entidades_geoapolo e WITH(NOLOCK)' +
      ' INNER JOIN user_geoapolo_entidade ue WITH(NOLOCK) ON e.geoentcod = ue.geoentcod';

    if Trim(AWhereClause) <> '' then
      sqlview := sqlview + ' WHERE ' + AWhereClause
    else
      sqlview := sqlview + ' WHERE (ue.atualizou_apolo IS NULL OR ue.atualizou_apolo <> ''S'')';

    sqlview := sqlview +
      ' ORDER BY CASE WHEN ue.atualizou_apolo = ''N'' ' +
      ' AND (e.Entobservacoes IS NULL OR e.Entobservacoes NOT LIKE ''%[PEND%NCIAS]%'') THEN 0 ELSE 1 END';

    modulo_dados.fdqueryentidade.Close;
    modulo_dados.fdqueryentidade.SQL.Clear;
    modulo_dados.fdqueryentidade.SQL.Text := sqlview;
    modulo_dados.fdqueryentidade.Open;

    lblmensagemgeoapolo.Caption := Format('%d registros encontrados no filtro avançado.', [modulo_dados.fdqueryentidade.RecordCount]);
    if modulo_dados.fdqueryentidade.RecordCount = 0 then
      lblmensagemgeoapolo.Font.Color := clMaroon
    else
      lblmensagemgeoapolo.Font.Color := clNavy;
  finally
    Screen.Cursor := crDefault;
  end;
end;

end.
