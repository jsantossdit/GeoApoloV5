unit unt_cadentidades;
interface
uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, ComCtrls, vcl.StdCtrls, Buttons, vcl.ExtCtrls, Mask, Grids, DBGrids,
  unt_consultav3, Data.DB, Data.DBXJSON, Data.DBXJSONReflect, idHTTP, IdSSLOpenSSL, System.JSON,
  Datasnap.DBClient, Vcl.Menus, System.Net.HttpClient, System.Net.URLClient, uEntidade, uEntidadeService,
  StrUtils, IniFiles, System.Net.HttpClientComponent;
// =============================================================================
//  CONSTANTES DE INTEGRAÇÃO — evita strings mágicas espalhadas pelo código
// =============================================================================
const
  BANCO_GEOAPOLO    = 'GeoApolo';
  BANCO_ALVO        = 'Alvo';
  INTEG_INTEGRA     = 'Integra';
  INTEG_NAO_INTEGRA = 'Não Integra';
  INTEG_MESCLA      = 'Mescla';
  // Controles de tela
  TELA1 = 'TELA1';
  TELA2 = 'TELA2';
  TELA3 = 'TELA3';
  TELA4 = 'TELA4';
  TELA5 = 'TELA5';
  TELA6 = 'TELA6';
  TELA7 = 'TELA7';
type
  TEnderecoInfo = record
    Logradouro: string;
    Cidade: string;
    Bairro: string;
    UF: string;
    CEP: string;
    Erro: Boolean;
    MensagemErro: string;
  end;
type
  Tfrmcadentidade = class(TForm)
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spbligacoes: TSpeedButton;
    spbsair: TSpeedButton;
    spblimpar: TSpeedButton;
    lblsair: TLabel;
    spbexcluir: TSpeedButton;
    StatusBar1: TStatusBar;
    Label2: TLabel;
    cin1: TPageControl;
    tabprincipal: TTabSheet;
    GroupBox1: TGroupBox;
    spbuscacidade: TSpeedButton;
    lblnomecidade: TLabel;
    lblcep: TLabel;
    lbltipofj: TLabel;
    lbldatacad: TLabel;
    lbldtnascimento: TLabel;
    lblestadocivil: TLabel;
    lblfalecido: TLabel;
    lblescolaridade: TLabel;
    lblsexo: TLabel;
    spbuscaocupacao: TSpeedButton;
    lblnomecargo: TLabel;
    spbgravatela1: TSpeedButton;
    spbuscatipotrat: TSpeedButton;
    spbuscalogradouro: TSpeedButton;
    lblentcod: TLabeledEdit;
    lblentnome: TLabeledEdit;
    lblentnomefantasia: TLabeledEdit;
    lblentenderno: TLabeledEdit;
    lblentender: TEdit;
    lblentendercompl: TLabeledEdit;
    lblentbair: TLabeledEdit;
    lblcidcod: TLabeledEdit;
    lbluf: TLabeledEdit;
    mskcep: TMaskEdit;
    cbotipofj: TComboBox;
    mskdtcadastro: TMaskEdit;
    mskdtnascimento: TMaskEdit;
    cboestadocivil: TComboBox;
    cbofalecido: TComboBox;
    cboescolaridade: TComboBox;
    cbosexo: TComboBox;
    lblcaixapostal: TLabeledEdit;
    lblcargocodestr: TLabeledEdit;
    lbltipotrat: TLabeledEdit;
    lbllogradouro: TLabeledEdit;
    tabcomplementar: TTabSheet;
    cin2: TPageControl;
    tabdadospessoais: TTabSheet;
    GroupBox11: TGroupBox;
    lblpossuifilhos: TLabel;
    spbdadospessoais: TSpeedButton;
    lblnomedopai: TLabeledEdit;
    lblnomedamae: TLabeledEdit;
    lblresidecom: TLabeledEdit;
    rdgfilhos_sim: TRadioButton;
    rdgfilhosnao: TRadioButton;
    lblquantosfilhos: TLabeledEdit;
    tabfinanceiro: TTabSheet;
    GroupBox8: TGroupBox;
    spbbuscatipocobcod: TSpeedButton;
    lbltipocobnome: TLabel;
    spbbco: TSpeedButton;
    lblnomebanco: TLabel;
    spbagencia: TSpeedButton;
    lblnomeagencia: TLabel;
    spbdadosfinanceiros: TSpeedButton;
    lblgeracarne: TLabel;
    spbuscadiocese: TSpeedButton;
    lbldiocesenome: TLabel;
    lbltipocobcod: TLabeledEdit;
    lblbconum: TLabeledEdit;
    lblagnum: TLabeledEdit;
    lbldiadebitoautomatico: TLabeledEdit;
    cbogeracarne: TComboBox;
    lbldioceseid: TLabeledEdit;
    tab_informacoescomplementares: TTabSheet;
    GroupBox3: TGroupBox;
    spbuscatividade: TSpeedButton;
    lblnomeatividade_economica: TLabel;
    spbuscaorigem: TSpeedButton;
    lblnomeorigem: TLabel;
    spbuscaregiao: TSpeedButton;
    lblnomeregiao: TLabel;
    lblativecodestr: TLabeledEdit;
    lblorigcodestr: TLabeledEdit;
    lblregiao: TLabeledEdit;
    lblconceito: TLabeledEdit;
    rdgcobranca: TRadioGroup;
    rdgentrega: TRadioGroup;
    tab_endereco_cobranca_outro: TTabSheet;
    spbuscalogradourocobranca: TSpeedButton;
    spbuscacidadecob: TSpeedButton;
    spbenderecocobranca: TSpeedButton;
    Label11: TLabel;
    lbllogradourocobranca: TLabeledEdit;
    lblendereco_cobranca: TLabeledEdit;
    lblnumerocobranca: TLabeledEdit;
    lblbairrocob: TLabeledEdit;
    lblcomplementocob: TLabeledEdit;
    mskcep_cob: TMaskEdit;
    lblcidadecobranca: TLabeledEdit;
    lblestadocob: TLabeledEdit;
    gridcobranca: TDBGrid;
    tab_enderecoentrega: TTabSheet;
    spbuscalogradouroentrega: TSpeedButton;
    lblcepentrega: TLabel;
    spbuscacidadeentrega: TSpeedButton;
    spbenderecoentrega: TSpeedButton;
    lbllogradouroentrega: TLabeledEdit;
    lblenderecoentrega: TLabeledEdit;
    lblentenderno_entrega: TLabeledEdit;
    lblbairro_entrega: TLabeledEdit;
    mskcepentrega: TMaskEdit;
    lblcidadeentrega: TLabeledEdit;
    lblestado_entrega: TLabeledEdit;
    gridenderecoentrega: TDBGrid;
    lblcompl_entrega: TLabeledEdit;
    tabcategorias: TTabSheet;
    spbuscategoria: TSpeedButton;
    spbgravacategoria: TSpeedButton;
    lblcategnome: TLabel;
    lblcategcodestr: TLabeledEdit;
    gridcategorias: TDBGrid;
    tblcontatos: TTabSheet;
    cin3: TPageControl;
    tblcomunicacao: TTabSheet;
    tab_comunicacao: TTabSheet;
    GroupBox5: TGroupBox;
    GroupBox6: TGroupBox;
    lbltipotelefone: TLabel;
    spbaddtelefone: TSpeedButton;
    lblnumerotelefone: TLabeledEdit;
    chkfoneprincipal: TCheckBox;
    gridtelefones: TDBGrid;
    lblddi: TLabeledEdit;
    lblddd: TLabeledEdit;
    lblramal: TLabeledEdit;
    cbotipotelefone: TComboBox;
    GroupBox7: TGroupBox;
    spbaddcontatoweb: TSpeedButton;
    lbltipocontato: TLabel;
    lblemail: TLabeledEdit;
    lblsite: TLabeledEdit;
    lblcomunicador: TLabeledEdit;
    lblendcomunicador: TLabeledEdit;
    cbotipocontato: TComboBox;
    chkwebprincipal: TCheckBox;
    tab_documentos: TTabSheet;
    GroupBox4: TGroupBox;
    GroupBox2: TGroupBox;
    spbdocumentos: TSpeedButton;
    lbltipodocumento: TLabel;
    gridocumentos: TDBGrid;
    lbldocumento: TLabeledEdit;
    cbotipodocumento: TComboBox;
    lblobservacoes: TLabeledEdit;
    cborecebelembrete: TComboBox;
    lblrecebelembrete: TLabel;
    tab_historico: TTabSheet;
    memonovohistorico: TMemo;
    memohistorico: TMemo;
    lblhistorico: TLabel;
    lblnovoregistrohistorico: TLabel;
    spbregistrahistorico: TSpeedButton;
    spbsalvainformacoescompl: TSpeedButton;
    gridwebcontato: TDBGrid;
    PopupMenu1: TPopupMenu;
    popmnugravaconfig: TMenuItem;
    lblgeocontacorrente: TLabeledEdit;
    lblcidcodcob: TLabeledEdit;
    lblcidcodentrega: TLabeledEdit;
    lblvalorcontribuicao: TLabeledEdit;
    tabobservacoes: TTabSheet;
    memobservacoes: TMemo;
    spblimpaobservacoes: TSpeedButton;
    lblemailcontato: TLabeledEdit;
    gridcontato: TDBGrid;
    tblprincipal: TTabSheet;
    spbuscacontato: TSpeedButton;
    lblcepcontato: TLabel;
    spbuscacep: TSpeedButton;
    spbuscacargocontat: TSpeedButton;
    lblcargocontatonome: TLabel;
    lblstatus: TLabel;
    lblcontatoprincipal: TLabel;
    lblentcontatonome: TLabel;
    lblgraudecisao: TLabel;
    spbgravacontato: TSpeedButton;
    lbllogradourocontato: TLabel;
    lbldatainiciovigencia: TLabel;
    lbldtterminovigencia: TLabel;
    lbltipotratamento: TLabel;
    lblcontatolograd: TLabel;
    lblentcontatocod: TLabeledEdit;
    mskcepcontato: TMaskEdit;
    cbologradourocontato: TComboBox;
    lblenderecocontato: TLabeledEdit;
    lblnumerocontato: TLabeledEdit;
    lblbairrocontato: TLabeledEdit;
    lblcomplendercontato: TLabeledEdit;
    lblcargocontato: TLabeledEdit;
    cbocontatoprincipal: TComboBox;
    cbostatuscontato: TComboBox;
    cbograudecisao: TComboBox;
    mskdtiniciovigencia: TMaskEdit;
    mskdtfinalvigencia: TMaskEdit;
    chkgrupooracao: TCheckBox;
    lbllocaldereferencia: TLabeledEdit;
    lblcidadecontato: TLabeledEdit;
    lblufcontato: TLabeledEdit;
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure spbsairClick(Sender: TObject);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure FormActivate(Sender: TObject);
    procedure cboescolaridadeKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbuscatividadeClick(Sender: TObject);
    procedure spbuscategoriaClick(Sender: TObject);
    procedure lblcidcodKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbuscaocupacaoClick(Sender: TObject);
    procedure spbusca_escolaridadeClick(Sender: TObject);
    procedure spbuscaorigemClick(Sender: TObject);
    procedure spbuscaregiaoClick(Sender: TObject);
    procedure spbuscacidadecobClick(Sender: TObject);
    procedure spbuscacidadeentregaClick(Sender: TObject);
    procedure lblcaixapostalEnter(Sender: TObject);
    procedure lblcargocodestrEnter(Sender: TObject);
    procedure lblcargocodestrKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblufEnter(Sender: TObject);
    procedure lblorigcodestrEnter(Sender: TObject);
    procedure tab_comunicacaoEnter(Sender: TObject);
    procedure spbgravacategoriaClick(Sender: TObject);
    procedure tabcategoriasEnter(Sender: TObject);
    procedure spbgravatela1Click(Sender: TObject);
    procedure rdgfilhos_simClick(Sender: TObject);
    procedure rdgfilhosnaoClick(Sender: TObject);
    procedure gridcategoriasKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbaddtelefoneClick(Sender: TObject);
    procedure lblconceitoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblativecodestrKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure tabdadospessoaisEnter(Sender: TObject);
    procedure spbaddcontatowebClick(Sender: TObject);
    procedure gridtelefonesKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure gridwebcontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbdocumentosClick(Sender: TObject);
    procedure gridocumentosKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblramalKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure gridtelefonesDblClick(Sender: TObject);
    procedure gridwebcontatoDblClick(Sender: TObject);
    procedure gridocumentosDblClick(Sender: TObject);
    procedure lblorigcodestrKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblufKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblcaixapostalKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure cbosexoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lbllocaldereferenciaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure cbotipofjKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure cbofalecidoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure mskdtnascimentoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure mskdtcadastroKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure cboestadocivilKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblcategcodestrKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbuscatipotratClick(Sender: TObject);
    procedure lbllogradouroKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbuscalogradouroClick(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure cbotipocontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblemailKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblsiteKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblcomunicadorKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblendcomunicadorKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure cbotipotelefoneKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblddiKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lbldddKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblnumerotelefoneKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbsalvarClick(Sender: TObject);
    procedure tab_documentosEnter(Sender: TObject);
    procedure spbenderecocobrancaClick(Sender: TObject);
    procedure spbenderecoentregaClick(Sender: TObject);
    procedure spbsalvainformacoescomplClick(Sender: TObject);
    procedure lblentnomeKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblentnomefantasiaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblentenderKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblentendernoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblentendercomplKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblentbairKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure mskcepKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbuscacidadeClick(Sender: TObject);
    procedure mskcepEnter(Sender: TObject);
    procedure lblcidcodEnter(Sender: TObject);
    procedure lblentcontatocodKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure mskcepcontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure cbologradourocontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblenderecocontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblnumerocontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblcomplendercontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblbairrocontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblcidadecontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblcargocontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure cbostatuscontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure cbocontatoprincipalKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lbltipotratKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblentnomefantasiaEnter(Sender: TObject);
    procedure spbuscalogradouroentregaClick(Sender: TObject);
    procedure lbllogradouroentregaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblenderecoentregaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblentenderno_entregaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblcompl_entregaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblbairro_entregaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure mskcepentregaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblcidadeentregaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblestado_entregaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbuscalogradourocobrancaClick(Sender: TObject);
    procedure spbuscacontatoClick(Sender: TObject);
    procedure lbllogradourocobrancaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblendereco_cobrancaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblnumerocobrancaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblbairrocobKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblcomplementocobKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure mskcep_cobKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblcidadecobrancaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblestadocobKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure rdgcobrancaClick(Sender: TObject);
    procedure lblnomedopaiEnter(Sender: TObject);
    procedure rdgentregaClick(Sender: TObject);
    procedure cin2Enter(Sender: TObject);
    procedure lblnomedopaiKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblnomedamaeKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblresidecomKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lbldocumentoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure cbotipodocumentoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblobservacoesKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lbltipocobcodKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblbconumKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblagnumKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbbuscatipocobcodClick(Sender: TObject);
    procedure spbbcoClick(Sender: TObject);
    procedure spbagenciaClick(Sender: TObject);
    procedure spbdadosfinanceirosClick(Sender: TObject);
    procedure spbgravacontatoClick(Sender: TObject);
    procedure spbuscacargocontatClick(Sender: TObject);
    procedure mskdtiniciovigenciaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure mskdtfinalvigenciaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lbldiadebitoautomaticoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure cbogeracarneKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lbldioceseidKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure cborecebelembreteKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbuscadioceseClick(Sender: TObject);
    procedure spbuscacepClick(Sender: TObject);
    procedure GroupBox4Enter(Sender: TObject);
    procedure spbregistrahistoricoClick(Sender: TObject);
    procedure spbdadospessoaisClick(Sender: TObject);
    procedure lbltipocobcodChange(Sender: TObject);
    procedure lblbconumEnter(Sender: TObject);
    procedure lblagnumEnter(Sender: TObject);
    procedure cborecebelembreteEnter(Sender: TObject);
    procedure lbllogradouroEnter(Sender: TObject);
    procedure lblregiaoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure popmnugravaconfigClick(Sender: TObject);
    procedure gridtelefonesMouseDown(Sender: TObject; Button: TMouseButton; Shift: TShiftState; X, Y: Integer);
    procedure gridwebcontatoMouseDown(Sender: TObject; Button: TMouseButton; Shift: TShiftState; X, Y: Integer);
    procedure lblgeocontacorrenteKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblgeocontacorrenteEnter(Sender: TObject);
    procedure cbogeracarneEnter(Sender: TObject);
    procedure lblcidcodentregaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblvalorcontribuicaoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spblimpaobservacoesClick(Sender: TObject);
    procedure mskcepcontatoEnter(Sender: TObject);
    procedure spbuscacidcontatoClick(Sender: TObject);
    procedure chkgrupooracaoClick(Sender: TObject);
    procedure FormShow(Sender: TObject);
    procedure GroupBox7Enter(Sender: TObject);
    procedure cbologradourocontatoEnter(Sender: TObject);
    procedure lblufcontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblconceitoEnter(Sender: TObject);
  private
    procedure CarregaDados(JSON: TJSONObject);
    procedure CarregaDadosEndereco(jsonArray: TJSONArray);
    procedure SalvarTelefone;
    procedure CarregarConfiguracaoEmail;
    // Helpers de integração — eliminam repetição do bloco if/then espalhado
    function IsGeoApolo: Boolean;
    function IsAlvo: Boolean;
    procedure BuscarNomeBanco(const ABcoNum: string);
    procedure BuscarViaCep(const ACep: String);
  public
    baseparacampanha, controle, controledocumentos, entcodapolo: string;
    cidcodcob, cidcodentrega, cidcod, controlegrid: string;
    procedure PreencherFormularioComEntidade(Ent: TEntidade);
  end;
var
  frmcadentidade: Tfrmcadentidade;
  flagprincipal, codigograuescolaridade, filhos: string;
  resp: word;
  memo_json: variant;

function grava_entidade(codigo_tela: string): string; export;
function mostra_entidade_categoria(entcod: string; integracao: string): string; export;
function mostra_telefones_entidade(entcod: string; integracao: string): string; export;
function mostra_entidade_contatoweb(entcod: string; integracao: string): string; export;
function mostra_entidade_documentos(entcod: string; integracao: string): string; export;
function carrega_combo_grauescolar: string; export;
function retorna_grauescolaridade(descricao: string): string; export;
function RetornaCidadeOuUF(const ACidCod, AIntegracao, ATipoRetorno: string): string; export;
function retorna_cidade_estado(cidcodlocal: string; integracao: string): string; export;
function retorna_nomecargo(cargocodestr: string): string; export;
function retorna_codigoatividade_economica(ativeconcodestr: string; ativeconnome: string; ativeconcnae: string; ativeconcnaecomp: string): string; export;
function retorna_regiaopais(const codigoregiao: string): string; export;
function retorna_tipologradouro(descricao: string): string; export;
function retorna_tipotratcod(const abreviatura: string): string; export;
function entcod_apolo_busca(flag: string; formulario: TForm): string; export;
function integra_regiao_apolo(regcodestr: string): string; export;
function integra_tipo_tratamento(tipotratcod: string): string; export;
function integra_tipo_logradouro(tipolograd: string): string; export;
function removerAcentuacao(str: string): string;
function mostra_dados_endereco_cobranca: string; export;
function atualiza_log_entidade_apolo(entcod: string): string; export;
function carrega_tipologradouro_contato: string; export;
function NullIfEmpty(const S: string): Variant; export;

implementation

uses funcoes, unt_dados, unt_entidades, unt_principal, unt_viacependereco,
  unt_logon, unt_ViaCEPUtils;

function NullIfEmpty(const S: string): Variant;
begin
  if Trim(S) = '' then
    Result := Null
  else
    Result := S;
end;
{$R *.dfm}
// =============================================================================
//  HELPERS PRIVADOS DE INTEGRAÇÃO
// =============================================================================
function Tfrmcadentidade.IsGeoApolo: Boolean;
begin
  Result := ((frmentidades.integraentidadeapolo = INTEG_NAO_INTEGRA) or
             (frmentidades.integraentidadeapolo = INTEG_MESCLA)) and
             (frmentidades.cbobuscabanco.Text = BANCO_GEOAPOLO);
end;
function Tfrmcadentidade.IsAlvo: Boolean;
begin
  Result := ((frmentidades.integraentidadeapolo = INTEG_INTEGRA) or
             (frmentidades.integraentidadeapolo = INTEG_MESCLA)) and
             (frmentidades.cbobuscabanco.Text = BANCO_ALVO);
end;
// =============================================================================
//  CONFIGURAÇÃO DE EMAIL — lê de arquivo .ini, nunca hardcoded
// =============================================================================
procedure Tfrmcadentidade.CarregarConfiguracaoEmail;
var
  vIni    : TIniFile;
  vArquivo: string;
begin
  vArquivo := ExtractFilePath(Application.ExeName) + 'config.ini';
  // Se não existir, cria com valores padrão
  if not FileExists(vArquivo) then
  begin
    vIni := TIniFile.Create(vArquivo);
    try
      vIni.WriteString ('Email', 'Desenvolvedor',   '');
      vIni.WriteString ('Email', 'Remetente',        '');
      vIni.WriteString ('Email', 'SMTPServer',       '');
      vIni.WriteInteger('Email', 'SMTPPorta',        587);
      vIni.WriteString ('Email', 'SMTPUsuario',      '');
      vIni.WriteString ('Email', 'SMTPSenha',        '');
      vIni.WriteBool   ('Email', 'EnviarEmailErro',  False);
    finally
      vIni.Free;
    end;
    ShowMessage(
      'Arquivo de configuração criado em:' + sLineBreak +
      vArquivo + sLineBreak + sLineBreak +
      'Preencha as configurações de e-mail antes de continuar.');
  end;
  // Lê o arquivo (recém-criado ou já existente)
  vIni := TIniFile.Create(vArquivo);
  try
    EmailDesenvolvedor := vIni.ReadString ('Email', 'Desenvolvedor',  '');
    EmailRemetente     := vIni.ReadString ('Email', 'Remetente',       '');
    SMTPServer         := vIni.ReadString ('Email', 'SMTPServer',      '');
    SMTPPorta          := vIni.ReadInteger('Email', 'SMTPPorta',       587);
    SMTPUsuario        := vIni.ReadString ('Email', 'SMTPUsuario',     '');
    SMTPSenha          := vIni.ReadString ('Email', 'SMTPSenha',       '');
    EnviarEmailErro    := vIni.ReadBool   ('Email', 'EnviarEmailErro', False);
  finally
    vIni.Free;
  end;
end;
procedure Tfrmcadentidade.FormShow(Sender: TObject);
begin
  // Credenciais lidas do arquivo de configuração — nunca no código-fonte
  CarregarConfiguracaoEmail;
end;
// =============================================================================
//  FORM
// =============================================================================
procedure Tfrmcadentidade.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Action := caFree;
end;
procedure Tfrmcadentidade.FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F10 then
    spbsair.Click;
end;

procedure Tfrmcadentidade.FormActivate(Sender: TObject);
var
  vSQL: string;
begin
  StatusBar1.Panels[1].Text := configura_statusbar('a');
  StatusBar1.Panels[3].Text := frmprincipal.nomebancosql;
  StatusBar1.Panels[5].Text := frmprincipal.nomeserversql;
  mskdtcadastro.Text := DateToStr(Date);
  if (controle = 'INCLUSÃO') and ((frmentidades.integraentidadeapolo = INTEG_NAO_INTEGRA) or
     (frmentidades.integraentidadeapolo = INTEG_MESCLA)) then
  begin
    lblentcod.Text := geoapolo_configcod(frmprincipal.codigo_empresa, 'USER_geoapolo_entidade', 'Sim');
    carrega_combo_grauescolar;
  end
  else if (controle = '') and (frmentidades.integraentidadeapolo = INTEG_INTEGRA) then
    controle := 'ALTERAÇÃO';
  with modulo_dados do
  begin
    vSQL := 'SELECT gera_camp_baseapolo, integra_entidades_apolo FROM USER_geoapolo_configuracoes';
    fdquerysql.Close;
    fdquerysql.SQL.Clear;
    fdquerysql.SQL.Text := vSQL;
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
    begin
      if fdquerysql.FieldByName('gera_camp_baseapolo').AsString = 'S' then
        baseparacampanha := 'Apolo'
      else if fdquerysql.FieldByName('gera_camp_baseapolo').AsString = 'N' then
        baseparacampanha := 'GeoApolo';
      frmentidades.integraentidadeapolo := fdquerysql.FieldByName('integra_entidades_apolo').AsString;
      if frmentidades.integraentidadeapolo = INTEG_INTEGRA then
        carrega_combo_grauescolar
      else if frmentidades.integraentidadeapolo = INTEG_NAO_INTEGRA then
        carrega_combo_grauescolar;
      cin1.ActivePageIndex := 0;
      if chkfoneprincipal.Checked then
        flagprincipal := 'Sim'
      else
        flagprincipal := 'Não';
      lblentcod.Refresh;
      lbltipotrat.SetFocus;
      StatusBar1.Panels[3].Text := controle;
    end;
  end;
end;
procedure Tfrmcadentidade.spbsairClick(Sender: TObject);
begin
  Close;
end;
procedure Tfrmcadentidade.spblimparClick(Sender: TObject);
begin
  // implementar limpeza se necessário
end;
// =============================================================================
//  HELPER — busca nome do banco pelo código
// =============================================================================
procedure Tfrmcadentidade.BuscarNomeBanco(const ABcoNum: string);
var
  vSQL: string;
begin
  if Trim(ABcoNum) = '' then
    Exit;
  with modulo_dados do
  begin
    // Usa fdquerysql2 (dedicado) para não conflitar com fdquerysql
    // que pode estar sendo usado por lblbconumEnter (busca tipo cobrança)
    // ou por qualquer outro lookup simultâneo nesta tela.
    if IsGeoApolo then
      vSQL := 'SELECT geobconome AS nome FROM USER_geoapolo_bancos WHERE geobconum = :bconum'
    else if IsAlvo then
      vSQL := 'SELECT bconome AS nome FROM banco WHERE bconum = :bconum'
    else
      Exit;
    fdquerysql2.Close;
    fdquerysql2.SQL.Clear;
    fdquerysql2.SQL.Text := vSQL;
    fdquerysql2.ParamByName('bconum').AsString := Trim(ABcoNum);
    if executaracao(fdquerysql2, fdbanco, true, dtsfdquerysql2) then
    begin
      if not fdquerysql2.IsEmpty then
      begin
        lblnomebanco.Caption := fdquerysql2.FieldByName('nome').AsString;
        lblnomebanco.Refresh;
      end
      else
      begin
        lblnomebanco.Caption := 'Banco não encontrado';
        lblnomebanco.Refresh;
      end;
    end;
  end;
end;
// =============================================================================
//  TELEFONE
// =============================================================================
procedure Tfrmcadentidade.spbaddtelefoneClick(Sender: TObject);
begin
  SalvarTelefone;
end;
procedure Tfrmcadentidade.SalvarTelefone;
var
  vEntFoneSeq: Integer;
  vFlagPrincipal: string;
  vSQL: string;
begin
  with modulo_dados, frmcadentidade do
  begin
    if not validacombo(cbotipotelefone, 'TIPO TELEFONE') then begin cbotipotelefone.SetFocus; Exit; end;
    if not validacampo(lblnumerotelefone, 'NÚMERO TELEFONE') then begin lblnumerotelefone.SetFocus; Exit; end;
    vFlagPrincipal := IfThen(chkfoneprincipal.Checked, 'Sim', 'Não');
    vSQL := '';
    fdbanco.StartTransaction;
    try
      // Obtém próximo SEQ
      fdquerysql.Close;
      fdquerysql.SQL.Text := 'SELECT COALESCE(MAX(entfoneseq), 0) + 1 AS foneseq FROM ent_fone';
      fdquerysql.Open;
      vEntFoneSeq := fdquerysql.FieldByName('foneseq').AsInteger;
      fdquerysql.Close;
      if IsGeoApolo then
      begin
        fdquerysql1.Close;
        fdquerysql1.SQL.Text :=
          'SELECT 1 FROM USER_geoapolo_entidade_comunicacao ' +
          'WHERE geoentcod = :pEntCod AND geotelefonenumero = :pNumero';
        fdquerysql1.ParamByName('pEntCod').AsString := lblentcod.Text;
        fdquerysql1.ParamByName('pNumero').AsString := lblnumerotelefone.Text;
        if executaracao(fdquerysql1, fdbanco, true, dtsfdquerysql1) then
          vSQL := 'UPDATE USER_geoapolo_entidade_comunicacao ' +
                  'SET geotipotelefone = :pTipo, geotelefoneddi = :pDDI, geotelefoneddd = :pDDD, ' +
                  '    geotelefonenumero = :pNumero, geotelefoneramal = :pRamal, flagtelprincipal = :pPrincipal ' +
                  'WHERE geoentcod = :pEntCod AND geotelefonenumero = :pNumero'
        else
          vSQL := 'INSERT INTO USER_geoapolo_entidade_comunicacao ' +
                  '(geoentcod, geotipotelefone, geotelefoneddi, geotelefoneddd, geotelefonenumero, geotelefoneramal, flagtelprincipal) ' +
                  'VALUES (:pEntCod, :pTipo, :pDDI, :pDDD, :pNumero, :pRamal, :pPrincipal)';
      end
      else if IsAlvo then
      begin
        fdquerysql1.Close;
        fdquerysql1.SQL.Text := 'SELECT 1 FROM ent_fone WHERE entcod = :pEntCod AND entfonenum = :pNumero';
        fdquerysql1.ParamByName('pEntCod').AsString := lblentcod.Text;
        fdquerysql1.ParamByName('pNumero').AsString := lblnumerotelefone.Text;
        if executaracao(fdquerysql1, fdbanco, true, dtsfdquerysql1) then
          vSQL := 'UPDATE ent_fone SET entfonetipo = :pTipo, entfoneddi = :pDDI, entfoneddd = :pDDD, ' +
                  'entfoneramalbipnum = :pRamal, entfoneprinc = :pPrincipal, entfonedthrcad = :pData ' +
                  'WHERE entcod = :pEntCod AND entfonenum = :pNumero'
        else
          vSQL := 'INSERT INTO ent_fone (entcod, entfoneseq, entfonetipo, entfoneddi, entfoneddd, entfonenum, entfoneramalbipnum, entfoneprinc, entfonedthrcad) ' +
                  'VALUES (:pEntCod, :pSeq, :pTipo, :pDDI, :pDDD, :pNumero, :pRamal, :pPrincipal, :pData)';
      end;
      if Trim(vSQL) = '' then
      begin
        MessageDlg('Erro: Nenhuma operação definida. Verifique as configurações de integração.', mtError, [mbOK], 0);
        fdbanco.Rollback;
        Exit;
      end;
      if MessageDlg('Confirma este telefone para a entidade?', mtConfirmation, [mbYes, mbNo], 0) = mrYes then
      begin
        fdquerysql3.Close;
        fdquerysql3.SQL.Clear;
        fdquerysql3.SQL.Text := vSQL;
        fdquerysql3.ParamByName('pEntCod').AsString   := lblentcod.Text;
        fdquerysql3.ParamByName('pTipo').AsString     := cbotipotelefone.Text;
        fdquerysql3.ParamByName('pDDI').AsString      := lblddi.Text;
        fdquerysql3.ParamByName('pDDD').AsString      := lblddd.Text;
        fdquerysql3.ParamByName('pNumero').AsString   := lblnumerotelefone.Text;
        fdquerysql3.ParamByName('pRamal').AsString    := lblramal.Text;
        fdquerysql3.ParamByName('pPrincipal').AsString := vFlagPrincipal;
        if fdquerysql3.Params.FindParam('pData') <> nil then
          fdquerysql3.ParamByName('pData').AsDateTime := Now;
        if fdquerysql3.Params.FindParam('pSeq') <> nil then
          fdquerysql3.ParamByName('pSeq').AsInteger := vEntFoneSeq;
        if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
        begin
          fdbanco.Commit;
          cbotipotelefone.ItemIndex := -1;
          chkfoneprincipal.Checked := False;
          lblddd.Clear;
          lblnumerotelefone.Clear;
          lblramal.Clear;
          mostra_telefones_entidade(lblentcod.Text, frmentidades.integraentidadeapolo);
          lblddd.SetFocus;
        end
        else
        begin
          fdbanco.Rollback;
          MessageDlg('Erro ao salvar telefone.', mtError, [mbOK], 0);
        end;
      end
      else
        fdbanco.Rollback;
    except
      on E: Exception do
      begin
        if fdbanco.InTransaction then
          fdbanco.Rollback;
        MessageDlg('Erro ao salvar telefone: ' + E.Message, mtError, [mbOK], 0);
      end;
    end;
  end;
end;
// =============================================================================
//  AGÊNCIA
// =============================================================================
// -----------------------------------------------------------------------------
//  2. spbagenciaClick  (Busca Agência)
//  PROBLEMA ORIGINAL: frm.Free sem desacoplar grid/datasource.
// -----------------------------------------------------------------------------
procedure Tfrmcadentidade.spbagenciaClick(Sender: TObject);
var
  vSQL, vControle: string;
  frm: TFrmConsulta3;
  i: Integer;
begin
  with frmcadentidade, modulo_dados do
  begin
    if lblbconum.Text = '' then
    begin
      MessageDlg('PARA FILTRAR UMA AGÊNCIA PRIMEIRO SELECIONE O BANCO!', mtWarning, [mbOK], 0);
      lblbconum.SetFocus;
      Exit;
    end;
    if IsGeoApolo then
    begin
      vSQL      := 'SELECT gag.geoagnum, gag.geoagnome ' +
                   'FROM USER_geoapolo_agbancaria gag WITH(NOLOCK) ' +
                   'WHERE gag.geobconum = :bconum';
      vControle := 'AGENCIA_BCO_ENTIDADE_GEOAPOLO';
    end
    else if IsAlvo then
    begin
      vSQL      := 'SELECT ag.agnum, ag.agnome FROM AG_BANCARIA ag WITH(NOLOCK) WHERE ag.bconum = :bconum';
      vControle := 'AGENCIA_BCO_ENTIDADE';
    end
    else
      Exit;
    fdquerysql9.Close;
    fdquerysql9.SQL.Clear;
    fdquerysql9.SQL.Text := vSQL;
    fdquerysql9.ParamByName('bconum').AsString := lblbconum.Text;
    if not executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
    begin
      MessageDlg('Nenhuma agência encontrada para este banco!', mtWarning, [mbOK], 0);
      Exit;
    end;
    frm := TFrmConsulta3.Create(Self);
    try
      frm.controle                := vControle;
      dtsfdquerysql9.DataSet      := fdquerysql9;
      frm.gridconsulta.DataSource := dtsfdquerysql9;
      for i := 0 to fdquerysql9.Fields.Count - 1 do
      begin
        frm.cbocampo.Items.Add(fdquerysql9.Fields[i].DisplayName);
        frm.cbordem.Items.Add(fdquerysql9.Fields[i].DisplayName);
      end;
      frm.gridconsulta.Refresh;
      frm.ShowModal;
    finally
      // CORREÇÃO: ordem obrigatória — desacopla antes de liberar
      frm.gridconsulta.DataSource := nil;
      dtsfdquerysql9.DataSet      := nil;
      fdquerysql9.Close;
      frm.Free;
    end;
  end;
end;
// =============================================================================
//  CORREÇÕES — BOTÕES DE BUSCA (Access Violation)
//  Substitua cada rotina correspondente na unit unt_cadentidades.pas
//
//  REGRA GERAL APLICADA EM TODOS OS BOTÕES:
//    No bloco finally, a ordem OBRIGATÓRIA é:
//      1. frm.gridconsulta.DataSource := nil   ← desacopla o grid do datasource
//      2. dtsfdquerysqlX.DataSet      := nil   ← desacopla o datasource do dataset
//      3. fdquerysqlX.Close                    ← fecha o dataset
//      4. frm.Free                             ← libera o form por último
//
//  LEITURA DOS CAMPOS SELECIONADOS:
//    Sempre APÓS o ShowModal retornar, enquanto o dataset ainda está aberto.
//    O TFrmConsulta3 (unt_consultav3.pas) deve fazer APENAS: ModalResult := mrOk
//    nos handlers de seleção (F3, duplo clique). Nunca acesse frmcadentidade
//    diretamente de dentro do form de consulta.
//
//  SHOW vs SHOWMODAL:
//    spbuscacidadeentregaClick usava frm.Show — corrigido para frm.ShowModal.
//    frm.Show retorna imediatamente e o finally libera o form enquanto
//    ele ainda está visível na tela.
// =============================================================================
// -----------------------------------------------------------------------------
//  1. spbbcoClick  (Busca Banco)
//  PROBLEMA ORIGINAL: frm.Free sem desacoplar grid/datasource; leitura de
//  campos dependia de acesso direto pelo form filho.
// -----------------------------------------------------------------------------
procedure Tfrmcadentidade.spbbcoClick(Sender: TObject);
var
  vSQL, vControle: string;
  frm: TFrmConsulta3;
  i: Integer;
begin
  with frmcadentidade, modulo_dados do
  begin
    if IsGeoApolo then
    begin
      vSQL      := 'SELECT bco.geobconum, bco.geobconome FROM USER_geoapolo_bancos bco WITH(NOLOCK)';
      vControle := 'BANCO_ENTIDADE_GEOAPOLO';
    end
    else if IsAlvo then
    begin
      vSQL      := 'SELECT bco.bconum, bco.bconome FROM banco bco WITH(NOLOCK)';
      vControle := 'BANCO_ENTIDADE';
    end
    else
      Exit;
    fdquerysql9.Close;
    fdquerysql9.SQL.Clear;
    fdquerysql9.SQL.Text := vSQL;
    if not executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
    begin
      MessageDlg('Nenhum banco encontrado!', mtWarning, [mbOK], 0);
      Exit;
    end;
    frm := TFrmConsulta3.Create(Self);
    try
      frm.controle                := vControle;
      dtsfdquerysql9.DataSet      := fdquerysql9;
      frm.gridconsulta.DataSource := dtsfdquerysql9;
      for i := 0 to fdquerysql9.Fields.Count - 1 do
      begin
        frm.cbocampo.Items.Add(fdquerysql9.Fields[i].DisplayName);
        frm.cbordem.Items.Add(fdquerysql9.Fields[i].DisplayName);
      end;
      if frm.cbocampo.Items.Count > 0 then frm.cbocampo.ItemIndex := 0;
      if frm.cbordem.Items.Count  > 0 then frm.cbordem.ItemIndex  := 0;
      frm.gridconsulta.Refresh;
      frm.ShowModal;
      // CORREÇÃO: leitura APÓS ShowModal, dataset ainda aberto e válido.
      // O TFrmConsulta3 no handler F3/DblClick deve fazer apenas: ModalResult := mrOk
      if (frm.ModalResult = mrOk) and (not fdquerysql9.IsEmpty) then
      begin
        if IsGeoApolo then
        begin
          lblbconum.Text       := fdquerysql9.FieldByName('geobconum').AsString;
          lblnomebanco.Caption := fdquerysql9.FieldByName('geobconome').AsString;
        end
        else if IsAlvo then
        begin
          lblbconum.Text       := fdquerysql9.FieldByName('bconum').AsString;
          lblnomebanco.Caption := fdquerysql9.FieldByName('bconome').AsString;
        end;
        lblbconum.Refresh;
        lblnomebanco.Refresh;
      end;
    finally
      // CORREÇÃO: ordem obrigatória — desacopla antes de liberar
      frm.gridconsulta.DataSource := nil;
      dtsfdquerysql9.DataSet      := nil;
      fdquerysql9.Close;
      frm.Free;
    end;
  end;
end;
// =============================================================================
//  TIPO COBRANÇA
// =============================================================================
// -----------------------------------------------------------------------------
//  3. spbbuscatipocobcodClick  (Busca Tipo Cobrança)
//  PROBLEMA ORIGINAL: frm.Free sem desacoplar grid/datasource.
// -----------------------------------------------------------------------------
procedure Tfrmcadentidade.spbbuscatipocobcodClick(Sender: TObject);
var
  vSQL, vControle: string;
  frm: TFrmConsulta3;
  i: Integer;
begin
  with modulo_dados, frmcadentidade do
  begin
    if IsGeoApolo then
      begin
        vSQL      := 'SELECT gtc.geotipocobcod, gtc.geotipocobnome FROM USER_geoapolo_tipo_cobranca gtc WITH(NOLOCK)';
        vControle := 'TIPO_COBRANCA_GEOAPOLO';
      end
    else if IsAlvo then
      begin
        vSQL      := 'SELECT tc.tipocobcod, tc.tipocobnome FROM tipo_cobranca tc WITH(NOLOCK) ORDER BY tc.tipocobcod ASC';
        vControle := 'TIPO_COBRANCA_ENTIDADE';
      end
    else
      Exit;
    fdquerysql9.Close;
    fdquerysql9.SQL.Clear;
    fdquerysql9.SQL.Text := vSQL;
    if not executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
      begin
        MessageDlg('Nenhum tipo de cobrança encontrado!', mtWarning, [mbOK], 0);
        Exit;
      end;
    frm := TFrmConsulta3.Create(Self);
    try
      frm.controle                := vControle;
      frm.KeyPreview              := True;
      dtsfdquerysql9.DataSet      := fdquerysql9;
      frm.gridconsulta.DataSource := dtsfdquerysql9;
      for i := 0 to fdquerysql9.Fields.Count - 1 do
        begin
          frm.cbocampo.Items.Add(fdquerysql9.Fields[i].DisplayName);
          frm.cbordem.Items.Add(fdquerysql9.Fields[i].DisplayName);
        end;
      frm.gridconsulta.Refresh;
      frm.lblprocurarpor.Text := '%%';
      frm.ShowModal;
    finally
      // CORREÇÃO: ordem obrigatória — desacopla antes de liberar
      frm.gridconsulta.DataSource := nil;
      dtsfdquerysql9.DataSet      := nil;
      fdquerysql9.Close;
      frm.Free;
    end;
  end;
end;
procedure Tfrmcadentidade.spbdadosfinanceirosClick(Sender: TObject);
begin
  grava_entidade(TELA3);
end;
procedure Tfrmcadentidade.spbdadospessoaisClick(Sender: TObject);
begin
  grava_entidade(TELA2);
end;
// =============================================================================
//  DOCUMENTOS
// =============================================================================
procedure Tfrmcadentidade.spbdocumentosClick(Sender: TObject);
var
  vSQL: string;
begin
  with modulo_dados do
  begin
    if lbldocumento.Text = '' then
    begin
      MessageDlg('O CAMPO NÚMERO DO DOCUMENTO É OBRIGATÓRIO!', mtError, [mbOK], 0);
      lbldocumento.SetFocus;
      Exit;
    end;
    if cbotipodocumento.Text = '' then
    begin
      MessageDlg('O CAMPO TIPO DE DOCUMENTO É OBRIGATÓRIO!', mtError, [mbOK], 0);
      cbotipodocumento.SetFocus;
      Exit;
    end;
    if controledocumentos = 'INCLUSÃO' then
    begin
      fdquerysql12.Close;
      fdquerysql12.SQL.Text :=
        'SELECT 1 FROM USER_geoapolo_entidade_documentos ' +
        'WHERE geoentcod = :entcod AND geotipodocumento = :tipodocumento';
      fdquerysql12.ParamByName('entcod').AsString        := lblentcod.Text;
      fdquerysql12.ParamByName('tipodocumento').AsString := cbotipodocumento.Text;
      if executaracao(fdquerysql12, fdbanco, true, dtsfdquerysql12) then
      begin
        MessageDlg('JÁ EXISTE ESTE TIPO DE DOCUMENTO PARA ESTA ENTIDADE!', mtError, [mbOK], 0);
        mostra_entidade_documentos(lblentcod.Text, frmentidades.integraentidadeapolo);
        lbldocumento.SetFocus;
        Exit;
      end;
    end;
    if MessageDlg('Confirma os dados deste documento?', mtConfirmation, [mbYes, mbNo], 0) <> mrYes then
      Exit;
    fdbanco.StartTransaction;
    try
      if IsGeoApolo then
      begin
        fdquerysql.Close;
        fdquerysql.SQL.Text :=
          'SELECT 1 FROM USER_geoapolo_entidade_documentos ' +
          'WHERE geoentcod = :entcod AND geonumerodocumento = :numerodocumento';
        fdquerysql.ParamByName('entcod').AsString          := lblentcod.Text;
        fdquerysql.ParamByName('numerodocumento').AsString := lbldocumento.Text;
        if not executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
          vSQL := 'INSERT INTO USER_geoapolo_entidade_documentos (geoentcod, geotipodocumento, geonumerodocumento, geoobservacoes) ' +
                  'VALUES (:entcod, :tipodocumento, :numerodocumento, :observacoes)'
        else
          vSQL := 'UPDATE USER_geoapolo_entidade_documentos ' +
                  'SET geonumerodocumento = :numerodocumento, geoobservacoes = :observacoes ' +
                  'WHERE geoentcod = :entcod AND geotipodocumento = :tipodocumento';
        fdquerysql3.Close;
        fdquerysql3.SQL.Clear;
        fdquerysql3.SQL.Text := vSQL;
        fdquerysql3.ParamByName('entcod').AsString          := lblentcod.Text;
        fdquerysql3.ParamByName('tipodocumento').AsString   := cbotipodocumento.Text;
        fdquerysql3.ParamByName('numerodocumento').AsString := lbldocumento.Text;
        fdquerysql3.ParamByName('observacoes').AsString     := lblobservacoes.Text;
        if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
        begin
          fdbanco.Commit;
          lbldocumento.Clear;
          lblobservacoes.Clear;
          cbotipodocumento.ItemIndex := -1;
          cbotipodocumento.SetFocus;
          mostra_entidade_documentos(lblentcod.Text, frmentidades.integraentidadeapolo);
          controledocumentos := 'INCLUSÃO';
          lbldocumento.SetFocus;
        end
        else
        begin
          fdbanco.Rollback;
          MessageDlg('PROBLEMAS AO TENTAR INSERIR REGISTRO DE DOCUMENTO!', mtError, [mbOK], 0);
          lbldocumento.SetFocus;
        end;
      end
      else if IsAlvo then
      begin
        // Atualiza GeoApolo com o documento
        fdquerysql.Close;
        fdquerysql.SQL.Text := 'SELECT 1 FROM USER_geoapolo_entidade_documentos WHERE geoentcod = :entcod AND geotipo';
        fdquerysql.ParamByName('entcod').AsString := lblentcod.Text;
        if not executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
          vSQL := 'INSERT INTO USER_geoapolo_entidade_documentos (geoentcod, geotipodocumento, geonumerodocumento) ' +
                  'VALUES (:entcod, :tipodocumento, :numerodocumento)'
        else
          vSQL := 'UPDATE USER_geoapolo_entidade_documentos ' +
                  'SET geotipodocumento = :tipodocumento, geonumerodocumento = :numerodocumento ' +
                  'WHERE geoentcod = :entcod';
        fdquerysql3.Close;
        fdquerysql3.SQL.Clear;
        fdquerysql3.SQL.Text := vSQL;
        fdquerysql3.ParamByName('entcod').AsString          := lblentcod.Text;
        fdquerysql3.ParamByName('tipodocumento').AsString   := cbotipodocumento.Text;
        fdquerysql3.ParamByName('numerodocumento').AsString := lbldocumento.Text;
        if not executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
        begin
          fdbanco.Rollback;
          MessageDlg('ERRO AO ATUALIZAR DOCUMENTO DA ENTIDADE!', mtError, [mbOK], 0);
          Exit;
        end;
        // Sincroniza com tabela entidade (CPF/CNPJ ou RG)
        if cbotipodocumento.Text = 'CPF/CNPJ' then
        begin
          fdquerysql3.Close;
          fdquerysql3.SQL.Text := 'UPDATE entidade SET entcpfcgc = :numerodocumento, enttipofj = :tipofj WHERE entcod = :entcod';
          fdquerysql3.ParamByName('entcod').AsString          := lblentcod.Text;
          fdquerysql3.ParamByName('tipofj').AsString          := 'Física';
          fdquerysql3.ParamByName('numerodocumento').AsString := lbldocumento.Text;
          executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3);
        end
        else if cbotipodocumento.Text = 'RG/IE' then
        begin
          fdquerysql3.Close;
          fdquerysql3.SQL.Text := 'UPDATE entidade SET entrgie = :numerodocumento, enttipofj = :tipofj WHERE entcod = :entcod';
          fdquerysql3.ParamByName('entcod').AsString          := lblentcod.Text;
          fdquerysql3.ParamByName('tipofj').AsString          := 'Física';
          fdquerysql3.ParamByName('numerodocumento').AsString := lbldocumento.Text;
          executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3);
        end;
        fdbanco.Commit;
        mostra_entidade_documentos(lblentcod.Text, frmentidades.integraentidadeapolo);
        lbldocumento.SetFocus;
      end;
    except
      on E: Exception do
      begin
        if fdbanco.InTransaction then
          fdbanco.Rollback;
        MessageDlg('Erro ao salvar documento: ' + E.Message, mtError, [mbOK], 0);
      end;
    end;
  end;
