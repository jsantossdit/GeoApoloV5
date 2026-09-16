unit unt_importainscritos_eventos;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.StdCtrls, Vcl.ExtCtrls,
  Vcl.ComCtrls, Vcl.Buttons, Vcl.Samples.Gauges, FireDAC.Comp.Client, Data.DB,
  unt_importeventos_model, unt_importeventos_repository, unt_importeventos_servico,
  unt_importeventos_leitorplanilha, unt_importeventos_controller, Vcl.Grids,
  Vcl.Mask;

type
  Tfrmimportacadastroeventos = class(TForm)
    Panel1: TPanel;
    spbimportar: TSpeedButton;
    spblimpar: TSpeedButton;
    spblocalizar: TSpeedButton;
    spbexcluir: TSpeedButton;
    spbretornar: TSpeedButton;
    lblmsg1: TLabel;
    StatusBar1: TStatusBar;
    opendir: TOpenDialog;
    GroupBox1: TGroupBox;
    lblarquivoorigem: TLabeledEdit;
    spbarquivoorigem: TSpeedButton;
    lblidevento: TLabeledEdit;
    spbconsulta: TSpeedButton;
    lbldescricaoevento: TLabel;
    GroupBox2: TGroupBox;
    lbltotalderegistros: TLabel;
    lblntotalregistros: TLabel;
    Label1: TLabel;
    lblnregcpf: TLabel;
    Label3: TLabel;
    Label4: TLabel;
    lblregsnoapolo: TLabel;
    lblnregsnoapolo: TLabel;
    Gauge1: TGauge;
    spblayoutreduzido: TSpeedButton;
    gridimporta: TStringGrid;
    procedure spbretornarClick(Sender: TObject);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbarquivoorigemClick(Sender: TObject);
    procedure spbimportarClick(Sender: TObject);
    procedure lblideventoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbconsultaClick(Sender: TObject);
    procedure lblarquivoorigemEnter(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure lblarquivoorigemKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spblayoutreduzidoClick(Sender: TObject);
    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
  private
    FController: TControllerImportacaoEventos;
    procedure AtualizarProgresso(AAtual, ATotal: Integer);
    procedure MostrarResultado(const AResultado: TResultadoImportacao);
    function ConfirmarReimportacaoSeNecessario(const AIdEvento: string): Boolean;
    procedure ExecutarImportacao(ALayoutCompleto: Boolean);
  public
    { Public declarations }
  end;

var
  frmimportacadastroeventos: Tfrmimportacadastroeventos;

implementation

{$R *.dfm}

uses unt_dados, funcoes, unt_principal, unt_consultav3, unt_Consultas4;

procedure Tfrmimportacadastroeventos.FormCreate(Sender: TObject);
var
  vRepositorio: IRepositorioCongressoRcc;
  vServicoVinculo: IServicoVinculoApolo;
  vLeitor: IImportadorPlanilha;
begin
  // Ajustar "modulo_dados.FDConexao" para o nome real do TFDConnection do projeto.
  vRepositorio := TRepositorioCongressoRccFireDAC.Create(modulo_dados.fdbanco);
  vServicoVinculo := TServicoVinculoApolo.Create(vRepositorio);
  vLeitor := TImportadorPlanilhaExcelOLE.Create;

  FController := TControllerImportacaoEventos.Create(vRepositorio, vServicoVinculo, vLeitor);
  FController.OnProgresso := AtualizarProgresso;
end;

procedure Tfrmimportacadastroeventos.FormDestroy(Sender: TObject);
begin
  FController.Free;
end;

procedure Tfrmimportacadastroeventos.AtualizarProgresso(AAtual, ATotal: Integer);
begin
  Gauge1.MaxValue := ATotal;
  Gauge1.Progress := AAtual;
  Gauge1.Refresh;
  Application.ProcessMessages;
end;

procedure Tfrmimportacadastroeventos.MostrarResultado(const AResultado: TResultadoImportacao);
begin
  lblntotalregistros.Caption := AResultado.TotalLinhas.ToString;
  lblnregcpf.Caption := AResultado.TotalComDocumento.ToString;
  lblnregsnoapolo.Caption := AResultado.TotalVinculadosApolo.ToString;
  lblntotalregistros.Refresh;
  lblnregcpf.Refresh;
  lblnregsnoapolo.Refresh;
  MessageDlg('IMPORTAÇÃO CONCLUÍDA COM SUCESSO !!!', mtInformation, [mbOK], 0);
end;

function Tfrmimportacadastroeventos.ConfirmarReimportacaoSeNecessario(const AIdEvento: string): Boolean;
begin
  Result := True;
  if FController.EventoJaImportado(AIdEvento) then
  begin
    if MessageDlg('Já existem registros deste evento na base, deseja reimportar ? (Y/N)',
      mtConfirmation, [mbYes, mbNo], 0) = mrYes then
    begin
      FController.RemoverImportacaoAnterior(AIdEvento);
      MessageDlg('REGISTROS REMOVIDOS !!!', mtInformation, [mbOK], 0);
    end
    else
      Result := False;
  end;
end;

procedure Tfrmimportacadastroeventos.ExecutarImportacao(ALayoutCompleto: Boolean);
var
  vResultado: TResultadoImportacao;
begin
  if lblidevento.Text = '' then
  begin
    MessageDlg('É OBRIGATÓRIO INFORMAR QUAL EVENTO DESEJA IMPORTAR CADASTROS !!!', mtError, [mbOK], 0);
    lblidevento.SetFocus;
    Exit;
  end;
  if lblarquivoorigem.Text = '' then
    Exit;

  if not ConfirmarReimportacaoSeNecessario(lblidevento.Text) then
    Exit;

  if MessageDlg('Confirma a Importação dos Cadastros deste Evento ? (Y/N)', mtConfirmation, [mbYes, mbNo], 0) <> mrYes then
    Exit;

  Screen.Cursor := crSQLWait;
  try
    if ALayoutCompleto then
      vResultado := FController.ImportarLayoutCompleto(lblidevento.Text, lblarquivoorigem.Text)
    else
      vResultado := FController.ImportarLayoutReduzido(lblidevento.Text, lblarquivoorigem.Text);
  finally
    Screen.Cursor := crDefault;
  end;

  MostrarResultado(vResultado);
  lblarquivoorigem.Clear;
  lblidevento.SetFocus;
end;

procedure Tfrmimportacadastroeventos.FormActivate(Sender: TObject);
begin
  lblidevento.SetFocus;
end;

procedure Tfrmimportacadastroeventos.FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F10 then
    spbretornar.Click;
end;

procedure Tfrmimportacadastroeventos.lblarquivoorigemEnter(Sender: TObject);
begin
  with modulo_dados do
  begin
    if (lblidevento.Text <> '') and (lbldescricaoevento.Caption = '...') then
    begin
      fdquerysql7.Close;
      fdquerysql7.SQL.Text := 'SELECT uge.descricao FROM USER_geoapolo_eventos uge WITH (NOLOCK) WHERE idevento = :pIdEvento';
      fdquerysql7.ParamByName('pIdEvento').AsString := lblidevento.Text;
      fdquerysql7.Open;
      if fdquerysql7.RecordCount > 0 then
      begin
        lbldescricaoevento.Caption := fdquerysql7.FieldByName('descricao').AsString;
        lbldescricaoevento.Refresh;
      end;
    end;
  end;
end;

procedure Tfrmimportacadastroeventos.lblarquivoorigemKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then
    spbarquivoorigem.Click;
end;

procedure Tfrmimportacadastroeventos.lblideventoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then
    lblarquivoorigem.SetFocus;
  if Key = VK_F4 then
    spbconsulta.Click;
end;

procedure Tfrmimportacadastroeventos.spbarquivoorigemClick(Sender: TObject);
begin
  opendir.Execute;
  lblarquivoorigem.Text := opendir.FileName;
  if MessageDlg('Confirma o carregamento do Arquivo ? (Y/N)', mtConfirmation, [mbYes, mbNo], 0) = mrYes then
    lblarquivoorigem.Refresh;
  // A pré-visualização em grid foi removida: a planilha agora é lida sob demanda
  // pelo controller no momento da importação (TImportadorPlanilhaExcelOLE),
  // e não há mais um TStringGrid intermediário para preencher aqui.
end;

procedure Tfrmimportacadastroeventos.spbconsultaClick(Sender: TObject);
var
  vQuery: TFDQuery;
  i: Integer;
begin
  // 1. Evita AV se o controller não existir
  if not Assigned(FController) then
    Exit;

  vQuery := FController.ListarEventosDisponiveis;

  // 2. Evita AV se a query retornar nula
  if not Assigned(vQuery) then
    Exit;

  try
    if vQuery.RecordCount > 0 then
    begin
      // 3. Criação segura do Form modal sem depender do Application
      frmconsulta3 := Tfrmconsulta3.Create(nil);
      try
        frmconsulta3.controle := 'EVENTOS_IMPORTA';

        // Limpa os combos antes de preencher, caso seja reaproveitado
        frmconsulta3.cbocampo.Items.Clear;
        frmconsulta3.cbordem.Items.Clear;

        for i := 0 to vQuery.FieldCount - 1 do
        begin
          frmconsulta3.cbocampo.Items.Add(vQuery.Fields[i].DisplayName);
          frmconsulta3.cbordem.Items.Add(vQuery.Fields[i].DisplayName);
        end;

        // Cria o DataSource amarrado ao ciclo de vida do form
        frmconsulta3.gridconsulta.DataSource := TDataSource.Create(frmconsulta3);
        frmconsulta3.gridconsulta.DataSource.DataSet := vQuery;

        frmconsulta3.ShowModal;
      finally
        // 4. GARANTE a destruição do Form após fechar
        FreeAndNil(frmconsulta3);
      end;
    end;
  finally
    // ATENÇÃO AQUI: Só mantenha o vQuery.Free se a rotina
    // "ListarEventosDisponiveis" der um TFDQuery.Create(...).
    // Se ela retorna uma query que já existe lá dentro, COMENTE a linha abaixo!
    vQuery.Free;
  end;
end;

procedure Tfrmimportacadastroeventos.spbimportarClick(Sender: TObject);
begin
  ExecutarImportacao(True);
end;

procedure Tfrmimportacadastroeventos.spblayoutreduzidoClick(Sender: TObject);
begin
  ExecutarImportacao(False);
end;

procedure Tfrmimportacadastroeventos.spbretornarClick(Sender: TObject);
begin
  Close;
end;

end.
