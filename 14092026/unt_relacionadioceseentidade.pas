unit unt_relacionadioceseentidade;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.ComCtrls, Vcl.StdCtrls, Vcl.Buttons,
  Vcl.ExtCtrls, Data.DB, Vcl.Grids, Vcl.DBGrids, Vcl.Mask,
  unt_relacionadioceseentidade_types,
  unt_relacionadioceseentidade_repository,
  unt_relacionadioceseentidade_service;

type
  Tfrmrelacionaentidadediocese = class(TForm)
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spblimpar: TSpeedButton;
    spbdeletar: TSpeedButton;
    spbabreos: TSpeedButton;
    spbsair: TSpeedButton;
    lblmsg1: TLabel;
    StatusBar1: TStatusBar;
    GroupBox1: TGroupBox;
    mskdtinicial: TMaskEdit;
    lbldatainicial: TLabel;
    mskdtfinal: TMaskEdit;
    lbldtfinal: TLabel;
    btnverificaentidadessemdiocese: TBitBtn;
    gridentidadessemdiocese: TDBGrid;
    lblentcod: TLabeledEdit;
    spbuscaentidade: TSpeedButton;
    lblentnome: TLabel;
    lblcidcod: TLabel;
    lbldioceseid: TLabeledEdit;
    spbuscadiocese: TSpeedButton;
    lbldiocesenome: TLabel;
    lblcidadediocese: TLabel;
    lblufsigla: TLabel;
    spbrelacionaentidade: TSpeedButton;
    lblplataformasve: TLabel;
    chkdioceserelacionada: TCheckBox;
    lblqtdperiodo: TLabel;
    lblnqtdperiodo: TLabel;
    procedure spbsairClick(Sender: TObject);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormActivate(Sender: TObject);
    procedure mskdtinicialKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure mskdtfinalKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblentcodKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lbldioceseidEnter(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure btnverificaentidadessemdioceseClick(Sender: TObject);
    procedure gridentidadessemdioceseDblClick(Sender: TObject);
    procedure spbuscadioceseClick(Sender: TObject);
    procedure spbrelacionaentidadeClick(Sender: TObject);
    procedure lbldioceseidKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbsalvarClick(Sender: TObject);
  private
    FRepository: IRelacionaDioceseEntidadeRepository;
    FService: IRelacionaDioceseEntidadeService;
    procedure InicializarServicos;
  public
    estadoid: string;
  end;

var
  frmrelacionaentidadediocese: Tfrmrelacionaentidadediocese;
  resp: word;

function retorna_diocese(dioceseid: string; cidade_entidade: string): string; export;
function retorna_entidade(entcod: string): string; export;

implementation

{$R *.dfm}

uses funcoes, unt_dados, unt_consultav3, unt_principal;

procedure Tfrmrelacionaentidadediocese.InicializarServicos;
begin
  if FService = nil then
  begin
    FRepository := TRelacionaDioceseEntidadeRepositoryFireDAC.Create(modulo_dados.fdbanco);
    FService := TRelacionaDioceseEntidadeService.Create(FRepository);
  end;
end;

procedure Tfrmrelacionaentidadediocese.btnverificaentidadessemdioceseClick(Sender: TObject);
var
  sql: string;
begin
  if (mskdtinicial.Text = '  /  /    ') or (mskdtfinal.Text = '  /  /    ') then
  begin
    MessageDlg('INFORME O PERÍODO DE CADASTRO DAS ENTIDADES QUE DESEJA RELACIONAR !!!', mtError, [mbOK], 0);
    spblimpar.Click;
    mskdtinicial.SetFocus;
    Exit;
  end;

  with modulo_dados do
  begin
    sql := 'SELECT e.entcod, e.entnome, e.cidcod, cid.cidnomecomp, cid.ufsigla, e1.USERDiocese_id, e1.USERNomeDiocese, e1.USERJanaSVE ' +
           'FROM entidade e WITH(NOLOCK) ' +
           'INNER JOIN ent_categ ec WITH(NOLOCK) ON e.entcod = ec.entcod ' +
           'INNER JOIN cidade cid WITH(NOLOCK) ON e.cidcod = cid.cidcod ' +
           'LEFT JOIN u_entidade e1 WITH(NOLOCK) ON e.entcod = e1.entcod ' +
           'WHERE SUBSTRING(ec.categcodestr,1,6) IN (''02.001'', ''02.002'', ''03.001'', ''03.002'', ''03.003'', ''03.004'', ''03.005'') ' +
           '  AND e.entdesdedata BETWEEN ' + QuotedStr(FormatDateTime('yyyy-mm-dd', StrToDateTime(mskdtinicial.Text))) +
           '                         AND ' + QuotedStr(FormatDateTime('yyyy-mm-dd', StrToDateTime(mskdtfinal.Text)));

    if chkdioceserelacionada.Checked then
    begin
      sql := sql + ' AND (e1.USERDiocese_id IS NULL OR RTRIM(e1.USERDiocese_id) = '''')';
    end;

    sql := sql + ' ORDER BY e.entcod ASC';

    fdquerysql4.Close;
    fdquerysql4.SQL.Clear;
    fdquerysql4.SQL.Text := sql;

    if executaracao(fdquerysql4, fdbanco, True, dtsfdquerysql4) then
    begin
      gridentidadessemdiocese.DataSource := dtsfdquerysql4;
      lblnqtdperiodo.Caption := IntToStr(fdquerysql4.RecordCount);
      lblnqtdperiodo.Refresh;
      gridentidadessemdiocese.Refresh;
      gridentidadessemdiocese.SetFocus;
    end;
  end;
end;

procedure Tfrmrelacionaentidadediocese.FormActivate(Sender: TObject);
begin
  InicializarServicos;
  statusbar1.Panels[1].Text := configura_statusbar('a');
  statusbar1.Panels[3].Text := statusbar1.Panels[1].Text;
  statusbar1.Panels[5].Text := nomecomputador;
  mskdtinicial.SetFocus;
end;

procedure Tfrmrelacionaentidadediocese.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Action := caFree;
end;

procedure Tfrmrelacionaentidadediocese.FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F10 then
    spbsair.Click;
end;

procedure Tfrmrelacionaentidadediocese.gridentidadessemdioceseDblClick(Sender: TObject);
begin
  with modulo_dados do
  begin
    lblentcod.Text := fdquerysql4.FieldByName('entcod').AsString;
    lblentnome.Caption := fdquerysql4.FieldByName('entnome').AsString;
    lblcidcod.Caption := fdquerysql4.FieldByName('cidnomecomp').AsString;
    lblufsigla.Caption := fdquerysql4.FieldByName('ufsigla').AsString;

    if fdquerysql4.FieldByName('USERJanaSVE').AsString = 'S' then
    begin
      lblplataformasve.Caption := 'JÁ DISPONÍVEL NA PLATAFORMA SVE';
      lblplataformasve.Font.Color := clGreen;
      lblplataformasve.Refresh;
    end
    else if fdquerysql4.FieldByName('USERJanaSVE').AsString = 'N' then
    begin
      lblplataformasve.Caption := 'AINDA NÃO FOI INCLUÍDA NA SVE';
      lblplataformasve.Font.Color := clRed;
      lblplataformasve.Refresh;
    end
    else
    begin
      lblplataformasve.Caption := '';
      lblplataformasve.Refresh;
    end;

    lbldioceseid.Text := fdquerysql4.FieldByName('USERDiocese_id').AsString;
    lbldiocesenome.Caption := fdquerysql4.FieldByName('USERNomeDiocese').AsString;
    lblcidadediocese.Caption := retorna_diocese(fdquerysql4.FieldByName('USERDiocese_id').AsString,
                                                fdquerysql4.FieldByName('cidnomecomp').AsString);
    lblcidadediocese.Refresh;
    lbldioceseid.SetFocus;
  end;
end;

function retorna_diocese(dioceseid: string; cidade_entidade: string): string;
var
  Rep: IRelacionaDioceseEntidadeRepository;
begin
  Rep := TRelacionaDioceseEntidadeRepositoryFireDAC.Create(modulo_dados.fdbanco);
  Result := Rep.BuscarDiocesePorCidade(dioceseid, cidade_entidade);
end;

function retorna_entidade(entcod: string): string;
var
  Rep: IRelacionaDioceseEntidadeRepository;
  Ent: TEntidadeDioceseDTO;
begin
  Rep := TRelacionaDioceseEntidadeRepositoryFireDAC.Create(modulo_dados.fdbanco);
  if Rep.BuscarEntidadePorCodigo(entcod, Ent) then
    Result := Ent.CidNomeComp
  else
    Result := 'NÃO ENCONTRADO';
end;

procedure Tfrmrelacionaentidadediocese.lbldioceseidEnter(Sender: TObject);
begin
  lblcidcod.Caption := retorna_entidade(lblentcod.Text);
end;

procedure Tfrmrelacionaentidadediocese.lbldioceseidKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then
    spbuscadiocese.Click;
  if (Key = VK_RETURN) or (Key = VK_TAB) then
  begin
    if Trim(lbldioceseid.Text) = '' then
    begin
      lbldiocesenome.Caption := 'Nome Entidade';
      lblcidadediocese.Caption := 'Cidade/Estado';
    end;
  end;
end;

procedure Tfrmrelacionaentidadediocese.lblentcodKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then
    spbuscaentidade.Click;
  if (Key = VK_RETURN) or (Key = VK_TAB) then
    lbldioceseid.SetFocus;
end;

procedure Tfrmrelacionaentidadediocese.mskdtfinalKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then
    lblentcod.SetFocus;
end;

procedure Tfrmrelacionaentidadediocese.mskdtinicialKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then
    mskdtfinal.SetFocus;
end;

procedure Tfrmrelacionaentidadediocese.spblimparClick(Sender: TObject);
begin
  mskdtinicial.Clear;
  mskdtfinal.Clear;
  lblentcod.Clear;
  lbldioceseid.Clear;
  lblentnome.Caption := 'Nome Entidade';
  lbldiocesenome.Caption := 'Nome Entidade';
  lblcidcod.Caption := 'Cidade';
  lblufsigla.Caption := 'Estado';
  lblcidadediocese.Caption := 'Cidade/Estado';
  lblplataformasve.Caption := '';
  lblnqtdperiodo.Caption := '0';
end;

procedure Tfrmrelacionaentidadediocese.spbrelacionaentidadeClick(Sender: TObject);
var
  Res: TResultadoVinculoDiocese;
begin
  InicializarServicos;

  if Trim(lblentcod.Text) = '' then
  begin
    MessageDlg('Selecione uma Entidade primeiro!', mtWarning, [mbOK], 0);
    Exit;
  end;

  resp := MessageDlg('Confirma esta Diocese para este Colaborador/Entidade? (Y/N)', mtConfirmation, [mbYes, mbNo], 0);
  if resp = IDYES then
  begin
    if (lbldiocesenome.Caption = 'Nome Entidade') and (Trim(lbldioceseid.Text) = '') then
      Res := FService.DesvincularEntidadeDiocese(lblentcod.Text)
    else
      Res := FService.VincularEntidadeDiocese(lblentcod.Text, lbldioceseid.Text, lbldiocesenome.Caption);

    if Res.Sucesso then
    begin
      MessageDlg(Res.Mensagem, mtInformation, [mbOK], 0);
      lblcidcod.Caption := 'Cidade';
      lblufsigla.Caption := 'Estado';
      lblentcod.Clear;
      lbldioceseid.Clear;
      lblentnome.Caption := 'Nome Entidade';
      lbldiocesenome.Caption := lblentnome.Caption;
      lblcidadediocese.Caption := 'Cidade/Estado';
      lblplataformasve.Caption := '';
      btnverificaentidadessemdiocese.Click;
      gridentidadessemdiocese.SetFocus;
    end
    else
    begin
      MessageDlg('Falha na operação: ' + Res.Mensagem, mtError, [mbOK], 0);
    end;
  end;
end;

procedure Tfrmrelacionaentidadediocese.spbsairClick(Sender: TObject);
begin
  frmrelacionaentidadediocese.Close;
  frmprincipal.Show;
end;

procedure Tfrmrelacionaentidadediocese.spbsalvarClick(Sender: TObject);
begin
  spbrelacionaentidade.Click;
end;

procedure Tfrmrelacionaentidadediocese.spbuscadioceseClick(Sender: TObject);
var
  i: Integer;
begin
  with modulo_dados do
  begin
    fdquerysql6.Close;
    fdquerysql6.SQL.Clear;
    fdquerysql6.SQL.Text := 'SELECT USERid FROM USEREstado_CNBB WITH(NOLOCK) WHERE usersigla = :ufsigla';
    fdquerysql6.ParamByName('ufsigla').AsString := lblufsigla.Caption;
    if executaracao(fdquerysql6, fdbanco, True, dtsfdquerysql6) then
      estadoid := fdquerysql6.FieldByName('userid').AsString;

    fdquerysql5.Close;
    fdquerysql5.SQL.Clear;
    fdquerysql5.SQL.Text :=
      'SELECT dio.id, dio.nome, estado.usersigla, estado.usernome_estado, uccnbb.descricao ' +
      'FROM USERdioceses_CNBB dio WITH(NOLOCK) ' +
      'INNER JOIN USEREstado_CNBB estado WITH(NOLOCK) ON dio.estado_id = estado.USERid ' +
      'INNER JOIN USERcidades_CNBB uccnbb WITH(NOLOCK) ON dio.id = uccnbb.diocese_id ' +
      'WHERE dio.estado_id = :estadoid ' +
      '  AND uccnbb.descricao LIKE :lblcidcod ' +
      '  AND estado.usersigla = :ufsigla';
    fdquerysql5.ParamByName('estadoid').AsString := lblufsigla.Caption;
    fdquerysql5.ParamByName('lblcidcod').AsString := lblcidcod.Caption;
    fdquerysql5.ParamByName('ufsigla').AsString := lblufsigla.Caption;

    if executaracao(fdquerysql5, fdbanco, True, dtsfdquerysql5) then
    begin
      Application.CreateForm(Tfrmconsulta3, frmconsulta3);
      with frmconsulta3 do
      begin
        controle := 'RELACIONA_DIOCESES';
        dtsfdquerysql5.DataSet := fdquerysql5;
        frmconsulta3.gridconsulta.DataSource := dtsfdquerysql5;
        for i := 0 to fdquerysql5.Fields.Count - 1 do
        begin
          frmconsulta3.cbocampo.Items.Add(fdquerysql5.Fields[i].DisplayName);
          frmconsulta3.cbordem.Items.Add(fdquerysql5.Fields[i].DisplayName);
        end;
        frmconsulta3.gridconsulta.Refresh;
        frmconsulta3.ShowModal;
      end;
    end;
  end;
end;

end.
