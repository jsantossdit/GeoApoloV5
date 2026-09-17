unit unt_novidadesversao;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.ComCtrls, Vcl.StdCtrls, Vcl.Buttons,
  Vcl.ExtCtrls;

type
  TfrmNovidadesVersao = class(TForm)
    Panel1: TPanel;
    spbretornar: TSpeedButton;
    lblmsg1: TLabel;
    StatusBar1: TStatusBar;
    rcenovidades: TRichEdit;
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure FormActivate(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure spbretornarClick(Sender: TObject);
    procedure WM_Sys(var Msg:TMessage); message WM_SysCommand;
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  frmNovidadesVersao: TfrmNovidadesVersao;

function carrega_novidades(versao: string; usucod : string) : string; export;

implementation

{$R *.dfm}

uses unt_versoes_types, unt_versoes_repository, unt_versoes_service, unt_principal, unt_dados, funcoes, unt_logon;

procedure TfrmNovidadesVersao.FormActivate(Sender: TObject);
begin
   frmprincipal.versaoatual:= getbuildinfo;
   frmnovidadesversao.Caption:= 'Novidades da Versão: '+getbuildinfo;
   statusbar1.Panels[1].text := configura_statusbar('a');
   statusbar1.Panels[3].text := configura_statusbar('a');
   statusbar1.Panels[5].text := frmprincipal.nomeserversql;
   carrega_novidades(frmprincipal.versaoatual,frmlogon.codigousuario);
end;

procedure TfrmNovidadesVersao.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
   action:=cafree;
end;

procedure TfrmNovidadesVersao.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f10 then
      spbretornar.Click;
end;

procedure TfrmNovidadesVersao.spbretornarClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      frmprincipal.versao:= getbuildinfo;
      sql:='SELECT * FROM user_geoapolo_userversao WHERE idversao = :idversao AND usucod = :usucod';
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := sql;
      fdquerysql.ParamByName('idversao').AsString := frmprincipal.versao;
      fdquerysql.ParamByName('usucod').AsString := frmlogon.codigousuario;
      if not executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
            sql:='INSERT INTO user_geoapolo_userversao (idversao, usucod ) VALUES (:versao, :codigousuario)';
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.parambyname('versao').AsString := frmprincipal.versao;
            fdquerysql3.ParamByName('codigousuario').AsString := frmlogon.codigousuario;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  frmnovidadesversao.Close;
               end;
         end
      else
         frmnovidadesversao.Close;
   end;
end;

function carrega_novidades(versao: string; usucod : string) : string;
begin
   with modulo_dados, frmprincipal,frmnovidadesversao do
   begin
      sql:='SELECT idversao FROM USER_geoapolo_userversao WHERE idversao = :idversao AND usucod = :usucod';
      fdquerysql4.Close;
      fdquerysql4.SQL.Clear;
      fdquerysql4.SQL.Text :=sql;
      fdquerysql4.ParamByName('idversao').AsString :=  frmprincipal.versaoatual  ;
      fdquerysql4.ParamByName('usucod').AsString := frmlogon.codigousuario;
      if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
         begin
            result:='S';
            spbretornar.Click;
         end
      else
         begin
            sql:='SELECT ugnv.textonovaversao FROM USER_geoapolo_novversao ugnv with(nolock) WHERE ugnv.idversao = :idversao';
            fdquerysql5.Close;
            fdquerysql5.SQL.Clear;
            fdquerysql5.SQL.Text := sql;
            fdquerysql5.ParamByName('idversao').AsString := frmprincipal.versaoatual;
            if executaracao(fdquerysql5, fdbanco, true, dtsfdquerysql5) then
               begin
                  result:='N';
                  rcenovidades.Lines.text := fdquerysql5.FieldByName('textonovaversao').AsString;
                  frmnovidadesversao.Refresh;
               end;
         end;
   end;
end;

procedure TfrmNovidadesVersao.WM_Sys(var Msg:TMessage);
begin
  if (Msg.WParam = SC_Close) and (Msg.LParam <> 0) then
  begin
    with frmNovidadesVersao do
    begin
       spbretornar.click;
    end;
  end
  else
    inherited;
end;

end.
