unit unt_excluicontabil_repository;

interface

uses
  System.SysUtils, System.Classes, System.Generics.Collections,
  FireDAC.Comp.Client, FireDAC.Stan.Param, Data.DB,
  unt_excluicontabil_types;

type
  IExcluiContabilRepository = interface
    ['{C39E8412-A81E-4735-9F77-9E4B65FD39A1}']
    function PesquisarLancamentos(const ACampo, AValor, AEmpresaCod, AOrigem: string): TList<TLancamentoContabilDTO>;
    function ObterLancamento(const AChave: string; out ALancamento: TLancamentoContabilDTO): Boolean;
    function ValidarIntegridadeOrigem(const ALancamento: TLancamentoContabilDTO): TValidacaoExclusaoDTO;
    function ExcluirLancamento(const AChave: string; const AUsuario: string): TResultadoExclusaoContabil;
    function PesquisarPorModulo(const AFiltro: TFiltroExclusaoModuloDTO): TList<TLancamentoContabilDTO>;
    function ExcluirEmLotePorModulo(const AFiltro: TFiltroExclusaoModuloDTO; const AUsuario: string): TResultadoExclusaoContabil;
  end;

  TExcluiContabilRepositoryFireDAC = class(TInterfacedObject, IExcluiContabilRepository)
  private
    FConexao: TFDConnection;
  public
    constructor Create(AConexao: TFDConnection);
    function PesquisarLancamentos(const ACampo, AValor, AEmpresaCod, AOrigem: string): TList<TLancamentoContabilDTO>;
    function ObterLancamento(const AChave: string; out ALancamento: TLancamentoContabilDTO): Boolean;
    function ValidarIntegridadeOrigem(const ALancamento: TLancamentoContabilDTO): TValidacaoExclusaoDTO;
    function ExcluirLancamento(const AChave: string; const AUsuario: string): TResultadoExclusaoContabil;
    function PesquisarPorModulo(const AFiltro: TFiltroExclusaoModuloDTO): TList<TLancamentoContabilDTO>;
    function ExcluirEmLotePorModulo(const AFiltro: TFiltroExclusaoModuloDTO; const AUsuario: string): TResultadoExclusaoContabil;
  end;

implementation

{ TExcluiContabilRepositoryFireDAC }

constructor TExcluiContabilRepositoryFireDAC.Create(AConexao: TFDConnection);
begin
  inherited Create;
  FConexao := AConexao;
end;

function TExcluiContabilRepositoryFireDAC.PesquisarLancamentos(
  const ACampo, AValor, AEmpresaCod, AOrigem: string): TList<TLancamentoContabilDTO>;
var
  Qry: TFDQuery;
  Item: TLancamentoContabilDTO;
  CampoValido: string;
begin
  Result := TList<TLancamentoContabilDTO>.Create;
  CampoValido := 'contablancchv';
  if SameText(ACampo, 'contablancorignum') then
    CampoValido := 'contablancorignum'
  else if SameText(ACampo, 'contablancmod') then
    CampoValido := 'contablancmod'
  else if SameText(ACampo, 'contablancctadeb') then
    CampoValido := 'contablancctadeb'
  else if SameText(ACampo, 'contablancctacred') then
    CampoValido := 'contablancctacred';

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexao;
    // TODO: Python SQLAlchemy -> Query em ContabLancamento com joins e filtros dinamicos
    Qry.SQL.Text :=
      'SELECT TOP 200 cl.contablancchv, cl.contablancorignum, cl.contablancorigchv, ' +
      '       cl.contablancmod, cl.contablancmodfin, cl.contablancdata, cl.planoctaempcod, ' +
      '       cl.contablancval, cl.contablanchist, cl.contablancctadeb, cl.contablancctacred ' +
      'FROM contab_lancamento cl WITH (NOLOCK) ' +
      'WHERE cl.planoctaempcod = :pempresa ';

    if Trim(AValor) <> '' then
      Qry.SQL.Add(Format('AND cl.%s LIKE :pvalor ', [CampoValido]));

    if Trim(AOrigem) <> '' then
      Qry.SQL.Add('AND cl.contablancmod = :porigem ');

    Qry.SQL.Add('ORDER BY cl.contablancdata DESC, cl.contablancchv DESC');

    Qry.ParamByName('pempresa').AsString := Trim(AEmpresaCod);
    if Trim(AValor) <> '' then
      Qry.ParamByName('pvalor').AsString := '%' + Trim(AValor) + '%';
    if Trim(AOrigem) <> '' then
      Qry.ParamByName('porigem').AsString := Trim(AOrigem);

    Qry.Open;
    while not Qry.Eof do
    begin
      Item.Chave := Trim(Qry.FieldByName('contablancchv').AsString);
      Item.NumeroOrigem := Trim(Qry.FieldByName('contablancorignum').AsString);
      Item.OrigemChave := Trim(Qry.FieldByName('contablancorigchv').AsString);
      Item.Modulo := Trim(Qry.FieldByName('contablancmod').AsString);
      Item.SubModulo := Trim(Qry.FieldByName('contablancmodfin').AsString);
      Item.Data := Qry.FieldByName('contablancdata').AsDateTime;
      Item.EmpresaCod := Trim(Qry.FieldByName('planoctaempcod').AsString);
      Item.Valor := Qry.FieldByName('contablancval').AsCurrency;
      Item.Historico := Trim(Qry.FieldByName('contablanchist').AsString);
      Item.ContaDebito := Trim(Qry.FieldByName('contablancctadeb').AsString);
      Item.ContaCredito := Trim(Qry.FieldByName('contablancctacred').AsString);
      Result.Add(Item);
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
end;

