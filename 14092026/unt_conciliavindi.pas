unit unt_conciliavindi;

interface

uses
  Winapi.Windows, Winapi.Messages,
  System.SysUtils, System.Variants, System.Classes,
  Vcl.Graphics, Vcl.Controls, Vcl.Forms, Vcl.Dialogs,
  Vcl.ComCtrls, Vcl.StdCtrls, Vcl.Buttons, Vcl.ExtCtrls,
  Vcl.Grids, Vcl.DBGrids, Vcl.Mask, Vcl.Menus,
  Data.DB,
  FireDAC.Comp.Client,    // TFDQuery, TFDConnection
  FireDAC.Stan.Param,     // TFDParams
  FireDAC.DApt;           // FireDAC dataset adapters

type
  // -------------------------------------------------------------------------
  // Registro de resultado da verificação de integridade de uma transação Vindi
  // -------------------------------------------------------------------------
  TIntegridadeResult = record
    Erros: TArray<string>;
    function TemErros: Boolean;
  end;

  // -------------------------------------------------------------------------
  // Serviço de domínio: regras de integridade da conciliação Vindi
  // -------------------------------------------------------------------------
  TConciliaVindiService = class
  private
    FQueryTemp: TFDQuery;   // query reutilizável injetada pelo construtor

    procedure AdicionarErro(var AResult: TIntegridadeResult; const AMensagem: string);
    function  BuscaValorOriginal(const APedidoId: string; out AValor: Single): Boolean;
    function  BuscaEntidadeIdVindi(const APedidoId: string; out AEntidadeId: string): Boolean;
    function  BuscaCpfPorEntidadeVindi(const AEntidadeId: string; out ACpf: string;
                                       var AResult: TIntegridadeResult): Boolean;
    procedure ChecaStatusVindi(const AEntidadeId: string; var AResult: TIntegridadeResult);
    procedure ChecaCategoriaApolo(const ACpf: string; var AResult: TIntegridadeResult;
                                  out AEntCod, AEntNome: string);
    procedure ChecaDuplicidadeCategoria(const AEntCod: string; var AResult: TIntegridadeResult);
    procedure ChecaTipoCobrancaEValor(const ACpf: string; AValorOriginal: Single;
                                      var AResult: TIntegridadeResult);
    function  RemoverFormatacaoCpfCnpj(const AValor: string): string;
  public
    constructor Create(AQueryTemp: TFDQuery);

    /// Executa todas as verificações de integridade para um pedido Vindi.
    /// Retorna registro com lista de erros encontrados (vazio = sem problemas).
    function ChecarIntegridade(const APedidoId: string): TIntegridadeResult;
  end;

  // -------------------------------------------------------------------------
  // Formulário principal
  // -------------------------------------------------------------------------
  Tfrmconciliavindi = class(TForm)
    panelmenu      : TPanel;
    spbsalvar      : TSpeedButton;
    spblimpar      : TSpeedButton;
    spbdeletar     : TSpeedButton;
    spbabreos      : TSpeedButton;
    spbsair        : TSpeedButton;
    lblmsg1        : TLabel;
    StatusBar1     : TStatusBar;
    GroupBox1      : TGroupBox;
    mskdtinicial   : TMaskEdit;
    mskdtfinal     : TMaskEdit;
    lbldtfinal     : TLabel;
    lbldatainicial : TLabel;
    griddocumentosaconciliar : TDBGrid;
    btnefetuafiltro          : TBitBtn;
    chkintegradasapolo       : TCheckBox;
    GroupBox2                : TGroupBox;
    lblnumerotransacoes      : TLabel;
    lblntransacoes           : TLabel;
    lblvalorbruto            : TLabel;
    lblvalorbrutomoeda       : TLabel;
    lblvalortarifas          : TLabel;
    lblvalortarifasreal      : TLabel;
    lblvalorliquido          : TLabel;
    lblvalorliquidomoeda     : TLabel;
    btnchecaintegridade      : TBitBtn;
    btnpreviaapolo           : TBitBtn;
    pnllogerros              : TPanel;
    memologerros             : TMemo;
    lbllogerros              : TLabel;
    grpprevia                : TGroupBox;
    btnvolta                 : TBitBtn;
    grpalterayapay           : TGroupBox;
    btnsalvaralteracoes      : TBitBtn;
    lblstatusentidadevindi   : TLabel;
    cbostatus                : TComboBox;
    lblyapayid               : TLabeledEdit;
    lblcpfcnpj               : TLabeledEdit;
    lbldataAlterado          : TLabel;
    mskdttransacao           : TMaskEdit;
    lblvindientidadeid       : TLabeledEdit;
    btneditartransacao       : TBitBtn;
    lblpreviaentidade        : TLabel;
    lblpreviaentidadetexto   : TLabel;
    lblpreviacpfcnpj         : TLabel;
    lblpreviacpfcnpjtexto    : TLabel;
    lblpreviavalorbruto      : TLabel;
    lblpreviatarifa          : TLabel;
    lblpreviavalorliquido    : TLabel;
    lblpreviavalorbrutotexto : TLabel;
    lblpreviatarifatexto     : TLabel;
    lblpreviavalorliquidotexto : TLabel;
    lblpreviacfin            : TLabel;
    lblpreviatipolanc        : TLabel;
    lblpreviacfintexto       : TLabel;
    lblpreviatipolanctexto   : TLabel;
    popmenu                  : TPopupMenu;
    popmnugravaconfig        : TMenuItem;
    lblpedidoid              : TLabeledEdit;

    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);

    procedure btnefetuafiltroClick(Sender: TObject);
    procedure btnchecaintegridadeClick(Sender: TObject);
    procedure btnpreviaapoloClick(Sender: TObject);
    procedure btnsalvaralteracoesClick(Sender: TObject);
    procedure btneditartransacaoClick(Sender: TObject);
    procedure btnvoltaClick(Sender: TObject);

    procedure mskdtinicialKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure mskdtfinalKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure mskdttransacaoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblyapayidKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblvindientidadeidKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure cbostatusKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblcpfcnpjKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblprocurarporKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);

    procedure griddocumentosaconciliarDrawColumnCell(Sender: TObject;
      const Rect: TRect; DataCol: Integer; Column: TColumn; State: TGridDrawState);

    procedure popmnugravaconfigClick(Sender: TObject);
    procedure spbsairClick(Sender: TObject);

  private
    // ----- estado interno encapsulado -----
    FDataInicial         : string;
    FDataFinal           : string;
    FValorOriginal       : Single;
    FUserValorContribuicao: Single;
    FCpfCnpj             : string;

    // serviço de domínio
    FVindiService: TConciliaVindiService;

    // ----- helpers de UI -----
    procedure AtualizarPainelResumo;
    procedure PreencherComboCampos;
    procedure ExibirPainelEdicao(AVisivel: Boolean);
    procedure ExibirPainelPrevia(AVisivel: Boolean);
    procedure LimparPainelPrevia;

    // ----- helpers de data -----
    function DataMascaraParaSQL(const AData: string): string;
    function DataMascaraParaDatetime(const AData: string): string;

    // ----- construção de SQL reutilizável -----
    function SqlBaseConcilia(AIntegradas: Boolean): string;
    function SqlResumoTransacoes(AIntegradas: Boolean): string;

  public
    { Public declarations }
  end;

