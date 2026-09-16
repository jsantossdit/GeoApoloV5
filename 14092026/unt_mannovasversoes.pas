unit unt_mannovasversoes;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.ComCtrls, Vcl.StdCtrls, Vcl.Buttons,
  Vcl.ExtCtrls, Data.DB, Vcl.Grids, Vcl.DBGrids, Vcl.Mask;

type
  Tfrmcadnovasversoes = class(TForm)
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spbligacoes: TSpeedButton;
    spbsair: TSpeedButton;
    spblimpar: TSpeedButton;
    lblsair: TLabel;
    spbexcluir: TSpeedButton;
    StatusBar1: TStatusBar;
    grpdadosdaversao: TGroupBox;
    lblidversao: TLabeledEdit;
    mskdtliberacao: TMaskEdit;
    lbldtliberacao: TLabel;
    lblnovidadesversao: TLabel;
    rcenovidades: TRichEdit;
    grpversoesgeoapolo: TGroupBox;
    gridversoes: TDBGrid;
    lblstatusdaversao: TLabel;
    cbostatusversao: TComboBox;
    procedure spbsalvarClick(Sender: TObject);
    procedure spbsairClick(Sender: TObject);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure FormActivate(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure gridversoesDblClick(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure lblidversaoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure mskdtliberacaoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure rcenovidadesKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbexcluirClick(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
    statusversao,controle:string;
  end;

var
  frmcadnovasversoes: Tfrmcadnovasversoes;


function carrega_versoes : string; export;

implementation

{$R *.dfm}

uses funcoes, unt_dados, unt_principal, unt_logon;

procedure Tfrmcadnovasversoes.FormActivate(Sender: TObject);
begin
   with frmprincipal,modulo_dados do
   begin
      statusbar1.Panels[1].text := configura_statusbar('a');
      statusbar1.Panels[3].text := configura_statusbar('a');
      statusbar1.Panels[5].text := frmprincipal.nomeserversql;
      if grpversoesgeoapolo.visible = false then
         begin
            grpversoesgeoapolo.Visible := true;
            grpversoesgeoapolo.left :=0;
            grpversoesgeoapolo.Top:=46;
            grpdadosdaversao.Visible:=false;
         end;
      frmcadnovasversoes.controle:='INCLUSÃO';
      carrega_versoes;
   end
end;

procedure Tfrmcadnovasversoes.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
   action:=cafree;
end;

procedure Tfrmcadnovasversoes.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   with frmprincipal, modulo_dados do
   begin
      if key = vk_f10 then
         spbsair.click;
      //
      if key = vk_insert then
         begin
            frmcadnovasversoes.controle:='INCLUSÃO';
            spblimpar.Click;
            grpversoesgeoapolo.Visible := false;
            grpdadosdaversao.Visible := true;
            lblidversao.SetFocus;
         end;
    end;
end;

procedure Tfrmcadnovasversoes.gridversoesDblClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      frmcadnovasversoes.controle:='ALTERAÇÃO';
      grpdadosdaversao.Visible :=true;
      rcenovidades.Lines.Move(rcenovidades.Lines.Count,1);
      rcenovidades.Refresh;
      grpdadosdaversao.Left:=8;
      grpdadosdaversao.top:= 70;
      lblidversao.text:= fdquerysql4.fieldbyname('idversao').asstring;
      mskdtliberacao.text:= fdquerysql4.FieldByName('data_lancamento').AsString;
      rcenovidades.Lines.text := fdquerysql4.fieldbyname('textonovaversao').asstring;
      if fdquerysql4.FieldByName('statusversao').asstring = 'S' then
         buscanacombo('Liberada',frmcadnovasversoes,cbostatusversao)
      else
         buscanacombo('Não Liberada',frmcadnovasversoes,cbostatusversao);
      grpdadosdaversao.Refresh;
      grpversoesgeoapolo.Visible:=false;
      lblidversao.setfocus;
   end;
end;

procedure Tfrmcadnovasversoes.lblidversaoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      mskdtliberacao.SetFocus;
end;

procedure Tfrmcadnovasversoes.mskdtliberacaoKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      cbostatusversao.SetFocus;
end;

procedure Tfrmcadnovasversoes.rcenovidadesKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_escape) then
      spbsalvar.Click;
end;

procedure Tfrmcadnovasversoes.spbexcluirClick(Sender: TObject);
begin
   messagedlg('PARA REMOVER ALGUMA VERSÃO QUE AINDA NÃO TENHA SIDO LIBERADA, SELECIONE O REGISTRO NO GRID E PRESSIONE <DELETE>',mtwarning,[mbok],0);
end;

procedure Tfrmcadnovasversoes.spblimparClick(Sender: TObject);
begin
   lblidversao.Clear; mskdtliberacao.Clear; rcenovidades.Clear;
end;

procedure Tfrmcadnovasversoes.spbsairClick(Sender: TObject);
begin
   close;
end;

procedure Tfrmcadnovasversoes.spbsalvarClick(Sender: TObject);
var
   dataversao:string;
begin
   with modulo_dados, frmprincipal,frmlogon do
   begin
      if cbostatusversao.text = 'Liberada' then
         statusversao:='S'
      else
         statusversao:='N';
      //
      if mskdtliberacao.text = '  /  /    ' then
         begin
            messagedlg('É OBRIGATÓRIO INFORMAR A DATA DE LIBERAÇÃO DE UMA NOVA VERSÃO !!!',mterror,[mbok],0);
            mskdtliberacao.SetFocus;
         end
      else
         begin
            dataversao:=copy(mskdtliberacao.Text,7,4)+'/'+copy(mskdtliberacao.Text,4,2)+'/'+copy(mskdtliberacao.Text,1,2);
         end;
      resp:=messagedlg('Confirma a '+frmcadnovasversoes.controle+' de uma Versão ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
      if resp = idyes  then
         begin
            if frmcadnovasversoes.controle = 'INCLUSÃO' then
               begin
                  sql:= 'INSERT INTO USER_geoapolo_novversao (idversao, data_lancamento, textonovaversao, statusversao)';
                  sql:=sql+' VALUES (:idversao, :dataliberacao, :novidades, :statusversao)';
               end
            else if frmcadnovasversoes.controle = 'ALTERAÇÃO' then
               begin
                  sql:='UPDATE USER_geoapolo_novversao SET textonovaversao = :novidades, statusversao = :statusversao, data_lancamento = :dataliberacao';
                  sql:=sql+' WHERE idversao = :idversao';
               end;
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('idversao').AsString := lblidversao.Text;
            fdquerysql3.ParamByName('dataliberacao').AsString := mskdtliberacao.Text;
            fdquerysql3.ParamByName('novidades').AsString := rcenovidades.Text;
            fdquerysql3.ParamByName('statusversao').AsString := statusversao;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  messagedlg('DADOS DA VERSÃO ATUALIZADO COM SUCESSO !!!',mtinformation,[mbok],0);
                  spblimpar.Click;
                  grpdadosdaversao.Visible:= false;
                  grpversoesgeoapolo.Visible := true;
                  carrega_versoes;
                  gridversoes.SetFocus;
               end;
         end;
   end;
end;

function carrega_versoes : string;
begin
   with modulo_dados, frmprincipal,frmcadnovasversoes do
   begin
      sql:='SELECT * FROM user_geoapolo_novversao';
      fdquerysql4.Close;
      fdquerysql4.SQL.Clear;
      fdquerysql4.SQL.Text := sql;
      if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
      if fdquerysql4.RecordCount > 0 then
         begin
            gridversoes.DataSource := dtsfdquerysql4;
            gridversoes.Refresh;
         end;
   end;
end;


end.
