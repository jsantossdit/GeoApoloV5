unit unt_excluicontabil_types;

interface

uses
  System.SysUtils, System.Classes;

type
  /// <summary>
  /// DTO representando um lançamento contábil no Apolo.
  /// </summary>
  TLancamentoContabilDTO = record
    Chave: string;
    NumeroOrigem: string;
    OrigemChave: string;
    Modulo: string;
    SubModulo: string;
    Data: TDateTime;
    EmpresaCod: string;
    Valor: Currency;
    Historico: string;
    ContaDebito: string;
    ContaCredito: string;
  end;

  /// <summary>
  /// Resultado da checagem de integridade referencial antes da exclusão.
  /// </summary>
  TValidacaoExclusaoDTO = record
    Permitido: Boolean;
    Mensagem: string;
    OrigemDetectada: string;
    class function PermitidoOk: TValidacaoExclusaoDTO; static;
    class function Bloqueado(const AMotivo, AOrigem: string): TValidacaoExclusaoDTO; static;
  end;

  /// <summary>
  /// Parâmetros de pesquisa para exclusão em lote por módulo.
  /// </summary>
  TFiltroExclusaoModuloDTO = record
    DataInicial: TDateTime;
    DataFinal: TDateTime;
    Modulo: string;
    SubModulo: string;
    EmpresaCod: string;
  end;

  /// <summary>
  /// Resultado da operação de exclusão contábil.
  /// </summary>
  TResultadoExclusaoContabil = record
    Sucesso: Boolean;
    Mensagem: string;
    RegistrosExcluidos: Integer;
    class function CriarSucesso(const AMensagem: string; ATotal: Integer): TResultadoExclusaoContabil; static;
    class function CriarFalha(const AMensagem: string): TResultadoExclusaoContabil; static;
  end;

implementation

class function TValidacaoExclusaoDTO.PermitidoOk: TValidacaoExclusaoDTO;
begin
  Result.Permitido := True;
  Result.Mensagem := 'Exclusão permitida.';
  Result.OrigemDetectada := '';
end;

class function TValidacaoExclusaoDTO.Bloqueado(const AMotivo, AOrigem: string): TValidacaoExclusaoDTO;
begin
  Result.Permitido := False;
  Result.Mensagem := AMotivo;
  Result.OrigemDetectada := AOrigem;
end;

class function TResultadoExclusaoContabil.CriarSucesso(const AMensagem: string; ATotal: Integer): TResultadoExclusaoContabil;
begin
  Result.Sucesso := True;
  Result.Mensagem := AMensagem;
  Result.RegistrosExcluidos := ATotal;
end;

class function TResultadoExclusaoContabil.CriarFalha(const AMensagem: string): TResultadoExclusaoContabil;
begin
  Result.Sucesso := False;
  Result.Mensagem := AMensagem;
  Result.RegistrosExcluidos := 0;
end;

end.
