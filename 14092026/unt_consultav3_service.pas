unit unt_consultav3_service;

interface

uses
  System.SysUtils, System.Classes, FireDAC.Comp.Client,
  unt_consultav3_types, unt_consultav3_repository;

type
  TConsultaService = class
  private
    FRepo: IConsultaRepository;
  public
    constructor Create(ARepository: IConsultaRepository);

    function MontarSqlConsulta(const AFiltro: TConsultaFiltroDTO): string;
    function ExecutarBusca(const AFiltro: TConsultaFiltroDTO; ATargetQuery: TFDQuery): Boolean;
    function ObterTitulo(const AControle: string): string;
  end;

implementation

constructor TConsultaService.Create(ARepository: IConsultaRepository);
begin
  inherited Create;
  if not Assigned(ARepository) then
    raise Exception.Create('TConsultaService: Repositório é obrigatório.');
  FRepo := ARepository;
end;

function TConsultaService.ObterTitulo(const AControle: string): string;
begin
  if AControle = 'CIDADE_CIDADE' then
    Result := 'Pesquisa de Cidades'
  else if AControle = 'CLIENTES' then
    Result := 'Pesquisa de Entidades e Clientes'
  else if AControle = 'CONTA_FINANCEIRASALDO' then
    Result := 'Pesquisa de Contas Financeiras'
  else if AControle = 'USUARIO_DEPARTAMENTO' then
    Result := 'Pesquisa de Departamentos'
  else if Pos('CATEGORIA', AControle) > 0 then
    Result := 'Pesquisa de Categorias'
  else if Pos('TIPOLOGRADOURO', AControle) > 0 then
    Result := 'Pesquisa de Tipos de Logradouro'
  else if Pos('ATIVIDADE_ECONOMICA', AControle) > 0 then
    Result := 'Pesquisa de Atividades Econômicas'
  else
    Result := 'Consulta Geral do Sistema';
end;

function TConsultaService.MontarSqlConsulta(const AFiltro: TConsultaFiltroDTO): string;
var
  CampoBusca, CampoOrdem, Direcao: string;
begin
  CampoBusca := Trim(AFiltro.CampoBusca);
  CampoOrdem := Trim(AFiltro.CampoOrdem);
  Direcao    := IfThen(AFiltro.OrdemAsc, 'ASC', 'DESC');

  // TODO: [SQLAlchemy Migration]
  // Cada bloco if corresponde a uma Model/View no SQLAlchemy.
  // Criar classes de QueryStrategy dinâmicas.

  if AFiltro.Controle = 'CIDADE_CIDADE' then
  begin
    if CampoBusca = '' then CampoBusca := 'cidnomecomp';
    if CampoOrdem = '' then CampoOrdem := 'cidnomecomp';
    Result :=
      'SELECT geocidcod as cidcod, cidnomecomp, ufsigla ' +
      '  FROM user_geoapolo_cidades WITH (NOLOCK) ' +
      ' WHERE ' + CampoBusca + ' LIKE :termo ' +
      ' ORDER BY ' + CampoOrdem + ' ' + Direcao;
  end
  else if AFiltro.Controle = 'CONTA_FINANCEIRASALDO' then
  begin
    if CampoBusca = '' then CampoBusca := 'contafinnome';
    if CampoOrdem = '' then CampoOrdem := 'contafinnome';
    Result :=
      'SELECT contafincod, contafinnome ' +
      '  FROM USER_geoapolo_contasfinanceiras WITH (NOLOCK) ' +
      ' WHERE ' + CampoBusca + ' LIKE :termo ' +
      ' ORDER BY ' + CampoOrdem + ' ' + Direcao;
  end
  else if AFiltro.Controle = 'USUARIO_DEPARTAMENTO' then
  begin
    if CampoBusca = '' then CampoBusca := 'nome_departamento';
    if CampoOrdem = '' then CampoOrdem := 'nome_departamento';
    Result :=
      'SELECT codigo_departamento, nome_departamento ' +
      '  FROM USER_geoapolo_departamentos WITH (NOLOCK) ' +
      ' WHERE ' + CampoBusca + ' LIKE :termo ' +
      ' ORDER BY ' + CampoOrdem + ' ' + Direcao;
  end
  else if AFiltro.Controle = 'CATEGORIA_ENTIDADE' then
  begin
    if CampoBusca = '' then CampoBusca := 'geocategnome';
    if CampoOrdem = '' then CampoOrdem := 'geocategnome';
    Result :=
      'SELECT geocategcodestr, geocategnome ' +
      '  FROM USER_geoapolo_categoria WITH (NOLOCK) ' +
      ' WHERE ' + CampoBusca + ' LIKE :termo ' +
      ' ORDER BY ' + CampoOrdem + ' ' + Direcao;
  end
  else if AFiltro.Controle = 'TIPOLOGRADOURO' then
  begin
    if CampoBusca = '' then CampoBusca := 'tipolograd';
    if CampoOrdem = '' then CampoOrdem := 'tipolograd';
    Result :=
      'SELECT tipolograd, tipologradabrev ' +
      '  FROM USER_geoapolo_tipologradouro WITH (NOLOCK) ' +
      ' WHERE ' + CampoBusca + ' LIKE :termo ' +
      ' ORDER BY ' + CampoOrdem + ' ' + Direcao;
  end
  else
  begin
    // Fallback genérico para clientes / entidades
    if CampoBusca = '' then CampoBusca := 'geoentnome';
    if CampoOrdem = '' then CampoOrdem := 'geoentnome';
    Result :=
      'SELECT TOP (50) geoentcod, geoentnome, geocidcod ' +
      '  FROM USER_geoapolo_entidade WITH (NOLOCK) ' +
      ' WHERE ' + CampoBusca + ' LIKE :termo ' +
      ' ORDER BY ' + CampoOrdem + ' ' + Direcao;
  end;
end;

function TConsultaService.ExecutarBusca(
  const AFiltro: TConsultaFiltroDTO; ATargetQuery: TFDQuery
): Boolean;
var
  Sql: string;
begin
  Sql := MontarSqlConsulta(AFiltro);
  Result := FRepo.ExecutarConsulta(Sql, AFiltro.TextoBusca, ATargetQuery);
end;

end.
