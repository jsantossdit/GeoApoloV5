unit unt_configbanco_types;

{
  Tipos de Dados e DTOs para Configurações de Bancos de Dados e Rede.
  Isolado de VCL e componentes visuais.
}

interface

uses
  System.SysUtils, System.Classes;

type
  TConfigBancoDTO = record
    TipoBanco      : string; // 'MSSQL', 'MySQL', 'SQLite'
    Servidor       : string;
    Porta          : Integer;
    NomeBanco      : string;
    Usuario        : string;
    Senha          : string;
    Protocolo      : string; // 'TCPIP'
    TimeoutConexao : Integer;
    DriverName     : string;
    Criptografado  : Boolean;
  end;

  TResultadoTesteConexao = record
    Sucesso         : Boolean;
    Mensagem        : string;
    TempoRespostaMs : Integer;
  end;

  TResultadoConfigBanco = record
    Sucesso  : Boolean;
    Mensagem : string;
  end;

implementation

end.