var
  frmconciliavindi: Tfrmconciliavindi;

implementation

uses
  unt_dados, funcoes, unt_principal, unt_logon;

{$R *.dfm}

// =============================================================================
//  TIntegridadeResult
// =============================================================================

function TIntegridadeResult.TemErros: Boolean;
begin
  Result := Length(Erros) > 0;
end;

// =============================================================================
//  TConciliaVindiService
// =============================================================================

constructor TConciliaVindiService.Create(AQueryTemp: TFDQuery);
begin
  inherited Create;
  FQueryTemp := AQueryTemp;
end;

procedure TConciliaVindiService.AdicionarErro(var AResult: TIntegridadeResult;
  const AMensagem: string);
var
  L: Integer;
begin
  L := Length(AResult.Erros);
  SetLength(AResult.Erros, L + 1);
  AResult.Erros[L] := AMensagem;
end;

function TConciliaVindiService.RemoverFormatacaoCpfCnpj(const AValor: string): string;
begin
  Result := buscatroca(buscatroca(buscatroca(AValor, '.', ''), '-', ''), '/', '');
end;

// --- Busca valor original da transação Yapay ---
function TConciliaVindiService.BuscaValorOriginal(const APedidoId: string; out AValor: Single): Boolean;
var
   sql:string;
begin
  Result := False;
  AValor  := 0;
  sql:='SELECT PrecoOriginal FROM USER_YapayTransacoes WHERE pedidoid = :APedidosId';
  modulo_dados.fdquerysql.close;
  modulo_dados.fdquerysql.sql.clear;
  modulo_dados.fdquerysql.sql.text := sql;
  modulo_dados.fdquerysql.parambyname('APedidosId').asstring := APedidoId;
  if funcoes.executaracao(modulo_dados.fdquerysql,modulo_dados.fdbanco,true,modulo_dados.dtsfdquerysql) then
  begin
    AValor := modulo_dados.fdquerysql.FieldByName('PrecoOriginal').AsSingle;
    Result := True;
  end;
end;

// --- Busca a entidade Vindi a partir do pedido ---
function TConciliaVindiService.BuscaEntidadeIdVindi(const APedidoId: string;
  out AEntidadeId: string): Boolean;
