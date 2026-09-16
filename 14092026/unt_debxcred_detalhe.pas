unit unt_debxcred_detalhe;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, ExtCtrls, StdCtrls, Mask, Buttons, ComCtrls, DB,
  FireDAC.Comp.Client, System.Generics.Collections, Vcl.DBGrids,
  uDebxCredDTO, uDebxCredController, FireDAC.Stan.Intf, FireDAC.Stan.Option,
  FireDAC.Stan.Param, FireDAC.Stan.Error, FireDAC.DatS, FireDAC.Phys.Intf,
  FireDAC.DApt.Intf, FireDAC.Comp.DataSet, Vcl.Grids;

type
  Tfrmdebcred_detalhe = class(TForm)
    panelmenu: TPanel;
    spbexecutar: TSpeedButton;
    spbimprimerecibo: TSpeedButton;
    spbsair: TSpeedButton;
    spblimpar: TSpeedButton;
    spbajuste: TSpeedButton;
    StatusBar1: TStatusBar;
    GroupBox1: TGroupBox;
    lbldatainicial: TLabel;
    lblnomecontacontabil: TLabel;
    spbuscacontacontabil: TSpeedButton;
    mskdtinicial: TMaskEdit;
    lblcodredconta: TLabeledEdit;
    GroupBox2: TGroupBox;
    dsdetalhe: TDataSource;
    mtdetalhe: TFDMemTable;
    dbgdetalhes: TDBGrid;

    procedure FormCreate(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbsairClick(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure spbuscacontacontabilClick(Sender: TObject);
    procedure spbexecutarClick(Sender: TObject);
    procedure dbgDetalhesDrawColumnCell(Sender: TObject; const Rect: TRect;
      DataCol: Integer; Column: TColumn; State: TGridDrawState);
    procedure mskdtinicialKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblcodredcontaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);

  private
    procedure ConfigurarComponentes;
    procedure CriarEstruturaMemTable;
    procedure CarregarGrid(const ALista: TObjectList<TDebxCredDetalheDTO>);
    procedure SetarStatus(const AMensagem: string);
    function GetEmpresaLogada: string;
  public
  end;

var
  frmdebcred_detalhe: Tfrmdebcred_detalhe;

implementation

uses unt_dados, unt_principal, unt_consultav3;

{$R *.dfm}

{ Tfrmdebcred_detalhe }

procedure Tfrmdebcred_detalhe.FormCreate(Sender: TObject);
begin
  ConfigurarComponentes;
  CriarEstruturaMemTable;
  SetarStatus('Pronto.');
end;

procedure Tfrmdebcred_detalhe.ConfigurarComponentes;
begin
  // Vincula os componentes de dados
  dsdetalhe.DataSet := mtdetalhe;
  dbgDetalhes.DataSource := dsdetalhe;

  // UX: Selecionar a linha toda e zebra no grid
  dbgDetalhes.Options := dbgDetalhes.Options + [dgRowSelect, dgTabs];
  dbgDetalhes.TitleFont.Style := [fsBold];
end;

procedure Tfrmdebcred_detalhe.CriarEstruturaMemTable;
begin
  mtdetalhe.Close;
  mtdetalhe.FieldDefs.Clear;
  // Estrutura idêntica ao DTO para facilitar o mapeamento
  mtdetalhe.FieldDefs.Add('Data', ftDate);
  mtdetalhe.FieldDefs.Add('Debito', ftCurrency);
  mtdetalhe.FieldDefs.Add('Credito', ftCurrency);
  mtdetalhe.FieldDefs.Add('Saldo', ftCurrency);
  mtdetalhe.FieldDefs.Add('Modulo', ftString, 20);
  mtdetalhe.FieldDefs.Add('Origem', ftString, 30);
  mtdetalhe.FieldDefs.Add('Documento', ftString, 20);
  mtdetalhe.FieldDefs.Add('Status', ftString, 10);
  mtdetalhe.FieldDefs.Add('ChaveContabil', ftString, 50);
  mtdetalhe.FieldDefs.Add('Inconsistencia', ftString, 100);
  mtdetalhe.CreateDataSet;
end;

function Tfrmdebcred_detalhe.GetEmpresaLogada: string;
begin
  // Padrão GeoApolo para filtrar por filial (1.01, 1.02, etc)
  Result := frmprincipal.codigo_empresa;
end;

procedure Tfrmdebcred_detalhe.spbexecutarClick(Sender: TObject);
var
  Controller: TDebxCredController;
  Lista: TObjectList<TDebxCredDetalheDTO>;
  DataConsulta: TDate;
begin
  // Validação de Data manual para evitar erro de overload E2250
  try
    DataConsulta := StrToDate(Trim(mskdtinicial.Text));
  except
    on E: Exception do
    begin
      MessageDlg('Data inválida! Verifique o formato dd/mm/aaaa.', mtWarning, [mbOK], 0);
      mskdtinicial.SetFocus;
      Exit;
    end;
  end;

  if Trim(lblcodredconta.Text) = '' then
  begin
    MessageDlg('É necessário informar uma conta contábil!', mtWarning, [mbOK], 0);
    lblcodredconta.SetFocus;
    Exit;
  end;

  Screen.Cursor := crHourGlass;
  SetarStatus('Consultando base de dados...');
  try
    Controller := TDebxCredController.Create(modulo_dados.fdbanco);
    try
      // Chama o método no Controller (Regra de Negócio)
      Lista := Controller.ConsultarDetalhes(DataConsulta, lblcodredconta.Text, GetEmpresaLogada);
      CarregarGrid(Lista);
    finally
      Controller.Free;
    end;
  finally
    Screen.Cursor := crDefault;
  end;
end;

procedure Tfrmdebcred_detalhe.CarregarGrid(const ALista: TObjectList<TDebxCredDetalheDTO>);
var
  Item: TDebxCredDetalheDTO;
  SaldoAcumulado: Currency;
begin
  mtdetalhe.DisableControls;
  try
    if not mtdetalhe.Active then mtdetalhe.CreateDataSet;
    mtdetalhe.EmptyDataSet;

    SaldoAcumulado := 0;

    for Item in ALista do
    begin
      SaldoAcumulado := SaldoAcumulado + (Item.Debito - Item.Credito);

      mtdetalhe.Append;
      mtdetalhe.FieldByName('Data').AsDateTime := Item.Data;
      mtdetalhe.FieldByName('Debito').AsCurrency := Item.Debito;
      mtdetalhe.FieldByName('Credito').AsCurrency := Item.Credito;
      mtdetalhe.FieldByName('Saldo').AsCurrency := SaldoAcumulado;
      mtdetalhe.FieldByName('Modulo').AsString := Item.Modulo;
      mtdetalhe.FieldByName('Origem').AsString := Item.Origem;
      mtdetalhe.FieldByName('Documento').AsString := Item.Documento;
      mtdetalhe.FieldByName('Status').AsString := Item.Status;
      mtdetalhe.FieldByName('ChaveContabil').AsString := Item.Chave;
      mtdetalhe.FieldByName('Inconsistencia').AsString := Item.ErroMsg;
      mtdetalhe.Post;
    end;

    SetarStatus(Format('Sucesso: %d registros encontrados.', [ALista.Count]));
  finally
    mtdetalhe.EnableControls;
  end;
end;

procedure Tfrmdebcred_detalhe.dbgDetalhesDrawColumnCell(Sender: TObject;
  const Rect: TRect; DataCol: Integer; Column: TColumn; State: TGridDrawState);
begin
  // UX: Destaca linhas com erro de origem/falha
  if mtdetalhe.FieldByName('Status').AsString = 'Falha' then
  begin
    dbgDetalhes.Canvas.Brush.Color := $00E1E1FF; // Vermelho pálido
    dbgDetalhes.Canvas.Font.Color := clRed;
  end;

  if gdSelected in State then
  begin
    dbgDetalhes.Canvas.Brush.Color := clHighlight;
    dbgDetalhes.Canvas.Font.Color := clHighlightText;
  end;

  dbgDetalhes.DefaultDrawColumnCell(Rect, DataCol, Column, State);
end;

procedure Tfrmdebcred_detalhe.spblimparClick(Sender: TObject);
begin
  if mtdetalhe.Active then mtdetalhe.EmptyDataSet;
  lblcodredconta.Clear;
  lblnomecontacontabil.Caption := '';
  mskdtinicial.Clear;
  mskdtinicial.SetFocus;
  SetarStatus('Filtros limpos.');
end;

procedure Tfrmdebcred_detalhe.spbuscacontacontabilClick(Sender: TObject);
begin
  // Aqui você deve reutilizar a lógica de busca do Plano de Contas
  // que implementamos no módulo principal.
end;

procedure Tfrmdebcred_detalhe.SetarStatus(const AMensagem: string);
begin
  StatusBar1.Panels[0].Text := AMensagem;
end;

procedure Tfrmdebcred_detalhe.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Action := caFree;
end;

procedure Tfrmdebcred_detalhe.FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F10 then spbsair.Click;
end;

procedure Tfrmdebcred_detalhe.spbsairClick(Sender: TObject);
begin
  Close;
end;

procedure Tfrmdebcred_detalhe.mskdtinicialKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_RETURN then lblcodredconta.SetFocus;
end;

procedure Tfrmdebcred_detalhe.lblcodredcontaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_RETURN then spbexecutar.Click;
end;

end.
