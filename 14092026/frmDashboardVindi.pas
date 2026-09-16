unit frmdashboardvindi;
interface
uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants,
  System.Classes, System.DateUtils, System.Math,
  Vcl.Graphics, Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.StdCtrls,
  Vcl.ExtCtrls, Vcl.ComCtrls, Vcl.Samples.Spin,
  VCLTee.TeeGDIPlus, VCLTee.TeEngine, VCLTee.Series, VCLTee.TeeProcs,
  VCLTee.Chart, FireDAC.Comp.Client,unt_intf_dashboardvindi, unt_repo_dashboardvindi;
type
  TfrmDashboardVindi = class(TForm)
    pnlTop: TPanel;
    lblAnoInicial: TLabel;
    seAnoInicial: TSpinEdit;
    btnAtualizar: TButton;
    pgcGraficos: TPageControl;
    tsEvolucaoAnual: TTabSheet;
    tsEvolucaoMensal: TTabSheet;
    tsMeioPagamento: TTabSheet;
    tsStatus: TTabSheet;
    tsTicketMedio: TTabSheet;
    tsTaxaEfetiva: TTabSheet;
    tsTopClientes: TTabSheet;
    ChartEvolucaoAnual: TChart;
    ChartEvolucaoMensal: TChart;
    ChartMeioPagamento: TChart;
    ChartStatus: TChart;
    ChartTicketMedio: TChart;
    ChartTaxaEfetiva: TChart;
    ChartTopClientes: TChart;
    procedure FormCreate(Sender: TObject);
    procedure btnAtualizarClick(Sender: TObject);
  private
    FRepository: IDashboardVindiRepository;
    FConnection: TFDConnection;
    procedure CarregarDashboard;
    procedure MontarGraficoEvolucaoAnual(const AItens: TArray<TEvolucaoAnual>);
    procedure MontarGraficoEvolucaoMensal(const AItens: TArray<TEvolucaoMensal>; const AAno: Integer);
    procedure MontarGraficoMeioPagamento(const AItens: TArray<TDistribuicaoMeioPagamento>);
    procedure MontarGraficoStatus(const AItens: TArray<TDistribuicaoStatus>);
    procedure MontarGraficoTicketMedio(const AItens: TArray<TEvolucaoAnual>);
    procedure MontarGraficoTaxaEfetiva(const AItens: TArray<TEvolucaoAnual>);
    procedure MontarGraficoTopClientes(const AItens: TArray<TTopCliente>);
    procedure MarcaFormatoMoeda(Sender: TChartSeries; ValueIndex: Integer; var MarkText: string);
    procedure MarcaFormatoPercentual(Sender: TChartSeries; ValueIndex: Integer; var MarkText: string);
  public
    /// <summary>
    ///   Conexão FireDAC a ser usada pelo dashboard. Deve ser atribuida pelo
    ///   formulário/módulo chamador antes de exibir o dashboard, por exemplo:
    ///   frmDashboardVindi.Connection := DM.FDConnection1;
    /// </summary>
    property Connection: TFDConnection read FConnection write FConnection;
  end;

implementation
{$R *.dfm}

uses unt_dados;
{ TfrmDashboardVindi }
procedure TfrmDashboardVindi.FormCreate(Sender: TObject);
begin
  seAnoInicial.MinValue := 2010;
  seAnoInicial.MaxValue := YearOf(Now);
  seAnoInicial.Value := YearOf(Now) - 3;
end;

procedure TfrmDashboardVindi.btnAtualizarClick(Sender: TObject);
begin
  CarregarDashboard;
end;

procedure TfrmDashboardVindi.MarcaFormatoMoeda(Sender: TChartSeries; ValueIndex: Integer; var MarkText: string);
begin
  MarkText := 'R$ ' + FormatFloat('#,##0.00', Sender.YValues.Value[ValueIndex]);
end;

procedure TfrmDashboardVindi.MarcaFormatoPercentual(Sender: TChartSeries; ValueIndex: Integer; var MarkText: string);
begin
  MarkText := FormatFloat('0.00', Sender.YValues.Value[ValueIndex]) + '%';
end;

procedure TfrmDashboardVindi.CarregarDashboard;
var
  anoInicial: Integer;
  itensEvolucaoAnual: TArray<TEvolucaoAnual>;
