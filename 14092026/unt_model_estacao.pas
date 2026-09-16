unit unt_model_estacao;

interface

type
  TEstacao = class
  private
    FCodigo: string;
    FDescricao: string;
    FDataCadastro: TDateTime;
    FEnderecoIP: string;
  public
    property Codigo: string read FCodigo write FCodigo;
    property Descricao: string read FDescricao write FDescricao;
    property DataCadastro: TDateTime read FDataCadastro write FDataCadastro;
    property EnderecoIP: string read FEnderecoIP write FEnderecoIP;
  end;

implementation
end.
