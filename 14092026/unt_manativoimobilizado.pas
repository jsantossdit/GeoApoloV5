unit unt_manativoimobilizado;

interface

uses
  Winapi.Windows, Winapi.Messages,
  System.SysUtils, System.Variants, System.Classes,
  Vcl.Graphics, Vcl.Controls, Vcl.Forms, Vcl.Dialogs,
  Vcl.StdCtrls, Vcl.Buttons, Vcl.ExtCtrls, Vcl.Imaging.jpeg,
  Vcl.ComCtrls, Vcl.Grids, Vcl.DBGrids, Vcl.Menus,
  Data.DB;

type
  Tfrmmanativofixo = class(TForm)
    panelmenu        : TPanel;
    spbsalvar        : TSpeedButton;
    spblimpar        : TSpeedButton;
    spbdeletar       : TSpeedButton;
    spbexibedepreciacao: TSpeedButton;
    spbsair          : TSpeedButton;
    lblmsg1          : TLabel;
    GroupBox1        : TGroupBox;
    lblcodigodobem          : TLabeledEdit;
    lbldescricaodobem       : TLabeledEdit;
    lblcctrlcodestr         : TLabeledEdit;
    lblcctrlnome            : TLabel;
    spbuscabem              : TSpeedButton;
    spbcctrlcodestr         : TSpeedButton;
    lbllocalizacaofisica    : TLabeledEdit;
    spbuscalocalizacao      : TSpeedButton;
    lbldescricaolocalizacao : TLabel;
    lblcodfuncresponsavel   : TLabeledEdit;
    spbuscafuncresp         : TSpeedButton;
    lblnomefuncresponsavel  : TLabel;
    gridativoimobilizado    : TDBGrid;
    StatusBar1              : TStatusBar;
    lblplaquetapatrimonio   : TLabeledEdit;
    lblclassificacaobem     : TLabeledEdit;
    spbuscaclassifibem      : TSpeedButton;
    lblnomeclassificacaobem : TLabel;
    lblcategbem             : TLabeledEdit;
    spbcategoriabem         : TSpeedButton;
    lblcategbemnome         : TLabel;
    PopupMenu               : TPopupMenu;
    popmnugravaconfig       : TMenuItem;
    lblcodmarcaproduto      : TLabeledEdit;
    spbuscamarca            : TSpeedButton;
    lblnomedamarca          : TLabel;
    lblnumeroserie          : TLabeledEdit;
    lblstatusdobem          : TLabeledEdit;
    spbuscastatus           : TSpeedButton;
    lblnomestatusdobem      : TLabel;
    lblempcod               : TLabeledEdit;
    lblempnome              : TLabel;

    // ── NOVOS COMPONENTES — DEPRECIAÇÃO ──────────────────────────────────
    // (adicionar no .dfm dentro do GroupBox1 ou em um GroupBox2 separado)
    GroupBox2               : TGroupBox;
    lbldataaquisicao        : TLabeledEdit;     // EditLabel = 'Data de Compra'
    lblvalorcompra          : TLabeledEdit;
    lbltaxadepanual         : TLabeledEdit;    // EditLabel = 'Taxa Dep. Anual (%)'
    lbldataultimarevisao    : TLabeledEdit;    // EditLabel = 'Última Revisão'
    lblcaminhofoto          : TLabeledEdit;           // 'Observações'
    // Resultados calculados (somente leitura — não gravam no BD)
    lblvaloratialdep        : TLabel;          // 'Valor Atual: R$ ...'
    lbldepacumulada         : TLabel;          // 'Dep. Acumulada: R$ ...'
    lblanosusodep           : TLabel;          // 'Anos em Uso: ...'
    spbcalculardepreciacao  : TSpeedButton;
    memoobservacoes: TMemo;
    lblobservacoes: TLabel;
    SpeedButton1: TSpeedButton;
    opendialog: TOpenDialog;
    GroupBox3: TGroupBox;




    // ─────────────────────────────────────────────────────────────────────

    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormActivate(Sender: TObject);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);

    { Navegação / validação inline }
    procedure lblcctrlcodestrEnter(Sender: TObject);
    procedure lblcctrlcodestrKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblcategbemEnter(Sender: TObject);
    procedure lblcategbemKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lbldescricaodobemEnter(Sender: TObject);
    procedure lbldescricaodobemKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblclassificacaobemEnter(Sender: TObject);
    procedure lblclassificacaobemKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblplaquetapatrimonioEnter(Sender: TObject);
    procedure lblplaquetapatrimonioKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblnumeroserieKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblcodmarcaprodutoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lbllocalizacaofisicaEnter(Sender: TObject);
    procedure lbllocalizacaofisicaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblcodfuncresponsavelEnter(Sender: TObject);
    procedure lblcodfuncresponsavelKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblstatusdobemEnter(Sender: TObject);
    procedure lblstatusdobemKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);

    { Botões de ação }
    procedure spbsairClick(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure spbsalvarClick(Sender: TObject);

    { Botões de lookup (F4) }
    procedure spbcctrlcodestrClick(Sender: TObject);
    procedure spbcategoriabemClick(Sender: TObject);
    procedure spbuscaclassifibemClick(Sender: TObject);
    procedure spbuscabemClick(Sender: TObject);
    procedure spbuscalocalizacaoClick(Sender: TObject);
    procedure spbuscafuncrespClick(Sender: TObject);
    procedure spbuscamarcaClick(Sender: TObject);
    procedure spbuscastatusClick(Sender: TObject);

    { Grid }
    procedure gridativoimobilizadoDblClick(Sender: TObject);
    procedure gridativoimobilizadoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);

    { Menu }
    procedure popmnugravaconfigClick(Sender: TObject);

    { Depreciação }
    procedure spbcalculardepreciacaoClick(Sender: TObject);
    procedure lbldataaquisicaoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblvalorcompraKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lbldataultimarevisaoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lbltaxadepanualKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblcaminhofotoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure memoobservacoesKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbexibedepreciacaoClick(Sender: TObject);
    procedure SpeedButton1Click(Sender: TObject);
    procedure spbexibedepreciacaoMouseDown(Sender: TObject;
      Button: TMouseButton; Shift: TShiftState; X, Y: Integer);
    procedure spbcalculardepreciacaoMouseDown(Sender: TObject;
      Button: TMouseButton; Shift: TShiftState; X, Y: Integer);

  private
    FControle : string;   // 'INCLUSÃO' | 'ALTERAÇÃO'

    { Helpers internos }
    procedure CarregarRegistroDoGrid;
    procedure LimparFormulario;
    procedure AtualizarGrid;

    { Resolvedores de descrição lazy (Enter nos campos) }
    procedure ResolverEmpresa;
    procedure ResolverCentroControle;
    procedure ResolverCategoria;
    procedure ResolverClassificacao;
    procedure ResolverLocalizacao;
    procedure ResolverFuncResponsavel;
    procedure ResolverMarca;
    procedure ResolverStatus;

    { Lookup genérico via TFrmConsulta4 }
    procedure AbrirConsulta(
      const ASQL          : string;
      const ACampoCodigo  : string;
      const ACampoDescr   : string;
      const ATitulo       : string;
      out   ACodigo       : string;
      out   ADescricao    : string
    );

    { Depreciação }
    procedure ExibirDepreciacao;

  public
    resp     : Word;
    controle : string;
  end;

