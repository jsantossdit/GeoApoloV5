unit unt_matchcode_contato;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, ExtCtrls, Buttons, ComCtrls;

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

uses funcoes, unt_dados, unt_consulta, unt_principal, unt_logon;

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
   statusbar1.Panels[3].Text := modulo_dados.zbanco.Database ;
   statusbar1.Refresh;
   lblorigem.SetFocus;
end;

procedure Tfrmmatchcode.spbuscaorigemClick(Sender: TObject);
begin
   with frmprincipal, modulo_dados do
   begin
      {montar a consulta e colocar abaixo}
      sql:='select * from usuarios where flagativo = '+chr(39)+'A'+chr(39);
      sql:=sql+' order by nome asc';
      executaracao(sql,zquerysql6);
      if zquerysql6.RecordCount > 0 then
         begin
            application.CreateForm(tfrmconsulta, frmconsulta);
            frmconsulta.controle:='USUARIO-ORIGEM';
            dtszquerysql6.DataSet :=zquerysql6;
            frmconsulta.gridconsulta.DataSource := dtszquerysql6;
            frmconsulta.ShowModal;
         end;
   end;
end;

procedure Tfrmmatchcode.spbuscadestinoClick(Sender: TObject);
begin
   with frmprincipal,modulo_dados do
   begin
      {montar a consulta e colocar abaixo}
      sql:='select * from usuarios where flagativo = '+chr(39)+'A'+chr(39);
      sql:='order by nome asc';
      executaracao(sql,zquerysql6);
      if zquerysql6.RecordCount > 0 then
         begin
            application.CreateForm(tfrmconsulta, frmconsulta);
            frmconsulta.controle:='USUARIO-DESTINO';
            dtszquerysql6.DataSet :=zquerysql6;
            frmconsulta.gridconsulta.DataSource := dtszquerysql6;
            frmconsulta.ShowModal;
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
      if (lbldestino.Text <> '') and (lblnomedestino.Caption = 'Nome Usuário Destino') then
         begin
             with modulo_dados do
             begin
                 sql:='SELECT nome, flagativo FROM usuarios WHERE codigo_usuario = '+lbldestino.Text;
                 executaracao(sql,zquerysql2);
                 if zquerysql2.RecordCount > 0 then
                    begin
                       lblnomedestino.Caption := zquerysql2.fieldbyname('nome').asstring;
                       lblstatusfunc1.Text := zquerysql2.fieldbyname('flagativo').asstring;
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
      {aqui deve-se programar a execução dos updates no banco transferindo os registros do código de origem para o código de destino}
      memoresultado.Lines.add('TRANSFERÊNCIA DE MOVIMENTAÇÃO DE USUÁRIOS ');
      memoresultado.lines.add('                                                                                        ');
      memoresultado.lines.add('                                                                                        ');
      memoresultado.lines.add('                                                                                        ');
      sql:='UPDATE sclpabx_ligacoes SET codigo_usuario = '+lbldestino.Text+ ' WHERE codigo_usuario = '+lblorigem.Text;
      executaracao(sql,zquerysql3);
      if zquerysql3.RowsAffected > 0 then
         begin
            memoresultado.Lines.add('ATUALIZANDO TABELA DE LIGAÇÕES TELEFONICAS - REGISTROS AFETADOS '+inttostr(zquerysql3.RowsAffected) );
         end;
      //
      sql:='UPDATE sclpabx_ramaisfuncionarios SET codigo_usuario = '+lbldestino.Text+' WHERE codigo_usuario = '+lblorigem.Text;
      executaracao(sql,zquerysql3);
      if zquerysql3.RowsAffected > 0 then
         begin
            memoresultado.Lines.add('ATUALIZANDO TABELA DE LIGAÇÕES TELEFONICAS - REGISTROS AFETADOS '+inttostr(zquerysql3.RowsAffected) );
         end;
      //
      sql:='UPDATE geoapoloscl_periodo SET codigo_usuariomaior = '+lbldestino.Text+' WHERE codigo_usuariomaior = '+lblorigem.Text;
      executaracao(sql,zquerysql3);
      if zquerysql3.RowsAffected > 0 then
         begin
            memoresultado.Lines.add('ATUALIZANDO TABELA DE ABERTURA E FECHAMENTO DE PERÍODO DE CONTAS NO PABX - REGISTROS AFETADOS '+inttostr(zquerysql3.RowsAffected) );
         end;
      //
      {ANTES DE ATUALIZAR VERIFICA SE EXISTE DO NOVO, CASO EXISTA DEVE PERMANECER}
      sql:='SELECT * FROM geoapolo_grupousuario WHERE codigo_usuario = '+lbldestino.text;
      executaracao(sql,zquerysql2);
      if zquerysql2.RecordCount <=0 then
         begin
            sql:='UPDATE geoapolo_grupousuario SET codigo_usuario = '+lbldestino.Text+' WHERE codigo_usuario = '+lblorigem.Text;
            executaracao(sql,zquerysql3);
            if zquerysql3.RowsAffected > 0 then
               begin
                  memoresultado.Lines.add('ATUALIZANDO TABELA DE ABERTURA E FECHAMENTO DE PERÍODO DE CONTAS NO PABX - REGISTROS AFETADOS '+inttostr(zquerysql3.RowsAffected) );
               end;
         end
      else
         begin
            sql:='DELETE FROM geoapolo_grupousuario WHERE codigo_usuario = '+lblorigem.text;
            executaracao(sql,zquerysql3);
            if zquerysql3.RowsAffected > 0 then
               memoresultado.lines.add('ATUALIZANDO TABELA DE ABERTURA E FECHAMENTO DE PERÍODO DE CONTAS NO PABX - REGISTROS AFETADOS '+inttostr(zquerysql3.RowsAffected));
         end;
      //
      sql:='UPDATE geoapolo_grupoemail SET codigo_usuario = '+lbldestino.Text+' WHERE codigo_usuario = '+lblorigem.Text;
      executaracao(sql,zquerysql3);
      if zquerysql3.RowsAffected > 0 then
         begin
            memoresultado.Lines.add('ATUALIZANDO TABELA DE GRUPOS DE EMAIL - REGISTROS AFETADOS '+inttostr(zquerysql3.RowsAffected) );
         end;
      //
      sql:='UPDATE geoapolo_logatividades SET codigo_usuario = '+lbldestino.Text+' WHERE codigo_usuario = '+lblorigem.Text;
      executaracao(sql,zquerysql3);
      if zquerysql3.RowsAffected > 0 then
         begin
            memoresultado.Lines.add('ATUALIZANDO TABELA DE LOG DE ATIVIDADES DO GEOAPOLO - REGISTROS AFETADOS '+inttostr(zquerysql3.RowsAffected) );
         end;
      //
      sql:='UPDATE geoapolo_sag_permissaocontato SET codigo_usuario = '+lbldestino.Text+' WHERE codigo_usuario = '+lblorigem.Text;
      executaracao(sql,zquerysql3);
      if zquerysql3.RowsAffected > 0 then
         begin
            memoresultado.Lines.add('ATUALIZANDO TABELA DE PERMISSÃO DE ACESSOS AOS CONTATOS DA AGENDA - REGISTROS AFETADOS '+inttostr(zquerysql3.RowsAffected) );
         end;
      //
      sql:='UPDATE sag_contatos2  SET codigo_usuario_ultatu = '+lbldestino.Text+' WHERE codigo_usuario_ultatu = '+lblorigem.Text;
      executaracao(sql,zquerysql3);
      if zquerysql3.RowsAffected > 0 then
         begin
            memoresultado.Lines.add('ATUALIZANDO TABELA DE CONTATOS DA AGENDA - REGISTROS AFETADOS '+inttostr(zquerysql3.RowsAffected) );
         end;
      //
      {ANTES DE ALTERAR VERIFICA SE JÁ EXISTE DO NOVO, CASO EXISTIR PREVALECE}
      sql:='SELECT * FROM usuarios_sistemas WHERE codigo_usuario = '+lbldestino.text;
      executaracao(sql,zquerysql2);
      if zquerysql2.RecordCount <=0 then
         begin
            sql:='UPDATE usuarios_sistemas SET codigo_usuario = '+lbldestino.Text+' WHERE codigo_usuario = '+lblorigem.Text;
            executaracao(sql,zquerysql3);
            if zquerysql3.RowsAffected > 0 then
               begin
                  memoresultado.Lines.add('ATUALIZANDO TABELA DE VINCULO ENTRE USUÁRIOS E SISTEMAS - REGISTROS AFETADOS '+inttostr(zquerysql3.RowsAffected) );
               end;
         end
      else
         begin
            sql:='DELETE FROM usuarios_sistemas WHERE codigo_usuario = '+lblorigem.text;
            executaracao(sql,zquerysql3);
            if zquerysql3.RowsAffected > 0  then
               memoresultado.Lines.add('ATUALIZANDO TABELA DE VINCULO ENTRE USUÁRIOS E SISTEMAS - REGISTROS AFETADOS '+inttostr(zquerysql3.RowsAffected) );
         end;
      //
      sql:='UPDATE scdisco_emprestimo SET codigo_usuario = '+lbldestino.Text+' WHERE codigo_usuario = '+lblorigem.Text;
      executaracao(sql,zquerysql3);
      if zquerysql3.RowsAffected > 0 then
         begin
            memoresultado.lines.add('ATUALIZANDO A TABELA DE EMPRÉSTIMOS DE CD DA DISCOTECA - REGISTROS AFETADOS '+inttostr(zquerysql3.RowsAffected));
         end;
      //
      if strtoint(lblorigem.Text) = frmlogon.codigousuario then
         begin
            sql:='DELETE FROM usuarios WHERE codigo_usuario = '+lblorigem.Text;
            executaracao(sql,zquerysql3);
            if zquerysql3.RowsAffected > 0 then
               begin
                  frmlogon.codigousuario := strtoint(lbldestino.Text);
                  exit;
               end;
         end;
      //
      spblimpar.Click;
      lblorigem.SetFocus;
      memoresultado.Refresh;
   end;
end;

procedure Tfrmmatchcode.lbldestinoEnter(Sender: TObject);
begin
   if (lblorigem.Text <> '') and (lblnomeorigem.Caption = 'Nome Usuário Origem') then
      begin
         with modulo_dados do
         begin
             sql:='SELECT nome, flagativo FROM usuarios WHERE codigo_usuario = '+lblorigem.Text;
             executaracao(sql,zquerysql2);
             if zquerysql2.RecordCount > 0 then
                begin
                   lblnomeorigem.Caption := zquerysql2.fieldbyname('nome').asstring;
                   lblstatus.Text := zquerysql2.fieldbyname('flagativo').asstring;
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