var
   sql:string;
begin
  Result     := False;
  AEntidadeId := '';
  sql:= 'SELECT vindientidadeid FROM user_vinditransacoes WHERE vinditransacaoid = :TVindiransacaoID';
  modulo_dados.fdquerysql.close;
  modulo_dados.fdquerysql.sql.clear;
  modulo_dados.fdquerysql.sql.text := sql;
  modulo_dados.fdquerysql.parambyname('TVindiransacaoID').asstring := APedidoId;
  if funcoes.executaracao(modulo_dados.fdquerysql, modulo_dados.fdbanco,true,modulo_dados.dtsfdquerysql) then
  begin
    AEntidadeId := modulo_dados.fdquerysql.FieldByName('vindientidadeid').AsString;
    Result      := True;
  end;
end;

// --- Busca CPF/CNPJ da entidade Vindi (somente status active) ---
function TConciliaVindiService.BuscaCpfPorEntidadeVindi(const AEntidadeId: string;
  out ACpf: string; var AResult: TIntegridadeResult): Boolean;
var
   sql:string;
begin
  Result := False;
  ACpf   := '';
  sql:= 'SELECT cpfcnpj FROM uservindi_entidade WHERE vindientidadeid = :AEntidadeId AND status = :AStatus';
  modulo_dados.fdquerysql.close;
  modulo_dados.fdquerysql.sql.clear;
  modulo_dados.fdquerysql.sql.text := sql;
  modulo_dados.fdquerysql.parambyname('AEntidadeId').asstring := AEntidadeId;
  modulo_dados.fdquerysql.parambyname('AStatus').asstring := 'active';
  if funcoes.executaracao(modulo_dados.fdquerysql, modulo_dados.fdbanco,true,modulo_dados.dtsfdquerysql) AND (modulo_dados.fdquerysql.FieldByName('cpfcnpj').AsString <> '') then
    begin
      ACpf   := modulo_dados.fdquerysql.FieldByName('cpfcnpj').AsString;
      Result := True;
    end
  else
    AdicionarErro(AResult,
      'O(A) COLABORADOR VINDI ' + AEntidadeId +
      ' NÃO TEM CPF/CNPJ CADASTRADO NA PLATAFORMA');
end;

// --- Verifica se a entidade Vindi está ativa ---
procedure TConciliaVindiService.ChecaStatusVindi(const AEntidadeId: string;
  var AResult: TIntegridadeResult);
var
   sql:string;
begin
   modulo_dados.fdquerysql.close;
   modulo_dados.fdquerysql.sql.clear;
   sql:='SELECT status FROM uservindi_entidade WHERE vindientidadeid = :AEntidadeId';
   modulo_dados.fdquerysql.sql.text := sql;
   modulo_dados.fdquerysql.parambyname('AEntidadeId').asstring:= AEntidadeId;
   if executaracao(modulo_dados.fdquerysql,modulo_dados.fdbanco, true, modulo_dados.dtsfdquerysql) then
     begin
        if modulo_dados.fdquerysql.FieldByName('status').AsString = 'inactive' then
              AdicionarErro(AResult,'A ENTIDADE VINDI: ' + AEntidadeId +' ESTÁ COM STATUS INATIVO E NÃO SERÁ IMPORTADA NA INTEGRAÇÃO');
     end
  else
     AdicionarErro(AResult,'NÃO EXISTE ESTA ENTIDADE ID ' + AEntidadeId +' NA TABELA DE ENTIDADES VINDI. VERIFIQUE.');
end;

// --- Constante auxiliar para a cláusula IN de categorias ---
function CategoriaSubstringIn: string;
begin
  Result :=
    QuotedStr('02.001') + ', ' + QuotedStr('02.002') + ', ' +
    QuotedStr('03.001') + ', ' + QuotedStr('03.002') + ', ' +
    QuotedStr('03.003') + ', ' + QuotedStr('03.004') + ', ' +
    QuotedStr('03.005');
end;

// --- Verifica existência e categoria no Apolo ---
procedure TConciliaVindiService.ChecaCategoriaApolo(const ACpf: string;
  var AResult: TIntegridadeResult; out AEntCod, AEntNome: string);
var
  sql,CpfLimpo: string;
