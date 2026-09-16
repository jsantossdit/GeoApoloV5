unit unt_cadconsulta;

interface

uses
  Winapi.Windows, Vcl.Dialogs, Winapi.Messages, System.SysUtils,
  unt_consultas4, System.Classes, Vcl.Controls, Vcl.Forms, Vcl.StdCtrls,
  Vcl.ExtCtrls, Vcl.Buttons, ConsultaModel, ConsultaRepository,
  ConsultaService, Data.DB, Vcl.Menus, Vcl.Grids, Vcl.DBGrids, Vcl.ComCtrls,
  FireDAC.Comp.Client, Vcl.Mask;

type
  Tfrmcadconsulta = class(TForm)
    lblcodconsulta: TLabeledEdit;
    lbldescricao: TLabeledEdit;
    memosql: TMemo;
    cbotipoconsulta: TComboBox;
    cbobancodaconsulta: TComboBox;
    spbsalvar: TSpeedButton;
    spbexcluir: TSpeedButton;
    spblimpar: TSpeedButton;
    spbretornar: TSpeedButton;
    Panel1: TPanel;
    lblbancodedados: TLabel;
    spbconsulta: TSpeedButton;
    statusbar1: TStatusBar;
    groupbox1: TGroupBox;
    groupbox2: TGroupBox;
    popmnuconsulta: TPopupMenu;
    cin: TPageControl;
    tblmanutencao: TTabSheet;
    rdgpermissaoconsulta: TRadioGroup;
    gridpermissao: TDBGrid;
    cbousuarios: TCombobox;
    cbousuarioorigem: TCombobox;
    cbousuariodestino: TComboBox;
    cbogrupos: TComboBox;
    lblnomedaconsulta: TLabel;

    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
    procedure spbsalvarClick(Sender: TObject);
    procedure spbexcluirClick(Sender: TObject);
    procedure spbconsultaClick(Sender: TObject);
    procedure lblcodconsultaExit(Sender: TObject);
    procedure rdgpermissaoconsultaClick(Sender: TObject);
    procedure mniNovoClick(Sender: TObject);
    procedure mniSalvarClick(Sender: TObject);
    procedure mniExcluirClick(Sender: TObject);
    procedure mniSairClick(Sender: TObject);
    procedure spbretornarClick(Sender: TObject);
    procedure lblcodconsultaKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cbousuariosEnter(Sender: TObject);
    procedure cbogruposChange(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure spbaplicapermissaoClick(Sender: TObject);

    procedure cbotipoconsultaEnter(Sender: TObject);
    procedure lbldescricaoEnter(Sender: TObject);
    procedure gridpermissaoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);

  private
    FRepository   : TConsultaRepository;
    FService      : TConsultaService;
    FModoInclusao : Boolean;

    procedure InicializarDependencias;
    procedure LiberarDependencias;
    function  MontarModelDaTela: TConsultaModel;
    procedure CarregarTela(AModel: TConsultaModel);
    procedure BuscarConsulta(ACodigo: Integer);     // digitou código no campo
    procedure BuscarDadosConsulta(ACodigo: Integer); // carrega tela após seleção
    procedure LimparTela;
    procedure AbrirFormConsulta;
    procedure AtualizarStatusBar;
    procedure AtualizarPermissoes;
  public
    procedure CarregarComboUsuarios(AQuery: TFDQuery; AComboList: array of TComboBox; const ACodigoGrupo: string);
    procedure CarregarGrupos(AQuery: TFDQuery; ACombo: TComboBox);
  end;

var
  frmcadconsulta: Tfrmcadconsulta;
  autorizacao:string;

  function mostra_permissoes(codigo_consulta : string) : string; export;
  function retorna_codigousuario(nomeusuario : string) : string; export;

implementation

uses
  unt_dados, funcoes;

{$R *.dfm}

procedure Tfrmcadconsulta.FormActivate(Sender: TObject);
begin
  // Carrega a lista de grupos assim que o form é criado
  CarregarGrupos(Modulo_Dados.fdquerysql1, cbogrupos);
end;

