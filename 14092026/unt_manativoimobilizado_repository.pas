unit unt_manativoimobilizado_repository;

{
  Repositório FireDAC para Gestão de Ativo Imobilizado.
  Preserva integridade transacional, consultas parametrizadas e hints WITH (NOLOCK).
}

interface

uses
  System.SysUtils, System.Classes, Data.DB,
  FireDAC.Comp.Client, FireDAC.Stan.Param,
  unt_manativoimobilizado_types;

type
  TAtivoImobilizadoRepository = class
  private
    FConn: TFDConnection;
    function RowToDTO(Qry: TFDQuery): TAtivoImobilizadoDTO;
  public
    constructor Create(AConnection: TFDConnection);

    // CRUD de Bens de Ativo Fixo
    function ListarBens(const AEmpCod: string): TArray<TAtivoImobilizadoDTO>;
    function ObterBem(const ANumeroDoBem, AEmpCod: string; out ABem: TAtivoImobilizadoDTO): Boolean;
    function InserirBem(const ABem: TAtivoImobilizadoDTO): TOperacaoResultadoAtivo;
    function AtualizarBem(const ABem: TAtivoImobilizadoDTO): TOperacaoResultadoAtivo;
    function ExcluirBem(const ANumeroDoBem: string): TOperacaoResultadoAtivo;

    // Lookups Auxiliares
    function ListarCentrosControle: TArray<TLookupItemDTO>;
    function ListarCategorias: TArray<TLookupItemDTO>;
    function ListarClassificacoes(const ACategoriaCod: string = ''): TArray<TLookupItemDTO>;
    function ListarLocalizacoes: TArray<TLookupItemDTO>;
    function ListarFuncionariosResponsaveis: TArray<TLookupItemDTO>;
    function ListarMarcas: TArray<TLookupItemDTO>;
    function ListarStatus: TArray<TLookupItemDTO>;
    function ListarEmpresas: TArray<TLookupItemDTO>;
  end;

implementation

constructor TAtivoImobilizadoRepository.Create(AConnection: TFDConnection);
begin
  inherited Create;
  FConn := AConnection;
end;

function TAtivoImobilizadoRepository.RowToDTO(Qry: TFDQuery): TAtivoImobilizadoDTO;
begin
  FillChar(Result, SizeOf(Result), 0);
  Result.NumeroDoBem              := Qry.FieldByName('numero_do_bem').AsString;
  Result.DescricaoDoBem           := Qry.FieldByName('descricao_do_bem').AsString;
  Result.EmpCod                   := Qry.FieldByName('empcod').AsString;
  Result.GeoCctrlCodEstr          := Qry.FieldByName('geocctrlcodestr').AsString;
  Result.GeoCctrlNome             := Qry.FieldByName('geocctrlnome').AsString;
  Result.CodigoBarrasAtivo        := Qry.FieldByName('codigo_barrasativo').AsString;
  Result.CodigoCategoriaBem       := Qry.FieldByName('codigo_categoria_bem').AsString;
  Result.CategoriaBem             := Qry.FieldByName('categoria_bem').AsString;
  Result.CodigoClassificacaoAtivo := Qry.FieldByName('codigo_classificacaoativoimobilizado').AsString;
  Result.Classificacao            := Qry.FieldByName('classificacao').AsString;
  Result.CodigoLocalizacao        := Qry.FieldByName('codigo_localizacao').AsString;
  Result.Localizacao              := Qry.FieldByName('localizacao').AsString;
  Result.CodigoFuncResponsavel    := Qry.FieldByName('codigo_func_responsavel').AsString;
  Result.NomeFuncResponsavel      := Qry.FieldByName('nome_completo').AsString;
  Result.CodigoDaMarca            := Qry.FieldByName('codigo_da_marca').AsString;
  Result.Marca                    := Qry.FieldByName('marca').AsString;
  Result.CodigoStatusBem          := Qry.FieldByName('codigo_status_bem').AsString;
  Result.DescricaoStatusBem       := Qry.FieldByName('descricao_status_bem').AsString;

  if not Qry.FieldByName('data_aquisicao').IsNull then
  begin
    Result.DataAquisicao    := Qry.FieldByName('data_aquisicao').AsDateTime;
    Result.TemDataAquisicao := True;
  end;

  Result.ValorCompra          := Qry.FieldByName('valor_compra').AsFloat;
  Result.TaxaDepreciacaoAnual := Qry.FieldByName('taxa_depreciacao_anual').AsFloat;

  if not Qry.FieldByName('data_ultima_revisao').IsNull then
  begin
    Result.DataUltimaRevisao    := Qry.FieldByName('data_ultima_revisao').AsDateTime;
    Result.TemDataUltimaRevisao := True;
  end;

  Result.CaminhoFoto := Qry.FieldByName('caminho_foto').AsString;
  Result.Observacoes := Qry.FieldByName('observacoes').AsString;
