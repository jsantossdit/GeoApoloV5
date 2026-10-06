unit unt_mapeamento_savic_entidade;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes,
  Vcl.Graphics, Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.StdCtrls, Vcl.Buttons,
  Vcl.ExtCtrls, Vcl.Grids, System.JSON, System.IOUtils, FireDAC.Comp.Client;

type
  TItemMapeamento = record
    Origem        : string; // 'Grupo de Oração' ou 'Coordenador'
    CampoSavic    : string;
    DescricaoSavic: string;
    TabelaDestino : string;
    CampoDestino  : string;
    RegraConversao: string;
  end;

  Tfrmmapeamento_savic_entidade = class(TForm)
    PanelTop: TPanel;
    lblstatus: TLabel;
    spbsalvardiretriz: TBitBtn;
    spbrestaurarpadrao: TBitBtn;
    spblimparassociacao: TBitBtn;
    spbfechar: TBitBtn;
    PanelMain: TPanel;
    GroupBoxSavic: TGroupBox;
    lblDetalheSavic: TLabel;
    rgOrigemSavic: TRadioGroup;
    lbCamposSavic: TListBox;
    GroupBoxEntidade: TGroupBox;
    lblTabelaDestino: TLabel;
    lblCampoDestino: TLabel;
    lblRegraConversao: TLabel;
    cbotabelaentidade: TComboBox;
    cbocampoentidade: TComboBox;
    cboregraconversao: TComboBox;
    btnassociar: TBitBtn;
    GroupBoxMapeamento: TGroupBox;
    gridmapeamento: TStringGrid;
    procedure FormShow(Sender: TObject);
    procedure spbfecharClick(Sender: TObject);
    procedure rgOrigemSavicClick(Sender: TObject);
    procedure lbCamposSavicClick(Sender: TObject);
    procedure cbotabelaentidadeChange(Sender: TObject);
    procedure btnassociarClick(Sender: TObject);
    procedure spblimparassociacaoClick(Sender: TObject);
    procedure spbrestaurarpadraoClick(Sender: TObject);
    procedure spbsalvardiretrizClick(Sender: TObject);
    procedure gridmapeamentoSelectCell(Sender: TObject; ACol, ARow: Integer;
      var CanSelect: Boolean);
  private
    { Private declarations }
    FListaMapeamentos: array of TItemMapeamento;
    procedure InicializarEstruturasCampos;
    procedure CarregarCamposTabelaEntidade(const ATabela: string);
    procedure AtualizarGrid;
    procedure DefinirMapeamentoPadrao;
    procedure CriarTabelaMapeamentoSeNaoExiste;
    procedure CarregarDiretrizesBancoOuJSON;
    function ObterCaminhoJSONConfig: string;
    procedure FiltrarListaCamposSavic;
  public
    { Public declarations }
  end;

var
  frmmapeamento_savic_entidade: Tfrmmapeamento_savic_entidade;

implementation

uses unt_dados, funcoes;

{$R *.dfm}

const
  TOTAL_CAMPOS_SAVIC = 34;

type
  TDefSavic = record
    Origem: string;
    Campo: string;
    Descricao: string;
    TabPadrao: string;
    CampoPadrao: string;
    RegraPadrao: string;
  end;