end;

procedure Tfrmcadentidade.spbgravacategoriaClick(Sender: TObject);
begin
  grava_entidade(TELA7);
end;

procedure Tfrmcadentidade.spbgravacontatoClick(Sender: TObject);
begin
  grava_entidade(TELA6);
end;

procedure Tfrmcadentidade.spbgravatela1Click(Sender: TObject);
begin
  if (lblnomecargo.Caption = '...') and (NullIfEmpty(lblcargocodestr.Text) <> '') then
  begin
    lblnomecargo.Caption := retorna_nomecargo(NullIfEmpty(lblcargocodestr.Text));
    lblnomecargo.Refresh;
  end;
  grava_entidade(TELA1);
end;
// =============================================================================
//  OBSERVAÇÕES
// =============================================================================
procedure Tfrmcadentidade.spblimpaobservacoesClick(Sender: TObject);
begin
  with modulo_dados do
  begin
    if MessageDlg('Confirma que já resolveu as observações aqui relatadas?', mtConfirmation, [mbYes, mbNo], 0) <> mrYes then
    begin
      memobservacoes.SetFocus;
      Exit;
    end;
    fdbanco.StartTransaction;
    try
      fdquerysql3.Close;
      fdquerysql3.SQL.Clear;
      fdquerysql3.SQL.Text := 'UPDATE USER_geoapolo_entidade SET geoobservacoes = :obs WHERE geoentcod = :entcod';
      fdquerysql3.ParamByName('obs').AsString    := memobservacoes.Text;
      fdquerysql3.ParamByName('entcod').AsString := lblentcod.Text;
      if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
      begin
        fdbanco.Commit;
        gravalog(frmlogon.codigousuario, DateToStr(Date), 'RESOLVEU AS PENDÊNCIAS DA ENTIDADE GEOAPOLO: ' + lblentcod.Text);
        MessageDlg('INFORMAÇÕES ATUALIZADAS COM SUCESSO!', mtInformation, [mbOK], 0);
      end
      else
      begin
        fdbanco.Rollback;
        MessageDlg('PROBLEMAS AO TENTAR ATUALIZAR AS OBSERVAÇÕES!', mtError, [mbOK], 0);
        memobservacoes.SetFocus;
      end;
    except
      on E: Exception do
      begin
        if fdbanco.InTransaction then fdbanco.Rollback;
        MessageDlg('Erro: ' + E.Message, mtError, [mbOK], 0);
      end;
    end;
  end;
end;
// =============================================================================
//  HISTÓRICO
// =============================================================================
procedure Tfrmcadentidade.spbregistrahistoricoClick(Sender: TObject);
var
  vHistorico: string;