procedure Tfrmcadconsulta.FormCreate(Sender: TObject);
begin
  InicializarDependencias;
  FModoInclusao := True;
  AtualizarStatusBar;
end;

procedure Tfrmcadconsulta.FormDestroy(Sender: TObject);
begin
  LiberarDependencias;
end;

procedure Tfrmcadconsulta.gridpermissaoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
var
  resp:word;
begin
   with modulo_dados do
   begin
     if key = vk_delete then
        begin
          resp:=messagedlg('Confirma a Remoção do Acesso deste usuário a esta consulta ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
          if resp = idyes then
             begin
                sql:='DELETE FROM user_geoapolo_permissaoconsulta WHERE codigo_consulta = :codconsulta AND usucod = :usucod';
                fdquerysql3.close;
                fdquerysql3.sql.clear;
                fdquerysql3.sql.text := sql;
                fdquerysql3.parambyname('codconsulta').asstring :=  fdquerysql4.fieldbyname('codigo_consulta').asstring;
                fdquerysql3.parambyname('usucod').asstring := fdquerysql4.fieldbyname('usucod').asstring;
                if executaracao(fdquerysql3,fdbanco,true,dtsfdquerysql3) then
                   begin
                     messagedlg('PERMISSÃO REMOVIDA COM SUCESSO',mtinformation,[mbok],0) ;
                     mostra_permissoes(fdquerysql4.fieldbyname('codigo_consulta').asstring) ;
                   end;
             end;
        end;
   end;
end;

procedure Tfrmcadconsulta.InicializarDependencias;
begin
  FRepository := TConsultaRepository.Create(modulo_dados.fdbanco);
  FService    := TConsultaService.Create(FRepository);
end;

procedure Tfrmcadconsulta.LiberarDependencias;
begin
  FreeAndNil(FService);
  FreeAndNil(FRepository);
end;

function Tfrmcadconsulta.MontarModelDaTela: TConsultaModel;
begin
  Result := TConsultaModel.Create;
  Result.Codigo        := strtoint(lblcodconsulta.Text);
  Result.Descricao     := lbldescricao.Text;
  Result.SentencaSQL   := memosql.Text;
  Result.BancoConsulta := cbobancodaconsulta.Text;

  case cbotipoconsulta.ItemIndex of
    0: Result.TipoConsulta := tcImediata;
    1: Result.TipoConsulta := tcCampanha;
    2: Result.TipoConsulta := tcMix;
  else
    Result.TipoConsulta := tcImediata;
  end;
end;

procedure Tfrmcadconsulta.CarregarTela(AModel: TConsultaModel);
begin
  lblcodconsulta.Text     := AModel.Codigo.ToString;
  lbldescricao.Text       := AModel.Descricao;
  memosql.Text            := AModel.SentencaSQL;
  cbobancodaconsulta.Text := AModel.BancoConsulta;

  case AModel.TipoConsulta of
    tcImediata: cbotipoconsulta.ItemIndex := 0;
    tcCampanha: cbotipoconsulta.ItemIndex := 1;
    tcMix:      cbotipoconsulta.ItemIndex := 2;
  end;

  AtualizarPermissoes;
  AtualizarStatusBar;
end;

procedure Tfrmcadconsulta.cbogruposChange(Sender: TObject);
begin
  cbousuarios.Clear;
  cbousuarioorigem.Clear;
  cbousuariodestino.Clear;
end;

procedure Tfrmcadconsulta.cbotipoconsultaEnter(Sender: TObject);
begin
   if lbldescricao.text <> '' then
      begin
         lblnomedaconsulta.caption:=lbldescricao.text;
         mostra_permissoes(lblcodconsulta.text);
      end;
end;

procedure Tfrmcadconsulta.cbousuariosEnter(Sender: TObject);
begin
// Apenas carregamos se o combo estiver vazio ou se o grupo mudou
  if TComboBox(Sender).Items.Count = 0 then
  begin
    CarregarComboUsuarios(Modulo_Dados.fdquerysql1,[cbousuarios, cbousuarioorigem, cbousuariodestino], cbogrupos.Text);
  end;
end;


// ============================================================
//  BUSCA PELO CÓDIGO DIGITADO NO CAMPO
// ============================================================
procedure Tfrmcadconsulta.BuscarConsulta(ACodigo: Integer);
begin
  if ACodigo <= 0 then
    Exit;

  BuscarDadosConsulta(ACodigo);
end;

// ============================================================
//  CARREGA TODOS OS CAMPOS PELO CÓDIGO
// ============================================================
procedure Tfrmcadconsulta.BuscarDadosConsulta(ACodigo: Integer);
begin
  with modulo_dados.fdquerysql1 do
  begin
    Close;
    SQL.Clear;
    SQL.Add('SELECT codigo_consulta, descricao_consulta,');
    SQL.Add('       sentenca_sql, tipo_consulta, banco_consulta');
    SQL.Add('FROM USER_geoapolo_consultas');
    SQL.Add('WHERE codigo_consulta = :pCodigo');
    ParamByName('pCodigo').AsInteger := ACodigo;
    Open;

    if IsEmpty then
    begin
      MessageDlg('Registro não encontrado.', mtWarning, [mbOK], 0);
      Exit;
    end;

    lblcodconsulta.Text := FieldByName('codigo_consulta').AsString;
    lbldescricao.Text   := FieldByName('descricao_consulta').AsString;
    memosql.Lines.Text  := FieldByName('sentenca_sql').AsString;
    lblnomedaconsulta.caption := lbldescricao.text; lblnomedaconsulta.Refresh;

    if FieldByName('tipo_consulta').AsString = 'I' then
       begin
           buscanacombo('IMEDIATAS',frmcadconsulta, cbotipoconsulta);
       end
    else if fieldbyname('tipo_consulta').asstring = 'C' then
       begin
          buscanacombo('CAMPANHAS',frmcadconsulta, cbotipoconsulta);
       end;
    buscanacombo(FieldByName('banco_consulta').AsString,frmcadconsulta, cbobancodaconsulta);
    FModoInclusao := False;
    AtualizarStatusBar;
    lbldescricao.SetFocus;
  end;
end;

// ============================================================
//  ABRE FORM DE BUSCA
// ============================================================
procedure Tfrmcadconsulta.AbrirFormConsulta;
var
  frmConsulta : TFrmConsulta4;
  lCodigo     : Integer;
begin
  with modulo_dados.fdquerysql1 do
  begin
    Close;
    SQL.Clear;
    SQL.Add('SELECT codigo_consulta, descricao_consulta');
    SQL.Add('FROM USER_geoapolo_consultas');
    SQL.Add('ORDER BY descricao_consulta');
    Open;

    if RecordCount = 0 then
    begin
      MessageDlg('Nenhuma consulta cadastrada encontrada.', mtWarning, [mbOK], 0);
      Exit;
    end;
  end;

  lCodigo := 0;

  frmConsulta := TFrmConsulta4.Create(Self);
  try
    frmConsulta.Titulo := 'Consulta de Sentenças SQL';
    frmConsulta.PopularGrid(
      modulo_dados.fdquerysql1,
      'codigo_consulta',
      'descricao_consulta'
    );

    if frmConsulta.ShowModal = mrOK then
      lCodigo := StrToIntDef(frmConsulta.CodigoSelecionado, 0);
  finally
    frmConsulta.Free;
    modulo_dados.fdquerysql1.Close;
  end;
  // Fora do try/finally — dataset já fechado, frmConsulta já liberado
  if lCodigo > 0 then
     begin
        BuscarDadosConsulta(lCodigo);

     end;
     mostra_permissoes(inttostr(lCodigo));
end;

// ============================================================
//  BOTÕES E EVENTOS
// ============================================================
procedure Tfrmcadconsulta.spbaplicapermissaoClick(Sender: TObject);
var codigo_usuario,codigo_grupo:string; resp:word;
begin
   with modulo_dados, frmcadconsulta do
   begin
      if (cbogrupos.text = '') and (cbousuarios.text = '') then
         begin
            messagedlg('É OBRIGATÓRIO ESCOLHER UM GRUPO OU UM USUÁRIO PARA APLICAR A PERMISSÃO !!!',mterror,[mbok],0);
            cbogrupos.setfocus;
            exit;
         end;
      if rdgpermissaoconsulta.ItemIndex = 0 then
         autorizacao:='A'
      else if rdgpermissaoconsulta.ItemIndex = 1 then
         autorizacao:='N'
      else
         begin
            messagedlg('VOCÊ PRECISA AUTORIZAR OU NÃO O ACESSO A ESTA CONSULTA !!!',mterror,[mbok],0);
            cbogrupos.setfocus;
            exit;
         end;
      //
      resp:=messagedlg('Confirma esta permissão para a consulta selecionada ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
      if resp = idyes then
         begin
            codigo_usuario:=retorna_codigousuario(cbousuarios.text);
            if (cbogrupos.text <> '') and (cbousuarios.text <> '') then
               begin
                  sql:='INSERT INTO USER_geoapolo_permissaoconsulta (usucod,autorizacao,codigo_consulta)';
                  sql:=sql+' VALUES (:codigo_usuario, :autorizacao, :codigoconsulta)';
                  fdquerysql3.close;
                  fdquerysql3.sql.clear;
                  fdquerysql3.sql.text := sql;
                  fdquerysql3.parambyname('codigo_usuario').asstring := codigo_usuario;
                  fdquerysql3.parambyname('autorizacao').asstring := autorizacao;
                  fdquerysql3.parambyname('codigoconsulta').asstring := lblcodconsulta.text;

                  if executaracao(fdquerysql3,fdbanco,true,dtsfdquerysql3) then
                     begin
                        messagedlg('PERMISSÃO CONCEDIDA AO USUÁRIO COM SUCESSO !!!',mtinformation,[mbok],0);
                        cbogrupos.ItemIndex:=-1; cbousuarios.ItemIndex:=-1; cbogrupos.Refresh; cbousuarios.Refresh;
                        autorizacao:='';
                        mostra_permissoes(lblcodconsulta.text);
                        cbogrupos.setfocus;
                     end
                  else
                     begin
                        messagedlg('PROBLEMAS AO TENTAR CONCEDER A PERMISSÃO AO USUÁRIO !!!',mterror,[mbok],0);
                        cbogrupos.setfocus;
                        exit;
                     end;
               end
            else if (cbogrupos.text <> '') and (cbousuarios.text = '') then
               begin
                  // dar permissão aos membros do grupo
                  //codigo_grupo:=retorna_codigogrupo(cbogrupos.Text);
                  sql:='SELECT ggu.codigo_grupo,gg.descricao, ggu.usucod';
                  sql:=sql+' FROM USER_geoapolo_grupousuario ggu';
                  sql:=sql+' INNER JOIN USER_geoapolo_grupo gg ON ggu.codigo_grupo = gg.codigo_grupo';
                  sql:=sql+' INNER JOIN USER_geoapolo_usuarios u ON ggu.usucod  = u.usucod';
                  sql:=sql+' WHERE u.flagativo = :flagativo';
                  sql:=sql+' AND   gg.descricao = :nomedogrupo';
                  fdquerysql.close;
                  fdquerysql.sql.clear;
                  fdquerysql.sql.text := sql;
                  fdquerysql.parambyname('flagativo').asstring := 'A';
                  fdquerysql.parambyname('nomedogrupo').asstring := cbogrupos.text ;
                  if executaracao(fdquerysql,fdbanco,false,dtsfdquerysql) then
                     begin
                        fdquerysql.first;
                        while not fdquerysql.eof do
                        begin
                           sql:='SELECT * FROM USER_geoapolo_permissaoconsulta WHERE usucod = :usucod';
                           sql:=sql+' AND codigo_consulta = :codigo_consulta';
                           fdquerysql1.close;
                           fdquerysql1.sql.clear;
                           fdquerysql1.sql.text := sql;
                           fdquerysql1.parambyname('usucod').asstring := fdquerysql.fieldbyname('usucod').asstring;
                           fdquerysql1.parambyname('codigo_consulta').asstring:= lblcodconsulta.text;

                           if not executaracao(fdquerysql1,fdbanco,false,dtsfdquerysql1) then
                              begin
                                 sql:='INSERT INTO USER_geoapolo_permissaoconsulta (usucod,autorizacao,codigo_consulta)';
                                 sql:=sql+' VALUES (:usucod, :autorizacao, :codigo_consulta)';
                                 fdquerysql3.close;
                                 fdquerysql3.sql.clear;
                                 fdquerysql3.sql.text := sql;
                                 fdquerysql3.parambyname('usucod').asstring := fdquerysql.fieldbyname('usucod').AsString;
                                 fdquerysql3.parambyname('autorizacao').asstring := autorizacao;
                                 fdquerysql3.parambyname('codigo_consulta').asstring := lblcodconsulta.text;
                                 if executaracao(fdquerysql3, fdbanco, false, dtsfdquerysql3) then
                                    begin
                                       mostra_permissoes(lblcodconsulta.text);
                                    end;
                              end;
                           fdquerysql.next;
                        end;
                        messagedlg('PERMISSÃO CONCEDIDA AO USUÁRIO COM SUCESSO !!!',mtinformation,[mbok],0);
                        cbogrupos.ItemIndex:=-1; cbousuarios.ItemIndex:=-1; cbogrupos.Refresh; cbousuarios.Refresh;
                        autorizacao:='';
                        mostra_permissoes(lblcodconsulta.text);
                        cbogrupos.setfocus;
                     end;
               end;
         end
      else
         begin
            cbogrupos.setfocus;
            exit;
         end;
   end;
end;


procedure Tfrmcadconsulta.spbconsultaClick(Sender: TObject);
begin
  AbrirFormConsulta;
end;

procedure Tfrmcadconsulta.spbsalvarClick(Sender: TObject);
var
  Consulta: TConsultaModel;
begin
  if Trim(lbldescricao.Text) = '' then
  begin
    MessageDlg('Informe a descrição da consulta.', mtWarning, [mbOK], 0);
    lbldescricao.SetFocus;
    Exit;
  end;

  Consulta := MontarModelDaTela;
  try
    FService.Salvar(Consulta, FModoInclusao);
    MessageDlg('CONSULTA SALVA COM SUCESSO.', mtInformation, [mbOK], 0);
    FModoInclusao := False;
    spblimpar.Click;
    AtualizarStatusBar;
  finally
    Consulta.Free;
  end;
end;

procedure Tfrmcadconsulta.spbexcluirClick(Sender: TObject);
begin
  if StrToIntDef(lblcodconsulta.Text, 0) = 0 then
  begin
    MessageDlg('NENHUMA CONSULTA SELECIONADA PARA EXCLUSÃO.', mtWarning, [mbOK], 0);
    Exit;
  end;

  if MessageDlg('Deseja realmente excluir esta consulta?',
     mtConfirmation, [mbYes, mbNo], 0) <> mrYes then
    Exit;

  FService.Excluir(StrToIntDef(lblcodconsulta.Text, 0));
  MessageDlg('CONSULTA REMOVIDA COM SUCESSO.', mtInformation, [mbOK], 0);
  LimparTela;
end;

procedure Tfrmcadconsulta.spblimparClick(Sender: TObject);
begin
   limpartela;
end;

procedure Tfrmcadconsulta.lblcodconsultaExit(Sender: TObject);
begin
  if (Trim(lblcodconsulta.Text) <> '') and (FModoInclusao) then
    BuscarConsulta(StrToIntDef(lblcodconsulta.Text, 0));
end;

procedure Tfrmcadconsulta.lblcodconsultaKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
  if Key = VK_F4 then
    spbconsulta.Click;
  if ((key = vk_tab) or (key = vk_return) and (lblcodconsulta.text <> '')) then
     frmcadconsulta.BuscarDadosConsulta(strtoint(lblcodconsulta.Text));
end;


procedure Tfrmcadconsulta.lbldescricaoEnter(Sender: TObject);
begin
   if lbldescricao.text <> '' then
      lblnomedaconsulta.caption:=lbldescricao.text;
end;

procedure Tfrmcadconsulta.LimparTela;
begin
  lblcodconsulta.Clear;
  lbldescricao.Clear;
  memosql.Clear;
  cbotipoconsulta.ItemIndex    := -1;
  cbobancodaconsulta.ItemIndex := -1;
  FModoInclusao := True;
  AtualizarStatusBar;
  lblcodconsulta.SetFocus;
end;

procedure Tfrmcadconsulta.AtualizarStatusBar;
begin
  if FModoInclusao then
    statusbar1.SimpleText := 'Modo: Inclusão'
  else
    statusbar1.SimpleText := 'Modo: Edição | Código: ' + lblcodconsulta.Text;
end;

procedure Tfrmcadconsulta.spbretornarClick(Sender: TObject);
begin
  Close;
end;

procedure Tfrmcadconsulta.rdgpermissaoconsultaClick(Sender: TObject);
begin
  AtualizarPermissoes;
end;

procedure Tfrmcadconsulta.AtualizarPermissoes;
begin
  // Implementar lógica de permissões se necessário
end;

procedure Tfrmcadconsulta.mniNovoClick(Sender: TObject);
begin
  LimparTela;
end;

procedure Tfrmcadconsulta.mniSalvarClick(Sender: TObject);
begin
  spbsalvarClick(Sender);
end;

procedure Tfrmcadconsulta.mniExcluirClick(Sender: TObject);
begin
  spbexcluirClick(Sender);
end;

procedure Tfrmcadconsulta.mniSairClick(Sender: TObject);
begin
  Close;
end;

procedure LimparComponentes(AOwner: TComponent);
var
  i: Integer;
begin
  for i := 0 to AOwner.ComponentCount - 1 do
  begin
    // Limpa TEdit
    if AOwner.Components[i] is TEdit then
      TEdit(AOwner.Components[i]).Clear

    // Limpa TMemo
    else if AOwner.Components[i] is TMemo then
      TMemo(AOwner.Components[i]).Clear

    // Limpa TComboBox (reseta o item selecionado)
    else if AOwner.Components[i] is TComboBox then
      TComboBox(AOwner.Components[i]).ItemIndex := -1

    // Limpa TRadioGroup
    else if AOwner.Components[i] is TRadioGroup then
      TRadioGroup(AOwner.Components[i]).ItemIndex := -1;
  end;
end;


function carrega_combo(nomecombo: tcombobox; consulta: string) : string;
begin
   with modulo_dados, frmcadconsulta do
   begin
      sql:=consulta;
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := sql;
      if executaracao(fdquerysql, fdbanco, true,dtsfdquerysql) then
         begin
            nomecombo.clear;
            while not fdquerysql.Eof do
            begin
               nomecombo.items.add(fdquerysql.fieldbyname('descricao').asstring);
               fdquerysql.next;
            end;
            nomecombo.Refresh;
         end;
   end;
end;

procedure TfrmCadConsulta.CarregarComboUsuarios(AQuery: TFDQuery; AComboList: array of TComboBox; const ACodigoGrupo: string);
var
  LCombo: TComboBox;
begin
  // 1. Preparação da SQL com Parâmetros (mais seguro)
  AQuery.Close;
  AQuery.SQL.Clear;

  if ACodigoGrupo.Trim = '' then
  begin
    AQuery.SQL.Add('SELECT usucod FROM USER_geoapolo_usuarios WHERE flagativo = :ativo ORDER BY usucod ASC');
    AQuery.ParamByName('ativo').AsString := 'A';
  end
  else
  begin
    AQuery.SQL.Add('SELECT u.usucod ');
    AQuery.SQL.Add('FROM USER_geoapolo_usuarios u ');
    AQuery.SQL.Add('INNER JOIN USER_geoapolo_grupousuario ggu ON u.usucod = ggu.usucod ');
    AQuery.SQL.Add('INNER JOIN USER_geoapolo_grupo gu ON ggu.codigo_grupo = gu.codigo_grupo');
    AQuery.SQL.Add('WHERE gu.descricao = :grupo AND u.flagativo = :ativo ');
    AQuery.SQL.Add('ORDER BY u.usucod ASC');
    AQuery.ParamByName('grupo').AsString := ACodigoGrupo;
    AQuery.ParamByName('ativo').AsString := 'A';
  end;

  // 2. Execução
  AQuery.Open;

  // 3. Preenchimento dos Combos
  for LCombo in AComboList do
  begin
    LCombo.Items.BeginUpdate;
    try
      LCombo.Clear;
      AQuery.First;
      while not AQuery.Eof do
      begin
        LCombo.Items.Add(AQuery.FieldByName('usucod').AsString);
        AQuery.Next;
      end;
    finally
      LCombo.Items.EndUpdate;
    end;
  end;
end;

procedure Tfrmcadconsulta.CarregarGrupos(AQuery: TFDQuery; ACombo: TComboBox);
begin
  AQuery.Close;
  AQuery.SQL.Clear;
  AQuery.SQL.Add('SELECT descricao FROM USER_geoapolo_grupo ORDER BY descricao ASC');

  ACombo.Items.BeginUpdate;
  try
    ACombo.Clear;
    AQuery.Open;
    while not AQuery.Eof do
    begin
      ACombo.Items.Add(AQuery.FieldByName('descricao').AsString);
      AQuery.Next;
    end;
  finally
    ACombo.Items.EndUpdate;
    AQuery.Close;
  end;

end;

function mostra_permissoes(codigo_consulta : string) : string;
begin
   with modulo_dados, frmcadconsulta do
   begin
      if codigo_consulta = '' then
         begin
            sql:='SELECT gc.descricao_consulta, u.usucod, gpc.autorizacao, gc.banco_consulta, gc.tipo_consulta, gpc.codigo_consulta, gpc.usucod';
            sql:=sql+' FROM USER_geoapolo_consultas gc';
            sql:=sql+' INNER JOIN USER_geoapolo_permissaoconsulta gpc ON gc.codigo_consulta = gpc.codigo_consulta';
            sql:=sql+' INNER JOIN USER_geoapolo_usuarios u ON gpc.usucod = u.usucod';
            sql:=sql+' ORDER by gc.descricao_consulta ASC';
         end
      else if codigo_consulta <> '' then
         begin
            sql:='SELECT gc.descricao_consulta, u.usucod, gpc.autorizacao, gc.banco_consulta, gc.tipo_consulta, gpc.codigo_consulta, gpc.usucod';
            sql:=sql+' FROM USER_geoapolo_consultas gc';
            sql:=sql+' INNER JOIN USER_geoapolo_permissaoconsulta gpc ON gc.codigo_consulta = gpc.codigo_consulta';
            sql:=sql+' INNER JOIN USER_geoapolo_usuarios u ON gpc.usucod = u.usucod';
            sql:=sql+' WHERE gc.codigo_consulta = :codigo_consulta';
            sql:=sql+' ORDER by gc.descricao_consulta ASC';
         end;
      fdquerysql4.close;
      fdquerysql4.sql.clear;
      fdquerysql4.sql.text := sql;
      fdquerysql4.parambyname('codigo_consulta').asstring:= codigo_consulta;
      if executaracao(fdquerysql4,fdbanco,false,dtsfdquerysql4) then
         begin
            gridpermissao.DataSource:=dtsfdquerysql4;
            gridpermissao.Refresh;
         end;
   end;
end;

function retorna_codigousuario(nomeusuario : string) : string;
begin
   with modulo_dados, frmcadconsulta do
   begin
      sql:='SELECT usucod FROM USER_geoapolo_usuarios WHERE usucod = :nomeusuario';
      fdquerysql.close;
      fdquerysql.sql.clear;
      fdquerysql.sql.text := sql;
      fdquerysql.parambyname('nomeusuario').asstring := nomeusuario;
      if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
         result:=fdquerysql.fieldbyname('usucod').asstring
      else
         result:='0';
   end;
end;

end.