var
  frmmanativofixo: Tfrmmanativofixo;

function mostrabensimobilizados: string; export;

implementation

{$R *.dfm}

uses
  funcoes, unt_principal, unt_dados,
  unt_consultas4, unt_logon;

{ ══════════════════════════════════════════════════════════════════════════
  HELPER GENÉRICO DE LOOKUP
  ══════════════════════════════════════════════════════════════════════════ }

procedure Tfrmmanativofixo.AbrirConsulta(
  const ASQL         : string;
  const ACampoCodigo : string;
  const ACampoDescr  : string;
  const ATitulo      : string;
  out   ACodigo      : string;
  out   ADescricao   : string
);
var
  frm : TFrmConsulta4;
begin
  ACodigo    := '';
  ADescricao := '';

  with modulo_dados do
  begin
    sql := ASQL;
    fdquerysql6.close;
    fdquerysql6.sql.clear;
    fdquerysql6.sql.text := sql;
    if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
    begin
    end;

    if fdquerysql6.IsEmpty then
    begin
      MessageDlg('Nenhum registro encontrado.', mtInformation, [mbOK], 0);
      Exit;
    end;

    frm := TFrmConsulta4.Create(Self);
    try
      frm.Titulo := ATitulo;
      frm.PopularGrid(fdquerysql6, ACampoCodigo, ACampoDescr);

      if frm.ShowModal = mrOK then
      begin
        ACodigo    := frm.CodigoSelecionado;
        ADescricao := frm.DescricaoSelecionada;
      end;
    finally
      frm.Free;
    end;
  end;
end;

{ ══════════════════════════════════════════════════════════════════════════
  FORM
  ══════════════════════════════════════════════════════════════════════════ }

procedure Tfrmmanativofixo.FormActivate(Sender: TObject);
begin
  StatusBar1.Panels[1].Text := configura_statusbar('a');
  StatusBar1.Panels[3].Text := configura_statusbar('a');
  StatusBar1.Panels[5].Text := frmprincipal.nomeserversql;
  StatusBar1.Refresh;

  configura_grid('GEOATIVOFIXO', frmmanativofixo, frmlogon.nomeusuario,
    'gridativoimobilizado', gridativoimobilizado, modulo_dados.dtsfdquerysql4);

  lblcodigodobem.Text := geoapolo_configcod(frmprincipal.codigo_empresa,
    'USER_geoapolo_satfi_ativoimobilizado', 'Sim');

  lblempcod.Text     := frmprincipal.codigo_empresa;
  lblempnome.Caption := frmprincipal.nome_empresa;
  lblempcod.Refresh;
  lblempnome.Refresh;

  FControle := 'INCLUSÃO';
  controle  := FControle;

  AtualizarGrid;
  lblempcod.SetFocus;
end;

procedure Tfrmmanativofixo.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Action := caFree;
end;

procedure Tfrmmanativofixo.FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F10 then
    spbsair.Click;
end;

{ ══════════════════════════════════════════════════════════════════════════
  GRID
  ══════════════════════════════════════════════════════════════════════════ }

procedure Tfrmmanativofixo.CarregarRegistroDoGrid;
begin
  with modulo_dados.fdquerysql4 do
  begin
    lblcodigodobem.Text             := FieldByName('numero_do_bem').AsString;
    lblempcod.Text                  := FieldByName('empcod').AsString;
    lblcctrlcodestr.Text            := FieldByName('geocctrlcodestr').AsString;
    lblcctrlnome.Caption            := FieldByName('geocctrlnome').AsString;
    lbldescricaodobem.Text          := FieldByName('descricao_do_bem').AsString;
    lblcategbem.Text                := FieldByName('codigo_categoria_bem').AsString;
    lblcategbemnome.Caption         := FieldByName('categoria_bem').AsString;
    lblclassificacaobem.Text        := FieldByName('codigo_classificacaoativoimobilizado').AsString;
    lblnomeclassificacaobem.Caption := FieldByName('classificacao').AsString;
    lblplaquetapatrimonio.Text      := FieldByName('codigo_barrasativo').AsString;
    lbllocalizacaofisica.Text       := FieldByName('codigo_localizacao').AsString;
    lbldescricaolocalizacao.Caption := FieldByName('localizacao').AsString;
    lblcodmarcaproduto.Text         := FieldByName('codigo_da_marca').AsString;
    lblnomedamarca.Caption          := FieldByName('marca').AsString;
    lblcodfuncresponsavel.Text      := FieldByName('codigo_func_responsavel').AsString;
    lblnomefuncresponsavel.Caption  := FieldByName('nome_completo').AsString;
    lblstatusdobem.Text             := FieldByName('codigo_status_bem').AsString;
    lblnomestatusdobem.Caption      := FieldByName('descricao_status_bem').AsString;

    // ── NOVOS CAMPOS — DEPRECIAÇÃO ────────────────────────────────────────
    //lbldataaquisicao.Text     := FieldByName('data_aquisicao').AsString;
    lbldataaquisicao.text     := FormatDateTime('dd/mm/yyyy', FieldByName('data_aquisicao').AsDateTime);
    lblvalorcompra.Text       := FieldByName('valor_compra').AsString;
    lbltaxadepanual.Text      := FieldByName('taxa_depreciacao_anual').AsString;
    //lbldataultimarevisao.Text := FieldByName('data_ultima_revisao').AsString;
    lbldataultimarevisao.text := FormatDateTime('dd/mm/yyyy',FieldByName('data_ultima_revisao').AsDateTime);
    lblcaminhofoto.Text       := FieldByName('caminho_foto').AsString;
    memoobservacoes.Text      := FieldByName('observacoes').AsString;
    // Recalcula e exibe resultado logo ao abrir o registro
    ExibirDepreciacao;
    // ─────────────────────────────────────────────────────────────────────
  end;

  GroupBox1.Refresh;
  GroupBox2.Refresh;

  FControle := 'ALTERAÇÃO';
  controle  := FControle;

  lblcctrlcodestr.SetFocus;
end;

procedure Tfrmmanativofixo.gridativoimobilizadoDblClick(Sender: TObject);
begin
  CarregarRegistroDoGrid;
end;

procedure Tfrmmanativofixo.gridativoimobilizadoKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
var
  codBem : string;
