unit funcoes;

interface

uses
  Windows, Messages, System.SysUtils, System.Classes, Graphics, Controls, Forms, Dialogs,
  ExtCtrls, StdCtrls, Grids, DBGrids, Buttons, DBCtrls, ComCtrls, Registry, MAPI,
  shellapi, Printers,   Winsock,IdHTTP, System.JSON,System.DateUtils,
  idipwatch,idstackwindows, idtext,idsmtp, idmessage, idattachmentfile,IdIOHandler,
  IdSSLOpenSSL,IdICMPClient,wininet, IdSSL,System.MaskUtils,
  Data.FMTBcd,
  Data.SqlExpr, Data.DBXMySql, FireDAC.Stan.Intf, FireDAC.Stan.Option,
  FireDAC.Stan.Error, FireDAC.UI.Intf, FireDAC.Phys.Intf, FireDAC.Stan.Def,
  FireDAC.Stan.Pool, FireDAC.Stan.Async, FireDAC.Phys, FireDAC.Phys.MySQL,
  FireDAC.Phys.MySQLDef, FireDAC.VCLUI.Wait, FireDAC.Comp.UI,
  FireDAC.Comp.Client, FireDAC.Phys.MSSQL, FireDAC.Phys.MSSQLDef,
  FireDAC.Stan.Param, FireDAC.DatS, FireDAC.DApt.Intf, FireDAC.DApt,
  FireDAC.Comp.DataSet,System.RegularExpressions, Data.DB, System.IOUtils,
  IdExplicitTLSClientServerBase, System.Net.HttpClient,
  System.Net.HttpClientComponent,
  unt_document_validators, unt_viacep_service, unt_email_service;



procedure AjustaLarguraColunas(DBGrid: TDBGrid);
procedure EnviarEmailErroSQL(const Assunto, Corpo, AnexoLog: string);

const
  msg1 = 'Caractere(s) inválido(s) no início do e-mail.';
  msg2 = 'Símbolo @ não foi encontrado.';
  msg3 = 'Excesso do símbolo @.';
  msg4 = 'Caractere(s) inválido(s) antes do símbolo @.';
  msg5 = 'Caractere(s) inválido(s) depois do símbolo @.';
  msg6 = 'Agrupamento de caractere(s) inválido(s) a esqueda do @.';
  msg7 = 'Não existe ponto(s) digitado(s).';
  msg8 = 'Ponto encontrado no final do e-mail.';
  msg9 = 'Ausência de caractere(s) após o último ponto.';
  msg10 = 'Excesso de ponto(s) a direita do @.';
  msg11 = 'Ponto(s) disposto(s) de forma errada após o @.';
  msg12 = 'Caractere(s) inválido(s) antes do ponto.';
  msg13 = 'Caractere(s) inválido(s) depois do ponto.';


type
  TTipoSQL = (tsSelect, tsInsert, tsUpdate, tsDelete, tsExec, tsCreate, tsOther);

  TViaCEPResult = record
    Logradouro: string;
    Bairro: string;
    Cidade: string;
    UF: string;
  end;

type
  TParamSQL = record
    Nome: string;
    Valor: Variant;
    Tipo: TFieldType;  // ftString, ftInteger, ftDate, etc.
    class function Criar(const ANome: string; AValor: Variant;
      ATipo: TFieldType = ftString): TParamSQL; static;
  end;

  type
  TViaCEPInfo = record
    Logradouro: string;
    Complemento: string;
    Bairro: string;
    Cidade: string;
    Estado: string;
    IBGE: string;
    Gia: string;
  end;

// Configurações de e-mail (configure uma vez no início da aplicação)
var
  EmailDesenvolvedor: string = 'geosoftware@gmail.com';
  EmailRemetente: string = 'julio.santos@sdit.com.br';
  SMTPServer: string = 'smtp.office365.com';
  SMTPPorta: Integer = 587;
  SMTPUsuario: string = '';
  SMTPSenha: string = '';
  EnviarEmailErro: Boolean = False; // Desabilitado por padrao caso nao configurado


  //function gravalog(usuario: string; data: tdatetime; hora: tdatetime; acao: string) : string;
function envia_emailwf(empcod: string; dequem:string; emailde:string; paraquem: string; emailpara:string; data: string; assunto:string; corpomsg: string; formulario:tform) : string; export;
function space(quantos: integer) : string; export;
function replicate(caracter : string; quantos:integer) : string;
function GetBuildInfo:string; export;
function delay(tempo:word) : string; export;
function mudatela : string; export;
function AdicionaHora(TimeAdd: Integer) : String; export;
function StrIsDate(const S: string): boolean; export;
function StrIsTime(const S: string): boolean; export;
function StrIsFloat(const S: string): boolean; export;
function StrIsInteger(const S: string): boolean; export;
function senha(mcad: string ) : string;  export;
function DifDate(dataini,datafin:string):integer; export;
function IsEmptyMask(const Value: string): Boolean; export;
function TextToDate(const Value: string): TDate; export;
function ConsultarViaCEP(const ACEP: string; out Resultado: TViaCEPResult): Boolean; export;
function ValidaCombo(Combo: TComboBox; const NomeCampo: string): Boolean; export;
function BuscarCEP(const ACEP: string): TViaCEPInfo; export;
function ExecutarAcaon(
  const Query      : TFDQuery;
  const Conexao    : TFDConnection;
  const SQL        : string;               // ← nova: recebe a SQL direto
  const Params     : array of TParamSQL;   // ← nova: array de parâmetros
  UsarTransacao    : Boolean      = False;
  DataSource       : TDataSource  = nil
): Boolean; export;

//function executaracao( clausula : string; query : TADOQuery ) : string; overload; export; -- desativada em 08/06/2026
// Função principal para executar queries
function ExecutarAcao(const Query: TFDQuery;  const Conexao: TFDConnection;  UsarTransacao: Boolean = False;  DataSource: TDataSource = nil): Boolean; overload; export;
// Função para identificar tipo de comando SQL
function IdentificarTipoSQL(const SQL: string): TTipoSQL; export;
//
function ExecutaDDL(fdbanco: TFDConnection; const ASQL: string): Boolean; export;
//
function BuscarCEPporEndereco(const UF, Cidade, Logradouro: string): string; export;

// function sqlrun( clausula : string; query : TADOQuery; conexao : TADOconnection; formulario : tform ) : string; export; -- desativada em 08/06/2026
procedure imprime(Nlin,Ncol: Integer;Var LinhaAtual: Integer; Var Arquivo: Text;Texto: Variant); export;
procedure SetDefaultPrinter(PrinterName: String); export;
// function montagrid(form : tform; grid : TStringGrid; consulta: TADOQuery): string; overload; export; -- desativada em 08/06/2026
function montagrid(form : tform; grid : TStringGrid; consulta: TFDQuery): string; overload; export;
function limpagrid(grid : TStringGrid) : string; export;
function setcursorsql(tipo : string) : string; export;
function CreateControl(AClass: TControlClass; AParent: TWinControl; ATop,ALeft,AWidth, AHeight: Integer): TControl;
function pegacidade (Nome : String) : String; export;
function importerro(linha: string) : string; export;
function CalculaCnpjCpf(Numero : String) : String; export;
function ChecaEstado(Dado : string) : boolean; export;
function IsConnected : Boolean; export;
function pingIp(Host: String): Boolean; export;
function IsConnectedToInternet: Boolean; export;
procedure ExploreWeb(page:PChar); export;
function func_VerifEmail(email: string; cond: string): boolean;
function RoundFloat(Value: Extended; Digits: Integer): Extended; export;
function StrZero(Zeros:string;Quant:integer):String; export;
function Strbranco(origem:string;Quant:integer):String; export;
Function ValidCPF(const s:string): Boolean; export;
Function ValidCNPJ(const s:string): Boolean; export;
function tiracento ( str: String ): String; export;
function fRemoveFormatoCarEsp(Texto: string): string; export;
function SEMCHAR(texto: string): string;  export;//stdcall;
function FileVerInfo(const FileName: string;var FileInfo: TStringList): Boolean; export;
function StrToPChar(const Str: string): PChar; export;
procedure ExecutePrograma(Nome, Parametros: String); export;
function IfThen(condicao: Boolean; valorSeVerdadeiro, valorSeFalso: Variant): Variant; export;
function buscanacombo(oqbusca : string; formulario : tform; combo : TComboBox) : string; export;
function ParOuImpar(const Valor: string): Variant; export;
//function buscanomedaclasse(classerecdespcodestr : string) : string; export;
//function buscatipolanccod(tipolanccod:string) : string; export;
function BuscaDireita(Busca,Text : string) : integer; export;
function BuscaTroca(Text,Busca,Troca : string) : string; export;
//function buscanomecentrocontrole(cctrlcodestr:string) : string; export;
function carrega_config(modulo : string; formulario:tform; combocampo:TComboBox; comboordem:TComboBox; rdg1:TRadioButton; rdg2:TRadioButton) : string; export;
//
function grava_configuracoes_grids(Formulario: TForm; Modulo: string; Grid: TDBGrid; NomeGrid: string;  Usuario: string;  Consulta: TDataSource): string; export;
function ChecaCEP(cCep:String ; cEstado:String): Boolean; export;
function gravalog(usucod: string; data : string; atividade : string) : string; export;
function nomedomes(Mes:Word;Abrev:Boolean):String;
function DataExtenso(Data:TDateTime): String; export;
Function Alinhar(Pe_Num:Real; Pe_QtdPos:Byte; EDC :Char):string; export;
//function atualiza_usuarios_pgsql_apolo : string; export;
//function gravalogapolo(modulo: string; usucod : string; logsysdatahora : string; logsysnumdoc: string; logsysobs:string) : string; export;
function configura_statusbar(a :string) : string; export;
function criptografia(chave : integer; recebetexto : string) : string; export;
function decriptografia(chave :integer; senhacripto : string; senhaoriginal : string) : string; export;
function preenche_vetor:string ; export;
function GetLocalIP : string; export;
function LogUser : String; export;
function NomeComputador : String; export;
function UserName : String; export;
// function carrega_campo_dinamico(query : TADOQuery ) : string; overload; export; -- desativada em 08/06/2026
function carrega_campo_dinamico(query : TFDQuery ) : string; overload; export;
function geoapolo_configcod(empresa : string; tabela : string; atualiza:string) : string; export;
function cria_view(sqlrec : string; modulo : string; baseparacampanha: string; formulario:tform): string; export;
//function sincronizaemail_apolo_geoapolo : string; export;
//function sincronizar_chapamix_usuariogeoapolo : string; export;
//function sincroniza_cidades_apolo_to_geoapolo : string; export;
//function adiciona_atualiza_usuarios_como_contatos_na_agenda : string; export;
//function atualiza_insere_contato_do_contato(codigo_contato : string; pe_codigo:string) : string; export;
//function Padr(s:string;n:integer):string; export;
function configura_statusbarmix(a :string) : string; export;
//function MostraMemo(Dts: TDataSource; Dbg: TDBGrid; Fld: TField): Boolean; export;


function grava_config_telabusca(modulo : string; campobusca: string; campo_ordem: string; ordemcampo : string; formulario : tform) : string; export;
//function valida_permissoes(codigousuario : string; permissoes : string) : boolean; export;
procedure Memoformat(RichEdit: TRichEdit; TextCol, TagCol, DopCol: TColor); export;

function Bissexto(AYear: Integer): Boolean; export;
function Idade(Nasc : TDate) : String; export;
function Dias(Data : TDate) : String; export;
function DiasDoMes(AYear, AMonth: Integer): Integer; export;
function linkweb(const url : string) : string; export;
function MemoryStatus: string; export;
function DifHora(Inicio,Fim : String):String; export;
function limpahtml(RichEdit: TRichEdit; html:string) : string;
function RemoveTags(const s: string): string; export;
function FormEstaCriado(AClass: TClass): Boolean; overload; export;
//function integraapolo : string; export;
function EnviarEmail2(Dominio, Porta, Usuario, Senha, DeNome, DeEmail,Para, Assunto, Corpo: string; CorpoMIME, AnexoMIME: integer; AutoResposta: Boolean): Boolean; export;
function carrega_mail_config : string; export;
Function ValidaEMail(const EMailIn: string):Boolean; export;
//function retorna_nomeproduto(codigo_produto : string; formulario : TForm) : string; export;
//function retorna_gruposoftware(formulario : TForm) : string; export;
function ValidaCampo(Edit: TCustomEdit; const NomeCampo: string): Boolean; export;

function GetFileExt(FileName: string): String; export;
function verifica_parametro(nome_campo : string) : string; export;
//function alarme_pic : string; export;
//function carrega_dados(consulta: Tquerysql; formulario : tform) : string; export;
function Alltrim(Search: string): string; export;
function integracoes : string; export;
function WinExecAndWait32(FileName: string; Visibility: Integer): Longword; export;
function ExportToCsv(Grid : TStringGrid; const FileName:string) : string; export;
function CheckMaskEmptyText(const EditMask: TEditMask; const Text:String):Boolean;
function RemoverPecaDaString(const S: string; Inicio, Tamanho: Integer): string; export;
function ConvertISODate(isoDate: string): TDateTime; export;
function ContarVirgulas(const Texto: string): Integer; export;
function configura_grid(Modulo: string; Formulario: TForm; Usuario: string; NomeDoGrid: string; ObjetoGrid: TDBGrid; Consulta: TDataSource): string; export;

// Função auxiliar para registrar erros (com envio de e-mail)
procedure RegistrarErroSQL(const SQL, Mensagem: string;  const NomeComputador: string = '';  const IP: string = '';  const NomeUsuario: string = '');
//
var
  vet_valido: array [0..35] of string = ('0','1','2','3','4','5','6','7', '8','9','a','b','c','d','e','f', 'g','h','i','j','k','l','m','n', 'o','p','q','r','s','t','u','v', 'w','x','y','z');
  alpha:array[1..93] of string;
  volta,mensagem,cripto:array[1..109] of string;
  porta,usuario,sql:string;
  cida,sequencia,y,a,i,j,tam,chavet:integer;

implementation

uses unt_principal ,  unt_logon, unt_configsysv2, unt_dados, unt_consultav3;


class function TParamSQL.Criar(const ANome: string; AValor: Variant;
  ATipo: TFieldType): TParamSQL;
begin
  Result.Nome  := ANome;
  Result.Valor := AValor;
  Result.Tipo  := ATipo;
end;

function verifica_parametro(nome_campo : string) : string;
var
   sql:string;
begin
  with modulo_dados do
  begin
     sql:='SELECT * FROM  USER_geoapolo_configuracoes';
     fdquerysql4.Close;
     fdquerysql4.SQL.Clear;
     fdquerysql4.SQL.Text := sql;

     if not executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
        begin
          messagedlg('NÃO EXISTEM PARÂMETROS CONFIGURADOS !!!',mtwarning,[mbok],0);
          application.CreateForm(tfrmconfig, frmconfig);
          frmconfig.ShowModal;
        end;
  end;
end;

procedure ExploreWeb(page:PChar);
// Requer a ShellApi declarada na clausua uses da unit
var
   Returnvalue : integer;
begin
  ReturnValue := ShellExecute(0, 'open', page, nil, nil,SW_SHOWNORMAL);
  if ReturnValue <= 32 then
  begin
    case Returnvalue of
       0 : MessageBox(0,'Error: Out of memory','Error',0);
       ERROR_FILE_NOT_FOUND: MessageBox(0,'Error: File not found','Error',0);
       ERROR_PATH_NOT_FOUND: MessageBox(0,'Error: Directory not found','Error',0);
       ERROR_BAD_FORMAT : MessageBox(0,'Error: Wrong format in EXE','Error',0);
    else
       MessageBox(0,PChar('Error Nr: '+IntToStr(Returnvalue)+' inShellExecute'),'Error',0)
    end;
  end;
end;

function mudatela : string;
var
  DevMode : TDevMode;
begin
  EnumDisplaySettings(nil,104,Devmode);
  ChangeDisplaySettings(DevMode,0);
end;

function func_VerifEmail(email: string; cond: string): boolean;
var
  i, j, tam_email, simb_arroba, simb_arroba2, qtd_arroba, qtd_pontos,
  qtd_pontos_esq, qtd_pontos_dir, posicao, posicao2, ponto, ponto2: integer;
  vet_email: array [0..49] of string; //50 posições, capacidade do Edit
  msg: string;
begin
  {Por Jaci Jr em 12-10-2001 (00:28 às 03:57)
  Contatos por jrcordeiro@eletroacre.com.br ou
  jrcordeiro@bol.com.br
  Nesta função (func_VerifEmail) é utilizada a função Copy, exemplo:
  Copy(s,i,t) significa trecho de s que começa em i com tamanho t}
 
  qtd_pontos:= 0; qtd_pontos_esq:= 0; qtd_pontos_dir:= 0; qtd_arroba:= 0;
  posicao:=0; posicao2:=0; simb_arroba:=0; simb_arroba2:=0; ponto:= 0;
  ponto2:= 0; msg:='';
  Result:= True;

  //Verificando parte inicial do E-mail
  tam_email:= Length(email);
  for i:= 0 to tam_email-1 do
  begin
     vet_email[i]:= Copy(email,i+1,1);
     if vet_email[i] = '@' then
        begin
           Inc(qtd_arroba);
           posicao:= i;
        end;
  end;
  //
  if ((vet_email[0] = '@') or (vet_email[0] = '.') or (vet_email[0] = '-')) then
     begin
        Result:= False;
        msg:= msg1;
     end;
  //Verificando se tem o símbolo @ e quantos tem
  if qtd_arroba < 1 then
     begin
        Result:= False;
        msg:= msg2;
     end
  else if qtd_arroba > 1 then
     begin
        Result:= False;
        msg:= msg3 + ' Encontrado(s): '+IntToStr(qtd_arroba)+'.';
     end
  else
     //Verificando o que vem antes e depois do símbolo @
     begin
        for i:=0 to 35 do
           begin
              if vet_email[posicao-1] <> vet_valido[i] then
                 Inc(simb_arroba)
              else Dec(simb_arroba);
                 if vet_email[posicao+1] <> vet_valido[i] then
                    Inc(simb_arroba2)
              else Dec(simb_arroba2);
           end;
        if simb_arroba = 36 then
           begin
           //Antes do arroba há um símbolo desconhecido do vetor válido
           Result:= False;
           msg:= msg4;
           end
        else if simb_arroba2 = 36 then
           begin
              //Depois do arroba há um símbolo desconhecido do vetor válido
              Result:= False;
              msg:= msg5;
          end
     end;

  //Verificando se há pontos e quantos, e Verificando parte final do e-mail
  for j:=0 to tam_email-1 do
     if vet_email[j] = '-' then
     if ((vet_email[j-1] = '.') or (vet_email[j-1] = '-')) then
     begin
        Result:= False;
        msg:= msg6;
     end;
  for i:=0 to tam_email-1 do
     if vet_email[i] = '.' then
        begin
           Inc(qtd_pontos);
           posicao2:= i+1;
     if i > posicao then
        Inc(qtd_pontos_dir)
     else
        Inc(qtd_pontos_esq);
     if ((vet_email[i-1] = '.') or (vet_email[i-1] = '-')) then
        begin
           Result:= False;
           msg:= msg6;
        end;
     end;
  if qtd_pontos < 1 then
  begin
  Result:= False;
  msg:= msg7;
  end
  else if vet_email[tam_email-1] = '.' then
  begin
  Result:= False;
  msg:= msg8;
  end
  else if vet_email[tam_email-1] = '.' then
  begin
  Result:= False;
  msg:= msg9;
  end
  else if qtd_pontos_dir > 3 then
  begin
  Result:= False;
  msg:= msg10 + ' Encontrado(s): '+
  IntToStr(qtd_pontos)+#10+'Encontrado(s) a direita do @: '+
  IntToStr(qtd_pontos_dir)+'.';
  end
  else if (not ((((tam_email - posicao2) = 3) and (qtd_pontos_dir = 1)) or
  (((tam_email - posicao2) = 2) and (qtd_pontos_dir = 3)) or
  (((tam_email - posicao2) = 2) and (qtd_pontos_dir = 1)))) then
  begin
  Result:= False;
  msg:= msg11 +#10+ 'Encontrado(s) a esquerda do @: '+
  IntToStr(qtd_pontos_esq) +#10+ 'Encontrado(s) a direita do @: '+
  IntToStr(qtd_pontos_dir)+'.';
  end
  else
  //Verificando o que vem antes e depois do ponto
  begin
  for i:=0 to 35 do
  begin
  if vet_email[posicao2-2] <> vet_valido[i] then Inc(ponto)
  else Dec(ponto);
  if vet_email[posicao2] <> vet_valido[i] then Inc(ponto2)
  else Dec(ponto2);
  end;
  if ponto = 36 then
    begin
      //Antes do ponto há um símbolo desconhecido do vetor válido
      Result:= False;
      msg:= msg12;
    end
  else if ponto2 = 36 then
    begin
      //Depois do ponto há um símbolo desconhecido do vetor válido
      Result:= False;
      msg:= msg13;
    end
  end;
  //Verificação final
  if cond = '' then
  begin
     if not Result then
        begin
           msg:= msg +#10+ 'Formato de E-mail não aceitável!!';
           MessageDlg(msg,mtWarning,[mbRetry],0);
        end;
  end;
end;

function IsConnected : Boolean;
var
  reg : TRegistry;
  buff : dword;
begin
  reg:= tregistry.Create ;
  Reg.RootKey:=HKey_local_machine;
  if reg.OpenKey('SystemCurrentControlSetServicesRemoteAccess',false)  then
  begin
    reg.ReadBinaryData('Remote Connection',buff,sizeof(buff));
    result := buff = 1;
    reg.CloseKey ;
    reg.Free ;
  end;
end;

function pingIp(Host: String): Boolean;
var
  IdICMPClient: TIdICMPClient;
begin
  try
    IdICMPClient := TIdICMPClient.Create(Nil);
    IdICMPClient.Host := Host;
    IdICMPClient.ReceiveTimeout := 1000;
    IdICMPClient.Ping;
    showmessage(inttostr(IdICMPClient.ReplyStatus.BytesReceived));
    Result := (IdICMPClient.ReplyStatus.BytesReceived > 0);
  finally
    IdICMPClient.Free;
  end;
end;

function IsConnectedToInternet: Boolean;
var
  dwConnectionTypes: DWORD;
begin
  dwConnectionTypes :=
  INTERNET_CONNECTION_MODEM +
  INTERNET_CONNECTION_LAN +
  INTERNET_CONNECTION_PROXY;
  Result := InternetGetConnectedState(@dwConnectionTypes, 0);
end;

function pegacidade (Nome : String) : String;
var
   PNome : String;
begin
   PNome := '';
   if pos (' ', Nome) <> 0 then
      PNome := copy (Nome, 1, pos ('-', Nome) - 1);
      Result := PNome;
end;

function StrIsInteger(const S: string): boolean;
begin
  try
     StrToInt(S);
     Result := true;
  except
     Result := false;
  end;
end;

function StrIsFloat(const S: string): boolean;
begin
  try
     StrToFloat(S);
     Result := true;
  except
     Result := false;
  end;
end;

function senha(mcad: string ) : string;
var
   t1,t2,t3,t4,t5,t6,v1,v2,v3,v4,v5,v6 : integer;
begin
   v1:= ord(mcad[1]);
   v2:= ord(mcad[2]);
   v3:= ord(mcad[3]);
   v4:= ord(mcad[4]);
   v5:= ord(mcad[5]);
   v6:= ord(mcad[6]);
   //
   t1:=((v1*1 + v2*2 + v4*3 + v5*4 + v3*6 + v6) mod 223)+32;
   t2:=((v1*2 + v2*5 + v4*1 + v5*3 + v5*3 + v3*5 +v6) mod 223) +32;
   t3:=((v1*6 + v2*3 + v4*7 + v5*1 + v3*2 + v6) mod 223)+32;
   t4:=((v1*2 + v2*5 + v4*1 + v5*3 + v3*7 + v6) mod 223)+32;
   t5:=((v1*4 + v2*4 + v4*3 + v5*5 + v3*1 + v6) mod 223)+32;
   t6:=((v1*3 + v2*1 + v4*7 + v5*2 + v3*6 + v6) mod 223)+32;
   result:= chr(t5)+chr(t1)+chr(t6)+chr(t2)+chr(t4)+chr(t3);
end;

{function gravalog(usuario: string; data: tdatetime; hora: tdatetime; acao: string) : string;
var
   wcodmov:integer;
begin
   with modulo_dados do
   begin
      query_sql.Active := false; query_sql.sql.clear;
      query_sql.sql.Text := 'insert into tab_log (usuario,data,hora,descricao_acao) values (:p1,:p2,:p3,:p4)';
      query_sql.Params[0].asstring := usuario;
      query_sql.params[1].asdatetime := data;
      query_sql.params[2].asdatetime := hora;
      query_sql.params[3].asstring := acao;
      query_sql.Execute ;
      //
      if query_sql.RecordsAffected = 0 then
         begin
            showmessage('PROBLEMAS COM A TABELA DE LOG, CONTATE O PROGRAMADOR');
            application.Terminate ;
         end;
   end;
end;}

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

function GetBuildInfo:string;
var
   VerInfoSize: DWORD;
   VerInfo: Pointer;
   VerValueSize: DWORD;
   VerValue: PVSFixedFileInfo;
   Dummy: DWORD;
   V1, V2, V3, V4: Word;
   Prog : string;
