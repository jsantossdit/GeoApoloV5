unit unt_categoriaentidade;

{ =============================================================================
  Módulo  : unt_categoriaentidade
  Autor   : (seu nome)
  Versão  : 2.0
  Data    : 2025
  Descr.  : Gerenciamento de relacionamento Usuário x Categoria x Entidade.
            Refatorado para FireDAC + OOP — sem variáveis globais de SQL,
            com separação clara de responsabilidades entre View e Service.
  ============================================================================= }
interface
uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, ComCtrls, Buttons, ExtCtrls, Grids, Gauges, Menus,
  FireDAC.Comp.Client,   // TFDQuery, TFDConnection
  FireDAC.Stan.Param,    // TFDParams
  FireDAC.Stan.Intf, Vcl.Mask;
// ---------------------------------------------------------------------------
// Enumeração: modo de operação do grid (por usuário ou por grupo)
// ---------------------------------------------------------------------------
type
  TGridOpcao = (goUsuario, goGrupo);
// ---------------------------------------------------------------------------
// TEntidadeService — encapsula toda a lógica de negócio / acesso a dados.
// A View (TForm) apenas chama métodos públicos desta classe.
// ---------------------------------------------------------------------------
type
  TEntidadeService = class
  strict private
    FConnection : TFDConnection;  // injetada pelo construtor
    // Executa SELECT e devolve um TFDQuery já aberto (caller libera)
    function  ExecQuery(const ASQL: string): TFDQuery;
    // Executa DML (INSERT / UPDATE / DELETE) e devolve linhas afetadas
    function  ExecDML(const ASQL: string): Integer;
  public
    constructor Create(AConnection: TFDConnection);
    // ---------- Carga de combos ----------
    procedure CarregarUsuariosAtivos(Dest: TStrings);
    procedure CarregarGrupos(Dest: TStrings);
    procedure CarregarUsuariosDoGrupo(const GrupoID: string; Dest: TStrings);
    // ---------- Carga do grid ----------
    // Preenche StringGrid com dados de categorias do usuário/grupo.
    // AGrid: grid destino; AGauge: barra de progresso opcional.
    procedure CarregarGridPorUsuario(const UsuarioID: string;
                                     AGrid: TStringGrid;
                                     AGauge: TGauge);
    procedure CarregarGridPorGrupo(const GrupoID: string;
                                   AGrid: TStringGrid;
                                   AGauge: TGauge);
    // ---------- Relacionamento (double-click no grid) ----------
    procedure RelacionarCategoriasDoUsuario(const UsuarioID, CategCod: string;
                                            AGauge: TGauge);
    procedure RelacionarCategoriasDoGrupo(const GrupoID, CategCod: string;
                                          AGauge: TGauge);
    // ---------- Remoção (Delete no grid) ----------
    procedure RemoverRelacionamentoUsuario(const UsuarioID, CategCod: string;
                                           AGauge: TGauge);
    procedure RemoverRelacionamentoGrupo(const GrupoID, CategCod: string;
                                         AGauge: TGauge);
    // ---------- Inserção de categoria ----------
    procedure InserirCategoriaUsuario(const UsuarioID, CategCod: string;
                                      AGauge: TGauge);
    procedure InserirCategoriaGrupo(const GrupoID, CategCod: string;
                                    AGauge: TGauge);
    // ---------- Consulta de categorias disponíveis ----------
    function  BuscarTodasCategorias: TFDQuery;
  end;
// ---------------------------------------------------------------------------
// TfrmRelacentidades — View limpa; não contém lógica de negócio.
// ---------------------------------------------------------------------------
type
  Tfrmrelacentidades = class(TForm)
    panelmenu       : TPanel;
    spbsalvar       : TSpeedButton;
    spbligacoes     : TSpeedButton;
    spbsair         : TSpeedButton;
    spblimpar       : TSpeedButton;
    lblsair         : TLabel;
    spbajuste       : TSpeedButton;
    StatusBar1      : TStatusBar;
    GroupBox1       : TGroupBox;
    lblusuario      : TLabel;
    Label2          : TLabel;
    cbousuario      : TComboBox;
    cbogrupo        : TComboBox;
    GroupBox2       : TGroupBox;
    gridUsuarioRelac: TStringGrid;
    grpcategoria    : TGroupBox;
    Gauge1          : TGauge;
    grpinserecateg  : TGroupBox;
    lblcategcodestr : TLabeledEdit;
    lblmsg1         : TLabel;
    spbusca         : TSpeedButton;
    btninserecateg  : TBitBtn;
    btncancelar     : TBitBtn;
    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbsairClick(Sender: TObject);
    procedure spbuscaClick(Sender: TObject);
    procedure btncancelarClick(Sender: TObject);
    procedure btninserecategClick(Sender: TObject);
    procedure gridUsuarioRelacEnter(Sender: TObject);
    procedure gridUsuarioRelacDblClick(Sender: TObject);
    procedure gridUsuarioRelacKeyUp(Sender: TObject; var Key: Word;
                                    Shift: TShiftState);
    procedure cbousuarioEnter(Sender: TObject);
    procedure lblcategcodestrKeyUp(Sender: TObject; var Key: Word;
                                   Shift: TShiftState);
  private
    FService: TEntidadeService;
    function  OpcaoAtual: TGridOpcao;
    procedure AtualizarGrid;
    procedure ExibirPainelInsercao;
    procedure OcultarPainelInsercao;
    procedure LimparGrid;
    procedure ConfigurarStatusBar;
    function  CategSelecionada: string;  // devolve código da linha corrente
  end;
