unit unt_configperfil_types;

{
  GeoApolo - Tipos e Contratos para Configuração de Perfis de Acesso e Matriz de Permissões
  Clean Architecture: Tipos desacoplados sem dependência de VCL ou DataSets.
}

interface

uses
  System.SysUtils;

type

  TDadosObjetoPerfil = record
    CodigoObjeto : Integer;
    NomeObjeto   : string;
    NomeAmigavel : string;
    Categoria    : string;
    CodigoGrupo  : Integer;
    StatusAcesso : string; // 'A' = Permitido / Liberado | 'N' = Negado / Bloqueado
  end;

  TResultadoConfigPerfil = record
    Sucesso       : Boolean;
    Mensagem      : string;
    TotalAfetados : Integer;
  end;

implementation

end.
