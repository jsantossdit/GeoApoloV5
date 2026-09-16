unit unt_cadtipocampanha;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, Grids, DBGrids, StdCtrls, ExtCtrls, Buttons, ComCtrls, Data.DB,
  Vcl.Imaging.jpeg, Vcl.Mask;

type
  Tfrmtipocampanha = class(TForm)
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spblimpar: TSpeedButton;
    spbdeletar: TSpeedButton;
    spbabreos: TSpeedButton;
    spbretornar: TSpeedButton;
    lblmsg1: TLabel;
    StatusBar1: TStatusBar;
    GroupBox1: TGroupBox;
    lblcodtipocamp: TLabeledEdit;
    lbldescricaotipocamp: TLabeledEdit;
    gridtipocampanha: TDBGrid;
    Panel1: TPanel;
    chkativadesativa: TCheckBox;
    chkgeracampanha: TCheckBox;
    procedure spbretornarClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure FormActivate(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure lbldescricaotipocampKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbsalvarClick(Sender: TObject);
    procedure gridtipocampanhaDblClick(Sender: TObject);
    procedure gridtipocampanhaKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure chkativadesativaClick(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  frmtipocampanha: Tfrmtipocampanha;
  ativado,sql,geracampanha,controle,baseparacampanha,integraentidadesapolo:string;
  resp:word;

function mostra_tipos_cadastrados(baseparacamp : string) : string; export;
  
implementation

uses funcoes, unt_dados, unt_principal;

{$R *.dfm}

procedure Tfrmtipocampanha.spbretornarClick(Sender: TObject);
begin
   close;
end;

procedure Tfrmtipocampanha.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
   close;
end;

procedure Tfrmtipocampanha.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f10 then
      spbretornar.Click;
end;

procedure Tfrmtipocampanha.chkativadesativaClick(Sender: TObject);
begin
   if chkativadesativa.Checked then
      ativado:='S'
   else
      ativado:='N';
end;

procedure Tfrmtipocampanha.FormActivate(Sender: TObject);
begin
   statusbar1.Panels[1].Text := configura_statusbar('a');
   statusbar1.panels[3].text := configura_statusbar('a');
   statusbar1.Panels[5].Text:= frmprincipal.nomeserversql;
   statusbar1.refresh;
   controle:='INCLUSÃO';
   with modulo_dados do
   begin
      sql:='SELECT gera_camp_baseapolo, integra_entidades_apolo FROM USER_geoapolo_configuracoes';
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := sql;
      if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
         begin
            if fdquerysql.FieldByName('gera_camp_baseapolo').Asstring = 'S' then
               begin
                  baseparacampanha:='Apolo';
                  integraentidadesapolo:=fdquerysql.FieldByName('integra_entidades_apolo').AsString;
               end
            else if fdquerysql.FieldByName('gera_camp_baseapolo').asstring = 'N' then
               begin
                  baseparacampanha:='GeoApolo';
                  integraentidadesapolo:=fdquerysql.FieldByName('integra_entidades_apolo').AsString;
               end;
         end;
      lblcodtipocamp.text:=geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_tipocampanha','Sim');
      lblcodtipocamp.Refresh;
      mostra_tipos_cadastrados(baseparacampanha);
      lbldescricaotipocamp.SetFocus;
   end;
end;

procedure Tfrmtipocampanha.spblimparClick(Sender: TObject);
begin
   lblcodtipocamp.Clear; lbldescricaotipocamp.Clear; chkativadesativa.Checked:=false; chkgeracampanha.Checked:=false;
   groupbox1.Refresh;
   lbldescricaotipocamp.SetFocus;
end;

procedure Tfrmtipocampanha.lbldescricaotipocampKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      begin
         chkativadesativa.Checked:=true;
         spbsalvar.click;
      end;
end;

procedure Tfrmtipocampanha.spbsalvarClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      if lbldescricaotipocamp.Text = '' then
         begin
            messagedlg('INFORME A DESCRIÇÃO DO TIPO DE CAMPANHA !!!',mterror,[mbok],0);
            lbldescricaotipocamp.SetFocus;
            exit;
         end;
      //
      if chkgeracampanha.Checked  then
         geracampanha:='S'
      else
         geracampanha:='N';
      //
      resp:=messagedlg('Confirma a '+controle+' para este Tipo de Campanha (Y/N)',mtconfirmation,[mbyes,mbno],0);
      if resp = idyes then
         begin
            if baseparacampanha = 'GeoApolo' then
               begin
                  if controle = 'INCLUSÃO' then
                     begin
                        sql:='INSERT INTO USER_geoapolo_tipocampanha(codigo_tipocampanha, descricaotipocamp,ativo,geracampanha) ';
                        sql:=sql+' VALUES (:ptipocampcod, :ptipocampnome, :ptipoativado, :ptipogeracamp)';
                     end
                  else if controle = 'ALTERAÇÃO' then
                     begin
                        sql:='UPDATE USER_geoapolo_tipocampanha SET descricaotipocamp = :ptipocampnome';
                        sql:=sql+', ativo = :pativado, geracampanha = :ptipogeracamp';
                        sql:=sql+' WHERE codigo_tipocampanha =:ptipocampcod ';
                     end;
               end
            else if baseparacampanha = 'Apolo' then
               begin
                  if controle = 'INCLUSÃO' then
                     begin
                         sql:='INSERT INTO tipo_campanha(tipocampcod, tipocampnome)';
                         sql:=sql+' VALUES (:ptipocampcod, :ptipocampnome)';
                     end
                  else if controle = 'ALTERAÇÃO' then
                     begin
                        sql:='UPDATE tipo_campanha SET tipocampnome = :ptipocampnome WHERE tipocampcod = :ptipocampcod';
                     end;

               end;
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('ptipocampcod').AsString := lblcodtipocamp.Text;
            fdquerysql3.ParamByName('ptipocampnome').AsString := lbldescricaotipocamp.text;
            if baseparacampanha = 'GeoApolo' then
               begin
                  fdquerysql3.ParamByName('ptipoativado').AsString := ativado;
                  fdquerysql3.ParamByName('ptipogeracamp').AsString := geracampanha;
               end;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  messagedlg('OPERAÇÃO DE '+controle+' PARA O TIPO DE CAMPANHA REALIZADO COM SUCESSO !!!',mtinformation,[mbok],0);
                  spblimpar.Click;
                  if controle = 'ALTERAÇÃO' then
                     lblcodtipocamp.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_tipocampanha','Não')
                  else if controle = 'INCLUSÃO' then
                     lblcodtipocamp.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_tipocampanha','Sim');
                  //
                  lblcodtipocamp.Refresh;
                  mostra_tipos_cadastrados(baseparacampanha);
                  lblcodtipocamp.text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_tipocampanha','Sim');
                  lblcodtipocamp.Refresh;
                  controle:='INCLUSÃO';
               end
            else
               begin
                  messagedlg('ERRO AO TENTAR INCLUIR UM NOVO TIPO CAMPANHA !!!',mterror,[mbok],0);
                  lbldescricaotipocamp.SetFocus;
               end;
         end
      else
         begin
            lbldescricaotipocamp.SetFocus;
            exit;
         end;
   end;
end;

function mostra_tipos_cadastrados(baseparacamp : string) : string;
begin
   if ((baseparacamp = 'Apolo') and (integraentidadesapolo = 'Mescla')) then
      sql:='SELECT * FROM tipo_campanha'
   else if (baseparacamp = 'GeoApolo') and ((integraentidadesapolo = 'Mescla') or (integraentidadesapolo = 'Não Integra')) then
      sql:='SELECT * FROM USER_geoapolo_tipocampanha ORDER BY codigo_tipocampanha ASC';
      modulo_dados.fdquerysql4.Close;
      modulo_dados.fdquerysql4.SQL.Clear;
      modulo_dados.fdquerysql4.SQL.Text := sql;
   if executaracao(modulo_dados.fdquerysql4, modulo_dados.fdbanco, true, modulo_dados.dtsfdquerysql4) then
      begin
      end;
   frmtipocampanha.gridtipocampanha.DataSource := modulo_dados.dtsfdquerysql4;
   frmtipocampanha.gridtipocampanha.Refresh;
end;

procedure Tfrmtipocampanha.gridtipocampanhaDblClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      if (baseparacampanha = 'GeoApolo') then
         begin
            lblcodtipocamp.Text := fdquerysql4.fieldbyname('codigo_tipocampanha').AsString;
            lbldescricaotipocamp.Text := fdquerysql4.fieldbyname('descricaotipocamp').asstring;
            if fdquerysql4.fieldbyname('ativo').asstring = 'S' then
               chkativadesativa.Checked:=true
            else
               chkativadesativa.Checked:=false;
            chkativadesativa.refresh;
            //
            if fdquerysql4.fieldbyname('geracampanha').AsString = 'S' then
               chkgeracampanha.Checked:=true
            else
               chkgeracampanha.Checked:=false;
            //
            frmtipocampanha.Refresh;
            lbldescricaotipocamp.SetFocus;
            controle:='ALTERAÇÃO';
         end
      else if baseparacampanha = 'Apolo' then
         begin
            lblcodtipocamp.Text := fdquerysql4.fieldbyname('tipocampcod').AsString;
            lbldescricaotipocamp.Text := fdquerysql4.fieldbyname('tipocampnome').asstring;
            if fdquerysql4.fieldbyname('ativo').asstring = 'S' then
               chkativadesativa.Checked:=true
            else
               chkativadesativa.Checked:=false;
            chkativadesativa.refresh;
            //
            if fdquerysql4.fieldbyname('geracampanha').AsString = 'S' then
               chkgeracampanha.Checked:=true
            else
               chkgeracampanha.Checked:=false;
            //
            frmtipocampanha.Refresh;
            lbldescricaotipocamp.SetFocus;
            controle:='ALTERAÇÃO';
         end;
   end;
end;

procedure Tfrmtipocampanha.gridtipocampanhaKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   with modulo_dados do
   begin
      if key = vk_delete then
         begin
            resp:=messagedlg('Confirma a exclusão deste tipo de campanha ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
            if resp = idyes then
               begin
                  if baseparacampanha = 'GeoApolo' then
                     begin
                        sql:='DELETE FROM USER_geoapolo_tipocampanha ';
                        sql:=sql+' WHERE codigo_tipocampanha = :pcodigotipocampanha';
                     end
                  else if baseparacampanha = 'Apolo' then
                     begin
                        sql:='DELETE FROM tipo_campanha WHERE tipocampcod =  :pcodigotipocampanha';
                     end;
                  fdquerysql3.Close;
                  fdquerysql3.SQL.Clear;
                  fdquerysql3.SQL.Text := sql;
                  if baseparacampanha = 'GeoApolo' then
                     fdquerysql3.ParamByName('pcodigotipocampanha').AsString :=fdquerysql4.fieldbyname('codigo_tipocampanha').asstring
                  else if baseparacampanha = 'Apolo' then
                     fdquerysql3.ParamByName('pcodigotipocampanha').AsString :=fdquerysql4.FieldByName('tipocampcod').AsString;
                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                      begin
                          messagedlg('TIPO DE CAMPANHA REMOVIDO COM SUCESSO !!!',mtinformation,[mbok],0);
                          if baseparacampanha = 'GeoApolo' then
                             lblcodtipocamp.text := geoapolo_configcod(frmprincipal.codigo_empresa,'user_geoapolo_tipocampanha','Sim');
                          lblcodtipocamp.Refresh;
                          mostra_tipos_cadastrados(baseparacampanha);
                          frmtipocampanha.Refresh; lblcodtipocamp.SetFocus;
                      end
                  else
                      begin
                          messagedlg('PROBLEMAS NA TENTATIVA DE EXCLUSÃO DO TIPO DE CAMPANHA, ELE DEVE ESTAR VINCULADO A UMA CAMPANHA REGISTRADA NO SISTEMA !!!',mterror,[mbok],0);
                          lblcodtipocamp.SetFocus;
                      end;
               end
            else
               begin
                  lbldescricaotipocamp.SetFocus;
                  exit;
               end;
         end;
   end;
end;

end.