const
  DEFS_SAVIC: array[0..TOTAL_CAMPOS_SAVIC - 1] of TDefSavic = (
    // GRUPOS DE ORAÇÃO
    (Origem: 'Grupo de Oração'; Campo: 'goid';                Descricao: 'ID do Grupo de Oração no SAVIC';       TabPadrao: 'USER_geoapolo_gruposdeoracao'; CampoPadrao: 'gocodigo';        RegraPadrao: 'Direto'),
    (Origem: 'Grupo de Oração'; Campo: 'GrupodeOracao';       Descricao: 'Nome do Grupo de Oração';              TabPadrao: 'USER_geoapolo_entidade';       CampoPadrao: 'geoentnome';       RegraPadrao: 'Direto'),
    (Origem: 'Grupo de Oração'; Campo: 'Cidade';              Descricao: 'Cidade onde o Grupo se reúne';         TabPadrao: 'USER_geoapolo_entidade';       CampoPadrao: 'geocidcod';        RegraPadrao: 'Lookup Cidade/UF'),
    (Origem: 'Grupo de Oração'; Campo: 'Estado';              Descricao: 'Sigla da UF da Reunião';               TabPadrao: 'USER_geoapolo_entidade';       CampoPadrao: 'geocidcod';        RegraPadrao: 'Lookup Cidade/UF'),
    (Origem: 'Grupo de Oração'; Campo: 'dias_semana';         Descricao: 'Dia da Semana da Reunião';             TabPadrao: 'USER_geoapolo_gruposdeoracao'; CampoPadrao: 'godiasemana';     RegraPadrao: 'Direto'),
    (Origem: 'Grupo de Oração'; Campo: 'horario';             Descricao: 'Horário habitual da Reunião';          TabPadrao: 'USER_geoapolo_gruposdeoracao'; CampoPadrao: 'gohorario';       RegraPadrao: 'Direto'),
    (Origem: 'Grupo de Oração'; Campo: 'Situacao';            Descricao: 'Situação / Homologação do Grupo';      TabPadrao: 'USER_geoapolo_gruposdeoracao'; CampoPadrao: 'gosituacao';      RegraPadrao: 'Direto'),
    (Origem: 'Grupo de Oração'; Campo: 'CaracteristicaGrupo'; Descricao: 'Características gerais do Grupo';      TabPadrao: 'USER_geoapolo_gruposdeoracao'; CampoPadrao: 'gocaracteristica';RegraPadrao: 'Direto'),
    (Origem: 'Grupo de Oração'; Campo: 'LOCAL';               Descricao: 'Local onde o Grupo se reúne';          TabPadrao: 'USER_geoapolo_gruposdeoracao'; CampoPadrao: 'golocalreuniao';  RegraPadrao: 'Direto'),
    (Origem: 'Grupo de Oração'; Campo: 'TipoLocalReuniao';    Descricao: 'Tipo de Local (Paróquia, etc.)';       TabPadrao: 'USER_geoapolo_gruposdeoracao'; CampoPadrao: 'gotipolocalreuniao'; RegraPadrao: 'Direto'),
    (Origem: 'Grupo de Oração'; Campo: 'datainclusao_go';     Descricao: 'Data de Inclusão do Grupo no SAVIC';   TabPadrao: 'USER_geoapolo_entidade';       CampoPadrao: 'geoentdatacad';    RegraPadrao: 'Data ISO (YYYY-MM-DD)'),
    (Origem: 'Grupo de Oração'; Campo: 'dataatualizacao_go';  Descricao: 'Data da Última Atualização no SAVIC';  TabPadrao: 'USER_geoapolo_entidade';       CampoPadrao: 'geoentdesdedata';  RegraPadrao: 'Data ISO (YYYY-MM-DD)'),
    (Origem: 'Grupo de Oração'; Campo: 'dioceseId';           Descricao: 'Código da Diocese do Grupo';           TabPadrao: 'USER_geoapolo_entidade';       CampoPadrao: 'geodioceseid';     RegraPadrao: 'Direto'),

    // COORDENADOR
    (Origem: 'Coordenador';     Campo: 'cadastroid_coord';    Descricao: 'ID do Coordenador no SAVIC';           TabPadrao: 'USER_geoapolo_coordenadores_grupodeoracao'; CampoPadrao: 'coordenador_cadastroid'; RegraPadrao: 'Direto'),
    (Origem: 'Coordenador';     Campo: 'Coordenador';         Descricao: 'Nome Completo do Coordenador';         TabPadrao: 'USER_geoapolo_entidade_contato'; CampoPadrao: 'geocontatonome'; RegraPadrao: 'Direto'),
    (Origem: 'Coordenador';     Campo: 'genero_coord';        Descricao: 'Gênero / Sexo do Coordenador';         TabPadrao: 'USER_geoapolo_entidade';       CampoPadrao: 'geoentgenero';     RegraPadrao: 'Tratamento Auto (Sr./Sra./Srta.)'),
    (Origem: 'Coordenador';     Campo: 'cpf_coordenador';     Descricao: 'CPF do Coordenador';                   TabPadrao: 'USER_geoapolo_entidade_documentos'; CampoPadrao: 'geonumerodocumento'; RegraPadrao: 'CPF/CNPJ Limpo'),
    (Origem: 'Coordenador';     Campo: 'rgcoord';             Descricao: 'Número do RG do Coordenador';          TabPadrao: 'USER_geoapolo_entidade_documentos'; CampoPadrao: 'geonumerodocumento'; RegraPadrao: 'Direto'),
    (Origem: 'Coordenador';     Campo: 'rgcoordemissor';      Descricao: 'Órgão Emissor do RG';                  TabPadrao: 'USER_geoapolo_entidade_documentos'; CampoPadrao: 'geoobservacoes'; RegraPadrao: 'Direto'),
    (Origem: 'Coordenador';     Campo: 'EnderecoCoordenador'; Descricao: 'Logradouro / Endereço';                TabPadrao: 'USER_geoapolo_entidade';       CampoPadrao: 'geoentender';      RegraPadrao: 'Direto'),
    (Origem: 'Coordenador';     Campo: 'Numero_CasaCoord';    Descricao: 'Número do Imóvel do Coordenador';      TabPadrao: 'USER_geoapolo_entidade';       CampoPadrao: 'geoenderno';       RegraPadrao: 'Direto'),
    (Origem: 'Coordenador';     Campo: 'Compl_coord';         Descricao: 'Complemento do Endereço';              TabPadrao: 'USER_geoapolo_entidade';       CampoPadrao: 'geoentendercomp';  RegraPadrao: 'Direto'),
    (Origem: 'Coordenador';     Campo: 'Bairro';              Descricao: 'Bairro de Residência';                 TabPadrao: 'USER_geoapolo_entidade';       CampoPadrao: 'geoentbair';       RegraPadrao: 'Direto'),
    (Origem: 'Coordenador';     Campo: 'CepCoord';            Descricao: 'CEP de Residência';                    TabPadrao: 'USER_geoapolo_entidade';       CampoPadrao: 'geoentcep';        RegraPadrao: 'Direto'),
    (Origem: 'Coordenador';     Campo: 'CaixaPostal_Coord';   Descricao: 'Caixa Postal do Coordenador';          TabPadrao: 'USER_geoapolo_entidade';       CampoPadrao: 'geoentcxapost';    RegraPadrao: 'Direto'),
    (Origem: 'Coordenador';     Campo: 'Telefone_Coord';      Descricao: 'Telefone Fixo do Coordenador';         TabPadrao: 'USER_geoapolo_entidade_comunicacao'; CampoPadrao: 'identificacao_contato'; RegraPadrao: 'Direto'),
    (Origem: 'Coordenador';     Campo: 'TelCom_Coord';        Descricao: 'Telefone Comercial do Coordenador';    TabPadrao: 'USER_geoapolo_entidade_comunicacao'; CampoPadrao: 'identificacao_contato'; RegraPadrao: 'Direto'),
    (Origem: 'Coordenador';     Campo: 'CelularCoord1';       Descricao: 'Celular Principal do Coordenador';     TabPadrao: 'USER_geoapolo_entidade_contato'; CampoPadrao: 'geocelularcontato'; RegraPadrao: 'Direto'),
    (Origem: 'Coordenador';     Campo: 'celularcoord2';       Descricao: 'Celular Secundário do Coordenador';    TabPadrao: 'USER_geoapolo_entidade_comunicacao'; CampoPadrao: 'identificacao_contato'; RegraPadrao: 'Direto'),
    (Origem: 'Coordenador';     Campo: 'diocesecoordenador';  Descricao: 'Diocese do Coordenador';               TabPadrao: 'USER_geoapolo_entidade';       CampoPadrao: 'geodioceseid';     RegraPadrao: 'Direto'),
    (Origem: 'Coordenador';     Campo: 'email';               Descricao: 'E-mail do Coordenador';                TabPadrao: 'USER_geoapolo_entidade_webcontato'; CampoPadrao: 'email';           RegraPadrao: 'Direto'),
    (Origem: 'Coordenador';     Campo: 'MandatoIndeterminado';Descricao: 'Flag de Mandato Indeterminado';        TabPadrao: 'USER_geoapolo_coordenadores_grupodeoracao'; CampoPadrao: 'mandato_indeterminado'; RegraPadrao: 'Direto'),
    (Origem: 'Coordenador';     Campo: 'Dataini_coordenacao'; Descricao: 'Início do Mandato da Coordenação';     TabPadrao: 'USER_geoapolo_coordenadores_grupodeoracao'; CampoPadrao: 'data_inicio_mandato'; RegraPadrao: 'Data ISO (YYYY-MM-DD)'),
    (Origem: 'Coordenador';     Campo: 'datafim_coordenacao'; Descricao: 'Término do Mandato da Coordenação';    TabPadrao: 'USER_geoapolo_coordenadores_grupodeoracao'; CampoPadrao: 'data_fim_mandato';    RegraPadrao: 'Data ISO (YYYY-MM-DD)')
  );

