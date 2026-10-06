unit unt_cadmarcas_types;

{
  Tipos de Dados e DTOs para Cadastro de Marcas de Produtos (USER_geoapolo_produto_marcas).
  Isolado de VCL e componentes visuais.
}

interface

uses
  System.SysUtils, System.Classes;

type
  TMarcaDTO = record
    CodigoMarca    : Integer;
    DescricaoMarca : string;
  end;

  TResultadoMarca = record
    Sucesso  : Boolean;
    Mensagem : string;
    Codigo   : Integer;
  end;

implementation

end.