var
  frmrelacentidades: Tfrmrelacentidades;
implementation
uses
  unt_dados,          // TmoduloDados com FDConnection
  unt_consultav3, funcoes;
{$R *.dfm}
// ===========================================================================
//  HELPERS INTERNOS
// ===========================================================================
{ Limpa todas as células do grid e mantém apenas o cabeçalho }
procedure LimpaStringGrid(AGrid: TStringGrid);
var
  R, C: Integer;
begin
  for R := 1 to AGrid.RowCount - 1 do
    for C := 0 to AGrid.ColCount - 1 do
      AGrid.Cells[C, R] := '';
  AGrid.RowCount := 2;
end;
// ===========================================================================
//  TEntidadeService
// ===========================================================================
constructor TEntidadeService.Create(AConnection: TFDConnection);
begin
  inherited Create;
  FConnection := AConnection;
end;
// ---------------------------------------------------------------------------
function TEntidadeService.ExecQuery(const ASQL: string): TFDQuery;
begin
  Result := TFDQuery.Create(nil);
  try
    Result.Connection := FConnection;
    Result.SQL.Text   := ASQL;
    Result.Open;
  except
    Result.Free;
    raise;
  end;
end;
// ---------------------------------------------------------------------------
function TEntidadeService.ExecDML(const ASQL: string): Integer;
var
  Q: TFDQuery;
begin
  Q := TFDQuery.Create(nil);
  try
    Q.Connection  := FConnection;
    Q.SQL.Text    := ASQL;
    Q.ExecSQL;
    Result := Q.RowsAffected;
  finally
    Q.Free;
  end;
end;
// ---------------------------------------------------------------------------
// Carga de combos
// ---------------------------------------------------------------------------
procedure TEntidadeService.CarregarUsuariosAtivos(Dest: TStrings);
var
  Q: TFDQuery;
begin
  Dest.Clear;
  Q := ExecQuery(
    'SELECT usucod FROM usuario WHERE UsuStat = ' + QuotedStr('Ativo') +
    ' ORDER BY usucod');
  try
    while not Q.Eof do
    begin
      Dest.Add(Q.FieldByName('usucod').AsString);
      Q.Next;
    end;
  finally
    Q.Free;
  end;
end;
// ---------------------------------------------------------------------------
procedure TEntidadeService.CarregarGrupos(Dest: TStrings);
var
  Q: TFDQuery;
begin
  Dest.Clear;
  Q := ExecQuery('SELECT GrpUsuCod FROM grp_usuario ORDER BY GrpUsuCod ASC');
  try
    while not Q.Eof do
    begin
      Dest.Add(Q.FieldByName('GrpUsuCod').AsString);
      Q.Next;
    end;
  finally
    Q.Free;
  end;
end;
// ---------------------------------------------------------------------------
procedure TEntidadeService.CarregarUsuariosDoGrupo(const GrupoID: string;
  Dest: TStrings);
var
  Q: TFDQuery;
  SQL: string;
begin
  Dest.Clear;
  SQL :=
    'SELECT gu.usucod'                                            + sLineBreak +
    'FROM   grp_x_usuario gu WITH(NOLOCK)'                       + sLineBreak +
    '       INNER JOIN usuario u WITH(NOLOCK) ON u.usucod = gu.usucod' + sLineBreak +
    'WHERE  gu.grpusucod = ' + QuotedStr(GrupoID)                + sLineBreak +
    '  AND  u.UsuStat = '   + QuotedStr('Ativo');
  Q := ExecQuery(SQL);
  try
    while not Q.Eof do
    begin
      Dest.Add(Q.FieldByName('usucod').AsString);
      Q.Next;
    end;
  finally
    Q.Free;
  end;
end;
// ---------------------------------------------------------------------------
// Carga do grid — Por Usuário
// ---------------------------------------------------------------------------
procedure TEntidadeService.CarregarGridPorUsuario(const UsuarioID: string;
  AGrid: TStringGrid; AGauge: TGauge);
var
  QCat, QRel: TFDQuery;
  Row: Integer;
  SQLRel: string;