{ Tfrmmapeamento_savic_entidade }

procedure Tfrmmapeamento_savic_entidade.FormShow(Sender: TObject);
begin
  InicializarEstruturasCampos;
  CriarTabelaMapeamentoSeNaoExiste;
  CarregarDiretrizesBancoOuJSON;
  FiltrarListaCamposSavic;
  AtualizarGrid;
end;

procedure Tfrmmapeamento_savic_entidade.InicializarEstruturasCampos;
begin
  cbotabelaentidade.Items.Clear;
  cbotabelaentidade.Items.Add('USER_geoapolo_entidade');
  cbotabelaentidade.Items.Add('USER_geoapolo_entidade_documentos');
  cbotabelaentidade.Items.Add('USER_geoapolo_entidade_comunicacao');
  cbotabelaentidade.Items.Add('USER_geoapolo_entidade_contato');
  cbotabelaentidade.Items.Add('USER_geoapolo_entidade_webcontato');
  cbotabelaentidade.Items.Add('USER_geoapolo_entcateg');
  cbotabelaentidade.Items.Add('USER_geoapolo_gruposdeoracao');
  cbotabelaentidade.Items.Add('USER_geoapolo_coordenadores_grupodeoracao');
  cbotabelaentidade.ItemIndex := 0;
  CarregarCamposTabelaEntidade(cbotabelaentidade.Text);

  // Configura grid
  gridmapeamento.ColCount := 6;
  gridmapeamento.ColWidths[0] := 110;
  gridmapeamento.ColWidths[1] := 130;
  gridmapeamento.ColWidths[2] := 190;
  gridmapeamento.ColWidths[3] := 220;
  gridmapeamento.ColWidths[4] := 140;
  gridmapeamento.ColWidths[5] := 150;

  gridmapeamento.Cells[0, 0] := 'Origem';
  gridmapeamento.Cells[1, 0] := 'Campo SAVIC';
  gridmapeamento.Cells[2, 0] := 'Descrição SAVIC';
  gridmapeamento.Cells[3, 0] := 'Tabela Destino (GeoAlvo)';
  gridmapeamento.Cells[4, 0] := 'Campo Destino';
  gridmapeamento.Cells[5, 0] := 'Regra Conversão';
