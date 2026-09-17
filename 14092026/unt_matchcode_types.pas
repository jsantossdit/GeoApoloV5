unit unt_matchcode_types;

interface

uses
  System.SysUtils, System.Classes;

type
  TMatchCodeUsuarioDTO = record
    OrigemUsucod : string;
    OrigemNome   : string;
    DestinoUsucod: string;
    DestinoNome  : string;
  end;

  TMatchCodeEntidadeDTO = record
    OrigemEntcod : string;
    OrigemNome   : string;
    DestinoEntcod: string;
    DestinoNome  : string;
  end;

  TResultadoMatchCode = record
    Sucesso          : Boolean;
    Mensagem         : string;
    RegistrosMigrados: Integer;
  end;

implementation

end.
