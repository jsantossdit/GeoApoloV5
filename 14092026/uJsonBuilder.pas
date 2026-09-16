unit uJsonBuilder;

interface

uses
  System.SysUtils, System.Classes, System.JSON, System.Generics.Collections,
  Data.DB, FireDAC.Comp.Client, FireDAC.Stan.Param, system.Variants;

type
  // Record para armazenar o mapeamento
  TFieldMapping = record
    CampoView: string;
    CampoJSON: string;
    TipoDado: string;
    ObjetoAninhado: string; // Ex: 'EntidadeUserFieldsObject'
    ValorPadrao: string;
  end;

  TJsonBuilder = class
  private
    FMapeamentos: TList<TFieldMapping>;
    FTemplateJSON: TJSONObject;
    FConnection: TFDConnection;
    FNomeTemplate: string; // Nome do template a ser usado

    procedure CarregarMapeamentos;
    procedure CarregarTemplate;
    function ObterValorFormatado(const Valor: Variant; const Tipo: string): TJSONValue;
    procedure PreencherObjetoAninhado(JSONObj: TJSONObject; const NomeObjeto: string;
      const Campo, Valor: string);

  public
    constructor Create(AConnection: TFDConnection; const NomeTemplate: string = 'entidade');
    destructor Destroy; override;

    function MontarJSON(Dataset: TDataSet): TJSONObject;
    procedure AtualizarMapeamento(const CampoView, CampoJSON, Tipo, ObjetoAninhado, ValorPadrao: string);
    procedure TrocarTemplate(const NovoNomeTemplate: string);

    property NomeTemplate: string read FNomeTemplate write FNomeTemplate;
  end;

implementation

constructor TJsonBuilder.Create(AConnection: TFDConnection; const NomeTemplate: string = 'entidade');
begin
  inherited Create;
  FConnection := AConnection;
  FNomeTemplate := NomeTemplate;
  FMapeamentos := TList<TFieldMapping>.Create;

  CarregarMapeamentos;
  CarregarTemplate;
end;

destructor TJsonBuilder.Destroy;
begin
  FreeAndNil(FMapeamentos);
  FreeAndNil(FTemplateJSON);
  inherited;
end;

procedure TJsonBuilder.CarregarMapeamentos;
var
  Query: TFDQuery;
  Mapping: TFieldMapping;
begin
  Query := TFDQuery.Create(nil);
  try
    Query.Connection := FConnection;

    // Busca mapeamentos para um template específico
    Query.SQL.Text :=
      'SELECT m.campo_view, m.campo_json, m.tipo_dado, m.objeto_aninhado, m.valor_padrao ' +
      'FROM user_geoapolo_mapeamento_json_campos m ' +
      'INNER JOIN user_geoapolo_json_templates t ON m.template_id = t.id ' +
      'WHERE t.nome = :template_nome AND m.ativo = 1 AND t.ativo = 1 ' +
      'ORDER BY m.ordem';

    Query.ParamByName('template_nome').AsString := FNomeTemplate;
    Query.Open;

    FMapeamentos.Clear;

    while not Query.Eof do
    begin
      Mapping.CampoView := Query.FieldByName('campo_view').AsString;
      Mapping.CampoJSON := Query.FieldByName('campo_json').AsString;
      Mapping.TipoDado := Query.FieldByName('tipo_dado').AsString;
      Mapping.ObjetoAninhado := Query.FieldByName('objeto_aninhado').AsString;
      Mapping.ValorPadrao := Query.FieldByName('valor_padrao').AsString;

      FMapeamentos.Add(Mapping);
      Query.Next;
    end;

  finally
    Query.Free;
  end;
end;

procedure TJsonBuilder.CarregarTemplate;
var
  Query: TFDQuery;
  TemplateStr: string;