begin
  if Key <> VK_DELETE then
    Exit;

  with modulo_dados do
  begin
    codBem := fdquerysql4.FieldByName('numero_do_bem').AsString;

    resp := MessageDlg(
      'Confirma a Exclusão deste Bem de Ativo Fixo Imobilizado? (Y/N)',
      mtConfirmation, [mbYes, mbNo], 0);

    if resp <> idYes then
      Exit;

    sql := 'DELETE FROM USER_geoapolo_satfi_ativoimobilizado' +
           ' WHERE numero_do_bem = :codBem';
    fdquerysql3.close;
    fdquerysql3.sql.clear;
    fdquerysql3.sql.text := sql;
    fdquerysql3.parambyname('codBem').asstring := codBem;

    if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
    begin
      MessageDlg('BEM DE ATIVO IMOBILIZADO REMOVIDO COM SUCESSO!',
        mtInformation, [mbOK], 0);
      gravalog(frmlogon.codigousuario, DateToStr(Date),
        'REMOVEU COM SUCESSO O BEM ' + codBem);
      AtualizarGrid;
    end
    else
      MessageDlg('ERRO AO TENTAR REMOVER O BEM, VERIFIQUE!', mtError, [mbOK], 0);

    lblcctrlcodestr.SetFocus;
  end;
end;

{ ══════════════════════════════════════════════════════════════════════════
  SALVAR / LIMPAR / SAIR
  ══════════════════════════════════════════════════════════════════════════ }

procedure Tfrmmanativofixo.spbsalvarClick(Sender: TObject);
begin
  with modulo_dados do
  begin
    resp := MessageDlg('Confirma a ' + FControle + ' deste Bem? (Y/N)',
      mtConfirmation, [mbYes, mbNo], 0);

    if resp <> idYes then
      Exit;

    if FControle = 'INCLUSÃO' then
    begin
      sql :=
        'INSERT INTO USER_geoapolo_satfi_ativoimobilizado' +
        ' (numero_do_bem, descricao_do_bem, geocctrlcodestr,' +
        '  codigo_barrasativo, codigo_categoria_bem,' +
        '  codigo_classificacaoativoimobilizado, codigo_localizacao,' +
        '  codigo_func_responsavel, codigo_da_marca, empcod, codigo_status_bem,' +
        // ── NOVOS CAMPOS ──
        '  data_aquisicao, valor_compra, taxa_depreciacao_anual,' +
        '  data_ultima_revisao, caminho_foto, observacoes)' +
        // ──────────────────
        ' VALUES (:codbem, :descricaobem, :cctrlcodestr, :plaquetapatrimonio,' +
        ' :categbem, :classificacaobem, :localizacaofisica, :codfuncresp,' +
        ' :codigomarca, :empresa, :statusdobem,' +
        // ── NOVOS PARAMS ──
        ' :dataaquisicao, :valorcompra, :taxadepanual,' +
        ' :dataultimarevisao, :caminhofoto, :observacoes)';
        // ──────────────────

      fdquerysql3.close;
      fdquerysql3.sql.clear;
      fdquerysql3.sql.text := sql;
      fdquerysql3.parambyname('codbem').asstring           := lblcodigodobem.Text;
      fdquerysql3.parambyname('descricaobem').asstring     := lbldescricaodobem.Text;
      fdquerysql3.parambyname('cctrlcodestr').asstring     := lblcctrlcodestr.Text;
      fdquerysql3.parambyname('plaquetapatrimonio').asstring := lblplaquetapatrimonio.Text;
      fdquerysql3.parambyname('categbem').asstring         := lblcategbem.Text;
      fdquerysql3.parambyname('classificacaobem').asstring := lblclassificacaobem.Text;
      fdquerysql3.parambyname('localizacaofisica').asstring := lbllocalizacaofisica.Text;
      fdquerysql3.parambyname('codfuncresp').asstring      := lblcodfuncresponsavel.Text;
      fdquerysql3.parambyname('codigomarca').asstring      := lblcodmarcaproduto.Text;
      fdquerysql3.parambyname('empresa').asstring          := lblempcod.Text;
      fdquerysql3.parambyname('statusdobem').asstring      := lblstatusdobem.Text;
      // ── NOVOS PARAMS — DEPRECIAÇÃO ────────────────────────────────────
      if lbldataaquisicao.Text <> '' then
        fdquerysql3.parambyname('dataaquisicao').asdate :=
          StrToDateDef(lbldataaquisicao.Text, 0)
      else
        fdquerysql3.parambyname('dataaquisicao').Clear;  // grava NULL

      if lblvalorcompra.Text <> '' then
        fdquerysql3.parambyname('valorcompra').asfloat :=
          StrToFloatDef(lblvalorcompra.Text, 0)
      else
        fdquerysql3.parambyname('valorcompra').Clear;

      if lbltaxadepanual.Text <> '' then
        fdquerysql3.parambyname('taxadepanual').asfloat :=
          StrToFloatDef(lbltaxadepanual.Text, 0)
      else
        fdquerysql3.parambyname('taxadepanual').Clear;

      if lbldataultimarevisao.Text <> '' then
        fdquerysql3.parambyname('dataultimarevisao').asdate :=
          StrToDateDef(lbldataultimarevisao.Text, 0)
      else
        fdquerysql3.parambyname('dataultimarevisao').Clear;

      fdquerysql3.parambyname('caminhofoto').asstring  := lblcaminhofoto.Text;
      fdquerysql3.parambyname('observacoes').asstring  := memoobservacoes.Text;
      // ─────────────────────────────────────────────────────────────────
    end
    else // ALTERAÇÃO
    begin
      sql :=
        'UPDATE USER_geoapolo_satfi_ativoimobilizado SET ' +
        '  descricao_do_bem                     = :descricaobem, ' +
        '  geocctrlcodestr                      = :cctrlcodestr, ' +
        '  codigo_barrasativo                   = :plaquetapatrimonio, ' +
        '  codigo_categoria_bem                 = :categbem, ' +
        '  codigo_classificacaoativoimobilizado = :classificacaobem, ' +
        '  codigo_localizacao                   = :localizacaofisica, ';

      if lblcodfuncresponsavel.Text = '' then
        sql := sql + '  codigo_func_responsavel = null, '
      else
        sql := sql + '  codigo_func_responsavel = :codfuncresp, ';

      sql := sql +
        '  codigo_da_marca      = :codigomarca, ' +
        '  empcod               = :empcod, ' +
        '  codigo_status_bem    = :statusdobem, ' +
        // ── NOVOS CAMPOS — DEPRECIAÇÃO ─────────────────────────────────
        '  data_aquisicao       = :dataaquisicao, ' +
        '  valor_compra         = :valorcompra, ' +
        '  taxa_depreciacao_anual = :taxadepanual, ' +
        '  data_ultima_revisao  = :dataultimarevisao, ' +
        '  caminho_foto         = :caminhofoto, ' +
        '  observacoes          = :observacoes ' +
        // ──────────────────────────────────────────────────────────────
        ' WHERE numero_do_bem = :numerodobem';

      fdquerysql3.close;
      fdquerysql3.sql.clear;
      fdquerysql3.sql.text := sql;
      fdquerysql3.parambyname('descricaobem').asstring     := lbldescricaodobem.Text;
      fdquerysql3.parambyname('cctrlcodestr').asstring     := lblcctrlcodestr.Text;
      fdquerysql3.parambyname('plaquetapatrimonio').asstring := lblplaquetapatrimonio.Text;
      fdquerysql3.parambyname('categbem').asstring         := lblcategbem.Text;
      fdquerysql3.parambyname('classificacaobem').asstring := lblclassificacaobem.Text;
      fdquerysql3.parambyname('localizacaofisica').asstring := lbllocalizacaofisica.Text;
      if lblcodfuncresponsavel.Text <> '' then
        fdquerysql3.parambyname('codfuncresp').asstring := lblcodfuncresponsavel.Text;
      fdquerysql3.parambyname('codigomarca').asstring      := lblcodmarcaproduto.Text;
      fdquerysql3.parambyname('empcod').asstring           := lblempcod.Text;
      fdquerysql3.parambyname('statusdobem').asstring      := lblstatusdobem.Text;
      fdquerysql3.parambyname('numerodobem').asstring      := lblcodigodobem.Text;
      // ── NOVOS PARAMS — DEPRECIAÇÃO ────────────────────────────────────
      if lbldataaquisicao.Text <> '' then
        fdquerysql3.parambyname('dataaquisicao').asdate :=
          StrToDateDef(lbldataaquisicao.Text, 0)
      else
        fdquerysql3.parambyname('dataaquisicao').Clear;

      if lblvalorcompra.Text <> '' then
        fdquerysql3.parambyname('valorcompra').asfloat :=
          StrToFloatDef(lblvalorcompra.Text, 0)
      else
        fdquerysql3.parambyname('valorcompra').Clear;

      if lbltaxadepanual.Text <> '' then
        fdquerysql3.parambyname('taxadepanual').asfloat :=
          StrToFloatDef(lbltaxadepanual.Text, 0)
      else
        fdquerysql3.parambyname('taxadepanual').Clear;

      if lbldataultimarevisao.Text <> '' then
        fdquerysql3.parambyname('dataultimarevisao').asdate :=
          StrToDateDef(lbldataultimarevisao.Text, 0)
      else
        fdquerysql3.parambyname('dataultimarevisao').Clear;

      fdquerysql3.parambyname('caminhofoto').asstring  := lblcaminhofoto.Text;
      fdquerysql3.parambyname('observacoes').asstring  := memoobservacoes.Text;
      // ─────────────────────────────────────────────────────────────────
    end;

    if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
    begin
      MessageDlg('A OPERAÇÃO DE ' + FControle + ' FOI CONCLUÍDA COM SUCESSO!',
        mtInformation, [mbOK], 0);
      LimparFormulario;
      AtualizarGrid;

      if FControle = 'INCLUSÃO' then
        lblcodigodobem.Text := geoapolo_configcod(frmprincipal.codigo_empresa,
          'USER_geoapolo_satfi_ativoimobilizado', 'Sim')
      else
        lblcodigodobem.Text := geoapolo_configcod(frmprincipal.codigo_empresa,
          'USER_geoapolo_satfi_ativoimobilizado', 'Não');

      FControle := 'INCLUSÃO';
      controle  := FControle;
      lblcodigodobem.Refresh;
    end
    else
    begin
      MessageDlg('ERRO AO TENTAR A ALTERAÇÃO!', mtError, [mbOK], 0);
      LimparFormulario;
      lblcctrlcodestr.SetFocus;
    end;
  end;