function TExcluiContabilRepositoryFireDAC.ObterLancamento(
  const AChave: string; out ALancamento: TLancamentoContabilDTO): Boolean;
var
  Qry: TFDQuery;
begin
  Result := False;
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexao;
    Qry.SQL.Text :=
      'SELECT cl.contablancchv, cl.contablancorignum, cl.contablancorigchv, ' +
      '       cl.contablancmod, cl.contablancmodfin, cl.contablancdata, cl.planoctaempcod, ' +
      '       cl.contablancval, cl.contablanchist, cl.contablancctadeb, cl.contablancctacred ' +
      'FROM contab_lancamento cl WITH (NOLOCK) ' +
      'WHERE cl.contablancchv = :pchv';
    Qry.ParamByName('pchv').AsString := Trim(AChave);
    Qry.Open;

    if not Qry.Eof then
    begin
      ALancamento.Chave := Trim(Qry.FieldByName('contablancchv').AsString);
      ALancamento.NumeroOrigem := Trim(Qry.FieldByName('contablancorignum').AsString);
      ALancamento.OrigemChave := Trim(Qry.FieldByName('contablancorigchv').AsString);
      ALancamento.Modulo := Trim(Qry.FieldByName('contablancmod').AsString);
      ALancamento.SubModulo := Trim(Qry.FieldByName('contablancmodfin').AsString);
      ALancamento.Data := Qry.FieldByName('contablancdata').AsDateTime;
      ALancamento.EmpresaCod := Trim(Qry.FieldByName('planoctaempcod').AsString);
      ALancamento.Valor := Qry.FieldByName('contablancval').AsCurrency;
      ALancamento.Historico := Trim(Qry.FieldByName('contablanchist').AsString);
      ALancamento.ContaDebito := Trim(Qry.FieldByName('contablancctadeb').AsString);
      ALancamento.ContaCredito := Trim(Qry.FieldByName('contablancctacred').AsString);
      Result := True;
    end;
  finally
    Qry.Free;
  end;
end;

function TExcluiContabilRepositoryFireDAC.ValidarIntegridadeOrigem(
  const ALancamento: TLancamentoContabilDTO): TValidacaoExclusaoDTO;
var
  Qry: TFDQuery;
