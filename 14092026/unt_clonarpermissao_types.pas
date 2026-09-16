unit unt_clonarpermissao_types;

{
  Tipos de Dados, DTOs e Estruturas para Clonagem de Permissões de Usuários.
  Totalmente desacoplado de VCL, forms e componentes de tela.
}

interface

uses
  System.SysUtils, System.Classes;

type
  TOpcoesClonagemDTO = record
    DireitosSistema      : Boolean;
    Relatorios           : Boolean;
    ContasFinanceiras    : Boolean;
    Formularios          : Boolean;
    CategoriasEntidades  : Boolean;
    TipoPagarReceber     : Boolean;
    GruposUsuario        : Boolean;
    Favoritos            : Boolean;
    TourUsuario          : Boolean;
    EmpresasFiliais      : Boolean;
    class function CriarTodasAtivas: TOpcoesClonagemDTO; static;
  end;

  TUsuarioResumoDTO = record
    Codigo : string;
    Nome   : string;
  end;

  TRelatorioClonagemDTO = record
    TotalDireitosSistema     : Integer;
    TotalRelatorios          : Integer;
    TotalContasFinanceiras   : Integer;
    TotalFormularios         : Integer;
    TotalCategoriasEntidades : Integer;
    TotalTipoPagarReceber    : Integer;
    TotalGruposUsuario       : Integer;
    TotalFavoritos           : Integer;
    TotalTourUsuario         : Integer;
    TotalEmpresasFiliais     : Integer;
    TotalGeral               : Integer;
  end;

  TOperacaoResultadoClonagem = record
    Sucesso     : Boolean;
    Mensagem    : string;
    TotalItens  : Integer;
    Relatorio   : TRelatorioClonagemDTO;
  end;

implementation

class function TOpcoesClonagemDTO.CriarTodasAtivas: TOpcoesClonagemDTO;
begin
  Result.DireitosSistema      := True;
  Result.Relatorios           := True;
  Result.ContasFinanceiras    := True;
  Result.Formularios          := True;
  Result.CategoriasEntidades  := True;
  Result.TipoPagarReceber     := True;
  Result.GruposUsuario        := True;
  Result.Favoritos            := True;
  Result.TourUsuario          := True;
  Result.EmpresasFiliais      := True;
end;

end.
