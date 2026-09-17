unit unt_empresa_types;

interface

uses
  System.SysUtils, System.Classes;

type
  TEmpresaDTO = record
    EmpCod : string;
    EmpNome: string;
    Ativa  : Boolean;
  end;

  TResultadoEmpresa = record
    Sucesso : Boolean;
    Mensagem: string;
  end;

implementation

end.
