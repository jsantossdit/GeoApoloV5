unit uDebxCredDTO;

interface

type
  // DTO para a visão resumida (o que já tínhamos)
  TDebxCredDTO = class
    Data: TDate;
    Debito: Currency;
    Credito: Currency;
    Diferenca: Currency;
  end;

  // DTO para a visão de DETALHES (o que está faltando)
  TDebxCredDetalheDTO = class
    Data: TDate;
    Debito: Currency;
    Credito: Currency;
    Modulo: string;
    Origem: string;
    Documento: string;
    Status: string;
    Chave: string;
    ErroMsg: string;
  end;

implementation

end.