begin
   Prog := Application.Exename;
   VerInfoSize := GetFileVersionInfoSize(PChar(prog), Dummy);
   GetMem(VerInfo, VerInfoSize);
   GetFileVersionInfo(PChar(prog), 0, VerInfoSize, VerInfo);
   VerQueryValue(VerInfo, '\', Pointer(VerValue), VerValueSize);
   with VerValue^ do
   begin
     V1 := dwFileVersionMS shr 16;
     V2 := dwFileVersionMS and $FFFF;
     V3 := dwFileVersionLS shr 16;
     V4 := dwFileVersionLS and $FFFF;
  end;
  FreeMem(VerInfo, VerInfoSize);
  result := Copy (IntToStr (100 + v1), 3, 2) + '.' +
  Copy (IntToStr (100 + v2), 3, 2) + '.' +
  Copy (IntToStr (100 + v3), 3, 2) + '.' +
  Copy (IntToStr (100 + v4), 2, 3);
end;

function delay(tempo:word): string;
var
   x1:double;
begin
   x1:=now;
   repeat until((now-x1)*86400) > tempo;
end;

function configura_statusbar(a :string) : string;
begin
   result:=modulo_dados.fdbanco.params.Database;
end;

function configura_statusbarmix(a :string) : string;
begin
 //  result:=frmprincipal.nomebancomix;
end;

function AdicionaHora(TimeAdd: Integer) : String;
{Adiciona à hora atual um numero de horas determinado. Caso este numero seje negativo, ele subtrairá da hora atual}
Var
   Horas,Min,SomaHoras,SomaMin : Integer;
   S, S1 : String;
begin
   Horas := Strtoint(Copy(TimetoStr(Time),1,2))+ TimeAdd;
   Min := Strtoint(Copy(TimetoStr(Time),4,2))+ TimeAdd ;
	SomaHoras := SomaHoras+Horas;
	SomaMin := SomaMin + Min;
	If SomaMin > 59 Then
      begin
         if SomaMin mod 60 = 0 Then
           begin
              Somahoras := Somahoras+(Somamin div 60);
  		        Somamin := 0;
           end
        else
           begin
  	           SomaHoras := SomaHoras + (SomaMin div 60);
              SomaMin := SomaMin mod 60;
           end;
      end;
   If Somamin = 0 Then
     begin
        S := '00';
     end
   else
      begin
         S := InttoStr(Somamin);
      end;
   //
   If Length(InttoStr(SomaHoras)) = 1 Then
      begin
         S1 := Concat('0',InttoStr(Somahoras));
      end
   else
      begin
         S1 := InttoStr(Somahoras);
      end;
   Result := Concat(S1,':',S,':00');
end;

function StrIsDate(const S: string): boolean;
begin
  try
     StrToDate(S);
     Result := true;
  except
     Result := false;
  end;
end;

function StrIsTime(const S: string): boolean;
begin
  try
     StrToTime(S);
     Result := true;
  except
     Result := false;
  end;
end;

function DifDate(dataini,datafin:string):integer;
var
   a,b,c:tdatetime;
   ct,s:integer;
begin
   if StrToDate(DataFin) < StrtoDate(DataIni) then
     begin
        Result := 0;
        exit;
     end;
   ct := 0;
   s := 1;
   a := strtodate(dataFin);
   b := strtodate(dataIni);
   if a > b then
     begin
        c := a;
        a := b;
        b := c;
        s := 1;
     end;
   a := a + 1;
   while (dayofweek(a)<>2) and (a <= b) do
     begin
        if dayofweek(a) in [2..6] then
           inc(ct);
        //
        a := a + 1;
     end;
   ct := ct + round((5*int((b-a)/7)));
   a := a + (7*int((b-a)/7));
   while a <= b do
     begin
        if dayofweek(a) in [2..6] then
           inc(ct);
        //
        a := a + 1;
     end;
   if ct < 0 then
        ct := 0;
   //
   result := s*ct;
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

function Strbranco(origem:string;Quant:integer):String;
{Insere espaços à frente de uma string}
var
   I,Tamanho:integer;
   aux: string;
begin
  aux := origem;
  Tamanho := length(origem);
  origem:='';
  for I:=1 to quant do
  origem:=origem + ' ';
  aux := origem + aux;
  Strbranco := aux;
end;

{function executaracao( clausula : string; query : TADOQuery ) : string;
var
   wpedaco,corpomensagem:string;
   formu:tform;
begin
   with modulo_dados do
   begin
      sql:='SET DATEFORMAT YMD';
      modulo_dados.comando.CommandText :=sql;
      modulo_dados.comando.Execute;
      wpedaco:= uppercase(copy(clausula,1,6));
      if (wpedaco = 'DECLAR') or (wpedaco = 'SELECT') then
         begin
            setcursorsql('sql');
            query.Connection := banco;
            query.active := false; query.sql.clear;
            query.sql.Text := clausula;
            try
               query.active:= true;
            except
            on E: exception do
               begin
                  showmessage(query.SQL.Text);
                  showmessage(e.message);
                  corpomensagem:='A MENSAGEM DE ERRO FOI '+e.message+' - '+clausula+' OCORREU NO MICRO '+nomecomputador+' - '+getlocalip+' - '+datetostr(date)+' - '+timetostr(time)+' O USUÁRIO LOGADO ERA '+chr(39)+''+chr(39);
{                  if EnviarEmail2(smtpserver,porta,'tecnologia@tvaparecida.com.br','12aparecida','GeoApolo','tecnologia@tvaparecida.com.br','geosoftware@gmail.com',
                                  'ERRO NA EXECUÇÃO DA CONSULTA SQL',corpomensagem,1,1,false) then
                     begin

                     end;
                  setcursorsql('');
                  exit;
               end;
            end;
            setcursorsql('');
            dtsquerysql.DataSet := query;
         end
      else if (wpedaco = 'INSERT') or (wpedaco = 'UPDATE') or (wpedaco = 'DELETE') or (wpedaco = 'EXECUT') or (wpedaco = 'CREATE') then
         begin
            setcursorsql('sql');
            query.active := false; query.sql.clear;
            query.sql.Text := clausula;
            try
               query.ExecSQL;
            except
            on E: exception do
               begin
                  showmessage(query.SQL.Text);
                  showmessage(e.message);
//                  corpomensagem:='A MENSAGEM DE ERRO FOI '+e.message+' - '+clausula+' OCORREU NO MICRO '+nomecomputador+' - '+getlocalip+' - '+datetostr(date)+' - '+timetostr(time)+' O USUÁRIO LOGADO ERA '+chr(39)+frmlogon.nomeusuario+chr(39) ;
                  if EnviarEmail2(smtpserver,porta,'tecnologia@tvaparecida.com.br','12aparecida','GeoApolo','tecnologia@tvaparecida.com.br','geosoftware@gmail.com',
                                  'ERRO NA EXECUÇÃO DA CONSULTA SQL',corpomensagem,1,1,false) then
                     begin

                     end;
                  setcursorsql('');
                  exit;
               end;
            end;
           setcursorsql('');
            //dtsquerysql.DataSet := query;
         end
      else
         begin
            setcursorsql('sql');
            query.Connection := banco;
            query.active := false; query.sql.clear;
            query.sql.Text := clausula;
            try
               query.active:= true;
            except
            on E: exception do
               begin
                  showmessage(query.SQL.Text);
                  showmessage(e.message);
                  corpomensagem:='A MENSAGEM DE ERRO FOI '+e.message+' - '+clausula+' OCORREU NO MICRO '+nomecomputador+' - '+getlocalip+' - '+datetostr(date)+' - '+timetostr(time)+' O USUÁRIO LOGADO ERA '+chr(39)+''+chr(39);
                  if EnviarEmail2(smtpserver,porta,'tecnologia@tvaparecida.com.br','12aparecida','GeoApolo','tecnologia@tvaparecida.com.br','geosoftware@gmail.com',
                                  'ERRO NA EXECUÇÃO DA CONSULTA SQL',corpomensagem,1,1,false) then
                     begin
                     end;
                  setcursorsql('');
                  exit;
               end;
            end;
            setcursorsql('');
            dtsquerysql.DataSet := query;
         end;
   end;
end;}

function IdentificarTipoSQL(const SQL: string): TTipoSQL;
var
  Comando: string;
begin
  Comando := UpperCase(Trim(Copy(SQL, 1, 6)));
  if (Comando = 'SELECT') or (Comando = 'DECLAR') then
    Result := tsSelect
  else if Comando = 'INSERT' then
    Result := tsInsert
  else if Comando = 'UPDATE' then
    Result := tsUpdate
  else if Comando = 'DELETE' then
    Result := tsDelete
  else if (Comando = 'EXECUT') or (Comando = 'EXEC  ') then
    Result := tsExec
  else if Comando = 'CREATE' then
    Result := tsCreate
  else
    Result := tsOther;
end;

function executaracao(const Query: TFDQuery;   const Conexao: TFDConnection; UsarTransacao: Boolean = False;   DataSource: TDataSource = nil): Boolean;
var
  TipoSQL: TTipoSQL;
  TransacaoIniciada: Boolean;
begin
  Result := False;
  TransacaoIniciada := False;
  // Validações
  if not Assigned(Query) then
  begin
    MessageDlg('Query não foi inicializada!', mtError, [mbOK], 0);
    Exit;
  end;
  if not Assigned(Conexao) then
  begin
    MessageDlg('Conexão não foi inicializada!', mtError, [mbOK], 0);
    Exit;
  end;
  if Trim(Query.SQL.Text) = '' then
  begin
    MessageDlg('Comando SQL vazio!', mtError, [mbOK], 0);
    Exit;
  end;
  try
    // Identifica tipo de comando
    TipoSQL := IdentificarTipoSQL(Query.SQL.Text);
    // Configura conexão se necessário
    if Query.Connection = nil then
      Query.Connection := Conexao;
    // Inicia transação se necessário
    if UsarTransacao and (TipoSQL in [tsInsert, tsUpdate, tsDelete, tsExec]) then
    begin
      if not Conexao.InTransaction then
      begin
        Conexao.StartTransaction;
        TransacaoIniciada := True;
      end;
    end;
//    query.ApplyUpdates(-1);
    try
      // Executa comando baseado no tipo
      case TipoSQL of
        tsSelect, tsOther:
          begin
            Query.Close;
            Query.Open;
            // Vincula ao DataSource se fornecido
            if Assigned(DataSource) then
              DataSource.DataSet := Query;
            // ⚠️ NOVO TRECHO: retorna False se não houver registros
            if Query.IsEmpty then
              Exit(False);
          end;
        tsInsert, tsUpdate, tsDelete, tsExec, tsCreate:
          begin
            Query.ExecSQL;
          end;
      end;
      // Commit se iniciou transação
      if TransacaoIniciada and Conexao.InTransaction then
        Conexao.Commit;
      Result := True;
    except
      on E: Exception do
      begin
        // Rollback se iniciou transação
        if TransacaoIniciada and Conexao.InTransaction then
          Conexao.Rollback;
        // Log do erro (com envio de e-mail automático)
        RegistrarErroSQL(Query.SQL.Text, E.Message);
        // Mostra erro ao usuário
        MessageDlg(
          'Erro ao executar comando SQL:' + sLineBreak + sLineBreak +
          E.Message + sLineBreak + sLineBreak +
          'O erro foi registrado e enviado ao desenvolvedor.',
          mtError, [mbOK], 0
        );
        Result := False;
      end;
       on E: EFDDBEngineException do
        begin
          modulo_dados.fdbanco.Connected := False;
          modulo_dados.fdbanco.Connected := True;
          query.Open;
        end;
    end;
  except
    on E: Exception do
    begin
      MessageDlg('Erro inesperado: ' + E.Message, mtError, [mbOK], 0);
      Result := False;
    end;
  end;
end;

procedure RegistrarErroSQL(const SQL, Mensagem: string;
  const NomeComputador: string = '';
  const IP: string = '';
  const NomeUsuario: string = '');
var
  ArquivoLog: string;
  Conteudo: TStringList;
  CorpoEmail: string;
begin
  try
    ArquivoLog := TPath.Combine(ExtractFilePath(ParamStr(0)), 'erros_sql.log');
    Conteudo := TStringList.Create;
    try
      // Carrega conteúdo existente se houver
      if FileExists(ArquivoLog) then
        Conteudo.LoadFromFile(ArquivoLog);
      // Adiciona novo erro
      Conteudo.Add('========================================');
      Conteudo.Add('Data/Hora: ' + DateTimeToStr(Now));
      if NomeComputador <> '' then
        Conteudo.Add('Computador: ' + NomeComputador);
      if IP <> '' then
        Conteudo.Add('IP: ' + IP);
      if NomeUsuario <> '' then
        Conteudo.Add('Usuário: ' + NomeUsuario);
      Conteudo.Add('Erro: ' + Mensagem);
      Conteudo.Add('SQL: ' + SQL);
      Conteudo.Add('========================================');
      Conteudo.Add('');
      // Salva arquivo
      Conteudo.SaveToFile(ArquivoLog);
      // Prepara corpo do e-mail
      CorpoEmail :=
        '<html><body>' +
        '<h2 style="color: #d9534f;">⚠️ ERRO NA EXECUÇÃO SQL - GeoApolo</h2>' +
        '<table style="border-collapse: collapse; width: 100%; font-family: Arial;">' +
        '<tr style="background-color: #f5f5f5;">' +
        '<td style="padding: 10px; border: 1px solid #ddd;"><strong>Data/Hora:</strong></td>' +
        '<td style="padding: 10px; border: 1px solid #ddd;">' + DateTimeToStr(Now) + '</td>' +
        '</tr>';
      if NomeComputador <> '' then
        CorpoEmail := CorpoEmail +
          '<tr>' +
          '<td style="padding: 10px; border: 1px solid #ddd;"><strong>Computador:</strong></td>' +
          '<td style="padding: 10px; border: 1px solid #ddd;">' + NomeComputador + '</td>' +
          '</tr>';
      if IP <> '' then
        CorpoEmail := CorpoEmail +
          '<tr style="background-color: #f5f5f5;">' +
          '<td style="padding: 10px; border: 1px solid #ddd;"><strong>IP:</strong></td>' +
          '<td style="padding: 10px; border: 1px solid #ddd;">' + IP + '</td>' +
          '</tr>';
      if NomeUsuario <> '' then
        CorpoEmail := CorpoEmail +
          '<tr>' +
          '<td style="padding: 10px; border: 1px solid #ddd;"><strong>Usuário:</strong></td>' +
          '<td style="padding: 10px; border: 1px solid #ddd;">' + NomeUsuario + '</td>' +
          '</tr>';
      CorpoEmail := CorpoEmail +
        '<tr style="background-color: #f5f5f5;">' +
        '<td style="padding: 10px; border: 1px solid #ddd;"><strong>Mensagem de Erro:</strong></td>' +
        '<td style="padding: 10px; border: 1px solid #ddd; color: #d9534f;">' + Mensagem + '</td>' +
        '</tr>' +
        '<tr>' +
        '<td style="padding: 10px; border: 1px solid #ddd;"><strong>Comando SQL:</strong></td>' +
        '<td style="padding: 10px; border: 1px solid #ddd;"><pre style="background-color: #f5f5f5; padding: 10px; overflow-x: auto;">' +
        SQL + '</pre></td>' +
        '</tr>' +
        '</table>' +
        '<br><p style="color: #777; font-size: 12px;">Este e-mail foi enviado automaticamente pelo sistema GeoApolo.</p>' +
        '</body></html>';
      // Envia e-mail se configurado
      if EnviarEmailErro and (SMTPServer <> '') and (EmailDesenvolvedor <> '') then
      begin
        TThread.CreateAnonymousThread(
          procedure
          begin
            EnviarEmailErroSQL('ERRO SQL - GeoApolo - ' + FormatDateTime('dd/mm/yyyy hh:nn:ss', Now), CorpoEmail, ArquivoLog);
          end
        ).Start;
      end;
    finally
      Conteudo.Free;
    end;
  except
    // Ignora erros no log para não quebrar a aplicação
  end;
end;

// Função interna para envio de e-mail
procedure EnviarEmailErroSQL(const Assunto, Corpo, AnexoLog: string);
var
  SMTP: TIdSMTP;
  Mensagem: TIdMessage;
  SSLHandler: TIdSSLIOHandlerSocketOpenSSL;
  TextoParte: TIdText;
begin
  SMTP := TIdSMTP.Create(nil);
  Mensagem := TIdMessage.Create(nil);
  try
    SSLHandler := TIdSSLIOHandlerSocketOpenSSL.Create(SMTP);

    SSLHandler.SSLOptions.Method := sslvTLSv1_2;
    SSLHandler.SSLOptions.Mode := sslmClient;

    SMTP.IOHandler := SSLHandler;
    SMTP.Host := SMTPServer;
    SMTP.Port := SMTPPorta;
    SMTP.Username := SMTPUsuario;
    SMTP.Password := SMTPSenha;
    SMTP.UseTLS := utUseExplicitTLS;

    Mensagem.From.Address := EmailRemetente;
    Mensagem.From.Name := 'Sistema GeoApolo';
    Mensagem.Recipients.EMailAddresses := EmailDesenvolvedor;
    Mensagem.Subject := Assunto;
    Mensagem.CharSet := 'UTF-8';

    TextoParte := TIdText.Create(Mensagem.MessageParts);
    TextoParte.Body.Text := Corpo;
    TextoParte.ContentType := 'text/html';

    if FileExists(AnexoLog) then
      TIdAttachmentFile.Create(Mensagem.MessageParts, AnexoLog);

    SMTP.Connect;
    try
      SMTP.Send(Mensagem);
    finally
      SMTP.Disconnect;
    end;
  except
    on E: Exception do
      gravalog(frmlogon.codigousuario, DateToStr(Date),
        'Falha ao enviar e-mail de erro SQL: ' + E.Message);
  end;

  Mensagem.Free;
  SMTP.Free;
end;

function sqlrun( clausula : string; query : TFDQuery; conexao : TFDconnection; formulario : tform ) : string;
var
   wpedaco,corpomensagem:string;
   formu:tform;
begin
   with modulo_dados do
   begin
      wpedaco:= uppercase(copy(clausula,1,6));
      if wpedaco = 'SELECT' then
         begin
            setcursorsql('sql');
            fdquerysql.Connection := conexao;
            fdquerysql.active := false; fdquerysql.sql.clear;
            fdquerysql.sql.Text := clausula;
            try
               fdquerysql.active:= true;
            except
            on E: exception do
               begin
                  showmessage(e.message);
                  corpomensagem:='A MENSAGEM DE ERRO FOI '+e.message+' OCORREU NO MICRO '+nomecomputador+' - '+getlocalip+' - '+datetostr(date)+' - '+timetostr(time)+' E O USUÁRIO LOGADO ERA: '+quotedstr(frmlogon.nomeusuario);
                  envia_emailwf(frmprincipal.codigo_empresa,'Sistema GeoApolo', 'rcc@sdit.com.br','Departamento de TI','julio.santos@sdit.com.br',datetostr(date),'ERRO NA EXECUÇÃO DA CONSULTA SQL',corpomensagem,formulario);
                  setcursorsql('');
                  exit;
               end;
            end;
            setcursorsql('');
            dtsfdquerysql.DataSet := fdquerysql;
         end
      else if (wpedaco = 'INSERT') or (wpedaco = 'UPDATE') or (wpedaco = 'DELETE') or (wpedaco = 'EXECUT') or (wpedaco = 'CREATE') then
         begin
            setcursorsql('sql');
            fdquerysql.active := false; fdquerysql.sql.clear;
            fdquerysql.sql.Text := clausula;
            try
               fdquerysql.ExecSQL;
            except
            on E: exception do
               begin
                  showmessage(e.message);
                  corpomensagem:='A MENSAGEM DE ERRO FOI '+e.message+' OCORREU NO MICRO '+nomecomputador+' - '+getlocalip+' - '+datetostr(date)+' - '+timetostr(time)+' E O USUÁRIO LOGADO ERA : '+chr(39)+frmlogon.nomeusuario+chr(39);
                  envia_emailwf(frmprincipal.codigo_empresa,'Sistema GeoApolo', 'rcc@sdit.com.br','Departamento de TI','julio.santos@sdit.com.br',datetostr(date),'ERRO NA EXECUÇÃO DA CONSULTA DE AÇÃO SQL',corpomensagem,formulario) ;
                  setcursorsql('');
                  exit;
               end;
            end;
            setcursorsql('');
            dtsfdquerysql.DataSet := fdquerysql;
         end;
   end;
end;

  // System.SysUtils, Vcl.Dialogs;
function ExecutaDDL(fdbanco: TFDConnection; const ASQL: string): Boolean;
var
  cmd: TFDCommand;
  tinhaMARS: Boolean;
begin
  Result := False;

  // Garante conexão ativa
  if not Assigned(fdbanco) then
    raise Exception.Create('Conexão FireDAC não informada.');

  if not fdbanco.Connected then
  begin
    try
      fdbanco.Connected := True;
    except
      on E: Exception do
      begin
        MessageDlg('Erro ao conectar no banco: ' + E.Message, mtError, [mbOK], 0);
        Exit(False);
      end;
    end;
  end;

  // Desativa temporariamente MARS (causa travamento em DDL às vezes)
  tinhaMARS := SameText(fdbanco.Params.Values['MARS'], 'Yes');
  if tinhaMARS then
    fdbanco.Params.Values['MARS'] := 'No';

  cmd := TFDCommand.Create(nil);
  try
    cmd.Connection := fdbanco;

    //  Configura execução direta
    cmd.CommandKind := skExecute;
    cmd.CommandText.Text := ASQL;
    cmd.ResourceOptions.CmdExecTimeout := 60; // tempo limite de 1 minuto
    cmd.ResourceOptions.DirectExecute := True;
    cmd.FetchOptions.Items := [];
    cmd.UpdateOptions.RequestLive := False;
    cmd.OptionsIntf := nil;
    cmd.Transaction := nil; // usa autocommit

    // 🔧 Garante autocommit
    fdbanco.TxOptions.AutoCommit := True;

    try
      cmd.Execute;
      Result := True;
    except
      on E: Exception do
      begin
        MessageDlg('Erro ao executar comando DDL:' + sLineBreak +
                   ASQL + sLineBreak + sLineBreak + E.Message, mtError, [mbOK], 0);
        Result := False;
      end;
    end;

  finally
    cmd.Free;

    // Restaura MARS caso estivesse ativado antes
    if tinhaMARS then
      fdbanco.Params.Values['MARS'] := 'Yes';
  end;
end;

function geoapolo_configcod(empresa : string; tabela : string; atualiza:string) : string;
var
   proximo_codigo,proximo_codigo_atualizado,sql:string;
begin
   with modulo_dados do
   begin
      sql:='SELECT (proximo_codigo+1) as proximo_codigo FROM USER_geoapolo_configcod WHERE empcod = :empcod';
      sql:=sql+' and geotabela = :tabela';
      fdquerysql6.close;
      fdquerysql6.sql.clear;
      fdquerysql6.sql.text :=sql;
      fdquerysql6.parambyname('empcod').asstring:=empresa;
      fdquerysql6.parambyname('tabela').asstring := tabela;
      if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
         begin
            if (not fdquerysql6.IsEmpty) and (fdquerysql6.fieldbyname('proximo_codigo').AsString <> '') then
               begin
                  proximo_codigo := fdquerysql6.fieldbyname('proximo_codigo').asstring;
                  if atualiza = 'Sim' then
                     begin
                        // CHECANDO SE TEM O NÚMERO JA CADASTRADO NA TABELA DE DESTINO
                        // atualizando próximo número
                        sql:='UPDATE USER_geoapolo_configcod SET proximo_codigo = :proximocodigo ';
                        sql:=sql+' WHERE geotabela = :tabela and empcod = :empcod';
                        fdquerysql3.close;
                        fdquerysql3.sql.clear;
                        fdquerysql3.sql.text := sql;
                        fdquerysql3.parambyname('proximocodigo').asstring:= proximo_codigo;
                        fdquerysql3.parambyname('empcod').asstring:= empresa;
                        fdquerysql3.parambyname('tabela').asstring := tabela;
                        if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                           begin
                              sql:='SELECT proximo_codigo FROM USER_geoapolo_configcod ';
                              sql:= sql+' WHERE empcod = :empresa and geotabela = :tabela';
                              fdquerysql6.close;
                              fdquerysql6.sql.clear;
                              fdquerysql6.sql.text := sql;
                              fdquerysql6.parambyname('empresa').asstring := empresa;
                              fdquerysql6.parambyname('tabela').asstring := tabela;
                              if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
                                 proximo_codigo := fdquerysql6.fieldbyname('proximo_codigo').asstring;
                           end
                        else
                           begin
                              messagedlg('ERRO AO ATUALIZAR CÓDIGO',mterror,[mbok],0);
                              exit;
                           end;
                     end;
               end
         end
      else
         begin
           //modificar aqui em 02/09/2016 - verificar se a geotabela nao existir, fará um select na tabela
           //para verificar o campo qual é o max a gerar ai pega o código e soma 1 para retornar o numero
           //novo
            sql:='SELECT * FROM USER_geoapolo_configcod  WHERE geotabela = :tabela';
            fdquerysql.close;
            fdquerysql.sql.clear;
            fdquerysql.sql.text := sql ;
            fdquerysql.parambyname('tabela').asstring :=  tabela;
            if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
               begin
                   if fdquerysql.IsEmpty then
                      begin
                        sql:='SELECT    ';
                      end;
               end;


           { if tabela = 'USER_geoapolo_usuarios' then
               begin
                  sql:='INSERT INTO USER_geoapolo_configcod (empcod,GEOTABELA, TABELA_ATIVA, proximo_codigo, ultimo_numero_utilizado ) ';
                  sql:=sql+' VALUES ('+'1.01'+', '+quotedstr(tabela)+', '+quotedstr('S')+', '+'1'+', '+'0'+');';
               end
            else
               begin }
                  sql:='INSERT INTO USER_geoapolo_configcod (empcod, GEOTABELA, TABELA_ATIVA, proximo_codigo, ultimo_numero_utilizado ) ';
                  sql:=sql+' VALUES (:empresa, :tabela, :tabelaativa, :proximocodigo, :ultimonumeroutilizado)';
                  //sql:=sql+' VALUES ('+empresa+', '+quotedstr(tabela)+', '+quotedstr('S')+', '+'1'+', '+'0'+');';
               //end;
            fdquerysql3.close;
            fdquerysql3.sql.clear;
            fdquerysql3.sql.text := sql;
            fdquerysql3.parambyname('empresa').asstring := empresa;
            fdquerysql3.parambyname('tabela').asstring := tabela;
            fdquerysql3.parambyname('tabelaativa').asstring := 'S';
            fdquerysql3.parambyname('proximocodigo').asstring := '1';
            fdquerysql3.parambyname('ultimonumeroutilizado').asstring := '0';
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  proximo_codigo:='1';
               end
            else
               begin
                  proximo_codigo_atualizado:=inttostr(strtoint(proximo_codigo)+1);
                  sql:='UPDATE USER_geoapolo_configcod SET proximo_codigo = :proximocodigoatualizado where geotabela = :tabela and empcod = :empcod ';
                  fdquerysql3.close;
                  fdquerysql3.sql.clear;
                  fdquerysql3.sql.text := sql;
                  fdquerysql3.parambyname('proximocodigoatualizado').asstring := '1';
                  fdquerysql3.parambyname('tabela').asstring := tabela;
                  fdquerysql3.parambyname('empcod').asstring := empresa;
                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                     begin
                     end;
               end;
         end;
      if proximo_codigo <> '' then
         result:= proximo_codigo;
   end;
end;
{
function atualiza_usuarios_pgsql_apolo : string;
var
   sql:string;
begin
   with modulo_dados do
   begin
      sql:='SELECT * FROM pgsql_usuarios';
      executaracao(sql,querysql);
      if querysql.RecordCount = 0 then
         begin
            //se a tabela pgsql_usuarios estiver vazia o sistema irá inserir todos os usuários ativos do
            postgresql dentro desta tabela no MSSQL Server
            sql:='select * from usuarios where flagativo = '+quotedstr('A');
            sql:=sql+' AND senha <> '+quotedstr('')+' order by nome asc';
            executaracao(sql,querysqlsql);
            if querysqlsql.RecordCount > 0 then
               begin
                  querysqlsql.First;
                  while not querysqlsql.Eof do
                  begin
                     sql:='INSERT INTO pgsql_usuarios (codigo_usuario, nome, flagativo) ';
                     sql:=sql+' VALUES ('+querysqlsql.fieldbyname('codigo_usuario').asstring+', ';
                     sql:=sql+quotedstr(querysqlsql.fieldbyname('nome').asstring)+', '+quotedstr(querysqlsql.fieldbyname('flagativo').asstring)+');';
                     executaracao(sql,querysql3);
                     if querysql3.RowsAffected > 0 then
                        querysqlsql.Next;
                  end;
               end
         end
      else if querysql.RecordCount > 0 then
         begin
             se já tiver registros na tabela ele irá dar update em todas verificando se já existe, caso não exista irá inserir
             sql:='select * from usuarios where flagativo = '+quotedstr('A');
             sql:=sql+' AND senha <> '+quotedstr('')+' order by nome asc';
             executaracao(sql,querysqlsql);
             if querysqlsql.RecordCount > 0 then
                begin
                   querysqlsql.First;
                   while not querysqlsql.eof do
                   begin
                      sql:='SELECT codigo_usuario FROM pgsql_usuarios WHERE codigo_usuario = '+querysqlsql.fieldbyname('codigo_usuario').asstring+';';
                      executaracao(sql,querysql);
                      if querysql.RecordCount > 0 then
                         begin
                            sql:='UPDATE pgsql_usuarios SET nome = '+chr(39)+querysqlsql.fieldbyname('nome').asstring+chr(39)+', flagativo = '+chr(39)+querysqlsql.fieldbyname('flagativo').asstring+chr(39)+' WHERE codigo_usuario = '+querysqlsql.fieldbyname('codigo_usuario').asstring+';';
                            executaracao(sql,querysql3);
                            if querysql3.RowsAffected > 0 then
                               querysqlsql.Next;
                         end
                      else
                         begin
                            sql:='INSERT INTO pgsql_usuarios (codigo_usuario, nome, flagativo) VALUES ('+querysqlsql.fieldbyname('codigo_usuario').asstring+', '+chr(39)+querysqlsql.fieldbyname('nome').asstring+chr(39)+', '+chr(39)+querysqlsql.fieldbyname('flagativo').asstring+chr(39)+');';
                            executaracao(sql,querysql3);
                            if querysql3.RowsAffected > 0 then
                               querysqlsql.Next;
                         end;
                   end;
                end;
         end;
   end;
end;   }

function buscanacombo(oqbusca : string; formulario : tform; combo : TComboBox) : string;
var
   i:integer;
begin
   for i := 0 to combo.Items.Count -1 do
      begin
         if combo.Items.Strings[i] = oqbusca then
            begin
               combo.ItemIndex := i;
               break;
            end
      end;
end;

function importerro(linha: string) : string;
var
   errorlog : textfile;
   caminho:string;
begin
   try
      //CRIA OU ABRE O ARQUIVO DE ERROS DE IMPORTAÇÃO
      caminho:='c:\Import.err';
      AssignFile(errorlog, caminho);
      if not FileExists(caminho) then
         Rewrite(errorlog);
      //
      Append(errorlog);
      WriteLn(errorlog, linha);
   finally
      closefile(errorlog);
   end;
end;

{function carrega_campo_dinamico(query : TADOQuery ) : string; overload;
var
   i:integer;
begin
   with modulo_dados, frmconsulta3 do
   begin
     for i:= 0 to query.FieldCount -1 do
     begin
        cbocampo.items.add(query.Fields[i].DisplayName);
        cbordem.items.add(query.Fields[i].DisplayName);
     end;
     frmconsulta3.Refresh;
   end;
end;}

function carrega_campo_dinamico(query : TFDQuery ) : string; overload;
var
   i:integer;
begin
   with modulo_dados, frmconsulta3 do
   begin
     for i:= 0 to query.FieldCount -1 do
     begin
        cbocampo.items.add(query.Fields[i].DisplayName);
        cbordem.items.add(query.Fields[i].DisplayName);
     end;
     frmconsulta3.Refresh;
   end;
end;

{function executaracao( clausula : string) : string;overload;
var
   wpedaco:string;
begin
   with modulo_dados do
   begin
      wpedaco:= uppercase(copy(clausula,1,6));
      if wpedaco = 'SELECT' then
         begin
            setcursorsql('sql');
            querysql2.active := false; querysql2.sql.clear;
            querysql2.sql.Text := clausula;
            try
               querysql2.active:= true;
            except
            on E: exception do
               begin
                  showmessage(e.message);
               end;
            end;
            setcursorsql('');
            dts_querysql2.DataSet := querysql2;
         end
      else if (wpedaco = 'INSERT') or (wpedaco = 'UPDATE') or (wpedaco = 'DELETE') then
         begin
            setcursorsql('sql');
            querysql2.active := false; querysql2.sql.clear;
            querysql2.sql.Text := clausula;
            try
               querysql2.ExecSQL ;
            except
            on E: exception do
               begin
                  showmessage(e.message);
               end;
            end;
            setcursorsql('');
            dts_querysql2.DataSet := querysql2;
         end;
   end;
end;}

{Procedure TablePack( oTable : TTable );
var
   iResult: DBIResult;
   szErrMsg: DBIMSG;
   pTblDesc: pCRTblDesc;
   bExclusive: Boolean;
   bActive: Boolean;
begin
   with oTable do
   begin
      bExclusive := Exclusive;
      bActive := Active;
      DisableControls;
      Close;
      Exclusive := True;
   end;
   case oTable.TableType of
   ttdBASE: begin
      oTable.Open;
      iResult := DbiPackTable( oTable.DBHandle, oTable.Handle, nil,nil, True );
      if iResult <> DBIERR_NONE then
         begin
            DbiGetErrorString( iResult, szErrMsg );
            MessageDlg( szErrMsg, mtError, [mbOk], 0 );
         end;
      end;
   ttParadox: begin
   GetMem( pTblDesc, SizeOf( CRTblDesc ));
   FillChar( pTblDesc^, SizeOf( CRTblDesc ), 0 );
   with pTblDesc^ do
   begin
      StrPCopy( szTblName, oTable.TableName );
      StrPCopy( szTblType, szParadox );
      bPack := True;
   end;
   iResult := DbiDoRestructure( oTable.DBHandle, 1, pTblDesc,nil, nil, nil, False );
   if iResult <> DBIERR_NONE then
      begin
         DbiGetErrorString( iResult, szErrMsg );
         ShowMessage( szErrMsg, mtError, [mbOk], 0 );
      end;
      FreeMem( pTblDesc, SizeOf( CRTblDesc ));
      end;
   else
      ShowMessage( 'Impossível compactar uma tabela deste tipoe!');
    end;
      with oTable do
      begin
      Close;
      Exclusive := bExclusive;
      Active := bActive;
      EnableControls;
   end;
end;}

{function montagrid(form : tform; grid : TStringGrid; consulta: TADOQuery): string;
var
   i,r,c:integer;
begin
   // monta coluna do string grid
   for i := 0 to consulta.FieldCount -1 do
   begin
      grid.ColCount :=i+1;
      grid.cols[i].Add(consulta.Fields[i].DisplayName);
  end;
   // monta os dados das colunas
   c:=0; r:=0;
   for r := 1 to consulta.RecordCount  do
   begin
      grid.RowCount :=(consulta.RecordCount) +1;
      for c := 0 to (consulta.FieldCount-1) do
      begin
           grid.Cells[C,R] := consulta.Fields[c].Value;
         //grid.ColWidths[c]:=consulta.Fields[i].Size
      end;
      consulta.Next;
      c:=0;
   end;
end;}

function montagrid(form : tform; grid : TStringGrid; consulta: TFDQuery): string; overload;
var
   i,r,c,coltam1,coltam2:integer;
begin
    // monta coluna do string grid
    for i := 0 to consulta.FieldCount -1 do
    begin
       grid.ColCount :=i+1;
       grid.cols[i].Add(consulta.Fields[i].DisplayName);
   end;
   // monta os dados das colunas
   c:=0; r:=0; coltam1:=0; coltam2:=0;
   for r := 1 to consulta.RecordCount  do
   begin
      for c := 0 to (consulta.FieldCount-1) do
      begin
         try
           grid.Cells[C,R] := consulta.Fields[c].Value;
           //grid.ColWidths[c]:=consulta.fields[c].Size;
         except
         on e:exception do
            begin
               showmessage(e.Message);
               showmessage(grid.Cells[c,r]);
            end
         end;
      end;
      grid.RowCount :=(consulta.RecordCount) +1;
      consulta.Next;
      c:=0;
   end;
   i:=0;
   consulta.close;
end;

function limpagrid(grid : TStringGrid) : string;
var
   c,r:integer;
begin
   for r:= 1 to grid.RowCount -1 do
   begin
      for c:= 0 to grid.ColCount -1 do
      begin
         grid.Cells[c,r]:='';
      end;
   end;
end;

function setcursorsql(tipo : string) : string;
begin
   if tipo = '' then
      screen.Cursor := crdefault
   else if tipo = 'sql' then
      screen.Cursor := crsqlwait
   else if tipo = 'drag' then
      screen.Cursor := crdrag;
end;

function CreateControl(AClass: TControlClass; AParent: TWinControl; ATop,ALeft,AWidth, AHeight: Integer): TControl;
begin
    Result := AClass.Create(nil);
    Result.Parent := AParent;
    Result.BoundsRect := Rect(ALeft, ATop, ALeft + AWidth, ATop + AHeight);
end;

function CalculaCnpjCpf(Numero : String) : String;
var
  i,j,k, Soma, Digito : Integer;
  CNPJ : Boolean;
begin
  Result := Numero;
  case Length(Numero) of
    9:
    CNPJ := False;
    12:
    CNPJ := True;
  else
     Exit;
  end;
  for j := 1 to 2 do
    begin
      k := 2;
      Soma := 0;
      for i := Length(Result) downto 1 do
        begin
          Soma := Soma + (Ord(Result[i])-Ord('0'))*k;
          Inc(k);
          if (k > 9) and CNPJ then
             k := 2;
    end;
  Digito := 11 - Soma mod 11;
  if Digito >= 10 then
    Digito := 0;
    Result := Result + Chr(Digito + Ord('0'));
  end;
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

function ChecaEstado(Dado : string) : boolean;
const
   Estados = 'SPMGRJRSSCPRESDFMTMSGOTOBASEALPBPEMARNCEPIPAAMAPFNACRRRO';
var
   Posicao : integer;
begin
  Result := true;
  if Dado <> '' then
    begin
      Posicao := Pos(UpperCase(Dado),Estados);
      if (Posicao = 0) or ((Posicao mod 2) = 0) then
        begin
           Result := false;
        end;
    end;
end;

// funcoes baixadas mas sem uso ainda
function PrimeiroNome (Nome : String) : String;
var
  PNome : String;
begin
   PNome := '';
   if pos (' ', Nome) <> 0 then
      PNome := copy (Nome, 1, pos (' ', Nome) - 1);
   Result := PNome;
end;

function BuscaDireita(Busca,Text : string) : integer;
{Pesquisa um caractere à direita da string,
 retornando sua posição}
var
   n,retorno : integer;
begin
   retorno := 0;
   for n := length(Text) downto 1 do
     begin
        if Copy(Text,n,1) = Busca then
           begin
              retorno := n;
              break;
           end;
     end;
   Result := retorno;
end;

//  4- Verifica Digito de Cheque. Enviada por Celso cdelphi@terra.com.br
function VerificaDigitoCheque(NumCheque, NumDigito : String): boolean;
var
 i, soma, digito : integer;
begin
   result := false;
   // Remove os espaços em branco
   NumCheque := TrimLeft(TrimRight(NumCheque));
   // Valido os parametros de entrada
   if (NumCheque = '') or (NumDigito = '') then
      exit;
   // Preencho com zeros a esquerda
   while length(NumCheque) < 6 do
       NumCheque := '0' + NumCheque;
   // Calculo módulo 11 com peso 7
   soma := 0;
   for i := 0 to 5 do
      soma := soma + ( StrToInt( NumCheque[i+1] ) * (7 - i) );
    digito := 11 - ( soma mod 11 );
   // Se digito > 9, digito deve ser 0
   if ( digito > 9 ) then
      digito := 0;
   // Retorno a comparação entre os digitos
   result := IntToStr(Digito) = NumDigito;
end;

//4- Edit estilo XP. Enviada por Bisa
{procedure EditXP;
var
 DC: HDC;
 R: TRect;
 T: TCanvas;
 BtnFaceColor: HBrush;
begin
 T:= TCanvas.Create;
 DC:= GetWindowDC(Edit1.Handle);
T.Handle:= DC;
 try
   GetWindowRect(Edit1.handle, R);
   OffSetRect(R, -R.Left, -R.Top);
   if Edit1.Focused then
   begin
     Frame3D(T, R, clSilver, clSilver, 1);
     Frame3D(T, R, $00856658, $00856658, 1);
   end
   else
   begin
     BtnFaceColor:= GetSysColorBrush(COLOR_BTNSHADOW);
     FrameRect(DC, R, BtnFaceColor);
     InflateRect(R, -1, -1);
     FrameRect(DC, R, BtnFaceColor);
     InflateRect(R, 1, 1);
   end;
 finally
   ReleaseDC(Edit1.Handle, DC);
   T.Handle:=0;
 end;
end;}

{Função Simples e Prática para Arredondar Valores.}
{  onde:

  Value = Valor a ser arredondado
  Digits = Nº de casas decimais}
function RoundFloat(Value: Extended; Digits: Integer): Extended;
var
   StrFmt: string;
begin
   StrFmt := '%.' + IntToStr(Digits) + 'f';
   Result := StrToFloat(Format(StrFmt, [Value]));
end;

function envia_emailwf(empcod: string; dequem:string; emailde:string; paraquem: string; emailpara:string; data: string; assunto:string; corpomsg: string; formulario:tform) : string;
begin
   with modulo_dados, formulario do
   begin
{      setcursorsql('sql');
      sql:='EXEC USERInsereWorkflowemail '+quotedstr(empcod)+', '+quotedstr(dequem)+', '+quotedstr(dequem)+', '+quotedstr(paraquem)+', '+quotedstr(emailpara)+', '+quotedstr(data)+', '+quotedstr(assunto)+', '+quotedstr(corpomsg)+', '+'HTML';
      executaracao(sql,querysql3);
      if querysql3.RowsAffected > 0 then
         begin
         end
      else
          showmessage(sql);
      setcursorsql('');
      //}
   end;
end;


{Validação de número de CPF}
Function ValidCPF(const s:string): Boolean;
begin
   Result := TDocumentValidators.ValidarCPF(s);
end;

{Validação de número de CGC}
Function ValidCNPJ(const s:string): Boolean;
begin
   Result := TDocumentValidators.ValidarCNPJ(s);
end;

function tiracento ( str: String ): String;
var
   i: Integer;
begin
   for i := 1 to Length ( str ) do
      case str[i] of
      'á': str[i] := 'a';
      'é': str[i] := 'e';
      'í': str[i] := 'i';
      'ó': str[i] := 'o';
      'ú': str[i] := 'u';
      'à': str[i] := 'a';
      'è': str[i] := 'e';
      'ì': str[i] := 'i';
      'ò': str[i] := 'o';
      'ù': str[i] := 'u';
      'â': str[i] := 'a';
      'ê': str[i] := 'e';
      'î': str[i] := 'i';
      'ô': str[i] := 'o';
      'û': str[i] := 'u';
      'ä': str[i] := 'a';
      'ë': str[i] := 'e';
      'ï': str[i] := 'i';
      'ö': str[i] := 'o';
      'ü': str[i] := 'u';
      'ã': str[i] := 'a';
      'õ': str[i] := 'o';
      'ñ': str[i] := 'n';
      'ç': str[i] := 'c';
      'Á': str[i] := 'A';
      'É': str[i] := 'E';
      'Í': str[i] := 'I';
      'Ó': str[i] := 'O';
      'Ú': str[i] := 'U';
      'À': str[i] := 'A';
      'È': str[i] := 'E';
      'Ì': str[i] := 'I';
      'Ò': str[i] := 'O';
      'Ù': str[i] := 'U';
      'Â': str[i] := 'A';
      'Ê': str[i] := 'E';
      'Î': str[i] := 'I';
      'Ô': str[i] := 'O';
      'Û': str[i] := 'U';
      'Ä': str[i] := 'A';
      'Ë': str[i] := 'E';
      'Ï': str[i] := 'I';
      'Ö': str[i] := 'O';
      'Ü': str[i] := 'U';
      'Ã': str[i] := 'A';
      'Õ': str[i] := 'O';
      'Ñ': str[i] := 'N';
      'Ç': str[i] := 'C';
      end;
   Result := str;
end;

function fRemoveFormatoCarEsp(Texto: string): string;
var
   Aux: string;
begin
   Aux := Texto;
   Aux := StringReplace(Aux, '/', '', [rfReplaceAll]);
 //  Aux := StringReplace(Aux, ',', '', [rfReplaceAll]);
//   Aux := StringReplace(Aux, '.','', [rfReplaceAll]);
   Aux := StringReplace(Aux, ':','' , [rfReplaceAll]);
   Aux := StringReplace(Aux, '-', '', [rfReplaceAll]);
//   Aux := StringReplace(Aux, '(', '', [rfReplaceAll]);
//   Aux := StringReplace(Aux, ')', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, 'º', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, 'ª', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, '°', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, '-', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, '*', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, '&', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, '¨', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, '%', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, '$', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, '#', '', [rfReplaceAll]);
 //  Aux := StringReplace(Aux, '@', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, '!', '', [rfReplaceAll]);
 //  Aux := StringReplace(Aux, '_', '', [rfReplaceAll]);
 //  Aux := StringReplace(Aux, '=', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, '+', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, '”', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, '´', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, '`', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, '§', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, ';', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, '<', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, '>', '', [rfReplaceAll]);
 //  Aux := StringReplace(Aux, ',', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, '{', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, '}', '', [rfReplaceAll]);
 //  Aux := StringReplace(Aux, '[', '', [rfReplaceAll]);
 //  Aux := StringReplace(Aux, ']', '', [rfReplaceAll]);
   Aux := StringReplace(Aux, '\', '', [rfReplaceAll]);
   fRemoveFormatoCarEsp := Aux;
end;

function FileVerInfo(const FileName: string;var FileInfo: TStringList): Boolean;
//
// Obtem diversas informações de um arquivo executável
//
// Requer um StringList criado antes de executar a função
// deve ser declarado na clausula Var no inicio da Unit
// StrLst := TStringList.Create;
//
//
const

Key: array[1..9] of string =('CompanyName',
  'FileDescription',
  'FileVersion',
  'InternalName',
  'LegalCopyright',
  'OriginalFilename',
  'ProductName',
  'ProductVersion',
  'Comments');

KeyBr: array [1..9] of string = ('Empresa..........................',
  'Descricao........................',
  'Versao do Arquivo...........',
  'Nome Interno...................',
  'Copyright..........................',
  'Nome Original do Arquivo.',
  'Produto.............................',
  'Versao do Produto............',
  'Comentarios...............:');
var
  Dummy : THandle;
  wnd:dword;
  c,BufferSize, Len : Integer;
  Buffer : PChar;
  LoCharSet, HiCharSet : Word;
  Translate, Return : Pointer;
  StrFileInfo, Flags : string;
  acumula,TargetOS, TypeArq : string;
  FixedFileInfo : Pointer;
  i : Byte;
begin
   Result := False;
   If not FileExists(FileName) then
      begin
         showmessage('Arquivo não encontrado');
         Result := False;
         exit;
      end;
   BufferSize := GetFileVersionInfoSize(pchar(FileName), wnd);
   if BufferSize <> 0 then
      begin
        GetMem(Buffer, Succ(BufferSize));
        try
          if GetFileVersionInfo(PChar(FileName), 0, BufferSize,Buffer) then
            begin
            if VerQueryValue(Buffer, '\VarFileInfo\Translation', Translate, UINT(Len)) then
               begin
                  LoCharSet := LoWord(Longint(Translate^));
                  HiCharSet := HiWord(Longint(Translate^));
                  for i := 1 to 9 do
                     begin
                        StrFileInfo := Format('\StringFileInfo\0%x0%x\%s',[LoCharSet, HiCharSet, Key[i]]);
                        if VerQueryValue(Buffer,PChar(StrFileInfo), Return,UINT(Len)) then
                           begin
                              FileInfo.Add(KeyBr[i] + ': ' + PChar(Return));
                              if i = 3 then
                                frmprincipal.versao :=PChar(Return);
                              // verifica o ultimo digito da versao, se for igual a 1 inclui zero no fim
                              for c := length(frmprincipal.versao) downto 0 do
                              begin
                                 acumula:=acumula+copy(frmprincipal.versao,c,1);
                                 if copy(frmprincipal.versao,c,1) = '.' then
                                    break;
                              end;
                              acumula:=buscatroca(acumula,'.','');
                              if length(acumula) = 1 then
                                 insert('0',frmprincipal.versao,(length(frmprincipal.versao)));
                           end;
                     end;
                  if VerQueryValue(Buffer,'\',FixedFileInfo, UINT(Len)) then
                  with TVSFixedFileInfo(FixedFileInfo^) do
                  begin
Flags := '';
if (dwFileFlags and VS_FF_DEBUG) = VS_FF_DEBUG then
begin
Flags := Concat(Flags,'*Debug* ');
end;
if (dwFileFlags and VS_FF_SPECIALBUILD) = VS_FF_SPECIALBUILD then
begin
Flags := Concat(Flags, '*Special Build* ');
end;
if (dwFileFlags and VS_FF_PRIVATEBUILD) = VS_FF_PRIVATEBUILD then
begin
Flags := Concat(Flags, '*Private Build* ');
end;
if (dwFileFlags and VS_FF_PRERELEASE) = VS_FF_PRERELEASE then
begin
Flags := Concat(Flags, '*Pre-Release Build* ');
end;
if (dwFileFlags and VS_FF_PATCHED) = VS_FF_PATCHED then
begin
Flags := Concat(Flags, '*Patched* ');
end;
if Flags <> '' then
begin
FileInfo.Add('Atributos: ' + Flags);
end;
TargetOS := 'Plataforma (OS): ';
case dwFileOS of
VOS_UNKNOWN : TargetOS := Concat(TargetOS, 'Desconhecido');
VOS_DOS : TargetOS := Concat(TargetOS, 'MS-DOS');
VOS_OS216 : TargetOS := Concat(TargetOS, '16-bit OS/2');
VOS_OS232 : TargetOS := Concat(TargetOS, '32-bit OS/2');
VOS_NT : TargetOS := Concat(TargetOS, 'Windows NT');
VOS_NT_WINDOWS32, 4: TargetOS := Concat(TargetOS, 'Win32 API');
VOS_DOS_WINDOWS16: TargetOS := Concat(TargetOS, '16-bit Windows ','sob MS-DOS');
else
TargetOS := Concat(TargetOS, 'Fora do Padrão. Código: ', IntToStr(dwFileOS));
end;
FileInfo.Add(TargetOS);
TypeArq := 'Tipo de Arquivo: ';
case dwFileType of
VFT_UNKNOWN : TypeArq := Concat(TypeArq,'Desconhecido');
VFT_APP : TypeArq := Concat(TypeArq,'Aplicacao');
VFT_DLL : TypeArq := Concat(TypeArq,'Dynamic-Link Lib.');
VFT_DRV : begin
TypeArq := Concat(TypeArq,'Device driver - Driver ');
case dwFileSubtype of
VFT2_UNKNOWN : TypeArq := Concat(TypeArq,'Desconhecido');
VFT2_DRV_PRINTER : TypeArq := Concat(TypeArq,'de Impressao');
VFT2_DRV_KEYBOARD : TypeArq := Concat(TypeArq,'de Teclado');
VFT2_DRV_LANGUAGE : TypeArq := Concat(TypeArq,'de Idioma');
VFT2_DRV_DISPLAY : TypeArq := Concat(TypeArq,'de Vídeo');
VFT2_DRV_MOUSE : TypeArq := Concat(TypeArq,'de Mouse');
VFT2_DRV_NETWORK : TypeArq := Concat(TypeArq,'de Rede');
VFT2_DRV_SYSTEM : TypeArq := Concat(TypeArq,'de Sistema');
VFT2_DRV_INSTALLABLE : TypeArq := Concat(TypeArq,'Instalavel');
VFT2_DRV_SOUND : TypeArq := Concat(TypeArq,'Multimida');
end;
end;
VFT_FONT : begin
TypeArq := Concat(TypeArq,'Fonte - Fonte ');
case dwFileSubtype of
VFT2_UNKNOWN : TypeArq := Concat(TypeArq, 'Desconhecida');
VFT2_FONT_RASTER : TypeArq := Concat(TypeArq,'Raster');
VFT2_FONT_VECTOR : TypeArq := Concat(TypeArq,'Vetorial');
VFT2_FONT_TRUETYPE : TypeArq := Concat(TypeArq,'TrueType');
end;
end;
VFT_VXD : TypeArq := Concat(TypeArq,'Virtual Device');
VFT_STATIC_LIB: TypeArq := Concat(TypeArq,'Static-Link Lib.');
end;
FileInfo.Add(TypeArq);
end;
end;
end;
finally
FreeMem(Buffer, Succ(BufferSize));
Result := FileInfo.Text <> '';
end;
end;
end;

function StrToPChar(const Str: string): PwideChar;
{Converte String em Pchar}
type
  TRingIndex = 0..7;
var
  Ring: array[TRingIndex] of PAnsiChar;
  RingIndex: TRingIndex;
  Ptr: pChar;
begin
  Ptr := @Str[Length(Str)];
  Inc(Ptr);
  if Ptr^ = #0 then
     begin
        Result := @Str[1];
     end
  else
     begin
        Result := StrAlloc(Length(Str)+1);
        RingIndex := (RingIndex + 1) mod (High(TRingIndex) + 1);
        StrPCopy(Result,Str);
        //StrDispose(Ring[RingIndex]);
        Ring[RingIndex]:= pansichar(Result);
     end;
end;

function ConvertISODate(isoDate: string): TDateTime;
var
  ano, mes, dia: Word;
begin
  // Assumindo formato 'YYYY-MM-DD'
  ano := StrToInt(Copy(isoDate, 1, 4));
  mes := StrToInt(Copy(isoDate, 6, 2));
  dia := StrToInt(Copy(isoDate, 9, 2));
  Result := EncodeDate(ano, mes, dia);
end;

procedure ExecutePrograma(Nome, Parametros: String);
Var
 Comando: Array[0..1024] of Char;
 Parms: Array[0..1024] of Char;
begin
  StrPCopy (Comando, Nome);
  StrPCopy (Parms, Parametros);
  ShellExecute (0, Nil, strtopchar(Comando), Parms, Nil, SW_ShowNormal);
//   winexec(strtopchar(Nome),SW_ShowMaximized);
end;

//Verifica se um CEP é valido ou não, passando o Estado e o Cep como parâmetro.
function ChecaCEP(cCep:String ; cEstado:String): Boolean;
var
cCEP1 : Integer;
begin
  cCep := copy(cCep,1,5) + copy(cCep,7,3);
  cCEP1 := StrToInt(copy(cCep,1,3));
  if Length(trim(cCep)) > 0 then
  begin
  if (StrToInt(cCep) <= 1000000.0) then
  begin
  MessageDlg('CEP tem que ser maior que [01000-000]',mtError,[mbOk],0);
  Result := False
  end
  else
  begin
  if Length(trim(copy(cCep,6,3))) < 3 then Result := False else
  if (cEstado = 'SP') and (cCEP1 >= 10 ) and (cCEP1 <= 199) then
     Result := True
  else
  if (cEstado = 'RJ') and (cCEP1 >= 200) and (cCEP1 <= 289) then Result := True else
  if (cEstado = 'ES') and (cCEP1 >= 290) and (cCEP1 <= 299) then Result := True else
  if (cEstado = 'MG') and (cCEP1 >= 300) and (cCEP1 <= 399) then Result := True else
  if (cEstado = 'BA') and (cCEP1 >= 400) and (cCEP1 <= 489) then Result := True else
  if (cEstado = 'SE') and (cCEP1 >= 490) and (cCEP1 <= 499) then Result := True else
  if (cEstado = 'PE') and (cCEP1 >= 500) and (cCEP1 <= 569) then Result := True else
  if (cEstado = 'AL') and (cCEP1 >= 570) and (cCEP1 <= 579) then Result := True else
  if (cEstado = 'PB') and (cCEP1 >= 580) and (cCEP1 <= 589) then Result := True else
  if (cEstado = 'RN') and (cCEP1 >= 590) and (cCEP1 <= 599) then Result := True else
  if (cEstado = 'CE') and (cCEP1 >= 600) and (cCEP1 <= 639) then Result := True else
  if (cEstado = 'PI') and (cCEP1 >= 640) and (cCEP1 <= 649) then Result := True else
  if (cEstado = 'MA') and (cCEP1 >= 650) and (cCEP1 <= 659) then Result := True else
  if (cEstado = 'PA') and (cCEP1 >= 660) and (cCEP1 <= 688) then Result := True else
  if (cEstado = 'AM') and ((cCEP1 >= 690) and (cCEP1 <= 692) or (cCEP1 >= 694) and

  (cCEP1 <= 698)) then Result := True else
  if (cEstado = 'AP') and (cCEP1 = 689) then Result := True else
  if (cEstado = 'RR') and (cCEP1 = 693) then Result := True else
  if (cEstado = 'AC') and (cCEP1 = 699) then Result := True else
  if ((cEstado = 'DF') or (cEstado = 'GO')) and (cCEP1 >= 700)and(cCEP1 <= 769)then

  Result := True else
  if (cEstado = 'TO') and (cCEP1 >= 770) and (cCEP1 <= 779) then Result := True else
  if (cEstado = 'MT') and (cCEP1 >= 780) and (cCEP1 <= 788) then Result := True else
  if (cEstado = 'MS') and (cCEP1 >= 790) and (cCEP1 <= 799) then Result := True else
  if (cEstado = 'RO') and (cCEP1 = 789) then Result := True else
  if (cEstado = 'PR') and (cCEP1 >= 800) and (cCEP1 <= 879) then Result := True else
  if (cEstado = 'SC') and (cCEP1 >= 880) and (cCEP1 <= 899) then Result := True else
  if (cEstado = 'RS') and (cCEP1 >= 900) and (cCEP1 <= 999) then Result := True else

  Result := False
  end;
  end
  else
  begin
  Result := True;
  end
end;

function gravalog(usucod: string; data : string; atividade : string) : string;
var
   data1,sql:string;
   hora1:tdatetime;
begin
   with modulo_dados do
   begin
      if data = '' then
         data:='01/01/1900'
      else
         data:=copy(data,7,4)+'-'+copy(data,4,2)+'-'+copy(data,1,2);
      hora1:=time;
      if usucod = '' then
         begin
            messagedlg('CÓDIGO DO USUÁRIO NÃO ENCONTRADO !!!!!',mterror,[mbok],0);
            exit;
         end;
      sql:='INSERT INTO USER_geoapolo_logatividades (usucod, data, descricao, hora) ';
      sql:=sql+' VALUES (:usucod, :data, :atividade, :hora1 );';
      fdquerysql3.Close;
      fdquerysql3.SQL.Clear;
      fdquerysql3.SQL.Text := sql;
      fdquerysql3.ParamByName('usucod').AsString := uppercase(usucod);
      fdquerysql3.ParamByName('data').AsString := data;
      fdquerysql3.ParamByName('atividade').AsString:= atividade;
      fdquerysql3.ParamByName('hora1').AsString := timetostr(hora1);
      if not executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
         begin
            messagedlg('PROBLEMAS AO GRAVAR O LOG DE ATIVIDADES !!!',mterror,[mbok],0);
            exit;
         end;
   end;
end;

function gravalogapolo(modulo: string; usucod : string; logsysdatahora : string; logsysnumdoc: string; logsysobs:string) : string;
var
   datahora,sql:string;
begin
   with modulo_dados do
   begin
      datahora:=copy(logsysdatahora,4,2)+'/'+copy(logsysdatahora,1,2)+'/'+copy(logsysdatahora,7,4);
      sql:='SELECT MAX(logsysseq)+1 AS LOGSYSSEQ FROM log_sys';
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := sql;
      if executaracao(fdquerysql,fdbanco, true, dtsfdquerysql) then
         begin
            sql:='INSERT INTO log_sys (EMPCOD, LOGSYSSEQ, LOGSYSTABELA, LOgSYSDATAHORA, LOGSYSOPER, USUCOD,  LOGSYSNUMDOC, LOGSYSOBS)';
            sql:= sql+' VALUES (:empcod, :logsysseq, :logsystabela, :logsysdatahora, :logsysoper, :usucod, :logsysnumdoc, :logsysobs)';
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('empcod').asstring := frmprincipal.codigo_empresa;
            fdquerysql3.ParamByName('logsysseq').AsString:= fdquerysql.FieldByName('logsysseq').AsString;
            fdquerysql3.ParamByName('logsystabela').AsString:= modulo;
            fdquerysql3.ParamByName('logsysdatahora').AsString:= datahora;
            fdquerysql3.ParamByName('logsysoper').AsString := 'Inclusão';
            fdquerysql3.ParamByName('usucod').AsString := usucod;
            fdquerysql3.ParamByName('logsysnumdoc').AsString := logsysnumdoc;
            fdquerysql3.ParamByName('logsysobs').AsString := logsysobs;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
               end;
         end;
   end;
end;

function nomedomes(Mes:Word;Abrev:Boolean):String;
{Retorna o nome de um mês abreviado ou não}
const
  NameL : array [1..12] of String[20] = ('JANEIRO','FEVEREIRO',
  'MARÇO','ABRIL',
  'MAIO','JUNHO','JULHO','AGOSTO','SETEMBRO','OUTUBRO',
  'NOVEMBRO','DEZEMBRO');
begin
  if (Mes in [1..12]) then
     if Abrev then
        Result := Copy(NameL[Mes],1,3)
     else
       Result := NameL[Mes];
end;

function DataExtenso(Data:TDateTime): String;
{Retorna uma data por extenso}
var
  NoDia : Integer;
  DiaDaSemana : array [1..7] of String;
  Meses : array [1..12] of String;
  Dia, Mes, Ano : Word;
begin
{ Dias da Semana }
  DiaDasemana [1]:= 'Domingo';
  DiaDasemana [2]:= 'Segunda-feira';
  DiaDasemana [3]:= 'Terçafeira';
  DiaDasemana [4]:= 'Quarta-feira';
  DiaDasemana [5]:= 'Quinta-feira';
  DiaDasemana [6]:= 'Sexta-feira';
  DiaDasemana [7]:= 'Sábado';
{ Meses do ano }
  Meses [1] := 'Janeiro';
  Meses [2] := 'Fevereiro';
  Meses [3] := 'Março';
  Meses [4] := 'Abril';
  Meses [5] := 'Maio';
  Meses [6] := 'Junho';
  Meses [7] := 'Julho';
  Meses [8] := 'Agosto';
  Meses [9] := 'Setembro';
  Meses [10]:= 'Outubro';
  Meses [11]:= 'Novembro';
  Meses [12]:= 'Dezembro';
  DecodeDate (Data, Ano, Mes, Dia);
  NoDia := DayOfWeek (Data);
  Result := DiaDaSemana[NoDia] + ', ' +
  IntToStr(Dia) + ' de ' + Meses[Mes]+ ' de ' + IntToStr(Ano);
end;

procedure imprime(Nlin,Ncol: Integer;Var LinhaAtual: Integer; Var Arquivo: Text;Texto: Variant);
{Função para impressão de linhas em um relatório}
var
   X: Integer;
begin
  Write(Arquivo,#13);
  If Nlin<>LinhaAtual then
    begin
      for X :=LinhaAtual to (Nlin-1) do
        begin
          WriteLn(Arquivo,'');
          LinhaAtual:=LinhaAtual+1;
        end;
    end;
  If Ncol>0 then
    begin
      For X:=0 to Ncol do
         Write(Arquivo,' ');
    end;
  If LinhaAtual >=63 then { 63 É O NÚMERO DA ÚLTIMA LINHA ANTES DO RODAPÉ}
    begin
      For X:=63 to 67 do { 67 É A QUANTIDADE DE LINHAS POR PÁGINA }
        begin
          Writeln(Arquivo,'');
          LinhaAtual:=1;
        end;
    end;
  Write(Arquivo,Texto);
end;

procedure SetDefaultPrinter(PrinterName: String);
var
  I: Integer;
  Device,driver,port : PChar;
  HdeviceMode: Thandle;
  aPrinter : TPrinter;
begin
  Printer.PrinterIndex := -1;
  getmem(Device, 255);
  getmem(Driver, 255);
  getmem(Port, 255);
  aPrinter := TPrinter.create;
  for I := 0 to Printer.printers.Count-1 do
    begin
      if Printer.printers[i] = PrinterName then
        begin
          aprinter.printerindex := i;
          aPrinter.getprinter
          (device, driver, port, HdeviceMode);
          StrCat(Device, ',');
          StrCat(Device, Driver );
          StrCat(Device, Port );
          WriteProfileString('windows', 'device', Device);
          StrCopy( Device, 'windows' );
          SendMessage(HWND_BROADCAST, WM_WININICHANGE,
          0, Longint(@Device));
        end;
    end;
  Freemem(Device, 255);
  Freemem(Driver, 255);
  Freemem(Port, 255);
  aPrinter.Free;
end;

Function Alinhar(Pe_Num:Real; Pe_QtdPos:Byte; EDC :Char):string;
// EDC: C = Centralizado
// D = Direita
// E = Esquerda
var
  I : integer;
  S : string;
  Num : string;
begin
  if EDC = 'D' then
    begin
      Num := Format('%*.*n', [Pe_QtdPos, 2, Pe_Num]);
      Alinhar := Num;
    end;
  if EDC = 'E' then
    begin
      Num := FormatFloat('###,###,###,##0.00',Pe_Num);
      Alinhar := Num;
    end;
  if EDC = 'C' then
    begin
      Num := FormatFloat('###,###,###,##0.00',Pe_Num);
      i := Pos(',',Num);
      i := i + 2;
      i := Pe_QtdPos - i;
      i := Round( i / 2 );
      i := Pe_QtdPos - i;
      Num := Format('%*.*n', [i,2,Pe_Num]);
      str(i,s);
      Alinhar := Num
    end;
end;

function preenche_vetor:string ;
var
  i,a,k:integer;
begin
   k:=65;
   for i:= 1 to 26 do
   begin
      alpha[i]:=chr(k);
      k:=k+1;
   end;
   k:=97;
   for i:= 27 to 52 do
   begin
      alpha[i]:=chr(k);
      k:=k+1;
   end;
   k:=48;
   for i:= 53 to 62 do
   begin
      alpha[i]:=chr(k);
      k:=k+1;
   end;
   k:=32;
   for i := 63 to 78 do
   begin
      alpha[i]:=chr(k);
      k:=k+1;
   end;
   k:=58;
   for i := 79 to 85 do
   begin
      alpha[i]:=chr(k);
      k:=k+1;
   end;
   k:=91;
   for i := 86 to 90 do
   begin
      alpha[i]:=chr(k);
      k:=k+1;
   end;
   k:=123;
   for i := 91 to 93 do
   begin
      alpha[i]:=chr(k);
      k:=k+1;
   end;
   k:=0;
end;

function criptografia(chave : integer; recebetexto : string) : string;
var
   ida:integer;
   senhacripto:string;
begin
   // a função abaixo alimenta os vetores com a tabela asc do alfabeto maiusculo e minusculo e os números de 0 a 10
   preenche_vetor;
   chavet:=chave; // chave é quem será base para fazer o calculo da criptografia
   tam:=0;
   {o for abaixo pega a senha digitada e joga dentro do vetor mensagem e já vê o tamanho que tem a senha, ou seja
    quantos caracteres tem.}
   for i := 1 to length(recebetexto) do
     begin
        mensagem[i]:=copy(recebetexto,i,1);
        tam:=tam+1;
     end;
   // rotina para criptografar e gerar a senha
   {o primeiro for irá percorrer a senha de 1 até o tamanho dela apurado no for anterior, o segundo for é o número de caratecteres que será inserido
   nos vetores alpha, inserção esta feita pela função preenche_vetor, que insere o alfabeto de A a Z em maiúsculo e minusculo mais os números de 0 a 9,
   o if verifica se a posição j está iguala posição i, se tiver ele pega o valor de j e soma com a chave de criptografia informada como parâmetro na função
   depois verifica se esta chave for menor que 63 (que é os alfabetos e os números da função preenche_vetor) depois disso no vetor cripto que irá guardar a
   senha criptografada jogo da posição I o resultado da variável j+ a chave, ou seja neste ponto o caracter já foi trocado. No último for da função vou gerar
   uma variável senhacripto com o resultado dos caracteres trocados, conforme abaixo concatenando caracter e caracter depois retornando a variável concatenada}
   for i:= 1 to tam do
   begin
      for j:=1 to 92 do
      begin
         if (alpha[j] = mensagem[i]) then
           begin
             ida:=j+chavet;
             if ida<=92 then
               begin
                 cripto[i]:=alpha[ida];
               end
             else
                 begin
                   ida:=ida-92;
                   cripto[i]:=alpha[ida];
                 end;
           end;
      end;
   end;
   // rotina que coloca a senha criptografada no edit
   i:=0;
   for i:= 1 to tam do
   begin
      senhacripto := senhacripto+cripto[i];
   end;
   result := senhacripto;
end;

function decriptografia(chave :integer; senhacripto : string; senhaoriginal : string) : string;
var
   senhadecripto:string;
   a:integer;
begin
   tam:=length(senhacripto);
   preenche_vetor;
   //
   for i:= 1 to tam do
   begin
      cripto[i]:=copy(senhacripto,i,1);
   end;
   //
   for a:= 1 to tam do
   begin
      for j:= 1 to 92 do
      begin
         if alpha[j] = cripto[a] then
         begin
            y:=j-chave;
            if y<=0 then
               begin
                  y:=y+92;
                  volta[a]:=alpha[y];
               end
            else
               begin
                  volta[a]:=alpha[y];
               end;
         end;
      end;
   end;
   // rotina que coloca a senha decodificada no edit
   i:=0;
   for i:= 1 to tam do
   begin
      senhadecripto := senhadecripto+volta[i];
   end;
   result := senhadecripto;
end;

function UserName : String;
//
// Retorna o usuário que está logado na rede
//
// Esta função funciona tanto no Win9x quanto no NT
//
var
   lpBuffer : Array[0..20] of Char;
   nSize    : dWord;
   Achou    : boolean;
   erro     : dWord;
begin
   nSize      := 120;
   Achou      := GetUserName(lpBuffer,nSize);
  if (Achou) then
     begin
        result   := lpBuffer;
     end
  else
     begin
        Erro   :=GetLastError();
        result :=IntToStr(Erro);
     end;
end;

function NomeComputador : String;
var
  lpBuffer : PChar;
  nSize : DWord;
const Buff_Size = MAX_COMPUTERNAME_LENGTH + 1;
begin
  nSize := Buff_Size;
  lpBuffer := StrAlloc(Buff_Size);
  GetComputerName(lpBuffer,nSize);
  Result := String(lpBuffer);
  StrDispose(lpBuffer);
end;

function LogUser : String;
{Retorna o nome do usuário logado na rede
 Requer a unit Registry declarada na clausula Uses da Unit}
var
  Registro: TRegistry;
begin
   Registro := TRegistry.Create;
   Registro.RootKey := HKEY_CURRENT_USER;
   if Registro.OpenKey('Network\Logon', false) then
   begin
      result := Registro.ReadString('username');
   end;
   Registro.Free;
end;

function GetLocalIP : string;
type
  TaPInAddr = array [0..10] of PInAddr;
  PaPInAddr = ^TaPInAddr;
var
  phe : PHostEnt;
  pptr : PaPInAddr;
  Buffer : array [0..63] of ansichar;
  I : Integer;
  GInitData : TWSADATA;
begin
  WSAStartup($101, GInitData);
  Result := '';
  GetHostName(Buffer, SizeOf(Buffer));
  phe :=GetHostByName(buffer);
  if phe = nil then Exit;
  pptr := PaPInAddr(Phe^.h_addr_list);
  I := 0;
  while pptr^[I] <> nil do
  begin
    result:=StrPas(inet_ntoa(pptr^[I]^));
    result := StrPas(inet_ntoa(pptr^[I]^));
    Inc(I);
  end;
  WSACleanup;
end;

function cria_view(sqlrec : string; modulo : string; baseparacampanha: string; formulario:tform): string;
var
  cmd: TFDCommand;
begin
   with modulo_dados, formulario do
   begin
       if baseparacampanha = 'Apolo' then
          begin
            sql:='SELECT * FROM sysobjects WHERE name = '+quotedstr(modulo);
            fdquerysql.close;
            fdquerysql.sql.clear;
            fdquerysql.sql.text := sql;
            setcursorsql('sql');
            if not executaracao(fdquerysql,fdbanco,true,dtsfdquerysql) then
               begin
                  sql:='CREATE VIEW '+modulo;
                  sql:=sql+' as '+sqlrec;
                  fdcomando.commandtext.clear;
                  fdcomando.ResourceOptions.CmdExecMode := amBlocking;
                  fdcomando.ResourceOptions.CmdExecTimeout := 300;
                  fdcomando.CommandText.add(sql);
                  fdcomando.Execute;
               end
            else
               begin
                  sql:='DROP VIEW '+modulo;
                  if ExecutaDDL(fdbanco, sql) then
                  begin
                  end;
                  sql:='';
                  sql:='CREATE VIEW '+modulo;
                  sql:=sql+' as '+sqlrec;
                  if ExecutaDDL(fdbanco, sql) then
                  else
               end;
            setcursorsql('');
          end
       else if baseparacampanha = 'GeoApolo' then
          begin
             setcursorsql('sql');
             fdquerysql12.close;
             fdquerysql12.sql.clear;
             sql:='SELECT NAME FROM sys.views WHERE name LIKE :pmodulo' ;
             fdquerysql12.sql.text := sql;
             fdquerysql12.parambyname('pmodulo').asstring := modulo;
             fdquerysql12.sql.text := sql;
             if executaracao(fdquerysql12, fdbanco, true, dtsfdquerysql12) then
                begin
                  sql:='DROP VIEW '+modulo;
                  if ExecutaDDL(fdbanco, sql) then
                end;
             sql:='CREATE VIEW '+lowercase(modulo)+' AS  ';
             sql:=sql+sqlrec+';';
             if ExecutaDDL(fdbanco, sql) then
             begin
             end;
             setcursorsql('');
          end;
      end;
end;
{
function sincronizaemail_apolo_geoapolo : string;
var
   nome:string;
begin
   with modulo_dados do
   begin
      //O QUE É ALTERADO AQUI NO GEOAPOLO É REPLICADO PARA A BASE DO APOLO
      sql:='select * from usuarios where flagativo = '+chr(39)+'A'+chr(39)+' and email is not null';
      executaracao(sql,querysqlsql);
      if querysqlsql.RecordCount > 0 then
         begin
            querysqlsql.First;
            while not querysqlsql.Eof do
            begin
               sql:='select * from usuario where usucod = '+quotedstr(querysqlsql.fieldbyname('login').AsString)+' and usustat = '+quotedstr('Ativo')+' and usuemail is not null';
               executaracao(sql,querysql);
               if querysql.RecordCount > 0 then
                  begin
                     sql:='UPDATE usuario SET usuemail = '+quotedstr(querysqlsql.fieldbyname('email').asstring);
                     sql:=sql+' WHERE usucod = '+quotedstr(uppercase(querysqlsql.fieldbyname('login').asstring))+' and usustat = '+quotedstr('Ativo');
                     executaracao(sql,querysql3);
                     if querysql3.RowsAffected > 0 then
                        begin

                        end;
                  end
               else
                  begin
                     nome:=tiracento(querysqlsql.fieldbyname('Nome').asstring);
                     sql:='SELECT usucod FROM usuario WHERE usunome = '+quotedstr(buscatroca(uppercase(nome),chr(39),quotedstr(chr(39))));
                     executaracao(sql,querysql2);
                     if querysql2.RecordCount > 0 then
                        begin
                           sql:='UPDATE usuario SET  usuemail = '+quotedstr(querysqlsql.fieldbyname('email').asstring);
                           sql:=sql+' WHERE  usunome = '+quotedstr(buscatroca(uppercase(nome),chr(39),quotedstr(chr(39))));
                           executaracao(sql,querysql3);
                           if querysql3.RowsAffected > 0 then
                              begin

                              end;
                        end;
                  end;
               querysqlsql.Next;
            end;
         end;
   end;
end;

function sincronizar_chapamix_usuariogeoapolo : string;
var
   linha, sql, data_nascimento, nomesemacento,secaogeoapolo,login,login1, login2:string;
   i,a,c,pendentes:integer;
begin
    with modulo_dados do
    begin
      pendentes:=0;
      sql:='select fofunc.PE_NOME, fofunc.FU_CHAPA, fofunc.fu_stf_codigo, fofunc.FU_ES_ID_ESTRUTURA, fope.PE_DT_NASC, fofunc.FU_MATRICULA, fofunc.fu_cac_codigo, fc.car_nome';
      sql:=sql+' from fo_funcionario fofunc with(nolock), fo_pessoa fope with(nolock), fo_cargo fc with(nolock)';
      sql:=sql+' WHERE fofunc.pe_codigo = fope.pe_codigo';
      sql:=sql+' and   fofunc.fu_cac_codigo = fc.cac_codigo';
      sql:=sql+' and   fofunc.fu_stf_codigo not in ('+quotedstr('D')+','+quotedstr('Y')+')';
      sql:=sql+' and   substring(fofunc.fu_es_id_estrutura,1,5) in('+quotedstr('01.01')+', '+quotedstr('02.01')+')' ;
      sql:=sql+' and   fofunc.fu_tfu_codigo in ('+quotedstr('N')+', '+quotedstr('T')+', '+quotedstr('Z')+', '+quotedstr('H')+', '+quotedstr('R')+')';
      sql:=sql+' and   fofunc.fu_tfu_codigo <> '+quotedstr('A');
      //sql:=sql+' and   fofunc.fu_chapa = '+quotedstr('1330');
      sql:=sql+' ORDER BY fofunc.pe_nome ASC';
      sqlrun(sql,querymix,banco_mix);
      if querymix.RecordCount > 0 then
         begin
            querymix.First;
            while not querymix.Eof do
            begin
               //cria login do usuário
               login:=''; login1:=''; login2:='';
               login:=buscatroca(querymix.fieldbyname('pe_nome').asstring,chr(39),quotedstr(chr(39)));
               for i:= 1 to length(login) do
               begin
                  if copy(login,i,1) <> ' ' then
                     login1:=login1+copy(login,i,1)
                  else
                     break;
               end;
               //
               for a:= length(login) downto 1 do
               begin
                  if copy(login,a,1) <> ' ' then
                     login2:=login2+copy(login,a,1)
                  else
                     break;
               end;
               sql:='';
               for c:= length(login2) downto 1 do
               begin
                  sql:=sql+copy(login2,c,1);
               end;
               login2:=sql;
               //
               login:=login1+'.'+login2;
               //
               sql:='SELECT * FROM geoapolo_cargos ';
               sql:=sql+' WHERE geo_cargocodestr = '+quotedstr(querymix.fieldbyname('fu_cac_codigo').AsString);
               executaracao(sql,querysqlsql);
               if querysqlsql.RecordCount > 0 then
                  begin
                     sql:='UPDATE geoapolo_cargos SET geo_cargocodestr = '+quotedstr(querymix.fieldbyname('fu_cac_codigo').asstring);
                     sql:=sql+', geo_cargonome = '+quotedstr(querymix.fieldbyname('car_nome').asstring);
                     sql:=sql+' WHERE geo_cargocodestr = '+quotedstr(querymix.fieldbyname('fu_cac_codigo').asstring);
                     executaracao(sql,querysqlsql3);
                     if querysqlsql3.RowsAffected > 0 then
                        begin
                        end;
                  end
               else
                  begin
                     sql:='INSERT INTO geoapolo_cargos (geo_cargocodestr, geo_cargonome) ';
                     sql:=sql+' VALUES ('+querymix.fieldbyname('fu_cac_codigo').asstring+', ';
                     sql:=sql+quotedstr(querymix.fieldbyname('car_nome').asstring)+');';
                     executaracao(sql,querysqlsql3);
                     if querysqlsql3.RowsAffected > 0 then
                        begin
                        end;
                  end;
               //-----------------------------------------------------------------------------------------------------------------------
               sql:='select * FROM usuarios WHERE nome = '+quotedstr(querymix.fieldbyname('pe_nome').asstring);
               executaracao(sql,querysqlsql);
               if querysqlsql.RecordCount > 0 then
                  begin
                     if copy(querymix.fieldbyname('pe_nome').asstring,1,1) = 'C' then
                        login:=login1+'.'+login2;
                     //
                     data_nascimento:=querymix.fieldbyname('PE_DT_NASC').asstring;
                     if data_nascimento = '  /  /    ' then
                        data_nascimento:='01/01/2000';
                     //
                     if data_nascimento = '//' then
                        data_nascimento:='01/01/2000';
                     //
                     data_nascimento:=copy(data_nascimento,4,2)+'/'+copy(data_nascimento,1,2)+'/'+copy(data_nascimento,7,4);
                     if querysqlsql.fieldbyname('login').asstring = '' then
                        begin
                           sql:='UPDATE usuarios SET data_nascimento = '+quotedstr(data_nascimento);
                           sql:=sql+', fu_chapa = '+quotedstr(querymix.fieldbyname('fu_chapa').asstring);
                           sql:=sql+', nome = '+quotedstr(buscatroca(querymix.fieldbyname('pe_nome').asstring,chr(39),quotedstr(chr(39))));
                           sql:=sql+', login = '+quotedstr(login)+', fu_matricula = '+quotedstr(querymix.fieldbyname('fu_matricula').asstring);
                           sql:=sql+', geo_cargocodestr = '+quotedstr(querymix.fieldbyname('fu_cac_codigo').asstring);
                           sql:=sql+' WHERE nome = '+quotedstr(querymix.fieldbyname('pe_nome').asstring)
                        end
                     else
                        begin
                           sql:='UPDATE usuarios SET data_nascimento = '+quotedstr(data_nascimento);
                           sql:=sql+', fu_chapa = '+quotedstr(querymix.fieldbyname('fu_chapa').asstring);
                           sql:=sql+', nome = '+quotedstr(buscatroca(querymix.fieldbyname('pe_nome').asstring,chr(39),quotedstr(chr(39))));
                           sql:=sql+', fu_matricula = '+quotedstr(querymix.fieldbyname('fu_matricula').asstring);
                           sql:=sql+', geo_cargocodestr = '+quotedstr(querymix.fieldbyname('fu_cac_codigo').asstring);
                           sql:=sql+' WHERE nome = '+quotedstr(querymix.fieldbyname('pe_nome').asstring);
                        end;
                     executaracao(sql,querysqlsql3);
                     if querysqlsql3.RowsAffected > 0 then
                        begin
                        end;
                  end
               else
                  begin
                     sql:='SELECT * FROM usuarios WHERE nome ='+quotedstr(buscatroca(querymix.fieldbyname('pe_nome').asstring,chr(39),quotedstr(chr(39))));
                     executaracao(sql,querysqlsql2);
                     if querysqlsql2.RecordCount = 0 then
                        begin
                           secaogeoapolo:=querymix.fieldbyname('FU_ES_ID_ESTRUTURA').asstring;
                           sql:='SELECT * FROM geoapolo_secoescctrlapolo WHERE cctrlcodestr = '+quotedstr(secaogeoapolo);
                           executaracao(sql,querysqlsql);
                           if querysqlsql.RecordCount > 0 then
                              begin
                                 secaogeoapolo:=querysqlsql.fieldbyname('codigo_secao').asstring;
                              end
                           else if copy(secaogeoapolo,1,5) = '02.01' then
                              secaogeoapolo := '224'
                           else
                              secaogeoapolo:='0';
                           //
                           data_nascimento:=querymix.fieldbyname('PE_DT_NASC').asstring;
                           data_nascimento:=copy(data_nascimento,4,2)+'/'+copy(data_nascimento,1,2)+'/'+copy(data_nascimento,7,4);
                           if secaogeoapolo <> '0' then
                              begin
                                  sql:='INSERT INTO usuarios (codigo_usuario,nome, codigo_secao, flagativo, login, email, fu_chapa, data_nascimento, fu_matricula, geo_cargocodestr) ';
                                  sql:=sql+' VALUES ('+geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_usuarios','Sim')+', '+quotedstr(buscatroca(querymix.fieldbyname('pe_nome').asstring,chr(39),quotedstr(chr(39))))+', '+secaogeoapolo;
                                  sql:=sql+', '+quotedstr('A')+', '+quotedstr('')+' , '+quotedstr('')+', '+quotedstr(querymix.fieldbyname('fu_chapa').asstring);
                                  sql:=sql+', '+quotedstr(data_nascimento)+', '+quotedstr(querymix.fieldbyname('fu_matricula').asstring)+', '+querymix.fieldbyname('fu_cac_codigo').AsString+');';
                                  executaracao(sql,querysqlsql3);
                                  if querysqlsql3.RowsAffected > 0 then
                                     begin
                                     end;
                              end
                           else
                              begin
                                  sql:='SELECT * FROM usuarios_pendentes WHERE nome ='+quotedstr(querymix.fieldbyname('pe_nome').asstring);
                                  sql:=sql+' and fu_matricula = '+quotedstr(querymix.fieldbyname('fu_matricula').asstring);
                                  executaracao(sql,querysqlsql1);
                                  if querysqlsql1.RecordCount =0 then
                                     begin
                                        sql:='INSERT INTO usuarios_pendentes (codigo_usuario,nome, codigo_secao, flagativo, login, email, fu_chapa, data_nascimento, fu_matricula,geo_cargocodestr) ';
                                        sql:=sql+' VALUES ('+geoapolo_configcod('1','usuarios_pendentes','Sim')+', '+quotedstr(buscatroca(querymix.fieldbyname('pe_nome').asstring,chr(39),quotedstr(chr(39))))+', '+secaogeoapolo;
                                        sql:=sql+', '+quotedstr('P')+', '+quotedstr(login)+' , '+quotedstr('')+', '+quotedstr(querymix.fieldbyname('fu_chapa').asstring);
                                        sql:=sql+', '+quotedstr(data_nascimento)+', '+quotedstr(querymix.fieldbyname('fu_matricula').asstring)+', '+querymix.fieldbyname('fu_cac_codigo').AsString+');';
                                        executaracao(sql,querysqlsql3);
                                        if querysqlsql3.RowsAffected > 0 then
                                           begin
                                           end;
                                        inc(pendentes);
                                     end;
                              end;
                        end
                     else
                  end;
                  querymix.next;
            end;
            if pendentes > 0 then
               begin
                  messagedlg('ALGUNS USUÁRIOS FORAM IMPORTADOS MAS TEM PENDÊNCIAS DE INFORMAÇÕES, VERIFIQUE NO MENU CADASTRO \ USUÁRIOS \ USUÁRIOS PENDENTES',mtwarning,[mbok],0);
                  resp:=messagedlg('Deseja acessá-los agora ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
                  if resp = idyes then
                     begin
                        application.CreateForm(tfrmusuariospendentes, frmusuariospendentes);
                        frmusuariospendentes.ShowModal;
                     end;
               end;
            // VERIFICA SE TEM FUNCIONÁRIOS DEMITIDOS E COMO ESTÁ O STATUS DESTE NO GEOAPOLO, CASO ESTEJAM ATIVOS ELE IRÁ MUDAR O
             // FLAGATIVO PARA I QUE É INATIVO
            sql:='select fofunc.PE_NOME, fofunc.FU_CHAPA, fofunc.FU_ES_ID_ESTRUTURA, fope.PE_DT_NASC, fofunc.FU_MATRICULA ';
            sql:=sql+' from fo_funcionario fofunc with(nolock), fo_pessoa fope with(nolock)';
            sql:=sql+' WHERE fofunc.pe_codigo = fope.pe_codigo';
            sql:=sql+' and   fofunc.fu_stf_codigo = '+quotedstr('D');
            sql:=sql+' and   substring(fofunc.fu_es_id_estrutura,1,5) = '+quotedstr('01.01');
            sql:=sql+' ORDER BY fofunc.pe_nome ASC';
            sqlrun(sql,modulo_dados.querymix,banco_mix);
            if querymix.RecordCount > 0 then
               begin
                  querymix.First;
                  while not querymix.Eof do
                  begin
                      //pega o nome do funcionário no mix e busca no postgresql para ver o status
                      sql:='SELECT nome FROM usuarios ';
                      sql:=sql+' WHERE fu_matricula = '+quotedstr(querymix.fieldbyname('fu_matricula').asstring);
                      executaracao(sql,querysqlsql);
                      if querysqlsql.RecordCount > 0 then
                         begin
                            sql:='UPDATE usuarios SET flagativo = '+quotedstr('I');
                            sql:=sql+' WHERE fu_matricula = '+quotedstr(querymix.fieldbyname('fu_matricula').asstring);
                            executaracao(sql,querysqlsql3);
                            if querysqlsql3.RowsAffected > 0 then
                               begin
                               end;
                            querymix.Next;
                         end
                      else
                         querymix.Next;
                  end;
               end;
            end;
      end;
end;

function sincroniza_cidades_apolo_to_geoapolo : string;
var
   cidnomecomp,estado:string;
begin
   with modulo_dados do
   begin
      sql:='SELECT gera_camp_baseapolo, integra_entidades_apolo FROM geoapolo_configuracoes';
      executaracao(sql,querysqlsql);
      if querysqlsql.fieldbyname('gera_camp_baseapolo').asstring = 'S' then
         begin
            sql:='SELECT cidnomecomp, ufsigla FROM cidade ORDER BY cidnomecomp ASC';
            executaracao(sql,querysql);
            if querysql.RecordCount > 0 then
               begin
                  querysql.First;
                  while not querysql.Eof do
                  begin
                     cidnomecomp:=trim(querysql.fieldbyname('cidnomecomp').asstring);
                     cidnomecomp :=buscatroca(cidnomecomp,chr(39),'-');
                     estado:=querysql.fieldbyname('ufsigla').asstring;
                     //
                     sql:='SELECT * FROM tab_cidades WHERE nome_cidade = '+quotedstr(cidnomecomp)+' and estado = '+quotedstr(estado);
                     executaracao(sql,querysqlsql);
                     if querysqlsql.RecordCount > 0 then
                        begin
                           //
                           sql:='UPDATE tab_cidades SET nome_cidade = '+quotedstr(cidnomecomp)+', estado = '+quotedstr(querysql.fieldbyname('ufsigla').asstring);
                           sql:=sql+' WHERE codigo_cidade = '+querysqlsql.fieldbyname('codigo_cidade').asstring;
                           executaracao(sql,querysqlsql3);
                           if querysqlsql3.RowsAffected > 0 then
                              querysql.Next;
                        end
                     else
                        begin
                           sql:='INSERT INTO tab_cidades (codigo_cidade,nome_cidade,estado)';
                           sql:=sql+' VALUES ('+geoapolo_configcod('1','tab_cidades','Sim')+', ';
                           sql:=sql+quotedstr(buscatroca(querysql.fieldbyname('cidnomecomp').asstring,chr(39),'-'))+', '+quotedstr(querysql.fieldbyname('ufsigla').asstring)+');';
                           executaracao(sql,querysqlsql3);
                           if querysqlsql3.RowsAffected > 0 then
                              querysql.Next;
                        end;
                  end;
               end;
         end;
   end;
end;

function adiciona_atualiza_usuarios_como_contatos_na_agenda : string;
var
   // tabela sag_contatos2
   status_func,codigo_contato,contatonovo, nome, n1,empresa, cargo,aniversario:string;
   i:integer;
begin
   with modulo_dados do
   begin
      sql:='select fu_matricula from usuarios where fu_matricula is not null';
      sql:=sql+' and flagativo = '+quotedstr('A');
      sql:=sql+' order by nome asc';
      executaracao(sql,querysqlsql2);
      if querysqlsql2.RecordCount > 0 then
         begin
            querysqlsql2.First;
            setcursorsql('sql');
            while not querysqlsql2.Eof do
            begin
               //
               sql:='SELECT * FROM fo_funcionario WHERE fu_matricula = '+quotedstr(querysqlsql2.fieldbyname('fu_matricula').asstring);
               sqlrun(sql,querysql5,banco_mix);
               if querysql5.RecordCount >  0 then
                  begin
                     // pega o status do funcionário antes de usar a consulta para outra coisa
                     sql:='SELECT funcstat FROM funcionario WHERE funccodchapamix = '+querysql5.fieldbyname('fu_chapa').AsString;
                     executaracao(sql,querysql6);
                     if querysql6.RecordCount > 0 then
                        status_func:=querysql6.fieldbyname('funcstat').AsString;
                     // pegar cargo
                     sql:='SELECT CAR_NOME FROM fo_cargo WHERE cac_codigo = '+quotedstr(querysql5.fieldbyname('fu_cac_codigo').asstring);
                     sqlrun(sql,querysql6,banco_mix);
                     if querysql6.RecordCount > 0 then
                        cargo:=querysql6.fieldbyname('car_nome').asstring;
                     // pegar empresa
                     sql:='select ES_RAZAO_SOCIAL from bs_estrutura where es_id_estrutura = '+quotedstr(querysql5.fieldbyname('fu_es_id_estrutura').asstring);
                     sqlrun(sql,querysql6,banco_mix);
                     if querysql6.RecordCount > 0 then
                        empresa:= querysql6.fieldbyname('es_razao_social').asstring;
                     //
                     sql:='SELECT pe_codigo,pe_nome,PE_DT_NASC from fo_pessoa WHERE pe_codigo = ';
                     sql:=sql+quotedstr(querysql5.fieldbyname('pe_codigo').asstring);
                     sqlrun(sql,querysql5,banco_mix);
                     if querysql5.RecordCount > 0 then
                        begin
                           nome:=querysql5.fieldbyname('pe_nome').asstring;
                           for i := 1 to length(nome) do
                           begin
                              if copy(nome,i,1) <> ' ' then
                                 n1:=n1+copy(nome,i,1)
                              else
                                 break;
                           end;
                           aniversario:= querysql5.fieldbyname('PE_DT_NASC').asstring;
                        end;
                  end;
                  //
                  if status_func = 'A' then
                     status_func:='Trabalhando'
                  else if status_func = 'F' then
                     status_func:='Férias'
                  else if status_func = 'D' then
                     status_func:='Demitido';
                  if (aniversario = '  /  /    ') or (aniversario = '//') or (aniversario = '') then
                     aniversario:='01/01/2000';
                  //
                   aniversario:=copy(aniversario,4,2)+'/'+copy(aniversario,1,2)+'/'+copy(aniversario,7,4);
                  // verifica se o contato existe no banco
                  sql:='SELECT * from sag_contatos2 where nome = '+quotedstr(nome);
                  executaracao(sql,querysqlsql4);
                  if querysqlsql4.RecordCount > 0 then
                     begin
                        sql:='UPDATE sag_contatos2 SET status_quando_funcionario = '+quotedstr(status_func);
                        sql:=sql+' where codigo_contato = '+querysqlsql4.fieldbyname('codigo_contato').asstring;
                        sql:='UPDATE sag_contatos2 set nome = '+quotedstr(nome)+', empresa = '+quotedstr(empresa)+', cargo = '+quotedstr(cargo)+', aniversario = '+quotedstr(aniversario)+', apelido = '+quotedstr(n1);
                        sql:=sql+', codigo_classe = '+quotedstr('11')+', ultima_atualizacao = '+quotedstr(copy(datetostr(date),4,2)+'/'+copy(datetostr(date),1,2)+'/'+copy(datetostr(date),7,4))+', codigo_usuario_ultatu = '+inttostr(frmlogon.codigousuario)+', status_quando_funcionario = '+quotedstr(status_func);
                        sql:=sql+' WHERE codigo_contato = '+querysqlsql4.fieldbyname('codigo_contato').asstring;
                        executaracao(sql,querysqlsql3);
                        if querysqlsql3.RowsAffected > 0 then
                           begin
                              atualiza_insere_contato_do_contato(querysqlsql4.fieldbyname('codigo_contato').asstring, querysql5.fieldbyname('pe_codigo').asstring);
                           end;
                        aniversario:='';
                        executaracao(sql,querysqlsql3);
                        if querysqlsql3.RowsAffected > 0 then
                        querysql5.Next;
                     end
                 else
                    begin
                      contatonovo:=geoapolo_configcod('1','sag_contatos2','Sim');
                      sql:='INSERT INTO sag_contatos2 (codigo_contato, nome, empresa, cargo, aniversario, codigo_classe, ultima_atualizacao, codigo_usuario_ultatu, apelido, status_quando_funcionario) ';
                      sql:=sql+' VALUES ('+contatonovo+', '+quotedstr(nome)+', '+chr(39)+empresa+chr(39)+', '+chr(39)+cargo+chr(39)+', '+quotedstr(aniversario)+', '+quotedstr('11')+', ';
                      sql:=sql+chr(39)+copy(datetostr(date),4,2)+'/'+copy(datetostr(date),1,2)+'/'+copy(datetostr(date),7,4)+chr(39)+', '+inttostr(frmlogon.codigousuario)+', '+quotedstr(n1)+', '+quotedstr(status_func)+');';
                      executaracao(sql,querysqlsql3);
                      if querysqlsql3.RowsAffected > 0 then
                         begin
                         end;
                      //
                      codigo_contato:=contatonovo;
                      atualiza_insere_contato_do_contato(codigo_contato, querysql5.fieldbyname('pe_codigo').asstring);
                      aniversario:='';
                      querysql5.next;
                   end;
                  // parte de comunicação com o contato
                  n1:='';
                  querysqlsql2.next;
            end;
            setcursorsql('');
         end;
   end;
end;

function atualiza_insere_contato_do_contato(codigo_contato : string; pe_codigo:string) : string;
var
   telefone,aplicativo,meio_contato,observacao,codigo_cidade:string;
begin
   with modulo_dados do
   begin
      // busca no mix conforme o código da pessoa
      sql:='SELECT * FROM fo_telefone_pessoa WHERE pe_codigo = '+quotedstr(pe_codigo);
      sql:=sql+' and pe_codigo <> '+quotedstr('37');
      sqlrun(sql,querysql4,banco_mix);
      if querysql4.RecordCount > 0 then
         begin
            querysql4.First;
            while not querysql4.Eof do
            begin
               telefone:=querysql4.fieldbyname('TPE_DDD').asstring+'-'+querysql4.fieldbyname('tpe_numero').asstring;
               if querysql4.FieldByName('tpe_obs').AsString <> '' then
                  observacao:=querysql4.fieldbyname('tpe_obs').asstring;
               if copy(querysql4.fieldbyname('tpe_numero').asstring,1,1) = '9' then
                  begin
                     aplicativo:='TELEFONE CELULAR';
                     meio_contato:='TELEFONE';
                  end
               else
                  begin
                     aplicativo := 'TELEFONE FIXO';
                     meio_contato:='TELEFONE';
                  end;
               // busca na agenda o número do telefone antes de fazer alguma coisa
               sql:='SELECT * FROM geoapolosag_comunicacao WHERE codigo_contato = '+codigo_contato;
               sql:=sql+' and identificacao_contato = '+quotedstr(telefone)+' and meio_contato = ';
               sql:=sql+quotedstr('TELEFONE');
               executaracao(sql,querysqlsql);
               if querysqlsql.RecordCount > 0 then
                  begin
                     sql:='UPDATE geoapolosag_comunicacao SET identificacao_contato = ';
                     sql:=sql+quotedstr(telefone)+', aplicativo = '+quotedstr(aplicativo);
                     sql:=sql+', meio_contato = '+quotedstr(meio_contato);
                     sql:=sql+' WHERE codigo_contato = '+codigo_contato+' and identificacao_contato = ';
                     sql:=sql+quotedstr(telefone);
                     executaracao(sql,querysqlsql3);
                     if querysqlsql3.RowsAffected > 0 then
                        begin
                        end;
                  end
               else
                  begin
                     sql:='INSERT INTO geoapolosag_comunicacao (codigo_contato, identificacao_contato, aplicativo, meio_contato)';
                     sql:=sql+' VALUES ('+codigo_contato+', '+chr(39)+telefone+chr(39)+', '+chr(39)+aplicativo+chr(39)+', '+chr(39)+meio_contato+chr(39)+');';
                     executaracao(sql,querysqlsql3);
                     if querysqlsql3.RowsAffected > 0 then
                        begin
                        end;
                  end;
               querysql4.Next;
            end;
         end;
      //
      sql:='SELECT pe_email FROM fo_pessoa WHERE pe_codigo = '+chr(39)+pe_codigo+chr(39);
      sqlrun(sql,querysql4,banco_mix);
      if querysql4.RecordCount > 0 then
         begin
            if querysql4.fieldbyname('pe_email').asstring <> '' then
               begin
                  sql:='SELECT * FROM geoapolosag_comunicacao WHERE aplicativo = '+chr(39)+'Outlook Express'+chr(39)+' and meio_contato = '+chr(39)+'Email'+chr(39)+' and identificacao_contato = '+chr(39)+querysql4.fieldbyname('pe_email').asstring+chr(39)+' and codigo_contato = '+CODIGO_contato;
                  executaracao(sql,querysqlsql);
                  if querysqlsql.RecordCount > 0 then
                     begin
                        sql:='UPDATE geoapolosag_comunicacao SET identificacao_contato = '+chr(39)+querysql4.fieldbyname('pe_email').asstring+chr(39);
                        sql:=sql+', aplicativo = '+chr(39)+aplicativo+chr(39)+', meio_contato = '+chr(39)+meio_contato+chr(39)+' WHERE codigo_contato = '+codigo_contato+' and identificacao_contato = '+chr(39)+querysql4.fieldbyname('pe_email').asstring+chr(39);
                        executaracao(sql,querysqlsql3);
                        if querysqlsql3.RowsAffected > 0 then
                     end
                  else
                     begin
                        sql:='INSERT INTO geoapolosag_comunicacao (codigo_contato, identificacao_contato, aplicativo, meio_contato)';
                        sql:=sql+' VALUES ('+codigo_contato+', '+chr(39)+querysql4.fieldbyname('pe_email').asstring+chr(39)+', '+chr(39)+'Outlook Express'+chr(39)+', '+chr(39)+'Email'+chr(39)+');';
                        executaracao(sql,querysqlsql3);
                        if querysqlsql3.RowsAffected > 0 then
                     end;
               end
         end;
      //
      sql:='select fp.pe_logradouro_end, fp.pe_numero_end, bb.ba_nome as Bairro, bsl.ci_nome, bsl.uf_sigla, fp.pe_cep';
      sql:=sql+' from fo_pessoa fp with(nolock), bs_bairro bb with(nolock), bs_localidade bsl with(nolock)';
      sql:=sql+' where fp.PE_BAIRRO_END = bb.ba_codigo';
      sql:=sql+' and   fp.PE_CIDADE_END = bsl.ci_codigo';
      sql:=sql+' and   fp.pe_codigo = '+quotedstr(pe_codigo);
      sqlrun(sql,querysql4,banco_mix);
      if querysql4.RecordCount > 0 then
         begin
            sql:='SELECT codigo_cidade FROM tab_cidades WHERE nome_cidade like ';
            sql:=sql+quotedstr(querysql4.fieldbyname('ci_nome').asstring);
            executaracao(sql,querysqlsql);
            if querysqlsql.RecordCount > 0 then
               codigo_cidade := querysqlsql.fieldbyname('codigo_cidade').asstring
            else
               codigo_cidade := '1';
            //
            sql:='SELECT codigo_contato FROM sag_endereco WHERE codigo_contato = ';
            sql:=sql+quotedstr(codigo_contato)+' and codigo_tipo = 1';
            executaracao(sql,querysqlsql);
            if querysqlsql.RecordCount > 0 then
               begin
                  sql:='UPDATE sag_endereco SET endereco = '+chr(39)+querysql4.fieldbyname('pe_logradouro_end').asstring+chr(39)+', codigo_cidade = '+codigo_cidade;
                  sql:=sql+', cep = '+quotedstr(querysql4.fieldbyname('pe_cep').AsString)+', pais = '+chr(39)+'BRASIL'+chr(39);
                  sql:=sql+', bairro = '+chr(39)+querysql4.fieldbyname('Bairro').asstring+chr(39)+' WHERE codigo_contato = '+codigo_contato;
                  executaracao(sql,querysqlsql3);
                  if querysqlsql3.RowsAffected > 0 then
               end
            else
               begin
                  sql:='INSERT INTO sag_endereco (codigo_tipo, endereco, codigo_cidade, cep, pais, codigo_contato, bairro) ';
                  sql:=sql+' VALUES (1'+', '+quotedstr(querysql4.fieldbyname('pe_logradouro_end').asstring)+', '+codigo_cidade+', ';
                  sql:=sql+quotedstr(querysql4.fieldbyname('pe_cep').asstring)+', '+chr(39)+'BRASIL'+chr(39)+', '+codigo_contato+', '+chr(39)+querysql4.fieldbyname('bairro').asstring+chr(39)+');';
                  executaracao(sql,querysqlsql3);
                  if querysqlsql3.RowsAffected > 0 then
               end;
            querysql4.Next;
         end
      else
         querysql4.Next;
   end;
end;

function Padr(s:string;n:integer):string;
//alinha uma string à direita
begin
   Result:=Format('%'+IntToStr(n)+'.'+IntToStr(n)+'s',[s]);
end;}

{create procedure Usergerar_codigo_ano(@empresa varchar(20), @tabela varchar(31), @ano varchar(4))
as
begin
     declare @X integer,
     @vcodini integer,
     @vcodfim integer,
     @CODIGO integer

     select @x=0
     select @vcodini=0
     select @vcodfim=0
     select @x = count(*) from config_cod_ano where empcod=@empresa
     and confcodanotabela=@tabela and confcodano = @ano
     if (@x<=0)
     begin
          --Registro_Nao_Existe
          --Anywhere e Adaptive
          --raiserror 50004
          --SqlServer
          raiserror (50004, -1, 16)
          return -1
     end
     else
     begin
          select @vcodini = confcodanoproxnum, @vcodfim = confcodanoultnum
          from config_cod_ano where empcod=@empresa and confcodanotabela=@tabela
          and confcodano = @ano

          select @vcodini=@vcodini+1
          if(@vcodfim<@vcodini)
          begin
               --Codigo final maior que inicial
               select @CODIGO=0
               --Anywhere e Adaptive
               --raiserror 50005
               --SqlServer
               raiserror (50005, -1, 16)
               return -1
          end
          else
          begin
               update config_cod_ano set confcodanoproxnum=@vcodini
               where empcod=@empresa and confcodanotabela=@tabela
               select @codigo=@vcodini
          end
     end
     return
end
;

create procedure USERCONTAB_GERAR_SEQ_RELAC
(
  @vEmpCod varchar(20),
  @vAno varchar(6),
  @vSequencia integer
)
as
begin
  /*

     Método para gerar a sequência de relacionamento dos lançamentos contábeis com o módulo de origem.
     Caso a sequência não esteja cadastrada para o ano corrente o cadastramento é realizado.
  */
  declare
    @vExiste smallint,
    @vTabela varchar(20)
  select @vTabela = 'LANC_CONTAB'
  /* Obter o ano corrente */
  select @vAno = cast(year(getdate()) as varchar)
  if datalength(@vAno) = 2
  begin
    select @vAno = '20' + @vAno
  end
  select @vExiste = 0
  select
    @vExiste = count(1)
  from Config_Cod_Ano
  where
    EmpCod = @vEmpCod and
    ConfCodAnoTabela = @vTabela and
    ConfCodAno = @vAno
  if @vExiste is null
  begin
    select @vExiste = 0
  end
  if (@vExiste = 0)
  begin
    insert into CONFIG_COD_ANO
    (
      EMPCOD, CONFCODANOTABELA,
      CONFCODANO, CONFCODANOMASCARA,
      CONFCODANOATIVA, CONFCODANOTAMANHO,
      CONFCODANOPROXNUM, CONFCODANOULTNUM,
      CONFCODANOFORMATO, CONFCODANOSEPARADOR,
      CONFCODANOORDEMCONCAT
    )
    values
    (
      @vEmpCod, @vTabela,
      @vAno, 'NNNNNNN',
      'Sim', 7,
      0, 9999999,
      'AAAA', '/',
      'Código,Separador,Ano'
    )
  end
  execute gerar_codigo_ano
    @vEmpCod,
    @vTabela,
    @vAno,
    @vSequencia
end
;

function MostraMemo(Dts: TDataSource; Dbg: TDBGrid; Fld: TField): Boolean;
var
  Frm: TForm;
  Ret: Boolean;
  Mem: TDBMemo;
begin
    Ret := False;
    if Dts.DataSet.RecordCount > 0 then
       if Dbg.SelectedField = Fld then
          begin
            Ret := True;
            Frm := TForm.Create(nil);
            try
              Frm.Width := 240;
              Frm.Height := 120;
              Frm.Top := controls.Mouse.CursorPos.Y;
              Frm.Left := controls.Mouse.CursorPos.X;
              Frm.BorderStyle := bsToolWindow;
              Frm.Caption := Fld.DisplayLabel;
              Mem := TDBMemo.Create(nil);
              try
                Mem.Parent := Frm;
                Mem.Align := alClient;
                Mem.DataSource := Dts;
                Mem.DataField := Fld.FieldName;
                Mem.ReadOnly := True;
                Mem.ScrollBars := ssVertical;
                Frm.ShowModal;
              finally
              Mem.Free;
              end;
            finally
            Frm.Free;
            end;
    end;
    Result := Ret;
end;}

function configura_grid(Modulo: string; Formulario: TForm; Usuario: string; NomeDoGrid: string; ObjetoGrid: TDBGrid; Consulta: TDataSource): string;  overload;
var
  qConfig: TFDQuery;
  ds: TDataSet;
  campo: string;
  col: TColumn;
  ListaCampos: TStringList;
  f: TField;
  novaPos: Integer;
begin
  Result := '';
  qConfig := TFDQuery.Create(nil);
  ListaCampos := TStringList.Create;
  try
    qConfig.Connection := Modulo_Dados.fdbanco;
    qConfig.SQL.Text :=
      'SELECT campo, posicao_atual, tamanho ' +
      'FROM USER_geoapolo_config_grid ' +
      'WHERE modulo = :mod AND usucod = :usu AND nome_grid = :grid ' +
      'ORDER BY posicao_atual ASC';
    qConfig.ParamByName('mod').AsString := Modulo;
    qConfig.ParamByName('usu').AsString := UpperCase(Usuario);
    qConfig.ParamByName('grid').AsString := NomeDoGrid;

    qConfig.Open;
    qConfig.FetchAll;

    if qConfig.IsEmpty then
      Exit;

    // Garante que o dataset está atribuído e ativo
    if (Consulta = nil) or (Consulta.DataSet = nil) then
    begin
      MessageDlg('Fonte de dados inválida ou dataset não atribuído.', mtError, [mbOK], 0);
      Exit;
    end;

    ds := Consulta.DataSet;
    if not ds.Active then
      ds.Open;

    // Desativa geração automática de colunas
//    ObjetoGrid.AutoGenerateColumns := False;

    // Primeiro, reordena os campos no dataset conforme a configuração
    qConfig.First;
    while not qConfig.Eof do
    begin
      ListaCampos.Add(qConfig.FieldByName('campo').AsString);
      qConfig.Next;
    end;

    for novaPos := 0 to ListaCampos.Count - 1 do
    begin
      f := ds.FindField(ListaCampos[novaPos]);
      if Assigned(f) then
        f.Index := novaPos; // <-- muda a ordem de exibição real
    end;

    // Agora recria as colunas na nova ordem
    ObjetoGrid.DataSource := nil;
    ObjetoGrid.Columns.Clear;

    qConfig.First;
    while not qConfig.Eof do
    begin
      campo := qConfig.FieldByName('campo').AsString;

      if ds.FindField(campo) <> nil then
      begin
        col := ObjetoGrid.Columns.Add;
        col.FieldName := campo;
        col.Width := qConfig.FieldByName('tamanho').AsInteger;
        col.Title.Caption := campo;
      end;

      qConfig.Next;
    end;

    // Reatribui o DataSource
    ObjetoGrid.DataSource := Consulta;

    // Força atualização visual
    ObjetoGrid.Repaint;

    Result := 'OK';
  except
    on E: Exception do
    begin
      MessageDlg('Erro ao configurar grid: ' + E.Message, mtError, [mbOK], 0);
      Result := 'ERRO';
    end;
  end;

  qConfig.Free;
  ListaCampos.Free;
end;

function carrega_config(modulo : string; formulario:tform; combocampo:TComboBox;
                        comboordem:TComboBox; rdg1:TRadioButton; rdg2:TRadioButton) : string;
var
   i:integer;
begin
   with modulo_dados, formulario do
   begin
     sql:='SELECT * FROM USER_geoapolo_configtelamovbanc WHERE modulo = :modulo';
     fdquerysql10.Close;
     fdquerysql10.SQL.Clear;
     fdquerysql10.SQL.Text := sql;
     fdquerysql10.ParamByName('modulo').AsString := modulo;
     if executaracao(fdquerysql10, fdbanco, true, dtsfdquerysql10) then
        begin
           buscanacombo(fdquerysql10.fieldbyname('campobusca').AsString,formulario,combocampo);
           buscanacombo(fdquerysql10.fieldbyname('campo_ordem').AsString,formulario,comboordem);
           if fdquerysql10.FieldByName('ordem_campo').AsString = 'A' then
              begin
                 rdg1.Checked := true;
                 rdg2.Checked := false;
              end
           else if fdquerysql10.FieldByName('ordem_campo').asstring = 'D' then
              begin
                 rdg2.Checked := true;
                 rdg1.Checked := false;
              end;
           combocampo.Refresh; comboordem.Refresh;
        end;
   end;
end;

function grava_config_telabusca(modulo : string; campobusca: string; campo_ordem: string; ordemcampo : string; formulario : tform) : string;
begin
   with modulo_dados, formulario do
   begin
      if campobusca = '' then
         begin
            messagedlg('NÃO FOI DEFINIDO UM CAMPO PADRÃO PARA BUSCA !!!',mterror,[mbok],0);
            exit;
         end;
      //
      if campo_ordem = '' then
         begin
            messagedlg('NÃO FOI DEFINIDO UM CAMPO PADRÃO PARA ORDENAÇÃO DOS DADOS !!!',mterror,[mbok],0);
            exit;
         end;
      //
      //ROTINAS GRAVAÇÃO DE PARÂMETROS DO OBJETO DE BUSCA
      fdquerysql23.Close;
      fdquerysql23.SQL.Clear;
      fdquerysql23.SQL.Add('SELECT *');
      fdquerysql23.SQL.Add('FROM USER_geoapolo_configtelamovbanc');
      fdquerysql23.SQL.Add('WHERE modulo = :modulo');
      fdquerysql23.ParamByName('modulo').AsString := modulo;
      if executaracao(fdquerysql23,fdbanco,true,dtsfdquerysql23) then
         begin
            fdquerysql3.close;
            fdquerysql3.sql.clear;
            fdquerysql3.SQL.Add('UPDATE USER_geoapolo_configtelamovbanc SET modulo = :modulo,');
            fdquerysql3.SQL.Add('    campobusca = :campobusca, campo_ordem = :campo_ordem,');
            fdquerysql3.SQL.Add('    ordem_campo = :ordemcampo WHERE modulo = :modulo_cond');
            fdquerysql3.ParamByName('modulo').AsString := modulo;
            fdquerysql3.ParamByName('campobusca').AsString := campobusca;
            fdquerysql3.ParamByName('campo_ordem').AsString := campo_ordem;
            fdquerysql3.ParamByName('ordemcampo').AsString := ordemcampo;
            fdquerysql3.ParamByName('modulo_cond').AsString := modulo;
            if executaracao(fdquerysql3, fdbanco, true,dtsfdquerysql3) then
               begin
               end;
         end
      else
         begin
            sql:='INSERT INTO USER_geoapolo_configtelamovbanc (usucod, modulo, campobusca, campo_ordem, ordem_campo)';
            sql:=sql+' VALUES ('+quotedstr(frmlogon.nomeusuario)+', '+quotedstr(modulo)+', '+quotedstr(campobusca)+', '+quotedstr(campo_ordem)+', '+quotedstr(ordemcampo)+');';
            fdquerysql3.close;
            fdquerysql3.sql.clear;
            fdquerysql3.SQL.Add('INSERT INTO USER_geoapolo_configtelamovbanc (usucod, modulo, campobusca, campo_ordem, ordem_campo)');
            fdquerysql3.SQL.Add('VALUES (:usucod, :modulo, :campobusca, :campo_ordem, :ordemcampo)');
            fdquerysql3.ParamByName('usucod').AsString := frmlogon.nomeusuario;
            fdquerysql3.ParamByName('modulo').AsString := modulo;
            fdquerysql3.ParamByName('campobusca').AsString := campobusca;
            fdquerysql3.ParamByName('campo_ordem').AsString := campo_ordem;
            fdquerysql3.ParamByName('ordemcampo').AsString := ordemcampo;
            if executaracao(fdquerysql3, fdbanco, true,dtsfdquerysql3) then
               begin
               end;
         end;
   end;
end;

procedure Memoformat(RichEdit: TRichEdit; TextCol, TagCol, DopCol: TColor);
var
  i, iDop: Integer;
  s: string;
  Col: TColor;
  isTag, isDop: Boolean;
begin
  iDop := 0;
  isDop := False;
  isTag := False;
  Col := TextCol;
  RichEdit.SetFocus;
  for i := 0 to Length(RichEdit.Text) do 
  begin
    RichEdit.SelStart := i;
    RichEdit.SelLength := 1;
    s := RichEdit.SelText; 
    if (s = '<') or (s = '{') then 
      isTag := True;
    if isTag then
      if (s = '"') then
        if not isDop then 
        begin
          iDop := 1;
          isDop := True;
        end
        else 
          isDop := False;
      if isTag then
        if isDop then 
        begin
          if iDop <> 1 then Col := DopCol;
        end
        else 
          Col := TagCol
        else 
          Col := TextCol;
      RichEdit.SelAttributes.Color := Col;
      iDop := 0;
      if (s = '>') or (s = '') then
        isTag := False;
    end;
    RichEdit.SelLength := 0;
end;

function CalcularIdade(const DataNasc: TDate): string;
var
  Anos, Meses, Dias: Integer;
  DataHoje, Ajustada: TDate;
begin
  DataHoje := Date;

  // calcula diferença básica
  Anos := YearsBetween(DataHoje, DataNasc);

  // aniversário ainda não chegou este ano?
  Ajustada := IncYear(DataNasc, Anos);
  if Ajustada > DataHoje then
  begin
    Dec(Anos);
    Ajustada := IncYear(DataNasc, Anos);
  end;

  Meses := MonthsBetween(DataHoje, Ajustada);
  Ajustada := IncMonth(Ajustada, Meses);

  Dias := DaysBetween(DataHoje, Ajustada);

  // formatação
  Result := '';

  if Anos > 0 then
  begin
    if Anos = 1 then
      Result := '1 ano'
    else
      Result := Format('%d anos', [Anos]);
  end;

  if Meses > 0 then
  begin
    if Result <> '' then Result := Result + ', ';
    if Meses = 1 then
      Result := Result + '1 mês'
    else
      Result := Result + Format('%d meses', [Meses]);
  end;

  if Dias > 0 then
  begin
    if Result <> '' then Result := Result + ' e ';
    if Dias = 1 then
      Result := Result + '1 dia'
    else
      Result := Result + Format('%d dias', [Dias]);
  end;

  if Result = '' then
    Result := '0';
end;

function Bissexto(AYear: Integer): Boolean;
begin
  Result := (AYear mod 4 = 0) and ((AYear mod 100 <> 0) or (AYear mod 400 = 0));
end;

function DiasDoMes(AYear, AMonth: Integer): Integer;
const
  DaysInMonth: array[1..12] of Integer = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31);
begin
  Result := DaysInMonth[AMonth];
  if (AMonth = 2) and Bissexto(AYear) then
     Inc(Result);
end;

function Dias(Data : TDate) : String;
begin
  Result := FloatToStr(Date - Data);
end;

function Idade(Nasc : TDate) : String;
Var
  AuxIdade, Meses, IdadeReal : String;
  MesesFloat : Real;
  IdadeInc : Integer;
begin
  AuxIdade := Format('%0.2f', [(Date - Nasc) / 365.6]);
  Meses := FloatToStr(Frac(StrToFloat(AuxIdade)));

  if AuxIdade = '0' then
  begin
    Result := '0,0';
    Exit;
  end;
  //
  showmessage('Meses:'+Meses);
  if ((Meses <> '') and (Meses[1] = '-')) then
     begin
       Meses := buscatroca(Meses,',','.');
       showmessage('Meses Ajustados:'+Meses);
       Meses := FloatToStr(StrToFloat(Meses) * -1);
     end;
  //
  Delete(Meses, 1, 2);
  //
  if Length(Meses) = 1 then
     Meses := Meses + '0';
  //
  if (Meses <> '0') And (Meses <> '') then
     MesesFloat := Round(((365.6 * StrToInt(Meses)) / 100) / 30)
  else
     MesesFloat := 0;
  //
  if MesesFloat <> 12 then
     IdadeReal := IntToStr(Trunc(StrToFloat(AuxIdade))) + ',' + FloatToStr(MesesFloat)
  else
     begin
        IdadeInc := Trunc(StrToFloat(AuxIdade));
        Inc(IdadeInc);
        IdadeReal := IntToStr(IdadeInc) + ',' + '0';
     end;
  //IdadeReal := buscatroca(IdadeReal,',','.');
  Result := IdadeReal;
end;

{function eject : string;
begin
   with frmemitecontas do
      writeln(arqtexto,chr(12));
end;

function cabec_principal : string;
var
   empresa,titulo:string;
begin
   with frmemitecontas do
   begin
      empresa:= 'Emissao: '+datetostr(date)+space(49-length('Emissao: '+datetostr(date)))+'FUNDACAO NOSSA SENHORA APARECIDA'+space(40)+'Pag..: '+inttostr(wpag);
      imprime(00,01,linhaatual,arqtexto,empresa);
      titulo:='RELATORIO DE CONTROLE DO PABX';
      imprime(01,53,linhaatual,arqtexto,trim(titulo));
      wlin:=2;
   end;
end;

function subcab(tipo : string) : string;
begin
   with modulo_dados do
   begin
       with frmemitecontas do
       begin
           if (rdgcontas.ItemIndex = 0) or (rdgcontas.itemindex = 1) then
              begin
{                 imprime(wlin,53,linhaatual,arqtexto,'FICHA INDIVIDUAL DE LIGACOES');
                 inc(wlin);
                 wvaria:='Ligacao de..: '+copy(tiracento(querysqlsql2.fieldbyname('nome').asstring),1,35)+' - '+querysqlsql2.fieldbyname('codigo_usuario').AsString+space(40)+'Periodo: '+mskperinicial.text+' a '+mskperfinal.text;
                 imprime(wlin,01,linhaatual,arqtexto,wvaria);
                 inc(wlin);
                 imprime(wlin,01,linhaatual,arqtexto,'Departamento: '+tiracento(querysqlsql2.fieldbyname('descricao').asstring));
                 inc(wlin);
                 imprime(wlin,00,linhaatual,arqtexto,replicate('_',135));
                 inc(wlin);
                 imprime(wlin,02,linhaatual,arqtexto,'Data'+space(6)+'Ramal Utilizado'+space(15)+'Numero Discado '+space(5)+'Horario'+space(10)+'Valor'+space(10)+'Natureza Ligacao');
                 inc(wlin);
                 imprime(wlin,00,linhaatual,arqtexto,replicate('_',135));
              end;
      end;
   end;
end;

function rodape : string;
begin
   with modulo_dados do
   begin
      with frmemitecontas do
      begin
//         sql:='SELECT Sum(sclpabx_ligacoes.valor) AS TotalConta FROM sclpabx_ligacoes WHERE (((sclpabx_ligacoes.codigo_usuario)= '+''''+codigousuario+''''+') AND codigo_classe = 1 AND flagimpresso <> '+''''+'I'+''''+');';
  //       executaracao(sql,querysqlsql);
         wlin:=wlin+1;
         imprime(wlin,00,linhaatual,arqtexto,replicate('_',135));
         wlin:=wlin+1;
         imprime(wlin,00,linhaatual,arqtexto,'Valor Total da Conta: '+formatfloat('R$ ###,###,##0.00',frmemitecontas.soma)+space(10)+'Concordo e Autorizo desconto em Folha de Pagto:_______________________');
      end;
   end;
end;}

function linkweb(const url : string) : string;
var
   buffer: String;
begin
   buffer := 'http://' + url;
   ShellExecute(Application.Handle, nil, PChar(buffer), nil, nil, SW_SHOWNORMAL);
end;

{
//---------------------------------------------------------------
// CharPrinter.pas - Tratamento de impressoras em modo caractere
//---------------------------------------------------------------
// Autor : Fernando Allen Marques de Oliveira
//         Dezembro de 2000.
//
// TPrinterStream : classe derivada de TStream para enviar dados
//                  diretamente para o spool da impressora sele-
//                  cionada.
//
// TCharPrinter : Classe base para implementação de impressoras.
//                não inclui personalização para nenhuma impres-
//                sora específica, envia dados sem formatação.
//
// Modificado em 20/05/2003 - Compatibilização com diretivas padrão do Delphi 7

unit CharPrinter;

interface

uses
  Windows, Messages, SysUtils, Classes, Graphics, Controls, Forms, Dialogs,
  Printers, WinSpool;

type
  { Stream para enviar caracteres à impressora atual
  TPrinterStream = class (TStream)
  private
    fPrinter : TPrinter;
    fHandle  : THandle;
    fTitle   : String;
    procedure  CreateHandle;
    procedure  FreeHandle;
  public
    constructor Create (aPrinter: TPrinter; aTitle : String);
    destructor  Destroy; override;
    function    Write (const Buffer; Count : Longint): Longint; override;
    property    Handle : THandle read fHandle;
  end;

  TCharPrinter = class(TObject)
  private
    { Private declarations
    fStream   : TStream;
  protected
    { Protected declarations
  public
    { Public declarations
 published
    { Published declarations
    constructor Create; virtual;
    destructor  Destroy; override;
    procedure   OpenDoc (aTitle : String); virtual;
    procedure   SendData (aData : String);
    procedure   CloseDoc; virtual;
    property    PrintStream : TStream read fStream;
  end;

  // Definições para TAdvancedPrinter //

  TprtLang = (lngEPFX,lngESCP2,lngHPPCL);
  TprtFontSize = (pfs5cpi,pfs10cpi,pfs12cpi,pfs17cpi,pfs20cpi);
  TprtTextStyle = (psBold,psItalic,psUnderline);
  TprtTextStyles = set of TprtTextStyle;

  TAdvancedPrinter = class (TCharPrinter)
  private
    fLang : TprtLang;
    fFontSize : TprtFontSize;
    fTextStyle : TprtTextStyles;
    procedure SetLang (lang : TprtLang);
    function  GetLang : TprtLang;
    procedure SetFontSize (size : TprtFontSize);
    function  GetFontSize : TprtFontSize;
    procedure SetTextStyle (styles : TprtTextStyles);
    function  GetTextStyle : TprtTextStyles;
    procedure UpdateStyle;
    procedure Initialize;
    function  Convert (s : string) : string;
  published
    constructor Create; override;
    procedure   OpenDoc (aTitle : String); override;
    property Language : TprtLang read GetLang write SetLang;
    property FontSize : TprtFontSize read GetFontSize write SetFontSize;
    property TextStyle : TprtTextStyles read GetTextStyle write SetTextStyle;
  public
    procedure CR;
    procedure LF; overload;
    procedure LF (Lines : integer); overload;
    procedure CRLF;
    procedure FF;
    procedure Write (txt : string);
    procedure WriteLeft  (txt, fill : string; size : integer);
    procedure WriteRight (txt, fill : string; size : integer);
    procedure WriteCenter(txt, fill : string; size : integer);
    procedure WriteRepeat(txt : string; quant : integer);
  end;

procedure Register;

implementation

procedure Register;
begin
{  RegisterComponents('AeF', [TCharPrinter]);
end;

{ =================== }
{ =  TPrinterStream = }
{ ===================

constructor TPrinterStream.Create (aPrinter : TPrinter; aTitle : String);
begin
  inherited Create;
  fPrinter := aPrinter;
  fTitle   := aTitle;
  CreateHandle;
end;

destructor TPrinterStream.Destroy;
begin
  FreeHandle;
  inherited;
end;

procedure TPrinterStream.FreeHandle;
begin
  if fHandle <> 0 then
  begin
    EndPagePrinter (fHandle);
    EndDocPrinter  (fHandle);
    ClosePrinter   (Handle);
    fHandle := 0;
  end;
end;

procedure TPrinterStream.CreateHandle;
type
  DOC_INFO_1 = packed record
    pDocName    : PChar;
    pOutputFile : PChar;
    pDataType   : PChar;
  end;
var
  aDevice,
  aDriver,
  aPort    : array[0..255] of Char;
  aMode    : Cardinal;
  DocInfo : DOC_INFO_1;
begin
  DocInfo.pDocName := nil;
  DocInfo.pOutputFile := nil;
  DocInfo.pDataType := 'RAW';

  FreeHandle;
  if fHandle = 0 then
  begin
    fPrinter.GetPrinter (aDevice, aDriver, aPort, aMode);
    if OpenPrinter (aDevice, fHandle, nil)
    then begin
      DocInfo.pDocName := PChar(fTitle);
      if StartDocPrinter (fHandle, 1, @DocInfo) = 0
      then begin
        ClosePrinter (fHandle);
        fHandle := 0;
      end else
      if not StartPagePrinter (fHandle)
      then begin
        EndDocPrinter (fHandle);
        ClosePrinter  (fHandle);
        fHandle := 0;
      end;
    end;
  end;
end;

function TPrinterStream.Write (const Buffer; Count : Longint) : Longint;
var
  Bytes : Cardinal;
begin
  WritePrinter (Handle, @Buffer, Count, Bytes);
  Result := Bytes;
end;

{ ================= }
{ =  TCharPrinter = }
{ =================

constructor TCharPrinter.Create;
begin
  inherited Create;
  fStream := nil;
end;

destructor TCharPrinter.Destroy;
begin
  if fStream <> nil
  then fStream.Free;
  inherited;
end;

procedure TCharPrinter.OpenDoc (aTitle : String);
begin
  if fStream = nil
  then fStream := TPrinterStream.Create (Printer, aTitle);
end;

procedure   TCharPrinter.CloseDoc;
begin
  if fStream <> nil
  then begin
    fStream.Free;
    fStream := nil;
  end;
end;

procedure   TCharPrinter.SendData (aData : String);
var
  Data : array[0..255] of char;
  cnt  : integer;
begin
  for cnt := 0 to length(aData) - 1
  do Data[cnt] := aData[cnt+1];

  fStream.Write (Data, length(aData));
end;

{ ===================== }
{ =  TAdvancedPrinter = }
{ =====================

procedure TAdvancedPrinter.SetLang (lang : TprtLang);
begin
  fLang := lang;
end;

function  TAdvancedPrinter.GetLang : TprtLang;
begin
  result := fLang;
end;

procedure TAdvancedPrinter.SetFontSize (size : TprtFontSize);
begin
  fFontSize := size;
  UpdateStyle;
end;

function  TAdvancedPrinter.GetFontSize : TprtFontSize;
begin
  result := fFontSize;
  UpdateStyle;
end;

procedure TAdvancedPrinter.SetTextStyle (styles : TprtTextStyles);
begin
  fTextStyle := styles;
  UpdateStyle;
end;

function  TAdvancedPrinter.GetTextStyle : TprtTextStyles;
begin
  result := fTextStyle;
  UpdateStyle;
end;

procedure TAdvancedPrinter.UpdateStyle;
var
  cmd : string;
  i : byte;
begin
  cmd := '';
  case fLang of
    lngESCP2, lngEPFX : begin
      i := 0;
      Case fFontSize of
        pfs5cpi  : i := 32;
        pfs10cpi : i := 0;
        pfs12cpi : i := 1;
        pfs17cpi : i := 4;
        pfs20cpi : i := 5;
      end;
      if psBold in fTextStyle then i := i + 8;
      if psItalic in fTextStyle then i := i + 64;
      if psUnderline in fTextStyle then i := i + 128;
      cmd := #27'!'+chr(i);
    end;
    lngHPPCL : begin
      Case fFontSize of
        pfs5cpi  : cmd := #27'(s5H';
        pfs10cpi : cmd := #27'(s10H';
        pfs12cpi : cmd := #27'(s12H';
        pfs17cpi : cmd := #27'(s17H';
        pfs20cpi : cmd := #27'(s20H';
      end;
      if psBold in fTextStyle
        then cmd := cmd + #27'(s3B'
        else cmd := cmd + #27'(s0B';
      if psItalic in fTextStyle
        then cmd := cmd + #27'(s1S'
        else cmd := cmd + #27'(s0S';
      if psUnderline in fTextStyle
        then cmd := cmd + #27'&d0D'
        else cmd := cmd + #27'&d@';
    end;
  end;
  SendData(cmd);
end;

procedure TAdvancedPrinter.Initialize;
begin
  case fLang of
    lngEPFX  : SendData (#27'@'#27'2'#27'P'#18);
    lngESCP2 : SendData (#27'@'#27'O'#27'2'#27'C0'#11#27'!'#0);
    lngHPPCL : SendData (#27'E'#27'&l2A'#27'&l0O'#27'&l6D'#27'(s4099T'#27'(s0P'#27'&k0S'#27'(s0S');
  end;
end;

function  TAdvancedPrinter.Convert (s : string) : string;
const
  accent   : string = 'ãàáäâèéëêìíïîõòóöôùúüûçÃÀÁÄÂÈÉËÊÌÍÏÎÕÒÓÖÔÙÚÜÛÇ';
  noaccent : string = 'aaaaaeeeeiiiiooooouuuucAAAAAEEEEIIIIOOOOOUUUUC';
var
  i : integer;
begin
  for i := 1 to length(accent) do
    While Pos(accent[i],s) > 0 do s[Pos(accent[i],s)] := noaccent[i];
  result := s;
end;

constructor TAdvancedPrinter.Create;
begin
  inherited Create;
  fLang := lngESCP2;
  fFontSize := pfs10cpi;
  fTextStyle := [];
end;

procedure   TAdvancedPrinter.OpenDoc (aTitle : String);
begin
  inherited OpenDoc (aTitle);
  Initialize;
end;

procedure TAdvancedPrinter.CR;
begin
  SendData (#13);
end;

procedure TAdvancedPrinter.LF;
begin
  SendData (#10);
end;

procedure TAdvancedPrinter.LF (Lines : integer);
begin
  while lines > 0 do begin
    SendData(#10); dec(lines);
  end;
end;

procedure TAdvancedPrinter.CRLF;
begin
  SendData (#13#10);
end;

procedure TAdvancedPrinter.FF;
begin
  SendData(#12);
end;

procedure TAdvancedPrinter.Write (txt : string);
begin
  txt := Convert (txt);
  SendData (txt);
end;

procedure TAdvancedPrinter.WriteLeft  (txt, fill : string; size : integer);
begin
  txt := Convert(txt);
  while Length(txt) < size do txt := txt + fill;
  SendData (Copy(txt,1,size));
end;

procedure TAdvancedPrinter.WriteRight (txt, fill : string; size : integer);
begin
  txt := Convert(txt);
  while Length(txt) < size do txt := fill + txt;
  SendData (Copy(txt,Length(txt)-size+1,size));
end;

procedure TAdvancedPrinter.WriteCenter(txt, fill : string; size : integer);
begin
  txt := Convert(txt);
  while Length(txt) < size do txt := fill + txt + fill;
  SendData (Copy(txt,(Length(txt)-size) div 2 + 1,size));
end;

procedure TAdvancedPrinter.WriteRepeat(txt : string; quant : integer);
var
  s : string;
begin
  s := '';
  txt := Convert(txt);
  while quant > 0 do begin
    s := s + txt;
    dec(quant);
  end;
  SendData (s);
end;


end.
}

function MemoryStatus: string;
var
MS:TMemoryStatus;
 FreeRes, PhysMem: string;
begin
   GlobalMemoryStatus(MS);
   PhysMem :=
          FormatFloat('Memória física disponível para o Windows: #,###" KB"',
          MS.dwTotalPhys / 1024);
   FreeRes := Format('( %d %% em uso )', [MS.dwMemoryLoad]);
   Result := PhysMem + ' - ' + FreeRes;
end;

function DifHora(Inicio,Fim : String):String;
{Retorna a diferença entre duas horas}
var
  FIni,FFim : TDateTime;
  informado,retorno:string;
begin
Fini := StrTotime(Inicio);
FFim := StrToTime(Fim);
If (Inicio > Fim) then
  begin
  Result := TimeToStr((StrTotime('23:59:59')-Fini)+FFim)
  end
else
  begin
  //Result := TimeToStr(FFim-Fini);
  informado:= TimeToStr((StrTotime('23:59:59') + StrToTime('00:00:01') -Fini)+FFim);
     retorno:=copy(informado,1,2)+copy(informado,4,2)+copy(informado,7,2);
     result:=retorno;
  end;
end;

{function buscatipolanccod(tipolanccod:string) : string;
begin
   with modulo_dados do
   begin
      if tipolanccod <> '' then
         begin
            sql:='SELECT tipolancnome FROM tipo_lanc WHERE tipolanccod = '+chr(39)+tipolanccod+chr(39);
            executaracao(sql,querysql);
            if querysql.RecordCount > 0 then
               begin
                  result:=querysql.fieldbyname('tipolancnome').AsString;
               end
            else
               result:='';
         end;
   end;
end;

function buscanomedaclasse(classerecdespcodestr : string) : string;
begin
   with modulo_dados do
   begin
      sql:='SELECT classerecdespnome FROM classe_rec_desp WHERE classerecdespcodestr = '+chr(39)+classerecdespcodestr+chr(39);
      executaracao(sql,querysql);
      if querysql.recordcount > 0 then
         begin
            result:=querysql.fieldbyname('classerecdespnome').asstring;
         end
      else
         result:= '';
   end;
end;

function buscanomecentrocontrole(cctrlcodestr:string) : string;
begin
   with modulo_dados do
   begin
      sql:='SELECT cctrlnome FROM centro_ctrl WHERE cctrlcodestr = '+chr(39)+cctrlcodestr+chr(39);
      executaracao(sql,querysql);
      if querysql.RecordCount > 0 then
         begin
            result:=querysql.fieldbyname('cctrlnome').AsString;
         end
      else
         result:='';
   end;
end;  }

function SEMCHAR(texto: string): string; //stdcall;
{Função que serve para nao aceitar caracteres especiais tipo !@#$%^&*()}
const
   NaoChar = '~`!@"#"$%^&*()+=|\<>,.?/æ';
var
   x: Integer;
begin
   for x := 1 to Length(texto) do
   begin
      if Pos(texto[x], NaoChar) <> 0 then
         delete(texto,x,1)
      else
         result := result + texto[x];
   end;
end;

{function apaga_senha_setup_maquina : string;
begin
  asm
    mov ax,2eh
    out 70h,ax
    mov ax,2fh
    out 71h,ax
  end;
end;   }

{function fnAbreQuery( Q: TQuery ): boolean;
begin
  if not Q.Active then begin

    if not Q.Prepared then
       Q.Prepare;

    Q.Open;
    result := True;

  end else
     result := False;
end; }


function MacAddress: string;
var
  Lib: Cardinal;
  Func: function(GUID: PGUID): Longint; stdcall;
  GUID1, GUID2: TGUID;
begin
  Result := '';
  Lib := LoadLibrary('rpcrt4.dll');
  if Lib > 0 then
  begin
    @Func := GetProcAddress(Lib, 'UuidCreateSequential');
    if Assigned(Func) then
    begin
      if (Func(@GUID1) = 0) and
         (Func(@GUID2) = 0) and
         (GUID1.D4[2] = GUID2.D4[2]) and
         (GUID1.D4[3] = GUID2.D4[3]) and
         (GUID1.D4[4] = GUID2.D4[4]) and
         (GUID1.D4[5] = GUID2.D4[5]) and
         (GUID1.D4[6] = GUID2.D4[6]) and
         (GUID1.D4[7] = GUID2.D4[7]) then
      begin
        Result :=
          IntToHex(GUID1.D4[2], 2) + '-' +
          IntToHex(GUID1.D4[3], 2) + '-' +
          IntToHex(GUID1.D4[4], 2) + '-' +
          IntToHex(GUID1.D4[5], 2) + '-' +
          IntToHex(GUID1.D4[6], 2) + '-' +
          IntToHex(GUID1.D4[7], 2);
      end;
    end;
  end;
end;


function FixDBGridColumnsWidth(const Grid: TDBGrid):string;
var Tamanhos : array of Integer;
    nI, Tam  : Integer;
    DataSet  : TDataSet;
begin
  SetLength(Tamanhos, Grid.Columns.Count);
  for nI := 0 to Grid.Columns.Count - 1 do
      Tamanhos[nI] := Grid.Canvas.TextWidth(Grid.Columns[nI].Title.Caption);

  DataSet := Grid.DataSource.DataSet;
  DataSet.DisableControls;

  try
    while not DataSet.Eof do
    begin
       for nI := 0 to Grid.Columns.Count - 1 do
       begin
          Tam := Grid.Canvas.TextWidth(DataSet.Fields[nI].Text);
          if Tam > Tamanhos[nI] then
             Tamanhos[nI] := Tam;
      end;
          DataSet.Next;
    end;

    for nI := 0 to Grid.Columns.Count - 1 do begin
        Grid.Columns[nI].Width := Tamanhos[nI] + 5;

        {checka espaço para colocar a imagem de ordenação na coluna}
        if Grid.Columns.Items[nI].Width < (Grid.Canvas.TextWidth(Grid.Columns[nI].Title.Caption)+ 5) then
           Grid.Columns[nI].Width := Grid.Columns[nI].Width + 5;
    end;
    DataSet.First;
  finally
    DataSet.EnableControls;
  end;
end;

{function formatarhtml(RichEdit: TRichEdit; TextCol, TagCol, DopCol: TColor);
var
  i, iDop: Integer;
  s: string;
  Col: TColor;
  isTag, isDop: Boolean;
begin
  iDop := 0;
  isDop := False;
  isTag := False;
  Col := TextCol;
  RichEdit.SetFocus;
  for i := 0 to Length(RichEdit.Text) do
  begin
    RichEdit.SelStart := i;
    RichEdit.SelLength := 1;
    s := RichEdit.SelText;
    if (s = '<') or (s = '{') then
      isTag := True;
    if isTag then
       if (s = '"') then
          if not isDop then
            begin
              iDop := 1;
              isDop := True;
            end
          else
             isDop := False;
      if isTag then
        if isDop then
        begin
          if iDop <> 1 then
             Col := DopCol;
        end
        else
          Col := TagCol
        else
          Col := TextCol;
      RichEdit.SelAttributes.Color := Col;
      iDop := 0;
      if (s = '>') or (s = ') then
        isTag := False;
    end;
    RichEdit.SelLength := 0;
end;}

function limpahtml(RichEdit: TRichEdit; html:string) : string;
var
   i,posini,posfim:integer;
   s:string;
begin
  RichEdit.SetFocus;
  posini:=0;
  posfim:= richedit.FindText(html,posini,length(html),[stWholeWord]);
  while posfim >= 0 do
  begin
      richedit.SetFocus;
      richedit.SelStart:=posfim;
      richedit.SelLength:=Length(html);
      posini:=posfim+length(html)+1;
      posfim:= richedit.FindText(html,posini,length(html),[stWholeWord]);
        if posfim > 0  then
          begin
             richedit.CutToClipboard
          end;
      end;
  richedit.Refresh;
  result:=richedit.Lines.Text;
end;

function RemoveTags(const s: string): string;
var
   i: Integer;
   InTag: Boolean;
begin
     Result := '';
     InTag := False;
     for i := 1 to Length(s) do
     begin
          if s[i] = '<' then
             inTag := True
          else if s[i] = '>' then
               inTag := False
          else if not InTag then
               Result := Result + s[i];
     end;
end;

function FormEstaCriado(AClass: TClass): Boolean;
var
  I: Integer;
begin
  Result := False;
  for I := 0 to Screen.FormCount -1 do
  begin
    if Screen.Forms[I] is AClass then
    begin
      Result := True;
      Break;
    end;
  end;
end;

{function FormEstaCriado(AClass: TQuickRep): Boolean; overload;
var
  I: Integer;
begin
end;
        }
function integraapolo : string;
begin
   with modulo_dados do
   begin
      sql:='SELECT integra_base_apolomix FROM USER_geoapolo_configuracoes';
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := sql;
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         result:=fdquerysql.fieldbyname('integra_base_apolomix').asstring
       else
          begin
             result:='N';
          end;
   end;
end;

function EmailTipoMIME(TipoMIME: Integer): String;
begin
  case TipoMIME of
    0  : result := 'text/plain';
    1  : result := 'text/html';
    2  : result := 'text/richtext';
    3  : result := 'text/x-aiff';
    4  : result := 'audio/basic';
    5  : result := 'audio/wav';
    6  : result := 'image/gif';
    7  : result := 'image/jpeg';
    8  : result := 'image/pjpeg';
    9  : result :=  'image/tiff';
    10 : result := 'image/x-png';
    11 : result := 'image/x-xbitmap';
    12 : result := 'image/bmp';
    13 : result := 'image/x-jg';
    14 : result := 'image/x-emf';
    15 : result := 'image/x-wmf';
    16 : result := 'video/avi';
    17 : result := 'video/mpeg';
    18 : result := 'application/postscript';
    19 : result := 'application/base64';
    20 : result := 'application/macbinhex40';
    21 : result := 'application/pdf';
    22 : result := 'application/x-compressed';
    23 : result := 'application/x-zip-compressed';
    24 : result := 'application/x-gzip-compressed';
    25 : result := 'application/java';
    26 : result := 'application/x-msdownload';
    27 : result := 'application/octet-stream';
    28 : result := 'multipart/mixed';
    29 : result := 'multipart/relative';
    30 : result := 'multipart/digest';
    31 : result := 'multipart/alternative';
    32 : result := 'multipart/related';
    33 : result := 'multipart/report';
    34 : result := 'multipart/signed';
    35 : result := 'multipart/encrypted';
  end;
end;

function EnviarEmail2(Dominio, Porta, Usuario, Senha, DeNome, DeEmail,
                            Para, Assunto, Corpo: string;
                            CorpoMIME, AnexoMIME: integer;
                            AutoResposta: Boolean): Boolean;
Var
  I         : Integer;
  IdCorpo   : TIdText;
  IdSmtp    : TIdSMTP;
  IdMessage : TIdMessage;
  IdAnexo   : TIdAttachmentFile;
  Idssl1    : TIdSSLIOHandlerSocketOpenSSL;
  //IdSSl1     : TIdSSLIOHandlerSocketOpenSSL;
begin
                    //Função enviar e-mail
try
  IdMessage := TIdMessage.Create(nil);
try
 // carrega_mail_config;
  //Cria a Estrutura da Mensagem
  IdMessage.Clear;
  IdMessage.IsEncoded := True;
  IdMessage.AttachmentEncoding := 'MIME';
  IdMessage.Encoding := meMIME; //meDefault
  IdMessage.ConvertPreamble := True;
  IdMessage.Priority := mpNormal;
  //IdMessage.ContentType := 'multipart/mixed';
  IdMessage.ContentType := 'text/html';
  IdMessage.CharSet := 'ISO-8859-1';
  IdMessage.Date := Now;
  //Define o Remetente e Destinatário
  IdMessage.From.Address := DeEmail;
  IdMessage.From.Text := DeNome + '';
  IdMessage.ReplyTo.EMailAddresses := DeEmail;
  IdMessage.Recipients.EMailAddresses := Trim(Para);
  if AutoResposta then begin
   IdMessage.ReceiptRecipient.Text := DeEmail;
  end;
  IdMessage.Subject := Trim( Assunto );
  //Adiciona o CORPO da Mensagem
  IdCorpo := TIdText.Create(IdMessage.MessageParts,nil);
  IdCorpo.ContentType := EmailTipoMIME(CorpoMIME);
  IdCorpo.ContentDescription := 'multipart-1';
  IdCorpo.CharSet := 'ISO-8859-1';
  IdCorpo.ContentTransfer := '32bit';
  IdCorpo.ContentDescription := 'Corpo da Mensagem';
  IdCorpo.Body.Clear;
  IdCorpo.Body.Add( Corpo );
  IdSMTP := TIdSMTP.Create(nil);
  if Porta = '25' then
     begin
       With IdSMTP Do
       begin
         try
           IdSSL1 := TIdSSLIOHandlerSocketOpenSSL.Create( nil );
           IdSMTP.IOHandler := IdSSL1;
           //UseTLS := utUseImplicitTLS;
         except
           on E: Exception do
           begin
             IOHandler := TIdIOHandler.MakeDefaultIOHandler( nil );
             //UseTLS := utNoTLSSupport;
             ShowMessage('SSL da Autenticação Segura Falhou.'        + #13 + '' + #13 +
                         'Pode ser uma instabilidade temporária na ' + #13 +
                         'conexão de sua Internet.'                  + #13 + '' +#13+
                         'Tente de novo agora ou mais tarde.');
             result := False;
           end;
         end;
         IdSSL1.SSLOptions.Method := sslvSSLv23;
         IdSSL1.SSLOptions.Mode := sslmClient;
       end;
     end
  else
     begin
        IdSSL1 := TIdSSLIOHandlerSocketOpenSSL.Create( nil );
        IdSMTP.IOHandler := IdSSL1;
        //IdSMTP.UseTLS             := utUseImplicitTLS;
        IdSSL1.SSLOptions.Method := sslvSSLv23;
        IdSSL1.SSLOptions.Mode := sslmClient;
     end;
  With IdSMTP Do
    try
      AuthType := SatDefault;
      ReadTimeout := 10000;
      Host := Dominio;
      Port := StrToInt(Porta);
      UserName := Usuario;
      Password := Senha;
      AuthType  := satDefault; //Login
      Host := Dominio;
      Password := Senha;
      Port := StrToInt(Porta);
      UserName := Usuario;
      IOHandler := IdSSL1;
      //UseTLS    := utUseRequireTLS;
      ConnectTimeout := 10000;
      ReadTimeout    := 10000;
      AuthType := satDefault; //Login
    try
      Connect;
      Authenticate;
    except
      on E: Exception do
      begin
        showmessage(e.message);
        ShowMessage('Autenticação Falhou.'                     +#13+ '' + #13 +
                    'Verifique seu Nome de Usuário e Senha ou '+#13+
                    'Tente de novo agora ou mais tarde.');
        result := False;
      end;
    end;
       if Connected then
       begin
         Send( IdMessage );
         result := True;
       end
    else
        begin
         raise Exception.Create('A conexão com o Provedor foi interrompida.' + #13 + '' + #13 +
                                'Verifique se a sua Internet está ativa.');
         result := False;
       end;
    finally
      Disconnect;
    end;
    except
      result := false;
   end;
   finally
    FreeAndNil( IdMessage );
    FreeAndNil( IdSMTP );
   end;
end;

function carrega_mail_config : string;
begin
   with modulo_dados do
   begin
      sql:='SELECT * FROM USER_geoapolo_mail_server';
      fdquerysql7.Close;
      fdquerysql7.SQL.Clear;
      fdquerysql7.SQL.Text := sql;
      if executaracao(fdquerysql7, fdbanco, true, dtsfdquerysql7) then
         begin
            smtpserver:=fdquerysql7.fieldbyname('servidor_envio').asstring;
            porta:=fdquerysql7.fieldbyname('porta_envio').asstring;
         end;
   end;
end;

Function ValidaEMail(const EMailIn: string):Boolean;
const
  CaraEsp: array[1..40] of string[1] =
  ( '!','#','$','%','¨','&','*',
  '(',')','+','=','§','¬','¢','¹','²',
  '³','£','´','`','ç','Ç',',',';',':',
  '<','>','~','^','?','/','','|','[',']','{','}',
  'º','ª','°');
var
  i,cont   : integer;
  EMail    : ShortString;
begin
  EMail := EMailIn;
  Result := True;
  cont := 0;
  if EMail <> '' then
    if (Pos('@', EMail)<>0) and (Pos('.', EMail)<>0) then    // existe @ .
    begin
      if (Pos('@', EMail)=1) or (Pos('@', EMail)= Length(EMail)) or (Pos('.', EMail)=1) or (Pos('.', EMail)= Length(EMail)) or (Pos(' ', EMail)<>0) then
        Result := False
      else                                   // @ seguido de . e vice-versa
        if (abs(Pos('@', EMail) - Pos('.', EMail)) = 1) then
          Result := False
        else
          begin
            for i := 1 to 40 do            // se existe Caracter Especial
              if Pos(CaraEsp[i], EMail)<>0 then
                Result := False;
            for i := 1 to length(EMail) do
            begin                                 // se existe apenas 1 @
              if EMail[i] = '@' then
                cont := cont + 1;                    // . seguidos de .
              if (EMail[i] = '.') and (EMail[i+1] = '.') then
                Result := false;
            end;
                                   // . no f, 2ou+ @, . no i, - no i, _ no i
            if (cont >=2) or ( EMail[length(EMail)]= '.' )
              or ( EMail[1]= '.' ) or ( EMail[1]= '_' )
              or ( EMail[1]= '-' )  then
                Result := false;
                                            // @ seguido de COM e vice-versa
            if (abs(Pos('@', EMail) - Pos('com', EMail)) = 1) then
              Result := False;
                                              // @ seguido de - e vice-versa
            if (abs(Pos('@', EMail) - Pos('-', EMail)) = 1) then
              Result := False;
                                              // @ seguido de _ e vice-versa
            if (abs(Pos('@', EMail) - Pos('_', EMail)) = 1) then
              Result := False;
          end;
    end
    else
      Result := False;
end;

{function retorna_nomeproduto(codigo_produto : string; formulario : TForm) : string;
begin
   with modulo_dados, formulario do
   begin
       sql:='SELECT prodnome FROM geoapolo_produtos WHERE codigo_produto = '+quotedstr(codigo_produto);
       executaracao(sql,querysqlsql);
       if querysqlsql.RecordCount > 0  then
          result:= querysqlsql.fieldbyname('prodnome').asstring
       else
          result:='';
   end;
end;

function retorna_gruposoftware(formulario : TForm) : string;
begin
   with formulario, modulo_dados do
   begin
      sql:='SELECT gruposoftware FROM geoapolo_configuracoes';
      executaracao(sql,querysqlsql);
      if querysqlsql.RecordCount > 0 then
         begin
            if querysqlsql.fieldbyname('gruposoftware').asstring = '' then
               begin
                  messagedlg('NÃO FOI CONFIGURADO O PARÂMETRO DE GRUPO DE SOFTWARE PARA ORIENTAR A PESQUISA !!!',mterror,[mbok],0);
                  exit;
               end
            else
               result:=querysqlsql.fieldbyname('gruposoftware').asstring;
         end
      else
         result:='0';
   end;
end;}

function ValidaCampo(Edit: TCustomEdit; const NomeCampo: string): Boolean;
begin
  Result := Trim(Edit.Text) <> '';

  if not Result then
  begin
    MessageDlg('O CAMPO ' + NomeCampo + ' NÃO PODE SER VAZIO !!!', mtError, [mbOK], 0);
    Edit.SetFocus;
  end;
end;

function ValidaCombo(Combo: TComboBox; const NomeCampo: string): Boolean;
begin
  Result := Trim(Combo.Text) <> '';

  if not Result then
  begin
    MessageDlg('O CAMPO ' + NomeCampo + ' NÃO PODE SER VAZIO !!!', mtError, [mbOK], 0);
    Combo.SetFocus;
  end;
end;

function BuscarCEPporEndereco(const UF, Cidade, Logradouro: string): string;
var
  HTTP: TIdHTTP;
  URL: string;
  Response: string;
  JSONArray: TJSONArray;
  Item: TJSONValue;
begin
  Result := '';
  HTTP := TIdHTTP.Create(nil);
  try
    HTTP.Request.ContentType := 'application/json';

    // URL ViaCEP por endereço (logradouro)
    URL := Format(
      'https://viacep.com.br/ws/%s/%s/%s/json/',
      [UF, StringReplace(Cidade, ' ', '%20', [rfReplaceAll]),
           StringReplace(Logradouro, ' ', '%20', [rfReplaceAll])]
    );

    Response := HTTP.Get(URL);

    // Resposta é um JSON Array
    JSONArray := TJSONObject.ParseJSONValue(Response) as TJSONArray;

    if Assigned(JSONArray) and (JSONArray.Count > 0) then
    begin
      Item := JSONArray.Items[0];
      Result := TJSONObject(Item).GetValue<string>('cep').Replace('-', '');
    end;
  except
    on E: Exception do
      raise Exception.Create('Erro ao consultar ViaCEP: ' + E.Message);
  end;

  HTTP.Free;
end;

{
procedure Tfrmestacoes.DimensionarGrid(dbg: TDbGrid; var formulario);
   type
      TArray = Array of integer;
   procedure AjustarColumns(Swidth,TSize:integer;Asize:TArray);
     var
       idx:integer;
   begin
     if Tsize = 0 then
        begin
           Tsize:=dbg.Columns.Count;
             for idx:=0 to dbg.Columns.Count-1 do
               dbg.Columns[Idx].Width:=
                     (dbg.Width- dbg.Canvas.TextWidth('AAAAAA')) div Tsize
        end
     else
      for idx:=0 to dbg.Columns.Count-1 do
        dbg.Columns[Idx].Width:=dbg.Columns[Idx].Width + (Swidth*Asize[idx] div Tsize);
    end;
  var
   Idx,Twidth,Tsize,Swidth: Integer;
   AWidth:TArray;
   Asize:TArray;
   NomeColuna:String;
 begin
   SetLength(AWidth,dbg.Columns.Count);
   SetLength(ASize,dbg.Columns.Count);
   TWidth:=0;
   TSize:=0;
     for Idx := 0 to dbg.Columns.Count - 1  do
        begin
          NomeColuna:=Dbg.Columns[Idx].Title.Caption;
          dbg.Columns[Idx].Width :=
                   dbg.Canvas.TextWidth(Dbg.Columns[Idx].Title.Caption+'A');
          AWidth[idx]:=dbg.Columns[Idx].Width;
          TWidth:= TWidth + AWidth[idx];
          Asize[idx]:= dbg.Columns[idx].Field.Size;
          Tsize:= Tsize+Asize[idx];
       end;
if dgColLines in dbg.Options then
     TWidth:= TWidth+ Dbg.Columns.Count;

//adiciona a largura da coluna indicada do cursor
if dgIndicator in Dbg.Options then
    TWidth:=TWidth+IndicatorWidth;

Swidth:=dbg.ClientWidth - TWidth;
AjustarColumns(Swidth,TSize,Asize);
dbg.Width:=dbg.Width + dbg.Canvas.TextWidth('AAAAAA');
Dbg.Left:=(Tform(formulario).Width - dbg.Width) div 2 -
          (dbg.Canvas.TextWidth('AA') div 2);
 end;
}

function GetFileExt(FileName: string): String;
var
i: integer;
begin
   Result:='\';
   for i:=Length(FileName) downto 1 do
   begin
      Result:=FileName[i]+Result;
      if FileName[i]='.\' then
         break;
   end;
end;

{function alarme_pic : string;
var
   titulo,corpomensagem,data:string;
begin
   with modulo_dados do
   begin
      sql:='SELECT servidor_envio, porta_envio';
      sql:=sql+' FROM geoapolo_mail_server';
      executaracao(sql,querysqlsql6);
      if querysqlsql6.RecordCount <=0 then
         begin
            messagedlg('CONFIGURAÇÕES PARA ENVIO DE E-MAIL NÃO FORAM ENCONTRADAS !!!',mterror,[mbok],0);
            exit;
         end;
      sql:='SELECT gpic.codigo_pic,gsp.descricao_status motivo_pic, gpic.data_abertura, gpic.data_prevista_realizacao,gmpic.descricao_motivopic,';
      sql:=sql+' gpic.geoentcod_solicitante, ge.geoentnome solicitante, gpic.texto_solicitacao, gpic.texto_andamento, gpic.codigo_motivopic, ';
      sql:=sql+' gpic.codigo_usuariorespsolucao, u.nome, ge.geocidcod, tc.nome_cidade, tc.estado, (gpic.data_prevista_realizacao-current_date) as dias_atraso';
      sql:=sql+' FROM geoapolo_pic gpic INNER JOIN geoapolo_pic_motivo gmpic ON gpic.codigo_motivopic = gmpic.codigo_motivopic';
      sql:=sql+' INNER JOIN geoapolo_pic_status gsp ON gpic.codigo_statuspic = gsp.codigo_statuspic';
      sql:=sql+' INNER JOIN geoapolo_entidade ge ON gpic.geoentcod_solicitante = ge.geoentcod';
      sql:=sql+' INNER JOIN tab_cidades tc ON ge.geocidcod = tc.codigo_cidade';
      sql:=sql+' LEFT JOIN usuarios u ON gpic.codigo_usuariorespsolucao = u.codigo_usuario';
      sql:=sql+' WHERE (gpic.data_prevista_realizacao-current_date) < 0';
      sql:=sql+' AND   gpic.data_fechamento is null';
      executaracao(sql,querysqlsql4);
      if querysqlsql4.RecordCount > 0 then
         begin
            querysqlsql4.first;
            while not querysqlsql4.eof  do
            begin
               titulo:='PREVISÃO DE ATENDIMENTO DO PIC '+querysqlsql4.fieldbyname('codigo_pic').asstring+' ULTRAPASSADO EM '+querysqlsql4.fieldbyname('dias_atraso').asstring+' DIA(S)';
               corpomensagem:=corpomensagem+'<TABLE BORDER="1" WIDTH=1300>';
               corpomensagem:=corpomensagem+'<tr><td colspan=7 align="CENTER"> '+titulo+'</td></tr>';
               corpomensagem:=corpomensagem+'<tr><td>';
               corpomensagem:=corpomensagem+'Número PIC  '+'</td>';
               corpomensagem:=corpomensagem+'<td>'+'  Entidade  '+'</td>';
               corpomensagem:=corpomensagem+'<td>'+'  Data Abertura  '+'</td>';
               corpomensagem:=corpomensagem+'<td>'+'  Solicitação  '+'</td>';
               corpomensagem:=corpomensagem+'<td>'+'  Responsável  '+'</td>';
               corpomensagem:=corpomensagem+'<td>'+'  Ações Tomadas  '+'</td>';
               corpomensagem:=corpomensagem+'</td></tr>';
               //
               corpomensagem:=corpomensagem+'<tr>';
               corpomensagem:=corpomensagem+'<td>'+querysqlsql4.fieldbyname('codigo_pic').asstring+'</td>';
               corpomensagem:=corpomensagem+'<td>'+querysqlsql4.fieldbyname('solicitante').asstring+'</td>';
               corpomensagem:=corpomensagem+'<td>'+querysqlsql4.fieldbyname('data_abertura').asstring+'</td>';
               corpomensagem:=corpomensagem+'<td>'+quotedstr(querysqlsql4.fieldbyname('texto_solicitacao').asstring)+'</td>';
               corpomensagem:=corpomensagem+'<td>'+querysqlsql4.fieldbyname('nome').asstring+'</td>';
               corpomensagem:=corpomensagem+'<td>'+querysqlsql4.fieldbyname('texto_andamento').asstring+'</td></tr>';
               //
               corpomensagem:=corpomensagem+'</table>';
               corpomensagem:=corpomensagem+'</body>';
               corpomensagem:=corpomensagem+'</html>';

               corpomensagem:=chr(149)+'A ENTIDADE '++' EM '++chr(13);
               corpomensagem:=corpomensagem+chr(13)+'FEZ A SEGUINTE SOLICITAÇÃO: '+CHR(13)++chr(13);
               corpomensagem:=corpomensagem+chr(13)+' SENDO O RESPONSÁVEL POR ESTA AÇÃO O '+;
               corpomensagem:=corpomensagem+CHR(13)+' E ELE TOMOU AS SEGUINTES AÇÕES :'+chr(13);
               corpomensagem:=corpomensagem+chr(13)+;

               sql:='SELECT gpmu.codigo_usuario,u.nome, u.email';
               sql:=sql+' FROM geoapolo_pic_motivousuario gpmu INNER JOIN usuarios u ON gpmu.codigo_usuario = u.codigo_usuario';
               sql:=sql+' WHERE gpmu.codigo_motivopic = '+querysqlsql4.fieldbyname('codigo_motivopic').asstring;
               sql:=sql+' GROUP BY gpmu.codigo_usuario,u.nome, u.email';
               executaracao(sql,querysqlsql5);
               if querysqlsql5.RecordCount > 0 then
                  begin
                     querysqlsql5.first;
                     while not querysqlsql5.eof do
                     begin
                        if EnviarEmail2(querysqlsql6.fieldbyname('servidor_envio').AsString,querysqlsql6.fieldbyname('porta_envio').AsString,'tecnologia@tvaparecida.com.br','12aparecida','GEOAPOLO','GEOAPOLO',querysqlsql5.fieldbyname('email').AsString,titulo,corpomensagem,1,1,false) then
                           begin
                         //     showmessage('E-MAIL ENVIADO COM SUCESSO !!!');
                           end;
                        //data:=copy(datetostr(date),4,2)+'/'+copy(datetostr(date),1,2)+'/'+copy(datetostr(date),7,4);
                        data:=datetostr(date);
                        envia_emailwf(querysqlsql5.fieldbyname('email').AsString, data,quotedstr('Alarme de Prazo de PIC Excedido'),corpomensagem,frmmissaopopular);
                        querysqlsql5.next;
                     end;
                  end;
               querysqlsql4.next;
            end;
         end;
   end;
end;

function carrega_dados(consulta: Tquerysql; formulario : tform) : string;
var
   i,a,b:integer;
begin
   with formulario do
   begin
      i:=0; b:=0;
      a:=consulta.fields.count;
      for i := 0 to formulario.ComponentCount -1 do
      begin
         if (formulario.Components[i] is TLabeledEdit) then
         begin
            (formulario.Components[i] as TLabeledEdit).text := consulta.fieldbyname(consulta.fields[b].DisplayName).asstring;
            inc(b);
         end;
         if b >= a then
            break;
      end;
   end;
end;      }

function integracoes : string;
begin
   with modulo_dados do
   begin
      sql:='SELECT gera_camp_baseapolo FROM USER_geoapolo_configuracoes';
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := sql;
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
            if fdquerysql.FieldByName('gera_camp_baseapolo').Asstring = 'S' then
               result:='Apolo'
            else if fdquerysql.FieldByName('gera_camp_baseapolo').asstring = 'N' then
               result:='GeoApolo';
         end;
   end;
end;

Function IPLocal( PC:String ):String;
var IP:TIdIPWatch;
    Host: TIdStackWindows;
begin
   Host := TIdStackWindows.Create;
   try
      Result := Host.ResolveHost( PC );
   Finally
      Host.Free;
   end;
End   ;

{function TFormPrincipal.getMacsNew: TStrings;
var
  i: Integer;
  NumInterfaces: Cardinal;
  AdapterInfo: array of TIpAdapterInfo;
  OutBufLen: ULONG;
  mac: string;
begin
  GetNumberOfInterfaces(NumInterfaces);
  SetLength(AdapterInfo, NumInterfaces);
  OutBufLen := NumInterfaces * SizeOf(TIpAdapterInfo);
  GetAdaptersInfo(@AdapterInfo[0], OutBufLen);

  Result := TStringList.Create;
  for i := 0 to NumInterfaces - 1 do begin
    mac := Format('%.2x:%.2x:%.2x:%.2x:%.2x:%.2x',
      [AdapterInfo[i].Address[0], AdapterInfo[i].Address[1],
       AdapterInfo[i].Address[2], AdapterInfo[i].Address[3],
       AdapterInfo[i].Address[4], AdapterInfo[i].Address[5]]);

    if mac <> '00:00:00:00:00:00' then
      Result.Add(mac)
    else
      Break;
  end;
end;

Function GetIP:string;
//--> Declare a Winsock na clausula uses da unit
var
    WSAData: TWSAData;
    HostEnt: PHostEnt;
    Name:string;
begin
  WSAStartup(2, WSAData);
  SetLength(Name, 255);
  Gethostname(PChar(Name), 255);
  SetLength(Name, StrLen(PChar(Name)));
  HostEnt := gethostbyname(PChar(Name));
  with HostEnt^ do
  begin
    Result := Format('%d.%d.%d.%d',
    [Byte(h_addr^[0]),Byte(h_addr^[1]),
    Byte(h_addr^[2]),Byte(h_addr^[3])]);
  end;
    WSACleanup;
end;     }

function Alltrim(Search: string): string;
{Remove os espathos em branco de ambos os lados da string}
var
   variavellimpa:string;
begin
   variavellimpa:=buscatroca(Search,' ','');
   Result := variavellimpa;
end;

function WinExecAndWait32(FileName: string; Visibility: Integer): Longword;
var { by Pat Ritchey }
  zAppName: array[0..512] of Char;
  zCurDir: array[0..255] of Char;
  WorkDir: string;
  StartupInfo: TStartupInfo;
  ProcessInfo: TProcessInformation;
begin
  StrPCopy(zAppName, FileName);
  GetDir(0, WorkDir);
  StrPCopy(zCurDir, WorkDir);
  FillChar(StartupInfo, SizeOf(StartupInfo), #0);
  StartupInfo.cb          := SizeOf(StartupInfo);
  StartupInfo.dwFlags     := STARTF_USESHOWWINDOW;
  StartupInfo.wShowWindow := Visibility;
  if not CreateProcess(nil,
    zAppName, // pointer to command line string
    nil, // pointer to process security attributes
    nil, // pointer to thread security attributes
    False, // handle inheritance flag
    CREATE_NEW_CONSOLE or // creation flags
    NORMAL_PRIORITY_CLASS,
    nil, //pointer to new environment block
    nil, // pointer to current directory name
    StartupInfo, // pointer to STARTUPINFO
    ProcessInfo) // pointer to PROCESS_INF
    then Result := WAIT_FAILED
  else
  begin
    WaitForSingleObject(ProcessInfo.hProcess, INFINITE);
    GetExitCodeProcess(ProcessInfo.hProcess, Result);
    CloseHandle(ProcessInfo.hProcess);
    CloseHandle(ProcessInfo.hThread);
  end;
end; { WinExecAndWait32 }

function ExportToCsv(Grid : TStringGrid; const FileName:string) : string;
const
  separador :string = ';';
var
  Col, Row : integer;
  linha : string;
  f : TextFile;
begin
  AssignFile(f, FileName);
  try
    Rewrite(f);
    for Row:=0 to Grid.RowCount-1 do
      begin
        linha := EmptyStr;
        for Col:=0 to Grid.ColCount-1 do
          begin
            linha := linha + Grid.Cells[Col, Row];
            if not(Col = Grid.ColCount-1) then
              linha := linha + separador;
          end;
        Writeln(f, Linha);
      end;
  finally
    CloseFile(f);
  end;
end;

function  Ret_Numero(Key: Char; Texto: string; EhDecimal: Boolean = False): Char;

begin
  if  not EhDecimal then
    begin
      { Chr(8) = Back Space }
      if  not ( Key in ['0'..'9', Chr(8)] ) then
          Key := #0
    end
  else
    begin
      {if  Key = #46 then
          Key := DecimalSeparator;}
      if  not ( Key in ['0'..'9', Chr(8)] ) then
          Key := #0
      else
       { if ( Key = DecimalSeparator ) and ( Pos( Key, Texto ) > 0 ) then
            Key := #0;}
    end;
  Result := Key;
end;

function CheckMaskEmptyText(const EditMask: TEditMask; const Text:String):Boolean;
var
   MaskOffset: Integer;
   CType: TMaskCharType;
   FMaskBlank:Char;
   Mask:String;
   default:boolean;
begin
   default:=true;
   FMaskBlank:= MaskGetMaskBlank(EditMask);
   for MaskOffset := 1 to Length(Editmask) do
      begin
         CType := MaskGetCharType(EditMask, MaskOffset);
         case CType of
              mcLiteral, mcIntlLiteral: Mask:=Mask+EditMask[MaskOffset];
              mcMaskOpt,mcMask:Mask:=Mask+FMaskBlank;
              mcFieldSeparator:
                 begin
                    if EditMask[MaskOffset+1] = '0' then
                       begin
                          Mask:='';
                          Break;
                          default:=false;
                       end;
                 end;
       end;
   end;
   if default then
      Mask:= FormatMaskText(EditMask,'');
   result:=Text = Mask;
end;

function IfThen(condicao: Boolean; valorSeVerdadeiro, valorSeFalso: Variant): Variant;
begin
  if condicao then
    Result := valorSeVerdadeiro
  else
    Result := valorSeFalso;
end;

function RemoverPecaDaString(const S: string; Inicio, Tamanho: Integer): string;
var
  Temp: string;
begin
  Temp := S;
  Delete(Temp, Inicio, Tamanho);
  Result := Temp;
end;

function ContarVirgulas(const Texto: string): Integer;
begin
  Result := TRegEx.Matches(Texto, ',').Count;
end;

{procedure AjustaLarguraColunas(DBGrid: TDBGrid);
var
  i, j, largura, maxLargura: Integer;
  tmpTexto: string;
  DS: TDataSet;
begin
  DS := DBGrid.DataSource.DataSet;
  if not Assigned(DS) or (DS.RecordCount = 0) then Exit;

  DS.DisableControls;
  try
    DS.First;
    for i := 0 to DBGrid.Columns.Count - 1 do
    begin
      maxLargura := DBGrid.Canvas.TextWidth(DBGrid.Columns[i].Title.Caption) + 25;

      for j := 0 to 10 do // verifica até 10 linhas, pra não pesar
      begin
        tmpTexto := DS.Fields[i].DisplayText;
        largura := DBGrid.Canvas.TextWidth(tmpTexto) + 25;
        if largura > maxLargura then
          maxLargura := largura;

        DS.Next;
        if DS.Eof then Break;
      end;

      DS.First;
      DBGrid.Columns[i].Width := maxLargura;
    end;
  finally
    DS.EnableControls;
  end;
end;   }

procedure AjustaLarguraColunas(DBGrid: TDBGrid);
var
  i, largura, maxLargura: Integer;
  tmpTexto: string;
  DS: TDataSet;
  Bmk: TBookmark;
  Contador: Integer;
begin
  if not Assigned(DBGrid) or
     not Assigned(DBGrid.DataSource) or
     not Assigned(DBGrid.DataSource.DataSet) then
    Exit;

  DS := DBGrid.DataSource.DataSet;

  if not DS.Active or DS.IsEmpty then
    Exit;

  DS.DisableControls;
  Bmk := DS.GetBookmark;

  try
    for i := 0 to DBGrid.Columns.Count - 1 do
    begin
      maxLargura := DBGrid.Canvas.TextWidth(
        DBGrid.Columns[i].Title.Caption
      ) + 25;

      DS.First;
      Contador := 0;

      while not DS.Eof and (Contador < 10) do
      begin
        tmpTexto := DBGrid.Columns[i].Field.DisplayText;

        largura := DBGrid.Canvas.TextWidth(tmpTexto) + 25;

        if largura > maxLargura then
          maxLargura := largura;

        Inc(Contador);
        DS.Next;
      end;

      DBGrid.Columns[i].Width := maxLargura;
    end;

    if DS.BookmarkValid(Bmk) then
      DS.GotoBookmark(Bmk);

  finally
    DS.FreeBookmark(Bmk);
    DS.EnableControls;
  end;
end;

function grava_configuracoes_grids(Formulario: TForm; Modulo: string; Grid: TDBGrid; NomeGrid: string;  Usuario: string;  Consulta: TDataSource): string;
var
  i: Integer;
  qConfig, qAux: TFDQuery;
begin
  Result := '';
  qConfig := TFDQuery.Create(nil);
  qAux := TFDQuery.Create(nil);
  try
    qConfig.Connection := Modulo_Dados.fdbanco;
    qAux.Connection := Modulo_Dados.fdbanco;

    Modulo_Dados.fdbanco.StartTransaction;
    try
      // Verifica se já existem configurações
      qConfig.SQL.Text :=
        'SELECT 1 FROM USER_geoapolo_config_grid ' +
        'WHERE modulo = :mod AND usucod = :usu AND nome_grid = :grid';
      qConfig.ParamByName('mod').AsString := Modulo;
      qConfig.ParamByName('usu').AsString := Usuario;
      qConfig.ParamByName('grid').AsString := NomeGrid;
      qConfig.Open;

      if not qConfig.IsEmpty then
      begin
        // Atualiza registros existentes
        for i := 0 to Grid.Columns.Count - 1 do
        begin
          qAux.SQL.Text :=
            'UPDATE USER_geoapolo_config_grid SET ' +
            'posicao_atual = :posicao, tamanho = :tamanho ' +
            'WHERE modulo = :mod AND usucod = :usu ' +
            'AND nome_grid = :grid AND campo = :campo';
          qAux.ParamByName('mod').AsString := Modulo;
          qAux.ParamByName('usu').AsString := Usuario;
          qAux.ParamByName('grid').AsString := NomeGrid;
          qAux.ParamByName('campo').AsString := Grid.Columns[i].FieldName;
          qAux.ParamByName('posicao').AsInteger := Grid.Columns[i].Index;
          qAux.ParamByName('tamanho').AsInteger := Grid.Columns[i].Width;
          qAux.ExecSQL;
        end;
      end
      else
      begin
        // Gera nova configuração
        if Formulario.ClassName = 'Tfrmentidades' then
        begin
          qAux.SQL.Text :=
            'SELECT c.name AS column_name FROM sys.columns c ' +
            'JOIN sys.objects o ON c.object_id = o.object_id ' +
            'WHERE o.name = :modulo';
          qAux.ParamByName('modulo').AsString := Modulo;
          qAux.Open;

          if not qAux.IsEmpty then
          begin
            qAux.First;
            while not qAux.Eof do
            begin
              i := Consulta.DataSet.FieldByName(qAux.FieldByName('column_name').AsString).Index;
              qConfig.SQL.Text :=
                'INSERT INTO USER_geoapolo_config_grid ' +
                '(modulo, nome_grid, campo, posicao_original, posicao_atual, usucod, tamanho) ' +
                'VALUES (:mod, :grid, :campo, 0, :pos, :usu, :tam)';
              qConfig.ParamByName('mod').AsString := Modulo;
              qConfig.ParamByName('grid').AsString := NomeGrid;
              qConfig.ParamByName('campo').AsString := qAux.FieldByName('column_name').AsString;
              qConfig.ParamByName('pos').AsInteger := i;
              qConfig.ParamByName('usu').AsString := Usuario;
              qConfig.ParamByName('tam').AsInteger := Consulta.DataSet.Fields[i].DisplayWidth;
              qConfig.ExecSQL;
              qAux.Next;
            end;
          end
          else
            ShowMessage('A view especificada não possui colunas.');
        end;
      end;

      Modulo_Dados.fdbanco.Commit;
      Result := 'OK';
    except
      on E: Exception do
      begin
        Modulo_Dados.fdbanco.Rollback;
        MessageDlg('Erro ao gravar configuração: ' + E.Message, mtError, [mbOK], 0);
        Result := 'ERRO';
      end;
    end;

  finally
    qConfig.Free;
    qAux.Free;
  end;
end;

function IsEmptyMask(const Value: string): Boolean;
begin
  // Remove caracteres da máscara e verifica se sobrou algo
  Result := Trim(StringReplace(StringReplace(Value, '/', '', [rfReplaceAll]), ' ', '', [rfReplaceAll])) = '';
end;

function TextToDate(const Value: string): TDate;
begin
  Result := StrToDateDef(Value, 0);
  if Result = 0 then
     raise Exception.Create('Data inválida: ' + Value);
end;
function ConsultarViaCEP(const ACEP: string; out Resultado: TViaCEPResult): Boolean;
var
  DTO: TViaCEPDTO;
begin
  Result := TViaCEPService.Consultar(ACEP, DTO);
  if Result then
  begin
    Resultado.Logradouro := DTO.Logradouro;
    Resultado.Bairro     := DTO.Bairro;
    Resultado.Cidade     := DTO.Cidade;
    Resultado.UF         := DTO.UF;
  end;
end;

function BuscarCEP(const ACEP: string): TViaCEPInfo;
var
  HTTP: TNetHTTPClient;
  Resposta: IHTTPResponse;
  JSON: TJSONObject;
  URL: string;
begin
  FillChar(Result, SizeOf(Result), 0);

  HTTP := TNetHTTPClient.Create(nil);
  try
    URL := 'https://viacep.com.br/ws/' + ACEP + '/json/';

    Resposta := HTTP.Get(URL);

    if Resposta.StatusCode = 200 then
    begin
      JSON := TJSONObject.ParseJSONValue(Resposta.ContentAsString) as TJSONObject;
      try
        if JSON.GetValue('erro') <> nil then
          raise Exception.Create('CEP não encontrado!');

        Result.Logradouro := JSON.GetValue<string>('logradouro');
        Result.Complemento := JSON.GetValue<string>('complemento');
        Result.Bairro      := JSON.GetValue<string>('bairro');
        Result.Cidade      := JSON.GetValue<string>('localidade');
        Result.Estado      := JSON.GetValue<string>('uf');
        Result.IBGE        := JSON.GetValue<string>('ibge');
        Result.Gia         := JSON.GetValue<string>('gia');
      finally
        JSON.Free;
      end;
    end
    else
      raise Exception.Create('Erro ao consultar CEP: ' + Resposta.StatusText);
  finally
    HTTP.Free;
  end;
end;

function ExecutarAcaon(
  const Query      : TFDQuery;
  const Conexao    : TFDConnection;
  const SQL        : string;               // ← nova: recebe a SQL direto
  const Params     : array of TParamSQL;   // ← nova: array de parâmetros
  UsarTransacao    : Boolean      = False;
  DataSource       : TDataSource  = nil
): Boolean;
var
  TipoSQL          : TTipoSQL;
  TransacaoIniciada: Boolean;
  P                : TParamSQL;
begin
  Result            := False;
  TransacaoIniciada := False;

  // ---------- validações ----------
  if not Assigned(Query) then
  begin
    MessageDlg('Query não foi inicializada!', mtError, [mbOK], 0);
    Exit;
  end;
  if not Assigned(Conexao) then
  begin
    MessageDlg('Conexão não foi inicializada!', mtError, [mbOK], 0);
    Exit;
  end;
  if Trim(SQL) = '' then
  begin
    MessageDlg('Comando SQL vazio!', mtError, [mbOK], 0);
    Exit;
  end;

  // ---------- prepara a query ----------
  Query.Close;
  Query.SQL.Clear;
  Query.SQL.Text := SQL;

  // aplica parâmetros
  for P in Params do
  begin
    Query.ParamByName(P.Nome).DataType := P.Tipo;
    Query.ParamByName(P.Nome).Value    := P.Valor;
  end;

  // ---------- execução (igual ao seu código atual) ----------
  try
    TipoSQL := IdentificarTipoSQL(Query.SQL.Text);

    if Query.Connection = nil then
      Query.Connection := Conexao;

    if UsarTransacao and (TipoSQL in [tsInsert, tsUpdate, tsDelete, tsExec]) then
      if not Conexao.InTransaction then
      begin
        Conexao.StartTransaction;
        TransacaoIniciada := True;
      end;

    try
      case TipoSQL of
        tsSelect, tsOther:
          begin
            Query.Open;
            if Assigned(DataSource) then
              DataSource.DataSet := Query;
            if Query.IsEmpty then
              Exit(False);
          end;
        tsInsert, tsUpdate, tsDelete, tsExec, tsCreate:
          Query.ExecSQL;
      end;

      if TransacaoIniciada and Conexao.InTransaction then
        Conexao.Commit;

      Result := True;

    except
      on E: Exception do
      begin
        if TransacaoIniciada and Conexao.InTransaction then
          Conexao.Rollback;
        RegistrarErroSQL(Query.SQL.Text, E.Message);
        MessageDlg(
          'Erro ao executar comando SQL:' + sLineBreak + sLineBreak +
          E.Message + sLineBreak + sLineBreak +
          'O erro foi registrado e enviado ao desenvolvedor.',
          mtError, [mbOK], 0
        );
      end;
    end;

  except
    on E: Exception do
    begin
       messagedlg('Erro Inesperado: '+e.Message, mterror,[mbok],0)  ;

    end;
  end;
end;

function ParOuImpar(const Valor: string): Variant;
var
  Numero: Int64;
begin
  if Trim(Valor) = '' then
  begin
    Result := 'Null';
    Exit;
  end;

  if not TryStrToInt64(Trim(Valor), Numero) then
  begin
    Result := 'Null';
    Exit;
  end;

  if (Numero mod 2) = 0 then
    Result := 'PAR'
  else
    Result := 'IMPAR';
end;

end.