begin
  with modulo_dados, frmcadentidade do
  begin
    if not IsAlvo then
    begin
      MessageDlg('NO MODO GEOAPOLO NÃO É PERMITIDO GRAVAÇÃO DE HISTÓRICO!', mtError, [mbOK], 0);
      Exit;
    end;
    if memonovohistorico.Text = '' then
    begin
      MessageDlg('NÃO É PERMITIDO SALVAR HISTÓRICO EM BRANCO!', mtError, [mbOK], 0);
      memonovohistorico.SetFocus;
      Exit;
    end;
    if MessageDlg('Confirma este histórico para a entidade?', mtConfirmation, [mbYes, mbNo], 0) <> mrYes then
      Exit;
    fdbanco.StartTransaction;
    try
      vHistorico := memohistorico.Lines.Text;
      vHistorico := QuotedStr(vHistorico + UpperCase(frmlogon.codigousuario) + '-' +
                               DateTimeToStr(Now) + '-' + memonovohistorico.Text) + Chr(13);
      atualiza_log_entidade_apolo(lblentcod.Text);
      fdquerysql3.Close;
      fdquerysql3.SQL.Clear;
      fdquerysql3.SQL.Text := 'UPDATE entidade SET enttextohist = :hist WHERE entcod = :entcod';
      fdquerysql3.ParamByName('hist').AsString   := vHistorico;
      fdquerysql3.ParamByName('entcod').AsString := lblentcod.Text;
      if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
      begin
        fdbanco.Commit;
        fdquerysql.Close;
        fdquerysql.SQL.Text := 'SELECT enttextohist FROM entidade WHERE entcod = :entcod';
        fdquerysql.ParamByName('entcod').AsString := lblentcod.Text;
        if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
          memohistorico.Lines.Add(fdquerysql.FieldByName('enttextohist').AsString);
        memohistorico.Refresh;
        memonovohistorico.Clear;
        memonovohistorico.SetFocus;
      end
      else
      begin
        fdbanco.Rollback;
        MessageDlg('PROBLEMAS AO ATUALIZAR HISTÓRICO DA ENTIDADE!', mtError, [mbOK], 0);
        memonovohistorico.SetFocus;
      end;
    except
      on E: Exception do
      begin
        if fdbanco.InTransaction then fdbanco.Rollback;
        MessageDlg('Erro: ' + E.Message, mtError, [mbOK], 0);
      end;
    end;
  end;
end;
// =============================================================================
//  CATEGORIAS
// =============================================================================
function mostra_entidade_categoria(entcod: string; integracao: string): string;
var
  vSQL: string;
begin
  with modulo_dados, frmcadentidade do
  begin
    fdQuerySQL17.Close;
    fdQuerySQL17.SQL.Clear;
    if frmcadentidade.IsGeoApolo then
      vSQL := 'SELECT ge.geoentcod, gc.geocategcodestr, gc.geocategnome, gec.geoentcod ' +
              'FROM USER_geoapolo_entidade ge WITH (NOLOCK) ' +
              'LEFT JOIN USER_geoapolo_entcateg gec ON ge.geoentcod = gec.geoentcod ' +
              'INNER JOIN USER_geoapolo_categoria gc ON gc.geocategcodestr = gec.geocategcodestr ' +
              'WHERE gec.geoentcod = :entcod'
    else if frmcadentidade.IsAlvo then
      vSQL := 'SELECT e.entcod, ec.categcodestr, cat.categnome, ec.entcod ' +
              'FROM entidade e WITH (NOLOCK) ' +
              'LEFT JOIN ent_categ ec WITH (NOLOCK) ON e.entcod = ec.entcod ' +
              'INNER JOIN categoria cat WITH (NOLOCK) ON ec.categcodestr = cat.categcodestr ' +
              'WHERE ec.entcod = :entcod';
    fdQuerySQL17.SQL.Text := vSQL;
    fdQuerySQL17.ParamByName('entcod').AsString := entcod;
    if executaracao(fdQuerySQL17, fdbanco, False, dtsFdQuerySQL17) then
    begin
      gridCategorias.DataSource := dtsFdQuerySQL17;
      gridCategorias.Refresh;
    end
    else
      MessageDlg('Não foi possível carregar as categorias.', mtError, [mbOK], 0);
  end;
end;
procedure Tfrmcadentidade.gridcategoriasKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
var
  vSQL: string;
begin
  with modulo_dados, frmentidades do
  begin
    if Key <> VK_DELETE then Exit;
    if fdquerysql17.IsEmpty then
    begin
      MessageDlg('Nenhuma categoria selecionada para exclusão!', mtWarning, [mbOK], 0);
      Exit;
    end;
    if MessageDlg('Deseja realmente excluir a categoria?' + sLineBreak + 'Esta ação não poderá ser desfeita!',
                  mtConfirmation, [mbYes, mbNo], 0) <> mrYes then
      Exit;
    fdbanco.StartTransaction;
    try
      if IsGeoApolo then
      begin
        vSQL := 'DELETE FROM USER_geoapolo_entcateg WHERE geoentcod = :pEntCod AND geocategcodestr = :pCategCode';
        fdquerysql3.Close;
        fdquerysql3.SQL.Clear;
        fdquerysql3.SQL.Text := vSQL;
        fdquerysql3.ParamByName('pEntCod').AsString    := fdquerysql17.FieldByName('geoentcod').AsString;
        fdquerysql3.ParamByName('pCategCode').AsString := fdquerysql17.FieldByName('geocategcodestr').AsString;
      end
      else if IsAlvo then
      begin
        vSQL := 'DELETE FROM ent_categ WHERE entcod = :pEntCod AND categcodestr = :pCategCode';
        fdquerysql3.Close;
        fdquerysql3.SQL.Clear;
        fdquerysql3.SQL.Text := vSQL;
        fdquerysql3.ParamByName('pEntCod').AsString    := fdquerysql17.FieldByName('entcod').AsString;
        fdquerysql3.ParamByName('pCategCode').AsString := fdquerysql17.FieldByName('categcodestr').AsString;
      end;
      if executaracao(fdquerysql3, fdbanco, True, dtsfdquerysql3) then
      begin
        fdbanco.Commit;
        MessageDlg('Categoria excluída com sucesso!', mtInformation, [mbOK], 0);
        mostra_entidade_categoria(lblentcod.Text, frmentidades.integraentidadeapolo);
        gridcategorias.Refresh;
        lblcategcodestr.SetFocus;
      end
      else
      begin
        fdbanco.Rollback;
        MessageDlg('Nenhum registro foi excluído!', mtWarning, [mbOK], 0);
      end;
    except
      on E: Exception do
      begin
        if fdbanco.InTransaction then fdbanco.Rollback;
        MessageDlg('Erro ao excluir categoria: ' + E.Message, mtError, [mbOK], 0);
      end;
    end;
  end;
end;
// =============================================================================
//  GRID EVENTOS
// =============================================================================
procedure Tfrmcadentidade.gridocumentosDblClick(Sender: TObject);
begin
  with modulo_dados do
  begin
    lbldocumento.Text := fdquerysql8.FieldByName('documento').AsString;
    buscanacombo(fdquerysql8.FieldByName('tipo').AsString, frmcadentidade, cbotipodocumento);
    lblobservacoes.Text  := fdquerysql8.FieldByName('observacoes').AsString;
    controledocumentos   := 'ALTERAÇÃO';
    lbldocumento.SetFocus;
  end;
end;
procedure Tfrmcadentidade.gridocumentosKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  with modulo_dados do
  begin
    if Key <> VK_DELETE then Exit;
    if MessageDlg('Confirma a remoção deste documento?', mtConfirmation, [mbYes, mbNo], 0) <> mrYes then
    begin
      lbldocumento.SetFocus;
      Exit;
    end;
    fdbanco.StartTransaction;
    try
      fdquerysql3.Close;
      fdquerysql3.SQL.Clear;
      fdquerysql3.SQL.Text :=
        'DELETE FROM USER_geoapolo_entidade_documentos ' +
        'WHERE geoentcod = :entcod AND geotipodocumento = :tipodocumento AND geonumerodocumento = :numerodocumento';
      fdquerysql3.ParamByName('entcod').AsString          := fdquerysql8.FieldByName('geoentcod').AsString;
      fdquerysql3.ParamByName('tipodocumento').AsString   := fdquerysql8.FieldByName('geotipodocumento').AsString;
      fdquerysql3.ParamByName('numerodocumento').AsString := fdquerysql8.FieldByName('geonumerodocumento').AsString;
      if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
      begin
        fdbanco.Commit;
        mostra_entidade_documentos(lblentcod.Text, frmentidades.integraentidadeapolo);
        lbldocumento.SetFocus;
      end
      else
      begin
        fdbanco.Rollback;
        MessageDlg('PROBLEMAS AO TENTAR EXCLUIR ESTE DOCUMENTO!', mtError, [mbOK], 0);
        lbldocumento.SetFocus;
      end;
    except
      on E: Exception do
      begin
        if fdbanco.InTransaction then fdbanco.Rollback;
        MessageDlg('Erro: ' + E.Message, mtError, [mbOK], 0);
      end;
    end;
  end;
end;
procedure Tfrmcadentidade.gridtelefonesDblClick(Sender: TObject);
begin
  MessageDlg('PARA ALTERAR UM TELEFONE, EXCLUA-O E INSIRA NOVAMENTE!', mtWarning, [mbOK], 0);
end;
procedure Tfrmcadentidade.gridtelefonesKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
var
  vSQL: string;
begin
  with modulo_dados do
  begin
    if Key <> VK_DELETE then Exit;
    if MessageDlg('Confirma a remoção deste telefone?', mtConfirmation, [mbYes, mbNo], 0) <> mrYes then
    begin
      lblddd.SetFocus;
      Exit;
    end;
    if IsGeoApolo then
      vSQL := 'DELETE FROM USER_geoapolo_entidade_comunicacao WHERE geoentcod = :entcod AND geotelefonenumero = :numerotelefone'
    else if IsAlvo then
      vSQL := 'DELETE FROM ent_fone WHERE entcod = :entcod AND entfonenum = :numerotelefone';
    fdbanco.StartTransaction;
    try
      fdquerysql3.Close;
      fdquerysql3.SQL.Clear;
      fdquerysql3.SQL.Text := vSQL;
      fdquerysql3.ParamByName('entcod').AsString        := lblentcod.Text;
      fdquerysql3.ParamByName('numerotelefone').AsString := fdquerysql6.FieldByName('geotelefonenumero').AsString;
      if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
      begin
        fdbanco.Commit;
        if IsAlvo then
          atualiza_log_entidade_apolo(lblentcod.Text);
        mostra_telefones_entidade(lblentcod.Text, frmentidades.integraentidadeapolo);
        lblddd.SetFocus;
      end
      else
      begin
        fdbanco.Rollback;
        MessageDlg('ERRO AO EXCLUIR UM TELEFONE!', mtError, [mbOK], 0);
        lblddd.SetFocus;
      end;
    except
      on E: Exception do
      begin
        if fdbanco.InTransaction then fdbanco.Rollback;
        MessageDlg('Erro: ' + E.Message, mtError, [mbOK], 0);
      end;
    end;
  end;
end;
procedure Tfrmcadentidade.gridtelefonesMouseDown(Sender: TObject; Button: TMouseButton; Shift: TShiftState; X, Y: Integer);
begin
  controlegrid := 'TELEFONES';
  popmnugravaconfig.Click;
end;
procedure Tfrmcadentidade.gridwebcontatoDblClick(Sender: TObject);
begin
  with modulo_dados do
  begin
    if IsGeoApolo then
    begin
      buscanacombo(fdquerysql15.FieldByName('tipo_contato').AsString, frmcadentidade, cbotipocontato);
      lblemail.Text        := fdquerysql15.FieldByName('email').AsString;
      lblsite.Text         := fdquerysql15.FieldByName('website').AsString;
      chkwebprincipal.Checked := fdquerysql15.FieldByName('flagemailprincipal').Text = 'Sim';
      lblcomunicador.Text  := fdquerysql15.FieldByName('comunicador_instantaneo').AsString;
      lblendcomunicador.Text := fdquerysql15.FieldByName('endereco_comunicador').AsString;
    end
    else if IsAlvo then
    begin
      buscanacombo(fdquerysql15.FieldByName('entwebtipo').AsString, frmcadentidade, cbotipocontato);
      lblemail.Text := fdquerysql15.FieldByName('entwebemail').AsString;
      chkwebprincipal.Checked := fdquerysql15.FieldByName('entwebemailprinc').AsString = 'Sim';
      chkwebprincipal.Refresh;
      lblsite.Text := fdquerysql15.FieldByName('entwebwww').AsString;
    end;
    cbotipocontato.SetFocus;
  end;
end;
procedure Tfrmcadentidade.gridwebcontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
var
  vSQL: string;
begin
  with modulo_dados do
  begin
    if Key <> VK_DELETE then
    begin
      lblemail.SetFocus;
      Exit;
    end;
    if IsGeoApolo then
    begin
      vSQL := 'DELETE FROM USER_geoapolo_entidade_webcontato WHERE email = :email AND geoentcod = :geoentcod';
      fdquerysql3.Close;
      fdquerysql3.SQL.Clear;
      fdquerysql3.SQL.Text := vSQL;
      fdquerysql3.ParamByName('email').AsString     := fdquerysql15.FieldByName('email').AsString;
      fdquerysql3.ParamByName('geoentcod').AsString := fdquerysql15.FieldByName('geoentcod').AsString;
    end
    else if IsAlvo then
    begin
      vSQL := 'DELETE FROM ent_web WHERE entwebemail = :email AND entcod = :entcod';
      fdquerysql3.Close;
      fdquerysql3.SQL.Clear;
      fdquerysql3.SQL.Text := vSQL;
      fdquerysql3.ParamByName('email').AsString  := fdquerysql15.FieldByName('entwebemail').AsString;
      fdquerysql3.ParamByName('entcod').AsString := fdquerysql15.FieldByName('entcod').AsString;
    end;
    if MessageDlg('Confirma a remoção deste contato web?', mtConfirmation, [mbYes, mbNo], 0) <> mrYes then
    begin
      lblemail.SetFocus;
      Exit;
    end;
    fdbanco.StartTransaction;
    try
      if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
      begin
        fdbanco.Commit;
        mostra_entidade_contatoweb(lblentcod.Text, frmentidades.integraentidadeapolo);
        gridwebcontato.SetFocus;
      end
      else
      begin
        fdbanco.Rollback;
        MessageDlg('ERRO AO EXCLUIR O EMAIL!', mtError, [mbOK], 0);
        lblemail.SetFocus;
      end;
    except
      on E: Exception do
      begin
        if fdbanco.InTransaction then fdbanco.Rollback;
        MessageDlg('Erro: ' + E.Message, mtError, [mbOK], 0);
      end;
    end;
  end;
end;
procedure Tfrmcadentidade.gridwebcontatoMouseDown(Sender: TObject; Button: TMouseButton; Shift: TShiftState; X, Y: Integer);
begin
  controlegrid := 'WEBCONTATO';
  popmnugravaconfig.Click;
end;
procedure Tfrmcadentidade.GroupBox4Enter(Sender: TObject);
begin
  lbldocumento.SetFocus;
end;
procedure Tfrmcadentidade.GroupBox7Enter(Sender: TObject);
begin
  mostra_entidade_contatoweb(lblentcod.Text, frmprincipal.integraentidadesapolo);
  cbotipocontato.SetFocus;
end;
// =============================================================================
//  SALVAR PRINCIPAL
// =============================================================================
procedure Tfrmcadentidade.spbsalvarClick(Sender: TObject);
var
  Ent: TEntidade;
  Service: TEntidadeService;
begin
  Ent     := TEntidade.Create;
  Service := TEntidadeService.Create(modulo_dados.fdbanco);
  try
    Ent.GeoEntCod    := lblentcod.Text;
    Ent.Tipotratcod  := lbltipotrat.Text;
    Ent.Nome         := lblentnome.Text;
    Ent.NomeFantasia := lblentnomefantasia.Text;
    Ent.cep          := mskcep.Text;
    Ent.Logradouro   := lbllogradouro.Text;
    Ent.Endereco     := lblentender.Text;
    Ent.numero       := lblentenderno.Text;
    Ent.Complemento  := lblentendercompl.Text;
    Ent.Bairro       := lblentbair.Text;
    Ent.CidadeCod    := lblcidcod.Text;
    Ent.DataCadastro := StrToDateDef(mskdtcadastro.Text, Now);
    case cin1.ActivePageIndex of
      0: Service.GravarTela1(Ent);
      1: Service.GravarTela2(Ent);
      2: Service.GravarTela3(Ent);
      3: Service.GravarTela4(Ent);
      4: Service.GravarTela5(Ent);
      5: Service.GravarTela6(Ent);
      6: Service.GravarTela7(Ent);
    end;
    ModalResult := mrOk;
    Close;
  except
    on E: Exception do
    begin
      MessageDlg('Erro ao salvar: ' + E.Message, mtError, [mbOK], 0);
      ModalResult := mrNone;
    end;
  end;
  Ent.Free;
  Service.Free;
end;
// =============================================================================
//  ESCOLARIDADE
// =============================================================================
function carrega_combo_grauescolar: string;
var
  vCodigoGrauEscolar: string;
  I: Integer;
  GrausEscolaridade: array[0..10] of string;
begin
  with modulo_dados, frmcadentidade do
  begin
    try
      if cboescolaridade.ItemIndex = -1 then
      begin
        fdquerysql.Close;
        fdquerysql.SQL.Clear;
        fdquerysql.SQL.Text := 'SELECT * FROM USER_geoapolo_grauescolaridade';
        fdquerysql.Open;
        if not fdquerysql.IsEmpty then
        begin
          cboescolaridade.Clear;
          while not fdquerysql.Eof do
          begin
            cboescolaridade.Items.Add(fdquerysql.FieldByName('grau_escolaridade').AsString);
            fdquerysql.Next;
          end;
        end
        else
        begin
          GrausEscolaridade[0]  := 'Superior Incompleto';
          GrausEscolaridade[1]  := 'Superior Completo';
          GrausEscolaridade[2]  := 'Segundo Grau Incompleto';
          GrausEscolaridade[3]  := 'Segundo Grau Completo';
          GrausEscolaridade[4]  := 'Primeiro Grau Incompleto';
          GrausEscolaridade[5]  := 'Primeiro Grau Completo';
          GrausEscolaridade[6]  := 'Pós-Graduado';
          GrausEscolaridade[7]  := 'Mestrado';
          GrausEscolaridade[8]  := 'Doutorado';
          GrausEscolaridade[9]  := 'Analfabeto';
          GrausEscolaridade[10] := 'Nenhum';
          if fdbanco.InTransaction then fdbanco.Rollback;
          fdbanco.StartTransaction;
          try
            for I := Low(GrausEscolaridade) to High(GrausEscolaridade) do
            begin
              vCodigoGrauEscolar := geoapolo_configcod(frmprincipal.codigo_empresa, 'USER_geoapolo_grauescolaridade', 'Sim');
              fdquerysql3.Close;
              fdquerysql3.SQL.Clear;
              fdquerysql3.SQL.Text :=
                'INSERT INTO USER_geoapolo_grauescolaridade (codigo_grauescolaridade, grau_escolaridade) ' +
                'VALUES (:codigo_grauescolaridade, :grau_escolaridade)';
              fdquerysql3.ParamByName('codigo_grauescolaridade').AsString := vCodigoGrauEscolar;
              fdquerysql3.ParamByName('grau_escolaridade').AsString       := GrausEscolaridade[I];
              executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3);
            end;
            fdbanco.Commit;
          except
            fdbanco.Rollback;
            raise;
          end;
          fdquerysql.Close;
          fdquerysql.SQL.Clear;
          fdquerysql.SQL.Text := 'SELECT * FROM USER_geoapolo_grauescolaridade ORDER BY grau_escolaridade';
          if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
          begin
            cboescolaridade.Clear;
            while not fdquerysql.Eof do
            begin
              cboescolaridade.Items.Add(fdquerysql.FieldByName('grau_escolaridade').AsString);
              fdquerysql.Next;
            end;
          end;
        end;
      end;
    except
      on E: Exception do
        raise Exception.Create('Erro ao carregar grau de escolaridade: ' + E.Message);
    end;
  end;
end;

procedure Tfrmcadentidade.CarregaDadosEndereco(jsonArray: TJSONArray);
begin
  // implementar conforme necessidade
end;

// =============================================================================
//  GRAVA ENTIDADE — orquestra as telas
// =============================================================================
function grava_entidade(codigo_tela: string): string;
var
  vSQL2, vSQLLocal, vDataCadastro, vGrauEscolaridade, vDataNiversario, vLogEntSeq, vDataConvertida: string;
  vTipoLogradouro: string;
  vCEP: string;
  vIdadeNumero: Double;