begin
  AEntCod  := '';
  AEntNome := '';
  CpfLimpo := RemoverFormatacaoCpfCnpj(ACpf);
  modulo_dados.fdquerysql.close;
  modulo_dados.fdquerysql.sql.clear;
  sql:='SELECT e.entcod, e.entnome FROM entidade e WITH(NOLOCK)  WHERE entcpfcgc = :Ecpf';
  modulo_dados.fdquerysql.sql.text := sql;
  modulo_dados.fdquerysql.parambyname('Ecpf').asstring := CpfLimpo;
  if executaracao(modulo_dados.fdquerysql,modulo_dados.fdbanco, true,modulo_dados.dtsfdquerysql) then
    begin
      AEntCod  := modulo_dados.fdquerysql.FieldByName('entcod').AsString;
      AEntNome := modulo_dados.fdquerysql.FieldByName('entnome').AsString;

      // Checa se pertence a alguma categoria do setor de projetos
      modulo_dados.fdquerysql.close;
      modulo_dados.fdquerysql.sql.clear;
      sql:='SELECT categcodestr FROM ent_categ WHERE SUBSTRING(categcodestr, 1, 6) ';
      sql:=sql+' IN (:CategoriaSubstringIn) AND entcod =:AEntcod ' ;
      modulo_dados.fdquerysql.sql.text := sql;
      modulo_dados.fdquerysql.parambyname('CategoriaSubstringIn').asstring := CategoriaSubstringIn;
      modulo_dados.fdquerysql.parambyname('AEntcod').asstring := AEntcod;
      if executaracao(modulo_dados.fdquerysql,modulo_dados.fdbanco, true, modulo_dados.dtsfdquerysql) then
         begin
            AdicionarErro(AResult,'A ENTIDADE CÓDIGO Nº ' + AEntCod +' NÃO ESTÁ NA CATEGORIA DE ENTIDADES DO SETOR DE ARRECADAÇÃO!');
         end ;
    end
  else
     AdicionarErro(AResult,'O CPF/CNPJ ' + CpfLimpo + ' NÃO FOI ENCONTRADO NA BASE DO APOLO. VERIFIQUE!');
end;

// --- Verifica duplicidade de categoria ---
procedure TConciliaVindiService.ChecaDuplicidadeCategoria(const AEntCod: string;
  var AResult: TIntegridadeResult);
var
   sql:string;
begin
  if AEntCod = '' then Exit;
     begin
        modulo_dados.fdquerysql.close;
        modulo_dados.fdquerysql.sql.clear;
        sql:='SELECT ec.entcod, COUNT(1) AS Numero ' +
             ' FROM ent_categ ec WITH(NOLOCK) ' +
             ' WHERE SUBSTRING(ec.categcodestr, 1, 6) IN (:Categorias)' +
             ' AND ec.entcod = :AEntcod ' +
             ' GROUP BY ec.entcod, SUBSTRING(ec.categcodestr, 1, 6)'+
             ' HAVING COUNT(1) > 1';
        modulo_dados.fdquerysql7.close;
        modulo_dados.fdquerysql7.sql.clear;
        modulo_dados.fdquerysql7.sql.text := sql;
        modulo_dados.fdquerysql7.parambyname('Categorias').asstring := CategoriaSubstringIn;
        modulo_dados.fdquerysql7.parambyname('AEntcod').asstring := AEntcod;
        if executaracao(modulo_dados.fdquerysql7,modulo_dados.fdbanco,true,modulo_dados.dtsfdquerysql7) and (modulo_dados.fdquerysql.FieldByName('numero').AsInteger > 1) then
           begin
              AdicionarErro(AResult,'A ENTIDADE ' + AEntCod +
                ' ESTÁ EM MAIS DE UMA CATEGORIA DO GRUPO DE PROJETOS.' +
                ' FAÇA A CORREÇÃO PELO SISTEMA APOLO!');
           end;
     end;
end;

// --- Verifica tipo de cobrança e divergência de valor ---
procedure TConciliaVindiService.ChecaTipoCobrancaEValor(const ACpf: string;
  AValorOriginal: Single; var AResult: TIntegridadeResult);
var
  CpfLimpo       : string;
  UserValor       : Single;
  sql,EntCod, EntNome : string;
begin
  if ACpf = '' then Exit;

    CpfLimpo := RemoverFormatacaoCpfCnpj(ACpf);
    sql:='SELECT e.entcod, e.entnome, e.tipocobcod, ue.USERValor_Contribuicao'+
    ' FROM entidade e WITH(NOLOCK)' +
    ' INNER JOIN u_entidade ue WITH(NOLOCK) ON e.entcod = ue.entcod' +
    ' WHERE e.entcpfcgc = :CpfLimpo';
    modulo_dados.fdquerysql.close;
    modulo_dados.fdquerysql.sql.clear;
    modulo_dados.fdquerysql.sql.text := sql;
    modulo_dados.fdquerysql.parambyname('CpfLimpo').asstring:= CpfLimpo;
    if executaracao(modulo_dados.fdquerysql,modulo_dados.fdbanco, true, modulo_dados.dtsfdquerysql) then
       begin
       end;

  if modulo_dados.fdquerysql.IsEmpty then Exit;

  EntCod   := modulo_dados.fdquerysql.FieldByName('entcod').AsString;
  EntNome  := modulo_dados.fdquerysql.FieldByName('entnome').AsString;
  UserValor := modulo_dados.fdquerysql.FieldByName('USERValor_Contribuicao').AsSingle;

  if AValorOriginal <> UserValor then
    AdicionarErro(AResult,
      'A ENTIDADE ' + EntCod + ' - ' + EntNome +
      ' FEZ UMA DOAÇÃO NO VALOR DE R$' + FloatToStr(AValorOriginal) +
      ' E NO SEU CADASTRO ESTÁ O VALOR DE R$ ' + FloatToStr(UserValor));

  if modulo_dados.fdquerysql.FieldByName('tipocobcod').AsString <> '0000011' then
    AdicionarErro(AResult,
      'A ENTIDADE ' + EntCod + ' - ' + EntNome +
      ' ESTÁ COM TIPO DE COBRANÇA ' + FQueryTemp.FieldByName('tipocobcod').AsString +
      ' - QUE É DIFERENTE DO CRÉDITO RECORRENTE');
