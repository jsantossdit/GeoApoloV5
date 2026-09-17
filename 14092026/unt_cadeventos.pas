unit unt_cadeventos;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.ComCtrls, Vcl.StdCtrls, Vcl.Buttons,
  Vcl.ExtCtrls, Data.DB, Vcl.Grids, Vcl.DBGrids, Vcl.Mask,
  unt_cadeventos_types, unt_cadeventos_repository, unt_cadeventos_service;

type
  Tfrmcadeventos = class(TForm)
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spbpesquisa: TSpeedButton;
    spbsair: TSpeedButton;
    spblimpar: TSpeedButton;
    lblsair: TLabel;
    spbexcluir: TSpeedButton;
    StatusBar1: TStatusBar;
    GroupBox1: TGroupBox;
    lblidevento: TLabeledEdit;
    lbldescricaoevento: TLabeledEdit;
    lbldatainicial: TLabel;
    mskdtinicial: TMaskEdit;
    mskdtfinal: TMaskEdit;
    lbldtfinal: TLabel;
    lbltemaprincipal: TLabeledEdit;
    lbltipoevento: TLabeledEdit;
    lbltipoevento_descricao: TLabel;
    spbconsulta: TSpeedButton;
    lblobservacoes: TLabel;
    memobservacoes: TMemo;
    grideventos: TDBGrid;
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbsairClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure lbldescricaoeventoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure mskdtinicialKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure mskdtfinalKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lbltemaprincipalKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lbltipoeventoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure memobservacoesKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spblimparClick(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure spbexcluirClick(Sender: TObject);
    procedure spbpesquisaClick(Sender: TObject);
    procedure spbconsultaClick(Sender: TObject);
    procedure grideventosDblClick(Sender: TObject);
    procedure spbsalvarClick(Sender: TObject);
    procedure grideventosKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  frmcadeventos: Tfrmcadeventos;
  controle:string;

function mostra_eventos_cadastrados(tema_principal : string) : string; export;

implementation

{$R *.dfm}

uses funcoes, unt_dados, unt_logon, unt_principal, unt_consultav3;

procedure Tfrmcadeventos.FormActivate(Sender: TObject);
begin
   with modulo_dados do
   begin
     statusbar1.panels[1].text := configura_statusbar('s');
     statusbar1.panels[3].text := statusbar1.panels[1].text;
     lblidevento.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_eventos','Sim');
     mostra_eventos_cadastrados('');
     controle:='INCLUSÃO';
     lblidevento.refresh; lbldescricaoevento.SetFocus;
   end;
end;

procedure Tfrmcadeventos.FormClose(Sender: TObject; var Action: TCloseAction);
begin
   action:=cafree;
end;

procedure Tfrmcadeventos.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f10  then
      spbsair.Click;
end;

procedure Tfrmcadeventos.grideventosDblClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      controle:='ALTERAÇÃO';
     lblidevento.Text := fdquerysql4.FieldByName('idevento').AsString;
     lbldescricaoevento.Text := fdquerysql4.FieldByName('descricao').asstring;
     mskdtinicial.Text := copy(fdquerysql4.FieldByName('data_inicial').Asstring,9,2)+'/'+copy(fdquerysql4.FieldByName('data_inicial').Asstring,6,2)+'/'+copy(fdquerysql4.FieldByName('data_inicial').Asstring,1,4);
     mskdtfinal.Text := copy(fdquerysql4.FieldByName('data_final').Asstring,9,2)+'/'+copy(fdquerysql4.FieldByName('data_final').Asstring,6,2)+'/'+copy(fdquerysql4.FieldByName('data_final').Asstring,1,4);
     lbltemaprincipal.Text := fdquerysql4.FieldByName('tema_principal').AsString;
     memobservacoes.Text := fdquerysql4.FieldByName('observacoes').AsString;
     lbltipoevento.Text := fdquerysql4.FieldByName('tipoeventcod').AsString;
     sql:='SELECT descricao_tipoevento FROM USER_geoapolo_tipo_eventos WHERE tipoeventcod = :tipodeevento';
     fdquerysql8.Close;
     fdquerysql8.SQL.Clear;
     fdquerysql8.SQL.Text := sql;
     fdquerysql8.ParamByName('tipodeevento').AsString :=  lbltipoevento.Text;
     if executaracao(fdquerysql8,fdbanco, true, dtsfdquerysql8) then
        lbltipoevento_descricao.Caption := fdquerysql8.FieldByName('descricao_tipoevento').AsString
     else
        begin
          lbltipoevento_descricao.Caption := 'TIPO DE EVENTO NÃO ENCONTRADO !!!';
          lbltipoevento_descricao.Refresh;
        end;
     lbldescricaoevento.SetFocus;
   end;
end;

procedure Tfrmcadeventos.grideventosKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_delete then
      begin
        with modulo_dados do
        begin
          frmprincipal.resp:=messagedlg('Confirma a Remoção deste Evento ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
          if frmprincipal.resp = idyes  then
             begin
               messagedlg('LEMBRANDO QUE PARA REMOVER O EVENTO ELE NÃO PODE TER NENHUMA INFORMAÇÃO VINCULADA A ELE',mtinformation,[mbok],0);
               sql:='DELETE FROM USER_geoapolo_eventos WHERE idevento = :idevento';
               fdquerysql3.Close;
               fdquerysql3.sql.Clear;
               fdquerysql3.sql.Text := sql;
               fdquerysql3.parambyname('idevento').asstring := fdquerysql4.FieldByName('idevento').AsString;

               if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                  begin
                    messagedlg('EVENTO REMOVIDO COM SUCESSO !!!',mtinformation,[mbok],0);
                    spblimpar.Click;
                    mostra_eventos_cadastrados('');
                    lblidevento.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_eventos','N');
                    lblidevento.Refresh;
                  end
               else
                  begin
                    messagedlg('ERRO AO TENTAR REMOVER O EVENTO !!!',mterror,[mbok],0);
                    lbldescricaoevento.SetFocus;
                  end;
             end;
        end;
      end;
end;

procedure Tfrmcadeventos.lbldescricaoeventoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      mskdtinicial.SetFocus;
end;

procedure Tfrmcadeventos.lbltemaprincipalKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lbltipoevento.SetFocus;
end;

procedure Tfrmcadeventos.lbltipoeventoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      memobservacoes.SetFocus;
   if key = vk_f4 then
      spbconsulta.Click;
end;

procedure Tfrmcadeventos.memobservacoesKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) then
      spbsalvar.Click;
end;

procedure Tfrmcadeventos.mskdtfinalKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lbltemaprincipal.SetFocus;
end;

procedure Tfrmcadeventos.mskdtinicialKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      mskdtfinal.SetFocus;
end;

procedure Tfrmcadeventos.spbconsultaClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      sql:='SELECT * FROM USER_geoapolo_tipo_eventos';
      fdquerysql7.Close;
      fdquerysql7.SQL.Clear;
      fdquerysql7.SQL.Text := sql;
      if executaracao(fdquerysql7, fdbanco, true, dtsfdquerysql7) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            with frmconsulta3 do
            begin
               frmconsulta3.controle :='TIPO_EVENTOS';
               gridconsulta.DataSource := dtsfdquerysql7;
               frmconsulta3.ShowModal;
            end;
         end;
   end;
end;

procedure Tfrmcadeventos.spbexcluirClick(Sender: TObject);
begin
   messagedlg('PARA REMOVER UM EVENTO, SELECIONE-O NO GRID ABAIXO E PRESISONE DELETE !!!',mtinformation,[mbok],0);
   grideventos.SetFocus;
end;

procedure Tfrmcadeventos.spbpesquisaClick(Sender: TObject);
begin
   mostra_eventos_cadastrados(inputbox('Informe o Tema Principal ou parte com o símbolo % antes e depois da parte do tema','Tema do Evento',''));
end;

procedure Tfrmcadeventos.spblimparClick(Sender: TObject);
begin
   lbldescricaoevento.Clear; mskdtinicial.Clear; mskdtfinal.Clear; lbltemaprincipal.Clear;
   memobservacoes.Clear; lbltipoevento.Clear;
end;

procedure Tfrmcadeventos.spbsairClick(Sender: TObject);
begin
   close;
end;

procedure Tfrmcadeventos.spbsalvarClick(Sender: TObject);
begin
   with modulo_dados do
   begin
     if lbldescricaoevento.Text = '' then
        begin
           messagedlg('NÃO É POSSÍVEL ATUALIZAR OU INSERIR UM EVENTO SEM DESCRIÇÃO !!!',mterror,[mbok],0);
           lbldescricaoevento.SetFocus;
        end;
     if mskdtfinal.Text = '  /  /    ' then
        begin
          messagedlg('NÃO É PERMITIDO INSERIR UM EVENTO SEM SUA DATA DE TÉRMINO !!!',mterror,[mbok],0);
          mskdtfinal.SetFocus;
        end;
     if mskdtinicial.Text = '  /  /    ' then
        begin
          mskdtinicial.text := mskdtfinal.Text;
          mskdtinicial.Refresh;
        end;
     frmprincipal.resp:=messagedlg('CONFIRMA A '+controle+' PARA ESTE EVENTO ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
     if frmprincipal.resp = idyes  then
        begin
           if controle = 'INCLUSÃO' then
              begin
                 sql:='INSERT INTO USER_geoapolo_eventos (idevento,descricao,data_inicial,data_final,tema_principal,tipoeventcod,observacoes)';
                 sql:=sql+' VALUES (:idevento, :descricaoevento, :datainicial, :datafinal, :temaprincipal, :codigotipoevento, :observacoesevento)';
              end
           else if controle = 'ALTERAÇÃO' then
              begin
                sql:='UPDATE USER_geoapolo_eventos SET descricao = :descricaoevento, data_inicial = :datainicial, data_final = :datafinal,';
                sql:=sql+' tema_principal = :temaprincipal, tipoeventcod = :codigotipoevento, observacoes = :observacoesevento';
                sql:=sql+' WHERE idevento = :idevento ';
              end;
           fdquerysql3.Close;
           fdquerysql3.SQL.Clear;
           fdquerysql3.SQL.Text := sql;
           fdquerysql3.ParamByName('idevento').asstring := lblidevento.Text;
           fdquerysql3.ParamByName('descricaoevento').AsString := lbldescricaoevento.text ;
           fdquerysql3.ParamByName('datainicial').AsString := formatdatetime('yyyy-MM-dd',strtodatetime(mskdtinicial.Text));
           fdquerysql3.ParamByName('datafinal').AsString :=formatdatetime('yyyy-MM-dd',strtodatetime(mskdtfinal.Text));
           fdquerysql3.ParamByName('temaprincipal').AsString := lbltemaprincipal.Text;
           fdquerysql3.ParamByName('codigotipoevento').AsString := lbltipoevento.Text;
           fdquerysql3.ParamByName('observacoesevento').AsString := memobservacoes.Text ;

           if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
              begin
                 messagedlg('Operação de '+controle+' deste Evento concluído com sucesso !!!',mtinformation,[mbok],0);
                 spblimpar.Click;
                 controle:='INCLUSÃO';
                 lblidevento.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_eventos','Sim');
                 mostra_eventos_cadastrados('');
                 lblidevento.Refresh; lbldescricaoevento.SetFocus;
              end
           else
              begin
                messagedlg('ERRO AO TENTAR REALIZAR A OPERAÇÃO DE : '+controle+' PARA ESTE EVENTO',mterror,[mbok],0);
                lbldescricaoevento.SetFocus;
                exit;
              end;
        end
     else
        begin
          lbldescricaoevento.SetFocus;
          exit;
        end;

   end;
end;

function mostra_eventos_cadastrados(tema_principal : string) : string;
begin
   with modulo_dados, frmcadeventos do
   begin
     if tema_principal = '' then
        begin
          sql:='SELECT uge.idevento,uge.descricao,uge.data_inicial,uge.data_final, uge.tema_principal, uge.tipoeventcod,uge.observacoes,';
          sql:=sql+' ugte.descricao_tipoevento, uge.entcod_coordenador_principal, ugent.geoentnome';
          sql:=sql+' FROM USER_geoapolo_eventos uge';
          sql:=sql+' INNER JOIN USER_geoapolo_tipo_eventos ugte with(nolock) ON uge.tipoeventcod= ugte.tipoeventcod';
          sql:=sql+' LEFT JOIN USER_geoapolo_entidade ugent with(nolock) ON  uge.entcod_coordenador_principal = ugent.entcod';
          sql:=sql+' ORDER BY uge.data_inicial DESC';
          fdquerysql4.Close;
          fdquerysql4.SQL.Clear;
          fdquerysql4.SQL.Text := sql;
          if executaracao(fdquerysql4, fdbanco, false, dtsfdquerysql4) then
             begin
               grideventos.datasource:= dtsfdquerysql4;
               grideventos.refresh; lbldescricaoevento.SetFocus;
             end;
        end
     else if tema_principal <> ''  then
        begin
          sql:='SELECT uge.idevento,uge.descricao,uge.data_inicial,uge.data_final, uge.tema_principal, uge.tipoeventcod,uge.observacoes,';
          sql:=sql+' ugte.descricao_tipoevento, uge.entcod_coordenador_principal, ugent.geoentnome';
          sql:=sql+' FROM USER_geoapolo_eventos uge';
          sql:=sql+' INNER JOIN USER_geoapolo_tipo_eventos ugte with(nolock) ON uge.tipoeventcod= ugte.tipoeventcod';
          sql:=sql+' LEFT JOIN USER_geoapolo_entidade ugent with(nolock) ON  uge.entcod_coordenador_principal = ugent.entcod';
          sql:=sql+' WHERE uge.tema_principal like :tema_principal';
          sql:=sql+' ORDER BY uge.data_inicial DESC';
          fdquerysql4.Close;
          fdquerysql4.SQL.Clear;
          fdquerysql4.SQL.Text := sql;
          fdquerysql4.ParamByName('temaprincipal').AsString :=  tema_principal;
          if executaracao(fdquerysql4, fdbanco, false, dtsfdquerysql4) then
              begin
               grideventos.datasource:= dtsfdquerysql4;
               grideventos.refresh; lbldescricaoevento.SetFocus;
             end;
        end;
   end;
end;

end.
