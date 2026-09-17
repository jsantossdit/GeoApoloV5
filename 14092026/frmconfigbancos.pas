unit frmconfigbancos;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, ExtCtrls, Buttons, Registry, ComCtrls, Grids, Vcl.Mask,
  unt_configbanco_types, unt_configbanco_repository, unt_configbanco_service;

type
  Tfrmconfigbanco = class(TForm)
    Panel1: TPanel;
    spbsalvar: TSpeedButton;
    spblimpar: TSpeedButton;
    spbconectabanco: TSpeedButton;
    spbexcluir: TSpeedButton;
    spbretornar: TSpeedButton;
    lblsair: TLabel;
    StatusBar1: TStatusBar;
    cin1: TPageControl;
    tab_bancogeo: TTabSheet;
    GroupBox1: TGroupBox;
    Label1: TLabel;
    lblsenha: TLabeledEdit;
    lblnomeservidor: TLabeledEdit;
    lblbancopost: TLabeledEdit;
    cboprotocolo: TComboBox;
    gridconfig: TStringGrid;
    OpenDialog1: TOpenDialog;
    lblusuariobanco1: TLabeledEdit;
    procedure spbretornarClick(Sender: TObject);
    procedure spbsalvarClick(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure spbexcluirClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure lblbancopostKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure FormKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblsenhaKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblnomeservidorKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cboprotocoloKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure gridconfigDblClick(Sender: TObject);
    procedure gridconfigKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbopendirClick(Sender: TObject);
    procedure lblusuariobanco1KeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
  private
    { Private declarations }
  public
    { Public declarations }
    i:integer;
  end;

var
  frmconfigbanco: Tfrmconfigbanco;
  resp:word;

implementation

uses unt_principal, unt_dados, funcoes;

{$R *.dfm}

procedure Tfrmconfigbanco.spbretornarClick(Sender: TObject);
begin
   application.Terminate;
end;

procedure Tfrmconfigbanco.spbsalvarClick(Sender: TObject);
var
   registro:tregistry;
begin
   resp:=messagedlg('Confirma as Configurações do banco ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
   if resp = idyes then
      begin
         registro:=tregistry.create;
         {ROTINA ABAIXO CONFIGURA OS DADOS PARA ACESSO USANDO ADO NO SQL SERVER DO APOLO}
         try
            registro.rootkey := HKEY_CURRENT_USER;
            if not registro.OpenKey('sdit\configuracoes\DataBase',false) then
               begin
                  registro.CreateKey ('sdit\configuracoes\DataBase');
                  if not registro.OpenKey('sdit\configuracoes\DataBase',False) then
                     ShowMessage('FALHA NA CRIAÇÃO DA CHAVE NO REGISTRO')
                  else
                     begin
                        if cboprotocolo.Text = 'TCPIP' then
                           begin
                              registro.WriteString('Senha do Banco SQL',criptografia(40,lblsenha.text));
                              registro.WriteString('ProtocoloSQL',cboprotocolo.text);
                              registro.WriteString('Nome do ServidorSQL',lblnomeservidor.text);
                              registro.WriteString('IP do ServidorSQL',lblnomeservidor.text);
                              registro.WriteString('Usuario MSSQL',lblusuariobanco1.text);
                              registro.WriteString('NomeBancoSQL',lblbancopost.text);
                           end ;
                     end;
               end
            else
               begin
                  if cboprotocolo.Text = 'TCPIP' then
                     begin
                        registro.WriteString('Senha do Banco SQL',criptografia(40,lblsenha.text));
                        registro.WriteString('ProtocoloSQL',cboprotocolo.text);
                        registro.WriteString('Nome do ServidorSQL',lblnomeservidor.text);
                        registro.WriteString('IP do ServidorSQL',lblnomeservidor.text);
                        registro.WriteString('Usuario MSSQL',lblusuariobanco1.text);
                        registro.WriteString('NomeBancoSQL',lblbancopost.text);
                        // - BANCO DE DADOS DO MIX
                        registro.WriteString('BancoMIX','Mix')
                     end ;
               end;
         finally
         end;
         if cboprotocolo.text = 'MySQL' then
            begin
               {AQUI FARÁ O SALVAMENTO DOS DADOS DE ACESSO AO APLICATIVO DA RCC BRASIL}
               registro.WriteString('Senha APP',criptografia(48,lblsenha.text));
               registro.WriteString('Protocolo APP',cboprotocolo.text);
               registro.WriteString('Nome do Servidor APP',criptografia(40,lblnomeservidor.text));
               registro.WriteString('IP do Servidor APP',criptografia(40,lblnomeservidor.text));
               registro.WriteString('Porta Comunicacao APP',criptografia(40,inputbox('Servidor de dados do APP','Informe a porta de Comunicação','')));
               registro.WriteString('Usuario admin APP',lblusuariobanco1.text);
               registro.WriteString('NomeBancoAPP',lblbancopost.text);
            end;
         gridconfig.Cells[0,i]:= lblnomeservidor.Text;
         gridconfig.Cells[1,i]:= lblbancopost.Text;
         gridconfig.Cells[2,i]:= cboprotocolo.Text;
         inc(i);
         gridconfig.Row:=i;
         registro.free;
         cin1.ActivePageIndex :=0; cin1.Refresh;
         messagedlg('DADOS GRAVADOS COM SUCESSO !!! QUANDO TERMINAR CLICK NO BOTÃO SAIR PARA QUE AS CONFIGURAÇÕES SEJAM CARREGADAS',mtinformation,[mbok],0);
         spblimpar.Click;
      end;
end;

procedure Tfrmconfigbanco.spblimparClick(Sender: TObject);
begin
   lblnomeservidor.Clear; lblusuariobanco1.clear; lblsenha.Clear; cboprotocolo.ItemIndex := -1;
   lblbancopost.Clear;
   lblbancopost.SetFocus;
end;

procedure Tfrmconfigbanco.FormActivate(Sender: TObject);
var
   registro:tregistry;
begin
   // rotina para ler os dados do Registro
   i:=1;
   cin1.ActivePageIndex :=0; cin1.Refresh;
   registro:=tregistry.Create ;
   // CORRIGIDO: só cria frmprincipal se ainda não existir
   if not FormEstaCriado(Tfrmprincipal) then
    Application.CreateForm(Tfrmprincipal, frmprincipal);

   registro.RootKey := HKEY_CURRENT_USER;
   if not registro.KeyExists ('sdit\configuracoes\DataBase') then
       begin
         // messagedlg('O SISTEMA ESTÁ SEM CONFIGURAÇÕES PARA O BANCO DE DADOS MS-SQL SERVER 2005 - CONFIGURAR SISTEMAS',mtinformation,[mbok],0);
       end
    else
       begin
          registro.OpenKey('sdit\configuracoes\DataBase', false);
          frmprincipal.nomeserversql :=registro.ReadString('Nome do ServidorSQL');
          frmprincipal.nomebancosql:= registro.ReadString('NomeBancoSQL');
          frmprincipal.ipserversql:=registro.ReadString('IP do ServidorSQL');
          //usuariobancosql:=decriptografia(40,registro.ReadString('Usuario MSSQL'),'');
          frmprincipal.usuariobancosql:=registro.ReadString('Usuario MSSQL');
          frmprincipal.senhasql:=registro.readstring('Senha do Banco SQL');
          frmprincipal.protocolo:=registro.readstring('ProtocoloADO');
          buscanacombo(registro.readstring('Protocolo'),frmconfigbanco,cboprotocolo);
          //-------------------------------------------------------------------------------//
          // DADOS DO SERVIDOR MYSQL DO APLICATIVO
          //servidorapp,portacomunicacao,nomebancoapp,usuarioapp,senhaapp:string;
            //
            gridconfig.Cells[0,0]:='Nome Servidor';
            gridconfig.Cells[1,0]:='Banco de dados';
            gridconfig.Cells[2,0]:='Protocolo';
            //
            gridconfig.Cells[0,1]:=frmprincipal.nomeserversql;
            gridconfig.Cells[1,1]:=frmprincipal.nomebancosql;
            gridconfig.Cells[2,1]:=frmprincipal.protocolo ;
            gridconfig.Refresh;
            cin1.Refresh;
            registro.CloseKey;
         end;
       registro.Free;
end;

procedure Tfrmconfigbanco.spbexcluirClick(Sender: TObject);
var
   registro:tregistry;
begin
   resp:=messagedlg('Confirma a exclusão das Configurações do banco ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
   if resp = idyes then
      begin
         registro:=tregistry.Create;
         registro.DeleteKey('sdit\configuracoes\DataBase');
         messagedlg('Configurações excluídas com sucesso !!!',mtinformation,[mbok],0);
         spbretornar.Click;
      end
   else
      lblnomeservidor.SetFocus;
end;

procedure Tfrmconfigbanco.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
   action :=cafree;
end;

procedure Tfrmconfigbanco.lblbancopostKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lblusuariobanco1.SetFocus;
end;

procedure Tfrmconfigbanco.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f10 then
      spbretornar.Click;
end;

procedure Tfrmconfigbanco.lblsenhaKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_return then
      lblnomeservidor.SetFocus;
end;

procedure Tfrmconfigbanco.lblnomeservidorKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if key = vk_return then
      cboprotocolo.SetFocus;
end;

procedure Tfrmconfigbanco.cboprotocoloKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_return then
      spbsalvar.Click;
end;

procedure Tfrmconfigbanco.gridconfigDblClick(Sender: TObject);
begin
   with frmconfigbanco do
   begin
      lblnomeservidor.Text := gridconfig.Cells[0,gridconfig.row];
      lblbancopost.Text :=gridconfig.Cells[1,gridconfig.row];
      buscanacombo(gridconfig.Cells[2,gridconfig.row],frmconfigbanco,cboprotocolo);
      frmconfigbanco.Refresh;
      lblbancopost.SetFocus;
   end;
end;

procedure Tfrmconfigbanco.gridconfigKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_delete then
      spbexcluir.Click;
end;

procedure Tfrmconfigbanco.spbopendirClick(Sender: TObject);
begin
   opendialog1.Execute ;
end;

procedure Tfrmconfigbanco.lblusuariobanco1KeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      lblsenha.setfocus;
end;

end.
