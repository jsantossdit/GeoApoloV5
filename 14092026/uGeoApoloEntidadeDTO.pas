unit uGeoApoloEntidadeDTO;

interface

uses
  System.Generics.Collections;

type
  TTelefoneDTO = class
  public
    Operacao: String;
    Tipo: String;
    DDI: String;
    DDD: String;
    Numero: String;
    Principal: String;
  end;

  TEmailDTO = class
  public
    Operacao: String;
    Tipo: String;
    Email: String;
    Principal: String;
  end;

  TCategoriaDTO = class
  public
    Operacao: String;
    Codigo: String;
    AtivaTabelaPreco: String;
  end;

  TEntidadeDTO = class
  public
    Operacao: String;
    Codigo: String;
    Nome: String;
    NomeFantasia: String;
    CPFCNPJ: String;
    RGIE: String;
    Endereco: String;
    NumeroEndereco: String;
    Bairro: String;
    Cep: String;
    CodigoCidade: String;

    Telefones: TObjectList<TTelefoneDTO>;
    Emails: TObjectList<TEmailDTO>;
    Categorias: TObjectList<TCategoriaDTO>;

    constructor Create;
    destructor Destroy; override;
  end;

implementation

constructor TEntidadeDTO.Create;
begin
  Telefones := TObjectList<TTelefoneDTO>.Create(True);
  Emails := TObjectList<TEmailDTO>.Create(True);
  Categorias := TObjectList<TCategoriaDTO>.Create(True);
end;

destructor TEntidadeDTO.Destroy;
begin
  Telefones.Free;
  Emails.Free;
  Categorias.Free;
  inherited;
end;

end.
