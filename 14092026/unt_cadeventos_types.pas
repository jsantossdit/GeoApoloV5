unit unt_cadeventos_types;

interface

uses
  System.SysUtils, System.Classes;

type
  TTipoEventoDTO = record
    TipoEventCod       : string;
    DescricaoTipoEvento: string;
  end;

  TEventoDTO = record
    IdEvento           : string;
    Descricao          : string;
    DataInicial        : string;
    DataFinal          : string;
    TemaPrincipal      : string;
    TipoEventCod       : string;
    DescricaoTipoEvento: string;
  end;

  TResultadoEvento = record
    Sucesso : Boolean;
    Mensagem: string;
    IdGerado: string;
  end;

implementation

end.
