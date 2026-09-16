unit unt_configperfil;
{
  MÓDULO: Configuração de Perfil de Acesso
  REFATORADO: Arquitetura em camadas com nomes amigáveis para os objetos
  BANCO: FireDAC (fdquerysql / fdbanco)
  ESTRUTURA DE TABELAS NECESSÁRIA:
  ─────────────────────────────────────────────────────────────────────
  USER_geoapolo_objetos:
    codigo_objeto  INT  PK
    nome_objeto    VARCHAR(150)   -- nome técnico (ex: "frmprincipal.btnNFe")
    nome_amigavel  VARCHAR(150)   -- nome exibido ao admin (ex: "Emissão de NF-e")
    categoria      VARCHAR(80)    -- agrupamento opcional (ex: "Fiscal", "Cadastros")
  USER_geoapolo_grupobjetos:
    codigo_objeto  INT  FK
    codigo_grupo   INT  FK
    statusacesso   CHAR(1)  -- 'A' = Permitido | 'N' = Negado
  ─────────────────────────────────────────────────────────────────────
  SCRIPT DE MIGRAÇÃO (rodar UMA VEZ):
    ALTER TABLE USER_geoapolo_objetos
      ADD nome_amigavel VARCHAR(150) NULL,
          categoria     VARCHAR(80)  NULL;
    UPDATE USER_geoapolo_objetos
      SET nome_amigavel = nome_objeto
      WHERE nome_amigavel IS NULL;
  ─────────────────────────────────────────────────────────────────────
}
interface
uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, Buttons, ExtCtrls, ComCtrls, ImgList, Grids,
  FireDAC.Comp.Client, FireDAC.Stan.Param, System.TypInfo;