end;

procedure Tfrmmanativofixo.LimparFormulario;
begin
  lblcctrlcodestr.Clear;       lblcctrlnome.Caption            := '...';
  lblcategbem.Clear;           lblcategbemnome.Caption         := '...';
  lbldescricaodobem.Clear;
  lblclassificacaobem.Clear;   lblnomeclassificacaobem.Caption := '...';
  lblplaquetapatrimonio.Clear;
  lbllocalizacaofisica.Clear;  lbldescricaolocalizacao.Caption := '...';
  lblcodfuncresponsavel.Clear; lblnomefuncresponsavel.Caption  := '...';
  lblcodmarcaproduto.Clear;    lblnomedamarca.Caption          := '...';
  lblnumeroserie.Clear;
  lblstatusdobem.Clear;        lblnomestatusdobem.Caption      := '...';
  lblempcod.Clear;             lblempnome.Caption              := '...';

  // ── NOVOS CAMPOS — DEPRECIAÇÃO ────────────────────────────────────────
  lbldataaquisicao.Clear;
  lblvalorcompra.Clear;
  lbltaxadepanual.Clear;
  lbldataultimarevisao.Clear;
  lblcaminhofoto.Clear;
  memoobservacoes.Clear;
  lblvaloratialdep.Caption  := 'Valor Atual: R$ -';
  lbldepacumulada.Caption   := 'Dep. Acumulada: R$ -';
  lblanosusodep.Caption     := 'Anos em Uso: -';
  // ─────────────────────────────────────────────────────────────────────

  GroupBox1.Refresh;
  GroupBox2.Refresh;
  lblcctrlcodestr.SetFocus;
end;

procedure Tfrmmanativofixo.memoobservacoesKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
    if (Key = VK_ESCAPE) or (Key = VK_TAB) then
       lblplaquetapatrimonio.setfocus;
end;

procedure Tfrmmanativofixo.spblimparClick(Sender: TObject);
begin
  LimparFormulario;
end;

procedure Tfrmmanativofixo.spbsairClick(Sender: TObject);
begin
  Close;
  frmprincipal.Show;
end;

{ ══════════════════════════════════════════════════════════════════════════
  LOOKUP (F4) — usa TFrmConsulta4
  ══════════════════════════════════════════════════════════════════════════ }

procedure Tfrmmanativofixo.spbcctrlcodestrClick(Sender: TObject);
var
  cod, descr: string;
begin
  AbrirConsulta(
    'SELECT geocctrlcodestr, geocctrlnome FROM USER_geoapolo_centrocontrole',
    'geocctrlcodestr', 'geocctrlnome', 'Centro de Controle', cod, descr);

  if cod <> '' then
  begin
    lblcctrlcodestr.Text := cod;
    lblcctrlnome.Caption := descr;
    lblcctrlnome.Refresh;
    lblcategbem.SetFocus;
  end;
end;

procedure Tfrmmanativofixo.spbexibedepreciacaoClick(Sender: TObject);
begin
   groupbox3.Visible:=true;
   groupbox3.top := 418;
   groupbox3.left:= 289;

end;

procedure Tfrmmanativofixo.spbexibedepreciacaoMouseDown(Sender: TObject;
  Button: TMouseButton; Shift: TShiftState; X, Y: Integer);
begin
   groupbox3.Visible:= false;
end;

procedure Tfrmmanativofixo.spbcategoriabemClick(Sender: TObject);
var
  cod, descr: string;