begin
  if not Assigned(modulo_dados.fdbanco) then
  begin
    ShowMessage('Conexão com o banco não configurada. Defina a propriedade ' +
      '"Connection" deste formulário antes de carregar o dashboard.');
    Exit;
  end;
  if not Assigned(FRepository) then
    FRepository := TDashboardVindiRepository.Create(modulo_dados.fdbanco);
  anoInicial := seAnoInicial.Value;
  Screen.Cursor := crHourGlass;
  try
    // Reaproveita a mesma consulta de evolução anual para os gráficos de
    // ticket médio e taxa efetiva, evitando ida desnecessária ao banco.
    itensEvolucaoAnual := FRepository.GetEvolucaoAnual(anoInicial);
    MontarGraficoEvolucaoAnual(itensEvolucaoAnual);
    MontarGraficoEvolucaoMensal(FRepository.GetEvolucaoMensal(YearOf(Now)), YearOf(Now));
    MontarGraficoMeioPagamento(FRepository.GetDistribuicaoPorMeioPagamento(anoInicial));
    MontarGraficoStatus(FRepository.GetDistribuicaoPorStatus(anoInicial));
    MontarGraficoTicketMedio(itensEvolucaoAnual);
    MontarGraficoTaxaEfetiva(itensEvolucaoAnual);
    MontarGraficoTopClientes(FRepository.GetTopClientesPorValorPago(anoInicial, 10));
  finally
    Screen.Cursor := crDefault;
  end;
end;

procedure TfrmDashboardVindi.MontarGraficoEvolucaoAnual(const AItens: TArray<TEvolucaoAnual>);
var
  serTotalPago, serTotalTaxa: TBarSeries;
  i: Integer;
begin
  ChartEvolucaoAnual.SeriesList.Clear;
  serTotalPago := TBarSeries.Create(ChartEvolucaoAnual);
  serTotalPago.Title := 'Total Pago';
  serTotalPago.SeriesColor := clSkyBlue;
  serTotalPago.Marks.Visible := True;
  serTotalPago.Marks.Style := smsValue;
  serTotalPago.OnGetMarkText := MarcaFormatoMoeda;
  serTotalPago.Marks.ArrowLength := 8;
  ChartEvolucaoAnual.AddSeries(serTotalPago);
  serTotalTaxa := TBarSeries.Create(ChartEvolucaoAnual);
  serTotalTaxa.Title := 'Total Taxa';
  serTotalTaxa.SeriesColor := clMoneyGreen;
  serTotalTaxa.Marks.Visible := True;
  serTotalTaxa.Marks.Style := smsValue;
  serTotalTaxa.OnGetMarkText := MarcaFormatoMoeda;
  serTotalTaxa.Marks.ArrowLength := 8;
  ChartEvolucaoAnual.AddSeries(serTotalTaxa);
  ChartEvolucaoAnual.Title.Text.Text := 'Evolução Anual - Valor Pago x Taxa';
  ChartEvolucaoAnual.Legend.Visible := True;
  for i := Low(AItens) to High(AItens) do
  begin
    serTotalPago.AddY(AItens[i].TotalPago, IntToStr(AItens[i].Ano));
    serTotalTaxa.AddY(AItens[i].TotalTaxa, IntToStr(AItens[i].Ano));
  end;
end;

procedure TfrmDashboardVindi.MontarGraficoEvolucaoMensal(const AItens: TArray<TEvolucaoMensal>; const AAno: Integer);
const
  NOMES_MESES: array[1..12] of string = (
    'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez');
var
  serie: TLineSeries;
  i: Integer;
begin
  ChartEvolucaoMensal.SeriesList.Clear;
  serie := TLineSeries.Create(ChartEvolucaoMensal);
  serie.Title := 'Total Pago';
  serie.SeriesColor := clSkyBlue;
  serie.Pointer.Visible := True;
  ChartEvolucaoMensal.AddSeries(serie);
  ChartEvolucaoMensal.Title.Text.Text := Format('Evolução Mensal - %d', [AAno]);
  ChartEvolucaoMensal.Legend.Visible := False;
  for i := Low(AItens) to High(AItens) do
    serie.AddY(AItens[i].TotalPago, NOMES_MESES[AItens[i].Mes]);
end;

procedure TfrmDashboardVindi.MontarGraficoMeioPagamento(const AItens: TArray<TDistribuicaoMeioPagamento>);
var
  serie: TPieSeries;
  i: Integer;