begin
  LimpaStringGrid(AGrid);
  AGrid.ColCount := 4;
  AGrid.Cells[0, 0] := 'Código Cat.';
  AGrid.Cells[1, 0] := 'Nome Categoria';
  AGrid.Cells[2, 0] := 'Total Categoria';
  AGrid.Cells[3, 0] := 'Total Relac. ao Usuário';
  QCat := ExecQuery(
    'SELECT categcodestr FROM categoria ORDER BY categcodestr ASC');
  try
    if QCat.IsEmpty then Exit;
    if Assigned(AGauge) then
    begin
      AGauge.MaxValue := QCat.RecordCount;
      AGauge.Progress := 0;
    end;
    Row := 1;
    while not QCat.Eof do
    begin
      SQLRel :=
        'SELECT ec.categcodestr,'                                              + sLineBreak +
        '       cat.categnome,'                                                + sLineBreak +
        '       (SELECT COUNT(e.entcod)'                                       + sLineBreak +
        '        FROM   entidade e WITH(NOLOCK)'                               + sLineBreak +
        '               INNER JOIN ent_categ ec2 WITH(NOLOCK)'                 + sLineBreak +
        '                       ON e.entcod = ec2.entcod'                      + sLineBreak +
        '        WHERE  ec2.categcodestr = ' +
              QuotedStr(QCat.FieldByName('categcodestr').AsString) +
        '       ) AS TotalCategoria,'                                          + sLineBreak +
        '       COUNT(ue.usucod) AS TotalUsuarioRelacionado'                   + sLineBreak +
        'FROM   usuario_ent  ue  WITH(NOLOCK)'                                 + sLineBreak +
        '       INNER JOIN ent_categ  ec  WITH(NOLOCK) ON ec.entcod  = ue.entcod' + sLineBreak +
        '       INNER JOIN categoria  cat WITH(NOLOCK) ON cat.categcodestr = ec.categcodestr' + sLineBreak +
        'WHERE  ec.categcodestr = ' + QuotedStr(QCat.FieldByName('categcodestr').AsString) + sLineBreak +
        '  AND  ue.usucod = ' + QuotedStr(UsuarioID)                          + sLineBreak +
        'GROUP BY ue.usucod, ec.categcodestr, cat.categnome';
      QRel := ExecQuery(SQLRel);
      try
        if not QRel.IsEmpty then
        begin
          AGrid.RowCount := Row + 1;
          AGrid.Cells[0, Row] := QRel.FieldByName('categcodestr').AsString;
          AGrid.Cells[1, Row] := QRel.FieldByName('categnome').AsString;
          AGrid.Cells[2, Row] := QRel.FieldByName('TotalCategoria').AsString;
          AGrid.Cells[3, Row] := QRel.FieldByName('TotalUsuarioRelacionado').AsString;
          Inc(Row);
        end;
      finally
        QRel.Free;
      end;
      if Assigned(AGauge) then
        AGauge.AddProgress(1);
      QCat.Next;
    end;
  finally
    QCat.Free;
  end;
end;
// ---------------------------------------------------------------------------
// Carga do grid — Por Grupo
// ---------------------------------------------------------------------------
procedure TEntidadeService.CarregarGridPorGrupo(const GrupoID: string;
  AGrid: TStringGrid; AGauge: TGauge);
var
  QUsuarios, QCat, QRel: TFDQuery;
  Row: Integer;
  SQLUsuarios, SQLRel: string;
begin
  LimpaStringGrid(AGrid);
  AGrid.ColCount := 5;
  AGrid.Cells[0, 0] := 'Usuário';
  AGrid.Cells[1, 0] := 'Código Cat.';
  AGrid.Cells[2, 0] := 'Nome Categoria';
  AGrid.Cells[3, 0] := 'Total Categoria';
  AGrid.Cells[4, 0] := 'Total Relac. ao Usuário';
  SQLUsuarios :=
    'SELECT gu.usucod'                                            + sLineBreak +
    'FROM   grp_x_usuario gu WITH(NOLOCK)'                       + sLineBreak +
    '       INNER JOIN usuario u WITH(NOLOCK) ON u.usucod = gu.usucod' + sLineBreak +
    'WHERE  gu.grpusucod = ' + QuotedStr(GrupoID)                + sLineBreak +
    '  AND  u.UsuStat = '   + QuotedStr('Ativo');
  QUsuarios := ExecQuery(SQLUsuarios);
  try
    if QUsuarios.IsEmpty then Exit;
    if Assigned(AGauge) then
    begin
      AGauge.MaxValue := QUsuarios.RecordCount;
      AGauge.Progress := 0;
    end;
    QCat := ExecQuery(
      'SELECT categcodestr FROM categoria ORDER BY categcodestr ASC');
    try
      Row := 1;
      while not QUsuarios.Eof do
      begin
        QCat.First;
        while not QCat.Eof do
        begin
          SQLRel :=
            'SELECT ec.categcodestr,'                                            + sLineBreak +
            '       cat.categnome,'                                              + sLineBreak +
            '       (SELECT COUNT(e.entcod)'                                     + sLineBreak +
            '        FROM   entidade e WITH(NOLOCK)'                             + sLineBreak +
            '               INNER JOIN ent_categ ec2 WITH(NOLOCK)'               + sLineBreak +
            '                       ON e.entcod = ec2.entcod'                    + sLineBreak +
            '        WHERE  ec2.categcodestr = ' +
                  QuotedStr(QCat.FieldByName('categcodestr').AsString) +
            '       ) AS TotalCategoria,'                                        + sLineBreak +
            '       COUNT(ue.usucod) AS TotalUsuarioRelacionado'                 + sLineBreak +
            'FROM   usuario_ent  ue  WITH(NOLOCK)'                               + sLineBreak +
            '       INNER JOIN ent_categ  ec  WITH(NOLOCK) ON ec.entcod  = ue.entcod' + sLineBreak +
            '       INNER JOIN categoria  cat WITH(NOLOCK) ON cat.categcodestr = ec.categcodestr' + sLineBreak +
            'WHERE  ec.categcodestr = ' + QuotedStr(QCat.FieldByName('categcodestr').AsString) + sLineBreak +
            '  AND  ue.usucod = ' + QuotedStr(QUsuarios.FieldByName('usucod').AsString) + sLineBreak +
            'GROUP BY ue.usucod, ec.categcodestr, cat.categnome';
          QRel := ExecQuery(SQLRel);
          try
            if not QRel.IsEmpty then
            begin
              AGrid.RowCount := Row + 1;
              AGrid.Cells[0, Row] := QUsuarios.FieldByName('usucod').AsString;
              AGrid.Cells[1, Row] := QRel.FieldByName('categcodestr').AsString;
              AGrid.Cells[2, Row] := QRel.FieldByName('categnome').AsString;
              AGrid.Cells[3, Row] := QRel.FieldByName('TotalCategoria').AsString;
              AGrid.Cells[4, Row] := QRel.FieldByName('TotalUsuarioRelacionado').AsString;
              Inc(Row);
            end;
          finally
            QRel.Free;
          end;
          QCat.Next;
        end; // loop categorias
        if Assigned(AGauge) then
          AGauge.AddProgress(1);
        QUsuarios.Next;
      end; // loop usuários
    finally
      QCat.Free;
    end;
  finally
    QUsuarios.Free;
  end;
