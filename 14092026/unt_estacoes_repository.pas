unit unt_estacoes_repository;

{
  Repositório FireDAC para o módulo de Estações de Trabalho.
  Garante persistência segura, queries parametrizadas e hints WITH (NOLOCK).
  Isolado de interface VCL.
}

interface

uses
  System.SysUtils, System.Classes, Data.DB,
  FireDAC.Comp.Client, FireDAC.Stan.Param,
  unt_estacoes_types;

type
  TEstacoesRepository = class
  private
    FConn: TFDConnection;
  public
    constructor Create(AConnection: TFDConnection);

    // Estações
    function ListarEstacoes(const AFiltro: TEstacaoFiltroDTO): TArray<TEstacaoDTO>;
    function ObterEstacao(const ACodigo: string): TEstacaoDTO;
    function InserirEstacao(const AEstacao: TEstacaoDTO): TOperacaoResultado;
    function AtualizarEstacao(const AEstacao: TEstacaoDTO): TOperacaoResultado;
    function ExcluirEstacao(const ACodigo: string): TOperacaoResultado;

    // Hardware
    function ListarHardwarePorEstacao(const ACodigoEstacao: string): TArray<THardwareDTO>;
    function InserirHardware(const AHardware: THardwareDTO): TOperacaoResultado;
    function AtualizarHardware(const AHardware: THardwareDTO): TOperacaoResultado;
    function ExcluirHardware(const ACodigoHardware: string): TOperacaoResultado;

    // Software
    function ListarSoftwarePorEstacao(const ACodigoEstacao: string): TArray<TSoftwareDTO>;
    function InserirSoftware(const ASoftware: TSoftwareDTO): TOperacaoResultado;
    function AtualizarSoftware(const ASoftware: TSoftwareDTO): TOperacaoResultado;
    function ExcluirSoftware(const ACodigoSoftware: string): TOperacaoResultado;

    // Usuários Vinculados
    function ListarUsuariosPorEstacao(const ACodigoEstacao: string): TArray<TUsuarioEstacaoDTO>;
    function VincularUsuario(const ACodigoUsuario, ACodigoEstacao, AResponsavel: string): TOperacaoResultado;
    function DesvincularUsuario(const ACodigoUsuario, ACodigoEstacao: string): TOperacaoResultado;
  end;

implementation

constructor TEstacoesRepository.Create(AConnection: TFDConnection);
begin
  inherited Create;
  FConn := AConnection;
end;

function TEstacoesRepository.ListarEstacoes(const AFiltro: TEstacaoFiltroDTO): TArray<TEstacaoDTO>;
var
  Qry: TFDQuery;
  SQL: string;
  Lista: TArray<TEstacaoDTO>;
  Item: TEstacaoDTO;
  Count: Integer;
