unit unt_secao;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, Buttons, ExtCtrls, Grids, DBGrids, ComCtrls, Vcl.Menus,
  Data.DB, Vcl.Mask;

type
  Tfrmdepartamentos = class(TForm)
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spblimpar: TSpeedButton;
    spbdeletar: TSpeedButton;
    spbabreos: TSpeedButton;
    spbretornar: TSpeedButton;
    lblmsg1: TLabel;
    StatusBar1: TStatusBar;
    GroupBox7: TGroupBox;
    lblcampo: TLabel;
    lblordem: TLabel;
    lblprocurarpor: TLabeledEdit;
    cbocampo: TComboBox;
    cbordem: TComboBox;
    rdgcrescente: TRadioButton;
    rdgdecrescente: TRadioButton;
    popmenu: TPopupMenu;
    popmenugravaconfig: TMenuItem;
    cin: TPageControl;
    tsprincipal: TTabSheet;
    TabSheet1: TTabSheet;
    GroupBox1: TGroupBox;
    lblempresa: TLabel;
    lblcodigodepartamento: TLabeledEdit;
    lblnomedepartamento: TLabeledEdit;
    cboempresas: TComboBox;
    chkdeptoativo: TCheckBox;
    GroupBox3: TGroupBox;
    lbldptoorigem: TLabeledEdit;
    lblnomesecao_origem: TLabel;
    lbldptodestino: TLabeledEdit;
    lblsecao_destino: TLabel;
    spbuscasecorigem: TSpeedButton;
    spbuscasecdestino: TSpeedButton;
    btnAplicar: TBitBtn;
    btnCancelar: TBitBtn;
    memoacao: TMemo;
    griddepartamentos: TDBGrid;
    tblintegraapolo: TTabSheet;
    lbllinkdepartamento: TLabeledEdit;
    spbbuscalinksecao: TSpeedButton;
    lblnomelinksecao: TLabel;
    lblcctrlcodestr: TLabeledEdit;
    spbuscalinkcc: TSpeedButton;
    lbllinkcctrlnome: TLabel;
    lbllinkestrutura: TLabeledEdit;
    spbestruturamixlink: TSpeedButton;
    lbleslinknome: TLabel;
    gridlinksecao: TDBGrid;
    spbsalvalink: TSpeedButton;
    procedure spbretornarClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure lblnomedepartamentoEnter(Sender: TObject);
    procedure lblnomedepartamentoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spblimparClick(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure cboempresasKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbsalvarClick(Sender: TObject);
    procedure spbdeletarClick(Sender: TObject);
    procedure griddepartamentosDblClick(Sender: TObject);
    procedure griddepartamentosKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbabreosClick(Sender: TObject);
    procedure FormKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblcodigodepartamentoKeyPress(Sender: TObject; var Key: Char);
    procedure spbuscalinkccClick(Sender: TObject);
    procedure lblcctrlcodestrKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure chkdeptoativoClick(Sender: TObject);
    procedure rdgcrescenteClick(Sender: TObject);
    procedure rdgdecrescenteClick(Sender: TObject);
    procedure lblprocurarporKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure popmenugravaconfigClick(Sender: TObject);
    procedure lbldptoorigemKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lbldptodestinoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lbldptodestinoEnter(Sender: TObject);
    procedure btnAplicarEnter(Sender: TObject);
    procedure btnCancelarClick(Sender: TObject);
    procedure btnAplicarClick(Sender: TObject);
    procedure spbuscasecorigemClick(Sender: TObject);
    procedure spbuscasecdestinoClick(Sender: TObject);
    procedure spbbuscalinksecaoClick(Sender: TObject);
    procedure spbestruturamixlinkClick(Sender: TObject);
    procedure spbsalvalinkClick(Sender: TObject);
    procedure lbllinkestruturaKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lbllinkdepartamentoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblcctrlcodestrEnter(Sender: TObject);
    procedure lbllinkestruturaEnter(Sender: TObject);
    procedure tblintegraapoloEnter(Sender: TObject);
    procedure gridlinksecaoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblcodigodepartamentoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
  private
    { Private declarations }
  public
    { Public declarations }
    secaoativa:string;
  end;

var
  frmdepartamentos: Tfrmdepartamentos;
  area,controle,controlevinculo,integracao,sql,secaoantiga,wordem:string;
  codigodepto,i,codigo_secao:integer;
  resp:word;

function mostradepartamento(tipo_pesquisa : string) : string; export;
function mostra_vinculodepartamento(codigodepartamento : string) : string; export;
function valida_empresa(nome_empresa : string) : string; export;
function valida_centrocontrole(codigosecao:string; integracao:string) : string; export;
function retorna_nomedepartamento(codigo: string) : string; export;
function retorna_nomecentroctrl(cctrlcodestr : string) : string; export;
function retorna_estruturamix(esidestrutura : string) : string; export;

implementation

uses unt_dados, funcoes, unt_principal, unt_consultav3, unt_logon,
     FireDAC.Comp.Client, FireDAC.Comp.DataSet, FireDAC.Stan.Param;

{$R *.dfm}

type
  TDepartamentoModel = class
  private
    FCodigoDepartamento: Integer;
    FNomeDepartamento: string;
    FEmpresaCodigo: string;
    FFlagAtivo: string;
  public
    property CodigoDepartamento: Integer read FCodigoDepartamento write FCodigoDepartamento;
    property NomeDepartamento: string read FNomeDepartamento write FNomeDepartamento;
    property EmpresaCodigo: string read FEmpresaCodigo write FEmpresaCodigo;
    property FlagAtivo: string read FFlagAtivo write FFlagAtivo;
  end;

  TFireDACHelper = class
  public
    class function OpenQuery(const ASQL: string; const AQuery: TFDQuery; const ADataSource: TDataSource = nil): Boolean; static;
    class function ExecSQL(const ASQL: string; const AQuery: TFDQuery): Boolean; static;
  end;

class function TFireDACHelper.OpenQuery(const ASQL: string; const AQuery: TFDQuery; const ADataSource: TDataSource = nil): Boolean;
begin
  Result := False;
  if not Assigned(AQuery) then
    Exit;
  AQuery.Close;
  AQuery.Connection := modulo_dados.fdbanco;
  AQuery.SQL.Text := ASQL;
  Result := executaracao(AQuery, modulo_dados.fdbanco, False, ADataSource);
end;

class function TFireDACHelper.ExecSQL(const ASQL: string; const AQuery: TFDQuery): Boolean;
begin
  Result := False;
  if not Assigned(AQuery) then
    Exit;
  AQuery.Close;
  AQuery.Connection := modulo_dados.fdbanco;
  AQuery.SQL.Text := ASQL;
  Result := executaracao(AQuery, modulo_dados.fdbanco, False);
end;

procedure Tfrmdepartamentos.spbretornarClick(Sender: TObject);
begin
   close;
end;

procedure Tfrmdepartamentos.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
   action:=cafree;
end;

function mostradepartamento(tipo_pesquisa : string) : string;
var
   i:integer;
begin
   with frmdepartamentos do
   begin
       i := 0;
       sql := 'SELECT ugd.codigo_departamento,ugd.nome_departamento, uge.empnome,ugd.flagativo,ugd.empcod';
       sql := sql + ' FROM USER_geoapolo_departamentos ugd with(nolock)';
       sql := sql + ' INNER JOIN USER_geoapolo_empresas uge with(nolock) ON ugd.empcod = uge.empcod';
       if tipo_pesquisa = 'E' then
          sql:='SELECT * FROM mostradepartamentos WHERE '+cbocampo.text+' like :lblprocurarpor ORDER BY '+cbordem.text+' '+wordem
       else
          sql:='SELECT * FROM mostradepartamentos';

       modulo_dados.fdquerysql2.close;
       modulo_dados.fdquerysql2.sql.clear;
       modulo_dados.fdquerysql2.sql.text := sql;
       if tipo_pesquisa = 'E' then
          modulo_dados.fdquerysql2.parambyname('lblprocurarpor').asstring := '%'+lblprocurarpor.text+'%';
       if executaracao(modulo_dados.fdquerysql2, modulo_dados.fdbanco,true,modulo_dados.dtsfdquerysql2) then
          begin
             modulo_dados.dtsfdquerysql2.DataSet := modulo_dados.fdquerysql2;
             griddepartamentos.DataSource := modulo_dados.dtsfdquerysql2;
             cbocampo.clear; cbordem.clear;
             for i := 0 to modulo_dados.fdquerysql2.Fields.Count - 1 do
             begin
                cbocampo.Items.Add(modulo_dados.fdquerysql2.Fields[i].DisplayName);
                cbordem.Items.Add(modulo_dados.fdquerysql2.Fields[i].DisplayName);
             end;
             lblnomedepartamento.setfocus;
          end
       else
          begin
             messagedlg('TABELA DE DEPARTAMENTOS ESTÁ VAZIA !!!',mtinformation,[mbok],0);
             lblnomedepartamento.SetFocus;
             exit;
          end;
   end;
end;

function mostra_vinculodepartamento(codigodepartamento : string) : string;
begin
   sql := 'SELECT ugd.codigo_departamento,ugd.nome_departamento, uge.empnome,ugd.flagativo,ugd.empcod';
   sql := sql + ' FROM USER_geoapolo_departamentos ugd with(nolock)';
   sql := sql + ' INNER JOIN USER_geoapolo_empresas uge with(nolock) ON ugd.empcod = uge.empcod';
   sql := sql + ' WHERE ugd.codigo_departamento = :codigodepartamento';
   modulo_dados.fdquerysql7.close;
   modulo_dados.fdquerysql7.sql.clear;
   modulo_dados.fdquerysql7.sql.text := sql;
   modulo_dados.fdquerysql7.parambyname('codigodepartamento').asstring := codigodepartamento;
   if executaracao(modulo_dados.fdquerysql7, modulo_dados.fdbanco, true, modulo_dados.dtsfdquerysql7) then
     begin
        modulo_dados.dtsfdquerysql7.DataSet := modulo_dados.fdquerysql7;
        frmdepartamentos.gridlinksecao.DataSource := modulo_dados.dtsfdquerysql7;
        frmdepartamentos.gridlinksecao.refresh;
     end;
end;

function valida_empresa(nome_empresa : string) : string;
begin
  {DEVE CUIDAR DE TODOS OS DADOS REFERENTE A EMPRESA QUE O M�DULO UTILIZAR}
  // BUSCA O C�DIGO DO DEPARTAMENTO
  if frmdepartamentos.cboempresas.Text <> '' then
     begin
        sql:='SELECT empcod FROM USER_geoapolo_empresas WHERE empnome = :cboempresas';
        modulo_dados.fdquerysql.close;
        modulo_dados.fdquerysql.sql.clear;
        modulo_dados.fdquerysql.sql.text := sql;
        modulo_dados.fdquerysql.parambyname('cboempresas').asstring := frmdepartamentos.cboempresas.text;
        if executaracao(modulo_dados.fdquerysql, modulo_dados.fdbanco, true, modulo_dados.dtsfdquerysql) then
           result := modulo_dados.fdquerysql.FieldByName('empcod').AsString;
     end;
end;

procedure Tfrmdepartamentos.lblnomedepartamentoEnter(Sender: TObject);
begin
   if trim(lblcodigodepartamento.Text) = '0' then
      lblcodigodepartamento.Text := '1';
end;

procedure Tfrmdepartamentos.lblnomedepartamentoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      cboempresas.SetFocus;
end;

procedure Tfrmdepartamentos.lbllinkestruturaEnter(Sender: TObject);
begin
   if (lblcctrlcodestr.text <> '') and (lbllinkcctrlnome.Caption = '...') then
      lbllinkcctrlnome.Caption:=retorna_nomecentroctrl(lblcctrlcodestr.text);
end;

procedure Tfrmdepartamentos.lbllinkestruturaKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = VK_F4 then
      spbestruturamixlink.click;
end;

procedure Tfrmdepartamentos.lbllinkdepartamentoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f4 then
      spbbuscalinksecao.Click;
   //
   if (key = vk_return) or (key = vk_tab) then
      lblcctrlcodestr.setfocus;
end;

procedure Tfrmdepartamentos.lblprocurarporKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      mostradepartamento('E');
end;

procedure Tfrmdepartamentos.lbldptodestinoEnter(Sender: TObject);
begin
   if (lbldptoorigem.text <> '') and (lblnomesecao_origem.Caption = 'Departamento de Origem') then
      begin
         lblnomesecao_origem.Caption:=retorna_nomedepartamento(lbldptoorigem.Text);
         lblnomesecao_origem.refresh;
      end;
end;

function retorna_nomedepartamento(codigo: string) : string;
begin
   sql:='SELECT descricao FROM USER_geoapolo_departamentos WHERE codigo_departamento = :codigodepartamento';
   modulo_dados.fdquerysql2.close;
   modulo_dados.fdquerysql2.sql.clear;
   modulo_dados.fdquerysql2.sql.text := sql;
   modulo_dados.fdquerysql2.parambyname('codigodepartamento').asstring := codigo;
   if executaracao(modulo_dados.fdquerysql2, modulo_dados.fdbanco, true, modulo_dados.dtsfdquerysql2) then
      result := modulo_dados.fdquerysql2.FieldByName('descricao').AsString;
end;

function retorna_nomecentroctrl(cctrlcodestr : string) : string;
begin
   sql:='SELECT cctrlnome FROM centro_ctrl WHERE cctrlcodestr = :cctrlcodestr';
   modulo_dados.fdquerysql.close;
   modulo_dados.fdquerysql.sql.clear;
   modulo_dados.fdquerysql.sql.text := sql;
   modulo_dados.fdquerysql.parambyname('cctrlcodestr').asstring := cctrlcodestr;
   if executaracao(modulo_dados.fdquerysql, modulo_dados.fdbanco, true, modulo_dados.dtsfdquerysql) then
      result := modulo_dados.fdquerysql.FieldByName('cctrlnome').AsString;
end;

function retorna_estruturamix(esidestrutura : string) : string;
begin
   with frmdepartamentos,modulo_dados do
   begin
      sql:='SELECT ES_ID_ESTRUTURA,ES_NOME FROM mix.dbo.BS_ESTRUTURA';
      sql:=sql+' WHERE ES_ID_ESTRUTURA = :esidestrutura';
      sql:=sql+' ORDER BY ES_ID_ESTRUTURA ASC';
      modulo_dados.fdquerysql.parambyname('esidestrutura1').asstring := esidestrutura;
      if executaracao(modulo_dados.fdquerysql, modulo_dados.fdbanco, true, modulo_dados.dtsfdquerysql) then
         begin
            result := modulo_dados.fdquerysql.FieldByName('ES_NOME').AsString;
         end;
   end;
end;

procedure Tfrmdepartamentos.lbldptodestinoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_f4) then
      spbuscasecdestino.click;
   if (key = vk_return) or (key = vk_tab) then
      btnAplicar.click;