end;

// --- Ponto de entrada público: executa todas as verificações ---
function TConciliaVindiService.ChecarIntegridade(const APedidoId: string): TIntegridadeResult;
var
  EntidadeId : string;
  Cpf        : string;
  EntCod     : string;
  EntNome    : string;
  ValorOrig  : Single;
begin
  SetLength(Result.Erros, 0);

  // 1. Valor original da transação Yapay
  BuscaValorOriginal(APedidoId, ValorOrig);

  // 2. EntidadeId na tabela Vindi
  if not BuscaEntidadeIdVindi(APedidoId, EntidadeId) then Exit;

  // 3. CPF/CNPJ da entidade Vindi
  if not BuscaCpfPorEntidadeVindi(EntidadeId, Cpf, Result) then
  begin
    ChecaStatusVindi(EntidadeId, Result);   // status mesmo sem CPF
    Exit;
  end;

  // 4. Status da entidade Vindi
  ChecaStatusVindi(EntidadeId, Result);

  // 5. Categoria no Apolo
  ChecaCategoriaApolo(Cpf, Result, EntCod, EntNome);

  // 6. Duplicidade de categoria
  ChecaDuplicidadeCategoria(EntCod, Result);

  // 7. Tipo de cobrança e valor
  ChecaTipoCobrancaEValor(Cpf, ValorOrig, Result);
end;

// =============================================================================
//  Tfrmconciliavindi — ciclo de vida
// =============================================================================

procedure Tfrmconciliavindi.FormCreate(Sender: TObject);
begin
  // Injeta a query temporária disponível no módulo de dados como FDQuery
  FVindiService := TConciliaVindiService.Create(modulo_dados.fdquerysql6);
end;

procedure Tfrmconciliavindi.FormDestroy(Sender: TObject);
begin
  FVindiService.Free;
end;

procedure Tfrmconciliavindi.FormActivate(Sender: TObject);
begin
  StatusBar1.Panels[1].Text := configura_statusbar('a');
  StatusBar1.Panels[3].Text := configura_statusbar('a');
  StatusBar1.Panels[5].Text := frmprincipal.nomeserversql;
  FCpfCnpj := 'a';
  StatusBar1.Refresh;
end;

procedure Tfrmconciliavindi.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Action := caFree;
end;

procedure Tfrmconciliavindi.FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F10 then
    spbsair.Click;
end;

// =============================================================================
//  Helpers privados
// =============================================================================

function Tfrmconciliavindi.DataMascaraParaSQL(const AData: string): string;
begin
  // entrada: DD/MM/AAAA → saída: AAAA/MM/DD
  Result :=
    Copy(AData, 7, 4) + '/' +
    Copy(AData, 4, 2) + '/' +
    Copy(AData, 1, 2);
end;

function Tfrmconciliavindi.DataMascaraParaDatetime(const AData: string): string;
begin
  // entrada: DD/MM/AAAA... → saída: MM/DD/AAAA...
  Result :=
    Copy(AData, 4, 2) + '/' +
    Copy(AData, 1, 2) + '/' +
    Copy(AData, 7, Length(AData) - 6);
end;

function Tfrmconciliavindi.SqlBaseConcilia(AIntegradas: Boolean): string;
const
  FLAG_S = 'S';
  FLAG_N = 'N';
var
  Flag: string;
begin
  Flag := IfThen(AIntegradas, FLAG_S, FLAG_N);
  Result :=
    'SELECT * FROM VW_USER_ConciliaVindi vwucv WITH(NOLOCK)' +
    ' WHERE CAST(vwucv.alterado AS date) BETWEEN ' + QuotedStr(FDataInicial) +
    ' AND ' + QuotedStr(FDataFinal) +
    ' AND vwucv.tipo <> ' + QuotedStr('Dinheiro') +
    ' AND vwucv.flagapolo = ' + QuotedStr(Flag) +
    ' ORDER BY CAST(vwucv.alterado AS date) ASC';