end;

procedure Tfrmmapeamento_savic_entidade.CarregarCamposTabelaEntidade(const ATabela: string);
begin
  cbocampoentidade.Items.Clear;
  if SameText(ATabela, 'USER_geoapolo_entidade') then
  begin
    cbocampoentidade.Items.Add('geoentnome');
    cbocampoentidade.Items.Add('geoentnomefantasia');
    cbocampoentidade.Items.Add('tipolograd');
    cbocampoentidade.Items.Add('geoentender');
    cbocampoentidade.Items.Add('geoenderno');
    cbocampoentidade.Items.Add('geoentendercomp');
    cbocampoentidade.Items.Add('geoentbair');
    cbocampoentidade.Items.Add('geoentcep');
    cbocampoentidade.Items.Add('geocidcod');
    cbocampoentidade.Items.Add('geoentgenero');
    cbocampoentidade.Items.Add('geoentestcivil');
    cbocampoentidade.Items.Add('geoentcxapost');
    cbocampoentidade.Items.Add('geoentdatacad');
    cbocampoentidade.Items.Add('geoentdesdedata');
    cbocampoentidade.Items.Add('geoentdataanivfund');
    cbocampoentidade.Items.Add('geocargocodestr');
    cbocampoentidade.Items.Add('geodioceseid');
    cbocampoentidade.Items.Add('entobservacoes');
  end
  else if SameText(ATabela, 'USER_geoapolo_entidade_documentos') then
  begin
    cbocampoentidade.Items.Add('geotipodocumento');
    cbocampoentidade.Items.Add('geonumerodocumento');
    cbocampoentidade.Items.Add('geoobservacoes');
  end
  else if SameText(ATabela, 'USER_geoapolo_entidade_comunicacao') then
  begin
    cbocampoentidade.Items.Add('aplicativo');
    cbocampoentidade.Items.Add('meio_contato');
    cbocampoentidade.Items.Add('identificacao_contato');
    cbocampoentidade.Items.Add('observacao');
  end
  else if SameText(ATabela, 'USER_geoapolo_entidade_contato') then
  begin
    cbocampoentidade.Items.Add('geocontatonome');
    cbocampoentidade.Items.Add('geotipocontato');
    cbocampoentidade.Items.Add('geocelularcontato');
    cbocampoentidade.Items.Add('geoemailcontato');
    cbocampoentidade.Items.Add('geocpfcontato');
    cbocampoentidade.Items.Add('georgcontato');
    cbocampoentidade.Items.Add('geocargocontato');
  end
  else if SameText(ATabela, 'USER_geoapolo_entidade_webcontato') then
  begin
    cbocampoentidade.Items.Add('tipo_contato');
    cbocampoentidade.Items.Add('email');
    cbocampoentidade.Items.Add('flagemailprincipal');
    cbocampoentidade.Items.Add('website');
  end
  else if SameText(ATabela, 'USER_geoapolo_entcateg') then
  begin
    cbocampoentidade.Items.Add('categcodestr');
  end
  else if SameText(ATabela, 'USER_geoapolo_gruposdeoracao') then
  begin
    cbocampoentidade.Items.Add('gocodigo');
    cbocampoentidade.Items.Add('gonome');
    cbocampoentidade.Items.Add('godiasemana');
    cbocampoentidade.Items.Add('gohorario');
    cbocampoentidade.Items.Add('golocalreuniao');
    cbocampoentidade.Items.Add('gotipolocalreuniao');
    cbocampoentidade.Items.Add('gosituacao');
    cbocampoentidade.Items.Add('gocaracteristica');
    cbocampoentidade.Items.Add('entcod');
  end
  else if SameText(ATabela, 'USER_geoapolo_coordenadores_grupodeoracao') then
  begin
    cbocampoentidade.Items.Add('gocodigo');
    cbocampoentidade.Items.Add('coordenador_cadastroid');
    cbocampoentidade.Items.Add('nome_coordenador');
    cbocampoentidade.Items.Add('cpf_coordenador');
    cbocampoentidade.Items.Add('rg_coordenador');
    cbocampoentidade.Items.Add('genero_coordenador');
    cbocampoentidade.Items.Add('data_inicio_mandato');
    cbocampoentidade.Items.Add('data_fim_mandato');
    cbocampoentidade.Items.Add('mandato_indeterminado');
    cbocampoentidade.Items.Add('entcod');
  end;

  if cbocampoentidade.Items.Count > 0 then
    cbocampoentidade.ItemIndex := 0;