begin
  with frmcadentidade, modulo_dados do
  begin
    if codigo_tela = TELA1 then
    begin
      // --- Validações ---
      if lblentcod.Text = '' then
      begin
        MessageDlg('O CAMPO CÓDIGO DA ENTIDADE É OBRIGATÓRIO!', mtError, [mbOK], 0);
        lblentcod.SetFocus;
        Exit;
      end;
      if lblentcod.Text <> '' then
        begin
          fdquerysql.Close;
          fdquerysql.SQL.Text := 'SELECT geoentcod FROM USER_geoapolo_entidade WHERE geoentcod = :entcod';
          fdquerysql.ParamByName('entcod').AsString := lblentcod.Text;
          if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
            begin
              controle := 'ALTERAÇÃO';
              lblentnome.SetFocus;
            end
          else
             controle:='INCLUSÃO';
        end;
      if not validacampo(lblentnome, 'NOME DA ENTIDADE') then Exit;
      if not validacampo(lblentender, 'ENDEREÇO ENTIDADE') then Exit;
      if not validacampo(lblentenderno, 'NÚMERO DO ENDEREÇO') then Exit;
      if not validacampo(lblentbair, 'BAIRRO DA ENTIDADE') then Exit;
      if not validacampo(mskcep, 'CEP DA ENTIDADE') then Exit;
      if not validacampo(lblcidcod, 'CÓDIGO DA CIDADE') then Exit;
      if not validacampo(lblcargocodestr, 'CARGO DA ENTIDADE') then
      begin
        lblcargocodestr.Text := '04';
        lblcargocodestr.SetFocus;
        Exit;
      end;

      if not validacombo(cboescolaridade, 'CAMPO ESCOLARIDADE É OBRIGATÓRIO') then
      begin
        buscanacombo('Nenhum', frmcadentidade, cboescolaridade);
        Exit;
      end;

      if Trim(mskcep.Text) = '' then
      begin
        if (lbllogradouro.Text <> '') and (lblentender.Text <> '') and (lblentenderno.Text <> '') and
           (lblentbair.Text <> '') and (lblnomecidade.Caption <> '...') and (lbluf.Text <> '') then
        begin
          try
            vCEP := BuscarCEPporEndereco(lbluf.Text, lblnomecidade.Caption, lblentender.Text);
            if vCEP <> '' then
              begin
                mskCEP.Text := vCEP;
                Exit;
              end
            else
              begin
                MessageDlg('Não foi possível localizar um CEP para o endereço informado.', mtError, [mbOK], 0);
                mskCEP.SetFocus;
                Exit;
              end;
          except
            on E: Exception do
            begin
              MessageDlg('Erro ao consultar CEP: ' + E.Message, mtError, [mbOK], 0);
              Exit;
            end;
          end;
        end
        else
          begin
            MessageDlg('O CEP está vazio e não foi possível calcular automaticamente.' + #13 +
                       'Preencha CEP ou os campos: Endereço, Número, Bairro, Cidade e Estado.',
                       mtError, [mbOK], 0);
            mskCEP.SetFocus;
            Exit;
          end;
      end;
      if IsEmptyMask(mskdtcadastro.Text) then
        begin
          MessageDlg('A DATA DE CADASTRO É OBRIGATÓRIA!', mtError, [mbOK], 0);
          mskdtcadastro.Text := FormatDateTime('dd/mm/yyyy', Now);
          mskdtcadastro.SetFocus;
          Exit;
        end;
      try
        vDataCadastro := FormatDateTime('yyyy-mm-dd', StrToDate(mskdtcadastro.Text));
      except
        on E: Exception do
        begin
          MessageDlg(E.Message, mtError, [mbOK], 0);
          mskdtcadastro.SetFocus;
          Exit;
        end;
      end;
      if not IsEmptyMask(mskdtnascimento.Text) then
        begin
          try
            vDataNiversario := FormatDateTime('yyyy-mm-dd', StrToDate(mskdtnascimento.Text));
          except
            on E: Exception do
            begin
              MessageDlg(E.Message, mtError, [mbOK], 0);
              mskdtnascimento.SetFocus;
              Exit;
            end;
          end;
        end
      else
        vDataNiversario := '';
      vGrauEscolaridade := retorna_grauescolaridade(cboescolaridade.Text);
      if MessageDlg('Confirma estas informações?', mtConfirmation, [mbYes, mbNo], 0) <> mrYes then
      begin
        lblentnome.SetFocus;
        Exit;
      end;
      fdbanco.StartTransaction;
      try
        if IsGeoApolo then
        begin
          if controle = 'INCLUSÃO' then
          begin
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text :=
              'INSERT INTO USER_geoapolo_entidade (geoentcod, geotipotratcod, geoentnome, geoentnomefantasia, tipolograd, ' +
              'geoentender, geoenderno, geoentendercomp, geoentbair, geoentdatacad, geoentdesdedata, geoentcep, geocidcod, ' +
              'geoentcxapost, geoentgenero, geolocalreferencia_ender, geotipofj, geofalecido, codigo_grauescolaridade, ' +
              'geocargocodestr, geoentdataanivfund, geoentestcivil, entcod, cidcodapolo) ' +
              'VALUES (:geoentcod, :geotipotratcod, :geoentnome, :geoentnomefantasia, :tipolograd, :geoentender, :geoenderno, ' +
              ':geoentendercomp, :geoentbair, :geoentdatacad, :geoentdesdedata, :geoentcep, :geocidcod, ' +
              ':geoentcxapost, :geoentgenero, :geolocalreferencia_ender, :geotipofj, :geofalecido, :codigo_grauescolaridade, ' +
              ':geocargocodestr, :geoentdataanivfund, :geoentestcivil, :entcod, :cidcodapolo)';
            vTipoLogradouro := retorna_tipologradouro(lbllogradouro.Text);
            fdquerysql3.ParamByName('geoentcod').AsString                := lblentcod.Text;
            fdquerysql3.ParamByName('geotipotratcod').AsString           := retorna_tipotratcod(lbltipotrat.Text);
            fdquerysql3.ParamByName('geoentnome').AsString               := lblentnome.Text;
            fdquerysql3.ParamByName('geoentnomefantasia').AsString       := lblentnomefantasia.Text;
            fdquerysql3.ParamByName('tipolograd').AsString               := retorna_tipologradouro(lbllogradouro.text);
            fdquerysql3.ParamByName('geoentender').AsString             := lblentender.Text;
            fdquerysql3.ParamByName('geoenderno').AsString              := lblentenderno.Text;
            fdquerysql3.ParamByName('geoentendercomp').AsString         := lblentendercompl.Text;
            fdquerysql3.ParamByName('geoentbair').AsString              := lblentbair.Text;
            fdquerysql3.ParamByName('geoentdatacad').AsString           := vDataCadastro;
            fdquerysql3.ParamByName('geoentdesdedata').AsString         := vDataCadastro;
            fdquerysql3.ParamByName('geoentcep').AsString               := mskcep.Text;
            fdquerysql3.ParamByName('geocidcod').AsString               := lblcidcod.Text;
            fdquerysql3.ParamByName('geoentcxapost').AsString           := lblcaixapostal.Text;
            fdquerysql3.ParamByName('geoentgenero').AsString            := Copy(cbosexo.Text, 1, 1);
            fdquerysql3.ParamByName('geolocalreferencia_ender').AsString := lbllocaldereferencia.Text;
            fdquerysql3.ParamByName('geotipofj').AsString               := Copy(cbotipofj.Text, 1, 1);
            fdquerysql3.ParamByName('geofalecido').AsString             := Copy(cbofalecido.Text, 1, 1);
            fdquerysql3.ParamByName('codigo_grauescolaridade').AsString := retorna_grauescolaridade(cboescolaridade.text);
            fdquerysql3.ParamByName('geocargocodestr').Value := NullIfEmpty(NullIfEmpty(lblcargocodestr.Text));
            fdquerysql3.ParamByName('geoentestcivil').Value := NullIfEmpty(NullIfEmpty(cboestadocivil.Text));
            fdquerysql3.ParamByName('entcod').AsString                  := entcodapolo;
            fdquerysql3.ParamByName('cidcodapolo').AsString             := lblcidcod.Text;
            if Trim(StringReplace(mskdtnascimento.Text, '/', '', [rfReplaceAll])) = '' then
              fdquerysql3.ParamByName('geoentdataanivfund').Clear
            else
              fdquerysql3.ParamByName('geoentdataanivfund').AsString := vDataNiversario;
           {
            ShowMessage(
                        'geoentcod='         + lblentcod.Text              + #13 +
                        'geotipotratcod='    + retorna_tipotratcod(lbltipotrat.Text) + #13 +
                        'tipolograd='        + retorna_tipologradouro(lbllogradouro.Text) + #13 +
                        'geoentdatacad='     + vDataCadastro               + #13 +
                        'geocidcod='         + lblcidcod.Text               + #13 +
                        'geoentgenero='      + Copy(cbosexo.Text, 1, 1)     + #13 +
                        'geotipofj='         + Copy(cbotipofj.Text, 1, 1)   + #13 +
                        'geofalecido='       + Copy(cbofalecido.Text, 1, 1) + #13 +
                        'codigo_grauescol='  + retorna_grauescolaridade(cboescolaridade.Text) + #13 +
                        'geocargocodestr='   + lblcargocodestr.Text          + #13 +
                        'geoentestcivil='    + cboestadocivil.Text           + #13 +
                        'entcod='            + entcodapolo                  + #13 +
                        'cidcodapolo='       + lblcidcod.Text
                      );    }

            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
               end;
          end
          else if controle = 'ALTERAÇÃO' then
            begin
              fdquerysql3.Close;
              fdquerysql3.SQL.Clear;
              fdquerysql3.SQL.Text :=
                'UPDATE USER_geoapolo_entidade SET ' +
                'geotipotratcod = :geotipotratcod, geoentnome = :geoentnome, geoentnomefantasia = :geoentnomefantasia, ' +
                'tipolograd = :tipolograd, geoentender = :geoentender, geoenderno = :geoenderno, ' +
                'geoentendercomp = :geoentendercomp, geoentbair = :geoentbair, geoentdatacad = :geoentdatacad, ' +
                'geoentcep = :geoentcep, geocidcod = :geocidcod, cidcodapolo = :cidcodapolo, ' +
                'geoentcxapost = :geoentcxapost, geoentgenero = :geoentgenero, ' +
                'geolocalreferencia_ender = :geolocalreferencia_ender, geofalecido = :geofalecido, ' +
                'codigo_grauescolaridade = :codigo_grauescolaridade, geocargocodestr = :geocargocodestr, ' +
                'geoentdataanivfund = :geoentdataanivfund, geoentestcivil = :geoentestcivil, entcod = :entcod ' +
                'WHERE geoentcod = :geoentcod';
              vTipoLogradouro := retorna_tipologradouro(lbllogradouro.Text);
              if lbltipotrat.Text = '' then fdquerysql3.ParamByName('geotipotratcod').Clear
              else fdquerysql3.ParamByName('geotipotratcod').AsString := lbltipotrat.Text;
              fdquerysql3.ParamByName('geoentnome').AsString               := lblentnome.Text;
              fdquerysql3.ParamByName('geoentnomefantasia').AsString       := lblentnomefantasia.Text;
              if vTipoLogradouro = 'null' then fdquerysql3.ParamByName('tipolograd').text := 'null'
              else fdquerysql3.ParamByName('tipolograd').AsString          := vTipoLogradouro;
              fdquerysql3.ParamByName('geoentender').AsString             := lblentender.Text;
              fdquerysql3.ParamByName('geoenderno').AsString              := lblentenderno.Text;
              fdquerysql3.ParamByName('geoentendercomp').AsString         := lblentendercompl.Text;
              fdquerysql3.ParamByName('geoentbair').AsString              := lblentbair.Text;
              fdquerysql3.ParamByName('geoentdatacad').AsString           := vDataCadastro;
              fdquerysql3.ParamByName('geoentcep').AsString               := mskcep.Text;
              fdquerysql3.ParamByName('geocidcod').AsString               := lblcidcod.Text;
              fdquerysql3.ParamByName('cidcodapolo').AsString             := lblcidcod.Text;
              fdquerysql3.ParamByName('geoentcxapost').AsString           := lblcaixapostal.Text;
              fdquerysql3.ParamByName('geoentgenero').AsString            := Copy(cbosexo.Text, 1, 1);
              fdquerysql3.ParamByName('geolocalreferencia_ender').AsString := lbllocaldereferencia.Text;
              fdquerysql3.ParamByName('geofalecido').AsString             := Copy(cbofalecido.Text, 1, 1);
              if vGrauEscolaridade = '' then fdquerysql3.ParamByName('codigo_grauescolaridade').Clear
              else fdquerysql3.ParamByName('codigo_grauescolaridade').AsString := retorna_grauescolaridade(cboescolaridade.Text);
              if NullIfEmpty(lblcargocodestr.Text) = '' then fdquerysql3.ParamByName('geocargocodestr').Clear
              else fdquerysql3.ParamByName('geocargocodestr').Value := NullIfEmpty(NullIfEmpty(lblcargocodestr.Text));
              if Trim(StringReplace(vDataNiversario, '/', '', [rfReplaceAll])) = '' then
                fdquerysql3.ParamByName('geoentdataanivfund').Clear
              else
                fdquerysql3.ParamByName('geoentdataanivfund').AsString    := vDataNiversario;
              fdquerysql3.ParamByName('geoentestcivil').Value := NullIfEmpty(NullIfEmpty(cboestadocivil.Text));
              fdquerysql3.ParamByName('entcod').AsString                  := entcodapolo;
              fdquerysql3.ParamByName('geoentcod').AsString               := frmentidades.vgeoentcod;
             {  ShowMessage(
              'geotipotratcod=' + retorna_tipotratcod(lbltipotrat.Text) + #13 +
              'tipolograd=' + retorna_tipologradouro(vTipoLogradouro) + #13 +
              'codigo_grauescolaridade=' + retorna_grauescolaridade(cboescolaridade.text) + #13 +
              'geocidcod=' + lblcidcod.Text + #13 +
              'entcod=' + entcodapolo
            );
            ShowMessage(
                        'geoentcod='         + lblentcod.Text              + #13 +
                        'geotipotratcod='    + retorna_tipotratcod(lbltipotrat.Text) + #13 +
                        'tipolograd='        + retorna_tipologradouro(lbllogradouro.Text) + #13 +
                        'geoentdatacad='     + vDataCadastro               + #13 +
                        'geocidcod='         + lblcidcod.Text               + #13 +
                        'geoentgenero='      + Copy(cbosexo.Text, 1, 1)     + #13 +
                        'geotipofj='         + Copy(cbotipofj.Text, 1, 1)   + #13 +
                        'geofalecido='       + Copy(cbofalecido.Text, 1, 1) + #13 +
                        'codigo_grauescol='  + retorna_grauescolaridade(cboescolaridade.Text) + #13 +
                        'geocargocodestr='   + lblcargocodestr.Text          + #13 +
                        'geoentestcivil='    + cboestadocivil.Text           + #13 +
                        'entcod='            + entcodapolo                  + #13 +
                        'cidcodapolo='       + lblcidcod.Text
                      );   }


              if not executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
              begin
                fdbanco.Rollback;
                MessageDlg('ERRO AO ATUALIZAR DADOS!', mtError, [mbOK], 0);
                Exit;
              end;
            end;
        end
        else if IsAlvo then
        begin
          if controle = 'ALTERAÇÃO' then
          begin
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text :=
              'UPDATE entidade SET entnome = :entnome, tipotratcod = :tipotratcod, entnomefant = :entnomefant, ' +
              'entlograd = :entlograd, entender = :entender, entenderno = :entenderno, ' +
              'entendercomp = :entendercomp, entbair = :entbair, entcep = :entcep, cidcod = :cidcod, ' +
              'enttipofj = :enttipofj, entcxapost = :entcxapost, entgenero = :entgenero, ' +
              'cargocodestr = :cargocodestr, entestcivil = :entestcivil, entgrauescol = :entgrauescol, ' +
              'entdataanivfund = :entdataanivfund, entdatacad = :entdatacad ' +
              'WHERE entcod = :entcod';
            fdquerysql3.ParamByName('entnome').AsString    := lblentnome.Text;
            fdquerysql3.ParamByName('tipotratcod').AsString := lbltipotrat.Text;
            fdquerysql3.ParamByName('entnomefant').AsString := lblentnomefantasia.Text;
            fdquerysql3.ParamByName('entlograd').AsString  := lbllogradouro.Text;
            fdquerysql3.ParamByName('entender').AsString   := lblentender.Text;
            fdquerysql3.ParamByName('entenderno').AsString := lblentenderno.Text;
            fdquerysql3.ParamByName('entendercomp').AsString := lblentendercompl.Text;
            fdquerysql3.ParamByName('entbair').AsString    := lblentbair.Text;
            fdquerysql3.ParamByName('entcep').AsString     := mskcep.Text;
            fdquerysql3.ParamByName('cidcod').AsString     := lblcidcod.Text;
            fdquerysql3.ParamByName('enttipofj').AsString  := cbotipofj.Text;
            fdquerysql3.ParamByName('entcxapost').AsString := lblcaixapostal.Text;
            case IndexStr(UpperCase(cbosexo.Text), ['MASCULINO', 'FEMININO', 'NENHUM']) of
              0: fdquerysql3.ParamByName('entgenero').AsString := 'M';
              1: fdquerysql3.ParamByName('entgenero').AsString := 'F';
              2: fdquerysql3.ParamByName('entgenero').AsString := 'N';
            else
              fdquerysql3.ParamByName('entgenero').AsString := cbosexo.Text;
            end;
            if trim(lblcargocodestr.text) = '' then
               fdquerysql3.ParamByName('cargocodestr').Clear
            else
               fdquerysql3.ParamByName('cargocodestr').Value:=trim(lblcargocodestr.text);
            //
            if trim(fdquerysql3.fieldbyname('entestcivil').asstring)='' then
               fdquerysql3.ParamByName('entestcivil').Clear
            else
               fdquerysql3.ParamByName('entestcivil').Value:=Trim(cboestadocivil.Text);
            //
            if cboescolaridade.Text = '' then fdquerysql3.ParamByName('entgrauescol').Clear
            else fdquerysql3.ParamByName('entgrauescol').AsString := cboescolaridade.Text;
            if Trim(StringReplace(mskdtnascimento.Text, '/', '', [rfReplaceAll])) = '' then
              fdquerysql3.ParamByName('entdataanivfund').Clear
            else
              fdquerysql3.ParamByName('entdataanivfund').AsString := vDataNiversario;
            if (vDataCadastro = '  /  /    ') or (vDataCadastro = '  -  -    ') then
              fdquerysql3.ParamByName('entdatacad').Clear
            else
              fdquerysql3.ParamByName('entdatacad').AsString := vDataCadastro;
            fdquerysql3.ParamByName('entcod').AsString := lblentcod.Text;
            if not executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
            begin
              fdbanco.Rollback;
              MessageDlg('ERRO AO ATUALIZAR DADOS!', mtError, [mbOK], 0);
              Exit;
            end;
            // Atualiza falecido
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := 'UPDATE u_entidade SET USERFalecido = :falecido WHERE entcod = :entcod';
            fdquerysql3.ParamByName('falecido').AsString := cbofalecido.Text;
            fdquerysql3.ParamByName('entcod').AsString   := lblentcod.Text;
            executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3);
            atualiza_log_entidade_apolo(lblentcod.Text);
          end;
        end;
        fdbanco.Commit;
        cin1.ActivePageIndex := 1;
        cin1.Refresh;
        cin2.ActivePageIndex := 0;
        cin2.Refresh;
        lblnomedopai.SetFocus;
      except
        on E: Exception do
        begin
          if fdbanco.InTransaction then fdbanco.Rollback;
          ShowMessage('Erro ao executar operação: ' + E.Message);
        end;
      end;
    end
    // -------------------------------------------------------------------------
    else if codigo_tela = TELA2 then
    begin
      fdbanco.StartTransaction;
      try
        if IsGeoApolo then
        begin
          if lblquantosfilhos.Text = '' then lblquantosfilhos.Text := '0';
          fdquerysql3.Close;
          fdquerysql3.SQL.Clear;
          fdquerysql3.SQL.Text :=
            'UPDATE USER_geoapolo_entidade SET geoentnomepai = :nomedopai, geoentnomemae = :nomedamae, ' +
            'geoentpossuifilho = :filhos, geoentmoracom = :moracom, numerofilhos = :quantosfilhos ' +
            'WHERE geoentcod = :geoentcod';
          fdquerysql3.ParamByName('nomedopai').AsString     := lblnomedopai.Text;
          fdquerysql3.ParamByName('nomedamae').AsString     := lblnomedamae.Text;
          fdquerysql3.ParamByName('geoentcod').AsString     := lblentcod.Text;
          fdquerysql3.ParamByName('moracom').AsString       := lblresidecom.Text;
          fdquerysql3.ParamByName('filhos').AsString        := filhos;
          fdquerysql3.ParamByName('quantosfilhos').AsString := lblquantosfilhos.Text;
        end
        else if IsAlvo then
        begin
          fdquerysql3.Close;
          fdquerysql3.SQL.Clear;
          fdquerysql3.SQL.Text :=
            'UPDATE entidade SET entnomepai = :nomedopai, entnomemae = :nomedamae, ' +
            'entmoracom = :moracom, entpossuifilho = :filhos ' +
            'WHERE entcod = :entcod';
          fdquerysql3.ParamByName('nomedopai').AsString := lblnomedopai.Text;
          fdquerysql3.ParamByName('nomedamae').AsString := lblnomedamae.Text;
          fdquerysql3.ParamByName('moracom').AsString   := lblresidecom.Text;
          fdquerysql3.ParamByName('filhos').AsString    := filhos;
          fdquerysql3.ParamByName('entcod').AsString    := lblentcod.Text;
        end;
        if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
        begin
          fdbanco.Commit;
          atualiza_log_entidade_apolo(lblentcod.Text);
          cin2.ActivePageIndex := 1;
          cin2.Refresh;
          lbltipocobcod.SetFocus;
        end
        else
        begin
          fdbanco.Rollback;
          MessageDlg('PROBLEMAS AO ATUALIZAR INFORMAÇÕES!', mtError, [mbOK], 0);
          lblnomedopai.SetFocus;
        end;
      except
        on E: Exception do
        begin
          if fdbanco.InTransaction then fdbanco.Rollback;
          MessageDlg('Erro: ' + E.Message, mtError, [mbOK], 0);
        end;
      end;
    end
    // -------------------------------------------------------------------------
    else if codigo_tela = TELA3 then
    begin
      if not validacampo(lblvalorcontribuicao, 'Valor da Doação') then Exit;
      if not validacampo(lbldioceseid, 'Id Diocese') then Exit;
      if fdbanco.InTransaction then fdbanco.Rollback;
      fdbanco.StartTransaction;
      try
        if IsGeoApolo then
        begin
          if Trim(lblvalorcontribuicao.Text) = '' then lblvalorcontribuicao.Text := '0';
          fdquerysql3.Close;
          fdquerysql3.SQL.Clear;
          fdquerysql3.SQL.Text :=
            'UPDATE USER_geoapolo_entidade SET geotipocobcod = :geotipocobcod, geobconum = :geobconum, ' +
            'geoagnum = :geoagnum, geoconta = :geoconta, geodia_contribuicao = :geodia_contribuicao, ' +
            'geogerarcarne = :geogerarcarne, geodioceseid = :geodioceseid, georecebelembrete = :georecebelembrete, ' +
            'geovalorcontribuicao = :geovalorcontribuicao ' +
            'WHERE geoentcod = :geoentcod';
          fdquerysql3.ParamByName('geotipocobcod').AsString         := lbltipocobcod.Text;
          fdquerysql3.ParamByName('geobconum').AsString             := lblbconum.Text;
          fdquerysql3.ParamByName('geoagnum').AsString              := lblagnum.Text;
          fdquerysql3.ParamByName('geoconta').AsString              := lblgeocontacorrente.Text;
          fdquerysql3.ParamByName('geodia_contribuicao').AsString   := lbldiadebitoautomatico.Text;
          fdquerysql3.ParamByName('geogerarcarne').AsString         := cbogeracarne.Text;
          fdquerysql3.ParamByName('geodioceseid').AsString          := lbldioceseid.Text;
          fdquerysql3.ParamByName('georecebelembrete').AsString     := cborecebelembrete.Text;
          fdquerysql3.ParamByName('geovalorcontribuicao').AsString  := buscatroca(lblvalorcontribuicao.Text, ',', '.');
          fdquerysql3.ParamByName('geoentcod').AsString             := lblentcod.Text;
          if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
          begin
            fdbanco.Commit;
            cin2.ActivePageIndex := 2;
            cin2.Refresh;
            lblativecodestr.SetFocus;
          end
          else
          begin
            fdbanco.Rollback;
            MessageDlg('Nenhum registro foi atualizado!', mtWarning, [mbOK], 0);
          end;
        end
        else if IsAlvo then
        begin
          fdquerysql3.Close;
          fdquerysql3.SQL.Clear;
          fdquerysql3.SQL.Text :=
            'UPDATE entidade SET tipocobcod = :tipocobcod, EntBcoAgCCorNum = :EntBcoAgCCorNum, ' +
            'ENTAGNUMDEPOSITO = :ENTAGNUMDEPOSITO WHERE entcod = :entcod';
          fdquerysql3.ParamByName('tipocobcod').AsString       := lbltipocobcod.Text;
          fdquerysql3.ParamByName('EntBcoAgCCorNum').AsString  := lblbconum.Text;
          fdquerysql3.ParamByName('ENTAGNUMDEPOSITO').AsString := lblagnum.Text;
          fdquerysql3.ParamByName('entcod').AsString           := lblentcod.Text;
          if not executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
          begin
            fdbanco.Rollback;
            MessageDlg('PROBLEMAS AO ATUALIZAR INFORMAÇÕES TELA 3 (entidade)!', mtError, [mbOK], 0);
            Exit;
          end;
          if Trim(lblvalorcontribuicao.Text) = '' then lblvalorcontribuicao.Text := '0';
          fdquerysql.Close;
          fdquerysql.SQL.Clear;
          fdquerysql.SQL.Text := 'SELECT nome FROM USERdioceses_CNBB WHERE id = :id';
          fdquerysql.ParamByName('id').AsString := lbldioceseid.Text;
          executaracao(fdquerysql, fdbanco, true, dtsfdquerysql);
          fdquerysql3.Close;
          fdquerysql3.SQL.Clear;
          fdquerysql3.SQL.Text :=
            'UPDATE u_entidade SET USERDia_Debito_CC = :dia, USERDiocese_id = :dioceseid, ' +
            'USERValor_Contribuicao = :valor, USERNomeDiocese = :nomedioce, ' +
            'USERGeraCarne = :geracarne, USERrecebelembretedoacao = :recebelembrete ' +
            'WHERE entcod = :entcod';
          fdquerysql3.ParamByName('dia').AsString           := lbldiadebitoautomatico.Text;
          fdquerysql3.ParamByName('dioceseid').AsString     := lbldioceseid.Text;
          fdquerysql3.ParamByName('valor').AsString         := buscatroca(lblvalorcontribuicao.Text, ',', '.');
          fdquerysql3.ParamByName('nomedioce').AsString     := IfThen(not fdquerysql.IsEmpty,
                                                                      fdquerysql.FieldByName('nome').AsString,
                                                                      lbldiocesenome.Caption);
          fdquerysql3.ParamByName('geracarne').AsString     := cbogeracarne.Text;
          fdquerysql3.ParamByName('recebelembrete').AsString := cborecebelembrete.Text;
          fdquerysql3.ParamByName('entcod').AsString        := lblentcod.Text;
          if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
          begin
            fdbanco.Commit;
            cin2.ActivePageIndex := 2;
            cin2.Refresh;
            lblativecodestr.SetFocus;
          end
          else
          begin
            fdbanco.Rollback;
            MessageDlg('PROBLEMAS AO ATUALIZAR INFORMAÇÕES TELA 3 (u_entidade)!', mtError, [mbOK], 0);
          end;
        end;
      except
        on E: Exception do
        begin
          if fdbanco.InTransaction then fdbanco.Rollback;
          MessageDlg('Erro ao atualizar informações: ' + E.Message, mtError, [mbOK], 0);
        end;
      end;
    end
    // -------------------------------------------------------------------------
    else if codigo_tela = TELA7 then
    begin
      if not validacampo(lblcategcodestr, 'CÓDIGO CATEGORIA') then
         Exit;
      fdbanco.StartTransaction;
      try
        if IsGeoApolo then
        begin
          fdquerysql1.Close;
          fdquerysql1.SQL.Clear;
          fdquerysql1.SQL.Text :=
            'SELECT 1 FROM USER_geoapolo_entcateg WHERE geoentcod = :geoentcod AND geocategcodestr = :categcodestr';
          fdquerysql1.ParamByName('geoentcod').AsString   := lblentcod.Text;
          fdquerysql1.ParamByName('categcodestr').AsString := lblcategcodestr.Text;
          if not executaracao(fdquerysql1, fdbanco, true, dtsfdquerysql1) then
          begin
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text :=
              'INSERT INTO USER_geoapolo_entcateg (geoentcod, geocategcodestr) VALUES (:entcod, :categcodestr)';
            fdquerysql3.ParamByName('entcod').AsString    := lblentcod.Text;
            fdquerysql3.ParamByName('categcodestr').AsString := lblcategcodestr.Text;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
            begin
              fdbanco.Commit;
              lblcategcodestr.Clear;
              lblcategnome.Caption := '...';
              lblcategcodestr.Refresh;
              lblcategnome.Refresh;
              mostra_entidade_categoria(lblentcod.Text, frmentidades.integraentidadeapolo);
            end
            else
              fdbanco.Rollback;
          end
          else
          begin
            fdbanco.Rollback;
            MessageDlg('ENTIDADE JÁ ASSOCIADA A ESTA CATEGORIA!', mtError, [mbOK], 0);
          end;
        end
        else if IsAlvo then
        begin
          fdquerysql1.Close;
          fdquerysql1.SQL.Clear;
          fdquerysql1.SQL.Text :='SELECT 1 FROM ent_categ WHERE entcod = :entcod AND categcodestr = :categcodestr';
          fdquerysql1.ParamByName('entcod').AsString    := lblentcod.Text;
          fdquerysql1.ParamByName('categcodestr').AsString := lblcategcodestr.Text;
          if not executaracao(fdquerysql1, fdbanco, true, dtsfdquerysql) then
          begin
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := 'INSERT INTO ent_categ (entcod, categcodestr, entcategativatabpv)' +
                                    'VALUES (:entcod, :categcodestr, :ativatabpv)';
            fdquerysql3.ParamByName('entcod').AsString    := lblentcod.Text;
            fdquerysql3.ParamByName('categcodestr').AsString := lblcategcodestr.Text;
            fdquerysql3.ParamByName('ativatabpv').AsString := 'Não';
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
              begin
                fdbanco.Commit;
                lblcategcodestr.Clear;
                lblcategnome.Caption := '...';
                lblcategnome.Refresh;
                mostra_entidade_categoria(lblentcod.Text, frmentidades.integraentidadeapolo);
                gridcategorias.Refresh;
              end
            else
              fdbanco.Rollback;
          end
          else
            begin
              fdbanco.Rollback;
              MessageDlg('ESTA CATEGORIA JÁ ESTÁ ATRIBUÍDA PARA A ENTIDADE!', mtError, [mbOK], 0);
              lblcategcodestr.SetFocus;
            end;
        end;
      except
        on E: Exception do
        begin
          if fdbanco.InTransaction then
             fdbanco.Rollback;
          MessageDlg('Erro: ' + E.Message, mtError, [mbOK], 0);
        end;
      end;
    end;
  end;
