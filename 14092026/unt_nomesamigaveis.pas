unit unt_nomesamigaveis;
{
  MÓDULO: Definição de Nomes Amigáveis
  Tela auxiliar usada por unt_configperfil para permitir que o admin
  edite o nome amigável e a categoria de cada objeto do sistema.

  IMPORTANTE: Este unit foi extraído de unt_configperfil.pas, onde a classe
  TfrmNomesAmigaveis estava declarada incorretamente (duas classes de form
  em um único unit, cujo {$R *.dfm só conseguia vincular a UM dos dois
  arquivos .dfm). Isso fazia com que o recurso de unt_nomesamigaveis.dfm
  nunca fosse embutido no executável, causando falha ao instanciar o form.
}
interface
uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, Grids,
  FireDAC.Comp.Client, FireDAC.Stan.Param;

type
  TfrmNomesAmigaveis = class(TForm)
    lblInstrucao : TLabel;
    grdObjetos   : TStringGrid;   // Colunas: Objeto Técnico | Nome Amigável | Categoria
    btnSalvar    : TButton;
    btnFechar    : TButton;
    btnGerarSugestao : TButton;   // Sugere nomes amigáveis automaticamente
    procedure FormCreate(Sender: TObject);
    procedure btnSalvarClick(Sender: TObject);
    procedure btnFecharClick(Sender: TObject);
    procedure btnGerarSugestaoClick(Sender: TObject);
    procedure grdObjetosSetEditText(Sender: TObject; ACol, ARow: Integer; const Value: string);
  private
    FAlterado : Boolean;
    procedure CarregarObjetos;
    procedure SalvarAlteracoes;
    function  SugerirNomeAmigavel(const ANomeTecnico: string): string;
  end;

var
  frmNomesAmigaveis : TfrmNomesAmigaveis;

implementation

uses
  unt_dados, funcoes;

{$R *.dfm}

{ ══════════════════════════════════════════════════════════════════════ }
{  TFRMNOMESAMIGAVEIS — Tela de definição de nomes amigáveis             }
{ ══════════════════════════════════════════════════════════════════════ }
procedure TfrmNomesAmigaveis.FormCreate(Sender: TObject);
begin
  FAlterado := False;
  { Configura o grid }
  grdObjetos.ColCount  := 3;
  grdObjetos.RowCount  := 5;
  grdObjetos.FixedRows := 1;
  grdObjetos.Options   := grdObjetos.Options + [goEditing];
  { Cabeçalhos das colunas }
  grdObjetos.Cells[0, 0] := 'Objeto Técnico (somente leitura)';
  grdObjetos.Cells[1, 0] := 'Nome Amigável (editável)';
  grdObjetos.Cells[2, 0] := 'Categoria (editável)';
  { Coluna 0 somente leitura — implementada via goColSizing / OnSelectCell }
  grdObjetos.ColWidths[0] := 200;
  grdObjetos.ColWidths[1] := 220;
  grdObjetos.ColWidths[2] := 140;
  CarregarObjetos;
end;

procedure TfrmNomesAmigaveis.CarregarObjetos;
var
  i : Integer;
begin
  with modulo_dados do
  begin
    sql:='SELECT nome_objeto, nome_amigavel, ISNULL(categoria,''Geral'') AS categoria ';
    sql:=sql+'  FROM USER_geoapolo_objetos ORDER BY nome_amigavel';
    fdquerysql.Close;
    fdquerysql.SQL.Clear;
    fdquerysql.SQL.Text := sql;
    if executaracao(fdquerysql,fdbanco, false, dtsfdquerysql) then
       begin
       end;
    grdObjetos.RowCount := fdquerysql.RecordCount + 1; // +1 para o header
    i := 2;
    grdobjetos.Cells[0,1]:='Nome Objetos';
    grdobjetos.Cells[1,1]:='Nome Amigável';
    grdobjetos.Cells[2,1]:='Categoria';
    fdquerysql.First;
    while not fdquerysql.Eof do
    begin
      grdObjetos.Cells[0, i] := fdquerysql.FieldByName('nome_objeto').AsString;
      grdObjetos.Cells[1, i] := fdquerysql.FieldByName('nome_amigavel').AsString;
      grdObjetos.Cells[2, i] := fdquerysql.FieldByName('categoria').AsString;
      Inc(i);
      fdquerysql.Next;
    end;
  end;
end;

procedure TfrmNomesAmigaveis.grdObjetosSetEditText(Sender: TObject;
  ACol, ARow: Integer; const Value: string);
begin
  { Coluna 0 (nome técnico) é somente leitura }
  if ACol = 0 then Exit;
  FAlterado := True;
end;

procedure TfrmNomesAmigaveis.SalvarAlteracoes;
var
  i : Integer;
begin
  with modulo_dados do
  begin
    for i := 1 to grdObjetos.RowCount - 1 do
    begin
      if Trim(grdObjetos.Cells[0, i]) = '' then Continue;
      if Trim(grdObjetos.Cells[1, i]) = '' then
      begin
        MessageDlg('O nome amigável não pode ficar em branco (linha ' + IntToStr(i) + ').',
                   mtWarning, [mbOK], 0);
        grdObjetos.Row := i;
        grdObjetos.Col := 1;
        Exit;
      end;
      sql:='UPDATE USER_geoapolo_objetos  SET nome_amigavel = :pnomeamigavel, categoria = :pnomecategoria';
      sql:=sql+' WHERE nome_objeto = :pnomeobjeto';
      fdquerysql3.Close;
      fdquerysql3.SQL.Clear;
      fdquerysql3.SQL.Text := sql;
      fdquerysql3.ParamByName('pnomeamigavel').AsString :=Trim(grdObjetos.Cells[1, i]);
      fdquerysql3.ParamByName('pnomecategoria').AsString :=Trim(grdObjetos.Cells[2, i]);
      fdquerysql3.ParamByName('pnomeobjeto').AsString :=grdObjetos.Cells[0, i];
      if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
         begin

         end;
    end;
  end;
  FAlterado := False;
  MessageDlg('Nomes amigáveis salvos com sucesso.', mtInformation, [mbOK], 0);
end;

function TfrmNomesAmigaveis.SugerirNomeAmigavel(const ANomeTecnico: string): string;
{
  Heurística simples para gerar sugestão de nome amigável a partir do nome técnico.
  Ex: "frmprincipal.btnEmitirNFe"   → "Emitir NF-e"
      "frmprincipal.mnuCadastros"   → "Cadastros"
      "frmprincipal.tbsheetFiscal"  → "Fiscal"
  Prefixos de controle reconhecidos: btn, mnu, tbs, pnl, lbl, cbo, edt, chk, rbtn, frm
}
const
  PREFIXOS : array[0..10] of string = (
    'btn','mnu','tbs','tbsheet','pnl','lbl','cbo','edt','chk','rbtn','frm'
  );
var
  sNome  : string;
  sPartes: TStringList;
  sParte : string;
  i      : Integer;
begin
  { Pega apenas o nome do componente após o ponto }
  sNome := ANomeTecnico;
  i := LastDelimiter('.', sNome);
  if i > 0 then
    sNome := Copy(sNome, i + 1, MaxInt);
  sNome := LowerCase(sNome);
  { Remove prefixo de controle }
  for sParte in PREFIXOS do
    if Pos(sParte, sNome) = 1 then
    begin
      Delete(sNome, 1, Length(sParte));
      Break;
    end;
  { Separa CamelCase em palavras }
  sPartes := TStringList.Create;
  try
    sPartes.Add('');
    for i := 1 to Length(sNome) do
    begin
      if (i > 1) and CharInSet(sNome[i], ['A'..'Z']) then
        sPartes.Add(sNome[i])
      else
        sPartes[sPartes.Count - 1] := sPartes[sPartes.Count - 1] + sNome[i];
    end;
    Result := '';
    for sParte in sPartes do
      if Trim(sParte) <> '' then
        Result := Result + ' ' + UpperCase(sParte[1]) + Copy(sParte, 2, MaxInt);
    Result := Trim(Result);
  finally
    sPartes.Free;
  end;
  if Result = '' then
    Result := ANomeTecnico;
end;

procedure TfrmNomesAmigaveis.btnGerarSugestaoClick(Sender: TObject);
{
  Preenche automaticamente a coluna "Nome Amigável" para linhas
  que ainda têm o nome técnico como nome amigável (não foram editadas).
}
var
  i         : Integer;
  sNomeTec  : string;
  sSugestao : string;
begin
  if MessageDlg('Gerar sugestões automáticas apenas para itens não editados?',
                mtConfirmation, [mbYes, mbNo], 0) <> idYes then Exit;
  for i := 1 to grdObjetos.RowCount - 1 do
  begin
    sNomeTec := grdObjetos.Cells[0, i];
    if sNomeTec = '' then Continue;
    { Só sugere se o nome amigável for idêntico ao técnico (nunca foi editado) }
    if grdObjetos.Cells[1, i] = sNomeTec then
    begin
      sSugestao := SugerirNomeAmigavel(sNomeTec);
      grdObjetos.Cells[1, i] := sSugestao;
      FAlterado := True;
    end;
  end;
end;

procedure TfrmNomesAmigaveis.btnSalvarClick(Sender: TObject);
begin
  SalvarAlteracoes;
end;

procedure TfrmNomesAmigaveis.btnFecharClick(Sender: TObject);
begin
  if FAlterado then
    if MessageDlg('Há alterações não salvas. Deseja salvar antes de fechar?',
                  mtConfirmation, [mbYes, mbNo], 0) = idYes then
      SalvarAlteracoes;
  Close;
end;

end.
