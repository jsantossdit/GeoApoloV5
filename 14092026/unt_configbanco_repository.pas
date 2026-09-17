unit unt_configbanco_repository;

{
  Repositório para Leitura, Gravação e Teste de Conexão de Bancos de Dados.
  Compatível com Windows Registry e FireDAC.
}

interface

uses
  System.SysUtils, System.Classes, System.Win.Registry, Winapi.Windows,
  FireDAC.Comp.Client, FireDAC.Stan.Param, FireDAC.Stan.Option,
  unt_configbanco_types;

type
  IConfigBancoRepository = interface
    ['{1A2B3C4D-5E6F-7A8B-9C0D-1E2F3A4B5C6D}']
    function CarregarConfiguracao(const ATipo: string = 'MSSQL'): TConfigBancoDTO;
    function SalvarConfiguracao(const AConfig: TConfigBancoDTO): Boolean;
    function TestarConexao(const AConfig: TConfigBancoDTO): TResultadoTesteConexao;
  end;

  TConfigBancoRepository = class(TInterfacedObject, IConfigBancoRepository)
  public
    function CarregarConfiguracao(const ATipo: string = 'MSSQL'): TConfigBancoDTO;
    function SalvarConfiguracao(const AConfig: TConfigBancoDTO): Boolean;
    function TestarConexao(const AConfig: TConfigBancoDTO): TResultadoTesteConexao;
  end;

implementation

function TConfigBancoRepository.CarregarConfiguracao(const ATipo: string): TConfigBancoDTO;
var
  Reg: TRegistry;
begin
  FillChar(Result, SizeOf(Result), 0);
  Result.TipoBanco      := ATipo;
  Result.Porta          := 1433;
  Result.TimeoutConexao := 15;
  Result.Protocolo      := 'TCPIP';
  Result.DriverName     := 'MSSQL';

  Reg := TRegistry.Create;
  try
    Reg.RootKey := HKEY_CURRENT_USER;
    if Reg.OpenKeyReadOnly('sdit\\configuracoes\\DataBase') then
    begin
      if SameText(ATipo, 'MSSQL') or (ATipo = '') then
      begin
        Result.Servidor   := Reg.ReadString('Nome do ServidorSQL');
        Result.NomeBanco  := Reg.ReadString('NomeBancoSQL');
        Result.Usuario    := Reg.ReadString('Usuario MSSQL');
        Result.Senha      := Reg.ReadString('Senha do Banco SQL');
        Result.Protocolo  := Reg.ReadString('ProtocoloSQL');
        if Result.Protocolo = '' then
          Result.Protocolo := 'TCPIP';
      end
      else if SameText(ATipo, 'MySQL') then
      begin
        Result.Servidor   := Reg.ReadString('Nome do Servidor APP');
        Result.NomeBanco  := Reg.ReadString('NomeBancoAPP');
        Result.Usuario    := Reg.ReadString('Usuario admin APP');
        Result.Senha      := Reg.ReadString('Senha APP');
        Result.Protocolo  := Reg.ReadString('Protocolo APP');
        Result.Porta      := 3306;
      end;
      Reg.CloseKey;
    end;
  finally
    Reg.Free;
  end;
end;

function TConfigBancoRepository.SalvarConfiguracao(const AConfig: TConfigBancoDTO): Boolean;
var
  Reg: TRegistry;
begin
  Result := False;
  Reg := TRegistry.Create;
  try
    Reg.RootKey := HKEY_CURRENT_USER;
    if Reg.OpenKey('sdit\\configuracoes\\DataBase', True) then
    begin
      if SameText(AConfig.TipoBanco, 'MSSQL') or (AConfig.TipoBanco = '') then
      begin
        Reg.WriteString('Nome do ServidorSQL', AConfig.Servidor);
        Reg.WriteString('IP do ServidorSQL', AConfig.Servidor);
        Reg.WriteString('NomeBancoSQL', AConfig.NomeBanco);
        Reg.WriteString('Usuario MSSQL', AConfig.Usuario);
        Reg.WriteString('Senha do Banco SQL', AConfig.Senha);
        Reg.WriteString('ProtocoloSQL', AConfig.Protocolo);
      end
      else if SameText(AConfig.TipoBanco, 'MySQL') then
      begin
        Reg.WriteString('Nome do Servidor APP', AConfig.Servidor);
        Reg.WriteString('IP do Servidor APP', AConfig.Servidor);
        Reg.WriteString('NomeBancoAPP', AConfig.NomeBanco);
        Reg.WriteString('Usuario admin APP', AConfig.Usuario);
        Reg.WriteString('Senha APP', AConfig.Senha);
        Reg.WriteString('Protocolo APP', AConfig.Protocolo);
        Reg.WriteInteger('Porta Comunicacao APP', AConfig.Porta);
      end;
      Reg.CloseKey;
      Result := True;
    end;
  finally
    Reg.Free;
  end;
end;

function TConfigBancoRepository.TestarConexao(const AConfig: TConfigBancoDTO): TResultadoTesteConexao;
var
  Conn: TFDConnection;
  Inicio: Cardinal;
begin
  Result.Sucesso := False;
  Result.Mensagem := '';
  Result.TempoRespostaMs := 0;

  Conn := TFDConnection.Create(nil);
  try
    try
      Inicio := GetTickCount;
      if SameText(AConfig.TipoBanco, 'MSSQL') or (AConfig.TipoBanco = '') then
      begin
        Conn.DriverName := 'MSSQL';
        Conn.Params.Values['Server'] := AConfig.Servidor;
        Conn.Params.Values['Database'] := AConfig.NomeBanco;
        Conn.Params.Values['User_Name'] := AConfig.Usuario;
        Conn.Params.Values['Password'] := AConfig.Senha;
        if AConfig.Porta > 0 then
          Conn.Params.Values['Port'] := IntToStr(AConfig.Porta);
      end
      else if SameText(AConfig.TipoBanco, 'MySQL') then
      begin
        Conn.DriverName := 'MySQL';
        Conn.Params.Values['Server'] := AConfig.Servidor;
        Conn.Params.Values['Database'] := AConfig.NomeBanco;
        Conn.Params.Values['User_Name'] := AConfig.Usuario;
        Conn.Params.Values['Password'] := AConfig.Senha;
        if AConfig.Porta > 0 then
          Conn.Params.Values['Port'] := IntToStr(AConfig.Porta);
      end;

      Conn.LoginPrompt := False;
      Conn.Connected := True;

      Result.TempoRespostaMs := Integer(GetTickCount - Inicio);
      Result.Sucesso := True;
      Result.Mensagem := Format('Conexao estabelecida com sucesso em %d ms.', [Result.TempoRespostaMs]);
      Conn.Connected := False;
    except
      on E: Exception do
      begin
        Result.Sucesso := False;
        Result.Mensagem := 'Falha ao conectar: ' + E.Message;
      end;
    end;
  finally
    Conn.Free;
  end;
end;

end.
