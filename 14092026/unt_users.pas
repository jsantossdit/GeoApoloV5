unit unt_users;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, Buttons, ExtCtrls, StdCtrls, Grids, DBGrids, ComCtrls, Menus, Data.DB,
  Vcl.Mask, Vcl.Imaging.jpeg;

type
  Tfrmusuarios = class(TForm)
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spblimpar: TSpeedButton;
    spbdeletar: TSpeedButton;
    spblocalizar: TSpeedButton;
    spbsair: TSpeedButton;
    lblf10: TLabel;
    StatusBar1: TStatusBar;
    lblmsg3: TLabel;
    lblf5: TLabel;
    PopupMenu1: TPopupMenu;
    GravaConfiguraes1: TMenuItem;
    spbatualizastatus: TSpeedButton;
    GroupBox7: TGroupBox;
    lblcampo: TLabel;
    lblordem: TLabel;
    lblprocurarpor: TLabeledEdit;
    cbocampo: TComboBox;
    cbordem: TComboBox;
    rdgcrescente: TRadioButton;
    rdgdecrescente: TRadioButton;
    rdbativos: TRadioButton;
    rdbinativos: TRadioButton;
    grpprincipal: TGroupBox;
    lbldtnascimento: TLabel;
    lblnomedepartamento: TLabel;
    spbbuscadepto: TSpeedButton;
    lblcodigouser: TLabeledEdit;
    lblnomeuser: TLabeledEdit;
    chkfuncionario: TCheckBox;
    lbllogin: TLabeledEdit;
    lblemailusuario: TLabeledEdit;
    mskdtnascimento: TMaskEdit;
    lblcodigodepto: TLabeledEdit;
    lblusucodapolo: TLabeledEdit;
    gridusuarios: TDBGrid;
    lblsenhaalvo: TLabeledEdit;
    procedure spbsairClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormActivate(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure spbdeletarClick(Sender: TObject);
    procedure gridusuariosKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbsalvarClick(Sender: TObject);
    procedure spblocalizarClick(Sender: TObject);
    procedure FormKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cboagendaKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblnomedeptoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure chkfuncionarioKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure chkfuncionarioClick(Sender: TObject);
    procedure lblcodigouserKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblemailKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblchapaKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbuscasecaoClick(Sender: TObject);
    procedure GravaConfiguraes1Click(Sender: TObject);
    procedure lblprocurarporKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cbocampoChange(Sender: TObject);
    procedure rdbinativosClick(Sender: TObject);
    procedure GroupBox7Enter(Sender: TObject);
    procedure lblnomeuserKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure mskdtnascimentoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblemailusuarioKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblloginKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure gridusuariosDblClick(Sender: TObject);
    procedure spbbuscadeptoClick(Sender: TObject);
    procedure lblcodigodeptoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure mskdtnascimentoEnter(Sender: TObject);
    procedure lblusucodapoloKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblsenhaalvoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  frmusuarios: Tfrmusuarios;
  vcodigodepartamento,ramal,ramalvelho,flaguser,controle,sql,usucodantigo:string;
  codigoagenda,codigosecao,codigousuariovelho,codigo_usuario:integer;
  resp:word;

function mostra_usuarios(detalhe : string) : string; export;
function valida_secao(codigo_secao: string; nome_secao : string; ordem : string) : string; export;
function checa_usuarios_pendentes : string; export;
function retorna_loginusuario(nome : string) : string; export;
function integraapolo1 : string; export;

implementation

uses funcoes, unt_dados, unt_logon, unt_principal, unt_consultav3,
  unt_users_types, unt_users_repository, unt_users_service;


{$R *.dfm}

procedure Tfrmusuarios.spbsairClick(Sender: TObject);
begin
   close;
end;

procedure Tfrmusuarios.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
   action :=cafree;
end;

function mostra_usuarios(detalhe : string) : string;
var
   sqlview:string;
   i:integer;
begin
   with modulo_dados, frmusuarios do
   begin
       if (rdbativos.Checked = false) and (rdbinativos.Checked = false) then
          rdbativos.Checked := true;
       //
       if detalhe = '' then
          begin
             if rdbativos.Checked then
                begin
                   sql:='SELECT usucod,nome_completo,flagativo,login,email,convert(varchar(10),data_nascimento,103) as data_nascimento,';
                   sql:=sql+' nome_departamento,codigo_departamento,codigo_usuario,usucod_apolo, senha_alvo FROM mostrausuarios WHERE flagativo <> :pFlagativo';
                end
             else if rdbinativos.Checked then
                begin
                   sql:='SELECT usucod,nome_completo,flagativo,login,email,convert(varchar(10),data_nascimento,103) as data_nascimento';
                   sql:=sql+',nome_departamento,codigo_departamento,codigo_usuario, usucod_apolo, senha_alvo FROM mostrausuarios WHERE flagativo = :pFlagativo';
                end;
             fdquerysql8.Close;
             fdquerysql8.SQL.Clear;
             fdquerysql8.sql.text := sql;
             fdquerysql8.ParamByName('pFlagativo').AsString := 'I';
             if executaracao(fdquerysql8,fdbanco,true,dtsfdquerysql8) then
                begin
                   gridusuarios.DataSource:=dtsfdquerysql8;
                   i:=0;
                   if cbocampo.ItemIndex <= 0 then
                      begin
                         for i:= 0 to fdquerysql8.fields.count -1 do
                         begin
                            cbocampo.items.add(fdquerysql8.fields[i].displayname);
                            cbordem.items.add(fdquerysql8.fields[i].displayname);
                         end;
                      end;
                  gridusuarios.refresh;
                end
             else
                begin
                  messagedlg('TABELA DE USUÁRIOS VAZIA !!!', mtwarning, [mbok],0);
               end;
          end
       else if detalhe <> '' then
          begin
               if rdbativos.Checked then
                  begin
                     sql:='SELECT * FROM mostrausuarios WHERE '+cbocampo.Text+' like :pProcurar and flagativo <> :pFlagativo ORDER BY '+cbordem.Text
                  end
               else if rdbinativos.Checked then
                  begin
                     sql:='SELECT * FROM mostrausuarios WHERE '+cbocampo.Text+' like :pProcurar and flagativo = :pFlagativo ORDER BY '+cbordem.Text;
                  end;
               fdquerysql8.Close;
               fdquerysql8.sql.Clear;
               fdquerysql8.SQL.Text:= sql;
               fdquerysql8.ParamByName('pProcurar').AsString := lblprocurarpor.Text + '%';
               fdquerysql8.ParamByName('pFlagativo').AsString := 'I';
               //
               if executaracao(fdquerysql8, fdbanco,true,dtsfdquerysql8) then
                  begin
                     gridusuarios.DataSource:=dtsfdquerysql8;
                     gridusuarios.refresh;
                     i:=0;
                     cbocampo.clear; cbordem.clear;
                     for i:= 0 to fdquerysql8.fields.count -1 do
                     begin
                        cbocampo.items.add(fdquerysql8.fields[i].displayname);
                        cbordem.items.add(fdquerysql8.fields[i].displayname);
                     end;
                  end
               else
                  begin
                     messagedlg('TABELA DE USU�RIOS VAZIA !!!', mtinformation, [mbok],0);
                  end;
          end;
   end;
end;

procedure Tfrmusuarios.FormActivate(Sender: TObject);
begin
   with modulo_dados do
   begin
      rdbativos.Checked := true;
      sql:='SELECT nome_departamento FROM USER_geoapolo_departamentos WHERE flagativo = :pFlagativo GROUP BY nome_departamento ORDER BY nome_departamento asc';
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.sql.text := sql;
      fdquerysql.ParamByName('pFlagativo').AsString := 'A';
      if executaracao(fdquerysql,fdbanco,true,dtsfdquerysql) then
         begin
         end
      else
         begin
            if integraapolo1 = 'S' then
               begin
                  sql:='SELECT distinct cctrlnome FROM centro_ctrl';
                  fdquerysql4.Close;
                  fdquerysql4.SQL.Clear;
                  fdquerysql4.SQL.Text := sql;
                  if executaracao(fdquerysql4,fdbanco,true,dtsfdquerysql4) then
                     begin
                        fdquerysql4.First;
                        while not fdquerysql4.Eof do
                        begin
                           vcodigodepartamento:=geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_departamentos','S');
                           sql:='INSERT INTO USER_geoapolo_departamentos (codigo_departamento,nome_departamento,empcod,flagativo)';
                           sql:=sql+' VALUES (:pCodDepto, :pNomeDepto, :pEmpCod, :pFlagativo)';
                           fdquerysql3.Close;
                           fdquerysql3.sql.clear;
                           fdquerysql3.sql.text := sql;
                           fdquerysql3.ParamByName('pCodDepto').AsString := vcodigodepartamento;
                           fdquerysql3.ParamByName('pNomeDepto').AsString := fdquerysql4.FieldByName('cctrlnome').AsString;
                           fdquerysql3.ParamByName('pEmpCod').AsString := frmprincipal.codigo_empresa;
                           fdquerysql3.ParamByName('pFlagativo').AsString := 'S';
                           if executaracao(fdquerysql3,fdbanco,true,dtsfdquerysql3) then
                              begin
                                 fdquerysql4.Next;
                              end;
                        end;
                     end;
                  messagedlg('FECHE O FORMULÁRIO E ABRA NOVAMENTE !!!',mtwarning,[mbok],0);
                  spbsair.click;
               end;
         end;
   end;
   lblcodigouser.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_usuarios','S');
   lblcodigouser.Refresh;
   controle:='INCLUSÃO';
   mostra_usuarios('');
   carrega_config('GEOUSUARIOS',frmusuarios,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
   configura_grid('GEOUSUARIOS',frmusuarios,frmlogon.nomeusuario,'gridusuarios',gridusuarios,modulo_dados.dtsfdquerysql8);
   gridusuarios.Refresh;
   statusbar1.Panels[1].Text :=configura_statusbar('a');
   statusbar1.Panels[3].Text :=configura_statusbar('a');
   statusbar1.Panels[5].Text := frmprincipal.nomeserversql;
   statusbar1.Refresh;
   lblnomeuser.SetFocus;
end;

procedure Tfrmusuarios.spblimparClick(Sender: TObject);
begin
   lblnomeuser.Clear;
   mskdtnascimento.Clear; lblemailusuario.Clear; lblnomeuser.SetFocus;
   lblprocurarpor.Clear; lbllogin.Clear;  lblusucodapolo.Clear; lblsenhaalvo.Clear;
end;

procedure Tfrmusuarios.spbbuscadeptoClick(Sender: TObject);
begin
   with modulo_dados do
   begin
     sql:='SELECT * FROM USER_geoapolo_departamentos ugd ORDER BY codigo_departamento ASC';
     fdquerysql4.Close;
     fdquerysql4.sql.clear;
     fdquerysql4.sql.text := sql;
     if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
        begin
           application.CreateForm(tfrmconsulta3, frmconsulta3);
           frmconsulta3.controle:='USUARIO_DEPARTAMENTO';
           dtsfdquerysql4.DataSet :=fdquerysql4;
           with frmconsulta3 do
           begin
             gridconsulta.DataSource:=dtsfdquerysql4;
             gridconsulta.Refresh;
             frmconsulta3.ShowModal;
           end;
        end
     else
        begin
          messagedlg('TABELA DE DEPARTAMENTOS EST� VAZIA !!!',mtwarning,[mbok],0);
          spbsair.Click;
        end;
   end;
end;

procedure Tfrmusuarios.spbdeletarClick(Sender: TObject);
begin
   messagedlg('PARA EXCLUIR UM USU�RIO ESCOLHA-O NO GRID E PRESSIONE DELETE, LEMBRE-SE ELE N�O PODE TER VINCULOS DENTRO DO SISTEMA !!!',mtinformation,[mbok],0);
end;

procedure Tfrmusuarios.gridusuariosDblClick(Sender: TObject);
var
   datanascimento:string;
begin
   with modulo_dados do
   begin
      controle:='ALTERAÇÃO';
      lblcodigouser.Text := fdquerysql8.FieldByName('codigo_usuario').AsString;
      lblnomeuser.Text := fdquerysql8.FieldByName('nome_completo').AsString;
      if fdquerysql8.FieldByName('data_nascimento').asstring = '' then
         datanascimento := 'null'
      else
         datanascimento:=fdquerysql8.FieldByName('data_nascimento').AsString;
      mskdtnascimento.Text := datanascimento;

      lblemailusuario.Text := fdquerysql8.FieldByName('email').AsString;
      lblcodigodepto.Text := fdquerysql8.FieldByName('codigo_departamento').AsString;
        sql:='SELECT nome_departamento FROM USER_geoapolo_departamentos WHERE codigo_departamento = :pCodDepto';
        fdquerysql.close;
        fdquerysql.sql.clear;
        fdquerysql.sql.text := sql;
        fdquerysql.ParamByName('pCodDepto').AsString := lblcodigodepto.Text;
        if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
           lblnomedepartamento.Caption := fdquerysql.FieldByName('nome_departamento').AsString;
      lblnomedepartamento.Refresh;
      lbllogin.Text := fdquerysql8.FieldByName('login').AsString;
      lblusucodapolo.text:= fdquerysql8.FieldByName('usucod_apolo').AsString;
      usucodantigo:= fdquerysql8.FieldByName('login').AsString;
      lblcodigouser.SetFocus;
   end;
end;

procedure Tfrmusuarios.gridusuariosKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_delete then
      begin
         with modulo_dados do
         begin
            resp:=messagedlg('Confirma a Exclusão deste usuário ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
            if resp  = idyes then
               begin
                  sql:='DELETE FROM USER_geoapolo_usuarios WHERE usucod = :pUsucod';
                  fdquerysql3.close;
                  fdquerysql3.sql.clear;
                  fdquerysql3.sql.text := sql;
                  fdquerysql3.ParamByName('pUsucod').AsString := fdquerysql8.fieldbyname('usucod').asstring;
                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                     begin
                        messagedlg('REGISTRO EXCLUÍDO COM SUCESSO !!!',mtconfirmation,[mbok],0);
                        mostra_usuarios('');
                        spblimpar.Click;
                        exit;
                     end
                  else
                     begin
                        messagedlg('PROBLEMAS OCORRERAM NA EXCLUSÃO DESTE USUÃRIO, VERIFIQUE SE NÃO HÁ VINCULOS DENTRO DO SISTEMA !!!',mtinformation,[mbok],0);
                        spblimpar.click;
                        exit;
                     end;
               end
            else
               begin
                  lblnomeuser.SetFocus;
                  exit;
               end;
         end;
      end;
   if key = vk_insert then
      begin
         lblcodigouser.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_usuarios','Sim');
         lblcodigouser.Refresh;
         controle:='INCLUSÃO';
         lblnomeuser.SetFocus;
      end;
end;

procedure Tfrmusuarios.spbsalvarClick(Sender: TObject);
var
   datanascimento:string;
begin
   with modulo_dados do
   begin
      // verifica sobre o funcionário ativo
      if chkfuncionario.Checked = false then
         flaguser := 'I'
      else
         flaguser := 'A';
      // verifica se o usuário já está cadastrado
      if (trim(lblnomeuser.text) <> '') and (controle = 'INCLUSÃO') then
         begin
            sql:='SELECT usucod FROM USER_geoapolo_usuarios WHERE nome_completo = :pNomeCompleto';
            fdquerysql.ParamByName('pNomeCompleto').AsString := lblnomeuser.Text;
            fdquerysql.close;
            fdquerysql.sql.clear;
            fdquerysql.sql.text := sql;
            if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
               begin
                  messagedlg('USUÁRIO JÁ CADASTRADO, FAVOR VERIFICAR !!!',mterror,[mbok],0);
                  lblnomeuser.SetFocus;
                  exit;
               end;
         end
      else if (trim(lblnomeuser.Text)='') and (controle = 'INCLUSÃO') then
         begin
            messagedlg('NÃO É PERMITIDO CADASTRAR UM USUÁRIO COM NOME VAZIO !!!',mterror,[mbok],0);
            lblnomeuser.Clear; lblnomeuser.SetFocus;
            lblnomeuser.SetFocus;
            exit;
         end;
      if ((lblcodigouser.Text= '0') or (lblcodigouser.Text = '')) then
         begin
            messagedlg('O CÓDIGO DO USUÁRIO NÃO PODE SER IGUAL A 0 OU NULO',mterror,[mbok],0);
            lblcodigouser.SetFocus;
            exit;
         end;
      if mskdtnascimento.Text <> '  /  /    ' then
         begin
           datanascimento:=copy(mskdtnascimento.Text,7,4)+'/'+copy(mskdtnascimento.Text,4,2)+'/'+copy(mskdtnascimento.Text,1,2);
         end;
      //
      resp := messagedlg('Confirma a operação de '+controle+' deste Usuário ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
      if resp = idyes then
         begin
            if controle = 'INCLUSÃO' then
               begin
                  sql:='INSERT INTO USER_geoapolo_usuarios (usucod, nome_completo, flagativo, login, email, data_nascimento, codigo_departamento, codigo_usuario, usucod_apolo, senha_alvo)';
                  if mskdtnascimento.text = '  /  /    ' then
                     sql:=sql+' VALUES (:pUsucod, :pNomeCompleto, :pFlagAtivo, :pLogin, :pEmail, null, :pCodDepto, :pCodUsuario, :pUsucod_apolo, :psenhaalvo)'
                  else
                     sql:=sql+' VALUES (:pUsucod, :pNomeCompleto, :pFlagAtivo, :pLogin, :pEmail, :pDataNasc, :pCodDepto, :pCodUsuario, :pUsucod_apolo, :psenhaalvo)';
                  fdquerysql3.Close;
                  fdquerysql3.SQL.Clear;
                  fdquerysql3.SQL.Text := sql;
                  fdquerysql3.ParamByName('pUsucod').AsString         := lbllogin.text;
                  fdquerysql3.ParamByName('pNomeCompleto').AsString   := lblnomeuser.Text;
                  fdquerysql3.ParamByName('pFlagAtivo').AsString      := flaguser;
                  fdquerysql3.ParamByName('pLogin').AsString          := lbllogin.text;
                  fdquerysql3.ParamByName('pEmail').AsString          := lblemailusuario.Text;
                  if mskdtnascimento.text <> '  /  /    ' then
                     fdquerysql3.ParamByName('pDataNasc').AsString    := datanascimento;
                  fdquerysql3.ParamByName('pCodDepto').AsString       := lblcodigodepto.text;
                  fdquerysql3.ParamByName('pCodUsuario').AsString     := lblcodigouser.text;
                  fdquerysql3.ParamByName('pUsucod_apolo').AsString   := lblusucodapolo.Text;
                  fdquerysql3.ParamByName('psenhaalvo').AsString      := criptografia(35,lblsenhaalvo.Text) ;
               end
            else if controle = 'ALTERAÇÃO' then
               begin
                  sql:='UPDATE USER_geoapolo_usuarios SET nome_completo = :pNomeCompleto';
                  sql:=sql+', flagativo = :pFlagAtivo, email = :pEmail, login = :pLogin';
                  sql:=sql+', codigo_departamento = :pCodDepto';
                  if mskdtnascimento.text = '  /  /    ' then
                     sql:=sql+', data_nascimento = null'
                  else
                     sql:=sql+', data_nascimento = :pDataNasc';
                  sql:=sql+', usucod_apolo = :pUsucod_apolo';
                  sql:=sql+', senha_alvo = :psenhaalvo';
                  sql:=sql+' WHERE codigo_usuario = :pCodUsuario AND usucod = :pUsucod';
                  fdquerysql3.Close;
                  fdquerysql3.SQL.Clear;
                  fdquerysql3.SQL.Text := sql;
                  fdquerysql3.ParamByName('pNomeCompleto').AsString   := lblnomeuser.text;
                  fdquerysql3.ParamByName('pFlagAtivo').AsString      := flaguser;
                  fdquerysql3.ParamByName('pEmail').AsString          := lblemailusuario.Text;
                  fdquerysql3.ParamByName('pLogin').AsString          := lbllogin.text;
                  fdquerysql3.ParamByName('pCodDepto').AsString       := lblcodigodepto.Text;
                  if mskdtnascimento.text <> '  /  /    ' then
                     fdquerysql3.ParamByName('pDataNasc').AsString := copy(mskdtnascimento.Text,7,4)+'/'+copy(mskdtnascimento.Text,4,2)+'/'+copy(mskdtnascimento.Text,1,2);
                  fdquerysql3.ParamByName('pUsucod_apolo').AsString   := lblusucodapolo.Text;
                  fdquerysql3.ParamByName('pCodUsuario').AsString     := lblcodigouser.Text;
                  fdquerysql3.ParamByName('pUsucod').AsString         := usucodantigo;
                  fdquerysql3.ParamByName('psenhaalvo').AsString      := criptografia(35,lblsenhaalvo.Text);
               end;
            if executaracao(fdquerysql3,fdbanco,true,dtsfdquerysql3) then
                begin
                   // FIM DA ROTINA QUE ATUALIZA RELACIONAMENTO ENTRE USU�RIO E RAMAL
                   // VERIFICA / ATUALIZA O STATUS NA TABELA DE CONTATOS DA AGENDA QUANDO FOR FUNCION�RIO
                    lblcodigouser.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_usuarios','Sim');
                    lblcodigouser.Refresh;
                    messagedlg('OPERAÇÃO DE '+controle+' FOI REALIZADA COM SUCESSO !!!',mtinformation,[mbok],0);
                    spblimpar.click;
                    controle:='INCLUSÃO';
                    mostra_usuarios('');
                 end
            end;
{            carrega_config('GEOUSUARIOS',frmusuarios,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
            configura_grid('GEOUSUARIOS',frmusuarios,'gridusuarios',frmlogon.nomeusuario,gridusuarios,modulo_dados.dtsfdquerysql8);}
         end
end;


procedure Tfrmusuarios.spblocalizarClick(Sender: TObject);
begin
   messagedlg('PARA EFETUAR UMA PESQUISA DIGITE O NOME DO USU�RIO NO CAMPO NOME E PRESSIONE <ENTER> !!!',mtinformation,[mbok],0);
end;

procedure Tfrmusuarios.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f3 then
      begin
         mostra_usuarios('');
      end;
   if key = vk_f10 then
      spbsair.Click;
   if key = vk_f5 then
      begin
         setcursorsql('sql');
         messagedlg('DADOS SINCRONIZADOS !!!',mtinformation,[mbok],0);
         setcursorsql('');
      end;
end;

procedure Tfrmusuarios.cboagendaKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      spbsalvar.Click;
end;

procedure Tfrmusuarios.lblnomedeptoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      chkfuncionario.SetFocus;
end;

procedure Tfrmusuarios.chkfuncionarioKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      spbsalvar.Click;
end;

procedure Tfrmusuarios.chkfuncionarioClick(Sender: TObject);
begin
   if chkfuncionario.Checked = true then
      flaguser:='A'
   else if chkfuncionario.Checked = false then
      flaguser:='I';
end;

procedure Tfrmusuarios.lblcodigodeptoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      lblemailusuario.SetFocus;
   if key = vk_f4 then
      spbbuscadepto.click;
end;

procedure Tfrmusuarios.lblcodigouserKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lblnomeuser.SetFocus;
end;

procedure Tfrmusuarios.lblemailKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_tab) or (key = vk_return)) then
      spbsalvar.click;
end;

procedure Tfrmusuarios.lblemailusuarioKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      lbllogin.SetFocus;
end;

procedure Tfrmusuarios.lblloginKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      begin
         lblusucodapolo.SetFocus;
      end;
end;

procedure Tfrmusuarios.lblchapaKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_tab) or (key = vk_return)) then
      spbsalvar.Click;
end;

procedure Tfrmusuarios.lblnomeuserKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      mskdtnascimento.SetFocus;
end;

function valida_secao(codigo_secao: string; nome_secao : string; ordem : string) : string;
begin
   with modulo_dados, frmusuarios do
   begin
      if ordem = '0' then
         begin
            sql:='SELECT codigo_departamento, nome_departamento FROM USER_geoapolo_departamentos WHERE codigo_departamento = :pCodDepto AND flagativo = :pFlagativo';
            fdquerysql.ParamByName('pCodDepto').AsString   := codigo_secao;
            fdquerysql.ParamByName('pFlagativo').AsString  := 'S';
         end
      else
         begin
            sql:='SELECT codigo_departamento, nome_departamento FROM USER_geoapolo_departamentos WHERE nome_departamento = :pNomeDepto AND flagativo = :pFlagativo';
            fdquerysql.ParamByName('pNomeDepto').AsString  := nome_secao;
            fdquerysql.ParamByName('pFlagativo').AsString  := 'S';
         end;
      fdquerysql.close;
      fdquerysql.sql.clear;
      fdquerysql.sql.text := sql;
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
            if ordem = '0' then
               result:=fdquerysql.fieldbyname('codigo_departamento').asstring
            else if ordem = '1' then
               result:=fdquerysql.fieldbyname('nome_departamento').asstring;
         end;
   end;
end;

procedure Tfrmusuarios.spbuscasecaoClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      sql:='SELECT ugd.codigo_departamento, ugd.nome_departamento,uge.empcod,uge.empnome';
      sql:=sql+' FROM  USER_geoapolo_departamentos ugd with(nolock)';
      sql:=sql+' INNER JOIN USER_geoapolo_empresas uge with(nolock) ON ugd.empcod = uge.empcod';
      sql:=sql+' WHERE ugd.flagativo = :pFlagativo';
      sql:=sql+' ORDER BY ugd.nome_departamento ASC';
      fdquerysql5.ParamByName('pFlagativo').AsString := 'S';
      fdquerysql5.close;
      fdquerysql5.sql.clear;
      fdquerysql5.sql.text := sql;
      if executaracao(fdquerysql5, fdbanco, true, dtsfdquerysql5) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            with frmconsulta3 do
            begin
               controle:='DEPARTAMENTOS';
               gridconsulta.DataSource := dtsfdquerysql5;
               frmconsulta3.ShowModal;
            end;
         end
      else
         begin
            messagedlg('TABELA DE DEPARTAMENTOS EST� VAZIA !!!',mterror,[mbok],0);
            spbsair.Click;
         end;
   end;
end;

function checa_usuarios_pendentes : string;
begin
   with modulo_dados, frmusuarios do
   begin
      sql:='SELECT flagativo FROM usuarios_pendentes WHERE flagativo = :pFlagativo';
      fdquerysql.ParamByName('pFlagativo').AsString := 'P';
      fdquerysql.close;
      fdquerysql.sql.clear;
      fdquerysql.sql.text := sql;
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
            resp:=messagedlg('Existem usu�rios que foram importados, mas est�o com pend�ncias, verificar agora ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
            if resp = idyes then
               begin
{                  if formestacriado(tfrmusuariospendentes) then
                     frmusuariospendentes.WindowState:=wsmaximized
                  else
                     begin
                        application.CreateForm(tfrmusuariospendentes, frmusuariospendentes);
                        frmusuariospendentes.ShowModal;
                     end;}
               end;
         end;
   end;
end;

procedure Tfrmusuarios.GravaConfiguraes1Click(Sender: TObject);
begin
   grava_configuracoes_grids(frmusuarios,'GEOUSUARIOS',gridusuarios,'gridusuarios',frmlogon.nomeusuario, modulo_dados.dtsfdquerysql8);
   grava_config_telabusca('GEOUSUARIOS',cbocampo.Text,cbordem.Text,'A',frmusuarios);
end;

procedure Tfrmusuarios.lblprocurarporKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      begin
         mostra_usuarios('t');
         carrega_config('GEOUSUARIOS',frmusuarios,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('GEOUSUARIOS',frmusuarios,'gridusuarios',frmlogon.nomeusuario,gridusuarios,modulo_dados.dtsfdquerysql8);
      end;
end;

procedure Tfrmusuarios.lblsenhaalvoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      begin
         chkfuncionario.Checked:= true;
         spbsalvar.Click;
      end;
end;

procedure Tfrmusuarios.lblusucodapoloKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      begin
         lblsenhaalvo.SetFocus;
      end;
end;

procedure Tfrmusuarios.mskdtnascimentoEnter(Sender: TObject);
begin
   if lblnomeuser.Text <> ''then
      begin
         lbllogin.text := retorna_loginusuario(lblnomeuser.Text);
         lbllogin.Refresh;
      end;
end;

procedure Tfrmusuarios.mskdtnascimentoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      lblcodigodepto.SetFocus;
end;

procedure Tfrmusuarios.cbocampoChange(Sender: TObject);
begin
   cbordem.itemindex:=cbocampo.itemindex;
end;

procedure Tfrmusuarios.rdbinativosClick(Sender: TObject);
begin
   if rdbinativos.Checked then
      rdbativos.Checked := false;
   rdbativos.Refresh;
end;

procedure Tfrmusuarios.GroupBox7Enter(Sender: TObject);
begin
   rdbativos.Checked := true;
end;

function retorna_loginusuario(nome : string) : string;
var
   login,login1,login2:string;
   i,a,c:integer;
begin
   with modulo_dados, frmusuarios do
   begin
      //cria login do usu�rio
      login:=''; login1:=''; login2:='';
      login:=buscatroca(nome,chr(39),quotedstr(chr(39)));
      for i:= 1 to length(login) do
      begin
         if copy(login,i,1) <> ' ' then
            login1:=login1+copy(login,i,1)
         else
            break;
      end;
      //
      for a:= length(login) downto 1 do
      begin
         if copy(login,a,1) <> ' ' then
            login2:=login2+copy(login,a,1)
         else
            break;
      end;
      sql:='';
      for c:= length(login2) downto 1 do
      begin
         sql:=sql+copy(login2,c,1);
      end;
      login2:=sql;
      //
      login:=login1+'.'+login2;
      result:=login;
   end;
end;

function integraapolo1 : string;
begin
   with modulo_dados do
   begin
      sql:='SELECT integra_base_apolomix FROM USER_geoapolo_configuracoes';
      fdquerysql.close;
      fdquerysql.sql.text := sql;
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         result:=fdquerysql.fieldbyname('integra_base_apolomix').asstring
       else
          begin
             result:='N';
          end;
   end;
end;

end.