end;

function TAtivoImobilizadoRepository.ListarBens(const AEmpCod: string): TArray<TAtivoImobilizadoDTO>;
var
  Qry: TFDQuery;
  Lista: TArray<TAtivoImobilizadoDTO>;
  Count: Integer;
begin
  SetLength(Lista, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT ugsa.numero_do_bem, ugsa.descricao_do_bem, ' +
      '       ugsa.geocctrlcodestr, ugcc.geocctrlnome, ' +
      '       ugsa.codigo_barrasativo, ugsa.codigo_categoria_bem, ' +
      '       ugsc.descricao AS categoria_bem, ' +
      '       ugsa.codigo_classificacaoativoimobilizado, ' +
      '       ugsca.descricao AS classificacao, ' +
      '       ugsa.codigo_localizacao, ugslf.localizacao, ' +
      '       ugsa.codigo_func_responsavel, ISNULL(ugu.nome_completo, '''') AS nome_completo, ' +
      '       ugsa.codigo_da_marca, ugpm.descricao_marca AS marca, ' +
      '       ugsa.codigo_status_bem, ISNULL(ugssi.descricao_status_bem, '''') AS descricao_status_bem, ' +
      '       ugsa.empcod, ' +
      '       ugsa.data_aquisicao, ugsa.valor_compra, ' +
      '       ugsa.taxa_depreciacao_anual, ugsa.data_ultima_revisao, ' +
      '       ugsa.caminho_foto, ugsa.observacoes ' +
      'FROM USER_geoapolo_satfi_ativoimobilizado ugsa WITH (NOLOCK) ' +
      'INNER JOIN USER_geoapolo_centrocontrole ugcc WITH (NOLOCK) ' +
      '        ON ugsa.geocctrlcodestr = ugcc.geocctrlcodestr ' +
      'INNER JOIN USER_geoapolo_satfi_categorias ugsc WITH (NOLOCK) ' +
      '        ON ugsa.codigo_categoria_bem = ugsc.codigo_categoria ' +
      'INNER JOIN USER_geoapolo_satfi_classificacaoativo ugsca WITH (NOLOCK) ' +
      '        ON ugsa.codigo_classificacaoativoimobilizado = ugsca.codigoclasse ' +
      'INNER JOIN USER_geoapolo_satfi_localizacao_fisica ugslf WITH (NOLOCK) ' +
      '        ON ugsa.codigo_localizacao = ugslf.codigo_localizacao ' +
      'LEFT JOIN USER_geoapolo_usuarios ugu WITH (NOLOCK) ' +
      '       ON ugsa.codigo_func_responsavel = ugu.usucod ' +
      'INNER JOIN USER_geoapolo_produto_marcas ugpm WITH (NOLOCK) ' +
      '        ON ugsa.codigo_da_marca = ugpm.codigo_marca ' +
      'LEFT JOIN USER_geoapolo_satfi_status_imobilizado ugssi WITH (NOLOCK) ' +
      '       ON ugsa.codigo_status_bem = ugssi.codigo_status_bem ' +
      'WHERE ugsa.empcod = :empcod ' +
      'ORDER BY CAST(ugsa.numero_do_bem AS INTEGER) ASC';

    Qry.ParamByName('empcod').AsString := AEmpCod;
    Qry.Open;

    Count := 0;
    while not Qry.Eof do
    begin
      SetLength(Lista, Count + 1);
      Lista[Count] := RowToDTO(Qry);
      Inc(Count);
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
  Result := Lista;
end;

function TAtivoImobilizadoRepository.ObterBem(const ANumeroDoBem, AEmpCod: string; out ABem: TAtivoImobilizadoDTO): Boolean;
var
  Qry: TFDQuery;
begin
  Result := False;
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT ugsa.numero_do_bem, ugsa.descricao_do_bem, ' +
      '       ugsa.geocctrlcodestr, ugcc.geocctrlnome, ' +
      '       ugsa.codigo_barrasativo, ugsa.codigo_categoria_bem, ' +
      '       ugsc.descricao AS categoria_bem, ' +
      '       ugsa.codigo_classificacaoativoimobilizado, ' +
      '       ugsca.descricao AS classificacao, ' +
      '       ugsa.codigo_localizacao, ugslf.localizacao, ' +
      '       ugsa.codigo_func_responsavel, ISNULL(ugu.nome_completo, '''') AS nome_completo, ' +
      '       ugsa.codigo_da_marca, ugpm.descricao_marca AS marca, ' +
      '       ugsa.codigo_status_bem, ISNULL(ugssi.descricao_status_bem, '''') AS descricao_status_bem, ' +
      '       ugsa.empcod, ' +
      '       ugsa.data_aquisicao, ugsa.valor_compra, ' +
      '       ugsa.taxa_depreciacao_anual, ugsa.data_ultima_revisao, ' +
      '       ugsa.caminho_foto, ugsa.observacoes ' +
      'FROM USER_geoapolo_satfi_ativoimobilizado ugsa WITH (NOLOCK) ' +
      'INNER JOIN USER_geoapolo_centrocontrole ugcc WITH (NOLOCK) ' +
      '        ON ugsa.geocctrlcodestr = ugcc.geocctrlcodestr ' +
      'INNER JOIN USER_geoapolo_satfi_categorias ugsc WITH (NOLOCK) ' +
      '        ON ugsa.codigo_categoria_bem = ugsc.codigo_categoria ' +
      'INNER JOIN USER_geoapolo_satfi_classificacaoativo ugsca WITH (NOLOCK) ' +
      '        ON ugsa.codigo_classificacaoativoimobilizado = ugsca.codigoclasse ' +
      'INNER JOIN USER_geoapolo_satfi_localizacao_fisica ugslf WITH (NOLOCK) ' +
      '        ON ugsa.codigo_localizacao = ugslf.codigo_localizacao ' +
      'LEFT JOIN USER_geoapolo_usuarios ugu WITH (NOLOCK) ' +
      '       ON ugsa.codigo_func_responsavel = ugu.usucod ' +
      'INNER JOIN USER_geoapolo_produto_marcas ugpm WITH (NOLOCK) ' +
      '        ON ugsa.codigo_da_marca = ugpm.codigo_marca ' +
      'LEFT JOIN USER_geoapolo_satfi_status_imobilizado ugssi WITH (NOLOCK) ' +
      '       ON ugsa.codigo_status_bem = ugssi.codigo_status_bem ' +
      'WHERE ugsa.numero_do_bem = :numBem AND ugsa.empcod = :empcod';

    Qry.ParamByName('numBem').AsString := ANumeroDoBem;
    Qry.ParamByName('empcod').AsString := AEmpCod;
    Qry.Open;

    if not Qry.Eof then
    begin
      ABem := RowToDTO(Qry);
      Result := True;
    end;
  finally
    Qry.Free;
  end;
end;

function TAtivoImobilizadoRepository.InserirBem(const ABem: TAtivoImobilizadoDTO): TOperacaoResultadoAtivo;
var
  Qry: TFDQuery;
begin
  Result.Sucesso := False;
  Result.Codigo := ABem.NumeroDoBem;
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'INSERT INTO USER_geoapolo_satfi_ativoimobilizado (' +
      '  numero_do_bem, descricao_do_bem, geocctrlcodestr, ' +
      '  codigo_barrasativo, codigo_categoria_bem, ' +
      '  codigo_classificacaoativoimobilizado, codigo_localizacao, ' +
      '  codigo_func_responsavel, codigo_da_marca, empcod, codigo_status_bem, ' +
      '  data_aquisicao, valor_compra, taxa_depreciacao_anual, ' +
      '  data_ultima_revisao, caminho_foto, observacoes ' +
      ') VALUES (' +
      '  :codbem, :descricaobem, :cctrlcodestr, ' +
      '  :plaquetapatrimonio, :categbem, ' +
      '  :classificacaobem, :localizacaofisica, ' +
      '  :codfuncresp, :codigomarca, :empresa, :statusdobem, ' +
      '  :dataaquisicao, :valorcompra, :taxadepanual, ' +
      '  :dataultimarevisao, :caminhofoto, :observacoes ' +
      ')';

    Qry.ParamByName('codbem').AsString             := ABem.NumeroDoBem;
    Qry.ParamByName('descricaobem').AsString       := ABem.DescricaoDoBem;
    Qry.ParamByName('cctrlcodestr').AsString       := ABem.GeoCctrlCodEstr;
    Qry.ParamByName('plaquetapatrimonio').AsString := ABem.CodigoBarrasAtivo;
    Qry.ParamByName('categbem').AsString           := ABem.CodigoCategoriaBem;
    Qry.ParamByName('classificacaobem').AsString   := ABem.CodigoClassificacaoAtivo;
    Qry.ParamByName('localizacaofisica').AsString  := ABem.CodigoLocalizacao;

    if ABem.CodigoFuncResponsavel <> '' then
      Qry.ParamByName('codfuncresp').AsString := ABem.CodigoFuncResponsavel
    else
      Qry.ParamByName('codfuncresp').Clear;

    Qry.ParamByName('codigomarca').AsString := ABem.CodigoDaMarca;
    Qry.ParamByName('empresa').AsString     := ABem.EmpCod;
    Qry.ParamByName('statusdobem').AsString := ABem.CodigoStatusBem;

    if ABem.TemDataAquisicao then
      Qry.ParamByName('dataaquisicao').AsDate := ABem.DataAquisicao
    else
      Qry.ParamByName('dataaquisicao').Clear;

    Qry.ParamByName('valorcompra').AsFloat   := ABem.ValorCompra;
    Qry.ParamByName('taxadepanual').AsFloat  := ABem.TaxaDepreciacaoAnual;

    if ABem.TemDataUltimaRevisao then
      Qry.ParamByName('dataultimarevisao').AsDate := ABem.DataUltimaRevisao
    else
      Qry.ParamByName('dataultimarevisao').Clear;

    Qry.ParamByName('caminhofoto').AsString := ABem.CaminhoFoto;
    Qry.ParamByName('observacoes').AsString := ABem.Observacoes;

    Qry.ExecSQL;
    Result.Sucesso := True;
    Result.Mensagem := 'Bem cadastrado com sucesso.';
  except
    on E: Exception do
    begin
      Result.Sucesso := False;
      Result.Mensagem := 'Erro ao inserir bem: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

function TAtivoImobilizadoRepository.AtualizarBem(const ABem: TAtivoImobilizadoDTO): TOperacaoResultadoAtivo;
var
  Qry: TFDQuery;
begin
  Result.Sucesso := False;
  Result.Codigo := ABem.NumeroDoBem;
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'UPDATE USER_geoapolo_satfi_ativoimobilizado SET ' +
      '  descricao_do_bem                     = :descricaobem, ' +
      '  geocctrlcodestr                      = :cctrlcodestr, ' +
      '  codigo_barrasativo                   = :plaquetapatrimonio, ' +
      '  codigo_categoria_bem                 = :categbem, ' +
      '  codigo_classificacaoativoimobilizado = :classificacaobem, ' +
      '  codigo_localizacao                   = :localizacaofisica, ' +
      '  codigo_func_responsavel              = :codfuncresp, ' +
      '  codigo_da_marca                      = :codigomarca, ' +
      '  empcod                               = :empcod, ' +
      '  codigo_status_bem                    = :statusdobem, ' +
      '  data_aquisicao                       = :dataaquisicao, ' +
      '  valor_compra                         = :valorcompra, ' +
      '  taxa_depreciacao_anual               = :taxadepanual, ' +
      '  data_ultima_revisao                  = :dataultimarevisao, ' +
      '  caminho_foto                         = :caminhofoto, ' +
      '  observacoes                          = :observacoes ' +
      'WHERE numero_do_bem = :numerodobem';

    Qry.ParamByName('descricaobem').AsString       := ABem.DescricaoDoBem;
    Qry.ParamByName('cctrlcodestr').AsString       := ABem.GeoCctrlCodEstr;
    Qry.ParamByName('plaquetapatrimonio').AsString := ABem.CodigoBarrasAtivo;
    Qry.ParamByName('categbem').AsString           := ABem.CodigoCategoriaBem;
    Qry.ParamByName('classificacaobem').AsString   := ABem.CodigoClassificacaoAtivo;
    Qry.ParamByName('localizacaofisica').AsString  := ABem.CodigoLocalizacao;

    if ABem.CodigoFuncResponsavel <> '' then
      Qry.ParamByName('codfuncresp').AsString := ABem.CodigoFuncResponsavel
    else
      Qry.ParamByName('codfuncresp').Clear;

    Qry.ParamByName('codigomarca').AsString := ABem.CodigoDaMarca;
    Qry.ParamByName('empcod').AsString      := ABem.EmpCod;
    Qry.ParamByName('statusdobem').AsString := ABem.CodigoStatusBem;

    if ABem.TemDataAquisicao then
      Qry.ParamByName('dataaquisicao').AsDate := ABem.DataAquisicao
    else
      Qry.ParamByName('dataaquisicao').Clear;

    Qry.ParamByName('valorcompra').AsFloat   := ABem.ValorCompra;
    Qry.ParamByName('taxadepanual').AsFloat  := ABem.TaxaDepreciacaoAnual;

    if ABem.TemDataUltimaRevisao then
      Qry.ParamByName('dataultimarevisao').AsDate := ABem.DataUltimaRevisao
    else
      Qry.ParamByName('dataultimarevisao').Clear;

    Qry.ParamByName('caminhofoto').AsString := ABem.CaminhoFoto;
    Qry.ParamByName('observacoes').AsString := ABem.Observacoes;
    Qry.ParamByName('numerodobem').AsString := ABem.NumeroDoBem;

    Qry.ExecSQL;
    Result.Sucesso := True;
    Result.Mensagem := 'Bem atualizado com sucesso.';
  except
    on E: Exception do
    begin
      Result.Sucesso := False;
      Result.Mensagem := 'Erro ao atualizar bem: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

function TAtivoImobilizadoRepository.ExcluirBem(const ANumeroDoBem: string): TOperacaoResultadoAtivo;
var
  Qry: TFDQuery;
begin
  Result.Sucesso := False;
  Result.Codigo := ANumeroDoBem;
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'DELETE FROM USER_geoapolo_satfi_ativoimobilizado WHERE numero_do_bem = :codBem';
    Qry.ParamByName('codBem').AsString := ANumeroDoBem;
    Qry.ExecSQL;

    Result.Sucesso := True;
    Result.Mensagem := 'Bem removido com sucesso.';
  except
    on E: Exception do
    begin
      Result.Sucesso := False;
      Result.Mensagem := 'Erro ao excluir bem: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

function TAtivoImobilizadoRepository.ListarCentrosControle: TArray<TLookupItemDTO>;
var
  Qry: TFDQuery;
  Lista: TArray<TLookupItemDTO>;
  Count: Integer;
begin
  SetLength(Lista, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT geocctrlcodestr, geocctrlnome ' +
      'FROM USER_geoapolo_centrocontrole WITH (NOLOCK) ' +
      'ORDER BY geocctrlcodestr ASC';
    Qry.Open;
    Count := 0;
    while not Qry.Eof do
    begin
      SetLength(Lista, Count + 1);
      Lista[Count].Codigo    := Qry.FieldByName('geocctrlcodestr').AsString;
      Lista[Count].Descricao := Qry.FieldByName('geocctrlnome').AsString;
      Inc(Count);
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
  Result := Lista;
end;

function TAtivoImobilizadoRepository.ListarCategorias: TArray<TLookupItemDTO>;
var
  Qry: TFDQuery;
  Lista: TArray<TLookupItemDTO>;
  Count: Integer;
begin
  SetLength(Lista, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT codigo_categoria, descricao ' +
      'FROM USER_geoapolo_satfi_categorias WITH (NOLOCK) ' +
      'ORDER BY codigo_categoria ASC';
    Qry.Open;
    Count := 0;
    while not Qry.Eof do
    begin
      SetLength(Lista, Count + 1);
      Lista[Count].Codigo    := Qry.FieldByName('codigo_categoria').AsString;
      Lista[Count].Descricao := Qry.FieldByName('descricao').AsString;
      Inc(Count);
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
  Result := Lista;
end;

function TAtivoImobilizadoRepository.ListarClassificacoes(const ACategoriaCod: string = ''): TArray<TLookupItemDTO>;
var
  Qry: TFDQuery;
  Lista: TArray<TLookupItemDTO>;
  Count: Integer;
begin
  SetLength(Lista, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    if ACategoriaCod <> '' then
    begin
      Qry.SQL.Text :=
        'SELECT ugsca.codigoclasse, ugsca.descricao, ugsc.descricao AS categoria ' +
        'FROM USER_geoapolo_satfi_classificacaoativo ugsca WITH (NOLOCK) ' +
        'INNER JOIN USER_geoapolo_satfi_categorias ugsc WITH (NOLOCK) ' +
        '        ON ugsca.codigo_categoria = ugsc.codigo_categoria ' +
        'WHERE ugsca.codigo_categoria = :categ ' +
        'ORDER BY ugsca.codigoclasse ASC';
      Qry.ParamByName('categ').AsString := ACategoriaCod;
    end
    else
    begin
      Qry.SQL.Text :=
        'SELECT ugsca.codigoclasse, ugsca.descricao, ugsc.descricao AS categoria ' +
        'FROM USER_geoapolo_satfi_classificacaoativo ugsca WITH (NOLOCK) ' +
        'INNER JOIN USER_geoapolo_satfi_categorias ugsc WITH (NOLOCK) ' +
        '        ON ugsca.codigo_categoria = ugsc.codigo_categoria ' +
        'ORDER BY ugsca.codigoclasse ASC';
    end;
    Qry.Open;
    Count := 0;
    while not Qry.Eof do
    begin
      SetLength(Lista, Count + 1);
      Lista[Count].Codigo    := Qry.FieldByName('codigoclasse').AsString;
      Lista[Count].Descricao := Qry.FieldByName('descricao').AsString;
      Lista[Count].Extra     := Qry.FieldByName('categoria').AsString;
      Inc(Count);
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
  Result := Lista;
end;

function TAtivoImobilizadoRepository.ListarLocalizacoes: TArray<TLookupItemDTO>;
var
  Qry: TFDQuery;
  Lista: TArray<TLookupItemDTO>;
  Count: Integer;
begin
  SetLength(Lista, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT ugslf.codigo_localizacao, ugslf.localizacao, ugd.nome_departamento ' +
      'FROM USER_geoapolo_satfi_localizacao_fisica ugslf WITH (NOLOCK) ' +
      'INNER JOIN USER_geoapolo_departamentos ugd WITH (NOLOCK) ' +
      '        ON ugslf.codigo_departamento = ugd.codigo_departamento ' +
      '       AND ugd.flagativo = ''A'' ' +
      'WHERE ugslf.grupo <> ''G'' ' +
      'ORDER BY ugslf.codigo_localizacao ASC';
    Qry.Open;
    Count := 0;
    while not Qry.Eof do
    begin
      SetLength(Lista, Count + 1);
      Lista[Count].Codigo    := Qry.FieldByName('codigo_localizacao').AsString;
      Lista[Count].Descricao := Qry.FieldByName('localizacao').AsString;
      Lista[Count].Extra     := Qry.FieldByName('nome_departamento').AsString;
      Inc(Count);
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
  Result := Lista;
end;

function TAtivoImobilizadoRepository.ListarFuncionariosResponsaveis: TArray<TLookupItemDTO>;
var
  Qry: TFDQuery;
  Lista: TArray<TLookupItemDTO>;
  Count: Integer;
begin
  SetLength(Lista, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT ugu.usucod, ugu.nome_completo, ugd.nome_departamento ' +
      'FROM USER_geoapolo_usuarios ugu WITH (NOLOCK) ' +
      'INNER JOIN USER_geoapolo_departamentos ugd WITH (NOLOCK) ' +
      '        ON ugu.codigo_departamento = ugd.codigo_departamento ' +
      '       AND ugd.flagativo = ''A'' ' +
      'WHERE ugu.flagativo = ''A'' ' +
      'ORDER BY ugu.nome_completo ASC';
    Qry.Open;
    Count := 0;
    while not Qry.Eof do
    begin
      SetLength(Lista, Count + 1);
      Lista[Count].Codigo    := Qry.FieldByName('usucod').AsString;
      Lista[Count].Descricao := Qry.FieldByName('nome_completo').AsString;
      Lista[Count].Extra     := Qry.FieldByName('nome_departamento').AsString;
      Inc(Count);
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
  Result := Lista;
end;

function TAtivoImobilizadoRepository.ListarMarcas: TArray<TLookupItemDTO>;
var
  Qry: TFDQuery;
  Lista: TArray<TLookupItemDTO>;
  Count: Integer;
begin
  SetLength(Lista, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT codigo_marca, descricao_marca ' +
      'FROM USER_geoapolo_produto_marcas WITH (NOLOCK) ' +
      'ORDER BY codigo_marca ASC';
    Qry.Open;
    Count := 0;
    while not Qry.Eof do
    begin
      SetLength(Lista, Count + 1);
      Lista[Count].Codigo    := Qry.FieldByName('codigo_marca').AsString;
      Lista[Count].Descricao := Qry.FieldByName('descricao_marca').AsString;
      Inc(Count);
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
  Result := Lista;
end;

function TAtivoImobilizadoRepository.ListarStatus: TArray<TLookupItemDTO>;
var
  Qry: TFDQuery;
  Lista: TArray<TLookupItemDTO>;
  Count: Integer;
begin
  SetLength(Lista, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT codigo_status_bem, descricao_status_bem ' +
      'FROM USER_geoapolo_satfi_status_imobilizado WITH (NOLOCK) ' +
      'ORDER BY codigo_status_bem ASC';
    Qry.Open;
    Count := 0;
    while not Qry.Eof do
    begin
      SetLength(Lista, Count + 1);
      Lista[Count].Codigo    := Qry.FieldByName('codigo_status_bem').AsString;
      Lista[Count].Descricao := Qry.FieldByName('descricao_status_bem').AsString;
      Inc(Count);
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
  Result := Lista;
end;

function TAtivoImobilizadoRepository.ListarEmpresas: TArray<TLookupItemDTO>;
var
  Qry: TFDQuery;
  Lista: TArray<TLookupItemDTO>;
  Count: Integer;
begin
  SetLength(Lista, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT empcod, empnome ' +
      'FROM USER_geoapolo_empresas WITH (NOLOCK) ' +
      'ORDER BY empcod ASC';
    Qry.Open;
    Count := 0;
    while not Qry.Eof do
    begin
      SetLength(Lista, Count + 1);
      Lista[Count].Codigo    := Qry.FieldByName('empcod').AsString;
      Lista[Count].Descricao := Qry.FieldByName('empnome').AsString;
      Inc(Count);
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
  Result := Lista;
end;

end.
