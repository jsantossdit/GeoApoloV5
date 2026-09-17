unit unt_users_types;

interface

uses
  System.SysUtils, System.Classes;

type
  TUsuarioDTO = record
    CodigoUsuario     : string;
    Usucod            : string;
    NomeCompleto      : string;
    FlagAtivo         : string; // 'A' (Ativo), 'I' (Inativo), 'S'
    Login             : string;
    Email             : string;
    DataNascimento    : string;
    CodigoDepartamento: string;
    NomeDepartamento  : string;
    UsucodApolo       : string;
    SenhaAlvo         : string;
    Senha             : string;
  end;

  TDepartamentoDTO = record
    CodigoDepartamento: string;
    NomeDepartamento  : string;
    EmpCod            : string;
    EmpNome           : string;
    FlagAtivo         : string;
  end;

  TSistemaDTO = record
    CodigoSistema: string;
    Descricao    : string;
    Sigla        : string;
  end;

  TGrupoUsuarioDTO = record
    CodigoGrupo  : string;
    Descricao    : string;
    TotalUsuarios: Integer;
  end;

  TVinculoGrupoUsuarioDTO = record
    CodigoGrupo : string;
    NomeGrupo   : string;
    Usucod      : string;
    Login       : string;
    NomeCompleto: string;
  end;

  TObjetoAcessoDTO = record
    CodigoObjeto: string;
    NomeObjeto  : string;
    NomeAmigavel: string;
    Categoria   : string;
  end;

  TPerfilItemDTO = record
    CodigoObjeto: string;
    NomeObjeto  : string;
    NomeAmigavel: string;
    Categoria   : string;
    CodigoGrupo : string;
    StatusAcesso: string; // 'A' = Permitido, 'N' = Negado
  end;

  TResultadoOperacaoUsuario = record
    Sucesso : Boolean;
    Mensagem: string;
    IdGerado: string;
  end;

implementation

end.
