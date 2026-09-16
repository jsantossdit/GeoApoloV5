unit unt_about;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, ExtCtrls, StdCtrls, ComCtrls, Buttons, jpeg, dateutils, Vcl.Mask;

type
  Tfrmabout = class(TForm)
    panelmenu: TPanel;
    spbretornar: TSpeedButton;
    barra_status: TStatusBar;
    lblmsg1: TLabel;
    cin: TPageControl;
    tabkeyactive: TTabSheet;
    tabinfosys: TTabSheet;
    GroupBox1: TGroupBox;
    memodescricao: TMemo;
    Panel1: TPanel;
    Image2: TImage;
    lblnomecomp: TLabeledEdit;
    lblip: TLabeledEdit;
    Memo1: TMemo;
    gruposenha: TGroupBox;
    lblusuario: TLabel;
    cbousuario: TComboBox;
    btnexecuta: TBitBtn;
    lblsenha: TLabeledEdit;
    datainicial: TDateTimePicker;
    datafinal: TDateTimePicker;
    lbldatainicial: TLabel;
    lbldatafinal: TLabel;
    lblchavedoperiodo: TLabeledEdit;
    lblcontrachave: TLabeledEdit;
    btnvalidar: TBitBtn;
    btnativar: TBitBtn;
    spbcheck: TSpeedButton;
    procedure FormKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbretornarClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormActivate(Sender: TObject);
    procedure gruposenhaMouseDown(Sender: TObject; Button: TMouseButton;
      Shift: TShiftState; X, Y: Integer);
    procedure gruposenhaEnter(Sender: TObject);
    procedure btnexecutaClick(Sender: TObject);
    procedure btnvalidarClick(Sender: TObject);
    procedure spbcheckClick(Sender: TObject);
    procedure tabkeyactiveEnter(Sender: TObject);
    procedure btnativarClick(Sender: TObject);
    procedure FormCreate(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
    validacao,flag:string;
  end;

var
  frmabout: Tfrmabout;
  sql:string;

function pega_chave_mes : string; export;

implementation

uses funcoes, unt_logon, unt_dados, unt_principal;

{$R *.dfm}

procedure Tfrmabout.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f10 then
      spbretornar.Click;
end;

procedure Tfrmabout.spbretornarClick(Sender: TObject);
begin
   if (frmabout.flag = 'LOGON') and (lblcontrachave.Text = '')  then
      begin
        with modulo_dados do
        begin
          fdbanco.Close;
          application.Terminate;
        end;
      end
   else
      begin
         frmabout.close;
         frmprincipal.Show;
      end;
end;

procedure Tfrmabout.FormClose(Sender: TObject; var Action: TCloseAction);
begin
   action:=cafree;
end;

procedure Tfrmabout.FormActivate(Sender: TObject);
var
   strlst:tstringlist;
   i:integer;
begin
   strlst:=tstringlist.Create;
   lblnomecomp.Text := nomecomputador;
   lblnomecomp.Refresh;
   lblip.Text := getlocalip;
   lblip.Refresh;
   fileverinfo(application.ExeName,strlst);
   for i:= 0 to strlst.Count -1 do
   begin
      memo1.Lines.add(strlst.Strings [i]);
      memo1.Refresh;
   end;
   if frmlogon.codigousuario = '3' then
      gruposenha.Visible := true;
   //
   {busca a chave do periodo e traz para ser decodificada}
   with modulo_dados,frmabout do
   begin
     sql:='SELECT palavra FROM user_geoapolo_dicionario WHERE month(data_inicial) = :datainicial';
     sql:=sql+' AND year(data_final) = :datafinal';
     fdquerysql4.Close;
     fdquerysql4.SQL.Clear;
     fdquerysql4.SQL.Text := sql;
     fdquerysql4.ParamByName('datainicial').AsString :=inttostr(monthof(date()));
     fdquerysql4.ParamByName('datafinal').AsString:=inttostr(yearof(date()));
     if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
        lblchavedoperiodo.Text := fdquerysql4.fieldbyname('palavra').asstring;
   end;
   frmprincipal.libera_validacao := 'ERRO';
   memo1.Lines.add(getbuildinfo);
   memo1.Lines.add('Usuário Logado .:'+' '+loguser);
   //
   if frmlogon.nomeusuario = 'ADMIN' then
      begin
         gruposenha.visible := true;
         cbousuario.setfocus;
      end;
end;

procedure Tfrmabout.gruposenhaMouseDown(Sender: TObject;
  Button: TMouseButton; Shift: TShiftState; X, Y: Integer);
begin
   gruposenha.Visible := false;
end;

procedure Tfrmabout.gruposenhaEnter(Sender: TObject);
begin
   with modulo_dados do
   begin
      sql:='SELECT login, senha FROM user_geoapolo_usuarios WHERE login is not null and login <> :loginconteudo ORDER BY nome_completo ASC';
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := sql;
      fdquerysql.ParamByName('loginconteudo').AsString :='';
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
            fdquerysql.First;
            while not fdquerysql.Eof do
            begin
               cbousuario.Items.add(fdquerysql.fieldbyname('login').asstring);
               fdquerysql.Next;
            end;
         end;
   end;
end;

procedure Tfrmabout.btnexecutaClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      sql:='SELECT senha FROM user_geoapolo_usuarios WHERE login = :cbousuario';
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := sql;
      fdquerysql.ParamByName('cbousuario').AsString :=cbousuario.Text;
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
            lblsenha.Text := decriptografia(32,fdquerysql.fieldbyname('senha').asstring,'aaa');
            lblsenha.Refresh;
         end;
   end;
end;

procedure Tfrmabout.btnvalidarClick(Sender: TObject);
var
   codchave:string;
begin
   if lblchavedoperiodo.Text = '' then
      begin
         messagedlg('A CHAVE DO PERÍODO NÃO FOI RECUPERADA DO BANCO DE DADOS, CONTATE DESENVOLVEDOR !!!',mterror,[mbok],0);
         lblchavedoperiodo.SetFocus;
         exit;
      end;
   //
   codchave := criptografia(42,lblchavedoperiodo.Text);
   lblchavedoperiodo.Refresh;
   if lblcontrachave.Text <> codchave then
      begin
         messagedlg('CONTRA CHAVE NÃO CONFERE COM A CHAVE DO PERÍODO, CONTATE O DESENVOLVEDOR !!!',mterror,[mbok],0);
         lblcontrachave.SetFocus;
         exit;
      end
   else if lblcontrachave.text = codchave then
      begin
         validacao:='OK';
         messagedlg('CONTRA-CHAVE CONFERE COM A CHAVE DO PERÍODO, FAÇA AGORA A ATIVAÇÃO ',mtinformation,[mbok],0);
      end;
end;

procedure Tfrmabout.spbcheckClick(Sender: TObject);
begin
   pega_chave_mes;
end;

function pega_chave_mes : string;
var
   mes,ano,sql:string;
begin
   with modulo_dados, frmabout do
   begin
   datainicial.Date := date; datainicial.Refresh;
   datafinal.Date := date+30; datafinal.Refresh;
   mes:=inttostr(monthof(datainicial.date)); ano:=inttostr(yearof(datainicial.date));
   sql:='SELECT * FROM user_geoapolo_dicionario WHERE month(data_inicial)= :mes';
   sql:=sql+' and year(data_inicial) = :ano';
   fdquerysql.Close;
   fdquerysql.SQL.Clear;
   fdquerysql.SQL.Text := sql;
   fdquerysql.ParamByName('mes').AsString := mes;
   fdquerysql.ParamByName('ano').AsString := ano;
   if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
       begin
          lblchavedoperiodo.Text := fdquerysql.fieldbyname('palavra').AsString; lblchavedoperiodo.Refresh;
       end;
   end;
end;

procedure Tfrmabout.tabkeyactiveEnter(Sender: TObject);
begin
   datainicial.Date := date;
   datafinal.Date := date+30; datainicial.Refresh; datafinal.Refresh;
end;

procedure Tfrmabout.btnativarClick(Sender: TObject);
var
   mes,ano:string;
begin
   with modulo_dados, frmabout do
   begin
      {após fazer a validação da chave, deve-se atualizar na tabela do banco, o campo flag_ativar para "s" afim de que esta chave não seja utilizada
      novamente, após gravar no banco o status, fecha o formulário.}
      if validacao = '' then
         begin
            messagedlg('A CHAVE INFORMADA NÃO FOI VALIDADA, PRIMEIRO DE UM CLIQUE NO BOTÃO VALIDAR !!!',mterror,[mbok],0);
            lblcontrachave.SetFocus;
            exit;
         end
      else if validacao = 'OK' then
         begin
            mes:=inttostr(monthof(datainicial.date)); ano:=inttostr(yearof(datainicial.date));
            frmprincipal.resp:=messagedlg('Confirma a Ativação desta Chave de Uso ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
            if frmprincipal.resp = idyes then
               begin
                  sql:='UPDATE user_geoapolo_dicionario SET flag_ativar = '+quotedstr('S');
                  sql:=sql+' WHERE month(data_inicial)=:mes and year(data_inicial) = :ano';
                  fdquerysql3.Close;
                  fdquerysql3.SQL.Clear;
                  fdquerysql3.SQL.Text := sql;
                  fdquerysql3.ParamByName('mes').AsString := mes;
                  fdquerysql3.ParamByName('ano').AsString := ano;
                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                     begin
                        messagedlg('CHAVE DE USO DO SISTEMA ATIVADA COM SUCESSO !!!',mtinformation,[mbok],0);
                        flag:=''; frmprincipal.libera_validacao := 'OK';
                        spbretornar.click;
                     end
                  else
                     begin
                        messagedlg('ERRO AO TENTAR FAZER A ATIVAÇÃO DA CHAVE DE USO DO SISTEMA !!!',mterror,[mbok],0);
                        exit;
                     end;
               end
            else
               begin
                  exit;
               end;
         end;
   end;
end;

procedure Tfrmabout.FormCreate(Sender: TObject);
begin
{   if not RegisterHotkey(Handle, 1, MOD_ALT, VK_F4) then
      begin
         messagedlg('PROIBIDO UTILIZAR O ATALHO ALT+F4',mterror,[mbok],0);
         lblchavedoperiodo.SetFocus;
         exit;
      end;}
end;

end.
