unit unt_confignetandsys;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, Buttons, ExtCtrls, StdCtrls, registry, ComCtrls, Vcl.Mask;

type
  Tfrmconfsys = class(TForm)
    Panel1: TPanel;
    spbsalvar: TSpeedButton;
    spblimpar: TSpeedButton;
    spblocalizar: TSpeedButton;
    spbexcluir: TSpeedButton;
    grprincipal: TGroupBox;
    spbretornar: TSpeedButton;
    lblmsg1: TLabel;
    StatusBar1: TStatusBar;
    GroupBox1: TGroupBox;
    chkintegrapolo: TCheckBox;
    chkfrotas: TCheckBox;
    GroupBox2: TGroupBox;
    chkapolo: TCheckBox;
    chkgeoapolo: TCheckBox;
    chkgeracamp: TCheckBox;
    chkintegraocorrmix: TCheckBox;
    chkintegra_apolo: TCheckBox;
    GroupBox3: TGroupBox;
    lblpathfoto: TLabeledEdit;
    lbllargura: TLabeledEdit;
    lblAltura: TLabeledEdit;
    lblintegraentidadeapolo: TLabel;
    cboentidades: TComboBox;
    lblvercodigo: TLabeledEdit;
    lblnomeverba: TLabel;
    spbuscaverba: TSpeedButton;
    chkintegramix: TCheckBox;
    lblcaminhoarquivoconvenio: TLabeledEdit;
    spbopendir: TSpeedButton;
    OpenDialog1: TOpenDialog;
    lblentidadeparceira: TLabeledEdit;
    spbuscategoria: TSpeedButton;
    lblcategnomeparceiros: TLabel;
    GroupBox4: TGroupBox;
    lblentidade: TLabeledEdit;
    spbentidade: TSpeedButton;
    lblnome_entidade: TLabel;
    GroupBox5: TGroupBox;
    lblcaminhoexclusao: TLabeledEdit;
    spbgeofaxineiro: TSpeedButton;
    lblcaminhobackup: TLabeledEdit;
    lblinstalacaolocal: TLabeledEdit;
    lbldirnovasversoes: TLabeledEdit;
    lblaplinstalador: TLabeledEdit;
    procedure spbretornarClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure spbsalvarClick(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure lblmodelosinternaKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblinstalacaolocalKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lbldirnovasversoesKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblaplinstaladorKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure FormKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblcaminhobackupKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure chkintegrapoloClick(Sender: TObject);
    procedure chkapoloClick(Sender: TObject);
    procedure chkgeoapoloClick(Sender: TObject);
    procedure chkfrotasClick(Sender: TObject);
    procedure chkgeracampClick(Sender: TObject);
    procedure chkintegraocorrmixClick(Sender: TObject);
    procedure chkintegra_apoloClick(Sender: TObject);
    procedure lblpathfotoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lbllarguraKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblAlturaKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure chkintegraentidadeapoloClick(Sender: TObject);
    procedure chkintegramixClick(Sender: TObject);
    procedure spbuscaverbaClick(Sender: TObject);
    procedure spbopendirClick(Sender: TObject);
    procedure spbuscategoriaClick(Sender: TObject);
    procedure lblentidadeparceiraEnter(Sender: TObject);
    procedure lblcaminhoarquivoconvenioEnter(Sender: TObject);
    procedure spbentidadeClick(Sender: TObject);
    procedure lblentidadeKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbuscaclasseClick(Sender: TObject);
    procedure spbgeofaxineiroClick(Sender: TObject);
    procedure lblentidadeparceiraKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblvercodigoKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  frmconfsys: Tfrmconfsys;
  resp:word;
  apolo_geoapolo,i:integer;
  entidade_apolo,integrabaseapolo,integrabasemix, integraocorrmix, campbaseapolo,kit_frotas,integra_com_apolo,sql,controle:string;

implementation

uses funcoes, unt_principal, unt_dados, unt_consultav3,
  unt_Consultas4;

{$R *.dfm}

procedure Tfrmconfsys.spbretornarClick(Sender: TObject);
begin
   close;
end;

procedure Tfrmconfsys.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
   action:=cafree;
end;

procedure Tfrmconfsys.spbsalvarClick(Sender: TObject);
begin
   with modulo_dados do
   begin
   resp:=messagedlg('Confirma as Configurações de Sistema ? (Y/N)',mtconfirmation,[mbyes,mbno],0);
   if resp = idyes then
      begin
         {ROTINA PARA TRATAMENTO DAS VARIÁVEIS PARA RETIRAR AS BARRAS \ E TROCAR POR - PARA GRAVAR NO BANCO}
         lblcaminhobackup.Text:=buscatroca(lblcaminhobackup.text,'\','$');
         lblinstalacaolocal.Text := buscatroca(lblinstalacaolocal.Text,'\','$');
         lbldirnovasversoes.Text := buscatroca(lbldirnovasversoes.text,'\','$');
         lblaplinstalador.Text := buscatroca(lblaplinstalador.Text,'\','$');
         lblpathfoto.Text := buscatroca(lblpathfoto.Text,'\','$');
         lblcaminhoarquivoconvenio.Text := buscatroca(lblcaminhoarquivoconvenio.Text,'\','$');
         lblcaminhoexclusao.Text :=buscatroca(lblcaminhoexclusao.Text,'\','$');
         // pega - troca por #
         lblinstalacaolocal.Text := buscatroca(lblinstalacaolocal.Text,'-','#');
         lbldirnovasversoes.Text := buscatroca(lbldirnovasversoes.text,'-','#');
         lblaplinstalador.Text := buscatroca(lblaplinstalador.Text,'-','#');
         lblpathfoto.Text := buscatroca(lblpathfoto.Text,'-','#');
         lblcaminhoarquivoconvenio.Text := buscatroca(lblcaminhoarquivoconvenio.Text,'-','#');
         lblcaminhoexclusao.Text := buscatroca(lblcaminhoexclusao.Text,'-','#');
         {FIM TRATAMENTO}
         if controle = 'INCLUSÃO' then
            begin
       {        sql:='INSERT INTO geoapolo_configuracoes (caminhobackupsistema, instalacaolocal, localnovasversoes,localinstaladorversoes, integra_geosec_cctrlcodestr, indexconsultasimediatas, integra_kitfrotas_com_apolo, gera_camp_baseapolo, ';
               sql:=sql+' integra_ocorrenciasptomix, integra_base_apolomix, caminhosalvarfotos, alturafoto, largurafoto, integra_entidades_apolo, integrabasemix, verba_telefone, caminhoarquivoconvenio, entcategparceira, entcod, caminhoexclusao_faxineiro ) ';
               sql:=sql+' VALUES (:lblcaminhobackup, :lblinstalacaolocal, :localnovasversoes, :kit_frotas,:campbaseapolo, :integraocorrmix, :integrabaseapolo, :lblpathfoto, :lblaltura, :lbllargura, :cboentidades, :integrabasemix, :lblvercodigo. :lblcaminhoarquivoconvenio,';
               sql:=sql+'         :lblentidadeparceira, :lblentidade, :lblcaminhoexclusao)';
               fdquerysql3.Close;
               fdquerysql3.SQL.Clear;
               fdquerysql3.sql.Text := sql;
               fdquerysql3.ParamByName('lblcaminhobackup').asstring := lblcaminhobackup.text;
               fdquerysql3.ParamByName('lblinstalacaolocal').AsString := lblinstalacaolocal.Text;
               fdquerysql3.ParamByName('localnovasversoes').AsString := lbllocalnovasversoes.text ;




               +chr(39)++chr(39)+', '+chr(39)++chr(39)+', '+chr(39)+lbldirnovasversoes.Text+chr(39)+', '+chr(39)+lblaplinstalador.Text+chr(39)+', '+chr(39)+integra_com_apolo+chr(39)+', ';
               sql:=sql+inttostr(apolo_geoapolo)+', '+chr(39)+kit_frotas+chr(39)+', '+chr(39)+campbaseapolo+chr(39)+', '+chr(39)+integraocorrmix+chr(39)+', '+chr(39)+integrabaseapolo+chr(39)+', '+chr(39)+lblpathfoto.Text+chr(39)+', '+chr(39)+lblaltura.Text+chr(39)+', '+chr(39)+lbllargura.Text+chr(39)+', '+chr(39)+cboentidades.text+chr(39);
               sql:=sql+', '+chr(39)+integrabasemix+chr(39)+', '+chr(39)+lblvercodigo.Text+chr(39)+', '+chr(39)+lblcaminhoarquivoconvenio.Text+chr(39)+', '+chr(39)+lblentidadeparceira.Text+chr(39)+', '+chr(39)+lblentidade.Text+chr(39)+', '+chr(39)+lblcaminhoexclusao.text+chr(39)+');';
               executaracao(sql,zquerysql3);
               if zquerysql3.RowsAffected > 0 then
                  begin
                     messagedlg('CONFIGURAÇÕES GRAVADAS COM SUCESSO !!!',mtinformation,[mbok],0);
                     lblcaminhobackup.SetFocus;
                     controle:='INCLUSÃO';
                  end
               else
                  begin
                     messagedlg('PROBLEMAS AO TENTAR GRAVAR AS INFORMAÇÕES !!!',mterror,[mbok],0);
                     lblcaminhobackup.SetFocus;
                  end; }
            end
         else if controle = 'ALTERAÇÃO' then
            begin
            {   sql:='UPDATE geoapolo_configuracoes set caminhobackupsistema = '+chr(39)+lblcaminhobackup.Text+chr(39)+', instalacaolocal = '+chr(39)+lblinstalacaolocal.Text+chr(39);
               sql:=sql+', localnovasversoes = '+chr(39)+lbldirnovasversoes.Text+chr(39)+', localinstaladorversoes = '+chr(39)+lblaplinstalador.Text+chr(39)+', integra_geosec_cctrlcodestr = '+chr(39)+integra_com_apolo+chr(39);
               sql:=sql+', indexconsultasimediatas = '+inttostr(apolo_geoapolo)+', integra_kitfrotas_com_apolo = '+chr(39)+kit_frotas+chr(39)+', gera_camp_baseapolo = '+chr(39)+campbaseapolo+chr(39)+', integra_ocorrenciasptomix = '+chr(39)+integraocorrmix+chr(39)+', integra_base_apolomix = '+chr(39)+integrabaseapolo+chr(39);
               sql:=sql+', caminhosalvarfotos = '+chr(39)+lblpathfoto.Text+chr(39)+', alturafoto = '+chr(39)+lblaltura.Text+chr(39)+', largurafoto = '+chr(39)+lbllargura.Text+chr(39)+', integra_entidades_apolo = '+chr(39)+cboentidades.text+chr(39)+', integrabasemix= '+chr(39)+integrabasemix+chr(39)+', verba_telefone='+chr(39)+lblvercodigo.text+chr(39)+', caminhoarquivoconvenio = '+chr(39)+lblcaminhoarquivoconvenio.text+chr(39);
               sql:=sql+', entcategparceira = '+chr(39)+lblentidadeparceira.Text+chr(39)+', entcod = '+chr(39)+lblentidade.Text+chr(39)+', caminhoexclusao_faxineiro = '+chr(39)+lblcaminhoexclusao.text+chr(39)+';';
               executaracao(sql,zquerysql3);
               if zquerysql3.RowsAffected > 0 then
                  begin
                     messagedlg('CONFIGURAÇÕES ALTERADAS COM SUCESSO !!!',mtinformation,[mbok],0);
                     lblcaminhobackup.SetFocus;
                     frmconfsys.Refresh; controle:='INCLUSÃO';
                  end
               else
                  begin
                     messagedlg('PROBLEMAS AO TENTAR GRAVAR A ALTERAÇÃO DAS INFORMAÇÕES !!!',mterror,[mbok],0);
                     lblcaminhobackup.SetFocus;
                  end; }
            end;
         spblimpar.Click;
      end;
   end;
end;

procedure Tfrmconfsys.spblimparClick(Sender: TObject);
begin
   lblcaminhobackup.Clear; lblinstalacaolocal.Clear; lbldirnovasversoes.Clear; lblaplinstalador.clear;
   chkintegrapolo.Checked := false; chkapolo.Checked := false; chkgeoapolo.Checked := false;
   chkfrotas.Checked := false; chkgeracamp.Checked := false; chkintegra_apolo.Checked := false;
   lblpathfoto.Clear; lbllargura.Clear; lblaltura.Clear; cboentidades.ItemIndex := -1;; lblvercodigo.Clear;
   lblentidadeparceira.Clear; lblcaminhoexclusao.Text;
end;

procedure Tfrmconfsys.FormActivate(Sender: TObject);
var
   registro:tregistry;
begin
   with modulo_dados do
   begin
      CONTROLE:='INCLUSÃO';
      sql:='SELECT * FROM geoapolo_configuracoes ';
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
          begin
             with frmprincipal do
             begin
                frmprincipal.caminhosbackup  := buscatroca(fdquerysql.fieldbyname('caminhobackupsistema').asstring,'$','\');
                frmprincipal.dirnovasversoes := buscatroca(fdquerysql.fieldbyname('localnovasversoes').AsString,'$','\');
                frmprincipal.dirinstalacaolocal := buscatroca(fdquerysql.fieldbyname('instalacaolocal').asstring,'$','\');
                frmprincipal.diraplinstalador:= buscatroca(fdquerysql.fieldbyname('localinstaladorversoes').asstring,'$','\');
                frmprincipal.pathfoto:=buscatroca(fdquerysql.fieldbyname('caminhosalvarfotos').asstring,'$','\');
                frmprincipal.alturafoto:=buscatroca(fdquerysql.fieldbyname('alturafoto').asstring,'$','\');
                frmprincipal.largurafoto:=buscatroca(fdquerysql.fieldbyname('largurafoto').asstring,'$','\');
                frmconfsys.lblcaminhoarquivoconvenio.Text :=buscatroca(fdquerysql.fieldbyname('caminhoarquivoconvenio').asstring,'$','\');
                frmconfsys.lblvercodigo.Text := fdquerysql.fieldbyname('verba_telefone').AsString;
                frmconfsys.lblentidadeparceira.Text := fdquerysql.fieldbyname('entcategparceira').asstring;
                sql:='SELECT geocategnome FROM geoapolo_categoria WHERE geocategcodestr = :entidadeparceira';
                if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
                   frmconfsys.lblcategnomeparceiros.Caption:=fdquerysql6.fieldbyname('geocategnome').asstring;
                //
                frmconfsys.lblcategnomeparceiros.Refresh;
                frmconfsys.lblcaminhoexclusao.Text := fdquerysql.fieldbyname('caminhoexclusao_faxineiro').AsString;
                frmconfsys.lblcaminhoexclusao.Text :=buscatroca(fdquerysql.fieldbyname('caminhoexclusao_faxineiro').asstring,'$','\');
                //
                frmprincipal.caminhosbackup  := buscatroca(frmprincipal.caminhosbackup,'#','-');
                frmprincipal.dirnovasversoes := buscatroca(frmprincipal.dirnovasversoes,'#','-');
                frmprincipal.dirinstalacaolocal := buscatroca(frmprincipal.dirinstalacaolocal,'#','-');
                frmprincipal.diraplinstalador:= buscatroca(frmprincipal.diraplinstalador,'#','-');
                frmprincipal.caminhoexclusao :=buscatroca(frmprincipal.caminhoexclusao,'#','-');
                frmprincipal.pathfoto:=buscatroca(pathfoto,'#','-');
                frmprincipal.alturafoto:=buscatroca(alturafoto,'#','-');
                frmprincipal.largurafoto:=buscatroca(largurafoto,'#','-');
                frmconfsys.lblcaminhoarquivoconvenio.Text :=buscatroca(lblcaminhoarquivoconvenio.text,'#','-');
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
                if fdquerysql.FieldByName('integra_kitfrotas_com_apolo').asstring = 'S' then
                   chkfrotas.Checked := true
                else
                   chkfrotas.Checked :=false;
                //
                if fdquerysql.FieldByName('gera_camp_baseapolo').AsString = 'S' then
                   chkgeracamp.Checked := true
                else
                   chkgeracamp.Checked := false;
                //
                if fdquerysql.FieldByName('integra_ocorrenciasptomix').AsString = 'S' then
                   chkintegraocorrmix.Checked := true
                else
                   chkintegraocorrmix.Checked := false;
                //
                if fdquerysql.FieldByName('integrabasemix').AsString = 'S' then
                   chkintegramix.Checked := true
                else
                   chkintegramix.Checked := false;
                //
                if fdquerysql.fieldbyname('integra_entidades_apolo').asstring <> '' then
                   buscanacombo(fdquerysql.fieldbyname('integra_entidades_apolo').AsString,frmconfsys,cboentidades);
                cboentidades.Refresh;
                lblentidade.Text := fdquerysql.fieldbyname('entcod').asstring;
                //
                lbldirnovasversoes.Text := frmprincipal.dirnovasversoes ;
                lblcaminhobackup.Text := frmprincipal.caminhosbackup ;
                lblaplinstalador.Text := frmprincipal.diraplinstalador ;
                lblinstalacaolocal.Text := frmprincipal.dirinstalacaolocal ;
                lblpathfoto.Text := frmprincipal.pathfoto ;
                lblaltura.Text := frmprincipal.alturafoto ;
                lbllargura.Text := frmprincipal.largurafoto;
                if ((dirnovasversoes <> '') or (dirinstalacaolocal<> '') or (diraplinstalador<> '')) then
                   controle:='ALTERAÇÃO'
                else
                   controle:='INCLUSÃO';
                frmconfsys.Refresh;
             end;
          end;
   end;
   statusbar1.Panels[1].Text := configura_statusbar('a');
   statusbar1.Panels[3].Text :=modulo_dados.fdbanco.ConnectionDefName;
end;

procedure Tfrmconfsys.lblmodelosinternaKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if key = vk_return then
      lblinstalacaolocal.SetFocus;
end;

procedure Tfrmconfsys.lblinstalacaolocalKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      lbldirnovasversoes.SetFocus;
end;

procedure Tfrmconfsys.lbldirnovasversoesKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      lblaplinstalador.SetFocus;
end;

procedure Tfrmconfsys.lblaplinstaladorKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      lblpathfoto.setfocus;;
end;

procedure Tfrmconfsys.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f10 then
      spbretornar.Click;
end;

procedure Tfrmconfsys.lblcaminhobackupKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      lblinstalacaolocal.SetFocus;
end;

procedure Tfrmconfsys.chkintegrapoloClick(Sender: TObject);
begin
   if chkintegrapolo.Checked then
      begin
         integra_com_apolo:= 'S';
      end
   else if chkintegrapolo.Checked = false then
      begin
         integra_com_apolo:= 'N';
      end;
end;

procedure Tfrmconfsys.chkapoloClick(Sender: TObject);
begin
   if chkgeoapolo.Checked then
      chkgeoapolo.Checked :=false;
   apolo_geoapolo:=0;
end;

procedure Tfrmconfsys.chkgeoapoloClick(Sender: TObject);
begin
   if chkapolo.Checked then
      chkapolo.Checked :=false;
   apolo_geoapolo:=1;
end;

procedure Tfrmconfsys.chkfrotasClick(Sender: TObject);
begin
   if chkfrotas.Checked then
      kit_frotas := 'S'
   else
      kit_frotas:= 'N';
end;

procedure Tfrmconfsys.chkgeracampClick(Sender: TObject);
begin
   if chkgeracamp.Checked then
      campbaseapolo := 'S'
   else
      campbaseapolo:= 'N';
end;

procedure Tfrmconfsys.chkintegraocorrmixClick(Sender: TObject);
begin
   if chkgeracamp.Checked then
      integraocorrmix := 'S'
   else
      integraocorrmix:= 'N';
end;

procedure Tfrmconfsys.chkintegra_apoloClick(Sender: TObject);
begin
   if chkintegra_apolo.Checked = true then
      integrabaseapolo:='S'
   else if chkintegra_apolo.Checked = false then
      integrabaseapolo:='N';
end;

procedure Tfrmconfsys.lblpathfotoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      lbllargura.SetFocus;
end;

procedure Tfrmconfsys.lblvercodigoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f4 then
      spbuscaverba.click;
end;

procedure Tfrmconfsys.lbllarguraKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      lblaltura.SetFocus;
end;

procedure Tfrmconfsys.lblAlturaKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if ((key = vk_return) or (key = vk_tab)) then
      spbsalvar.Click;
end;

procedure Tfrmconfsys.chkintegraentidadeapoloClick(Sender: TObject);
begin
   if chkgeracamp.Checked then
      entidade_apolo := 'S'
   else
      entidade_apolo:= 'N';
end;

procedure Tfrmconfsys.chkintegramixClick(Sender: TObject);
begin
   if chkintegra_apolo.Checked = true then
      integrabasemix:='S'
   else if chkintegra_apolo.Checked = false then
      integrabasemix:='N';
end;

procedure Tfrmconfsys.spbuscaverbaClick(Sender: TObject);
begin
    if integrabasemix = 'S' then
       begin
      {    with modulo_dados do
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
          end; }
       end
    else if integrabasemix = 'N' then
       begin
          messagedlg('O SISTEMA NÃO ESTÁ CONFIGURADO PARA INTEGRAR COM A BASE MIX RH !!!',mterror,[mbok],0);
          chkintegramix.SetFocus;
          exit;
       end;
end;

procedure Tfrmconfsys.spbopendirClick(Sender: TObject);
begin
   opendialog1.Execute;
   lblcaminhoarquivoconvenio.Text := opendialog1.FileName;
end;

procedure Tfrmconfsys.spbuscategoriaClick(Sender: TObject);
begin
    with modulo_dados do
    begin
 {      sql:='select * from geoapolo_categoria';
       executaracao(sql,zquerysql1);
       if zquerysql1.RecordCount > 0 then
          begin
             application.CreateForm(tfrmconsulta, frmconsulta);
             with frmconsulta do
             begin
                dtszquerysql1.DataSet := zquerysql1;
                gridconsulta.DataSource := dtszquerysql1;
                frmconsulta.controle := 'CATEGORIA_ENTIDADE_CONFIG';
                frmconsulta.ShowModal;
             end;
          end;  }
    end;
    //fdquerysql1.close;
end;

procedure Tfrmconfsys.lblentidadeparceiraEnter(Sender: TObject);
begin
   with modulo_dados do
   begin
   {   if lblnomeverba.Caption = 'Descrição Verba de Telefone' then
         begin
             sql:='select ver_codigo, ver_nome from fo_verbas WHERE ver_codigo = '+chr(39)+lblvercodigo.text+chr(39);
             sqlrun(sql,querysql1,banco_mix);
             if querysql1.RecordCount > 0 then
                begin
                   lblnomeverba.Caption := querysql1.fieldbyname('ver_nome').asstring;
                   lblnomeverba.Refresh;
                end;
         end;}
   end;
end;

procedure Tfrmconfsys.lblentidadeparceiraKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f4 then
      spbuscategoria.click;
end;

procedure Tfrmconfsys.lblcaminhoarquivoconvenioEnter(Sender: TObject);
begin
 {  with modulo_dados do
   begin
    if lblnomeverba.Caption = 'Categoria Entidades Parceiras' then
         begin
           sql:='SELECT geocategnome FROM geoapolo_categorias WHERE geocategcodestr = '+chr(39)+lblcategnomeparceiros.caption+chr(39);
             executaracao(sql,zquerysql1);
             if zquerysql1.RecordCount > 0 then
                begin
                   lblcategnomeparceiros.Caption := zquerysql1.fieldbyname('geocategnome').asstring;
                   lblcategnomeparceiros.Refresh;
                end;
         end;
   end; }
end;

procedure Tfrmconfsys.spbentidadeClick(Sender: TObject);
begin
{   with modulo_dados do
   begin
      sql:='SELECT e.entcod, e.entnome';
      sql:=sql+' FROM ENTIDADE E WITH(NOLOCK), ent_categ ec with(nolock)';
      sql:=sql+' where e.entcod = ec.entcod';
      sql:=sql+' and   substring(ec.categcodestr,1,3) = :zerozerosete'+chr(39)+'007'+chr(39);
      executaracao(sql,queryentidade);
      if queryentidade.RecordCount > 0 then
         begin
            application.CreateForm(tfrmconsulta3, frmconsulta3);
            frmconsulta3.controle := 'SETORES_OPTV';
            with frmconsulta3 do
            begin
               dtsqueryentidade.DataSet := queryentidade;
               carrega_campo_dinamico(queryentidade);
               frmconsulta3.gridconsulta.DataSource := dtsqueryentidade;
               frmconsulta3.gridconsulta.Refresh;
               frmconsulta3.gridconsulta.Refresh;
               frmconsulta3.ShowModal;
            end;
         end;
   end; }
end;

procedure Tfrmconfsys.lblentidadeKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   with modulo_dados do
   begin
      if (key = vk_return) then
         begin
            if (lblentidade.Text <> '') and (lblnome_entidade.Caption = '...') then
               begin
                {  sql:='SELECT e.entcod, e.entnome';
                  sql:=sql+' from entidade e with(nolock), ent_categ ec with(nolock)';
                  sql:=sql+' WHERE e.entcod = ec.entcod ';
                  sql:=sql+' and   substring(ec.categcodestr,1,3) = '+chr(39)+'007'+chr(39);
                  sql:=sql+' and   e.entcod = '+chr(39)+lblentidade.Text+chr(39);
                  executaracao(sql,querysql1);
                  if querysql1.RecordCount > 0 then
                     begin
                        lblentidade.Text := querysql1.fieldbyname('entcod').asstring;
                        lblnome_entidade.Caption := querysql1.fieldbyname('entnome').asstring;
                     end;}
               end;
         end;
   end;
end;

procedure Tfrmconfsys.spbuscaclasseClick(Sender: TObject);
begin
   with modulo_dados do
   begin
 {     sql:='select crd.classerecdespcodestr, crd.classerecdespcodestr from classe_rec_desp crd with(nolock)';
      executaracao(sql,queryentidade);
      if queryentidade.RecordCount > 0 then
         begin
            frmconsulta3.controle := 'BUSCACLASSECAMP';
            with frmconsulta3 do
            begin
               dtsqueryentidade.DataSet := queryentidade;
               carrega_campo_dinamico(queryentidade);
               frmconsulta3.gridconsulta.DataSource := dtsqueryentidade;
               frmconsulta3.gridconsulta.Refresh;
               frmconsulta3.gridconsulta.Refresh;
               frmconsulta3.ShowModal;
            end;
         end; }
   end;
end;

procedure Tfrmconfsys.spbgeofaxineiroClick(Sender: TObject);
begin
   opendialog1.Execute;
   lblcaminhoexclusao.Text := opendialog1.FileName;
end;

end.