end;
// ---------------------------------------------------------------------------
// Relacionamento — Usuário
// ---------------------------------------------------------------------------
procedure TEntidadeService.RelacionarCategoriasDoUsuario(
  const UsuarioID, CategCod: string; AGauge: TGauge);
var
  QEnt: TFDQuery;
  SQL: string;
begin
  SQL :=
    'SELECT ec.entcod'                                        + sLineBreak +
    'FROM   ent_categ ec WITH(NOLOCK)'                        + sLineBreak +
    'WHERE  ec.categcodestr = ' + QuotedStr(CategCod)         + sLineBreak +
    '  AND  ec.entcod NOT IN ('                               + sLineBreak +
    '       SELECT entcod FROM usuario_ent'                   + sLineBreak +
    '       WHERE  usucod = ' + QuotedStr(UsuarioID) + ')';
  QEnt := ExecQuery(SQL);
  try
    if QEnt.IsEmpty then Exit;
    if Assigned(AGauge) then
    begin
      AGauge.MaxValue := QEnt.RecordCount;
      AGauge.Progress := 0;
    end;
    while not QEnt.Eof do
    begin
      ExecDML(
        'INSERT INTO usuario_ent (UsuCod, EntCod, UsuEntRelacAvulso) VALUES (' +
        QuotedStr(UsuarioID) + ', ' +
        QuotedStr(QEnt.FieldByName('entcod').AsString) + ', ' +
        QuotedStr('Não') + ')');
      if Assigned(AGauge) then AGauge.AddProgress(1);
      QEnt.Next;
    end;
  finally
    QEnt.Free;
  end;
end;
// ---------------------------------------------------------------------------
// Relacionamento — Grupo
// ---------------------------------------------------------------------------
procedure TEntidadeService.RelacionarCategoriasDoGrupo(
  const GrupoID, CategCod: string; AGauge: TGauge);
var
  QUsu, QEnt: TFDQuery;
  SQLUsu, SQLEnt: string;
begin
  SQLUsu :=
    'SELECT usucod FROM grp_x_usuario WHERE grpusucod = ' + QuotedStr(GrupoID);
  QUsu := ExecQuery(SQLUsu);
  try
    if QUsu.IsEmpty then Exit;
    while not QUsu.Eof do
    begin
      SQLEnt :=
        'SELECT ec.entcod'                                      + sLineBreak +
        'FROM   ent_categ ec WITH(NOLOCK)'                      + sLineBreak +
        'WHERE  ec.categcodestr = ' + QuotedStr(CategCod)       + sLineBreak +
        '  AND  ec.entcod NOT IN ('                             + sLineBreak +
        '       SELECT entcod FROM usuario_ent'                 + sLineBreak +
        '       WHERE  usucod = ' +
              QuotedStr(QUsu.FieldByName('usucod').AsString) + ')';
      QEnt := ExecQuery(SQLEnt);
      try
        while not QEnt.Eof do
        begin
          ExecDML(
            'INSERT INTO usuario_ent (UsuCod, EntCod, UsuEntRelacAvulso) VALUES (' +
            QuotedStr(QUsu.FieldByName('usucod').AsString) + ', ' +
            QuotedStr(QEnt.FieldByName('entcod').AsString) + ', ' +
            QuotedStr('Não') + ')');
          if Assigned(AGauge) then AGauge.AddProgress(1);
          QEnt.Next;
        end;
      finally
        QEnt.Free;
      end;
      QUsu.Next;
    end;
  finally
    QUsu.Free;
  end;
end;
// ---------------------------------------------------------------------------
// Remoção — Usuário
// ---------------------------------------------------------------------------
procedure TEntidadeService.RemoverRelacionamentoUsuario(
  const UsuarioID, CategCod: string; AGauge: TGauge);
var
  QEnt: TFDQuery;
  SQL: string;
