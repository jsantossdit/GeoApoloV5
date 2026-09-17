unit unt_cadtipotratamento_types;

interface

uses
  System.SysUtils, System.Classes;

type
  TTipoTratamentoDTO = record
    TipoTratCod        : string;
    Abreviatura        : string;
    DescricaoTratamento: string;
  end;

  TResultadoTipoTratamento = record
    Sucesso : Boolean;
    Mensagem: string;
    IdGerado: string;
  end;

implementation

end.