end;

// =============================================================================
//  FUNÇÕES AUXILIARES
// =============================================================================
function retorna_regiaopais(const codigoregiao: string): string;
begin
  Result := '...';
  with modulo_dados do
  begin
    fdquerysql.Close;
    fdquerysql.SQL.Text := 'SELECT geo_regnome FROM USER_geoapolo_regiao_pais WHERE georegcodestr = :georegcodestr';
    fdquerysql.ParamByName('georegcodestr').AsString := codigoregiao;
    fdquerysql.Open;
    if not fdquerysql.IsEmpty then
      Result := fdquerysql.FieldByName('geo_regnome').AsString;
  end;
end;
function retorna_grauescolaridade(descricao: string): string;
begin
  Result := 'null';
  if Trim(descricao) = '' then Exit;
  with modulo_dados do
  begin
    fdquerysql.Close;
    fdquerysql.SQL.Clear;
    fdquerysql.SQL.Text :=
      'SELECT codigo_grauescolaridade FROM USER_geoapolo_grauescolaridade WHERE grau_escolaridade = :pDescricao';
    fdquerysql.ParamByName('pDescricao').AsString := descricao;
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
    begin
      if not fdquerysql.IsEmpty then
        Result := fdquerysql.FieldByName('codigo_grauescolaridade').AsString
      else
        Result := 'null';
    end;
  end;
end;

function retorna_tipotratcod(const abreviatura: string): string;
begin
  Result := 'null';

  if Trim(abreviatura) = '' then
    Exit;

  with modulo_dados do
  begin
    fdquerysql.Close;
    fdquerysql.SQL.Clear;
    fdquerysql.SQL.Text :=
      'SELECT tipotratcod ' +
      'FROM user_geoapolo_tipotratamento ' +
      'WHERE abreviatura = :pAbreviatura';

    fdquerysql.ParamByName('pAbreviatura').AsString := abreviatura;

    if executaracao(fdquerysql, fdbanco, True, dtsfdquerysql) then
    begin
      if not fdquerysql.IsEmpty then
        Result := fdquerysql.FieldByName('tipotratcod').AsString
      else
        Result := 'null';
    end;
  end;
end;

function retorna_tipologradouro(descricao: string): string;
begin
  Result := 'NULL';
  if descricao = '' then Exit;
  with modulo_dados do
  begin
    fdquerysql.Close;
    fdquerysql.SQL.Clear;
    fdquerysql.SQL.Text := 'SELECT tipolograd FROM USER_geoapolo_tipologradouro WHERE tipologradabrev = :lbllogradouro';
    fdquerysql.ParamByName('lbllogradouro').AsString := descricao;
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
      Result := fdquerysql.FieldByName('tipolograd').AsString
    else
      Result := 'NULL';
  end;
end;

function retorna_nomecargo(cargocodestr: string): string;
begin
  Result := 'NULL';
  if cargocodestr = '' then
    Exit;
  with modulo_dados do
  begin
    fdquerysql.Close;
    fdquerysql.SQL.Clear;
    fdquerysql.SQL.Text := 'SELECT geocargonome FROM USER_geoapolo_cargos WHERE geocargocodestr = :cargocodestr';
    fdquerysql.ParamByName('cargocodestr').AsString := cargocodestr;
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
      Result := fdquerysql.FieldByName('geocargonome').AsString;
  end;
end;

function retorna_cidade_estado(cidcodlocal: string; integracao: string): string;
var
  vSQL: string;
begin
  with modulo_dados, frmprincipal, frmcadentidade do
  begin
    if (lblcidcod.Text = '') or (lblnomecidade.Caption <> '...') then Exit;
    if (integracao = INTEG_NAO_INTEGRA) or (integracao = INTEG_MESCLA) then
      vSQL := 'SELECT cidnomecomp, ufsigla FROM USER_geoapolo_cidades WHERE geocidcod = :pcidadelocal'
    else
      vSQL := 'SELECT cidnomecomp, ufsigla FROM cidade WHERE cidcod = :pcidadelocal';
    fdquerysql6.Close;
    fdquerysql6.SQL.Clear;
    fdquerysql6.SQL.Text := vSQL;
    fdquerysql6.ParamByName('pcidadelocal').AsString := cidcodlocal;
    if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
    begin
      lblnomecidade.Caption := UpperCase(fdquerysql6.FieldByName('cidnomecomp').AsString);
      lbluf.Text            := UpperCase(fdquerysql6.FieldByName('ufsigla').AsString);
      lblnomecidade.Refresh;
      lbluf.Refresh;
    end;
  end;
end;

function RetornaCidadeOuUF(const ACidCod, AIntegracao, ATipoRetorno: string): string;
var
  vSQL: string;
begin
  Result := '';
  with Modulo_Dados do
  begin
    fdquerysql6.Close;
    fdquerysql6.SQL.Clear;
    if (AIntegracao = INTEG_NAO_INTEGRA) or (AIntegracao = INTEG_MESCLA) then
      vSQL := 'SELECT cidnomecomp, ufsigla FROM USER_geoapolo_cidades WHERE geocidcod = :pCod'
    else if AIntegracao = INTEG_INTEGRA then
      vSQL := 'SELECT cidnomecomp, ufsigla FROM cidade WHERE cidcod = :pCod';
    fdquerysql6.SQL.Text := vSQL;
    fdquerysql6.ParamByName('pCod').AsString := ACidCod;
    if not executaracao(fdquerysql6, FDBanco, True, dtsfdquerysql6) then Exit;
    if fdquerysql6.IsEmpty then Exit;
    if SameText(ATipoRetorno, 'cidade') then
      Result := fdquerysql6.FieldByName('cidnomecomp').AsString
    else if SameText(ATipoRetorno, 'uf') then
      Result := fdquerysql6.FieldByName('ufsigla').AsString
    else
      raise Exception.Create('ATipoRetorno inválido. Use "cidade" ou "uf".');
  end;
end;

// =============================================================================
//  INTEGRAÇÃO REGIÃO — corrigida
// =============================================================================
function integra_regiao_apolo(regcodestr: string): string;
begin
  with modulo_dados, frmcadentidade do
  begin
    // Verifica se a região já existe no GeoApolo
    fdquerysql.Close;
    fdquerysql.SQL.Clear;
    fdquerysql.SQL.Text := 'SELECT georegcodestr FROM USER_geoapolo_regiao_pais WHERE georegcodestr = :regcodestr';
    fdquerysql.ParamByName('regcodestr').AsString := regcodestr;
    if not executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
    begin
      // Não existe — busca o nome na tabela do Apolo
      fdquerysql2.Close;
      fdquerysql2.SQL.Clear;
      fdquerysql2.SQL.Text := 'SELECT regnome FROM regiao WHERE regcodestr = :regcodestr';
      fdquerysql2.ParamByName('regcodestr').AsString := regcodestr;
      if executaracao(fdquerysql2, fdbanco, true, dtsfdquerysql2) then
      begin
        fdquerysql3.Close;
        fdquerysql3.SQL.Clear;
        fdquerysql3.SQL.Text :=
          'INSERT INTO USER_geoapolo_regiao_pais (georegcodestr, geo_regnome) VALUES (:regcodestr, :geo_regnome)';
        fdquerysql3.ParamByName('regcodestr').AsString  := regcodestr;
        fdquerysql3.ParamByName('geo_regnome').AsString := fdquerysql2.FieldByName('regnome').AsString;
        executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3);
      end;
    end;
    // Atualiza a entidade com o código de região
    if regcodestr = '' then Exit;
    fdquerysql3.Close;
    fdquerysql3.SQL.Clear;
    if IsGeoApolo then
    begin
      fdquerysql3.SQL.Text :=
        'UPDATE USER_geoapolo_entidade SET georegcodestr = :regcodestr WHERE geoentcod = :geoentcod';
      fdquerysql3.ParamByName('regcodestr').AsString := lblregiao.Text;
      fdquerysql3.ParamByName('geoentcod').AsString  := lblentcod.Text;
    end
    else if IsAlvo then
    begin
      fdquerysql3.SQL.Text :=
        'UPDATE entidade SET regcodestr = :regcodestr WHERE entcod = :entcod';
      fdquerysql3.ParamByName('regcodestr').AsString := lblregiao.Text;
      fdquerysql3.ParamByName('entcod').AsString     := lblentcod.Text;
    end;
    executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3);
  end;
end;

// =============================================================================
//  TIPO TRATAMENTO
// =============================================================================
function integra_tipo_tratamento(tipotratcod: string): string;
var
  vSQL: string;
begin
  with frmcadentidade, modulo_dados, frmentidades do
  begin
    if tipotratcod = '' then
      vSQL := 'SELECT * FROM tipo_tratamento'
    else
      vSQL := 'SELECT * FROM tipo_tratamento WHERE tipotratcod = :tipotratcod';
    fdquerysql.Close;
    fdquerysql.SQL.Clear;
    fdquerysql.SQL.Text := vSQL;
    if tipotratcod <> '' then
      fdquerysql.ParamByName('tipotratcod').AsString := tipotratcod;
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
    begin
      fdquerysql.First;
      while not fdquerysql.Eof do
      begin
        fdquerysql3.Close;
        fdquerysql3.SQL.Clear;
        fdquerysql3.SQL.Text := 'INSERT INTO USER_geoapolo_tipotratamento (tipotratcod, abreviatura, descricao_tratamento) ' +
          'VALUES (:codigotipo, :tipotratcod, :tipotratnome)';
        fdquerysql3.ParamByName('codigotipo').AsString   := geoapolo_configcod(frmprincipal.codigo_empresa, 'USER_geoapolo_tipotratamento', 'Sim');
        fdquerysql3.ParamByName('tipotratcod').AsString  := fdquerysql.FieldByName('tipotratcod').AsString;
        fdquerysql3.ParamByName('tipotratnome').AsString := fdquerysql.FieldByName('tipotratnome').AsString;
        if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
          fdquerysql.Next;
      end;
    end;
  end;
end;
function integra_tipo_logradouro(tipolograd: string): string;
var
  vSQL: string;
begin
  with frmcadentidade, modulo_dados, frmentidades do
  begin
    if frmentidades.integraentidadeapolo <> INTEG_MESCLA then Exit;
    if tipolograd = '' then
      vSQL := 'SELECT * FROM tipo_lograd'
    else
      vSQL := 'SELECT * FROM tipo_lograd WHERE tipologradabrev = :tipolograd';
    fdquerysql.Close;
    fdquerysql.SQL.Clear;
    fdquerysql.SQL.Text := vSQL;
    if tipolograd <> '' then
      fdquerysql.ParamByName('tipolograd').AsString := tipolograd;
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
    begin
      fdquerysql.First;
      while not fdquerysql.Eof do
      begin
        fdquerysql3.Close;
        fdquerysql3.SQL.Clear;
        fdquerysql3.SQL.Text :=
          'INSERT INTO USER_geoapolo_tipologradouro (tipolograd, tipologradabrev, tipologradouro) ' +
          'VALUES (:codtipologradouro, :tipologradabrev, :tipologradnome)';
        fdquerysql3.ParamByName('codtipologradouro').AsString := geoapolo_configcod(frmprincipal.codigo_empresa, 'USER_geoapolo_tipologradouro', 'Sim');
        fdquerysql3.ParamByName('tipologradabrev').AsString   := fdquerysql.FieldByName('tipologradabrev').AsString;
        fdquerysql3.ParamByName('tipologradnome').AsString    := fdquerysql.FieldByName('tipologradnome').AsString;
        if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
          fdquerysql.Next;
      end;
    end;
  end;
end;
// =============================================================================
//  GRIDS — CARGA DE DADOS
// =============================================================================
function mostra_telefones_entidade(entcod: string; integracao: string): string;
var
  vSQL: string;
begin
  with modulo_dados, frmcadentidade do
  begin
    if frmcadentidade.IsGeoApolo then
      vSQL := 'SELECT gec.geotelefoneddd AS ddd, gec.geotelefonenumero AS numero, gec.flagtelprincipal AS principal, ' +
              'gec.geotipotelefone AS tipotelefone, gec.geotelefoneramal, gec.geotelefoneddi AS ddi ' +
              'FROM USER_geoapolo_entidade_comunicacao gec WHERE gec.geoentcod = :entcod'
    else if frmcadentidade.IsAlvo then
      vSQL := 'SELECT ef.EntFoneDDD AS ddd, ef.EntFoneNum AS numero, ef.EntFonePrinc AS telefoneprincipal, ' +
              'ef.EntFoneRamalBip AS ramal, ef.entfoneddi AS ddi, ef.EntFoneTipo AS tipotelefone ' +
              'FROM ent_fone ef WITH(NOLOCK) WHERE ef.entcod = :entcod';
    fdquerysql6.Close;
    fdquerysql6.SQL.Clear;
    fdquerysql6.SQL.Text := vSQL;
    fdquerysql6.ParamByName('entcod').AsString := entcod;
    if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
    begin
      dtsfdquerysql6.DataSet    := fdquerysql6;
      gridtelefones.DataSource  := dtsfdquerysql6;
      gridtelefones.Refresh;
    end;
  end;
end;
function mostra_entidade_contatoweb(entcod: string; integracao: string): string;
var
  vSQL: string;
begin
  with modulo_dados, frmcadentidade do
  begin
    if frmcadentidade.IsGeoApolo then
    begin
      vSQL := 'SELECT tipo_contato, email, comunicador_instantaneo, endereco_comunicador, ' +
              'flagemailprincipal, website, geoentcod FROM USER_geoapolo_entidade_webcontato ' +
              'WHERE geoentcod = :entcod';
      fdquerysql15.Close;
      fdquerysql15.SQL.Clear;
      fdquerysql15.SQL.Text := vSQL;
      fdquerysql15.ParamByName('entcod').AsString := entcod;
      if executaracao(fdquerysql15, fdbanco, true, dtsfdquerysql15) then
      begin
        gridwebcontato.DataSource := dtsfdquerysql15;
        gridwebcontato.Refresh;
      end;
    end
    else if frmcadentidade.IsAlvo then
    begin
      // Carrega tipos de contato no combo
      fdquerysql15.Close;
      fdquerysql15.SQL.Clear;
      fdquerysql15.SQL.Text := 'SELECT entwebtipo FROM ent_web ew GROUP BY EntWebTipo';
      if executaracao(fdquerysql15, fdbanco, true, dtsfdquerysql15) then
      begin
        cbotipocontato.Items.Clear;
        while not fdquerysql15.Eof do
        begin
          cbotipocontato.Items.Add(fdquerysql15.FieldByName('entwebtipo').AsString);
          fdquerysql15.Next;
        end;
      end;
      // Busca o entcod do Apolo
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := 'SELECT entcod FROM USER_geoapolo_entidade WHERE geoentcod = :entcod';
      fdquerysql.ParamByName('entcod').AsString := entcod;
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
        entcod := fdquerysql.FieldByName('entcod').AsString;
      fdquerysql15.Close;
      fdquerysql15.SQL.Clear;
      fdquerysql15.SQL.Text :=
        'SELECT ew.EntWebEMail AS email, ew.entwebtipo AS tipo_contato, ew.entwebwww AS website, ' +
        'ew.entwebemailprinc AS flagemailprincipal, ew.EntCod ' +
        'FROM ent_web ew WITH(NOLOCK) WHERE ew.entcod = :entcod';
      fdquerysql15.ParamByName('entcod').AsString := entcod;
      if executaracao(fdquerysql15, fdbanco, false, dtsfdquerysql15) then
      begin
        gridwebcontato.DataSource := dtsfdquerysql15;
        gridwebcontato.Refresh;
      end;
    end;
  end;
end;
function mostra_entidade_documentos(entcod: string; integracao: string): string;
var
  vSQL: string;