begin
  AbrirConsulta(
    'SELECT ugsc.codigo_categoria, ugsc.descricao AS Categoria' +
    ' FROM USER_geoapolo_satfi_categorias ugsc WITH(NOLOCK)',
    'codigo_categoria', 'Categoria', 'Categoria do Bem', cod, descr);

  if cod <> '' then
  begin
    lblcategbem.Text        := cod;
    lblcategbemnome.Caption := descr;
    lblcategbemnome.Refresh;
    lbldescricaodobem.SetFocus;
  end;
end;

procedure Tfrmmanativofixo.spbuscaclassifibemClick(Sender: TObject);
var
  cod, descr: string;
begin
  AbrirConsulta(
    'SELECT ugsca.codigoclasse, ugsca.descricao,' +
    '       ugsca.codigo_categoria, ugsc.descricao AS Categoria' +
    ' FROM USER_geoapolo_satfi_classificacaoativo ugsca WITH(NOLOCK)' +
    ' INNER JOIN USER_geoapolo_satfi_categorias ugsc WITH(NOLOCK)' +
    '        ON ugsca.codigo_categoria = ugsc.codigo_categoria' +
    ' ORDER BY ugsca.codigoclasse ASC',
    'codigoclasse', 'descricao', 'Classificação do Ativo', cod, descr);

  if cod <> '' then
  begin
    lblclassificacaobem.Text            := cod;
    lblnomeclassificacaobem.Caption     := descr;
    lblnomeclassificacaobem.Refresh;
    lblplaquetapatrimonio.SetFocus;
  end;
end;

procedure Tfrmmanativofixo.spbuscabemClick(Sender: TObject);
var
  cod, descr, ASQL: string;
begin
  ASQL :=
    'SELECT ugsai.numero_do_bem, ugsai.descricao_do_bem,' +
    '       ugsai.geocctrlcodestr, ugcc.geocctrlnome AS CentroControle,' +
    '       ugsai.codigo_categoria_bem, ugsc.descricao AS Categoria,' +
    '       ugsai.codigo_classificacaoativoimobilizado AS CodClassificacao,' +
    '       ugsca.descricao AS Classificacao,' +
    '       ugsai.codigo_barrasativo, ugsai.numero_de_serie,' +
    '       ugsai.codigo_da_marca, ugpm.descricao_marca AS Marca,' +
    '       ugsai.codigo_localizacao, ugslf.localizacao AS Localizacao,' +
    '       ugsai.codigo_func_responsavel, ugu.nome_completo,' +
    '       ugsai.codigo_status_bem, ugssi.descricao_status_bem AS StatusDoBem' +
    ' FROM USER_geoapolo_satfi_ativoimobilizado ugsai WITH(NOLOCK)' +
    ' INNER JOIN USER_geoapolo_centrocontrole ugcc WITH(NOLOCK)' +
    '        ON ugsai.geocctrlcodestr = ugcc.geocctrlcodestr' +
    ' INNER JOIN USER_geoapolo_satfi_categorias ugsc WITH(NOLOCK)' +
    '        ON ugsai.codigo_categoria_bem = ugsc.codigo_categoria' +
    ' INNER JOIN USER_geoapolo_satfi_classificacaoativo ugsca WITH(NOLOCK)' +
    '        ON ugsai.codigo_classificacaoativoimobilizado = ugsca.codigoclasse' +
    ' INNER JOIN USER_geoapolo_produto_marcas ugpm WITH(NOLOCK)' +
    '        ON ugsai.codigo_da_marca = ugpm.codigo_marca' +
    ' INNER JOIN USER_geoapolo_satfi_localizacao_fisica ugslf WITH(NOLOCK)' +
    '        ON ugsai.codigo_localizacao = ugslf.codigo_localizacao' +
    ' INNER JOIN USER_geoapolo_usuarios ugu WITH(NOLOCK)' +
    '        ON ugsai.codigo_func_responsavel = ugu.usucod' +
    ' INNER JOIN USER_geoapolo_satfi_status_imobilizado ugssi WITH(NOLOCK)' +
    '        ON ugsai.codigo_status_bem = ugssi.codigo_status_bem';

  AbrirConsulta(ASQL, 'numero_do_bem', 'descricao_do_bem', 'Busca de Bem', cod, descr);

  if cod <> '' then
  begin
    lblcodigodobem.Text    := cod;
    lbldescricaodobem.Text := descr;
    lblcodigodobem.Refresh;
    lbldescricaodobem.Refresh;
  end;
end;

procedure Tfrmmanativofixo.spbuscalocalizacaoClick(Sender: TObject);
var
  cod, descr: string;
begin
  AbrirConsulta(
    'SELECT ugslf.codigo_localizacao AS stfcodlocestr,' +
    '       ugslf.grupo, ugslf.localizacao,' +
    '       ugslf.codigo_departamento, ugd.nome_departamento AS departamento' +
    ' FROM USER_geoapolo_satfi_localizacao_fisica ugslf WITH(NOLOCK)' +
    ' INNER JOIN USER_geoapolo_departamentos ugd WITH(NOLOCK)' +
    '        ON ugslf.codigo_departamento = ugd.codigo_departamento' +
    '       AND ugd.flagativo = ' + QuotedStr('A') +
    ' ORDER BY ugslf.codigo_localizacao ASC',
    'stfcodlocestr', 'localizacao', 'Localização Física', cod, descr);

  if cod <> '' then
  begin
    lbllocalizacaofisica.Text           := cod;
    lbldescricaolocalizacao.Caption     := descr;
    lbldescricaolocalizacao.Refresh;
    lblcodfuncresponsavel.SetFocus;
  end;
end;

procedure Tfrmmanativofixo.spbuscafuncrespClick(Sender: TObject);
var
  cod, descr: string;
begin
  AbrirConsulta(
    'SELECT ugu.usucod, ugu.usucod_apolo, ugu.nome_completo,' +
    '       ugu.codigo_departamento, ugd.nome_departamento' +
    ' FROM USER_geoapolo_usuarios ugu' +
    ' INNER JOIN USER_geoapolo_departamentos ugd WITH(NOLOCK)' +
    '        ON ugu.codigo_departamento = ugd.codigo_departamento' +
    '       AND ugd.flagativo = ' + QuotedStr('A') +
    ' WHERE ugu.flagativo = ' + QuotedStr('A'),
    'usucod', 'nome_completo', 'Responsável pelo Bem', cod, descr);

  if cod <> '' then
  begin
    lblcodfuncresponsavel.Text         := cod;
    lblnomefuncresponsavel.Caption     := descr;
    lblnomefuncresponsavel.Refresh;
    lblstatusdobem.SetFocus;
  end;
end;

procedure Tfrmmanativofixo.spbuscamarcaClick(Sender: TObject);
var
  cod, descr: string;
begin
  AbrirConsulta(
    'SELECT ugpm.codigo_marca, ugpm.descricao_marca' +
    ' FROM USER_geoapolo_produto_marcas ugpm WITH(NOLOCK)' +
    ' ORDER BY ugpm.codigo_marca ASC',
    'codigo_marca', 'descricao_marca', 'Marca do Produto', cod, descr);

  if cod <> '' then
  begin
    lblcodmarcaproduto.Text := cod;
    lblnomedamarca.Caption  := descr;
    lblnomedamarca.Refresh;
    lbllocalizacaofisica.SetFocus;
  end;
