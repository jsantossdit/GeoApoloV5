unit unt_entidades_types;

interface

type
  TDecisaoLinha = (dlNenhuma, dlManterSVE, dlManterAlvo);

  TEntidadeFiltroDTO = record
    BaseDados     : string;  // 'GeoApolo' ou 'Alvo'
    TipoPesquisa  : string;  // 'Consulta' ou 'Especifica'
    FiltroEspecial: string;  // 'JAEXPORTADA' ou ''
    CampoBusca    : string;  // ex: 'entnome'
    TextoBusca    : string;
    CampoOrdenacao: string;
    OrdemAsc      : Boolean; // True = ASC, False = DESC
  end;

  TItemDiferencaComparacao = record
    IndiceMapa : Integer;
    Rotulo     : string;
    ValorSVE   : string;
    ValorAlvo  : string;
    Decisao    : TDecisaoLinha;
  end;

  TResultadoOperacaoDTO = record
    Sucesso : Boolean;
    Mensagem: string;
    Codigo  : string;
  end;

  TCredencialAlvoDTO = record
    UsuarioAlvo    : string;
    SenhaAlvoCripto: string;
    TokenAlvo      : string;
  end;

  TEntidadeEdicaoDTO = record
    Codigo           : string;
    CodigoAlternativo: string;
    TipoTratamento   : string;
    Nome             : string;
    NomeFantasia     : string;
    CEP              : string;
    Logradouro       : string;
    Endereco         : string;
    Numero           : string;
    Complemento      : string;
    Bairro           : string;
    CodigoCidade     : string;
    NomeCidade       : string;
    UF               : string;
    Genero           : string;
    EstadoCivil      : string;
    DataNascimento   : string;
    DataCadastro     : string;
    NomePai          : string;
    NomeMae          : string;
    PossuiFilhos     : Boolean;
    NumeroFilhos     : Integer;
    ValorContribuicao: Double;
    DioceseId        : string;
    NomeDiocese      : string;
    Observacoes      : string;
    ModoIntegracao   : string;
  end;

implementation

end.