begin
  with modulo_dados, frmcadentidade do
  begin
    if frmentidades.cbobuscabanco.Text = BANCO_GEOAPOLO then
    begin
      vSQL :=
        'SELECT uged.geonumerodocumento as Documento, uged.geotipodocumento tipo, uged.geoobservacoes as observacoes, uged.geoentcod as entcod, uge.entcod ' +
        'FROM USER_geoapolo_entidade_documentos uged WITH(NOLOCK) ' +
        'LEFT JOIN USER_geoapolo_entidade uge WITH(NOLOCK) ON uged.geoentcod = uge.geoentcod ' +
        'WHERE uge.geoentcod = :entcod';
    end
    else if frmentidades.cbobuscabanco.Text = BANCO_ALVO then
    begin
      vSQL :=
        'SELECT v.Tipo, v.Documento, '''' AS Observacoes, e.EntCod ' +
        'FROM ENTIDADE e ' +
        'CROSS APPLY (VALUES (e.EntCpfCgc, ''CPF/CNPJ''), (e.entrgie, ''RG/IE'')) v(Documento,Tipo) ' +
        'WHERE e.entcod = :entcod';
    end;
    fdquerysql8.Close;
    fdquerysql8.SQL.Clear;
    fdquerysql8.SQL.Text := vSQL;
    fdquerysql8.ParamByName('entcod').AsString := entcod;
    if executaracao(fdquerysql8, fdbanco, true, dtsfdquerysql8) then
    begin
      gridocumentos.DataSource := dtsfdquerysql8;
      gridocumentos.Refresh;
    end;
  end;
end;
function mostra_dados_endereco_cobranca: string;
var
  vSQL: string;
begin
  with modulo_dados, frmcadentidade do
  begin
    vSQL :=
      'SELECT e.geoentcod, e.geoentnome, ugeea.tipo_logradouro, ugeea.endereco, ugeea.bairro, ugeea.geocidcod, ' +
      'ugc.cidnomecomp, ugc.ufsigla ' +
      'FROM USER_geoapolo_entidade e WITH(NOLOCK) ' +
      'LEFT JOIN USER_geoapolo_entidade_endereco_adicionais ugeea WITH(NOLOCK) ON e.geoentcod = ugeea.geoentcod ' +
      'LEFT JOIN USER_geoapolo_cidades ugc WITH(NOLOCK) ON ugeea.geocidcod = ugc.geocidcod';
    fdquerysql18.Close;
    fdquerysql18.SQL.Clear;
    fdquerysql18.SQL.Text := vSQL;
    if executaracao(fdquerysql18, fdbanco, true, dtsfdquerysql18) then
    begin
      dtsfdquerysql18.DataSet   := fdquerysql18;
      gridcobranca.DataSource   := dtsfdquerysql18;
      gridcobranca.Refresh;
    end;
  end;
end;
// =============================================================================
//  LOG
// =============================================================================
function atualiza_log_entidade_apolo(entcod: string): string;
var
  vLogEntSeq: string;
begin
  with modulo_dados, frmcadentidade do
  begin
    fdquerysql12.Close;
    fdquerysql12.SQL.Clear;
    fdquerysql12.SQL.Text := 'SELECT COALESCE(MAX(logentseq), 0) + 1 AS logentsequencia FROM log_entidade';
    if executaracao(fdquerysql12, fdbanco, true, dtsfdquerysql2) then
      vLogEntSeq := fdquerysql12.FieldByName('logentsequencia').AsString
    else
      vLogEntSeq := '1';
    fdquerysql3.Close;
    fdquerysql3.SQL.Clear;
    fdquerysql3.SQL.Text :=
      'INSERT INTO log_entidade (empcod, logentseq, logentcod, logentoper, logentdatahora, usucod) ' +
      'VALUES (:empcod, :logentseq, :entcod, :operacao, :datahora, :usucod)';
    fdquerysql3.ParamByName('empcod').AsString    := frmprincipal.codigo_empresa;
    fdquerysql3.ParamByName('logentseq').AsString := vLogEntSeq;
    fdquerysql3.ParamByName('entcod').AsString    := entcod;
    fdquerysql3.ParamByName('operacao').AsString  := 'Alteração';
    fdquerysql3.ParamByName('datahora').AsDateTime := Now;
    fdquerysql3.ParamByName('usucod').AsString    := UpperCase(frmlogon.codigousuario);
    executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3);
  end;
end;
// =============================================================================
//  TIPO LOGRADOURO CONTATO
// =============================================================================
function carrega_tipologradouro_contato: string;
var
  vSQL: string;
begin
  with frmcadentidade, modulo_dados do
  begin
    cbologradourocontato.Clear;
    vSQL := 'SELECT ugtl.tipologradabrev FROM USER_geoapolo_tipologradouro ugtl ORDER BY ugtl.tipolograd ASC';
    fdquerysql.Close;
    fdquerysql.SQL.Clear;
    fdquerysql.SQL.Text := vSQL;
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
    begin
      fdquerysql.First;
      while not fdquerysql.Eof do
      begin
        cbologradourocontato.Items.Add(fdquerysql.FieldByName('tipologradabrev').AsString);
        fdquerysql.Next;
      end;
    end;
  end;
end;
// =============================================================================
//  ATIVIDADE ECONÔMICA
// =============================================================================
function retorna_codigoatividade_economica(ativeconcodestr: string; ativeconnome: string;
  ativeconcnae: string; ativeconcnaecomp: string): string;
begin
  with modulo_dados, frmcadentidade do
  begin
    fdquerysql.Close;
    fdquerysql.SQL.Clear;
    fdquerysql.SQL.Text := 'SELECT * FROM USER_geoapolo_atividade_economica WHERE ativeconnome = :ativeconnome';
    fdquerysql.ParamByName('ativeconnome').AsString := ativeconnome;
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
    begin
      lblativecodestr.Text          := fdquerysql.FieldByName('ativeconcodestr').AsString;
      lblnomeatividade_economica.Caption := fdquerysql.FieldByName('ativeconnome').AsString;
      lblativecodestr.Refresh;
      lblnomeatividade_economica.Refresh;
    end
    else
    begin
      fdquerysql3.Close;
      fdquerysql3.SQL.Clear;
      fdquerysql3.SQL.Text :=
        'INSERT INTO USER_geoapolo_atividade_economica (ativeconcodestr, ativeconnome, ativeconcnae, ativeconcnaecomp) ' +
        'VALUES (:ativeconcodestr, :ativeconnome, :ativeconcnae, :ativeconcnaecomp)';
      fdquerysql3.ParamByName('ativeconcodestr').AsString  := ativeconcodestr;
      fdquerysql3.ParamByName('ativeconnome').AsString     := ativeconnome;
      fdquerysql3.ParamByName('ativeconcnae').AsString     := ativeconcnae;
      fdquerysql3.ParamByName('ativeconcnaecomp').AsString := ativeconcnaecomp;
      if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
      begin
        lblativecodestr.Text               := ativeconcodestr;
        lblnomeatividade_economica.Caption := ativeconnome;
        lblnomeatividade_economica.Refresh;
        lblativecodestr.Refresh;
      end;
    end;
  end;
end;
// =============================================================================
//  ENTCOD APOLO
// =============================================================================
function entcod_apolo_busca(flag: string; formulario: TForm): string;
begin
  with modulo_dados, formulario do
  begin
    fdquerysql.Close;
    fdquerysql.SQL.Clear;
    fdquerysql.SQL.Text :=
      'SELECT ConfCodProxNum + 1 AS proximo FROM CONFIG_COD ' +
      'WHERE ConfCodTabela = :tabela AND empcod = :empcod';
    fdquerysql.ParamByName('tabela').AsString  := 'ENTIDADE';
    fdquerysql.ParamByName('empcod').AsString  := frmprincipal.codigo_empresa;
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
    begin
      fdquerysql3.Close;
      fdquerysql3.SQL.Clear;
      fdquerysql3.SQL.Text :=
        'UPDATE config_cod SET confcodproxnum = :proximo WHERE confcodtabela = :tabela AND empcod = :empcod';
      fdquerysql3.ParamByName('proximo').AsString := fdquerysql.FieldByName('proximo').AsString;
      fdquerysql3.ParamByName('tabela').AsString  := 'ENTIDADE';
      fdquerysql3.ParamByName('empcod').AsString  := frmprincipal.codigo_empresa;
      executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3);
      Result := fdquerysql.FieldByName('proximo').AsString;
    end;
  end;
end;

// =============================================================================
//  POPUP MENU
// =============================================================================
procedure Tfrmcadentidade.popmnugravaconfigClick(Sender: TObject);
begin
  if controlegrid = 'TELEFONE' then
    grava_configuracoes_grids(frmentidades, 'GEOGRIDTELEFONES', gridtelefones, 'gridtelefones', frmlogon.nomeusuario, modulo_dados.dtsfdquerysql6)
  else if controlegrid = 'WEBCONTATO' then
    grava_configuracoes_grids(frmentidades, 'GEOGRIDWEBCONTATO', gridwebcontato, 'gridwebcontato', frmlogon.nomeusuario, modulo_dados.dtsfdquerysql5);
end;

// =============================================================================
//  AUXILIARES DIVERSAS
// =============================================================================
function removerAcentuacao(str: string): string;
var
  x: Integer;
const
  ComAcento = 'àâêôûãõáéíóúçüÀÂÊÔÛÃÕÁÉÍÓÚÇÜ';
  SemAcento = 'aaeouaoaeioucuAAEOUAOAEIOUCU';
begin
  for x := 1 to Length(str) do
    if Pos(str[x], ComAcento) <> 0 then
      str[x] := SemAcento[Pos(str[x], ComAcento)];
  Result := str;
end;
procedure Tfrmcadentidade.CarregaDados(JSON: TJSONObject);
begin
  // implementar conforme necessidade
end;
procedure Tfrmcadentidade.PreencherFormularioComEntidade(Ent: TEntidade);
begin
  lblentcod.Text          := Ent.GeoEntCod;
  lblentnome.Text         := Ent.Nome;
  lblentnomefantasia.Text := Ent.NomeFantasia;
  lbllogradouro.Text      := Ent.Logradouro;
  lblentender.Text        := Ent.Endereco;
  lblentenderno.Text      := Ent.Numero;
  lblentbair.Text         := Ent.Bairro;
  lblentendercompl.Text   := Ent.Complemento;
  lblcidcod.Text          := Ent.CidadeCod;
  lblNomeCidade.Caption   := Ent.NomeCidade;
  lbluf.Text              := Ent.Estado;
  lblcaixapostal.Text     := Ent.CaixaPostal;
  mskdtcadastro.Text      := DateToStr(Ent.DataCadastro);
  mskdtnascimento.Text    := DateToStr(Ent.DataAniversario);
end;
// =============================================================================
//  EVENTOS DE TECLADO E FOCO — mantidos do original
// =============================================================================
procedure Tfrmcadentidade.cboestadocivilKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if ((Key = VK_RETURN) or (Key = VK_TAB)) then
     mskdtnascimento.SetFocus;
end;
procedure Tfrmcadentidade.cbofalecidoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if ((Key = VK_RETURN) or (Key = VK_TAB)) then
     lbllocaldereferencia.SetFocus;
end;
procedure Tfrmcadentidade.cbogeracarneEnter(Sender: TObject);
begin
   if isAlvo then
      begin
        if (lbltipocobcod.Text = '0000020') or (lbltipocobcod.Text = '0000012') then
          begin
            cbogeracarne.Text := 'Sim';
            cbogeracarne.Refresh;
          end;
      end
   else
      begin
        cbogeracarne.Text := 'Sim';
        cbogeracarne.Refresh;
      end;
  if lblvalorcontribuicao.Text = '' then
    lblvalorcontribuicao.Text := '25';
end;
procedure Tfrmcadentidade.cbogeracarneKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if ((Key = VK_RETURN) or (Key = VK_TAB)) then
     lbldioceseid.SetFocus;
end;
procedure Tfrmcadentidade.cbologradourocontatoEnter(Sender: TObject);
var
  Info: TViaCEPInfo;
begin
  if (mskcepcontato.Text <> '') and (lblenderecocontato.Text = '') then
  begin
    Info := BuscarCEP(mskcepcontato.Text);
    lblenderecocontato.Text  := UpperCase(Info.Logradouro);
    lblcomplendercontato.Text := UpperCase(Info.Complemento);
    lblbairrocontato.Text    := UpperCase(Info.Bairro);
    lblcidadecontato.Text    := UpperCase(Info.Cidade);
    lblufcontato.Text        := UpperCase(Info.Estado);
  end;
end;

procedure Tfrmcadentidade.cbologradourocontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then lblenderecocontato.SetFocus;
end;
procedure Tfrmcadentidade.cborecebelembreteEnter(Sender: TObject);
begin
  with modulo_dados do
  begin
    if (lbldioceseid.Text <> '') and ((lbldiocesenome.Caption = 'Nome Diocese') or (lbldiocesenome.Caption = '')) then
    begin
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := 'SELECT nome FROM USERdioceses_CNBB WITH(NOLOCK) WHERE id = :dioceseid';
      fdquerysql.ParamByName('dioceseid').AsString := lbldioceseid.Text;
      if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
      begin
        lbldiocesenome.Caption := fdquerysql.FieldByName('nome').AsString;
        lbldiocesenome.Refresh;
      end;
    end;
  end;
end;
procedure Tfrmcadentidade.cborecebelembreteKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then spbdadosfinanceiros.Click;
end;
procedure Tfrmcadentidade.cbosexoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then
    if (cin1.ActivePageIndex = 0) and IsAlvo then
      cbofalecido.SetFocus;
end;
procedure Tfrmcadentidade.cbostatuscontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then cbocontatoprincipal.SetFocus;
end;
procedure Tfrmcadentidade.cbotipocontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then lblemail.SetFocus;
end;
procedure Tfrmcadentidade.cbotipodocumentoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then lblobservacoes.SetFocus;
end;
procedure Tfrmcadentidade.cbotipofjKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if ((Key = VK_RETURN) or (Key = VK_TAB)) then
     cboestadocivil.SetFocus;
end;
procedure Tfrmcadentidade.cbotipotelefoneKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then lblddi.SetFocus;
end;
procedure Tfrmcadentidade.chkgrupooracaoClick(Sender: TObject);
var
  vNomeDoGrupo, vLocalDeReuniao: string;
begin
  if chkgrupooracao.Checked then
  begin
    vNomeDoGrupo   := InputBox('Pesquisa por Grupo de Oração', 'Informe o nome do grupo', '');
    vLocalDeReuniao := InputBox('Pesquisa por Grupo de Oração', 'Informe o Local de Reunião', '');
  end;
end;
procedure Tfrmcadentidade.cin2Enter(Sender: TObject);
begin
  cin2.ActivePageIndex := 0;
  cin2.Refresh;
end;
procedure Tfrmcadentidade.rdgcobrancaClick(Sender: TObject);
begin
  if rdgcobranca.ItemIndex = 1 then cin2.ActivePageIndex := 2;
end;
procedure Tfrmcadentidade.rdgentregaClick(Sender: TObject);
begin
  if rdgentrega.ItemIndex = 1 then cin2.ActivePageIndex := 3;
end;
procedure Tfrmcadentidade.rdgfilhosnaoClick(Sender: TObject);
begin
  if rdgfilhosnao.Checked then filhos := 'Não';
end;
procedure Tfrmcadentidade.rdgfilhos_simClick(Sender: TObject);
begin
  if rdgfilhos_sim.Checked then
  begin
    filhos := 'Sim';
    lblquantosfilhos.Visible := True;
    lblquantosfilhos.SetFocus;
  end;
end;
procedure Tfrmcadentidade.lblcargocodestrKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then spbuscaocupacao.Click;
  if (Key = VK_RETURN) or (Key = VK_TAB) then spbgravatela1.Click;
end;
procedure Tfrmcadentidade.lblcargocontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then mskdtiniciovigencia.SetFocus;
  if Key = VK_F4 then spbuscacargocontat.Click;
end;
procedure Tfrmcadentidade.lblcategcodestrKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then spbuscategoria.Click;
  if (Key = VK_RETURN) or (Key = VK_TAB) then spbgravacategoria.Click;
end;
procedure Tfrmcadentidade.lblcaixapostalEnter(Sender: TObject);
begin
  if (lbluf.Text <> '') and (not checaestado(lbluf.Text)) then
  begin
    MessageDlg('UNIDADE DA FEDERAÇÃO INVÁLIDA!', mtError, [mbOK], 0);
    lbluf.SetFocus;
  end;
end;
procedure Tfrmcadentidade.lblcaixapostalKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then cbosexo.SetFocus;
end;
procedure Tfrmcadentidade.lblcargocodestrEnter(Sender: TObject);
begin
  if cboescolaridade.Text <> '' then
    codigograuescolaridade := retorna_grauescolaridade(cboescolaridade.Text);
end;
procedure Tfrmcadentidade.lblcidadecobrancaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then spbuscacidadecob.Click;
  if (Key = VK_TAB) or (Key = VK_RETURN) then lblestadocob.SetFocus;
end;
procedure Tfrmcadentidade.lblcidadecontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then lblufcontato.SetFocus;
end;
procedure Tfrmcadentidade.lblcidadeentregaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then spbuscacidadeentrega.Click;
  if (Key = VK_RETURN) or (Key = VK_TAB) then lblestado_entrega.SetFocus;
end;
procedure Tfrmcadentidade.lblcidcodEnter(Sender: TObject);
begin
  // reservado para implementação futura
end;
procedure Tfrmcadentidade.lblcidcodentregaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then lblcidadeentrega.SetFocus;
end;
procedure Tfrmcadentidade.lblcidcodKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then spbuscacidade.Click;
  if (Key = VK_TAB) or (Key = VK_RETURN) then lbluf.SetFocus;
end;
procedure Tfrmcadentidade.lblcomplementocobKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then mskcep_cob.SetFocus;
end;
procedure Tfrmcadentidade.lblcomplendercontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then lblbairrocontato.SetFocus;
end;
procedure Tfrmcadentidade.lblcompl_entregaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then mskcepentrega.SetFocus;
end;
procedure Tfrmcadentidade.lblcomunicadorKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then lblendcomunicador.SetFocus;
end;
procedure Tfrmcadentidade.lblconceitoEnter(Sender: TObject);
begin
  if lblregiao.Text = '' then
  begin
    MessageDlg('INFORME A REGIÃO DA ENTIDADE!', mtWarning, [mbOK], 0);
    lblregiao.SetFocus;
  end;
end;
procedure Tfrmcadentidade.lblconceitoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then spbsalvainformacoescompl.Click;
end;
procedure Tfrmcadentidade.lbldddKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then lblnumerotelefone.SetFocus;
end;
procedure Tfrmcadentidade.lblddiKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then lblddd.SetFocus;
end;
procedure Tfrmcadentidade.lbldiadebitoautomaticoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then lblvalorcontribuicao.SetFocus;
end;
procedure Tfrmcadentidade.lbldioceseidKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then cborecebelembrete.SetFocus;
  if Key = VK_F4 then spbuscadiocese.Click;
end;
procedure Tfrmcadentidade.lbldocumentoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then cbotipodocumento.SetFocus;
end;
procedure Tfrmcadentidade.lblemailKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then lblsite.SetFocus;
end;
procedure Tfrmcadentidade.lblendcomunicadorKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then spbaddcontatoweb.Click;
end;
procedure Tfrmcadentidade.lblenderecocontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then lblnumerocontato.SetFocus;
end;
procedure Tfrmcadentidade.lblenderecoentregaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then lblentenderno_entrega.SetFocus;
end;
procedure Tfrmcadentidade.lblendereco_cobrancaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then lblnumerocobranca.SetFocus;
end;
procedure Tfrmcadentidade.lblentbairKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then lblcidcod.SetFocus;
end;
procedure Tfrmcadentidade.lblentcontatocodKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then mskcepcontato.SetFocus;
  if Key = VK_F4 then spbuscacontato.Click;
end;
procedure Tfrmcadentidade.lblentendercomplKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then lblentbair.SetFocus;
end;
procedure Tfrmcadentidade.lblentenderKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then lblentenderno.SetFocus;
end;
procedure Tfrmcadentidade.lblentendernoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then lblentendercompl.SetFocus;
end;
procedure Tfrmcadentidade.lblentenderno_entregaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then lblbairro_entrega.SetFocus;
end;
procedure Tfrmcadentidade.lblentnomefantasiaEnter(Sender: TObject);
begin
  if lblentnome.Text = '' then
  begin
    MessageDlg('NOME DA ENTIDADE É CAMPO OBRIGATÓRIO!', mtWarning, [mbOK], 0);
    lblentnome.SetFocus;
  end;
end;
procedure Tfrmcadentidade.lblentnomefantasiaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then mskcep.SetFocus;
end;
procedure Tfrmcadentidade.lblentnomeKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if ((Key = VK_TAB) or (Key = VK_RETURN)) then
     lblentnomefantasia.SetFocus;
end;

procedure Tfrmcadentidade.lblestadocobKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if ((Key = VK_TAB) or (Key = VK_RETURN)) then
     spbenderecocobranca.Click;
end;

procedure Tfrmcadentidade.lblestado_entregaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if ((Key = VK_RETURN) or (Key = VK_TAB)) then
     spbenderecoentrega.Click;
end;

procedure Tfrmcadentidade.lblgeocontacorrenteEnter(Sender: TObject);
var
  vSQL: string;
begin
  with modulo_dados do
  begin
    if (lblagnum.Text = '') or (lblnomeagencia.Caption <> '...') then
        Exit;
    if IsGeoApolo then
      vSQL := 'SELECT geoagnome AS nome FROM USER_geoapolo_agbancaria WHERE GEOagnum = :agnum AND geobconum = :bconum'
    else if IsAlvo then
      vSQL := 'SELECT agnome AS nome FROM ag_bancaria WHERE agnum = :agnum AND bconum = :bconum';
    fdquerysql.Close;
    fdquerysql.SQL.Clear;
    fdquerysql.SQL.Text := vSQL;
    fdquerysql.ParamByName('agnum').AsString  := lblagnum.Text;
    fdquerysql.ParamByName('bconum').AsString := lblbconum.Text;
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
      begin
        lblnomeagencia.Caption := fdquerysql.FieldByName('nome').AsString;
        lblnomeagencia.Refresh;
      end;
  end;
end;
procedure Tfrmcadentidade.lblgeocontacorrenteKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then lbldiadebitoautomatico.SetFocus;
end;
procedure Tfrmcadentidade.lbllocaldereferenciaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then cbotipofj.SetFocus;
end;
procedure Tfrmcadentidade.lbllogradourocobrancaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then spbuscalogradourocobranca.Click;
  if (Key = VK_TAB) or (Key = VK_RETURN) then lblendereco_cobranca.SetFocus;
end;

procedure Tfrmcadentidade.lbllogradouroEnter(Sender: TObject);
var
  vSQL: string;
begin
  if mskcep.Text = '' then
     Exit;
  with modulo_dados do
  begin
    if IsGeoApolo then
    begin
      vSQL :=
        'SELECT ugca.tipologradabreviado, ugca.cependerloc, ugca.cepbair1, ugc.cidnomecomp, ugc.ufsigla, ' +
        'ugca.cepcidcodcorreio, ugca.ceptaborigem ' +
        'FROM USER_geoapolo_cepapolo ugca WITH(NOLOCK) ' +
        'INNER JOIN USER_geoapolo_cidades ugc WITH(NOLOCK) ON ugca.cepcidcodcorreio = ugc.geocidcod ' +
        'WHERE ugca.cepcod = :cep';
      fdquerysql18.Close;
      fdquerysql18.SQL.Clear;
      fdquerysql18.SQL.Text := vSQL;
      fdquerysql18.ParamByName('cep').AsString := mskcep.Text;
      if executaracao(fdquerysql18, fdbanco, true, dtsfdquerysql18) then
        begin
          if fdquerysql18.FieldByName('ceptaborigem').AsString = 'CEP_ESP' then
            begin
              lbllogradouro.Text    := fdquerysql18.FieldByName('tipologradabreviado').AsString;
              lblentender.Text      := fdquerysql18.FieldByName('cependerloc').AsString;
              lblentbair.Text       := fdquerysql18.FieldByName('cepbair1').AsString;
              lblcidcod.Text        := fdquerysql18.FieldByName('cepcidcodcorreio').AsString;
              lblnomecidade.Caption := fdquerysql18.FieldByName('cidnomecomp').AsString;
              lbluf.Text            := fdquerysql18.FieldByName('ufsigla').AsString;
            end;
          lbllogradouro.SetFocus;
        end
      else
         begin
           {SE NÃO ENCONTRAR O CEP, VAI BUSCAR ELE NO VIA CEP}
             if ((Trim(mskcep.Text) <> '') and (lblnomecidade.Caption = '...')) then
              begin
                BuscarViaCep(mskcep.Text);
              end;
              Exit;
         end;
    end;
  end;
end;

procedure Tfrmcadentidade.BuscarViaCep(const ACep: String);
var
  Http: TNetHTTPClient;
  Resp: IHTTPResponse;
  Json: TJSONObject;
  Logradouro, Bairro, Cidade, UF, CodCidade : String;
  SQL : String;
begin
  Http := TNetHTTPClient.Create(nil);
  try
    Resp := Http.Get(Format('https://viacep.com.br/ws/%s/json/',  [StringReplace(ACep,'-','',[rfReplaceAll])]) );

    if Resp.StatusCode <> 200 then
      Exit;

    Json := TJSONObject.ParseJSONValue(Resp.ContentAsString) as TJSONObject;
    try
      if Json.GetValue('erro') <> nil then
      begin
        ShowMessage('CEP não encontrado.');
        Exit;
      end;

      Logradouro := Json.GetValue<string>('logradouro');
      Bairro     := Json.GetValue<string>('bairro');
      Cidade     := Json.GetValue<string>('localidade');
      UF         := Json.GetValue<string>('uf');

      //
      // procura cidade no GeoApolo
      //
      SQL :=
        'SELECT geocidcod '+
        'FROM USER_geoapolo_cidades '+
        'WHERE cidnomecomp = :cidade '+
        'AND ufsigla = :uf';

      modulo_dados.fdquerysql19.Close;
      modulo_dados.fdquerysql19.SQL.Text := SQL;
      modulo_dados.fdquerysql19.ParamByName('cidade').AsString := Cidade;
      modulo_dados.fdquerysql19.ParamByName('uf').AsString := UF;

      if executaracao(modulo_dados.fdquerysql19,modulo_dados.fdbanco, True, modulo_dados.dtsfdquerysql19) then
        begin
          CodCidade := modulo_dados.fdquerysql19.FieldByName('geocidcod').AsString;
        end
      else
        begin
          ShowMessage('Cidade não cadastrada no GeoApolo.');
          Exit;
        end;

      //
      // grava CEP na tabela local
      //
      SQL :=
        'INSERT INTO USER_geoapolo_cepapolo ('+
        'cepcod,'+
        'tipologradabreviado,'+
        'cependerloc,'+
        'cepbair1,'+
        'cepcidcodcorreio,'+
        'ceptaborigem'+
        ') VALUES ('+
        ':cepcod,'+
        ':tipologradouro,'+
        ':logradouro,'+
        ':bairro,'+
        ':cidade,'+
        '''CEP_ESP'''+
        ')';

      modulo_dados.fdquerysql3.Close;
      modulo_dados.fdquerysql3.SQL.Text := SQL;

      modulo_dados.fdquerysql3.ParamByName('cepcod').AsString :=
        StringReplace(ACep,'-','',[rfReplaceAll]);

      modulo_dados.fdquerysql3.ParamByName('tipologradouro').AsString :=
        Copy(Logradouro,1,Pos(' ',Logradouro)-1);

      modulo_dados.fdquerysql3.ParamByName('logradouro').AsString :=
        Logradouro;

      modulo_dados.fdquerysql3.ParamByName('bairro').AsString :=
        Bairro;

      modulo_dados.fdquerysql3.ParamByName('cidade').AsString :=
        CodCidade;

      modulo_dados.fdquerysql3.ExecSQL;

      //
      // preencher tela
      //
      lbllogradouro.Text    := Copy(Logradouro,1,Pos(' ',Logradouro)-1);
      lblentender.Text      := Trim(Copy(Logradouro,Pos(' ', Logradouro) + 1,Length(Logradouro)));
      lblentbair.Text       := Bairro;
      lblcidcod.Text        := CodCidade;
      lblnomecidade.Caption := Cidade;
      lbluf.Text            := UF;
    finally
      Json.Free;
    end;

  finally
    Http.Free;
  end;
end;

procedure Tfrmcadentidade.lbllogradouroentregaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then
      spbuscalogradouroentrega.Click;
  if ((Key = VK_RETURN) or (Key = VK_TAB)) then
     lblenderecoentrega.SetFocus;
end;
procedure Tfrmcadentidade.lbllogradouroKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then
     spbuscalogradouro.Click;
  if ((Key = VK_RETURN) or (Key = VK_TAB)) then
     lblentender.SetFocus;
end;

procedure Tfrmcadentidade.lblnomedamaeKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then lblresidecom.SetFocus;
end;
procedure Tfrmcadentidade.lblnomedopaiEnter(Sender: TObject);
begin
  if frmentidades.filhossimnao = 'Sim' then
  begin
    rdgfilhos_sim.Checked := True;
    rdgfilhosnao.Checked  := False;
  end
  else
  begin
    rdgfilhos_sim.Checked := False;
    rdgfilhosnao.Checked  := True;
  end;
end;
procedure Tfrmcadentidade.lblnomedopaiKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then lblnomedamae.SetFocus;
end;
procedure Tfrmcadentidade.lblnumerocobrancaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then lblbairrocob.SetFocus;
end;
procedure Tfrmcadentidade.lblnumerocontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then lblcomplendercontato.SetFocus;
end;
procedure Tfrmcadentidade.lblnumerotelefoneKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then
    if not validacampo(lblnumerotelefone, 'NUMERO DO TELEFONE') then lblramal.SetFocus;
end;
procedure Tfrmcadentidade.lblobservacoesKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then spbdocumentos.Click;
end;
procedure Tfrmcadentidade.lblorigcodestrEnter(Sender: TObject);
begin
  with modulo_dados do
  begin
    if (lblativecodestr.Text <> '') and (lblnomeatividade_economica.Caption = '...') then
    begin
      fdquerysql2.Close;
      fdquerysql2.SQL.Clear;
      fdquerysql2.SQL.Text :=
        'SELECT nome_atividade_economica FROM USER_geoagenda_atividade_economica WHERE codigo_atividade_economica = :ativeconcodestr';
      fdquerysql2.ParamByName('ativeconcodestr').AsString := lblativecodestr.Text;
      if executaracao(fdquerysql2, fdbanco, true, dtsfdquerysql2) then
      begin
        lblnomeatividade_economica.Caption := fdquerysql2.FieldByName('nome_atividade_economica').AsString;
        lblnomeatividade_economica.Refresh;
      end;
    end;
  end;
end;
procedure Tfrmcadentidade.lblorigcodestrKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then lblregiao.SetFocus;
  if Key = VK_F4 then spbuscaorigem.Click;
end;
procedure Tfrmcadentidade.lblramalKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then spbaddtelefone.Click;
end;
procedure Tfrmcadentidade.lblregiaoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then spbuscaregiao.Click;
  if (Key = VK_RETURN) or (Key = VK_TAB) then
  begin
    lblnomeregiao.Caption := retorna_regiaopais(lblregiao.Text);
    lblnomeregiao.Refresh;
    lblconceito.SetFocus;
  end;
end;
procedure Tfrmcadentidade.lblresidecomKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then rdgfilhosnao.SetFocus;
end;
procedure Tfrmcadentidade.lblsiteKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then lblcomunicador.SetFocus;
end;
procedure Tfrmcadentidade.lbltipocobcodChange(Sender: TObject);
begin
  lbltipocobnome.Caption := '...';
end;
procedure Tfrmcadentidade.lbltipocobcodKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then spbbuscatipocobcod.Click;
  if (Key = VK_RETURN) or (Key = VK_TAB) then lblbconum.SetFocus;
end;
procedure Tfrmcadentidade.lbltipotratKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if ((Key = VK_RETURN) or (Key = VK_TAB)) then
      lblentnome.SetFocus;
  if Key = VK_F4 then
     spbuscatipotrat.Click;
end;

procedure Tfrmcadentidade.lblufcontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if ((Key = VK_TAB) or (Key = VK_RETURN)) then
      lblcargocontato.SetFocus;
end;

procedure Tfrmcadentidade.lblufEnter(Sender: TObject);
var
   vCEP:string;
begin
  if (lblcidcod.Text <> '') and (lblnomecidade.Caption = '...') then
    begin
      retorna_cidade_estado(lblcidcod.Text, frmentidades.integraentidadeapolo);
      lblnomecidade.Refresh;
    end;
  if (mskcep.text = '') then
     begin
        vCEP := BuscarCEPporEndereco(lbluf.Text, lblnomecidade.Caption, lblentender.Text);
     end;
end;

procedure Tfrmcadentidade.lblufKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if ((Key = VK_RETURN) or (Key = VK_TAB)) then
     lblcaixapostal.SetFocus;
end;

procedure Tfrmcadentidade.lblvalorcontribuicaoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if ((Key = VK_RETURN) or (Key = VK_TAB)) then
    cbogeracarne.SetFocus;
end;

procedure Tfrmcadentidade.mskcepcontatoEnter(Sender: TObject);
begin
  with modulo_dados do
  begin
    if (lblentcontatonome.Caption = '...') and (lblentcontatocod.Text <> '') then
    begin
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := 'SELECT e.entnome FROM entidade e WITH(NOLOCK) WHERE entcod = :entcontatocod';
      fdquerysql.ParamByName('entcontatocod').AsString := lblentcontatocod.Text;
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
      begin
        lblentcontatonome.Caption := fdquerysql.FieldByName('entnome').AsString;
        lblentcontatonome.Refresh;
      end;
    end;
  end;
end;
procedure Tfrmcadentidade.mskcepcontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then cbologradourocontato.SetFocus;
end;
procedure Tfrmcadentidade.mskcepEnter(Sender: TObject);
begin
  // reservado para implementação futura
end;

procedure Tfrmcadentidade.mskcepentregaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then lblcidcodentrega.SetFocus;
end;

procedure Tfrmcadentidade.mskcepKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if ((Key = VK_TAB) or (Key = VK_RETURN)) then
     lbllogradouro.SetFocus;
end;

procedure Tfrmcadentidade.mskcep_cobKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then lblcidadecobranca.SetFocus;
end;

procedure Tfrmcadentidade.mskdtcadastroKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if ((Key = VK_RETURN) or (Key = VK_TAB)) then
     cboescolaridade.SetFocus;
end;

procedure Tfrmcadentidade.mskdtfinalvigenciaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then cbostatuscontato.SetFocus;
end;

procedure Tfrmcadentidade.mskdtiniciovigenciaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then mskdtfinalvigencia.SetFocus;
end;

procedure Tfrmcadentidade.mskdtnascimentoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then mskdtcadastro.SetFocus;
end;
// =============================================================================
//  BUSCAS (SPEEDBUTTONS)
// =============================================================================
// -----------------------------------------------------------------------------
//  5. spbuscatipotratClick  (Busca Tipo Tratamento)
//  PROBLEMA ORIGINAL: frm.Free sem desacoplar grid/datasource.
// -----------------------------------------------------------------------------
{procedure Tfrmcadentidade.spbuscatipotratClick(Sender: TObject);
var
  vSQL, vControle: string;
  frm: TFrmConsulta3;
  i: Integer;
begin
  with modulo_dados do
  begin
    fdquerysql20.Close;
    fdquerysql20.SQL.Clear;
    if IsGeoApolo then
        begin
          vSQL      := 'SELECT * FROM USER_geoapolo_tipotratamento';
          vControle := 'TIPOTRATENTIDADE';
        end
    else if IsAlvo then
        begin
          vSQL      := 'SELECT * FROM tipo_tratamento';
          vControle := 'TIPOTRATENTIDADE_APOLO';
        end
    else
        begin
          MessageDlg('Banco não identificado. Verifique as configurações de integração.',
                     mtWarning, [mbOK], 0);
          Exit;
        end;
    // CORREÇÃO 1: usa fdquerysql20 (dedicado a este lookup),
    // nunca fdquerysql9 que pode estar em uso por outro lookup simultâneo.
    fdquerysql20.SQL.Text := vSQL;
    // CORREÇÃO 2: executaracao retorna False tanto para erro quanto para
    // "sem linhas". Aqui só interrompemos se a tabela realmente estiver vazia
    // (IsEmpty). Se houver erro de execução, executaracao já exibe mensagem.
    // Para GeoApolo vazio: importa os dados e tenta novamente UMA vez.
    if executaracao(fdquerysql20, fdbanco, true, dtsfdquerysql20) then
       begin
       end;
    if fdquerysql20.IsEmpty then
    begin
      fdquerysql20.Close;
      fdquerysql20.sql.clear;
      if IsGeoApolo then
      begin
        integra_tipo_tratamento('');
        // Reabre após importar
        //fdquerysql20.Open;
        if executaracao(fdquerysql20, fdbanco, true, dtsfdquerysql20) then
           begin
           end;
       { if fdquerysql20.IsEmpty then
        begin
          MessageDlg('Nenhum tipo de tratamento encontrado mesmo após importação.',
                     mtWarning, [mbOK], 0);
          fdquerysql20.Close;
          Exit;
        end;
      end
      else
      begin
        MessageDlg('Tabela de tipo de tratamento está vazia!', mtWarning, [mbOK], 0);
        Exit;
      end;
    end;
    frm := TFrmConsulta3.Create(Self);
    try
      frm.controle                 := vControle;
      dtsfdquerysql20.DataSet      := fdquerysql20;
      frm.gridconsulta.DataSource  := dtsfdquerysql20;
      for i := 0 to fdquerysql20.Fields.Count - 1 do
      begin
        frm.cbocampo.Items.Add(fdquerysql20.Fields[i].DisplayName);
        frm.cbordem.Items.Add(fdquerysql20.Fields[i].DisplayName);
      end;
      if frm.cbocampo.Items.Count > 0 then frm.cbocampo.ItemIndex := 0;
      if frm.cbordem.Items.Count  > 0 then frm.cbordem.ItemIndex  := 0;
      frm.gridconsulta.Refresh;
      frm.ShowModal;
    finally
      // Ordem obrigatória — desacopla antes de liberar
      frm.gridconsulta.DataSource := nil;
      dtsfdquerysql20.DataSet     := nil;
      fdquerysql20.Close;
      frm.Free;
    end;
  end;
end; }

procedure Tfrmcadentidade.spbuscatipotratClick(Sender: TObject);
var
  vSQL, vControle: string;
  frm: TFrmConsulta3;
  i: Integer;
begin
  with modulo_dados do
  begin

    if IsGeoApolo then
        begin
          vSQL      := 'SELECT * FROM USER_geoapolo_tipotratamento';
          vControle := 'TIPOTRATENTIDADE';
        end
    else if IsAlvo then
        begin
          vSQL      := 'SELECT * FROM tipo_tratamento';
          vControle := 'TIPOTRATENTIDADE_APOLO';
        end
    else
        begin
          MessageDlg('Banco não identificado. Verifique as configurações de integração.',
                     mtWarning, [mbOK], 0);
          Exit;
        end;
    // CORREÇÃO 1: usa fdquerysql20 (dedicado a este lookup),
    // nunca fdquerysql9 que pode estar em uso por outro lookup simultâneo.
    fdquerysql20.Close;
    fdquerysql20.SQL.Clear;
    fdquerysql20.SQL.Text := vSQL;
    // CORREÇÃO 2: executaracao retorna False tanto para erro quanto para
    // "sem linhas". Aqui só interrompemos se a tabela realmente estiver vazia
    // (IsEmpty). Se houver erro de execução, executaracao já exibe mensagem.
    // Para GeoApolo vazio: importa os dados e tenta novamente UMA vez.
    if executaracao(fdquerysql20, fdbanco, true, dtsfdquerysql20) then
       begin
       end;
    if fdquerysql20.IsEmpty then
    begin
      if IsGeoApolo then
        begin
          integra_tipo_tratamento('');
         { if fdquerysql20.IsEmpty then
          begin
            MessageDlg('Nenhum tipo de tratamento encontrado mesmo após importação.',
                       mtWarning, [mbOK], 0);
            fdquerysql20.Close;
            Exit;
          end; }
        end
      else
        begin
          MessageDlg('Tabela de tipo de tratamento está vazia!', mtWarning, [mbOK], 0);
          Exit;
        end;
    end;
    frm := TFrmConsulta3.Create(Self);
    try
      frm.controle                 := vControle;
      dtsfdquerysql20.DataSet      := fdquerysql20;
      frm.gridconsulta.DataSource  := dtsfdquerysql20;
      for i := 0 to fdquerysql20.Fields.Count - 1 do
      begin
        frm.cbocampo.Items.Add(fdquerysql20.Fields[i].DisplayName);
        frm.cbordem.Items.Add(fdquerysql20.Fields[i].DisplayName);
      end;
      if frm.cbocampo.Items.Count > 0 then frm.cbocampo.ItemIndex := 0;
      if frm.cbordem.Items.Count  > 0 then frm.cbordem.ItemIndex  := 0;
      frm.gridconsulta.Refresh;
      frm.ShowModal;
    finally
      // Ordem obrigatória — desacopla antes de liberar
      frm.gridconsulta.DataSource := nil;
      dtsfdquerysql20.DataSet     := nil;
      fdquerysql20.Close;
      frm.Free;
    end;
  end;
end;

// -----------------------------------------------------------------------------
//  13. spbuscatividadeClick  (Busca Atividade Econômica)
//  PROBLEMA ORIGINAL: frm.Free sem desacoplar grid/datasource.
// -----------------------------------------------------------------------------
procedure Tfrmcadentidade.spbuscatividadeClick(Sender: TObject);
var
  vSQL, vControle: string;
  frm: TFrmConsulta3;
  i: Integer;
begin
  with modulo_dados do
  begin
    if IsGeoApolo then
      begin
        vSQL      := 'SELECT * FROM USER_geoapolo_atividade_economica ORDER BY ativeconnome ASC';
        vControle := 'ATIVIDADE_ECONOMICAG';
      end
    else if IsAlvo then
      begin
        vSQL      := 'SELECT AE.ativeconcodestr, ae.AtivEconNome, ae.ativeconcnae, ae.AtivEconCNAEComp ' +
                     'FROM ATIV_ECONOMICA ae WITH(NOLOCK) ORDER BY ae.AtivEconCodEstr ASC';
        vControle := 'ATIVIDADE_ECONOMICA_APOLO';
      end
    else
      Exit;
    fdquerysql19.Close;
    fdquerysql19.SQL.Clear;
    fdquerysql19.SQL.Text := vSQL;
    if not executaracao(fdquerysql19, fdbanco, true, dtsfdquerysql19) then
      begin
        MessageDlg('TABELA DE ATIVIDADE ECONÔMICA ESTÁ VAZIA!', mtWarning, [mbOK], 0);
        Exit;
      end;
    frm := TFrmConsulta3.Create(Self);
    try
      frm.controle                 := vControle;
      dtsfdquerysql19.DataSet      := fdquerysql19;
      frm.gridconsulta.DataSource  := dtsfdquerysql19;
      for i := 0 to fdquerysql19.Fields.Count - 1 do
      begin
        frm.cbocampo.Items.Add(fdquerysql19.Fields[i].DisplayName);
        frm.cbordem.Items.Add(fdquerysql19.Fields[i].DisplayName);
      end;
      frm.gridconsulta.Refresh;
      frm.ShowModal;
    finally
      // CORREÇÃO: ordem obrigatória — desacopla antes de liberar
      frm.gridconsulta.DataSource := nil;
      dtsfdquerysql19.DataSet     := nil;
      fdquerysql19.Close;
      frm.Free;
    end;
  end;
end;

// -----------------------------------------------------------------------------
//  14. spbuscategoriaClick  (Busca Categoria)
//  PROBLEMA ORIGINAL: frm.Free sem desacoplar grid/datasource; fdquerysql19
//  era aberto duas vezes (executaracao + fdquerysql19.Open redundante).
// -----------------------------------------------------------------------------
procedure Tfrmcadentidade.spbuscategoriaClick(Sender: TObject);
var
  vSQL, vControle: string;
  frm: TFrmConsulta3;
  i: Integer;
begin
  with modulo_dados do
  begin
    if IsGeoApolo then
      begin
        vSQL      := 'SELECT gc.geocategcodestr, gc.geocategnome ' +
                     'FROM USER_geoapolo_categoria gc ' +
                     'GROUP BY gc.geocategcodestr, gc.geocategnome';
        vControle := 'CATEGORIA_ENTIDADE';
      end
    else if IsAlvo then
      begin
        vSQL      := 'SELECT cat.categcodestr, cat.categnome FROM categoria cat WITH(NOLOCK) ' +
                     'LEFT JOIN USUARIO_CATEG utc WITH(NOLOCK) ' +
                     '  ON cat.CategCodEstr = utc.CategCodEstr AND utc.usucod = :codigousuario';
        vControle := 'CATEGORIA_ENTIDADE_ALVO';
      end
    else
      Exit;
    fdquerysql19.Close;
    fdquerysql19.SQL.Clear;
    fdquerysql19.SQL.Text := vSQL;
    if IsAlvo then
      fdquerysql19.ParamByName('codigousuario').AsString := frmlogon.codigousuario;
    if not executaracao(fdquerysql19, fdbanco, true, dtsfdquerysql19) then
    begin
      MessageDlg('TABELA DE CATEGORIAS ESTÁ VAZIA!', mtWarning, [mbOK], 0);
      Exit;
    end;
    frm := TFrmConsulta3.Create(Self);
    try
      frm.controle                 := vControle;
      dtsfdquerysql19.DataSet      := fdquerysql19;
      frm.gridconsulta.DataSource  := dtsfdquerysql19;
      for i := 0 to fdquerysql19.Fields.Count - 1 do
      begin
        frm.cbocampo.Items.Add(fdquerysql19.Fields[i].DisplayName);
        frm.cbordem.Items.Add(fdquerysql19.Fields[i].DisplayName);
      end;
      if IsAlvo then frm.cbocampo.ItemIndex := 0;
      frm.gridconsulta.Refresh;
      frm.ShowModal;
    finally
      // CORREÇÃO: ordem obrigatória — desacopla antes de liberar
      frm.gridconsulta.DataSource := nil;
      dtsfdquerysql19.DataSet     := nil;
      fdquerysql19.Close;
      frm.Free;
    end;
  end;
end;

// -----------------------------------------------------------------------------
//  4. spbuscaocupacaoClick  (Busca Cargo/Ocupação)
//  PROBLEMA ORIGINAL: leitura de campos dentro do form filho via variável
//  global frmconsulta3 (ponteiro diferente do frm local = AV garantido).
//  CORREÇÃO: leitura APÓS ShowModal retornar, com dataset ainda aberto.
//  ATENÇÃO: em unt_consultav3.pas, para controle = 'OCUPACAO', substitua
//  todo o bloco que acessa frmcadentidade por apenas: ModalResult := mrOk;
// -----------------------------------------------------------------------------
procedure Tfrmcadentidade.spbuscaocupacaoClick(Sender: TObject);
var
  vSQL, vControle: string;
  frm: TFrmConsulta3;
  i: Integer;
begin
  with modulo_dados do
  begin
    if IsGeoApolo then
      begin
        vSQL      := 'SELECT geocargocodestr, geocargonome FROM USER_geoapolo_cargos ORDER BY geocargonome ASC';
        vControle := 'OCUPACAO';
      end
    else if IsAlvo then
      begin
        vSQL      := 'SELECT cargocodestr, cargonome FROM cargo ORDER BY cargocodestr ASC';
        vControle := 'OCUPACAO';
      end
    else
      Exit;
    // Usa fdquerysql9 — não conflita com fdquerysql usado por outros lookups
    fdquerysql9.Close;
    fdquerysql9.SQL.Clear;
    fdquerysql9.SQL.Text := vSQL;
    if not executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
      begin
        MessageDlg('TABELA DE CARGOS ESTÁ VAZIA!', mtWarning, [mbOK], 0);
        Exit;
      end;
    frm := TFrmConsulta3.Create(Self);
    try
      frm.controle                := vControle;
      dtsfdquerysql9.DataSet      := fdquerysql9;
      frm.gridconsulta.DataSource := dtsfdquerysql9;
      for i := 0 to fdquerysql9.Fields.Count - 1 do
        begin
          frm.cbocampo.Items.Add(fdquerysql9.Fields[i].DisplayName);
          frm.cbordem.Items.Add(fdquerysql9.Fields[i].DisplayName);
        end;
      frm.gridconsulta.Refresh;
      frm.ShowModal;
      // CORREÇÃO: leitura APÓS ShowModal, dataset ainda aberto e válido
      if (frm.ModalResult = mrOk) and (not fdquerysql9.IsEmpty) then
      begin
        if IsGeoApolo then
          begin
            lblcargocodestr.Text := fdquerysql9.FieldByName('geocargocodestr').AsString;
            lblnomecargo.Caption := fdquerysql9.FieldByName('geocargonome').AsString;
          end
        else if IsAlvo then
          begin
            lblcargocodestr.Text := fdquerysql9.FieldByName('cargocodestr').AsString;
            lblnomecargo.Caption := fdquerysql9.FieldByName('cargonome').AsString;
          end;
        lblcargocodestr.Refresh;
        lblnomecargo.Refresh;
      end;
    finally
      // CORREÇÃO: ordem obrigatória — desacopla antes de liberar
      frm.gridconsulta.DataSource := nil;
      dtsfdquerysql9.DataSet      := nil;
      fdquerysql9.Close;
      frm.Free;
    end;
  end;
end;

// -----------------------------------------------------------------------------
//  15. spbuscaorigemClick  (Busca Origem)
//  PROBLEMA ORIGINAL: frm.Free sem desacoplar grid/datasource.
// -----------------------------------------------------------------------------
procedure Tfrmcadentidade.spbuscaorigemClick(Sender: TObject);
var
  vSQL, vControle: string;
  frm: TFrmConsulta3;
  i: Integer;
begin
  with modulo_dados do
  begin
    if IsGeoApolo then
    begin
      vSQL      := 'SELECT * FROM USER_geoapolo_origens ORDER BY geo_orignome ASC';
      vControle := 'ORIGEM_ENTIDADE';
    end
    else if IsAlvo then
    begin
      vSQL      := 'SELECT o.origcodestr, o.orignome FROM origem o WITH(NOLOCK) ' +
                   'WHERE o.origgrupo = :F AND o.origativa = :statusorigem';
      vControle := 'ORIGEM_ENTIDADE_APOLO';
    end
    else
      Exit;
    fdquerysql9.Close;
    fdquerysql9.SQL.Clear;
    fdquerysql9.SQL.Text := vSQL;
    if IsAlvo then
    begin
      fdquerysql9.ParamByName('F').AsString            := 'F';
      fdquerysql9.ParamByName('statusorigem').AsString := 'Ativa';
    end;
    if not executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
    begin
      MessageDlg('A TABELA DE ORIGEM ESTÁ VAZIA!', mtWarning, [mbOK], 0);
      Exit;
    end;
    frm := TFrmConsulta3.Create(Self);
    try
      frm.controle                := vControle;
      dtsfdquerysql9.DataSet      := fdquerysql9;
      frm.gridconsulta.DataSource := dtsfdquerysql9;
      for i := 0 to fdquerysql9.Fields.Count - 1 do
      begin
        frm.cbocampo.Items.Add(fdquerysql9.Fields[i].DisplayName);
        frm.cbordem.Items.Add(fdquerysql9.Fields[i].DisplayName);
      end;
      frm.gridconsulta.Refresh;
      frm.ShowModal;
    finally
      // CORREÇÃO: ordem obrigatória — desacopla antes de liberar
      frm.gridconsulta.DataSource := nil;
      dtsfdquerysql9.DataSet      := nil;
      fdquerysql9.Close;
      frm.Free;
    end;
  end;
end;
// -----------------------------------------------------------------------------
//  16. spbuscaregiaoClick  (Busca Região)
//  PROBLEMA ORIGINAL: frm.Free sem desacoplar grid/datasource.
// -----------------------------------------------------------------------------
procedure Tfrmcadentidade.spbuscaregiaoClick(Sender: TObject);
var
  vSQL, vControle: string;
  frm: TFrmConsulta3;
begin
  with modulo_dados do
  begin
    if IsGeoApolo then
    begin
      vSQL      := 'SELECT georegcodestr AS regcodestr, geo_regnome AS regnome ' +
                   'FROM USER_geoapolo_regiao_pais ORDER BY geo_regnome ASC';
      vControle := 'REGIAO_ENTIDADE';
    end
    else if IsAlvo then
    begin
      vSQL      := 'SELECT R.RegCodEstr, r.RegNome FROM regiao r WITH(NOLOCK)';
      vControle := 'REGIAO_ENTIDADE_APOLO';
    end
    else
      Exit;
    fdquerysql9.Close;
    fdquerysql9.SQL.Clear;
    fdquerysql9.SQL.Text := vSQL;
    if not executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
    begin
      MessageDlg('TABELA DE REGIÃO ESTÁ VAZIA!', mtWarning, [mbOK], 0);
      Exit;
    end;
    frm := TFrmConsulta3.Create(Self);
    try
      frm.controle                := vControle;
      dtsfdquerysql9.DataSet      := fdquerysql9;
      frm.gridconsulta.DataSource := dtsfdquerysql9;
      frm.gridconsulta.Refresh;
      frm.ShowModal;
    finally
      // CORREÇÃO: ordem obrigatória — desacopla antes de liberar
      frm.gridconsulta.DataSource := nil;
      dtsfdquerysql9.DataSet      := nil;
      fdquerysql9.Close;
      frm.Free;
    end;
  end;
end;
// -----------------------------------------------------------------------------
//  9. spbuscacidadeClick  (Busca Cidade — endereço principal)
//  PROBLEMA ORIGINAL: frm.Free sem desacoplar grid/datasource.
// -----------------------------------------------------------------------------
procedure Tfrmcadentidade.spbuscacidadeClick(Sender: TObject);
var
  frm: TFrmConsulta3;
  i: Integer;
begin

    if not (IsGeoApolo or IsAlvo) then
       Exit;
    modulo_dados.fdquerysql9.Close;
    modulo_dados.fdquerysql9.SQL.Clear;
    modulo_dados.fdquerysql9.SQL.Text := 'SELECT * FROM USER_geoapolo_cidades';
    if not executaracao(modulo_dados.fdquerysql9, modulo_dados.fdbanco, true, modulo_dados.dtsfdquerysql9) then
      begin
        MessageDlg('Tabela de cidades está vazia!', mtWarning, [mbOK], 0);
        Exit;
      end;

    frm := TFrmConsulta3.Create(Self);
    try
      frm.controle                := 'ENTCIDCOD';
      modulo_dados.dtsfdquerysql9.DataSet      := modulo_dados.fdquerysql9;
      frm.gridconsulta.DataSource := modulo_dados.dtsfdquerysql9;
      for i := 0 to modulo_dados.fdquerysql9.Fields.Count - 1 do
      begin
        frm.cbocampo.Items.Add(modulo_dados.fdquerysql9.Fields[i].DisplayName);
        frm.cbordem.Items.Add(modulo_dados.fdquerysql9.Fields[i].DisplayName);
      end;
      frm.gridconsulta.Refresh;
      frm.ShowModal;
    finally
      // CORREÇÃO: ordem obrigatória — desacopla antes de liberar
      frm.gridconsulta.DataSource := nil;
      modulo_dados.dtsfdquerysql9.DataSet      := nil;
      modulo_dados.fdquerysql9.Close;
      frm.Free;
    end;

end;

// -----------------------------------------------------------------------------
//  10. spbuscacidadecobClick  (Busca Cidade Cobrança)
//  PROBLEMA ORIGINAL: frm.Free sem desacoplar grid/datasource.
// -----------------------------------------------------------------------------
procedure Tfrmcadentidade.spbuscacidadecobClick(Sender: TObject);
var
  frm: TFrmConsulta3;
  i: Integer;
begin
  with modulo_dados do
  begin
    fdquerysql9.Close;
    fdquerysql9.SQL.Clear;
    fdquerysql9.SQL.Text := 'SELECT * FROM USER_geoapolo_cidades ORDER BY ufsigla ASC';
    if not executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
    begin
      MessageDlg('Tabela de cidades está vazia!', mtWarning, [mbOK], 0);
      Exit;
    end;
    frm := TFrmConsulta3.Create(Self);
    try
      frm.controle                := 'CIDADES_COBRANCA';
      dtsfdquerysql9.DataSet      := fdquerysql9;
      frm.gridconsulta.DataSource := dtsfdquerysql9;
      for i := 0 to fdquerysql9.Fields.Count - 1 do
      begin
        frm.cbocampo.Items.Add(fdquerysql9.Fields[i].DisplayName);
        frm.cbordem.Items.Add(fdquerysql9.Fields[i].DisplayName);
      end;
      frm.gridconsulta.Refresh;
      frm.ShowModal;
    finally
      // CORREÇÃO: ordem obrigatória — desacopla antes de liberar
      frm.gridconsulta.DataSource := nil;
      dtsfdquerysql9.DataSet      := nil;
      fdquerysql9.Close;
      frm.Free;
    end;
  end;
end;
// -----------------------------------------------------------------------------
//  11. spbuscacidadeentregaClick  (Busca Cidade Entrega)
//  PROBLEMA ORIGINAL: usava frm.Show (não-modal) — finally liberava o form
//  imediatamente enquanto ele ainda estava visível na tela.
//  CORREÇÃO: trocado para frm.ShowModal + desacoplamento no finally.
// -----------------------------------------------------------------------------
procedure Tfrmcadentidade.spbuscacidadeentregaClick(Sender: TObject);
var
  frm: TFrmConsulta3;
  i: Integer;
begin
  with modulo_dados do
  begin
    if not IsGeoApolo then Exit;
    fdquerysql9.Close;
    fdquerysql9.SQL.Clear;
    fdquerysql9.SQL.Text := 'SELECT * FROM USER_geoapolo_cidades ORDER BY ufsigla ASC';
    if not executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
    begin
      MessageDlg('TABELA DE CIDADES ESTÁ VAZIA!', mtWarning, [mbOK], 0);
      Exit;
    end;
    frm := TFrmConsulta3.Create(Self);
    try
      frm.controle                := 'CIDADES_ENTREGA';
      dtsfdquerysql9.DataSet      := fdquerysql9;
      frm.gridconsulta.DataSource := dtsfdquerysql9;
      for i := 0 to fdquerysql9.Fields.Count - 1 do
      begin
        frm.cbocampo.Items.Add(fdquerysql9.Fields[i].DisplayName);
        frm.cbordem.Items.Add(fdquerysql9.Fields[i].DisplayName);
      end;
      frm.gridconsulta.Refresh;
      frm.ShowModal; // CORREÇÃO: era frm.Show — causava Free imediato pelo finally
    finally
      // CORREÇÃO: ordem obrigatória — desacopla antes de liberar
      frm.gridconsulta.DataSource := nil;
      dtsfdquerysql9.DataSet      := nil;
      fdquerysql9.Close;
      frm.Free;
    end;
  end;
end;
// -----------------------------------------------------------------------------
//  6. spbuscalogradouroClick  (Busca Tipo Logradouro)
//  PROBLEMA ORIGINAL: frm.Free sem desacoplar grid/datasource.
// -----------------------------------------------------------------------------
procedure Tfrmcadentidade.spbuscalogradouroClick(Sender: TObject);
var
  vSQL, vControle: string;
  frm: TFrmConsulta3;
  i: Integer;
begin
  with modulo_dados do
  begin
    if IsGeoApolo then
    begin
      vSQL      := 'SELECT * FROM USER_geoapolo_tipologradouro';
      vControle := 'TIPOLOGRADOURO';
    end
    else if IsAlvo then
    begin
      MessageDlg('INTEGRAÇÃO SINCRONIZAR AINDA NÃO CONFIGURADA!', mtWarning, [mbOK], 0);
      Exit;
    end
    else
      Exit;
    fdquerysql9.Close;
    fdquerysql9.SQL.Clear;
    fdquerysql9.SQL.Text := vSQL;
    {if not executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
    begin
      integra_tipo_logradouro('');
      spbuscalogradouro.Click;
      Exit;
    end;          }
    fdquerysql10.Close;
    fdquerysql10.SQL.Clear;
    fdquerysql10.SQL.Text :='SELECT 1 '+
                            'FROM sys.tables '+
                            'WHERE name = ''tipo_lograd''';
    fdquerysql10.Open;

    if (not fdquerysql10.IsEmpty) and (not executaracao(fdquerysql9, fdbanco, True, dtsfdquerysql9)) then
    begin
      integra_tipo_logradouro('');
      spbuscalogradouro.Click;
      Exit;
    end;
    frm := TFrmConsulta3.Create(Self);
    try
      frm.controle                := vControle;
      dtsfdquerysql9.DataSet      := fdquerysql9;
      frm.gridconsulta.DataSource := dtsfdquerysql9;
      for i := 0 to fdquerysql9.Fields.Count - 1 do
      begin
        frm.cbocampo.Items.Add(fdquerysql9.Fields[i].DisplayName);
        frm.cbordem.Items.Add(fdquerysql9.Fields[i].DisplayName);
      end;
      frm.gridconsulta.Refresh;
      frm.ShowModal;
    finally
      // CORREÇÃO: ordem obrigatória — desacopla antes de liberar
      frm.gridconsulta.DataSource := nil;
      dtsfdquerysql9.DataSet      := nil;
      fdquerysql9.Close;
      frm.Free;
    end;
  end;
