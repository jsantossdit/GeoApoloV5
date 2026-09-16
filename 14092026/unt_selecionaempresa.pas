unit unt_selecionaempresa;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.Buttons, Vcl.ExtCtrls, Vcl.ComCtrls,
  Vcl.Grids, Vcl.DBGrids, Data.DB;

type
  Tfrmempresa = class(TForm)
    gridempresas: TDBGrid;
    StatusBar1: TStatusBar;
    panelmenu: TPanel;
    spbretornar: TSpeedButton;
    procedure spbretornarClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure gridempresasDblClick(Sender: TObject);
    procedure gridempresasKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure FormActivate(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
    empresajafoi:string;
  end;

var
  frmempresa: Tfrmempresa;

function selecionaempresa : string; export;

implementation

{$R *.dfm}

uses unt_dados, funcoes, unt_principal, unt_novidadesversao, unt_logon;

function selecionaempresa : string;
begin
   with modulo_dados, frmempresa do
   begin
      sql:='';
      sql:='SELECT empcod,empnome FROM USER_geoapolo_empresas ORDER BY empcod ASC';
      fdquerysql11.Close;
      fdquerysql11.SQL.Clear;
      fdquerysql11.sql.Text := sql;
      if executaracao(fdquerysql11, fdbanco, true, dtsfdquerysql11) then
         begin
            sql:='SELECT  integra_base_apolomix FROM USER_geoapolo_configuracoes';
            fdquerysql12.Close;
            fdquerysql12.SQL.Clear;
            fdquerysql12.SQL.Text := sql;
            if executaracao(fdquerysql12, fdbanco, true, dtsfdquerysql12) then
               begin
                 if fdquerysql12.FieldByName('integra_base_apolomix').AsString = 'S' then
                    sql:='SELECT empcod,empnome FROM empresa_filial ORDER BY empcod ASC'
                 else if (fdquerysql12.FieldByName('integra_base_apolomix').AsString = 'N') or (fdquerysql12.FieldByName('integra_base_apolomix').AsString = '') then
                    sql:='SELECT * FROM USER_geoapolo_empresas';
               end;
            fdquerysql12.Close;
            fdquerysql12.SQL.clear;
            fdquerysql12.SQL.Text := sql;
            if executaracao(fdquerysql12, fdbanco, true, dtsfdquerysql12) then
               begin
                  sql:='SELECT * FROM USER_geoapolo_empresas';
                  fdquerysql13.Close;
                  fdquerysql13.SQL.Clear;
                  fdquerysql13.SQL.Text := sql;
                  if not executaracao(fdquerysql13, fdbanco, true, dtsfdquerysql13) then
                     begin
                        fdquerysql13.First;
                        while not fdquerysql13.Eof  do
                        begin
                            sql:= 'INSERT INTO USER_geoapolo_empresas (empcod, empnome)';
                            sql:=sql+' VALUES (:empcod, :empnome)';
                            fdquerysql3.Close;
                            fdquerysql3.SQL.Clear;
                            fdquerysql3.SQL.Text := sql;
                            fdquerysql3.ParamByName('empcod').AsString :=fdquerysql12.fieldbyname('empcod').asstring;
                            fdquerysql3.ParamByName('empnome').AsString:=fdquerysql12.FieldByName('empnome').AsString;
                            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                               begin
                               end
                            else
                               begin
                                  messagedlg('ERRO AO ATUALIZAR TABELA DE EMPRESAS !!!',mterror,[mbok],0);
                                  exit;
                               end;
                            fdquerysql13.Next;
                        end;
                     end
               end
            else
               begin
                 sql:='SELECT * FROM USER_geoapolo_empresas ORDER BY empcod ASC';
                 fdquerysql11.Close;
                 fdquerysql11.SQL.Clear;
                 fdquerysql11.SQL.Text := sql;
                 if executaracao(fdquerysql11, fdbanco, true, dtsfdquerysql11) then
                    begin
                    end;
               end;
            gridempresas.datasource:=modulo_dados.dtsfdquerysql11;
            gridempresas.refresh;
         end;
   end;
end;

procedure Tfrmempresa.FormActivate(Sender: TObject);
begin
   selecionaempresa;
end;

procedure Tfrmempresa.FormClose(Sender: TObject; var Action: TCloseAction);
begin
   Action := caHide;
end;

procedure Tfrmempresa.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f10 then
      spbretornar.click;
   if key = vk_f3 then
      gridempresas.OnDblClick(self);
end;

procedure Tfrmempresa.gridempresasDblClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      frmprincipal.Caption := '';
      verifica_parametro('');
      frmprincipal.codigo_empresa:= fdquerysql11.fieldbyname('empcod').AsString;
      frmprincipal.nome_empresa:=fdquerysql11.fieldbyname('empnome').asstring;
      empresajafoi:='JÁ';

      frmprincipal.Caption:=frmprincipal.Caption+'   '+frmprincipal.codigo_empresa+' - '+frmprincipal.nome_empresa;
      application.CreateForm(tfrmnovidadesversao, frmnovidadesversao);
      with frmnovidadesversao do
      begin
         if carrega_novidades(frmprincipal.versaoatual, frmlogon.codigousuario) = 'N' then
            begin
               frmnovidadesversao.rcenovidades.SelStart:=0;
               frmnovidadesversao.ShowModal;
            end;
      end;
      frmprincipal.Show;
   end;
end;

procedure Tfrmempresa.gridempresasKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_return then
      gridempresas.OnDblClick(self);
end;

procedure Tfrmempresa.spbretornarClick(Sender: TObject);
begin
   frmempresa.Close;
end;



end.