begin
  // Remove da tabela de categoria
  ExecDML(
    'DELETE FROM usuario_categ' + sLineBreak +
    'WHERE  usucod       = ' + QuotedStr(UsuarioID) + sLineBreak +
    '  AND  categcodestr = ' + QuotedStr(CategCod));
  // Remove entidades relacionadas
  SQL :=
    'SELECT ec.entcod'                                          + sLineBreak +
    'FROM   ent_categ  ec  WITH(NOLOCK)'                        + sLineBreak +
    '       INNER JOIN usuario_ent ue WITH(NOLOCK)'             + sLineBreak +
    '               ON ec.entcod = ue.entcod'                   + sLineBreak +
    'WHERE  ec.categcodestr = ' + QuotedStr(CategCod)           + sLineBreak +
    '  AND  ue.usucod = '       + QuotedStr(UsuarioID);
  QEnt := ExecQuery(SQL);
  try
    if QEnt.IsEmpty then Exit;
    if Assigned(AGauge) then
    begin
      AGauge.MaxValue := QEnt.RecordCount;
      AGauge.Progress := 0;
    end;
    while not QEnt.Eof do
    begin
      ExecDML(
        'DELETE FROM usuario_ent' + sLineBreak +
        'WHERE  entcod = ' + QuotedStr(QEnt.FieldByName('entcod').AsString) + sLineBreak +
        '  AND  usucod = ' + QuotedStr(UsuarioID));
      if Assigned(AGauge) then AGauge.AddProgress(1);
      QEnt.Next;
    end;
  finally
    QEnt.Free;
  end;
end;
// ---------------------------------------------------------------------------
// Remoção — Grupo
// ---------------------------------------------------------------------------
procedure TEntidadeService.RemoverRelacionamentoGrupo(
  const GrupoID, CategCod: string; AGauge: TGauge);
var
  QUsu, QEnt: TFDQuery;
begin
  QUsu := ExecQuery(
    'SELECT usucod FROM grp_x_usuario WHERE grpusucod = ' + QuotedStr(GrupoID));
  try
    while not QUsu.Eof do
    begin
      ExecDML(
        'DELETE FROM usuario_categ' + sLineBreak +
        'WHERE  usucod       = ' + QuotedStr(QUsu.FieldByName('usucod').AsString) + sLineBreak +
        '  AND  categcodestr = ' + QuotedStr(CategCod));
      QEnt := ExecQuery(
        'SELECT ec.entcod'                                        + sLineBreak +
        'FROM   ent_categ  ec  WITH(NOLOCK)'                      + sLineBreak +
        '       INNER JOIN usuario_ent ue WITH(NOLOCK)'           + sLineBreak +
        '               ON ec.entcod = ue.entcod'                 + sLineBreak +
        'WHERE  ec.categcodestr = ' + QuotedStr(CategCod)         + sLineBreak +
        '  AND  ue.usucod = ' + QuotedStr(QUsu.FieldByName('usucod').AsString));
      try
        if Assigned(AGauge) then
        begin
          AGauge.MaxValue := QEnt.RecordCount;
          AGauge.Progress := 0;
        end;
        while not QEnt.Eof do
        begin
          ExecDML(
            'DELETE FROM usuario_ent' + sLineBreak +
            'WHERE  entcod = ' + QuotedStr(QEnt.FieldByName('entcod').AsString) + sLineBreak +
            '  AND  usucod = ' + QuotedStr(QUsu.FieldByName('usucod').AsString));
          if Assigned(AGauge) then AGauge.AddProgress(1);
          QEnt.Next;
        end;
      finally
        QEnt.Free;
      end;
      QUsu.Next;
    end;
  finally
    QUsu.Free;
  end;
end;
// ---------------------------------------------------------------------------
// Inserção de Categoria — Usuário
// ---------------------------------------------------------------------------
procedure TEntidadeService.InserirCategoriaUsuario(
  const UsuarioID, CategCod: string; AGauge: TGauge);
var
  QCheck, QEnt: TFDQuery;
begin
  QCheck := ExecQuery(
    'SELECT 1 FROM usuario_categ' + sLineBreak +
    'WHERE  categcodestr = ' + QuotedStr(CategCod) + sLineBreak +
    '  AND  usucod = '       + QuotedStr(UsuarioID));
  try
    if not QCheck.IsEmpty then
      ExecDML(
        'UPDATE usuario_categ SET categcodestr = ' + QuotedStr(CategCod) + sLineBreak +
        'WHERE  usucod = ' + QuotedStr(UsuarioID) + sLineBreak +
        '  AND  categcodestr = ' + QuotedStr(CategCod))
    else
      ExecDML(
        'INSERT INTO usuario_categ (usucod, categcodestr, UsuCategTodasEnt) VALUES (' +
        QuotedStr(UsuarioID) + ', ' + QuotedStr(CategCod) + ', ' + QuotedStr('Sim') + ')');
  finally
    QCheck.Free;
  end;
  // Relaciona entidades ainda não vinculadas
  QEnt := ExecQuery(
    'SELECT ec.entcod'                                           + sLineBreak +
    'FROM   ent_categ ec WITH(NOLOCK)'                           + sLineBreak +
    'WHERE  ec.categcodestr = ' + QuotedStr(CategCod)            + sLineBreak +
    '  AND  ec.entcod NOT IN ('                                  + sLineBreak +
    '       SELECT entcod FROM usuario_ent'                      + sLineBreak +
    '       WHERE  usucod = ' + QuotedStr(UsuarioID) + ')');
  try
    if QEnt.IsEmpty then Exit;
    if Assigned(AGauge) then
    begin
      AGauge.MaxValue := QEnt.RecordCount;
      AGauge.Progress := 0;
    end;
    while not QEnt.Eof do
    begin
      ExecDML(
        'INSERT INTO usuario_ent (usucod, entcod, UsuEntRelacAvulso) VALUES (' +
        QuotedStr(UsuarioID) + ', ' +
        QuotedStr(QEnt.FieldByName('entcod').AsString) + ', ' +
        QuotedStr('Sim') + ')');
      if Assigned(AGauge) then AGauge.AddProgress(1);
      QEnt.Next;
    end;
  finally
    QEnt.Free;
  end;
