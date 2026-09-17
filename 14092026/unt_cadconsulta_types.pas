unit unt_cadconsulta_types;

{
  GeoApolo - Tipos e Contratos para Cadastro de Consultas Dinâmicas
  Clean Architecture: Tipos desacoplados sem dependência de VCL ou DataSets.
}

interface

uses
  System.SysUtils;

type

  TTipoConsultaCad = (tcImediata, tcCampanha, tcMix, tcGeral);

  TDadosConsultaCad = record
    Codigo        : Integer;
    Descricao     : string;
    SentencaSQL   : string;
    TipoConsulta  : TTipoConsultaCad;
    BancoConsulta : string;
  end;

  TResultadoConsultaCad = record
    Sucesso  : Boolean;
    Mensagem : string;
    IdGerado : Integer;
  end;

implementation

end.
