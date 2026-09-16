unit unt_matchcode;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, ExtCtrls, Buttons, ComCtrls, Vcl.Mask;

type
  Tfrmmatchcode = class(TForm)
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spblimpar: TSpeedButton;
    spbdeletar: TSpeedButton;
    spblocalizar: TSpeedButton;
    spbsair: TSpeedButton;
    lblf10: TLabel;
    lblmsg3: TLabel;
    lblf5: TLabel;
    StatusBar1: TStatusBar;
    lblorigem: TLabeledEdit;
    lbldestino: TLabeledEdit;
    spbuscaorigem: TSpeedButton;
    spbuscadestino: TSpeedButton;
    lblnomeorigem: TLabel;
    lblnomedestino: TLabel;
    memoresultado: TMemo;
    grpprincipal: TGroupBox;
    lblstatus: TLabeledEdit;
    lblstatusfunc1: TLabeledEdit;
    procedure spbsairClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spblimparClick(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure spbuscaorigemClick(Sender: TObject);
    procedure spbuscadestinoClick(Sender: TObject);
    procedure spbsalvarClick(Sender: TObject);
    procedure lbldestinoEnter(Sender: TObject);
    procedure lblorigemKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lbldestinoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  frmmatchcode: Tfrmmatchcode;

implementation

uses funcoes, unt_dados, unt_consultav3, unt_principal, unt_logon;

{$R *.dfm}

procedure Tfrmmatchcode.spbsairClick(Sender: TObject);
begin
   close;
end;

procedure Tfrmmatchcode.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
   action:=cafree;
end;

procedure Tfrmmatchcode.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f10 then
      spbsair.Click;
   //
   if key = vk_f4 then
      spbuscaorigem.Click;
   //
   if key = vk_f5 then
      spbuscadestino.Click;
end;

procedure Tfrmmatchcode.spblimparClick(Sender: TObject);
begin
   lblorigem.Clear; lbldestino.Clear;
   lblnomeorigem.Caption := ''; lblnomedestino.Caption :='';
   lblorigem.SetFocus;
end;

procedure Tfrmmatchcode.FormActivate(Sender: TObject);
begin
   statusbar1.Panels[1].Text :=configura_statusbar('a');
   statusbar1.Panels[3].Text := modulo_dados.fdbanco.params.database;
   statusbar1.Refresh;
   lblorigem.SetFocus;
end;

procedure Tfrmmatchcode.spbuscaorigemClick(Sender: TObject);
begin
   with frmprincipal, modulo_dados do
   begin
      {montar a consulta e colocar abaixo}
      sql:='SELECT * FROM usuarios WHERE flagativo = :flagativo';
      sql:=sql+' ORDER BY nome ASC';
      fdquerysql6.Close;
      fdquerysql6.SQL.Clear;
      fdquerysql6.SQL.Text := sql;
      fdquerysql6.ParamByName('flagativo').AsString := 'A';
      if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            frmconsulta3.controle:='USUARIO-ORIGEM';
            frmconsulta3.gridconsulta.DataSource := dtsfdquerysql6;
            frmconsulta3.ShowModal;
         end;
   end;
end;

procedure Tfrmmatchcode.spbuscadestinoClick(Sender: TObject);
begin
   with frmprincipal,modulo_dados do
   begin
      {montar a consulta e colocar abaixo}
      sql:='SELECT * FROM usuarios WHERE flagativo = :flagativo';
      sql:=sql+' ORDER BY nome ASC';
      fdquerysql6.Close;
      fdquerysql6.SQL.Clear;
      fdquerysql6.SQL.Text := sql;
      fdquerysql6.ParamByName('flagativo').AsString := 'A';

      if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            frmconsulta3.controle:='USUARIO-DESTINO';

            frmconsulta3.gridconsulta.DataSource := dtsfdquerysql6;
            frmconsulta3.ShowModal;
         end;
   end;
end;

procedure Tfrmmatchcode.spbsalvarClick(Sender: TObject);
begin
   with frmprincipal, modulo_dados do
   begin
      if lblorigem.Text = lbldestino.Text then
         begin
            messagedlg('VOCÊ NÃO PODE TRANSFERIR UM FUNCIONÁRIO PARA ELE MESMO COM MESMO CÓDIGO, OPERAÇÃO RECUSADA',mterror,[mbok],0);
            spblimpar.Click;
            lblorigem.SetFocus;
            exit;
         end;
      //
      if ((lblorigem.text <> '') and (lbldestino.text = '') or ((lblorigem.text = '') and (lbldestino.text <> '')))  then
         begin
            messagedlg('É NECESSÁRIO PREENCHER USUÁRIO DE ORIGEM E DESTINO PARA PROSSEGUIR !!!',mterror,[mbok],0);
            lblorigem.setfocus;
            exit;
         end;
      //
      if (lbldestino.Text <> '') and (lblnomedestino.Caption = 'Nome Usuário Destino') then
         begin
             with modulo_dados do
             begin
                 sql:='SELECT nome, flagativo FROM usuarios WHERE codigo_usuario = :codigousuario';
                 fdquerysql2.Close;
                 fdquerysql2.SQL.Clear;
                 fdquerysql2.SQL.Text := sql;
                 fdquerysql2.ParamByName('codigousuario').AsString :=lbldestino.Text;
                 if executaracao(fdquerysql2, fdbanco, true, dtsfdquerysql2) then
                    begin
                       lblnomedestino.Caption := fdquerysql2.fieldbyname('nome').asstring;
                       lblstatusfunc1.Text := fdquerysql2.fieldbyname('flagativo').asstring;
                       lblnomedestino.Refresh; lblstatusfunc1.Refresh;
                    end
                 else
                    begin
                       messagedlg('Código de Usuário não foi encontrado !!!',mterror,[mbok],0);
                       lblorigem.SetFocus;
                       exit;
                    end;
             end;
         end;
      //
      resp:=messagedlg('Confirma a Transferência de dados entre estes usuários ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
      if resp = idyes  then
         begin
            {aqui deve-se programar a execução dos updates no banco transferindo os registros do código de origem para o código de destino}
            memoresultado.Lines.add('TRANSFERÊNCIA DE MOVIMENTAÇÃO DE USUÁRIOS ');
            memoresultado.lines.add('                                                                                        ');
            memoresultado.lines.add('                                                                                        ');
            memoresultado.lines.add('                                                                                        ');
            sql:='UPDATE sclpabx_ligacoes SET codigo_usuario = :codigousuariodestino WHERE codigo_usuario = :codigousuarioorigem';
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('codigousuariodestino').AsString :=lbldestino.Text;
            fdquerysql3.ParamByName('codigousuarioorigem').AsString := lblorigem.Text;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  memoresultado.Lines.add('ATUALIZANDO TABELA DE LIGAÇÕES TELEFONICAS - REGISTROS AFETADOS '+inttostr(fdquerysql3.RowsAffected) );
               end;
            //
            sql:='UPDATE geoapolo_permissaoconsulta SET codigo_usuario = :codigousuariodestino WHERE codigo_usuario = :codigousuarioorigem';
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('codigousuariodestino').AsString :=lbldestino.Text;
            fdquerysql3.ParamByName('codigousuarioorigem').AsString := lblorigem.Text;

            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  memoresultado.Lines.add('ATUALIZANDO TABELA DE PERMISSÃO EM CONSULTAS - REGISTROS AFETADOS '+inttostr(fdquerysql3.RowsAffected) );
               end;
            //
            sql:='UPDATE int_adm_usrgrp SET codigo_usuario = :codigousuariodestino WHERE codigo_usuario = :codigousuarioorigem';
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('codigousuariodestino').AsString :=lbldestino.Text;
            fdquerysql3.ParamByName('codigousuariorigem').AsString := lblorigem.Text;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  memoresultado.Lines.add('ATUALIZANDO TABELA DE GRUPOS ADMINISTRATIVOS GEOAPOLO2 - REGISTROS AFETADOS '+inttostr(fdquerysql3.RowsAffected) );
               end;
            //
            sql:='DELETE FROM sclpabx_ramaisfuncionarios WHERE codigo_usuario =:codigousuariodestino';
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('codigousuariodestino').AsString :=lbldestino.Text;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
               end;

            sql:='UPDATE sclpabx_ramaisfuncionarios SET codigo_usuario = :codigousuariodestino WHERE codigo_usuario = :codigousuarioorigem';
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('codigousuariodestino').AsString :=lbldestino.Text;
            fdquerysql3.ParamByName('codigousuarioorigem').AsString := lblorigem.Text;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  memoresultado.Lines.add('ATUALIZANDO TABELA DE LIGAÇÕES TELEFONICAS - REGISTROS AFETADOS '+inttostr(fdquerysql3.RowsAffected) );
               end;
            //
            sql:='UPDATE geoapoloscl_periodo SET codigo_usuariomaior = :codigousuariodestino WHERE codigo_usuariomaior = :codigousuarioorigem';
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('codigousuariodestino').AsString :=lbldestino.Text;
            fdquerysql3.ParamByName('codigousuariorigem').AsString := lblorigem.Text;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  memoresultado.Lines.add('ATUALIZANDO TABELA DE ABERTURA E FECHAMENTO DE PERÍODO DE CONTAS NO PABX - REGISTROS AFETADOS '+inttostr(fdquerysql3.RowsAffected) );
               end;
            //
            {ANTES DE ATUALIZAR VERIFICA SE EXISTE DO NOVO, CASO EXISTA DEVE PERMANECER}
            sql:='SELECT * FROM geoapolo_grupousuario WHERE codigo_usuario = :codigousuariodestino';
            fdquerysql2.Close;
            fdquerysql2.SQL.Text := sql;
            fdquerysql2.ParamByName('codigousuariodestino').AsString := lbldestino.text;
            if executaracao(fdquerysql2, fdbanco, true, dtsfdquerysql2) then
               begin
                  sql:='UPDATE geoapolo_grupousuario SET codigo_usuario = :codigousuariodestino WHERE codigo_usuario = :codigousuarioorigem';
                  fdquerysql3.close;
                  fdquerysql3.SQL.Clear;
                  fdquerysql3.SQL.Text := sql;
                  fdquerysql3.ParamByName('codigousuariodestino').AsString := lbldestino.Text ;
                  fdquerysql3.ParamByName('codigousuariooriegem').AsString := lblorigem.Text;
                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                     begin
                        memoresultado.Lines.add('ATUALIZANDO TABELA DE ABERTURA E FECHAMENTO DE PERÍODO DE CONTAS NO PABX - REGISTROS AFETADOS '+inttostr(fdquerysql3.RowsAffected) );
                     end;
               end
            else
               begin
                  sql:='DELETE FROM geoapolo_grupousuario WHERE codigo_usuario = :codigousuariooriegem';
                  fdquerysql3.close;
                  fdquerysql3.SQL.Clear;
                  fdquerysql3.SQL.Text := sql;
                  fdquerysql3.ParamByName('codigousuariooriegem').AsString := lblorigem.Text ;

                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                     memoresultado.lines.add('ATUALIZANDO TABELA DE ABERTURA E FECHAMENTO DE PERÍODO DE CONTAS NO PABX - REGISTROS AFETADOS '+inttostr(fdquerysql3.RowsAffected));
               end;
            //
            sql:='UPDATE geoapolo_grupoemail SET codigo_usuario = :codigousuariodestino WHERE codigo_usuario = :codigousuarioorigem';
            fdquerysql3.close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('codigousuariodestino').AsString := lbldestino.Text ;
            fdquerysql3.ParamByName('codigousuarioorigem').AsString := lblorigem.Text;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  memoresultado.Lines.add('ATUALIZANDO TABELA DE GRUPOS DE EMAIL - REGISTROS AFETADOS '+inttostr(fdquerysql3.RowsAffected) );
               end;
            //
            sql:='UPDATE geoapolo_logatividades SET codigo_usuario = :codigousuariodestino WHERE codigo_usuario = :codigousuarioorigem';
            fdquerysql3.close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('codigousuariodestino').AsString := lbldestino.Text ;
            fdquerysql3.ParamByName('codigousuarioorigem').AsString := lblorigem.Text;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  memoresultado.Lines.add('ATUALIZANDO TABELA DE LOG DE ATIVIDADES DO GEOAPOLO - REGISTROS AFETADOS '+inttostr(fdquerysql3.RowsAffected) );
               end;
            //
            sql:='UPDATE geoapolo_sag_permissaocontato SET codigo_usuario = :codigousuariodestino WHERE codigo_usuario = '+lblorigem.Text;
            fdquerysql3.close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('codigousuariodestino').AsString := lbldestino.Text ;
            fdquerysql3.ParamByName('codigousuarioorigem').AsString := lblorigem.Text;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  memoresultado.Lines.add('ATUALIZANDO TABELA DE PERMISSÃO DE ACESSOS AOS CONTATOS DA AGENDA - REGISTROS AFETADOS '+inttostr(fdquerysql3.RowsAffected) );
               end;
            //
            sql:='UPDATE sag_contatos2  SET codigo_usuario_ultatu = :codigousuariodestino WHERE codigo_usuario_ultatu = :codigousuariorigem';
            fdquerysql3.close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('codigousuariodestino').AsString := lbldestino.Text ;
            fdquerysql3.ParamByName('codigousuarioorigem').AsString := lblorigem.Text;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  memoresultado.Lines.add('ATUALIZANDO TABELA DE CONTATOS DA AGENDA - REGISTROS AFETADOS '+inttostr(fdquerysql3.RowsAffected) );
               end;
            //
            {ANTES DE ALTERAR VERIFICA SE JÁ EXISTE DO NOVO, CASO EXISTIR PREVALECE}
            sql:='SELECT * FROM usuarios_sistemas WHERE codigo_usuario = :codigousuariodestino';
            fdquerysql2.Close;
            fdquerysql2.SQL.Clear;
            fdquerysql2.sql.Text := sql;
            fdquerysql2.ParamByName('codigousuariodestino').AsString := lbldestino.text;
            if executaracao(fdquerysql2, fdbanco, true, dtsfdquerysql2) then
               begin
                  sql:='UPDATE usuarios_sistemas SET codigo_usuario = :codigousuariodestino WHERE codigo_usuario = :codigousuariorigem';
                  fdquerysql3.close;
                  fdquerysql3.SQL.Clear;
                  fdquerysql3.SQL.Text := sql;
                  fdquerysql3.ParamByName('codigousuariodestino').AsString := lbldestino.Text ;
                  fdquerysql3.ParamByName('codigousuarioorigem').AsString := lblorigem.Text;
                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                     begin
                        memoresultado.Lines.add('ATUALIZANDO TABELA DE VINCULO ENTRE USUÁRIOS E SISTEMAS - REGISTROS AFETADOS '+inttostr(fdquerysql3.RowsAffected) );
                     end;
               end
            else
               begin
                  sql:='DELETE FROM usuarios_sistemas WHERE codigo_usuario = :codigousuariorigem';
                  fdquerysql3.close;
                  fdquerysql3.SQL.Clear;
                  fdquerysql3.SQL.Text := sql;
                  fdquerysql3.ParamByName('codigousuariorigem').AsString := lbldestino.Text ;
                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                     memoresultado.Lines.add('ATUALIZANDO TABELA DE VINCULO ENTRE USUÁRIOS E SISTEMAS - REGISTROS AFETADOS '+inttostr(fdquerysql3.RowsAffected) );
               end;
            //
            sql:='UPDATE scdisco_emprestimo SET codigo_usuario = :codigousuariodestino ';
            sql:=sql+' WHERE codigo_usuario = :codigousuariorigem';
            fdquerysql3.close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('codigousuariodestino').AsString := lbldestino.Text ;
            fdquerysql3.ParamByName('codigousuarioorigem').AsString := lblorigem.Text;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  memoresultado.lines.add('ATUALIZANDO A TABELA DE EMPRÉSTIMOS DE CD DA DISCOTECA - REGISTROS AFETADOS '+inttostr(fdquerysql3.RowsAffected));
               end;
            //
            //
            sql:='UPDATE geoapolo_usuariocateg SET codigo_usuario = :codigousuariodestino WHERE codigo_usuario = :codigousuariorigem';
            fdquerysql3.close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('codigousuariodestino').AsString := lbldestino.Text ;
            fdquerysql3.ParamByName('codigousuarioorigem').AsString := lblorigem.Text;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  memoresultado.lines.add('ATUALIZANDO A TABELA DE CATEGORIAS DE ENTIDADE COM USUÁRIOS - REGISTROS AFETADOS '+inttostr(fdquerysql3.RowsAffected));
               end;
            //
            sql:='DELETE FROM usuarios WHERE codigo_usuario = :codigousuariorigem';
            fdquerysql3.close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('codigousuariodestino').AsString := lbldestino.Text ;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                 messagedlg('USUÁRIO DE ORIGEM TRANSFERIDO COM SUCESSO PARA O DESTINO !!!',mtinformation,[mbok],0);
                  exit;
               end;
            spblimpar.Click;
            lblorigem.SetFocus;
            memoresultado.Refresh;
         end;
   end;
end;

procedure Tfrmmatchcode.lbldestinoEnter(Sender: TObject);
begin
   if (lblorigem.Text <> '') and (lblnomeorigem.Caption = 'Nome Usuário Origem') then
      begin
         with modulo_dados do
         begin
             sql:='SELECT nome, flagativo FROM usuarios WHERE codigo_usuario = :codigousuariorigem';
             fdquerysql2.close;
             fdquerysql2.SQL.Clear;
             fdquerysql2.SQL.Text := sql;
             fdquerysql2.ParamByName('codigousuariodestino').AsString := lbldestino.Text ;
             if executaracao(fdquerysql2, fdbanco, true, dtsfdquerysql2) then
                begin
                   lblnomeorigem.Caption := fdquerysql2.fieldbyname('nome').asstring;
                   lblstatus.Text := fdquerysql2.fieldbyname('flagativo').asstring;
                   lblnomeorigem.Refresh; lblstatus.Refresh;
                   lbldestino.SetFocus;
                end
             else
                begin
                   messagedlg('Código de Usuário não foi encontrado !!!',mterror,[mbok],0);
                   lblorigem.SetFocus;
                   exit;
                end;
         end;
      end;
end;

procedure Tfrmmatchcode.lblorigemKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      lbldestino.SetFocus;
end;

procedure Tfrmmatchcode.lbldestinoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      spbsalvar.Click;
end;

end.








