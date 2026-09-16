unit unt_categoriaentidade_types;

{
  Tipos de Dados e DTOs para Relacionamento Usuário x Grupo x Categoria x Entidade.
  Isolado de VCL, forms e componentes visuais.
}

interface

uses
  System.SysUtils, System.Classes;

type
  TModoRelacionamento = (mrUsuario, mrGrupo);

  TCategoriaResumoDTO = record
    CodigoCategoria : string;
    Descricao       : string;
    TotalEntidades  : Integer;
    Vinculada       : Boolean;
  end;

  TUsuarioItemDTO = record
    Codigo : string;
    Nome   : string;
  end;

  TGrupoItemDTO = record
    Codigo    : string;
    Descricao : string;
  end;

  TOperacaoResultado = record
    Sucesso  : Boolean;
    Mensagem : string;
    Codigo   : string;
  end;

implementation

end.
