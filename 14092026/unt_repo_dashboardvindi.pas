unit unt_repo_dashboardvindi;

interface

uses
  System.SysUtils, System.Generics.Collections,
  FireDAC.Comp.Client, Data.DB,
  unt_intf_dashboardvindi;

type
  TDashboardVindiRepository = class(TInterfacedObject, IDashboardVindiRepository)
  private
    FConnection: TFDConnection;
    function CriarQuery: TFDQuery;
  public
    constructor Create(const AConnection: TFDConnection);

    function GetEvolucaoAnual(const AAnoInicial: Integer): TArray<TEvolucaoAnual>;
    function GetEvolucaoMensal(const AAno: Integer): TArray<TEvolucaoMensal>;
    function GetDistribuicaoPorMeioPagamento(const AAnoInicial: Integer): TArray<TDistribuicaoMeioPagamento>;
    function GetDistribuicaoPorStatus(const AAnoInicial: Integer): TArray<TDistribuicaoStatus>;
    function GetTopClientesPorValorPago(const AAnoInicial: Integer; const ATopN: Integer = 10): TArray<TTopCliente>;
  end;

implementation

{ TDashboardVindiRepository }

constructor TDashboardVindiRepository.Create(const AConnection: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConnection) then
    raise Exception.Create('TDashboardVindiRepository: conex�o n�o informada.');
  FConnection := AConnection;
end;

function TDashboardVindiRepository.CriarQuery: TFDQuery;
begin
  Result := TFDQuery.Create(nil);
  Result.Connection := FConnection;
end;

function TDashboardVindiRepository.GetEvolucaoAnual(const AAnoInicial: Integer): TArray<TEvolucaoAnual>;
var
  qry: TFDQuery;
  lista: TList<TEvolucaoAnual>;
  item: TEvolucaoAnual;
begin
  qry := CriarQuery;
  lista := TList<TEvolucaoAnual>.Create;
  try
    qry.SQL.Text :=
      ' SELECT YEAR(uyt.alterado)   AS Ano, '                              +
      '        SUM(uyt.precopago)  AS TotalPago, '                        +
      '        SUM(uyt.taxa)       AS TotalTaxa, '                        +
      '        COUNT(*)            AS Qtd '                               +
      ' FROM USER_YapayTransacoes uyt WITH(NOLOCK) '                      +
      ' INNER JOIN USER_VindiTransacoes uvt WITH(NOLOCK) '                +
      '         ON uyt.PedidoId = uvt.VindiTransacaoId '                  +
      ' INNER JOIN USERVindi_entidade uve WITH(NOLOCK) '                  +
      '         ON uvt.VindiEntidadeId = uve.VindiEntidadeId '            +
      ' WHERE YEAR(uyt.alterado) >= :AnoInicial '                        +
      ' GROUP BY YEAR(uyt.alterado) '                                     +
      ' ORDER BY Ano';
    qry.ParamByName('AnoInicial').AsInteger := AAnoInicial;
    qry.Open;

    while not qry.Eof do
    begin
      item.Ano           := qry.FieldByName('Ano').AsInteger;
      item.TotalPago      := qry.FieldByName('TotalPago').AsCurrency;
      item.TotalTaxa      := qry.FieldByName('TotalTaxa').AsCurrency;
      item.QtdTransacoes  := qry.FieldByName('Qtd').AsInteger;
      lista.Add(item);
      qry.Next;
    end;

    Result := lista.ToArray;
  finally
    qry.Free;
    lista.Free;
  end;
end;

function TDashboardVindiRepository.GetEvolucaoMensal(const AAno: Integer): TArray<TEvolucaoMensal>;
var
  qry: TFDQuery;
  lista: TList<TEvolucaoMensal>;
  item: TEvolucaoMensal;
begin
  qry := CriarQuery;
  lista := TList<TEvolucaoMensal>.Create;
  try
    qry.SQL.Text :=
      ' SELECT YEAR(uyt.alterado)   AS Ano, '                              +
      '        MONTH(uyt.alterado) AS Mes, '                              +
      '        SUM(uyt.precopago)  AS TotalPago, '                        +
      '        COUNT(*)            AS Qtd '                               +
      ' FROM USER_YapayTransacoes uyt WITH(NOLOCK) '                      +
      ' INNER JOIN USER_VindiTransacoes uvt WITH(NOLOCK) '                +
      '         ON uyt.PedidoId = uvt.VindiTransacaoId '                  +
      ' INNER JOIN USERVindi_entidade uve WITH(NOLOCK) '                  +
      '         ON uvt.VindiEntidadeId = uve.VindiEntidadeId '            +
      ' WHERE YEAR(uyt.alterado) = :Ano '                                +
      ' GROUP BY YEAR(uyt.alterado), MONTH(uyt.alterado) '                +
      ' ORDER BY Mes';
    qry.ParamByName('Ano').AsInteger := AAno;
    qry.Open;

    while not qry.Eof do
    begin
      item.Ano           := qry.FieldByName('Ano').AsInteger;
      item.Mes            := qry.FieldByName('Mes').AsInteger;
      item.TotalPago      := qry.FieldByName('TotalPago').AsCurrency;
      item.QtdTransacoes  := qry.FieldByName('Qtd').AsInteger;
      lista.Add(item);
      qry.Next;
    end;

    Result := lista.ToArray;
  finally
    qry.Free;
    lista.Free;
  end;
end;

function TDashboardVindiRepository.GetDistribuicaoPorMeioPagamento(const AAnoInicial: Integer): TArray<TDistribuicaoMeioPagamento>;
var
  qry: TFDQuery;
  lista: TList<TDistribuicaoMeioPagamento>;
  item: TDistribuicaoMeioPagamento;
