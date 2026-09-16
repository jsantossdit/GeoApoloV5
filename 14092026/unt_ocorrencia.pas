unit unt_ocorrencia;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, ComCtrls, StdCtrls, Buttons, ExtCtrls, Grids, DBGrids, Mask,
  DBCtrls, Menus, ImgList, Data.DB;

type
  Tfrmocorrencia = class(TForm)
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spblimpar: TSpeedButton;
    spbdeletar: TSpeedButton;
    spbnovaocorrencia: TSpeedButton;
    spbsair: TSpeedButton;
    lblmsg2: TLabel;
    StatusBar1: TStatusBar;
    grpocorrencia: TGroupBox;
    lblcodocorrencia: TLabeledEdit;
    lbldataocorrencia: TLabel;
    mskdtocorrencia: TMaskEdit;
    lblareasdisponiveis: TLabel;
    cboareadisponivel: TComboBox;
    lblmotivocorr: TLabel;
    cbomotivoocorrencia: TComboBox;
    lbltexto_ocorr: TLabel;
    lblresponsavel_solucao: TLabel;
    gridocorrencias: TDBGrid;
    rdgpendente: TRadioButton;
    rdgemandamento: TRadioButton;
    rdgcancelado: TRadioButton;
    rdgresolvido: TRadioButton;
    cboresponsavel_solucao: TComboBox;
    rdgtodas: TRadioButton;
    grpcancelamento: TGroupBox;
    Label1: TLabel;
    lblresponsavel: TLabeledEdit;
    mskdtcanc: TMaskEdit;
    lblmotivocancelamento: TLabeledEdit;
    btnok: TBitBtn;
    btncancelar: TBitBtn;
    memosolicitacao: TRichEdit;
    rdgtransferido: TRadioButton;
    PopupMenu1: TPopupMenu;
    GravaConfiguraes1: TMenuItem;
    pgcontrol: TPageControl;
    tab_ocorrencia: TTabSheet;
    tab_solucao: TTabSheet;
    memojadigitado: TMemo;
    memosolucao: TMemo;
    lblinsert: TLabel;
    lbldblclick: TLabel;
    Label2: TLabel;
    lblorigcodestr: TLabeledEdit;
    lblorigdescr: TLabel;
    spbconsulta: TSpeedButton;
    lblsolicitante: TLabeledEdit;
    spbuscasolicitante: TSpeedButton;
    lblsolicitantenome: TLabel;
    pnlfechamento: TPanel;
    GroupBox1: TGroupBox;
    procedure spbsairClick(Sender: TObject);
    procedure FormKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormActivate(Sender: TObject);
    procedure cbomotivoocorrenciaEnter(Sender: TObject);
    procedure cboresponsavel_solucaoEnter(Sender: TObject);
    procedure cbomotivoocorrenciaKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cboareadisponivelKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cboresponsavel_solucaoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure cbosolicitanteKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure memosolicitacaoEnter(Sender: TObject);
    procedure memosolicitacaoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spblimparClick(Sender: TObject);
    procedure spbsalvarClick(Sender: TObject);
    procedure rdgpendenteClick(Sender: TObject);
    procedure rdgemandamentoClick(Sender: TObject);
    procedure rdgcanceladoClick(Sender: TObject);
    procedure rdgresolvidoClick(Sender: TObject);
    procedure rdgtodasClick(Sender: TObject);
    procedure gridocorrenciasDblClick(Sender: TObject);
    procedure btnokClick(Sender: TObject);
    procedure btncancelarClick(Sender: TObject);
    procedure mskdtcancKeyDown(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure rdgtransferidoClick(Sender: TObject);
    procedure GravaConfiguraes1Click(Sender: TObject);
    procedure spbnovaocorrenciaClick(Sender: TObject);
    procedure gridocorrenciasDrawColumnCell(Sender: TObject; const Rect: TRect;
      DataCol: Integer; Column: TColumn; State: TGridDrawState);
    procedure lblorigcodestrKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblsolicitanteKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbuscasolicitanteClick(Sender: TObject);
    procedure spbconsultaClick(Sender: TObject);
    procedure mskdtocorrenciaKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  frmocorrencia: Tfrmocorrencia;
  sql,sql2,codigo_ocorrencia,controle:string;
  resp:word;

function mostra_ocorrencias(status : string) : string; export;

implementation

uses funcoes, unt_dados, unt_logon, unt_principal, unt_consultav3;

{$R *.dfm}

procedure Tfrmocorrencia.spbsairClick(Sender: TObject);
begin
   close;
end;

procedure Tfrmocorrencia.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f10 then
      spbsair.Click;
   if key = vk_delete then
      begin
         with modulo_dados do
         begin
            grpcancelamento.Visible := true;
            grpcancelamento.Top :=352;
            grpcancelamento.Left :=288;
            mskdtcanc.Text := datetostr(date);
            lblresponsavel.text := frmlogon.nomeusuario ;
            lblresponsavel.Refresh;
            mskdtcanc.SetFocus;
         end;
      end;
   if key = vk_insert then
      begin
         spblimpar.Click;
         controle:='INCLUSÃO';
         statusbar1.panels[1].text := controle;
         statusbar1.Refresh;
         lblsolicitante.SetFocus;
      end;
end;

procedure Tfrmocorrencia.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
   action:=cafree;
end;

procedure Tfrmocorrencia.FormActivate(Sender: TObject);
begin
   statusbar1.Panels[0].Text := 'Banco Apolo';
   statusbar1.Panels[1].Text := configura_statusbar('a');
   controle:='INCLUSÃO';
   with modulo_dados do
   begin
      // ÁREA DISPONIVEL PARA SOLICITACAO  - BASEADO NOS GRUPOS CRIADOS DENTRO DOS MOTIVOS DE OCORRÊNCIA DO APOLO
      // POSTERIORMENTE DEVE SER ADAPTADA ESSA ROTINA PARA FUNCIONAMENTO SOMENTE NO GEOAPOLO
      sql:='SELECT MotOcorDescr';
      sql:=sql+' FROM motivo_ocor';
      sql:=sql+' WHERE MotOcorGrupo = :grupo_ocorrencia';//+quotedstr('T');
      sql:=sql+' ORDER by MotOcorDescr ASC';
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := sql;
      fdquerysql.ParamByName('grupo_ocorrencia').asstring := 'T';
      if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
         begin
            fdquerysql.First;
            while not fdquerysql.Eof do
            begin
               cboareadisponivel.Items.add(fdquerysql.fieldbyname('motocordescr').asstring);
               fdquerysql.Next;
            end;
            cboareadisponivel.Refresh;
         end;
      mskdtocorrencia.Text := datetostr(date);
      mskdtocorrencia.Refresh;
      pgcontrol.ActivePageIndex :=0;
      mostra_ocorrencias('');
      frmocorrencia.Refresh;
      configura_grid('OCORRENCIA',frmocorrencia,frmlogon.codigousuario,'gridocorrencias',frmocorrencia.gridocorrencias,modulo_dados.dtsfdquerysql4);
      rdgpendente.Checked := true;
      lblsolicitante.SetFocus;
   end;
end;

procedure Tfrmocorrencia.cbomotivoocorrenciaEnter(Sender: TObject);
begin
   with modulo_dados do
   begin
      if cboareadisponivel.Text = '' then
         begin
            messagedlg('PARA ESCOLHER UM MOTIVO DA OCORRÊNCIA PRIMEIRO SELECIONE A ÁREA DISPONÍVEL POR FAVOR ',mterror,[mbok],0);
            cboareadisponivel.SetFocus;
            exit;
         end
      else if (cboareadisponivel.Text <> '') then
         begin
            sql:='select MotOcorCodEstr from motivo_ocor';
            sql:=sql+' where MotOcorGrupo = :grupo_ocorrencia';
            sql:=sql+' and   MotOcorDescr = :arearesponsavel';
            fdquerysql.Close;
            fdquerysql.SQL.Clear;
            fdquerysql.SQL.Text := sql;
            fdquerysql.ParamByName('grupo_ocorrencia').AsString := 'T';
            fdquerysql.ParamByName('arearesponsavel').AsString := cboareadisponivel.Text;
            if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
               begin
                  sql:='select MotOcorDescr from motivo_ocor';
                  sql:=sql+' where motocorgrupo = :grupo' ;
                  sql:=sql+' and Motocorcodestr like :descricaoocorrencia';
                  fdquerysql.Close;
                  fdquerysql.SQL.Clear;
                  fdquerysql.SQL.Text := sql;
                  fdquerysql.ParamByName('grupo').AsString := 'F';
                  fdquerysql.ParamByName('descricaoocorrencia').AsString := fdquerysql.fieldbyname('motocorcodestr').asstring+'%';
                  if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
                     begin
                        cbomotivoocorrencia.Clear;
                        fdquerysql.First;
                        while not fdquerysql.Eof do
                        begin
                           cbomotivoocorrencia.Items.add(fdquerysql.fieldbyname('motocordescr').asstring);
                           fdquerysql.Next;
                        end;
                        if controle ='ALTERAÇÃO' then
                           begin
                              buscanacombo(fdquerysql4.fieldbyname('MotOcorDescr').asstring,frmocorrencia,cbomotivoocorrencia);
                              cbomotivoocorrencia.Refresh;
                           end;                                 
                     end;
                  cbomotivoocorrencia.Refresh;
               end;
         end;
   end;
end;

procedure Tfrmocorrencia.cboresponsavel_solucaoEnter(Sender: TObject);
var
   i:integer;
begin
   with modulo_dados do
   begin
      if cbomotivoocorrencia.Text = '' then
         begin
            messagedlg('PARA SELECIONAR UM RESPONSÁVEL PELA SOLUÇÃO, POR FAVOR SELECIONE O MOTIVO DA OCORRÊNCIA ANTES !!!',mterror,[mbok],0);
            cbomotivoocorrencia.SetFocus;
            exit;
         end
      else if cbomotivoocorrencia.Text <> '' then
         begin
            cboresponsavel_solucao.Clear;
            sql:='select MotOcorResp1, MotOcorResp2, MotOcorResp3';
            sql:=sql+' from motivo_ocor where MotOcorGrupo = :grupo';//+quotedstr('F');
            sql:=sql+' and   MotOcorDescr = :cbomotivo_ocorrencia';
            fdquerysql.close;
            fdquerysql.SQL.Clear;
            fdquerysql.sql.Text := sql;
            fdquerysql.ParamByName('grupo').AsString := 'F';
            fdquerysql.ParamByName('cbomotivo_ocorrencia').AsString := cbomotivoocorrencia.Text ;
            if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
               begin
                  cboresponsavel_solucao.Items.Add(fdquerysql.fieldbyname('MotOcorResp1').asstring);
                  cboresponsavel_solucao.Items.Add(fdquerysql.fieldbyname('MotOcorResp2').asstring);
                  cboresponsavel_solucao.Items.Add(fdquerysql.fieldbyname('MotOcorResp3').asstring);
                  cboresponsavel_solucao.ItemIndex :=0;
                  cboresponsavel_solucao.Refresh;
               end;
            if controle = 'ALTERAÇÃO' then
               begin
                  buscanacombo(fdquerysql4.fieldbyname('OcorRespSol').asstring,frmocorrencia,cboresponsavel_solucao);
                  cboresponsavel_solucao.Refresh;
               end;
         end;
   end;
end;

procedure Tfrmocorrencia.cbomotivoocorrenciaKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      lblorigcodestr.SetFocus;
end;

procedure Tfrmocorrencia.cboareadisponivelKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      cbomotivoocorrencia.SetFocus;
end;

procedure Tfrmocorrencia.cboresponsavel_solucaoKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      memosolicitacao.SetFocus;
end;

procedure Tfrmocorrencia.cbosolicitanteKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if (key= vk_tab) or (key = vk_return) then
      cboareadisponivel.SetFocus;
end;

procedure Tfrmocorrencia.memosolicitacaoEnter(Sender: TObject);
begin
   with modulo_dados do
   begin
      if controle <> 'INCLUSÃO' then
         begin
            if (fdquerysql4.fieldbyname('ocorstat').asstring = 'Cancelado') or (fdquerysql4.fieldbyname('ocorstat').asstring = 'Resolvido') or  (fdquerysql4.fieldbyname('ocorstat').asstring = 'Transferido') then
               begin
                  messagedlg('NÃO É PERMITIDO EDITAR UMA OCORRÊNCIA QUE FOI CANCELADA, TRANSFERIDA OU JÁ RESOLVIDA !!!',mterror,[mbok],0);
                  exit;
               end;
            if cboresponsavel_solucao.Text = '' then
               begin
                   messagedlg('NÃO FOI INFORMADO UM RESPONSÁVEL PELA SOLUÇÃO, E ESTE CAMPO É OBRIGATÓRIO !!!',mterror,[mbok],0);
               end;
         end;
   end;
end;

procedure Tfrmocorrencia.memosolicitacaoKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if (key = vk_escape) or (key = vk_f2) then
      spbsalvar.Click;
end;

procedure Tfrmocorrencia.spbconsultaClick(Sender: TObject);
var
   i:integer;
begin
   with modulo_dados do
   begin
      sql:='SELECT o.OrigCodEstr, o.OrigNome FROM ORIGEM o with(nolock) ORDER BY o.OrigCodEstr ASC'  ;
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := sql;
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
           application.CreateForm(tfrmconsulta3, frmconsulta3);
           frmconsulta3.controle := 'ORIGEMOCORRENCIA';

           frmconsulta3.gridconsulta.DataSource := dtsfdquerysql;
           for i:= 0 to fdquerysql.fields.count -1 do
           begin
              frmconsulta3.cbocampo.items.add(fdquerysql.fields[i].displayname);
              frmconsulta3.cbordem.items.add(fdquerysql.fields[i].displayname);
           end;
           frmconsulta3.gridconsulta.Refresh;
           frmconsulta3.ShowModal  ;
         end;
   end;
end;

procedure Tfrmocorrencia.spblimparClick(Sender: TObject);
begin
   lblsolicitante.Clear; lblsolicitantenome.caption := '...'; mskdtocorrencia.Text := datetostr(date);
   cboareadisponivel.ItemIndex := -1; cbomotivoocorrencia.ItemIndex := -1;
   cboresponsavel_solucao.ItemIndex := -1; memosolicitacao.Clear;
   controle:='INCLUSÃO';    memojadigitado.Clear;
end;

procedure Tfrmocorrencia.spbsalvarClick(Sender: TObject);
var
   entcod, motocorcodestr, entnomefant,solicitacao:string;
   i,a,c:integer;
   datainicial, datafinal : tdatetime;
begin
   with modulo_dados do
   begin
       {DATA INICIAL E FINAL DO PERIODO NO CASO DE INSERÇÃO SOMENTE ILUSTRATIVO}
       datainicial:= now-30;
       datafinal:=now;
       // formatando a data no padrão do ambiente RCC
       //datainicial:= strtodatetime());
       //datafinal:=strtodatetime();
       SQL:='SELECT mo.motocorcodestr FROM motivo_ocor mo with(nolock) WHERE mo.motocordescr = :motivoocorrencia';
       fdquerysql.Close;
       fdquerysql.SQL.Clear;
       fdquerysql.SQL.Text := sql;
       fdquerysql.ParamByName('motivoocorrencia').asstring := cbomotivoocorrencia.Text;
       if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
          begin
             motocorcodestr := fdquerysql.FieldByName('motocorcodestr').AsString;
          end;
       if lblsolicitante.text <> '' then
          begin
             entcod:=lblsolicitante.Text;
          end;
      {NESTA ETAPA O CÓDIGO DA OCORRÊNCIA QUANDO FOR PARA ABRIR, SERÁ INFORMADO APENAS NO MOMENTO DA GRAVAÇÃO, POIS NESSA HORA QUE
      VAI RODAR A ROTINA DA RIOSOFT PARA GERAR O CÓDIGO CORRETAMENTE}
      if ((lblsolicitante.text = '') OR (mskdtocorrencia.text = '  /  /    ') or (cboareadisponivel.text = '')) then
         begin
            messagedlg('É OBRIGATÓRIO INFORMAR ESTE CAMPO PARA A OCORRÊNCIA !!!',mterror,[mbok],0);
            lblsolicitante.SetFocus;
         end;
      resp:=messagedlg('Confirma a '+controle+' PARA ESTA OCORRÊNCIA ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
      if resp = idyes  then
         begin
            if controle = 'INCLUSÃO' then
               begin
                  sql:='DECLARE @vcodigoocorrencia varchar(7)';
                  sql:=sql+'exec User_geraocorrencia_projetosv2 :empcod';//+frmprincipal.codigo_empresa;
                  sql:=sql+', :individual'; //+'INDIVIDUAL';
                  sql:=sql+', :motocorcodestr'; //+motocorcodestr ;
                  sql:=sql+', :entcod '+entcod;
                  sql:=sql+', '+''; // código da ocorrência que na inclusão ainda não existe;
                  sql:=sql+', '+lblorigcodestr.Text;
                  sql:=sql+', '+frmlogon.codigousuario;
                  sql:=sql+', '+memosolicitacao.Text;
                  sql:=sql+', '+'NULL';
                  sql:=sql+', '+'NULL';
                  sql:=sql+', '+'NULL';
                  sql:=sql+', '+formatdatetime('yyyy-MM-dd', datainicial) ;
                  sql:=sql+', '+formatdatetime('yyyy-MM-dd', datafinal);
                  sql:=sql+', @vcodigoocorrencia OUTPUT';
               end
            else if controle = 'ALTERAÇÃO' then
               begin
                  sql:='DECLARE @vcodigoocorrencia varchar(7)';
                  sql:=sql+'EXEC User_geraocorrencia_projetosv2';
                  sql:=sql+quotedstr(frmprincipal.codigo_empresa);
                  sql:=sql+', '+quotedstr('INDIVIDUAL');
                  sql:=sql+', '+quotedstr(motocorcodestr);
                  sql:=sql+', '+quotedstr(entcod);
                  sql:=sql+', '+quotedstr(lblcodocorrencia.Text); // código da ocorrência que na inclusão ainda não existe;
                  sql:=sql+', '+quotedstr(lblorigcodestr.Text);
                  sql:=sql+', '+quotedstr(frmlogon.codigousuario);
                  sql:=sql+', '+quotedstr(memosolicitacao.Text);
                  sql:=sql+', '+quotedstr('NULL');
                  sql:=sql+', '+quotedstr('NULL');
                  sql:=sql+', '+quotedstr('NULL');
                  sql:=sql+', '+  quotedstr(formatdatetime('yyyy-MM-dd', datainicial)) ;
                  sql:=sql+', '+quotedstr(formatdatetime('yyyy-MM-dd', datafinal));
                  sql:=sql+', @vcodigoocorrencia OUTPUT';
               end;
            fdcomando.CommandText.Text := sql;
            fdcomando.Execute;
            sql:='UPDATE ocorrencia SET ocorstat = '+quotedstr('Em Andamento')+' WHERE ocorcod = :ocorcod';
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := sql;
            fdquerysql3.ParamByName('ocorcod').AsString :=   lblcodocorrencia.Text;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  messagedlg('OCORRÊNCIA ATUALIZADA COM SUCESSO !!!',mtinformation,[mbok],0);
                  spblimpar.Click;
               end;
            rdgpendente.setfocus;
            rdgpendente.Checked;
            mostra_ocorrencias('Pendente');
            lblsolicitante.SetFocus;
         end;

   end;
end;

procedure Tfrmocorrencia.spbuscasolicitanteClick(Sender: TObject);
var
   i:integer;
begin
   with modulo_dados do
   begin
      sql:='SELECT e.entcod, e.entnome, ec.categcodestr, e.entstatdescr';
      sql:=sql+' FROM ENTIDADE e with(nolock)';
      sql:=sql+' INNER JOIN ENT_CATEG ec with(nolock) ON e.EntCod = ec.EntCod';
      sql:=sql+' WHERE ec.CategCodEstr in (:categoria01, :categoria02, :categoria03)';
      sql:=sql+' GROUP BY e.entcod, e.EntNome, ec.categcodestr, e.EntStatDescr';
      sql:=sql+' ORDER BY e.EntNome ASC';
      //
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := sql;
      fdquerysql.ParamByName('categoria01').AsString := '09.01';
      fdquerysql.ParamByName('categoria02').AsString := '03.001';
      fdquerysql.ParamByName('categoria03').AsString := '03.004';
      if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
         begin
           application.CreateForm(tfrmconsulta3, frmconsulta3);
           frmconsulta3.controle := 'ENTIDADESOLICITANTEOCORRENCIA';
           dtsfdquerysql9.DataSet := fdquerysql;
           frmconsulta3.gridconsulta.DataSource := dtsfdquerysql;
           for i:= 0 to fdquerysql.fields.count -1 do
           begin
              frmconsulta3.cbocampo.items.add(fdquerysql.fields[i].displayname);
              frmconsulta3.cbordem.items.add(fdquerysql.fields[i].displayname);
           end;
           frmconsulta3.gridconsulta.Refresh;
           frmconsulta3.ShowModal
         end;
   end;
end;

function mostra_ocorrencias(status : string) : string;
begin
   with modulo_dados, frmocorrencia do
   begin
      if status <> '' then
         begin
             sql:='SELECT o.OcorCod, o.OcorStat, o.EntCod, o.ocorentnome, o.OcorRespSol, o.OcorData, ';
             sql:=sql+'   o.motocorcodestr, mo.motocordescr, o.ocortexto, o.ocorresptexto, o.origcodestr';
             sql:=sql+' FROM OCORRENCIA o with(nolock)    ';
             sql:=sql+' INNER JOIN MOTIVO_OCOR mo with(nolock) ON o.MotOcorCodEstr = mo.MotOcorCodEstr';
             sql:=sql+' INNER JOIN ENTIDADE e with(NOLOCK) ON o.EntCod = e.EntCod';
             sql:=sql+' WHERE o.OcorStat = :ocorstatus' ;
             sql:=sql+' AND      CAST(o.ocordata as date) > :datainicial';
             sql:=sql+' AND   o.empcod = :empcod';
             sql:=sql+' ORDER BY o.ocordata DESC';
         end
      else if status = '' then
         begin
            sql:='select o.ocorcod, o.OcorStat, o.entcod, o.ocorentnome, o.OcorRespSol, o.OcorData,';
            sql:=sql+' o.MotOcorCodEstr, mo.MotOcorDescr, o.ocortexto, o.ocorresptexto, o.origcodestr';
            sql:=sql+' from ocorrencia o with(nolock), motivo_ocor mo with(nolock)';
            sql:=sql+' where o.motocorcodestr = mo.motocorcodestr';
            sql:=sql+' AND   o.empcod = :empcod';
            sql:=sql+' order by o.ocordata desc';
         end;
      fdquerysql4.Close;
      fdquerysql4.SQL.Clear;
      fdquerysql4.SQL.Text := sql;
      fdquerysql4.ParamByName('ocorstatus').AsString :=status;
      fdquerysql4.ParamByName('datainicial').AsString := '2015-01-01';
      fdquerysql4.ParamByName('empcod').AsString :=frmprincipal.codigo_empresa;
      if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
         begin
            gridocorrencias.DataSource := dtsfdquerysql4;
            gridocorrencias.Refresh;
            lblcodocorrencia.SetFocus;
         end;
   end;
end;


procedure Tfrmocorrencia.rdgpendenteClick(Sender: TObject);
begin
   mostra_ocorrencias('Pendente');
end;

procedure Tfrmocorrencia.rdgemandamentoClick(Sender: TObject);
begin
   mostra_ocorrencias('Em Andamento');
end;

procedure Tfrmocorrencia.rdgcanceladoClick(Sender: TObject);
begin
   mostra_ocorrencias('Cancelado');
end;

procedure Tfrmocorrencia.rdgresolvidoClick(Sender: TObject);
begin
   mostra_ocorrencias('Resolvido');
end;

procedure Tfrmocorrencia.rdgtodasClick(Sender: TObject);
begin
   mostra_ocorrencias('');
end;

procedure Tfrmocorrencia.gridocorrenciasDblClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      controle:='ALTERAÇÃO';
      lblcodocorrencia.Text := fdquerysql4.fieldbyname('ocorcod').asstring;
      lblsolicitante.text:= fdquerysql4.FieldByName('entcod').AsString;
      lblsolicitantenome.Caption := fdquerysql4.FieldByName('ocorentnome').AsString;
      lblorigcodestr.text := fdquerysql4.FieldByName('origcodestr').AsString;
      sql:='SELECT orignome FROM origem WHERE origcodestr = :origcodestr';
      fdquerysql.Close;
      fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text := sql;
      fdquerysql.ParamByName('origcodestr').AsString :=lblorigcodestr.Text;
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
            lblorigdescr.Caption := fdquerysql.FieldByName('orignome').AsString;
            lblorigdescr.Refresh;
         end;
      mskdtocorrencia.Text := copy(fdquerysql4.fieldbyname('ocordata').asstring,1,2)+'/'+copy(fdquerysql4.fieldbyname('ocordata').asstring,4,2)+'/'+copy(fdquerysql4.fieldbyname('ocordata').asstring,7,4);
      sql:='SELECT MotOcorDescr FROM motivo_ocor WHERE substring(motocorcodestr,1,2) = :motocorcodestr';
      fdquerysql.Close;
      fdquerysql.sql.Clear;
      fdquerysql.sql.Text:= sql;
      fdquerysql.parambyname('motocorcodestr').asstring :=copy(fdquerysql4.fieldbyname('motocorcodestr').AsString,1,2);

      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         buscanacombo(fdquerysql.fieldbyname('motocordescr').AsString,frmocorrencia,cboareadisponivel);
      //
      buscanacombo(fdquerysql4.fieldbyname('OcorRespSol').asstring,frmocorrencia, cboresponsavel_solucao);
      cboresponsavel_solucao.Refresh;
      cbomotivoocorrencia.SetFocus;
      cboresponsavel_solucao.SetFocus;
      memojadigitado.Clear;
      memojadigitado.Lines.Add(fdquerysql4.fieldbyname('ocortexto').asstring);
      memosolucao.Clear;
      memosolucao.Lines.add(fdquerysql4.fieldbyname('ocorresptexto').asstring);
      //
      if (fdquerysql4.fieldbyname('ocorstat').asstring = 'Cancelado') or  (fdquerysql4.fieldbyname('ocorstat').asstring = 'Transferido') then
         begin
            lblsolicitante.Enabled := false;
            cboareadisponivel.Enabled := false;
            cbomotivoocorrencia.Enabled := false;
            cboresponsavel_solucao.Enabled := false;
         end
      else if (fdquerysql4.fieldbyname('ocorstat').asstring <> 'Cancelado') or  (fdquerysql4.fieldbyname('ocorstat').asstring <> 'Transferido') then
         begin
            lblsolicitante.Enabled := true;
            cboareadisponivel.Enabled := true;
            cbomotivoocorrencia.Enabled := true;
            cboresponsavel_solucao.Enabled := true;
            lblsolicitante.SetFocus;
         end;
      //
   end;
end;

procedure Tfrmocorrencia.gridocorrenciasDrawColumnCell(Sender: TObject;
  const Rect: TRect; DataCol: Integer; Column: TColumn; State: TGridDrawState);
begin
 {  with modulo_dados do
   begin
      if querysql4.FieldByName('ocorstat').asstring='Pendente' then
         begin
            gridocorrencias.Canvas.Font.Color :=clwhite;
            gridocorrencias.Canvas.Brush.Color:=clNavy  ;
            gridocorrencias.Canvas.FillRect(Rect);
         end
      else if querysql4.FieldByName('ocorstat').asstring='Em Andamento' then
         begin
            gridocorrencias.Canvas.Font.Color := clblack;
            gridocorrencias.Canvas.Brush.Color:= clGray;
            gridocorrencias.Canvas.FillRect(Rect);
         end
      else if querysql4.FieldByName('ocorstat').asstring = 'Cancelado' then
         begin
            gridocorrencias.Canvas.Brush.Color:= clSilver;
            gridocorrencias.Canvas.Font.Color := clblack;
            gridocorrencias.Canvas.FillRect(Rect);
         end
      else if querysql4.FieldByName('ocorstat').asstring = 'Resolvido' then
         begin
            gridocorrencias.Canvas.Brush.Color:= clLtGray;
            gridocorrencias.Canvas.Font.Color := clblack;
            gridocorrencias.Canvas.FillRect(Rect);
         end
      else if querysql4.FieldByName('ocorstat').asstring = 'Transferido' then
         begin
            gridocorrencias.Canvas.Brush.Color:= clYellow;
            gridocorrencias.Canvas.Font.Color := clblack;
            gridocorrencias.Canvas.FillRect(Rect);
         end;

   end;    }
end;

procedure Tfrmocorrencia.lblorigcodestrKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f4 then
      spbconsulta.Click;
   if (key = vk_return) or (key = vk_tab) then
      cboresponsavel_solucao.SetFocus;
end;

procedure Tfrmocorrencia.lblsolicitanteKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f4 then
      spbuscasolicitante.Click;
   if (key = vk_return) or (key = vk_tab) then
      mskdtocorrencia.SetFocus;
end;

procedure Tfrmocorrencia.btnokClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      if mskdtcanc.Text = '  /  /    ' then
         begin
            messagedlg('É OBRIGATÓRIO INFORMAR A DATA DE CANCELAMENTO !!!',mterror,[mbok],0);
            mskdtcanc.SetFocus;
            exit;
         end;
      if lblmotivocancelamento.Text = '' then
         begin
            messagedlg('É OBRIGATÓRIO INFORMAR UM MOTIVO DE CANCELAMENTO !!!',mterror,[mbok],0);
            lblmotivocancelamento.setfocus;
            exit;
         end;
      //
      resp:=messagedlg('Atenção !!! uma vez cancelada não poderá mais reverter, Confirma ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
      if resp = idyes then
         begin
            sql:='UPDATE ocorrencia SET ocordatacanc = :datacancelamento';
            sql:=sql+', ocorrespcanc = :responsavelpelocancelamento, ocormotcanc = :motivocancelamento'+quotedstr(lblmotivocancelamento.Text)+', ocorstat = :statuscancelamento'+quotedstr('Cancelado');
            sql:=sql+' WHERE ocorcod = :ocorcod ';
            fdquerysql3.Close;
            fdquerysql3.sql.Clear;
            fdquerysql3.sql.Text := sql;
            fdquerysql3.parambyname('datacancelamento').asstring:=copy(mskdtcanc.Text,4,2)+'/'+copy(mskdtcanc.Text,1,2)+'/'+copy(mskdtcanc.Text,7,4);
            fdquerysql3.parambyname('responsavelpelocancelamento').asstring:=lblresponsavel.Text;
            fdquerysql3.parambyname('ocorcod').asstring:= fdquerysql4.fieldbyname('ocorcod').asstring;

            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  messagedlg('OCORRÊNCIA CANCELADA COM SUCESSO !!!',mtinformation,[mbok],0);
                  mskdtcanc.Clear; lblresponsavel.Clear;
                  mskdtcanc.Text := datetostr(date);
                  grpcancelamento.visible:=false;
                  lblsolicitante.SetFocus;
               end
            else
               begin
                  messagedlg('PROBLEMAS AO TENTAR FAZER O CANCELAMENTO DESTA OCORRÊNCIA !!!',mterror,[mbok],0);
                  mskdtcanc.SetFocus;
                  exit;
               end;
         end
      else
         begin
            mskdtcanc.SetFocus;
            exit;
         end;
   end;
end;

procedure Tfrmocorrencia.btncancelarClick(Sender: TObject);
begin
   grpcancelamento.Visible := false;
   lblsolicitante.SetFocus;
end;

procedure Tfrmocorrencia.mskdtcancKeyDown(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      lblmotivocancelamento.SetFocus;
end;

procedure Tfrmocorrencia.mskdtocorrenciaKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_tab) or (key = vk_return) then
      cboareadisponivel.SetFocus;
end;

procedure Tfrmocorrencia.rdgtransferidoClick(Sender: TObject);
begin
   mostra_ocorrencias('Transferido');
end;

procedure Tfrmocorrencia.GravaConfiguraes1Click(Sender: TObject);
begin
   grava_configuracoes_grids(frmocorrencia,'OCORRENCIA',gridocorrencias,'gridocorrencias',frmlogon.nomeusuario,modulo_dados.dtsfdquerysql4);
end;

procedure Tfrmocorrencia.spbnovaocorrenciaClick(Sender: TObject);
begin
   controle:='INCLUSÃO';
   if lblsolicitante.Enabled = false then
      lblsolicitante.Enabled := true;
   //
   if cboareadisponivel.Enabled = false then
      lblsolicitante.Enabled := true;
   //
   if cbomotivoocorrencia.Enabled = false then
      cbomotivoocorrencia.Enabled := true;
   //
   if cboresponsavel_solucao.Enabled = false then
      cboresponsavel_solucao.Enabled := true;
   spblimpar.Click;
   if lblsolicitante.Enabled = false then
      begin
         lblsolicitante.Enabled :=true;
         lblsolicitante.SetFocus;
      end
   else
      lblsolicitante.SetFocus;
end;

end.