end;

procedure Tfrmmapeamento_savic_entidade.cbotabelaentidadeChange(Sender: TObject);
begin
  CarregarCamposTabelaEntidade(cbotabelaentidade.Text);
end;

procedure Tfrmmapeamento_savic_entidade.DefinirMapeamentoPadrao;
var
  i: Integer;
begin
  SetLength(FListaMapeamentos, TOTAL_CAMPOS_SAVIC);
  for i := 0 to TOTAL_CAMPOS_SAVIC - 1 do
  begin
    FListaMapeamentos[i].Origem         := DEFS_SAVIC[i].Origem;
    FListaMapeamentos[i].CampoSavic     := DEFS_SAVIC[i].Campo;
    FListaMapeamentos[i].DescricaoSavic := DEFS_SAVIC[i].Descricao;
    FListaMapeamentos[i].TabelaDestino  := DEFS_SAVIC[i].TabPadrao;
    FListaMapeamentos[i].CampoDestino   := DEFS_SAVIC[i].CampoPadrao;
    FListaMapeamentos[i].RegraConversao := DEFS_SAVIC[i].RegraPadrao;
  end;
end;

procedure Tfrmmapeamento_savic_entidade.FiltrarListaCamposSavic;
var
  i: Integer;
  FiltroOrigem: string;
begin
  lbCamposSavic.Items.Clear;
  case rgOrigemSavic.ItemIndex of
    1: FiltroOrigem := 'Grupo de Oração';
    2: FiltroOrigem := 'Coordenador';
  else
    FiltroOrigem := '';
  end;

  for i := 0 to High(FListaMapeamentos) do
  begin
    if (FiltroOrigem = '') or SameText(FListaMapeamentos[i].Origem, FiltroOrigem) then
    begin
      lbCamposSavic.Items.Add(Format('[%s] %s - %s',
        [FListaMapeamentos[i].Origem, FListaMapeamentos[i].CampoSavic, FListaMapeamentos[i].DescricaoSavic]));
    end;
  end;

  if lbCamposSavic.Items.Count > 0 then
  begin
    lbCamposSavic.ItemIndex := 0;
    lbCamposSavicClick(nil);
  end;
end;

procedure Tfrmmapeamento_savic_entidade.rgOrigemSavicClick(Sender: TObject);
begin
  FiltrarListaCamposSavic;
end;

procedure Tfrmmapeamento_savic_entidade.lbCamposSavicClick(Sender: TObject);
var
  Texto, CampoNome: string;
  PosIni, PosFim, i: Integer;
begin
  if lbCamposSavic.ItemIndex < 0 then Exit;
  Texto := lbCamposSavic.Items[lbCamposSavic.ItemIndex];
  PosIni := Pos('] ', Texto);
  if PosIni <= 0 then Exit;
  PosFim := Pos(' - ', Texto);
  if PosFim <= 0 then Exit;

  CampoNome := Copy(Texto, PosIni + 2, PosFim - (PosIni + 2));

  for i := 0 to High(FListaMapeamentos) do
  begin
    if SameText(FListaMapeamentos[i].CampoSavic, CampoNome) then
    begin
      lblDetalheSavic.Caption := Format('Campo: %s | Origem: %s'#13#10'Descrição: %s',
        [FListaMapeamentos[i].CampoSavic, FListaMapeamentos[i].Origem, FListaMapeamentos[i].DescricaoSavic]);

      // Posiciona na tabela/campo do mapeamento se configurado
      if FListaMapeamentos[i].TabelaDestino <> '' then
      begin
        cbotabelaentidade.ItemIndex := cbotabelaentidade.Items.IndexOf(FListaMapeamentos[i].TabelaDestino);
        if cbotabelaentidade.ItemIndex >= 0 then
        begin
          CarregarCamposTabelaEntidade(cbotabelaentidade.Text);
          cbocampoentidade.ItemIndex := cbocampoentidade.Items.IndexOf(FListaMapeamentos[i].CampoDestino);
        end;
      end;

      if FListaMapeamentos[i].RegraConversao <> '' then
        cboregraconversao.ItemIndex := cboregraconversao.Items.IndexOf(FListaMapeamentos[i].RegraConversao);

      // Destaca a linha no grid
      gridmapeamento.Row := i + 1;
      Break;
    end;
  end;
