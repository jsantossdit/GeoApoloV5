unit unt_nomesamigaveis_service;

{
  GeoApolo - Serviço de Regras de Negócio para Nomes Amigáveis de Objetos
  Clean Architecture: Normalização, heurística de sugestão de nomes e persistência.
}

interface

uses
  System.SysUtils, System.Classes,
  unt_nomesamigaveis_types, unt_nomesamigaveis_repository;

type

  TNomesAmigaveisService = class
  private
    FRepository: TNomesAmigaveisRepository;
  public
    constructor Create(ARepository: TNomesAmigaveisRepository);

    function SugerirNomeAmigavel(const ANomeTecnico: string): string;
    function ListarObjetos(const ACategoria, AFiltro: string;
      out ALista: TArray<TDadosObjetoAmigavel>): Boolean;
    function ObterObjeto(const ANomeObjeto: string;
      out ADados: TDadosObjetoAmigavel): Boolean;
    function AtualizarObjeto(const ANomeObjeto, ANomeAmigavel, ACategoria: string;
      out AResultado: TResultadoNomesAmigaveis): Boolean;
    function SalvarObjeto(const ADados: TDadosObjetoAmigavel;
      out AResultado: TResultadoNomesAmigaveis): Boolean;
    function GerarSugestoesAutomaticas(out ATotalAtualizados: Integer): Boolean;
  end;

implementation

{ TNomesAmigaveisService }

constructor TNomesAmigaveisService.Create(
  ARepository: TNomesAmigaveisRepository);
begin
  inherited Create;
  if not Assigned(ARepository) then
    raise EArgumentNilException.Create('TNomesAmigaveisService: Repositorio nao pode ser nulo.');
  FRepository := ARepository;
end;

function TNomesAmigaveisService.SugerirNomeAmigavel(
  const ANomeTecnico: string): string;
const
  PREFIXOS: array[0..10] of string = (
    'tbsheet', 'btn', 'mnu', 'tbs', 'pnl', 'lbl', 'cbo', 'edt', 'chk', 'rbtn', 'frm'
  );
var
  sNome: string;
  sPartes: TStringList;
  sParte: string;
  i: Integer;
begin
  sNome := Trim(ANomeTecnico);
  i := LastDelimiter('.', sNome);
  if i > 0 then
    sNome := Copy(sNome, i + 1, MaxInt);

  for sParte in PREFIXOS do
  begin
    if (Length(sNome) > Length(sParte)) and
       (SameText(Copy(sNome, 1, Length(sParte)), sParte)) then
    begin
      Delete(sNome, 1, Length(sParte));
      Break;
    end;
  end;

  sPartes := TStringList.Create;
  try
    sPartes.Add('');
    for i := 1 to Length(sNome) do
    begin
      if (i > 1) and CharInSet(sNome[i], ['A'..'Z']) and
         not CharInSet(sNome[i - 1], ['A'..'Z']) then
        sPartes.Add(sNome[i])
      else
        sPartes[sPartes.Count - 1] := sPartes[sPartes.Count - 1] + sNome[i];
    end;

    Result := '';
    for sParte in sPartes do
    begin
      if Trim(sParte) <> '' then
        Result := Result + ' ' + UpperCase(sParte[1]) + Copy(sParte, 2, MaxInt);
    end;
    Result := Trim(Result);
  finally
    sPartes.Free;
  end;

  if Result = '' then
    Result := ANomeTecnico;
end;

function TNomesAmigaveisService.ListarObjetos(const ACategoria,
  AFiltro: string; out ALista: TArray<TDadosObjetoAmigavel>): Boolean;
begin
  Result := FRepository.ListarObjetos(Trim(ACategoria), Trim(AFiltro), ALista);
end;

function TNomesAmigaveisService.ObterObjeto(const ANomeObjeto: string;
  out ADados: TDadosObjetoAmigavel): Boolean;
begin
  if Trim(ANomeObjeto) = '' then
  begin
    ADados := Default(TDadosObjetoAmigavel);
    Result := False;
    Exit;
  end;
  Result := FRepository.ObterObjeto(Trim(ANomeObjeto), ADados);
end;

