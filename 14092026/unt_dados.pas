unit unt_dados;

interface

uses
	SysUtils, Classes, DB, Dialogs, Menus, Buttons, Windows,
	Messages, Controls, ExtCtrls, ComCtrls,	StdCtrls, Registry,
  Datasnap.DBClient, Datasnap.Provider,

  Data.FMTBcd,
  Data.SqlExpr, Data.DBXMySql, FireDAC.Stan.Intf, FireDAC.Stan.Option,
  FireDAC.Stan.Error, FireDAC.UI.Intf, FireDAC.Phys.Intf, FireDAC.Stan.Def,
  FireDAC.Stan.Pool, FireDAC.Stan.Async, FireDAC.Phys, FireDAC.Phys.MySQL,
  FireDAC.Phys.MySQLDef, FireDAC.VCLUI.Wait, FireDAC.Comp.UI,
  FireDAC.Comp.Client, FireDAC.Phys.MSSQL, FireDAC.Phys.MSSQLDef,
  FireDAC.Stan.Param, FireDAC.DatS, FireDAC.DApt.Intf, FireDAC.DApt,
  FireDAC.Comp.DataSet, FireDAC.Phys.SQLite, FireDAC.Phys.SQLiteDef,
  FireDAC.Stan.ExprFuncs, FireDAC.Phys.SQLiteWrapper.Stat;


type
	Tmodulo_dados = class(TDataModule)
    fdbanco: TFDConnection;
    fdquerysql: TFDQuery;
    dtsfdquerysql: TDataSource;
    dtsquerysve: TDataSource;
    dtsquerybanco: TDataSource;
    fdquerysql10: TFDQuery;
    dtsfdquerysql10: TDataSource;
    fdquerysql3: TFDQuery;
    dtsfdquerysql3: TDataSource;
    fdquerysql4: TFDQuery;
    dtsfdquerysql4: TDataSource;
    fdqueryentidade: TFDQuery;
    dtsfdqueryentidade: TDataSource;
    fdquerysql6: TFDQuery;
    dtsfdquerysql6: TDataSource;
    fdquerysql16: TFDQuery;
    dtsfdquerysql16: TDataSource;
    dtsfdquerysql14: TDataSource;
    fdquerysql14: TFDQuery;
    fdquerysql1: TFDQuery;
    dtsfdquerysql1: TDataSource;
    fdcomando: TFDCommand;
    dtsfdquerysql12: TDataSource;
    fdquerysql12: TFDQuery;
    fdquerysql7: TFDQuery;
    dtsfdquerysql7: TDataSource;
    fdquerysql22: TFDQuery;
    dtsfdquerysql22: TDataSource;
    dtsfdquerysql23: TDataSource;
    fdquerysql23: TFDQuery;
    dtsfdquerysql11: TDataSource;
    fdquerysql11: TFDQuery;
    dtsfdquerysql17: TDataSource;
    fdquerysql17: TFDQuery;
    fdquerysql18: TFDQuery;
    dtsfdquerysql18: TDataSource;
    fdquerysql8: TFDQuery;
    dtsfdquerysql8: TDataSource;
    fdquerysql2: TFDQuery;
    dtsfdquerysql2: TDataSource;

    fdquerysql19: TFDQuery;
    dtsfdquerysql19: TDataSource;
    fdquerysql20: TFDQuery;
    dtsfdquerysql20: TDataSource;
    fdquerysql15: TFDQuery;
    dtsfdquerysql15: TDataSource;
    fdquerysql9: TFDQuery;
    dtsfdquerysql9: TDataSource;
    fdquerysql13: TFDQuery;
    dtsfdquerysql13: TDataSource;
    dtsfdconsulta: TDataSource;
    fdquerysql5: TFDQuery;
    dtsfdquerysql5: TDataSource;
    fdbancosqlite: TFDConnection;
		procedure DataModuleCreate(Sender: TObject);
	private
		{ Private declarations }
	public
		{ Public declarations }
	end;

var
  modulo_dados: Tmodulo_dados;
  catalogo: string;

function conecta_banco(nome_banco: string): string;

implementation

uses funcoes, unt_principal;

{$R *.dfm}

procedure Tmodulo_dados.DataModuleCreate(Sender: TObject);
begin
   conecta_banco('FDALVO');
end;

function conecta_banco(nome_banco: string): string;
begin
  if not Assigned(modulo_dados) then Exit;
  if not Assigned(frmprincipal) then Exit;   // guarda obrigatória

  with modulo_dados, frmprincipal do
  begin
    if nome_banco = 'FDALVO' then
    begin
      if not Assigned(fdbanco) then Exit;
      fdbanco.Connected := False;
      fdbanco.Params.Clear;
      fdbanco.Params.Values['DriverID']  := 'MSSQL';
      fdbanco.Params.Values['Server']    := frmprincipal.nomeserversql;
      fdbanco.Params.Values['Database']  := frmprincipal.nomebancosql;
      fdbanco.Params.Values['User_Name'] := frmprincipal.usuariobancosql;
      fdbanco.Params.Values['Password']  := frmprincipal.senhasql;
      fdbanco.Params.Values['Encrypt']   := 'No';
      fdbanco.Params.Values['Protocol'] := 'TCPIP'; //frmprincipal.protocolo;
      fdbanco.Params.Values['Encrypt'] := 'True';
      fdbanco.LoginPrompt                := False;
      fdbanco.ResourceOptions.AutoReconnect  := True;
      fdbanco.ResourceOptions.SilentMode     := True;
      fdbanco.TxOptions.AutoCommit           := True;
      fdbanco.FetchOptions.Mode              := fmAll;
      fdbanco.FetchOptions.Items             := [];
      try
        fdbanco.Connected := True;         // dentro do bloco, fdbanco garantido
      except
        on E: Exception do
          MessageDlg('ERRO AO CONECTAR: ' + E.Message, mtError, [mbOK], 0);
      end;
    end;
  end;
end;

end.
