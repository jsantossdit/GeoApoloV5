unit unt_cadtipotratamento;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.ComCtrls, Vcl.StdCtrls, Vcl.Buttons,
  Vcl.ExtCtrls, Data.DB, Vcl.Grids, Vcl.DBGrids, Vcl.Mask;

type
  Tfrmcadtipotratamento = class(TForm)
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spblimpar: TSpeedButton;
    spbdeletar: TSpeedButton;
    spbabreos: TSpeedButton;
    spbretornar: TSpeedButton;
    lblmsg1: TLabel;
    StatusBar1: TStatusBar;
    grptipotratamento: TGroupBox;
    lbltipotratcod: TLabeledEdit;
    lblabreviatura: TLabeledEdit;
    lbldescricaotratamento: TLabeledEdit;
    gridtipotratamento: TDBGrid;
    procedure spbretornarClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure FormActivate(Sender: TObject);
    procedure lblabreviaturaKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lbldescricaotratamentoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spblimparClick(Sender: TObject);
    procedure spbabreosClick(Sender: TObject);
    procedure spbdeletarClick(Sender: TObject);
    procedure spbsalvarClick(Sender: TObject);
    procedure gridtipotratamentoDblClick(Sender: TObject);
    procedure gridtipotratamentoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  frmcadtipotratamento: Tfrmcadtipotratamento;
  controle:string;
  resp:word;

function mostra_tipotratamento : string; export;

implementation

{$R *.dfm}

uses unt_dados, funcoes, unt_consultav3, unt_logon, unt_selecionaempresa,
  unt_principal;



procedure Tfrmcadtipotratamento.FormActivate(Sender: TObject);
begin
   statusbar1.Panels[2].Text := configura_statusbar('a');
   statusbar1.Refresh;
   mostra_tipotratamento;
   lbltipotratcod.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_tipotratamento','S');
   lbltipotratcod.Refresh;
   controle:='INCLUSÃO';
   lblabreviatura.SetFocus;
end;

procedure Tfrmcadtipotratamento.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
   action:=cafree;
end;

procedure Tfrmcadtipotratamento.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f10 then
      spbretornar.Click;
end;

procedure Tfrmcadtipotratamento.gridtipotratamentoDblClick(Sender: TObject);
begin
   with modulo_dados do
   begin
     controle:='ALTERAÇÃO';
     lbltipotratcod.Text := fdquerysql4.FieldByName('tipotratcod').AsString;
     lblabreviatura.Text := fdquerysql4.FieldByName('abreviatura').AsString;
     lbldescricaotratamento.Text := fdquerysql4.FieldByName('descricao_tratamento').AsString;
     lblabreviatura.SetFocus;
   end;
end;

