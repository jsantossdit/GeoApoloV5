unit frmconfigbancos;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, ExtCtrls, Buttons, Registry, ComCtrls, Grids, Vcl.Mask,
  FireDAC.Comp.Client,
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
    tab_bancosavic: TTabSheet;
    GroupBoxSavic: TGroupBox;
    lblsavic_servidor: TLabeledEdit;
    lblsavic_porta: TLabeledEdit;
    lblsavic_banco: TLabeledEdit;
    lblsavic_usuario: TLabeledEdit;
    lblsavic_senha: TLabeledEdit;
    tab_bancoapp: TTabSheet;
    GroupBoxApp: TGroupBox;
    lblapp_servidor: TLabeledEdit;
    lblapp_porta: TLabeledEdit;
    lblapp_banco: TLabeledEdit;
    lblapp_usuario: TLabeledEdit;
    lblapp_senha: TLabeledEdit;
    procedure spbretornarClick(Sender: TObject);
    procedure spbsalvarClick(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure spbconectabancoClick(Sender: TObject);
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
    i: integer;
    AbaInicial: Integer;
  end;

var
  frmconfigbanco: Tfrmconfigbanco;
  resp:word;

implementation

uses unt_principal, unt_dados, funcoes;

{$R *.dfm}

procedure Tfrmconfigbanco.spbretornarClick(Sender: TObject);
begin
   Close;
end;

procedure Tfrmconfigbanco.spbconectabancoClick(Sender: TObject);
var
  FDConn: TFDConnection;
  nInicio: Cardinal;
begin
  FDConn := TFDConnection.Create(nil);
  try
    try
      nInicio := GetTickCount;
      if cin1.ActivePageIndex = 0 then
      begin
        FDConn.DriverName := 'MSSQL';
        FDConn.Params.Values['Server']                 := SanitizarNomeServidor(lblnomeservidor.Text);
        FDConn.Params.Values['Database']               := Trim(lblbancopost.Text);
        FDConn.Params.Values['User_Name']              := Trim(lblusuariobanco1.Text);
        FDConn.Params.Values['Password']               := lblsenha.Text;
        FDConn.Params.Values['Encrypt']                := 'No';
        FDConn.Params.Values['TrustServerCertificate'] := 'Yes';
        FDConn.Params.Values['MARS']                   := 'Yes';
        if (Trim(cboprotocolo.Text) <> '') and not (ServidorEhLocal(lblnomeservidor.Text) and (Pos('\', lblnomeservidor.Text) > 0)) then
          FDConn.Params.Values['Protocol'] := Trim(cboprotocolo.Text);
      end
      else if cin1.ActivePageIndex = 1 then
      begin
        FDConn.DriverName := 'MySQL';
        FDConn.Params.Values['Server']    := Trim(lblsavic_servidor.Text);
        FDConn.Params.Values['Database']  := Trim(lblsavic_banco.Text);
        FDConn.Params.Values['User_Name'] := Trim(lblsavic_usuario.Text);
        FDConn.Params.Values['Password']  := lblsavic_senha.Text;
        FDConn.Params.Values['Port']      := Trim(lblsavic_porta.Text);
      end
      else
      begin
        FDConn.DriverName := 'MySQL';
        FDConn.Params.Values['Server']    := Trim(lblapp_servidor.Text);
        FDConn.Params.Values['Database']  := Trim(lblapp_banco.Text);
        FDConn.Params.Values['User_Name'] := Trim(lblapp_usuario.Text);
        FDConn.Params.Values['Password']  := lblapp_senha.Text;
        FDConn.Params.Values['Port']      := Trim(lblapp_porta.Text);
      end;
      FDConn.LoginPrompt := False;
      FDConn.Connected := True;
      MessageDlg(Format('Conexão realizada com sucesso! (%d ms)', [GetTickCount - nInicio]), mtInformation, [mbOK], 0);
      FDConn.Connected := False;
    except
      on E: Exception do
      begin
        if cin1.ActivePageIndex = 0 then
          MessageDlg(TratarErroConexaoMSSQL(E, SanitizarNomeServidor(lblnomeservidor.Text), Trim(lblbancopost.Text)), mtError, [mbOK], 0)
        else
          MessageDlg('Falha na conexão: ' + E.Message, mtError, [mbOK], 0);
      end;
    end;
  finally
    FDConn.Free;
  end;
end;

procedure Tfrmconfigbanco.spbsalvarClick(Sender: TObject);
var
   registro: tregistry;
   nPorta: Integer;
begin
   resp := messagedlg('Confirma as Configurações do banco ? (Y/N)', mtconfirmation, [mbyes, mbno], 0);
   if resp = idyes then
   begin
      registro := tregistry.create;
      try
         registro.rootkey := HKEY_CURRENT_USER;
         if not registro.OpenKey('sdit\configuracoes\DataBase', True) then
         begin
            ShowMessage('FALHA NA ABERTURA DA CHAVE NO REGISTRO');
            Exit;
         end;

         if cin1.ActivePageIndex = 0 then
         begin
            lblnomeservidor.Text := SanitizarNomeServidor(lblnomeservidor.Text);
            // Configurações do SQL Server GeoAlvo / Alvo
            registro.WriteString('Senha do Banco SQL', criptografia(40, lblsenha.Text));
            registro.WriteString('ProtocoloSQL', cboprotocolo.Text);
            registro.WriteString('Nome do ServidorSQL', lblnomeservidor.Text);
            registro.WriteString('IP do ServidorSQL', lblnomeservidor.Text);
            registro.WriteString('Usuario MSSQL', Trim(lblusuariobanco1.Text));
            registro.WriteString('NomeBancoSQL', Trim(lblbancopost.Text));
            registro.WriteString('BancoMIX', 'Mix');

            if Assigned(frmprincipal) then
            begin
               frmprincipal.nomeserversql   := lblnomeservidor.Text;
               frmprincipal.nomebancosql    := Trim(lblbancopost.Text);
               frmprincipal.usuariobancosql := Trim(lblusuariobanco1.Text);
               frmprincipal.senhasql        := lblsenha.Text;
               frmprincipal.protocolo       := cboprotocolo.Text;
               conecta_banco('FDALVO');
            end;

            gridconfig.Cells[0, 1] := lblnomeservidor.Text;
            gridconfig.Cells[1, 1] := lblbancopost.Text;
            gridconfig.Cells[2, 1] := cboprotocolo.Text;
            gridconfig.Refresh;
         end
         else if cin1.ActivePageIndex = 1 then
         begin
            // Configurações do MySQL Savic Legado
            registro.WriteString('Nome do Servidor SAVIC', lblsavic_servidor.Text);
            registro.WriteString('IP do Servidor SAVIC', lblsavic_servidor.Text);
            registro.WriteString('NomeBancoSAVIC', lblsavic_banco.Text);
            registro.WriteString('Usuario admin SAVIC', lblsavic_usuario.Text);
            registro.WriteString('Senha SAVIC', lblsavic_senha.Text);
            registro.WriteString('Protocolo SAVIC', 'MySQL');
            try
               nPorta := StrToIntDef(lblsavic_porta.Text, 3306);
            except
               nPorta := 3306;
            end;
            registro.WriteInteger('Porta Comunicacao SAVIC', nPorta);
         end
         else if cin1.ActivePageIndex = 2 then
         begin
            // Configurações do MySQL Aplicativo RCC
            registro.WriteString('Nome do Servidor APP RCC', lblapp_servidor.Text);
            registro.WriteString('IP do Servidor APP RCC', lblapp_servidor.Text);
            registro.WriteString('NomeBancoAPP RCC', lblapp_banco.Text);
            registro.WriteString('Usuario admin APP RCC', lblapp_usuario.Text);
            registro.WriteString('Senha APP RCC', lblapp_senha.Text);
            registro.WriteString('Protocolo APP RCC', 'MySQL');
            try
               nPorta := StrToIntDef(lblapp_porta.Text, 3306);
            except
               nPorta := 3306;
            end;
            registro.WriteInteger('Porta Comunicacao APP RCC', nPorta);

            // Mantém também as chaves gerais e o objeto frmprincipal sincronizados
            registro.WriteString('Nome do Servidor APP', lblapp_servidor.Text);
            registro.WriteString('IP do Servidor APP', lblapp_servidor.Text);
            registro.WriteString('NomeBancoAPP', lblapp_banco.Text);
            registro.WriteString('Usuario admin APP', lblapp_usuario.Text);
            registro.WriteString('Senha APP', lblapp_senha.Text);
            registro.WriteString('Protocolo APP', 'MySQL');
            registro.WriteInteger('Porta Comunicacao APP', nPorta);

            if Assigned(frmprincipal) then
            begin
               frmprincipal.servidorapp      := lblapp_servidor.Text;
               frmprincipal.portacomunicacao := lblapp_porta.Text;
               frmprincipal.nomebancoapp     := lblapp_banco.Text;
               frmprincipal.usuarioapp       := lblapp_usuario.Text;
               frmprincipal.senhaapp         := lblapp_senha.Text;
            end;
         end;
         registro.CloseKey;
         messagedlg('DADOS GRAVADOS COM SUCESSO !!!', mtinformation, [mbok], 0);
      finally
         registro.free;
      end;
   end;
end;

procedure Tfrmconfigbanco.spblimparClick(Sender: TObject);
begin
   if cin1.ActivePageIndex = 0 then
   begin
      lblnomeservidor.Clear; lblusuariobanco1.clear; lblsenha.Clear; cboprotocolo.ItemIndex := -1;
      lblbancopost.Clear;
      lblbancopost.SetFocus;
   end
   else if cin1.ActivePageIndex = 1 then
   begin
      lblsavic_servidor.Clear;
      lblsavic_porta.Text := '3306';
      lblsavic_banco.Clear;
      lblsavic_usuario.Clear;
      lblsavic_senha.Clear;
      lblsavic_servidor.SetFocus;
   end
   else
   begin
      lblapp_servidor.Clear;
      lblapp_porta.Text := '3306';
      lblapp_banco.Clear;
      lblapp_usuario.Clear;
      lblapp_senha.Clear;
      lblapp_servidor.SetFocus;
   end;
end;

procedure Tfrmconfigbanco.FormActivate(Sender: TObject);
var
   registro:tregistry;
begin
   i := 1;
   if (AbaInicial >= 0) and (AbaInicial <= 2) then
      cin1.ActivePageIndex := AbaInicial
   else
      cin1.ActivePageIndex := 0;
   cin1.Refresh;

   if not FormEstaCriado(Tfrmprincipal) then
      Application.CreateForm(Tfrmprincipal, frmprincipal);

   // Valores padrão do Savic
   lblsavic_servidor.Text := '167.71.28.209';
   lblsavic_porta.Text    := '3333';
   lblsavic_banco.Text    := 'rccbrasilsavic';
   lblsavic_usuario.Text  := 'rccbrasilsavic';
   lblsavic_senha.Text    := 'b2J4earCJuNcM7';

   // Valores padrão do Aplicativo RCC
   lblapp_servidor.Text   := '';
   lblapp_porta.Text      := '3306';
   lblapp_banco.Text      := '';
   lblapp_usuario.Text    := '';
   lblapp_senha.Text      := '';

   registro := tregistry.Create;
   try
      registro.RootKey := HKEY_CURRENT_USER;
      if registro.OpenKey('sdit\configuracoes\DataBase', False) then
      begin
         // GeoAlvo SQL Server
         if registro.ValueExists('Nome do ServidorSQL') then
         begin
            frmprincipal.nomeserversql := SanitizarNomeServidor(registro.ReadString('Nome do ServidorSQL'));
            lblnomeservidor.Text := frmprincipal.nomeserversql;
         end;
         if registro.ValueExists('NomeBancoSQL') then
         begin
            frmprincipal.nomebancosql := Trim(registro.ReadString('NomeBancoSQL'));
            lblbancopost.Text := frmprincipal.nomebancosql;
         end;
         if registro.ValueExists('IP do ServidorSQL') then
            frmprincipal.ipserversql := SanitizarNomeServidor(registro.ReadString('IP do ServidorSQL'));
         if registro.ValueExists('Usuario MSSQL') then
         begin
            frmprincipal.usuariobancosql := Trim(registro.ReadString('Usuario MSSQL'));
            lblusuariobanco1.Text := frmprincipal.usuariobancosql;
         end;
         if registro.ValueExists('Senha do Banco SQL') then
         begin
            try
               frmprincipal.senhasql := decriptografia(40, registro.ReadString('Senha do Banco SQL'), '');
            except
               frmprincipal.senhasql := registro.ReadString('Senha do Banco SQL');
            end;
            if (registro.ReadString('Senha do Banco SQL') = 'semsenha') or (Trim(frmprincipal.senhasql) = '') then
               frmprincipal.senhasql := registro.ReadString('Senha do Banco SQL');
            lblsenha.Text := frmprincipal.senhasql;
         end;
         if registro.ValueExists('ProtocoloSQL') then
         begin
            frmprincipal.protocolo := registro.ReadString('ProtocoloSQL');
            buscanacombo(frmprincipal.protocolo, frmconfigbanco, cboprotocolo);
         end;

         // Savic MySQL
         if registro.ValueExists('Nome do Servidor SAVIC') and (Trim(registro.ReadString('Nome do Servidor SAVIC')) <> '') then
            lblsavic_servidor.Text := Trim(registro.ReadString('Nome do Servidor SAVIC'))
         else if registro.ValueExists('Nome do Servidor APP') and (Trim(registro.ReadString('Nome do Servidor APP')) <> '') then
            lblsavic_servidor.Text := Trim(registro.ReadString('Nome do Servidor APP'));

         if registro.ValueExists('Porta Comunicacao SAVIC') then
            lblsavic_porta.Text := IntToStr(registro.ReadInteger('Porta Comunicacao SAVIC'))
         else if registro.ValueExists('Porta Comunicacao APP') then
         begin
            try
               lblsavic_porta.Text := Trim(registro.ReadString('Porta Comunicacao APP'));
            except
               try
                  lblsavic_porta.Text := IntToStr(registro.ReadInteger('Porta Comunicacao APP'));
               except
                  lblsavic_porta.Text := '3306';
               end;
            end;
         end;

         if registro.ValueExists('NomeBancoSAVIC') and (Trim(registro.ReadString('NomeBancoSAVIC')) <> '') then
            lblsavic_banco.Text := Trim(registro.ReadString('NomeBancoSAVIC'))
         else if registro.ValueExists('NomeBancoAPP') and (Trim(registro.ReadString('NomeBancoAPP')) <> '') then
            lblsavic_banco.Text := Trim(registro.ReadString('NomeBancoAPP'));

         if registro.ValueExists('Usuario admin SAVIC') and (Trim(registro.ReadString('Usuario admin SAVIC')) <> '') then
            lblsavic_usuario.Text := Trim(registro.ReadString('Usuario admin SAVIC'))
         else if registro.ValueExists('Usuario admin APP') and (Trim(registro.ReadString('Usuario admin APP')) <> '') then
            lblsavic_usuario.Text := Trim(registro.ReadString('Usuario admin APP'));

         if registro.ValueExists('Senha SAVIC') and (Trim(registro.ReadString('Senha SAVIC')) <> '') then
            lblsavic_senha.Text := Trim(registro.ReadString('Senha SAVIC'))
         else if registro.ValueExists('Senha APP') and (Trim(registro.ReadString('Senha APP')) <> '') then
            lblsavic_senha.Text := Trim(registro.ReadString('Senha APP'));

         // Aplicativo RCC MySQL
         if registro.ValueExists('Nome do Servidor APP RCC') and (Trim(registro.ReadString('Nome do Servidor APP RCC')) <> '') then
            lblapp_servidor.Text := Trim(registro.ReadString('Nome do Servidor APP RCC'))
         else if registro.ValueExists('Nome do Servidor APP') and (Trim(registro.ReadString('Nome do Servidor APP')) <> '') then
            lblapp_servidor.Text := Trim(registro.ReadString('Nome do Servidor APP'));

         if registro.ValueExists('Porta Comunicacao APP RCC') then
            lblapp_porta.Text := IntToStr(registro.ReadInteger('Porta Comunicacao APP RCC'))
         else if registro.ValueExists('Porta Comunicacao APP') then
         begin
            try
               lblapp_porta.Text := Trim(registro.ReadString('Porta Comunicacao APP'));
            except
               try
                  lblapp_porta.Text := IntToStr(registro.ReadInteger('Porta Comunicacao APP'));
               except
                  lblapp_porta.Text := '3306';
               end;
            end;
         end;

         if registro.ValueExists('NomeBancoAPP RCC') and (Trim(registro.ReadString('NomeBancoAPP RCC')) <> '') then
            lblapp_banco.Text := Trim(registro.ReadString('NomeBancoAPP RCC'))
         else if registro.ValueExists('NomeBancoAPP') and (Trim(registro.ReadString('NomeBancoAPP')) <> '') then
            lblapp_banco.Text := Trim(registro.ReadString('NomeBancoAPP'));

         if registro.ValueExists('Usuario admin APP RCC') and (Trim(registro.ReadString('Usuario admin APP RCC')) <> '') then
            lblapp_usuario.Text := Trim(registro.ReadString('Usuario admin APP RCC'))
         else if registro.ValueExists('Usuario admin APP') and (Trim(registro.ReadString('Usuario admin APP')) <> '') then
            lblapp_usuario.Text := Trim(registro.ReadString('Usuario admin APP'));

         if registro.ValueExists('Senha APP RCC') and (Trim(registro.ReadString('Senha APP RCC')) <> '') then
            lblapp_senha.Text := Trim(registro.ReadString('Senha APP RCC'))
         else if registro.ValueExists('Senha APP') and (Trim(registro.ReadString('Senha APP')) <> '') then
            lblapp_senha.Text := Trim(registro.ReadString('Senha APP'));

         gridconfig.RowCount := 2;
         gridconfig.Cells[0, 0] := 'Nome Servidor';
         gridconfig.Cells[1, 0] := 'Banco de dados';
         gridconfig.Cells[2, 0] := 'Protocolo';

         gridconfig.Cells[0, 1] := frmprincipal.nomeserversql;
         gridconfig.Cells[1, 1] := frmprincipal.nomebancosql;
         gridconfig.Cells[2, 1] := frmprincipal.protocolo;
         gridconfig.Refresh;

         registro.CloseKey;
      end;
   finally
      registro.Free;
   end;
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
