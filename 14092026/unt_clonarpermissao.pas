unit unt_clonarpermissao;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, ComCtrls, StdCtrls, Buttons, Grids, DBGrids, ExtCtrls, Gauges,
  FireDAC.Stan.Error, FireDAC.UI.Intf, FireDAC.Phys.Intf, FireDAC.Stan.Def,
  FireDAC.Stan.Pool, FireDAC.Stan.Async, FireDAC.Phys, FireDAC.Phys.MySQL,
  FireDAC.Phys.MySQLDef, FireDAC.VCLUI.Wait, FireDAC.Comp.UI,
  FireDAC.Comp.Client, FireDAC.Phys.MSSQL, FireDAC.Phys.MSSQLDef,
  FireDAC.Stan.Param, FireDAC.DatS, FireDAC.DApt.Intf, FireDAC.DApt,
  FireDAC.Comp.DataSet,System.RegularExpressions, Data.DB, System.IOUtils;


type
  Tfrmclonarpermissao = class(TForm)
    StatusBar1: TStatusBar;
    Panel1: TPanel;
    spbdesligar: TSpeedButton;
    spblimpar: TSpeedButton;
    spblocalizar: TSpeedButton;
    spbexcluir: TSpeedButton;
    spbretornar: TSpeedButton;
    lblmsg1: TLabel;
    SpeedButton1: TSpeedButton;
    GroupBox1: TGroupBox;
    grid_direitos: TDBGrid;
    lblusuario_origem: TLabel;
    cbouserorigem: TComboBox;
    lbluserdestino: TLabel;
    cbouserdestino: TComboBox;
    btnclonar: TBitBtn;
    Gauge1: TGauge;
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbretornarClick(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure btnclonarClick(Sender: TObject);
    procedure cbouserorigemKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cbouserdestinoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  frmclonarpermissao: Tfrmclonarpermissao;
  sql:string;
  resp:word;

function clonar_permissao_relatorios(usucodorigem : string; usucodestino: string) : string; export;
function clonar_permissao_contasfinanceiras(usucodorigem: string; usucodestino:string) : string; export;
function clonar_permissao_formularios(usucodorigem: string; usucodestino:string) : string; export;
function clonar_permissao_usuarioxcategoria(usucodorigem: string; usucodestino:string) : string; export;
function clonar_permissao_tipopagarreceber(usucodorigem: string; usucodestino:string) : string; export;
function clonar_permissao_grupousuario(usucodorigem: string; usucodestino:string) : string; export;
function clonar_permissao_favoritos(usucodorigem: string; usucodestino:string) : string; export;
function clonar_permissao_empresafilial(usucodorigem: string; usucodestino:string) : string; export;
function clonar_permissao_tourusuario(usucodorigem: string; usucodestino:string) : string; export;

implementation

uses funcoes, unt_dados;

{$R *.dfm}

procedure Tfrmclonarpermissao.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
   action:=cafree;
end;

procedure Tfrmclonarpermissao.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f10 then
      spbretornar.Click;
end;

procedure Tfrmclonarpermissao.spbretornarClick(Sender: TObject);
begin
   close;
end;

procedure Tfrmclonarpermissao.FormActivate(Sender: TObject);
begin
   with modulo_dados do
   begin
      sql:='SELECT usucod FROM usuario WHERE usustat = :ativo ORDER BY usucod ASC';
      fdquerysql.close;
      fdquerysql.sql.clear;
      fdquerysql.sql.text := sql;
      fdquerysql.parambyname('ativo').asstring := 'Ativo';
      if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
         begin
            fdquerysql.First;
            while not fdquerysql.Eof do
            begin
               cbouserorigem.Items.add(fdquerysql.fieldbyname('usucod').asstring);
               cbouserdestino.Items.Add(fdquerysql.fieldbyname('usucod').asstring);
               fdquerysql.Next;
            end;
         end;
      statusbar1.Panels[0].Text := 'Banco Alvo';
      statusbar1.Panels[1].Text := configura_statusbar('1');
      statusbar1.panels[2].Text := 'Banco GeoApolo';
      statusbar1.Panels[3].Text := statusbar1.Panels[1].Text;
      cbouserorigem.SetFocus;
   end;
end;

procedure Tfrmclonarpermissao.btnclonarClick(Sender: TObject);
begin
   if cbouserdestino.Text = '' then
      begin
         messagedlg('INFORME O USUÁRIO QUE RECEBERÁ AS PERMISSÕES !!!',mterror,[mbok],0);
         cbouserdestino.SetFocus;
         exit;
      end;
   resp:=messagedlg('Confirma a Clonagem de Permissão do usuário '+quotedstr(cbouserorigem.Text)+' para o usuário '+quotedstr(cbouserdestino.Text),mtconfirmation,[mbyes,mbno],0);
   if resp = idyes then
      begin
         gauge1.Visible := true;
         gauge1.Refresh;
         with modulo_dados do
         begin
            sql:='SELECT * FROM dir_usuario WHERE usucod = :pusucod';
            fdquerysql1.close;
            fdquerysql1.sql.clear;
            fdquerysql1.sql.text  := sql;
            fdquerysql1.parambyname('pusucod').asstring :=cbouserorigem.Text;
            if executaracao(fdquerysql1, fdbanco, false, dtsfdquerysql1) then
               begin
                  gauge1.MaxValue := fdquerysql1.RecordCount ;
                  fdquerysql1.first;
                  while not fdquerysql1.Eof do
                  begin
                      sql:='SELECT * FROM dir_usuario WHERE usucod = :pcbodestino ';
                      sql:=sql+' AND tabsistcod = :ptabsistcod ';
                      fdquerysql2.close;
                      fdquerysql2.sql.clear;
                      fdquerysql2.sql.text := sql;
                      fdquerysql2.parambyname('pcbodestino').asstring :=cbouserdestino.Text;
                      fdquerysql2.parambyname('ptabsistcod').asstring :=fdquerysql1.fieldbyname('tabsistcod').asstring;
                      if executaracao(fdquerysql2, fdbanco, false, dtsfdquerysql2) then
                         fdquerysql1.Next
                      else
                         begin
                            {INSERE O DIREITO PARA O USUÁRIO DESTINO}
                            sql:='INSERT INTO dir_usuario (TABSISTCOD, USUCOD, DIRUSUACESSO, DIRUSUINCLUI, DIRUSUEXCLUI, DIRUSUALTERA, DIRUSUCONSULTA, DIRUSUVISUALFRONT)';
                            sql:=sql+' VALUES (:ptabsistcod, :pdirusuinclui, :pdirusuacesso, :pdirusuexclui, :pdirusuconsulta, :pdirusuvisualfront)';
                            fdquerysql3.close;
                            fdquerysql3.sql.clear;
                            fdquerysql3.sql.text := sql;
                            fdquerysql3.parambyname('ptabsistcod').asstring :=fdquerysql1.fieldbyname('tabsistcod').asstring;
                            fdquerysql3.parambyname('pdirusuinclui').asstring := fdquerysql1.fieldbyname('dirusuinclui').asstring;
                            fdquerysql3.parambyname('pdirusuacesso').asstring := fdquerysql1.fieldbyname('dirusuacesso').asstring;
                            fdquerysql3.parambyname('pdirusuexclui').asstring := fdquerysql1.fieldbyname('dirusuexclui').asstring;
                            fdquerysql3.parambyname('pdirusuconsulta').asstring := fdquerysql1.fieldbyname('dirusuconsulta').asstring;
                            fdquerysql3.parambyname('pdirusuvisualfront').asstring := fdquerysql1.fieldbyname('dirusuvisualfront').asstring;
                            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                               begin
                                  fdquerysql1.Next;
                                  gauge1.AddProgress(1); gauge1.Refresh;
                               end
                            else
                               begin
                                  messagedlg('PROBLEMAS NA TRANSFERÊNCIA DE DIREITOS !!!',mterror,[mbok],0);
                                  cbouserorigem.SetFocus;
                                  exit;
                               end;
                         end;
                  end;
                  clonar_permissao_relatorios(cbouserorigem.Text,cbouserdestino.text);
                  clonar_permissao_contasfinanceiras(cbouserorigem.Text,cbouserdestino.text);
                  clonar_permissao_formularios(cbouserorigem.Text,cbouserdestino.text);
                  clonar_permissao_usuarioxcategoria(cbouserorigem.Text,cbouserdestino.text);
                  clonar_permissao_tipopagarreceber(cbouserorigem.text,cbouserdestino.text);
                  clonar_permissao_grupousuario(cbouserorigem.text,cbouserdestino.text);
                  clonar_permissao_favoritos(cbouserorigem.text,cbouserdestino.text);
                  clonar_permissao_empresafilial(cbouserorigem.text,cbouserdestino.text);
                  clonar_permissao_tourusuario(cbouserorigem.Text,cbouserdestino.Text);
                  frmclonarpermissao.refresh;
                  messagedlg('CLONAGEM DE PERMISSÃO DE USUÁRIO TERMINADA !!!',mtinformation,[mbok],0);
                  gauge1.Visible := false;
               end
            else
               begin
                  messagedlg('O USUÁRIO '+quotedstr(cbouserorigem.Text)+' NÃO TEM DIREITOS NO SISTEMA ',mtwarning,[mbok],0);
                  cbouserorigem.SetFocus;
                  exit;
               end;
         end;
      end;
end;

procedure Tfrmclonarpermissao.cbouserorigemKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      cbouserdestino.SetFocus;
end;

procedure Tfrmclonarpermissao.cbouserdestinoKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      btnclonar.Click;
end;

function clonar_permissao_relatorios(usucodorigem : string; usucodestino: string) : string;
begin
   with modulo_dados, frmclonarpermissao do
   begin
      sql:='SELECT * FROM dir_rel_usuario WHERE usucod = :pusucodorigem';
      fdquerysql1.close;
      fdquerysql1.sql.clear;
      fdquerysql1.sql.text := sql;
      fdquerysql1.parambyname('pusucodorigem').asstring :=usucodorigem;
      if executaracao(fdquerysql1, fdbanco, true, dtsfdquerysql1) then
         begin
            gauge1.Visible := true;
            gauge1.MaxValue := fdquerysql1.RecordCount ;
            while not fdquerysql1.Eof do
            begin
               sql:='SELECT * FROM dir_rel_usuario WHERE usucod = :pusucoddestino  and relcod = :prelcod';
               fdquerysql2.close;
               fdquerysql2.sql.clear;
               fdquerysql2.sql.text:=sql;
               fdquerysql2.parambyname('pusucoddestino').asstring :=cbouserdestino.Text;
               fdquerysql2.parambyname('prelcod').asstring :=fdquerysql1.fieldbyname('relcod').asstring;
               if executaracao(fdquerysql2, fdbanco, false, dtsfdquerysql2) then
                  begin
                     sql:='INSERT INTO dir_rel_usuario (relcod, usucod) ';
                     sql:=sql+' VALUES (:prelcod, :pusucodestino)';
                     fdquerysql3.close;
                     fdquerysql3.sql.clear;
                     fdquerysql3.sql.text := sql;
                     fdquerysql3.parambyname('prelcod').asstring:=fdquerysql1.fieldbyname('relcod').asstring;
                     fdquerysql3.parambyname('pusucodestino').asstring := usucodestino;
                     if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                        begin
                           gauge1.AddProgress(1);
                           gauge1.Refresh;
                           fdquerysql1.Next;
                        end
                     else
                        begin
                           messagedlg('PROBLEMAS AO CLONAR PERMISSÃO DE RELATÓRIOS !!!',mterror,[mbok],0);
                           exit;
                        end;
                  end
               else
                  fdquerysql1.Next;
            end;
         end;
   end;
end;

function clonar_permissao_contasfinanceiras(usucodorigem: string; usucodestino:string) : string;
begin
   with modulo_dados, frmclonarpermissao do
   begin
      sql:='SELECT * FROM usuario_conta_fin WHERE usucod = :pusucodorigem';
      fdquerysql.close;
      fdquerysql.sql.clear;
      fdquerysql.sql.text := sql;
      fdquerysql.parambyname('pusucodorigem').asstring := usucodestino;
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
            gauge1.Visible := true;
            gauge1.MaxValue:=fdquerysql.RecordCount ;
            while not fdquerysql.Eof do
            begin
               sql:='SELECT * FROM usuario_conta_fin WHERE usucod = :pusucodestino';
               sql:=sql+' AND contafincod = :pcontafincod';
               fdquerysql1.close;
               fdquerysql1.sql.clear;
               fdquerysql1.sql.text := sql;
               fdquerysql1.parambyname('pusucodestino').asstring :=usucodestino;
               fdquerysql1.parambyname('pcontafincod').asstring := fdquerysql.fieldbyname('contafincod').AsString;
               if executaracao(fdquerysql1, fdbanco, true, dtsfdquerysql1) then
                  begin
                     sql:='INSERT INTO usuario_conta_fin (contafincod, usucod) ';
                     sql:=sql+' VALUES (:pcontafincod, :pusucodestino)';
                     fdquerysql3.close;
                     fdquerysql3.sql.clear;
                     fdquerysql3.sql.text := sql;
                     fdquerysql3.parambyname('pcontafincod').asstring := fdquerysql.fieldbyname('contafincod').AsString;
                     fdquerysql3.parambyname('pusucodestino').asstring := usucodestino;
                     if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                        begin
                           gauge1.AddProgress(1); gauge1.Refresh;
                           fdquerysql.Next;
                        end
                     else
                        begin
                           messagedlg('PROBLEMAS AO CLONAR PERMISSÃO DE CONTAS FINANCEIRAS !!!',mterror,[mbok],0);
                           exit;
                        end;
                  end
               else
                  begin
                     fdquerysql.next;
                  end;
          end;
      end;
   end;
end;

function clonar_permissao_formularios(usucodorigem: string; usucodestino:string) : string;
begin
   with modulo_dados, frmclonarpermissao do
   begin
      sql:='SELECT * FROM ctrl_forms WHERE usucod = :pusucodorigem';
      fdquerysql.close;
      fdquerysql.sql.clear;
      fdquerysql.sql.text := sql;
      fdquerysql.parambyname('pusucodorigem').asstring := usucodorigem;
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
            gauge1.Visible := true;
            gauge1.MaxValue:=fdquerysql.RecordCount ;
            while not fdquerysql.Eof do
            begin
               sql:='SELECT * FROM ctrl_forms WHERE usucod = :pusucod';
               sql:=sql+' AND tabsistcod = :ptabsist';
               fdquerysql1.Close;
               fdquerysql1.SQL.clear;
               fdquerysql1.SQL.Text := sql;
               fdquerysql1.ParamByName('pusucod').AsString :=usucodestino;
               fdquerysql1.ParamByName('ptabsist').AsString :=fdquerysql.fieldbyname('tabsistcod').AsString;
               if executaracao(fdquerysql1, fdbanco, false, dtsfdquerysql1) then
                  begin
                     sql:='INSERT INTO ctrl_forms (empcod, tabsistcod, usucod, ctrlformsnome) ';
                     sql:=sql+' VALUES (:pempcod, :ptabsistcod, :pctrlformsnome)';
                     fdquerysql3.close;
                     fdquerysql3.sql.clear;
                     fdquerysql3.sql.text := sql;
                     fdquerysql3.parambyname('pempcod').asstring :=fdquerysql.fieldbyname('empcod').AsString;
                     fdquerysql3.parambyname('ptabsistcod').asstring :=fdquerysql.fieldbyname('tabsistcod').AsString;
                     fdquerysql3.parambyname('pusucodestino').asstring := usucodestino;
                     fdquerysql3.parambyname('pctrlformsnome').asstring :=fdquerysql.fieldbyname('ctrlformsnome').AsString;
                     if executaracao(fdquerysql3, fdbanco, false, dtsfdquerysql3) then
                        begin
                           gauge1.AddProgress(1); gauge1.Refresh;
                           fdquerysql.Next;
                        end
                     else
                        begin
                           messagedlg('PROBLEMAS AO CLONAR PERMISSÃO DE FORMULÁRIOS !!!',mterror,[mbok],0);
                           exit;
                        end;
                     fdquerysql1.next;
                  end
               else
                  begin
                     sql:='UPDATE ctrl_forms SET ctrlformsnome = :pctrlformsnome';
                     sql:=sql+' WHERE empcod = :pempcod';
                     sql:=sql+' and tabsistcod = :ptabsistcod';
                     sql:=sql+' and usucod = :pusucodestino';
                     fdquerysql3.close;
                     fdquerysql3.sql.clear;
                     fdquerysql3.sql.text := sql;
                     fdquerysql3.parambyname('pctrlformsnome').asstring := fdquerysql.fieldbyname('ctrlformsnome').AsString;
                     fdquerysql3.parambyname('pempcod').asstring := fdquerysql.fieldbyname('empcod').AsString;
                     fdquerysql3.parambyname('ptabsistcod').asstring:=fdquerysql.fieldbyname('tabsistcod').AsString;
                     fdquerysql3.parambyname('pusucodestino').asstring := usucodestino;
                     if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                        begin
                        end;
                     fdquerysql.next;
                  end;
            end;
         end;
      end;
end;

function clonar_permissao_usuarioxcategoria(usucodorigem: string; usucodestino:string) : string;
begin
   with modulo_dados, frmclonarpermissao do
   begin
      // ABAIXO FAZ A RELAÇÃO DO USUÁRIO COM A CATEGORIA
      sql:='SELECT * FROM usuario_categ WHERE usucod = :pusucodorigem';
      fdquerysql.close;
      fdquerysql.sql.clear;
      fdquerysql.sql.text := sql;
      fdquerysql.parambyname('pusucodorigem').asstring:=usucodorigem;
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
            fdquerysql.First;
            gauge1.Visible := true;
            gauge1.MaxValue:=fdquerysql.RecordCount;
            while not fdquerysql.eof do
            begin
               // EFETUAR BUSCA PARA SABER SE O USUÁRIO DE DESTINO JÁ TEM PERMISSÃO NA CATEGORIA
               sql:='SELECT * FROM usuario_categ WHERE usucod = :pusucodestino and categcodestr = :pcategcodestr';
               fdquerysql5.close;
               fdquerysql5.sql.clear;
               fdquerysql5.sql.text := sql;
               fdquerysql5.parambyname('pusucodestino').asstring := usucodestino;
               fdquerysql5.parambyname('pcategcodestr').asstring :=fdquerysql.fieldbyname('categcodestr').asstring;
               if executaracao(fdquerysql5, fdbanco, true, dtsfdquerysql5) then
                  begin
                     sql:='INSERT INTO usuario_categ (usucod, categcodestr, usucategtodasent) ';
                     sql:=sql+' VALUES (:pusucodestino, :pcategcodestr, :pusucategtodasent)';
                     fdquerysql3.close;
                     fdquerysql3.sql.text := sql;
                     fdquerysql3.parambyname('pusucodestino').asstring :=usucodestino;
                     fdquerysql3.parambyname('pcategcodestr').asstring :=fdquerysql.fieldbyname('categcodestr').AsString;
                     fdquerysql3.parambyname('pusucategtodasent').asstring := 'Sim';
                     if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                        begin
                        end
                     else
                        begin
                           messagedlg('PROBLEMAS AO CLONAR PERMISSÃO DE USUARIOS X CATEGORIA !!!',mterror,[mbok],0);
                           exit;
                        end;
                  end;
               gauge1.addprogress(1); gauge1.refresh;
               fdquerysql.next;
            end;
         end;
      gauge1.Visible := false;
      // ABAIXO FAZ A RELAÇÃO DO USUÁRIO COM AS ENTIDADES DE CADA CATEGORIA
      sql:='SELECT substring(categcodestr,1,3) as categ';
      sql:=sql+' FROM usuario_categ';
      sql:=sql+' WHERE usucod = :pusucodorigem';
      sql:=sql+' GROUP BY substring(categcodestr,1,3)';
      fdquerysql.close;
      fdquerysql.sql.clear;
      fdquerysql.sql.text := sql;
      fdquerysql.parambyname('pusucodorigem').asstring:= usucodorigem;
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
            fdquerysql.First;
            gauge1.visible:=true;
            gauge1.MaxValue := fdquerysql.RecordCount ;
            while not fdquerysql.Eof do
            begin
               sql:='INSERT INTO USUARIO_ENT (USUCOD, ENTCOD)';
               sql:=sql+'  SELECT distinct :pusucodestino, ENT_CATEG.ENTCOD';
               sql:=sql+'  FROM ENT_CATEG';
               sql:=sql+'  WHERE ENT_CATEG.CATEGCODESTR like :pcateg%';
               sql:=sql+' AND 0 = (SELECT count(1) FROM USUARIO_ENT A';
               sql:=sql+'        WHERE A.USUCOD = :pusucodestino  and A.ENTCOD = ENT_CATEG.ENTCOD)';
               fdquerysql3.close;
               fdquerysql3.sql.clear;
               fdquerysql3.sql.text := sql;
               fdquerysql3.parambyname('pusucodestino').asstring := usucodestino;
               fdquerysql3.parambyname('pcateg').asstring := fdquerysql.fieldbyname('categ').AsString;
               fdquerysql3.parambyname('pusucodestino').asstring :=usucodestino;
               if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                  begin
                     gauge1.AddProgress(1); gauge1.Refresh;
                     fdquerysql.Next;
                  end
               else
                  fdquerysql.Next;
            end;
      end;
   end;
end;

function clonar_permissao_tipopagarreceber(usucodorigem: string; usucodestino:string) : string;
begin
   with modulo_dados, frmclonarpermissao do
   begin
      // ABAIXO FAZ A RELAÇÃO DO USUÁRIO COM A CATEGORIA
      sql:='SELECT * FROM tipo_pag_rec_usuario WHERE tipopagreccod = :pusucodorigem';
      fdquerysql.close;
      fdquerysql.sql.clear;
      fdquerysql.sql.text := sql;
      fdquerysql.parambyname('pusucodorigem').asstring := usucodorigem;
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
            fdquerysql.First;
            gauge1.Visible := true;
            gauge1.MaxValue:=fdquerysql.RecordCount;
            while not fdquerysql.eof do
            begin
               // EFETUAR BUSCA PARA SABER SE O USUÁRIO DE DESTINO JÁ TEM PERMISSÃO NO TIPO PAGAR E RECEBER
               sql:='SELECT * FROM tipo_pag_rec_usuario WHERE usucod =:pusucodestino ';
               fdquerysql5.close;
               fdquerysql5.sql.clear;
               fdquerysql5.sql.text := sql;
               fdquerysql5.parambyname('pusucodestino').asstring := usucodestino;
               if executaracao(fdquerysql5, fdbanco, true, dtsfdquerysql5) then
                  begin
                     sql:='INSERT INTO tipo_pag_rec_usuario (tipopagreccod,usucod) ';
                     sql:=sql+' VALUES (:ptipopagreccod,:pusucodestino)';
                     fdquerysql3.close;
                     fdquerysql3.sql.clear;
                     fdquerysql3.sql.text := sql;
                     fdquerysql3.parambyname('ptipopagreccod').asstring :=fdquerysql.fieldbyname('tipopagreccod').asstring;
                     fdquerysql3.parambyname('pusucodestino').asstring := usucodestino;
                     if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                        begin
                        end
                     else
                        begin
                           messagedlg('PROBLEMAS AO CLONAR PERMISSÃO DE TIPO PAGAR E RECEBER !!!',mterror,[mbok],0);
                           exit;
                        end;
                  end;
               gauge1.addprogress(1); gauge1.refresh;
               fdquerysql.next;
            end;
         end;
      gauge1.Visible := false;
   end;
end;

function clonar_permissao_grupousuario(usucodorigem: string; usucodestino:string) : string;
begin
   with modulo_dados, frmclonarpermissao do
   begin
      // ABAIXO FAZ A RELAÇÃO DO USUÁRIO COM A CATEGORIA
      sql:='SELECT * FROM GRP_X_USUARIO WHERE usucod = :pusucodorigem';
      fdquerysql.close;
      fdquerysql.sql.clear;
      fdquerysql.sql.text := sql;
      fdquerysql.parambyname('pusucodorigem').asstring :=usucodorigem;
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
            fdquerysql.First;
            gauge1.Visible := true;
            gauge1.MaxValue:=fdquerysql.RecordCount;
            while not fdquerysql.eof do
            begin
               // EFETUAR BUSCA PARA SABER SE O USUÁRIO DE DESTINO JÁ TEM PERMISSÃO DE GRUPOS E USUÁRIOS
               sql:='SELECT * FROM GRP_X_USUARIO WHERE usucod = :pusucodestino AND grpusucod = :pgrpusucod';
               fdquerysql5.close;
               fdquerysql5.sql.clear;
               fdquerysql5.sql.text := sql;
               fdquerysql5.parambyname('pusucodestino').asstring:=  usucodestino;
               fdquerysql5.parambyname('pgrpusucod').asstring :=fdquerysql.fieldbyname('grpusucod').asstring ;
               if executaracao(fdquerysql5, fdbanco, true, dtsfdquerysql5) then
                  begin
                     sql:='INSERT INTO GRP_X_USUARIO (grpusucod,usucod, grpususuperv) ';
                     sql:=sql+' VALUES (:pgrpusucod, :pusucodestino, :pgrpususuperv)';
                     fdquerysql3.close;
                     fdquerysql3.sql.clear;
                     fdquerysql3.sql.text :=sql;
                     fdquerysql3.parambyname('pgrpusucod').asstring :=fdquerysql.fieldbyname('grpusucod').asstring;
                     fdquerysql3.parambyname('pusucodestino').asstring :=usucodestino;
                     fdquerysql3.parambyname('pgrpususuperv').asstring :=fdquerysql.fieldbyname('grpususuperv').asstring;
                     if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                        begin
                        end
                     else
                        begin
                           messagedlg('PROBLEMAS AO CLONAR PERMISSÃO DE GRUPOS X USUÁRIOS !!!',mterror,[mbok],0);
                           exit;
                        end;
                  end;
               gauge1.addprogress(1); gauge1.refresh;
               fdquerysql.next;
            end;
         end;
      gauge1.Visible := false;
   end;
end;

function clonar_permissao_favoritos(usucodorigem: string; usucodestino:string) : string;
begin
  with modulo_dados, frmclonarpermissao do
  begin
    sql:='SELECT empcod,tabsistcod,ctrlfavususistema ';
    sql:=sql+' FROM ctrl_favoritos_usu ';
    sql:=sql+' WHERE usucod = :pusucodorigem';
    fdquerysql.close;
    fdquerysql.sql.clear;
    fdquerysql.sql.text := sql;
    fdquerysql.parambyname('pusucodorigem').asstring:=usucodorigem;
    if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
     begin
         fdquerysql.First;
         gauge1.Visible := true;
         gauge1.MaxValue:=fdquerysql.RecordCount;
         while not fdquerysql.eof do
         begin
            // EFETUAR BUSCA PARA SABER SE O USUÁRIO DE DESTINO JÁ TEM PERMISSÃO DE MENU FAVORITOS
            sql:='SELECT * FROM ctrl_favoritos_usu WHERE usucod = :pusucod';
            fdquerysql5.Close;
            fdquerysql5.SQL.Clear;
            fdquerysql5.SQL.Text := sql;
            fdquerysql5.ParamByName('pusucod').AsString := usucodestino;
            if executaracao(fdquerysql5, fdbanco, false, dtsfdquerysql5) then
               begin
                  sql:='INSERT INTO ctrl_favoritos_usu (empcod,tabsistcod,usucod,ctrlfavususistema)   ';
                  sql:=sql+' VALUES (:pempcod, :ptabsistcod, :pusucod, :pctrlfavususistema)';
                  fdquerysql3.Close;
                  fdquerysql3.SQL.Clear;
                  fdquerysql3.SQL.Text := sql;
                  fdquerysql3.ParamByName('pempcod').AsString := fdquerysql.FieldByName('empcod').AsString;
                  fdquerysql3.ParamByName('ptabsistcod').AsString := fdquerysql.FieldByName('tabsistcod').AsString ;
                  fdquerysql3.ParamByName('pusucod').AsString := usucodestino;
                  fdquerysql3.ParamByName('pcgtrlfavususistema').AsString :=fdquerysql.FieldByName('ctrlfavususistema').AsString;
                  if executaracao(fdquerysql3, fdbanco, false, dtsfdquerysql3) then
                    begin
                    end
                  else
                    begin
                      messagedlg('PROBLEMAS AO CLONAR PERMISSÃO DE GRUPOS X USUÁRIOS !!!',mterror,[mbok],0);
                      exit;
                    end;
               end;
            gauge1.addprogress(1); gauge1.refresh;
            fdquerysql.next;
         end;
      gauge1.Visible := false;
     end;
  end;
end;

function clonar_permissao_tourusuario(usucodorigem: string; usucodestino:string) : string;
begin
  with modulo_dados, frmclonarpermissao do
  begin
    sql:='SELECT idtour, usucod FROM tour_usuario WHERE usucod = :pusucodorigem';
    fdquerysql.Close;
    fdquerysql.SQL.Clear;
    fdquerysql.SQL.Text := sql;
    fdquerysql.ParamByName('pusucodorigem').AsString := usucodorigem;
    if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
       begin
          fdquerysql.First;
          gauge1.Visible := true;
          fdquerysql.FetchAll;
          gauge1.MaxValue:=fdquerysql.RecordCount;
          while not fdquerysql.eof do
          begin
             // EFETUAR BUSCA PARA SABER SE O USUÁRIO DE DESTINO JÁ TEM PERMISSÃO DE MENU FAVORITOS
             sql:='SELECT idtour,usucod FROM tour_usuario WHERE usucod = :pusucodestino';
             fdquerysql5.Close;
             fdquerysql5.SQL.Clear;
             fdquerysql5.SQL.Text := sql;
             fdquerysql5.ParamByName('pusucodestino').AsString := usucodestino;
             if executaracao(fdquerysql5, fdbanco, false, dtsfdquerysql5) then
                begin
                   sql:='INSERT INTO tour_usuario (idtour,usucod';
                   sql:=sql+' VALUES (:pidtour, :pusucod)';
                   fdquerysql3.Close;
                   fdquerysql3.SQL.Clear;
                   fdquerysql3.SQL.Text := sql;
                   fdquerysql3.ParamByName('pidtour').AsString := fdquerysql.FieldByName('idtour').AsString;
                   fdquerysql3.ParamByName('pusucod').AsString := fdquerysql.FieldByName('usucod').AsString;
                   if executaracao(fdquerysql3, fdbanco, false, dtsfdquerysql3) then
                      begin
                      end
                   else
                      begin
                         messagedlg('PROBLEMAS AO CLONAR PERMISSÃO DE GRUPOS X USUÁRIOS !!!',mterror,[mbok],0);
                         exit;
                      end;
                  end;
               gauge1.addprogress(1); gauge1.refresh;
               fdquerysql.next;
            end;
         end;
      gauge1.Visible := false;
   end;
end;

function clonar_permissao_empresafilial(usucodorigem, usucodestino: string): string;
var
  QOrigem, QDestino, QInsert: TFDQuery;
  sql: string;
begin
  Result := '';
  with Modulo_Dados, frmClonarPermissao do
  begin
    // Inicializa queries
    QOrigem := TFDQuery.Create(nil);
    QDestino := TFDQuery.Create(nil);
    QInsert := TFDQuery.Create(nil);
    try
      QOrigem.Connection := fdbanco;
      QDestino.Connection := fdbanco;
      QInsert.Connection := fdbanco;
      // Busca permissões do usuário de origem
      QOrigem.SQL.Text := 'SELECT empcod, empfilusupermacessist, empfilusupermverdet FROM emp_fil_usuario WHERE usucod = :pusucod';
      QOrigem.ParamByName('pusucod').AsString := usucodorigem;
      if not executaracao(QOrigem, fdbanco, False) then
        Exit;
      if QOrigem.RecordCount > 0 then
      begin
        QOrigem.First;
        gauge1.Visible := True;
        gauge1.MaxValue := QOrigem.RecordCount;
        while not QOrigem.Eof do
        begin
          // Verifica se o usuário destino já tem permissão
          QDestino.SQL.Text :='SELECT 1 FROM emp_fil_usuario WHERE usucod = :pusucod';
          QDestino.ParamByName('pusucod').AsString := usucodestino;
          if not executaracao(QDestino, fdbanco, False) then
            Exit;
          // Caso não tenha, insere a permissão
          if QDestino.RecordCount = 0 then
          begin
            QInsert.SQL.Text := 'INSERT INTO emp_fil_usuario (empcod, usucod, empfilusupermacessist, empfilusupermverdet) ' +
              'VALUES (:pempcod, :pusucod, :pacessist, :pverdet)';
            QInsert.ParamByName('pempcod').AsString :=  QOrigem.FieldByName('empcod').AsString;
            QInsert.ParamByName('pusucod').AsString := usucodestino;
            QInsert.ParamByName('pacessist').AsString := QOrigem.FieldByName('empfilusupermacessist').AsString;
            QInsert.ParamByName('pverdet').AsString := QOrigem.FieldByName('empfilusupermverdet').AsString;
            if not executaracao(QInsert, fdbanco, True) then
              begin
                MessageDlg('Problemas ao clonar permissão de grupos x usuários!',mtError, [mbOK], 0);
                Exit;
              end;
          end;
          gauge1.AddProgress(1);
          gauge1.Refresh;
          QOrigem.Next;
        end;
      end;
      gauge1.Visible := False;
      Result := 'Clonagem concluída com sucesso.';
    finally
      QOrigem.Free;
      QDestino.Free;
      QInsert.Free;
    end;
  end;
end;

end.