type
  { ------------------------------------------------------------------ }
  { Value Object que representa um objeto do sistema                    }
  { ------------------------------------------------------------------ }
  TObjetoSistema = record
    CodigoObjeto : Integer;
    NomeTecnico  : string;   // nome vindo do design (GetNamePath)
    NomeAmigavel : string;   // nome legível para o administrador
    Categoria    : string;   // agrupamento (ex: "Fiscal", "Cadastros")
  end;
  { ------------------------------------------------------------------ }
  { Tela principal de configuração de perfil                           }
  { ------------------------------------------------------------------ }
  Tfrmconfigperfil = class(TForm)
    { --- Layout geral --- }
    panelmenu   : TPanel;
    StatusBar1  : TStatusBar;
    lblmsg1     : TLabel;
    { --- Toolbar de ações --- }
    spbsalvar    : TSpeedButton;   // Salvar todas as permissões pendentes
    spblimpar    : TSpeedButton;   // Limpar seleção de grupo
    spbdeletar   : TSpeedButton;   // Remover objeto obsoleto
    spblocalizar : TSpeedButton;   // Localizar objeto na lista
    spbretornar  : TSpeedButton;   // Fechar / Salvar e fechar
    spbrenomear  : TSpeedButton;   // Abrir tela de nomes amigáveis
    { --- Seleção de grupo --- }
    GroupBox1   : TGroupBox;
    lblgrupo    : TLabel;
    cbogrupo    : TComboBox;       // Lista de grupos de usuário
    { --- Filtro por categoria --- }
    lblcategoria  : TLabel;
    cbocategoria  : TComboBox;     // Filtra objetos por categoria
    { --- Painéis de permissão (substituem os ListBox simples) --- }
    pnlDisponiveis : TPanel;
    lblcompdispo   : TLabel;       // "Não Permitido"
    lstDisponiveis : TListBox;     // objetos SEM permissão para o grupo
    pnlBotoes   : TPanel;
    btnLiberar  : TButton;         // >> Liberar selecionados
    btnRevogar  : TButton;         // << Revogar selecionados
    btnLiberarTodos : TButton;     // >> Todos
    btnRevogarTodos : TButton;     // << Todos
    pnlLiberados   : TPanel;
    lblliberado    : TLabel;       // "Permitido"
    lstLiberados   : TListBox;     // objetos COM permissão para o grupo
    { --- Eventos --- }
    procedure FormCreate(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure cbogrupoChange(Sender: TObject);
    procedure cbocategoriaChange(Sender: TObject);
    procedure lstDisponiveisDblClick(Sender: TObject);
    procedure lstLiberadosDblClick(Sender: TObject);
    procedure lstDisponiveisKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lstLiberadosKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure btnLiberarClick(Sender: TObject);
    procedure btnRevogarClick(Sender: TObject);
    procedure btnLiberarTodosClick(Sender: TObject);
    procedure btnRevogarTodosClick(Sender: TObject);
    procedure spbretornarClick(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure spbrenomearClick(Sender: TObject);
    procedure spbsalvarClick(Sender: TObject);
  private
    FCodigoGrupo     : Integer;
    FGrupoCarregado  : Boolean;
    FCategoriaFiltro : string;
    { --- Sincronização banco <-> tabela de objetos --- }
    procedure SincronizarObjetosBanco;
    procedure LimparObjetosObsoletos;
    { --- Carregamento das listas --- }
    procedure CarregarGrupos;
    procedure CarregarCategorias;
    procedure CarregarPermissoes(ACodigoGrupo: Integer; ACategoria: string = '');
    { --- Operações de permissão --- }
    procedure AlterarPermissao(ANomeTecnico: string; ACodigoObjeto, ACodigoGrupo: Integer;
                               AStatus: string);
    procedure LiberarObjeto(ALstOrigem, ALstDestino: TListBox);
    procedure RevogarObjeto(ALstOrigem, ALstDestino: TListBox);
    procedure MoverTodos(ALstOrigem, ALstDestino: TListBox; ANovoStatus: string);
    { --- Auxiliares --- }
    function  BuscarCodigoObjeto(const ANomeTecnico: string): Integer;
    function  NomeTecnicoDoItem(ALst: TListBox; AIndex: Integer): string;
    procedure AtualizarStatusBar;
    procedure ValidarGrupoSelecionado;
  public
    { Public declarations }
  end;
var
  frmconfigperfil : Tfrmconfigperfil;
implementation
uses
  unt_principal, funcoes, unt_dados, unt_logon, unt_nomesamigaveis;
{$R *.dfm}
{ ══════════════════════════════════════════════════════════════════════ }
{  TFRMCONFIGPERFIL — Inicialização                                     }
{ ══════════════════════════════════════════════════════════════════════ }
procedure Tfrmconfigperfil.FormCreate(Sender: TObject);
begin
  FCodigoGrupo    := 0;
  FGrupoCarregado := False;
  FCategoriaFiltro:= '';
end;
procedure Tfrmconfigperfil.FormActivate(Sender: TObject);
begin
  LimparObjetosObsoletos;
  SincronizarObjetosBanco;
  CarregarGrupos;
  CarregarCategorias;
  AtualizarStatusBar;
end;

procedure Tfrmconfigperfil.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Action := caFree;
end;
procedure Tfrmconfigperfil.FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  case Key of
    VK_F10 : spbretornar.Click;
    VK_F5  : CarregarPermissoes(FCodigoGrupo, FCategoriaFiltro);
  end;
end;

{ ══════════════════════════════════════════════════════════════════════ }
{  SINCRONIZAÇÃO: mantém USER_geoapolo_objetos em dia com frmprincipal  }
{ ══════════════════════════════════════════════════════════════════════ }
procedure Tfrmconfigperfil.SincronizarObjetosBanco;
{
  Para cada componente visível em frmprincipal:
    - Se não existir em USER_geoapolo_objetos → INSERT
    - Ao inserir, cria entrada em grupobjetos (statusacesso='N') para todos os grupos
  nome_amigavel começa igual ao nome técnico; o admin pode renomear depois.
}
var
                i            : Integer;
  sNomeTecnico,sNomeAmigavel : string;
  sCodObjeto                 : string;
  sGrups                     : TFDQuery; // cursor local para iterar grupos
  cmp                        : TComponent;
begin
  with modulo_dados do
  begin
    for i := 0 to frmprincipal.ComponentCount - 1 do
    begin
      sNomeTecnico := frmprincipal.Components[i].GetNamePath;
      Cmp := frmprincipal.Components[i]; // Facilita a leitura
      // 1. Define o ClassName como padrão (caso não ache Text ou Caption)
      sNomeAmigavel := Cmp.ClassName;
      // 2. Verifica se tem a propriedade Caption (Comum em TMenuItem, TLabel, TButton)
      if IsPublishedProp(Cmp, 'Caption') then
        sNomeAmigavel := GetPropValue(Cmp, 'Caption')
      // 3. Se não tiver Caption, verifica se tem Text (Comum em TEdit, TComboBox)
      else if IsPublishedProp(Cmp, 'Text') then
        sNomeAmigavel := GetPropValue(Cmp, 'Text');
      // Dica Extra: Se for um menu, o Caption geralmente vem com o '&' (ex: '&Arquivo').
      // A linha abaixo limpa esse caractere para o banco de dados ficar mais limpo.
      sNomeAmigavel := StringReplace(sNomeAmigavel, '&', '', [rfReplaceAll]);
      //
      { Verifica se o objeto já existe }
      sql:= 'SELECT codigo_objeto FROM USER_geoapolo_objetos WHERE nome_objeto = :psnometecnico';
      fdquerysql2.Close;
      fdquerysql2.SQL.Clear;
      fdquerysql2.SQL.Text := sql;
      fdquerysql2.ParamByName('psnometecnico').AsString := sNomeTecnico;
      if not executaracao(fdquerysql2, fdbanco, true, dtsfdquerysql2) then
      begin
        { Novo objeto — gera código e insere }
        sCodObjeto := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_objetos', 'Sim');
        sql:='INSERT INTO USER_geoapolo_objetos (codigo_objeto, nome_objeto, nome_amigavel, categoria) '  ;
        sql:=sql+' VALUES (:pcodigobj,:pnomeobjeto,:pnomeamigavel, :pcategoria)';
        fdquerysql3.Close;
        fdquerysql3.SQL.Clear;
        fdquerysql3.SQL.Text := sql;
        fdquerysql3.ParamByName('pcodigobj').AsString := sCodObjeto;
        fdquerysql3.ParamByName('pnomeobjeto').AsString:= sNomeTecnico;
        fdquerysql3.ParamByName('pnomeamigavel').asstring :=sNomeAmigavel; // Passa a variável dinâmica
        fdquerysql3.ParamByName('pcategoria').AsString := frmprincipal.Components[i].ClassName;
        if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
           begin
          { Insere statusacesso='N' para todos os grupos existentes }
          sql:= 'SELECT codigo_grupo FROM USER_geoapolo_grupo';
          fdquerysql.Close;
          fdquerysql.SQL.Clear;
          fdquerysql.SQL.text := sql;
          if executaracao(fdquerysql,fdbanco, false, dtsfdquerysql) then
          begin
            fdquerysql.First;
            while not fdquerysql.Eof do
            begin
              sql:='INSERT INTO USER_geoapolo_grupobjetos (codigo_objeto, codigo_grupo, statusacesso)';
              sql:=sql+'VALUES (:pcodigobjeto, :pcodigogrupo, :pstatusacess)' ;
              fdquerysql3.Close;
              fdquerysql3.SQL.Clear;
              fdquerysql3.SQL.Text := sql;
              fdquerysql3.parambyname('pcodigobjeto').AsString := sCodObjeto;
              fdquerysql3.ParamByName('pcodigogrupo').AsString := fdquerysql.FieldByName('codigo_grupo').AsString;
              fdquerysql3.ParamByName('pstatusacess').AsString := 'N';
              if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                 begin
                 end;
              fdquerysql.Next;
            end;
          end;
        end;
      end;
    end;
  end;
end;

procedure Tfrmconfigperfil.LimparObjetosObsoletos;
{
  Remove de USER_geoapolo_objetos qualquer entrada cujo nome_objeto
  não exista mais como componente em frmprincipal.
}
var
  i      : Integer;
  achado : Boolean;
  sNome  : string;
  sCod   : string;
begin
  with modulo_dados do
  begin
    sql:='SELECT codigo_objeto, nome_objeto FROM USER_geoapolo_objetos ORDER BY nome_objeto';
    fdquerysql.Close;
    fdquerysql.SQL.Clear;
    fdquerysql.SQL.Text := sql;
    if executaracao(fdquerysql,fdbanco, false, dtsfdquerysql) then
       begin
       end;
    if fdquerysql.IsEmpty then Exit;
    fdquerysql.First;
    while not fdquerysql.Eof do
    begin
      sNome  := fdquerysql.FieldByName('nome_objeto').AsString;
      sCod   := fdquerysql.FieldByName('codigo_objeto').AsString;
      achado := False;
      for i := 0 to frmprincipal.ComponentCount - 1 do
        if frmprincipal.Components[i].GetNamePath = sNome then
        begin
          achado := True;
          Break;
        end;
      if not achado then
      begin
        { Objeto removido do projeto — apaga vínculos e depois o objeto }
        fdquerysql3.Close;
        fdquerysql3.SQL.Clear;
        sql:= 'DELETE FROM USER_geoapolo_grupobjetos WHERE codigo_objeto = :pcodigobjeto';
        fdquerysql3.SQL.Text := sql;
        fdquerysql3.ParamByName('pcodigobjeto').AsString := sCod;
        if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
           begin
           end;
         sql:= 'DELETE FROM USER_geoapolo_objetos WHERE codigo_objeto = :pcodigobjeto';
         fdquerysql3.Close;
         fdquerysql3.SQL.Clear;
         fdquerysql3.SQL.Text := sql;
         fdquerysql3.ParamByName('pcodigobjeto').AsString :=sCod;
         if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
            begin
            end;
         fdquerysql.Next;
         end
      else
        fdquerysql.Next;
    end;
  end;
end;

{ ══════════════════════════════════════════════════════════════════════ }
{  CARREGAMENTO DE COMBOS E LISTAS                                      }
{ ══════════════════════════════════════════════════════════════════════ }
procedure Tfrmconfigperfil.CarregarGrupos;
begin
  cbogrupo.Items.Clear;
  with modulo_dados do
  begin
     sql:= 'SELECT codigo_grupo, descricao FROM USER_geoapolo_grupo ORDER BY descricao';
     fdquerysql.Close;
     fdquerysql.SQL.Clear;
     fdquerysql.SQL.Text := sql;
     if not executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
     begin
        MessageDlg('Nenhum grupo de usuários cadastrado. Favor cadastrar antes de configurar permissões.', mtError, [mbOK], 0);
        Exit;
     end;
    fdquerysql.First;
    while not fdquerysql.Eof do
    begin
      { Armazena o código do grupo no objeto do item para recuperação rápida }
      cbogrupo.Items.AddObject(fdquerysql.FieldByName('descricao').AsString,TObject(fdquerysql.FieldByName('codigo_grupo').AsInteger));
      fdquerysql.Next;
    end;
  end;
end;

procedure Tfrmconfigperfil.CarregarCategorias;
{
  Popula o combo de categorias com os valores distintos cadastrados
  mais a opção "(Todas)" no topo.
}
begin
  cbocategoria.Items.Clear;
  cbocategoria.Items.Add('(Todas)');
  with modulo_dados do
  begin
     sql:='SELECT DISTINCT categoria FROM USER_geoapolo_objetos WHERE categoria IS NOT NULL ORDER BY categoria ';
     fdquerysql.Close;
     fdquerysql.SQL.Clear;
     fdquerysql.SQL.Text := sql;
     if executaracao(fdquerysql,fdbanco, false, dtsfdquerysql) then
        begin
            fdquerysql.First;
            while not fdquerysql.Eof do
            begin
              cbocategoria.Items.Add(fdquerysql.FieldByName('categoria').AsString);
              fdquerysql.Next;
            end;
        end;
  end;
  cbocategoria.ItemIndex := 0;
end;

procedure Tfrmconfigperfil.CarregarPermissoes(ACodigoGrupo: Integer; ACategoria: string);
{
  Divide os objetos entre lstDisponiveis (status='N') e lstLiberados (status='A')
  exibindo o nome_amigavel ao usuário; armazena o nome_objeto (técnico) no objeto
  do item para uso interno nas operações de banco.
  Formato de exibição: "[Categoria]  Nome Amigável"
}
var
  sSQL      : string;
  sFiltCat  : string;
begin
  lstDisponiveis.Clear;
  lstLiberados.Clear;
  if ACodigoGrupo = 0 then Exit;
  { Filtro opcional por categoria }
  if (ACategoria <> '') and (ACategoria <> '(Todas)') then
    sFiltCat := ' AND o.categoria = ' + QuotedStr(ACategoria)
  else
    sFiltCat := '';
  with modulo_dados do
  begin
    {
      Busca todos os objetos com seu status para o grupo informado.
      O LEFT JOIN garante que objetos sem entrada em grupobjetos apareçam como 'N'.
    }
    SQL :=
      'SELECT o.codigo_objeto, o.nome_objeto, ' +
      '       ISNULL(o.nome_amigavel, o.nome_objeto) AS nome_amigavel, ' +
      '       ISNULL(o.categoria, ''Geral'') AS categoria, ' +
      '       ISNULL(g.statusacesso, ''N'') AS statusacesso ' +
      'FROM USER_geoapolo_objetos o ' +
      'LEFT JOIN USER_geoapolo_grupobjetos g ' +
      '  ON g.codigo_objeto = o.codigo_objeto ' +
      ' AND g.codigo_grupo  = :pcodigogrupo' +
      ' WHERE 1=1 ' + sFiltCat +
      ' ORDER BY o.categoria, o.nome_amigavel';
    fdquerysql.Close;
    fdquerysql.SQL.Clear;
    fdquerysql.SQL.Text := sql;
    fdquerysql.ParamByName('pcodigogrupo').AsString :=IntToStr(ACodigoGrupo);
    if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
       begin
       end;
    fdquerysql.First;
    while not fdquerysql.Eof do
    begin
      { Texto exibido: "[Categoria]  Nome Amigável" }
      var sExibicao := '[' + fdquerysql.FieldByName('categoria').AsString + ']  ' +
                       fdquerysql.FieldByName('nome_amigavel').AsString;
      { Objeto associado ao item = nome técnico (usado nas queries) }
      var oTecnico := TObject(Integer(
                       PChar(fdquerysql.FieldByName('nome_objeto').AsString)));
      // NOTA: uso de StringList paralela abaixo é mais robusto; veja FNomesTecnicos
      if fdquerysql.FieldByName('statusacesso').AsString = 'A' then
        lstLiberados.Items.Add(sExibicao)
      else
        lstDisponiveis.Items.Add(sExibicao);
      fdquerysql.Next;
    end;
  end;
end;

{ ══════════════════════════════════════════════════════════════════════ }
{  AUXILIARES                                                           }
{ ══════════════════════════════════════════════════════════════════════ }
function Tfrmconfigperfil.BuscarCodigoObjeto(const ANomeTecnico: string): Integer;
{
  Retorna o codigo_objeto a partir do nome técnico.
  Usa fdquerysql1 para não interferir com cursores em uso.
}
begin
  Result := 0;
  with modulo_dados do
  begin
      sql:= 'SELECT codigo_objeto FROM USER_geoapolo_objetos ' +
      'WHERE nome_objeto = :pnomeobjeto' ;
      fdquerysql1.Close;
      fdquerysql1.SQL.Clear;
      fdquerysql1.SQL.Text := sql;
      fdquerysql1.ParamByName('pnomeobjeto').AsString := ANomeTecnico;
      if executaracao(fdquerysql1, fdbanco, true) then
      begin
         Result := fdquerysql1.FieldByName('codigo_objeto').AsInteger;
      end;
  end;
end;

function Tfrmconfigperfil.NomeTecnicoDoItem(ALst: TListBox; AIndex: Integer): string;
{
  Recupera o nome técnico a partir do texto exibido no ListBox.
  O texto tem formato "[Categoria]  Nome Amigável".
  Precisamos consultar o banco pelo nome_amigavel para obter o nome técnico.
  Estratégia: busca por nome_amigavel exibido.
  (Para performance em listas grandes, usar uma TStringList paralela de nomes técnicos.)
}
var
  sTexto       : string;
  sNomeAmigavel: string;
  sPosIni      : Integer;
begin
  Result := '';
  if AIndex < 0 then Exit;
  sTexto := ALst.Items[AIndex];
  { Remove prefixo "[Categoria]  " }
  sPosIni := Pos(']  ', sTexto);
  if sPosIni > 0 then
    sNomeAmigavel := Copy(sTexto, sPosIni + 3, MaxInt)
  else
    sNomeAmigavel := sTexto;
  with modulo_dados do
  begin
     sql:='SELECT nome_objeto FROM USER_geoapolo_objetos WHERE nome_amigavel = :pnomeamigavel';
     fdquerysql1.Close;
     fdquerysql1.sql.clear;
     fdquerysql1.sql.Text := sql;
     fdquerysql1.parambyname('pnomeamigavel').asstring:=sNomeAmigavel;
     if executaracao(fdquerysql1, fdbanco, false, dtsfdquerysql1) then
      Result := fdquerysql1.FieldByName('nome_objeto').AsString;
  end;
end;

procedure Tfrmconfigperfil.AtualizarStatusBar;
begin
  StatusBar1.Panels[0].Text := 'Banco Alvo';
  StatusBar1.Panels[1].Text := configura_statusbar('a');
  StatusBar1.Panels[2].Text := 'Banco GeoApolo';
  StatusBar1.Panels[3].Text := configura_statusbar('a');
end;

procedure Tfrmconfigperfil.ValidarGrupoSelecionado;
begin
  if FCodigoGrupo = 0 then
    raise Exception.Create('Selecione um grupo de usuários antes de alterar permissões.');
end;

{ ══════════════════════════════════════════════════════════════════════ }
{  OPERAÇÕES DE PERMISSÃO                                               }
{ ══════════════════════════════════════════════════════════════════════ }
procedure Tfrmconfigperfil.AlterarPermissao(ANomeTecnico: string;
  ACodigoObjeto, ACodigoGrupo: Integer; AStatus: string);
{
  Faz o UPSERT na tabela USER_geoapolo_grupobjetos:
    - Se já existe um registro → UPDATE statusacesso
    - Se não existe → INSERT
}
begin
  with modulo_dados do
  begin
     sql:='SELECT codigo_objeto FROM USER_geoapolo_grupobjetos WHERE codigo_objeto = :pcodigobjeto AND codigo_grupo  = :pcodigogrupo';
     fdquerysql2.Close;
     fdquerysql2.sql.clear;
     fdquerysql2.SQL.Text := sql;
     fdquerysql2.ParamByName('pcodigobjeto').AsString :=   inttostr(ACodigoObjeto);
     fdquerysql2.ParamByName('pcodigogrupo').AsString :=  inttostr(ACodigoGrupo);
     if executaracao(fdquerysql2, fdbanco, true, dtsfdquerysql2) then
       begin
         sql:='UPDATE USER_geoapolo_grupobjetos SET statusacesso =  :pAStatus  WHERE codigo_objeto = :pACodigoObjeto AND codigo_grupo  = :pCodigoGrupo ' ;
         fdquerysql3.Close;
         fdquerysql3.sql.Clear;
         fdquerysql3.sql.Text := sql;
         fdquerysql3.parambyname('pAstatus') .asstring := AStatus;
         fdquerysql3.parambyname('pACodigoObjeto').asstring := Inttostr(ACodigoObjeto);
         fdquerysql3.parambyname('pCodigoGrupo').asstring := Inttostr(ACodigoGrupo);
       end
     else
        begin
           sql:='INSERT INTO USER_geoapolo_grupobjetos (codigo_objeto, codigo_grupo, statusacesso) ';
           sql:=sql+' VALUES (:pACodigoObjeto,:pAcodigoGrupo, :pAStatus)';
           fdquerysql3.Close;
           fdquerysql3.SQL.Clear;
           fdquerysql3.SQL.Text := sql;
           fdquerysql3.ParamByName('pACodigoObjeto').AsString :=  Inttostr(ACodigoObjeto);
           fdquerysql3.ParamByName('pAcodigoGrupo').AsString :=   Inttostr(ACodigoGrupo);
           fdquerysql3.ParamByName('pAStatus').AsString := AStatus;
        end;
     if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
        begin
        end;
  end;
end;

procedure Tfrmconfigperfil.LiberarObjeto(ALstOrigem, ALstDestino: TListBox);
{
  Move o item selecionado de "Disponíveis" → "Liberados" (statusacesso='A')
}
var
  sNomeTecnico : string;
  iCodigo      : Integer;
  sTexto       : string;
begin
  ValidarGrupoSelecionado;
  if ALstOrigem.ItemIndex < 0 then Exit;
  sTexto       := ALstOrigem.Items[ALstOrigem.ItemIndex];
  sNomeTecnico := NomeTecnicoDoItem(ALstOrigem, ALstOrigem.ItemIndex);
  iCodigo      := BuscarCodigoObjeto(sNomeTecnico);
  if iCodigo = 0 then
  begin
    MessageDlg('Objeto não encontrado na base de dados.', mtError, [mbOK], 0);
    Exit;
  end;
  AlterarPermissao(sNomeTecnico, iCodigo, FCodigoGrupo, 'A');
  ALstDestino.Items.Add(sTexto);
  ALstOrigem.Items.Delete(ALstOrigem.ItemIndex);
end;

procedure Tfrmconfigperfil.RevogarObjeto(ALstOrigem, ALstDestino: TListBox);
{
  Move o item selecionado de "Liberados" → "Disponíveis" (statusacesso='N')
}
var
  sNomeTecnico : string;
  iCodigo      : Integer;
  sTexto       : string;
begin
  ValidarGrupoSelecionado;
  if ALstOrigem.ItemIndex < 0 then Exit;
  sTexto       := ALstOrigem.Items[ALstOrigem.ItemIndex];
  sNomeTecnico := NomeTecnicoDoItem(ALstOrigem, ALstOrigem.ItemIndex);
  iCodigo      := BuscarCodigoObjeto(sNomeTecnico);
  if iCodigo = 0 then
  begin
    MessageDlg('Objeto não encontrado na base de dados.', mtError, [mbOK], 0);
    Exit;
  end;
  if MessageDlg(
       'Confirma a retirada da permissão de acesso para "' + sTexto + '"?',
       mtConfirmation, [mbYes, mbNo], 0) <> idYes then Exit;
  AlterarPermissao(sNomeTecnico, iCodigo, FCodigoGrupo, 'N');
  ALstDestino.Items.Add(sTexto);
  ALstOrigem.Items.Delete(ALstOrigem.ItemIndex);
end;

procedure Tfrmconfigperfil.MoverTodos(ALstOrigem, ALstDestino: TListBox; ANovoStatus: string);
{
  Move TODOS os itens de uma lista para a outra atualizando o banco.
}
var
  i            : Integer;
  sNomeTecnico : string;
  iCodigo      : Integer;
  sTexto       : string;
begin
  ValidarGrupoSelecionado;
  if ALstOrigem.Items.Count = 0 then Exit;
  for i := ALstOrigem.Items.Count - 1 downto 0 do
  begin
    sTexto       := ALstOrigem.Items[i];
    sNomeTecnico := NomeTecnicoDoItem(ALstOrigem, i);
    iCodigo      := BuscarCodigoObjeto(sNomeTecnico);
    if iCodigo > 0 then
    begin
      AlterarPermissao(sNomeTecnico, iCodigo, FCodigoGrupo, ANovoStatus);
      ALstDestino.Items.Add(sTexto);
      ALstOrigem.Items.Delete(i);
    end;
  end;
end;

{ ══════════════════════════════════════════════════════════════════════ }
{  EVENTOS DOS COMBOS                                                   }
{ ══════════════════════════════════════════════════════════════════════ }
procedure Tfrmconfigperfil.cbogrupoChange(Sender: TObject);
begin
  FGrupoCarregado := False;
  lstDisponiveis.Clear;
  lstLiberados.Clear;
  if cbogrupo.ItemIndex < 0 then
  begin
     FCodigoGrupo := 0;
     Exit;
  end;
  { O código do grupo foi armazenado como objeto do item em CarregarGrupos }
  FCodigoGrupo := Integer(cbogrupo.Items.Objects[cbogrupo.ItemIndex]);
  if FCodigoGrupo = 0 then
  begin
    { Fallback: busca no banco caso Items.Objects não esteja preenchido }
    with modulo_dados do
    begin
       sql:='SELECT codigo_grupo FROM USER_geoapolo_grupo WHERE descricao = :pDescricao';
       fdquerysql.Close;
       fdquerysql.SQL.Clear;
       fdquerysql.SQL.Text := sql;
       fdquerysql.ParamByName('pDescricao').AsString := cbogrupo.Text;
       if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
        FCodigoGrupo := fdquerysql.FieldByName('codigo_grupo').AsInteger;
    end;
  end;
  CarregarPermissoes(FCodigoGrupo, FCategoriaFiltro);
  FGrupoCarregado := True;
end;

procedure Tfrmconfigperfil.cbocategoriaChange(Sender: TObject);
begin
  if cbocategoria.ItemIndex <= 0 then
    FCategoriaFiltro := ''
  else
    FCategoriaFiltro := cbocategoria.Text;
  if FCodigoGrupo > 0 then
    CarregarPermissoes(FCodigoGrupo, FCategoriaFiltro);
end;

{ ══════════════════════════════════════════════════════════════════════ }
{  EVENTOS DAS LISTAS                                                    }
{ ══════════════════════════════════════════════════════════════════════ }
procedure Tfrmconfigperfil.lstDisponiveisDblClick(Sender: TObject);
begin
  LiberarObjeto(lstDisponiveis, lstLiberados);
end;

procedure Tfrmconfigperfil.lstLiberadosDblClick(Sender: TObject);
begin
  RevogarObjeto(lstLiberados, lstDisponiveis);
end;

procedure Tfrmconfigperfil.lstDisponiveisKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
  if Key = VK_RETURN then
    LiberarObjeto(lstDisponiveis, lstLiberados);
end;

procedure Tfrmconfigperfil.lstLiberadosKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
  if Key = VK_RETURN then
    RevogarObjeto(lstLiberados, lstDisponiveis);
end;

{ ══════════════════════════════════════════════════════════════════════ }
{  EVENTOS DOS BOTÕES                                                   }
{ ══════════════════════════════════════════════════════════════════════ }
procedure Tfrmconfigperfil.btnLiberarClick(Sender: TObject);
begin
  LiberarObjeto(lstDisponiveis, lstLiberados);
end;

procedure Tfrmconfigperfil.btnRevogarClick(Sender: TObject);
begin
  RevogarObjeto(lstLiberados, lstDisponiveis);
end;

procedure Tfrmconfigperfil.btnLiberarTodosClick(Sender: TObject);
begin
  if MessageDlg('Liberar TODOS os objetos para o grupo "' + cbogrupo.Text + '"?',
                mtConfirmation, [mbYes, mbNo], 0) = idYes then
    MoverTodos(lstDisponiveis, lstLiberados, 'A');
end;

procedure Tfrmconfigperfil.btnRevogarTodosClick(Sender: TObject);
begin
  if MessageDlg('Revogar TODAS as permissões do grupo "' + cbogrupo.Text + '"?',
                mtConfirmation, [mbYes, mbNo], 0) = idYes then
    MoverTodos(lstLiberados, lstDisponiveis, 'N');
end;

{ ══════════════════════════════════════════════════════════════════════ }
{  TOOLBAR                                                              }
{ ══════════════════════════════════════════════════════════════════════ }
procedure Tfrmconfigperfil.spbsalvarClick(Sender: TObject);
begin
  { Permissões já são salvas imediatamente ao mover o item.
    Este botão pode ser usado para recarregar e confirmar consistência. }
  if FCodigoGrupo > 0 then
  begin
    CarregarPermissoes(FCodigoGrupo, FCategoriaFiltro);
    MessageDlg('Permissões atualizadas com sucesso.', mtInformation, [mbOK], 0);
  end;
end;

procedure Tfrmconfigperfil.spblimparClick(Sender: TObject);
begin
  cbogrupo.ItemIndex := -1;
  FCodigoGrupo       := 0;
  FGrupoCarregado    := False;
  lstDisponiveis.Clear;
  lstLiberados.Clear;
end;

procedure Tfrmconfigperfil.spbretornarClick(Sender: TObject);
begin
  Close;
end;
procedure Tfrmconfigperfil.spbrenomearClick(Sender: TObject);
{
  Abre a tela auxiliar de definição de nomes amigáveis.
  Ao fechar, recarrega as permissões para refletir os novos nomes.
}
var
  frmNomes : TfrmNomesAmigaveis;
begin
  frmNomes := TfrmNomesAmigaveis.Create(Self);
  try
    frmNomes.ShowModal;
    { Recarrega categorias e permissões pois o admin pode ter alterado }
    CarregarCategorias;
    if FCodigoGrupo > 0 then
      CarregarPermissoes(FCodigoGrupo, FCategoriaFiltro);
  finally
    frmNomes.Free;
  end;
end;

end.
