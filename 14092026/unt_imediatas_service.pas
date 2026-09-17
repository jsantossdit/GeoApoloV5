unit unt_imediatas_service;

{
  GeoApolo - Serviço de Regras de Negócio para Consultas Imediatas e Exportações
  Clean Architecture: Validação de segurança SQL e exportação desacoplada.
}

interface

uses
  System.SysUtils, System.Classes, System.Diagnostics, Data.DB, FireDAC.Comp.Client,
  unt_imediatas_types, unt_imediatas_repository;

type

  TImediatasService = class
  private
    FRepository: TImediatasRepository;
  public
    constructor Create(ARepository: TImediatasRepository);

    function ListarConsultasPermitidas(const ABanco, AUsucod: string;
      out ALista: TArray<TDadosConsultaImediata>): Boolean;
    function ObterConsulta(const ACodigo: string;
      out ADados: TDadosConsultaImediata): Boolean;

    function ValidarSegurancaSQL(const ASentencaSQL: string; out AMensagemErro: string): Boolean;
    function ExecutarConsulta(const ASentencaSQL: string; AQueryDestino: TFDQuery;
      AConexaoAlvo: TFDConnection = nil): TResultadoExecucaoConsulta;

    function ExportarDataSetParaCSV(ADataSet: TDataSet; const ACaminhoArquivo: string;
      const ADelimitador: Char = ';'): TResultadoExportacao;
  end;

implementation

{ TImediatasService }

constructor TImediatasService.Create(ARepository: TImediatasRepository);
begin
  inherited Create;
  if not Assigned(ARepository) then
    raise EArgumentNilException.Create('TImediatasService: Repositorio nao pode ser nulo.');
  FRepository := ARepository;
end;

function TImediatasService.ListarConsultasPermitidas(const ABanco,
  AUsucod: string; out ALista: TArray<TDadosConsultaImediata>): Boolean;
begin
  Result := FRepository.ListarConsultasPermitidas(ABanco, AUsucod, ALista);
end;

function TImediatasService.ObterConsulta(const ACodigo: string;
  out ADados: TDadosConsultaImediata): Boolean;
begin
  if Trim(ACodigo) = '' then
    Exit(False);
  Result := FRepository.ObterConsulta(ACodigo, ADados);
end;

function TImediatasService.ValidarSegurancaSQL(const ASentencaSQL: string;
  out AMensagemErro: string): Boolean;
var
  SqlUpper: string;
begin
  Result := False;
  AMensagemErro := '';
  SqlUpper := UpperCase(Trim(ASentencaSQL));

  if SqlUpper = '' then
  begin
    AMensagemErro := 'A sentenca SQL da consulta esta vazia.';
    Exit;
  end;

  // Consultas imediatas devem ser somente leitura (SELECT ou WITH CTE)
  if (not SqlUpper.StartsWith('SELECT')) and (not SqlUpper.StartsWith('WITH')) then
  begin
    AMensagemErro := 'Apenas instrucoes de leitura (SELECT ou WITH) sao permitidas em consultas imediatas.';
    Exit;
  end;

  // Bloqueia comandos destrutivos
  if Pos('DROP ', SqlUpper) > 0 then
  begin
    AMensagemErro := 'Comando proibido detectado: DROP.';
    Exit;
  end;
  if Pos('TRUNCATE ', SqlUpper) > 0 then
  begin
    AMensagemErro := 'Comando proibido detectado: TRUNCATE.';
    Exit;
  end;
  if (Pos('DELETE ', SqlUpper) > 0) or (Pos('DELETE FROM', SqlUpper) > 0) then
  begin
    AMensagemErro := 'Comando proibido detectado: DELETE.';
    Exit;
  end;
  if Pos('UPDATE ', SqlUpper) > 0 then
  begin
    AMensagemErro := 'Comando proibido detectado: UPDATE.';
    Exit;
  end;
  if Pos('ALTER TABLE', SqlUpper) > 0 then
  begin
    AMensagemErro := 'Comando proibido detectado: ALTER TABLE.';
    Exit;
  end;

  Result := True;
end;

function TImediatasService.ExecutarConsulta(const ASentencaSQL: string;
  AQueryDestino: TFDQuery; AConexaoAlvo: TFDConnection): TResultadoExecucaoConsulta;
var
  Stopwatch: TStopwatch;
  MsgErro: string;
begin
  Result.Sucesso         := False;
  Result.Mensagem        := '';
  Result.TotalRegistros  := 0;
  Result.TempoExecucaoMs := 0;

  if not ValidarSegurancaSQL(ASentencaSQL, MsgErro) then
  begin
    Result.Mensagem := MsgErro;
    Exit;
  end;

  try
    Stopwatch := TStopwatch.StartNew;
    Result.TotalRegistros := FRepository.ExecutarConsultaSQL(ASentencaSQL, AQueryDestino, AConexaoAlvo);
    Stopwatch.Stop;

    Result.TempoExecucaoMs := Stopwatch.ElapsedMilliseconds;
    Result.Sucesso         := True;
    Result.Mensagem        := Format('Consulta executada com sucesso. %d registro(s) obtido(s) em %d ms.',
      [Result.TotalRegistros, Result.TempoExecucaoMs]);
  except
    on E: Exception do
    begin
      Result.Mensagem := 'Erro ao executar consulta no banco de dados: ' + E.Message;
    end;
  end;
end;

function TImediatasService.ExportarDataSetParaCSV(ADataSet: TDataSet;
  const ACaminhoArquivo: string; const ADelimitador: Char): TResultadoExportacao;
var
  Arquivo: TStringList;
  Linha: string;
  I: Integer;
  Total: Integer;
begin
  Result.Sucesso        := False;
  Result.Mensagem       := '';
  Result.CaminhoArquivo := ACaminhoArquivo;
  Result.TotalLinhas    := 0;

  if not Assigned(ADataSet) or (not ADataSet.Active) then
  begin
    Result.Mensagem := 'DataSet invalido ou fechado para exportacao.';
    Exit;
  end;

  Arquivo := TStringList.Create;
  try
    // Cabeçalho com nomes dos campos
    Linha := '';
    for I := 0 to ADataSet.FieldCount - 1 do
    begin
      if I > 0 then
        Linha := Linha + ADelimitador;
      Linha := Linha + '"' + StringReplace(ADataSet.Fields[I].DisplayName, '"', '""', [rfReplaceAll]) + '"';
    end;
    Arquivo.Add(Linha);

    // Linhas de dados
    Total := 0;
    ADataSet.DisableControls;
    try
      ADataSet.First;
      while not ADataSet.Eof do
      begin
        Linha := '';
        for I := 0 to ADataSet.FieldCount - 1 do
        begin
          if I > 0 then
            Linha := Linha + ADelimitador;
          Linha := Linha + '"' + StringReplace(ADataSet.Fields[I].AsString, '"', '""', [rfReplaceAll]) + '"';
        end;
        Arquivo.Add(Linha);
        Inc(Total);
        ADataSet.Next;
      end;
    finally
      ADataSet.EnableControls;
    end;

    Arquivo.SaveToFile(ACaminhoArquivo, TEncoding.UTF8);
    Result.Sucesso     := True;
    Result.TotalLinhas := Total;
    Result.Mensagem    := Format('Exportacao concluida com sucesso. %d linha(s) gravada(s).', [Total]);
  finally
    Arquivo.Free;
  end;
end;

end.
