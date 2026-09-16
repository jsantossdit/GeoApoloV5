unit unt_cadcategorias;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, ComCtrls, StdCtrls, Buttons, ExtCtrls, XPMan, Grids, DBGrids, Data.DB,
  Vcl.Mask;

type
  Tfrmcadcategoria = class(TForm)
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spbligacoes: TSpeedButton;
    spbsair: TSpeedButton;
    spblimpar: TSpeedButton;
    lblsair: TLabel;
    StatusBar1: TStatusBar;
    GroupBox1: TGroupBox;
    lblcategcodestr: TLabeledEdit;
    lblcodcategalt: TLabeledEdit;
    lblcategnome: TLabeledEdit;
    GroupBox2: TGroupBox;
    gridusuarios: TDBGrid;
    gridusuariosrelac: TDBGrid;
    lblusuariosdisp: TLabel;
    lblusuariosrelac: TLabel;
    gridcategorias: TDBGrid;
    chkgrupo: TCheckBox;
    spbliga1: TSpeedButton;
    spbligatodos: TSpeedButton;
    spbdesliga1: TSpeedButton;
    spbdesligatodos: TSpeedButton;
    spbexcluir: TSpeedButton;
    procedure spbsairClick(Sender: TObject);
    procedure FormKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormActivate(Sender: TObject);
    procedure lblcategcodestrKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblcodcategaltKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblcategnomeKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblcodcategaltEnter(Sender: TObject);
    procedure spbsalvarClick(Sender: TObject);
    procedure chkgrupoClick(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure gridcategoriasDblClick(Sender: TObject);
    procedure spbliga1Click(Sender: TObject);
    procedure spbdesliga1Click(Sender: TObject);
    procedure spbligatodosClick(Sender: TObject);
    procedure spbdesligatodosClick(Sender: TObject);
    procedure gridcategoriasKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbexcluirClick(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
    codestr:array [0..255] of string;
  end;

var
  frmcadcategoria: Tfrmcadcategoria;
  categoriavelha,grupo,sql,controle:string;
  resp:word;

function mostra_usuarios_disponiveis : string; export;
function mostra_categorias : string; export;
function mostra_usuarios_relacionados : string; export;
function trata_codigoestruturado_categoria( estruturado : string) : string; export;

implementation

uses funcoes, unt_dados, unt_principal, unt_logon;

{$R *.dfm}

procedure Tfrmcadcategoria.spbsairClick(Sender: TObject);
begin
   close;
   frmprincipal.Show;
end;

function trata_codigoestruturado_categoria( estruturado : string) : string;
var
   contaponto,i:integer;
   cabecodigo,variantecodigo:string;
begin
   with modulo_dados do
   begin
      with frmcadcategoria do
      begin
         // primeiro passo é verificar se o campo não está vazio, se estiver faz o que tem abaixo;
         if lblcategcodestr.Text = '' then
            begin
               messagedlg('O CAMPO CÓDIGO DA CATEGORIA É DE PREENCHIMENTO OBRIGATÓRIO !!!',mterror,[mbok],0);
               lblcategcodestr.SetFocus;
               exit;
            end
         else
            // no segundo passo inicia-se o tratamento da geração de código estruturado.
            begin
               for i:= length(estruturado) downto 0 do
               begin
                  if copy(estruturado,i,1) <> '.' then
                     variantecodigo:=variantecodigo+copy(estruturado,i,1)
                  else
                     break;
               end;
               //
               for i:= length(variantecodigo)downto 1 do
               begin
                  cabecodigo:=cabecodigo+copy(variantecodigo,i,1);
               end;
            end;

      end;
   end;
end;

procedure Tfrmcadcategoria.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f10 then
      spbsair.Click;
end;

procedure Tfrmcadcategoria.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
   action:=cafree;
end;

procedure Tfrmcadcategoria.FormActivate(Sender: TObject);
begin
   statusbar1.Panels[0].Text := 'Banco de Dados';
   statusbar1.Panels[1].Text := configura_statusbar('a');
   statusbar1.Refresh;
   controle:='INCLUSÃO';
   statusbar1.Panels[5].Text := controle;
   lblcodcategalt.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_categoria','S');
   lblcodcategalt.Refresh;
   mostra_usuarios_disponiveis;  mostra_usuarios_relacionados;
   mostra_categorias;
end;

procedure Tfrmcadcategoria.lblcategcodestrKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      begin
         lblcodcategalt.SetFocus;
         exit;
      end;
end;

procedure Tfrmcadcategoria.lblcodcategaltKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      lblcategnome.SetFocus;
end;

procedure Tfrmcadcategoria.lblcategnomeKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      spbsalvar.Click;
end;

procedure Tfrmcadcategoria.lblcodcategaltEnter(Sender: TObject);
begin
   if lblcategcodestr.Text = '' then
      begin
         messagedlg('É OBRIGATÓRIO INFORMAR O CÓDIGO DA CATEGORIA !!!',mterror,[mbok],0);
         lblcategcodestr.SetFocus;
      end
   else
      begin
         trata_codigoestruturado_categoria(lblcategcodestr.Text);
         mostra_usuarios_relacionados;
      end;
end;

procedure Tfrmcadcategoria.spbsalvarClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      if (frmprincipal.integraentidadesapolo = 'Não Integra') then
         begin
            if not validacampo(lblcategnome,'NOME DA CATEGORIA') then exit;
            if ((chkgrupo.Checked = false) and (grupo = '')) then
               grupo:='N';
            //
            if controle = 'INCLUSÃO' then
               begin
                  sql:='SELECT geocategcodestr FROM USER_geoapolo_categoria WHERE geocategcodestr = :pcategcodestr';
                  fdquerysql.Close;
                  fdquerysql.SQL.Clear;
                  fdquerysql.SQL.Text := sql;
                  fdquerysql.ParamByName('pcategcodestr').AsString :=quotedstr(lblcategcodestr.Text);
                  if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
                     begin
                        messagedlg('CÓDIGO ESTRUTURADO DE CATEGORIA JÁ UTILIZADO !!!',mterror,[mbok],0);
                        lblcategcodestr.setfocus;
                        exit;
                     end;
               end;
            sql:='SELECT max(geocategcodalt)+1 as codigo FROM USER_geoapolo_categoria';
            fdquerysql.Close;
            fdquerysql.SQL.Clear;
            fdquerysql.SQL.Text := sql;
            if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
               begin
                  if lblcodcategalt.text = '' then
                     lblcodcategalt.Text:=fdquerysql.FieldByName('codigo').AsString
               end;
            resp:=messagedlg('Confirma a '+controle+' desta categoria de entidade ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
            if resp = idyes then
               begin
                  if controle = 'INCLUSÃO' then
                     begin
                        sql:='INSERT INTO USER_geoapolo_categoria (geocategcodestr, geocategcodalt, geocategnome, geocategcodniv, geocateggrupo, geoempcod)';
                        sql:=sql+' VALUES (:pcategcodestr, :pcodcatalt, :pcategnome,:pcategcodniv, :pcateggrupo, :pgeoempcod)';
                     end
                  else if controle ='ALTERAÇÃO' then
                     begin
                        sql:='UPDATE USER_geoapolo_categoria SET geocategcodestr = :pcategcodestr, geocategcodalt = :pcategcodalt, geocategnome = :pcategnome, geocateggrupo = :pcateggrupo ';
                        sql:=sql+' WHERE geocategcodestr = :pcategcodestrvelha';
                     end;
                  fdquerysql3.Close;
                  fdquerysql3.SQL.Clear;
                  fdquerysql3.SQL.Text := sql;
                  fdquerysql3.ParamByName('pcategcodestr').AsString:= lblcategcodestr.Text;
                  fdquerysql3.ParamByName('pcodcatalt').AsString := lblcodcategalt.Text;
                  fdquerysql3.ParamByName('pcategnome').AsString :=lblcategnome.Text;
                  fdquerysql3.ParamByName('pcategcodniv').AsString :='F';
                  fdquerysql3.ParamByName('pcateggrupo').AsString :=grupo;
                  fdquerysql3.ParamByName('pgeoempcod').AsString := frmprincipal.codigo_empresa;
                  if controle = 'ALTERAÇÃO' then
                     fdquerysql3.ParamByName('pcategcodestrvelha').AsString := categoriavelha;
                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                     begin
                        messagedlg('OPERAÇÃO NA CATEGORIA REALIZADA COM SUCESSO COM SUCESSO !!!',mtinformation,[mbok],0);
                        mostra_categorias;
                        lblcodcategalt.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_categoria','S');
                        controle:='INCLUSÃO'; statusbar1.Panels[5].Text := controle;
                     end
                 else
                     begin
                        messagedlg('PROBLEMAS AO TENTAR REALIZAR A OPERAÇÃO DE '+controle+' COM ESTA CATEGORIA !!!',mterror,[mbok],0);
                        lblcategcodestr.SetFocus;
                        exit;
                     end;
               end;
         end
      else
         begin
            messagedlg('ESTA BASE DE DADOS DO GEOAPOLO ESTÁ CONFIGURADA PARA INTEGRAR COM A BASE APOLO/ALVO, CATEGORIAS DEVEM SER CADASTRADAS E ATUALIZADAS PELO SISTEMA',mtwarning,[mbok],0);
            exit;
         end;
   end;
end;

function mostra_usuarios_disponiveis : string;
begin
   with modulo_dados,frmcadcategoria do
   begin
      sql:='SELECT ugu.login, ugd.nome_departamento, ugu.usucod';
      sql:=sql+' FROM USER_geoapolo_usuarios ugu with(nolock)';
      sql:=sql+' INNER JOIN USER_geoapolo_departamentos ugd with(nolock) ON ugu.codigo_departamento = ugd.codigo_departamento';
      sql:=sql+' WHERE ugu.login is not null';
      //sql:=sql+' AND ugu.login <> '+quotedstr('');
      sql:=sql+' AND ugu.flagativo = :pflagativo';
      sql:=sql+' ORDER BY ugu.login ASC';
      fdquerysql4.Close;
      fdquerysql4.SQL.Clear;
      fdquerysql4.SQL.Text := sql;
      fdquerysql4.parambyname('pflagativo').AsString :='A';
      if executaracao(fdquerysql4, fdbanco, false, dtsfdquerysql4) then
         begin
            gridusuarios.DataSource := dtsfdquerysql4;
            gridusuarios.Refresh;
         end;
   end;
end;

function mostra_usuarios_relacionados : string;
begin
   with modulo_dados,frmcadcategoria do
   begin
      if lblcategcodestr.Text = '' then
         begin
            sql:='SELECT ugu.login, ugc.geocategnome,ugcat.usucod, ugcat.geocategcodestr';
            sql:=sql+' FROM USER_geoapolo_usuarios ugu with(nolock)';
            sql:=sql+' INNER JOIN USER_geoapolo_usuario_categ ugcat ON ugu.usucod = ugcat.usucod';
            sql:=sql+' INNER JOIN USER_geoapolo_categoria ugc with(nolock) ON ugcat.geocategcodestr = ugc.geocategcodestr';
         end
      else if lblcategcodestr.Text <> '' then
         begin
            sql:='SELECT ugu.login,ugc.geocategnome,ugcat.usucod, ugcat.geocategcodestr';
            sql:=sql+' FROM USER_geoapolo_usuarios ugu with(nolock)';
            sql:=sql+' INNER JOIN USER_geoapolo_usuario_categ ugcat with(nolock) ON ugu.usucod = ugcat.usucod';
            sql:=sql+' INNER JOIN USER_geoapolo_categoria ugc with(nolock) ON ugcat.geocategcodestr = ugc.geocategcodestr';
            sql:=sql+' WHERE ugcat.geocategcodestr = :pcategcodestr'; //+quotedstr();
         end;
      fdquerysql6.Close;
      fdquerysql6.SQL.Clear;
      fdquerysql6.SQL.Text := sql;
      if lblcategcodestr.Text <> '' then
         fdquerysql6.ParamByName('pcategcodestr').AsString := lblcategcodestr.text;
      if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
         begin
            gridusuariosrelac.DataSource := dtsfdquerysql6;
            gridusuariosrelac.Refresh;
         end;
   end;
end;

function mostra_categorias : string;
begin
   with modulo_dados,frmcadcategoria do
   begin
      if (frmprincipal.integraentidadesapolo = 'Não Integra') then
         begin
            sql:='SELECT ugc.geocategcodestr, ugc.geocategnome,ugc.geocateggrupo, ugc.geocategcodalt';
            sql:=sql+' FROM USER_geoapolo_categoria ugc with(nolock)';
            sql:=sql+' ORDER BY ugc.geocategcodestr';
            fdquerysql5.Close;
            fdquerysql5.SQL.Clear;
            fdquerysql5.SQL.Text := sql;
            if executaracao(fdquerysql5, fdbanco, false, dtsfdquerysql5) then
               begin
                  gridcategorias.DataSource := dtsfdquerysql5;
                  gridcategorias.Refresh;
                  lblcategcodestr.SetFocus;
               end;
         end
      else
         begin
            messagedlg('ESTA BASE GEOAPOLO ESTÁ CONFIGURADA PARA INTEGRAR ENTIDADES COM O APOLO/ALVO, FAÇA A MANUTENÇÃO POR LÁ !!!',mtwarning,[mbok],0);
            exit;
         end;
   end;
end;

procedure Tfrmcadcategoria.chkgrupoClick(Sender: TObject);
begin
   if chkgrupo.Checked then
      grupo := 'S'
   else if chkgrupo.Checked = false then
      grupo := 'N';
end;

procedure Tfrmcadcategoria.spblimparClick(Sender: TObject);
begin
   lblcategcodestr.Clear; lblcodcategalt.Clear; chkgrupo.Checked:=false;
   lblcategnome.Clear;
end;

procedure Tfrmcadcategoria.gridcategoriasDblClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      controle:='ALTERAÇÃO';
      statusbar1.Panels[5].Text := controle;
      lblcategcodestr.Text := fdquerysql5.fieldbyname('geocategcodestr').asstring;
      categoriavelha:=lblcategcodestr.Text;
      lblcodcategalt.Text := fdquerysql5.fieldbyname('geocategcodalt').asstring;
      if fdquerysql5.FieldByName('geocateggrupo').asstring = 'N' then
         begin
            chkgrupo.Checked := false;
            grupo:='N';
         end
      else if fdquerysql5.FieldByName('geocateggrupo').asstring = 'S' then
         begin
            chkgrupo.Checked := true;
            grupo:='S';
         end;
      lblcategnome.Text := fdquerysql5.fieldbyname('geocategnome').asstring;
      groupbox1.Refresh;
      lblcategcodestr.SetFocus;
      mostra_usuarios_relacionados;
   end;
end;

procedure Tfrmcadcategoria.spbliga1Click(Sender: TObject);
begin
   with modulo_dados do
   begin
      if grupo = 'N' then
         begin
            if lblcategcodestr.Text = '' then
               begin
                  messagedlg('ANTES DE RELACIONAR O USUÁRIO, PRIMEIRO SELECIONE A CATEGORIA !!!',mterror,[mbok],0);
                  lblcategcodestr.SetFocus;
                  exit;
               end;
            if fdquerysql6.IsEmpty then
               begin
                  sql:='SELECT * FROM user_geoapolo_usuariocateg WHERE usucod =:pusucod and geocategcodestr = :pgeocategcodestr ';
               end
            else
               begin
                  sql:='SELECT * FROM USER_geoapolo_usuario_categ  WHERE usucod = :pusucod and geocategcodestr = :p´geocategcodestr';
               end;
            fdquerysql.Close;
            fdquerysql.SQL.Clear;
            fdquerysql.SQL.text := sql;
            fdquerysql.ParamByName('pusucod').AsString := fdquerysql4.fieldbyname('usucod').asstring;
            if not fdquerysql6.IsEmpty then
               fdquerysql.ParamByName('pgeocategcodestr').AsString := lblcategcodestr.Text
            else
               fdquerysql.ParamByName('pcategcodestr').AsString :=  fdquerysql6.fieldbyname('geocategcodestr').asstring;

            if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
               begin
                  messagedlg('USUÁRIO JÁ ESTÁ RELACIONADO A ESTA CATEGORIA !!!', mtwarning,[mbok],0);
                  gridusuarios.SetFocus;
                  exit;
               end
            else
               begin
                  sql:='INSERT INTO USER_geoapolo_usuario_categ (usucod, geocategcodestr, TodasEntidades)';
                  sql:=sql+' VALUES (:pusucod, :pcategcodestr, :ptodasentidades, :ptodasentidades)'; //'+quotedstr()+', ';
//                  sql:=sql+quotedstr()+', '+quotedstr('Sim')+');';
                  fdquerysql3.Close;
                  fdquerysql3.sql.Clear;
                  fdquerysql3.sql.Text := sql;
                  fdquerysql3.ParamByName('pusucod').AsString :=fdquerysql4.fieldbyname('usucod').asstring;
                  fdquerysql3.ParamByName('pcategcodestr').AsString:=lblcategcodestr.Text;
                  fdquerysql3.ParamByName('ptodasentidades').AsString := 'Sim';
                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                     begin
                        //messagedlg('USUÁRIO RELACIONADO COM SUCESSO !!!',mtinformation,[mbok],0);
                        mostra_usuarios_disponiveis; mostra_usuarios_relacionados;
                        gridusuarios.SetFocus;
                     end;
               end;
         end
      else
         begin
            messagedlg('NÃO É POSSÍVEL RELACIONAR GRUPOS DE CATEGORIA AOS USUÁRIOS !!!',mterror,[mbok],0);
            exit;
         end;
   end;
end;

procedure Tfrmcadcategoria.spbdesliga1Click(Sender: TObject);
begin
   with modulo_dados do
   begin
      sql:='DELETE FROM USER_geoapolo_usuariocateg ';
      sql:=sql+' WHERE usucod = :pusucod';
      sql:=sql+' AND geocategcodestr = :pcategcodestr';
      fdquerysql3.Close;
      fdquerysql3.SQL.Clear;
      fdquerysql3.SQL.Text := sql;
      fdquerysql3.ParamByName('pusucod').AsString:=fdquerysql6.fieldbyname('usucod').asstring;
      fdquerysql3.ParamByName('pcategcodestr').AsString :=fdquerysql6.fieldbyname('geocategcodestr').asstring;
      if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
         begin
            mostra_usuarios_disponiveis;  mostra_usuarios_relacionados;
            gridusuarios.SetFocus;
         end
      else
         begin
            messagedlg('PROBLEMAS AO TENTAR REMOVER O VINCULO ENTRE USUÁRIO E CATEGORIA !!!',mterror,[mbok],0);
            gridusuarios.SetFocus;
            exit;
         end;
   end;
end;

procedure Tfrmcadcategoria.spbligatodosClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      fdquerysql4.First;
      while not fdquerysql4.Eof do
      begin
         if lblcategcodestr.Text = '' then
            begin
               messagedlg('SELECIONE A CATEGORIA PARA VINCULAR OS USUÁRIOS !!!',mterror,[mbok],0);
               lblcategcodestr.SetFocus;
               exit;
            end;
         if not fdquerysql6.IsEmpty then
            begin
               sql:='SELECT * FROM USER_geoapolo_usuariocateg WHERE usucod = : pusucod AND geocategcodestr = :pcategcodestr ';
            end
         else
            begin
               sql:='SELECT * FROM USER_geoapolo_usuariocateg WHERE usucod = :pusucod AND geocategcodestr :pcategcodestr';
            end;
         fdquerysql.close;
         fdquerysql.SQL.Clear;
         fdquerysql.SQL.text := sql;
         fdquerysql.ParamByName('pusucod').AsString := fdquerysql4.fieldbyname('usucod').asstring;
         if not fdquerysql6.IsEmpty then
            fdquerysql.ParamByName('pcategcodestr').AsString :=  lblcategcodestr.text
         else
            fdquerysql.ParamByName('pcategcodestr').AsString := fdquerysql6.fieldbyname('geocategcodestr').asstring;
         //
         if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
            begin
               fdquerysql4.Next;
            end
         else
            begin
              sql:='INSERT INTO USER_geoapolo_usuariocateg (usucod, geocategcodestr, TodasEntidades)';
              sql:=sql+' VALUES (:pusucod, :pcategcodestr, :ptodasentidades)';
              fdquerysql3.Close;
              fdquerysql3.SQL.Clear;
              fdquerysql3.SQL.Text := sql;
              fdquerysql3.ParamByName('pusucod').AsString :=fdquerysql4.fieldbyname('usucod').asstring;
              fdquerysql3.ParamByName('pcategcodestr').AsString := lblcategcodestr.Text;
              fdquerysql3.ParamByName('ptodasentidades').AsString := 'Sim';
              if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                 fdquerysql4.Next;
            end;
      end;
      messagedlg('TODAS AS ENTIDADES FORAM RELACIONADAS A ESTA CATEGORIA COM SUCESSO !!!',mtinformation,[mbok],0);
      mostra_usuarios_relacionados;
      gridusuarios.SetFocus;
   end;
end;

procedure Tfrmcadcategoria.spbdesligatodosClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      if lblcategcodestr.Text = '' then
         begin
            messagedlg('SELECIONE A CATEGORIA AO QUAL DESEJA REMOVER O VINCULO COM OS USUÁRIOS !!!',mtwarning,[mbok],0);
            lblcategcodestr.SetFocus;
         end
      else
         begin
            sql:='DELETE FROM USER_geoapolo_usuariocateg ';
            sql:=sql+' WHERE geocategcodestr = :pcategcodestr';
            fdquerysql3.Close;
            fdquerysql3.SQL.clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('pcategcodestr').AsString :=lblcategcodestr.Text;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  messagedlg('TODOS OS VINCULOS DE USUÁRIOS COM ESTA CATEGORIA FORAM REMOVIDOS !!!',mtinformation,[mbok],0);
                  mostra_usuarios_relacionados; mostra_usuarios_disponiveis;
                  gridusuarios.SetFocus;
               end
            else
               begin
                  messagedlg('ERRO AO TENTAR REMOVER OS VINCULOS DE USUÁRIOS COM ESTA CATEGORIA !!!',mterror,[mbok],0);
                  gridusuarios.SetFocus;
                  exit;
               end;
         end;
   end;
end;

procedure Tfrmcadcategoria.gridcategoriasKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if key = vk_delete then
      spbexcluir.Click;
end;

procedure Tfrmcadcategoria.spbexcluirClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      resp:=messagedlg('Confirma a Exclusão desta Categoria de Entidade ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
      if resp = idyes then
         begin
            sql:='DELETE FROM USER_geoapolo_categoria WHERE geocategcodestr = :pcategcodestr';
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('pgeocategcodestr').AsString :=fdquerysql5.fieldbyname('geocategcodestr').asstring;
            if executaracao(fdquerysql3, fdbanco, false, dtsfdquerysql3) then
               begin
                  messagedlg('CATEGORIA REMOVIDA COM SUCESSO !!!',mtinformation,[mbok],0);
                  mostra_categorias;
                  lblcategcodestr.SetFocus;
               end
            else
               begin
                  messagedlg('PROBLEMAS AO TENTAR REMOVER ESTA CATEGORIA, VERIFIQUE OS VINCULOS',mterror,[mbok],0);
                  lblcategcodestr.SetFocus;
                  exit;
               end;
         end
      else
         begin
            lblcategcodestr.SetFocus;
            exit;
         end;
   end;
end;

end.