end;

procedure Tfrmmapeamento_savic_entidade.btnassociarClick(Sender: TObject);
var
  i, LinhaAtiva: Integer;
begin
  LinhaAtiva := gridmapeamento.Row - 1;
  if (LinhaAtiva < 0) or (LinhaAtiva > High(FListaMapeamentos)) then
  begin
    ShowMessage('Selecione uma linha no grid ou um campo SAVIC na lista à esquerda.');
    Exit;
  end;

  FListaMapeamentos[LinhaAtiva].TabelaDestino  := cbotabelaentidade.Text;
  FListaMapeamentos[LinhaAtiva].CampoDestino   := cbocampoentidade.Text;
  FListaMapeamentos[LinhaAtiva].RegraConversao := cboregraconversao.Text;

  AtualizarGrid;
  lblstatus.Caption := Format('Campo %s associado a %s.%s',
    [FListaMapeamentos[LinhaAtiva].CampoSavic, cbotabelaentidade.Text, cbocampoentidade.Text]);
  lblstatus.Font.Color := clBlue;
end;

procedure Tfrmmapeamento_savic_entidade.spblimparassociacaoClick(Sender: TObject);
var
  LinhaAtiva: Integer;
begin
  LinhaAtiva := gridmapeamento.Row - 1;
  if (LinhaAtiva >= 0) and (LinhaAtiva <= High(FListaMapeamentos)) then
  begin
    FListaMapeamentos[LinhaAtiva].TabelaDestino  := '';
    FListaMapeamentos[LinhaAtiva].CampoDestino   := '';
    FListaMapeamentos[LinhaAtiva].RegraConversao := 'Direto';
    AtualizarGrid;
    lblstatus.Caption := 'Associação removida para a linha selecionada.';
    lblstatus.Font.Color := clMaroon;
  end;
end;

procedure Tfrmmapeamento_savic_entidade.spbrestaurarpadraoClick(Sender: TObject);
begin
  if MessageDlg('Deseja restaurar todas as diretrizes para o mapeamento padrão?',
                mtConfirmation, [mbYes, mbNo], 0) = mrYes then
  begin
    DefinirMapeamentoPadrao;
    AtualizarGrid;
    FiltrarListaCamposSavic;
    lblstatus.Caption := 'Diretrizes padrão restauradas.';
    lblstatus.Font.Color := clGreen;
  end;
end;

procedure Tfrmmapeamento_savic_entidade.AtualizarGrid;
var
  i: Integer;
begin
  gridmapeamento.RowCount := Length(FListaMapeamentos) + 1;
  for i := 0 to High(FListaMapeamentos) do
  begin
    gridmapeamento.Cells[0, i + 1] := FListaMapeamentos[i].Origem;
    gridmapeamento.Cells[1, i + 1] := FListaMapeamentos[i].CampoSavic;
    gridmapeamento.Cells[2, i + 1] := FListaMapeamentos[i].DescricaoSavic;
    gridmapeamento.Cells[3, i + 1] := FListaMapeamentos[i].TabelaDestino;
    gridmapeamento.Cells[4, i + 1] := FListaMapeamentos[i].CampoDestino;
    gridmapeamento.Cells[5, i + 1] := FListaMapeamentos[i].RegraConversao;
  end;
end;

procedure Tfrmmapeamento_savic_entidade.gridmapeamentoSelectCell(Sender: TObject;
  ACol, ARow: Integer; var CanSelect: Boolean);
var
  Idx: Integer;
begin
  Idx := ARow - 1;
  if (Idx >= 0) and (Idx <= High(FListaMapeamentos)) then
  begin
    lblDetalheSavic.Caption := Format('Campo: %s | Origem: %s'#13#10'Descrição: %s',
      [FListaMapeamentos[Idx].CampoSavic, FListaMapeamentos[Idx].Origem, FListaMapeamentos[Idx].DescricaoSavic]);

    if FListaMapeamentos[Idx].TabelaDestino <> '' then
    begin
      cbotabelaentidade.ItemIndex := cbotabelaentidade.Items.IndexOf(FListaMapeamentos[Idx].TabelaDestino);
      if cbotabelaentidade.ItemIndex >= 0 then
      begin
        CarregarCamposTabelaEntidade(cbotabelaentidade.Text);
        cbocampoentidade.ItemIndex := cbocampoentidade.Items.IndexOf(FListaMapeamentos[Idx].CampoDestino);
      end;
    end;

    if FListaMapeamentos[Idx].RegraConversao <> '' then
      cboregraconversao.ItemIndex := cboregraconversao.Items.IndexOf(FListaMapeamentos[Idx].RegraConversao);
  end;
