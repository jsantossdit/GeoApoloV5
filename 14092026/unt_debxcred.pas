unit unt_debxcred;
interface
uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, ExtCtrls, StdCtrls, Mask, ComCtrls, Buttons, DBGrids, DB,
  FireDAC.Comp.Client, FireDAC.Stan.Param, ComObj,
  unt_consultas4, unt_debxcredctafin_service,
  uDebxCredController, uDebxCredDTO, uDebxCredMemTableHelper,
  System.Generics.Collections, Vcl.Grids, FireDAC.Stan.Intf,
  FireDAC.Stan.Option, FireDAC.Stan.Error, FireDAC.DatS, FireDAC.Phys.Intf,
  FireDAC.DApt.Intf, FireDAC.Comp.DataSet;
type
  Tfrmdebxcred = class(TForm)
    panelmenu: TPanel;
    spbexecutar: TSpeedButton;
    spbexportaexcel: TSpeedButton;
    spbretornar: TSpeedButton;
    spblimpar: TSpeedButton;
    StatusBar1: TStatusBar;
    GroupBox1: TGroupBox;
    lbldatainicial: TLabel;
    mskdtinicial: TMaskEdit;
    lbldatafinal: TLabel;
    mskdtfinal: TMaskEdit;
    lblcodredconta: TLabeledEdit;
    lblnomecontacontabil: TLabel;
    spbuscacontacontabil: TSpeedButton;
    GroupBox2: TGroupBox;
    dbgValores: TDBGrid;
    mtDebxCred: TFDMemTable;
    dsDebxCred: TDataSource;
    pnlTotais: TPanel;
    lblTotalDebito: TLabel;
    lblTotalCredito: TLabel;
    lblSaldo: TLabel;
    edtFiltroTexto: TEdit;
    cbCampoFiltro: TComboBox;
    chkSomenteDiverg: TCheckBox;
    btnLimparFiltro: TSpeedButton;
    lblContadorRegistros: TLabel;
    procedure FormCreate(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbretornarClick(Sender: TObject);
    procedure mskdtinicialKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure mskdtfinalKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblcodredcontaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure mskdtfinalEnter(Sender: TObject);
    procedure lblcodredcontaEnter(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure spbuscacontacontabilClick(Sender: TObject);
    procedure spbexecutarClick(Sender: TObject);
    procedure spbexportaexcelClick(Sender: TObject);
    procedure dbgValoresDrawColumnCell(Sender: TObject; const Rect: TRect;
      DataCol: Integer; Column: TColumn; State: TGridDrawState);
    procedure edtFiltroTextoChange(Sender: TObject);
    procedure chkSomenteDivergClick(Sender: TObject);
    procedure btnLimparFiltroClick(Sender: TObject);
  private
    // --- Inicialização ---
    procedure ConfigurarGrid;
    procedure ConfigurarCamposFiltro;
    // --- Validação ---
    function ValidarPeriodo: Boolean;
    function ValidarContaContabil: Boolean;
    // --- Busca e exibição ---
    procedure BuscarNomeConta(const ACodRed: string);
    procedure CarregarDados(const ALista: TObjectList<TDebxCredDTO>);
    // --- Filtros ---
    procedure AplicarFiltros;
    procedure LimparFiltros;
    // --- Rodapé ---
    procedure AtualizarRodape(const ADebito, ACredito: Currency; const ARegistros: Integer);
    procedure ZerarRodape;
    // --- Exportação ---
    procedure ExportarParaExcel;
    // --- UI helpers ---
    procedure IniciarProcessamento;
    procedure FinalizarProcessamento;
    procedure SetarStatus(const AMensagem: string);
  end;
var
  frmdebxcred: Tfrmdebxcred;

implementation
uses
  unt_dados, unt_principal, Math, StrUtils;

{$R *.dfm}

// =============================================================================
//  INICIALIZAÇÃO
// =============================================================================
procedure Tfrmdebxcred.FormCreate(Sender: TObject);
begin
  ConfigurarGrid;
  ConfigurarCamposFiltro;
  ZerarRodape;
  SetarStatus('Pronto.');
end;

procedure Tfrmdebxcred.ConfigurarGrid;
begin
  dsDebxCred.DataSet    := mtDebxCred;
  dbgValores.DataSource := dsDebxCred;
  TDebxCredMemTableHelper.Configurar(mtDebxCred);
  dbgValores.DefaultDrawing := False;
end;

procedure Tfrmdebxcred.ConfigurarCamposFiltro;
begin
  cbCampoFiltro.Items.Clear;
  cbCampoFiltro.Items.AddStrings(['DATA', 'DEBITO', 'CREDITO', 'DIFERENCA']);
  cbCampoFiltro.ItemIndex := 0;
  chkSomenteDiverg.Caption := 'Somente divergências';
  btnLimparFiltro.Hint     := 'Limpar filtros aplicados';
  btnLimparFiltro.ShowHint := True;
end;

// =============================================================================
//  VALIDAÇÃO
// =============================================================================
function Tfrmdebxcred.ValidarPeriodo: Boolean;
var
  DtInicial, DtFinal: TDate;
begin
  Result := False;
  if Trim(mskdtinicial.Text) = '' then
  begin
    MessageDlg('Informe a data inicial.', mtWarning, [mbOK], 0);
    mskdtinicial.SetFocus;
    Exit;
  end;
  if Trim(mskdtfinal.Text) = '' then
  begin
    MessageDlg('Informe a data final.', mtWarning, [mbOK], 0);
    mskdtfinal.SetFocus;
    Exit;
  end;
  try
    DtInicial := StrToDate(mskdtinicial.Text);
    DtFinal   := StrToDate(mskdtfinal.Text);
  except
    MessageDlg('Data inválida. Verifique o formato dd/mm/aaaa.', mtWarning, [mbOK], 0);
    Exit;
  end;
  if DtInicial > DtFinal then
  begin
    MessageDlg('A data inicial não pode ser maior que a data final.', mtWarning, [mbOK], 0);
    mskdtinicial.SetFocus;
    Exit;
  end;
  Result := True;
end;

function Tfrmdebxcred.ValidarContaContabil: Boolean;
begin
  Result := True;
end;

// =============================================================================
//  BUSCA E EXIBIÇÃO
// =============================================================================
procedure Tfrmdebxcred.BuscarNomeConta(const ACodRed: string);
const
  SQL_NOME_CONTA =
    'SELECT PlanoCtaNome ' +
    'FROM plano_cta WITH(NOLOCK) ' +
    'WHERE PlanoCtaCodRed = :COD';
begin
  if Trim(ACodRed) = '' then
  begin
    lblnomecontacontabil.Caption := '';
    Exit;
  end;
  with modulo_dados.fdquerysql do
  begin
    Close;
    SQL.Text := SQL_NOME_CONTA;
    ParamByName('COD').AsString := ACodRed;
    Open;
    if not IsEmpty then
      lblnomecontacontabil.Caption := FieldByName('PlanoCtaNome').AsString
    else
    begin
      lblnomecontacontabil.Caption := '';
      MessageDlg('Conta contábil não encontrada.', mtError, [mbOK], 0);
      lblcodredconta.Clear;
      lblcodredconta.SetFocus;
    end;
    Close;
  end;
end;

procedure Tfrmdebxcred.CarregarDados(const ALista: TObjectList<TDebxCredDTO>);
var
  Item: TDebxCredDTO;
  TotalDebito, TotalCredito: Currency;
begin
  mtDebxCred.DisableControls;
  try
    mtDebxCred.EmptyDataSet;
    TotalDebito  := 0;
    TotalCredito := 0;
    for Item in ALista do
    begin
      mtDebxCred.AppendRecord([
        Item.Data,
        Item.Debito,
        Item.Credito,
        Item.Diferenca
      ]);
      TotalDebito  := TotalDebito  + Item.Debito;
      TotalCredito := TotalCredito + Item.Credito;
    end;
    if ALista.Count > 0 then
      mtDebxCred.First;
    AtualizarRodape(TotalDebito, TotalCredito, ALista.Count);
    SetarStatus(Format('%d registro(s) encontrado(s).', [ALista.Count]));
  finally
    mtDebxCred.EnableControls;
  end;
end;

// =============================================================================
//  FILTROS
// =============================================================================
procedure Tfrmdebxcred.AplicarFiltros;
var
  Filtro, Campo, TextoFiltro, Operador, ValorNumerico: string;
  TesteValor: Double;
begin
  try
    Filtro       := '';
    Campo        := cbCampoFiltro.Text;
    TextoFiltro  := Trim(edtFiltroTexto.Text);
    if TextoFiltro <> '' then
    begin
      if Campo = 'DATA' then
        Filtro := Format('%s LIKE ''%%%s%%''', [Campo, TextoFiltro])
      else
      begin
        Operador      := '=';
        ValorNumerico := TextoFiltro;
        if Length(TextoFiltro) >= 2 then
        begin
          if CharInSet(TextoFiltro[1], ['>', '<', '=']) and
             CharInSet(TextoFiltro[2], ['>', '<', '=']) then
          begin
            Operador      := Copy(TextoFiltro, 1, 2);
            ValorNumerico := Trim(Copy(TextoFiltro, 3, MaxInt));
          end
          else if CharInSet(TextoFiltro[1], ['>', '<', '=']) then
          begin
            Operador      := Copy(TextoFiltro, 1, 1);
            ValorNumerico := Trim(Copy(TextoFiltro, 2, MaxInt));
          end;
        end;
        if not TryStrToFloat(
          StringReplace(ValorNumerico, '.', ',', [rfReplaceAll]),
          TesteValor) then
        begin
          SetarStatus('Valor de filtro inválido para campo numérico.');
          Exit;
        end;
        ValorNumerico := StringReplace(ValorNumerico, ',', '.', [rfReplaceAll]);
        Filtro := Format('%s %s %s', [Campo, Operador, ValorNumerico]);
      end;
    end;
    if chkSomenteDiverg.Checked then
    begin
      if Filtro <> '' then
        Filtro := Filtro + ' AND ';
      Filtro := Filtro + '(DIFERENCA <> 0)';
    end;
    mtDebxCred.Filtered := False;
    mtDebxCred.Filter   := Filtro;
    mtDebxCred.Filtered := Filtro <> '';
    if mtDebxCred.Filtered then
      SetarStatus(Format('Filtro aplicado — %d registro(s) visível(is).', [mtDebxCred.RecordCount]))
    else
      SetarStatus('Filtro removido.');
  except
    on E: Exception do
      MessageDlg('Erro ao aplicar filtro: ' + E.Message, mtError, [mbOK], 0);
  end;
end;

procedure Tfrmdebxcred.LimparFiltros;
begin
  edtFiltroTexto.Clear;
  chkSomenteDiverg.Checked := False;
  mtDebxCred.Filtered := False;
  mtDebxCred.Filter   := '';
  SetarStatus('Filtros removidos.');
end;

// =============================================================================
//  RODAPÉ
// =============================================================================
procedure Tfrmdebxcred.AtualizarRodape(const ADebito, ACredito: Currency;
  const ARegistros: Integer);
var
  Saldo: Currency;
begin
  Saldo := ADebito - ACredito;
  lblTotalDebito.Caption       := Format('TOTAL DÉBITO: R$ %.2f',  [ADebito]);
  lblTotalCredito.Caption      := Format('TOTAL CRÉDITO: R$ %.2f', [ACredito]);
  lblSaldo.Caption             := Format('SALDO: R$ %.2f',         [Saldo]);
  lblContadorRegistros.Caption := Format('Registros: %d',          [ARegistros]);
  if Saldo < 0 then
    lblSaldo.Font.Color := clRed
  else if Saldo > 0 then
    lblSaldo.Font.Color := clGreen
  else
    lblSaldo.Font.Color := clWindowText;
end;

procedure Tfrmdebxcred.ZerarRodape;
begin
  AtualizarRodape(0, 0, 0);
end;

// =============================================================================
//  EXPORTAÇÃO
// =============================================================================
procedure Tfrmdebxcred.ExportarParaExcel;
var
  Excel, Workbook, Sheet: OleVariant;
  Row, Col, I: Integer;
begin
  if mtDebxCred.IsEmpty then
  begin
    MessageDlg('Não há dados para exportar.', mtInformation, [mbOK], 0);
    Exit;
  end;
  IniciarProcessamento;
  try
    Excel    := CreateOleObject('Excel.Application');
    Workbook := Excel.Workbooks.Add;
    Sheet    := Workbook.ActiveSheet;
    Col := 1;
    for I := 0 to mtDebxCred.Fields.Count - 1 do
    begin
      Sheet.Cells[1, Col]           := mtDebxCred.Fields[I].DisplayLabel;
      Sheet.Cells[1, Col].Font.Bold := True;
      Inc(Col);
    end;
    mtDebxCred.DisableControls;
    mtDebxCred.First;
    Row := 2;
    try
      while not mtDebxCred.Eof do
      begin
        Col := 1;
        for I := 0 to mtDebxCred.Fields.Count - 1 do
        begin
          Sheet.Cells[Row, Col] := mtDebxCred.Fields[I].Value;
          Inc(Col);
        end;
        mtDebxCred.Next;
        Inc(Row);
      end;
    finally
      mtDebxCred.EnableControls;
    end;
    Sheet.Columns.AutoFit;
    Excel.Visible := True;
    SetarStatus('Exportação para Excel concluída.');
  except
    on E: Exception do
      MessageDlg('Erro ao exportar para Excel: ' + E.Message, mtError, [mbOK], 0);
  end;
  FinalizarProcessamento;
end;

// =============================================================================
//  UI HELPERS
// =============================================================================
procedure Tfrmdebxcred.IniciarProcessamento;
begin
  Screen.Cursor     := crHourGlass;
  panelmenu.Enabled := False;
  SetarStatus('Processando...');
  Application.ProcessMessages;
end;

procedure Tfrmdebxcred.FinalizarProcessamento;
begin
  Screen.Cursor     := crDefault;
  panelmenu.Enabled := True;
end;

procedure Tfrmdebxcred.SetarStatus(const AMensagem: string);
begin
  StatusBar1.SimpleText := AMensagem;
  Application.ProcessMessages;
end;

// =============================================================================
//  EVENTOS DE FORMULÁRIO
// =============================================================================
procedure Tfrmdebxcred.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Action := caFree;
end;

procedure Tfrmdebxcred.FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F10 then
    Close;
end;

// =============================================================================
//  EVENTOS DOS BOTÕES
// =============================================================================
procedure Tfrmdebxcred.spbretornarClick(Sender: TObject);
begin
  Close;
end;

procedure Tfrmdebxcred.spblimparClick(Sender: TObject);
begin
  mtDebxCred.EmptyDataSet;
  lblnomecontacontabil.Caption := '';
  lblcodredconta.Clear;
  mskdtinicial.Clear;
  mskdtfinal.Clear;
  LimparFiltros;
  ZerarRodape;
  mskdtinicial.SetFocus;
  SetarStatus('Campos limpos.');
end;

procedure Tfrmdebxcred.spbexecutarClick(Sender: TObject);
var
  Controller : TDebxCredController;
  Lista      : TObjectList<TDebxCredDTO>;
begin
  if not ValidarPeriodo then
    Exit;
  IniciarProcessamento;
  try
    Controller := TDebxCredController.Create(modulo_dados.fdbanco);
    try
      Lista := Controller.Consultar(
        StrToDate(mskdtinicial.Text),
        StrToDate(mskdtfinal.Text),
        Trim(lblcodredconta.Text)
      );
      try
        CarregarDados(Lista);
        AplicarFiltros;
      finally
        Lista.Free;
      end;
    finally
      Controller.Free;
    end;
  except
    on E: Exception do
    begin
      MessageDlg('Erro ao executar consulta: ' + E.Message, mtError, [mbOK], 0);
      SetarStatus('Erro na consulta.');
    end;
  end;
  FinalizarProcessamento;
end;

procedure Tfrmdebxcred.spbexportaexcelClick(Sender: TObject);
begin
  ExportarParaExcel;
end;

procedure Tfrmdebxcred.spbuscacontacontabilClick(Sender: TObject);
const
  SQL_LISTA_CONTAS =
    'SELECT PlanoCtaCodRed, PlanoCtaNome ' +
    'FROM plano_cta WITH(NOLOCK) ' +
    'WHERE PlanoCtaTipo = ''A'' ' +
    'ORDER BY PlanoCtaCodEstr';
var
  fConsulta : TFrmConsulta4;
  LLista    : TListaContasFinanceiras;
  LMemTable : TFDMemTable;
  I         : Integer;
begin
  // Se código já preenchido manualmente, apenas resolve o nome
  if Trim(lblcodredconta.Text) <> '' then
  begin
    BuscarNomeConta(lblcodredconta.Text);
    Exit;
  end;
  if not ((frmprincipal.integraentidadesapolo = 'Integra') or
          (frmprincipal.integraentidadesapolo = 'Mescla')) then
  begin
    MessageDlg('Integração com plano de contas não habilitada.', mtWarning, [mbOK], 0);
    Exit;
  end;
  // ---------------------------------------------------------------
  // PASSO 1 — carrega contas analíticas do banco no array
  // ---------------------------------------------------------------
  SetLength(LLista, 0);
  with modulo_dados.fdquerysql do
  begin
    Close;
    SQL.Clear;
    SQL.Text := SQL_LISTA_CONTAS;
    Open;
    if IsEmpty then
    begin
      MessageDlg('Tabela do plano de contas está vazia.', mtWarning, [mbOK], 0);
      Close;
      Exit;
    end;
    First;
    while not Eof do
    begin
      SetLength(LLista, Length(LLista) + 1);
      I := High(LLista);
      LLista[I].Codigo := FieldByName('PlanoCtaCodRed').AsString;
      LLista[I].Nome   := FieldByName('PlanoCtaNome').AsString;
      Next;
    end;
    Close;
  end;
  // ---------------------------------------------------------------
  // PASSO 2 — converte TListaContasFinanceiras para TFDMemTable
  //           pois PopularGrid(ASource: TDataSet; ...) exige TDataSet.
  //           CORREÇÃO: passar o array diretamente causaria E2010
  //           "Incompatible types: TDataSet and TArray<...>".
  // ---------------------------------------------------------------
  LMemTable := TFDMemTable.Create(nil);
  try
    LMemTable.FieldDefs.Add('PlanoCtaCodRed', ftString, 20);
    LMemTable.FieldDefs.Add('PlanoCtaNome',   ftString, 100);
    LMemTable.CreateDataSet;
    LMemTable.DisableControls;
    try
      for I := 0 to High(LLista) do
      begin
        LMemTable.Append;
        LMemTable.FieldByName('PlanoCtaCodRed').AsString := LLista[I].Codigo;
        LMemTable.FieldByName('PlanoCtaNome').AsString   := LLista[I].Nome;
        LMemTable.Post;
      end;
    finally
      LMemTable.EnableControls;
    end;
    LMemTable.First;
    // ---------------------------------------------------------------
    // PASSO 3 — exibe o form de consulta modal
    // ---------------------------------------------------------------
    fConsulta := TFrmConsulta4.Create(nil);
    try
      fConsulta.Titulo := 'Plano de Contas Contábil';
      fConsulta.PopularGrid(LMemTable, 'PlanoCtaCodRed', 'PlanoCtaNome');
      if fConsulta.ShowModal = mrOK then
      begin
        lblcodredconta.Text          := fConsulta.CodigoSelecionado;
        lblnomecontacontabil.Caption := fConsulta.DescricaoSelecionada;
        SetarStatus('Conta selecionada: ' + fConsulta.DescricaoSelecionada);
      end;
    finally
      FreeAndNil(fConsulta);
    end;
  finally
    FreeAndNil(LMemTable);
  end;
end;

// =============================================================================
//  EVENTOS DOS CAMPOS
// =============================================================================
procedure Tfrmdebxcred.mskdtinicialKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_RETURN then
    mskdtfinal.SetFocus;
end;

procedure Tfrmdebxcred.mskdtfinalKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_RETURN then
    lblcodredconta.SetFocus;
end;

procedure Tfrmdebxcred.lblcodredcontaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_RETURN then
  begin
    if Trim(lblcodredconta.Text) <> '' then
      BuscarNomeConta(lblcodredconta.Text)
    else
      spbexecutar.Click;
  end;
  if Key = VK_F4 then
    spbuscacontacontabil.Click;
end;

procedure Tfrmdebxcred.mskdtfinalEnter(Sender: TObject);
begin
  if Trim(mskdtinicial.Text) = '' then
    mskdtinicial.SetFocus;
end;

procedure Tfrmdebxcred.lblcodredcontaEnter(Sender: TObject);
begin
  if (Trim(mskdtinicial.Text) = '') or (Trim(mskdtfinal.Text) = '') then
  begin
    SetarStatus('Atenção: informe o período antes de selecionar a conta.');
    mskdtinicial.SetFocus;
  end;
end;

// =============================================================================
//  EVENTOS DOS FILTROS
// =============================================================================
procedure Tfrmdebxcred.edtFiltroTextoChange(Sender: TObject);
begin
  AplicarFiltros;
end;

procedure Tfrmdebxcred.chkSomenteDivergClick(Sender: TObject);
begin
  AplicarFiltros;
end;

procedure Tfrmdebxcred.btnLimparFiltroClick(Sender: TObject);
begin
  LimparFiltros;
end;

// =============================================================================
//  DESENHO DO GRID
// =============================================================================
procedure Tfrmdebxcred.dbgValoresDrawColumnCell(Sender: TObject;
  const Rect: TRect; DataCol: Integer; Column: TColumn; State: TGridDrawState);
var
  Divergencia: Currency;
  CorFundo: TColor;
begin
  if gdSelected in State then
  begin
    dbgValores.Canvas.Brush.Color := clHighlight;
    dbgValores.Canvas.Font.Color  := clHighlightText;
  end
  else
  begin
    Divergencia := mtDebxCred.FieldByName('DIFERENCA').AsCurrency;
    if Divergencia <> 0 then
      CorFundo := $00DDDDFF
    else if (mtDebxCred.RecNo mod 2) = 0 then
      CorFundo := $00F5F5F5
    else
      CorFundo := clWhite;
    dbgValores.Canvas.Brush.Color := CorFundo;
    dbgValores.Canvas.Font.Color  := clBlack;
  end;
  dbgValores.Canvas.FillRect(Rect);
  dbgValores.DefaultDrawColumnCell(Rect, DataCol, Column, State);
end;

end.
