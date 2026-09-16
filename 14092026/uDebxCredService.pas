unit uDebxCredService;

interface

uses
  System.SysUtils,
  System.Generics.Collections,
  uDebxCredDTO,
  uDebxCredRepository;

type
  TDebxCredService = class
  private
    FRepository: TDebxCredRepository;
  public
    constructor Create(ARepository: TDebxCredRepository);

    function Consultar(
      const ADataInicial, ADataFinal: TDate;
      const ACodConta: string
    ): TObjectList<TDebxCredDTO>;
  end;

implementation

constructor TDebxCredService.Create(ARepository: TDebxCredRepository);
begin
  inherited Create;
  FRepository := ARepository;
end;

function TDebxCredService.Consultar(
  const ADataInicial, ADataFinal: TDate;
  const ACodConta: string
): TObjectList<TDebxCredDTO>;
begin
  if ADataInicial > ADataFinal then
    raise Exception.Create('A data inicial não pode ser maior que a data final.');

  Result := FRepository.Consultar(ADataInicial, ADataFinal, ACodConta);
end;

end.