end;

procedure Tfrmdepartamentos.lbldptoorigemKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_f4) then
      spbuscasecorigem.click;
   if (key = vk_return) or (key = vk_tab) then
      lbldptodestino.setfocus;
end;

procedure Tfrmdepartamentos.popmenugravaconfigClick(Sender: TObject);
begin
   grava_config_telabusca('DEPARTAMENTOS',cbocampo.Text,cbordem.Text,'A',frmdepartamentos);
end;

procedure Tfrmdepartamentos.rdgcrescenteClick(Sender: TObject);
begin
   wordem:='ASC';
end;

procedure Tfrmdepartamentos.rdgdecrescenteClick(Sender: TObject);
begin
   wordem:='DESC';
end;

procedure Tfrmdepartamentos.spblimparClick(Sender: TObject);
begin
   lblnomedepartamento.Clear; cboempresas.itemindex:=-1; lblcctrlcodestr.Clear;
   lbllinkcctrlnome.Caption := '...';
   controle:='INCLUSÃO';
   lblcodigodepartamento.Refresh;
   mostradepartamento('');
end;

procedure Tfrmdepartamentos.FormActivate(Sender: TObject);
var
   sql:string;
begin
   with modulo_dados do
   begin
      cin.ActivePageIndex:=0; cin.refresh;
      statusbar1.Panels[1].text := configura_statusbar('a');
      statusbar1.Panels[3].Text:= configura_statusbar('a');
      statusbar1.Panels[5].text := frmprincipal.nomeserversql;
      statusbar1.Refresh;
      controle:='INCLUSÃO'; wordem:='ASC';
      sql:='SELECT empnome FROM USER_geoapolo_empresas ORDER BY empnome ASC';
      fdquerysql.close;
      fdquerysql.sql.clear;
      fdquerysql.sql.text := sql;
      if executaracao(modulo_dados.fdquerysql, modulo_dados.fdbanco, true, modulo_dados.dtsfdquerysql) then
         begin
            modulo_dados.fdquerysql.First;
            while not modulo_dados.fdquerysql.Eof do
            begin
               cboempresas.Items.Add(modulo_dados.fdquerysql.FieldByName('empnome').AsString);
               modulo_dados.fdquerysql.Next;
            end;
         end
       else
          begin
             messagedlg('TABELA DE EMPRESAS VAZIA, N�O SER� PERMITIDO A MANUTEN��O NOS DEPARTAMENTOS !!!',mtwarning,[mbok],0);
             exit;
          end;
       mostradepartamento('');
       carrega_config('DEPARTAMENTOS',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
       configura_grid('DEPARTAMENTOS',frmConsulta3,'gridconsulta3',frmlogon.nomeusuario,griddepartamentos,modulo_dados.dtsfdquerysql);

      // checa a configuraçaoo do geoapolo para ver se há integraçãoentre os departamentos do geoapolo com os centro de controle
      // do alvo
      sql:='SELECT integra_geosec_cctrlcodestr FROM USER_geoapolo_configuracoes';
      modulo_dados.fdquerysql.close;
      modulo_dados.fdquerysql.sql.clear;
      modulo_dados.fdquerysql.sql.text := sql;
      if executaracao(modulo_dados.fdquerysql, modulo_dados.fdbanco, true, modulo_dados.dtsfdquerysql) then
         begin
            if modulo_dados.fdquerysql.FieldByName('integra_geosec_cctrlcodestr').AsString = 'N' then
               begin
                  lblcctrlcodestr.Visible := false;
                  integracao := 'N';
               end
            else if modulo_dados.fdquerysql.FieldByName('integra_geosec_cctrlcodestr').AsString = 'S' then
               begin
                  lblcctrlcodestr.Visible := true;
                  integracao := 'S';
               end;
         end;
     secaoativa:='A';
     lblcodigodepartamento.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_departamentos','Sim');
     lblcodigodepartamento.Refresh; lblnomedepartamento.SetFocus;
   end;
end;

procedure Tfrmdepartamentos.btnAplicarClick(Sender: TObject);
begin
{   with modulo_dados do
   begin
      if (lblsecao_origem.text = '') or (lblsecaodestino.text = '') then
         begin
            messagedlg('� PRECISO INFORMAR A SE��O DE ORIGEM E DESTINO !!!',mterror,[mbok],0);
            lblsecao_origem.setfocus;
            exit;
         end;
      //
      resp:=messagedlg('Confirma a Transfer�ncia de Dados e Remo��o da Se��o de Origem ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
      if resp = idyes then
         begin
            // TRANSFER�NCIA DA TABELA DE USU�RIOS;
            memoacao.clear;
            sql:='UPDATE USER_geoapolo_usuarios SET codigo_departamento = '+lblsecaodestino.text+' WHERE codigo_departamento = '+lblsecao_origem.text;
            executaracao(sql,querysql3);
            if querysql3.RowsAffected > 0 then
               begin
                  memoacao.lines.add('TABELA DE USU�RIOS : '+inttostr(querysql3.RowsAffected));
                  memoacao.refresh;
               end;
            // TRANSFER�NCIA DA TABELA GEOAPOLOSCL_PERIODO
            sql:='UPDATE geoapoloscl_periodo SET codigo_secaomaior = '+lblsecaodestino.text+' WHERE codigo_secaomaior = '+lblsecao_origem.text;
            executaracao(sql,querysql3);
            if querysql3.RowsAffected > 0 then
               begin
                  memoacao.lines.add('TABELA GEOAPOLOSCL_PERIODO : '+inttostr(querysql3.RowsAffected));
                  memoacao.refresh;
               end;
            // TRANSFER�NCIA DA TABELA SCLPABX_RAMAIS
            sql:='UPDATE sclpabx_ramais SET codigo_secao = '+lblsecaodestino.text+' WHERE codigo_secao = '+lblsecao_origem.text;
            executaracao(sql,querysql3);
            if querysql3.RowsAffected > 0 then
               begin
                  memoacao.lines.add('TABELA SCLPABX_RAMAIS : '+inttostr(querysql3.RowsAffected));
                  memoacao.refresh;
               end;
            // AP�S TRANSFERIR TODOS OS RESULTADOS DAS SE��ES, DEVER� DELETAR A SE��O DE ORIGEM
            sql:='DELETE FROM geoapolo_secao WHERE codigo_secao = '+lblsecao_origem.text;
            executaracao(sql,querysql3);
            if querysql3.RowsAffected > 0 then
               begin
                  messagedlg('SE��O DE ORIGEM REMOVIDA COM SUCESSO !!!',mtinformation,[mbok],0);
                  lblsecao_origem.clear;lblsecaodestino.clear;
                  lblnomesecao_origem.Caption:='Se��o Origem'; lblsecao_destino.Caption:='Se��o Destino';
                  lblsecao_origem.setfocus;
               end;

         end
      else
         begin
            lblsecao_origem.setfocus;
            exit;
         end;
   end;        }
end;

procedure Tfrmdepartamentos.btnAplicarEnter(Sender: TObject);
begin
   if (lbldptodestino.text <> '') and (lblsecao_destino.Caption = 'Se��o Destino') then
      begin
         lblsecao_destino.Caption:=retorna_nomedepartamento(lbldptodestino.text);
         lblsecao_destino.refresh;
      end;
end;

procedure Tfrmdepartamentos.btnCancelarClick(Sender: TObject);
begin
   lbldptoorigem.clear;
   lbldptodestino.clear; lbldptoorigem.setfocus;
end;

procedure Tfrmdepartamentos.cboempresasKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_return then
      spbsalvar.Click;
end;

procedure Tfrmdepartamentos.spbsalvalinkClick(Sender: TObject);
begin
   with modulo_dados do
   begin
{      if (lbllinkestrutura.text <> '') and (lbleslinknome.Caption = '...') then
         begin
            lbleslinknome.caption:=retorna_estruturamix(lbllinkestrutura.Text);
         end;
      resp:=messagedlg('Confirma os Vinculos (Y/N)',mtconfirmation,[mbyes,mbno],0);
      if resp = idyes  then
         begin
            sql:='INSERT INTO geoapolo_secoescctrlapolo(codigo_secao,cctrlcodestr,cctrlnome, es_id_estrutura, es_nome)';
            sql:=sql+' VALUES ('+lbllinksecao.text+', '+quotedstr(lblcctrlcodestr.text)+', '+quotedstr(lbllinkcctrlnome.caption);
            sql:=sql+', '+quotedstr(lbllinkestrutura.text)+', '+quotedstr(lbleslinknome.Caption)+');';
            executaracao(sql,querysql3);
            if querysql3.RowsAffected > 0 then
               begin
                  lbllinksecao.clear; lblnomelinksecao.caption :='...';
                  lblcctrlcodestr.clear; lbllinkcctrlnome.caption:='...';
                  lbllinkestrutura.clear; lbleslinknome.caption :='...';
                  lbllinksecao.Refresh; lblnomelinksecao.refresh; lblcctrlcodestr.Refresh; lbllinkcctrlnome.Refresh;
                  lbllinkestrutura.Refresh; lbleslinknome.refresh; lbllinksecao.refresh; lblnomelinksecao.refresh;
                  mostra_vinculosecao(lblcodigosecao.Text);
                  lbllinksecao.setfocus;
               end
            else
               begin
                  messagedlg('ERRO AO VINCULAR A SE��O COM O CENTRO DE CONTROLE E ESTRUTURA DA FOLHA !!!',mterror,[mbok],0);
                  lbllinksecao.setfocus;
                  exit;
               end;
         end;}
   end;
end;

procedure Tfrmdepartamentos.spbsalvarClick(Sender: TObject);
var
   sql1:string;
begin
   with modulo_dados do
   begin
      //
      if lblnomedepartamento.Text  = '' then
         begin
            messagedlg('INFORME O NOME DO DEPARTAMENTO QUE DESEJA CADASTRAR !!!',mterror,[mbok],0);
            lblnomedepartamento.SetFocus;
            exit;
         end;
      //
      if cboempresas.Text = '' then
         begin
            messagedlg('INFORME A EMPRESA QUE DESEJA VINCULAR ESTE DEPARTAMENTO !!!',mterror,[mbok],0);
            cboempresas.SetFocus;
            exit;
         end;
      //
      if lblcctrlcodestr.text <> '' then
         begin

         end;
      resp:=messagedlg('Confirma esta Operação de '+controle+' (Y/N)',mtconfirmation,[mbyes,mbno],0);
      if resp = idyes then
         begin
            if controle = 'INCLUSÃO' then
               begin
                  if secaoativa = '' then
                     secaoativa:='A';
                  sql:='INSERT INTO USER_geoapolo_departamentos (codigo_departamento,nome_departamento, empcod, flagativo)';
                  sql:=sql1+' VALUES (:codigodepartamento, :nomedepartamento, :empresa, :flagativo)';
               end
            else if controle = 'ALTERAÇÃO' then
               begin
                  sql:='UPDATE USER_geoapolo_departamentos SET nome_departamento = :nomedepartamento, ' +
                         ' empcod = :empresa, flagativo = :flagativo ' +
                         ' WHERE codigo_departamento = :codigodepartamento;';
               end;
            modulo_dados.fdquerysql3.close;
            modulo_dados.fdquerysql3.sql.clear;
            modulo_dados.fdquerysql3.sql.text := sql;
            modulo_dados.fdquerysql3.parambyname('codigodepartamento').asstring := lblcodigodepartamento.text;
            modulo_dados.fdquerysql3.parambyname('nomedepartamento').asstring := lblnomedepartamento.text;
            modulo_dados.fdquerysql3.parambyname('empresa').asstring :=valida_empresa(cboempresas.Text);
            modulo_dados.fdquerysql3.parambyname('flagativo').asstring := secaoativa;

            if executaracao(modulo_dados.fdquerysql3, modulo_dados.fdbanco, true, modulo_dados.dtsfdquerysql3) then
               begin
                  messagedlg('A OPERAÇÃO DE '+CONTROLE+' FOI REALIZADA COM SUCESSO !!!',mtinformation,[mbok],0);
                  lblcodigodepartamento.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_departamentos','Sim');
                  spblimpar.Click;
                  controle:='INCLUSÃO';
                  lblnomedepartamento.SetFocus;
                  exit
               end
            else
               begin
                  messagedlg('ERRO AO EXECUTAR A '+CONTROLE+' PARA ESTE DEPARTAMENTO !!!',mterror,[mbok],0);
                  spblimpar.Click;
                  exit;
               end;
         end
      else
         begin
            lblnomedepartamento.setfocus;
            controle:='INCLUSÃO';
            exit;
         end;
   end;
end;

function valida_centrocontrole(codigosecao:string; integracao:string) : string;
begin
 {  with modulo_dados, frmcadsecao do
   begin
      if (integracao = 'S') and (lblcctrlcodestr.Text <> '') then
         begin
            sql:='SELECT * FROM geoapolo_secoescctrlapolo WHERE codigo_secao = '+codigosecao;
            executaracao(sql,querysql2);
            if querysql2.RecordCount > 0 then
               begin
                  sql:='UPDATE geoapolo_secoescctrlapolo set cctrlcodestr = '+chr(39)+lblcctrlcodestr.Text+chr(39)+' WHERE codigo_secao = '+lblcodigosecao.Text+';';
                  executaracao(sql,querysql3);
                  if querysql3.RowsAffected > 0 then
               end
            else
               begin
                  sql:='INSERT INTO geoapolo_secoescctrlapolo (codigo_secao,cctrlcodestr) VALUES ('+codigosecao+', '+chr(39)+lblcctrlcodestr.Text+chr(39)+');';
                  executaracao(sql,querysql3);
                  if querysql3.RowsAffected > 0 then
               end;
         end;
   end;}
end;

procedure Tfrmdepartamentos.spbdeletarClick(Sender: TObject);
begin
   messagedlg('PARA EXCLUIR UM DEPARTAMENTO ELE N�O PODE TER NENHUM V�NCULO NO SISTEMA !!!',mtinformation,[mbok],0);
   griddepartamentos.SetFocus;
end;

procedure Tfrmdepartamentos.spbestruturamixlinkClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      sql:='SELECT ES_ID_ESTRUTURA,ES_NOME';
      sql:=sql+' FROM mix.dbo.BS_ESTRUTURA';
      sql:=sql+' ORDER BY ES_ID_ESTRUTURA ASC';
      if executaracao(modulo_dados.fdquerysql4, modulo_dados.fdbanco, true, modulo_dados.dtsfdquerysql4) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            frmconsulta3.controle := 'ESTRUTURA_MIX';
            with frmconsulta3 do
            begin
               modulo_dados.dtsfdquerysql4.DataSet := modulo_dados.fdquerysql4;
               gridconsulta.DataSource := dtsfdquerysql4;
               gridconsulta.Refresh;
            end;
            frmconsulta3.showmodal;
         end;
   end;
end;

procedure Tfrmdepartamentos.gridlinksecaoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   with modulo_dados do
   begin
{      if key = VK_DELETE then
         begin
            resp:=messagedlg('Confirma a Remo��o destes Vinculos (Y/N)',mtconfirmation,[mbyes,mbno],0);
            if resp = IDYES then
               begin
                  sql:='DELETE FROM geoapolo_secoescctrlapolo WHERE codigo_secao = '+querysql7.fieldbyname('codigo_secao').asstring;
                  executaracao(sql,querysql3);
                  if querysql3.RowsAffected > 0 then
                     begin
                        messagedlg('VINCULO REMOVIDO COM SUCESSO !!!!',mtinformation,[mbok],0);
                        lbllinksecao.clear; lblnomelinksecao.caption :='...';
                        lblcctrlcodestr.clear; lbllinkcctrlnome.caption:='...';
                        lbllinkestrutura.clear; lbleslinknome.caption :='...';
                        lbllinksecao.Refresh; lblnomelinksecao.refresh; lblcctrlcodestr.Refresh; lbllinkcctrlnome.Refresh;
                        lbllinkestrutura.Refresh; lbleslinknome.refresh; lbllinksecao.refresh; lblnomelinksecao.refresh;
                        mostra_vinculosecao(lblcodigodepartamento.Text);
                     end
                  else
                     begin
                        messagedlg('ERRO AO TENTAR REMOVER O VINCULO DA SE��O !!!',mterror,[mbok],0);
                        exit;
                     end;
               end
            else
               begin
                  lbllinksecao.setfocus;
                  exit;
               end;
         end;}
   end;
end;

procedure Tfrmdepartamentos.griddepartamentosDblClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      controle:='ALTERAÇÃO';
      lblcodigodepartamento.Text := modulo_dados.fdquerysql2.FieldByName('codigo_departamento').AsString;
      mostra_vinculodepartamento(modulo_dados.fdquerysql2.FieldByName('codigo_departamento').AsString);
      lblnomedepartamento.Text := modulo_dados.fdquerysql2.FieldByName('nome_departamento').AsString;
      //carrega_dados(fdquerysql2,frmcadsecao);
      secaoantiga := lblcodigodepartamento.Text;
      buscanacombo(modulo_dados.fdquerysql2.FieldByName('empnome').AsString, frmdepartamentos, cboempresas);
      //
      if modulo_dados.fdquerysql2.FieldByName('flagativo').AsString = 'A' then
         chkdeptoativo.Checked := true
      else
         chkdeptoativo.Checked := false;
      //
      chkdeptoativo.Refresh;
      frmdepartamentos.Refresh;
   end;
end;

procedure Tfrmdepartamentos.griddepartamentosKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   with modulo_dados do
   begin
      if key = vk_delete then
         begin
            messagedlg('Lembre-se que para excluir um Departamento, ele não pode ter nenhum vinculo no sistema !!!',mtinformation,[mbok],0);
            resp:=messagedlg('Confirma a Exclusão deste Departamento?(Y/N)',mtconfirmation,[mbyes,mbno],0);
            if resp = idyes then
               begin
                  sql := 'DELETE FROM USER_geoapolo_departamentos WHERE codigo_departamento = :codigodepartamento';
                  modulo_dados.fdquerysql3.close;
                  modulo_dados.fdquerysql3.sql.clear;
                  modulo_dados.fdquerysql3.sql.text := sql;
                  modulo_dados.fdquerysql3.parambyname('codigodepartamento').asstring := modulo_dados.fdquerysql2.FieldByName('codigo_departamento').AsString;
                  if executaracao(modulo_dados.fdquerysql3, modulo_dados.fdbanco, true, modulo_dados.dtsfdquerysql3) then
                     begin
                        messagedlg('Exclusão efetuada com sucesso !!!',mtinformation,[mbok],0);
                        spblimpar.click;
                        mostradepartamento('');
                        lblnomedepartamento.setfocus;
                     end
                  else
                     begin
                        messagedlg('A exclusão não foi permitida, algum vinculo existe com este departamento !!!',mterror,[mbok],0);
                        cin.ActivePageIndex:=1;
                        lblnomedepartamento.setfocus;
                        exit;
                     end;
               end
            else
               begin
                  spblimpar.Click;
                  lblnomedepartamento.SetFocus;
               end;
         end;
   end;
end;

procedure Tfrmdepartamentos.spbabreosClick(Sender: TObject);
begin
   messagedlg('PARA LOCALIZAR UMA SE��O, PROCURE NO GRID E D� UM DUPLO CLICK OU DIGITE NO NOME DELA NO CAMPO E PRESSIONE ENTER !!!',mtinformation,[mbok],0);
   lblnomedepartamento.setfocus;
end;

procedure Tfrmdepartamentos.spbbuscalinksecaoClick(Sender: TObject);
begin
   with frmprincipal, modulo_dados do
   begin
      {montar a consulta e colocar abaixo}
      sql := 'SELECT * FROM mostrasecao';
      modulo_dados.fdquerysql6.close;
      modulo_dados.fdquerysql6.sql.clear;
      modulo_dados.fdquerysql6.sql.text := sql ;
      if executaracao(modulo_dados.fdquerysql6, modulo_dados.fdbanco, true, modulo_dados.dtsfdquerysql6) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            frmconsulta3.controle := 'SECAO_LINK';
            modulo_dados.dtsfdquerysql6.DataSet := modulo_dados.fdquerysql6;
            frmconsulta3.gridconsulta.DataSource := modulo_dados.dtsfdquerysql6;
            frmconsulta3.ShowModal;
         end;
   end;
end;

procedure Tfrmdepartamentos.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f10 then
      spbretornar.Click;
   //
  //
  with modulo_dados do
  begin
      if key = vk_f2 then
         begin
            {sql:='SELECT sec.codigo_secao, sec.descricao as Secao, dep.descricao as departamento, sec.producao_tv, sec.flagativo FROM secao sec, departamento dep ';
            sql:=sql+' WHERE sec.codigo_depto = dep.codigo_depto and sec.descricao like '+chr(39)+'%'+inputbox('Informe o nome da Se��o','Se��o','')+'%'+chr(39);}
            // view: geoapolo_secao
            sql := 'SELECT * FROM geoapolo_secao WHERE secao like :nomedodepartamento';
            modulo_dados.fdquerysql2.close;
            modulo_dados.fdquerysql2.sql.clear;
            modulo_dados.fdquerysql2.sql.text := sql;
            modulo_dados.fdquerysql2.parambyname('nomedodepartamento').asstring := '%'+inputbox('Informe o nome do Departamento','Departamento','')+'%';
            if executaracao(modulo_dados.fdquerysql2, modulo_dados.fdbanco, true, modulo_dados.dtsfdquerysql2) then
               begin
                  modulo_dados.dtsfdquerysql2.DataSet := modulo_dados.fdquerysql2;
                  griddepartamentos.DataSource := modulo_dados.dtsfdquerysql2;
                  griddepartamentos.Refresh;
               end;
         end;
  end;
end;

procedure Tfrmdepartamentos.lblcodigodepartamentoKeyPress(Sender: TObject;
  var Key: Char);
begin
  // S� ENTRA NUMERO
  If not( key in['0'..'9',#8] ) then
    begin
       beep;
       key:=#0;
    end;
end;

procedure Tfrmdepartamentos.lblcodigodepartamentoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lblnomedepartamento.SetFocus;
end;

procedure Tfrmdepartamentos.spbuscasecdestinoClick(Sender: TObject);
begin
   with frmprincipal, modulo_dados do
   begin
      {montar a consulta e colocar abaixo}
      sql := 'SELECT * FROM USER_geoapolo_departamentos ORDER BY codigo_departamento ASC';
      modulo_dados.fdquerysql6.close;
      modulo_dados.fdquerysql6.sql.clear;
      modulo_dados.fdquerysql6.sql.text := sql;
      if executaracao(modulo_dados.fdquerysql6, modulo_dados.fdbanco, true, modulo_dados.dtsfdquerysql6) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            frmconsulta3.controle := 'SECAO-DESTINO';
            modulo_dados.dtsfdquerysql6.DataSet := modulo_dados.fdquerysql6;
            frmconsulta3.gridconsulta.DataSource := modulo_dados.dtsfdquerysql6;
            frmconsulta3.ShowModal;
         end;
   end;
end;

procedure Tfrmdepartamentos.spbuscasecorigemClick(Sender: TObject);
begin
   with frmprincipal, modulo_dados do
   begin
      {montar a consulta e colocar abaixo}
      sql := 'SELECT * FROM USER_geoapolo_departamentos ORDER BY codigo_departamento ASC';
      modulo_dados.fdquerysql6.close;
      modulo_dados.fdquerysql6.sql.clear;
      modulo_dados.fdquerysql6.sql.text := sql;
      if executaracao(modulo_dados.fdquerysql6, modulo_dados.fdbanco, true, modulo_dados.dtsfdquerysql6) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            frmconsulta3.controle := 'SECAO-ORIGEM';
            modulo_dados.dtsfdquerysql6.DataSet := modulo_dados.fdquerysql6;
            frmconsulta3.gridconsulta.DataSource := modulo_dados.dtsfdquerysql6;
            frmconsulta3.ShowModal;
         end;
   end;
end;

procedure Tfrmdepartamentos.tblintegraapoloEnter(Sender: TObject);
begin
   mostra_vinculodepartamento(lblcodigodepartamento.Text);
end;

procedure Tfrmdepartamentos.spbuscalinkccClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      if (frmprincipal.integraentidadesapolo = 'Não Integra') then
         begin
            sql:='SELECT ugcc.geocctrlcodestr, ugcc.geoctrlcodreduzido, ugcc.geocctrlnome';
            sql:=sql+' FROM USER_geoapolo_centrocontrole ugcc with(nolock)';
         end
      else
         sql := 'SELECT cctrlcodestr, cctrlnome FROM centro_ctrl ORDER BY cctrlcodestr ASC';
      modulo_dados.fdquerysql4.close;
      modulo_dados.fdquerysql4.sql.clear;
      modulo_dados.fdquerysql4.sql.text := sql;
      if executaracao(modulo_dados.fdquerysql4, modulo_dados.fdbanco, true, modulo_dados.dtsfdquerysql4) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            frmconsulta3.controle := 'CENTRO_DE_CONTROLE_SECAO';
            with frmconsulta3 do
            begin
               dtsfdquerysql4.DataSet := modulo_dados.fdquerysql4;
               gridconsulta.DataSource := modulo_dados.dtsfdquerysql4;
               gridconsulta.Refresh;
            end;
            frmconsulta3.showmodal;
         end;
   end;
end;

procedure Tfrmdepartamentos.lblcctrlcodestrEnter(Sender: TObject);
begin
   if (lbllinkdepartamento.text <> '') and (lblnomelinksecao.caption = '...') then
      begin
         lblnomelinksecao.caption:= retorna_nomedepartamento(lbllinkdepartamento.text);
         lblnomelinksecao.Refresh;
      end;
end;

procedure Tfrmdepartamentos.lblcctrlcodestrKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_escape)) then
      spbsalvar.Click;
   if key = vk_f4 then
      spbuscalinkcc.click;
   if key = vk_delete  then
      begin
         with modulo_dados do
         begin
            sql := 'DELETE FROM geoapolo_secoescctrlapolo WHERE codigo_secao = :codigodepartamento';
            modulo_dados.fdquerysql3.close;
            modulo_dados.fdquerysql3.sql.clear;
            modulo_dados.fdquerysql3.sql.text := sql;
            modulo_dados.fdquerysql3.parambyname('codigodepartamento').asstring:= lblcodigodepartamento.Text;
            if executaracao(modulo_dados.fdquerysql3, modulo_dados.fdbanco, true, modulo_dados.dtsfdquerysql3) then
               begin
                  messagedlg('O VINCULO ENTRE A SE��O E O CENTRO DE CONTROLE DO APOLO FOI REMOVIDO COM SUCESSO !!!',mtinformation,[mbok],0);
                  lblnomedepartamento.setfocus;
                  exit;
               end
            else
               begin
                  messagedlg('PROBLEMAS AO TENTAR REMOVER O VINCULO ENTRE A SE��O E OS CENTROS DE CONTROLE DO APOLO !!!',mterror,[mbok],0);
                  lblnomedepartamento.setfocus;
                  exit;
               end;
         end;
      end;
end;

procedure Tfrmdepartamentos.chkdeptoativoClick(Sender: TObject);
begin
   if chkdeptoativo.Checked = true then
      secaoativa:='A'
   else if chkdeptoativo.Checked = false then
      secaoativa:='I';
end;

end.