end;

procedure Tfrmmanativofixo.spbuscastatusClick(Sender: TObject);
var
  cod, descr: string;
begin
  AbrirConsulta(
    'SELECT ugssi.codigo_status_bem, ugssi.descricao_status_bem' +
    ' FROM USER_geoapolo_satfi_status_imobilizado ugssi WITH(NOLOCK)',
    'codigo_status_bem', 'descricao_status_bem', 'Status do Bem', cod, descr);

  if cod <> '' then
  begin
    lblstatusdobem.Text        := cod;
    lblnomestatusdobem.Caption := descr;
    lblnomestatusdobem.Refresh;
    spbsalvar.Click;
  end;
end;

procedure Tfrmmanativofixo.SpeedButton1Click(Sender: TObject);
begin
   opendialog.Execute;
   lblcaminhofoto.text := opendialog.FileName;
   lblcaminhofoto.Refresh;
end;

{ ══════════════════════════════════════════════════════════════════════════
  RESOLVEDORES LAZY (descrição ao entrar no próximo campo)
  ══════════════════════════════════════════════════════════════════════════ }

procedure Tfrmmanativofixo.ResolverEmpresa;
begin
  if (lblempcod.Text = '') or (lblempnome.Caption <> '...') then
    Exit;

  with modulo_dados do
  begin
    sql := 'SELECT empnome FROM USER_geoapolo_empresas WHERE empcod = :empcod';
    fdquerysql.close;
    fdquerysql.sql.clear;
    fdquerysql.sql.text := sql;
    fdquerysql.parambyname('empcod').asstring := lblempcod.Text;
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
    begin
      lblempnome.Caption := fdquerysql.FieldByName('empnome').AsString;
      lblempnome.Refresh;
    end;
  end;
end;

procedure Tfrmmanativofixo.ResolverCentroControle;
begin
  if (lblcctrlcodestr.Text = '') or (lblcctrlnome.Caption <> '...') then
    Exit;

  with modulo_dados do
  begin
    sql := 'SELECT geocctrlnome FROM USER_geoapolo_centrocontrole' +
           ' WHERE geocctrlcodestr = :cctrlcodestr';
    fdquerysql.close;
    fdquerysql.sql.clear;
    fdquerysql.sql.text := sql;
    fdquerysql.parambyname('cctrlcodestr').asstring := lblcctrlcodestr.Text;
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
    begin
      lblcctrlnome.Caption := fdquerysql.FieldByName('geocctrlnome').AsString;
      lblcctrlnome.Refresh;
    end;
  end;
end;

procedure Tfrmmanativofixo.ResolverCategoria;
begin
  if (lblcategbem.Text = '') or (lblcategbemnome.Caption <> '...') then
    Exit;

  with modulo_dados do
  begin
    sql := 'SELECT descricao FROM USER_geoapolo_satfi_categorias' +
           ' WHERE codigo_categoria = :codcategbem';
    fdquerysql.close;
    fdquerysql.sql.clear;
    fdquerysql.sql.text := sql;
    fdquerysql.parambyname('codcategbem').asstring := lblcategbem.Text;
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
    begin
      lblcategbemnome.Caption := fdquerysql.FieldByName('descricao').AsString;
      lblcategbemnome.Refresh;
    end;
  end;
end;

procedure Tfrmmanativofixo.ResolverClassificacao;
begin
  if (lblclassificacaobem.Text = '') or (lblnomeclassificacaobem.Caption <> '...') then
    Exit;

  with modulo_dados do
  begin
    sql := 'SELECT descricao FROM USER_geoapolo_satfi_classificacaoativo' +
           ' WHERE codigoclasse = :codigoclasse';
    fdquerysql.close;
    fdquerysql.sql.clear;
    fdquerysql.sql.text := sql;
    fdquerysql.parambyname('codigoclasse').asstring := lblclassificacaobem.Text;
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
    begin
      lblnomeclassificacaobem.Caption := fdquerysql.FieldByName('descricao').AsString;
      lblnomeclassificacaobem.Refresh;
    end
    else
    begin
      MessageDlg('CÓDIGO DE CLASSIFICAÇÃO INVÁLIDO!', mtError, [mbOK], 0);
      lblclassificacaobem.SetFocus;
    end;
  end;
end;

procedure Tfrmmanativofixo.ResolverLocalizacao;
begin
  if (lbllocalizacaofisica.Text = '') or (lbldescricaolocalizacao.Caption <> '...') then
    Exit;

  with modulo_dados do
  begin
    sql := 'SELECT localizacao FROM USER_geoapolo_satfi_localizacao_fisica' +
           ' WHERE codigo_localizacao = :codigolocalizacao' +
           '   AND grupo <> ' + QuotedStr('G');
    fdquerysql.close;
    fdquerysql.sql.clear;
    fdquerysql.sql.text := sql;
    fdquerysql.parambyname('codigolocalizacao').asstring := lbllocalizacaofisica.Text;
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
    begin
      lbldescricaolocalizacao.Caption := fdquerysql.FieldByName('localizacao').AsString;
      lbldescricaolocalizacao.Refresh;
    end;
  end;
end;

procedure Tfrmmanativofixo.ResolverFuncResponsavel;
begin
  if (lblcodfuncresponsavel.Text = '') or (lblnomefuncresponsavel.Caption <> '...') then
    Exit;

  with modulo_dados do
  begin
    sql := 'SELECT ugu.nome_completo FROM USER_geoapolo_usuarios ugu' +
           ' WHERE ugu.usucod = :usucod';
    fdquerysql.close;
    fdquerysql.sql.clear;
    fdquerysql.sql.text := sql;
    fdquerysql.parambyname('usucod').asstring := lblcodfuncresponsavel.Text;
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
    begin
      lblnomefuncresponsavel.Caption := fdquerysql.FieldByName('nome_completo').AsString;
      lblnomefuncresponsavel.Refresh;
    end;
  end;
end;

procedure Tfrmmanativofixo.ResolverMarca;
begin
  if (lblcodmarcaproduto.Text = '') or (lblnomedamarca.Caption <> '...') then
    Exit;

  with modulo_dados do
  begin
    sql := 'SELECT descricao_marca FROM USER_geoapolo_produto_marcas' +
           ' WHERE codigo_marca = :codigomarca';
    fdquerysql.close;
    fdquerysql.sql.clear;
    fdquerysql.sql.text := sql;
    fdquerysql.parambyname('codigomarca').asstring := lblcodmarcaproduto.Text;
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
    begin
      lblnomedamarca.Caption := fdquerysql.FieldByName('descricao_marca').AsString;
      lblnomedamarca.Refresh;
    end;
  end;
end;