begin
  Result := TValidacaoExclusaoDTO.PermitidoOk;
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexao;

    // 1. Financeiro Realizado -> Checar lanc_mov_ctrl_banc
    if SameText(ALancamento.Modulo, 'Financeiro') and SameText(ALancamento.SubModulo, 'Realizado') then
    begin
      Qry.SQL.Text := 'SELECT TOP 1 movctrlbancnum FROM lanc_mov_ctrl_banc WITH (NOLOCK) WHERE movctrlbancnum = :pnum';
      Qry.ParamByName('pnum').AsString := ALancamento.NumeroOrigem;
      Qry.Open;
      if not Qry.Eof then
        Exit(TValidacaoExclusaoDTO.Bloqueado('Lançamento possui origem no Movimento Bancário. Estorne pela tesouraria.', ALancamento.NumeroOrigem));
      Qry.Close;
    end;

    // 2. Financeiro Id.Depósito -> Checar lanc_mov_ctrl_banc_ent
    if SameText(ALancamento.Modulo, 'Financeiro') and (Pos('Dep', ALancamento.SubModulo) > 0) then
    begin
      Qry.SQL.Text := 'SELECT TOP 1 movctrlbancnum FROM lanc_mov_ctrl_banc_ent WITH (NOLOCK) WHERE movctrlbancnum = :pnum';
      Qry.ParamByName('pnum').AsString := ALancamento.NumeroOrigem;
      Qry.Open;
      if not Qry.Eof then
        Exit(TValidacaoExclusaoDTO.Bloqueado('Lançamento possui vínculo com Depósitos de Entidades.', ALancamento.NumeroOrigem));
      Qry.Close;
    end;

    // 3. Financeiro Provisão -> Checar doc_fin
    if SameText(ALancamento.Modulo, 'Financeiro') and (Pos('Prov', ALancamento.SubModulo) > 0) then
    begin
      Qry.SQL.Text := 'SELECT TOP 1 docfinchv FROM doc_fin WITH (NOLOCK) WHERE docfinchv = :pchv';
      Qry.ParamByName('pchv').AsString := ALancamento.OrigemChave;
      Qry.Open;
      if not Qry.Eof then
        Exit(TValidacaoExclusaoDTO.Bloqueado('Lançamento tem origem em Contas a Pagar/Receber (Documento Financeiro).', ALancamento.OrigemChave));
      Qry.Close;
    end;

    // 4. Estoque -> Checar mov_estq
    if SameText(ALancamento.Modulo, 'Estoque') then
    begin
      Qry.SQL.Text := 'SELECT TOP 1 movestqchv FROM mov_estq WITH (NOLOCK) WHERE movestqchv = :pchv';
      Qry.ParamByName('pchv').AsString := ALancamento.OrigemChave;
      Qry.Open;
      if not Qry.Eof then
        Exit(TValidacaoExclusaoDTO.Bloqueado('Lançamento originado de Movimentação de Estoque.', ALancamento.OrigemChave));
      Qry.Close;
    end;

    // 5. Vendas -> Checar nota_fiscal
    if SameText(ALancamento.Modulo, 'Vendas') then
    begin
      Qry.SQL.Text := 'SELECT TOP 1 nfnum FROM nota_fiscal WITH (NOLOCK) WHERE nfnum = :pnum';
      Qry.ParamByName('pnum').AsString := ALancamento.NumeroOrigem;
      Qry.Open;
      if not Qry.Eof then
        Exit(TValidacaoExclusaoDTO.Bloqueado('Lançamento originado de Nota Fiscal de Vendas.', ALancamento.NumeroOrigem));
      Qry.Close;
    end;

  finally
    Qry.Free;
  end;
end;

function TExcluiContabilRepositoryFireDAC.ExcluirLancamento(
  const AChave: string; const AUsuario: string): TResultadoExclusaoContabil;
var
  Qry: TFDQuery;
begin
  if (FConexao = nil) or (not FConexao.Connected) then
    Exit(TResultadoExclusaoContabil.CriarFalha('Conexão indisponível.'));

  FConexao.StartTransaction;
  Qry := TFDQuery.Create(nil);
  try
    try
      Qry.Connection := FConexao;
      // Exclusão parametrizada do lançamento contábil
      Qry.SQL.Text := 'DELETE FROM contab_lancamento WHERE contablancchv = :pchv';
      Qry.ParamByName('pchv').AsString := Trim(AChave);
      Qry.ExecSQL;

      FConexao.Commit;
      Result := TResultadoExclusaoContabil.CriarSucesso(
        Format('Lançamento contábil %s excluído com sucesso.', [AChave]), Qry.RowsAffected);
    except
      on E: Exception do
      begin
        if FConexao.InTransaction then
          FConexao.Rollback;
        Result := TResultadoExclusaoContabil.CriarFalha('Erro ao excluir lançamento: ' + E.Message);
      end;
    end;
  finally
    Qry.Free;
  end;
end;

function TExcluiContabilRepositoryFireDAC.PesquisarPorModulo(
  const AFiltro: TFiltroExclusaoModuloDTO): TList<TLancamentoContabilDTO>;
var
  Qry: TFDQuery;
  Item: TLancamentoContabilDTO;
