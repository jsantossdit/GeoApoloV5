unit unt_desligafunc_types;

interface

uses
  System.SysUtils, System.Classes;

type
  /// <summary>
  /// DTO que representa os dados cadastrais do funcionário/usuário para desligamento.
  /// </summary>
  TUsuarioDesligamentoDTO = record
    UsuCod: string;
    UsuNome: string;
    UsuDepto: string;
    UsuStat: string;
  end;

  /// <summary>
  /// Resultado da operação de desligamento/desativação.
  /// </summary>
  TResultadoDesligamentoDTO = record
    Sucesso: Boolean;
    Mensagem: string;
    VinculosEntidadesRemovidos: Integer;
    VinculosCategoriasRemovidos: Integer;
    PermissoesRelatoriosRemovidas: Integer;
    PermissoesContasFinRemovidas: Integer;
    class function CriarSucesso(const AMensagem: string): TResultadoDesligamentoDTO; static;
    class function CriarFalha(const AMensagem: string): TResultadoDesligamentoDTO; static;
  end;

implementation

class function TResultadoDesligamentoDTO.CriarSucesso(const AMensagem: string): TResultadoDesligamentoDTO;
begin
  Result.Sucesso := True;
  Result.Mensagem := AMensagem;
  Result.VinculosEntidadesRemovidos := 0;
  Result.VinculosCategoriasRemovidos := 0;
  Result.PermissoesRelatoriosRemovidas := 0;
  Result.PermissoesContasFinRemovidas := 0;
end;

class function TResultadoDesligamentoDTO.CriarFalha(const AMensagem: string): TResultadoDesligamentoDTO;
begin
  Result.Sucesso := False;
  Result.Mensagem := AMensagem;
  Result.VinculosEntidadesRemovidos := 0;
  Result.VinculosCategoriasRemovidos := 0;
  Result.PermissoesRelatoriosRemovidas := 0;
  Result.PermissoesContasFinRemovidas := 0;
end;

end.