begin
  Query := TFDQuery.Create(nil);
  try
    Query.Connection := FConnection;
    Query.SQL.Text :=
      'SELECT template_json FROM user_geoapolo_json_templates WHERE nome = :nome AND ativo = 1';
    Query.ParamByName('nome').AsString := FNomeTemplate;
    Query.Open;

    if not Query.IsEmpty then
    begin
      TemplateStr := Query.FieldByName('template_json').AsString;
      FTemplateJSON := TJSONObject.ParseJSONValue(TemplateStr) as TJSONObject;
    end
    else
    begin
      // Template padrão se não encontrar no banco
      FTemplateJSON := TJSONObject.Create;
    end;

  finally
    Query.Free;
  end;
end;

function TJsonBuilder.ObterValorFormatado(const Valor: Variant; const Tipo: string): TJSONValue;
var
  TipoLower: string;
begin
  Result := nil;

  if VarIsNull(Valor) or VarIsEmpty(Valor) then
  begin
    Result := TJSONNull.Create;
    Exit;
  end;

  TipoLower := LowerCase(Tipo);

  if TipoLower = 'string' then
    Result := TJSONString.Create(VarToStr(Valor))
  else if (TipoLower = 'integer') or (TipoLower = 'int') then
    Result := TJSONNumber.Create(StrToIntDef(VarToStr(Valor), 0))
  else if (TipoLower = 'float') or (TipoLower = 'decimal') or (TipoLower = 'currency') then
    Result := TJSONNumber.Create(StrToFloatDef(VarToStr(Valor), 0.0))
  else if (TipoLower = 'boolean') or (TipoLower = 'bool') then
    Result := TJSONBool.Create(StrToBoolDef(VarToStr(Valor), False))
  else if (TipoLower = 'datetime') or (TipoLower = 'date') then
  begin
    try
      Result := TJSONString.Create(FormatDateTime('yyyy-mm-dd"T"hh:nn:ss.zzz"-03:00"',
        StrToDateTime(VarToStr(Valor))));
    except
      Result := TJSONString.Create(VarToStr(Valor));
    end;
  end
  else
    Result := TJSONString.Create(VarToStr(Valor));
end;

procedure TJsonBuilder.PreencherObjetoAninhado(JSONObj: TJSONObject;
  const NomeObjeto, Campo, Valor: string);
var
  ObjetoAninhado: TJSONObject;
begin
  // Verifica se o objeto aninhado já existe
  ObjetoAninhado := JSONObj.GetValue(NomeObjeto) as TJSONObject;

  if ObjetoAninhado = nil then
  begin
    // Cria o objeto aninhado se não existir
    ObjetoAninhado := TJSONObject.Create;
    JSONObj.AddPair(NomeObjeto, ObjetoAninhado);
  end;

  // Adiciona ou atualiza o campo no objeto aninhado
  ObjetoAninhado.RemovePair(Campo); // Remove se já existir
  ObjetoAninhado.AddPair(Campo, TJSONString.Create(Valor));
end;

function TJsonBuilder.MontarJSON(Dataset: TDataSet): TJSONObject;
var
  Mapping: TFieldMapping;
  Field: TField;
  ValorFormatado: TJSONValue;
  I: Integer;
begin
  Result := FTemplateJSON.Clone as TJSONObject;

  // Percorre todos os mapeamentos configurados
  for I := 0 to FMapeamentos.Count - 1 do
  begin
    Mapping := FMapeamentos[I];

    // Procura o campo na view/dataset
    Field := Dataset.FindField(Mapping.CampoView);

    if Assigned(Field) then
    begin
      // Campo existe na view
      ValorFormatado := ObterValorFormatado(Field.Value, Mapping.TipoDado);

      if Mapping.ObjetoAninhado <> '' then
      begin
        // Campo pertence a um objeto aninhado
        PreencherObjetoAninhado(Result, Mapping.ObjetoAninhado,
          Mapping.CampoJSON, Field.AsString);
      end
      else
      begin
        // Campo do nível raiz
        Result.RemovePair(Mapping.CampoJSON); // Remove se já existir
        Result.AddPair(Mapping.CampoJSON, ValorFormatado);
      end;
    end
    else if Mapping.ValorPadrao <> '' then
    begin
      // Campo não existe na view, usa valor padrão
      ValorFormatado := ObterValorFormatado(Mapping.ValorPadrao, Mapping.TipoDado);

      if Mapping.ObjetoAninhado <> '' then
        PreencherObjetoAninhado(Result, Mapping.ObjetoAninhado,
          Mapping.CampoJSON, Mapping.ValorPadrao)
      else
        Result.AddPair(Mapping.CampoJSON, ValorFormatado);
    end;
  end;
