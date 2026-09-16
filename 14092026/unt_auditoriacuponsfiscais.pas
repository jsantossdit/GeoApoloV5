unit unt_auditoriacuponsfiscais;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.StdCtrls, Vcl.Buttons, Vcl.ExtCtrls,
  Vcl.ComCtrls, Vcl.Mask,  Winapi.ShellAPI;

type
  Tfrmauditoriacupons = class(TForm)
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spbligacoes: TSpeedButton;
    spbsair: TSpeedButton;
    spblimpar: TSpeedButton;
    lblsair: TLabel;
    spbexcluir: TSpeedButton;
    StatusBar1: TStatusBar;
    lblcaminhobase: TLabeledEdit;
    spbconectasqlite: TSpeedButton;
    OpenDialog: TOpenDialog;
    btnintegraalvo: TButton;
    btnintegrachavealvo: TButton;
    procedure spbconectasqliteClick(Sender: TObject);
    procedure spbsairClick(Sender: TObject);
    procedure btnintegraalvoClick(Sender: TObject);
    procedure btnintegrachavealvoClick(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  frmauditoriacupons: Tfrmauditoriacupons;

  function StrZero(Zeros:string;Quant:integer):String; export;
  function space(quantos: integer) : string; export;
  function BuscaTroca(Text,Busca,Troca : string) : string; export;
  function replicate(caracter : string; quantos:integer) : string; export;


implementation

{$R *.dfm}

uses unt_dados, funcoes;

procedure Tfrmauditoriacupons.btnintegraalvoClick(Sender: TObject);
var
   numerodocaixa,nomedoarquivo,linha,caminhodabase,sql,nfnum:string;
   i:integer;
   transmitiu,naotransmitiu,integrou,naointegrou,integroufinanceiro,naointegroufinanceiro,baixouestoque,naobaixouestoque:integer; // controle para resumo da auditoria
   vempcod, ventcod, ventnome,vserie,vnfnum,vsefaz,vintegra, vintegrafinanc,vintegrafiscal,vbxaestq,vnfvaltotnota:string;
   arquivo:textfile;
   ArquivoOrigem, ArquivoDestino: string;
   resp:word;
begin
   numerodocaixa:='01';
   assignfile(arquivo,'c:\SDIT\LogAuditoriaIntegracao.txt');
   rewrite(arquivo);

   transmitiu:=0; naotransmitiu:=0;
   integrou:=0; naointegrou:=0;
   integroufinanceiro:=0; naointegroufinanceiro:=0;
   baixouestoque:=0; naobaixouestoque:=0;

   writeln(arquivo,'-----------------------------------------------------------------------------------------');
   writeln(arquivo,'AUDITORIA INTEGRAÇÃO DE NFC-e COM O ALVO - CONGRESSO NACIONAL CENÁCULO 2026');
   writeln(arquivo,'-----------------------------------------------------------------------------------------');
   caminhodabase:= lblcaminhobase.text ;

   if not fileexists(caminhodabase) then
      begin
         numerodocaixa:=inttostr(strtoint(numerodocaixa)+1);
         numerodocaixa:=strzero(numerodocaixa,2);
         caminhodabase:=lblcaminhobase.Text ;
      end
   else
     begin
       {RODA CONSULTA NA BASE DO LOJA, PARA PEGAR TODAS AS CHAVES, DE POSSE DELAS VE NA BASE APOLO SE EXISTE, CASO
       NÃO EXISTA MUDA O FLAG}
       sql:='SELECT nf.empcod, nf.entcod, e.ENTNAT, substr(e.ENTNOME,1,45) as EntNome,nf.CtrlDFModForm, nf.ctrldfserie, nf.nfnum, nf.NFVALTOTNOTA,';
       sql:=sql+'       (CASE';
       sql:=sql+'	      WHEN (SELECT count(1) FROM NOTA_FISCAL_ELETRONICA_TRANS WHERE nfnum = nf.nfnum) > 0 THEN '+quotedstr('Transmitiu');
       sql:=sql+'	      WHEN (SELECT count(1) FROM NOTA_FISCAL_ELETRONICA_TRANS WHERE nfnum = nf.nfnum) <= 0 THEN '+quotedstr('Não Transmitiu');
       sql:=sql+'	      END) AS SEFAZ,';
       sql:=sql+' nf.NFINTEG, nf.NFINTEGFIN,nf.NFINTEGFISC, nf.NFBXAESTQ';
       sql:=sql+' FROM nota_fiscal nf';
       sql:=sql+' INNER JOIN entidade e ON nf.entcod = e.entcod';
       sql:=sql+' WHERE nf.nfdataemis between :datainicial AND :datafinal';
       //sql:=sql+' AND nf.nfinteg = '+quotedstr('Não');
       //sql:=sql+' AND nf.entcod <> '+quotedstr('5008320');
       //
       modulo_dados.fdquerysql.Connection:= modulo_dados.fdbancosqlite;
       modulo_dados.fdquerysql.Close;
       modulo_dados.fdquerysql.SQL.Clear;
       modulo_dados.fdquerysql.SQL.Text := sql;
       modulo_dados.fdquerysql.ParamByName('datainicial').AsString := '2026-07-24';
       modulo_dados.fdquerysql.ParamByName('datafinal').AsString := '2026-07-29';
       if executaracao(modulo_dados.fdquerysql,modulo_dados.fdbancosqlite,true,modulo_dados.dtsfdquerysql) then
          begin
             writeln(arquivo,replicate('-',160));
             writeln(arquivo,' CAIXA COM NÚMERO DE SÉRIE: '+modulo_dados.fdquerysql.FieldByName('ctrldfserie').asstring);
             writeln(arquivo,replicate('-',160));
             writeln(arquivo,'EmpCod'+space(2)+'ENTCOD '+space(3)+'ENTNOME'+space(52-length(modulo_dados.fdquerysql.fieldbyname('entnome').asstring)-1)+'SÉRIE'+space(3)+'NÚMERO NFC-e'+space(9)+'Status NFC-e'+space(14-length('Não Transmitiu')+2)+'Integrou'+space(4)+'Int.Fin'+space(2)+'Int.Fisc'+space(4)+'Baixou Estoq');
             while not modulo_dados.fdquerysql.Eof do
             begin
                  vempcod :=modulo_dados.fdquerysql.FieldByName('empcod').AsString ;
                  ventcod := modulo_dados.fdquerysql.fieldbyname('entcod').asstring;
                  ventnome:=modulo_dados.fdquerysql.fieldbyname('entnome').asstring+space(45-length(modulo_dados.fdquerysql.fieldbyname('entnome').asstring)-1);
                  vserie :=modulo_dados.fdquerysql.FieldByName('ctrldfserie').AsString;
                  vnfnum:= modulo_dados.fdquerysql.FieldByName('nfnum').AsString;
                  vsefaz := modulo_dados.fdquerysql.FieldByName('sefaz').AsString;
                  if vsefaz = 'Transmitiu' then
                     transmitiu:=transmitiu+1
                  else if vsefaz = 'Não Transmitiu' then
                     naotransmitiu:=naotransmitiu+1;
                  vintegra := modulo_dados.fdquerysql.FieldByName('NFINTEG').AsString;
                  if vintegra = 'Sim' then
                     integrou:=integrou+1
                  else
                     naointegrou := naointegrou+1;
                  vintegrafinanc := modulo_dados.fdquerysql.FieldByName('NFINTEGFIN').AsString;
                  vintegrafiscal := modulo_dados.fdquerysql.FieldByName('nfintegfisc').AsString;
                  vbxaestq := modulo_dados.fdquerysql.FieldByName('nfbxaestq').AsString;
                  vnfvaltotnota := modulo_dados.fdquerysql.FieldByName('nfvaltotnota').AsString;
                  writeln(arquivo,vempcod+space(4)+ventcod+space(3)+ventnome+vserie+space(3)+vnfnum+space(14)+vsefaz+space(14-length(vsefaz))+vintegra+space(10-length(vintegra))+vintegrafinanc+space(10-length(vintegrafinanc))+vintegrafiscal+space(10-length(vintegrafiscal))+modulo_dados.fdquerysql.FieldByName('nfbxaestq').asstring+space(3)+vnfvaltotnota);
                  ventnome:='';
                  modulo_dados.fdquerysql.Next;
             end;
              writeln(arquivo,replicate('-',160));
              writeln(arquivo,'');
              writeln(arquivo,'RESUMO DA AUDITORIA');
              writeln(arquivo,replicate('_',160));
              writeln(arquivo,'FORAM TRANSMITIDOS: '+inttostr(transmitiu)+' CUPONS');
              writeln(arquivo,'NÃO FORAM TRANSMITIDOS: '+inttostr(naotransmitiu)+' CUPONS');
              writeln(arquivo,'FORAM INTEGRADOS NO APOLO/ALVO: '+inttostr(integrou)+' CUPONS');
              writeln(arquivo,'NÃO FORAM INTEGRADOS NO APOLO/ALVO: '+inttostr(naointegrou)+' CUPONS');
              writeln(arquivo,'FORAM INTEGRADOS NO APOLO/ALVO: '+inttostr(integroufinanceiro)+' CUPONS');
              writeln(arquivo,'NÃO FORAM INTEGRADOS NO APOLO/ALVO: '+inttostr(naointegroufinanceiro)+' CUPONS');
              writeln(arquivo,'FORAM BAIXADOS NO ESTOQUE: '+inttostr(baixouestoque)+' CUPONS');
              writeln(arquivo,'NÃO FORAM BAIXADOS NO ESTOQUE: '+inttostr(naobaixouestoque)+' CUPONS');
              writeln(arquivo,'');
              writeln(arquivo,'---------------------------------------------------------------------------');
              writeln(arquivo,'');
              writeln(arquivo,'');
              writeln(arquivo,'');
              writeln(arquivo,'FINAL DA VERIFICAÇÃO');
              closefile(arquivo);
          end;
       ArquivoOrigem  := 'C:\SDIT\LogAuditoriaIntegracao.txt';
       ArquivoDestino := 'C:\SDIT\LogAuditoriaIntegracao'+'-'+modulo_dados.fdquerysql.fieldbyname('ctrldfserie').asstring+'.txt';
       if not RenameFile(ArquivoOrigem, ArquivoDestino) then
           RaiseLastOSError;
       resp:=messagedlg('AUDITORIA DE CHAVES DE ACESSO TERMINADA DESEJA ABRIR O ARQUIVO DE LOG? (y/n)',mtinformation,[mbyes,mbno],0);
       if resp = idyes then
          begin
             ShellExecute(0,'open','notepad.exe',PChar(ArquivoDestino),  nil,  SW_SHOWNORMAL);
          end;
       resp:=messagedlg('AUDITORIA DE CHAVES DE ACESSO TERMINADA DESEJA ABRIR O ARQUIVO DE LOG? (y/n)',mtinformation,[mbyes,mbno],0);
       if resp = idyes then
          begin
            ShellExecute(0,'open','notepad.exe',pchar(ArquivoDestino),  nil,  SW_SHOWNORMAL);
          end;
     end;
end;

procedure Tfrmauditoriacupons.btnintegrachavealvoClick(Sender: TObject);
var
   numerodocaixa,nomedoarquivo,linha,caminhodabase,sql,nfnum:string;
   i:integer;
   arquivo:textfile;
   ArquivoOrigem, ArquivoDestino: string;
   resp:word;
begin
   assignfile(arquivo,'c:\sdit\LogIntegracao-ChaveAcesso.txt');
   rewrite(arquivo);
   //
   {MONTA O CABEÇALHO DO ARQUIVO DE AUDITORIA }
   writeln(arquivo,'-----------------------------------------------------------------------------------------------------------------');
   writeln(arquivo,'AUDITORIA QUE VERIFICA SE A CHAVE DE ACESSO BASE LOJA ENCONTRA-SE NA BASE DO ALVO');
   writeln(arquivo,'-----------------------------------------------------------------------------------------------------------------');
   {RODA CONSULTA NA BASE DO LOJA, PARA PEGAR TODAS AS CHAVES, DE POSSE DELAS VE NA BASE APOLO SE EXISTE, CASO
   NÃO EXISTA MUDA O FLAG}
   sql:='SELECT ctrldfmodform, ctrldfserie, nfnum, nfetranschvacesso ';
   sql:=sql+' FROM nota_fiscal_eletronica_trans WHERE date(nfetransdataemis) between '+quotedstr('2026-07-24')+' and '+quotedstr('2026-07-29')  ;

   modulo_dados.fdquerysql.Connection:= modulo_dados.fdbancosqlite;
   modulo_dados.fdquerysql.Close;
   modulo_dados.fdquerysql.sql.clear;
   modulo_dados.fdquerysql.SQL.text := sql;
   if executaracao(modulo_dados.fdquerysql,modulo_dados.fdbancosqlite,false,modulo_dados.dtsfdquerysql) then
      begin
      end;
   //
   writeln(arquivo,'CAIXA COM NFC-e EMITIDAS NA SÉRIE: '+modulo_dados.fdquerysql.fieldbyname('ctrldfserie').asstring);
   writeln(arquivo,'-----------------------------------------------------------------------------------------------------------------');
   nfnum:='';
   modulo_dados.fdquerysql.First;
   while not modulo_dados.fdquerysql.Eof do
   begin
      {BUSCA NA BASE ALVO A CHAVE DE ACESSO}
      sql:='SELECT nfnum FROM nota_fiscal_eletronica_trans ';
      sql:=sql+' WHERE nfetranschvacesso = :nfchaveacesso';
      modulo_dados.fdquerysql.Connection:= modulo_dados.fdbancosqlite;
      modulo_dados.fdquerysql1.Close;
      modulo_dados.fdquerysql1.SQL.Clear;
      modulo_dados.fdquerysql1.SQL.Text := sql;
      modulo_dados.fdquerysql1.ParamByName('nfchaveacesso').AsString :=modulo_dados.fdquerysql.FieldByName('nfetranschvacesso').AsString;
      if executaracao(modulo_dados.fdquerysql1, modulo_dados.fdbancosqlite, true, modulo_dados.dtsfdquerysql1) then
         begin
         end;
      nfnum:=modulo_dados.fdquerysql1.FieldByName('nfnum').AsString;
      if nfnum = '' then
         begin
            writeln(arquivo,'ModForm: '+modulo_dados.fdquerysql1.FieldByName('ctrldfmodform').AsString+' - Série: '+modulo_dados.fdquerysql1.fieldbyname('ctrldfserie').asstring+' - Número Cupom: '+modulo_dados.fdquerysql1.fieldbyname('nfnum').asstring+' Operador: OP'+numerodocaixa+' CHAVE: '+modulo_dados.fdquerysql1.FieldByName('nfetranschvacesso').AsString);
            sql:='UPDATE nota_fiscal SET nfinteg = '+'Não'+', nfintegfin = '+'Não'+', nfbxaestq = '+'Não';
            sql:=sql+' WHERE ctrldfmodform = '+'NFC-e'+' AND ctrldfserie = '+modulo_dados.fdquerysql1.FieldByName('ctrldfserie').AsString+' AND nfnum = '+quotedstr(modulo_dados.fdquerysql1.fieldbyname('nfnum').AsString);
            modulo_dados.fdquerysql1.Active:=false;
            modulo_dados.fdquerysql1.SQL.Clear;
            modulo_dados.fdquerysql1.SQL.text := sql;
            try
               modulo_dados.fdquerysql1.ExecSQL;
            except
            on e:exception do
               begin
                  showmessage('ERRO AO ATUALIZAR O CUPOM FISCAL');
               end;
            end;
            writeln(arquivo,'A NFC-e '+nfnum+' NÃO ENCONTRA-SE NA BASE DO ALVO');
         end
      else
         writeln(arquivo,'A NFC-e '+nfnum+' ENCONTRA-SE NA BASE DO ALVO');
      modulo_dados.fdquerysql.next;
   end;
   closefile(arquivo);
   ArquivoOrigem  := 'C:\SDIT\LogIntegracao-ChaveAcesso.txt';
   ArquivoDestino := 'C:\SDIT\LogIntegracao-ChaveAcesso'+'-'+modulo_dados.fdquerysql.fieldbyname('ctrldfserie').asstring+'.txt';
   if not RenameFile(ArquivoOrigem, ArquivoDestino) then
       RaiseLastOSError;
   resp:=messagedlg('AUDITORIA DE CHAVES DE ACESSO TERMINADA DESEJA ABRIR O ARQUIVO DE LOG? (y/n)',mtinformation,[mbyes,mbno],0);
   if resp = idyes then
      begin
         ShellExecute(0,'open','notepad.exe',PChar(ArquivoDestino),  nil,  SW_SHOWNORMAL);
      end;
end;

procedure Tfrmauditoriacupons.spbconectasqliteClick(Sender: TObject);
begin
   if modulo_dados.fdbancosqlite.Connected  then
      begin
        modulo_dados.fdbancosqlite.Connected := false;
      end;
   OpenDialog.Title := 'Selecione o arquivo do banco SQLite';
   OpenDialog.Filter := 'Arquivos SQLite (*.db;*.sqlite)|*.db;*.sqlite|Todos os arquivos';
   OpenDialog.Options := [ofFileMustExist]; // Garante que o usuário não digite um nome de arquivo que não existe
   // O método Execute abre a tela e retorna True se o usuário clicou em "Abrir"
   if OpenDialog.Execute then
   begin
     // Supondo que seu componente de conexão se chame FDConnection1
     modulo_dados.fdbancosqlite.Connected := False; // Desconecta caso já estivesse conectado
     // Passa o caminho escolhido no diálogo para o parâmetro Database
     modulo_dados.fdbancosqlite.Params.Values['Database'] := OpenDialog.FileName;
      try
         try
           modulo_dados.fdbancosqlite.Params.Values['Password']:= '';
           modulo_dados.fdbancosqlite.Connected := True;
           lblcaminhobase.Text := opendialog.FileName;
            ShowMessage('Conectado com sucesso!');
          except
            on E: Exception do
               begin
                  ShowMessage('Erro ao conectar: ' + E.Message);
               end;
         end;
      finally
        //OpenDialog.Free; // Libera o componente da memória
      end;
   end;
end;

procedure Tfrmauditoriacupons.spbsairClick(Sender: TObject);
begin
   close;
end;

function StrZero(Zeros:string;Quant:integer):String;
{Insere Zeros à frente de uma string}
var
I,Tamanho:integer;
aux: string;
begin
  aux := zeros;
  Tamanho := length(ZEROS);
  ZEROS:='';
  for I:=1 to quant-tamanho do
  ZEROS:=ZEROS + '0';
  aux := zeros + aux;
  StrZero := aux;
end;

function replicate(caracter : string; quantos:integer) : string;
var
  i:integer;
  espaco:string;
begin
   espaco:='';
   for i := length(espaco) to quantos do
      begin
         espaco:=espaco+caracter;
      end;
   result:=espaco
end;

function space(quantos: integer) : string;
var
   i:integer;
   espaco:string;
begin
   espaco:=' ';
   for i := length(espaco) to quantos do
      begin
         espaco:=espaco+' ';
      end;
   result:=espaco
end;

function BuscaTroca(Text,Busca,Troca : string) : string;
var
   n : integer;
begin
  for n := 1 to length(Text) do
  begin
    if Copy(Text,n,1) = Busca then
      begin
        Delete(Text,n,1);
        Insert(Troca,Text,n);
      end;
  end;
  Result := Text;
end;

end.
