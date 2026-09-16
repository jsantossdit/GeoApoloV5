unit unt_consultav3_types;

interface

uses
  System.SysUtils, System.Classes, Data.DB;

type
  TConsultaFiltroDTO = record
    Controle    : string;   // Ex: 'CLIENTES', 'CIDADE_CIDADE', 'BANCOS', etc.
    CampoBusca  : string;
    TextoBusca  : string;
    CampoOrdem  : string;
    OrdemAsc    : Boolean;
    DataInicial : TDateTime;
    DataFinal   : TDateTime;
    TemPeriodo  : Boolean;
  end;

  TItemConsultaDTO = record
    Codigo    : string;
    Descricao : string;
    Dados     : TStrings;
  end;

  TConsultaConfigDTO = record
    TituloJanela   : string;
    TabelaView     : string;
    CampoChave     : string;
    CampoDescricao : string;
    CamposExibicao : array of string;
    LabelsColunas  : array of string;
    SqlBase        : string;
  end;

implementation

end.
