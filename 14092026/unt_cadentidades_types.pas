unit unt_cadentidades_types;

interface

uses
  System.SysUtils, System.Classes;

type
  TModoGravacao = (mgInclusao, mgAlteracao);
  TBaseDestino = (bdGeoApolo, bdAlvo);

  TDadosPessoaisDTO = record
    Codigo           : string;
    CodigoAlternativo: string;
    TipoTratamento   : string;
    Nome             : string;
    NomeFantasia     : string;
    TipoFJ           : string; // 'F' ou 'J'
    Genero           : string; // 'M', 'F', 'N'
    EstadoCivil      : string;
    DataNascimento   : string;
    DataCadastro     : string;
    GrauEscolaridade : string;
    CargoCodigo      : string;
    Falecido         : Boolean;
    NomePai          : string;
    NomeMae          : string;
    PossuiFilhos     : Boolean;
    NumeroFilhos     : Integer;
    ResideCom        : string;
  end;

  TDadosEnderecoDTO = record
    CEP           : string;
    Logradouro    : string;
    Endereco      : string;
    Numero        : string;
    Complemento   : string;
    Bairro        : string;
    CodigoCidade  : string;
    NomeCidade    : string;
    UF            : string;
    CaixaPostal   : string;
    Referencia    : string;
  end;

  TDadosFinanceirosDTO = record
    TipoCobrancaCodigo : string;
    BancoNumero        : string;
    AgenciaNumero      : string;
    ContaCorrente      : string;
    DiaDebitoCC        : Integer;
    ValorContribuicao  : Double;
    GeraCarne          : Boolean;
    DioceseId          : string;
    RecebeLembrete     : Boolean;
  end;

  TEntidadeCompletaDTO = record
    BaseDestino : TBaseDestino;
    Modo        : TModoGravacao;
    Pessoais    : TDadosPessoaisDTO;
    Endereco    : TDadosEnderecoDTO;
    Financeiro  : TDadosFinanceirosDTO;
    AtivEconCod : string;
    OrigemCod   : string;
    RegiaoCod   : string;
    Conceito    : string;
    Observacoes : string;
  end;

implementation

end.
