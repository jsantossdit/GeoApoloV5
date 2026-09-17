unit unt_ocorrencia_types;

interface

uses
  System.SysUtils, System.Classes;

type
  TOcorrenciaDTO = record
    OcorCod        : string;
    OcorStat       : string; // 'Pendente', 'Em Andamento', 'Resolvido', 'Cancelado', 'Transferido'
    EntCod         : string;
    OcorEntNome    : string;
    OcorRespSol    : string;
    OcorData       : string;
    MotOcorCodEstr : string;
    MotOcorDescr   : string;
    OcorTexto      : string;
    OcorRespTexto  : string;
    OrigCodEstr    : string;
    OrigNome       : string;
    EmpCod         : string;
    OcorDataCanc   : string;
    OcorRespCanc   : string;
    OcorMotCanc    : string;
  end;

  TMotivoOcorDTO = record
    MotOcorCodEstr : string;
    MotOcorDescr   : string;
    MotOcorGrupo   : string; // 'T' (area), 'F' (motivo)
    MotOcorResp1   : string;
    MotOcorResp2   : string;
    MotOcorResp3   : string;
  end;

  TOrigemDTO = record
    OrigCodEstr : string;
    OrigNome    : string;
  end;

  TSolicitanteDTO = record
    EntCod      : string;
    EntNome     : string;
    CategCodEstr: string;
    EntStatDescr: string;
  end;

  TResultadoOcorrencia = record
    Sucesso : Boolean;
    Mensagem: string;
    IdGerado: string;
  end;

implementation

end.