end;

function Tfrmconciliavindi.SqlResumoTransacoes(AIntegradas: Boolean): string;
const
  FLAG_S = 'S';
  FLAG_N = 'N';
var
  Flag: string;
begin
    Flag := IfThen(AIntegradas, FLAG_S, FLAG_N);
  Result :=
    'DECLARE @n NUMERIC(10), @vb NUMERIC(14,2), @vt NUMERIC(14,2), @vl NUMERIC(14,2) ' +
    'SELECT @n = COUNT(1), @vb = SUM(uyt.precooriginal), @vt = SUM(uyt.taxa), @vl = SUM(uyt.precopago) ' +
    'FROM USER_YapayTransacoes uyt WITH(NOLOCK) ' +
    'WHERE CAST(uyt.alterado AS date) BETWEEN :FDataInicial AND :FDataFinal' +
    ' AND uyt.flagapolo = ' + quotedstr(Flag) +
    ' SELECT @n AS ntransacoes, @vb AS valorbruto, @vt AS tarifa, @vl AS valorliquido';

end;

procedure Tfrmconciliavindi.AtualizarPainelResumo;
var
   retorno:string;
begin
  with modulo_dados do
  begin
    retorno:=SqlResumoTransacoes(chkintegradasapolo.Checked);
    fdquerysql5.close;
    fdquerysql5.sql.clear;
    fdquerysql5.sql.text:= retorno;
    fdquerysql5.parambyname('FDataInicial').asdate := strtodate(mskdtinicial.text);
    fdquerysql5.parambyname('FDataFinal').asdate := strtodate(mskdtfinal.text);

    if executaracao(fdquerysql5,modulo_dados.fdbanco,true,dtsfdquerysql5) then
    begin
      lblntransacoes.Caption      := IntToStr(fdquerysql5.FieldByName('ntransacoes').AsInteger);
      lblvalorbrutomoeda.Caption  := FormatFloat('R$ ,0.00,', fdquerysql5.FieldByName('valorbruto').asfloat);
      lblvalortarifasreal.Caption := FormatFloat('R$ ,0.00,', fdquerysql5.FieldByName('tarifa').asfloat);
      lblvalorliquidomoeda.Caption:= FormatFloat('R$ ,0.00,', fdquerysql5.FieldByName('valorliquido').asfloat);
      lblntransacoes.Refresh;
      lblvalorbrutomoeda.Refresh;
      lblvalortarifasreal.Refresh;
      lblvalorliquidomoeda.Refresh;
    end;
  end;
end;

procedure Tfrmconciliavindi.PreencherComboCampos;
begin

end;

procedure Tfrmconciliavindi.ExibirPainelEdicao(AVisivel: Boolean);
begin
  grpalterayapay.Visible := AVisivel;
  if AVisivel then
  begin
    grpalterayapay.Top  := 13;
    grpalterayapay.Left := 416;
  end
  else
  begin
    grpalterayapay.Top  := 283;
    grpalterayapay.Left := 723;
  end;
end;

procedure Tfrmconciliavindi.ExibirPainelPrevia(AVisivel: Boolean);
begin
  grpprevia.Visible := AVisivel;
  if AVisivel then
  begin
    grpprevia.Top  := 13;
    grpprevia.Left := 416;
  end
  else
  begin
    grpprevia.Top  := 25;
    grpprevia.Left := 560;
  end;
end;

procedure Tfrmconciliavindi.LimparPainelPrevia;
begin
  lblpreviaentidadetexto.Caption    := '...';
  lblpreviacpfcnpjtexto.Caption     := '...';
  lblpreviatarifatexto.Caption      := '...';
  lblpreviavalorliquidotexto.Caption:= '...';
  grpprevia.Refresh;
end;

// =============================================================================
//  Botões e eventos
// =============================================================================

procedure Tfrmconciliavindi.btnefetuafiltroClick(Sender: TObject);
var
   sql:string;
begin
  FDataInicial := DataMascaraParaSQL(mskdtinicial.Text);
  FDataFinal   := DataMascaraParaSQL(mskdtfinal.Text);

  with modulo_dados do
  begin
    sql:= SqlBaseConcilia(chkintegradasapolo.Checked);
    fdquerysql4.close;
    fdquerysql4.sql.clear;
    fdquerysql4.sql.text := sql;
    if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
    begin
      AtualizarPainelResumo;
      PreencherComboCampos;

      dtsfdquerysql4.DataSet := fdquerysql4;
     { carrega_config('GEOCONCILIAVINDIAPOLO', frmconciliavindi, cbocampo, cbordem, rdgcrescente, rdgdecrescente);
      configura_grid('GEOCONCILIAVINDIAPOLO', frmconciliavindi, 'griddocumentosaconciliar',
        frmlogon.nomeusuario, griddocumentosaconciliar, modulo_dados.dtsquerysql);  }
      setcursorsql('');
      griddocumentosaconciliar.DataSource := dtsfdquerysql4;
      griddocumentosaconciliar.Refresh;
      mskdtinicial.SetFocus;
    end;
  end;
