unit unt_imediatas;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, Buttons, Grids, DBGrids,Registry, ExtCtrls, ComCtrls,
  OleServer, ExcelXP, ComObj, ADODB, DB, Excel2010, Vcl.Samples.Gauges,
  Data.FMTBcd, Data.SqlExpr, Data.DBXMySql,FireDAC.Stan.Option;

type
  Tfrmimediatas = class(TForm)
    GroupBox1: TGroupBox;
    cboconsultas: TComboBox;
    gridimediatas: TDBGrid;
    Panel1: TPanel;
    spblimpar: TSpeedButton;
    spbexecutar: TSpeedButton;
    spbexportaexcel: TSpeedButton;
    spbexcluir: TSpeedButton;
    spbretornar: TSpeedButton;
    StatusBar1: TStatusBar;
    lblnumeroreg: TLabel;
    lblnreg: TLabel;
    lblmensagem1: TLabel;
    cbodatabase: TComboBox;
    SaveDialog1: TSaveDialog;
    Gauge1: TGauge;
    procedure spbretornarClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure spbexecutarClick(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure spbexportaexcelClick(Sender: TObject);
    procedure spbexcluirClick(Sender: TObject);
    procedure cbodatabaseKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cboconsultasEnter(Sender: TObject);
    procedure gridimediatasDrawColumnCell(Sender: TObject; const Rect: TRect;
      DataCol: Integer; Column: TColumn; State: TGridDrawState);

  private
    { Private declarations }
  public
    { Public declarations }
    nomedoarquivo:string;
  end;

var
  frmimediatas: Tfrmimediatas;
  registro:tregistry;
  sql,nomealias:string;
  i,c:integer;

function carrega_consultaspermitidas(bancodedados: string; pcodigousuario: string) : string; export;
//function export_to_excel : string; export;
function analisa_sql(sqltxt : string) : string; export;
//function export_to_excel : string; export;
function export_to_text : string; export;
function export_para_Excelv2(DSPadrao: TDataSet) : string; export;
function VerificaTipo(aTField : TField) : string; export;

implementation

uses unt_principal, frmconfigbancos, unt_dados, funcoes, unt_logon;

{$R *.dfm}

procedure Tfrmimediatas.spbretornarClick(Sender: TObject);
begin
   frmimediatas.Close;
   frmprincipal.show;
end;

procedure Tfrmimediatas.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
   action:=cafree;
end;

procedure Tfrmimediatas.gridimediatasDrawColumnCell(Sender: TObject;
  const Rect: TRect; DataCol: Integer; Column: TColumn; State: TGridDrawState);
var
  displaytext :string;
begin
  if Column.Field is TMemoField then
  begin
    // Limitar o texto exibido
    DisplayText := Copy(Column.Field.AsString, 1, 50) + '...';
    // Desenha o texto no grid
    gridimediatas.Canvas.FillRect(Rect);
    gridimediatas.Canvas.TextRect(Rect, Rect.Left + 2, Rect.Top + 2, DisplayText);
  end;
end;

procedure Tfrmimediatas.spbexecutarClick(Sender: TObject);
var
   pegasentenca : variant;
   bancomysql :tsqlconnection;
begin
   if cboconsultas.ItemIndex = -1 then
      begin
         messagedlg('PARA EXECUTAR UMA CONSULTA, PRIMEIRO SELECIONE QUAL CONSULTA DESEJA !!!', mtwarning,[mbok],0);
         cboconsultas.SetFocus;
         exit;
      end;
   // rotina de execução abaixo
   with modulo_dados do
   begin
       if (cboconsultas.ItemIndex <> -1) then
          begin
             sql:='SELECT * FROM USER_geoapolo_consultas WHERE descricao_consulta = :cboconsultas';
             fdquerysql2.Close;
             fdquerysql2.SQL.Clear;
             fdquerysql2.SQL.Text := sql;
             fdquerysql2.ParamByName('cboconsultas').AsString := cboconsultas.Text;

             if executaracao(fdquerysql2, fdbanco, true, dtsfdquerysql2) then
                begin
                   pegasentenca:=fdquerysql2.fieldbyname('sentenca_sql').asstring;
                   sql:=pegasentenca;
                   analisa_sql(pegasentenca);
                   if cbodatabase.Text = 'ALVO' then
                      begin
                         fdquerysql4.Close;
                         fdquerysql4.SQL.Clear;
                         fdquerysql4.SQL.Text := sql;
                         if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
                            begin
                               fdquerysql4.FetchAll;
                               gridimediatas.DataSource := dtsfdquerysql4;
                               lblnreg.Caption := inttostr(fdquerysql4.RecordCount);
                               gauge1.MaxValue:=fdquerysql4.RecordCount;
                               lblnreg.Refresh;
                               gridimediatas.refresh;
                            end;
                         gravalog(frmlogon.codigousuario,datetostr(date),'EXECUTOU A CONSULTA '+quotedstr(cboconsultas.Text));
                      end
                   else if cbodatabase.Text = 'GEOAPOLO' then
                      begin
                         fdquerysql4.Close;
                         fdquerysql4.SQL.Clear;
                         fdquerysql4.SQL.Text := sql;

                         if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
                            begin
                               fdquerysql4.FetchAll;
                               gridimediatas.DataSource := dtsfdquerysql4;
                               lblnreg.Caption := inttostr(fdquerysql4.RecordCount);
                               gauge1.MaxValue:=fdquerysql4.RecordCount;
                               lblnreg.Refresh;
                               gridimediatas.refresh;
                            end;
                      end
                   else if cbodatabase.Text = 'APLICATIVO RCC' then
                      begin
                         {zbanco.HostName := frmprincipal.servidorapp;
                         zbanco.Port := strtoint(frmprincipal.portacomunicacao);
                         zbanco.User := frmprincipal.usuarioapp;
                         zbanco.Password := frmprincipal.senhaapp;
                         zbanco.Protocol := 'mysql';
                         zbanco.Properties.Add('auth_protocol');
                         zbanco.Properties.Add('caching_sha2_password');
                         zbanco.Database := frmprincipal.nomebancoapp;
                         zbanco.Connect; }
                         //mysql
                         //executaracao(sql,fdquerysql4);
                         if fdquerysql4.RecordCount > 0 then
                            begin
                               dtsfdquerysql4.DataSet := fdquerysql4;
                               gridimediatas.DataSource := dtsfdquerysql4;
                               lblnreg.Caption := inttostr(fdquerysql4.RecordCount);
                               lblnreg.Refresh;
                               gridimediatas.Refresh;
                            end;
                      end
                   else if cbodatabase.Text = 'K2 - Firebird' then
                      begin
                          //executaracaok2(sql,querysqlk22);
{                          if zbancok2.Connected then
                             begin
                                //querysqlk22.Active := false;
                                querysqlk22.SQL.Clear; querysqlk22.SQL.Text := sql;
                                try
                                   querysqlk22.Open;
                                except
                                on e:exception do
                                   begin
                                      showmessage(e.Message);
                                      exit;
                                   end;
                                end;
                                if querysqlk22.RecordCount > 0 then
                                  begin
                                     dtsquerysqlk22.DataSet := querysqlk22;
                                     gridimediatas.DataSource := dtsquerysqlk22;
                                     lblnreg.Caption := inttostr(querysqlk21.RecordCount);
                                     lblnreg.Refresh;
                                     gridimediatas.Refresh;
                                  end;
                             end;  }
                      end;
                end;
          end;
   end;
end;

function analisa_sql(sqltxt : string) : string;
var
   posini,posfim:integer;
   varinptbox,flagsql,resultado:string;
begin
   with modulo_dados,frmimediatas do
   begin
     { if (trim(copy(uppercase(sqltxt),1,6)) <> 'SELECT') and (trim(copy(uppercase(sqltxt),1,6)) <> 'INSERT') and (trim(copy(uppercase(sqltxt),1,6)) <> 'DELETE') and (trim(copy(uppercase(sqltxt),1,6)) <> 'UPDATE') then
         begin
            messagedlg('ESTA NÃO É UMA SENTENÇA SQL VÁLIDA !!!',mterror,[mbok],0);
            cboconsultas.ItemIndex := -1; cboconsultas.SetFocus;
         end;  }
      flagsql:='0';
      // FAZ TRATAMENTO DE PARÂMETROS QUE NECESSITEM DE ENTRADA MANUAL
      for i:= 0 to length(sqltxt) do
      begin
         if copy(sqltxt,i,1) = '|'  then
            flagsql:='1';
         if (copy(sqltxt,i,1) = '|') or (flagsql = '1') then
            begin
               varinptbox := varinptbox+copy(sqltxt,i,1);
               if copy(sqltxt,i,1) = '|' then
                  begin
                     posini:=pos('|',sqltxt);
                     posfim:=pos('^',sqltxt);
                     varinptbox:=copy(sqltxt,posini+1,((posfim)-(posini+1)));
                     //varinptbox:=buscatroca(varinptbox,'|','');
                     //varinptbox:=buscatroca(varinptbox,'^','');
                     if varinptbox = '' then
                        varinptbox:='Parametro';
                     resultado:=inputbox('GEOAPOLO',varinptbox,'');
                     // ROTINA DE MACRO SUBSTITUIÇÃO
                     insert(quotedstr(resultado),sqltxt,posini);
                     delete(sqltxt,((posini+2)+length(resultado)),(posfim-posini)+1);
                     posini:=0; posfim:=0; varinptbox:=''; flagsql:='0';
                 end;
            end;
      end;
      // FAZ TRATAMENTO DE PARÂMETROS FIXOS NUMÉRICOS E CARACTERES
      for i:= 0 to length(sqltxt) do
      begin
         if copy(sqltxt,i,1) = '['  then
            flagsql:='1';
         if (copy(sqltxt,i,1) = '[') or (flagsql = '1') then
            begin
               varinptbox := varinptbox+copy(sqltxt,i,1);
               if copy(sqltxt,i,1) = ']' then
                  begin
                     posini:=pos('[',sqltxt);
                     posfim:=pos(']',sqltxt);
                     varinptbox:=buscatroca(varinptbox,'[','');
                     varinptbox:=buscatroca(varinptbox,']','');
                     // ROTINA DE MACRO SUBSTITUIÇÃO
                     insert(quotedstr(varinptbox)+' ',sqltxt,posini);
                     delete(sqltxt,((posini)+length(varinptbox)+2),(posfim-posini)+2);
                     posini:=0; posfim:=0; varinptbox:=''; flagsql:='0';
                 end;
            end;
      end;
      // FAZ TRATAMENTO DE PARÂMETROS DO TIPO DATA
      i:=0;
      for i:=0 to length(sqltxt) do
      begin
         if copy(sqltxt,i,1) = '{'  then
            flagsql:='1';
         if (copy(sqltxt,i,1) = '{') or (flagsql = '1') then
            begin
               varinptbox := varinptbox+copy(sqltxt,i,1);
               if copy(sqltxt,i,1) = '}' then
                  begin
                     posini:=pos('{',sqltxt);
                     posfim:=pos('}',sqltxt);
                     varinptbox:=buscatroca(varinptbox,'{','');
                     varinptbox:=buscatroca(varinptbox,'}','');
                     // ROTINA DE TRATAMENTO DE DATA
                     if length(varinptbox) > 0 then
                        resultado:=inputbox('GEOAPOLO - DIGITE A DATA SEPARADAS POR BARRAS',varinptbox,'')
                     else
                        resultado:='01/01/1900';
                     if resultado = '//' then
                        resultado:='01/01/1900';
                     if not strisdate(resultado) then
                        resultado:='01/01/1900';
                     resultado:=formatdatetime('yyyy-MM-dd',strtodatetime(resultado));
                     //copy(resultado,4,2)+'/'+copy(resultado,1,2)+'/'+copy(resultado,7,4);
                     // ROTINA DE MACRO SUBSTITUIÇÃO
                     insert(quotedstr(resultado),sqltxt,posini);
                     delete(sqltxt,((posini+2)+length(resultado)),(posfim-posini)+1);
                     posini:=0; posfim:=0; varinptbox:=''; flagsql:='0';
                 end;
            end;
      end;
      i:=0;
      for i := 0 to length(sqltxt) do
      begin
          if copy(sqltxt,i,1) = '&' then
             begin
                insert(chr(39),sqltxt,i);
                delete(sqltxt,i+1,1);
             end;
           if copy(sqltxt,i,1) = '?' then
             begin
                insert(chr(39),sqltxt,i);
                delete(sqltxt,i+1,1);
             end;
      end;
      sql:=sqltxt;
      result:=sqltxt;
   end;
end;

procedure Tfrmimediatas.spblimparClick(Sender: TObject);
begin
   cboconsultas.ItemIndex := -1;
end;

procedure Tfrmimediatas.cboconsultasEnter(Sender: TObject);
begin
   carrega_consultaspermitidas(cbodatabase.text,frmlogon.codigousuario);
end;

procedure Tfrmimediatas.cbodatabaseKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      cboconsultas.setfocus;
end;

procedure Tfrmimediatas.FormActivate(Sender: TObject);
begin
   with modulo_dados do
   begin
      // indice de configuração
      sql:='SELECT indexconsultasimediatas FROM USER_geoapolo_configuracoes';
      fdquerysql.Close;
      fdquerysql.SQL.clear;
      fdquerysql.SQL.Text := sql;
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
            if fdquerysql.FieldByName('indexconsultasimediatas').AsInteger = 1 then
               cbodatabase.ItemIndex := fdquerysql.fieldbyname('indexconsultasimediatas').asinteger
            else if fdquerysql.FieldByName('indexconsultasimediatas').asinteger = 0 then
               cbodatabase.ItemIndex := fdquerysql.fieldbyname('indexconsultasimediatas').asinteger;
         end;
      carrega_consultaspermitidas(cbodatabase.text,frmlogon.codigousuario);
      cbodatabase.Refresh;
      //
      cbodatabase.ItemIndex:=1; cbodatabase.Refresh;
      statusbar1.Panels[1].Text := configura_statusbar('a');
      statusbar1.Panels[3].Text := configura_statusbar('a');
      statusbar1.panels[5].text := frmprincipal.nomeserversql;
   end;
end;

function carrega_consultaspermitidas(bancodedados: string; pcodigousuario: string) : string;
begin
   with modulo_dados, frmimediatas do
   begin
      sql:='SELECT gac.descricao_consulta, gpc.usucod, gpc.autorizacao, gac.codigo_consulta';
      sql:=sql+' FROM USER_geoapolo_consultas gac';
      sql:=sql+' INNER JOIN USER_geoapolo_permissaoconsulta gpc ON gac.codigo_consulta = gpc.codigo_consulta';
      sql:=sql+' WHERE gpc.usucod = :codigousuario'; //+quotedstr();
      sql:=sql+' AND   gac.banco_consulta =:cbodatabase '; //+quotedstr();
      sql:=sql+' AND   gac.tipo_consulta = '+quotedstr('I');
      sql:=sql+' AND   gpc.autorizacao = '+quotedstr('A');
      fdquerysql1.Close;
      fdquerysql1.SQL.Clear;
      fdquerysql1.SQL.Text := sql;
      if (pcodigousuario = '') and (frmprincipal.usucod_apolo<> '') then
         pcodigousuario:=frmprincipal.usucod_apolo;

      fdquerysql1.ParamByName('codigousuario').AsString :=  pcodigousuario;
      fdquerysql1.ParamByName('cbodatabase').AsString :=   cbodatabase.text ;
      if executaracao(fdquerysql1, fdbanco, true, dtsfdquerysql1) then
         begin
            fdquerysql1.First;
            cboconsultas.Clear;
            while not fdquerysql1.Eof do
            begin
               cboconsultas.Items.Add(fdquerysql1.fieldbyname('descricao_consulta').asstring);
               fdquerysql1.Next;
            end;
         end;
   end;
end;

{procedure VerificarTipo (aTField: TField);
var FieldType: String;
begin
  FieldType:= aTField.ClassName;
  if (FieldType = 'TStringField') or (FieldType = 'TWideStringField') then
    begin
     { É Texto
     showmessage('é texto');
    end;
  if (FieldType = 'TDateField')     or
     (FieldType = 'TDateTimeField') or
     (FieldType = 'TTimeField')     then
    begin
     { É Data / Data/Hora
     showmessage('é data hora');
    end;
  if (FieldType = 'TIntegerField')  or
     (FieldType = '´TSmallIntField') or
     (FieldType = 'TLargeintField') then
    begin
     { É Inteiro
     showmessage('é inteiro');
    end;
  if (FieldType = 'TFloatField')    or
     (FieldType = 'TCurrencyField') or
     (FieldType = 'TBCDField')      or
     (FieldType = 'TFMTBCDField')   then
    begin
     { É Numérico ou Valor
     showmessage('é valor');
    end;
end;
                   }
function VerificaTipo(aTField: TField): string;
begin
  if aTField is TStringField then
    Result := 'String'
  else if aTField is TWideStringField then
    Result := 'String'
  else if aTField is TDateField then
    Result := 'Data'
  else if aTField is TDateTimeField then
    Result := 'Data'
  else if aTField is TTimeField then
    Result := 'Data'
  else if aTField is TIntegerField then
    Result := 'Inteiro'
  else if aTField is TSmallIntField then
    Result := 'Inteiro'
  else if aTField is TLargeIntField then
    Result := 'Inteiro'
  else if aTField is TFloatField then
    Result := 'Dinheiro'
  else if aTField is TCurrencyField then
    Result := 'Dinheiro'
  else if aTField is TBCDField then
    Result := 'Valor'
  else if aTField is TFMTBCDField then
    Result := 'Valor'
  else if aTField is TMemoField then
    Result := 'Memo' // Tipo específico para campos Memo
  else
    Result := 'Desconhecido';
end;

procedure Tfrmimediatas.spbexportaexcelClick(Sender: TObject);
var
   linha,coluna:integer;
   planilha: variant;
   valorcampo:string;
begin
   planilha:= CreateOleObject('Excel.Application');
   planilha.workbooks.add(1);
   planilha.caption:='Exportação de Dados GeoApolo - SDIT';
   planilha.visible:=true;

   with modulo_dados do
   begin
     fdquerysql4.DisableControls;
     fdquerysql4.First;
     for linha :=0 to fdquerysql4.RecordCount -1 do
     begin
          for coluna := 1 to fdquerysql4.Fields.Count do
          begin
            if VerificaTipo(fdquerysql4.Fields[coluna-1]) = 'String' Then
               valorcampo:=fdquerysql4.Fields[coluna-1].AsString
            else if VerificaTipo(fdquerysql4.Fields[coluna-1]) = 'Data' Then
               valorcampo:=formatdatetime('dd/mm/yyyy',fdquerysql4.Fields[coluna-1].AsDateTime)
            else if VerificaTipo(fdquerysql4.Fields[coluna-1]) = 'Inteiro'  then
               valorcampo:=inttostr(fdquerysql4.Fields[coluna-1].AsInteger)
            else if Verificatipo(fdquerysql4.Fields[coluna-1]) = 'Valor' then
               valorcampo:=floattostr(fdquerysql4.Fields[coluna-1].AsFloat)
            else if Verificatipo(fdquerysql4.Fields[coluna-1]) = 'Dinheiro' then
               valorcampo:=currtostr(fdquerysql4.Fields[coluna-1].AsCurrency)
            else if Verificatipo(fdquerysql4.Fields[coluna-1]) = 'Memo' then
               valorcampo:=fdquerysql4.fields[coluna-1].AsWideString;
            planilha.cells[linha+2,coluna]:=valorcampo;
          end;
          frmimediatas.gauge1.addprogress(1);
          frmimediatas.Gauge1.Refresh;
          fdquerysql4.Next;
     end;
     for coluna := 1 to fdquerysql4.Fields.Count do
     begin
        valorcampo:= fdquerysql4.Fields[coluna-1].DisplayLabel;
        planilha.cells[1,coluna]:=valorcampo;
     end;
     planilha.columns.AutoFit;
     fdquerysql4.EnableControls;
     gravalog(frmlogon.codigousuario,datetostr(date),'EXPORTOU PARA O EXCEL, DADOS DA CONSULTA: '+cboconsultas.Text);
   end;
end;

{function export_to_excel : string;
Var
  i,j,c,p1,p2,Cont : Integer;
  colunas: array[1..300] of string;
  alfabeto:string;
begin
   with modulo_dados, frmimediatas do
   begin
      p2:=27; p1:=0; j:=1;
      alfabeto:='ABCDEFGHIJKLMNOPQRSTUVXWYZ';
      if (cbodatabase.Text = 'APOLO') or (cbodatabase.Text = 'MIX') then
         begin
            for i:= 0 to querysql4.FieldCount do
            begin
               if i <= 26 then
                  colunas[i]:=trim(copy(alfabeto,i,1))
               else if i > 26 then
                  begin
                     for c:= 1 to 26 do
                     begin
                        colunas[p2]:=copy(alfabeto,p1,1)+trim(copy(alfabeto,c,1));
                        inc(p2);
                     end;
                     inc(p1);
                  end;
            end;
         end
      else
         begin
            for i:= 0 to querysql4.FieldCount do
            begin
               if i <= 26 then
                  colunas[i]:=trim(copy(alfabeto,i,1))
               else if i > 26 then
                  begin
                     for c:= 1 to 26 do
                     begin
                        colunas[p2]:=copy(alfabeto,p1,1)+trim(copy(alfabeto,c,1));
                        inc(p2);
                     end;
                     inc(p1);
                  end;
            end;
         end;
      //
      if (cbodatabase.Text = 'APOLO') or (cbodatabase.Text = 'MIX') then
        begin
          if querysql4.Active = false then
             begin
                messagedlg('EXECUTE PRIMEIRO A CONSULTA DEPOIS REALIZE A EXPORTAÇÃO !!!',mtwarning,[mbok],0);
                exit;
             end;
        end;
      //
      if cbodatabase.Text = 'GEOAPOLO' then
         begin
          if querysql4.Active = false then
             begin
                messagedlg('EXECUTE PRIMEIRO A CONSULTA DEPOIS REALIZE A EXPORTAÇÃO !!!',mtwarning,[mbok],0);
                exit;
             end;
         end;
       Cont := 2;
       Excel.Workbooks.Add(EmptyParam,0); // Cria um novo documento
       Excel.Caption := 'Exportando Consulta para o Excel'; /// Mesma função do caption de um form
       Excel.Visible[0] := True;// Se false, o excel irá rodar em background....
       if (cbodatabase.Text = 'Apolo') or (cbodatabase.Text = 'Mix') then
          begin
             If(Not(querysql4.Active))Then
               querysql4.Active := True;
          end
       else if (cbodatabase.Text = 'GEOAPOLO') then
          begin
            If(Not(querysql4.Active))Then
               querysql4.Active := True;
          end;
       // montagem das colunas da planilha
       j:=1;
       if (cbodatabase.Text = 'APOLO') or (cbodatabase.Text = 'MIX') then
          begin
             for i:= 0 to querysql4.FieldCount -1  do
             begin
                excel.range[colunas[j]+'1',colunas[j]+'1'].value2 := querysql4.Fields[i].DisplayName;
                inc(j);
             end;
             querysql4.First;
             j:=1;
             While not querysql4.Eof do
             Begin
                With excel do
                Begin
                   for i:= 0 to querysql4.fields.count -1 do
                   begin
                      range[colunas[j]+IntToStr(Cont),colunas[j]+IntToStr(Cont)].Value2  := querysql4.Fields[i].DisplayText;
                      inc(j);
                   end;
                   querysql4.Next;
                   inc(cont);
                   j:=1;
                End;
             End;
          end
       else if(cbodatabase.Text = 'GEOAPOLO') then
          begin
             for i:= 0 to querysql4.FieldCount -1  do
             begin
                excel.Range[colunas[j]+'1',colunas[j]+'1'].Value2 := querysql4.Fields[i].DisplayName;
                inc(j);
             end;
             querysql4.First;
             j:=1;
             While not querysql4.Eof do
             Begin
                With(excel)Do
                Begin
                   for i:= 0 to querysql4.fields.Count -1 do
                   begin
                      excel.range[colunas[j]+IntToStr(Cont),colunas[j]+IntToStr(Cont)].Value2  := querysql4.Fields[i].DisplayText;
                      inc(j);
                   end;
                   querysql4.Next;
                   inc(cont);
                   j:=1;
                End;
             End;

          end;
     //  excel.ActiveWorkbook.SaveCopyAs(inputbox('Onde deseja Salvar o Arquivo','Caminho do arquivo','')+'.xls',0); // Salva uma copia do documento em C:\ com o nome de teste.xls
   end;
end;    }

function export_para_Excelv2(DSPadrao: TDataSet) : string;
Var
  Lin, Col   : Integer;
  xExcel     : Variant;
  Conteudo : String;
begin

  Try
   if DSPadrao.RecordCount < 1 then
   begin
     Application.MessageBox('Nenhum registro a ser exportado','Atenção',MB_OK);
     Exit;
   end;
   Try
     xExcel:= CreateoleObject('Excel.Application');
     xExcel.WorkBooks.add(1);
     xExcel.caption := 'Exportação GeoApolo - SDIT';
     xExcel.visible := False;

     DSPadrao.DisableControls;
     DSPadrao.First;

     for Lin := 0 to DSPadrao.RecordCount - 1 do
     begin
       for Col := 1 to DSPadrao.FieldCount do
       begin
         Conteudo := DSPadrao.Fields[Col - 1].AsString;
         xExcel.cells[Lin + 2,Col]:= Conteudo;
       end;
      DSPadrao.Next;
      Application.ProcessMessages;
     end;
     for Col := 1 to DSPadrao.FieldCount do
     begin
       Conteudo := DSPadrao.Fields[Lin - 1].Name;
       xExcel.cells[1,Col] := Conteudo;
       {xExcel.Range['A1','Z1'].font.bold := true; // Negrito
       xExcel.Range['A1','Z1'].Interior.Color := $00D6D6D6; // Cor da Célula
       xExcel.Range['A1','Z1'].RowHeight := 25; //Altura da Célula }
     end;
     //xExcel.columns.Autofit;  //Alinhar automaticamete o tamanho da coluna
     xExcel.visible := True;
   finally
     DSPadrao.EnableControls;
     //led := True;
   end;
  Except
    on e : Exception do
        raise Exception.Create('Erro ao exportar planilha ' +#13+
                               '================'+#13+#13+
                               'Menssagem : ' + E.Message +#13+
                               'Classe : '    + E.ClassName);
  end;
end;


procedure Tfrmimediatas.spbexcluirClick(Sender: TObject);
var
    i: integer;
begin
{   with modulo_dados do
   begin
    //troque o "SeuDataSet" pelo Nome do Table ou Query utilzado no DBGrid
    for i := 0 to querysql3.FieldCount-1 do
      querysql4.Fields[i].DisplayWidth := Length(querysql3.Fields[i].Text);
   end;}
   savedialog1.Execute;
   nomedoarquivo:=savedialog1.FileName ;
   export_to_text;
end;

function export_to_text : string;
var
   arquivo:textfile;
   linha:string;
   i:integer;
begin
   with modulo_dados, frmimediatas do
   begin
      if ((cbodatabase.Text = 'APOLO') or (cbodatabase.Text = 'MIX')) then
         begin
            if fdquerysql4.Active = false then
               fdquerysql4.Active := true;
         end
      else if (cbodatabase.Text = 'GEOAPOLO') then
         begin
            if fdquerysql4.Active = false then
               fdquerysql4.Active := true;
         end;
      //
      assignfile(arquivo,nomedoarquivo);
     rewrite(arquivo);
     Write(arquivo, #239+#187+#191);
      // montando linha de titulo das colunas
      if ((cbodatabase.Text = 'APOLO') or (cbodatabase.Text = 'MIX')) then
         begin
            linha:='';
            for i:= 0 to fdquerysql4.FieldCount -1 do
            begin
               linha:=linha+UTF8Encode(fdquerysql4.Fields[i].DisplayName)+';';
            end;
            writeln(arquivo,linha);
            //
            fdquerysql4.First;
            while not fdquerysql4.Eof do
            begin
               linha:='';
               for i := 1 to fdquerysql4.FieldCount -1 do
                  if fdquerysql4.Fields[i].DisplayText <> '' then
                     linha:=linha+UTF8Encode(fdquerysql4.Fields[i].DisplayText)+';'
                  else
                     linha:=linha+UTF8Encode(chr(39)+' '+chr(39))+';';
               writeln(arquivo,linha);
               frmimediatas.gauge1.addprogress(1);
               frmimediatas.Gauge1.Refresh;
               fdquerysql4.Next;
            end;
            closefile(arquivo);
         end
      else if (cbodatabase.Text = 'GEOAPOLO') then
         begin
            linha:='';
            for i:= 0 to fdquerysql4.FieldCount -1 do
            begin
               linha:=linha+UTF8Encode(fdquerysql4.Fields[i].DisplayName)+';';
            end;
            writeln(arquivo,linha);
            //
            fdquerysql4.First;
            while not fdquerysql4.Eof do
            begin
               linha:='';
               for i := 1 to fdquerysql4.FieldCount -1 do
                  if fdquerysql4.Fields[i].DisplayText <> '' then
                     linha:=linha+UTF8Encode(fdquerysql4.Fields[i].DisplayText)+';'
                  else
                     linha:=linha+UTF8Encode(chr(39)+' '+chr(39))+';';
               writeln(arquivo,linha);
            fdquerysql4.Next;
            end;
            closefile(arquivo);
            showmessage('EXPORTAÇÃO CONCLUÍDA !!!');
         end;
   end;
end;

{procedure Tfrmimediatas.SendToOpenOffice(aDataSet: TDataSet);
var
   OpenDesktop, Calc, Sheets, Sheet: Variant; 
   Connect, OpenOffice : Variant; 
   i : Integer; // Coluna 
   j : Integer; // Linha
   teste : string; 
begin 
   Screen.Cursor      := crSQLWait; 
   aDataset.Open; 
   aDataset.Last;

   // Cria o link OLE com o OpenOffice 
   if VarIsEmpty(OpenOffice) then 
      OpenOffice := CreateOleObject('com.sun.star.ServiceManager'); 
   Connect := not (VarIsEmpty(OpenOffice) or VarIsNull(OpenOffice)); 

   // Inicia o Calc 
   OpenDesktop := OpenOffice.CreateInstance('com.sun.star.frame.Desktop'); 
   Calc        := OpenDesktop.LoadComponentFromURL('private:factory/scalc', '_blank', 0, VarArrayCreate([0, - 1], varVariant)); 
   Sheets      := Calc.Sheets; 
   Sheet       := Sheets.getByIndex(0); 

   // Cria linha de cabeçalho 
   i := 0;
   while i <= aDataset.FieldCount - 1 do begin 
         Sheet.getCellByPosition(i,0).setString(aDataset.Fields[i].FieldName); 
         i := i + 1; 
   end; 

   // Preenche a planilha 
   j := 1; 
   aDataset.First; 
   while not aDataset.Eof do 
   begin 
         i := 0; 
         while i <= aDataset.FieldCount - 1 do
         begin 
              if aDataset.Fields[i].DataType in [ftDate, ftTime, ftDateTime] then 
              begin 
                 if ((DateToStr(aDataset.Fields[i].Value) <> Null) and (DateToStr(aDataset.Fields[i].Value) <> '')) then 
                    Sheet.getCellByPosition(i,j).SetString(aDataset.Fields[i].Value); 
              end 
              else if aDataset.Fields[i].DataType in [ftSmallint, ftInteger, ftLargeint] then 
              begin 
                 if ((IntToStr(aDataset.Fields[i].Value) <> Null) and (IntToStr(aDataset.Fields[i].Value) <> '')) then 
                    Sheet.getCellByPosition(i,j).SetValue(aDataset.Fie0A   Sheets      := Calc.Sheets; 
   Sheet       := Sheets.getByIndex(0); 

   // Cria linha de cabeçalho 
   i := 0; 
   while i <= aDataset.FieldCount - 1 do begin 
         Sheet.getCellByPosition(i,0).setString(aDataset.Fields[i].FieldName); 
         i := i + 1; 
   end; 

   // Preenche a planilha 
   j := 1; 
   aDataset.First; 
   while not aDataset.Eof do 
   begin 
         i := 0; 
         while i <= aDataset.FieldCount - 1 do 
         begin 
              if aDataset.Fields[i].DataType in [ftDate, ftTime, ftDateTime] then 
              begin 
                 if ((DateToStr(aDataset.Fields[i].Value) <> Null) and (DateToStr(aDataset.Fields[i].Value) <> '')) then 
                    Sheet.getCellByPosition(i,j).SetString(aDataset.Fields[i].Value);
              end 
              else if aDataset.Fields[i].DataType in [ftSmallint, ftInteger, ftLargeint] then 
              begin 
                 if ((IntToStr(aDataset.Fields[i].Value) <> Null) and (IntToStr(aDataset.Fields[i].Value) <> '')) then 
                    Sheet.getCellByPosition(i,j).SetValue(aDataset.Fields[i].Value); 
              end 
              else if aDataset.Fields[i].DataType in [ftFloat, ftCurrency] then 
              begin 
                 if ((FloatToStr(aDataset.Fields[i].Value) <> Null) and (FloatToStr(aDataset.Fields[i].Value) <> '')) then 
                    Sheet.getCellByPosition(i,j).SetValue(aDataset.Fields[i].Value); 
              end 
              else begin 
                 if ((aDataset.Fields[i].Value <> Null) and (aDataset.Fields[i].Value <> '')) then 
                 begin 
                    teste := ''; 
                    teste := aDataset.Fields[i].Value; 
                    Sheet.getCellByPosition(i,j).SetString(teste); 
                 end;    
              end; 

               i := i + 1; 
         end; 
         aDataset.Next; 
         j := j + 1; 
   end; 
   Screen.Cursor      := crArrow; 
   // Desconecta o OpenOffice 
   OpenOffice         := Unassigned; 
   ShowMessage('Planilha Gerada');
end;
           }


{procedure ExportarToExcel;
var
  linha, coluna : integer;
  planilha : variant;
  valorcampo : string;
begin

  planilha:= CreateoleObject('Excel.Application');
  planilha.WorkBooks.add(1);
  planilha.caption := 'Exportando dados do dbGrid, dataset ou query para o Excel';
  planilha.visible := true;

  Query1.First;
  for linha := 0 to Query1.RecordCount - 1 do
  begin
    for coluna := 1 to Query1.FieldCount do
    begin
      valorcampo := Query1.Fields[coluna - 1].AsString;
      planilha.cells[linha + 2,coluna] := valorCampo;
    end;
    Query1.Next;
  end;
  for coluna := 1 to Query1.FieldCount do
  begin
    valorcampo := Query1.Fields[coluna - 1].DisplayLabel;
    planilha.cells[1,coluna] := valorcampo;
  end;
  planilha.columns.Autofit;
end;}

end.
