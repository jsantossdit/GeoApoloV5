unit unt_configsys_types;

{
  Tipos de Dados e DTOs para Configurações Gerais e Parâmetros do Sistema.
  Isolado de VCL, forms e componentes visuais.
}

interface

uses
  System.SysUtils, System.Classes;

type
  TConfiguracoesSistemaDTO = record
    EmpresaCodigo             : string;
    CaminhoBackupSistema      : string;
    InstalacaoLocal           : string;
    LocalNovasVersoes         : string;
    LocalInstaladorVersoes    : string;
    CaminhoArquivoConvenio    : string;
    CaminhoInventario         : string;
    CaminhoDocTI              : string;
    CaminhoDocMissaoPopular   : string;
    CaminhoBaseAlvoLoja       : string;
    EntCategParceira          : string;
    EntCodConsumidorFinal     : string;
    NomeConsumidorFinal       : string;
    OrigCodEstr               : string;
    MotOcorCodEstr            : string;
    IntegraEntidadesApolo     : string; // 'Integra', 'Mescla', 'Não Integra'
    GrupoHardware             : string;
    GrupoSoftware             : string;
    TempoMaximoMissao         : string;
    StatusFechaPIC            : string;
  end;

  TServidorEmailDTO = record
    CodigoServidor      : string;
    Protocolo           : string;
    ServidorEnvio       : string;
    PortaEnvio          : Integer;
    ServidorRecebimento : string;
    PortaRecebimento    : Integer;
  end;

  TContaEmailDTO = record
    CodigoConta    : string;
    ContaEmail     : string;
    Senha          : string;
    CodigoServidor : string;
  end;

  TOperacaoResultado = record
    Sucesso  : Boolean;
    Mensagem : string;
    Codigo   : string;
  end;

implementation

end.