begin
  ChartMeioPagamento.SeriesList.Clear;
  serie := TPieSeries.Create(ChartMeioPagamento);
  serie.Title := 'Meio de Pagamento';
  ChartMeioPagamento.AddSeries(serie);
  ChartMeioPagamento.Title.Text.Text := 'Distribuição por Meio de Pagamento (Valor)';
  ChartMeioPagamento.Legend.Visible := True;
  for i := Low(AItens) to High(AItens) do
    serie.Add(AItens[i].TotalPago, AItens[i].MeioPagamento);
end;

procedure TfrmDashboardVindi.MontarGraficoStatus(const AItens: TArray<TDistribuicaoStatus>);
var
  serie: TPieSeries;
  i: Integer;
begin
  ChartStatus.SeriesList.Clear;
  serie := TPieSeries.Create(ChartStatus);
  serie.Title := 'Status';
  ChartStatus.AddSeries(serie);
  ChartStatus.Title.Text.Text := 'Distribuição por Status (Quantidade de Transaçães)';
  ChartStatus.Legend.Visible := True;
  for i := Low(AItens) to High(AItens) do
    serie.Add(AItens[i].QtdTransacoes, AItens[i].Status);
end;
procedure TfrmDashboardVindi.MontarGraficoTicketMedio(const AItens: TArray<TEvolucaoAnual>);
var
  serie: TLineSeries;
  i: Integer;
  ticketMedio: Currency;
begin
  ChartTicketMedio.SeriesList.Clear;
  serie := TLineSeries.Create(ChartTicketMedio);
  serie.Title := 'Ticket Médio';
  serie.SeriesColor := clPurple;
  serie.Pointer.Visible := True;
  serie.Marks.Visible := True;
  serie.Marks.Style := smsValue;
  serie.OnGetMarkText := MarcaFormatoMoeda;
  ChartTicketMedio.AddSeries(serie);
  ChartTicketMedio.Title.Text.Text := 'Ticket Médio Anual (Valor Pago / Qtd. Transações)';
  ChartTicketMedio.Legend.Visible := False;
  for i := Low(AItens) to High(AItens) do
  begin
    if AItens[i].QtdTransacoes > 0 then
      ticketMedio := AItens[i].TotalPago / AItens[i].QtdTransacoes
    else
      ticketMedio := 0;
    serie.AddY(ticketMedio, IntToStr(AItens[i].Ano));
  end;
end;
procedure TfrmDashboardVindi.MontarGraficoTaxaEfetiva(const AItens: TArray<TEvolucaoAnual>);
var
  serie: TLineSeries;
  i: Integer;
  taxaEfetiva: Double;
begin
  ChartTaxaEfetiva.SeriesList.Clear;
  serie := TLineSeries.Create(ChartTaxaEfetiva);
  serie.Title := 'Taxa Efetiva (%)';
  serie.SeriesColor := clRed;
  serie.Pointer.Visible := True;
  serie.Marks.Visible := True;
  serie.Marks.Style := smsValue;
  serie.OnGetMarkText := MarcaFormatoPercentual;
  ChartTaxaEfetiva.AddSeries(serie);
  ChartTaxaEfetiva.Title.Text.Text := 'Taxa Efetiva Anual (Total Taxa / Total Pago)';
  ChartTaxaEfetiva.Legend.Visible := False;
  for i := Low(AItens) to High(AItens) do
  begin
    if AItens[i].TotalPago > 0 then
      taxaEfetiva := (AItens[i].TotalTaxa / AItens[i].TotalPago) * 100
    else
      taxaEfetiva := 0;
    serie.AddY(taxaEfetiva, IntToStr(AItens[i].Ano));
  end;
end;

procedure TfrmDashboardVindi.MontarGraficoTopClientes(const AItens: TArray<TTopCliente>);
var
  serie: TBarSeries;
  i: Integer;
begin
  ChartTopClientes.SeriesList.Clear;
  serie := TBarSeries.Create(ChartTopClientes);
  serie.Title := 'Valor Pago';
  serie.SeriesColor := clTeal;
  serie.Marks.Visible := True;
  serie.Marks.Style := smsValue;
  serie.OnGetMarkText := MarcaFormatoMoeda;
  ChartTopClientes.AddSeries(serie);
  ChartTopClientes.Title.Text.Text := 'Top 10 Clientes por Valor Pago';
  ChartTopClientes.Legend.Visible := False;
  for i := Low(AItens) to High(AItens) do
    serie.AddY(AItens[i].TotalPago, AItens[i].Nome);
end;
end.
