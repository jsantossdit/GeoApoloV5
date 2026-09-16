unit unt_debxcredctafin;
interface
uses
  Winapi.Windows, Winapi.Messages,
  System.SysUtils, System.Variants, System.Classes,
  Vcl.Graphics, Vcl.Controls, Vcl.Forms, Vcl.Dialogs,
  Vcl.ComCtrls, Vcl.ExtCtrls, Vcl.Grids, Vcl.StdCtrls, Vcl.Mask, Vcl.Buttons,
  FireDAC.Comp.Client,
  unt_debxcredctafin_service;
type
  Tfrmdebxcredfin = class(TForm)
    GroupBox1: TGroupBox;
    lbldatainicial: TLabel;
    lbldatafinal: TLabel;
    lblnomecontafinanceira: TLabel;
    spbuscacontafinanceira: TSpeedButton;
    mskdtinicial: TMaskEdit;
    mskdtfinal: TMaskEdit;
    lblcontafincod: TLabeledEdit;
    GroupBox2: TGroupBox;
    gridvalores: TStringGrid;
    panelmenu: TPanel;
    spbexecutar: TSpeedButton;
    spbimprimerecibo: TSpeedButton;
    spbsair: TSpeedButton;
    spblimpar: TSpeedButton;
    lblsair: TLabel;
    spbajuste: TSpeedButton;
    StatusBar1: TStatusBar;
    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbsairClick(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure spbuscacontafinanceiraClick(Sender: TObject);
    procedure spbexecutarClick(Sender: TObject);
    procedure mskdtinicialKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure mskdtfinalKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblcontafincodKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
  private
    FService: IDebXCredService;
    procedure InicializarGrid;
    procedure LimparGrid;
    procedure PreencherGrid(const AResultado: TResultadoMovimento);
    function ValidarCampos: Boolean;
    function ObterDataInicial: TDate;
    function ObterDataFinal: TDate;
    procedure AtualizarNomeContaFinanceira;
    // Método centralizado e seguro para obter o nome do usuário logado.
    // Nunca acesse frmlogon diretamente fora deste método.
    function ObterNomeUsuarioLogado: string;
  public
  end;
var
  frmdebxcredfin: Tfrmdebxcredfin;
implementation
uses
  unt_dados, funcoes, unt_logon, unt_Consultas4, Data.DB;
{$R *.dfm}
{ ============================================================
  MÉTODO SEGURO PARA ACESSAR frmlogon.nomeusuario
  ============================================================
  Raiz do AV original: frmlogon é uma variável global que pode
  ser nil (form ainda não criado) ou apontar para memória
  inválida (form destruído após caHide não recriar a instância).
  Centralizar o acesso aqui permite tratar todos os casos em
  um único lugar.
  ============================================================ }
function Tfrmdebxcredfin.ObterNomeUsuarioLogado: string;
begin
  Result := '';
  // Guard 1: variável global pode ser nil se o form de logon
  // nunca foi criado ou foi destruído (não é o caso com caHide,
  // mas protege contra refactorings futuros).
  if not Assigned(frmlogon) then
  begin
    MessageDlg('Sessão de usuário não encontrada. Faça login novamente.',
      mtError, [mbOK], 0);
    Exit;
  end;
  // Guard 2: nomeusuario em branco indica que o logon não foi
  // concluído com sucesso (ex.: form aberto mas botão Entrar
  // ainda não foi pressionado).
  Result := Trim(frmlogon.nomeusuario);
  if Result = '' then
  begin
    MessageDlg('Nenhum usuário autenticado. Faça login antes de continuar.',
      mtWarning, [mbOK], 0);
    Result := '';
  end;
end;
{ ============================================================
  CICLO DE VIDA DO FORM
  ============================================================ }
procedure Tfrmdebxcredfin.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Action := caHide;
end;

procedure Tfrmdebxcredfin.FormCreate(Sender: TObject);
begin
  FService := nil;
end;

procedure Tfrmdebxcredfin.FormDestroy(Sender: TObject);
begin
  FService := nil;
end;

procedure Tfrmdebxcredfin.FormActivate(Sender: TObject);
begin
  if not Assigned(FService) then
    FService := TDebXCredService.Create(modulo_dados.fdbanco);
  StatusBar1.Panels[0].Text := 'Banco de Dados';
  StatusBar1.Panels[1].Text := configura_statusbar('a');
  StatusBar1.Refresh;
  InicializarGrid;
end;

procedure Tfrmdebxcredfin.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
  if Key = VK_F10 then
    spbsair.Click;
end;

{ ============================================================
  NAVEGAÇÃO POR TECLADO
  ============================================================ }
procedure Tfrmdebxcredfin.mskdtinicialKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
  if Key = VK_RETURN then
    mskdtfinal.SetFocus;
end;

procedure Tfrmdebxcredfin.mskdtfinalKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
  if Key = VK_RETURN then
    lblcontafincod.SetFocus;
end;

procedure Tfrmdebxcredfin.lblcontafincodKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
  case Key of
    VK_RETURN : spbexecutar.Click;
    VK_F4     : spbuscacontafinanceira.Click;
  end;
end;

{ ============================================================
  AÇÕES DOS BOTÕES
  ============================================================ }
procedure Tfrmdebxcredfin.spbsairClick(Sender: TObject);
begin
  Close;
end;

procedure Tfrmdebxcredfin.spblimparClick(Sender: TObject);
begin
  LimparGrid;
  mskdtinicial.Clear;
  mskdtfinal.Clear;
  lblcontafincod.Text := '';
  lblnomecontafinanceira.Caption := '...';
  mskdtinicial.SetFocus;
end;

procedure Tfrmdebxcredfin.spbuscacontafinanceiraClick(Sender: TObject);
var
  LForm     : TFrmConsulta4;
  LCodigo   : string;
  LNome     : string;
  LGrupo    : string;
  LLista    : TListaContasFinanceiras;
  LQry      : TFDQuery;
  LMemTable : TFDMemTable;
  i         : Integer;
begin
  // ----------------------------------------------------------------
  // PASSO 1 — obtém o usuário logado de forma segura
  // ----------------------------------------------------------------
  LGrupo := '';
  try
    LGrupo := FService.BuscarGrupoUsuario(ObterNomeUsuarioLogado);
  except
    on E: Exception do
    begin
      MessageDlg('Erro ao buscar grupo do usuário: ' + E.Message,
        mtError, [mbOK], 0);
      Exit;
    end;
  end;
  if LGrupo = '' then
  begin
    MessageDlg('Usuário não possui grupo cadastrado.', mtWarning, [mbOK], 0);
    Exit;
  end;
  // ----------------------------------------------------------------
  // PASSO 2 — executa o SELECT e monta o array LLista
  // ----------------------------------------------------------------
  SetLength(LLista, 0);
  LQry := TFDQuery.Create(nil);
  try
    LQry.Connection := modulo_dados.fdbanco;
    LQry.SQL.Text   :=
      'SELECT ContaFinCod, ContaFinNome ' +
      'FROM   CONTA_FIN '                 +
      'ORDER BY ContaFinNome';
    LQry.Open;
    SetLength(LLista, LQry.RecordCount);
    i := 0;
    while not LQry.EOF do
    begin
      LLista[i].Codigo := LQry.FieldByName('ContaFinCod').AsString;
      LLista[i].Nome   := LQry.FieldByName('ContaFinNome').AsString;
      Inc(i);
      LQry.Next;
    end;
  finally
    FreeAndNil(LQry);
  end;
  if Length(LLista) = 0 then
  begin
    MessageDlg('Nenhuma conta financeira disponível.',
      mtInformation, [mbOK], 0);
    Exit;
  end;
  // ----------------------------------------------------------------
  // PASSO 3 — converte TArray<TContaFinanceiraItem> para TFDMemTable
  //           pois PopularGrid(ASource: TDataSet) exige um TDataSet.
  //           CORREÇÃO E2010 (linha 229): passar LLista diretamente
  //           causava "Incompatible types: TDataSet and TArray<...>".
  // ----------------------------------------------------------------
  LMemTable := TFDMemTable.Create(nil);
  try
    LMemTable.FieldDefs.Add('ContaFinCod',  ftString, 20);
    LMemTable.FieldDefs.Add('ContaFinNome', ftString, 100);
    LMemTable.CreateDataSet;
    for i := 0 to High(LLista) do
    begin
      LMemTable.Append;
      LMemTable.FieldByName('ContaFinCod').AsString  := LLista[i].Codigo;
      LMemTable.FieldByName('ContaFinNome').AsString := LLista[i].Nome;
      LMemTable.Post;
    end;

    LMemTable.First;
    // ----------------------------------------------------------------
    // PASSO 4 — exibe o form de consulta modal
    // ----------------------------------------------------------------
    LCodigo := '';
    LNome   := '';
    LForm := TFrmConsulta4.Create(nil);
    try
      LForm.PopularGrid(LMemTable, 'ContaFinCod', 'ContaFinNome');
      if LForm.ShowModal = mrOK then
      begin
        LCodigo := LForm.CodigoSelecionado;
        LNome   := LForm.DescricaoSelecionada;
      end;
    finally
      FreeAndNil(LForm);
    end;
  finally
    FreeAndNil(LMemTable);  // liberado APÓS o form fechar, pois PopularGrid copia os dados internamente
  end;

  // ----------------------------------------------------------------
  // PASSO 5 — aplica o resultado na tela
  // ----------------------------------------------------------------
  if LCodigo <> '' then
  begin
    lblcontafincod.Text            := LCodigo;
    lblnomecontafinanceira.Caption := LNome;
  end;
end;
procedure Tfrmdebxcredfin.spbexecutarClick(Sender: TObject);
var
  LResultado : TResultadoMovimento;
begin
  AtualizarNomeContaFinanceira;
  if not ValidarCampos then
    Exit;
  if MessageDlg('Confirma os dados acima para consulta?', mtConfirmation, [mbYes, mbNo], 0) <> idYes then
    Exit;
  // ----------------------------------------------------------------
  // CORREÇÃO E2010 (linha 257): 'mouse' sem qualificação conflita com
  // a propriedade global Mouse: TMouse do VCL (Vcl.Controls), fazendo
  // o compilador tentar usar TMouse onde se espera string — gerando o
  // erro de tipo incompatível. Qualificar com 'funcoes.' resolve.
  // ----------------------------------------------------------------
  funcoes.setcursorsql('sql');
  try
    try
      LResultado := FService.ConsultarMovimentos(
        lblcontafincod.Text,
        ObterDataInicial,
        ObterDataFinal
      );
      PreencherGrid(LResultado);
      mskdtinicial.SetFocus;
    except
      on E: Exception do
        MessageDlg('Erro ao consultar movimentos: ' + E.Message,
          mtError, [mbOK], 0);
    end;
  finally
    funcoes.setcursorsql('');
  end;
end;
{ ============================================================
  MÉTODOS PRIVADOS
  ============================================================ }
procedure Tfrmdebxcredfin.InicializarGrid;
begin
  gridvalores.Cells[0, 0] := 'Data';
  gridvalores.Cells[1, 0] := 'Débito';
  gridvalores.Cells[2, 0] := 'Crédito';
  gridvalores.Cells[3, 0] := 'Diferença';
  gridvalores.Refresh;
end;
procedure Tfrmdebxcredfin.LimparGrid;
var
  i: Integer;
begin
  for i := 0 to gridvalores.ColCount - 1 do
    gridvalores.Cols[i].Clear;
  gridvalores.RowCount := 2;
  InicializarGrid;
end;
procedure Tfrmdebxcredfin.PreencherGrid(const AResultado: TResultadoMovimento);
var
  i    : Integer;
  LLin : Integer;
begin
  LimparGrid;
  gridvalores.RowCount := Length(AResultado.Registros) + 5;
  for i := 0 to High(AResultado.Registros) do
  begin
    LLin := i + 1;
    gridvalores.Cells[0, LLin] := DateToStr(AResultado.Registros[i].Data);
    gridvalores.Cells[1, LLin] := FormatFloat('R$ ###,###,##0.00', AResultado.Registros[i].Debito);
    gridvalores.Cells[2, LLin] := FormatFloat('R$ ###,###,##0.00', AResultado.Registros[i].Credito);
    gridvalores.Cells[3, LLin] := FormatFloat('R$ ###,###,##0.00', AResultado.Registros[i].Diferenca);
  end;
  LLin := Length(AResultado.Registros) + 2;
  gridvalores.Cells[0, LLin]     := 'Total Débito';
  gridvalores.Cells[1, LLin]     := FormatFloat('R$ ###,###,##0.00', AResultado.TotalDebito);
  gridvalores.Cells[0, LLin + 1] := 'Total Crédito';
  gridvalores.Cells[1, LLin + 1] := FormatFloat('R$ ###,###,##0.00', AResultado.TotalCredito);
  gridvalores.Cells[0, LLin + 2] := 'Saldo';
  gridvalores.Cells[1, LLin + 2] := FormatFloat('R$ ###,###,##0.00', AResultado.Saldo);
  gridvalores.Refresh;
end;
function Tfrmdebxcredfin.ValidarCampos: Boolean;
begin
  Result := False;
  if mskdtinicial.Text = '  /  /    ' then
  begin
    MessageDlg('É obrigatório informar a data inicial para consulta.',
      mtWarning, [mbOK], 0);
    mskdtinicial.SetFocus;
    Exit;
  end;
  if mskdtfinal.Text = '  /  /    ' then
  begin
    MessageDlg('É obrigatório informar a data final para consulta.',
      mtWarning, [mbOK], 0);
    mskdtfinal.SetFocus;
    Exit;
  end;
  if lblcontafincod.Text = '' then
  begin
    MessageDlg('Não é possível consultar sem informar uma conta financeira.',
      mtError, [mbOK], 0);
    lblcontafincod.SetFocus;
    Exit;
  end;
  if ObterDataInicial > ObterDataFinal then
  begin
    MessageDlg('A data inicial não pode ser maior que a data final.',
      mtWarning, [mbOK], 0);
    mskdtinicial.SetFocus;
    Exit;
  end;
  Result := True;
end;
function Tfrmdebxcredfin.ObterDataInicial: TDate;
begin
  Result := StrToDate(mskdtinicial.Text);
end;
function Tfrmdebxcredfin.ObterDataFinal: TDate;
begin
  Result := StrToDate(mskdtfinal.Text);
end;
procedure Tfrmdebxcredfin.AtualizarNomeContaFinanceira;
var
  LNome: string;
begin
  if (lblcontafincod.Text <> '') and (lblnomecontafinanceira.Caption = '...') then
  begin
    LNome := FService.BuscarNomeContaFinanceira(lblcontafincod.Text);
    if LNome <> '' then
    begin
      lblnomecontafinanceira.Caption := LNome;
      lblnomecontafinanceira.Refresh;
    end;
  end;
end;
end.
