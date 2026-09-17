unit unt_departamentos_types;

{
  GeoApolo - Tipos e DTOs para Gestão de Departamentos e Seções
  Clean Architecture: Tipos desacoplados sem dependência de VCL ou DataSets.
}

interface

uses
  System.SysUtils;

type

  TDadosDepartamento = record
    CodigoDepartamento : Integer;
    NomeDepartamento   : string;
    EmpCod             : string;
    EmpNome            : string;
    FlagAtivo          : string; // 'A' = Ativo, 'I' = Inativo
    CCtrlCodEstr       : string; // Centro de controle / custo vinculado
    CCtrlNome          : string;
  end;

  TResultadoDepartamento = record
    Sucesso            : Boolean;
    Mensagem           : string;
    CodigoDepartamento : Integer;
  end;

implementation

end.