function TNomesAmigaveisService.AtualizarObjeto(const ANomeObjeto,
  ANomeAmigavel, ACategoria: string;
  out AResultado: TResultadoNomesAmigaveis): Boolean;
var
  ObjLimpo, AmigavelLimpo, CategLimpa: string;
begin
  Result := False;
  AResultado.Sucesso := False;
  AResultado.TotalAfetados := 0;

  ObjLimpo := Trim(ANomeObjeto);
  AmigavelLimpo := Trim(ANomeAmigavel);
  CategLimpa := Trim(ACategoria);
  if CategLimpa = '' then
    CategLimpa := 'Geral';

  if ObjLimpo = '' then
  begin
    AResultado.Mensagem := 'Nome tecnico do objeto e obrigatorio.';
    Exit;
  end;

  if AmigavelLimpo = '' then
  begin
    AResultado.Mensagem := 'Nome amigavel nao pode ser em branco.';
    Exit;
  end;

  try
    if FRepository.AtualizarNomeAmigavel(ObjLimpo, AmigavelLimpo, CategLimpa) then
    begin
      AResultado.Sucesso := True;
      AResultado.TotalAfetados := 1;
      AResultado.Mensagem := 'Nome amigavel atualizado com sucesso!';
      Result := True;
    end
    else
    begin
      AResultado.Mensagem := 'Falha ao atualizar registro no banco de dados.';
    end;
  except
    on E: Exception do
      AResultado.Mensagem := 'Erro ao atualizar nome amigavel: ' + E.Message;
  end;
end;

function TNomesAmigaveisService.SalvarObjeto(
  const ADados: TDadosObjetoAmigavel;
  out AResultado: TResultadoNomesAmigaveis): Boolean;
var
  DadosLimpos: TDadosObjetoAmigavel;
begin
  Result := False;
  AResultado.Sucesso := False;
  AResultado.TotalAfetados := 0;

  if Trim(ADados.NomeObjeto) = '' then
  begin
    AResultado.Mensagem := 'Nome tecnico do objeto e obrigatorio.';
    Exit;
  end;

  DadosLimpos := ADados;
  DadosLimpos.NomeObjeto := Trim(ADados.NomeObjeto);
  DadosLimpos.NomeAmigavel := Trim(ADados.NomeAmigavel);
  if DadosLimpos.NomeAmigavel = '' then
    DadosLimpos.NomeAmigavel := SugerirNomeAmigavel(DadosLimpos.NomeObjeto);

  DadosLimpos.Categoria := Trim(ADados.Categoria);
  if DadosLimpos.Categoria = '' then
    DadosLimpos.Categoria := 'Geral';

  try
    if FRepository.SalvarObjeto(DadosLimpos) then
    begin
      AResultado.Sucesso := True;
      AResultado.TotalAfetados := 1;
      AResultado.Mensagem := 'Objeto cadastrado/atualizado com sucesso!';
      Result := True;
    end
    else
    begin
      AResultado.Mensagem := 'Falha ao salvar objeto no banco.';
    end;
  except
    on E: Exception do
      AResultado.Mensagem := 'Erro ao salvar objeto: ' + E.Message;
  end;
end;

function TNomesAmigaveisService.GerarSugestoesAutomaticas(
  out ATotalAtualizados: Integer): Boolean;
var
  Lista: TArray<TDadosObjetoAmigavel>;
  Item: TDadosObjetoAmigavel;
  Sugestao: string;
begin
  Result := False;
  ATotalAtualizados := 0;

  if not FRepository.ListarObjetos('', '', Lista) then
    Exit;

  for Item in Lista do
  begin
    // Sò sugere se ainda estiver vazio ou igual ao nome técnico original
    if (Trim(Item.NomeAmigavel) = '') or (SameText(Trim(Item.NomeAmigavel), Trim(Item.NomeObjeto))) then
    begin
      Sugestao := SugerirNomeAmigavel(Item.NomeObjeto);
      if FRepository.AtualizarNomeAmigavel(Item.NomeObjeto, Sugestao, Item.Categoria) then
        Inc(ATotalAtualizados);
    end;
  end;

  Result := True;
end;

end.