end;
// ---------------------------------------------------------------------------
// Inserção de Categoria — Grupo
// ---------------------------------------------------------------------------
procedure TEntidadeService.InserirCategoriaGrupo(
  const GrupoID, CategCod: string; AGauge: TGauge);
var
  QUsu, QEnt, QSeq: TFDQuery;
  Seq: Integer;
  UsuID: string;
begin
  // Busca usuários ativos do grupo
  QUsu := ExecQuery(
    'SELECT grpu.usucod, grpu.grpusucod'                        + sLineBreak +
    'FROM   GRP_X_USUARIO grpu WITH(NOLOCK)'                    + sLineBreak +
    '       INNER JOIN usuario u WITH(NOLOCK) ON grpu.usucod = u.usucod' + sLineBreak +
    'WHERE  u.usustat    = ' + QuotedStr('Ativo')               + sLineBreak +
    '  AND  grpu.grpusucod = ' + QuotedStr(GrupoID));
  try
    if QUsu.IsEmpty then Exit;
    if Assigned(AGauge) then
    begin
      AGauge.MaxValue := QUsu.RecordCount;
      AGauge.Progress := 0;
    end;
    // ------- Insere categoria no grupo (categ_usuario) -------
    ExecDML('SET IDENTITY_INSERT dbo.categ_usuario ON');
    try
      QSeq := ExecQuery(
        'SELECT ISNULL(MAX(categususeq), 0) + 1 AS sequencia FROM categ_usuario');
      try
        Seq := QSeq.FieldByName('sequencia').AsInteger;
      finally
        QSeq.Free;
      end;
      // Insere linha do grupo (usucod = NULL)
      if ExecQuery(
        'SELECT 1 FROM categ_usuario' + sLineBreak +
        'WHERE  categcodestr = ' + QuotedStr(CategCod) + sLineBreak +
        '  AND  grpusucod = '    + QuotedStr(GrupoID)).IsEmpty then
      begin
        ExecDML(
          'INSERT INTO categ_usuario ' +
          '(categcodestr, categususeq, usucod, grpusucod, ' +
          ' CategUsuDirAcesso, CategUsuDirInclui, CategUsuDirExclui, ' +
          ' CategUsuDirAltera, CategUsuDirConsulta)' + sLineBreak +
          'VALUES (' + QuotedStr(CategCod) + ', ' + IntToStr(Seq) +
          ', NULL, ' + QuotedStr(GrupoID) +
          ', ' + QuotedStr('T') + ', ' + QuotedStr('T') +
          ', ' + QuotedStr('T') + ', ' + QuotedStr('T') +
          ', ' + QuotedStr('T') + ')');
        // Insere linha por usuário
        QUsu.First;
        while not QUsu.Eof do
        begin
          UsuID := QUsu.FieldByName('usucod').AsString;
          QSeq := ExecQuery(
            'SELECT ISNULL(MAX(categususeq), 0) + 1 AS sequencia FROM categ_usuario');
          try
            Seq := QSeq.FieldByName('sequencia').AsInteger;
          finally
            QSeq.Free;
          end;
          ExecDML(
            'INSERT INTO categ_usuario ' +
            '(categcodestr, categususeq, usucod, grpusucod, ' +
            ' CategUsuDirAcesso, CategUsuDirInclui, CategUsuDirExclui, ' +
            ' CategUsuDirAltera, CategUsuDirConsulta)' + sLineBreak +
            'VALUES (' + QuotedStr(CategCod) + ', ' + IntToStr(Seq) +
            ', ' + QuotedStr(UsuID) + ', NULL' +
            ', ' + QuotedStr('T') + ', ' + QuotedStr('T') +
            ', ' + QuotedStr('T') + ', ' + QuotedStr('T') +
            ', ' + QuotedStr('T') + ')');
          QUsu.Next;
        end;
      end;
    finally
      ExecDML('SET IDENTITY_INSERT dbo.categ_usuario OFF');
    end;
    // ------- Insere em usuario_categ e usuario_ent por usuário -------
    QUsu.First;
    while not QUsu.Eof do
    begin
      UsuID := QUsu.FieldByName('usucod').AsString;
      if ExecQuery(
        'SELECT 1 FROM usuario_categ' + sLineBreak +
        'WHERE  categcodestr = ' + QuotedStr(CategCod) + sLineBreak +
        '  AND  usucod = '       + QuotedStr(UsuID)).IsEmpty then
      begin
        ExecDML(
          'INSERT INTO usuario_categ (usucod, categcodestr, UsuCategTodasEnt) VALUES (' +
          QuotedStr(UsuID) + ', ' + QuotedStr(CategCod) + ', ' + QuotedStr('Sim') + ')');
      end;
      QEnt := ExecQuery(
        'SELECT ec.entcod'                                       + sLineBreak +
        'FROM   ent_categ ec WITH(NOLOCK)'                       + sLineBreak +
        'WHERE  ec.categcodestr = ' + QuotedStr(CategCod)        + sLineBreak +
        '  AND  ec.entcod NOT IN ('                              + sLineBreak +
        '       SELECT entcod FROM usuario_ent'                  + sLineBreak +
        '       WHERE  usucod = ' + QuotedStr(UsuID) + ')');
      try
        while not QEnt.Eof do
        begin
          ExecDML(
            'INSERT INTO usuario_ent (usucod, entcod, UsuEntRelacAvulso) VALUES (' +
            QuotedStr(UsuID) + ', ' +
            QuotedStr(QEnt.FieldByName('entcod').AsString) + ', ' +
            QuotedStr('Sim') + ')');
          if Assigned(AGauge) then AGauge.AddProgress(1);
          QEnt.Next;
        end;
      finally
        QEnt.Free;
      end;
      QUsu.Next;
    end;
  finally
    QUsu.Free;
  end;