end;
// -----------------------------------------------------------------------------
//  7. spbuscalogradourocobrancaClick  (Busca Logradouro Endereço Cobrança)
//  PROBLEMA ORIGINAL: frm.Free sem desacoplar grid/datasource.
// -----------------------------------------------------------------------------
procedure Tfrmcadentidade.spbuscalogradourocobrancaClick(Sender: TObject);
var
  frm: TFrmConsulta3;
  i: Integer;
begin
  with modulo_dados do
  begin
    if not IsGeoApolo then Exit;
    fdquerysql9.Close;
    fdquerysql9.SQL.Clear;
    fdquerysql9.SQL.Text := 'SELECT * FROM USER_geoapolo_tipologradouro';
    if not executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
    begin
      MessageDlg('Tabela de logradouro está vazia!', mtWarning, [mbOK], 0);
      Exit;
    end;
    frm := TFrmConsulta3.Create(Self);
    try
      frm.controle                := 'TIPOLOGRADOURO_ENDCOBRANCA';
      dtsfdquerysql9.DataSet      := fdquerysql9;
      frm.gridconsulta.DataSource := dtsfdquerysql9;
      for i := 0 to fdquerysql9.Fields.Count - 1 do
      begin
        frm.cbocampo.Items.Add(fdquerysql9.Fields[i].DisplayName);
        frm.cbordem.Items.Add(fdquerysql9.Fields[i].DisplayName);
      end;
      frm.gridconsulta.Refresh;
      frm.ShowModal;
    finally
      // CORREÇÃO: ordem obrigatória — desacopla antes de liberar
      frm.gridconsulta.DataSource := nil;
      dtsfdquerysql9.DataSet      := nil;
      fdquerysql9.Close;
      frm.Free;
    end;
  end;