procedure Tfrmcadtipotratamento.gridtipotratamentoKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   with modulo_dados do
   begin
     if key = vk_delete  then
        begin
          messagedlg('PARA REMOVER ALGUM TIPO DE TRATAMENTO, O MESMO NÃO PODE ESTAR LIGADO A NENHUMA ENTIDADE !!!',mtwarning,[mbok],0);
          resp:=messagedlg('Confirma a remoção deste Tipo de tratamento ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
          if resp = idyes  then
             begin
               sql:='DELETE FROM USER_geoapolo_tipotratamento WHERE tipotratcod = :ptipotratcod';
               fdquerysql3.Close;
               fdquerysql3.SQL.Clear;
               fdquerysql3.SQL.Text:= sql;
               fdquerysql3.ParamByName('ptipotratcod').AsString :=fdquerysql4.FieldByName('tipotratcod').AsString;
               if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                  begin
                    messagedlg('TIPO DE TRATAMENTO REMOVIDO COM SUCESSO !!!',mtinformation,[mbok],0);
                    mostra_tipotratamento;
                    lblabreviatura.SetFocus;
                  end
               else
                  begin
                    messagedlg('ERRO AO TENTAR REMOVER ESTE TIPO DE TRATAMENTO, VERIFIQUE SE NÃO ESTÁ RELACIONADO A ALGUMA ENTIDADE !!!',mterror,[mbok],0);
                    lblabreviatura.SetFocus;
                    exit;
                  end;
             end;
        end;
   end;
end;

procedure Tfrmcadtipotratamento.lblabreviaturaKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lbldescricaotratamento.setfocus;
end;

procedure Tfrmcadtipotratamento.lbldescricaotratamentoKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      spbsalvar.Click;
end;

procedure Tfrmcadtipotratamento.spbabreosClick(Sender: TObject);
begin
   messagedlg('OPÇÃO NÃO IMPLEMENTADA !!!',mtwarning,[mbok],0);
end;

procedure Tfrmcadtipotratamento.spbdeletarClick(Sender: TObject);
begin
   messagedlg('PARA REMOVER ALGUM TIPO DE TRATAMENTO, O MESMO NÃO PODE TER VINCULOS NO SISTEMA, SELECIONE O REGISTRO E PRESSIONE DELETE !!!',mtwarning,[mbok],0);
   gridtipotratamento.SetFocus;
end;

procedure Tfrmcadtipotratamento.spblimparClick(Sender: TObject);
begin
   lblabreviatura.clear; lbldescricaotratamento.Clear; controle:='INCLUSÃO';
   lblabreviatura.SetFocus;
end;

procedure Tfrmcadtipotratamento.spbretornarClick(Sender: TObject);
begin
   close;
end;

procedure Tfrmcadtipotratamento.spbsalvarClick(Sender: TObject);
begin
   with modulo_dados do
   begin
     if lblabreviatura.Text = '' then
        begin
          messagedlg('É OBRIGATÓRIO INFORMAR A ABREVIATURA PARA O TIPO DE TRATAMENTO !!!',mterror,[mbok],0);
          lblabreviatura.SetFocus;
          exit
        end;
     if lbldescricaotratamento.Text = '' then
        begin
          messagedlg('É OBRIGATÓRIO INFORMAR A DESCRIÇÃO PARA O TIPO DE TRATAMENTO !!!',mterror,[mbok],0);
          lbldescricaotratamento.SetFocus;
          exit
        end;
     //
     resp:=messagedlg('Confirma a '+controle+' PARA ESTE TIPO DE TRATAMENTO ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
     if resp = idyes  then
        begin
           if controle = 'INCLUSÃO' then
              begin
                 sql:='INSERT INTO USER_geoapolo_tipotratamento (tipotratcod,abreviatura,descricao_tratamento) ';
                 sql:=sql+' VALUES (:ptipotratcod, :pabreviatura, :pdescricaotipotratamento)';
              end
           else if controle = 'ALTERAÇÃO' then
              begin
                 sql:='UPDATE USER_geoapolo_tipotratamento SET abreviatura = :pabreviatura, descricao_tratamento = :pdescricaotipotratamento';
                 sql:=sql+' WHERE tipotratcod = :ptipotratcod';
              end;
           fdquerysql3.Close;
           fdquerysql3.SQL.Clear;
           fdquerysql3.SQL.Text := sql;
           fdquerysql3.ParamByName('ptipotratcod').AsString := lbltipotratcod.Text;
           fdquerysql3.ParamByName('pabreviatura').AsString := lblabreviatura.Text;
           fdquerysql3.ParamByName('pdescricaotipotratamento').AsString:= lbldescricaotratamento.Text;
           if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
              begin
                messagedlg('TIPO DE TRATAMENTO ATUALIZADO COM SUCESSO !!!',mtinformation,[mbok],0);
                spblimpar.Click;
                lbltipotratcod.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_tipotratamento','S');
                lbltipotratcod.Refresh;
                mostra_tipotratamento;
                lblabreviatura.SetFocus;
              end
           else
              begin
                 messagedlg('ERRO AO TENTAR ATUALIZAR TIPOS DE TRATAMENTO !!!',mterror,[mbok],0);
                 lblabreviatura.SetFocus;
              end;
        end
     else
        begin
          lblabreviatura.SetFocus;
          exit;
        end;
   end;
end;

function mostra_tipotratamento : string;
begin
  with modulo_dados,frmcadtipotratamento do
  begin
    sql:='SELECT * FROM USER_geoapolo_tipotratamento ORDER BY abreviatura ASC';
    fdquerysql4.Close;
    fdquerysql4.SQL.Clear;
    fdquerysql4.SQL.Text := sql;
    if executaracao(fdquerysql4, fdbanco, false, dtsfdquerysql4) then
       begin
         gridtipotratamento.datasource:= dtsfdquerysql4;
         gridtipotratamento.refresh;
       end;
  end;
end;

end.