end;
// ---------------------------------------------------------------------------
function TEntidadeService.BuscarTodasCategorias: TFDQuery;
begin
  Result := ExecQuery(
    'SELECT cat.categcodestr, cat.categnome FROM categoria cat WITH(NOLOCK)' +
    ' ORDER BY cat.categcodestr ASC');
end;
// ===========================================================================
//  Tfrmrelacentidades — View
// ===========================================================================
procedure Tfrmrelacentidades.FormCreate(Sender: TObject);
begin
  FService := TEntidadeService.Create(modulo_dados.fdbanco);
end;
// ---------------------------------------------------------------------------
procedure Tfrmrelacentidades.FormDestroy(Sender: TObject);
begin
  FService.Free;
end;
// ---------------------------------------------------------------------------
procedure Tfrmrelacentidades.FormActivate(Sender: TObject);
begin
  try
    FService.CarregarUsuariosAtivos(cbousuario.Items);
    if cbousuario.Items.Count = 0 then
    begin
      MessageDlg('Não há usuários cadastrados na base!', mtError, [mbOK], 0);
      Exit;
    end;
    FService.CarregarGrupos(cbogrupo.Items);
    if cbogrupo.Items.Count = 0 then
    begin
      MessageDlg('Não há grupos de usuários cadastrados!', mtError, [mbOK], 0);
      Exit;
    end;
    ConfigurarStatusBar;
    OcultarPainelInsercao;
  except
    on E: Exception do
      MessageDlg('Erro ao carregar dados: ' + E.Message, mtError, [mbOK], 0);
  end;
end;
// ---------------------------------------------------------------------------
procedure Tfrmrelacentidades.ConfigurarStatusBar;
begin
  StatusBar1.Panels[0].Text := 'Banco Apolo';
  StatusBar1.Panels[1].Text := configura_statusbar('a');
end;
// ---------------------------------------------------------------------------
procedure Tfrmrelacentidades.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Action := caFree;
end;
// ---------------------------------------------------------------------------
procedure Tfrmrelacentidades.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
  if Key = VK_F10 then
    spbsair.Click;
end;
// ---------------------------------------------------------------------------
procedure Tfrmrelacentidades.spbsairClick(Sender: TObject);
begin
  Close;
end;
// ---------------------------------------------------------------------------
// Helpers da View
// ---------------------------------------------------------------------------
function Tfrmrelacentidades.OpcaoAtual: TGridOpcao;
begin
  if (cbousuario.Text = '') and (cbogrupo.Text <> '') then
    Result := goGrupo
  else
    Result := goUsuario;
end;
// ---------------------------------------------------------------------------
procedure Tfrmrelacentidades.LimparGrid;
begin
  LimpaStringGrid(gridUsuarioRelac);
end;
// ---------------------------------------------------------------------------
procedure Tfrmrelacentidades.AtualizarGrid;
begin
  Gauge1.Progress := 0;
  case OpcaoAtual of
    goUsuario: FService.CarregarGridPorUsuario(cbousuario.Text,
                                               gridUsuarioRelac, Gauge1);
    goGrupo  : FService.CarregarGridPorGrupo(cbogrupo.Text,
                                             gridUsuarioRelac, Gauge1);
  end;
  gridUsuarioRelac.Refresh;
end;
// ---------------------------------------------------------------------------
function Tfrmrelacentidades.CategSelecionada: string;
begin
  // Coluna 0 para usuário, coluna 1 para grupo
  if OpcaoAtual = goGrupo then
    Result := gridUsuarioRelac.Cells[1, gridUsuarioRelac.Row]
  else
    Result := gridUsuarioRelac.Cells[0, gridUsuarioRelac.Row];
