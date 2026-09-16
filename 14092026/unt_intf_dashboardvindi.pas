unit unt_intf_dashboardvindi;

{
  Interface do reposit�rio de dados do Dashboard de Concilia��o Vindi/Yapay.
  Baseado na view VW_USER_ConciliaVindi.

  Observa��o: os agrupamentos por per�odo usam o campo uyt.alterado (data de
  altera��o do registro em USER_YapayTransacoes) como refer�ncia temporal da
  transa��o. Se existir um campo mais adequado (ex: data de pagamento efetivo),
  troque a refer�ncia dentro do reposit�rio (unt_repo_dashboardvindi.pas).
}

interface

uses
  System.SysUtils;

type
  TEvolucaoAnual = record
    Ano: Integer;
    TotalPago: Currency;
    TotalTaxa: Currency;
    QtdTransacoes: Integer;
  end;

  TEvolucaoMensal = record
    Ano: Integer;
    Mes: Integer;
    TotalPago: Currency;
    QtdTransacoes: Integer;
  end;

  TDistribuicaoMeioPagamento = record
    MeioPagamento: string;
    TotalPago: Currency;
    QtdTransacoes: Integer;
  end;

  TDistribuicaoStatus = record
    Status: string;
    QtdTransacoes: Integer;
    TotalPago: Currency;
  end;

  TTopCliente = record
    Nome: string;
    Email: string;
    TotalPago: Currency;
    QtdTransacoes: Integer;
  end;

  IDashboardVindiRepository = interface
    ['{8B2E1E1A-6C2E-4A6B-9C7B-3E2F4D1A9F10}']

    /// <summary> Soma anual de precopago/taxa a partir do ano informado. </summary>
    function GetEvolucaoAnual(const AAnoInicial: Integer): TArray<TEvolucaoAnual>;

    /// <summary> Soma mensal de precopago para um ano espec�fico (drill-down). </summary>
    function GetEvolucaoMensal(const AAno: Integer): TArray<TEvolucaoMensal>;

    /// <summary> Distribui��o de valores/quantidade por meio de pagamento. </summary>
    function GetDistribuicaoPorMeioPagamento(const AAnoInicial: Integer): TArray<TDistribuicaoMeioPagamento>;

    /// <summary> Distribui��o de quantidade/valores por status da entidade Vindi. </summary>
    function GetDistribuicaoPorStatus(const AAnoInicial: Integer): TArray<TDistribuicaoStatus>;

    /// <summary> Ranking dos clientes com maior valor pago, a partir do ano informado. </summary>
    function GetTopClientesPorValorPago(const AAnoInicial: Integer; const ATopN: Integer = 10): TArray<TTopCliente>;
  end;

implementation

end.
