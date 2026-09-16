unit unt_configsysv2;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.StdCtrls, Vcl.ComCtrls, Vcl.Buttons,
  Vcl.ExtCtrls, registry, Vcl.Grids, Vcl.DBGrids, Data.DB, Vcl.Mask;

type
  Tfrmconfig = class(TForm)
    cinsistema: TPageControl;
    subcin_sistema: TTabSheet;
    subcin_entidades: TTabSheet;
    subcin_email: TTabSheet;
    lblcaminhobackup: TLabeledEdit;
    lblinstalacaolocal: TLabeledEdit;
    lbldirnovasversoes: TLabeledEdit;
    lblaplinstalador: TLabeledEdit;
    Panel1: TPanel;
    spbsalvar: TSpeedButton;
    spblimpar: TSpeedButton;
    spblocalizar: TSpeedButton;
    spbexcluir: TSpeedButton;
    spbretornar: TSpeedButton;
    lblmsg1: TLabel;
    StatusBar1: TStatusBar;
    chkintegra_apolo: TCheckBox;
    chkintegramix: TCheckBox;
    chkintegrapolo: TCheckBox;
    GroupBox2: TGroupBox;
    chkapolo: TCheckBox;
    chkgeoapolo: TCheckBox;
    lblentidadeparceira: TLabeledEdit;
    spbuscategoria: TSpeedButton;
    lblcategnomeparceiros: TLabel;
    lblcaminhoarquivoconvenio: TLabeledEdit;
    spbopendir: TSpeedButton;
    lblimapserver: TLabeledEdit;
    cboprotocolo: TComboBox;
    lblprotocolo: TLabel;
    lblsmtpserver: TLabeledEdit;
    lblportarecebimento: TLabeledEdit;
    lblportaenvio: TLabeledEdit;
    chkgeracamp: TCheckBox;
    gridemail: TDBGrid;
    btninserir: TBitBtn;
    btncancelar: TBitBtn;
    lblcodigoservidor: TLabeledEdit;
    tabemailmonitoramento: TTabSheet;
    lblcontaemail: TLabeledEdit;
    lblsenha: TLabeledEdit;
    lblservidor: TLabeledEdit;
    spbuscaservidoremail: TSpeedButton;
    gridcontasemail: TDBGrid;
    btncontaemail: TBitBtn;
    btncancelaemail: TBitBtn;
    lblcodigoconta: TLabeledEdit;
    lblcaminhoinventario: TLabeledEdit;
    spbinventarioti: TSpeedButton;
    cinestoque: TTabSheet;
    grpestoque: TGroupBox;
    lblgruposoftware: TLabeledEdit;
    spbuscagruposoftware: TSpeedButton;
    lblgrupohardware: TLabeledEdit;
    spbuscagruphardware: TSpeedButton;
    lblnomegruposoftware: TLabel;
    lblnomegrupohardware: TLabel;
    lblcaminhodocti: TLabeledEdit;
    spbcaminhodocti: TSpeedButton;
    opendialog: TOpenDialog;
    TabSheet1: TTabSheet;
    lbltempoduracao: TLabeledEdit;
    lblcaminhodocmissaopopular: TLabeledEdit;
    spbdocmissaopopular: TSpeedButton;
    lblcategcodformadoropiniao: TLabeledEdit;
    spbuscacategoriaformaopiniao: TSpeedButton;
    lblcategcodestr_formaopiniao: TLabel;
    lblstatusfechapic: TLabeledEdit;
    lblstatusfechapicnome: TLabel;
    spbuscastatusfechapic: TSpeedButton;
    lblcodtipocamp: TLabeledEdit;
    spbuscacodtipocamp: TSpeedButton;
    lbldescricaotipocamp: TLabel;
    lbldocanexopic: TLabeledEdit;
    spbdocanexopic: TSpeedButton;
    tabmoduloloja: TTabSheet;
    spbbuscaalvoloja: TSpeedButton;
    lblcaminhobasealvoloja: TLabeledEdit;
    lblentcodconsumidorfinal: TLabeledEdit;
    spbuscaentidade: TSpeedButton;
    lblentnomeconsumidorfinal: TLabel;
    lblorigpadraodescr: TLabel;
    spbuscaorigempadrao: TSpeedButton;
    lblorigcodestrpadrao: TLabeledEdit;
    lblentidade: TLabeledEdit;
    spbentidade: TSpeedButton;
    cboentidades: TComboBox;
    lblintegraentidadeapolo: TLabel;
    lblnome_entidade: TLabel;
    lbldescricaomotivoocor: TLabel;
    spbbuscamotocorcodestr: TSpeedButton;
    lblmotocorcodestr: TLabeledEdit;
    spbuscasolucaoocorrencia: TSpeedButton;
    lbltiposolucaoocorrencia: TLabeledEdit;
    lbldescricaosolucaoocorrencia: TLabel;
    lblcategcodestrpadraofornecedores: TLabeledEdit;
    spbuscacategpadraofornecedores: TSpeedButton;
    lblcategnomepadraofornecedores: TLabel;
    procedure spbretornarClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormActivate(Sender: TObject);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbsalvarClick(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure lblcaminhobackupKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblinstalacaolocalKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lbldirnovasversoesKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblaplinstaladorKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure chkintegra_apoloKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure chkintegra_apoloClick(Sender: TObject);
    procedure chkintegramixClick(Sender: TObject);
    procedure chkintegramixKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure chkintegrapoloKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure chkintegrapoloClick(Sender: TObject);
    procedure chkapoloClick(Sender: TObject);
    procedure chkapoloKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure chkgeoapoloClick(Sender: TObject);
    procedure chkgeoapoloKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbuscaverbaClick(Sender: TObject);
    procedure lblvercodigoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblentidadeparceiraKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblentidadeparceiraEnter(Sender: TObject);
    procedure btninserirClick(Sender: TObject);
    procedure subcin_emailEnter(Sender: TObject);
    procedure cboprotocoloKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblimapserverKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblportarecebimentoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblsmtpserverKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblportaenvioKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure btncancelarClick(Sender: TObject);
    procedure gridemailDblClick(Sender: TObject);
    procedure gridemailKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure tabemailmonitoramentoEnter(Sender: TObject);
    procedure lblservidorKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblcontaemailKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblsenhaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure btncontaemailClick(Sender: TObject);
    procedure lblsenhaEnter(Sender: TObject);
    procedure lblsmtpserverEnter(Sender: TObject);
    procedure spbuscaservidoremailClick(Sender: TObject);
    procedure gridcontasemailDblClick(Sender: TObject);
    procedure gridcontasemailKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure chkgeracampClick(Sender: TObject);
    procedure lblgruposoftwareKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblgrupohardwareKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbuscagruposoftwareClick(Sender: TObject);
    procedure spbuscagruphardwareClick(Sender: TObject);
    procedure spbcaminhodoctiClick(Sender: TObject);
    procedure spbdocmissaopopularClick(Sender: TObject);
    procedure lbltempoduracaoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblcaminhodocmissaopopularKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblcategcodformadoropiniaoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbuscacategoriaformaopiniaoClick(Sender: TObject);
    procedure spbuscastatusfechapicClick(Sender: TObject);
    procedure spbuscacodtipocampClick(Sender: TObject);
    procedure spbdocanexopicClick(Sender: TObject);
    procedure lblentidadeKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblmotocorcodestrKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbbuscamotocorcodestrClick(Sender: TObject);
    procedure spbuscaorigempadraoClick(Sender: TObject);
    procedure spbentidadeClick(Sender: TObject);
    procedure spbuscasolucaoocorrenciaClick(Sender: TObject);
    procedure lbltiposolucaoocorrenciaKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblAlturaKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbuscacategpadraofornecedoresClick(Sender: TObject);
    procedure lblcategcodestrpadraofornecedoresKeyUp(Sender: TObject;
      var Key: Word; Shift: TShiftState);
    procedure spbbuscaalvolojaClick(Sender: TObject);
    procedure lblcaminhobasealvolojaKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblentcodconsumidorfinalKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbuscaentidadeClick(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  frmconfig: Tfrmconfig;
  apolo_geoapolo:integer;
  integraentidadeapolo,controle_contas,controle_email,entidade_apolo,integrabaseapolo,integrabasemix, integraocorrmix, campbaseapolo,integra_com_apolo,sql,controle:string;

function lista_servidores_email : string; export;
function limpa_controles : string; export;
function listacontas : string; export;
function buscacodigoservidor(nomeservidor : string) : string; export;
function limpacontrolesemail : string; export;

implementation

{$R *.dfm}

uses unt_dados, unt_principal, funcoes, unt_consultav3, unt_entidades,
  unt_logon;

procedure Tfrmconfig.btncancelarClick(Sender: TObject);
begin
   limpa_controles; controle_email:='INCLUS�O';
   cinsistema.ActivePageIndex:=0;
   cinsistema.refresh;
end;

procedure Tfrmconfig.btncontaemailClick(Sender: TObject);
var
   codigo:string;
begin
   with modulo_dados,frmprincipal do
   begin
      if lblcontaemail.text = '' then
         begin
            messagedlg('PARA SALVAR UMA CONTA DE EMAIL PRIMEIRO DEVE INFORM�-LA !!!',mterror,[mbok],0);
            lblcontaemail.setfocus;
            exit;
         end;
      //
      if lblsenha.text = '' then
         begin
            messagedlg('NÃO É PERMITIDO SALVAR UMA CONTA DE EMAIL SEM SENHA !!!',mterror,[mbok],0);
            lblsenha.setfocus;
            exit;
         end;
      //
      if lblservidor.text = '' then
         begin
            messagedlg('NÃO É POSSÍVEL MONITORAR UM EMAIL SEM QUE VOCÉ INFORME QUAL SEU PROVEDOR !!!',mterror,[mbok],0);
            lblservidor.setfocus;
            exit;
         end;
      //
      resp:=messagedlg('Confirma os dados desta conta de email ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
      if resp = idyes  then
         begin
            codigo:=buscacodigoservidor(lblservidor.text);
            if controle_email = 'INCLUSÂO' then
               begin
                  sql:='INSERT INTO geoapolo_contas_email (codigo_conta,conta_email,senha,codigo_servidor)';
                  sql:=sql+' VALUES (:pcodigoconta, :pcontaemail, :psenha, :pcodigoservidor)';
               end
            else if controle_email = 'ALTERAÇÃO' then
               begin
                  sql:='UPDATE geoapolo_contas_email SET conta_email = :pcontaemail, senha = :psenha, codigo_servidor = :pcodigoservidor';
                  sql:=sql+' WHERE codigo_conta = :pcodigoconta';
               end;
            //
            fdquerysql3.close;
            fdquerysql3.sql.clear;
            fdquerysql3.sql.text := sql;
            fdquerysql3.parambyname('pcodigoconta').asstring := lblcodigoconta.text;
            fdquerysql3.parambyname('pcontaemail').asstring := lblcontaemail.text;
            fdquerysql3.parambyname('psenha').asstring := criptografia(42,lblsenha.text);
            fdquerysql3.parambyname('pcodigoservidor').asstring := codigo;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  messagedlg('CONTA DE EMAIL ATUALIZADA COM SUCESSO !!!',mtinformation,[mbok],0);
                  limpacontrolesemail;
                  lblcodigoconta.text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_contas_email','S');
                  cinsistema.ActivePageIndex:=3; cinsistema.refresh;
                  listacontas;
                  lblcodigoconta.refresh;
                  lblcontaemail.setfocus;
               end;
         end
      else
         begin
            btncancelaemail.click;
         end;
   end;
end;

function buscacodigoservidor(nomeservidor : string) : string;
var
   codigo:string;
begin
   with modulo_dados, frmconfig do
   begin
      sql:='SELECT * FROM geoapolo_mail_server WHERE servidor_recebimento = :pservidorrecebimento';
      fdquerysql1.close;
      fdquerysql1.sql.text := sql;
      fdquerysql1.parambyname('pservidorrecebimento').asstring :=nomeservidor;
      if executaracao(fdquerysql1, fdbanco, true, dtsfdquerysql1) then
         codigo:= fdquerysql1.fieldbyname('codigo_servidor').asstring
      else
         codigo:='0';
      //
      result:=codigo;
   end;
end;

procedure Tfrmconfig.btninserirClick(Sender: TObject);
begin
   with modulo_dados,frmprincipal do
   begin
      if lblimapserver.text = '' then
         begin
            messagedlg('� OBRIGAT�RIO INFORMAR UM SERVIDOR DE RECEBIMENTO DE EMAILS PARA INSERIR ',mterror,[mbok],0);
            lblimapserver.setfocus;
            exit;
         end;
      if lblsmtpserver.text = '' then
         begin
            messagedlg('� OBRIGAT�RIO INFORMAR UM SERVIDOR DE ENVIO DE EMAILS PARA INSERIR ',mterror,[mbok],0);
            lblsmtpserver.setfocus;
            exit;
         end;
      //
      if lblportarecebimento.text = '' then
        begin
            messagedlg('� OBRIGAT�RIO INFORMAR A PORTA DE ACESSO AO SERVIDOR ',mterror,[mbok],0);
            lblsmtpserver.setfocus;
            exit;
        end;
      //
      if lblportaenvio.text = '' then
         begin
            messagedlg('� OBRIGAT�RIO INFORMAR A PORTA DE ACESSO AO SERVIDOR ',mterror,[mbok],0);
            lblsmtpserver.setfocus;
            exit;
         end;
      //
      resp:=messagedlg('Confirma os dados para este servidor de Email ? ',mtconfirmation,[mbyes,mbno],0);
      if resp = idyes  then
         begin
            if controle_email = 'INCLUS�O' then
               begin
                  sql:='INSERT INTO geoapolo_mail_server (codigo_servidor,protocolo,servidor_envio,porta_envio,servidor_recebimento,porta_recebimento)';
                  sql:=sql+' VALUES (:pcodigoservidor, :pcodigoprotocolo, :psmtpserver, :pimapserver, :pportaenvio, :pservidorrecebimento, :pportarecebimento)';
               end
            else if controle_email = 'ALTERA��O' then
               begin
                  sql:='UPDATE geoapolo_mail_server SET protocolo = :pcodigoprotocolo, servidor_envio = :psmtpserver ';
                  sql:=sql+' , porta_envio = :pportaenvio, , servidor_recebimento = :pservidorrecebimento, porta_recebimento = :portarecebimento';
                  sql:=sql+' WHERE codigo_servidor = :pcodigoservidor';
               end;
            //
            fdquerysql3.close;
            fdquerysql3.sql.text := sql;
            fdquerysql3.ParamByName('pcodigoservidor').AsString := lblcodigoservidor.text;
            fdquerysql3.parambyname('pcodigoprotocolo').asstring := cboprotocolo.text;
            fdquerysql3.parambyname('psmtpserver').asstring:= lblsmtpserver.text;
            fdquerysql3.parambyname('pimapserver').asstring := lblimapserver.text;
            fdquerysql3.parambyname('pportaenvio').asstring := lblportaenvio.text;
            fdquerysql3.parambyname('pservidorrecebimento').asstring := lblimapserver.text;
            fdquerysql3.parambyname('pportarecebimento').asstring := lblportarecebimento.text;
            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
               begin
                  messagedlg('ATUALIZA��O REALIZADA COM SUCESSO !!!',mtinformation,[mbok],0);
                  lblcodigoservidor.text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_mail_server','Sim');
                  lista_servidores_email;  limpa_controles;
                  lblcodigoservidor.refresh;   cinsistema.ActivePageIndex:=2; cinsistema.refresh;
                  cboprotocolo.setfocus;
               end
            else
               begin
                  messagedlg('ERRO AO ATUALIZAR O REGISTRO !!!',mterror,[mbok],0);
                  cboprotocolo.setfocus;
                  exit;
               end;
         end;
   end;
end;

procedure Tfrmconfig.cboprotocoloKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = VK_TAB) then
      begin
         lblimapserver.setfocus;
      end;
end;

procedure Tfrmconfig.chkapoloClick(Sender: TObject);
begin
   lblcaminhoarquivoconvenio.setfocus;
end;

procedure Tfrmconfig.chkapoloKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      lblcaminhoarquivoconvenio.setfocus;
end;

procedure Tfrmconfig.chkgeoapoloClick(Sender: TObject);
begin
   lblcaminhoarquivoconvenio.setfocus;
end;

procedure Tfrmconfig.chkgeoapoloKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      lblcaminhoarquivoconvenio.setfocus;
end;

procedure Tfrmconfig.chkgeracampClick(Sender: TObject);
begin
   if chkgeracamp.Checked then
      campbaseapolo := 'S'
   else
      campbaseapolo:='N';
end;

procedure Tfrmconfig.chkintegramixClick(Sender: TObject);
begin
   if chkintegramix.Checked then
      integrabasemix:='S'
   else
     integrabasemix:='N';
end;

procedure Tfrmconfig.chkintegramixKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      chkintegrapolo.setfocus;
end;

procedure Tfrmconfig.chkintegrapoloClick(Sender: TObject);
begin
   chkapolo.setfocus;
end;

procedure Tfrmconfig.chkintegrapoloKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      chkapolo.setfocus;
end;

procedure Tfrmconfig.chkintegra_apoloClick(Sender: TObject);
begin
   chkintegramix.setfocus;
end;

procedure Tfrmconfig.chkintegra_apoloKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      chkintegramix.setfocus;
end;

procedure Tfrmconfig.FormActivate(Sender: TObject);
var
   registro:tregistry;
begin
   with modulo_dados do
   begin
      CONTROLE:='INCLUSÃO';
      statusbar1.Panels[1].Text := configura_statusbar('1');
      statusbar1.Panels[3].text :=configura_statusbar('1');
      statusbar1.Panels[5].text := frmprincipal.nomeserversql;
      cinsistema.ActivePageIndex:=0;
      cinsistema.refresh;
      sql:='SELECT * FROM USER_geoapolo_configuracoes';
      fdquerysql.close;
      fdquerysql.sql.text := sql;
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
          begin
             with frmprincipal do
             begin
                {frmprincipal.caminhosbackup  := buscatroca(querysql.fieldbyname('caminhobackupsistema').asstring,'$','\');
                frmprincipal.dirnovasversoes := buscatroca(querysql.fieldbyname('localnovasversoes').AsString,'$','\');
                frmprincipal.dirinstalacaolocal := buscatroca(querysql.fieldbyname('instalacaolocal').asstring,'$','\');
                frmprincipal.diraplinstalador := buscatroca(querysql.fieldbyname('localinstaladorversoes').asstring,'$','\');
                frmprincipal.pathfoto:=buscatroca(querysql.fieldbyname('caminhosalvarfotos').asstring,'$','\');
                frmprincipal.alturafoto:=buscatroca(querysql.fieldbyname('alturafoto').asstring,'$','\');
                frmprincipal.largurafoto:=buscatroca(querysql.fieldbyname('largurafoto').asstring,'$','\');
                frmconfig.lblcaminhoarquivoconvenio.Text :=buscatroca(querysql.fieldbyname('caminhoarquivoconvenio').asstring,'$','\');}

                frmconfig.lblentidadeparceira.Text := fdquerysql.fieldbyname('entcategparceira').asstring;
                sql:='SELECT geocategnome FROM USER_geoapolo_categoria WHERE geocategcodestr = :pgeocategcodestr';
                fdquerysql6.close;
                fdquerysql6.sql.text := sql;
                fdquerysql6.ParamByName('pgeocategcodestr').AsString := lblentidadeparceira.text;
                if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
                   frmconfig.lblcategnomeparceiros.Caption:=fdquerysql6.fieldbyname('geocategnome').asstring;
                //
                frmconfig.lblcategnomeparceiros.Refresh;
                //
{                frmprincipal.caminhosbackup  := buscatroca(frmprincipal.caminhosbackup,'#','-');
                frmprincipal.dirnovasversoes := buscatroca(frmprincipal.dirnovasversoes,'#','-');
                frmprincipal.dirinstalacaolocal := buscatroca(frmprincipal.dirinstalacaolocal,'#','-');
                frmprincipal.diraplinstalador:= buscatroca(frmprincipal.diraplinstalador,'#','-');
                frmprincipal.caminhoexclusao :=buscatroca(frmprincipal.caminhoexclusao,'#','-');
                frmprincipal.pathfoto:=buscatroca(pathfoto,'#','-');
                frmprincipal.alturafoto:=buscatroca(alturafoto,'#','-');
                frmprincipal.largurafoto:=buscatroca(largurafoto,'#','-');}
                lblmotocorcodestr.Text:= fdquerysql.FieldByName('motocorcodestr').AsString;
                lblcaminhobasealvoloja.text := fdquerysql.FieldByName('caminhobasealvoloja').AsString;
                if lbldescricaomotivoocor.caption ='Descri��o do motivo da Ocorr�ncia' then
                   begin
                      with modulo_dados do
                      begin
                         if (frmprincipal.integraentidadesapolo = 'Integra') or (frmprincipal.integraentidadesapolo = 'Mescla') then
                            begin
                               sql:='SELECT motocordescr FROM motivo_ocor WHERE motocorcodestr = :pmotocorcodestr';
                               fdquerysql12.close;
                               fdquerysql12.sql.text := sql;
                               fdquerysql12.ParamByName('pmotocorcodestr').AsString := lblmotocorcodestr.Text;
                               if executaracao(fdquerysql12, fdbanco, true, dtsfdquerysql12) then
                                  begin
                                     lbldescricaomotivoocor.Caption := fdquerysql12.FieldByName('motocordescr').AsString;
                                     lbldescricaomotivoocor.Refresh;
                                  end;
                            end
                         else if (frmprincipal.integraentidadesapolo = 'N�o Integra') then
                            begin
                               sql:='SELECT motocordescr FROM USER_geoapolo_motivo_ocor WHERE motocorcodestr = :pmotocorcodestr';
                               fdquerysql12.close;
                               fdquerysql12.sql.text := sql;
                               fdquerysql12.ParamByName('pmotocorcodestr').AsString := lblmotocorcodestr.Text;
                               if executaracao(fdquerysql12, fdbanco, true, dtsfdquerysql12) then
                                  begin
                                     lbldescricaomotivoocor.Caption := fdquerysql12.FieldByName('motocordescr').AsString;
                                     lbldescricaomotivoocor.Refresh;
                                  end;
                            end;
                      end;
                   end;
                if (frmprincipal.integraentidadesapolo = 'Integra') or (frmprincipal.integraentidadesapolo = 'Mescla') then
                   lblorigcodestrpadrao.text := fdquerysql.FieldByName('origcodestr').AsString
                else if (frmprincipal.integraentidadesapolo = 'N�o Integra') then
                   lblorigcodestrpadrao.text:= fdquerysql.FieldByName('origcodestr').AsString;
                if lblorigpadraodescr.caption ='Descri��o da Origem de ocorr�ncia padr�o' then
                   begin
                      with modulo_dados do
                      begin
                         if (frmprincipal.integraentidadesapolo = 'Integra') or (frmprincipal.integraentidadesapolo = 'Mescla') then
                            begin
                               sql:='SELECT orignome FROM origem WHERE origcodestr = :porigcodestrpadrao';
                               fdquerysql12.close;
                               fdquerysql12.sql.text := sql;
                               fdquerysql12.parambyname('porigcodestrpadrao').asstring :=lblorigcodestrpadrao.text;
                               if executaracao(fdquerysql12, fdbanco, true, dtsfdquerysql12) then
                                  begin
                                     lblorigpadraodescr.caption := fdquerysql12.FieldByName('orignome').AsString;
                                     lblorigpadraodescr.Refresh;
                                  end;
                            end
                         else if (frmprincipal.integraentidadesapolo = 'N�o Integra') then
                            begin
                               sql:='SELECT geo_orignome FROM USER_geoapolo_origens WHERE geo_origcodestr = :porigcodestrpadrao';
                               fdquerysql12.active := false;
                               fdquerysql12.sql.text := sql;
                               fdquerysql12.parambyname('porigcodestrpadrao').asstring := lblorigcodestrpadrao.text;
                               if executaracao(fdquerysql12, fdbanco, true, dtsfdquerysql12) then
                                  begin
                                     lblorigpadraodescr.caption := fdquerysql12.FieldByName('geo_orignome').AsString;
                                     lblorigpadraodescr.Refresh;
                                  end;
                            end;
                      end;
                   end;
                frmconfig.lblcaminhoarquivoconvenio.Text :=buscatroca(lblcaminhoarquivoconvenio.text,'#','-');
                if fdquerysql.fieldbyname('integra_base_apolomix').asstring = 'S' then
                   begin
                      chkintegra_apolo.Checked := true;
                      integrabaseapolo:='S';
                   end
                else
                   begin
                      chkintegra_apolo.Checked := false;
                      integrabaseapolo:='N';
                   end;
                //
                if fdquerysql.fieldbyname('integra_geosec_cctrlcodestr').asstring = 'S' then
                   begin
                      chkintegrapolo.Checked := true;
                      integra_com_apolo:='S';
                   end
                else
                  integra_com_apolo := 'N';
                //
                if fdquerysql.fieldbyname('indexconsultasimediatas').asinteger = 0 then
                   begin
                      chkapolo.Checked := true;
                      chkgeoapolo.Checked :=false;
                   end
                else if fdquerysql.fieldbyname('indexconsultasimediatas').asinteger = 1 then
                   begin
                      chkgeoapolo.Checked := true;
                      chkapolo.Checked := false;
                   end;
                //
                if fdquerysql.FieldByName('gera_camp_baseapolo').AsString = 'S' then
                   chkgeracamp.Checked := true
                else
                   chkgeracamp.Checked := false;
                //
                if fdquerysql.FieldByName('integrabasemix').AsString = 'S' then
                   chkintegramix.Checked := true
                else
                   chkintegramix.Checked := false;
                //
                if fdquerysql.fieldbyname('integra_entidades_apolo').asstring <> '' then
                   buscanacombo(fdquerysql.fieldbyname('integra_entidades_apolo').AsString,frmconfig,cboentidades);
                //
                lblcaminhoinventario.text := fdquerysql.fieldbyname('caminhoinventario').asstring;
                lblcaminhodocti.text := fdquerysql.fieldbyname('caminhodocti').asstring;
                lbltempoduracao.text := fdquerysql.fieldbyname('tempomaximomissao').asstring;
                //
                cboentidades.Refresh;
                lblentidade.Text := fdquerysql.fieldbyname('geoentcod').asstring;
                //
                lbldirnovasversoes.Text := frmprincipal.dirnovasversoes ;
                lblcaminhobackup.Text := frmprincipal.caminhosbackup ;
                lblaplinstalador.Text := frmprincipal.diraplinstalador ;
                lblinstalacaolocal.Text := frmprincipal.dirinstalacaolocal ;

                lblcaminhodocmissaopopular.text := fdquerysql.fieldbyname('caminhodocmissaopopular').asstring;
                lbldocanexopic.text := fdquerysql.fieldbyname('caminhodocanexopic').asstring;
                lblcategcodformadoropiniao.text := fdquerysql.fieldbyname('categcodestr_formadoropiniao').asstring;
                sql:='SELECT geocategnome FROM USER_geoapolo_categoria WHERE geocategcodestr = :pgeocategcodestr';
                fdquerysql6.close;
                fdquerysql6.sql.text := sql;
                fdquerysql6.parambyname('pgeocategcodestr').asstring :=lblcategcodformadoropiniao.Text;
                if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
                   frmconfig.lblcategcodestr_formaopiniao.Caption:=fdquerysql6.fieldbyname('geocategnome').asstring;
                 //
                if ((dirnovasversoes <> '') or (dirinstalacaolocal<> '') or (diraplinstalador<> '')) then
                   frmprincipal.controle:='ALTERAÇÃO'
                else
                   frmprincipal.controle:='INCLUSÃO';
                lblstatusfechapic.text := fdquerysql.fieldbyname('status_fechapic').asstring;
                if lblstatusfechapic.text <> '' then
                   begin
                      sql:='SELECT descricao_status FROM USER_geoapolo_pic_status WHERE codigo_statuspic = :pcodigostatuspic';
                      fdquerysql6.close;
                      fdquerysql6.sql.text := sql;
                      fdquerysql6.parambyname('pcodigostatuspic').asstring :=lblstatusfechapic.text;
                      if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
                         lblstatusfechapicnome.caption:= fdquerysql6.fieldbyname('descricao_status').asstring;
                   end;
                //
                lblcodtipocamp.text := fdquerysql.fieldbyname('codigo_tipocamp_geracamp').asstring;
                lbltiposolucaoocorrencia.text := fdquerysql.FieldByName('tiposolocorcod').AsString;
                lblcategcodestrpadraofornecedores.Text:= fdquerysql.FieldByName('categcodestr_padraofornecedores').AsString;
                if (frmprincipal.integraentidadesapolo = 'Integra') or (frmprincipal.integraentidadesapolo = 'Mescla') then
                   begin
                      sql:='SELECT categnome FROM categoria WHERE categcodestr = :pcategcodestrpadraofornecedores';
                      fdquerysql1.close;
                      fdquerysql1.sql.text := sql;
                      fdquerysql1.parambyname('pcategcodestrpadraofornecedores').asstring := lblcategcodestrpadraofornecedores.Text;
                      if executaracao(fdquerysql1, fdbanco, true, dtsfdquerysql1) then
                         begin
                            lblcategnomepadraofornecedores.Caption := fdquerysql1.FieldByName('categnome').AsString;
                            lblcategnomepadraofornecedores.Refresh;
                         end;
                   end
                else if (frmprincipal.integraentidadesapolo = 'N�o Integra') then
                   begin
                      sql:='SELECT geocategnome FROM USER_geoapolo_categoria WHERE geocategcodestr = :pcategcodestrpadraofornecedores';
                      fdquerysql1.close;
                      fdquerysql1.sql.text := sql;
                      fdquerysql1.parambyname('pcategcodestrpadraofornecedores').asstring := lblcategcodestrpadraofornecedores.Text;
                      if executaracao(fdquerysql1, fdbanco, true, dtsfdquerysql1) then
                         begin
                            lblcategnomepadraofornecedores.Caption := fdquerysql1.FieldByName('geocategnome').AsString;
                            lblcategnomepadraofornecedores.Refresh;
                         end;
                   end;
                lblentcodconsumidorfinal.text:= fdquerysql.FieldByName('entcod_consumidorfinal').AsString;
                sql:='SELECT e.entnome FROM entidade e with(nolock) WHERE e.entcod = :pentcodconsumidorfinal';
                fdquerysql18.close;
                fdquerysql18.sql.text := sql;
                fdquerysql18.parambyname('pentcodconsumidorfinal').asstring :=lblentcodconsumidorfinal.Text;
                if executaracao(fdquerysql18, fdbanco, true, dtsfdquerysql18) then
                   begin
                      lblentnomeconsumidorfinal.Caption := fdquerysql18.FieldByName('entnome').AsString;
                      lblentnomeconsumidorfinal.Refresh;
                   end;
                //
                frmconfig.Refresh;
             end;
          end;
   end;
   statusbar1.panels[1].text := configura_statusbar('a');
   statusbar1.panels[3].text := configura_statusbar('a');
   statusbar1.panels[5].text := frmprincipal.nomeserversql;
   statusbar1.Refresh;
end;

procedure Tfrmconfig.FormClose(Sender: TObject; var Action: TCloseAction);
begin
   action:=cafree;
end;

procedure Tfrmconfig.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f10 then
      spbretornar.Click;
end;

procedure Tfrmconfig.gridcontasemailDblClick(Sender: TObject);
begin
   controle_email:='ALTERA��O';
   with modulo_dados do
   begin
      lblcodigoconta.text := fdquerysql5.fieldbyname('codigo_conta').asstring;
      lblcontaemail.text := fdquerysql5.fieldbyname('conta_email').asstring;
      lblsenha.text := decriptografia(42,fdquerysql5.fieldbyname('senha').asstring,'');
      sql:='SELECT servidor_recebimento FROM USER_geoapolo_mail_server WHERE codigo_servidor = :pcodigoservidor';
      fdquerysql1.close;
      fdquerysql1.sql.text := sql;
      fdquerysql1.parambyname('pcodigoservidor').asstring := fdquerysql5.fieldbyname('codigo_servidor').asstring;
      if executaracao(fdquerysql1, fdbanco, true, dtsfdquerysql1) then
         begin
            lblservidor.text := fdquerysql1.fieldbyname('servidor_recebimento').asstring;
            lblservidor.refresh;
         end;
      lblcontaemail.setfocus;
   end;
end;

procedure Tfrmconfig.gridcontasemailKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   with modulo_dados,frmprincipal do
   begin
      if key = VK_DELETE then
         begin
            resp:=messagedlg('Confirma a remo��o de monitoramento deste e-mail ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
            if resp = idyes then
               begin
                  sql:='DELETE FROM USER_geoapolo_contas_email WHERE codigo_conta = :pcodigoconta';
                  fdquerysql3.close;
                  fdquerysql3.sql.text := sql;
                  fdquerysql3.ParamByName('pcodigoconta').AsString := fdquerysql5.FieldByName('codigo_conta').AsString;
                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                     begin
                        messagedlg('MONITORAMENTO REMOVIDO COM SUCESSO !!!',mtinformation,[mbok],0);
                        listacontas;
                        lblcontaemail.setfocus;
                     end
                  else
                     begin
                        messagedlg('ERRO AO TENTAR REMOVER ESTE MONITORAMENTO !!!',mterror,[mbok],0);
                        lblcontaemail.setfocus;
                        exit;
                     end;
               end
            else
               begin
                  lblcontaemail.setfocus;
                  exit;
               end;
         end;
   end;
end;

procedure Tfrmconfig.gridemailDblClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      lblcodigoservidor.text:= fdquerysql4.fieldbyname('codigo_servidor').asstring;
      buscanacombo(fdquerysql4.fieldbyname('protocolo').asstring,frmconfig,cboprotocolo);
      lblimapserver.text := fdquerysql4.fieldbyname('servidor_recebimento').asstring;
      lblportarecebimento.text := fdquerysql4.fieldbyname('porta_recebimento').asstring;
      lblsmtpserver.text := fdquerysql4.fieldbyname('servidor_envio').asstring;
      lblportaenvio.text := fdquerysql4.fieldbyname('porta_envio').asstring;
      controle_email:='ALTERA��O';
      lblimapserver.setfocus;
   end;
end;

procedure Tfrmconfig.gridemailKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   with modulo_dados,frmprincipal do
   begin
      if key = VK_DELETE then
         begin
            resp:=messagedlg('Confirma a Remo��o deste Servidor de Email, n�o poder� haver contas vinculadas a ele ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
            if resp = idyes then
               begin
                  sql:='DELETE FROM USER_geoapolo_mail_server WHERE codigo_servidor = :pcodigoservidor';
                  fdquerysql3.close;
                  fdquerysql3.sql.text := sql;
                  fdquerysql3.parambyname('pcodigoservidor').asstring:=fdquerysql4.fieldbyname('codigo_servidor').asstring;
                  if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                     begin
                        messagedlg('SERVIDOR DE EMAIL REMOVIDO COM SUCESSO !!!',mtinformation,[mbok],0);
                        lista_servidores_email;
                        lblimapserver.setfocus;
                     end
                  else
                     begin
                        lblimapserver.setfocus;
                        exit;
                     end;
               end
            else
               begin
                  lblimapserver.setfocus;
                  exit;
               end;
         end;
   end;
end;

procedure Tfrmconfig.lblAlturaKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      lblentidade.SetFocus;
end;

procedure Tfrmconfig.lblaplinstaladorKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      chkintegra_apolo.SetFocus;
end;

procedure Tfrmconfig.lblcaminhobackupKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      lblinstalacaolocal.SetFocus;
end;

procedure Tfrmconfig.lblcaminhobasealvolojaKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lblentcodconsumidorfinal.SetFocus;
end;

procedure Tfrmconfig.lblcaminhodocmissaopopularKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lblcategcodformadoropiniao.setfocus;
end;

procedure Tfrmconfig.lblcontaemailKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return))  then
      lblsenha.setfocus;
end;

procedure Tfrmconfig.lbldirnovasversoesKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      lblaplinstalador.setfocus;;
end;

procedure Tfrmconfig.lblcategcodestrpadraofornecedoresKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if key = vk_f4 then
      spbuscacategpadraofornecedores.Click;
   if ((key = vk_return) or (key = vk_tab)) then
      begin
         cinsistema.ActivePageIndex:=2;
         cinsistema.Refresh;
      end;
end;

procedure Tfrmconfig.lblcategcodformadoropiniaoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = VK_F4 then
      spbuscacategoriaformaopiniao.click;
   if key = VK_RETURN then
      spbsalvar.click;
end;

procedure Tfrmconfig.lblentcodconsumidorfinalKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   with modulo_dados do
   begin
      if (key = vk_tab) or (key = vk_return) then
         begin
            if (lblentcodconsumidorfinal.text <> '') and (lblentnomeconsumidorfinal.caption = '...') then
               begin
                  if (frmprincipal.integraentidadesapolo = 'Integra') then
                     begin
                        sql:='SELECT e.entnome FROM entidade e with(nolock) WHERE e.entcod = :pentcod';
                        fdquerysql18.close;
                        fdquerysql18.sql.text := sql;
                        fdquerysql18.parambyname('pentcod').asstring :=lblentcodconsumidorfinal.Text;
                        if executaracao(fdquerysql18, fdbanco, true, dtsfdquerysql18) then
                           begin
                              lblentnomeconsumidorfinal.Caption := fdquerysql18.fieldbyname('entnome').asstring;
                              lblentnomeconsumidorfinal.Refresh;
                           end;
                     end;
                end;
            cinsistema.ActivePageIndex := 5;
            cinsistema.Refresh
         end;
   end;
   if key = vk_f4 then
      spbuscaentidade.Click;
end;

procedure Tfrmconfig.lblentidadeKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      lblorigcodestrpadrao.SetFocus;
   if key = vk_f4 then
      spbentidade.Click;
end;

procedure Tfrmconfig.lblentidadeparceiraEnter(Sender: TObject);
begin
 {  with modulo_dados do
   begin
      if lblnomeverba.Caption = 'Descri��o Verba de Telefone' then
         begin
             sql:='select ver_codigo, ver_nome from fo_verbas WHERE ver_codigo = '+chr(39)+lblvercodigo.text+chr(39);
             sqlrun(sql,querysql1,banco_mix);
             if querysql1.RecordCount > 0 then
                begin
                   lblnomeverba.Caption := querysql1.fieldbyname('ver_nome').asstring;
                   lblnomeverba.Refresh;
                end;
         end;
   end; }
end;

procedure Tfrmconfig.lblentidadeparceiraKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f4 then
      spbuscategoria.click;
   if ((key = vk_return) or (key = vk_tab)) then
      lblmotocorcodestr.SetFocus;
end;

procedure Tfrmconfig.lblgrupohardwareKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = VK_F4 then
      spbuscagruphardware.click;
   if (key = vk_tab) or (key = vk_return) then
      spbsalvar.click;
end;

procedure Tfrmconfig.lblgruposoftwareKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = VK_F4 then
      spbuscagruposoftware.click;
   if (key = vk_tab) or (key = vk_return) then
      lblgrupohardware.setfocus;
end;

procedure Tfrmconfig.lblimapserverKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      lblportarecebimento.setfocus;
end;

procedure Tfrmconfig.lblinstalacaolocalKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      lbldirnovasversoes.SetFocus;
end;

procedure Tfrmconfig.lblmotocorcodestrKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      lblorigcodestrpadrao.SetFocus;
   if key = vk_f4 then
      spbbuscamotocorcodestr.Click;
end;

procedure Tfrmconfig.lblportaenvioKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      btninserir.setfocus;
end;

procedure Tfrmconfig.lblportarecebimentoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      lblsmtpserver.setfocus;
end;

procedure Tfrmconfig.lblvercodigoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab)  then
      cboentidades.SetFocus;
   if key = vk_f4 then
      spbuscaorigempadrao.Click;
end;

procedure Tfrmconfig.spbbuscaalvolojaClick(Sender: TObject);
begin
{   opendialog.execute;
   lblcaminhodabasealvoloja.text := opendialog.FileName;
   lblcaminhodabasealvoloja.refresh;}
   messagedlg('UTILIZANDO O WINDOWS EXPLORER, COPIE E COLE O CAMINHO DA BASE E CONFIGURE A TAG DE NUMERO DO CAIXA {NUMERODOCAIXA}',mtwarning,[mbok],0);
   lblcaminhobasealvoloja.setfocus;
end;

procedure Tfrmconfig.spbbuscamotocorcodestrClick(Sender: TObject);
var
   i:integer;
begin
   with modulo_dados do
   begin
      if ((cboentidades.text = 'Integra') or (cboentidades.text = 'Mescla')) then
         begin
            sql:='SELECT mo.motocorcodestr, mo.motocordescr';
            sql:=sql+' FROM MOTIVO_OCOR mo with(nolock)';
            sql:=sql+' WHERE mo.MotOcorGrupo = :pmotocorgrupo';
            sql:=sql+' ORDER BY mo.MotOcorCodEstr ASC';
            fdquerysql6.close;
            fdquerysql6.sql.text := sql;
            fdquerysql6.parambyname('pmotocorgrupo').asstring :='F'
         end
      else if (cboentidades.text = 'N�o Integra') then
         begin
            sql:=' SELECT * FROM USER_geoapolo_motivo_ocor';
            fdquerysql6.close;
            fdquerysql6.sql.text := sql;
         end;
      if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
         begin
            application.createform(tfrmconsulta3, frmconsulta3);
            with frmconsulta3 do
            begin
                for i:= 0 to fdquerysql6.fields.count -1 do
                begin
                   cbocampo.items.add(fdquerysql6.fields[i].displayname);
                   cbordem.items.add(fdquerysql6.fields[i].displayname);
                end;
               dtsfdquerysql6.DataSet := fdquerysql6;
               gridconsulta.DataSource:=dtsfdquerysql6;
               frmconsulta3.controle:='MOTIVO_OCORRENCIA_PADRAO';
               frmconsulta3.showmodal;
            end;
         end;
   end;
end;

procedure Tfrmconfig.spbcaminhodoctiClick(Sender: TObject);
begin
   opendialog.execute;
   lblcaminhodocti.text := opendialog.filename;
   lblcaminhodocti.refresh;
end;

procedure Tfrmconfig.spbdocanexopicClick(Sender: TObject);
begin
   opendialog.execute;
   lbldocanexopic.text := opendialog.filename;
   lbldocanexopic.refresh;
end;

procedure Tfrmconfig.spbdocmissaopopularClick(Sender: TObject);
begin
   opendialog.execute;
   lblcaminhodocmissaopopular.text := opendialog.filename;
   lblcaminhodocmissaopopular.refresh;
end;

procedure Tfrmconfig.spbentidadeClick(Sender: TObject);
var
   i:integer;
begin
   with modulo_dados, frmprincipal do
   begin
      {QUANDO A OP��O DE INTEGRA��O FOR INTEGRA OU MESCLA, VAI BUSCAR AS ENTIDADES DO APOLO, J� QUANDO FOR N�O INTEGRA, PEGA S� DA BASE GEOAPOLO}
      integraentidadeapolo:=verifica_integracao_entidades(frmprincipal.codigo_empresa);
      if (integraentidadeapolo = 'Mescla') or (integraentidadeapolo = 'Integra') then
         begin
            sql:='SELECT e.entcod, e.entnome, ec.categcodestr, cat.categnome';
            sql:=sql+' FROM entidade e with(nolock) ';
            sql:=sql+' INNER JOIN ent_categ ec with(nolock) ON e.entcod = ec.entcod';
            sql:=sql+' INNER JOIN categoria cat with(nolock) ON ec.categcodestr = cat.categcodestr ';
         end
      else if (integraentidadeapolo = 'N�o Integra') then
         begin
            sql:= 'SELECT  uge.geoentcod, uge.geoentnome,ugec.geocategcodestr, ugc.geocategnome';
            sql:=sql+' FROM USER_geoapolo_entidade uge with(nolock)';
            sql:=sql+' INNER JOIN USER_geoapolo_entcateg ugec with(nolock) ON uge.geoentcod = ugec.geoentcod';
            sql:=sql+' INNER JOIN USER_geoapolo_categoria ugc with(nolock) ON ugec.geocategcodestr = ugc.geocategcodestr';
         end;
      fdquerysql9.close;
      fdquerysql9.SQL.Clear;
      fdquerysql9.sql.text := sql;
      if executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            with frmconsulta3 do
            begin
                fdquerysql9.First;
                for i:= 0 to fdquerysql9.fields.count -1 do
                begin
                   cbocampo.items.add(fdquerysql9.fields[i].displayname);
                   cbordem.items.add(fdquerysql9.fields[i].displayname);
                end;
               dtsfdquerysql9.DataSet:=fdquerysql9;
               gridconsulta.datasource:=dtsfdquerysql9;
               if ((integraentidadeapolo = 'Integra') or (integraentidadeapolo = 'Mescla')) then
                  frmconsulta3.controle:='BUSCAENTPADRAOOCORAPOLO'
               else if (cboentidades.text = 'Não Integra') then
                  frmconsulta3.controle := 'BUSCAENTPADRAOOCORGEOAPOLO';
               frmconsulta3.ShowModal;
            end;
         end;
   end;
end;

procedure Tfrmconfig.spblimparClick(Sender: TObject);
begin
   lblcaminhobackup.Clear; lblinstalacaolocal.Clear; lbldirnovasversoes.Clear; lblaplinstalador.clear;
   chkintegrapolo.Checked := false; chkapolo.Checked := false; chkgeoapolo.Checked := false;
   chkgeracamp.Checked := false; chkintegra_apolo.Checked := false; chkintegramix.Checked:=false;
   cboentidades.ItemIndex := -1; lblentidadeparceira.Clear;   lblcaminhoinventario.clear; lblgruposoftware.clear;
   lblgrupohardware.clear; lblcaminhodocti.clear; lblcaminhodocmissaopopular.clear; lbldocanexopic.clear;
end;

procedure Tfrmconfig.spbretornarClick(Sender: TObject);
begin
   close;
end;

procedure Tfrmconfig.spbsalvarClick(Sender: TObject);
begin
   with modulo_dados,frmprincipal do
   begin
   if lblgruposoftware.text = '' then
      lblgruposoftware.text:='0';
   //
   if lblgrupohardware.text = '' then
      lblgrupohardware.text := '0';
   //
   if frmprincipal.codigo_empresa = '' then
      begin
        sql:='SELECT TOP 1 empcod FROM USER_geoapolo_empresas';
        fdquerysql.close;
        fdquerysql.sql.clear;
        fdquerysql.sql.text := sql;
        if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
           begin
              frmprincipal.codigo_empresa:=fdquerysql.FieldByName('empcod').AsString;
           end;
      end;
   resp:=messagedlg('Confirma as Configurações de Sistema ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
   if resp = idyes then
      begin
         {ROTINA PARA TRATAMENTO DAS VARI�VEIS PARA RETIRAR AS BARRAS \ E TROCAR POR - PARA GRAVAR NO BANCO}
         {FIM TRATAMENTO}
         if frmprincipal.controle = 'INCLUSÃO' then
            begin
               sql:='INSERT INTO USER_geoapolo_configuracoes (';
               sql:=sql+'  empcod, caminhobackupsistema, instalacaolocal, localnovasversoes, localinstaladorversoes,';
               sql:=sql+'  integra_geosec_cctrlcodestr, indexconsultasimediatas, gera_camp_baseapolo,';
               sql:=sql+'  integra_ocorrenciasptomix, integra_base_apolomix, integra_entidades_apolo, integrabasemix,';
               sql:=sql+'  caminhoarquivoconvenio, entcategparceira, geoentcod, caminhoexclusao_faxineiro,';
               sql:=sql+'  caminhoinventario, grupohardware, gruposoftware, caminhodocti,';
               sql:=sql+'  caminhodocmissaopopular, tempomaximomissao, categcodestr_formadoropiniao,';
               sql:=sql+'  status_fechapic, codigo_tipocamp_geracamp, caminhodocanexopic,';
               sql:=sql+'  motocorcodestr, origcodestr, tiposolocorcod, categcodestr_padraofornecedores,';
               sql:=sql+'  caminhobasealvoloja, entcod_consumidorfinal)';
               sql:=sql+' VALUES (';
               sql:=sql+'  :pempcod, :pcaminhobackupsistema, :pinstalacaolocal, :plocalnovasversoes, :plocalinstaladorversoes,';
               sql:=sql+'  :pintegra_geosec_cctrlcodestr, :pindexconsultasimediatas, :pgera_camp_baseapolo,';
               sql:=sql+'  :pintegra_ocorrenciasptomix, :pintegra_base_apolomix, :pintegra_entidades_apolo, :pintegrabasemix,';
               sql:=sql+'  :pcaminhoarquivoconvenio, :pentcategparceira, :pgeoentcod, :pcaminhoexclusao_faxineiro,';
               sql:=sql+'  :pcaminhoinventario, :pgrupohardware, :pgruposoftware, :pcaminhodocti,';
               sql:=sql+'  :pcaminhodocmissaopopular, :ptempomaximomissao, :pcategcodestr_formadoropiniao,';
               sql:=sql+'  :pstatus_fechapic, :pcodigo_tipocamp_geracamp, :pcaminhodocanexopic,';
               sql:=sql+'  :pmotocorcodestr, :porigcodestr, :ptiposolocorcod, :pcategcodestr_padraofornecedores,';
               sql:=sql+'  :pcaminhobasealvoloja, :pentcod_consumidorfinal)';
               fdquerysql3.Close;
               fdquerysql3.sql.clear;
               fdquerysql3.SQL.Text := sql;
               fdquerysql3.ParamByName('pempcod').AsString := frmprincipal.codigo_empresa;
               fdquerysql3.ParamByName('pcaminhobackupsistema').AsString := lblcaminhobackup.Text;
               fdquerysql3.ParamByName('pinstalacaolocal').AsString := lblinstalacaolocal.Text;
               fdquerysql3.ParamByName('plocalnovasversoes').AsString := lbldirnovasversoes.Text;
               fdquerysql3.ParamByName('plocalinstaladorversoes').AsString := lblaplinstalador.Text;
               fdquerysql3.ParamByName('pintegra_geosec_cctrlcodestr').AsString := integra_com_apolo;
               fdquerysql3.ParamByName('pindexconsultasimediatas').AsInteger := apolo_geoapolo;
               fdquerysql3.ParamByName('pgera_camp_baseapolo').AsString := campbaseapolo;
               fdquerysql3.ParamByName('pintegra_ocorrenciasptomix').AsString := integraocorrmix;
               fdquerysql3.ParamByName('pintegra_base_apolomix').AsString := integrabaseapolo;
               fdquerysql3.ParamByName('pintegra_entidades_apolo').AsString := cboentidades.Text;
               fdquerysql3.ParamByName('pintegrabasemix').AsString := integrabasemix;
               fdquerysql3.ParamByName('pcaminhoarquivoconvenio').AsString := lblcaminhoarquivoconvenio.Text;
               fdquerysql3.ParamByName('pentcategparceira').AsString := lblentidadeparceira.Text;
               fdquerysql3.ParamByName('pgeoentcod').AsString := lblentidade.Text;
               fdquerysql3.ParamByName('pcaminhoexclusao_faxineiro').AsString := '';
               fdquerysql3.ParamByName('pcaminhoinventario').AsString := lblcaminhoinventario.Text;
               fdquerysql3.ParamByName('pgrupohardware').AsString := lblgrupohardware.Text;
               fdquerysql3.ParamByName('pgruposoftware').AsString := lblgruposoftware.Text;
               fdquerysql3.ParamByName('pcaminhodocti').AsString := lblcaminhodocti.Text;
               fdquerysql3.ParamByName('pcaminhodocmissaopopular').AsString := lblcaminhodocmissaopopular.Text;
               fdquerysql3.ParamByName('ptempomaximomissao').AsString := lbltempoduracao.Text;
               fdquerysql3.ParamByName('pcategcodestr_formadoropiniao').AsString := lblcategcodformadoropiniao.Text;
               fdquerysql3.ParamByName('pstatus_fechapic').AsString := lblstatusfechapic.Text;
               fdquerysql3.ParamByName('pcodigo_tipocamp_geracamp').AsString := lblcodtipocamp.Text;
               fdquerysql3.ParamByName('pcaminhodocanexopic').AsString := lbldocanexopic.Text;
               fdquerysql3.ParamByName('pmotocorcodestr').AsString := lblmotocorcodestr.Text;
               fdquerysql3.ParamByName('porigcodestr').AsString := lblorigcodestrpadrao.Text;
               fdquerysql3.ParamByName('ptiposolocorcod').AsString := lbltiposolucaoocorrencia.Text;
               fdquerysql3.ParamByName('pcategcodestr_padraofornecedores').AsString := lblcategcodestrpadraofornecedores.Text;
               fdquerysql3.ParamByName('pcaminhobasealvoloja').AsString := lblcaminhobasealvoloja.Text;
               fdquerysql3.ParamByName('pentcod_consumidorfinal').AsString := lblentcodconsumidorfinal.Text;
               if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                  begin
                     messagedlg('CONFIGURAÇÕES SALVAS COM SUCESSO !!!',mtinformation,[mbok],0);
                     cinsistema.ActivePageIndex:=0; lblcaminhobackup.SetFocus;
                     frmprincipal.controle:='INCLUSÃO';
                  end
               else
                  begin
                     messagedlg('PROBLEMAS AO TENTAR GRAVAR AS INFORMA��ES !!!',mterror,[mbok],0);
                     lblcaminhobackup.SetFocus;
                  end;
            end
         else if frmprincipal.controle = 'ALTERAÇÃO' then
            begin
               sql:='UPDATE USER_geoapolo_configuracoes SET';
               sql:=sql+' caminhobackupsistema = :pcaminhobackupsistema, instalacaolocal = :pinstalacaolocal';
               sql:=sql+', localnovasversoes = :plocalnovasversoes, localinstaladorversoes = :plocalinstaladorversoes';
               sql:=sql+', integra_geosec_cctrlcodestr = :pintegra_geosec_cctrlcodestr, indexconsultasimediatas = :pindexconsultasimediatas';
               sql:=sql+', gera_camp_baseapolo = :pgera_camp_baseapolo, integra_ocorrenciasptomix = :pintegra_ocorrenciasptomix';
               sql:=sql+', integra_base_apolomix = :pintegra_base_apolomix, integra_entidades_apolo = :pintegra_entidades_apolo';
               sql:=sql+', integrabasemix = :pintegrabasemix, caminhoarquivoconvenio = :pcaminhoarquivoconvenio';
               sql:=sql+', entcategparceira = :pentcategparceira, geoentcod = :pgeoentcod, caminhoinventario = :pcaminhoinventario';
               sql:=sql+', grupohardware = :pgrupohardware, gruposoftware = :pgruposoftware, caminhodocti = :pcaminhodocti';
               sql:=sql+', caminhodocmissaopopular = :pcaminhodocmissaopopular, tempomaximomissao = :ptempomaximomissao';
               sql:=sql+', categcodestr_formadoropiniao = :pcategcodestr_formadoropiniao, status_fechapic = :pstatus_fechapic';
               sql:=sql+', codigo_tipocamp_geracamp = :pcodigo_tipocamp_geracamp, caminhodocanexopic = :pcaminhodocanexopic';
               sql:=sql+', motocorcodestr = :pmotocorcodestr, origcodestr = :porigcodestr, tiposolocorcod = :ptiposolocorcod';
               sql:=sql+', categcodestr_padraofornecedores = :pcategcodestr_padraofornecedores';
               sql:=sql+', caminhobasealvoloja = :pcaminhobasealvoloja, entcod_consumidorfinal = :pentcod_consumidorfinal';
               sql:=sql+' WHERE empcod = :pempcod';
               fdquerysql3.Close;
               fdquerysql3.sql.clear;
               fdquerysql3.SQL.Text := sql;
               fdquerysql3.ParamByName('pcaminhobackupsistema').AsString := lblcaminhobackup.Text;
               fdquerysql3.ParamByName('pinstalacaolocal').AsString := lblinstalacaolocal.Text;
               fdquerysql3.ParamByName('plocalnovasversoes').AsString := lbldirnovasversoes.Text;
               fdquerysql3.ParamByName('plocalinstaladorversoes').AsString := lblaplinstalador.Text;
               fdquerysql3.ParamByName('pintegra_geosec_cctrlcodestr').AsString := integra_com_apolo;
               fdquerysql3.ParamByName('pindexconsultasimediatas').AsInteger := apolo_geoapolo;
               fdquerysql3.ParamByName('pgera_camp_baseapolo').AsString := campbaseapolo;
               fdquerysql3.ParamByName('pintegra_ocorrenciasptomix').AsString := integraocorrmix;
               fdquerysql3.ParamByName('pintegra_base_apolomix').AsString := integrabaseapolo;
               fdquerysql3.ParamByName('pintegra_entidades_apolo').AsString := cboentidades.Text;
               fdquerysql3.ParamByName('pintegrabasemix').AsString := integrabasemix;
               fdquerysql3.ParamByName('pcaminhoarquivoconvenio').AsString := lblcaminhoarquivoconvenio.Text;
               fdquerysql3.ParamByName('pentcategparceira').AsString := lblentidadeparceira.Text;
               fdquerysql3.ParamByName('pgeoentcod').AsString := lblentidade.Text;
               fdquerysql3.ParamByName('pcaminhoinventario').AsString := lblcaminhoinventario.Text;
               fdquerysql3.ParamByName('pgrupohardware').AsString := lblgrupohardware.Text;
               fdquerysql3.ParamByName('pgruposoftware').AsString := lblgruposoftware.Text;
               fdquerysql3.ParamByName('pcaminhodocti').AsString := lblcaminhodocti.Text;
               fdquerysql3.ParamByName('pcaminhodocmissaopopular').AsString := lblcaminhodocmissaopopular.Text;
               fdquerysql3.ParamByName('ptempomaximomissao').AsString := lbltempoduracao.Text;
               fdquerysql3.ParamByName('pcategcodestr_formadoropiniao').AsString := lblcategcodformadoropiniao.Text;
               fdquerysql3.ParamByName('pstatus_fechapic').AsString := lblstatusfechapic.Text;
               fdquerysql3.ParamByName('pcodigo_tipocamp_geracamp').AsString := lblcodtipocamp.Text;
               fdquerysql3.ParamByName('pcaminhodocanexopic').AsString := lbldocanexopic.Text;
               fdquerysql3.ParamByName('pmotocorcodestr').AsString := lblmotocorcodestr.Text;
               fdquerysql3.ParamByName('porigcodestr').AsString := lblorigcodestrpadrao.Text;
               fdquerysql3.ParamByName('ptiposolocorcod').AsString := lbltiposolucaoocorrencia.Text;
               fdquerysql3.ParamByName('pcategcodestr_padraofornecedores').AsString := lblcategcodestrpadraofornecedores.Text;
               fdquerysql3.ParamByName('pcaminhobasealvoloja').AsString := lblcaminhobasealvoloja.Text;
               fdquerysql3.ParamByName('pentcod_consumidorfinal').AsString := lblentcodconsumidorfinal.Text;
               fdquerysql3.ParamByName('pempcod').AsString := frmprincipal.codigo_empresa;
               if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
                  begin
                     messagedlg('CONFIGURAÇÕES ALTERADAS COM SUCESSO !!!',mtinformation,[mbok],0);
                     cinsistema.ActivePageIndex:=0; lblcaminhobackup.SetFocus;
                     frmconfig.Refresh; frmprincipal.controle:='INCLUSÃO';
                  end
               else
                  begin
                     messagedlg('PROBLEMAS AO TENTAR GRAVAR A ALTERAÇÃO DAS INFORMA��ES !!!',mterror,[mbok],0);
                     lblcaminhobackup.SetFocus;
                  end;
            end;
         spblimpar.Click;
      end;
   end;
end;

procedure Tfrmconfig.spbuscacategoriaformaopiniaoClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      sql:='SELECT geocategcodestr, geocategnome FROM USER_geoapolo_categoria';
      sql:=sql+' ORDER BY geocategcodestr ASC';
       fdquerysql.Close;
       fdquerysql.sql.clear;
       fdquerysql.SQL.Text := sql;
       if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            frmconsulta3.controle:='CATEGORIAFORMADOROPINIAO';
            dtsfdquerysql.DataSet :=fdquerysql;
            frmconsulta3.gridconsulta.DataSource := dtsfdquerysql;
            frmconsulta3.ShowModal;
         end
      else
         begin
            messagedlg('NÃO HÁ CATEGORIAS DISPONÍVEIS NA BASE DE DADOS',mterror,[mbok],0);
            lblcategcodformadoropiniao.setfocus;
            exit;
         end;

   end;
end;

procedure Tfrmconfig.spbuscacategpadraofornecedoresClick(Sender: TObject);
var
   i:integer;
begin
   with modulo_dados do
   begin
      if ((cboentidades.text = 'Não Integra') or (cboentidades.text = 'Mescla')) then
         begin
            // UTILIZA A TABELA DE CATEGORIAS DO GEOAPOLO
            sql:='SELECT ugc.geocategcodestr, ugc.geocategnome, ugc.geocategcodniv, ' ;
            sql:=sql+'   ugc.geocateggrupo, ugc.geoempcod, ugc.geocategcodalt';
            sql:=sql+' FROM USER_geoapolo_categoria ugc with(nolock) ';
            sql:=sql+' ORDER BY ugc.geocategcodestr';
         end
      else if (cboentidades.text = 'Integra') then
         begin
            // BUSCA AS CATEGORIAS SOMENTE DA BASE APOLO
            sql:='SELECT ec.categcodestr, cat.categnome FROM ent_categ ec';
            sql:=sql+' INNER JOIN categoria cat ON ec.CategCodEstr = cat.CategCodEstr';
            sql:=sql+' GROUP BY ec.CategCodEstr, cat.categnome';
            sql:=sql+' ORDER BY ec.CategCodEstr';
         end;
       fdquerysql9.Close;
       fdquerysql9.sql.clear;
       fdquerysql9.SQL.Text := sql;
       if executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            frmconsulta3.controle:='CATEGORIAPADRAOFORNECEDORES';
            dtsfdquerysql9.DataSet:=fdquerysql9;
            with frmConsulta3 do
            begin
                for i:= 0 to fdquerysql9.fields.count -1 do
                begin
                   cbocampo.items.add(fdquerysql9.fields[i].displayname);
                   cbordem.items.add(fdquerysql9.fields[i].displayname);
                end;
            end;
            frmconsulta3.ShowModal;
         end;
   end;
end;

procedure Tfrmconfig.spbuscacodtipocampClick(Sender: TObject);
var i:integer;
begin
   with modulo_dados do
   begin
      sql:='SELECT * FROM USER_geoapolo_tipo_campanha';
       fdquerysql.Close;
       fdquerysql.sql.clear;
       fdquerysql.SQL.Text := sql;
       if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
            dtsfdquerysql.DataSet := fdquerysql;
            application.createform(tfrmconsulta3, frmconsulta3);
            with frmConsulta3 do
            begin
                for i:= 0 to fdquerysql.fields.count -1 do
                begin
                   cbocampo.items.add(fdquerysql.fields[i].displayname);
                   cbordem.items.add(fdquerysql.fields[i].displayname);
                end;
            end;
            frmconsulta3.gridconsulta.DataSource:=dtsfdquerysql;
            frmconsulta3.controle:='BUSCATIPOCAMPANHACONFIG';
            frmconsulta3.showmodal;
         end;
   end;
end;

procedure Tfrmconfig.spbuscaentidadeClick(Sender: TObject);
var
   i:integer;
begin
   with modulo_dados do
   begin
       sql:='SELECT e.entcod, e.entnome FROM entidade e WITH(NOLOCK) WHERE e.entnome LIKE :pentnome';
       fdquerysql18.Close;
       fdquerysql18.sql.clear;
       fdquerysql18.SQL.Text := sql;
       fdquerysql18.ParamByName('pentnome').AsString := 'CONSUMIDOR%';
       if executaracao(fdquerysql18, fdbanco, true, dtsfdquerysql18) then
         begin
            dtsfdquerysql18.DataSet := fdquerysql18;
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            with frmconsulta3 do
            begin
               gridconsulta.DataSource := dtsfdquerysql18;
                for i:= 0 to fdquerysql18.fields.count -1 do
                begin
                   cbocampo.items.add(fdquerysql18.fields[i].displayname);
                   cbordem.items.add(fdquerysql18.fields[i].displayname);
                end;
               frmconsulta3.controle:='BUSCAENTIDADECONSUMIDORFINALAPOLO';
               frmconsulta3.ShowModal;
            end;
         end
      else
         begin
            messagedlg('N�O H� NO SISTEMA NENHUMA ENTIDADE QUE TENHA O NOME CONSUMIDOR',mtwarning,[mbok],0);
            lblentcodconsumidorfinal.SetFocus;
            exit;
         end;
   end;
end;

procedure Tfrmconfig.spbuscagruphardwareClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      sql:='SELECT * FROM USER_geoapolo_produto_grupo';
       fdquerysql.Close;
       fdquerysql.sql.clear;
       fdquerysql.SQL.Text := sql;
       if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
            application.createform(tfrmconsulta3, frmconsulta3);
            with frmconsulta3 do
            begin
               dtsfdquerysql.DataSet := fdquerysql;
               gridconsulta.DataSource:=dtsfdquerysql;
               frmconsulta3.controle:='GRUPO_HARDWARE_PARAMETRO';
               frmconsulta3.showmodal;
            end;
         end;
   end;
end;

procedure Tfrmconfig.spbuscagruposoftwareClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      sql:='SELECT * FROM USER_geoapolo_produto_grupo';
       fdquerysql.Close;
       fdquerysql.sql.clear;
       fdquerysql.SQL.Text := sql;
       if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
            application.createform(tfrmconsulta3, frmconsulta3);
            with frmconsulta3 do
            begin
               dtsfdquerysql.DataSet := fdquerysql;
               gridconsulta.DataSource:=dtsfdquerysql;
               frmconsulta3.controle:='GRUPO_SOFTWARE_PARAMETRO';
               frmconsulta3.showmodal;
            end;
         end;
   end;
end;

procedure Tfrmconfig.spbuscaorigempadraoClick(Sender: TObject);
var
   i:integer;
begin
   with modulo_dados do
   begin
      if ((cboentidades.text = 'Integra') or (cboentidades.text = 'Mescla')) then
         begin
            sql:='SELECT o.OrigCodEstr, o.OrigNome';
            sql:=sql+' FROM ORIGEM o with(nolock)';
            sql:=sql+' WHERE o.OrigGrupo = :poriggrupo';
            sql:=sql+' AND o.OrigAtiva = :porigativa';
            sql:=sql+' ORDER BY o.OrigCodEstr ASC';
         end
      else if (cboentidades.text = 'Não Integra') then
         begin
            sql:='SELECT * FROM USER_geoapolo_origens';
         end;
       fdquerysql6.Close;
       fdquerysql6.SQL.Text := sql;
       if ((cboentidades.text = 'Integra') or (cboentidades.text = 'Mescla')) then
          begin
             fdquerysql6.ParamByName('poriggrupo').AsString := 'F';
             fdquerysql6.ParamByName('porigativa').AsString := 'Sim';
          end;
       if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            with frmconsulta3 do
            begin
                for i:= 0 to fdquerysql6.fields.count -1 do
                begin
                   cbocampo.items.add(fdquerysql6.fields[i].displayname);
                   cbordem.items.add(fdquerysql6.fields[i].displayname);
                end;
               dtsfdquerysql6.DataSet:=fdquerysql6;
               gridconsulta.datasource:=dtsfdquerysql6;
               if ((cboentidades.text = 'Integra') or (cboentidades.text = 'Mescla')) then
                  frmconsulta3.controle:='BUSCAORIGEMPADRAOIM'
               else if (cboentidades.text = 'Não Integra') then
                  frmconsulta3.controle := 'BUSCAORIGEMPADRAONI';
               frmconsulta3.ShowModal;
            end;
         end;
   end;
end;

procedure Tfrmconfig.spbuscaservidoremailClick(Sender: TObject);
begin
    with modulo_dados do
    begin
        sql:='SELECT servidor_recebimento, porta_recebimento FROM USER_geoapolo_mail_server ORDER BY servidor_recebimento ASC';
        fdquerysql1.Close;
        fdquerysql1.sql.clear;
        fdquerysql1.SQL.Text := sql;
        if executaracao(fdquerysql1, fdbanco, true, dtsfdquerysql1) then
          begin
             application.CreateForm(tfrmconsulta3, frmconsulta3);
             with frmconsulta3 do
             begin
                dtsfdquerysql1.DataSet := fdquerysql1;
                gridconsulta.DataSource := dtsfdquerysql1;
                frmconsulta3.controle := 'BUSCASERVIDOREMAIL';
                frmconsulta3.ShowModal;
             end;
          end;
    end;
end;

procedure Tfrmconfig.spbuscasolucaoocorrenciaClick(Sender: TObject);
var
   i:integer;
begin
   with modulo_dados do
   begin
      if (frmprincipal.integraentidadesapolo = 'Integra') or (frmprincipal.integraentidadesapolo = 'Mescla') then
         begin
            sql:='SELECT tso.tiposolocorcod, tso.tiposolocornome, tso.tiposolocortexto';
            sql:=sql+' FROM TIPO_SOL_OCOR tso with(nolock)';
            sql:=sql+' ORDER BY tso.TipoSolOcorCod';
         end
      else if (frmprincipal.integraentidadesapolo = 'N�o Integra') then
         begin
            sql:='SELECT ugtso.tiposolocorcod, ugtso.tiposolocornome, ugtso.tiposolocortexto';
            sql:=sql+' FROM USER_geoapolo_tipo_solocor ugtso with(nolock)';
            sql:=sql+' ORDER BY ugtso.tiposolocorcod';
         end;
       fdquerysql7.Close;
       fdquerysql7.sql.clear;
       fdquerysql7.SQL.Text := sql;
       if executaracao(fdquerysql7, fdbanco, true, dtsfdquerysql7) then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            integraentidadeapolo:=verifica_integracao_entidades(frmprincipal.codigo_empresa);
            with frmconsulta3 do
            begin
                fdquerysql7.First;
                for i:= 0 to fdquerysql7.fields.count -1 do
                begin
                   cbocampo.items.add(fdquerysql7.fields[i].displayname);
                   cbordem.items.add(fdquerysql7.fields[i].displayname);
                end;
               dtsfdquerysql7.DataSet:=fdquerysql7;
               gridconsulta.datasource:=dtsfdquerysql7;
               if ((integraentidadeapolo = 'Integra') or (integraentidadeapolo = 'Mescla')) then
                  frmconsulta3.controle:='BUSCASOLOCORAPOLO'
               else if (cboentidades.text = 'Não Integra') then
                  frmconsulta3.controle := 'BUSCASOLOCORGEOAPOLO';
               frmconsulta3.ShowModal;
            end;
         end;
   end;
end;

procedure Tfrmconfig.spbuscastatusfechapicClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      sql:='SELECT * FROM USER_geoapolo_pic_status';
       fdquerysql.Close;
       fdquerysql.sql.clear;
       fdquerysql.SQL.Text := sql;
       if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
         begin
            dtsfdquerysql.DataSet := fdquerysql;
            application.createform(tfrmconsulta3, frmconsulta3);
            frmconsulta3.gridconsulta.DataSource:=dtsfdquerysql;
            frmconsulta3.controle:='BUSCASTATUSPICCONFIG';
            frmconsulta3.showmodal;
         end;
   end;
end;

procedure Tfrmconfig.spbuscaverbaClick(Sender: TObject);
begin
{    if integrabasemix = 'S' then
       begin
          with modulo_dados do
          begin
             sql:='select ver_codigo, ver_nome from fo_verbas order by ver_nome asc';
             sqlrun(sql,querysql1,banco_mix);
             if querysql1.RecordCount > 0 then
                begin
                   application.CreateForm(tfrmconsulta, frmconsulta);
                   with frmconsulta do
                   begin
                      dtsquerysql1.DataSet := querysql1;
                      gridconsulta.DataSource := dtsquerysql1;
                      frmconsulta.controle := 'BUSCAVERBACONFIG';
                      frmconsulta.ShowModal;
                   end;
                end;
          end;
       end
    else if integrabasemix = 'N' then
       begin
          messagedlg('O SISTEMA N�O EST� CONFIGURADO PARA INTEGRAR COM A BASE MIX RH !!!',mterror,[mbok],0);
          chkintegramix.SetFocus;
          exit;
       end;}
end;

procedure Tfrmconfig.subcin_emailEnter(Sender: TObject);
begin
   controle_email:='INCLUSÃO';
   lista_servidores_email;
   lblcodigoservidor.text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_mail_server','S');
   lblcodigoservidor.refresh;
   cboprotocolo.setfocus;
end;

procedure Tfrmconfig.tabemailmonitoramentoEnter(Sender: TObject);
begin
   lblcodigoconta.text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_contas_email','S');
   lblcodigoconta.refresh;
   listacontas;
   lblcontaemail.setfocus;
   controle_email:='INCLUSÃO';
end;

function lista_servidores_email : string;
begin
   with modulo_dados, frmconfig do
   begin
      sql:='SELECT * FROM USER_geoapolo_mail_server ORDER BY codigo_servidor ASC';
       fdquerysql4.Close;
       fdquerysql4.sql.clear;
       fdquerysql4.SQL.Text := sql;
       if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
         begin
            dtsfdquerysql4.DataSet:=fdquerysql4;
            gridemail.DataSource:=dtsfdquerysql4;
            gridemail.refresh;
            cboprotocolo.setfocus;
         end;
   end;
end;

function limpa_controles : string;
begin
   with frmconfig do
   begin
      cboprotocolo.itemindex:=-1; lblimapserver.clear; lblportarecebimento.clear;
      lblsmtpserver.clear; lblportaenvio.clear;
      cinsistema.ActivePageIndex:=0; cinsistema.refresh;
   end;
end;

function limpacontrolesemail : string;
begin
   with frmconfig do
   begin
      lblcontaemail.clear; lblsenha.clear; lblservidor.clear;
   end;
end;

function listacontas : string;
begin
   with modulo_dados, frmconfig do
   begin
      sql:='SELECT * FROM USER_geoapolo_contas_email ORDER BY conta_email ASC';
       fdquerysql5.Close;
       fdquerysql5.sql.clear;
       fdquerysql5.SQL.Text := sql;
       if executaracao(fdquerysql5, fdbanco, true, dtsfdquerysql5) then
         begin
            dtsfdquerysql5.DataSet:=fdquerysql5;
            gridcontasemail.DataSource:= dtsfdquerysql5;
            gridcontasemail.refresh;
            lblcontaemail.setfocus;
         end;
   end;
end;

procedure Tfrmconfig.lblsenhaEnter(Sender: TObject);
begin
   with modulo_dados do
   begin
      if lblcontaemail.text <> '' then
         begin
             sql:='SELECT * FROM USER_geoapolo_contas_email WHERE conta_email = :pconta_email';
             fdquerysql2.Close;
             fdquerysql2.sql.clear;
             fdquerysql2.SQL.Text := sql;
             fdquerysql2.ParamByName('pconta_email').AsString := lblcontaemail.text;
             if executaracao(fdquerysql2, fdbanco, true, dtsfdquerysql2) then
               begin
                  messagedlg('ESTA CONTA DE EMAIL JÁ ESTÁ SOB MONITORAMENTO !!!',mterror,[mbok],0);
                  lblcontaemail.setfocus;
                  exit;
               end;
         end;
   end;
end;

procedure Tfrmconfig.lblsenhaKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return)) then
      lblservidor.setfocus;
end;

procedure Tfrmconfig.lblservidorKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = VK_F4 then
      spbuscaservidoremail.click;
   if ((key = vk_return)) then
      btncontaemail.click;
end;

procedure Tfrmconfig.lblsmtpserverEnter(Sender: TObject);
begin
   with modulo_dados do
   begin
      if lblimapserver.text <> '' then
         begin
             sql:='SELECT * FROM USER_geoapolo_mail_server WHERE servidor_recebimento = :pservidor_recebimento';
             fdquerysql2.Close;
             fdquerysql2.sql.clear;
             fdquerysql2.SQL.Text := sql;
             fdquerysql2.ParamByName('pservidor_recebimento').AsString := lblimapserver.text;
             if executaracao(fdquerysql2, fdbanco, true, dtsfdquerysql2) then
               begin
                  messagedlg('ESTE SERVIDOR JÁ ESTÁ CADASTRADO, FAVOR INFORMAR OUTRO !!!',mterror,[mbok],0);
                  lblimapserver.clear; lblimapserver.setfocus;
                  exit;
               end;
         end;
   end;
end;

procedure Tfrmconfig.lblsmtpserverKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      lblportaenvio.setfocus;
end;

procedure Tfrmconfig.lbltempoduracaoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if (key = vk_return) or (key = vk_tab) then
      lblcaminhodocmissaopopular.setfocus;
end;

procedure Tfrmconfig.lbltiposolucaoocorrenciaKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if key = vk_f4 then
      spbuscasolucaoocorrencia.Click;
   if ((key = vk_return) or (key = vk_tab)) then
      lblcategcodestrpadraofornecedores.SetFocus;
end;

end.