begin
  Result := TList<TLancamentoContabilDTO>.Create;
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexao;
    Qry.SQL.Text :=
      'SELECT cl.contablancchv, cl.contablancorignum, cl.contablancorigchv, ' +
      '       cl.contablancmod, cl.contablancmodfin, cl.contablancdata, cl.planoctaempcod, ' +
      '       cl.contablancval, cl.contablanchist, cl.contablancctadeb, cl.contablancctacred ' +
      'FROM contab_lancamento cl WITH (NOLOCK) ' +
      'WHERE cl.contablancdata >= :pini AND cl.contablancdata <= :pfim ' +
      '  AND cl.planoctaempcod = :pempresa ';

    if Trim(AFiltro.Modulo) <> '' then
      Qry.SQL.Add('AND cl.contablancmod = :pmodulo ');

    if Trim(AFiltro.SubModulo) <> '' then
      Qry.SQL.Add('AND cl.contablancmodfin = :psubmodulo ');

    Qry.SQL.Add('ORDER BY cl.contablancdata ASC');

    Qry.ParamByName('pini').AsDate := AFiltro.DataInicial;
    Qry.ParamByName('pfim').AsDate := AFiltro.DataFinal;
    Qry.ParamByName('pempresa').AsString := Trim(AFiltro.EmpresaCod);
    if Trim(AFiltro.Modulo) <> '' then
      Qry.ParamByName('pmodulo').AsString := Trim(AFiltro.Modulo);
    if Trim(AFiltro.SubModulo) <> '' then
      Qry.ParamByName('psubmodulo').AsString := Trim(AFiltro.SubModulo);

    Qry.Open;
    while not Qry.Eof do
    begin
      Item.Chave := Trim(Qry.FieldByName('contablancchv').AsString);
      Item.NumeroOrigem := Trim(Qry.FieldByName('contablancorignum').AsString);
      Item.OrigemChave := Trim(Qry.FieldByName('contablancorigchv').AsString);
      Item.Modulo := Trim(Qry.FieldByName('contablancmod').AsString);
      Item.SubModulo := Trim(Qry.FieldByName('contablancmodfin').AsString);
      Item.Data := Qry.FieldByName('contablancdata').AsDateTime;
      Item.EmpresaCod := Trim(Qry.FieldByName('planoctaempcod').AsString);
      Item.Valor := Qry.FieldByName('contablancval').AsCurrency;
      Item.Historico := Trim(Qry.FieldByName('contablanchist').AsString);
      Item.ContaDebito := Trim(Qry.FieldByName('contablancctadeb').AsString);
      Item.ContaCredito := Trim(Qry.FieldByName('contablancctacred').AsString);
      Result.Add(Item);
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
end;

function TExcluiContabilRepositoryFireDAC.ExcluirEmLotePorModulo(
  const AFiltro: TFiltroExclusaoModuloDTO; const AUsuario: string): TResultadoExclusaoContabil;
var
  Qry: TFDQuery;
begin
  if (FConexao = nil) or (not FConexao.Connected) then
    Exit(TResultadoExclusaoContabil.CriarFalha('Conexão com o banco indisponível.'));

  FConexao.StartTransaction;
  Qry := TFDQuery.Create(nil);
  try
    try
      Qry.Connection := FConexao;
      Qry.SQL.Text :=
        'DELETE FROM contab_lancamento ' +
        'WHERE contablancdata >= :pini AND contablancdata <= :pfim ' +
        '  AND planoctaempcod = :pempresa ';

      if Trim(AFiltro.Modulo) <> '' then
        Qry.SQL.Add('AND contablancmod = :pmodulo ');

      if Trim(AFiltro.SubModulo) <> '' then
        Qry.SQL.Add('AND contablancmodfin = :psubmodulo ');

      Qry.ParamByName('pini').AsDate := AFiltro.DataInicial;
      Qry.ParamByName('pfim').AsDate := AFiltro.DataFinal;
      Qry.ParamByName('pempresa').AsString := Trim(AFiltro.EmpresaCod);
      if Trim(AFiltro.Modulo) <> '' then
        Qry.ParamByName('pmodulo').AsString := Trim(AFiltro.Modulo);
      if Trim(AFiltro.SubModulo) <> '' then
        Qry.ParamByName('psubmodulo').AsString := Trim(AFiltro.SubModulo);

      Qry.ExecSQL;
      FConexao.Commit;
      Result := TResultadoExclusaoContabil.CriarSucesso(
        Format('Exclusão em lote finalizada. %d lançamentos contábeis removidos.', [Qry.RowsAffected]),
        Qry.RowsAffected);
    except
      on E: Exception do
      begin
        if FConexao.InTransaction then
          FConexao.Rollback;
        Result := TResultadoExclusaoContabil.CriarFalha('Erro na exclusão em lote: ' + E.Message);
      end;
    end;
  finally
    Qry.Free;
  end;
end;

end.