end;

function Tfrmmapeamento_savic_entidade.ObterCaminhoJSONConfig: string;
begin
  Result := IncludeTrailingPathDelimiter(ExtractFilePath(Application.ExeName)) +
            'config_mapeamento_savic_entidade.json';
end;

procedure Tfrmmapeamento_savic_entidade.CriarTabelaMapeamentoSeNaoExiste;
var
  sSql: string;
begin
  if not Assigned(modulo_dados) or not Assigned(modulo_dados.fdbanco) or not modulo_dados.fdbanco.Connected then
    Exit;

  sSql :=
    'IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = ''USER_geoapolo_mapeamento_savic'') ' +
    'BEGIN ' +
    '  CREATE TABLE USER_geoapolo_mapeamento_savic ( ' +
    '    id INT IDENTITY(1,1) PRIMARY KEY, ' +
    '    origem VARCHAR(30) NOT NULL, ' +
    '    campo_savic VARCHAR(60) NOT NULL, ' +
    '    descricao_savic VARCHAR(150) NULL, ' +
    '    tabela_destino VARCHAR(80) NULL, ' +
    '    campo_destino VARCHAR(60) NULL, ' +
    '    regra_conversao VARCHAR(60) NULL, ' +
    '    data_atualizacao DATETIME DEFAULT GETDATE(), ' +
    '    CONSTRAINT UQ_savic_origem_campo UNIQUE (origem, campo_savic) ' +
    '  ); ' +
    'END';
  try
    modulo_dados.fdbanco.ExecSQL(sSql);
  except
  end;
end;

procedure Tfrmmapeamento_savic_entidade.CarregarDiretrizesBancoOuJSON;
var
  Qry: TFDQuery;
  i: Integer;
  JaCarregouBanco: Boolean;
  CaminhoJSON, Conteudo: string;
  JsonArray: TJSONArray;
  JsonObj: TJSONObject;
begin
  DefinirMapeamentoPadrao;
  JaCarregouBanco := False;

  if Assigned(modulo_dados) and Assigned(modulo_dados.fdbanco) and modulo_dados.fdbanco.Connected then
  begin
    Qry := TFDQuery.Create(nil);
    try
      Qry.Connection := modulo_dados.fdbanco;
      Qry.SQL.Text := 'SELECT origem, campo_savic, descricao_savic, tabela_destino, campo_destino, regra_conversao ' +
                      'FROM USER_geoapolo_mapeamento_savic WITH (NOLOCK)';
      try
        Qry.Open;
        if not Qry.IsEmpty then
        begin
          while not Qry.Eof do
          begin
            for i := 0 to High(FListaMapeamentos) do
            begin
              if SameText(FListaMapeamentos[i].CampoSavic, Qry.FieldByName('campo_savic').AsString) and
                 SameText(FListaMapeamentos[i].Origem, Qry.FieldByName('origem').AsString) then
              begin
                FListaMapeamentos[i].TabelaDestino  := Qry.FieldByName('tabela_destino').AsString;
                FListaMapeamentos[i].CampoDestino   := Qry.FieldByName('campo_destino').AsString;
                FListaMapeamentos[i].RegraConversao := Qry.FieldByName('regra_conversao').AsString;
                Break;
              end;
            end;
            Qry.Next;
          end;
          JaCarregouBanco := True;
        end;
      except
      end;
    finally
      Qry.Free;
    end;
  end;

  if not JaCarregouBanco then
  begin
    CaminhoJSON := ObterCaminhoJSONConfig;
    if FileExists(CaminhoJSON) then
    begin
      try
        Conteudo := TFile.ReadAllText(CaminhoJSON, TEncoding.UTF8);
        JsonArray := TJSONObject.ParseJSONValue(Conteudo) as TJSONArray;
        if Assigned(JsonArray) then
        try
          for i := 0 to JsonArray.Count - 1 do
          begin
            JsonObj := JsonArray.Items[i] as TJSONObject;
            if Assigned(JsonObj) then
            begin
              for var k := 0 to High(FListaMapeamentos) do
              begin
                if SameText(FListaMapeamentos[k].CampoSavic, JsonObj.GetValue<string>('campo_savic', '')) and
                   SameText(FListaMapeamentos[k].Origem, JsonObj.GetValue<string>('origem', '')) then
                begin
                  FListaMapeamentos[k].TabelaDestino  := JsonObj.GetValue<string>('tabela_destino', '');
                  FListaMapeamentos[k].CampoDestino   := JsonObj.GetValue<string>('campo_destino', '');
                  FListaMapeamentos[k].RegraConversao := JsonObj.GetValue<string>('regra_conversao', 'Direto');
                  Break;
                end;
              end;
            end;
          end;
        finally
          JsonArray.Free;
        end;
      except
      end;
    end;
  end;