end;

procedure Tfrmconciliavindi.btnchecaintegridadeClick(Sender: TObject);
var
  Resultado   : TIntegridadeResult;
  PedidoId    : string;
  Mensagem    : string;
begin
  memologerros.Clear;
  with modulo_dados do
  begin
    fdquerysql4.First;
    while not fdquerysql4.Eof do
    begin
      PedidoId  := fdquerysql4.FieldByName('pedidoid').AsString;
      Resultado := FVindiService.ChecarIntegridade(PedidoId);

      for Mensagem in Resultado.Erros do
        memologerros.Lines.Add(Mensagem);

      fdquerysql4.Next;
    end;
  end;
  memologerros.Lines.Add('FINAL DA CHECAGEM DE INTEGRIDADE DOS DADOS!!!');
  memologerros.Refresh;
end;

procedure Tfrmconciliavindi.btnpreviaapoloClick(Sender: TObject);
var
  sql, EntCod, EntNome, CpfApolo: string;
begin
  if chkintegradasapolo.Checked then
    begin
      MessageDlg('NÃO É POSSÍVEL TER PRÉVIA DO QUE JÁ FOI IMPORTADO PARA O APOLO', mtError, [mbOK], 0);
      mskdtinicial.SetFocus;
      Exit;
    end;

  with modulo_dados do
  begin
     sql:='SELECT entcod, entnome, entcpfcgc FROM entidade WHERE entcpfcgc = :ACpf ';
     fdquerysql9.close;
     fdquerysql9.sql.clear;
     fdquerysql9.sql.text := sql;
     fdquerysql9.parambyname('ACpf').asstring :=buscatroca(buscatroca(buscatroca(fdquerysql4.FieldByName('cpfcnpj').AsString,'.',''),'-',''),'/','');

     if executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
        begin
          EntCod   := fdquerysql9.FieldByName('entcod').Text;
          EntNome  := fdquerysql9.FieldByName('entnome').Text;
          CpfApolo := fdquerysql9.FieldByName('entcpfcgc').Text;
        end;

    lblpreviaentidadetexto.Caption    := EntCod + ' - ' + EntNome;
    lblpreviacpfcnpjtexto.Caption     := CpfApolo;
    lblpreviavalorbrutotexto.Caption  := FormatFloat('R$ ,0.00,', StrToFloat(fdquerysql4.FieldByName('precooriginal').AsString));
    lblpreviatarifatexto.Caption      := FormatFloat('R$ ,0.00,', StrToFloat(fdquerysql4.FieldByName('taxa').AsString));
    lblpreviavalorliquidotexto.Caption:= FormatFloat('R$ ,0.00,', StrToFloat(fdquerysql4.FieldByName('precopago').AsString));
  end;
  ExibirPainelPrevia(True);
  grpprevia.Refresh;
end;

procedure Tfrmconciliavindi.btnsalvaralteracoesClick(Sender: TObject);
var
  sql,ValteradoConvertido: string;
begin
  if MessageDlg('Confirma a alteração desta Transação da Yapay? (Y/N)',
    mtConfirmation, [mbYes, mbNo], 0) <> idYes then Exit;

  with modulo_dados do
  begin
    // Atualiza status e CPF/CNPJ na entidade Vindi
      sql:='UPDATE uservindi_entidade SET status = :cbostatu, cpfcnpj = :ACpfCnpj ' +
      ' WHERE vindientidadeid = :AVindiEntidadeID ' ;
      fdquerysql3.close;
      fdquerysql3.sql.clear;
      fdquerysql3.sql.text := sql;
      fdquerysql3.parambyname('cbostatus').asstring:= cbostatus.text;
      fdquerysql3.parambyname('ACpfCnpj').asstring := lblcpfcnpj.text;
      fdquerysql3.parambyname('AVindiEntidadeID').asstring :=lblvindientidadeid.Text;
      if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
         begin
            // Atualiza data alterada na transação Yapay
            ValteradoConvertido := DataMascaraParaDatetime(mskdttransacao.Text);
            sql:='UPDATE user_yapaytransacoes SET alterado = CAST(ValteradoConvertido WHERE yapayid = :yapayid' ;
            fdquerysql3.close;
            fdquerysql3.sql.clear;
            fdquerysql3.sql.text := sql;
            fdquerysql3.parambyname('yapayid').asstring := lblyapayid.text;
            if executaracao(fdquerysql3,fdbanco,true,dtsfdquerysql3) then
               begin
               end;
         end;
    end;
    setcursorsql('');
    btnefetuafiltro.Click;
    ExibirPainelEdicao(False);
    gravalog(frmlogon.codigousuario, DateToStr(Date), 'ALTEROU A TRANSAÇÃO: ' + lblyapayid.Text);
    setcursorsql('');
