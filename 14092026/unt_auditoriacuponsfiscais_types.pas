unit unt_auditoriacuponsfiscais_types;

interface

uses
  System.SysUtils, System.Classes;

type
  /// <summary>
  /// Representa os dados auditados de uma NFC-e emitida no PDV / Caixa.
  /// </summary>
  TAuditoriaCupomDTO = record
    EmpCod: string;
    EntCod: string;
    EntNome: string;
    Serie: string;
    NFNum: string;
    ValorTotal: Currency;
    StatusSefaz: string; // 'Transmitiu' ou 'Não Transmitiu'
    IntegradoAlvo: Boolean;
    IntegradoFinanc: Boolean;
    IntegradoFiscal: Boolean;
    BaixouEstoque: Boolean;
    function StatusResumo: string;
  end;

  /// <summary>
  /// Contadores consolidados da auditoria do caixa.
  /// </summary>
  TResumoAuditoriaCupomDTO = record
    TotalCupons: Integer;
    TotalTransmitidos: Integer;
    TotalNaoTransmitidos: Integer;
    TotalIntegrados: Integer;
    TotalNaoIntegrados: Integer;
    TotalIntegradosFinanc: Integer;
    TotalIntegradosFiscal: Integer;
    TotalBaixouEstoque: Integer;
  end;

  /// <summary>
  /// Resultado da sincronização/correção de flags de cupom fiscal no Apolo.
  /// </summary>
  TResultadoSincronizacaoCupom = record
    Sucesso: Boolean;
    Mensagem: string;
    CuponsAtualizados: Integer;
    class function CriarSucesso(const AMensagem: string; ATotal: Integer): TResultadoSincronizacaoCupom; static;
    class function CriarFalha(const AMensagem: string): TResultadoSincronizacaoCupom; static;
  end;

implementation

function TAuditoriaCupomDTO.StatusResumo: string;
begin
  Result := Format('NFC-e %s (Série %s) - R$ %.2f | SEFAZ: %s', [NFNum, Serie, ValorTotal, StatusSefaz]);
end;

class function TResultadoSincronizacaoCupom.CriarSucesso(const AMensagem: string; ATotal: Integer): TResultadoSincronizacaoCupom;
begin
  Result.Sucesso := True;
  Result.Mensagem := AMensagem;
  Result.CuponsAtualizados := ATotal;
end;

class function TResultadoSincronizacaoCupom.CriarFalha(const AMensagem: string): TResultadoSincronizacaoCupom;
begin
  Result.Sucesso := False;
  Result.Mensagem := AMensagem;
  Result.CuponsAtualizados := 0;
end;

end.
