unit unt_usuario_ctasfin_types;

interface

uses
  System.SysUtils, System.Classes, System.Generics.Collections;

type
  /// <summary>
  /// DTO que representa uma conta financeira do sistema Apolo.
  /// </summary>
  TContaFinanceiraDTO = record
    ContaFinCod: string;
    ContaFinNome: string;
    ContaFinCcorNum: string;
    function ToStringFormatado: string;
  end;

  /// <summary>
  /// DTO que representa a associação entre um usuário e uma conta financeira.
  /// </summary>
  TUsuarioContaFinDTO = record
    UsuCod: string;
    ContaFinCod: string;
    ContaFinNome: string;
  end;

  /// <summary>
  /// Resultado padronizado das operações de permissão de contas financeiras.
  /// </summary>
  TResultadoOperacaoContasFin = record
    Sucesso: Boolean;
    Mensagem: string;
    TotalAfetado: Integer;
    class function CriarSucesso(const AMensagem: string; ATotal: Integer = 0): TResultadoOperacaoContasFin; static;
    class function CriarFalha(const AMensagem: string): TResultadoOperacaoContasFin; static;
  end;

implementation

function TContaFinanceiraDTO.ToStringFormatado: string;
begin
  Result := Trim(ContaFinCod) + ' -> ' + Trim(ContaFinNome);
end;

class function TResultadoOperacaoContasFin.CriarSucesso(const AMensagem: string; ATotal: Integer): TResultadoOperacaoContasFin;
begin
  Result.Sucesso := True;
  Result.Mensagem := AMensagem;
  Result.TotalAfetado := ATotal;
end;

class function TResultadoOperacaoContasFin.CriarFalha(const AMensagem: string): TResultadoOperacaoContasFin;
begin
  Result.Sucesso := False;
  Result.Mensagem := AMensagem;
  Result.TotalAfetado := 0;
end;

end.
