unit ConsultaModel;

interface
type
  TTipoConsulta = (tcImediata, tcCampanha, tcMix);
  TConsultaModel = class
  private
    FCodigo: Integer;
    FDescricao: string;
    FSentencaSQL: string;
    FTipoConsulta: TTipoConsulta;
    FBancoConsulta: string;
  public
    property Codigo: Integer read FCodigo write FCodigo;
    property Descricao: string read FDescricao write FDescricao;
    property SentencaSQL: string read FSentencaSQL write FSentencaSQL;
    property TipoConsulta: TTipoConsulta read FTipoConsulta write FTipoConsulta;
    property BancoConsulta: string read FBancoConsulta write FBancoConsulta;
  end;
implementation
end.
