unit unt_empresa;

interface

 uses
    system.sysutils;

type
  TEmpresa = class
  private
    FCod  : string;
    FNome : string;
  public
    property Cod  : string read FCod  write FCod;
    property Nome : string read FNome write FNome;

    procedure Limpar;
    function  Valida: string;
  end;


implementation

procedure TEmpresa.Limpar;
begin
  FCod  := '';
  FNome := '';
end;

function TEmpresa.Valida: string;
begin
  Result := '';
  if Trim(FNome) = '' then
    Result := 'NÃO É PERMITIDO GRAVAR UMA EMPRESA SEM NOME !!!';
end;

end.
