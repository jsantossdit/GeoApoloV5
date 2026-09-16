unit uDebxCredController;

interface

uses
  System.Generics.Collections,
  FireDAC.Comp.Client,
  uDebxCredDTO,
  uDebxCredRepository,
  uDebxCredService;

type
  TDebxCredController = class
  private
    FRepository: TDebxCredRepository;
    FService: TDebxCredService;
  public
    constructor Create(AConnection: TFDConnection);
    destructor Destroy; override;

    function Consultar(
      const ADataInicial, ADataFinal: TDate;
      const ACodConta: string
    ): TObjectList<TDebxCredDTO>;
    // ADICIONE ESTA LINHA:
    function ConsultarDetalhes(AData: TDate; AConta, AEmpresa: string): TObjectList<TDebxCredDetalheDTO>;
  end;

implementation

uses unt_dados;

constructor TDebxCredController.Create(AConnection: TFDConnection);
begin
  inherited Create;

  FRepository := TDebxCredRepository.Create(AConnection);
  FService := TDebxCredService.Create(FRepository);
end;

destructor TDebxCredController.Destroy;
begin
  FService.Free;
  FRepository.Free;
  inherited;
end;

function TDebxCredController.Consultar(
  const ADataInicial, ADataFinal: TDate;
  const ACodConta: string
): TObjectList<TDebxCredDTO>;
begin
  Result := FService.Consultar(ADataInicial, ADataFinal, ACodConta);
end;

function TDebxCredController.ConsultarDetalhes(AData: TDate; AConta, AEmpresa: string): TObjectList<TDebxCredDetalheDTO>;
var
  Query: TFDQuery;
  Item: TDebxCredDetalheDTO;
begin
  Result := TObjectList<TDebxCredDetalheDTO>.Create(True);
  Query := TFDQuery.Create(nil);
  try
    Query.Connection := modulo_dados.fdbanco; // Certifique-se que o Controller tem a conexão
    Query.SQL.Add('SELECT cl.ContabLancData, cl.ContabLancValor, cl.ContabLancCtaCred, ');
    Query.SQL.Add('       cl.ContabLancCtaDeb, cl.ContabLancMod, cl.ContabLancModFin, ');
    Query.SQL.Add('       cl.ContabLancOrigNum, cl.ContabLancChv ');
    Query.SQL.Add('FROM contab_lancamento cl WITH(NOLOCK) ');
    Query.SQL.Add('WHERE cl.ContabLancData = :DATA ');
    Query.SQL.Add('  AND (cl.ContabLancCtaCred = :CONTA OR cl.ContabLancCtaDeb = :CONTA) ');

    // Se o seu banco usa PlanoCtaEmpCod na tabela de lançamentos, descomente abaixo:
    // Query.SQL.Add(' AND cl.PlanoCtaEmpCod = :EMPRESA ');

    Query.ParamByName('DATA').AsDate := AData;
    Query.ParamByName('CONTA').AsString := AConta;
    // Query.ParamByName('EMPRESA').AsString := AEmpresa;

    Query.Open;

    while not Query.Eof do
    begin
      Item := TDebxCredDetalheDTO.Create;
      Item.Data      := Query.FieldByName('ContabLancData').AsDateTime;
      Item.Modulo    := Query.FieldByName('ContabLancMod').AsString;
      Item.Origem    := Query.FieldByName('ContabLancModFin').AsString;
      Item.Documento := Query.FieldByName('ContabLancOrigNum').AsString;
      Item.Chave     := Query.FieldByName('ContabLancChv').AsString;

      // Lógica de Débito/Crédito
      if Query.FieldByName('ContabLancCtaDeb').AsString = AConta then
      begin
        Item.Debito  := Query.FieldByName('ContabLancValor').AsCurrency;
        Item.Credito := 0;
      end
      else
      begin
        Item.Debito  := 0;
        Item.Credito := Query.FieldByName('ContabLancValor').AsCurrency;
      end;

      // Simulação de validação de Status (conforme seu código original)
      Item.Status := 'Ok';

      Result.Add(Item);
      Query.Next;
    end;
  finally
    Query.Free;
  end;
end;

end.