begin
  SetLength(Lista, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    SQL := 'SELECT TOP (500) ' +
           '  e.codigo_estacao, e.descricao, e.codigo_departamento, d.nome_departamento, ' +
           '  e.data_cadastro, e.codigo_usuario, e.usuario_responsavel, e.tag_servico, ' +
           '  e.geoentcod, ent.geoentnome, e.modelo_estacao, e.codigo_localizacao, ' +
           '  loc.localizacao, e.enderecoip, e.observacoes ' +
           'FROM USER_geoapolo_satfi_estacao e WITH (NOLOCK) ' +
           'LEFT JOIN USER_geoapolo_departamentos d WITH (NOLOCK) ON e.codigo_departamento = d.codigo_departamento ' +
           'LEFT JOIN USER_geoapolo_entidade ent WITH (NOLOCK) ON e.geoentcod = ent.geoentcod ' +
           'LEFT JOIN USER_geoapolo_satfi_localizacao_fisica loc WITH (NOLOCK) ON e.codigo_localizacao = loc.codigo_localizacao ' +
           'WHERE 1=1 ';

    if Trim(AFiltro.TextoBusca) <> '' then
    begin
      if SameText(AFiltro.CampoBusca, 'codigo_estacao') then
        SQL := SQL + ' AND e.codigo_estacao LIKE :busca '
      else if SameText(AFiltro.CampoBusca, 'tag_servico') then
        SQL := SQL + ' AND e.tag_servico LIKE :busca '
      else
        SQL := SQL + ' AND e.descricao LIKE :busca ';
    end;

    if Trim(AFiltro.Departamento) <> '' then
      SQL := SQL + ' AND e.codigo_departamento = :departamento ';

    if SameText(AFiltro.CampoOrdem, 'codigo_estacao') then
      SQL := SQL + ' ORDER BY e.codigo_estacao '
    else
      SQL := SQL + ' ORDER BY e.descricao ';

    if AFiltro.OrdemAsc then
      SQL := SQL + ' ASC'
    else
      SQL := SQL + ' DESC';

    Qry.SQL.Text := SQL;

    if Trim(AFiltro.TextoBusca) <> '' then
      Qry.ParamByName('busca').AsString := '%' + Trim(AFiltro.TextoBusca) + '%';
    if Trim(AFiltro.Departamento) <> '' then
      Qry.ParamByName('departamento').AsString := Trim(AFiltro.Departamento);

    Qry.Open;
    Count := 0;
    while not Qry.Eof do
    begin
      SetLength(Lista, Count + 1);
      Item.CodigoEstacao      := Qry.FieldByName('codigo_estacao').AsString;
      Item.Descricao          := Qry.FieldByName('descricao').AsString;
      Item.CodigoDepartamento := Qry.FieldByName('codigo_departamento').AsString;
      Item.NomeDepartamento   := Qry.FieldByName('nome_departamento').AsString;
      Item.DataCadastro       := Qry.FieldByName('data_cadastro').AsDateTime;
      Item.CodigoUsuario      := Qry.FieldByName('codigo_usuario').AsString;
      Item.UsuarioResponsavel := Qry.FieldByName('usuario_responsavel').AsString;
      Item.TagServico         := Qry.FieldByName('tag_servico').AsString;
      Item.GeoEntCod          := Qry.FieldByName('geoentcod').AsString;
      Item.NomeEntidade       := Qry.FieldByName('geoentnome').AsString;
      Item.ModeloEstacao      := Qry.FieldByName('modelo_estacao').AsString;
      Item.CodigoLocalizacao  := Qry.FieldByName('codigo_localizacao').AsString;
      Item.NomeLocalizacao    := Qry.FieldByName('localizacao').AsString;
      Item.EnderecoIP         := Qry.FieldByName('enderecoip').AsString;
      Item.Observacoes        := Qry.FieldByName('observacoes').AsString;
      Lista[Count] := Item;
      Inc(Count);
      Qry.Next;
    end;

    Result := Lista;
  finally
    Qry.Free;
  end;
end;

function TEstacoesRepository.ObterEstacao(const ACodigo: string): TEstacaoDTO;
var
  Qry: TFDQuery;
begin
  FillChar(Result, SizeOf(Result), 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT TOP (1) ' +
                    '  e.codigo_estacao, e.descricao, e.codigo_departamento, d.nome_departamento, ' +
                    '  e.data_cadastro, e.codigo_usuario, e.usuario_responsavel, e.tag_servico, ' +
                    '  e.geoentcod, ent.geoentnome, e.modelo_estacao, e.codigo_localizacao, ' +
                    '  loc.localizacao, e.enderecoip, e.observacoes ' +
                    'FROM USER_geoapolo_satfi_estacao e WITH (NOLOCK) ' +
                    'LEFT JOIN USER_geoapolo_departamentos d WITH (NOLOCK) ON e.codigo_departamento = d.codigo_departamento ' +
                    'LEFT JOIN USER_geoapolo_entidade ent WITH (NOLOCK) ON e.geoentcod = ent.geoentcod ' +
                    'LEFT JOIN USER_geoapolo_satfi_localizacao_fisica loc WITH (NOLOCK) ON e.codigo_localizacao = loc.codigo_localizacao ' +
                    'WHERE e.codigo_estacao = :cod';
    Qry.ParamByName('cod').AsString := ACodigo;
    Qry.Open;

    if not Qry.IsEmpty then
    begin
      Result.CodigoEstacao      := Qry.FieldByName('codigo_estacao').AsString;
      Result.Descricao          := Qry.FieldByName('descricao').AsString;
      Result.CodigoDepartamento := Qry.FieldByName('codigo_departamento').AsString;
      Result.NomeDepartamento   := Qry.FieldByName('nome_departamento').AsString;
      Result.DataCadastro       := Qry.FieldByName('data_cadastro').AsDateTime;
      Result.CodigoUsuario      := Qry.FieldByName('codigo_usuario').AsString;
      Result.UsuarioResponsavel := Qry.FieldByName('usuario_responsavel').AsString;
      Result.TagServico         := Qry.FieldByName('tag_servico').AsString;
      Result.GeoEntCod          := Qry.FieldByName('geoentcod').AsString;
      Result.NomeEntidade       := Qry.FieldByName('geoentnome').AsString;
      Result.ModeloEstacao      := Qry.FieldByName('modelo_estacao').AsString;
      Result.CodigoLocalizacao  := Qry.FieldByName('codigo_localizacao').AsString;
      Result.NomeLocalizacao    := Qry.FieldByName('localizacao').AsString;
      Result.EnderecoIP         := Qry.FieldByName('enderecoip').AsString;
      Result.Observacoes        := Qry.FieldByName('observacoes').AsString;
    end;
  finally
    Qry.Free;
  end;
end;

function TEstacoesRepository.InserirEstacao(const AEstacao: TEstacaoDTO): TOperacaoResultado;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'INSERT INTO USER_geoapolo_satfi_estacao ( ' +
                    '  codigo_estacao, descricao, codigo_departamento, data_cadastro, ' +
                    '  codigo_usuario, usuario_responsavel, tag_servico, geoentcod, ' +
                    '  modelo_estacao, codigo_localizacao, enderecoip, observacoes ' +
                    ') VALUES ( ' +
                    '  :cod, :desc, :dep, :data, :usu, :resp, :tag, :ent, :modelo, :loc, :ip, :obs ' +
                    ')';
    Qry.ParamByName('cod').AsString := AEstacao.CodigoEstacao;
    Qry.ParamByName('desc').AsString := AEstacao.Descricao;
    Qry.ParamByName('dep').AsString := AEstacao.CodigoDepartamento;
    if AEstacao.DataCadastro > 0 then
      Qry.ParamByName('data').AsDateTime := AEstacao.DataCadastro
    else
      Qry.ParamByName('data').AsDateTime := Now;
    Qry.ParamByName('usu').AsString := AEstacao.CodigoUsuario;
    Qry.ParamByName('resp').AsString := AEstacao.UsuarioResponsavel;
    Qry.ParamByName('tag').AsString := AEstacao.TagServico;
    Qry.ParamByName('ent').AsString := AEstacao.GeoEntCod;
    Qry.ParamByName('modelo').AsString := AEstacao.ModeloEstacao;
    Qry.ParamByName('loc').AsString := AEstacao.CodigoLocalizacao;
    Qry.ParamByName('ip').AsString := AEstacao.EnderecoIP;
    Qry.ParamByName('obs').AsString := AEstacao.Observacoes;
    Qry.ExecSQL;

    Result.Sucesso := True;
    Result.Mensagem := 'Estação cadastrada com sucesso!';
    Result.Codigo := AEstacao.CodigoEstacao;
  except
    on E: Exception do
    begin
      Result.Sucesso := False;
      Result.Mensagem := 'Falha ao incluir estação: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

function TEstacoesRepository.AtualizarEstacao(const AEstacao: TEstacaoDTO): TOperacaoResultado;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'UPDATE USER_geoapolo_satfi_estacao SET ' +
                    '  descricao = :desc, ' +
                    '  codigo_departamento = :dep, ' +
                    '  codigo_usuario = :usu, ' +
                    '  usuario_responsavel = :resp, ' +
                    '  tag_servico = :tag, ' +
                    '  geoentcod = :ent, ' +
                    '  modelo_estacao = :modelo, ' +
                    '  codigo_localizacao = :loc, ' +
                    '  enderecoip = :ip, ' +
                    '  observacoes = :obs ' +
                    'WHERE codigo_estacao = :cod';
    Qry.ParamByName('desc').AsString := AEstacao.Descricao;
    Qry.ParamByName('dep').AsString := AEstacao.CodigoDepartamento;
    Qry.ParamByName('usu').AsString := AEstacao.CodigoUsuario;
    Qry.ParamByName('resp').AsString := AEstacao.UsuarioResponsavel;
    Qry.ParamByName('tag').AsString := AEstacao.TagServico;
    Qry.ParamByName('ent').AsString := AEstacao.GeoEntCod;
    Qry.ParamByName('modelo').AsString := AEstacao.ModeloEstacao;
    Qry.ParamByName('loc').AsString := AEstacao.CodigoLocalizacao;
    Qry.ParamByName('ip').AsString := AEstacao.EnderecoIP;
    Qry.ParamByName('obs').AsString := AEstacao.Observacoes;
    Qry.ParamByName('cod').AsString := AEstacao.CodigoEstacao;
    Qry.ExecSQL;

    Result.Sucesso := True;
    Result.Mensagem := 'Estação atualizada com sucesso!';
    Result.Codigo := AEstacao.CodigoEstacao;
  except
    on E: Exception do
    begin
      Result.Sucesso := False;
      Result.Mensagem := 'Falha ao atualizar estação: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

function TEstacoesRepository.ExcluirEstacao(const ACodigo: string): TOperacaoResultado;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;

    // Valida se existem hardwares ou softwares vinculados
    Qry.SQL.Text := 'SELECT COUNT(*) FROM USER_geoapolo_satfi_hardware WITH (NOLOCK) WHERE codigo_estacao = :cod';
    Qry.ParamByName('cod').AsString := ACodigo;
    Qry.Open;
    if Qry.Fields[0].AsInteger > 0 then
    begin
      Result.Sucesso := False;
      Result.Mensagem := 'Não é possível excluir: existem hardwares vinculados a esta estação.';
      Exit;
    end;
    Qry.Close;

    Qry.SQL.Text := 'DELETE FROM USER_geoapolo_usuario_estacao WHERE codigo_estacao = :cod';
    Qry.ParamByName('cod').AsString := ACodigo;
    Qry.ExecSQL;

    Qry.SQL.Text := 'DELETE FROM USER_geoapolo_satfi_estacao WHERE codigo_estacao = :cod';
    Qry.ParamByName('cod').AsString := ACodigo;
    Qry.ExecSQL;

    Result.Sucesso := True;
    Result.Mensagem := 'Estação excluída com sucesso!';
    Result.Codigo := ACodigo;
  except
    on E: Exception do
    begin
      Result.Sucesso := False;
      Result.Mensagem := 'Falha ao excluir estação: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

function TEstacoesRepository.ListarHardwarePorEstacao(const ACodigoEstacao: string): TArray<THardwareDTO>;
var
  Qry: TFDQuery;
  Lista: TArray<THardwareDTO>;
  Item: THardwareDTO;
  Count: Integer;
begin
  SetLength(Lista, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT ' +
                    '  h.codigo_hardware, h.descricao, h.valor, h.data_compra, h.data_ativacao, ' +
                    '  h.tempo_garantia, h.codigo_status_h, h.codigo_estacao, h.codigoclasse, ' +
                    '  h.observacoes, h.nf, ISNULL(h.ip, '''') AS ip, ISNULL(h.rack, '''') AS rack, ' +
                    '  ISNULL(h.patchpanel, '''') AS patchpanel ' +
                    'FROM USER_geoapolo_satfi_hardware h WITH (NOLOCK) ' +
                    'WHERE h.codigo_estacao = :cod ' +
                    'ORDER BY h.codigo_hardware ASC';
    Qry.ParamByName('cod').AsString := ACodigoEstacao;
    Qry.Open;

    Count := 0;
    while not Qry.Eof do
    begin
      SetLength(Lista, Count + 1);
      Item.CodigoHardware := Qry.FieldByName('codigo_hardware').AsString;
      Item.Descricao      := Qry.FieldByName('descricao').AsString;
      Item.Valor          := Qry.FieldByName('valor').AsFloat;
      Item.DataCompra     := Qry.FieldByName('data_compra').AsDateTime;
      Item.DataAtivacao   := Qry.FieldByName('data_ativacao').AsDateTime;
      Item.TempoGarantia  := Qry.FieldByName('tempo_garantia').AsInteger;
      Item.CodigoStatus   := Qry.FieldByName('codigo_status_h').AsInteger;
      Item.CodigoEstacao  := Qry.FieldByName('codigo_estacao').AsString;
      Item.CodigoClasse   := Qry.FieldByName('codigoclasse').AsInteger;
      Item.Observacoes    := Qry.FieldByName('observacoes').AsString;
      Item.NF             := Qry.FieldByName('nf').AsString;
      Item.EnderecoIP     := Qry.FieldByName('ip').AsString;
      Item.Rack           := Qry.FieldByName('rack').AsString;
      Item.PatchPanel     := Qry.FieldByName('patchpanel').AsString;
      Lista[Count] := Item;
      Inc(Count);
      Qry.Next;
    end;

    Result := Lista;
  finally
    Qry.Free;
  end;
end;

function TEstacoesRepository.InserirHardware(const AHardware: THardwareDTO): TOperacaoResultado;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'INSERT INTO USER_geoapolo_satfi_hardware ( ' +
                    '  codigo_hardware, descricao, valor, data_compra, data_ativacao, ' +
                    '  tempo_garantia, codigo_status_h, codigo_estacao, codigoclasse, ' +
                    '  observacoes, nf, ip, rack, patchpanel ' +
                    ') VALUES ( ' +
                    '  :cod, :desc, :val, :compra, :ativacao, :garantia, :status, :estacao, ' +
                    '  :classe, :obs, :nf, :ip, :rack, :patch ' +
                    ')';
    Qry.ParamByName('cod').AsString := AHardware.CodigoHardware;
    Qry.ParamByName('desc').AsString := AHardware.Descricao;
    Qry.ParamByName('val').AsFloat := AHardware.Valor;
    if AHardware.DataCompra > 0 then
      Qry.ParamByName('compra').AsDateTime := AHardware.DataCompra
    else
      Qry.ParamByName('compra').Clear;
    if AHardware.DataAtivacao > 0 then
      Qry.ParamByName('ativacao').AsDateTime := AHardware.DataAtivacao
    else
      Qry.ParamByName('ativacao').Clear;
    Qry.ParamByName('garantia').AsInteger := AHardware.TempoGarantia;
    Qry.ParamByName('status').AsInteger := AHardware.CodigoStatus;
    Qry.ParamByName('estacao').AsString := AHardware.CodigoEstacao;
    Qry.ParamByName('classe').AsInteger := AHardware.CodigoClasse;
    Qry.ParamByName('obs').AsString := AHardware.Observacoes;
    Qry.ParamByName('nf').AsString := AHardware.NF;
    Qry.ParamByName('ip').AsString := AHardware.EnderecoIP;
    Qry.ParamByName('rack').AsString := AHardware.Rack;
    Qry.ParamByName('patch').AsString := AHardware.PatchPanel;
    Qry.ExecSQL;

    Result.Sucesso := True;
    Result.Mensagem := 'Hardware cadastrado com sucesso!';
    Result.Codigo := AHardware.CodigoHardware;
  except
    on E: Exception do
    begin
      Result.Sucesso := False;
      Result.Mensagem := 'Falha ao incluir hardware: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

function TEstacoesRepository.AtualizarHardware(const AHardware: THardwareDTO): TOperacaoResultado;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'UPDATE USER_geoapolo_satfi_hardware SET ' +
                    '  descricao = :desc, valor = :val, tempo_garantia = :garantia, ' +
                    '  codigo_status_h = :status, codigoclasse = :classe, observacoes = :obs, ' +
                    '  nf = :nf, ip = :ip, rack = :rack, patchpanel = :patch ' +
                    'WHERE codigo_hardware = :cod';
    Qry.ParamByName('desc').AsString := AHardware.Descricao;
    Qry.ParamByName('val').AsFloat := AHardware.Valor;
    Qry.ParamByName('garantia').AsInteger := AHardware.TempoGarantia;
    Qry.ParamByName('status').AsInteger := AHardware.CodigoStatus;
    Qry.ParamByName('classe').AsInteger := AHardware.CodigoClasse;
    Qry.ParamByName('obs').AsString := AHardware.Observacoes;
    Qry.ParamByName('nf').AsString := AHardware.NF;
    Qry.ParamByName('ip').AsString := AHardware.EnderecoIP;
    Qry.ParamByName('rack').AsString := AHardware.Rack;
    Qry.ParamByName('patch').AsString := AHardware.PatchPanel;
    Qry.ParamByName('cod').AsString := AHardware.CodigoHardware;
    Qry.ExecSQL;

    Result.Sucesso := True;
    Result.Mensagem := 'Hardware atualizado com sucesso!';
    Result.Codigo := AHardware.CodigoHardware;
  except
    on E: Exception do
    begin
      Result.Sucesso := False;
      Result.Mensagem := 'Falha ao atualizar hardware: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

function TEstacoesRepository.ExcluirHardware(const ACodigoHardware: string): TOperacaoResultado;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'DELETE FROM USER_geoapolo_satfi_hardware WHERE codigo_hardware = :cod';
    Qry.ParamByName('cod').AsString := ACodigoHardware;
    Qry.ExecSQL;

    Result.Sucesso := True;
    Result.Mensagem := 'Hardware excluído com sucesso!';
    Result.Codigo := ACodigoHardware;
  except
    on E: Exception do
    begin
      Result.Sucesso := False;
      Result.Mensagem := 'Falha ao excluir hardware: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

function TEstacoesRepository.ListarSoftwarePorEstacao(const ACodigoEstacao: string): TArray<TSoftwareDTO>;
var
  Qry: TFDQuery;
  Lista: TArray<TSoftwareDTO>;
  Item: TSoftwareDTO;
  Count: Integer;
begin
  SetLength(Lista, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT ' +
                    '  codigo_software, descricao, nfsoft, valor, data_compra, ' +
                    '  data_vencimento, tipo_licenca, codigo_estacao, codigoclasse, observacoes ' +
                    'FROM USER_geoapolo_satfi_software WITH (NOLOCK) ' +
                    'WHERE codigo_estacao = :cod ' +
                    'ORDER BY codigo_software ASC';
    Qry.ParamByName('cod').AsString := ACodigoEstacao;
    Qry.Open;

    Count := 0;
    while not Qry.Eof do
    begin
      SetLength(Lista, Count + 1);
      Item.CodigoSoftware := Qry.FieldByName('codigo_software').AsString;
      Item.Descricao      := Qry.FieldByName('descricao').AsString;
      Item.NF             := Qry.FieldByName('nfsoft').AsString;
      Item.Valor          := Qry.FieldByName('valor').AsFloat;
      Item.DataCompra     := Qry.FieldByName('data_compra').AsDateTime;
      Item.DataVencimento := Qry.FieldByName('data_vencimento').AsDateTime;
      Item.TipoLicenca    := Qry.FieldByName('tipo_licenca').AsString;
      Item.CodigoEstacao  := Qry.FieldByName('codigo_estacao').AsString;
      Item.CodigoClasse   := Qry.FieldByName('codigoclasse').AsInteger;
      Item.Observacoes    := Qry.FieldByName('observacoes').AsString;
      Lista[Count] := Item;
      Inc(Count);
      Qry.Next;
    end;

    Result := Lista;
  finally
    Qry.Free;
  end;
end;

function TEstacoesRepository.InserirSoftware(const ASoftware: TSoftwareDTO): TOperacaoResultado;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'INSERT INTO USER_geoapolo_satfi_software ( ' +
                    '  codigo_software, descricao, nfsoft, valor, data_compra, ' +
                    '  data_vencimento, tipo_licenca, codigo_estacao, codigoclasse, observacoes ' +
                    ') VALUES ( ' +
                    '  :cod, :desc, :nf, :val, :compra, :venc, :lic, :estacao, :classe, :obs ' +
                    ')';
    Qry.ParamByName('cod').AsString := ASoftware.CodigoSoftware;
    Qry.ParamByName('desc').AsString := ASoftware.Descricao;
    Qry.ParamByName('nf').AsString := ASoftware.NF;
    Qry.ParamByName('val').AsFloat := ASoftware.Valor;
    if ASoftware.DataCompra > 0 then
      Qry.ParamByName('compra').AsDateTime := ASoftware.DataCompra
    else
      Qry.ParamByName('compra').Clear;
    if ASoftware.DataVencimento > 0 then
      Qry.ParamByName('venc').AsDateTime := ASoftware.DataVencimento
    else
      Qry.ParamByName('venc').Clear;
    Qry.ParamByName('lic').AsString := ASoftware.TipoLicenca;
    Qry.ParamByName('estacao').AsString := ASoftware.CodigoEstacao;
    Qry.ParamByName('classe').AsInteger := ASoftware.CodigoClasse;
    Qry.ParamByName('obs').AsString := ASoftware.Observacoes;
    Qry.ExecSQL;

    Result.Sucesso := True;
    Result.Mensagem := 'Software registrado com sucesso!';
    Result.Codigo := ASoftware.CodigoSoftware;
  except
    on E: Exception do
    begin
      Result.Sucesso := False;
      Result.Mensagem := 'Falha ao incluir software: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

function TEstacoesRepository.AtualizarSoftware(const ASoftware: TSoftwareDTO): TOperacaoResultado;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'UPDATE USER_geoapolo_satfi_software SET ' +
                    '  descricao = :desc, nfsoft = :nf, valor = :val, ' +
                    '  tipo_licenca = :lic, codigoclasse = :classe, observacoes = :obs ' +
                    'WHERE codigo_software = :cod';
    Qry.ParamByName('desc').AsString := ASoftware.Descricao;
    Qry.ParamByName('nf').AsString := ASoftware.NF;
    Qry.ParamByName('val').AsFloat := ASoftware.Valor;
    Qry.ParamByName('lic').AsString := ASoftware.TipoLicenca;
    Qry.ParamByName('classe').AsInteger := ASoftware.CodigoClasse;
    Qry.ParamByName('obs').AsString := ASoftware.Observacoes;
    Qry.ParamByName('cod').AsString := ASoftware.CodigoSoftware;
    Qry.ExecSQL;

    Result.Sucesso := True;
    Result.Mensagem := 'Software atualizado com sucesso!';
    Result.Codigo := ASoftware.CodigoSoftware;
  except
    on E: Exception do
    begin
      Result.Sucesso := False;
      Result.Mensagem := 'Falha ao atualizar software: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

function TEstacoesRepository.ExcluirSoftware(const ACodigoSoftware: string): TOperacaoResultado;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'DELETE FROM USER_geoapolo_satfi_software WHERE codigo_software = :cod';
    Qry.ParamByName('cod').AsString := ACodigoSoftware;
    Qry.ExecSQL;

    Result.Sucesso := True;
    Result.Mensagem := 'Software excluído com sucesso!';
    Result.Codigo := ACodigoSoftware;
  except
    on E: Exception do
    begin
      Result.Sucesso := False;
      Result.Mensagem := 'Falha ao excluir software: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

function TEstacoesRepository.ListarUsuariosPorEstacao(const ACodigoEstacao: string): TArray<TUsuarioEstacaoDTO>;
var
  Qry: TFDQuery;
  Lista: TArray<TUsuarioEstacaoDTO>;
  Item: TUsuarioEstacaoDTO;
  Count: Integer;
begin
  SetLength(Lista, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT ' +
                    '  ue.codigo_usuario, u.usunome, ue.codigo_estacao, ue.data_vinculo, ue.responsavel ' +
                    'FROM USER_geoapolo_usuario_estacao ue WITH (NOLOCK) ' +
                    'LEFT JOIN USER_geoapolo_usuarios u WITH (NOLOCK) ON ue.codigo_usuario = u.usucod ' +
                    'WHERE ue.codigo_estacao = :cod ' +
                    'ORDER BY u.usunome ASC';
    Qry.ParamByName('cod').AsString := ACodigoEstacao;
    Qry.Open;

    Count := 0;
    while not Qry.Eof do
    begin
      SetLength(Lista, Count + 1);
      Item.CodigoUsuario := Qry.FieldByName('codigo_usuario').AsString;
      Item.NomeUsuario   := Qry.FieldByName('usunome').AsString;
      Item.CodigoEstacao := Qry.FieldByName('codigo_estacao').AsString;
      Item.DataVinculo   := Qry.FieldByName('data_vinculo').AsDateTime;
      Item.Responsavel   := Qry.FieldByName('responsavel').AsString;
      Lista[Count] := Item;
      Inc(Count);
      Qry.Next;
    end;

    Result := Lista;
  finally
    Qry.Free;
  end;
end;

function TEstacoesRepository.VincularUsuario(const ACodigoUsuario, ACodigoEstacao, AResponsavel: string): TOperacaoResultado;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'INSERT INTO USER_geoapolo_usuario_estacao (codigo_usuario, codigo_estacao, data_vinculo, responsavel) ' +
                    'VALUES (:usu, :est, GETDATE(), :resp)';
    Qry.ParamByName('usu').AsString := ACodigoUsuario;
    Qry.ParamByName('est').AsString := ACodigoEstacao;
    Qry.ParamByName('resp').AsString := AResponsavel;
    Qry.ExecSQL;

    Result.Sucesso := True;
    Result.Mensagem := 'Usuário vinculado à estação com sucesso!';
    Result.Codigo := ACodigoUsuario;
  except
    on E: Exception do
    begin
      Result.Sucesso := False;
      Result.Mensagem := 'Falha ao vincular usuário: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

function TEstacoesRepository.DesvincularUsuario(const ACodigoUsuario, ACodigoEstacao: string): TOperacaoResultado;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'DELETE FROM USER_geoapolo_usuario_estacao WHERE codigo_usuario = :usu AND codigo_estacao = :est';
    Qry.ParamByName('usu').AsString := ACodigoUsuario;
    Qry.ParamByName('est').AsString := ACodigoEstacao;
    Qry.ExecSQL;

    Result.Sucesso := True;
    Result.Mensagem := 'Vínculo do usuário removido com sucesso!';
    Result.Codigo := ACodigoUsuario;
  except
    on E: Exception do
    begin
      Result.Sucesso := False;
      Result.Mensagem := 'Falha ao desvincular usuário: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

end.