end;

procedure TJsonBuilder.AtualizarMapeamento(const CampoView, CampoJSON, Tipo,
  ObjetoAninhado, ValorPadrao: string);
var
  Query: TFDQuery;
  TemplateId: Integer;
begin
  Query := TFDQuery.Create(nil);
  try
    Query.Connection := FConnection;

    // Primeiro, pega o ID do template atual
    Query.SQL.Text := 'SELECT id FROM user_geoapolo_json_templates WHERE nome = :nome AND ativo = 1';
    Query.ParamByName('nome').AsString := FNomeTemplate;
    Query.Open;

    if Query.IsEmpty then
      raise Exception.Create('Template não encontrado: ' + FNomeTemplate);

    TemplateId := Query.FieldByName('id').AsInteger;
    Query.Close;

    // Agora insere/atualiza o mapeamento
    Query.SQL.Text :=
      'INSERT INTO user_geoapolo_mapeamento_json_campos ' +
      '(template_id, campo_view, campo_json, tipo_dado, objeto_aninhado, valor_padrao, ativo) ' +
      'VALUES (:template_id, :campo_view, :campo_json, :tipo_dado, :objeto_aninhado, :valor_padrao, 1) ' +
      'ON DUPLICATE KEY UPDATE ' +
      'tipo_dado = :tipo_dado2, objeto_aninhado = :objeto_aninhado2, ' +
      'valor_padrao = :valor_padrao2';

    Query.ParamByName('template_id').AsInteger := TemplateId;
    Query.ParamByName('campo_view').AsString := CampoView;
    Query.ParamByName('campo_json').AsString := CampoJSON;
    Query.ParamByName('tipo_dado').AsString := Tipo;
    Query.ParamByName('tipo_dado2').AsString := Tipo;
    Query.ParamByName('objeto_aninhado').AsString := ObjetoAninhado;
    Query.ParamByName('objeto_aninhado2').AsString := ObjetoAninhado;
    Query.ParamByName('valor_padrao').AsString := ValorPadrao;
    Query.ParamByName('valor_padrao2').AsString := ValorPadrao;

    Query.ExecSQL;

  finally
    Query.Free;
  end;
end;

procedure TJsonBuilder.TrocarTemplate(const NovoNomeTemplate: string);
begin
  if FNomeTemplate <> NovoNomeTemplate then
  begin
    FNomeTemplate := NovoNomeTemplate;

    // Recarrega mapeamentos e template
    FreeAndNil(FTemplateJSON);
    CarregarMapeamentos;
    CarregarTemplate;
  end;
end;

end.

// ===== EXEMPLO DE USO =====

{unit uExemploUso;

interface

uses
  uJsonBuilder, Data.DB, FireDAC.Comp.Client, System.JSON;

procedure ExemploDeUso;

implementation

procedure ExemploDeUso;
var
  JsonBuilder: TJsonBuilder;
  Query: TFDQuery;
  JSONResult: TJSONObject;
  Connection: TFDConnection;
begin
  Connection := TFDConnection.Create(nil);
  JsonBuilder := TJsonBuilder.Create(Connection);
  Query := TFDQuery.Create(nil);

  try
    // Configura conexão...

    // Consulta sua view
    Query.Connection := Connection;
    Query.SQL.Text := 'SELECT * FROM sua_view WHERE codigo = :codigo';
    Query.ParamByName('codigo').AsString := '3005700';
    Query.Open;

    if not Query.IsEmpty then
    begin
      // Monta o JSON baseado nos mapeamentos
      JSONResult := JsonBuilder.MontarJSON(Query);

      // Usa o JSON
      Writeln(JSONResult.ToJSON);

      JSONResult.Free;
    end;

  finally
    Query.Free;
    JsonBuilder.Free;
    Connection.Free;
  end;
end;   }

end.
