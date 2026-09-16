unit unt_usersadm;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, Buttons, ExtCtrls, StdCtrls, Grids, DBGrids, ComCtrls, Data.DB,
  Vcl.Mask;

type
  Tfrmusuariosadm = class(TForm)
    GroupBox1: TGroupBox;
    lblcodigouser: TLabeledEdit;
    lblnomeuser: TLabeledEdit;
    GroupBox2: TGroupBox;
    dbgusuarios: TDBGrid;
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spblimpar: TSpeedButton;
    spbdeletar: TSpeedButton;
    spbabreos: TSpeedButton;
    spbsair: TSpeedButton;
    lblmsg2: TLabel;
    GroupBox3: TGroupBox;
    lblsa: TLabeledEdit;
    Label1: TLabel;
    cbosistemas: TComboBox;
    btnvincular: TBitBtn;
    gridsistemas: TDBGrid;
    StatusBar1: TStatusBar;
    lblogin: TLabeledEdit;
    chkflagativo: TCheckBox;
    chkzerasenha: TCheckBox;
    procedure spbsairClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormActivate(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure cbodepartamentosKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cbodepartamentosEnter(Sender: TObject);
    procedure dbgusuariosDblClick(Sender: TObject);
    procedure spbdeletarClick(Sender: TObject);
    procedure dbgusuariosKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbsalvarClick(Sender: TObject);
    procedure spbabreosClick(Sender: TObject);
    procedure FormKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cbosistemasKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure btnvincularClick(Sender: TObject);
    procedure cbosistemasEnter(Sender: TObject);
    procedure gridsistemasKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure gridsistemasDblClick(Sender: TObject);
    procedure lbloginKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure chkflagativoClick(Sender: TObject);
    procedure lblnomeuserKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  frmusuariosadm: Tfrmusuariosadm;
  controlesistema,flagativo,login,controle,sql,codigo_usuario:string;
  codigosistemavelho,codigodepartamento:integer;
  resp:word;

function mostra_usuarios : string; export;
function mostra_sistemasusuarios(codigousuario:string) : string; export;

implementation

uses funcoes, unt_dados, unt_principal, unt_selecionaempresa, unt_logon;

{$R *.dfm}

procedure Tfrmusuariosadm.spbsairClick(Sender: TObject);
begin
   close;
end;

procedure Tfrmusuariosadm.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
   action :=cafree;
end;

function mostra_usuarios : string;
begin
   with modulo_dados, frmusuariosadm do
   begin
       sql:='SELECT * FROM mostrausuarios WHERE flagativo <> :pflagativo ORDER BY nome_completo ASC;';
       fdquerysql4.Close;
       fdquerysql4.SQL.Clear;
       fdquerysql4.SQL.Text := sql;
       fdquerysql4.ParamByName('pflagativo').AsString := 'I';
       if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
          begin
             dbgusuarios.DataSource := dtsfdquerysql4;
             dbgusuarios.Refresh;
             exit;
          end
       else
          begin
             messagedlg('TABELA DE USUÁRIOS VAZIA !!!', mtwarning, [mbok],0);
             exit;
          end;
    end;
end;

function mostra_sistemasusuarios(codigousuario:string) : string;
begin
   with modulo_dados, frmusuariosadm do
   begin
       // parei aqui em 30/10/2019
      sql:='SELECT ugs.codigo_sistema, ugs.descricao, ugs.sigla, ugus.usucod, ugu.login';
      sql:=sql+' FROM USER_geoapolo_usuariossistemas ugus with(nolock)';
      sql:=sql+' INNER JOIN USER_geoapolo_sistemas ugs with(nolock) ON ugus.codigo_sistema = ugs.codigo_sistema';
      sql:=sql+' INNER JOIN USER_geoapolo_usuarios ugu with(nolock) ON ugus.usucod = ugu.usucod';
      sql:=sql+' WHERE ugus.usucod= :pusucod';
      fdquerysql5.close;
      fdquerysql5.SQL.Clear;
      fdquerysql5.SQL.Text := sql;
      fdquerysql5.ParamByName('pusucod').AsString := codigousuario;
      if executaracao(fdquerysql5, fdbanco, true, dtsfdquerysql5) then
          begin
             gridsistemas.DataSource := dtsfdquerysql5;
             gridsistemas.Refresh;
             exit;
          end
       else
          begin
             messagedlg('TABELA DE VINCULOS ENTRE SISTEMA E O USUÁRIO ESTÁ VAZIA !!!', mtwarning, [mbok],0);
             exit;
          end;
    end;
end;

procedure Tfrmusuariosadm.FormActivate(Sender: TObject);
begin
   with modulo_dados do
   begin
      // carregamento dos sistemas cadastrados
      sql:='SELECT * FROM USER_geoapolo_sistemas ORDER BY descricao ASC;';
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := sql;
      if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
         begin
            fdquerysql.First;
            while not fdquerysql.eof do
            begin
               cbosistemas.Items.Add(fdquerysql.fieldbyname('descricao').asstring);
               fdquerysql.Next;
            end;
         end
      else
         begin
            sql:='INSERT INTO USER_geoapolo_sistemas (codigo_sistema,descricao) ';
            sql:=sql+' VALUES (:pcodigosistema, :pdescricao)';
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('pcodigosistema').AsString:=geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_sistemas','Sim');
            fdquerysql3.ParamByName('pdescricao').AsString := 'GeoApolo';
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  sql:='SELECT * FROM USER_geoapolo_sistemas ORDER BY descricao ASC;';
                  fdquerysql.Close;
                  fdquerysql.SQL.Clear;
                  fdquerysql.SQL.Text := sql;
                  if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
                     begin
                        fdquerysql.First;
                        while not fdquerysql.eof do
                        begin
                           cbosistemas.Items.Add(fdquerysql.fieldbyname('descricao').asstring);
                           fdquerysql.Next;
                        end;
                     end;
               end;
         end;
      //
   end;
   controle:='ALTERAÇÃO';
   controlesistema:='INCLUSÃO';
   lblcodigouser.Text :=geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_usuarios','S');
   lblcodigouser.Refresh;
   statusbar1.Panels[0].Text := 'Banco de Dados';
   statusbar1.Panels[1].Text := configura_statusbar('a');
   statusbar1.Panels[2].Text := 'Banco GeoApolo';
   statusbar1.Panels[3].Text := configura_statusbar('a');
   statusbar1.Refresh;
   mostra_usuarios;
end;

procedure Tfrmusuariosadm.spblimparClick(Sender: TObject);
begin
   lblnomeuser.Clear; lblogin.Clear;
   mostra_usuarios;
end;

procedure Tfrmusuariosadm.cbodepartamentosKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      lblogin.SetFocus;
end;

procedure Tfrmusuariosadm.cbodepartamentosEnter(Sender: TObject);
var
   i,cdsec:integer;
begin
   if trim(lblnomeuser.Text) = '' then
      begin
         messagedlg('PARA INCLUIR UM USUÁRIO É NECESSÁRIO O NOME DO MESMO !!!',mtwarning,[mbok],0);
         lblnomeuser.Clear;
         lblnomeuser.setfocus;
         exit;
      end;
   controlesistema:='INCLUSÃO';
   with modulo_dados do
   begin
      if lblnomeuser.Text <> '' then
         begin
            sql:='SELECT * FROM USER_geoapolo_usuarios WHERE login = :pnomeuser ;';
            fdquerysql.Close;
            fdquerysql.SQL.Clear;
            fdquerysql.SQL.Text := sql;
            fdquerysql.ParamByName('pnomeuser').AsString := lblnomeuser.Text;
            if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
               begin
                  if fdquerysql.FieldByName('usucod').asstring <> '0' then
                     begin
                        controle:='ALTERAÇÃO';
                        lblcodigouser.Text := fdquerysql.fieldbyname('usucod').asstring;
                        lblnomeuser.Text := fdquerysql.fieldbyname('login').AsString ;
                        cdsec:=fdquerysql.fieldbyname('codigo_departamento').asinteger;
                     end;
               end
            else
               controle:='ALTERAÇÃO';
         end;
   end;
end;

procedure Tfrmusuariosadm.dbgusuariosDblClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      controle:='ALTERAÇÃO';
      lblcodigouser.Text := fdquerysql4.fieldbyname('usucod').asstring;
      codigo_usuario:=lblcodigouser.Text;
      lblnomeuser.Text := fdquerysql4.fieldbyname('nome_completo').asstring;
      lblogin.Text := fdquerysql4.fieldbyname('login').asstring;
      lblcodigouser.Refresh; lblnomeuser.Refresh;
      if fdquerysql4.FieldByName('flagativo').AsString = 'A' then
         chkflagativo.Checked :=true
      else if fdquerysql4.fieldbyname('flagativo').asstring = '' then
         chkflagativo.Checked := false;
   end;
end;

procedure Tfrmusuariosadm.spbdeletarClick(Sender: TObject);
begin
   messagedlg('PARA EXCLUIR UM USUÁRIO ESCOLHA-O NO GRID E PRESSIONE DELETE, LEMBRE-SE ELE NÃO PODE TER VINCULOS DENTRO DO SISTEMA !!!',mtinformation,[mbok],0);
end;

procedure Tfrmusuariosadm.dbgusuariosKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
var
   entrada:string;
begin
   if key = vk_delete then
      begin
         with modulo_dados do
         begin
            resp:=messagedlg('Confirma a Exclusão deste usuário ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
            if resp  = idyes then
               begin
                  sql:='DELETE FROM USER_geoapolo_usuarios WHERE usucod = :pusucod';
                  fdquerysql3.Close;
                  fdquerysql3.sql.clear;
                  fdquerysql3.SQL.Text:= sql;
                  fdquerysql3.ParamByName('pusucod').AsString := codigo_usuario;
                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                     begin
                        messagedlg('REGISTRO EXCLUÍDO COM SUCESSO !!!',mtinformation,[mbok],0);
                        spblimpar.Click;
                        exit;
                     end
                  else
                     begin
                        messagedlg('PROBLEMAS OCORRERAM NA EXCLUSÃO DESTE USUÁRIO, VERIFIQUE SE NÃO HÁ VINCULOS DENTRO DO SISTEMA !!!',mterror,[mbok],0);
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
   if key = vk_f2 then
      begin
         with modulo_dados do
         begin
             entrada:=inputbox('Pesquisa Seletiva de Usuários','O que deseja buscar','');
             sql:='SELECT * FROM mostrausuarios WHERE flagativo <> :pflagativo AND nome_completo like :pnomecompleto';
             fdquerysql4.Close;
             fdquerysql4.SQL.Clear;
             fdquerysql4.SQL.Text := sql;
             fdquerysql4.ParamByName('pflagativo').AsString := 'I';
             fdquerysql4.ParamByName('pnomecompleto').AsString :='%'+entrada+'%';
             if executaracao(fdquerysql4, fdbanco, false, dtsfdquerysql4) then
                begin
                   dbgusuarios.DataSource := dtsfdquerysql4;
                   dbgusuarios.Refresh;
                   exit;
                end
             else
                begin
                   messagedlg('TABELA DE USUÁRIOS VAZIA !!!', mtwarning, [mbok],0);
                   exit;
                end;
         end;
      end;
end;

procedure Tfrmusuariosadm.spbsalvarClick(Sender: TObject);
var
   i:integer;
begin
   with modulo_dados do
   begin
      if controle = 'ALTERAÇÃO' then
         begin
            resp := messagedlg('Confirma a Alteracao deste Usuário ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
            if resp = idyes then
               begin
                  if chkflagativo.Checked = true then
                     flagativo:='A'
                  else if chkflagativo.Checked = false then
                     flagativo:='I';
                  if trim(lblogin.Text) = '' then
                     begin
                        if trim(lblnomeuser.Text) <> '' then
                           begin
                              for i:= 0 to length(lblnomeuser.Text) do
                              begin
                                 if copy(lblnomeuser.Text,i,1) = ' ' then
                                    begin
                                       login:=copy(lblnomeuser.Text,1,i);
                                       break;
                                    end;
                              end;
                           end;
                     end
                  else
                     login:=lblogin.Text;
                  // VERIFICAÇÃO DE OPÇÃO PARA ZERAR SENHA DO USUÁRIO
                  if chkzerasenha.Checked = true then
                     begin
                       sql:='UPDATE USER_geoapolo_usuarios SET usucod = :pusucod, nome_completo = :pnomecompleto, login = :login, flagativo = :pflagativo';
                       sql:=sql+', senha = :psenha WHERE usucod = :pusucod';
                     end
                  else
                     begin
                       sql:='UPDATE USER_geoapolo_usuarios SET usucod = :pusucod';
                       sql:=sql+', nome_completo = :pnomecompleto, login = :login, flagativo = :pflagativo, senha = :psenha';
                       sql:=sql+' WHERE usucod = :pusucodorigem';
                     end;
                  fdquerysql3.Close;
                  fdquerysql3.SQL.Clear;
                  fdquerysql3.SQL.Text := sql;
                  fdquerysql3.ParamByName('pusucod').AsString :=  codigo_usuario;
                  fdquerysql3.ParamByName('pnomecompleto').AsString :=lblnomeuser.text;
                  fdquerysql3.ParamByName('login').AsString:=login;
                  fdquerysql3.ParamByName('pflagativo').AsString:=flagativo;
                  fdquerysql3.ParamByName('psenha').AsString :='';
                  fdquerysql3.ParamByName('pusucod').AsString := lblcodigouser.Text;
                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                     begin
                        messagedlg('Usuário Alterado com Sucesso !!!',mtinformation,[mbok],0);
                        spblimpar.click;
                        exit;
                     end
                  else
                     begin
                        messagedlg('Este registro violou alguma regra de integridade do banco de dados !!!',mterror,[mbok],0);
                        exit;
                     end;
               end
            else
               lblnomeuser.SetFocus;
         end;
   end;
end;

procedure Tfrmusuariosadm.spbabreosClick(Sender: TObject);
begin
   messagedlg('PARA EFETUAR UMA PESQUISA DIGITE O NOME DO USUÁRIO NO CAMPO NOME E PRESSIONE ENTER !!!',mtinformation,[mbok],0);
end;

procedure Tfrmusuariosadm.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f10 then
      spbsair.Click;
end;

procedure Tfrmusuariosadm.cbosistemasKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_return then
      btnvincular.Click;
end;

procedure Tfrmusuariosadm.btnvincularClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      if trim(cbosistemas.Text) = '' then
         begin
            messagedlg('VOCÊ PRECISA INFORMAR QUAIS SISTEMAS O USUÁRIO PODERÁ ACESSAR !!!',mtwarning,[mbok],0);
            cbosistemas.SetFocus;
            exit;
         end;
      if trim(cbosistemas.Text) <> '' then
         begin
            sql:='SELECT * FROM USER_geoapolo_sistemas WHERE descricao = :pcbosistemas';
            fdquerysql1.Close;
            fdquerysql1.SQL.Clear;
            fdquerysql1.SQL.Text := sql;
            fdquerysql1.ParamByName('pcbosistemas').AsString :=cbosistemas.Text;
            if executaracao(fdquerysql1, fdbanco, false, dtsfdquerysql1) then
               begin
                  lblsa.Text := fdquerysql1.fieldbyname('codigo_sistema').asstring;
                  lblsa.Refresh;
               end;
         end
      else
         begin
            messagedlg('VOCÊ PRECISA DEFINIR QUAIS SISTEMAS O USUÁRIO ESTÁ AUTORIZADO A ACESSAR !!!',mtwarning,[mbok],0);
            cbosistemas.SetFocus;
         end;
      // VERIFICA SE O SISTEMA JÁ FOI VINCULADO AO USUÁRIO
      if trim(lblsa.Text) <> '' then
         begin
            sql:='SELECT codigo_sistema FROM USER_geoapolo_usuariossistemas ';
            sql:=sql+' WHERE codigo_sistema = :pcodigosistema AND usucod = :pusucod';
            fdquerysql.Close;
            fdquerysql.SQL.Clear;
            fdquerysql.SQL.Text := sql;
            fdquerysql.ParamByName('pcodigosistema').AsString :=lblsa.text;
            fdquerysql.ParamByName('pusucod').AsString :=lblcodigouser.Text;
            if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
               begin
                  messagedlg('ESTE USUÁRIO JÁ FOI AUTORIZADO A UTILIZAR ESTE SISTEMA !!!',mtwarning,[mbok],0);
                  cbosistemas.ItemIndex := -1;
                  cbosistemas.SetFocus;
                  exit;
               end;
         end;
      resp:=messagedlg('Confirma a Autorização do Usuário para este Sistema ? (Y/N)',mtinformation,[mbyes,mbno],0);
      if resp = idyes then
         begin
            if controlesistema = 'INCLUSÃO' then
               begin
                  sql:='INSERT INTO USER_geoapolo_usuariossistemas (usucod,codigo_sistema) ';
                  sql:=sql+' VALUES (:pusucod, :pcodigosistema)';
               end
            else if controlesistema = 'ALTERAÇÃO' then
               begin
                  sql:='UPDATE USER_geoapolo_usuariossistemas SET codigo_sistema = :pcodigosistema';
                  sql:=sql+' WHERE usucod = :pusucod';
                  sql:=sql+' AND codigo_sistema = :pcodigosistema';
               end;
              fdquerysql3.Close;
              fdquerysql3.SQL.Clear;
              fdquerysql3.SQL.Text := sql;
              fdquerysql3.ParamByName('pusucod').AsString :=lblcodigouser.Text;
              fdquerysql3.ParamByName('pcodigosistema').AsString :=lblsa.Text;
              if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                 begin
                    messagedlg('VÍNCULO ATUALIZADO COM SUCESSO !!!',mtinformation,[mbok],0);
                    cbosistemas.ItemIndex := -1; lblsa.Clear;
                    controlesistema:='INCLUSÃO';
                    mostra_sistemasusuarios(lblcodigouser.Text);
                    exit;
                 end;
         end
      else
         begin
            cbosistemas.SetFocus;
            exit;
         end;
   end;
end;

procedure Tfrmusuariosadm.cbosistemasEnter(Sender: TObject);
begin
   mostra_sistemasusuarios(lblcodigouser.Text);
end;

procedure Tfrmusuariosadm.gridsistemasKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   with modulo_dados do
   begin
      if key = vk_delete then
         begin
            resp:=messagedlg('Confirma remoção da autorização deste usuário ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
            if resp = idyes then
               begin
                  sql:='DELETE FROM USER_geoapolo_usuariossistemas WHERE usucod = :pusucod';
                  sql:=sql+' AND codigo_sistema = :pcodigosistema';
                  fdquerysql3.Close;
                  fdquerysql3.SQL.Clear;
                  fdquerysql3.SQL.Text := sql;
                  fdquerysql3.ParamByName('pusucod').AsString :=fdquerysql5.fieldbyname('usucod').asstring;
                  fdquerysql3.parambyname('pcodigosistema').AsString := fdquerysql5.FieldByName('codigo_sistema').AsString;
                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                     begin
                        messagedlg('REMOÇÃO DA PERMISSÃO FOI EXECUTADA COM SUCESSO !!!',mtinformation,[mbok],0);
                        cbosistemas.ItemIndex := -1; lblsa.Clear;
                        cbosistemas.SetFocus;
                     end
                  else
                     begin
                        cbosistemas.SetFocus;
                        exit;
                     end;
               end
            else
               begin
                  cbosistemas.SetFocus;
                  exit;
               end;
         end;
   end;
end;

procedure Tfrmusuariosadm.gridsistemasDblClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      lblsa.Text := fdquerysql4.fieldbyname('codigo_sistema').asstring;
      codigosistemavelho:=strtoint(lblsa.text);
      buscanacombo(fdquerysql4.fieldbyname('descricao').asstring,frmusuariosadm,cbosistemas);
      frmusuariosadm.Refresh;
      controlesistema:='ALTERAÇÃO';
      cbosistemas.SetFocus;
      exit;
   end;
end;

procedure Tfrmusuariosadm.lblnomeuserKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lblogin.setfocus;
end;

procedure Tfrmusuariosadm.lbloginKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_return then
      cbosistemas.SetFocus;
end;

procedure Tfrmusuariosadm.chkflagativoClick(Sender: TObject);
begin
   if chkflagativo.Checked = true then
      flagativo:='A'
   else if chkflagativo.Checked = false then
      flagativo:='';
end;

end.
