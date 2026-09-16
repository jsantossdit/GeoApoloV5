unit unt_cadempresas;

interface

uses
  Winapi.Windows, Winapi.Messages,
  System.SysUtils, System.Variants, System.Classes,
  Vcl.Graphics, Vcl.Controls, Vcl.Forms, Vcl.Dialogs,
  Vcl.StdCtrls, Vcl.ComCtrls, Vcl.Buttons, Vcl.ExtCtrls,
  Data.DB, Vcl.Grids, Vcl.DBGrids,
  FireDAC.Comp.Client,   // TFDQuery
  unt_empresa, Vcl.Mask;

type
  Tfrmcadempresas = class(TForm)
    panelmenu  : TPanel;
    spbsalvar  : TSpeedButton;
    spbligacoes: TSpeedButton;
    spbsair    : TSpeedButton;
    spblimpar  : TSpeedButton;
    lblsair    : TLabel;
    spbexcluir : TSpeedButton;
    StatusBar1 : TStatusBar;
    GroupBox1  : TGroupBox;
    lblempcod  : TLabeledEdit;
    lblempnome : TLabeledEdit;
    gridempresas: TDBGrid;

    procedure FormActivate(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbsalvarClick(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure spbsairClick(Sender: TObject);
    procedure spbligacoesClick(Sender: TObject);
    procedure gridempresasDblClick(Sender: TObject);
    procedure gridempresasKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);

  private
    FEmpresa : TEmpresa;
    FControle: string;  // 'INCLUSÃO' | 'ALTERAÇÃO'

    procedure CarregarFormulario(const AEmpresa: TEmpresa);
    procedure LimparFormulario;
    procedure PrepararInclusao;
  public
    { Public declarations }
  end;

var
  frmcadempresas: Tfrmcadempresas;

// Mantém assinatura original para compatibilidade com restante do projeto
function mostraempresas(const AParametro: string): string;

implementation

{$R *.dfm}

uses
  funcoes, unt_dados, unt_principal;

{ ---------------------------------------------------------------------------
  Funções auxiliares (escopo de unit, padrão do projeto)
  --------------------------------------------------------------------------- }

function mostraempresas(const AParametro: string): string;
var
  LSQL: string;
begin
  Result := '';
  with modulo_dados, frmcadempresas do
  begin
    if AParametro.IsEmpty then
      LSQL := 'SELECT empcod, empnome FROM USER_geoapolo_empresas ORDER BY empcod ASC'
    else
      LSQL := 'SELECT empcod, empnome FROM USER_geoapolo_empresas';

    // FireDAC: abre a query e vincula ao DataSource já existente no DataModule
    fdquerysql4.Close;
    fdquerysql4.SQL.Text := LSQL;
    if executaracao(fdquerysql4, fdbanco,true,dtsfdquerysql4) then
    begin
      gridempresas.DataSource := dtsfdquerysql4;
      gridempresas.SetFocus;
    end;
  end;
end;

{ ---------------------------------------------------------------------------
  Métodos privados do formulário
  --------------------------------------------------------------------------- }

procedure Tfrmcadempresas.CarregarFormulario(const AEmpresa: TEmpresa);
begin
  lblempcod.Text := AEmpresa.Cod;
  lblempnome.Text := AEmpresa.Nome;
  GroupBox1.Refresh;
  lblempnome.SetFocus;
end;

procedure Tfrmcadempresas.LimparFormulario;
begin
  FEmpresa.Limpar;
  FEmpresa.Cod := geoapolo_configcod(frmprincipal.codigo_empresa,
                                     'USER_geoapolo_empresas', 'S');
  lblempcod.Text := FEmpresa.Cod;
  lblempnome.Clear;
  lblempnome.SetFocus;
end;

procedure Tfrmcadempresas.PrepararInclusao;
begin
  FControle := 'INCLUSÃO';
  LimparFormulario;
end;

{ ---------------------------------------------------------------------------
  Eventos do formulário
  --------------------------------------------------------------------------- }

procedure Tfrmcadempresas.FormActivate(Sender: TObject);
begin
  FEmpresa := TEmpresa.Create;
  mostraempresas('');
  PrepararInclusao;
end;

procedure Tfrmcadempresas.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  FEmpresa.Free;
  Action := caFree;
end;

procedure Tfrmcadempresas.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
  if Key = VK_F10 then
    spbsair.Click;
end;

{ ---------------------------------------------------------------------------
  Eventos do grid
  --------------------------------------------------------------------------- }

procedure Tfrmcadempresas.gridempresasDblClick(Sender: TObject);
begin
  with modulo_dados do
  begin
    FControle      := 'ALTERAÇÃO';
    FEmpresa.Cod   := fdquerysql4.FieldByName('empcod').AsString;
    FEmpresa.Nome  := fdquerysql4.FieldByName('empnome').AsString;
    CarregarFormulario(FEmpresa);
  end;
end;

procedure Tfrmcadempresas.gridempresasKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
var
  LCod: string;
  LSQL: string;
begin
  if Key <> VK_DELETE then Exit;
  LCod := modulo_dados.fdquerysql4.FieldByName('empcod').AsString;

  MessageDlg('LEMBRETE: Para remover uma empresa, ela não poderá ter ' + 'vínculos em qualquer parte do sistema !!!', mtWarning, [mbOK], 0);

  if MessageDlg('Confirma a Remoção desta empresa ? (Y/N)', mtConfirmation, [mbYes, mbNo], 0) <> idYes then Exit;

  LSQL := 'DELETE FROM USER_geoapolo_empresas WHERE empcod = :empcod';

  // FireDAC: usa ExecSQL direto, sem precisar de querysql3 para DML simples
  modulo_dados.fdquerysql3.Close;
  modulo_dados.fdquerysql3.sql.clear;
  modulo_dados.fdquerysql3.sql.text := LSQL;
  modulo_dados.fdquerysql3.parambyname('empcod').asstring:= LCod;
  modulo_dados.fdquerysql3.ExecSQL;

  mostraempresas('');

  if modulo_dados.fdquerysql4.RecordCount > 0 then
      begin
        PrepararInclusao;
      end
  else
    begin
       MessageDlg('A EMPRESA POSSUI VÍNCULOS NO SISTEMA. PARA REMOÇÃO CONSULTE A EQUIPE DE SUPORTE !!!', mtError, [mbOK], 0);
       lblempnome.SetFocus;
    end;
end;

{ ---------------------------------------------------------------------------
  Eventos dos botões
  --------------------------------------------------------------------------- }
procedure Tfrmcadempresas.spbsalvarClick(Sender: TObject);
var
  LMsgValidacao: string;
  LSQL: string;
begin
  with modulo_dados do
  begin
    // Garante código antes de qualquer validação
    if trim(lblempcod.Text).IsEmpty then
    begin
      FEmpresa.Cod   := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_empresas', 'Sim');
      lblempcod.Text := FEmpresa.Cod;
      lblempcod.Refresh;
    end;

    // Popula objeto antes de validar
    FEmpresa.Cod  := lblempcod.Text;
    FEmpresa.Nome := lblempnome.Text;

    // Validação via objeto
    LMsgValidacao := FEmpresa.Valida;
    if not LMsgValidacao.IsEmpty then
      begin
        MessageDlg(LMsgValidacao, mtError, [mbOK], 0);
        lblempnome.SetFocus;
        Exit;
      end;

    if MessageDlg('Confirma a ' + FControle + ' para esta empresa ? (Y/N)', mtConfirmation, [mbYes, mbNo], 0) <> idYes then Exit;

    // Monta SQL conforme operação
    if FControle = 'INCLUSÃO' then
      LSQL := 'INSERT INTO USER_geoapolo_empresas (empcod, empnome) VALUES (:empcod, :empnome)'
    else
      LSQL := 'UPDATE USER_geoapolo_empresas SET empnome = :empnome WHERE empcod = :empcod' ;

    // FireDAC: ExecSQL para DML
    modulo_dados.fdquerysql3.Close;
    modulo_dados.fdquerysql3.sql.clear;
    modulo_dados.fdquerysql3.sql.Text := LSQL;
    modulo_dados.fdquerysql3.parambyname('empnome').asstring := FEmpresa.Nome;
    modulo_dados.fdquerysql3.parambyname('empcod').asstring :=FEmpresa.Cod;
    modulo_dados.fdquerysql3.ExecSQL;

    if modulo_dados.fdquerysql3.RowsAffected > 0 then
      begin
        MessageDlg(FControle + ' realizada com sucesso !!!', mtInformation, [mbOK], 0);
        mostraempresas('');
        PrepararInclusao;
      end
    else
       begin
          MessageDlg('ERRO AO REALIZAR A ' + FControle + ' PARA ESTA EMPRESA', mtError, [mbOK], 0);
          mostraempresas('');
          lblempcod.SetFocus;
       end;
  end;
end;

procedure Tfrmcadempresas.spblimparClick(Sender: TObject);
begin
  PrepararInclusao;
end;

procedure Tfrmcadempresas.spbsairClick(Sender: TObject);
begin
  Close;
end;

procedure Tfrmcadempresas.spbligacoesClick(Sender: TObject);
begin
  MessageDlg('PARA LOCALIZAR UMA EMPRESA, SELECIONE NO GRID ABAIXO !!!', mtInformation, [mbOK], 0);
end;

end.
