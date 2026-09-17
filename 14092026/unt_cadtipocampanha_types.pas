unit unt_cadtipocampanha_types;

interface

uses
  System.SysUtils, System.Classes;

type
  TTipoCampanhaDTO = record
    CodigoTipoCampanha: string;
    DescricaoTipoCamp : string;
    Ativo             : string; // 'S' ou 'N'
    GeraCampanha      : string; // 'S' ou 'N'
  end;

  TResultadoTipoCampanha = record
    Sucesso : Boolean;
    Mensagem: string;
    IdGerado: string;
  end;

implementation

end.
