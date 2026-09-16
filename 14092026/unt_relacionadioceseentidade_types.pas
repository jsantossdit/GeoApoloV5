unit unt_relacionadioceseentidade_types;

interface

uses
  System.SysUtils, System.Classes;

type
  /// <summary>
  /// Representa os dados da entidade para vínculo com diocese.
  /// </summary>
  TEntidadeDioceseDTO = record
    EntCod: string;
    EntNome: string;
    CidCod: string;
    CidNomeComp: string;
    UFSigla: string;
    USERDioceseId: string;
    USERNomeDiocese: string;
    USERJanaSVE: string; // 'S', 'N' ou ''
    function TemDiocese: Boolean;
    function StatusSVEResumo: string;
  end;

  /// <summary>
  /// Representa uma Diocese da CNBB e sua localização.
  /// </summary>
  TDioceseCNBBDTO = record
    Id: string;
    EstadoId: string;
    Nome: string;
    DescricaoCidade: string;
    UFSigla: string;
    NomeEstado: string;
  end;

  /// <summary>
  /// Filtro para pesquisa de entidades no período.
  /// </summary>
  TFiltroEntidadeDioceseDTO = record
    DataInicial: TDateTime;
    DataFinal: TDateTime;
    ApenasSemDiocese: Boolean;
  end;

  /// <summary>
  /// Resultado de operações de vínculo ou desvínculo.
  /// </summary>
  TResultadoVinculoDiocese = record
    Sucesso: Boolean;
    Mensagem: string;
    EntidadesAfetadas: Integer;
    class function CriarSucesso(const AMensagem: string; const ATotal: Integer = 1): TResultadoVinculoDiocese; static;
    class function CriarFalha(const AMensagem: string): TResultadoVinculoDiocese; static;
  end;

implementation

{ TEntidadeDioceseDTO }

function TEntidadeDioceseDTO.TemDiocese: Boolean;
begin
  Result := (Trim(USERDioceseId) <> '') and (Trim(USERNomeDiocese) <> '');
end;

function TEntidadeDioceseDTO.StatusSVEResumo: string;
begin
  if SameText(USERJanaSVE, 'S') then
    Result := 'JÁ DISPONÍVEL NA SVE'
  else if SameText(USERJanaSVE, 'N') then
    Result := 'NÃO INCLUÍDA NA SVE'
  else
    Result := 'NÃO INFORMADO';
end;

{ TResultadoVinculoDiocese }

class function TResultadoVinculoDiocese.CriarSucesso(const AMensagem: string; const ATotal: Integer): TResultadoVinculoDiocese;
begin
  Result.Sucesso := True;
  Result.Mensagem := AMensagem;
  Result.EntidadesAfetadas := ATotal;
end;

class function TResultadoVinculoDiocese.CriarFalha(const AMensagem: string): TResultadoVinculoDiocese;
begin
  Result.Sucesso := False;
  Result.Mensagem := AMensagem;
  Result.EntidadesAfetadas := 0;
end;

end.
