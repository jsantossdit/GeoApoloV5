unit unt_estacoes_types;

{
  Tipos de Dados e DTOs para o Módulo de Estações de Trabalho (TI e Ativo Fixo).
  Isolado de VCL, forms e componentes visuais.
}

interface

uses
  System.SysUtils, System.Classes;

type
  TEstacaoDTO = record
    CodigoEstacao      : string;
    Descricao          : string;
    CodigoDepartamento : string;
    NomeDepartamento   : string;
    DataCadastro       : TDateTime;
    CodigoUsuario      : string;
    UsuarioResponsavel : string;
    TagServico         : string;
    GeoEntCod          : string;
    NomeEntidade       : string;
    ModeloEstacao      : string;
    CodigoLocalizacao  : string;
    NomeLocalizacao    : string;
    EnderecoIP         : string;
    Observacoes        : string;
  end;

  THardwareDTO = record
    CodigoHardware  : string;
    Descricao       : string;
    Valor           : Double;
    DataCompra      : TDateTime;
    DataAtivacao    : TDateTime;
    TempoGarantia   : Integer; // Dias
    CodigoStatus    : Integer;
    NomeStatus      : string;
    CodigoEstacao   : string;
    CodigoClasse    : Integer;
    NomeClasse      : string;
    Observacoes     : string;
    NF              : string;
    Marca           : string;
    EnderecoIP      : string;
    Rack            : string;
    PatchPanel      : string;
  end;

  TSoftwareDTO = record
    CodigoSoftware : string;
    Descricao      : string;
    NF             : string;
    Valor          : Double;
    DataCompra     : TDateTime;
    DataVencimento : TDateTime;
    TipoLicenca    : string;
    CodigoEstacao  : string;
    CodigoClasse   : Integer;
    Observacoes    : string;
  end;

  TUsuarioEstacaoDTO = record
    CodigoUsuario   : string;
    NomeUsuario     : string;
    CodigoEstacao   : string;
    DataVinculo     : TDateTime;
    Responsavel     : string;
  end;

  TEstacaoFiltroDTO = record
    CampoBusca   : string;
    TextoBusca   : string;
    CampoOrdem   : string;
    OrdemAsc     : Boolean;
    Departamento : string;
  end;

  TOperacaoResultado = record
    Sucesso  : Boolean;
    Mensagem : string;
    Codigo   : string;
  end;

implementation

end.