end;
// -----------------------------------------------------------------------------
//  8. spbuscalogradouroentregaClick  (Busca Logradouro Endereço Entrega)
//  PROBLEMA ORIGINAL: frm.Free sem desacoplar grid/datasource.
// -----------------------------------------------------------------------------
procedure Tfrmcadentidade.spbuscalogradouroentregaClick(Sender: TObject);
var
  frm: TFrmConsulta3;
  i: Integer;
begin
  with modulo_dados do
  begin
    if not IsGeoApolo then
    begin
      MessageDlg('INTEGRAÇÃO SINCRONIZAR AINDA NÃO CONFIGURADA!', mtWarning, [mbOK], 0);
      Exit;
    end;
    fdquerysql9.Close;
    fdquerysql9.SQL.Clear;
    fdquerysql9.SQL.Text := 'SELECT * FROM USER_geoapolo_tipologradouro';
    if not executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
    begin
      integra_tipo_logradouro('');
      spbuscalogradouroentrega.Click;
      Exit;
    end;
    frm := TFrmConsulta3.Create(Self);
    try
      frm.controle                := 'TIPOLOGRADOURO_ENDENTREGA';
      dtsfdquerysql9.DataSet      := fdquerysql9;
      frm.gridconsulta.DataSource := dtsfdquerysql9;
      for i := 0 to fdquerysql9.Fields.Count - 1 do
      begin
        frm.cbocampo.Items.Add(fdquerysql9.Fields[i].DisplayName);
        frm.cbordem.Items.Add(fdquerysql9.Fields[i].DisplayName);
      end;
      frm.gridconsulta.Refresh;
      frm.ShowModal;
    finally
      // CORREÇÃO: ordem obrigatória — desacopla antes de liberar
      frm.gridconsulta.DataSource := nil;
      dtsfdquerysql9.DataSet      := nil;
      fdquerysql9.Close;
      frm.Free;
    end;
  end;
end;
// -----------------------------------------------------------------------------
//  17. spbuscacargocontatClick  (Busca Cargo do Contato)
//  PROBLEMA ORIGINAL: usava fdquerysql (compartilhado) — reabertura durante
//  o modal causava AV; frm.Free sem desacoplar grid/datasource.
//  CORREÇÃO: migrado para fdquerysql9 dedicado.
// -----------------------------------------------------------------------------
procedure Tfrmcadentidade.spbuscacargocontatClick(Sender: TObject);
var
  vSQL, vControle: string;
  frm: TFrmConsulta3;
  i: Integer;
begin
  with modulo_dados do
  begin
    if IsGeoApolo then
    begin
      vSQL      := 'SELECT * FROM USER_geoapolo_cargos ORDER BY geocargonome ASC';
      vControle := 'OCUPACAO_CONTATO';
    end
    else if IsAlvo then
    begin
      vSQL      := 'SELECT cargocodestr, cargonome FROM cargo ORDER BY cargocodestr ASC';
      vControle := 'OCUPACAO_CONTATO';
    end
    else
      Exit;
    // CORREÇÃO: usa fdquerysql9 — não conflita com fdquerysql usado em outros eventos
    fdquerysql9.Close;
    fdquerysql9.SQL.Clear;
    fdquerysql9.SQL.Text := vSQL;
    if not executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
    begin
      MessageDlg('TABELA DE CARGOS ESTÁ VAZIA!', mtWarning, [mbOK], 0);
      Exit;
    end;
    frm := TFrmConsulta3.Create(Self);
    try
      frm.controle                := vControle;
      dtsfdquerysql9.DataSet      := fdquerysql9;
      frm.gridconsulta.DataSource := dtsfdquerysql9;
      for i := 0 to fdquerysql9.Fields.Count - 1 do
      begin
        frm.cbocampo.Items.Add(fdquerysql9.Fields[i].DisplayName);
        frm.cbordem.Items.Add(fdquerysql9.Fields[i].DisplayName);
      end;
      frm.gridconsulta.Refresh;
      frm.ShowModal;
    finally
      // CORREÇÃO: ordem obrigatória — desacopla antes de liberar
      frm.gridconsulta.DataSource := nil;
      dtsfdquerysql9.DataSet      := nil;
      fdquerysql9.Close;
      frm.Free;
    end;
  end;
end;
procedure Tfrmcadentidade.spbuscacepClick(Sender: TObject);
begin
  ShowMessage('AINDA POR DESENVOLVER');
end;
// -----------------------------------------------------------------------------
//  18. spbuscacontatoClick  (Busca Contato)
//  PROBLEMA ORIGINAL: frm.Free sem desacoplar grid/datasource.
// -----------------------------------------------------------------------------
procedure Tfrmcadentidade.spbuscacontatoClick(Sender: TObject);
var
  vSQL: string;
  frm: TFrmConsulta3;
  i: Integer;
begin
  with modulo_dados do
  begin
    if IsGeoApolo then
    begin
      vSQL :=
        'SELECT uge.geoentcod, uge.geotipotratcod, uge.geoentnome, uge.geoentcep, ' +
        'ugtl.tipolograd AS geoentlograd, uge.geoentender, uge.geoenderno, uge.geoentendercomp, ' +
        'uge.geoentbair, uge.geocidcod, ugc.cidnomecomp, ugc.ufsigla, uge.geocargocodestr, ugcar.geocargonome ' +
        'FROM USER_geoapolo_entidade uge WITH(NOLOCK) ' +
        'INNER JOIN USER_geoapolo_cidades ugc ON uge.geocidcod = ugc.geocidcod ' +
        'INNER JOIN USER_geoapolo_entcateg ugec ON uge.geoentcod = ugec.geoentcod ' +
        'LEFT JOIN USER_geoapolo_tipologradouro ugtl ON uge.tipolograd = ugtl.tipolograd ' +
        'LEFT JOIN USER_geoapolo_cargos ugcar ON uge.geocargocodestr = ugcar.geocargocodestr';
      if chkgrupooracao.Checked then
        vSQL := vSQL + ' WHERE uge.geocidcod = :geocidcod AND SUBSTRING(ugec.geocategcodestr,1,2) IN (''02'')';
    end
    else if IsAlvo then
        begin
          vSQL :=
            'SELECT e.entcod, e.tipotratcod, e.entnome, e.entlograd, e.entender, e.entenderno, e.entbair, ' +
            'e.entcep, cid.cidnomecomp, cid.ufsigla, e.cargocodestr, cargo.cargonome, ew.entwebemail ' +
            'FROM entidade e WITH(NOLOCK) ' +
            'INNER JOIN cidade cid WITH(NOLOCK) ON e.cidcod = cid.cidcod ' +
            'INNER JOIN ent_categ ec WITH(NOLOCK) ON e.entcod = ec.entcod ' +
            'LEFT JOIN cargo ON e.cargocodestr = cargo.cargocodestr ' +
            'LEFT JOIN ent_web ew ON e.entcod = ew.entcod AND ew.entwebemailprinc = :entwebemailprinc';
        end
    else
      Exit;
    fdquerysql13.Close;
    fdquerysql13.SQL.Clear;
    fdquerysql13.SQL.Text := vSQL;
    if IsGeoApolo and chkgrupooracao.Checked then
      fdquerysql13.ParamByName('geocidcod').AsString := lblcidcod.Text;
    if IsAlvo then
      fdquerysql13.ParamByName('entwebemailprinc').AsString := 'Sim';
    if not executaracao(fdquerysql13, fdbanco, true, dtsfdquerysql13) then
    begin
      MessageDlg('Nenhum contato encontrado!', mtWarning, [mbOK], 0);
      Exit;
    end;
    frm := TFrmConsulta3.Create(Self);
    try
      frm.controle                := IfThen(IsGeoApolo, 'BUSCA_CONTATO_ENTIDADE', 'BUSCA_CONTATO_ENTIDADE_APOLO');
      frm.KeyPreview              := True;
      dtsfdquerysql13.DataSet     := fdquerysql13;
      frm.gridconsulta.DataSource := dtsfdquerysql13;
      for i := 0 to fdquerysql13.Fields.Count - 1 do
      begin
        frm.cbocampo.Items.Add(fdquerysql13.Fields[i].DisplayName);
        frm.cbordem.Items.Add(fdquerysql13.Fields[i].DisplayName);
      end;
      frm.gridconsulta.Refresh;
      frm.ShowModal;
    finally
      // CORREÇÃO: ordem obrigatória — desacopla antes de liberar
      frm.gridconsulta.DataSource := nil;
      dtsfdquerysql13.DataSet     := nil;
      fdquerysql13.Close;
      frm.Free;
    end;
  end;
end;

procedure Tfrmcadentidade.spbuscadioceseClick(Sender: TObject);
var
  i: Integer;
  vSQL: string;
begin
  with modulo_dados do
  begin
    vSQL :=
      'SELECT udcnbb.id, udcnbb.nome ' +
      'FROM USERdioceses_CNBB udcnbb WITH(NOLOCK) ' +
      'INNER JOIN USEREstado_CNBB uecnbb WITH(NOLOCK) ON udcnbb.estado_id = uecnbb.USERiD ' +
      'INNER JOIN USERcidades_CNBB uccnbb WITH(NOLOCK) ON udcnbb.id = uccnbb.diocese_id ' +
      'WHERE uecnbb.USERsigla = :uf AND uccnbb.descricao = :nomecidade';
    fdquerysql9.Close;
    fdquerysql9.SQL.Clear;
    fdquerysql9.SQL.Text := vSQL;
    fdquerysql9.ParamByName('uf').AsString        := lbluf.Text;
    fdquerysql9.ParamByName('nomecidade').AsString := lblnomecidade.Caption;
    if executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
    begin
      var frm := TFrmConsulta3.Create(Self);
      try
        frm.controle := 'DIOCESES_CNBB_ENTIDADE';
        frm.KeyPreview := True;
        dtsfdquerysql9.DataSet := fdquerysql9;
        frm.gridconsulta.DataSource := dtsfdquerysql9;
        for i := 0 to fdquerysql9.Fields.Count - 1 do
        begin
          frm.cbocampo.Items.Add(fdquerysql9.Fields[i].DisplayName);
          frm.cbordem.Items.Add(fdquerysql9.Fields[i].DisplayName);
        end;
        frm.gridconsulta.Refresh;
        frm.lblprocurarpor.Text := '%%';
        frm.ShowModal;
      finally
        frm.Free;
      end;
    end;
  end;
end;

// -----------------------------------------------------------------------------
//  12. spbuscacidcontatoClick  (Busca Cidade do Contato)
//  PROBLEMA ORIGINAL: frm.Free sem desacoplar grid/datasource.
// -----------------------------------------------------------------------------
procedure Tfrmcadentidade.spbuscacidcontatoClick(Sender: TObject);
var
  frm: TFrmConsulta3;
  i: Integer;
begin
  with modulo_dados do
  begin
    if not (IsGeoApolo or IsAlvo) then Exit;
    fdquerysql9.Close;
    fdquerysql9.SQL.Clear;
    fdquerysql9.SQL.Text := 'SELECT * FROM USER_geoapolo_cidades';
    if not executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
    begin
      MessageDlg('Tabela de cidades está vazia!', mtWarning, [mbOK], 0);
      Exit;
    end;
    frm := TFrmConsulta3.Create(Self);
    try
      frm.controle                := 'ENTCIDCODCONTATO';
      dtsfdquerysql9.DataSet      := fdquerysql9;
      frm.gridconsulta.DataSource := dtsfdquerysql9;
      for i := 0 to fdquerysql9.Fields.Count - 1 do
      begin
        frm.cbocampo.Items.Add(fdquerysql9.Fields[i].DisplayName);
        frm.cbordem.Items.Add(fdquerysql9.Fields[i].DisplayName);
      end;
      frm.gridconsulta.Refresh;
      frm.ShowModal;
    finally
      // CORREÇÃO: ordem obrigatória — desacopla antes de liberar
      frm.gridconsulta.DataSource := nil;
      dtsfdquerysql9.DataSet      := nil;
      fdquerysql9.Close;
      frm.Free;
    end;
  end;
end;

// -----------------------------------------------------------------------------
//  20. spbusca_escolaridadeClick  (Busca Grau Escolaridade)
//  PROBLEMA ORIGINAL: usava fdquerysql (compartilhado); frm.Free sem
//  desacoplar grid/datasource.
//  CORREÇÃO: migrado para fdquerysql9 dedicado.
// -----------------------------------------------------------------------------
procedure Tfrmcadentidade.spbusca_escolaridadeClick(Sender: TObject);
var
  frm: TFrmConsulta3;
  i: Integer;
begin
  with modulo_dados do
  begin
    if not IsGeoApolo then Exit;
    // CORREÇÃO: usa fdquerysql9 — não conflita com fdquerysql usado em outros eventos
    fdquerysql9.Close;
    fdquerysql9.SQL.Clear;
    fdquerysql9.SQL.Text := 'SELECT * FROM USER_geoapolo_grauescolaridade ORDER BY grau_escolaridade ASC';
    if not executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
    begin
      MessageDlg('TABELA DE GRAU DE ESCOLARIDADE ESTÁ VAZIA!', mtWarning, [mbOK], 0);
      Exit;
    end;
    frm := TFrmConsulta3.Create(Self);
    try
      frm.controle                := 'GRAU_ESCOLARIDADE';
      dtsfdquerysql9.DataSet      := fdquerysql9;
      frm.gridconsulta.DataSource := dtsfdquerysql9;
      for i := 0 to fdquerysql9.Fields.Count - 1 do
      begin
        frm.cbocampo.Items.Add(fdquerysql9.Fields[i].DisplayName);
        frm.cbordem.Items.Add(fdquerysql9.Fields[i].DisplayName);
      end;
      frm.gridconsulta.Refresh;
      frm.ShowModal;
    finally
      // CORREÇÃO: ordem obrigatória — desacopla antes de liberar
      frm.gridconsulta.DataSource := nil;
      dtsfdquerysql9.DataSet      := nil;
      fdquerysql9.Close;
      frm.Free;
    end;
  end;
end;

procedure Tfrmcadentidade.spbsalvainformacoescomplClick(Sender: TObject);
begin
  grava_entidade(TELA4);
end;

procedure Tfrmcadentidade.spbenderecocobrancaClick(Sender: TObject);
begin
  grava_entidade(TELA5);
end;

procedure Tfrmcadentidade.spbenderecoentregaClick(Sender: TObject);
begin
  grava_entidade(TELA5);
end;

procedure Tfrmcadentidade.tabcategoriasEnter(Sender: TObject);
begin
  mostra_entidade_categoria(lblentcod.Text, frmentidades.integraentidadeapolo);
end;

procedure Tfrmcadentidade.tabdadospessoaisEnter(Sender: TObject);
begin
  with frmentidades do
  begin
    if filhossimnao = 'Sim' then
    begin
      rdgfilhos_sim.Checked := True;
      rdgfilhosnao.Checked  := False;
    end
    else
    begin
      rdgfilhosnao.Checked  := True;
      rdgfilhos_sim.Checked := False;
    end;
  end;
end;

procedure Tfrmcadentidade.tab_comunicacaoEnter(Sender: TObject);
begin
  lblddd.SetFocus;
  mostra_entidade_contatoweb(frmentidades.vgeoentcod, frmentidades.integraentidadeapolo);
  mostra_telefones_entidade(frmentidades.vgeoentcod, frmentidades.integraentidadeapolo);
  configura_grid('GEOGRIDTELEFONES', frmcadentidade, 'gridtelefones', frmlogon.nomeusuario, gridtelefones, modulo_dados.dtsfdquerysql);
  configura_grid('GEOGRIDWEBCONTATO', frmcadentidade, 'gridwebcontato', frmlogon.nomeusuario, gridwebcontato, modulo_dados.dtsfdquerysql);
end;

procedure Tfrmcadentidade.tab_documentosEnter(Sender: TObject);
begin
  controledocumentos := 'INCLUSÃO';
  mostra_entidade_documentos(lblentcod.Text, frmprincipal.integraentidadesapolo);
end;

procedure Tfrmcadentidade.cboescolaridadeKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if ((Key = VK_RETURN) or (Key = VK_TAB)) then
     lblcargocodestr.SetFocus;
end;

procedure Tfrmcadentidade.lblativecodestrKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then spbuscatividade.Click;
  if (Key = VK_RETURN) or (Key = VK_TAB) then lblorigcodestr.SetFocus;
end;

procedure Tfrmcadentidade.lblagnumEnter(Sender: TObject);
begin
  // Busca o nome do banco ao entrar no campo agência,
  // mas só se o código do banco estiver preenchido e o nome ainda não foi buscado
  if (Trim(lblbconum.Text) = '') or (lblnomebanco.Caption <> '') then
    Exit
  else
     BuscarNomeBanco(lblbconum.Text);
end;

procedure Tfrmcadentidade.lblagnumKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then spbagencia.Click;
  if (Key = VK_RETURN) or (Key = VK_TAB) then lblgeocontacorrente.SetFocus;
end;

procedure Tfrmcadentidade.lblbconumEnter(Sender: TObject);
begin
  with modulo_dados do
  begin
    if (lbltipocobcod.Text <> '') and (lbltipocobnome.Caption = '...') then
    begin
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := 'SELECT tipocobnome FROM tipo_cobranca WHERE tipocobcod = :tipocobcod';
      fdquerysql.ParamByName('tipocobcod').AsString := lbltipocobcod.Text;
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
      begin
        lbltipocobnome.Caption := fdquerysql.FieldByName('tipocobnome').AsString;
        lbltipocobcod.Refresh;
      end;
    end;
  end;
end;

procedure Tfrmcadentidade.lblbconumKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then
  begin
    spbbco.Click;
    Exit;
  end;
  // Ao limpar o campo, reseta a legenda para que lblagnumEnter saiba que
  // ainda não buscou (a guarda usa Caption = '...' como sentinela)
  if Trim(lblbconum.Text) = '' then
  begin
    lblnomebanco.Caption := '...';
    lblnomebanco.Refresh;
    Exit;
  end;
  if (Key = VK_RETURN) or (Key = VK_TAB) then
  begin
    BuscarNomeBanco(lblbconum.Text);
    lblagnum.SetFocus;
  end;
end;

procedure Tfrmcadentidade.spbaddcontatowebClick(Sender: TObject);
var
  vEmailAntigo: string;
  vEntWebSeq: Integer;
  vSQL: string;
begin
  with modulo_dados do
  begin
    if not validacombo(cbotipocontato, 'TIPO DE CONTATO NÃO PODE SER VAZIO!') then begin cbotipocontato.SetFocus; Exit; end;
    if not validacampo(lblemail, 'E-MAIL NÃO PODE SER VAZIO!') then Exit;
    flagprincipal := IfThen(chkwebprincipal.Checked, 'Sim', 'Não');
    fdbanco.StartTransaction;
    try
      if IsGeoApolo then
      begin
        fdquerysql.Close;
        fdquerysql.SQL.Clear;
        fdquerysql.SQL.Text :=
          'SELECT 1 FROM USER_geoapolo_entidade_webcontato WHERE email = :email AND geoentcod = :geoentcod';
        fdquerysql.ParamByName('email').AsString    := lblemail.Text;
        fdquerysql.ParamByName('geoentcod').AsString := frmentidades.vgeoentcod;
        if executaracao(fdquerysql, fdbanco, True, dtsfdquerysql) then
          vSQL := 'UPDATE USER_geoapolo_entidade_webcontato ' +
                  'SET tipo_contato = :tipo_contato, website = :website, comunicador_instantaneo = :comunicador_instantaneo, ' +
                  'endereco_comunicador = :endereco_comunicador, flagemailprincipal = :flagemailprincipal ' +
                  'WHERE geoentcod = :geoentcod AND email = :email'
        else
          vSQL := 'INSERT INTO USER_geoapolo_entidade_webcontato ' +
                  '(geoentcod, tipo_contato, website, email, flagemailprincipal, comunicador_instantaneo, endereco_comunicador) ' +
                  'VALUES (:geoentcod, :tipo_contato, :website, :email, :flagemailprincipal, :comunicador_instantaneo, :endereco_comunicador)';
        fdquerysql3.Close;
        fdquerysql3.SQL.Clear;
        fdquerysql3.SQL.Text := vSQL;
        fdquerysql3.ParamByName('tipo_contato').AsString           := cbotipocontato.Text;
        fdquerysql3.ParamByName('website').AsString                := lblsite.Text;
        fdquerysql3.ParamByName('comunicador_instantaneo').AsString := lblcomunicador.Text;
        fdquerysql3.ParamByName('endereco_comunicador').AsString    := lblendcomunicador.Text;
        fdquerysql3.ParamByName('flagemailprincipal').AsString      := flagprincipal;
        fdquerysql3.ParamByName('email').AsString                   := lblemail.Text;
        fdquerysql3.ParamByName('geoentcod').AsString               := lblentcod.Text;
        if executaracao(fdquerysql3, fdbanco, True, dtsfdquerysql3) then
        begin
          fdbanco.Commit;
          lblemail.Clear; lblsite.Clear; lblcomunicador.Clear; lblendcomunicador.Clear;
          cbotipocontato.ItemIndex := -1;
          chkwebprincipal.Checked := False;
          chkwebprincipal.Refresh;
          mostra_entidade_contatoweb(lblentcod.Text, frmentidades.integraentidadeapolo);
          cbotipocontato.SetFocus;
        end
        else
        begin
          fdbanco.Rollback;
          MessageDlg('PROBLEMAS AO TENTAR REALIZAR A OPERAÇÃO!', mtError, [mbOK], 0);
          lblemail.SetFocus;
        end;
      end
      else if IsAlvo then
      begin
        fdquerysql.Close;
        fdquerysql.SQL.Clear;
        fdquerysql.SQL.Text := 'SELECT MAX(entwebseq) + 1 AS sequencia FROM ent_web';
        if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
          vEntWebSeq := fdquerysql.FieldByName('sequencia').AsInteger;
        fdquerysql.Close;
        fdquerysql.SQL.Clear;
        fdquerysql.SQL.Text := 'SELECT entwebemail FROM ent_web ew WITH(NOLOCK) WHERE ew.entwebemail = :email AND entcod = :entcod';
        fdquerysql.ParamByName('email').AsString  := lblemail.Text;
        fdquerysql.ParamByName('entcod').AsString := lblentcod.Text;
        if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
        begin
          vEmailAntigo := fdquerysql.FieldByName('entwebemail').AsString;
          vSQL := 'UPDATE ent_web SET entwebtipo = :webtipo, entwebemail = :email, entwebwww = :site, ' +
                  'entwebemailprinc = :emailprinc WHERE entcod = :entcod AND entwebemail = :emailantigo';
        end
        else
          vSQL := 'INSERT INTO ent_web (entcod, entwebseq, entwebtipo, entwebemail, entwebwww, entwebemailprinc) ' +
                  'VALUES (:entcod, :emailseq, :webtipo, :email, :site, :emailprinc)';
        fdquerysql3.Close;
        fdquerysql3.SQL.Clear;
        fdquerysql3.SQL.Text := vSQL;
        fdquerysql3.ParamByName('webtipo').AsString   := cbotipocontato.Text;
        fdquerysql3.ParamByName('email').AsString     := lblemail.Text;
        fdquerysql3.ParamByName('site').AsString      := lblsite.Text;
        fdquerysql3.ParamByName('emailprinc').AsString := flagprincipal;
        fdquerysql3.ParamByName('entcod').AsString    := lblentcod.Text;
        if fdquerysql3.Params.FindParam('emailantigo') <> nil then
          fdquerysql3.ParamByName('emailantigo').AsString := vEmailAntigo;
        if fdquerysql3.Params.FindParam('emailseq') <> nil then
          fdquerysql3.ParamByName('emailseq').AsInteger := vEntWebSeq;
        if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
          begin
            fdbanco.Commit;
            cbotipocontato.ItemIndex := -1;
            atualiza_log_entidade_apolo(lblentcod.Text);
            lblemail.Clear; lblsite.Clear;
            chkwebprincipal.Checked := False;
            mostra_entidade_contatoweb(lblentcod.Text, frmentidades.integraentidadeapolo);
            lblemail.SetFocus;
          end
        else
            begin
              fdbanco.Rollback;
              MessageDlg('ERRO AO SALVAR CONTATO WEB!', mtError, [mbOK], 0);
            end;
      end;
    except
      on E: Exception do
      begin
        if fdbanco.InTransaction then fdbanco.Rollback;
        MessageDlg('Erro: ' + E.Message, mtError, [mbOK], 0);
      end;
    end;
  end;
end;

procedure Tfrmcadentidade.cbocontatoprincipalKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then cbograudecisao.SetFocus;
end;

procedure Tfrmcadentidade.lblbairrocobKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then lblcomplementocob.SetFocus;
end;

procedure Tfrmcadentidade.lblbairrocontatoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then lblcidadecontato.SetFocus;
end;

procedure Tfrmcadentidade.lblbairro_entregaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then lblcompl_entrega.SetFocus;
end;

end.
