unit unt_grupousuario;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, ExtCtrls, ComCtrls, Buttons, Grids, DBGrids, Data.DB,
  Vcl.Mask;

type
  Tfrmgrupousuarios = class(TForm)
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spblimpar: TSpeedButton;
    spbdeletar: TSpeedButton;
    spblocalizar: TSpeedButton;
    spbretornar: TSpeedButton;
    lblmsg1: TLabel;
    StatusBar1: TStatusBar;
    GroupBox1: TGroupBox;
    lblcodigogrupo: TLabeledEdit;
    lbldescricao: TLabeledEdit;
    gridgrupos: TDBGrid;
    GroupBox2: TGroupBox;
    lblusuario: TLabel;
    cbousuarios: TComboBox;
    spbsalvagrupo: TSpeedButton;
    gridusuariosgrupo: TDBGrid;
    spbvinculo: TSpeedButton;
    procedure FormActivate(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure spbretornarClick(Sender: TObject);
    procedure FormKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lbldescricaoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbsalvagrupoClick(Sender: TObject);
    procedure spbvinculoClick(Sender: TObject);
    procedure gridgruposDblClick(Sender: TObject);
    procedure lblcodigogrupoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lbldescricaoEnter(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure gridgruposKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure gridusuariosgrupoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  frmgrupousuarios: Tfrmgrupousuarios;
  codigousuario,codigouserold,controlev,controle,sql:string;
  resp:word;
  codigogrupo,codigogrupoold:integer;

function mostragrupos : string; export;
function mostravinculos(codigo_grupo : string) : string; export;
  
implementation

uses funcoes, unt_dados, unt_logon, unt_principal;

{$R *.dfm}

procedure Tfrmgrupousuarios.FormActivate(Sender: TObject);
begin
   lblcodigogrupo.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_grupo','Sim');
   lblcodigogrupo.Refresh;
   mostragrupos;
   //mostravinculos;
   controlev:='INCLUSÃO';
   statusbar1.Panels[1].Text := configura_statusbar('a');
   // carrega combo de usuários
   with modulo_dados do
   begin
      sql:='SELECT u.usucod, u.login';
      sql:=sql+' FROM USER_geoapolo_usuarios u';
      sql:=sql+' WHERE   u.flagativo = :pflagativo';
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := sql;
      fdquerysql.ParamByName('pflagativo').AsString :='A';
      if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
         begin
            fdquerysql.First;
            while not fdquerysql.Eof do
            begin
               cbousuarios.Items.Add(fdquerysql.fieldbyname('login').asstring);
               fdquerysql.Next;
            end;
         end
      else
         begin
            messagedlg('NÃO HÁ USUÁRIOS AUTORIZADOS A UTILIZAR ESTE SISTEMA !!!',mtwarning,[mbok],0);
            exit;
         end;
      cbousuarios.Refresh;
      lbldescricao.SetFocus;
   end;
end;

function mostragrupos : string;
begin
   with modulo_dados, frmgrupousuarios do
   begin
      sql:='SELECT * FROM USER_geoapolo_grupo;';
      fdquerysql4.Close;
      fdquerysql4.SQL.Clear;
      fdquerysql4.SQL.Text := sql;
      if executaracao(fdquerysql4, fdbanco, false, dtsfdquerysql4) then
         begin
            gridgrupos.DataSource := dtsfdquerysql4;
            gridgrupos.Refresh;
         end
      else
         begin
            lbldescricao.SetFocus;
            exit;
         end;
   end;
end;

function mostravinculos(codigo_grupo : string) : string;
begin
   with modulo_dados, frmgrupousuarios do
   begin
      sql:='SELECT ugu.login as Login,ugu.usunome as Usuario,ugg.descricao,uggu.codigo_grupo,uggu.usucod';
      sql:=sql+' FROM USER_geoapolo_usuarios ugu with(nolock)';
      sql:=sql+' INNER JOIN USER_geoapolo_grupousuario uggu with(nolock) ON ugu.usucod = uggu.usucod';
      sql:=sql+' INNER JOIN user_geoapolo_grupo ugg with(nolock) ON uggu.codigo_grupo = ugg.codigo_grupo';
      sql:=sql+' WHERE ugg.codigo_grupo = :pcodigogrupo';
      sql:=sql+' AND flagativo = :pflagativo';
      fdquerysql6.Close;
      fdquerysql6.SQL.Clear;
      fdquerysql6.SQL.Text := sql;
      fdquerysql6.ParamByName('pcodigogrupo').AsString :=codigo_grupo;
      fdquerysql6.ParamByName('pflagativo').AsString :='A';
      if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
         begin
            gridusuariosgrupo.DataSource := dtsfdquerysql6;
            gridusuariosgrupo.Refresh;
         end
      else
         begin
            lbldescricao.SetFocus;
            exit;
         end;
   end;
end;

procedure Tfrmgrupousuarios.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
   action:=cafree;
end;

procedure Tfrmgrupousuarios.spbretornarClick(Sender: TObject);
begin
   close;
end;

procedure Tfrmgrupousuarios.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f10 then
      spbretornar.Click ;
end;

procedure Tfrmgrupousuarios.lbldescricaoKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      spbsalvagrupo.Click;
end;

procedure Tfrmgrupousuarios.spbsalvagrupoClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      if trim(lbldescricao.Text) = '' then
         begin
            messagedlg('NÃO É PERMITIDO GRAVAR UM GRUPO SEM DESCRIÇÃO !!!',mtwarning,[mbok],0);
            lbldescricao.SetFocus;
            exit;
         end;
      // VERIFICA SE NÃO HÁ NENHUM REGISTRO COM A MESMA DESCRIÇÃO DO GRUPO A SER INCLUIDO OU ALTERADO
      sql:='SELECT descricao FROM USER_geoapolo_grupo WHERE descricao = :pdescricao';
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := sql;
      fdquerysql.ParamByName('pdescricao').AsString :=lbldescricao.Text;
      if (executaracao(fdquerysql, fdbanco, false, dtsfdquerysql))  then
        if (controle = 'INCLUSÃO') then
           begin
              messagedlg('JÁ EXISTE UM GRUPO COM ESTE NOME, FAVOR ALTERAR !!!',mtwarning,[mbok],0);
              lbldescricao.SetFocus;
              exit;
           end;
      //
      if lblcodigogrupo.Text = '' then
         begin
            lblcodigogrupo.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_grupo','Sim');
            lblcodigogrupo.Refresh;
         end;
      //
      resp:=messagedlg('Confirma a '+controle+' deste Grupo ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
      if resp = idyes then
         begin
            if controlev = 'INCLUSÃO' then
               begin
                  sql:='INSERT INTO USER_geoapolo_grupo (codigo_grupo, descricao) ';
                  sql:=sql+' VALUES (:pcodigogrupo, pdescricao)'; //'++', '+quotedstr()+');';
               end
            else if controlev = 'ALTERAÇÃO' then
               begin
                  sql:='UPDATE USER_geoapolo_grupo SET descricao =:pdescricao ';
                  sql:=sql+' WHERE codigo_grupo = :pcodigogrupo';
               end;
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('pcodigogrupo').AsString := lblcodigogrupo.text;
            fdquerysql3.ParamByName('pdescricao').AsString:=  lbldescricao.Text;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  messagedlg(controlev+' EFETUADA COM SUCESSO !!!',mtinformation,[mbok],0);
                  lbldescricao.Clear;
                  controlev:='INCLUSÃO';
                  lblcodigogrupo.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_grupo','S');
                  mostragrupos;
                  cbousuarios.SetFocus;
                  exit;
               end;
         end
      else
         begin
            lbldescricao.SetFocus;
            exit;
         end;
   end;
end;

procedure Tfrmgrupousuarios.spbvinculoClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      if lbldescricao.Text = '' then
         begin
            messagedlg('SELECIONE O GRUPO PARA VINCULAR O USUÁRIO !!!',mtwarning,[mbok],0);
            lblcodigogrupo.SetFocus;
            exit;
         end;
      //
      if trim(cbousuarios.Text) = '' then
         begin
            messagedlg('USUÁRIO NÃO FOI SELECIONADO !!!',mterror,[mbok],0);
            cbousuarios.SetFocus;
            exit;
         end
      else
         begin
            sql:='SELECT usucod FROM USER_geoapolo_usuarios WHERE login = :pcbousuarios';
            fdquerysql1.Close;
            fdquerysql1.SQL.Clear;
            fdquerysql1.SQL.Text := sql;
            fdquerysql1.ParamByName('pcbusuarios').AsString := cbousuarios.Text;
            if executaracao(fdquerysql1, fdbanco, false, dtsfdquerysql1) then
               codigousuario:=fdquerysql1.fieldbyname('usucod').asstring
            else
               begin
                  messagedlg('PROBLEMAS PARA ENCONTRAR O CÓDIGO DO USUÁRIO !!!',mterror,[mbok],0);
                  cbousuarios.SetFocus;
                  exit;
               end;
         end;
      // ROTINA ABAIXO VERIFICA SE O USUÁRIO JÁ ESTÁ VINCULADO AO GRUPO
      sql:='SELECT * FROM USER_geoapolo_grupousuario WHERE codigo_grupo = :pcodigogrupo';
      sql:=sql+' AND usucod = :pcodigousuario';
      fdquerysql1.Close;
      fdquerysql1.SQL.Clear;
      fdquerysql1.SQL.Text := sql;
      fdquerysql1.ParamByName('pcodigogrupo').AsString :=lblcodigogrupo.Text;
      fdquerysql1.ParamByName('pcodigousuario').AsString :=codigousuario;
      if executaracao(fdquerysql1, fdbanco, false, dtsfdquerysql1) then
         begin
            messagedlg('ESTE USUÁRIO JÁ ESTÁ VINCULADO A ESTE GRUPO, PARA ALTERAR DÊ UM DUPLO CLICK NO GRID ABAIXO !!!!',mtwarning,[mbok],0);
            controlev:='ALTERAÇÃO';
            cbousuarios.SetFocus;
            exit;
         end
      else
         begin
            controlev:='INCLUSÃO';
         end;
      resp:=messagedlg('Confirma o Vinculo deste usuário com o grupo acima ? (Y/N):',mtconfirmation,[mbyes,mbno],0);
      if resp = idyes then
         begin
            if controlev = 'INCLUSÃO' then
               begin
                  sql:='INSERT INTO USER_geoapolo_grupousuario (codigo_grupo,usucod) ';
                  SQL:=SQL+' VALUES (:pcodigogrupo, :pcodigousuario)';
               end
            else if controlev = 'ALTERAÇÃO' then
               begin
                  sql:='UPDATE USER_geoapolo_grupousuario SET codigo_grupo = :pcodigogrupo ';
                  sql:=sql+', usucod = :pcodigousuario';
                  sql:=sql+' WHERE codigo_grupo = :pcodigogrupo' ;
                  sql:=sql+' AND usucod  = :pusucodigold';
               end;
           fdquerysql3.close;
           fdquerysql3.SQL.Clear;
           fdquerysql3.SQL.Text := sql;
           fdquerysql3.ParamByName('pcodigogrupo').AsString :=lblcodigogrupo.Text;
           fdquerysql3.ParamByName('pcodigousuario').AsString :=codigousuario;
           fdquerysql3.parambyname('pcodigogrupoold').asstring := codigousuario;
           fdquerysql3.ParamByName('pusucodigoold').AsString := lblcodigogrupo.Text ;
           if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
              begin
                  messagedlg('VINCULO ATUALIZADO COM SUCESSO !!!',mtinformation,[mbok],0);
                  cbousuarios.ItemIndex := -1; cbousuarios.SetFocus;
                  mostravinculos(lblcodigogrupo.Text);
                  controlev:='INCLUSÃO';
               end;
         end
      else
         begin
            exit;
         end;
   end;
end;

procedure Tfrmgrupousuarios.gridgruposDblClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      spblimpar.Click;
      controlev:='ALTERAÇÃO';
      lblcodigogrupo.Text := fdquerysql4.fieldbyname('codigo_grupo').asstring;
      lbldescricao.Text := fdquerysql4.fieldbyname('descricao').asstring;
      mostravinculos(lblcodigogrupo.Text);
      lbldescricao.Refresh;
      lbldescricao.SetFocus;
   end;
end;

procedure Tfrmgrupousuarios.lblcodigogrupoKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lbldescricao.SetFocus;
end;

procedure Tfrmgrupousuarios.lbldescricaoEnter(Sender: TObject);
begin
   with modulo_dados do
   begin
      if trim(lblcodigogrupo.Text) <> '' then
         begin
            sql:='SELECT descricao FROM USER_geoapolo_grupo WHERE codigo_grupo = :pcodigogrupo';
            fdquerysql1.Close;
            fdquerysql1.sql.clear;
            fdquerysql1.sql.Text := sql;
            fdquerysql1.ParamByName('pcodigogrupo').AsString :=lblcodigogrupo.Text;
            if executaracao(fdquerysql1, fdbanco, true, dtsfdquerysql1) then
               begin
                  lbldescricao.Text := fdquerysql1.fieldbyname('descricao').asstring;
                  lbldescricao.Refresh; lbldescricao.SetFocus;
                  exit;
               end;
         end;
   end;
end;

procedure Tfrmgrupousuarios.spblimparClick(Sender: TObject);
begin
   lblcodigogrupo.Clear; lbldescricao.Clear;
   controle:='INCLUSÃO'; controlev:='INCLUSÃO';
   lblcodigogrupo.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_grupo','S');
   lbldescricao.SetFocus;
end;

procedure Tfrmgrupousuarios.gridgruposKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   with modulo_dados do
   begin
      if key = vk_delete then
         begin
            resp:=messagedlg('Confirma a remoção deste grupo ?, lembre-se, caso haja algum usuário vinculado a ele, a remoção não será permitida (Y/N)',mtconfirmation,[mbyes,mbno],0);
            if resp = idyes then
               begin
                  sql:='DELETE FROM USER_geoapolo_grupo WHERE codigo_grupo = :pcodigogrupo';
                  fdquerysql3.Close;
                  fdquerysql3.SQL.Clear;
                  fdquerysql3.SQL.Text := sql;
                  fdquerysql3.ParamByName('pcodigogrupo').AsString := fdquerysql4.fieldbyname('codigo_grupo').asstring;
                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                     begin
                        messagedlg('GRUPO REMOVIDO COM SUCESSO !!!',mtinformation,[mbok],0);
                        spblimpar.Click;
                        lblcodigogrupo.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_grupo','Sim');
                        controlev:='INCLUSÃO';
                        mostragrupos;
                        lbldescricao.SetFocus;
                     end
                  else
                     begin
                        sql:='DELETE FROM USER_geoapolo_grupousuario ';
                        sql:=sql+' WHERE codigo_grupo in (select codigo_grupo FROM geoapolo_grupo WHERE descricao = :pdescricao)';
                        fdquerysql3.Close;
                        fdquerysql3.SQL.Clear;
                        fdquerysql3.SQL.Text := sql;
                        fdquerysql3.parambyname('pdescricao').asstring :=lbldescricao.text;
                        if executaracao(fdquerysql3, fdbanco, false, dtsfdquerysql3) then
                           begin
                              sql:='DELETE FROM USER_geoapolo_grupobjeto WHERE codigo_grupo in (select codigo_grupo FROM USER_geoapolo_grupo WHERE descricao = :pdescricao)';
                              fdquerysql3.Close;
                              fdquerysql3.SQL.Clear;
                              fdquerysql3.SQL.Text := sql;
                              fdquerysql3.ParamByName('pdescricao').AsString := lbldescricao.Text;
                              if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                                 begin
                                    sql:='DELETE FROM USER_geoapolo_grupo WHERE codigo_grupo = :pcodigogrupo';
                                    fdquerysql3.Close;
                                    fdquerysql3.SQL.Clear;
                                    fdquerysql3.SQL.Text := sql;
                                    fdquerysql3.ParamByName('pcodiggrupo').AsString := fdquerysql4.fieldbyname('codigo_grupo').asstring;
                                    if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                                       begin
                                          messagedlg('GRUPO REMOVIDO COM SUCESSO !!!',mtinformation,[mbok],0);
                                          spblimpar.Click;
                                          lblcodigogrupo.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_grupo','Sim');
                                          mostragrupos;
                                          lbldescricao.SetFocus;
                                       end;
                                 end;
                           end
                        else
                           begin
                              messagedlg('PROBLEMAS AO REMOVER O GRUPO, VERIFIQUE SE NÃO HÁ USUÁRIOS VINCULADOS A ELE !!!',mterror,[mbok],0);
                              lbldescricao.SetFocus;
                              spblimpar.Click;
                              mostragrupos;
                              exit;
                           end;
                     end;
               end
            else
               begin
                  lbldescricao.SetFocus;
                  exit;
               end;
         end;
   end;
end;

procedure Tfrmgrupousuarios.gridusuariosgrupoKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   with modulo_dados do
   begin
      if key = vk_delete then
         begin
            resp:=messagedlg('Confirma a remoção deste usuário do grupo atual ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
            if resp = idyes then
               begin
                  sql:='DELETE FROM USER_geoapolo_grupousuario WHERE usucod = :pusucod AND codigo_grupo = :pcodigogrupo';
                  fdquerysql3.Close;
                  fdquerysql3.SQL.Clear;
                  fdquerysql3.SQL.text := sql;
                  fdquerysql3.ParamByName('pusucod').AsString := fdquerysql6.fieldbyname('usucod').asstring;
                  fdquerysql3.ParamByName('pcodigogrupo').AsString := fdquerysql6.fieldbyname('codigo_grupo').asstring;
                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                     begin
                        messagedlg('USUÁRIO REMOVIDO COM SUCESSO !!!',mtinformation,[mbok],0);
                        spblimpar.Click;
                        lblcodigogrupo.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'geoapolo_grupo','Não');
                        mostragrupos;
                        mostravinculos(lblcodigogrupo.Text);
                     end
                  else
                     begin
                        sql:='DELETE FROM USER_geoapolo_grupobjeto ';
                        sql:=sql+' WHERE codigo_grupo = :pcodigogrupo';
                        fdquerysql3.Close;
                        fdquerysql3.SQL.Clear;
                        fdquerysql3.SQL.Text := sql;
                        fdquerysql3.ParamByName('pcodigogrupo').AsString := lblcodigogrupo.Text;
                        if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                           begin
                              messagedlg('USUÁRIO REMOVIDO COM SUCESSO !!!',mtinformation,[mbok],0);
                              spblimpar.Click;
                              lblcodigogrupo.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'user_geoapolo_grupo','Não');
                              mostragrupos;
                              mostravinculos(lblcodigogrupo.Text);
                           end
                        else
                           begin
                              messagedlg('PROBLEMAS AO REMOVER ESTE USUÁRIO DO GRUPO ACIMA !!!',mterror,[mbok],0);
                              lbldescricao.SetFocus;
                              exit;
                           end;
                     end;
               end
            else
               begin
                  cbousuarios.SetFocus;
                  exit;
               end;
         end;
   end;
end;

end.