end;

procedure Tfrmmapeamento_savic_entidade.spbsalvardiretrizClick(Sender: TObject);
var
  i: Integer;
  sSql: string;
  Qry: TFDQuery;
  JsonArray: TJSONArray;
  JsonObj: TJSONObject;
  CaminhoJSON: string;
begin
  Screen.Cursor := crHourGlass;
  try
    CriarTabelaMapeamentoSeNaoExiste;

    // 1. Grava no SQL Server
    if Assigned(modulo_dados) and Assigned(modulo_dados.fdbanco) and modulo_dados.fdbanco.Connected then
    begin
      Qry := TFDQuery.Create(nil);
      try
        Qry.Connection := modulo_dados.fdbanco;
        for i := 0 to High(FListaMapeamentos) do
        begin
          sSql :=
            'IF EXISTS (SELECT 1 FROM USER_geoapolo_mapeamento_savic WHERE origem = :origem AND campo_savic = :campo_savic) ' +
            'BEGIN ' +
            '  UPDATE USER_geoapolo_mapeamento_savic ' +
            '  SET tabela_destino = :tabela_destino, campo_destino = :campo_destino, ' +
            '      regra_conversao = :regra_conversao, data_atualizacao = GETDATE() ' +
            '  WHERE origem = :origem AND campo_savic = :campo_savic; ' +
            'END ' +
            'ELSE ' +
            'BEGIN ' +
            '  INSERT INTO USER_geoapolo_mapeamento_savic ' +
            '    (origem, campo_savic, descricao_savic, tabela_destino, campo_destino, regra_conversao) ' +
            '  VALUES (:origem, :campo_savic, :descricao_savic, :tabela_destino, :campo_destino, :regra_conversao); ' +
            'END';

          Qry.Close;
          Qry.SQL.Text := sSql;
          Qry.ParamByName('origem').AsString          := FListaMapeamentos[i].Origem;
          Qry.ParamByName('campo_savic').AsString      := FListaMapeamentos[i].CampoSavic;
          Qry.ParamByName('descricao_savic').AsString  := FListaMapeamentos[i].DescricaoSavic;
          Qry.ParamByName('tabela_destino').AsString   := FListaMapeamentos[i].TabelaDestino;
          Qry.ParamByName('campo_destino').AsString    := FListaMapeamentos[i].CampoDestino;
          Qry.ParamByName('regra_conversao').AsString  := FListaMapeamentos[i].RegraConversao;
          Qry.ExecSQL;
        end;
      finally
        Qry.Free;
      end;
    end;

    // 2. Grava em JSON local como diretriz portátil
    JsonArray := TJSONArray.Create;
    try
      for i := 0 to High(FListaMapeamentos) do
      begin
        JsonObj := TJSONObject.Create;
        JsonObj.AddPair('origem',          FListaMapeamentos[i].Origem);
        JsonObj.AddPair('campo_savic',      FListaMapeamentos[i].CampoSavic);
        JsonObj.AddPair('descricao_savic',  FListaMapeamentos[i].DescricaoSavic);
        JsonObj.AddPair('tabela_destino',   FListaMapeamentos[i].TabelaDestino);
        JsonObj.AddPair('campo_destino',    FListaMapeamentos[i].CampoDestino);
        JsonObj.AddPair('regra_conversao',  FListaMapeamentos[i].RegraConversao);
        JsonArray.AddElement(JsonObj);
      end;
      CaminhoJSON := ObterCaminhoJSONConfig;
      TFile.WriteAllText(CaminhoJSON, JsonArray.Format(2), TEncoding.UTF8);
    finally
      JsonArray.Free;
    end;

    lblstatus.Caption := 'Diretrizes gravadas com sucesso no Banco de Dados e em JSON!';
    lblstatus.Font.Color := clGreen;
    MessageDlg('Diretrizes de Mapeamento SAVIC x Entidade gravadas com sucesso!'#13#10 +
               'Elas serão utilizadas como diretriz padrão para os próximos processos de importação.',
               mtInformation, [mbOK], 0);
  finally
    Screen.Cursor := crDefault;
  end;
end;

procedure Tfrmmapeamento_savic_entidade.spbfecharClick(Sender: TObject);
begin
  Close;
end;

end.
