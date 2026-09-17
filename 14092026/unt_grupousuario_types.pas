unit unt_grupousuario_types;

{
  GeoApolo - Tipos e Contratos para Gestão de Grupos de Usuários e Vínculos
  Clean Architecture: Tipos desacoplados sem dependência de VCL ou DataSets.
}

interface

uses
  System.SysUtils;

type

  TDadosGrupoUsuario = record
    CodigoGrupo   : string;
    Descricao     : string;
    TotalUsuarios : Integer;
  end;

  TVinculoUsuarioGrupo = record
    CodigoGrupo  : string;
    NomeGrupo    : string;
    Usucod       : string;
    Login        : string;
    NomeCompleto : string;
  end;

  TResultadoGrupoUsuario = record
    Sucesso       : Boolean;
    Mensagem      : string;
    IdGerado      : string;
    TotalAfetados : Integer;
  end;

implementation

end.