end;
// ---------------------------------------------------------------------------
procedure Tfrmrelacentidades.ExibirPainelInsercao;
begin
  grpinserecateg.Left    := 368;
  grpinserecateg.Top     := 72;
  grpinserecateg.Visible := True;
  lblcategcodestr.SetFocus;
end;
// ---------------------------------------------------------------------------
procedure Tfrmrelacentidades.OcultarPainelInsercao;
begin
  grpinserecateg.Visible := False;
  lblcategcodestr.Clear;
end;
// ---------------------------------------------------------------------------
// Eventos do grid
// ---------------------------------------------------------------------------
procedure Tfrmrelacentidades.gridUsuarioRelacEnter(Sender: TObject);
begin
  AtualizarGrid;
end;
// ---------------------------------------------------------------------------
procedure Tfrmrelacentidades.gridUsuarioRelacDblClick(Sender: TObject);
var
  Categ: string;
begin
  if MessageDlg('Confirma o relacionamento deste usuário a todas as entidades desta categoria?',
                mtConfirmation, [mbYes, mbNo], 0) <> idYes then
  begin
    cbousuario.SetFocus;
    Exit;
  end;
  Categ := CategSelecionada;
  if Categ = '' then Exit;
  try
    case OpcaoAtual of
      goUsuario: FService.RelacionarCategoriasDoUsuario(cbousuario.Text, Categ, Gauge1);
      goGrupo  : FService.RelacionarCategoriasDoGrupo(cbogrupo.Text, Categ, Gauge1);
    end;
    AtualizarGrid;
  except
    on E: Exception do
      MessageDlg('Erro ao relacionar: ' + E.Message, mtError, [mbOK], 0);
  end;
end;
// ---------------------------------------------------------------------------
procedure Tfrmrelacentidades.gridUsuarioRelacKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
var
  Categ: string;
begin
  if Key = VK_DELETE then
  begin
    if MessageDlg('Confirma a remoção do vínculo com a categoria?',
                  mtConfirmation, [mbYes, mbNo], 0) <> idYes then Exit;
    Categ := CategSelecionada;
    if Categ = '' then Exit;
    try
      case OpcaoAtual of
        goUsuario: FService.RemoverRelacionamentoUsuario(cbousuario.Text, Categ, Gauge1);
        goGrupo  : FService.RemoverRelacionamentoGrupo(cbogrupo.Text, Categ, Gauge1);
      end;
      AtualizarGrid;
      cbousuario.SetFocus;
    except
      on E: Exception do
        MessageDlg('Erro ao remover: ' + E.Message, mtError, [mbOK], 0);
    end;
  end;
  if Key = VK_INSERT then
    ExibirPainelInsercao;
end;
// ---------------------------------------------------------------------------
procedure Tfrmrelacentidades.cbousuarioEnter(Sender: TObject);
begin
  if cbogrupo.Text <> '' then
    FService.CarregarUsuariosDoGrupo(cbogrupo.Text, cbousuario.Items);
end;
// ---------------------------------------------------------------------------
procedure Tfrmrelacentidades.spbuscaClick(Sender: TObject);
var
  QCat: TFDQuery;
begin
  if (cbousuario.Text = '') and (cbogrupo.Text = '') then Exit;
  try
    QCat := FService.BuscarTodasCategorias;
    try
      if QCat.IsEmpty then
      begin
        MessageDlg('Não há categorias disponíveis!', mtWarning, [mbOK], 0);
        Exit;
      end;
      Application.CreateForm(TfrmConsulta3, frmConsulta3);
      with frmConsulta3, modulo_dados do
      begin
        controle    := 'GEOUSUARIOENTIDADECATEGORIA';
        sqlrec1     := QCat.SQL.Text;
        dtsfdquerysql4.DataSet := QCat;
        gridconsulta.DataSource := dtsfdquerysql4;
        carrega_campo_dinamico(Qcat);
        gridconsulta.Refresh;
        ShowModal;
      end;
    finally
      QCat.Free;
    end;
  except
    on E: Exception do
      MessageDlg('Erro na consulta: ' + E.Message, mtError, [mbOK], 0);
  end;
end;
// ---------------------------------------------------------------------------
procedure Tfrmrelacentidades.btncancelarClick(Sender: TObject);
begin
  OcultarPainelInsercao;
  gridUsuarioRelac.SetFocus;
end;
// ---------------------------------------------------------------------------
procedure Tfrmrelacentidades.btninserecategClick(Sender: TObject);
begin
  if lblcategcodestr.Text = '' then
  begin
    MessageDlg('Informe o código da categoria!', mtWarning, [mbOK], 0);
    lblcategcodestr.SetFocus;
    Exit;
  end;
  try
    case OpcaoAtual of
      goUsuario: FService.InserirCategoriaUsuario(cbousuario.Text,
                                                  lblcategcodestr.Text, Gauge1);
      goGrupo  : FService.InserirCategoriaGrupo(cbogrupo.Text,
                                                lblcategcodestr.Text, Gauge1);
    end;
    OcultarPainelInsercao;
    AtualizarGrid;
  except
    on E: Exception do
      MessageDlg('Erro ao inserir categoria: ' + E.Message, mtError, [mbOK], 0);
  end;
end;
// ---------------------------------------------------------------------------
procedure Tfrmrelacentidades.lblcategcodestrKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then
    spbusca.Click;
end;
end.