begin
  qry := CriarQuery;
  lista := TList<TDistribuicaoMeioPagamento>.Create;
  try
    qry.SQL.Text :=
      ' SELECT ISNULL(uyt.meiodepagamento, ''N�o informado'') AS MeioPagamento, ' +
      '        SUM(uyt.precopago)  AS TotalPago, '                        +
      '        COUNT(*)            AS Qtd '                               +
      ' FROM USER_YapayTransacoes uyt WITH(NOLOCK) '                      +
      ' INNER JOIN USER_VindiTransacoes uvt WITH(NOLOCK) '                +
      '         ON uyt.PedidoId = uvt.VindiTransacaoId '                  +
      ' INNER JOIN USERVindi_entidade uve WITH(NOLOCK) '                  +
      '         ON uvt.VindiEntidadeId = uve.VindiEntidadeId '            +
      ' WHERE YEAR(uyt.alterado) >= :AnoInicial '                        +
      ' GROUP BY uyt.meiodepagamento '                                    +
      ' ORDER BY TotalPago DESC';
    qry.ParamByName('AnoInicial').AsInteger := AAnoInicial;
    qry.Open;

    while not qry.Eof do
    begin
      item.MeioPagamento  := qry.FieldByName('MeioPagamento').AsString;
      item.TotalPago      := qry.FieldByName('TotalPago').AsCurrency;
      item.QtdTransacoes  := qry.FieldByName('Qtd').AsInteger;
      lista.Add(item);
      qry.Next;
    end;

    Result := lista.ToArray;
  finally
    qry.Free;
    lista.Free;
  end;
end;

function TDashboardVindiRepository.GetDistribuicaoPorStatus(const AAnoInicial: Integer): TArray<TDistribuicaoStatus>;
var
  qry: TFDQuery;
  lista: TList<TDistribuicaoStatus>;
  item: TDistribuicaoStatus;
begin
  qry := CriarQuery;
  lista := TList<TDistribuicaoStatus>.Create;
  try
    qry.SQL.Text :=
      ' SELECT ISNULL(uve.status, ''N�o informado'') AS Status, '        +
      '        COUNT(*)            AS Qtd, '                              +
      '        SUM(uyt.precopago)  AS TotalPago '                        +
      ' FROM USER_YapayTransacoes uyt WITH(NOLOCK) '                      +
      ' INNER JOIN USER_VindiTransacoes uvt WITH(NOLOCK) '                +
      '         ON uyt.PedidoId = uvt.VindiTransacaoId '                  +
      ' INNER JOIN USERVindi_entidade uve WITH(NOLOCK) '                  +
      '         ON uvt.VindiEntidadeId = uve.VindiEntidadeId '            +
      ' WHERE YEAR(uyt.alterado) >= :AnoInicial '                        +
      ' GROUP BY uve.status '                                             +
      ' ORDER BY Qtd DESC';
    qry.ParamByName('AnoInicial').AsInteger := AAnoInicial;
    qry.Open;

    while not qry.Eof do
    begin
      item.Status         := qry.FieldByName('Status').AsString;
      item.QtdTransacoes  := qry.FieldByName('Qtd').AsInteger;
      item.TotalPago      := qry.FieldByName('TotalPago').AsCurrency;
      lista.Add(item);
      qry.Next;
    end;

    Result := lista.ToArray;
  finally
    qry.Free;
    lista.Free;
  end;
end;

function TDashboardVindiRepository.GetTopClientesPorValorPago(const AAnoInicial: Integer; const ATopN: Integer): TArray<TTopCliente>;
var
  qry: TFDQuery;
  lista: TList<TTopCliente>;
  item: TTopCliente;
begin
  qry := CriarQuery;
  lista := TList<TTopCliente>.Create;
  try
    qry.SQL.Text :=
      ' SELECT TOP (:TopN) '                                              +
      '        ISNULL(uyt.clientenome, ''N�o informado'') AS Nome, '     +
      '        ISNULL(uyt.clienteemail, '''') AS Email, '                +
      '        SUM(uyt.precopago) AS TotalPago, '                        +
      '        COUNT(*)           AS Qtd '                               +
      ' FROM USER_YapayTransacoes uyt WITH(NOLOCK) '                      +
      ' INNER JOIN USER_VindiTransacoes uvt WITH(NOLOCK) '                +
      '         ON uyt.PedidoId = uvt.VindiTransacaoId '                  +
      ' INNER JOIN USERVindi_entidade uve WITH(NOLOCK) '                  +
      '         ON uvt.VindiEntidadeId = uve.VindiEntidadeId '            +
      ' WHERE YEAR(uyt.alterado) >= :AnoInicial '                        +
      ' GROUP BY uyt.clientenome, uyt.clienteemail '                      +
      ' ORDER BY SUM(uyt.precopago) DESC';
    qry.ParamByName('TopN').AsInteger := ATopN;
    qry.ParamByName('AnoInicial').AsInteger := AAnoInicial;
    qry.Open;

    while not qry.Eof do
    begin
      item.Nome           := qry.FieldByName('Nome').AsString;
      item.Email          := qry.FieldByName('Email').AsString;
      item.TotalPago      := qry.FieldByName('TotalPago').AsCurrency;
      item.QtdTransacoes  := qry.FieldByName('Qtd').AsInteger;
      lista.Add(item);
      qry.Next;
    end;

    Result := lista.ToArray;
  finally
    qry.Free;
    lista.Free;
  end;
end;

end.
