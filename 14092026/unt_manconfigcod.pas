unit unt_manconfigcod;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.StdCtrls, Vcl.ExtCtrls,
  Vcl.ComCtrls, Vcl.Buttons, Data.DB, Vcl.Grids, Vcl.DBGrids, Vcl.Menus,
  Vcl.Mask;

type
  TfrmManCodigosSistema = class(TForm)
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spblimpar: TSpeedButton;
    spbdeletar: TSpeedButton;
    spbabreos: TSpeedButton;
    spbsair: TSpeedButton;
    lblmsg1: TLabel;
    StatusBar1: TStatusBar;
    grpbuscaccontrole: TGroupBox;
    lblcampo: TLabel;
    lblordem: TLabel;
    lblprocurarpor: TLabeledEdit;
    cbocampo: TComboBox;
    cbordem: TComboBox;
    rdgcrescente: TRadioButton;
    rdgdecrescente: TRadioButton;
    GroupBox1: TGroupBox;
    lblempcod: TLabeledEdit;
    lblempnome: TLabel;
    chktabelaativa: TCheckBox;
    lblproximocodigo: TLabeledEdit;
    gridconfigcod: TDBGrid;
    lblgeotabela: TLabeledEdit;
    popmenu: TPopupMenu;
    popmnugravaconfig: TMenuItem;
    procedure spbsairClick(Sender: TObject);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormActivate(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure gridconfigcodDblClick(Sender: TObject);
    procedure spbsalvarClick(Sender: TObject);
    procedure chktabelaativaClick(Sender: TObject);
    procedure popmnugravaconfigClick(Sender: TObject);
    procedure lblprocurarporKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
  private
    { Private declarations }
  public
    { Public declarations }
    vtabelaativa:string;
  end;

var
  frmManCodigosSistema: TfrmManCodigosSistema;

function mostra_tabelas(parametro : string) : string; export;

implementation

{$R *.dfm}

uses funcoes, unt_dados, unt_principal, unt_logon;

procedure TfrmManCodigosSistema.chktabelaativaClick(Sender: TObject);
begin
   if chktabelaativa.Checked  then
      vtabelaativa:='S'
   else
      vtabelaativa:='N';
end;

procedure TfrmManCodigosSistema.FormActivate(Sender: TObject);
begin
   with modulo_dados do
   begin
      statusbar1.Panels[1].text := configura_statusbar('a');
      statusbar1.Panels[3].text := configura_statusbar('a');
      statusbar1.Panels[5].text := frmprincipal.nomeserversql;
      mostra_tabelas('');
      lblempcod.text:= frmprincipal.codigo_empresa;
      lblempcod.Enabled := false;
      lblempnome.Caption := frmprincipal.nome_empresa;
      lblempcod.Refresh; lblempnome.Refresh;
      carrega_config('GEOCONFIGCOD',frmManCodigosSistema,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
      configura_grid('GEOCONFIGCOD',frmManCodigosSistema,'gridconfigcod',frmlogon.nomeusuario,gridconfigcod,modulo_dados.dtsfdquerysql);
      lblgeotabela.SetFocus;
   end;
end;

function mostra_tabelas(parametro : string) : string;
var
   i:integer;
begin
   with modulo_dados, frmprincipal,frmManCodigosSistema do
   begin
      sql:='SELECT ugcc.geotabela, ugcc.proximo_codigo, ugcc.tabela_ativa, ugcc.empcod, uge.empnome';
      sql:=sql+' FROM USER_geoapolo_configcod ugcc with(nolock)';
      sql:=sql+' INNER JOIN USER_geoapolo_empresas uge with(nolock) ON ugcc.empcod = uge.empcod';
      cria_view(sql,'vw_geoapolo_configcod','GeoApolo',frmManCodigosSistema);
      fdquerysql4.Close;
      fdquerysql4.SQL.Clear;
      fdquerysql4.SQL.Text := sql;
      if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
         begin
            if parametro = '' then
               begin
                  sql:='SELECT * FROM vw_geoapolo_configcod ORDER BY geotabela ASC'
               end
            else if parametro<> '' then
               begin
                 sql:='SELECT *';
                 sql:=sql+' FROM vw_geoapolo_configcod gacc with(nolock)';
                 sql:=sql+' WHERE '+cbocampo.Text+' LIKE :procurarpor';
                 sql:=sql+' ORDER BY '+cbocampo.Text+' ASC';
               end;
            fdquerysql4.Close;
            fdquerysql4.SQL.Clear;
            fdquerysql4.SQL.Text := sql;
            fdquerysql4.ParamByname('procurarpor').AsString :=lblprocurarpor.Text;
            if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
               begin
                  i:=0;
                  for i := 0 to fdquerysql4.Fields.count -1 do
                     begin
                        cbocampo.Items.Add(fdquerysql4.Fields[i].DisplayName);
                        cbordem.Items.Add(fdquerysql4.Fields[i].DisplayName);
                     end;
                  gridconfigcod.DataSource := dtsfdquerysql4;
                  gridconfigcod.SetFocus;
               end;
         end;
   end
end;

procedure TfrmManCodigosSistema.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
   action:=cafree;
end;

procedure TfrmManCodigosSistema.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f10 then
      spbsair.Click;
end;

procedure TfrmManCodigosSistema.gridconfigcodDblClick(Sender: TObject);
begin
   with modulo_dados, frmprincipal, frmManCodigosSistema do
   begin
      controle:='ALTERAÇÃO';
      lblgeotabela.Text:= fdquerysql4.FieldByName('geotabela').AsString;
      if fdquerysql4.FieldByName('tabela_ativa').asstring = 'S' then
         chktabelaativa.Checked := true
      else
         chktabelaativa.Checked :=false;
      lblproximocodigo.text:= fdquerysql4.FieldByName('proximo_codigo').AsString;
      lblgeotabela.SetFocus;
   end;
end;

procedure TfrmManCodigosSistema.lblprocurarporKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   with modulo_dados do
   begin
      if (key = vk_return) or (key = vk_tab) then
         begin
            if (lblprocurarpor.text <> '') and (cbocampo.Text<> '') then
               begin
                  mostra_tabelas(lblprocurarpor.Text);
                  lblgeotabela.SetFocus;
               end;
         end;
   end;
end;

procedure TfrmManCodigosSistema.popmnugravaconfigClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      grava_configuracoes_grids(frmManCodigosSistema,'GEOCONFIGCOD',gridconfigcod,'gridconfigcod',frmlogon.nomeusuario, modulo_dados.dtsfdquerysql4);
      grava_config_telabusca('GEOCONFIGCOD',cbocampo.Text,cbordem.Text,'A',frmManCodigosSistema);
   end;
end;

procedure TfrmManCodigosSistema.spblimparClick(Sender: TObject);
begin
   lblgeotabela.Clear;
   chktabelaativa.Checked:= false;
   lblproximocodigo.Clear;
   lblgeotabela.SetFocus;
end;

procedure TfrmManCodigosSistema.spbsairClick(Sender: TObject);
begin
   close;
end;

procedure TfrmManCodigosSistema.spbsalvarClick(Sender: TObject);
begin
   with modulo_dados,frmprincipal do
   begin
      if lblgeotabela.text = '' then
         begin
            messagedlg('NÃO É PERMITIDO SALVAR TABELA EM BRANCO !!!',mterror,[mbok],0);
            lblgeotabela.SetFocus;
         end;
      if lblproximocodigo.text = '' then
         begin
            lblproximocodigo.text := '0';
         end;
      if StrToInt(lblproximocodigo.Text) <0 then
         begin
            messagedlg('NÃO É POSSÍVEL INSERIR UM CÓDIGO NEGATIVO !!!',mterror,[mbok],0);
            lblproximocodigo.Text:='0';
            lblproximocodigo.SetFocus;
         end;
      resp:=messagedlg('Confirma a '+controle+' para esta tabela ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
      if resp = idyes then
         begin
            if controle = 'INCLUSÃO' then
               begin
                  messagedlg('NÃO É POSSÍVEL INCLUIR TABELAS NO GEOAPOLO A NÃO SER PELO DESENVOLVIMENTO !!!',mterror,[mbok],0);
                  lblgeotabela.SetFocus;
                  exit;
               end
            else if controle = 'ALTERAÇÃO' then
               begin
                  sql:='UPDATE user_geoapolo_configcod SET tabela_ativa = :vtabelaativa, proximo_codigo = :proximocodigo';
                  sql:=sql+' WHERE geotabela = :geotabela';
               end;
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('vtabelaativa').AsString := vtabelaativa;
            fdquerysql3.ParamByName('proximocodigo').AsString := lblproximocodigo.Text;
            fdquerysql3.parambyname('geotabela').asstring:=lblgeotabela.Text;
            if executaracao(fdquerysql3,fdbanco, true, dtsfdquerysql3) then
               begin
                  spblimpar.Click;
                  lblgeotabela.SetFocus;
                  exit;
               end;
         end
      else
         begin
            lblgeotabela.SetFocus;
            exit;
         end;
   end;
end;

end.
