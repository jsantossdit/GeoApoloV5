unit unt_matchcodecontato;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.ExtCtrls, Vcl.ComCtrls,
  Vcl.StdCtrls, Vcl.Buttons, Vcl.Mask;

type
  TfrmMatchContato = class(TForm)
    grpprincipal: TGroupBox;
    spbuscaorigem: TSpeedButton;
    spbuscadestino: TSpeedButton;
    lblnomeorigem: TLabel;
    lblnomedestino: TLabel;
    lblorigem: TLabeledEdit;
    lbldestino: TLabeledEdit;
    memoresultado: TMemo;
    StatusBar1: TStatusBar;
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spblimpar: TSpeedButton;
    spbdeletar: TSpeedButton;
    spblocalizar: TSpeedButton;
    spbsair: TSpeedButton;
    lblf10: TLabel;
    lblmsg3: TLabel;
    procedure spbsairClick(Sender: TObject);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblorigemKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lbldestinoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbuscaorigemClick(Sender: TObject);
    procedure spbuscadestinoClick(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure spbsalvarClick(Sender: TObject);
    procedure lbldestinoEnter(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  frmMatchContato: TfrmMatchContato;
  resp:word;

implementation

{$R *.dfm}

uses unt_principal, funcoes, unt_dados, unt_consultav3, unt_logon;

procedure TfrmMatchContato.FormActivate(Sender: TObject);
begin
   statusbar1.panels[1].text := configura_statusbar('a');
   statusbar1.panels[3].text := configura_statusbar('a');
   statusbar1.Panels[5].text := frmprincipal.nomeserversql;
   statusbar1.refresh;
end;

procedure TfrmMatchContato.FormClose(Sender: TObject; var Action: TCloseAction);
begin
   action:=cafree;
end;

procedure TfrmMatchContato.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f10  then
      spbsair.click;
end;

procedure TfrmMatchContato.lbldestinoEnter(Sender: TObject);
begin
   if (lblorigem.Text <> '') and (lblnomeorigem.Caption = 'Nome Contato Origem') then
      begin
         with modulo_dados do
         begin
             sql:='SELECT e.entnome FROM entidade e with(nolock) WHERE e.entcod =  :pentcodorigem';
             fdquerysql2.Close;
             fdquerysql2.SQL.Clear;
             fdquerysql2.SQL.Text := sql;
             fdquerysql2.ParamByName('pentcodorigem').AsString := lblorigem.Text;
             if executaracao(fdquerysql2, fdbanco, true, dtsfdquerysql2) then
                begin
                   lblnomeorigem.Caption := fdquerysql2.fieldbyname('entnome').asstring;
                   lblnomeorigem.Refresh;
                   lbldestino.SetFocus;
                end
             else
                begin
                   messagedlg('Código da Entidade não foi encontrado !!!',mterror,[mbok],0);
                   lblorigem.SetFocus;
                   exit;
                end;
         end;
      end;
end;

procedure TfrmMatchContato.lbldestinoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f4 then
      spbuscadestino.click;
   if (key = vk_tab) or (key = vk_return) then
      spbsalvar.click;
end;

procedure TfrmMatchContato.lblorigemKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f4 then
      spbuscaorigem.click;
   if (key = vk_tab) or (key = vk_return) then
      lbldestino.setfocus;
end;

procedure TfrmMatchContato.spblimparClick(Sender: TObject);
begin
   lblorigem.Clear; lbldestino.Clear;
   lblnomeorigem.Caption := 'Nome Contato Origem'; lblnomedestino.Caption :='Nome Contato Destino';
   lblorigem.SetFocus;
end;

procedure TfrmMatchContato.spbsairClick(Sender: TObject);
begin
   close;
end;

procedure TfrmMatchContato.spbsalvarClick(Sender: TObject);
var
   vusuarioapolo : string;
begin
   with modulo_dados, frmMatchContato do
   begin
      if lblorigem.text = lbldestino.text  then
         begin
            messagedlg('VOCÊ NÃO PODE TRANSFERIR UM CONTATO PARA O MESMO CÓDIGO !!!',mterror,[mbok],0);
            lblorigem.setfocus;
            exit;
         end;
      if (lbldestino.Text <> '') and (lblnomedestino.Caption = 'Nome Contato Destino') then
         begin
         end;
      //
      resp:=messagedlg('Confirma a Transferência de dados entre estes Contatos ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
      if resp = idyes  then
        begin
            {aqui deve-se programar a execução dos updates no banco transferindo os registros do código de origem para o código de destino}
            vusuarioapolo:='';
            sql:='SELECT usucod FROM usuario WHERE usunome = :pusunome';
            fdquerysql.Close;
            fdquerysql.sql.clear;
            fdquerysql.SQL.Text := sql;
            fdquerysql.ParamByName('pusunome').AsString:=frmlogon.nomecompletousuario;
            if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
               begin
                  vusuarioapolo:=fdquerysql.FieldByName('usucod').AsString;
               end;
            if vusuarioapolo = '' then
               begin
                  messagedlg('NÃO FOI ENCONTRADO O USUÁRIO APOLO PARA ESTE USUÁRIO DO GEOAPOLO, EXECUÇÃO NÃO SERÁ PERMITIDA !!!',mterror,[mbok],0);
                  exit;
               end;
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            sql:='execute TRANSF_MOV_ENTIDADE :pentorigem,:pentdestino,:pvalida,:pcodigoempresa, :puserapolo,'+'';
            fdquerysql3.ParamByName('pentorigem').AsString := lblorigem.Text;
            fdquerysql3.ParamByName('pentdestino').AsString := lbldestino.Text;
            fdquerysql3.ParamByName('pcodigoempresa').AsString :=  frmprincipal.codigo_empresa;
            fdquerysql3.ParamByName('pvalida').AsBoolean := false;
            fdquerysql3.ParamByName('puserapolo').AsString:= frmlogon.CodigoUsuario;
            fdquerysql3.SQL.Text := sql;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin

               end;
            fdquerysql.Close;
            fdquerysql.SQL.Clear;
            sql:='SELECT entcod FROM entidade WHERE entcod = :pentidadeorigem ';
            fdquerysql.SQL.Text := sql;
            fdquerysql.ParamByName('pentidadeorigem').AsString := lblorigem.Text;
            if not executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
               begin
                   messagedlg('ENTIDADE MESCLADA COM SUCESSO !!!',mtinformation,[mbok],0);
                   setcursorsql('');
                   spblimpar.Click;
               end
            else
              begin
                 messagedlg('OCORREU ALGUM ERRO AO TENTAR MESCLAR ESTA ENTIDADE !!!',mterror,[mbok],0);
                 lblorigem.SetFocus;
              end;
            memoresultado.Lines.add('Mesclagem finalizada ');
            memoresultado.lines.add('                                                                                        ');
            memoresultado.lines.add('                                                                                        ');
            memoresultado.lines.add('                                                                                        ');
            //
        end
   end;
end;

procedure TfrmMatchContato.spbuscadestinoClick(Sender: TObject);
var i:integer;
begin
   with frmprincipal, modulo_dados do
   begin
      {montar a consulta e colocar abaixo}
      sql:='SELECT EntCod, EntNome';
      sql:=sql+' FROM ENTIDADE with(nolock)';
      fdquerysql6.Close;
      fdquerysql6.SQL.Clear;
      fdquerysql6.SQL.Text := sql;
      if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            frmconsulta3.controle:='ENTIDADE-DESTINO';
            dtsfdquerysql6.DataSet :=fdquerysql6;
            for i:= 0 to fdquerysql6.fields.count -1 do
            begin
               frmconsulta3.cbocampo.items.add(fdquerysql6.fields[i].displayname);
               frmconsulta3.cbordem.items.add(fdquerysql6.fields[i].displayname);
            end;
            frmconsulta3.gridconsulta.DataSource := dtsfdquerysql6;
            frmconsulta3.ShowModal;
         end;
   end;
end;

procedure TfrmMatchContato.spbuscaorigemClick(Sender: TObject);
var i:integer;
begin
   with frmprincipal, modulo_dados do
   begin
      {montar a consulta e colocar abaixo}
      sql:='SELECT EntCod, EntNome';
      sql:=sql+' FROM ENTIDADE  with(nolock)';
      fdquerysql6.Close;
      fdquerysql6.SQL.clear;
      fdquerysql6.SQL.Text := sql;
      if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            frmconsulta3.controle:='ENTIDADE-ORIGEM';
            dtsfdquerysql6.DataSet :=fdquerysql6;
            for i:= 0 to fdquerysql6.fields.count -1 do
            begin
               frmconsulta3.cbocampo.items.add(fdquerysql6.fields[i].displayname);
               frmconsulta3.cbordem.items.add(fdquerysql6.fields[i].displayname);
            end;
            frmconsulta3.gridconsulta.DataSource := dtsfdquerysql6;
            frmconsulta3.ShowModal;
         end;
   end;
end;

end.
