unit unt_cadcores_types;

{
  Tipos de Dados e DTOs para Cadastro de Cores de Produtos.
  Isolado de VCL e componentes visuais.
}

interface

uses
  System.SysUtils, System.Classes;

type
  TCorDTO = record
    CodigoCor    : Integer;
    DescricaoCor : string;
  end;

  TResultadoCor = record
    Sucesso  : Boolean;
    Mensagem : string;
    Codigo   : Integer;
  end;

implementation

end.
