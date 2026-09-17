unit unt_imediatas_types;

{
  GeoApolo - Tipos e Contratos para Execução de Consultas Imediatas e Exportação
  Clean Architecture: Tipos desacoplados sem dependência de VCL ou DataSets.
}

interface

uses
  System.SysUtils;

type

  TDadosConsultaImediata = record
    CodigoConsulta : string;
    Descricao      : string;
    SentencaSQL    : string;
    BancoConsulta  : string; // 'Apolo', 'GeoApolo', 'CRM'
    TipoConsulta   : string; // 'I' (Imediata), 'T' (Tabela/Geral)
  end;

  TResultadoExecucaoConsulta = record
    Sucesso         : Boolean;
    Mensagem        : string;
    TotalRegistros  : Integer;
    TempoExecucaoMs : Int64;
  end;

  TResultadoExportacao = record
    Sucesso        : Boolean;
    Mensagem       : string;
    CaminhoArquivo : string;
    TotalLinhas    : Integer;
  end;

implementation

end.
