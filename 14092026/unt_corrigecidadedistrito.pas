unit unt_corrigecidadedistrito;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Data.DB, Vcl.Grids, Vcl.DBGrids,
  Vcl.StdCtrls, Vcl.ComCtrls, Vcl.Buttons, Vcl.ExtCtrls, Vcl.Menus,
  IdBaseComponent, IdComponent, IdTCPConnection, IdTCPClient, IdHTTP, Vcl.Mask;

type
  Tfrmdistritocidades = class(TForm)
    Panel1: TPanel;
    spblistapedvendaagrup: TSpeedButton;
    spblimpar: TSpeedButton;
    spblocalizar: TSpeedButton;
    spbexcluir: TSpeedButton;
    spbretornar: TSpeedButton;
    lblmsg1: TLabel;
    StatusBar1: TStatusBar;
    v: TGroupBox;
    gridcidadesedistritos: TDBGrid;
    spbfiltrar: TSpeedButton;
    GroupBox1: TGroupBox;
    grpcepsdodistrito: TGroupBox;
    gridcepsvinculados: TDBGrid;
    gridentidades: TDBGrid;
    lblcidadecidade: TLabeledEdit;
    spbuscacidade: TSpeedButton;
    lblnomecidade: TLabel;
    PopupMenu1: TPopupMenu;
    popupdistritos: TMenuItem;
    spbfiltraentidades: TSpeedButton;
    spbfiltracep: TSpeedButton;
    spbcorrigecidades: TSpeedButton;
    lblqtdreg: TLabel;
    lblqtdnreg: TLabel;
    GroupBox2: TGroupBox;
    gridendercomp: TDBGrid;
    BitBtn1: TBitBtn;
    procedure spbfiltrarClick(Sender: TObject);
    procedure spbretornarClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure lblcidadecidadeKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbuscacidadeClick(Sender: TObject);
    procedure popupdistritosClick(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure spbfiltraentidadesClick(Sender: TObject);
    procedure spbfiltracepClick(Sender: TObject);
    procedure spbcorrigecidadesClick(Sender: TObject);
    procedure gridcidadesedistritosDblClick(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure BitBtn1Click(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  frmdistritocidades: Tfrmdistritocidades;

implementation

{$R *.dfm}

uses unt_dados, funcoes, unt_consultav3, unt_logon; //

procedure Tfrmdistritocidades.BitBtn1Click(Sender: TObject);
var
//  wsAtendeCliente: AtendeCliente;
 // wsConsultaCepReq: consultaCEP;
 // wsConsultaCepResp: consultaCEPResponse;
  sEndCep: string;

begin
  //  InvRegistry.RegisterInvokeOptions(TypeInfo(YourSoapInterface), ioDocument);
  //    CHANGE TO
  //  InvRegistry.RegisterInvokeOptions(TypeInfo(YourSoapInterface), ioHasAllSOAPActions);   ((( TESTADO OK COM ESSE )))
  //    OR
  //  InvRegistry.RegisterInvokeOptions(TypeInfo(YourSoapInterface), ioHasNamespace);

  {try
    try
      //wsConsultaCepReq := consultaCEP.Create;
      //wsConsultaCepResp := consultaCEPResponse.Create;

      HTTPRIO1.HTTPWebNode.UseUTF8InHeader := True;
      wsAtendeCliente := GetAtendeCliente(False, '', HTTPRIO1);

      wsConsultaCepReq.cep := edtCep.Text;

      try
        wsConsultaCepResp := wsAtendeCliente.consultaCEP( wsConsultaCepReq );
      except
        on E: ERemotableException do
        begin
          if (UpperCase(Trim(E.message)) = 'CEP NAO ENCONTRADO') or (UpperCase(Trim(E.message)) = 'CEP NAO INFORMADO') then
          begin
            Application.MessageBox(PChar(Format('Atenção! Cep %s não informado/encontrado!', [edtCep.Text])), PChar('Mensagem'), MB_OK + MB_ICONINFORMATION);
            Exit;
          end
          else
          begin
            raise Exception.Create( E.message );
          end;
        end;
      end;

      sEndCep := wsConsultaCepResp.return.cep + #13;
      sEndCep := sEndCep + wsConsultaCepResp.return.end_ + #13;
      sEndCep := sEndCep + wsConsultaCepResp.return.complemento + #13;
      sEndCep := sEndCep + wsConsultaCepResp.return.complemento2 + #13;
      sEndCep := sEndCep + wsConsultaCepResp.return.bairro + #13;
      sEndCep := sEndCep + wsConsultaCepResp.return.cidade + #13;
      sEndCep := sEndCep + wsConsultaCepResp.return.uf + #13;

      ShowMessage( sEndCep );
    finally
      FreeAndNil(wsConsultaCepReq);
      FreeAndNil(wsConsultaCepResp);
      wsAtendeCliente._Release;
    end

  except
    on E: Exception do
    begin
      Application.MessageBox(PChar(Format('Atenção! %s%s ', [#13#13, E.message])), PChar('Erro'), MB_OK + MB_ICONERROR);
    end;
  end;   }end;

procedure Tfrmdistritocidades.FormActivate(Sender: TObject);
begin
   //carrega_config('DISTRITOCIDADES',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
   configura_grid('DISTRITOCIDADES',frmdistritocidades,frmlogon.nomeusuario,'gridcidadesedistritos',gridcidadesedistritos,modulo_dados.dtsfdquerysql);
end;

procedure Tfrmdistritocidades.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
   action:=cafree;
end;

procedure Tfrmdistritocidades.gridcidadesedistritosDblClick(Sender: TObject);
begin
   showmessage(inttostr(gridcidadesedistritos.Columns[gridcidadesedistritos.Selectedindex].Width));
   spbfiltraentidades.Click;
   spbfiltracep.Click;
end;

procedure Tfrmdistritocidades.lblcidadecidadeKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if key = vk_f4 then
      begin
         spbuscacidade.Click;
      end;
end;

procedure Tfrmdistritocidades.popupdistritosClick(Sender: TObject);
begin
   grava_configuracoes_grids(frmdistritocidades,'DISTRITOCIDADES',gridcidadesedistritos,'gridcidadesedistritos',frmlogon.nomeusuario,modulo_dados.dtsfdquerysql);
   //grava_config_telabusca('DISTRITOCIDADES',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
end;

procedure Tfrmdistritocidades.spbcorrigecidadesClick(Sender: TObject);
var
   vnomedistrito,vnovobairro,vnovobairromenor:string;
   vcep:string;
   tamanhocampobairro:integer;
   resp:word;
begin
   with modulo_dados do
   begin
      if fdquerysql6.RecordCount <=0 then
         begin
            if fdquerysql12.RecordCount <=0 then
               begin
                  if fdquerysql5.RecordCount <= 0 then
                     begin
                        resp:=messagedlg('NÃO HÁ ENTIDADES,CEP´S E ENDEREÇOS COMPLEMENTARES VINCULADOS A ESTE DISTRITO, CONFIRMA A REMOÇÃO ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
                        if resp=idyes then
                           begin
                              sql:='DELETE FROM cidade WHERE cidcod = :cidcod';
                              fdquerysql3.Close;
                              fdquerysql3.SQL.clear;
                              fdquerysql3.SQL.Text := sql;
                              fdquerysql3.ParamByName('cidcod').AsString :=fdquerysql4.FieldByName('cidcod').AsString;
                              if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                                 begin
                                    messagedlg('DISTRITO REMOVIDO COM SUCESSO !!!',mtinformation,[mbok],0);
                                    spbfiltrar.Click;
                                 end
                              else
                                 begin
                                    messagedlg('OCORREU ERRO AO TENTAR REMOVER O DISTRITO, POR FAVOR VERIFIQUE SE AINDA HÁ ALGUMA INTEGRAÇÃO !!!',mterror,[mbok],0);
                                    gridcidadesedistritos.SetFocus;
                                    exit;
                                 end;
                           end;
                     end;
               end;
         end;
      if lblcidadecidade.Text = '' then
        begin
           messagedlg('NÃO HÁ COMO EXECUTAR ESTA OPERAÇÃO SEM QUE DEFINA A CIDADE CORRETA',mterror,[mbok],0);
           lblcidadecidade.SetFocus;
           exit;
        end;
      if (fdquerysql6.FieldByName('cidcod').AsString = lblcidadecidade.Text) or (fdquerysql12.FieldByName('cidcod').AsString = lblcidadecidade.Text) then
         begin
            messagedlg('O CÓDIGO DO DISTRITO É O MESMO DA CIDADE CORRRETA CITADA, NENHUMA ALTERAÇÃO SERÁ FEITA !!!',mtwarning,[mbok],0);
            lblcidadecidade.Clear;
            gridcidadesedistritos.SetFocus;
            exit;
         end;
      resp:=messagedlg('Confirma a Transferência de Registros entre o Distrito e Cidades e posterior remoção do distrito ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
      if resp = idyes then
         begin
            spbfiltraentidades.Click;
            spbfiltracep.Click;
            fdquerysql6.First;
            while not fdquerysql6.Eof do
            begin
               vnomedistrito:=fdquerysql4.FieldByName('CIDADEAPOLO').AsString;
               tamanhocampobairro:=fdquerysql6.FieldByName('entbair').Size;
               if vnovobairro = '' then
                  vnovobairro:=fdquerysql6.FieldByName('entbair').AsString+'   ('+vnomedistrito+')';
               if length(vnovobairro) > tamanhocampobairro then
                  begin
                     messagedlg('TAMANHO DO NOME DO BAIRRO MAIS O DISTRITO EXCEDE O TAMANHO DO CAMPO BAIRRO',mterror,[mbok],0);
                     vnovobairromenor:=inputbox('Nome Bairro mais Distrito','',vnovobairro);
                     vnovobairro:=vnovobairromenor
                  end
               else
                  begin
                    // DEPOIS DE MONTAR O NOME DO BAIRRO+DISTRITO, FAZ-SE OS UPDATES NA TABELA DE CIDADES, MOVENDO DO DISTRITO PARA A CIDADE CORRETA
                    sql:='UPDATE entidade SET cidcod = '+quotedstr(lblcidadecidade.Text)+', entbair = '+quotedstr(vnovobairro);
                    sql:=sql+' WHERE entcod = :entcod'; //+quotedstr();
                    sql:=sql+' AND   cidcod = :cidcod'; //+quotedstr();
                    fdquerysql3.Close;
                    fdquerysql3.SQL.Clear;
                    fdquerysql3.SQL.Text := sql;
                    fdquerysql3.ParamByName('entcod').AsString :=fdquerysql6.FieldByName('entcod').AsString;
                    fdquerysql3.ParamByName('cidcod').AsString :=fdquerysql4.FieldByName('cidcod').AsString;
                    if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                       begin
                       end;
                    fdquerysql6.Next;
                  end;
            end;
            // APÓS MUDAR A TABELA DE ENTIDADES, DEVE-SE MUDAR TAMBÉM A TABELA ENDER_ENT ONDE SE GRAVA ENDEREÇOS DA ENTIDADE, QUANDO O
            // ENDEREÇO DE COBRANÇA NÃO É O MESMO
            fdquerysql5.first;
            while not fdquerysql5.eof do
            begin
               vnomedistrito:=fdquerysql4.FieldByName('CIDADEAPOLO').AsString;
               tamanhocampobairro:=fdquerysql5.FieldByName('enderentbair').Size;
               if vnovobairro = '' then
                  vnovobairro:=fdquerysql5.FieldByName('enderentbair').AsString+'   ('+vnomedistrito+')';
               if length(vnovobairro) > tamanhocampobairro then
                  begin
                     messagedlg('TAMANHO DO NOME DO BAIRRO MAIS O DISTRITO EXCEDE O TAMANHO DO CAMPO BAIRRO',mterror,[mbok],0);
                     vnovobairromenor:=inputbox('Nome Bairro mais Distrito','',vnovobairro);
                     vnovobairro:=vnovobairromenor;
                  end
               else
                  begin
                     {AO PROCEDER AS ALTERAÇÕES, ALGUMAS COISAS JÁ DEVE SER TRATADAS CONFORME SEGUE:
                     1 - OS ENDEREÇOS DEVEM SER SALVOS TODOS EM MAIÚSCULOS PARA MANTER O PADRÃO ADOTADO NA RCC
                     2 - DEVE-SE CHECAR O LOGRADOURO E JÁ GRAVA-LO CORRETAMENTE NO CAMPO DA TABELA ENDER_ENT
                     3 - DEVE-SE LIMPAR O CAMPO ENDER_ENT REMOVENDO O LOGRADOURO QUANDO NECESSÁRIO
                     4 - DEVE-SE TAMBÉM GRAVAR O CAMPO ENDERENTBAIR TODO EM CAIXA ALTA E ADICIONAR O DISTRITO CONFORME
                         REALIZADO NO CAMPO ENT_BAIR DA TABELA DE ENTIDADE
                     5 - DEVE-SE TAMBÉM TRATAR O CAMPO CEP REMOVENDO O - DOS REGISTROS, GRAVANDO TODOS SEM A FORMATAÇÃO
                         DO CAMPO, MANTENDO O PADRÃO DA TABELA DE ENTIDADES
                     }
                     // PARTE 1 E 5 - CONVERTENDO TODOS OS CAMPOS PARA MAIUSCULO E JÁ REMOVENDO O - DO CAMPO CEP DEIXANDO
                     // PADRÃO COMO NA ENTIDADE
                     sql:='UPDATE ender_ent SET enderent = upper(enderent), enderentcomp = upper(enderentcomp), enderentbair = upper(enderentbair),';
                     sql:=sql+' enderentcep = REPLACE(EnderEntCep,'+quotedstr('-')+', '+quotedstr('')+') ';
                     fdquerysql3.Close;
                     fdquerysql3.SQL.Clear;
                     fdquerysql3.SQL.Text := sql;
                     if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                        begin
                        end;
                     // PARTE 2 E 3 - CHECAR LOGRADOURO DO CAMPO ENDERENT E GRAVÁ-LO NO LUGAR CERTO JÁ LIMPANDO
                     // O CAMPO ENDERENT REMOVENDO O LOGRADOURO DELE
                     sql:='UPDATE ender_ent SET tipologradabrev = :tipologradabrev, enderent =  upper(substring(enderent,4,len(enderent)-3))';
                     sql:=sql+' WHERE SUBSTRING(EnderEnt,1,3) = :tipologradouro';
                     fdquerysql3.Close;
                     fdquerysql3.SQL.Clear;
                     fdquerysql3.SQL.Text := sql;
                     fdquerysql3.ParamByName('tipologradabrev').AsString :='R';
                     fdquerysql3.ParamByName('tipologradouro').AsString := 'Rua';
                     if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                        begin
                        end;
                     sql:='UPDATE ender_ent SET tipologradabrev = :tipologradabrev, enderent =  upper(substring(enderent,4,len(enderent)-3))';
                     sql:=sql+' WHERE SUBSTRING(EnderEnt,1,3) = :tipologradouro';
                     fdquerysql3.Close;
                     fdquerysql3.SQL.Clear;
                     fdquerysql3.SQL.Text := sql;
                     fdquerysql3.ParamByName('tipologradabrev').AsString :='Av';
                     fdquerysql3.ParamByName('tipologradouro').AsString := 'Av';
                     if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                        begin
                        end;
                     sql:='UPDATE ender_ent SET tipologradabrev = :tipologradabrev, enderent = upper(ltrim(substring(enderent,8,len(enderent)-7)))';
                     sql:=sql+' WHERE  substring(enderent,1,7) = :tipologradouro';
                     fdquerysql3.Close;
                     fdquerysql3.SQL.Clear;
                     fdquerysql3.SQL.Text := sql;
                     fdquerysql3.ParamByName('tipologradabrev').AsString :='Av';
                     fdquerysql3.ParamByName('tipologradouro').AsString := 'Avenida';
                     if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                        begin
                        end;
                     sql:='UPDATE ender_ent SET tipologradabrev = :tipologradabrev, enderent=upper(ltrim(substring(enderent,4,len(enderent)-3)))';
                     sql:=sql+' WHERE  substring(enderent,1,3) = :tipologradouro';
                     fdquerysql3.Close;
                     fdquerysql3.SQL.Clear;
                     fdquerysql3.SQL.Text := sql;
                     fdquerysql3.ParamByName('tipologradabrev').AsString := 'Av';
                     fdquerysql3.ParamByName('tipologradouro').AsString:='Av.';
                     if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                        begin
                        end;
                     sql:='UPDATE ender_ent SET tipologradabrev = :tipologradabrev, enderent=upper(ltrim(substring(enderent,8,len(enderent)-7)))';
                     sql:=sql+' WHERE  substring(enderent,1,7) = :tipologradouro';
                     fdquerysql3.Close;
                     fdquerysql3.SQL.Clear;
                     fdquerysql3.SQL.Text := sql;
                     fdquerysql3.ParamByName('tipologradabrev').AsString := 'Al';
                     fdquerysql3.ParamByName('tipologradouro').AsString:='ALAMEDA';
                     if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                        begin
                        end;
                     sql:='UPDATE ender_ent SET tipologradabrev = '+quotedstr('Pç')+', enderent=upper(ltrim(substring(enderent,6,len(enderent)-5)))';
                     sql:=sql+' WHERE  substring(enderent,1,5) = '+quotedstr('PRAÇA');
                     fdquerysql3.Close;
                     fdquerysql3.SQL.Clear;
                     fdquerysql3.SQL.Text := sql;
                     fdquerysql3.ParamByName('tipologradabrev').AsString := 'Pç';
                     fdquerysql3.ParamByName('tipologradouro').AsString:='PRAÇA';
                     if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                        begin
                        end;
                     // PARTE 4 - DEVE-SE TAMBÉM GRAVAR O CAMPO ENDERENTBAIR TODO EM CAIXA ALTA E ADICIONAR O DISTRITO CONFORME
                     //    REALIZADO NO CAMPO ENT_BAIR DA TABELA DE ENTIDADE
                    sql:='UPDATE ender_ent SET cidcod = :cidcod, enderentbair = :entbair';
                    sql:=sql+' WHERE entcod =:entcod ';
                    sql:=sql+' AND   cidcod =:cidcodbusca ';
                    fdquerysql3.Close;
                    fdquerysql3.SQL.Clear;
                    fdquerysql3.SQL.Text := sql;
                    fdquerysql3.parambyname('cidcod').asstring:=lblcidadecidade.Text;
                    fdquerysql3.parambyname('entbair').asstring:= vnovobairro;
                    fdquerysql3.parambyname('entcod').asstring := fdquerysql5.fieldbyname('entcod').asstring;
                    fdquerysql3.parambyname('cidcodbusca').asstring := fdquerysql4.fieldbyname('cidcod').asstring;
                    if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                       begin
                       end;
                       fdquerysql5.Next;
                  end;
            end;
            // ALTERAÇÕES NA TABELA DE CEP
            fdquerysql12.First;
            while not fdquerysql12.Eof  do
            begin
               vcep:=fdquerysql12.FieldByName('cepcod').AsString;
               sql:='UPDATE cep SET cidcod = :cidade';
               sql:=sql+' WHERE cidcod = :cidcod';
               fdquerysql3.Close;
               fdquerysql3.SQL.Clear;
               fdquerysql3.SQL.Text := sql;
               fdquerysql3.parambyname('cidade').asstring := lblcidadecidade.Text;
               fdquerysql3.ParamByName('cidcod').AsString := fdquerysql4.FieldByName('cidcod').AsString;
               if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                  begin
                  end;
               fdquerysql12.Next;
            end;
            // DEPOIS DE MUDAR AS ENTIDADES E CEP´S ERRADOS, DEVE-SE REMOVER O DISTRITO DA TABELA DE CIDADES DO APOLO
            sql:='DELETE FROM cidade WHERE cidcod = :cidcod';
            fdquerysql3.Close;
            fdquerysql3.sql.clear;
            fdquerysql3.sql.Text := sql;
            fdquerysql3.parambyname('cidcod').asstring:=fdquerysql4.FieldByName('cidcod').AsString;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  messagedlg('DISTRITO-CIDADE REMOVIDO COM SUCESSO DA BASE, DADOS AGORA NA CIDADE DE '+lblcidadecidade.Text+'-'+lblnomecidade.Caption,mtinformation,[mbok],0);
                  gridcidadesedistritos.SetFocus;
                  spblimpar.click;
                  exit;
               end;
         end
      else
         begin
            gridentidades.SetFocus;
            exit;
         end;
   end;
end;

procedure Tfrmdistritocidades.spbfiltracepClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      sql:='SELECT cep.cepcod,cep.cepnomeloc,cep.tipologradabrev,cep.cependerloc,cep.CepEnderLocComp,cep.cidcod,cid.cidnomecomp,cid.ufsigla';
      sql:=sql+' FROM cep with(nolock)';
      sql:=sql+' INNER JOIN cidade cid with(nolock) ON cep.cidcod = cid.CidCod';
      sql:=sql+' WHERE CEP.CidCod = :cidcod';
      fdquerysql12.Close;
      fdquerysql12.sql.Clear;
      fdquerysql12.sql.Text := sql;
      fdquerysql12.parambyname('cidcod').AsString :=fdquerysql4.fieldbyname('cidcod').asstring;
      if executaracao(fdquerysql12, fdbanco, true, dtsfdquerysql3) then
         begin
            gridcepsvinculados.DataSource:= dtsfdquerysql12;
            gridcepsvinculados.Refresh;
         end
      else
         begin
            messagedlg('NÃO HÁ CEP´S VINCULADOS A ESTE DISTRITO !!!',mtwarning,[mbok],0);
         end;
   end;
end;

procedure Tfrmdistritocidades.spbfiltraentidadesClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      sql:='SELECT e.entcod,e.entnome,e.entcpfcgc,e.entrgie,cid.cidcod,cid.cidnomecomp,cid.ufsigla,e.entbair';
      sql:=sql+' FROM ENTIDADE e with(nolock)';
      sql:=sql+' INNER JOIN cidade cid with(nolock) ON e.cidcod = cid.cidcod';
      sql:=sql+' WHERE e.cidcod = :cidcod';
      fdquerysql6.Close;
      fdquerysql6.sql.Clear;
      fdquerysql6.sql.Text := sql;
      fdquerysql6.parambyname('cidcod').asstring :=fdquerysql4.FieldByName('cidcod').AsString;
      if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
         begin
            gridentidades.DataSource:=dtsfdquerysql6;
            gridentidades.Refresh;
         end
      else
         begin
            messagedlg('NÃO HÁ ENTIDADES VINCULADAS A ESTE DISTRITO !!!',mtwarning,[mbok],0);
         end;
      //
      sql:='SELECT * ';
      sql:=sql+' FROM ENDER_ENT ee with(nolock)';
      sql:=sql+' WHERE ee.CidCod = :cidcod';
      fdquerysql5.Close;
      fdquerysql5.SQL.Clear;
      fdquerysql5.SQL.Text:=sql;
      fdquerysql5.ParamByName('cidcod').AsString := fdquerysql4.FieldByName('cidcod').AsString;
      if executaracao(fdquerysql5, fdbanco, true, dtsfdquerysql5) then
         begin
            gridendercomp.datasource:=dtsfdquerysql5;
            gridendercomp.refresh;
         end;
   end;
end;

procedure Tfrmdistritocidades.spbfiltrarClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      sql:='SELECT cid.CidCod,cid.CidCodMunDipj IBGEAPOLO,substring(ua.codigo_ibge,1,15) as IBGESITE,';
      sql:=sql+'   substring(cid.CidNomeComp,1,38) as CIDADEAPOLO,cid.UfSigla ,substring(ua.cidade,1,45) as CIDADEIBGE,UA.estado';
      sql:=sql+'   FROM CIDADE cid ';
      sql:=sql+'   LEFT JOIN USERIBGE_ATUALIZADO ua ON ua.codigo_ibge=cid.CidCodMunDipj';
      sql:=sql+'   WHERE cid.CidNomeComp NOT LIKE SUBSTRING(ua.cidade,1,3)+ '+quotedstr('%');
      fdquerysql4.Close;
      fdquerysql4.SQL.Clear;
      fdquerysql4.SQL.Text := sql;
      if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
         begin
            gridcidadesedistritos.datasource:=dtsfdquerysql4;
            configura_grid('DISTRITOCIDADES',frmdistritocidades,frmlogon.nomeusuario,'gridcidadesedistritos',gridcidadesedistritos,modulo_dados.dtsfdquerysql);
            lblqtdnreg.Caption:= inttostr(fdquerysql4.RecordCount);
            lblqtdnreg.Refresh;
            gridcidadesedistritos.refresh;
         end;
   end;
end;

procedure Tfrmdistritocidades.spblimparClick(Sender: TObject);
begin
   lblcidadecidade.Clear; lblnomecidade.Caption :='....';
   with modulo_dados do
   begin
      fdquerysql6.active:=false;
      fdquerysql12.Active:=false;
   end;
   spbfiltrar.Click;
end;

function lista_entidades(cidcod : string) : string;
begin
   with modulo_dados,frmdistritocidades do
   begin
      sql:='SELECT e.entcod,e.entnome,cid.cidnomecomp,cid.ufsigla';
      sql:=sql+' FROM entidade e with(nolock)';
      sql:=sql+' INNER JOIN cidade cid with(nolock) ON e.cidcod = cid.cidcod';
      sql:=sql+' WHERE e.cidcod = :cidcod';
      fdquerysql1.Close;
      fdquerysql1.SQL.Clear;
      fdquerysql1.SQL.Text := sql;
      fdquerysql1.ParamByName('cidcod').AsString := sql;
      if executaracao(fdquerysql1, fdbanco, true, dtsfdquerysql1) then
         begin
            gridentidades.DataSource:=dtsfdquerysql1;
            gridentidades.Refresh;
         end;
   end;
end;

function lista_ceps(cidcod : string) : string;
begin
   with modulo_dados, frmdistritocidades do
   begin
      sql:='';
   end;
end;

procedure Tfrmdistritocidades.spbretornarClick(Sender: TObject);
begin
   close;
end;

procedure Tfrmdistritocidades.spbuscacidadeClick(Sender: TObject);
var i:integer;
begin
   with modulo_dados do
   begin
      SQL:='SELECT cid.CidCod, cid.CidNomeComp, cid.ufsigla FROM CIDADE cid with(nolock) ORDER BY cid.cidnomecomp ASC,cid.UfSigla ASC';
      fdquerysql8.Close;
      fdquerysql8.sql.clear;
      fdquerysql8.SQL.Text:=sql;
      if executaracao(fdquerysql8, fdbanco, true, dtsfdquerysql8) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            frmconsulta3.controle := 'CIDADE_CIDADE';
            dtsfdquerysql8.DataSet := fdquerysql8;
            frmconsulta3.gridconsulta.DataSource := dtsfdquerysql8;
            for i:= 0 to fdquerysql8.fields.count -1 do
            begin
               frmconsulta3.cbocampo.items.add(fdquerysql8.fields[i].displayname);
               frmconsulta3.cbordem.items.add(fdquerysql8.fields[i].displayname);
            end;
            frmconsulta3.gridconsulta.Refresh;
            frmconsulta3.ShowModal;
         end
      else
         begin
            messagedlg('TABELA DE CIDADES ESTÁ VAZIA !!!',mtwarning,[mbok],0);
            exit;
         end;
   end;
end;

end.
