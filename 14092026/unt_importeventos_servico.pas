unit unt_importeventos_servico;

interface

uses
  System.SysUtils,
  unt_importeventos_model, unt_importeventos_repository;

type
  /// <summary>Resolve, a partir de um CPF/CNPJ, se a pessoa existe no Apolo e se
  /// "colabora com projetos" (tem categoria de projeto E contribuição registrada).
  /// Isola a regra de negócio do acesso a dados e do parsing de planilha.</summary>
  IServicoVinculoApolo = interface
    ['{2E7C9C0B-6E9E-4E42-8C7D-9E7A0B2C3F44}']
    function ObterVinculo(const ADocumento: string; AConcatenarCategorias: Boolean): TInfoVinculoApolo;
  end;

  TServicoVinculoApolo = class(TInterfacedObject, IServicoVinculoApolo)
  private
    FRepositorio: IRepositorioCongressoRcc;
  public
    constructor Create(ARepositorio: IRepositorioCongressoRcc);
    function ObterVinculo(const ADocumento: string; AConcatenarCategorias: Boolean): TInfoVinculoApolo;
  end;

implementation

constructor TServicoVinculoApolo.Create(ARepositorio: IRepositorioCongressoRcc);
begin
  inherited Create;
  FRepositorio := ARepositorio;
end;

function TServicoVinculoApolo.ObterVinculo(const ADocumento: string;
  AConcatenarCategorias: Boolean): TInfoVinculoApolo;
var
  vDocumento: string;
  vEntidade: TInfoEntidade;
begin
  Result := Default (TInfoVinculoApolo); // EntCod/CategCodEstr/AnoMes = '', ColaboraProjetos = False
  vDocumento := SomenteDigitos(ADocumento);
  if vDocumento = '' then
    Exit;

  vEntidade := FRepositorio.BuscarEntidadePorDocumento(vDocumento);
  if not vEntidade.Encontrado then
    Exit;

  Result.EntCod := vEntidade.EntCod;

  if AConcatenarCategorias then
    Result.CategCodEstr := FRepositorio.BuscarCategoriasProjeto(Result.EntCod)
  else
    Result.CategCodEstr := FRepositorio.BuscarCategoriaProjeto(Result.EntCod);

  Result.AnoMesUltimaContribuicao := FRepositorio.BuscarUltimaContribuicao(Result.EntCod);

  Result.ColaboraProjetos := (Result.CategCodEstr <> '') and (Result.AnoMesUltimaContribuicao <> '');
end;

end.