procedure Tfrmmanativofixo.ResolverStatus;
begin
  if (lblstatusdobem.Text = '') or (lblnomestatusdobem.Caption <> '...') then
    Exit;

  with modulo_dados do
  begin
    sql := 'SELECT descricao_status_bem FROM USER_geoapolo_satfi_status_imobilizado' +
           ' WHERE codigo_status_bem = :statusdobem';
    fdquerysql.close;
    fdquerysql.sql.clear;
    fdquerysql.sql.text := sql;
    fdquerysql.parambyname('statusdobem').asstring := lblstatusdobem.Text;
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
    begin
      lblnomestatusdobem.Caption := fdquerysql.FieldByName('descricao_status_bem').AsString;
      lblnomestatusdobem.Refresh;
    end;
  end;
end;

{ ══════════════════════════════════════════════════════════════════════════
  DEPRECIAÇÃO — método de cálculo (Linha Reta)
  ══════════════════════════════════════════════════════════════════════════
  Fórmula Linha Reta:
    DepreciacaoAnual  = ValorCompra * (TaxaAnual / 100)
    AnosEmUso         = (Hoje - DataAquisicao) / 365.25
    DepAcumulada      = DepreciacaoAnual * AnosEmUso
    ValorAtual        = MAX(ValorCompra - DepAcumulada, 0)

  Regras aplicadas:
    • Se data_aquisicao ou valor_compra estiverem vazios → não calcula.
    • Se taxa = 0 → exibe aviso e não calcula.
    • O valor atual nunca fica negativo (bem totalmente depreciado = R$ 0,00).
  ══════════════════════════════════════════════════════════════════════════ }

procedure Tfrmmanativofixo.ExibirDepreciacao;
var
  dtAquisicao  : TDate;
  vlCompra     : Double;
  taxaAnual    : Double;
  anosEmUso    : Double;
  depAnual     : Double;
  depAcumulada : Double;
  vlAtual      : Double;
begin
  // Limpa os labels antes de qualquer validação
  //lblvaloratialdep.Caption := 'Valor Atual: R$ -';
  lbldepacumulada.Caption  := 'Dep. Acumulada: R$ -';
  lblanosusodep.Caption    := 'Anos em Uso: -';

  // Validações de entrada
  if lbldataaquisicao.Text = '' then
    Exit;
  if lblvalorcompra.Text = '' then
    Exit;

  dtAquisicao := StrToDateDef(lbldataaquisicao.Text, 0);
  if dtAquisicao = 0 then
  begin
    lblvaloratialdep.Caption := 'Data de aquisição inválida';
    Exit;
  end;

  vlCompra  := StrToFloatDef(lblvalorcompra.Text, 0);
  taxaAnual := StrToFloatDef(lbltaxadepanual.Text, 0);

  if taxaAnual <= 0 then
  begin
    lblvaloratialdep.Caption := 'Informe a taxa de depreciação anual (%)';
    Exit;
  end;

  // Cálculo Linha Reta
  anosEmUso    := (Date - dtAquisicao) / 365.25;
  depAnual     := vlCompra * (taxaAnual / 100);
  depAcumulada := depAnual * anosEmUso;
  vlAtual      := vlCompra - depAcumulada;

  if vlAtual < 0 then
    vlAtual := 0; // bem totalmente depreciado

  // Exibição
  lblanosusodep.Caption   := Format('Anos em Uso: %.2f', [anosEmUso]);
  lbldepacumulada.Caption := Format('Dep. Acumulada: R$ %.2f', [depAcumulada]);
  lblvaloratialdep.Caption := Format('Valor Atual: R$ %.2f', [vlAtual]);

  lblanosusodep.Refresh;
  lbldepacumulada.Refresh;
  lblvaloratialdep.Refresh;
end;

procedure Tfrmmanativofixo.spbcalculardepreciacaoClick(Sender: TObject);
begin
  ExibirDepreciacao;
end;

procedure Tfrmmanativofixo.spbcalculardepreciacaoMouseDown(Sender: TObject;
  Button: TMouseButton; Shift: TShiftState; X, Y: Integer);
begin
   groupbox3.Visible := false;
end;

{ ══════════════════════════════════════════════════════════════════════════
  EVENTOS DE NAVEGAÇÃO / VALIDAÇÃO DOS CAMPOS
  ══════════════════════════════════════════════════════════════════════════ }

procedure Tfrmmanativofixo.lblcctrlcodestrEnter(Sender: TObject);
begin
  ResolverEmpresa;
end;

procedure Tfrmmanativofixo.lblcctrlcodestrKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then
    spbcctrlcodestr.Click;

  if (Key = VK_RETURN) or (Key = VK_TAB) then
  begin
    Key := 0;
    lblcctrlnome.Caption := '...';
    lbldescricaodobem.SetFocus;
  end;
end;

procedure Tfrmmanativofixo.lblcaminhofotoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
    if (Key = VK_RETURN) or (Key = VK_TAB) then
        memoobservacoes.setfocus;
end;

procedure Tfrmmanativofixo.lblcategbemEnter(Sender: TObject);
begin
  if lblcctrlcodestr.Text = '' then
  begin
    MessageDlg('CAMPO DE CENTRO DE CUSTOS É OBRIGATÓRIO!', mtError, [mbOK], 0);
    lblcctrlcodestr.SetFocus;
    Exit;
  end;
  ResolverCentroControle;
end;

procedure Tfrmmanativofixo.lblcategbemKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then
    spbcategoriabem.Click;

  if (Key = VK_RETURN) or (Key = VK_TAB) then
    lblclassificacaobem.SetFocus;
end;

procedure Tfrmmanativofixo.lbldataaquisicaoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then
     lblvalorcompra.setfocus;
end;

procedure Tfrmmanativofixo.lbldataultimarevisaoKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
    if (Key = VK_RETURN) or (Key = VK_TAB) then
       lblcaminhofoto.setfocus;
end;

procedure Tfrmmanativofixo.lbldescricaodobemEnter(Sender: TObject);
begin
  if lblcategbem.Text = '' then
  begin
    MessageDlg('O CAMPO CATEGORIA DO BEM É OBRIGATÓRIO!', mtError, [mbOK], 0);
    lblcategbem.SetFocus;
    Exit;
  end;
  ResolverCategoria;
end;

procedure Tfrmmanativofixo.lbldescricaodobemKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then
  begin
    Key := 0;
    Perform(WM_NEXTDLGCTL, 0, 0);
  end;
end;

procedure Tfrmmanativofixo.lblclassificacaobemEnter(Sender: TObject);
begin
  if lbldescricaodobem.Text = '' then
  begin
    MessageDlg('É OBRIGATÓRIO INFORMAR UMA DESCRIÇÃO DO BEM!', mtError, [mbOK], 0);
    lbldescricaodobem.SetFocus;
  end;
end;

procedure Tfrmmanativofixo.lblclassificacaobemKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then
    spbuscaclassifibem.Click;

  if (Key = VK_RETURN) or (Key = VK_TAB) then
    lblcodmarcaproduto.SetFocus;
end;