end;

procedure Tfrmconciliavindi.btneditartransacaoClick(Sender: TObject);
begin
  if chkintegradasapolo.Checked then
  begin
    MessageDlg('NÃO É PERMITIDO EDITAR TRANSAÇÕES JÁ INTEGRADAS AO ALVO !!!', mtError, [mbOK], 0);
    griddocumentosaconciliar.SetFocus;
    Exit;
  end;

  with modulo_dados do
  begin
    lblyapayid.Text         := fdquerysql4.FieldByName('yapayid').AsString;
    lblvindientidadeid.Text := fdquerysql4.FieldByName('VindiEntidadeID').AsString;
    buscanacombo(fdquerysql4.FieldByName('status').AsString, frmconciliavindi, cbostatus);
    cbostatus.Refresh;
    lblcpfcnpj.Text         := fdquerysql4.FieldByName('cpfcnpj').AsString;
    mskdttransacao.Text     := fdquerysql4.FieldByName('alterado').AsString;
    lblpedidoid.Text        := fdquerysql4.FieldByName('pedidoid').AsString;
  end;

  ExibirPainelEdicao(True);
  lblyapayid.SetFocus;
end;

procedure Tfrmconciliavindi.btnvoltaClick(Sender: TObject);
begin
  LimparPainelPrevia;
  ExibirPainelPrevia(False);
end;

// =============================================================================
//  DrawColumnCell — coloração por regra de negócio
// =============================================================================

procedure Tfrmconciliavindi.griddocumentosaconciliarDrawColumnCell(
  Sender: TObject; const Rect: TRect; DataCol: Integer; Column: TColumn;
  State: TGridDrawState);
var
  Status   : string;
  BrushColor: TColor;
begin
  with modulo_dados do
  begin
    Status     := fdquerysql4.FieldByName('status').AsString;
    BrushColor := clWindow; // padrão sem destaque

    if (Status = 'inactive') or (FCpfCnpj = '') then
      BrushColor := clRed
    else if FValorOriginal < FUserValorContribuicao then
      BrushColor := clYellow
    else if FValorOriginal > FUserValorContribuicao then
      BrushColor := clGreen;

    if BrushColor <> clWindow then
    begin
      griddocumentosaconciliar.Canvas.Brush.Color := BrushColor;
      griddocumentosaconciliar.Canvas.Font.Color  := clWindowText;
      griddocumentosaconciliar.Canvas.FillRect(Rect);
      griddocumentosaconciliar.DefaultDrawColumnCell(Rect, DataCol, Column, State);
    end;
  end;
end;

// =============================================================================
//  Pesquisa por campo
// =============================================================================

procedure Tfrmconciliavindi.lblprocurarporKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);

begin

end;

// =============================================================================
//  Popup — grava configurações de grid
// =============================================================================

procedure Tfrmconciliavindi.popmnugravaconfigClick(Sender: TObject);
begin
  grava_configuracoes_grids(frmconciliavindi, 'GEOCONCILIAVINDIAPOLO',
    griddocumentosaconciliar, 'griddocumentosaconciliar',
    frmlogon.nomeusuario, modulo_dados.dtsfdquerysql5);
  // grava_config_telabusca('GEOCONCILIAVINDIAPOLO', cbocampo.Text, cbordem.Text, 'A', frmconciliavindi);
end;

// =============================================================================
//  Navegação por teclado (Tab/Enter entre campos)
// =============================================================================

procedure Tfrmconciliavindi.mskdtinicialKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then mskdtfinal.SetFocus;
end;

procedure Tfrmconciliavindi.mskdtfinalKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then btnefetuafiltro.Click;
end;

procedure Tfrmconciliavindi.lblyapayidKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then lblvindientidadeid.SetFocus;
end;

procedure Tfrmconciliavindi.lblvindientidadeidKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then cbostatus.SetFocus;
end;

procedure Tfrmconciliavindi.cbostatusKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then lblcpfcnpj.SetFocus;
end;

procedure Tfrmconciliavindi.lblcpfcnpjKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then mskdttransacao.SetFocus;
end;

procedure Tfrmconciliavindi.mskdttransacaoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then btnsalvaralteracoes.Click;
end;

procedure Tfrmconciliavindi.spbsairClick(Sender: TObject);
begin
  Close;
end;

end.