procedure Tfrmmanativofixo.lblplaquetapatrimonioEnter(Sender: TObject);
begin
  if lblclassificacaobem.Text = '' then
  begin
    lblclassificacaobem.Text := '0';
    Exit;
  end;
  ResolverClassificacao;
end;

procedure Tfrmmanativofixo.lblplaquetapatrimonioKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then
    lblnumeroserie.SetFocus;
end;

procedure Tfrmmanativofixo.lblnumeroserieKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then
    lblcodfuncresponsavel.SetFocus;
end;

procedure Tfrmmanativofixo.lblcodmarcaprodutoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then
    spbuscamarca.Click;

  if (Key = VK_RETURN) or (Key = VK_TAB) then
    lbllocalizacaofisica.SetFocus;
end;

procedure Tfrmmanativofixo.lbllocalizacaofisicaEnter(Sender: TObject);
begin
  if lblcodmarcaproduto.Text = '' then
    lblcodmarcaproduto.Text := '11';
  ResolverMarca;
end;

procedure Tfrmmanativofixo.lbllocalizacaofisicaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then
    spbuscalocalizacao.Click;

  if (Key = VK_RETURN) or (Key = VK_TAB) then
    lblstatusdobem.SetFocus;
end;

procedure Tfrmmanativofixo.lblcodfuncresponsavelEnter(Sender: TObject);
begin
  if lbllocalizacaofisica.Text = '' then
  begin
    MessageDlg('É OBRIGATÓRIO INFORMAR UMA LOCALIZAÇÃO FÍSICA!', mtError, [mbOK], 0);
    lbllocalizacaofisica.SetFocus;
    Exit;
  end;
  ResolverLocalizacao;
end;

procedure Tfrmmanativofixo.lblcodfuncresponsavelKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then
    spbuscafuncresp.Click;

  if (Key = VK_RETURN) or (Key = VK_TAB) then
    lblstatusdobem.SetFocus;
end;

procedure Tfrmmanativofixo.lblstatusdobemEnter(Sender: TObject);
begin
  ResolverFuncResponsavel;
end;

procedure Tfrmmanativofixo.lblstatusdobemKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then
    spbuscastatus.Click;
  if (Key = VK_RETURN) or (Key = VK_TAB) then
    lbldataaquisicao.setfocus;
end;

procedure Tfrmmanativofixo.lbltaxadepanualKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
    if (Key = VK_RETURN) or (Key = VK_TAB) then
       lbldataultimarevisao.setfocus;
end;

procedure Tfrmmanativofixo.lblvalorcompraKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then
     lbltaxadepanual.setfocus;
end;

{ ══════════════════════════════════════════════════════════════════════════
  MENU / CONFIG GRID
  ══════════════════════════════════════════════════════════════════════════ }

procedure Tfrmmanativofixo.popmnugravaconfigClick(Sender: TObject);
begin
  grava_configuracoes_grids(frmmanativofixo, 'GEOATIVOFIXO', gridativoimobilizado,
    'gridativoimobilizado', frmlogon.nomeusuario, modulo_dados.dtsfdquerysql4);
end;

{ ══════════════════════════════════════════════════════════════════════════
  ATUALIZAR GRID PRINCIPAL
  ══════════════════════════════════════════════════════════════════════════ }

procedure Tfrmmanativofixo.AtualizarGrid;
begin
  mostrabensimobilizados;
end;

{ ══════════════════════════════════════════════════════════════════════════
  FUNÇÃO GLOBAL
  ══════════════════════════════════════════════════════════════════════════ }

function mostrabensimobilizados: string;
const
  SQL_BENS =
    'SELECT ugsa.numero_do_bem, ugsa.descricao_do_bem,' +
    '       ugsa.geocctrlcodestr, ugcc.geocctrlnome,' +
    '       ugsa.codigo_barrasativo, ugsa.codigo_categoria_bem,' +
    '       ugsc.descricao AS categoria_bem,' +
    '       ugsa.codigo_classificacaoativoimobilizado,' +
    '       ugsca.descricao AS classificacao,' +
    '       ugsa.codigo_localizacao, ugslf.localizacao,' +
    '       ugsa.codigo_func_responsavel, ugu.nome_completo,' +
    '       ugsa.codigo_da_marca, ugpm.descricao_marca AS marca,' +
    '       ugsa.codigo_status_bem, ugssi.descricao_status_bem,' +
    '       ugsa.empcod,' +
    // ── NOVOS CAMPOS — DEPRECIAÇÃO ────────────────────────────────────────
    '       ugsa.data_aquisicao, ugsa.valor_compra,' +
    '       ugsa.taxa_depreciacao_anual, ugsa.data_ultima_revisao,' +
    '       ugsa.caminho_foto, ugsa.observacoes' +
    // ─────────────────────────────────────────────────────────────────────
    ' FROM USER_geoapolo_satfi_ativoimobilizado ugsa WITH(NOLOCK)' +
    ' INNER JOIN USER_geoapolo_centrocontrole ugcc WITH(NOLOCK)' +
    '        ON ugsa.geocctrlcodestr = ugcc.geocctrlcodestr' +
    ' INNER JOIN USER_geoapolo_satfi_categorias ugsc WITH(NOLOCK)' +
    '        ON ugsa.codigo_categoria_bem = ugsc.codigo_categoria' +
    ' INNER JOIN USER_geoapolo_satfi_classificacaoativo ugsca WITH(NOLOCK)' +
    '        ON ugsa.codigo_classificacaoativoimobilizado = ugsca.codigoclasse' +
    ' INNER JOIN USER_geoapolo_satfi_localizacao_fisica ugslf WITH(NOLOCK)' +
    '        ON ugsa.codigo_localizacao = ugslf.codigo_localizacao' +
    ' INNER JOIN USER_geoapolo_usuarios ugu WITH(NOLOCK)' +
    '        ON ugsa.codigo_func_responsavel = ugu.usucod' +
    ' INNER JOIN USER_geoapolo_produto_marcas ugpm WITH(NOLOCK)' +
    '        ON ugsa.codigo_da_marca = ugpm.codigo_marca' +
    ' LEFT JOIN USER_geoapolo_satfi_status_imobilizado ugssi WITH(NOLOCK)' +
    '        ON ugsa.codigo_status_bem = ugssi.codigo_status_bem' +
    ' WHERE ugsa.empcod = %s' +
    ' ORDER BY CAST(ugsa.numero_do_bem AS INTEGER) ASC';
begin
  Result := '';

  with modulo_dados, frmmanativofixo do
  begin
    sql := Format(SQL_BENS, [QuotedStr(frmprincipal.codigo_empresa)]);
    fdquerysql4.close;
    fdquerysql4.sql.clear;
    fdquerysql4.sql.text := sql;

    if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
    begin
      dtsfdquerysql4.DataSet          := fdquerysql4;
      gridativoimobilizado.DataSource := dtsfdquerysql4;
      gridativoimobilizado.Refresh;
      gridativoimobilizado.SetFocus;
    end;
  end;
end;

end.
