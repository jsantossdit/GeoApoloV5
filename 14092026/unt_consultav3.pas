unit unt_consultav3;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, ComCtrls, StdCtrls, ExtCtrls, Grids, DBGrids, Menus, Data.DB,
  Vcl.Mask;


type
  TfrmConsulta3 = class(TForm)
    GroupBox7: TGroupBox;
    lblcampo: TLabel;
    lblordem: TLabel;
    lblperiodo: TLabel;
    lbla: TLabel;
    lblprocurarpor: TLabeledEdit;
    cbocampo: TComboBox;
    cbordem: TComboBox;
    rdgcrescente: TRadioButton;
    rdgdecrescente: TRadioButton;
    datainicial: TDateTimePicker;
    datafinal: TDateTimePicker;
    GroupBox1: TGroupBox;
    gridconsulta: TDBGrid;
    StatusBar1: TStatusBar;
    lblmensagem: TLabel;
    PopupMenu1: TPopupMenu;
    gravaropcoes: TMenuItem;
    procedure lblprocurarporKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure FormActivate(Sender: TObject);
    procedure gridconsultaKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure rdgcrescenteClick(Sender: TObject);
    procedure rdgdecrescenteClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure cbocampoChange(Sender: TObject);
    procedure gridconsultaDblClick(Sender: TObject);
    procedure cbocampoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure cbordemKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure gravaropcoesClick(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
    wordem_campo,controle,sqlrec1:string;
    ValorSelecionado: string;   // valor que será devolvido ao chamador
    CampoOrigem: string;        // opcional: identifica qual campo do form chamador deve receber
  end;

var
  frmConsulta3: TfrmConsulta3;
  sql, ordem:string;
  formulario:tform;

//function cria_view(sqlrec : string): string; export;
//function cria_viewmix(sqlrec : string): string; export;
//function busca_detalhada : string; export;

implementation

uses funcoes, unt_dados,  unt_corrigecidadedistrito,
  unt_logon, unt_debxcredctafin,  unt_users,
  unt_cadentidades, unt_configsysv2,  unt_cadconsulta,
  unt_estacoes, unt_cadcores, unt_relacionadioceseentidade, unt_cadeventos,
  unt_ocorrencia,
  unt_entidades, unt_matchcode,
   //unt_manativoimobilizado, unt_cadmarcas,
  //unt_gafincadcartao, unt_campanhas,
  unt_principal;
 { unt_gafinctasapagar,
  unt_debxcred, unt_corrigecuponsnomeados, unt_campemailmarketing;}

{$R *.dfm}

procedure TfrmConsulta3.lblprocurarporKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
var
   i:integer;
begin
   if key = VK_RETURN then
      begin
         if cbocampo.text = '' then
            begin
               messagedlg('INFORMA O CAMPO PARA PESQUISA !!!',mterror,[mbok],0);
               cbocampo.setfocus;
               exit;
            end;
         if lblprocurarpor.Text = '' then
            begin
               messagedlg('INFORME O QUE PESQUISAR !!!',mterror,[mbok],0);
               lblprocurarpor.setfocus;
               exit;
            end;
         if controle = 'CLIENTES' then
            begin
               with modulo_dados do
               begin
                  SQL:='SELECT e.entcod,e.entnome,ec.categcodestr,cat.categnome';
                  sql:=sql+' FROM entidade e with(nolock)';
                  sql:=sql+' INNER JOIN ent_categ ec with(nolock) ON e.entcod = ec.entcod';
                  sql:=sql+' INNER JOIN categoria cat with(nolock) ON ec.categcodestr = cat.categcodestr';
                  sql:=sql+' WHERE substring(ec.categcodestr,1,3) = '+quotedstr('01.');
                  sql:=sql+' AND   '+cbocampo.Text+' like % :lblprocurarpor%';
                  sql:=sql+' ORDER BY '+cbordem.Text+' ASC';
                  fdquerysql8.Close;
                  fdquerysql8.SQL.Clear;
                  fdquerysql8.SQL.Text := sql;
                  fdquerysql8.parambyname('lblprocurarpor').asstring := lblprocurarpor.Text;
                  if executaracao(fdquerysql8, fdbanco, true, dtsfdquerysql8) then
                     begin
                        gridconsulta.DataSource:= dtsfdquerysql8;
                        gridconsulta.refresh; gridconsulta.setfocus;
                     end;
               end;
            end
         else if controle = 'CIDADE_CIDADE' then
            begin
               with modulo_dados do
               begin
                  sql:='SELECT cid.CidCod, cid.CidNomeComp, cid.ufsigla FROM CIDADE cid with(nolock) ';
                  sql:=sql+' WHERE '+cbocampo.Text+' like :lblprocurarpor';
                  sql:=sql+' ORDER BY '+quotedstr(cbordem.Text);
                  fdquerysql8.Close;
                  fdquerysql8.SQL.Clear;
                  fdquerysql8.SQL.Text := sql;
                  fdquerysql8.parambyname('lblprocurarpor').asstring := lblprocurarpor.Text;
                  if executaracao(fdquerysql8, fdbanco, true, dtsfdquerysql8) then
                     begin
                        gridconsulta.DataSource:= dtsfdquerysql8;
                        gridconsulta.refresh; gridconsulta.setfocus;
                     end;
               end;
            end
         else if controle = 'CIDADES_ENTREGA' then
            begin
               with modulo_dados,frmcadentidade do
               begin
                 SQL:='SELECT * FROM USER_geoapolo_cidades';
                 sql:=sql+' WHERE '+cbocampo.text+' LIKE :lblprocurarpor';
                 sql:=sql+' ORDER BY ufsigla ASC';
                 fdquerysql9.Close;
                 fdquerysql9.SQL.Clear;
                 fdquerysql9.SQL.Text := sql;
                 if executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
                    begin
                       gridconsulta.DataSource:=dtsfdquerysql9;
                       gridconsulta.Refresh; lblprocurarpor.SetFocus;
                    end;
               end;
            end
         else if controle = 'CIDADES_COBRANCA' then
            begin
               with modulo_dados,frmcadentidade do
               begin
                 SQL:='SELECT * FROM USER_geoapolo_cidades';
                 sql:=sql+' WHERE '+cbocampo.text+' LIKE :lblprocurarpor';
                 sql:=sql+' ORDER BY ufsigla ASC';
                 fdquerysql9.Close;
                 fdquerysql9.SQL.Clear;
                 fdquerysql9.SQL.Text := sql;
                 if executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
                    begin
                       gridconsulta.DataSource:=dtsfdquerysql9;
                       gridconsulta.Refresh; lblprocurarpor.SetFocus;
                    end;
               end;
            end
         else if controle = 'NOTA_FISCAL_PVAGRUP' then
            begin
{               with modulo_dados, frmapuracmfatpedidoagrupado do
               begin
                  sql:='SELECT nf.entcod,nf.nfentnome,nf.nfnum,nf.nfdataemis';
                  sql:=sql+' FROM nota_fiscal nf with(nolock)';
                  sql:=sql+' WHERE nf.empcod = '+quotedstr(lblempcod.Text);
                  sql:=sql+' AND   nf.entcod = '+quotedstr(lblentcod.Text);
                  sql:=sql+' AND   NF.nfdataemis between '+quotedstr(datainicial)+' and '+quotedstr(datafinal);
                  sql:=sql+' AND  '+cbocampo.Text+' like '+quotedstr(lblprocurarpor.Text);
                  sql:=sql+' ORDER BY '+quotedstr(cbordem.Text);
                  executaracao(sql,querysql9);
                  if querysql9.RecordCount > 0 then
                     begin
                        dtsquerysql9.DataSet:=querysql9;
                        gridconsulta.DataSource:=dtsquerysql9;
                        gridconsulta.Refresh; gridconsulta.SetFocus;
                     end;}
               end;
            end
         else if controle = 'OS_SEM_CMUTILIZADO' then
            begin
{               with modulo_dados do
               begin
                  sql:='SELECT DISTINCT mios.ordservnum,e.entnome';
                  sql:=sql+' FROM MEDIDA_ITEM_ORD_SERV mios with(nolock)';
                  sql:=sql+' INNER JOIN ord_serv os with(nolock) ON mios.ordservnum = os.ordservnum and mios.empcod = os.EmpCod';
                  sql:=sql+' INNER JOIN doc_ord_serv dos with(nolock) ON os.ordservnum = dos.ordservnum';
                  sql:=sql+' INNER JOIN entidade e with(nolock) ON os.entcod = e.entcod';
                  sql:=sql+' INNER JOIN ped_venda_nota_fiscal pvnf ON dos.docordservnum  = pvnf.pedvendanum';
                  sql:=sql+' WHERE      mios.ordservnum not in (SELECT ordservnum';
                  sql:=sql+'                                    FROM USER_Cm_Utilizado)';
                  sql:=sql+'  				                          AND        os.ordservdata BETWEEN  '+quotedstr(frmapuracmfatpedidoagrupado.datainicial)+' and '+quotedstr(frmapuracmfatpedidoagrupado.datafinal);
                  sql:=sql+'				                            AND        mios.medidaitordservtipo in('+quotedstr('Utilização')+', '+quotedstr('Retalho')+','+quotedstr('Final')+') ';
                  sql:=sql+' AND '+cbocampo.text+' like '+quotedstr(lblprocurarpor.text);
                  sql:=sql+' ORDER BY '+quotedstr(cbordem.text);
                  executaracao(sql,querysql13);
                  if querysql13.recordcount > 0 then
                     begin
                        dtsquerysql13.dataset:=querysql13;
                        gridconsulta.datasource:=dtsquerysql13;
                        gridconsulta.refresh; gridconsulta.setfocus;
                     end;
               end;}
            end
         else if controle = 'SITCODESTRORIG' then
            begin
               with modulo_dados do
               begin
                  sql:='SELECT sit.sitcodestr,sit.SitNome';
                  sql:=sql+' FROM situacao sit with(nolock)';
                  sql:=sql+' WHERE '+cbocampo.Text+' LIKE :lblprocurarpor';
                  sql:=sql+' ORDER BY sit.'+cbordem.Text+' ASC';
                  fdquerysql4.Close;
                  fdquerysql4.SQL.Clear;
                  fdquerysql4.SQL.Text := sql;
                  fdquerysql4.ParamByName('lblprocurarpor').asstring:= lblprocurarpor.Text;
                  if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
                     begin
                        gridconsulta.DataSource := dtsfdquerysql4;
                        gridconsulta.Refresh; gridconsulta.SetFocus;
                     end;
               end;
            end
         else if controle = 'SITCODESTRDESTINO' then
            begin
               with modulo_dados do
               begin
                  sql:='SELECT sit.sitcodestr,sit.SitNome';
                  sql:=sql+' FROM situacao sit with(nolock)';
                  sql:=sql+' WHERE '+cbocampo.Text+' LIKE :lblprocurarpor';
                  sql:=sql+' ORDER BY sit.'+cbordem.Text+' ASC';
                  fdquerysql4.Close;
                  fdquerysql4.SQL.Clear;
                  fdquerysql4.SQL.Text :=sql;
                  fdquerysql4.ParamByName('lblprocurarpor').AsString:= lblprocurarpor.Text;
                  if executaracao(fdquerysql4,fdbanco, true,dtsfdquerysql4) then
                     begin
                        gridconsulta.DataSource := dtsfdquerysql4;
                        gridconsulta.Refresh; gridconsulta.SetFocus;
                     end;
               end;
            end
         else if controle = 'CATEGORIA_SITUACAO_TITULOS' then
            begin
               with modulo_dados do
               begin
                  sql:='SELECT cat.categcodestr,cat.categnome';
                  sql:=sql+' FROM categoria cat with(nolock)';
                  sql:=sql+' WHERE '+cbocampo.Text+' LIKE :lblprocurarpor';
                  sql:=sql+' ORDER BY cat.CategCodEstr ASC';
                  fdquerysql4.Close;
                  fdquerysql4.sql.clear;
                  fdquerysql4.SQL.Text := text;
                  fdquerysql4.ParamByName('lblprocurarpor').AsString := lblprocurarpor.Text;
                  if executaracao(fdquerysql4,fdbanco, true, dtsfdquerysql4) then
                     begin
                       gridconsulta.DataSource:=dtsfdquerysql4;
                       gridconsulta.Refresh; gridconsulta.SetFocus;
                     end;
               end;
            end
         else if controle = 'CONTA_FINANCEIRASALDO' then
            begin
               with modulo_dados do
               begin
                  sql:='SELECT DISTINCT cf.contafincod,cf.contafinnome';
                  sql:=sql+' FROM conta_fin cf with(nolock)';
                  sql:=sql+' INNER JOIN usuario_conta_fin ucf with(nolock) ON cf.ContaFinCod = ucf.ContaFinCod';
                  sql:=sql+' INNER JOIN GRP_X_USUARIO gu with(nolock) ON ucf.UsuCod = gu.UsuCod';
                  sql:=sql+' WHERE '+cbocampo.Text+' LIKE :lblprocurarpor';
                  fdquerysql11.Close;
                  fdquerysql11.SQL.Clear;
                  fdquerysql11.SQL.Text := sql;
                  fdquerysql11.ParamByName('lblprocurarpor').AsString := lblprocurarpor.Text;
                  if executaracao(fdquerysql11,fdbanco, true, dtsfdquerysql11) then
                     begin
                       gridconsulta.DataSource:=dtsfdquerysql11;
                       gridconsulta.Refresh; gridconsulta.SetFocus;
                     end;
               end;
            end
         else if controle = 'BUSCAENTIDADEAPOLO' then
            begin
                 with modulo_dados do
                 begin
                     sql:='SELECT * FROM entidades WHERE '+cbocampo.text+' like :lblprocurarpor';
                     sql:=sql+' ORDER BY '+cbordem.text+' ASC';
                     fdquerysql4.Close;
                     fdquerysql4.SQL.Clear;
                     fdquerysql4.SQL.Text := sql;
                     fdquerysql4.parambyname('lblprocurarpor').asstring := lblprocurarpor.Text;
                     if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
                        begin
                           gridconsulta.DataSource:= dtsfdquerysql4;
                           gridconsulta.refresh;
                        end;
                 end;
            end
         else if controle = 'USUARIO_DEPARTAMENTO' then
            begin
               with modulo_dados do
               begin
                 sql:='SELECT * FROM USER_geoapolo_departamentos ugd';
                 sql:=sql+' WHERE '+cbocampo.Text+' like :lblprocurarpor';
                 sql:=sql+' ORDER BY '+cbordem.Text+' ASC';
                 fdquerysql4.Close;
                 fdquerysql4.SQL.Clear;
                 fdquerysql4.SQL.Text := sql;
                 fdquerysql4.ParamByName('lblprocurarpor').AsString := lblprocurarpor.Text;
                 if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
                    begin
                      gridconsulta.DataSource:=dtsfdquerysql4;
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'USUARIO_ESTACAO' then
            begin
              with modulo_dados do
              begin
                sql:='SELECT ugu.nome_completo, ugd.nome_departamento, ugu.usucod,ugu.login,ugu.codigo_usuario';
           	    sql:=sql+' FROM USER_geoapolo_usuarios ugu with(nolock) ';
                sql:=sql+' INNER JOIN USER_geoapolo_departamentos ugd with(nolock) ON ugu.codigo_departamento = ugd.codigo_departamento';
                sql:=sql+' WHERE ugu.flagativo = '+quotedstr('A');
                sql:=sql+' AND '+cbocampo.Text+' like :lblprocurarpor';
                sql:=sql+' ORDER BY '+cbordem.Text+' ASC';
                fdquerysql6.Close;
                fdquerysql6.SQL.Clear;
                fdquerysql6.SQL.Text := sql;
                fdquerysql6.ParamByName('lblprocurarpor').AsString := lblprocurarpor.Text;
                if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
                    begin
                      gridconsulta.DataSource:=dtsfdquerysql6;
                      gridconsulta.Refresh;
                    end;
              end;
            end
         else if controle = 'OCUPACAO' then
            begin
               with modulo_dados, frmcadentidade do
               begin
                 sql:='SELECT * FROM USER_geoapolo_cargos' ;
                 sql:=sql+' WHERE '+cbocampo.Text+' like :lblprocurarpor';
                 sql:=sql+' ORDER BY '+cbordem.Text+' ASC';
                 fdquerysql.close;
                 fdquerysql.sql.clear;
                 fdquerysql.sql.text := sql;
                 fdquerysql.ParamByName('lblprocurarpor').AsString := lblprocurarpor.text;
                 if executaracao(fdquerysql,fdbanco,true,dtsfdquerysql) then
                    begin
                      gridconsulta.DataSource:=dtsfdquerysql;
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'OCUPACAO_CONTATO' then
            begin
               with modulo_dados, frmcadentidade do
               begin
                 sql:='SELECT * FROM USER_geoapolo_cargos' ;
                 sql:=sql+' WHERE '+cbocampo.Text+' like :lblprocurarpor';
                 sql:=sql+' ORDER BY '+cbordem.Text+' ASC';
                 fdquerysql.close;
                 fdquerysql.sql.clear;
                 fdquerysql.sql.text := sql;
                 fdquerysql.ParamByName('lblprocurarpor').AsString := lblprocurarpor.text;
                 if executaracao(fdquerysql,fdbanco,true,dtsfdquerysql) then
                    begin
                      gridconsulta.DataSource:=dtsfdquerysql;
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'CATEGORIA_ENTIDADE' then
            begin
                with modulo_dados, frmcadentidade do
                begin
                  // Monta a SQL base
                  fdquerysql17.Close;
                  fdquerysql19.SQL.Clear;
                  sql:='SELECT geocategcodestr, geocategnome FROM USER_geoapolo_categoria gc WHERE ' + cbocampo.Text + ' LIKE :filtro';
                  fdquerysql19.sql.text := sql;
                  fdquerysql19.ParamByName('filtro').AsString := '%' + Trim(lblprocurarpor.Text) + '%';
                  if executaracao(fdquerysql19, fdbanco, False, dtsfdquerysql19) then
                    begin
                      fdquerysql19.open;
                      frmconsulta3.gridconsulta.DataSource := dtsfdquerysql19;
                      frmconsulta3.gridconsulta.Refresh;
                    end;
                end;
            end
         else if controle = 'CATEGORIA_ENTIDADE_ALVO' then
            begin
                with modulo_dados, frmcadentidade do
                begin
                  fdquerysql19.Close;
                  fdquerysql19.SQL.Clear;
                  sql:='SELECT cat.categcodestr, cat.categnome FROM categoria cat WITH (NOLOCK)';
                  sql:=sql+' LEFT JOIN USUARIO_CATEG utc WITH (NOLOCK) ON cat.CategCodEstr = utc.CategCodEstr';
                  sql:=sql+' WHERE cat.' + cbocampo.Text + ' LIKE :procurarpor';
                  sql:=sql+' AND utc.usucod = :usucod';
                  fdquerysql19.sql.text := sql;
                  fdquerysql19.ParamByName('procurarpor').AsString := '%' + Trim(lblprocurarpor.Text) + '%';
                  fdquerysql19.ParamByName('usucod').AsString := frmlogon.codigousuario;
                  // Executa via sua função genérica
                  if executaracao(fdquerysql19, fdbanco, true, dtsfdquerysql19) then
                  begin
                      fdquerysql19.open;
                      frmconsulta3.gridconsulta.DataSource := dtsfdquerysql19;
                      frmconsulta3.gridconsulta.Refresh;
                  end;
                end;
            end
         else if controle = 'TIPOLOGRADOURO_ENDENTREGA' then
            begin
               with modulo_dados do
               begin
                 SQL:='SELECT * FROM USER_geoapolo_tipologradouro';
                 sql:=sql+' WHERE '+cbocampo.Text+' like :procurarpor';
                 fdquerysql9.close;
                 fdquerysql9.sql.clear;
                 fdquerysql9.sql.text := sql;
                 fdquerysql9.parambyname('procurarpor').asstring :=lblprocurarpor.text;
                 ValorSelecionado := fdquerysql9.FieldByName('tipologradabrev').AsString;
                 if executaracao(fdquerysql9, fdbanco, true,dtsfdquerysql9) then
                    begin
                       frmconsulta3.gridconsulta.DataSource := dtsfdquerysql9;
                       frmconsulta3.gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'TIPOLOGRADOURO' then
            begin
               with modulo_dados do
               begin
                  SQL:='SELECT * FROM USER_geoapolo_tipologradouro';
                  sql:=sql+' WHERE '+cbocampo.text+' LIKE :lblprocurarpor';
                  fdquerysql9.Close;
                  fdquerysql9.SQL.Clear;
                  fdquerysql9.SQL.Text := sql;
                  fdquerysql9.ParamByName('lblprocurarpor').AsString := lblprocurarpor.text;
                  ValorSelecionado := fdquerysql1.FieldByName('tipologradabrev').AsString;
                  if executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
                     begin
                        dtsfdquerysql9.DataSet:=fdquerysql9;
                        controle := 'TIPOLOGRADOURO';
                        gridconsulta.DataSource:=dtsfdquerysql9;
                     end;
               end;
            end
         else if controle = 'TIPOLOGRADOURO_MESCLA' then
            begin
               with frmconsulta3, modulo_dados do
               begin
                  sql:='SELECT tipologradabrev FROM tipo_lograd WHERE '+cbocampo.Text+' LIKE :lblprocurarpor';
                  fdquerysql9.Close;
                  fdquerysql9.SQL.Clear;
                  fdquerysql9.SQL.Text := sql;
                  fdquerysql9.ParamByName('lblprocurarpor').AsString := lblprocurarpor.text;
                  ValorSelecionado := fdquerysql1.FieldByName('tipologradabrev').AsString;
                  if executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
                     begin
                        controle:= 'TIPOLOGRADOURO_MESCLA';
                        gridconsulta.DataSource:=dtsfdquerysql9;
                     end;
               end;
            end
         else if controle = 'ATIVIDADE_ECONOMICAG' then
            begin
               with modulo_dados,frmcadentidade do
               begin
                  sql:='SELECT * from USER_geoapolo_atividade_economica ';
                  sql:=sql+' WHERE '+cbocampo.text+' LIKE :procurarpor';
                  sql:=sql+' ORDER BY ativeconnome ASC';
                  fdquerysql19.close;
                  fdquerysql19.sql.clear;
                  fdquerysql19.sql.text := sql;
                  fdquerysql19.parambyname('procurarpor').asstring:= lblprocurarpor.text;
                  if executaracao(fdquerysql19,fdbanco, true,dtsfdquerysql19) then
                     begin
                       gridconsulta.DataSource:=dtsfdquerysql19;
                       gridconsulta.Refresh; lblprocurarpor.SetFocus;
                     end;
               end;
            end
         else if controle = 'ATIVIDADE_ECONOMICA_APOLO' then
            begin
               with modulo_dados, frmcadentidade do
               begin
                  sql:='SELECT ae.ativeconcodestr, ae.ativeconnome';
                  sql:=sql+' FROM ativ_economica ae with(nolock)';
                  sql:=sql+' WHERE '+cbocampo.text+' LIKE :procurarpor';
                  sql:=sql+' ORDER BY '+cbordem.Text+' ASC';
                  fdquerysql19.close;
                  fdquerysql19.sql.clear;
                  fdquerysql19.sql.text := sql;
                  fdquerysql19.parambyname('procurarpor').asstring:= lblprocurarpor.Text;
                  if executaracao(fdquerysql19,fdbanco,true, dtsfdquerysql19) then
                     begin
                        gridconsulta.DataSource := dtsfdquerysql19;
                        gridconsulta.Refresh; lblprocurarpor.SetFocus;
                     end;
               end;
            end
         else if controle = 'ORIGEM_ENTIDADE' then
            begin
               with frmconsulta3, modulo_dados do
               begin
                  sql:='SELECT * FROM USER_geoapolo_origens ';
                  sql:=sql+' WHERE '+cbocampo.text+' LIKE :procurarpor';
                  sql:=sql+' ORDER BY '+cbordem.text;
                  if rdgcrescente.Checked then
                     sql:=sql+' ASC';
                  if rdgdecrescente.Checked  then
                     sql:=sql+' DESC';
                  fdquerysql9.close;
                  fdquerysql9.SQL.Clear;
                  fdquerysql9.SQL.Text := sql;
                  fdquerysql9.ParamByName('procurarpor').AsString := lblprocurarpor.Text;
                  if executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
                     begin
                        controle:='ORIGEM_ENTIDADE';
                        gridconsulta.DataSource:=dtsfdquerysql9;
                     end;
               end;
            end
         else if controle = 'ORIGEM_ENTIDADE_APOLO' then
            begin
               with frmconsulta3, modulo_dados do
               begin
                  sql:='SELECT * FROM origens o ';
                  sql:=sql+' WHERE '+cbocampo.Text+' LIKE :procurarpor';
                  sql:=sql+' ORDER BY '+cbordem.Text;
                  if rdgcrescente.Checked  then
                     sql:=sql+' ASC';
                  if rdgdecrescente.Checked then
                     sql:=sql+' DESC';
                  fdquerysql9.Close;
                  fdquerysql9.SQL.Clear;
                  fdquerysql9.SQL.Text := sql;
                  fdquerysql9.ParamByName('procurarpor').AsString := lblprocurarpor.Text ;
                  if executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
                     begin
                        controle:='ORIGEM_ENTIDADE_APOLO';
                        gridconsulta.DataSource := dtsfdquerysql9;
                     end;
               end;
            end
         else if controle = 'TIPOLOGRADOURO_ENDCOBRANCA' then
            begin
               with modulo_dados do
               begin
                 SQL:='SELECT * FROM USER_geoapolo_tipologradouro';
                 sql:=sql+' WHERE '+cbocampo.Text+' like :procurarpor';
                 fdquerysql9.Close;
                 fdquerysql9.SQL.Clear;
                 fdquerysql9.SQL.Text := sql;
                 fdquerysql9.ParamByName('procurarpor').AsString := lblprocurarpor.Text;
                 if executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
                    begin
                       frmconsulta3.gridconsulta.DataSource := dtsfdquerysql9;
                       frmconsulta3.gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'TIPOTRATENTIDADE' then
            begin
              if trim(cbocampo.text)='' then
                 cbocampo.itemindex:=0;
              if trim(lblprocurarpor.text) = '' then
                 lblprocurarpor.text := '%%';

              sql := 'SELECT * FROM USER_geoapolo_tipotratamento WHERE ' + cbocampo.Text + ' LIKE :procurarpor';
              with modulo_dados do
              begin
                if not Assigned(modulo_dados.fdquerysql20) then
                  Exit;
                fdquerysql20.Close;
                fdquerysql20.SQL.Clear;
                fdquerysql20.SQL.Text := sql;
                fdquerysql20.ParamByName('procurarpor').AsString := lblprocurarpor.Text;
                if executaracao(fdquerysql20, fdbanco, True, dtsfdquerysql20) then
                  begin
                    // ✅ Usar DataSource LOCAL do próprio frmconsulta3
                    //    evitando vincular o DataSource global ao grid
                    if Assigned(modulo_dados.dtsfdquerysql20) then
                       modulo_dados.dtsfdquerysql20.DataSet := fdquerysql20;
                    if Assigned(gridconsulta) then
                      begin
                        gridconsulta.DataSource := dtsfdquerysql20;
                        gridconsulta.Refresh;
                      end;
                  end;
              end;
            end
         else if controle = 'TIPOTRATENTIDADE_APOLO' then
            begin
               with frmconsulta3, modulo_dados do
               begin
                  SQL:='SELECT * FROM TIPO_TRATAMENTO';
                  sql:=sql+' WHERE '+cbocampo.Text+' LIKE :procurarpor';
                  fdquerysql20.close;
                  fdquerysql20.sql.clear;
                  fdquerysql20.sql.text := sql;
                  fdquerysql20.parambyname('procurarpor').asstring:=lblprocurarpor.Text;
                  if executaracao(fdquerysql20, fdbanco, true, dtsfdquerysql20) then
                    begin
                      gridconsulta.DataSource:=dtsfdquerysql20;
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if (controle = 'REGIAO_ENTIDADE') then
            begin
               with modulo_dados do
               begin
                  sql:='SELECT * FROM USER_geoapolo_regiao_pais ';
                  sql:=sql+' WHERE '+cbocampo.text+' LIKE :procurarpor';
                  sql:=sql+' ORDER BY '+cbordem.text+' ASC';
                  fdquerysql9.close;
                  fdquerysql9.sql.clear;
                  fdquerysql9.sql.text := sql;
                  fdquerysql9.parambyname('procurarpor').asstring:=lblprocurarpor.text;
                  if executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
                     begin
                       gridconsulta.DataSource:=dtsfdquerysql9;
                       gridconsulta.Refresh; lblprocurarpor.SetFocus;
                     end;
               end;
            end
         else if (controle = 'REGIAO_ENTIDADE_APOLO') then
            begin
               with modulo_dados do
               begin
                  sql:='SELECT reg.regcodestr, reg.regnome, reg.regcodalt';
                  sql:=sql+' FROM regiao reg with(nolock)';
                  sql:=sql+' WHERE '+cbocampo.text+' LIKE :procurarpor';
                  sql:=sql+' ORDER BY '+cbordem.Text+' ASC';
                  fdquerysql9.close;
                  fdquerysql9.sql.clear;
                  fdquerysql9.sql.text := sql;
                  fdquerysql9.parambyname('procurarpor').asstring:=lblprocurarpor.text;
                  if executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
                     begin
                       gridconsulta.DataSource:=dtsfdquerysql9;
                       gridconsulta.Refresh; lblprocurarpor.SetFocus;
                     end;
               end;
            end
         else if ((controle = 'BUSCA_CONTATO_ENTIDADE') or (controle = 'BUSCA_CONTATO_ENTIDADE_APOLO')) then
            begin
               with modulo_dados,frmcadentidade do
               begin
                   if (((frmentidades.integraentidadeapolo = 'Não Integra') or (frmentidades.integraentidadeapolo = 'Mescla')) AND (frmentidades.cbobuscabanco.text = 'GeoApolo')) then
                      begin
                         sql:='SELECT uge.geoentcod, uge.geoentnome, uge.geoentcep, uge.geotipotratcod, ugtl.tipologradouro as geoenttipolograd, uge.geoentender, uge.geoenderno,';
                         sql:=sql+'   uge.geoentendercomp, uge.geoentbair, uge.geocidcod, ugc.cidnomecomp, ugc.ufsigla, uge.geocargocodestr,';
                         sql:=sql+'   ugcar.geocargonome';
                         sql:=sql+' FROM USER_geoapolo_entidade uge with(nolock)';
                         sql:=sql+' LEFT JOIN USER_geoapolo_cidades ugc ON uge.geocidcod = ugc.geocidcod';
                         sql:=sql+' LEFT JOIN USER_geoapolo_cargos ugcar ON uge.geocargocodestr = ugcar.geocargocodestr';
                         sql:=sql+' LEFT JOIN USER_geoapolo_tipologradouro ugtl ON uge.tipolograd = ugtl.tipolograd';
                         sql:=sql+' WHERE uge.geoentcod <> :entcod';
                         sql:=sql+' AND   uge.'+cbocampo.Text+' LIKE :procurarpor';
                         sql:=sql+' ORDER BY '+cbordem.Text+' ASC'
                      end
                   else if (((frmentidades.integraentidadeapolo = 'Integra') or (frmentidades.integraentidadeapolo = 'Mescla')) AND (frmentidades.cbobuscabanco.Text= 'Apolo')) then
                      begin
                         sql:='SELECT e.entcod, e.tipotratcod, e.entnome, e.entlograd, e.entender, e.EntEnderNo, e.EntEnderComp, e.entbair,';
                         sql:=sql+' e.entcep, e.cidcod, cid.cidnomecomp, cid.ufsigla, ec.categcodestr,  e1.RowGuid, e.cargocodestr, cargo.cargonome,ew.entwebemail';
                         sql:=sql+' FROM entidade e with(nolock)';
                         sql:=sql+' INNER JOIN cidade cid with(nolock) ON e.cidcod = cid.CidCod';
                         sql:=sql+' INNER JOIN u_entidade e1 with(nolock) ON e.entcod = e1.entcod';
                         sql:=sql+' INNER JOIN ent_categ ec with(nolock) ON e.entcod = ec.EntCod';
                         sql:=sql+' LEFT JOIN cargo with(nolock) ON e.cargocodestr = cargo.cargocodestr';
                         sql:=sql+' LEFT JOIN ent_web ew ON e.entcod = ew.entcod AND ew.entwebemailprinc = '+quotedstr('Sim');
                         sql:=sql+' WHERE  e.'+cbocampo.Text+' LIKE :procurarpor';
                         sql:=sql+' ORDER BY '+cbordem.Text+' ASC'
                      end;
                   fdquerysql13.close;
                   fdquerysql13.sql.clear;
                   fdquerysql13.sql.text :=sql;
                   fdquerysql13.parambyname('procurarpor').asstring:= '%'+lblprocurarpor.text+'%';
                   if executaracao(fdquerysql13, fdbanco, true, dtsfdquerysql13) then
                      begin
                         gridconsulta.DataSource:=dtsfdquerysql13;
                         gridconsulta.Refresh; lblprocurarpor.SetFocus;
                      end;
               end;
            end
         else if (controle = 'ENTCIDCOD') then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                 SQL:='SELECT * FROM USER_geoapolo_cidades';
                 sql:=sql+' WHERE '+cbocampo.Text+' LIKE :procurarpor';
                 sql:=sql+' ORDER BY '+cbordem.Text+' ASC';
                 fdquerysql9.close;
                 fdquerysql9.sql.clear;
                 fdquerysql9.sql.text := sql;
                 fdquerysql9.parambyname('procurarpor').asstring := quotedstr(lblprocurarpor.Text);
                 if executaracao(fdquerysql9,fdbanco,true,dtsfdquerysql9) then
                   begin
                     gridconsulta.DataSource:=dtsfdquerysql9;
                     gridconsulta.Refresh;
                   end;
               end;
            end
         else if (controle = 'GRUPO_PRODUTO')  then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  SQL:='SELECT * FROM USER_geoapolo_produto_grupo ';
                  sql:=sql+' WHERE '+cbocampo.Text+' LIKE :procurarpor';
                  sql:=sql+' ORDER BY '+cbordem.Text+' ASC';
                  fdquerysql1.Close;
                  fdquerysql1.SQL.Clear;
                  fdquerysql1.SQL.Text := lblprocurarpor.Text;
                  if executaracao(fdquerysql1, fdbanco, true, dtsfdquerysql1) then
                     begin
                       gridconsulta.DataSource:=dtsfdquerysql1;
                       gridconsulta.Refresh;
                     end;
               end;
             end
         else if (controle = 'BUSCAGRUPOPRODUTOVENDA') then
            begin
               with modulo_dados do
               begin
                  sql:='SELECT ProdCodEstr,ProdNome FROM produto';
                  SQL:=SQL+' WHERE prodgrupo = '+quotedstr('T');
                  sql:=sql+' AND   LEN(prodcodestr) =2';
                  sql:=sql+' AND '+frmconsulta3.cbocampo.Text;
                  sql:=sql+' LIKE :procurarpor';
                  sql:=sql+' ORDER BY '+frmconsulta3.cbordem.Text;
                  if rdgcrescente.Checked then
                     sql:=sql+' ASC';
                  if rdgdecrescente.Checked  then
                     sql:=sql+' DESC';
                  fdquerysql.Close;
                  fdquerysql.SQL.Clear;
                  fdquerysql.SQL.Text := sql;
                  fdquerysql.ParamByName('procurarpor').AsString := lblprocurarpor.Text;
                  if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
                     begin
                        controle := 'BUSCAGRUPOPRODUTOVENDA';
                        gridconsulta.DataSource:=dtsfdquerysql;
                        gridconsulta.setfocus;
                     end;
               end;
            end
         else if (controle = 'ENTDIDADEPVSPVP') then
            begin
               with modulo_dados do
               begin
                  sql:='SELECT e.entcod, substring(e.entnome,1,30) as entnome, cid.CidNomeComp, cid.UfSigla,cat.categnome';
                  sql:=sql+' FROM ENTIDADE e with(nolock) INNER JOIN ent_categ ec WITH(NOLOCK) ON e.EntCod = ec.EntCod';
                  sql:=sql+' INNER JOIN CATEGORIA cat with(nolock) ON ec.categcodestr = cat.categcodestr';
                  sql:=sql+' INNER JOIN CIDADE cid with(nolock) ON e.CidCod = cid.CidCod';
                  sql:=sql+' WHERE SUBSTRING(ec.categcodestr,1,2) = '+quotedstr('01');
                  sql:=sql+' AND  '+frmconsulta3.cbocampo.text;
                  sql:=sql+' LIKE :procurarpor';
                  sql:=sql+' ORDER BY '+frmconsulta3.cbordem.text;
                  if rdgcrescente.checked  then
                     sql:=sql+' ASC';
                  if rdgdecrescente.checked  then
                     sql:=sql+' DESC';
                  fdquerysql6.Close;
                  fdquerysql6.SQL.Clear;
                  fdquerysql6.SQL.Text := sql;
                  fdquerysql6.ParamByName('procurarpor').AsString := lblprocurarpor.text;
                  if executaracao(fdquerysql6, fdbanco, true, dtsfdquerysql6) then
                     begin
                        dtsfdquerysql6.dataset:=fdquerysql6;
                        controle:='ENTDIDADEPVSPVP';
                        gridconsulta.datasource:=dtsfdquerysql6;
                        gridconsulta.setfocus;
                     end;
              end;
            end
         else if (controle = 'PRODUTOPVSPVP') then
            begin
               with modulo_dados do
               begin
                  sql:='SELECT p.prodcodestr,p.prodcodred,p.prodnome,p.prodnomealt1';
                  sql:=sql+' FROM produto p with(nolock)';
                  sql:=sql+' WHERE substring(p.prodcodestr,1,2) = '+quotedstr('09');
                  sql:=sql+' AND  '+frmconsulta3.cbocampo.text;
                  sql:=sql+' LIKE :procurarpor';
                  sql:=sql+' ORDER BY p.'+frmconsulta3.cbordem.text;
                  if rdgcrescente.checked  then
                     sql:=sql+' ASC';
                  if rdgdecrescente.checked  then
                     sql:=sql+' DESC';
                  fdquerysql.Close;
                  fdquerysql.SQL.Clear;
                  fdquerysql.SQL.Text := sql;
                  fdquerysql.ParamByName('procurarpor').AsString := lblprocurarpor.text;
                  if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
                     begin
                        controle:='PRODUTOPVSPVP';
                        gridconsulta.datasource:=dtsfdquerysql;
                        gridconsulta.setfocus;
                     end;
              end;
            end
         else if controle = 'NATOPPVSPVP' then
            begin
               with modulo_dados do
               begin
                  sql:='SELECT np.natopcodestr,np.natopnome';
                  sql:=sql+' FROM NAT_OPERACAO np with(nolock)';
                  sql:=sql+' WHERE  '+frmconsulta3.cbocampo.text;
                  sql:=sql+' LIKE :procurarpor';
                  sql:=sql+' ORDER BY np.'+frmconsulta3.cbordem.text;
                  if rdgcrescente.checked  then
                     sql:=sql+' ASC';
                  if rdgdecrescente.checked  then
                     sql:=sql+' DESC';
                  fdquerysql.Close;
                  fdquerysql.SQL.Clear;
                  fdquerysql.SQL.Text := sql;
                  fdquerysql.ParamByName('procurarpor').AsString := lblprocurarpor.text;
                  if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
                     begin
                        controle:='NATOPPVSPVP';
                        gridconsulta.datasource:=dtsfdquerysql;
                        gridconsulta.setfocus;
                     end;
              end;
            end
         else if controle = 'ENTIDADE-REINF' then
            begin
               with modulo_dados do
               begin
                  sql:='SELECT e.entcod, e.entnome, c.categcodestr,c.categnome';
                  sql:=sql+' FROM entidade e WITH(NOLOCK)';
                  sql:=sql+' INNER JOIN ent_categ ec WITH(NOLOCK) ON e.entcod = ec.entcod';
                  sql:=sql+' INNER JOIN categoria c WITH(NOLOCK) ON ec.categcodestr = c.categcodestr';
                  sql:=sql+' WHERE ec.categcodestr like '+quotedstr('01%');
                  sql:=sql+' AND '+cbocampo.Text +' like :procurarpor';
                  sql:=sql+' ORDER BY e.'+cbordem.Text;
                  if rdgcrescente.checked  then
                     sql:=sql+' ASC';
                  if rdgdecrescente.checked  then
                     sql:=sql+' DESC';
                  fdquerysql4.Close;
                  fdquerysql4.SQL.Clear;
                  fdquerysql4.SQL.Text := sql;
                  fdquerysql4.ParamByName('procurarpor').AsString := lblprocurarpor.Text;
                  if executaracao(fdquerysql4, fdbanco, false, dtsfdquerysql4) then
                     begin
                        controle:='ENTIDADE-REINF';
                        gridconsulta.DataSource:=dtsfdquerysql4;
                        gridconsulta.SetFocus;
                     end;
               end;
            end
         else if controle = 'CONTA_FINANCEIRASALDO' then
            begin
               with modulo_dados do
               begin
                  sql:='SELECT DISTINCT cf.contafincod, cf.contafinnome';
                  sql:=sql+' FROM conta_fin cf with(nolock), usuario_conta_fin ucf with(nolock), grp_x_usuario gu with(nolock)';
                  sql:=sql+' WHERE cf.contafincod = ucf.contafincod';
                  sql:=sql+' AND   ucf.usucod = gu.usucod';
                  sql:=sql+' AND ((gu.GrpUsuCod = :grpusucod) )';
                  sql:=sql+' AND '+cbocampo.Text +' like :procurarpor';
                  sql:=sql+' ORDER BY '+cbordem.Text;
                  if rdgcrescente.checked  then
                     sql:=sql+' ASC';
                  if rdgdecrescente.checked  then
                     sql:=sql+' DESC';
                  fdquerysql11.close;
                  fdquerysql11.sql.clear;
                  fdquerysql11.sql.Text:= sql;
                  fdquerysql11.parambyname('grpusucod').asstring:=fdquerysql1.fieldbyname('GrpUsuCod').asstring;
                  fdquerysql11.ParamByName('procurarpor').AsString := lblprocurarpor.Text;
                  if executaracao(fdquerysql11, fdbanco, false, dtsfdquerysql11) then
                     begin
                        with frmconsulta3 do
                        begin
                           controle := 'CONTA_FINANCEIRASALDO';
                           gridconsulta.DataSource := dtsfdquerysql11;
                           gridconsulta.Refresh;
                        end;
                     end;
               end;
            end
         else if controle = 'MARCA_PRODUTO' then
            begin
              with modulo_dados, frmconsulta3 do
              begin
                sql:='SELECT * FROM USER_geoapolo_produto_marcas ';
                sql:=sql+' WHERE '+cbocampo.Text+' LIKE :procurarpor';
                sql:=sql+' ORDER BY '+cbordem.Text+' ASC';
                fdquerysql2.Close;
                fdquerysql2.SQL.Clear;
                fdquerysql2.SQL.Text := sql;
                fdquerysql2.ParamByName('procurarpor').AsString := lblprocurarpor.Text;
                if executaracao(fdquerysql2, fdbanco, true, dtsfdquerysql2) then
                   begin
                     gridconsulta.DataSource:=dtsfdquerysql2;
                     gridconsulta.Refresh
                   end;
              end;
            end
         else if controle = 'MARCA_ESTACOES' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql:='SELECT * FROM USER_geoapolo_produto_marcas ';
                  sql:=sql+' WHERE '+cbocampo.Text+' LIKE :procurarpor';
                  sql:=sql+' ORDER BY '+cbordem.Text+' ASC';
                  fdquerysql.Close;
                  fdquerysql.SQL.Clear;
                  fdquerysql.SQL.Text:=sql;
                  fdquerysql.ParamByName('procurarpor').AsString := lblprocurarpor.Text ;
                  if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
                     begin
                       gridconsulta.DataSource := dtsfdquerysql;
                       gridconsulta.Refresh;
                     end;
               end;
            end
         else if controle = 'COR_PRODUTO' then
            begin
              with modulo_dados, frmconsulta3 do
              begin
                sql:='SELECT * FROM USER_geoapolo_produto_cores';
                sql:=sql+' WHERE '+cbocampo.Text+' LIKE :procurarpor';
                sql:=sql+' ORDER BY '+cbordem.Text+' ASC';
                fdquerysql5.Close;
                fdquerysql5.SQL.Clear;
                fdquerysql5.SQL.Text := sql;
                fdquerysql5.ParamByName('procurarpor').AsString:=lblprocurarpor.Text ;
                if executaracao(fdquerysql5, fdbanco, false, dtsfdquerysql5) then
                   begin
                     gridconsulta.DataSource:=dtsfdquerysql5;
                     gridconsulta.Refresh
                   end;
              end;
            end
         else if controle = 'CONSULTAS_IMEDIATAS' then
            begin
              with modulo_dados, frmconsulta3 do
              begin
                  sql := 'SELECT * FROM USER_geoapolo_consultas ';
                  sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' ORDER BY ' + cbordem.Text + ' ASC';
                  fdquerysql7.Close;
                  fdquerysql7.SQL.Clear;
                  fdquerysql7.SQL.Text := sql;
                  fdquerysql7.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql7, fdbanco, false, dtsfdquerysql7) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql7;
                      gridconsulta.Refresh;
                    end;
              end;
            end
         else if controle = 'DEPARTAMENTO_ESTACAO' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql := 'SELECT ugd.codigo_departamento, ugd.nome_departamento';
                  sql := sql + ' FROM USER_geoapolo_departamentos ugd with(nolock)';
                  sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' ORDER BY ' + cbordem.Text + ' ASC';
                  fdquerysql6.Close;
                  fdquerysql6.SQL.Clear;
                  fdquerysql6.SQL.Text := sql;
                  fdquerysql6.ParamByName('procurarpor').AsString := lblprocurarpor.Text;
                  if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql6;
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'ENTIDADE_ESTACAO' then
            begin
              with modulo_dados, frmconsulta3 do
              begin
                sql := 'SELECT * FROM USER_geoapolo_entidade';
                sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';
                sql := sql + ' ORDER BY ' + cbordem.Text + ' ASC';
                fdquerysql6.Close;
                fdquerysql6.SQL.Clear;
                fdquerysql6.SQL.Text := sql;
                fdquerysql6.ParamByName('procurarpor').AsString := lblprocurarpor.Text;
                if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
                  begin
                    gridconsulta.DataSource := dtsfdquerysql6;
                    gridconsulta.Refresh;
                  end;
              end;
            end
         else if controle = 'LOCALIZACAO_FISICA_ESTACAO' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql := 'SELECT ugslf.*, ugd.nome_departamento as Departamento';
                  sql := sql + ' FROM USER_geoapolo_satfi_localizacao_fisica ugslf';
                  sql := sql + ' INNER JOIN USER_geoapolo_departamentos ugd with(nolock) ON ugslf.codigo_departamento = ugd.codigo_departamento';
                  sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' ORDER BY ' + cbordem.Text + ' ASC';
                  fdquerysql6.Close;
                  fdquerysql6.SQL.Clear;
                  fdquerysql6.SQL.Text := sql;
                  fdquerysql6.ParamByName('procurarpor').AsString := lblprocurarpor.Text;
                  if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql6;
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'LOCALIZACAO_FISICA_REDE' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql := 'SELECT ugslf.codigo_localizacao, ugslf.grupo, ugslf.localizacao, ugslf.codigo_departamento, ugd.nome_departamento';
                  sql := sql + ' FROM USER_geoapolo_satfi_localizacao_fisica ugslf with(nolock)';
                  sql := sql + ' INNER JOIN USER_geoapolo_departamentos ugd with(nolock) ON ugslf.codigo_departamento = ugd.codigo_departamento';
                  sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' ORDER BY ' + cbordem.Text + ' ASC';
                  fdquerysql6.Close;
                  fdquerysql6.SQL.Clear;
                  fdquerysql6.SQL.Text := sql;
                  fdquerysql6.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql6;
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'RELACIONA_DIOCESES' then
            begin
              with modulo_dados, frmconsulta3 do
              begin
                  sql := 'SELECT dio.id, dio.nome, estado.usersigla, estado.usernome_estado, uccnbb.descricao';
                  sql := sql + ' FROM USERdioceses_CNBB dio with(nolock)';
                  sql := sql + ' INNER JOIN USEREstado_CNBB estado ON dio.estado_id = estado.USERid';
                  sql := sql + ' LEFT JOIN USERcidades_CNBB uccnbb with(nolock) ON dio.id = uccnbb.diocese_id';
                  sql := sql + ' WHERE estado.USERid = ' + QuotedStr(frmrelacionaentidadediocese.estadoid);
                  sql := sql + ' AND ' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' ORDER BY ' + cbordem.Text + ' ASC';

                  fdquerysql5.Close;
                  fdquerysql5.SQL.Clear;
                  fdquerysql5.SQL.Text := sql;
                  fdquerysql5.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql5, fdbanco, false, dtsfdquerysql5) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql5;
                      gridconsulta.Refresh;
                    end;
                end;
            end
         else if controle = 'TIPO_EVENTOS' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql := 'SELECT * FROM USER_geoapolo_tipo_eventos';
                  sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';

                  fdquerysql7.Close;
                  fdquerysql7.SQL.Clear;
                  fdquerysql7.SQL.Text := sql;
                  fdquerysql7.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql7, fdbanco, false, dtsfdquerysql7) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql7;
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'EVENTOS_IMPORTA' then
            begin
              with modulo_dados, frmconsulta3 do
              begin
                  sql := 'SELECT uge.idevento, uge.descricao FROM USER_geoapolo_eventos uge with(nolock)';
                  sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';

                  fdquerysql9.Close;
                  fdquerysql9.SQL.Clear;
                  fdquerysql9.SQL.Text := sql;
                  fdquerysql9.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql9, fdbanco, false, dtsfdquerysql9) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql9;
                      gridconsulta.Refresh;
                    end;
              end;
            end
         else if controle = 'MOTIVO_OCORRENCIA_PADRAO' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql := 'SELECT mo.motocorcodestr, mo.motocordescr';
                  sql := sql + ' FROM MOTIVO_OCOR mo with(nolock)';
                  sql := sql + ' WHERE mo.MotOcorGrupo = ' + QuotedStr('F');
                  sql := sql + ' AND ' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' ORDER BY mo.MotOcorCodEstr ASC';

                  fdquerysql.Close;
                  fdquerysql.SQL.Clear;
                  fdquerysql.SQL.Text := sql;
                  fdquerysql.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql;
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'BUSCAORIGEMPADRAOIM' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql := 'SELECT o.OrigCodEstr, o.OrigNome';
                  sql := sql + ' FROM ORIGEM o with(nolock)';
                  sql := sql + ' WHERE o.OrigGrupo = ' + QuotedStr('F');
                  sql := sql + ' AND o.OrigAtiva = ' + QuotedStr('Sim');
                  sql := sql + ' AND ' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' ORDER BY o.OrigCodEstr ASC';

                  fdquerysql6.Close;
                  fdquerysql6.SQL.Clear;
                  fdquerysql6.SQL.Text := sql;
                  fdquerysql6.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql6;
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'BUSCAORIGEMPADRAONI' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql := 'SELECT ugo.geo_origcodestr, ugo.geo_orignome';
                  sql := sql + ' FROM USER_geoapolo_origens ugo with(nolock)';
                  sql := sql + ' WHERE ugo.geo_origativa = ' + QuotedStr('Sim');
                  sql := sql + ' AND ' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' ORDER BY ugo.geo_origcodestr ASC';

                  fdquerysql6.Close;
                  fdquerysql6.SQL.Clear;
                  fdquerysql6.SQL.Text := sql;
                  fdquerysql6.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql6;
                      gridconsulta.Refresh;
                    end;
               end;
             end
         else if controle = 'ENTIDADESOLICITANTEOCORRENCIA' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql := 'SELECT e.entcod, e.entnome, ec.categcodestr, e.entstatdescr';
                  sql := sql + ' FROM ENTIDADE e with(nolock)';
                  sql := sql + ' INNER JOIN ENT_CATEG ec with(nolock) ON e.EntCod = ec.EntCod';
                  sql := sql + ' WHERE ec.CategCodEstr in (' + QuotedStr('09.01') + ', ' + QuotedStr('03.001') + ', ' + QuotedStr('03.004') + ')';
                  sql := sql + ' AND ' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' GROUP BY e.entcod, e.EntNome, ec.categcodestr, e.EntStatDescr';
                  sql := sql + ' ORDER BY e.EntNome ASC';

                  fdquerysql.Close;
                  fdquerysql.SQL.Clear;
                  fdquerysql.SQL.Text := sql;
                  fdquerysql.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql;
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'ORIGEMOCORRENCIA' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql := 'SELECT o.OrigCodEstr, o.OrigNome FROM ORIGEM o with(nolock)';
                  sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' ORDER BY o.OrigCodEstr ASC';

                  fdquerysql.Close;
                  fdquerysql.SQL.Clear;
                  fdquerysql.SQL.Text := sql;
                  fdquerysql.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql;
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'ENTIDADE-ORIGEM' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql := 'SELECT EntCod, EntNome';
                  sql := sql + ' FROM ENTIDADE with(nolock)';
                  sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';

                  fdquerysql6.Close;
                  fdquerysql6.SQL.Clear;
                  fdquerysql6.SQL.Text := sql;
                  fdquerysql6.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql6;
                      setcursorsql('');
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'ENTIDADE-DESTINO' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql := 'SELECT EntCod, EntNome';
                  sql := sql + ' FROM ENTIDADE e with(nolock)';
                  sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';

                  fdquerysql6.Close;
                  fdquerysql6.SQL.Clear;
                  fdquerysql6.SQL.Text := sql;
                  fdquerysql6.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql6;
                      setcursorsql('');
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'CATEGORIA_APOLOSAVIC' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql := 'SELECT cat.CategCodEstr, cat.CategNome';
                  sql := sql + ' FROM CATEGORIA cat with(nolock)';
                  sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' ORDER BY cat.CategCodEstr ASC';

                  fdquerysql6.Close;
                  fdquerysql6.SQL.Clear;
                  fdquerysql6.SQL.Text := sql;
                  fdquerysql6.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql6;
                      setcursorsql('');
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'FUNCAO_APOLOSAVIC' then
            begin
{                 with modulo_dados, frmconsulta3 do
                 begin
                    executaracao(sql,fdquerysql6);
                    if querysql6.RecordCount > 0 then
                       begin
                          sql:='SELECT f.funcaoId, f.descricao AS NomeFuncao';
                          sql:=sql+' FROM funcao f';
                          sql:=sql+' WHERE '+cbocampo.Text+' LIKE '+quotedstr(lblprocurarpor.text);
                          sql:=sql+' ORDER BY f.funcaoid ASC';
                          fdbanco.params.values['Servers']:='191.252.53.94';
                          fdbanco.params.Username:='rccbrasilsavic';
                          fdbanco.params.Password:='b2J4earCJuNcM7';
                          fdbanco.params.Database:='rccbrasilsavic';
                          try
                            fdbanco.connected := true;
                          except
                          On e: exception do
                             begin
                                showmessage(e.Message);
                                exit;
                             end;
                          end;
                          fdquerysql6.Connection:=fdbanco;
                          if executaracao(fdquerysql6,fdbanco,true,dtsfdquerysql6) then
                             begin
                                gridconsulta.DataSource := dtsfdquerysql6;
                                setcursorsql('');
                                gridconsulta.Refresh;
                              end;
                       end;}
               end
         else if controle = 'ORIGEM_SAVIC' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql := 'SELECT o.origcodestr, o.orignome';
                  sql := sql + ' FROM origem o';
                  sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' ORDER BY o.origcodestr ASC';

                  fdquerysql6.Close;
                  fdquerysql6.SQL.Clear;
                  fdquerysql6.SQL.Text := sql;
                  fdquerysql6.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql6;
                      setcursorsql('');
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'TIPO_COBRANCA_ENTIDADE' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql := 'SELECT tc.tipocobcod, tc.tipocobnome FROM tipo_cobranca tc with(nolock)';
                  sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' ORDER BY ' + cbordem.Text + ' ASC';

                  fdquerysql9.Close;
                  fdquerysql9.SQL.Clear;
                  fdquerysql9.SQL.Text := sql;
                  fdquerysql9.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql9, fdbanco, false, dtsfdquerysql9) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql9;
                      setcursorsql('');
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'TIPO_COBRANCA_GEOAPOLO' then
            begin
               with modulo_dados, frmprincipal do
               begin
                  sql := 'SELECT gtc.geotipocobcod, gtc.geotipocobnome FROM USER_geoapolo_tipo_cobranca gtc with(nolock)';
                  sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' ORDER BY ' + cbordem.Text + ' ASC';

                  fdquerysql9.Close;
                  fdquerysql9.SQL.Clear;
                  fdquerysql9.SQL.Text := sql;
                  fdquerysql9.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql9, fdbanco, false, dtsfdquerysql9) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql9;
                      setcursorsql('');
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'BANCO_ENTIDADE' then
            begin
                if not Assigned(modulo_dados) then Exit;
                if not Assigned(frmconsulta3) then Exit;

                with modulo_dados, frmconsulta3 do
                begin
                  // Garante que o combobox tem valor antes de montar o SQL
                  if (Trim(cbocampo.Text) = '') or (Trim(cbordem.Text) = '') then
                    begin
                      ShowMessage('Selecione o campo e a ordem antes de consultar.');
                      Exit;
                    end;

                  try
                    fdquerysql9.Close;
                    fdquerysql9.SQL.Clear;
                    fdquerysql9.SQL.Text :=
                      'SELECT bco.bconum, bco.bconome FROM banco bco WITH(NOLOCK)' +
                      ' WHERE bco.' + cbocampo.Text + ' LIKE :procurarpor' +
                      ' ORDER BY bco.' + cbordem.Text + ' ASC';

                    fdquerysql9.ParamByName('procurarpor').AsString :=
                      '%' + lblprocurarpor.Text + '%';

                    if executaracao(fdquerysql9, fdbanco, True, dtsfdquerysql9) then
                    begin
                      dtsfdquerysql9.DataSet  := fdquerysql9;
                      gridconsulta.DataSource := dtsfdquerysql9;
                      gridconsulta.Refresh;
                      setcursorsql('');
                    end;
                  except
                    on E: Exception do
                      ShowMessage('Erro na consulta: ' + E.Message);
                  end;
                end;            end
         else if controle = 'BANCO_ENTIDADE_GEOAPOLO' then
            begin
               with modulo_dados do
                begin
                  fdquerysql9.Close;
                  fdquerysql9.SQL.Clear;
                  fdquerysql9.SQL.Text :=
                    'SELECT bco.geobconum, bco.geobconome FROM USER_geoapolo_bancos bco WITH(NOLOCK)' +
                    ' WHERE bco.' + cbocampo.Text + ' LIKE :procurarpor' +
                    ' ORDER BY bco.' + cbordem.Text + ' ASC';
                  fdquerysql9.ParamByName('procurarpor').AsString := '%' + lblprocurarpor.Text + '%';

                  if executaracao(fdquerysql9, fdbanco, True, dtsfdquerysql9) then
                  begin
                    dtsfdquerysql9.DataSet         := fdquerysql9;
                    frmconsulta3.gridconsulta.DataSource := dtsfdquerysql9;
                    setcursorsql('');
                    frmconsulta3.gridconsulta.Refresh;
                  end;
                end;
            end
         else if controle = 'AGENCIA_BCO_ENTIDADE' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql := 'SELECT ag.agnum, ag.agnome FROM ag_bancaria ag with(nolock)';
                  sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';
                  if frmcadentidade.lblbconum.Text <> '' then
                    sql := sql + ' AND bconum = ' + QuotedStr(frmcadentidade.lblbconum.Text);
                  sql := sql + ' ORDER BY ' + cbordem.Text + ' ASC';

                  fdquerysql9.Close;
                  fdquerysql9.SQL.Clear;
                  fdquerysql9.SQL.Text := sql;
                  fdquerysql9.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql9, fdbanco, false, dtsfdquerysql9) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql9;
                      setcursorsql('');
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'AGENCIA_BCO_ENTIDADE_GEOAPOLO' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql := 'SELECT gag.geoagnum, gag.geoagnome FROM USER_geoapolo_agbancaria gag with(nolock)';
                  sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';
                  if frmcadentidade.lblbconum.Text <> '' then
                    sql := sql + ' AND gag.geobconum = ' + QuotedStr(frmcadentidade.lblbconum.Text);
                  sql := sql + ' ORDER BY ' + cbordem.Text + ' ASC';

                  fdquerysql9.Close;
                  fdquerysql9.SQL.Clear;
                  fdquerysql9.SQL.Text := sql;
                  fdquerysql9.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql9, fdbanco, false, dtsfdquerysql9) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql9;
                      setcursorsql('');
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'DIOCESES_CNBB_ENTIDADE' then
            begin
               with modulo_dados do
               begin
                  sql:='SELECT udcnbb.id, udcnbb.nome';
                  sql:=sql+' FROM USERdioceses_CNBB udcnbb with(nolock)';
                  sql:=sql+' INNER JOIN USEREstado_CNBB uecnbb with(nolock) ON udcnbb.estado_id = uecnbb.USERiD';
                  sql:=sql+' INNER JOIN USERcidades_CNBB uccnbb with(nolock) ON udcnbb.id = uccnbb.diocese_id';
                  sql:=sql+' WHERE udcnbb.'+cbocampo.Text+' LIKE :procurarpor';
                  sql:=sql+' GROUP BY udcnbb.ID, udcnbb.nome ';
                  sql:=sql+' ORDER BY '+cbordem.Text+' ASC';
                  fdquerysql9.close;
                  fdquerysql9.sql.clear;
                  fdquerysql9.sql.text := sql;
                  fdquerysql9.parambyname('procurarpor').asstring:= quotedstr(lblprocurarpor.Text);
                  if executaracao(fdquerysql9, fdbanco, true, dtsfdquerysql9) then
                     begin
                        dtsfdconsulta.dataset := fdquerysql9;
                        setcursorsql('');
                        gridconsulta.Refresh;
                     end;
               end;
            end
         else if controle = 'CATEGORIA_IMPORTA_GRUPOORACAO' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql := 'SELECT cat.categcodestr, cat.categnome';
                  sql := sql + ' FROM categoria cat with(nolock)';
                  sql := sql + ' WHERE substring(cat.CategCodEstr,1,6) in (' + QuotedStr('02.001') + ', ' + QuotedStr('02.002') + ', ' + QuotedStr('03.001') + ', ' + QuotedStr('03.002') + ', ' + QuotedStr('03.003') + ', ' + QuotedStr('03.004') + ', ' + QuotedStr('03.005') + ', ' + QuotedStr('03.006') + ')';
                  sql := sql + ' AND ' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' ORDER BY ' + cbordem.Text + ' ASC';

                  fdquerysql5.Close;
                  fdquerysql5.SQL.Clear;
                  fdquerysql5.SQL.Text := sql;
                  fdquerysql5.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql5, fdbanco, false, dtsfdquerysql5) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql5;
                      setcursorsql('');
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'IMOBILIZADOCENTROCONTROLE' then
            begin
              with modulo_dados, frmconsulta3 do
              begin
                  sql := 'SELECT geocctrlcodestr, geocctrlnome';
                  sql := sql + ' FROM USER_geoapolo_centrocontrole';
                  sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' ORDER BY ' + cbordem.Text + ' ASC';

                  fdquerysql6.Close;
                  fdquerysql6.SQL.Clear;
                  fdquerysql6.SQL.Text := sql;
                  fdquerysql6.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql6;
                      setcursorsql('');
                      gridconsulta.Refresh;
                    end;
              end;
            end
         else if controle = 'IMOBILIZADOCLASSIFICACAO' then
            begin
              with modulo_dados, frmconsulta3 do
              begin
                  sql := 'SELECT ugsca.codigoclasse, ugsca.descricao, ugsca.codigo_categoria';
                  sql := sql + ' FROM vw_geoapolo_satfimob ugsca with(nolock)';
                  sql := sql + ' WHERE ugsca.' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' ORDER BY ugsca.' + cbordem.Text + ' ASC';

                  fdquerysql6.Close;
                  fdquerysql6.SQL.Clear;
                  fdquerysql6.SQL.Text := sql;
                  fdquerysql6.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql6;
                      setcursorsql('');
                      gridconsulta.Refresh;
                    end;
              end;
            end
         else if controle = 'IMOBILIZADOCATEGORIABEM' then
            begin
              with modulo_dados, frmconsulta3 do
              begin
                sql := 'SELECT ugsc.codigo_categoria, ugsc.descricao as Categoria';
                sql := sql + ' FROM USER_geoapolo_satfi_categorias ugsc with(nolock)';
                sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';
                sql := sql + ' ORDER BY ' + cbordem.Text + ' ASC';

                fdquerysql6.Close;
                fdquerysql6.SQL.Clear;
                fdquerysql6.SQL.Text := sql;
                fdquerysql6.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
                  begin
                    gridconsulta.DataSource := dtsfdquerysql6;
                    setcursorsql('');
                    gridconsulta.Refresh;
                  end;
              end;
            end
         else if controle = 'IMOBILIZADOLOCALIZACAOFISICA' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql := 'SELECT ugslf.codigo_localizacao as stfcodlocestr, ugslf.grupo, ugslf.localizacao, ugslf.codigo_departamento, ugd.nome_departamento as departamento';
                  sql := sql + ' FROM USER_geoapolo_satfi_localizacao_fisica ugslf with(nolock)';
                  sql := sql + ' INNER JOIN USER_geoapolo_departamentos ugd with(nolock) ON ugslf.codigo_departamento = ugd.codigo_departamento AND ugd.flagativo = ' + QuotedStr('A');
                  sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' ORDER BY ' + cbordem.Text + ' ASC';

                  fdquerysql6.Close;
                  fdquerysql6.SQL.Clear;
                  fdquerysql6.SQL.Text := sql;
                  fdquerysql6.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql6;
                      setcursorsql('');
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'IMOBILIZADORESPONSAVELBEM' then
            begin
                with modulo_dados, frmconsulta3 do
                begin
                  sql := 'SELECT ugu.usucod, ugu.usucod_apolo, ugu.nome_completo, ugu.codigo_departamento, ugd.nome_departamento';
                  sql := sql + ' FROM USER_geoapolo_usuarios ugu';
                  sql := sql + ' INNER JOIN USER_geoapolo_departamentos ugd with(nolock) ON ugu.codigo_departamento = ugd.codigo_departamento AND ugd.flagativo = ' + QuotedStr('A');
                  sql := sql + ' WHERE ugu.flagativo = ' + QuotedStr('A');
                  sql := sql + ' AND ' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' ORDER BY ' + cbordem.Text + ' ASC';

                  fdquerysql6.Close;
                  fdquerysql6.SQL.Clear;
                  fdquerysql6.SQL.Text := sql;
                  fdquerysql6.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql6;
                      setcursorsql('');
                      gridconsulta.Refresh;
                    end;
                end;
            end
         else if controle = 'IMOBILIZADOMARCA' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql := 'SELECT ugpm.codigo_marca, ugpm.descricao_marca';
                  sql := sql + ' FROM USER_geoapolo_produto_marcas ugpm with(nolock)';
                  sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' ORDER BY ' + cbordem.Text + ' ASC';

                  fdquerysql6.Close;
                  fdquerysql6.SQL.Clear;
                  fdquerysql6.SQL.Text := sql;
                  fdquerysql6.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql6;
                      setcursorsql('');
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'BUSCAMARCACADMARCA' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql := 'SELECT ugpm.codigo_marca, ugpm.descricao_marca';
                  sql := sql + ' FROM user_geoapolo_produto_marcas ugpm';
                  sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' ORDER BY descricao_marca ASC';

                  fdquerysql6.Close;
                  fdquerysql6.SQL.Clear;
                  fdquerysql6.SQL.Text := sql;
                  fdquerysql6.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql6;
                      setcursorsql('');
                      gridconsulta.Refresh;
                    end;
               end;
            end
         else if controle = 'IMOBILIZADOSTATUS' then
            begin
              with modulo_dados, frmconsulta3 do
              begin
                  sql := 'SELECT ugssi.codigo_status_bem, ugssi.descricao_status_bem';
                  sql := sql + ' FROM USER_geoapolo_satfi_status_imobilizado ugssi with(nolock)';
                  sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';
                  sql := sql + ' ORDER BY ' + cbordem.Text + ' ASC';

                  fdquerysql6.Close;
                  fdquerysql6.SQL.Clear;
                  fdquerysql6.SQL.Text := sql;
                  fdquerysql6.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                  if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
                    begin
                      gridconsulta.DataSource := dtsfdquerysql6;
                      setcursorsql('');
                      gridconsulta.Refresh;
                    end;
              end;
            end
         else if controle = 'IMOBILIZADOBUSCABEM' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                sql := 'SELECT ugsai.numero_do_bem, ugsai.descricao_do_bem, ugsai.geocctrlcodestr, ugcc.geocctrlnome as CentroControle,';
                sql := sql + '   ugsai.codigo_categoria_bem, ugsc.descricao as Categoria, ugsai.codigo_classificacaoativoimobilizado as CodClassificacao,';
                sql := sql + '   ugsc.descricao as Classificacao, ugsai.plaqueta_do_bem, ugsai.numero_de_serie, ugsai.codigo_da_marca, ugpm.descricao_marca as Marca,';
                sql := sql + '   ugsai.codigo_localizacao, ugslf.localizacao as Localizacao, ugsai.codigo_func_responsavel, ugu.nome_completo, ugsai.codigo_status_bem,';
                sql := sql + '   ugssi.descricao_status_bem as StatusDoBem';
                sql := sql + ' FROM USER_geoapolo_satfi_ativoimobilizado ugsai with(nolock)';
                sql := sql + ' INNER JOIN USER_geoapolo_centrocontrole ugcc with(nolock) ON ugsai.geocctrlcodestr = ugcc.geocctrlcodestr';
                sql := sql + ' INNER JOIN USER_geoapolo_satfi_categorias ugsc with(nolock) ON ugsai.codigo_categoria_bem = ugsc.codigo_categoria';
                sql := sql + ' INNER JOIN USER_geoapolo_satfi_classificacaoativo ugsca with(nolock) ON ugsai.codigo_classificacaoativoimobilizado = ugsca.codigoclasse';
                sql := sql + ' INNER JOIN USER_geoapolo_produto_marcas ugpm with(nolock) ON ugsai.codigo_da_marca = ugpm.codigo_marca';
                sql := sql + ' INNER JOIN USER_geoapolo_satfi_localizacao_fisica ugslf with(nolock) ON ugsai.codigo_localizacao = ugslf.codigo_localizacao';
                sql := sql + ' INNER JOIN USER_geoapolo_usuarios ugu with(nolock) ON ugsai.codigo_func_responsavel = ugu.usucod';
                sql := sql + ' INNER JOIN USER_geoapolo_satfi_status_imobilizado ugssi with(nolock) ON ugsai.codigo_status_bem = ugssi.codigo_status_bem';
                sql := sql + ' WHERE ' + cbocampo.Text + ' LIKE :procurarpor';
                sql := sql + ' ORDER BY ' + cbordem.Text + ' ASC';

                fdquerysql6.Close;
                fdquerysql6.SQL.Clear;
                fdquerysql6.SQL.Text := sql;
                fdquerysql6.ParamByName('procurarpor').AsString := lblprocurarpor.Text;

                if executaracao(fdquerysql6, fdbanco, false, dtsfdquerysql6) then
                  begin
                    gridconsulta.DataSource := dtsfdquerysql6;
                    setcursorsql('');
                    gridconsulta.Refresh;
                  end;

               end;
            end
         else if controle = 'GEOCADCARTADOCREDITO' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                   sql:='SELECT ugb.geobconum, ugb.geobconome ';
                   sql:=sql+ ' FROM USER_geoapolo_bancos ugb with(nolock)';
                   sql:=sql+ ' WHERE '+cbocampo.Text+' LIKE :procurarpor';
                   sql:=sql+' ORDER BY '+cbordem.Text+' ASC';
                   fdquerysql.Close;
                   fdquerysql.SQL.Clear;
                   fdquerysql.SQL.Text := sql;
                   if executaracao(fdquerysql, fdbanco, false, dtsfdquerysql) then
                      begin
                         gridconsulta.DataSource := dtsfdquerysql;
                         setcursorsql('');
                         gridconsulta.Refresh;
                      end;
               end;
            end
         else if controle = 'BUSCAENTPADRAOOCORAPOLO' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql:='SELECT e.entcod, e.entnome, ec.categcodestr, cat.categnome';
                  sql:=sql+' FROM entidade e with(nolock) ';
                  sql:=sql+' INNER JOIN ent_categ ec with(nolock) ON e.entcod = ec.entcod';
                  sql:=sql+' INNER JOIN categoria cat with(nolock) ON ec.categcodestr = cat.categcodestr';
                  sql:=sql+' WHERE '+cbocampo.Text+' LIKE :procurarpor';
                  fdquerysql9.Close;
                  fdquerysql9.SQL.Clear;
                  fdquerysql9.SQL.Text := sql;
                  if executaracao(fdquerysql9, fdbanco, false, dtsfdquerysql9) then
                     begin
                        gridconsulta.DataSource := dtsfdquerysql9;
                        setcursorsql('');
                        gridconsulta.Refresh;
                     end;
               end;
            end
         else if controle = 'BUSCAENTPADRAOOCORGEOAPOLO' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql:= 'SELECT  uge.geoentcod, uge.geoentnome,ugec.geocategcodestr, ugc.geocategnome';
                  sql:=sql+' FROM USER_geoapolo_entidade uge with(nolock)';
                  sql:=sql+' INNER JOIN USER_geoapolo_entcateg ugec with(nolock) ON uge.geoentcod = ugec.geoentcod';
                  sql:=sql+' INNER JOIN USER_geoapolo_categoria ugc with(nolock) ON ugec.geocategcodestr = ugc.geocategcodestr';
                  sql:=sql+' WHERE '+cbocampo.Text+' LIKE :procurarpor';
                  fdquerysql9.Close;
                  fdquerysql9.SQL.Clear;
                  fdquerysql9.SQL.Text := sql;
                  if executaracao(fdquerysql9, fdbanco, false, dtsfdquerysql9) then
                     begin
                        gridconsulta.DataSource := dtsfdquerysql9;
                        setcursorsql('');
                        gridconsulta.Refresh;
                     end;
               end;
            end
         else if controle = 'BUSCASOLOCORAPOLO' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql:='SELECT tso.tiposolocorcod, tso.tiposolocornome, tso.tiposolocortexto';
                  sql:=sql+' FROM TIPO_SOL_OCOR tso with(nolock)';
                  sql:=sql+' WHERE '+cbocampo.Text+' LIKE :procurarpor';
                  sql:=sql+' ORDER BY tso.TipoSolOcorCod';
                  fdquerysql7.Close;
                  fdquerysql7.SQL.Clear;
                  fdquerysql7.SQL.Text := sql;
                  if executaracao(fdquerysql7, fdbanco, false, dtsfdquerysql7) then
                     begin
                        fdquerysql7.First;
                        for i:= 0 to fdquerysql7.fields.count -1 do
                        begin
                           cbocampo.items.add(fdquerysql7.fields[i].displayname);
                           cbordem.items.add(fdquerysql7.fields[i].displayname);
                        end;
                        gridconsulta.datasource:=dtsfdquerysql7;
                     end;
               end;
            end
         else if controle = 'BUSCASOLOCORGEOAPOLO' then
            begin
               showmessage('AINDA NÃO HÁ DESENVOLVIMENTO PARA ROTINA DE OCORRÊNCIA NO GEOAPOLO !!!');
            end
         else if controle = 'TIPOCAMPANHA' then
            begin
               with modulo_dados, frmconsulta3 do
               begin
                  sql:='SELECT * FROM tipo_campanha';
                  sql:=sql+' WHERE '+cbocampo.Text+' LIKE :procurarpor';
                  sql:=sql+' ORDER BY '+cbordem.Text+' ASC';
                  fdquerysql2.Close;
                  fdquerysql2.SQL.Clear;
                  fdquerysql2.SQL.Text := sql;
                  if executaracao(fdquerysql2, fdbanco, false, dtsfdquerysql2) then
                     begin
                         fdquerysql2.First;
                        for i:= 0 to fdquerysql2.fields.count -1 do
                        begin
                           cbocampo.items.add(fdquerysql2.fields[i].displayname);
                           cbordem.items.add(fdquerysql2.fields[i].displayname);
                        end;
                        gridconsulta.datasource:=dtsfdquerysql2;
                       end;
               end;
            end
         else if controle = 'GEOTIPOCAMPANHA' then
            begin
                with modulo_dados, frmconsulta3 do
                 begin
                    sql:='SELECT * FROM USER_geoapolo_tipocampanha';
                    sql:=sql+' WHERE '+cbocampo.Text+' LIKE :procurarpor';
                    sql:=sql+' ORDER BY '+cbordem.Text+' ASC';
                    fdquerysql2.Close;
                    fdquerysql2.SQL.Clear;
                    fdquerysql2.SQL.Text := sql;
                    if executaracao(fdquerysql2, fdbanco, false, dtsfdquerysql2) then
                    begin
                       fdquerysql2.First;
                       for i:= 0 to fdquerysql2.fields.count -1 do
                       begin
                          cbocampo.items.add(fdquerysql2.fields[i].displayname);
                          cbordem.items.add(fdquerysql2.fields[i].displayname);
                       end;
                       gridconsulta.datasource:=dtsfdquerysql2;
                    end;
                 end;
            end
         else if controle = 'CATEGORIAPADRAOFORNECEDORES' then
            begin
               with  modulo_dados do
               begin
                  if ((frmprincipal.integraentidadesapolo = 'Não Integra') or (frmprincipal.integraentidadesapolo = 'Mescla')) then
                     begin
                        // UTILIZA A TABELA DE CATEGORIAS DO GEOAPOLO
                        sql:='SELECT ugc.geocategcodestr, ugc.geocategnome, ugc.geocategcodniv, ' ;
                        sql:=sql+'   ugc.geocateggrupo, ugc.geoempcod, ugc.geocategcodalt';
                        sql:=sql+' FROM USER_geoapolo_categoria ugc with(nolock) ';
                        sql:=sql+' WHERE '+frmconsulta3.cbocampo.Text+' LIKE :procurarpor';
                        sql:=sql+' ORDER BY ugc.geocategcodestr';
                     end
                  else if (frmprincipal.integraentidadesapolo = 'Integra') then
                     begin
                        // BUSCA AS CATEGORIAS SOMENTE DA BASE APOLO
                        sql:='SELECT ec.categcodestr, cat.categnome FROM ent_categ ec';
                        sql:=sql+' INNER JOIN categoria cat ON ec.CategCodEstr = cat.CategCodEstr';
                        sql:=sql+' WHERE '+frmconsulta3.cbocampo.Text+' LIKE :procurarpor';
                        sql:=sql+' GROUP BY ec.CategCodEstr, cat.categnome';
                        sql:=sql+' ORDER BY ec.CategCodEstr';
                     end;
                  fdquerysql9.Close;
                  fdquerysql9.SQL.Clear;
                  fdquerysql9.SQL.Text := sql;
                  fdquerysql9.ParamByName('procurarpor').AsString := frmconsulta3.lblprocurarpor.text;
                  if executaracao(fdquerysql9, fdbanco, false, dtsfdquerysql9) then
                     begin
                        with frmConsulta3 do
                        begin
                           for i:= 0 to fdquerysql9.fields.count -1 do
                           begin
                              cbocampo.items.add(fdquerysql9.fields[i].displayname);
                              cbordem.items.add(fdquerysql9.fields[i].displayname);
                           end;
                        end;
                     end;                end;
            end
         else if controle = 'GEOLCTOCARTOES' then
            begin
               with modulo_dados do
               begin
                  {if (frmprincipal.integraentidadesapolo = 'Integra') or (frmprincipal.integraentidadesapolo = 'Mescla')  then
                     begin
                        sql:='SELECT e.entcod, e.entnome';
                        sql:=sql+' FROM entidade e with(nolock)';
                        sql:=sql+' INNER JOIN ent_categ ec with(nolock) ON e.entcod = ec.entcod ';
                        sql:=sql+' INNER JOIN categoria cat with(nolock) ON ec.categcodestr = cat.categcodestr';
                        sql:=sql+' WHERE '+cbocampo.Text+' LIKE '+quotedstr(lblprocurarpor.Text);
                        sql:=sql+' ORDER BY e.entcod ASC';
                     end
                  else if (frmprincipal.integraentidadesapolo = 'Não Integra') then
                     begin
                        sql:='SELECT uge.geoentcod, uge.geoentnome';
                        sql:=sql+' FROM USER_geoapolo_entidade uge with(nolock)';
                        sql:=sql+' INNER JOIN USER_geoapolo_entcateg ugec with(nolock) ON uge.geoentcod = ugec.geoentcod ';
                        sql:=sql+' INNER JOIN USER_geoapolo_categoria ugc with(nolock) ON ugec.geocategcodestr = ugc.geocategcodestr';
                        sql:=sql+' WHERE '+cbocampo.Text+' LIKE '+quotedstr(lblprocurarpor.Text);
                        sql:=sql+' ORDER BY uge.geoentcod ASC';
                     end ;
                  executaracao(sql,querysql4);
                  if querysql4.RecordCount > 0 then
                     begin
                        dtsquerysql4.DataSet:=querysql4;
                        with frmConsulta3 do
                        begin
                            for i:= 0 to querysql4.fields.count -1 do
                            begin
                               cbocampo.items.add(querysql4.fields[i].displayname);
                               cbordem.items.add(querysql4.fields[i].displayname);
                            end;
                        end;
                     end;}
               end;
            end
         else if controle = 'GEOCLASSELCTOCARTOES' then
            begin
{               with modulo_dados do
               begin
                  if (frmprincipal.integraentidadesapolo = 'Integra') or (frmprincipal.integraentidadesapolo = 'Mescla') then
                     begin
                        sql:='SELECT classerecdespcodestr, classerecdespnome';
                        sql:=sql+' FROM classe_rec_desp crd with(nolock)';
                        sql:=sql+' WHERE '+cbocampo.text+' LIKE '+quotedstr(lblprocurarpor.text);
                     end
                  else if (frmprincipal.integraentidadesapolo = 'Não Integra') then
                     begin
                        sql:='SELECT classerecdespcodestr, classerecdespnome';
                        sql:=sql+' FROM USER_geoapolo_classe_recdesp geoclasserd with(nolock)';
                        sql:=sql+' WHERE '+cbocampo.text+' LIKE '+quotedstr(lblprocurarpor.text);
                     end;
                  executaracao(sql,querysql10);
                  if querysql10.RecordCount > 0 then
                     begin
                        dtsquerysql10.DataSet:=querysql10;
                        with frmConsulta3 do
                        begin
                            for i:= 0 to querysql10.fields.count -1 do
                            begin
                               cbocampo.items.add(querysql10.fields[i].displayname);
                               cbordem.items.add(querysql10.fields[i].displayname);
                            end;
                        end;
                     end;
               end;}
            end
         else if controle = 'TIPOLANC_VENDASCUPONS' then
            begin
               with modulo_dados do
               begin
                  sql:='SELECT tl.tipolanccod, tl.TipoLancNome';
                  sql:=sql+' FROM tipo_lanc tl with(nolock)';
                  sql:=sql+' WHERE tl.tipolancmod = '+quotedstr('Vendas');
                  sql:=sql+' AND tl.tipolancnome not like '+quotedstr('%NÃO USAR%');
                  sql:=sql+' AND tl.tipolancoper = '+quotedstr('Saída');
                  sql:=sql+' AND '+cbocampo.Text+' LIKE :procurarpor';
                  fdquerysql7.Close;
                  fdquerysql7.SQL.Clear;
                  fdquerysql7.SQL.Text := sql;
                  if executaracao(fdquerysql7, fdbanco, false, dtsfdquerysql7) then
                     begin
                        with frmconsulta3 do
                        begin
                           for i:= 0 to fdquerysql7.fields.count -1 do
                           begin
                              cbocampo.items.add(fdquerysql7.fields[i].displayname);
                              cbordem.items.add(fdquerysql7.fields[i].displayname);
                           end;
                        end;
                     end;
               end;
            end
         else if (controle = 'CAMPANHASEMAIL-APOLO') and (frmprincipal.baseparacampanha = 'S') then
            begin
               with modulo_dados do
               begin
                  sql:='SELECT camp.CampNum, camp.campnome, camp.campdatacad, camp.tipocampcod, tipocamp.TipoCampNome,';
                  sql:=sql+' camp.campdataini, camp.campdatafim, camp.CampAprovData, camp.campaprovnome, camp.CampDataApres,';
                  sql:=sql+' camp.CampObjetivo, camp.UsuCod, camp.CampSql, camp.CampStat';
                  sql:=sql+' FROM campanha camp with(nolock)';
                  sql:=sql+' INNER JOIN tipo_campanha tipocamp with(nolock) ON camp.tipocampcod = tipocamp.tipocampcod';
                  sql:=sql+' WHERE camp.campstat = '+quotedstr('Aberta');
                  sql:=sql+' AND '+cbocampo.Text+' LIKE :procurarpor';
                  fdquerysql4.Close;
                  fdquerysql4.SQL.Clear;
                  fdquerysql4.SQL.Text := sql;
                  if executaracao(fdquerysql4, fdbanco, false, dtsfdquerysql4) then
                     begin
                        with frmconsulta3 do
                        begin
                           for i:= 0 to fdquerysql4.fields.count -1 do
                           begin
                              cbocampo.items.add(fdquerysql4.fields[i].displayname);
                              cbordem.items.add(fdquerysql4.fields[i].displayname);
                           end;
                        end;
                     end;
               end;
            end
         else if (controle = 'CAMPANHASEMAIL-GEOAPOLO') and (frmprincipal.baseparacampanha = 'N') then
            begin
               with modulo_dados do
               begin
                  sql:='SELECT gcc.empcod, gcc.codigo_campanha, gcc.nome_campanha, gcc.data_cadastro_campanha, gtc.descricaotipocamp,gcc.data_inicial_campanha,gcc.data_final_campanha,';
                  sql:=sql+'         gcc.aprovador_campanha,gcc.apresentacao_campanha,gcc.data_apresentacao, gcc.data_aprovacao_campanha, gcc.objetivo_campanha,gcc.mote_campanha,';
                  sql:=sql+'         gcc.plano_comum_campanha,gcc.usucod_login,gcc.valor_total_receita,gcc.valor_total_custo,gcc.valor_total_liquido,gcc.conclusao_geral_campanha,gcc.status_campanha,';
                  sql:=sql+'         gcc.estrategia_campanha,gcc.dinamica_campanha,gcc.codigo_consulta_selecao, gcc.codigo_tipocampanha';
                  sql:=sql+' FROM USER_geoapolo_crm_campanha gcc INNER JOIN geoapolo_tipocampanha gtc ON gcc.codigo_tipocampanha = gtc.codigo_tipocampanha';
                  sql:=sql+' WHERE gcc.status_campanha = '+quotedstr('Aberta');
                  fdquerysql4.Close;
                  fdquerysql4.SQL.Clear;
                  fdquerysql4.SQL.Text := sql;
                  if executaracao(fdquerysql4, fdbanco, false, dtsfdquerysql4) then
                     begin
                        with frmconsulta3 do
                        begin
                           for i:= 0 to fdquerysql4.fields.count -1 do
                           begin
                              cbocampo.items.add(fdquerysql4.fields[i].displayname);
                              cbordem.items.add(fdquerysql4.fields[i].displayname);
                           end;
                        end;
                     end;
               end;
            end
         else if (controle = 'ENTCIDCODCONTATO') and (frmprincipal.baseparacampanha = 'S') then
            begin
               with modulo_dados do
               begin
                  SQL:='SELECT * FROM USER_geoapolo_cidades';
                  sql:=sql+' WHERE '+cbocampo.Text +' LIKE :procurarpor';
                  fdquerysql9.Close;
                  fdquerysql9.SQL.Clear;
                  fdquerysql9.SQL.Text := sql;
                  if executaracao(fdquerysql9, fdbanco, false, dtsfdquerysql9) then
                     begin
                        with frmconsulta3 do
                        begin
                           for i:= 0 to fdquerysql9.fields.count -1 do
                           begin
                              cbocampo.items.add(fdquerysql9.fields[i].displayname);
                              cbordem.items.add(fdquerysql9.fields[i].displayname);
                           end;
                        end;
                     end;
               end;
            end
         else if (controle = 'BUSCAENTIDADECONSUMIDORFINALAPOLO') and (frmprincipal.baseparacampanha = 'S') then
            begin
               with modulo_dados do
               begin
                  sql:='SELECT e.entcod, e.entnome FROM entidade e with(nolock) ';
                  sql:=sql+' WHERE e.entnome like '+quotedstr('CONSUMIDOR%');
                  sql:=sql+' AND  '+cbocampo.Text+' LIKE :procurarpor';
                  fdquerysql18.Close;
                  fdquerysql18.SQL.Clear;
                  fdquerysql18.SQL.Text := sql;
                  if executaracao(fdquerysql18, fdbanco, false, dtsfdquerysql18) then
                     begin
                        application.CreateForm(tfrmconsulta3, frmconsulta3);
                        with frmconsulta3 do
                        begin
                           gridconsulta.DataSource := dtsfdquerysql18;
                           for i:= 0 to fdquerysql18.fields.count -1 do
                           begin
                              cbocampo.items.add(fdquerysql18.fields[i].displayname);
                              cbordem.items.add(fdquerysql18.fields[i].displayname);
                           end;
                        end;
                     end;
               end;
            end
         else if (controle = 'IMOBILIZADOBUSCABEM') then
            begin
               with modulo_dados do
               begin
                  sql:='SELECT ugsai.numero_do_bem, ugsai.descricao_do_bem, ugsai.geocctrlcodestr, ugcc.geocctrlnome as CentroControle,';
                  sql:=sql+'   ugsai.codigo_categoria_bem, ugsc.descricao as Categoria, ugsai.codigo_classificacaoativoimobilizado as CodClassificacao,';
                  sql:=sql+'	 ugsc.descricao as Classificacao, ugsai.plaqueta_do_bem,ugsai.numero_de_serie, ugsai.codigo_da_marca, ugpm.descricao_marca as Marca,';
                  sql:=sql+'   ugsai.codigo_localizacao, ugslf.localizacao as Localizacao, ugsai.codigo_func_responsavel, ugu.nome_completo, ugsai.codigo_status_bem,';
                  sql:=sql+'	 ugssi.descricao_status_bem as StatusDoBem';
                  sql:=sql+' FROM USER_geoapolo_satfi_ativoimobilizado ugsai with(nolock)';
                  sql:=sql+' INNER JOIN USER_geoapolo_centrocontrole ugcc with(nolock) ON ugsai.geocctrlcodestr = ugcc.geocctrlcodestr';
                  sql:=sql+' INNER JOIN USER_geoapolo_satfi_categorias ugsc with(nolock) ON ugsai.codigo_categoria_bem = ugsc.codigo_categoria';
                  sql:=sql+' INNER JOIN USER_geoapolo_satfi_classificacaoativo ugsca with(nolock) ON ugsai.codigo_classificacaoativoimobilizado = ugsca.codigoclasse';
                  sql:=sql+' INNER JOIN USER_geoapolo_produto_marcas ugpm with(nolock) ON ugsai.codigo_da_marca = ugpm.codigo_marca';
                  sql:=sql+' INNER JOIN USER_geoapolo_satfi_localizacao_fisica ugslf with(nolock) ON ugsai.codigo_localizacao = ugslf.codigo_localizacao';
                  sql:=sql+' INNER JOIN USER_geoapolo_usuarios ugu with(nolock) ON ugsai.codigo_func_responsavel = ugu.usucod';
                  sql:=sql+' INNER JOIN USER_geoapolo_satfi_status_imobilizado ugssi with(nolock) ON ugsai.codigo_status_bem = ugssi.codigo_status_bem';
               end;
            end
         else if (controle = 'GEOBUSCACARTAOCREDITO') then
            begin
               with modulo_dados do
               begin
                  sql:='SELECT ugccb.geobconum as Banco, ugccb.geonumerocartao as Cartao, ugccb.geonatureza,ugccb.geonomeimpresso, ugccb.geobandeira, ugccb.geodatavalidade, ugccb.geocodigoseguranca';
                  sql:=sql+' FROM USER_geoapolo_controlecartoesbancarios ugccb with(nolock)';
                  sql:=sql+' ORDER BY ugccb.geobconum ASC';
                  fdquerysql4.Close;
                  fdquerysql4.SQL.Clear;
                  fdquerysql4.SQL.Text := sql;
                  if executaracao(fdquerysql4, fdbanco, false, dtsfdquerysql4) then
                     begin
                        application.CreateForm(tfrmconsulta3, frmconsulta3);
                        with frmconsulta3 do
                        begin
                           gridconsulta.DataSource := dtsfdquerysql4;
                           for i:= 0 to fdquerysql4.fields.count -1 do
                           begin
                              cbocampo.items.add(fdquerysql4.fields[i].displayname);
                              cbordem.items.add(fdquerysql4.fields[i].displayname);
                           end;
                        end;
                     end;
               end;
            end;
end;

function busca_detalhada : string;
var
   a:integer;
   campos:string;
begin
   with modulo_dados, frmconsulta3 do
   begin
       //
       if cbocampo.Text = '' then
          begin
             messagedlg('DEFINA POR QUAL CAMPO DESEJA PESQUISAR !!!',mterror,[mbok],0);
             cbocampo.SetFocus;
             exit;
          end;
       if cbordem.Text = '' then
          begin
             messagedlg('PARA FAZER UMA PESQUISA É NECESSÁRIO ESTABELECER O CAMPO DE ORDENAÇÃO DA MESMA !!!',mterror,[mbok],0);
             cbordem.SetFocus;
             exit;
          end;
       sql:='SELECT * FROM '+frmconsulta3.controle+' WHERE '+cbocampo.Text+' LIKE '+chr(39)+lblprocurarpor.Text+chr(39)+' ORDER BY '+cbordem.Text;
       if (controle = 'ENTIDADEFOTOFUNCIONARIO') then
          begin
          end
       else
          begin
          end;
   end;
end;

function cria_viewmix(sqlrec : string): string;
begin
end;

procedure TfrmConsulta3.cbocampoKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_return then
      lblprocurarpor.setfocus;
end;

procedure TfrmConsulta3.cbordemKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_return then
      lblprocurarpor.setfocus;
end;

procedure TfrmConsulta3.FormActivate(Sender: TObject);
var cshift : TShiftState; tecla:word;
begin
   statusbar1.Panels[1].text := configura_statusbar('a');
   statusbar1.Panels[3].text:= configura_statusbar('a');
   statusbar1.panels[5].text :=frmprincipal.nomeserversql;
   if controle = 'EMPRESA_FILIAL' then
      begin
         carrega_config('EMPRESA_FILIAL',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('EMPRESA_FILIAL',frmConsulta3,'gridconsulta3',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql);
      end
   else if controle = 'CLIENTES' then
      begin
         carrega_config('CLIENTES',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('CLIENTES',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql);
      end
   else if controle = 'NOTA_FISCAL_PVAGRUP' then
      begin
         carrega_config('NOTA_FISCAL_PVAGRUP',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('NOTA_FISCAL_PVAGRUP',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql);
      end
   else if controle = 'OS_SEM_CMUTILIZADO' then
      begin
         carrega_config('OS_SEM_CMUTILIZADO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('OS_SEM_CMUTILIZADO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql);
      end
   else if controle = 'SITCODESTRORIG' then
      begin
         carrega_config('SITCODESTRORIG',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('SITCODESTRORIG',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql4);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql4; gridconsulta.refresh;
      end
   else if controle = 'SITCODESTRDESTINO' then
      begin
         carrega_config('SITCODESTRDESTINO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('SITCODESTRDESTINO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql4);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql4; gridconsulta.Refresh;
      end
   else if controle = 'CATEGORIA_SITUACAO_TITULOS' then
      begin
         carrega_config('CATEGORIA_SITUACAO_TITULOS',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('CATEGORIA_SITUACAO_TITULOS',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql4);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql4; gridconsulta.Refresh;
      end
   else if controle = 'CONTA_FINANCEIRASALDO' then
      begin
         carrega_config('CONTA_FINANCEIRASALDO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('CONTA_FINANCEIRASALDO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql11);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql4; gridconsulta.Refresh;
      end
   else if controle = 'USUARIO_DEPARTAMENTO' then
      begin
         carrega_config('USUARIO_DEPARTAMENTO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('USUARIO_DEPARTAMENTO',frmconsulta3,frmlogon.nomeusuario,'gridconsulta',gridconsulta,modulo_dados.dtsfdquerysql4);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql4; gridconsulta.Refresh;
      end
   else if controle = 'CIDADE_CIDADE' then
      begin
         carrega_config('CIDADE_CIDADE',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('CIDADE_CIDADE',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql);
         //gridconsulta.DataSource:= modulo_dados.dtsfdquerysql9; gridconsulta.Refresh;
      end
   else if controle = 'CIDADES_COBRANCA' then
      begin
         carrega_config('CIDADES_COBRANCA',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('CIDADES_COBRANCA',frmconsulta3,frmlogon.nomeusuario,'gridconsulta',gridconsulta,modulo_dados.dtsfdquerysql9);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql9; gridconsulta.Refresh;
      end
   else if controle = 'CIDADES_ENTREGA' then
      begin
         carrega_config('CIDADES_ENTREGA',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('CIDADES_ENTREGA',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql9);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql9; gridconsulta.Refresh;
      end
   else if controle = 'TIPOLOGRADOURO' then
      begin
         carrega_config('TIPOLOGRADOURO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('TIPOLOGRADOURO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql9; gridconsulta.Refresh;
      end
   else if controle = 'TIPOLOGRADOURO_MESCLA' then
      begin
         carrega_config('TIPOLOGRADOURO_MESCLA',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('TIPOLOGRADOURO_MESCLA',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql9; gridconsulta.Refresh;
      end
   else if controle = 'TIPOLOGRADOURO_ENDCOBRANCA' then
      begin
         carrega_config('TIPOLOGRADOURO_ENDCOBRANCA',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('TIPOLOGRADOURO_ENDCOBRANCA',frmconsulta3,frmlogon.nomeusuario,'gridconsulta',gridconsulta,modulo_dados.dtsfdquerysql9);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql9; gridconsulta.Refresh;
      end
   else if controle = 'TIPOLOGRADOURO_ENDENTREGA' then
      begin
         carrega_config('TIPOLOGRADOURO_ENDENTREGA',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('TIPOLOGRADOURO_ENDENTREGA',frmconsulta3,frmlogon.nomeusuario,'gridconsulta',gridconsulta,modulo_dados.dtsfdquerysql1);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql1; gridconsulta.Refresh;
      end
   else if controle = 'ORIGEM_ENTIDADE' then
      begin
         carrega_config('ORIGEM_ENTIDADE',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('ORIGEM_ENTIDADE',frmconsulta3,frmlogon.nomeusuario,'gridconsulta',gridconsulta,modulo_dados.dtsfdquerysql9);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql9; gridconsulta.Refresh;
      end
   else if controle = 'ORIGEM_ENTIDADE_APOLO' then
      begin
         carrega_config('ORIGEM_ENTIDADE_APOLO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('ORIGEM_ENTIDADE_APOLO',frmconsulta3,frmlogon.nomeusuario,'gridconsulta',gridconsulta,modulo_dados.dtsfdquerysql9);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql9; gridconsulta.Refresh;
      end
   else if controle = 'ATIVIDADE_ECONOMICAG' then
      begin
         carrega_config('ATIVIDADE_ECONOMICAG',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('ATIVIDADE_ECONOMICAG',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql9);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql9; gridconsulta.Refresh;
      end
   else if controle = 'ATIVIDADE_ECONOMICA_APOLO' then
      begin
         carrega_config('ATIVIDADE_ECONOMICA_APOLO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('ATIVIDADE_ECONOMICA_APOLO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql9);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql9; gridconsulta.Refresh;
      end
   else if controle = 'GRUPO_PRODUTO' then
      begin
         carrega_config('GRUPO_PRODUTO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('GRUPO_PRODUTO',frmconsulta3,frmlogon.nomeusuario,'gridconsulta',gridconsulta,modulo_dados.dtsfdquerysql1);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql1; gridconsulta.Refresh;
      end
   else if controle = 'MARCA_PRODUTO' then
      begin
         carrega_config('MARCA_PRODUTO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('MARCA_PRODUTO',frmconsulta3,frmlogon.nomeusuario,'gridconsulta',gridconsulta,modulo_dados.dtsfdquerysql1);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql14; gridconsulta.Refresh;
      end
   else if controle = 'MARCA_ESTACOES' then
     begin
        carrega_config('MARCA_ESTACOES',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
        configura_grid('MARCA_ESTACOES',frmconsulta3,frmlogon.nomeusuario,'gridconsulta',gridconsulta,modulo_dados.dtsfdquerysql1);
        gridconsulta.DataSource:=modulo_dados.dtsfdquerysql14; gridconsulta.Refresh;
     end
   else if controle = 'COR_PRODUTO' then
      begin
         carrega_config('COR_PRODUTO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('COR_PRODUTO',frmconsulta3,frmlogon.nomeusuario,'gridconsulta',gridconsulta,modulo_dados.dtsfdquerysql1);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql1; gridconsulta.Refresh;
      end
   else if controle = 'CONSULTAS_IMEDIATAS' then
      begin
         carrega_config('CONSULTAS_IMEDIATAS',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('CONSULTAS_IMEDIATAS',frmconsulta3,frmlogon.nomeusuario,'gridconsulta',gridconsulta,modulo_dados.dtsfdquerysql17);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql7; gridconsulta.Refresh;
      end
   else if controle = 'DEPARTAMENTO_ESTACAO' then
      begin
         carrega_config('DEPARTAMENTO_ESTACAO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('DEPARTAMENTO_ESTACAO',frmconsulta3,frmlogon.nomeusuario,'gridconsulta',gridconsulta,modulo_dados.dtsfdquerysql6);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql8; gridconsulta.Refresh;
      end
   else if controle = 'ENTIDADE_ESTACAO' then
      begin
         carrega_config('ENTIDADE_ESTACAO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('ENTIDADE_ESTACAO',frmconsulta3,frmlogon.nomeusuario,'gridconsulta',gridconsulta,modulo_dados.dtsfdquerysql6);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'REPRESENTANTE_LEGAL' then
      begin
         carrega_config('REPRESENTANTE_LEGAL',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
//         configura_grid('ENTIDADE_ESTACAO',frmconsulta3,frmlogon.nomeusuario,'gridconsulta',gridconsulta,modulo_dados.dtsquerysql6);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'ENTCIDCOD' then
      begin
         carrega_config('ENTCIDCOD',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('ENTCIDCOD',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql9; gridconsulta.Refresh;
      end
   else if controle = 'LOCALIZACAO_FISICA_REDE' then
      begin
         carrega_config('LOCALIZACAO_FISICA_REDE',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('LOCALIZACAO_FISICA_REDE',frmconsulta3,frmlogon.nomeusuario,'gridconsulta',gridconsulta,modulo_dados.dtsfdquerysql6);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'USUARIO_ESTACAO' then
      begin
         carrega_config('USUARIO_ESTACAO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('USUARIO_ESTACAO',frmconsulta3,frmlogon.nomeusuario,'gridconsulta',gridconsulta,modulo_dados.dtsfdquerysql6);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'RELACIONA_DIOCESES' then
      begin
         carrega_config('RELACIONA_DIOCESES',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('RELACIONA_DIOCESES',frmconsulta3,frmlogon.nomeusuario,'gridconsulta',gridconsulta,modulo_dados.dtsfdquerysql5);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql5; gridconsulta.Refresh;
      end
   else if controle = 'TIPO_EVENTOS' then
      begin
         carrega_config('TIPO_EVENTOS',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('RELACIONA_DIOCESES',frmconsulta3,frmlogon.nomeusuario,'gridconsulta',gridconsulta,modulo_dados.dtsfdquerysql7);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql7; gridconsulta.Refresh;
      end
   else if controle = 'EVENTOS_IMPORTA' then
      begin
         carrega_config('EVENTOS_IMPORTA',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('EVENTOS_IMPORTA',frmconsulta3,frmlogon.nomeusuario,'gridconsulta',gridconsulta,modulo_dados.dtsfdquerysql7);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql7; gridconsulta.Refresh;
      end
   else if controle = 'CONTA_FINANCEIRASALDO' then
      begin
         carrega_config('CONTA_FINANCEIRASALDO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('CONTA_FINANCEIRASALDO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql11);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql; gridconsulta.Refresh;
      end
   else if controle = 'MOTIVO_OCORRENCIA_PADRAO' then
      begin
         carrega_config('MOTIVO_OCORRENCIA_PADRAO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('MOTIVO_OCORRENCIA_PADRAO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql11);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'BUSCAORIGEMPADRAOIM' then
      begin
         carrega_config('BUSCAORIGEMPADRAOIM',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('BUSCAORIGEMPADRAOIM',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql11);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'BUSCAORIGEMPADRAONI' then
      begin
         carrega_config('BUSCAORIGEMPADRAONI',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('BUSCAORIGEMPADRAONI',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql11);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'ENTIDADESOLICITANTEOCORRENCIA' then
      begin
         carrega_config('ENTIDADESOLICITANTEOCORRENCIA',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('ENTIDADESOLICITANTEOCORRENCIA',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql11);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'ORIGEMOCORRENCIA' then
      begin
         carrega_config('ORIGEMOCORRENCIA',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('ORIGEMOCORRENCIA',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql11);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'ENTIDADE-ORIGEM' then
      begin
         carrega_config('ENTIDADE-ORIGEM',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('ENTIDADE-ORIGEM',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql11);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'ENTIDADE-DESTINO' then
      begin
         carrega_config('ENTIDADE-DESTINO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('ENTIDADE-DESTINO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql11);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'CATEGORIA_APOLOSAVIC' then
      begin
         carrega_config('CATEGORIA_APOLOSAVIC',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('CATEGORIA_APOLOSAVIC',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql11);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'FUNCAO_APOLOSAVIC' then
      begin
         carrega_config('FUNCAO_APOLOSAVIC',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('FUNCAO_APOLOSAVIC',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql11);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'ORIGEM_SAVIC' then
      begin
         carrega_config('ORIGEM_SAVIC',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('ORIGEM_SAVIC',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql11);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'BUSCA_CONTATO_ENTIDADE' then
      begin
         carrega_config('BUSCA_CONTATO_ENTIDADE',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('BUSCA_CONTATO_ENTIDADE',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql11);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'BUSCA_CONTATO_ENTIDADE_APOLO' then
      begin
         carrega_config('BUSCA_CONTATO_ENTIDADE_APOLO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('BUSCA_CONTATO_ENTIDADE_APOLO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql11);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'TIPO_COBRANCA_ENTIDADE' then
      begin
         carrega_config('TIPO_COBRANCA_ENTIDADE',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('TIPO_COBRANCA_ENTIDADE',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql11);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'TIPO_COBRANCA_GEOAPOLO' then
      begin
         carrega_config('TIPO_COBRANCA_GEOAPOLO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('TIPO_COBRANCA_GEOAPOLO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql11);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'BANCO_ENTIDADE' then
      begin
         carrega_config('BANCO_ENTIDADE',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('BANCO_ENTIDADE',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql9);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql9; gridconsulta.Refresh;
      end
   else if controle = 'BANCO_ENTIDADE_GEOAPOLO' then
      begin
         carrega_config('BANCO_ENTIDADE_GEOAPOLO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('BANCO_ENTIDADE_GEOAPOLO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql9);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql9; gridconsulta.Refresh;
      end
   else if controle = 'AGENCIA_BCO_ENTIDADE' then
      begin
         carrega_config('AGENCIA_BCO_ENTIDADE',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('AGENCIA_BCO_ENTIDADE',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql9);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql9; gridconsulta.Refresh;
      end
   else if controle = 'AGENCIA_BCO_ENTIDADE_GEOAPOLO' then
      begin
         carrega_config('AGENCIA_BCO_ENTIDADE_GEOAPOLO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('AGENCIA_BCO_ENTIDADE_GEOAPOLO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql9);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql9; gridconsulta.Refresh;
      end
   else if controle = 'TIPOTRATENTIDADE' then
      begin
         carrega_config('TIPOTRATENTIDADE',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('TIPOTRATENTIDADE',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql20);
         if Assigned(frmconsulta3) and Assigned(frmconsulta3.lblprocurarpor) then
            frmconsulta3.lblprocurarpor.text := '%%';
         tecla:=vk_return;
         cbocampo.SetFocus;
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql20; gridconsulta.Refresh;
      end
   else if controle = 'TIPOTRATENTIDADE_APOLO' then
      begin
         carrega_config('TIPOTRATENTIDADE_APOLO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('TIPOTRATENTIDADE_APOLO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql9);
         if Assigned(frmconsulta3) and Assigned(frmconsulta3.lblprocurarpor) then
            frmconsulta3.lblprocurarpor.text := '%%';
         tecla:=vk_return;
         cbocampo.SetFocus;
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'DIOCESES_CNBB_ENTIDADE' then
      begin
         carrega_config('DIOCESES_CNBB_ENTIDADE',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('DIOCESES_CNBB_ENTIDADE',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql9);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql9; gridconsulta.Refresh;
      end
   else if controle = 'CATEGORIA_ENTIDADE' then
      begin
         carrega_config('CATEGORIA_ENTIDADE',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('CATEGORIA_ENTIDADE',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql17);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql17; gridconsulta.Refresh;
      end
   else if controle = 'CATEGORIA_ENTIDADE_ALVO' then
      begin
         carrega_config('CATEGORIA_ENTIDADE_ALVO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('CATEGORIA_ENTIDADE_ALVO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql11);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'CATEGORIA_IMPORTA_GRUPOORACAO' then
      begin
         carrega_config('CATEGORIA_IMPORTA_GRUPOORACAO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('CATEGORIA_IMPORTA_GRUPOORACAO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql6);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql5; gridconsulta.Refresh;
      end
   else if controle = 'DEPARTAMENTO_ESTACAO' then
      begin
         carrega_config('DEPARTAMENTO_ESTACAO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('DEPARTAMENTO_ESTACAO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql6);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql5; gridconsulta.Refresh;
      end
   else if controle = 'IMOBILIZADOCENTROCONTROLE' then
      begin
         carrega_config('IMOBILIZADOCENTROCONTROLE',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('IMOBILIZADOCENTROCONTROLE',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql6);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'IMOBILIZADOCLASSIFICACAO' then
      begin
         carrega_config('IMOBILIZADOCLASSIFICACAO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('IMOBILIZADOCLASSIFICACAO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql6);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'IMOBILIZADOLOCALIZACAOFISICA' then
      begin
         carrega_config('IMOBILIZADOLOCALIZACAOFISICA',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('IMOBILIZADOLOCALIZACAOFISICA',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql6);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'IMOBILIZADORESPONSAVELBEM' then
      begin
         carrega_config('IMOBILIZADORESPONSAVELBEM',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('IMOBILIZADORESPONSAVELBEM',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql6);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'IMOBILIZADOMARCA' then
      begin
         carrega_config('IMOBILIZADOMARCA',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('IMOBILIZADOMARCA',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql6);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'BUSCAMARCACADMARCA' then
      begin
         carrega_config('BUSCAMARCACADMARCA',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('BUSCAMARCACADMARCA',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql6);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'IMOBILIZADOCATEGORIABEM' then
      begin
         carrega_config('IMOBILIZADOCATEGORIABEM',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('IMOBILIZADOCATEGORIABEM',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql6);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'IMOBILIZADOSTATUS' then
      begin
         carrega_config('IMOBILIZADOSTATUS',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('IMOBILIZADOSTATUS',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql6);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'GEOCADCARTADOCREDITO' then
      begin
         carrega_config('GEOCADCARTADOCREDITO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('GEOCADCARTADOCREDITO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql6);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql6; gridconsulta.Refresh;
      end
   else if controle = 'BUSCAENTPADRAOOCORAPOLO' then
      begin
         carrega_config('BUSCAENTPADRAOOCORAPOLO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('BUSCAENTPADRAOOCORAPOLO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql9);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql9; gridconsulta.Refresh;
      end
   else if controle = 'BUSCAENTPADRAOOCORGEOAPOLO' then
      begin
         carrega_config('BUSCAENTPADRAOOCORGEOAPOLO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('BUSCAENTPADRAOOCORGEOAPOLO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql9);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql9; gridconsulta.Refresh;
      end
   else if controle = 'BUSCASOLOCORAPOLO' then
      begin
         carrega_config('BUSCASOLOCORAPOLO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('BUSCASOLOCORAPOLO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql9);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql9; gridconsulta.Refresh;
      end
   else if controle = 'BUSCASOLOCORGEOAPOLO' then
      begin
         carrega_config('BUSCASOLOCORGEOAPOLO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('BUSCASOLOCORGEOAPOLO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql9);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql9; gridconsulta.Refresh;
      end
   else if controle = 'TIPOCAMPANHA' then
      begin
         carrega_config('TIPOCAMPANHA',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('TIPOCAMPANHA',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql2);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql2; gridconsulta.Refresh;
      end
   else if controle = 'GEOTIPOCAMPANHA' then
      begin
         carrega_config('GEOTIPOCAMPANHA',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('GEOTIPOCAMPANHA',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql2);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql2; gridconsulta.Refresh;
      end
   else if controle = 'CATEGORIAPADRAOFORNECEDORES' then
      begin
         carrega_config('CATEGORIAPADRAOFORNECEDORES',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('CATEGORIAPADRAOFORNECEDORES',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql9);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql9; gridconsulta.Refresh;
      end
   else if controle = 'GEOLCTOCARTOES' then
      begin
         carrega_config('GEOLCTOCARTOES',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('GEOLCTOCARTOES',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql4);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql4; gridconsulta.Refresh;
      end
   else if controle = 'GEOCLASSELCTOCARTOES' then
      begin
         carrega_config('GEOCLASSELCTOCARTOES',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('GEOCLASSELCTOCARTOES',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql9);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql4; gridconsulta.Refresh;
      end
   else if controle = 'TIPOLANC_VENDASCUPONS' then
      begin
         carrega_config('TIPOLANC_VENDASCUPONS',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('TIPOLANC_VENDASCUPONS',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql7);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql7; gridconsulta.Refresh;
      end
   else if (controle = 'CAMPANHAS-EMAIL') AND (frmprincipal.baseparacampanha = 'S') then
     begin
         carrega_config('CAMPANHASEMAIL-APOLO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('CAMPANHASEMAIL-APOLO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql7);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql7; gridconsulta.Refresh;

     end
   else if (controle = 'CAMPANHAS-EMAIL') and (frmprincipal.baseparacampanha = 'N') then
      begin
         carrega_config('CAMPANHASEMAIL-GEOAPOLO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('CAMPANHASEMAIL-GEOAPOLO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql7);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql7; gridconsulta.Refresh;
      end
   else if (controle = 'ENTCIDCODCONTATO') and (frmprincipal.baseparacampanha= 'S') then
      begin
         carrega_config('ENTCIDCODCONTATO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('ENTCIDCODCONTATO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql7);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql7; gridconsulta.Refresh;
      end
   else if (controle = 'BUSCAENTIDADECONSUMIDORFINALAPOLO') and (frmprincipal.baseparacampanha='S') then
      begin
         carrega_config('BUSCAENTIDADECONSUMIDORFINALAPOLO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('BUSCAENTIDADECONSUMIDORFINALAPOLO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql7);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql7; gridconsulta.Refresh;
      end
   else if (controle = 'IMOBILIZADOBUSCABEM')  then
      begin
         carrega_config('IMOBILIZADOBUSCABEM',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('IMOBILIZADOBUSCABEM',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql7);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql7; gridconsulta.Refresh;
      end
   else if (controle = 'GEOBUSCACARTAOCREDITO') then
      begin
         carrega_config('GEOBUSCACARTAOCREDITO',frmconsulta3,cbocampo,cbordem,rdgcrescente,rdgdecrescente);
         configura_grid('GEOBUSCACARTAOCREDITO',frmconsulta3,'gridconsulta',frmlogon.nomeusuario,gridconsulta,modulo_dados.dtsfdquerysql4);
         gridconsulta.DataSource:=modulo_dados.dtsfdquerysql4; gridconsulta.Refresh;
      end;
   gridconsulta.Refresh;
   configura_statusbar('1');
end;

procedure TfrmConsulta3.gridconsultaKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
   if key = vk_f3 then
      gridconsulta.OnDblClick(self);
   if (key = VK_INSERT) and (controle = 'COR_PRODUTO') then
      begin
        application.CreateForm(tfrmcadcores, frmcadcores);
        frmcadcores.ShowModal;
      end;
end;

procedure TfrmConsulta3.rdgcrescenteClick(Sender: TObject);
begin
   wordem_campo := 'C';
end;

procedure TfrmConsulta3.rdgdecrescenteClick(Sender: TObject);
begin
   wordem_campo := 'D';
end;

procedure TfrmConsulta3.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
   action:=cafree;
end;

procedure TfrmConsulta3.cbocampoChange(Sender: TObject);
begin
   cbordem.ItemIndex := cbocampo.ItemIndex ;
   cbordem.Refresh;
end;

procedure TfrmConsulta3.gravaropcoesClick(Sender: TObject);
begin
   if controle = 'CIDADE_CIDADE' then
      begin
         grava_configuracoes_grids(frmconsulta3,'CIDADE_CIDADE',gridconsulta,'gridconsulta',frmlogon.nomeusuario,modulo_dados.dtsfdquerysql8);
         grava_config_telabusca('CIDADE_CIDADE',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'NOTA_FISCAL_PVAGRUP' then
      begin
         grava_configuracoes_grids(frmconsulta3,'NOTA_FISCAL_PVAGRUP',gridconsulta,'gridconsulta',frmlogon.nomeusuario, modulo_dados.dtsfdquerysql9);
         grava_config_telabusca('NOTA_FISCAL_PVAGRUP',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'CLIENTES' then
      begin
         grava_configuracoes_grids(frmconsulta3,'CLIENTES',gridconsulta,'gridconsulta',frmlogon.nomeusuario, modulo_dados.dtsfdquerysql9);
         grava_config_telabusca('CLIENTES',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'EMPRESA_FILIAL' then
      begin
         grava_configuracoes_grids(frmconsulta3,'EMPRESA_FILIAL',gridconsulta,'gridconsulta',frmlogon.nomeusuario, modulo_dados.dtsfdquerysql8);
         grava_config_telabusca('EMPRESA_FILIAL',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'OS_SEM_CMUTILIZADO' then
      begin
         grava_configuracoes_grids(frmconsulta3,'OS_SEM_CMUTILIZADO',gridconsulta,'gridconsulta',frmlogon.nomeusuario,modulo_dados.dtsfdquerysql13);
         grava_config_telabusca('OS_SEM_CMUTILIZADO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'CONTA_FINANCEIRASALDO' then
      begin
         grava_configuracoes_grids(frmconsulta3,'CONTA_FINANCEIRASALDO',gridconsulta,'gridconsulta',frmlogon.nomeusuario, modulo_dados.dtsfdquerysql11);
         grava_config_telabusca('CONTA_FINANCEIRASALDO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'SITCODESTRORIG' then
      begin
         grava_configuracoes_grids(frmconsulta3,'SITCODESTRORIG',gridconsulta,'gridconsulta',frmlogon.nomeusuario, modulo_dados.dtsfdquerysql4);
         grava_config_telabusca('SITCODESTRORIG',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'SITCODESTRDESTINO' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'SITCODESTRDESTINO',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('SITCODESTRDESTINO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'CATEGORIA_SITUACAO_TITULOS' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'CATEGORIA_SITUACAO_TITULOS',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('CATEGORIA_SITUACAO_TITULOS',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'ATIVIDADE_ECONOMICAG' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'ATIVIDADE_ECONOMICAG',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('ATIVIDADE_ECONOMICAG',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'ATIVIDADE_ECONOMICA_APOLO' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'ATIVIDADE_ECONOMICA_APOLO',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('ATIVIDADE_ECONOMICA_APOLO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'TIPOLOGRADOURO_ENDENTREGA' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'TIPOLOGRADOURO_ENDENTREGA',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('TIPOLOGRADOURO_ENDENTREGA',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'TIPOLOGRADOURO_MESCLA' then
      begin
  //       grava_configuracoes_grids(frmconsulta3,'TIPOLOGRADOURO_MESCLA',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('TIPOLOGRADOURO_MESCLA',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'CIDADES_COBRANCA' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'CIDADES_COBRANCA',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('CIDADES_COBRANCA',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'CIDADES_ENTREGA' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'CIDADES_ENTREGA',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('CIDADES_ENTREGA',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'TIPOTRATENTIDADE' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'TIPOTRATENTIDADE',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('TIPOTRATENTIDADE',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'TIPOTRATENTIDADE_APOLO' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'TIPOTRATENTIDADE_APOLO',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('TIPOTRATENTIDADE_APOLO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'TIPOLOGRADOURO' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'TIPOLOGRADOURO',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('TIPOLOGRADOURO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'ORIGEM_ENTIDADE' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'ORIGEM_ENTIDADE',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('ORIGEM_ENTIDADE',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'ORIGEM_ENTIDADE_APOLO' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'ORIGEM_ENTIDADE_APOLO',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('ORIGEM_ENTIDADE_APOLO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'REGIAO_ENTIDADE' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'REGIAO_ENTIDADE',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('REGIAO_ENTIDADE',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'REGIAO_ENTIDADE_APOLO' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'REGIAO_ENTIDADE_APOLO',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('REGIAO_ENTIDADE_APOLO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'BUSCA_CONTATO_ENTIDADE' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'BUSCA_CONTATO_ENTIDADE',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('BUSCA_CONTATO_ENTIDADE',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'BUSCA_CONTATO_ENTIDADE_APOLO' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'BUSCA_CONTATO_ENTIDADE_APOLO',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('BUSCA_CONTATO_ENTIDADE_APOLO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'TIPOLOGRADOURO_ENDCOBRANCA' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'TIPOLOGRADOURO_ENDCOBRANCA',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('TIPOLOGRADOURO_ENDCOBRANCA',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'ENTCIDCOD' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'ENTCIDCOD',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('ENTCIDCOD',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'GRUPO_PRODUTO' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'GRUPO_PRODUTO',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('GRUPO_PRODUTO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'MARCA_PRODUTO' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'MARCA_PRODUTO',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('MARCA_PRODUTO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'COR_PRODUTO' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'COR_PRODUTO',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('COR_PRODUTO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'NATOPPVSPVP' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'NATOPPVSPVP',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('NATOPPVSPVP',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'CONTA_FINANCEIRASALDO' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'CONTA_FINANCEIRASALDO',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('CONTA_FINANCEIRASALDO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'CONSULTAS_IMEDIATAS' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'CONSULTAS_IMEDIATAS',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('CONSULTAS_IMEDIATAS',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'USUARIO_ESTACAO' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'USUARIO_ESTACAO',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('USUARIO_ESTACAO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'RELACIONA_DIOCESES' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'RELACIONA_DIOCESES',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('RELACIONA_DIOCESES',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'TIPO_EVENTOS' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'TIPO_EVENTOS',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('TIPO_EVENTOS',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'EVENTOS_IMPORTA' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'EVENTOS_IMPORTA',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('EVENTOS_IMPORTA',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'MOTIVO_OCORRENCIA_PADRAO' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'MOTIVO_OCORRENCIA_PADRAO',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('MOTIVO_OCORRENCIA_PADRAO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'BUSCAORIGEMPADRAOIM' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'BUSCAORIGEMPADRAO',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('BUSCAORIGEMPADRAO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'BUSCAORIGEMPADRAONI' then
      begin
         grava_config_telabusca('BUSCAORIGEMPADRAONI',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'ENTIDADESOLICITANTEOCORRENCIA' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'ENTIDADESOLICITANTEOCORRENCIA',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('ENTIDADESOLICITANTEOCORRENCIA',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'ORIGEMOCORRENCIA' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'ORIGEMOCORRENCIA',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('ORIGEMOCORRENCIA',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'ENTIDADE-ORIGEM' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'ENTIDADE-ORIGEM',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('ENTIDADE-ORIGEM',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'ENTIDADE-DESTINO' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'ENTIDADE-DESTINO',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('ENTIDADE-DESTINO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'CATEGORIA_APOLOSAVIC' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'CATEGORIA_APOLOSAVIC',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('CATEGORIA_APOLOSAVIC',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'FUNCAO_APOLOSAVIC' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'FUNCAO_APOLOSAVIC',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('FUNCAO_APOLOSAVIC',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'ORIGEM_SAVIC' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'ORIGEM_SAVIC',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('ORIGEM_SAVIC',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'TIPO_COBRANCA_ENTIDADE' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'TIPO_COBRANCA_ENTIDADE',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('TIPO_COBRANCA_ENTIDADE',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'TIPO_COBRANCA_GEOAPOLO' then
      begin
         grava_configuracoes_grids(frmconsulta3,'TIPO_COBRANCA_GEOAPOLO',gridconsulta,'gridconsulta',frmlogon.lblusuario.Text,modulo_dados.dtsfdquerysql9);
         grava_config_telabusca('TIPO_COBRANCA_GEOAPOLO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'BANCO_ENTIDADE' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'BANCO_ENTIDADE',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('BANCO_ENTIDADE',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'BANCO_ENTIDADE_GEOAPOLO' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'BANCO_ENTIDADE_GEOAPOLO',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('BANCO_ENTIDADE_GEOAPOLO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'AGENCIA_BCO_ENTIDADE' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'AGENCIA_BCO_ENTIDADE',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('AGENCIA_BCO_ENTIDADE',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'AGENCIA_BCO_ENTIDADE_GEOAPOLO' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'AGENCIA_BCO_ENTIDADE_GEOAPOLO',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('AGENCIA_BCO_ENTIDADE_GEOAPOLO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'CATEGORIA_ENTIDADE' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'CATEGORIA_ENTIDADE',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('CATEGORIA_ENTIDADE',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'CATEGORIA_ENTIDADE_ALVO' then
      begin
//         grava_configuracoes_grids(frmconsulta3,'CATEGORIA_ENTIDADE_ALVO',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('CATEGORIA_ENTIDADE_ALVO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'DIOCESES_CNBB_ENTIDADE' then
      begin
         //grava_configuracoes_grids(frmconsulta3,'DIOCESES_CNBB_ENTIDADE',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('DIOCESES_CNBB_ENTIDADE',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
   else if controle = 'CATEGORIA_IMPORTA_GRUPOORACAO' then
      begin
  //       grava_configuracoes_grids(frmconsulta3,'CATEGORIA_IMPORTA_GRUPOORACAO',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('CATEGORIA_IMPORTA_GRUPOORACAO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end
  else if controle = 'DEPARTAMENTO_ESTACAO' then
     begin
        grava_config_telabusca('DEPARTAMENTO_ESTACAO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'IMOBILIZADOCENTROCONTROLE' then
     begin
        grava_config_telabusca('IMOBILIZADOCENTROCONTROLE',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'IMOBILIZADOCLASSIFICACAO' then
     begin
        grava_config_telabusca('IMOBILIZADOCLASSIFICACAO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'IMOBILIZADOLOCALIZACAOFISICA' then
     begin
        grava_config_telabusca('IMOBILIZADOLOCALIZACAOFISICA',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'IMOBILIZADORESPONSAVELBEM' then
     begin
        grava_config_telabusca('IMOBILIZADORESPONSAVELBEM',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'IMOBILIZADOMARCA' then
     begin
        grava_config_telabusca('IMOBILIZADOMARCA',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'IMOBILIZADOBUSCABEM' then
     begin
       grava_config_telabusca('IMOBILIZADOBUSCABEM',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'BUSCAMARCACADMARCA' then
     begin
        grava_config_telabusca('BUSCAMARCACADMARCA',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'IMOBILIZADOSTATUS' then
     begin
        grava_config_telabusca('IMOBILIZADOSTATUS',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'GEOCADCARTADOCREDITO' then
     begin
        grava_config_telabusca('GEOCADCARTADOCREDITO',cbocampo.Text, cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'BUSCAENTPADRAOOCORGEOAPOLO' then
     begin
        grava_config_telabusca('BUSCAENTPADRAOOCORGEOAPOLO',cbocampo.Text, cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'BUSCAENTPADRAOOCORAPOLO' then
     begin
        grava_config_telabusca('BUSCAENTPADRAOOCORAPOLO',cbocampo.Text, cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'TIPOCAMPANHA' then
     begin
        grava_config_telabusca('TIPOCAMPANHA',cbocampo.Text, cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'GEOTIPOCAMPANHA' then
     begin
        grava_config_telabusca('GEOTIPOCAMPANHA',cbocampo.Text, cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'CATEGORIAPADRAOFORNECEDORES' then
     begin
        grava_config_telabusca('CATEGORIAPADRAOFORNECEDORES',cbocampo.Text, cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'GEOLCTOCARTOES' then
     begin
        grava_config_telabusca('GEOLCTOCARTOES',cbocampo.Text, cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'GEOCLASSELCTOCARTOES' then
     begin
        grava_config_telabusca('GEOCLASSELCTOCARTOES',cbocampo.Text, cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'TIPOLANC_VENDASCUPONS' then
     begin
        grava_config_telabusca('TIPOLANC_VENDASCUPONS',cbocampo.Text, cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'CAMPANHASEMAIL-APOLO' then
     begin
        grava_config_telabusca('CAMPANHASEMAIL-APOLO',cbocampo.Text, cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'CAMPANHASEMAIL-GEOAPOLO' then
     begin
        grava_config_telabusca('CAMPANHASEMAIL-GEOAPOLO',cbocampo.Text, cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'ENTCIDCODCONTATO' then
     begin
        grava_config_telabusca('ENTCIDCODCONTATO',cbocampo.Text, cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'BUSCAENTIDADECONSUMIDORFINALAPOLO' then
     begin
        grava_config_telabusca('BUSCAENTIDADECONSUMIDORFINALAPOLO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
     end
  else if controle = 'GEOBUSCACARTAOCREDITO' then
     begin
        grava_configuracoes_grids(frmconsulta3,'GEOBUSCACARTAOCREDITO',gridconsulta,'gridconsulta',frmlogon.nomeusuario,modulo_dados.dtsfdquerysql4);
        grava_config_telabusca('GEOBUSCACARTAOCREDITO',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
     end;
 {  else
      begin
         grava_configuracoes_grids(frmconsulta3,'GEOCONSULTA3ENTIDADE',gridconsulta,'gridconsulta',frmlogon.nomeusuario);
         grava_config_telabusca('GEOCONSULTA3ENTIDADE',cbocampo.Text,cbordem.Text,'A',frmconsulta3);
      end; }
end;

procedure TfrmConsulta3.gridconsultaDblClick(Sender: TObject);
begin
   with modulo_dados do
   begin
      if controle = 'EMPRESA_FILIAL' then
       begin
       end
     else if controle = 'CLIENTES' then
        begin
        end
     else if controle = 'CIDADE_CIDADE' then
        begin
           with frmdistritocidades do
           begin
              lblcidadecidade.Text:= fdquerysql8.fieldbyname('cidcod').asstring;
              lblnomecidade.Caption:= fdquerysql8.fieldbyname('cidnomecomp').asstring;
              lblprocurarpor.clear;
              frmconsulta3.close;
           end;
        end
     else if controle = 'NOTA_FISCAL_PVAGRUP' then
        begin
        end
     else if controle = 'OS_SEM_CMUTILIZADO' then
        begin
        end
     else if controle = 'SITCODESTRORIG' then
        begin
        end
     else if controle = 'SITCODESTRDESTINO' then
        begin
{            with frmalterasitcod do
            begin
               lblsitcodestrdestino.Text := querysql4.FieldByName('sitcodestr').AsString;
               lblnomesituacaodestino.Caption := querysql4.FieldByName('sitnome').AsString;
               lblsitcodestrdestino.Refresh; lblnomesituacaodestino.Refresh;
               lblsitcodestrdestino.SetFocus;
               lblprocurarpor.clear;
               frmconsulta3.close;
            end;}
        end
     else if controle = 'CATEGORIA_SITUACAO_TITULOS' then
        begin
          { with frmalterasitcod do
           begin
              lblcategcodestr.Text := querysql4.FieldByName('categcodestr').AsString;
              lblcategnome.Caption := querysql4.FieldByName('categnome').AsString;
              lblcategcodestr.Refresh; lblcategnome.Refresh;
              lblcategcodestr.SetFocus;
              lblprocurarpor.clear;
              frmconsulta3.close;
           end;  }
        end
     else if controle = 'CONTA_FINANCEIRASALDO' then
        begin
           with frmdebxcredfin do
           begin
              lblcontafincod.text := fdquerysql11.fieldbyname('contafincod').asstring;
              lblnomecontafinanceira.Caption := fdquerysql11.FieldByName('contafinnome').AsString;
              lblprocurarpor.clear;
              frmconsulta3.close;
           end;
        end
     else if controle = 'USUARIO_DEPARTAMENTO' then
        begin
           with frmusuarios do
           begin
              lblcodigodepto.Text := fdquerysql4.fieldbyname('codigo_departamento').asstring;
              lblnomedepartamento.caption:= fdquerysql4.fieldbyname('nome_departamento').asstring;
              lblprocurarpor.clear;
              frmconsulta3.close;
           end;
        end
     else if ((controle = 'CATEGORIA_ENTIDADE') or (controle = 'CATEGORIA_ENTIDADE_ALVO')) then
        begin
           with frmcadentidade do
           begin
              if ((frmentidades.integraentidadeapolo = 'Não Integra') or (frmentidades.integraentidadeapolo = 'Mescla') AND (frmentidades.cbobuscabanco.text = 'GeoApolo')) then
                 begin
                    lblcategcodestr.text := fdquerysql19.fieldbyname('geocategcodestr').asstring;
                    lblcategnome.Caption:= fdquerysql19.fieldbyname('geocategnome').asstring;
                 end
              else if ((frmentidades.integraentidadeapolo = 'Integra') or (frmentidades.integraentidadeapolo = 'Mescla') AND (frmentidades.cbobuscabanco.text = 'Alvo')) then
                 begin
                    lblcategcodestr.text := fdquerysql19.fieldbyname('categcodestr').asstring;
                    lblcategnome.Caption:= fdquerysql19.fieldbyname('categnome').asstring;
                 end;
              lblprocurarpor.clear;
              mostra_entidade_categoria(lblentcod.Text,frmentidades.integraentidadeapolo);
              frmconsulta3.close;
           end;
        end
     else if controle = 'TIPOLOGRADOURO_ENDENTREGA' then
        begin
           with frmcadentidade do
           begin
              lbllogradouroentrega.Text := fdquerysql1.fieldbyname('tipologradabrev').asstring;
              lblprocurarpor.clear; frmConsulta3.close;
           end;
        end
     else if controle = 'TIPOLOGRADOURO_ENDCOBRANCA' then
        begin
           with frmcadentidade, modulo_dados do
           begin
              lbllogradourocobranca.Text := fdquerysql9.fieldbyname('tipologradabrev').asstring;
              lbllogradourocobranca.Refresh; lblprocurarpor.clear;
              frmconsulta3.Close;
           end;
        end
     else if controle = 'TIPOLOGRADOURO_MESCLA' then
        begin
           with frmcadentidade, modulo_dados do
           begin
              lbllogradouro.Text:= fdquerysql9.FieldByName('tipologradabrev').AsString;
              lbllogradouro.Refresh; lblprocurarpor.Clear;
              frmconsulta3.close;
           end;
        end
     else if controle = 'CIDADES_COBRANCA' then
        begin
            with frmcadentidade do
            begin
               lblcidadecobranca.Text := fdquerysql19.fieldbyname('geocidnomecomp').asstring;
               lblestadocob.text := fdquerysql19.fieldbyname('ufsigla').asstring;
               cidcodcob:=fdquerysql1.FieldByName('geocidcod').AsString;
               lblprocurarpor.Clear;
               frmconsulta3.Close;
            end
        end
     else if controle = 'CIDADES_ENTREGA' then
        begin
            with frmcadentidade do
            begin
               lblcidadeentrega.Text := fdquerysql19.FieldByName('cidnomecomp').AsString;
               lblestado_entrega.Text:= fdquerysql19.FieldByName('ufsigla').AsString;
               cidcod:=fdquerysql1.FieldByName('geocidcod').AsString;
               lblprocurarpor.clear;
               frmconsulta3.close;
            end;
        end
     else if controle = 'ATIVIDADE_ECONOMICAG' then
        begin
            with frmcadentidade do
            begin
               lblativecodestr.Text := fdquerysql19.fieldbyname('ativeconcodestr').asstring;
               lblnomeatividade_economica.Caption:= fdquerysql19.fieldbyname('ativeconnome').asstring;
               lblprocurarpor.Clear;
               frmconsulta3.close;
            end;
        end
     else if controle = 'ATIVIDADE_ECONOMICA_APOLO' then
        begin
           with frmcadentidade do
           begin
               lblativecodestr.Text := fdquerysql19.fieldbyname('ativeconcodestr').asstring;
               lblnomeatividade_economica.Caption:= fdquerysql19.fieldbyname('ativeconnome').asstring;
               lblprocurarpor.Clear;
               frmconsulta3.close;
           end
        end
     else if controle = 'ORIGEM_ENTIDADE' then
        begin
         with frmcadentidade do
         begin
            lblorigcodestr.Text := fdquerysql9.FieldByName('geo_origcodestr').AsString;
            lblnomeorigem.Caption := fdquerysql9.FieldByName('geo_orignome').AsString;
            lblprocurarpor.Clear;
            frmconsulta3.Close;
        end;
      end
     else if controle = 'ORIGEM_ENTIDADE_APOLO' then
        begin
           with frmcadentidade,modulo_dados do
           begin
              lblorigcodestr.text:=fdquerysql9.FieldByName('origcodestr').AsString;
              lblnomeorigem.Caption := fdquerysql9.FieldByName('orignome').AsString;
              lblprocurarpor.Clear;
              frmconsulta3.Close;
           end;
        end
     else if controle = 'REGIAO_ENTIDADE' then
        begin
           with frmcadentidade do
           begin
              lblregiao.text:= fdquerysql9.fieldbyname('georegcodestr').asstring;
              lblnomeregiao.Caption := fdquerysql9.fieldbyname('geo_regnome').asstring;
              lblregiao.Refresh; lblprocurarpor.clear;
              frmconsulta3.close;
           end;
        end
     else if controle = 'REGIAO_ENTIDADE_APOLO' then
        begin
           with frmcadentidade do
           begin
              lblregiao.text:=fdquerysql9.FieldByName('regcodestr').AsString;
              lblnomeregiao.caption := fdquerysql9.FieldByName('regnome').AsString;
              lblregiao.Refresh; lblprocurarpor.Clear;
              frmconsulta3.Close;
           end;
        end
     else if controle = 'BUSCA_CONTATO_ENTIDADE' then
        begin
           with frmcadentidade do
           begin
              cin3.ActivePageIndex:=0; cin3.Refresh;
              lblentcontatocod.Text := fdquerysql13.FieldByName('geoentcod').AsString;
              lbltipotratamento.Caption := fdquerysql13.fieldbyname('geotipotratcod').asstring;
              lblentcontatonome.Caption:= fdquerysql13.FieldByName('geoentnome').AsString;
              mskcepcontato.Text := fdquerysql13.FieldByName('geoentcep').AsString;

              buscanacombo(fdquerysql13.FieldByName('geoenttipolograd').AsString,frmcadentidade,cbologradourocontato);
              lblenderecocontato.Text := fdquerysql13.FieldByName('geoentender').AsString;
              lblnumerocontato.Text := fdquerysql13.FieldByName('geoenderno').AsString;
              lblcomplendercontato.Text := fdquerysql13.FieldByName('geoentendercomp').AsString;
              lblbairrocontato.Text := fdquerysql13.FieldByName('geoentbair').AsString;
              lblcargocontato.Text := fdquerysql13.FieldByName('geocargocodestr').AsString;
              lblcargocontatonome.caption:= fdquerysql13.fieldbyname('geocargonome').asstring;
              //mostra_entidade_contatoweb(querysql13.FieldByName('geoentcod').AsString,frmentidades.integraentidadeapolo);
              lblentcontatocod.SetFocus;
              frmconsulta3.close;
           end;
        end
     else if controle = 'BUSCA_CONTATO_ENTIDADE_APOLO' then
        begin
           with frmcadentidade do
           begin
              cin3.ActivePageIndex:=0; cin3.Refresh;
              lblentcontatocod.Text := fdquerysql13.FieldByName('entcod').AsString;
              lbltipotratamento.Caption := fdquerysql13.fieldbyname('tipotratcod').asstring;
              lblentcontatonome.Caption:= fdquerysql13.FieldByName('entnome').AsString;
              mskcepcontato.Text := fdquerysql13.FieldByName('entcep').AsString;
              cbologradourocontato.Items.Add(fdquerysql13.FieldByName('entlograd').AsString);
              buscanacombo(fdquerysql13.FieldByName('entlograd').AsString,frmcadentidade,cbologradourocontato);
              lblenderecocontato.Text := fdquerysql13.FieldByName('entender').AsString;
              lblnumerocontato.Text := fdquerysql13.FieldByName('entenderno').AsString;
              lblcomplendercontato.Text := fdquerysql13.FieldByName('entendercomp').AsString;
              lblbairrocontato.Text := fdquerysql13.FieldByName('entbair').AsString;

              lblcargocontato.Text := fdquerysql13.FieldByName('cargocodestr').AsString;
              lblcargocontatonome.caption:= fdquerysql13.fieldbyname('cargonome').asstring;
              lblemailcontato.Text:=  fdquerysql13.FieldByName('entwebemail').AsString;
              lblentcontatocod.SetFocus;
              frmconsulta3.close;
           end;
        end
     else if controle = 'TIPOTRATENTIDADE' then
        begin
           if Assigned(modulo_dados.fdquerysql20) and modulo_dados.fdquerysql20.Active and Assigned(frmcadentidade.lbltipotrat) then
          begin
            frmcadentidade.lbltipotrat.Text := modulo_dados.fdquerysql20.FieldByName('abreviatura').AsString;

            ModalResult := mrOk;
          end;
        end
     else if controle = 'TIPOTRATENTIDADE_APOLO' then
        begin
           with frmcadentidade do
           begin
              lbltipotrat.text := fdquerysql9.fieldbyname('tipotratcod').asstring;
              lbltipotrat.refresh;
              ModalResult := mrOk;
              frmconsulta3.close;
           end;
        end
     else if controle = 'TIPOLOGRADOURO' then
        begin
           with frmcadentidade do
           begin
              lbllogradouro.text := fdquerysql9.fieldbyname('tipologradabrev').asstring;
              lbltipotrat.refresh;
              frmconsulta3.close;
           end;
        end
     else if controle = 'GRUPO_PRODUTO' then
        begin
            {with frmprodutos do
            begin
               lblcodigogrupo.Text := querysql1.fieldbyname('grupocod').asstring;
               lblnomegrupo.text := querysql1.fieldbyname('nome_grupo').AsString;
               lblcodgrupoestr.Text := querysql1.FieldByName('codigo_estruturado').AsString;
               controlegrupo:='ALTERAÇÃO';
               mostra_produtos('E');
               frmprodutos.Refresh;
               frmconsulta3.Close;
            end;}
        end
     else if controle = 'MARCA_PRODUTO' then
        begin
{           with frmprodutos do
           begin
             lblcodmarca.Text := querysql2.FieldByName('codigo_marca').AsString;
             lblnomemarca.Caption:= querysql2.FieldByName('descricao_marca').AsString;
             frmprodutos.Refresh;
             frmconsulta3.Close;
           end;}
        end
     else if controle = 'COR_PRODUTO' then
        begin
{           with frmprodutos do
           begin
             lblcor.Text := querysql5.FieldByName('codigo_cor').AsString;
             lbldescricaocor.Caption:= querysql5.FieldByName('descricao_cor').AsString;
             lblcodprodestruturado.SetFocus;
             frmprodutos.Refresh;
             frmconsulta3.Close;
           end;}
        end
     else if controle = 'CONSULTAS_IMEDIATAS' then
        begin
           with frmcadconsulta do
           begin
              lblcodconsulta.text :=fdquerysql7.fieldbyname('codigo_consulta').asstring;
              lbldescricao.text := fdquerysql7.fieldbyname('descricao_consulta').asstring;
              if fdquerysql7.FieldByName('tipo_consulta').AsString = 'I' then
                 buscanacombo('IMEDIATAS',frmcadconsulta, cbotipoconsulta)
              else
                 buscanacombo('CAMPANHA',frmcadconsulta,cbotipoconsulta);
              buscanacombo(fdquerysql7.FieldByName('banco_consulta').AsString,frmcadconsulta,cbobancodaconsulta);
              cbotipoconsulta.Refresh;
              memosql.Lines.Text := fdquerysql7.FieldByName('sentenca_sql').AsString;
              setcursorsql('');
              frmcadconsulta.Refresh; frmConsulta3.close;
           end;
        end
     else if controle = 'DEPARTAMENTO_ESTACAO' then
        begin
           with frmestacoes do
           begin
              lblcodigodepartamento.text := fdquerysql6.fieldbyname('codigo_departamento').asstring;
              buscanacombo(fdquerysql6.fieldbyname('nome_departamento').asstring,frmestacoes,cbodepartamentos);
              lblcodigodepartamento.refresh; cbodepartamentos.Refresh;
              frmconsulta3.close
           end;
        end
     else if controle = 'ENTCIDCOD' then
        begin
           with frmcadentidade do
           begin
              lblcidcod.Text := fdquerysql9.FieldByName('geocidcod').AsString;
              lblnomecidade.Caption := fdquerysql9.FieldByName('cidnomecomp').AsString;
              lbluf.Text := fdquerysql9.FieldByName('ufsigla').AsString;
              lblcidcod.Refresh; lblnomecidade.Refresh; lbluf.Refresh;
              frmconsulta3.Close;
           end;
        end
    else if controle = 'USUARIO_ESTACAO' then
        begin
           with frmestacoes do
           begin
              lblcodigousuario.Text := fdquerysql6.FieldByName('codigo_usuario').AsString;
              lblnomeusuario.Text:= fdquerysql6.FieldByName('nome_completo').AsString;
              lblcodigousuario.refresh; lblnomeusuario.refresh;
              frmconsulta3.Close;
           end;
        end
     else if controle = 'ENTIDADE_ESTACAO' then
        begin
           with frmestacoes do
           begin
              lblentcod.text := fdquerysql6.fieldbyname('geoentcod').AsString;
              edtentnome.text:= fdquerysql6.FieldByName('geoentnome').AsString;
              lblentcod.refresh; edtentnome.refresh;
              frmconsulta3.close;
           end;
        end
     else if controle = 'LOCALIZACAO_FISICA_ESTACAO' then
        begin
           with frmestacoes do
           begin
              lbllocalizacao.text := fdquerysql6.fieldbyname('codigo_localizacao').asstring;
              edtlocalizacao.Text:= fdquerysql6.fieldbyname('localizacao').asstring;
              lbllocalizacao.Refresh; edtlocalizacao.Refresh;
              frmconsulta3.close;
           end;
        end
     else if controle = 'LOCALIZACAO_FISICA_REDE' then
        begin
          with frmestacoes do
          begin
            lblcodlocalizacaofisica.Text := fdquerysql6.FieldByName('codigo_localizacao').AsString;
            edtdescricaolocalizacao.Text := fdquerysql6.FieldByName('localizacao').AsString;
            lblcodlocalizacaofisica.Refresh; edtdescricaolocalizacao.Refresh;
            frmconsulta3.Close;
          end;
        end
     else if controle = 'MARCAS_ESTACOES' then
        begin
           with frmestacoes do
           begin
              lblcodmarca.text := fdquerysql.FieldByName('codigo_marca').AsString;
              lblmarca.Text := fdquerysql.FieldByName('descricao_marca').AsString;
              frmconsulta3.Close;
           end;
        end
     else if controle = 'RELACIONA_DIOCESES' then
        begin
           with frmrelacionaentidadediocese do
           begin
              lbldioceseid.Text := fdquerysql5.FieldByName('id').AsString;
              lbldiocesenome.Caption := fdquerysql5.FieldByName('nome').AsString;
              lblcidadediocese.Caption := lblcidcod.Caption+'/'+fdquerysql5.FieldByName('usersigla').AsString;
              lbldioceseid.Refresh; lbldiocesenome.Refresh;
              frmconsulta3.Close;
           end;
        end
     else if controle = 'OCUPACAO' then
        begin
           // Apenas sinaliza confirmação — o caller (spbuscaocupacaoClick)
           // lê os campos de fdquerysql9 após o ShowModal retornar.
           // Isso evita:
           //   - Access Violation por ler fdquerysql (dataset errado)
           //   - Access Violation por chamar frmconsulta3.Close
           //     (ponteiro global ≠ variável local frm criada no caller)
           ModalResult := mrOk;
        end
     else if controle = 'OCUPACAO_CONTATO' then
        begin
           ModalResult := mrOk;
        end
      else if controle = 'CONTA_FINANCEIRASALDO' then
        begin
           with frmdebxcredfin do
           begin
              lblcontafincod.Text := fdquerysql11.FieldByName('contafincod').AsString;
              lblnomecontafinanceira.caption := fdquerysql11.fieldbyname('contafinnome').asstring;
              lblnomecontafinanceira.Refresh;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end
        end
     else if controle = 'TIPO_EVENTOS' then
        begin
            with frmcadeventos do
            begin
               lbltipoevento.Text := fdquerysql7.FieldByName('tipoeventcod').AsString;
               lbltipoevento_descricao.Caption := fdquerysql7.FieldByName('descricao_tipoevento').AsString;
               lbltipoevento_descricao.Refresh;
               lblprocurarpor.Clear; frmconsulta3.Close;
            end;
        end
     else if controle = 'EVENTOS_IMPORTA' then
        begin
        end
     else if controle = 'MOTIVO_OCORRENCIA_PADRAO' then
        begin
           with frmconfig do
           begin
              lblmotocorcodestr.text:= fdquerysql6.FieldByName('motocorcodestr').AsString;
              lbldescricaomotivoocor.Caption := fdquerysql6.FieldByName('motocordescr').AsString;
              lbldescricaomotivoocor.Refresh  ;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end;
        end
     else if controle = 'BUSCAORIGEMPADRAOIM' then
          begin
             with frmconfig do
             begin
                lblorigcodestrpadrao.text:= fdquerysql6.FieldByName('origcodestr').AsString;
                lblorigpadraodescr.Caption:= fdquerysql6.FieldByName('orignome').AsString;
                lblorigpadraodescr.Refresh;
                lblprocurarpor.Clear; frmconsulta3.Close;
             end;
          end
     else if controle = 'BUSCAORIGEMPADRAONI' then
        begin
           with frmconfig do
           begin
              lblorigcodestrpadrao.text:= fdquerysql6.FieldByName('geo_origcodestr').AsString;
              lblorigpadraodescr.Caption:= fdquerysql6.FieldByName('geo_orignome').AsString;
              lblorigpadraodescr.Refresh;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end;
        end
     else if controle = 'ENTIDADESOLICITANTEOCORRENCIA' then
        begin
           with frmocorrencia do
           begin
              lblsolicitante.text:= fdquerysql.FieldByName('entcod').AsString;
              lblsolicitantenome.Caption := fdquerysql.FieldByName('entnome').AsString;
              lblsolicitante.Refresh;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end;
        end
     else if controle = 'ORIGEMOCORRENCIA' then
        begin
           with frmocorrencia do
           begin
              lblorigcodestr.text:= fdquerysql.FieldByName('origcodestr').AsString;
              lblorigdescr.Caption := fdquerysql.FieldByName('orignome').AsString;
              lblorigcodestr.Refresh;
              lblprocurarpor.Clear; frmconsulta3.close;
           end;
        end
     else if controle = 'ENTIDADE-ORIGEM' then
        begin
{           with frmMatchContato do
           begin
              lblorigem.text:= querysql6.FieldByName('entcod').AsString;
              lblnomeorigem.Caption := querysql6.FieldByName('entnome').AsString;
              lblorigem.Refresh;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end;}
        end
     else if controle = 'ENTIDADE-DESTINO' then
        begin
         {  with frmmatchcontato do
           begin
              lbldestino.text := querysql6.FieldByName('entcod').AsString;
              lblnomedestino.Caption := querysql6.FieldByName('entnome').AsString;
              lbldestino.Refresh;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end; }
        end
     else if controle = 'CATEGORIA_APOLOSAVIC' then
        begin
           {with frmvalidaorigensentidadesavic do
           begin
              lblcategcodestr.text:= querysql6.FieldByName('categcodestr').AsString;
              lblcategnome.Caption := querysql6.FieldByName('categnome').AsString;
              lblcategcodestr.Refresh;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end;}
        end
     else if controle = 'FUNCAO_APOLOSAVIC' then
        begin
 {          with  frmvalidaorigensentidadesavic do
           begin
              lblfuncaosavic.text:= querysql6.FieldByName('funcaoid').AsString;
              lblnomefuncaosavic.caption := querysql6.FieldByName('nomefuncao').AsString;
              lblfuncaosavic.Refresh;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end;   }
        end
     else if controle = 'ORIGEM_SAVIC' then
        begin
{           with  frmvalidaorigensentidadesavic do
           begin
              lblorigemsavic.Text:= querysql6.FieldByName('origcodestr').AsString;
              lblorignome.caption := querysql6.fieldbyname('orignome').AsString;
              lblorigemsavic.Refresh;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end;  }
        end
     else if controle = 'TIPO_COBRANCA_ENTIDADE' then
        begin
           with frmconsulta3,modulo_dados do
           begin
              frmcadentidade.lbltipocobcod.text := fdquerysql9.FieldByName('tipocobcod').AsString;
              frmcadentidade.lbltipocobnome.Caption := fdquerysql9.FieldByName('tipocobnome').AsString;
              frmcadentidade.lbltipocobcod.Refresh;
              Self.ModalResult:= mrOk;
           end;
        end
     else if controle = 'TIPO_COBRANCA_GEOAPOLO' then
        begin
           with frmconsulta3, modulo_dados do
           begin
              frmcadentidade.lbltipocobcod.text := fdquerysql9.FieldByName('geotipocobcod').AsString;
              frmcadentidade.lbltipocobnome.Caption := fdquerysql9.FieldByName('geotipocobnome').AsString;
              frmcadentidade.lbltipocobcod.Refresh;
              Self.ModalResult := mrOk;
           end;
        end
     else if controle = 'BANCO_ENTIDADE' then
        begin
           with frmcadentidade do
           begin
              lblbconum.text:= fdquerysql9.FieldByName('bconum').AsString;
              lblnomebanco.Caption := fdquerysql9.FieldByName('bconome').Asstring;
              lblbconum.Refresh;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end;
        end
     else if controle = 'BANCO_ENTIDADE_GEOAPOLO' then
        begin
           with frmcadentidade do
           begin
              lblbconum.text:= fdquerysql9.FieldByName('geobconum').AsString;
              lblnomebanco.Caption := fdquerysql9.FieldByName('geobconome').Asstring;
              lblbconum.Refresh;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end;
        end
     else if controle = 'AGENCIA_BCO_ENTIDADE' then
        begin
           with frmcadentidade do
           begin
              lblagnum.text := fdquerysql9.FieldByName('agnum').AsString;
              lblnomeagencia.Caption := fdquerysql9.FieldByName('agnome').AsString;
              lblagnum.Refresh;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end;
        end
     else if controle = 'AGENCIA_BCO_ENTIDADE_GEOAPOLO' then
        begin
           with frmcadentidade do
           begin
              lblagnum.text:= fdquerysql9.FieldByName('geoagnum').AsString;
              lblnomeagencia.Caption := fdquerysql9.FieldByName('geoagnome').AsString;
              lblagnum.Refresh;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end;
        end
     else if controle = 'DIOCESES_CNBB_ENTIDADE' then
        begin
           with frmcadentidade do
           begin
              cin2.ActivePageIndex:=1;
              lbldioceseid.Text:= fdquerysql9.FieldByName('id').AsString;
              lbldiocesenome.caption:= fdquerysql9.FieldByName('nome').AsString;
              lbldioceseid.Refresh; lbldiocesenome.Refresh;
              lblprocurarpor.Clear;
              Self.ModalResult:=mrok;
           end;
        end
     else if controle = 'CATEGORIA_IMPORTA_GRUPOORACAO' then
        begin
{           with frmmoderacaogrupodeoracao do
           begin
              lblcategcodestr.text := querysql5.FieldByName('categcodestr').AsString;
              lblcategnome.caption := querysql5.FieldByName('categnome').AsString;
              lblcategcodestr.refresh; lblcategnome.refresh;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end;}
        end
     else if controle = 'IMOBILIZADOCENTROCONTROLE' then
        begin
{          with frmmanativofixo do
          begin
             lblcctrlcodestr.text := querysql6.FieldByName('geocctrlcodestr').AsString;
             lblcctrlnome.Caption := querysql6.FieldByName('geocctrlnome').AsString;
             lblcctrlcodestr.Refresh; lblcctrlnome.Refresh;
             lblprocurarpor.Clear; frmconsulta3.Close;
          end;}
        end
     else if controle = 'IMOBILIZADOCLASSIFICACAO' then
        begin
{           with frmmanativofixo do
           begin
             lblclassificacaobem.text:= querysql6.FieldByName('codigoclasse').AsString;
             lblnomeclassificacaobem.caption := querysql6.FieldByName('descricao').AsString;
             lblclassificacaobem.Refresh; lblnomeclassificacaobem.Refresh;
             lblprocurarpor.Clear; frmconsulta3.Close;
           end;}
        end
     else if controle = 'IMOBILIZADOCATEGORIABEM' then
        begin
{           with frmmanativofixo do
           begin
              lblcategbem.text:= querysql6.FieldByName('codigo_categoria').AsString;
              lblcategbemnome.Caption := querysql6.FieldByName('categoria').AsString;
              lblcategbem.Refresh; lblcategbemnome.Refresh;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end;}
        end
     else if controle = 'IMOBILIZADOLOCALIZACAOFISICA' then
        begin
{           with frmmanativofixo do
           begin
              lbllocalizacaofisica.Text:= querysql6.FieldByName('stfcodlocestr').AsString;
              lbldescricaolocalizacao.Caption := querysql6.FieldByName('localizacao').AsString;
              lbllocalizacaofisica.Refresh; lbldescricaolocalizacao.refresh;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end;}
        end
     else if controle = 'IMOBILIZADORESPONSAVELBEM' then
        begin
{          with frmmanativofixo do
          begin
            lblcodfuncresponsavel.text:= querysql6.FieldByName('usucod').AsString;
            lblnomefuncresponsavel.caption:= querysql6.FieldByName('nome_completo').AsString;
            lblcodfuncresponsavel.Refresh; lblnomefuncresponsavel.Refresh;
            lblprocurarpor.Clear; frmconsulta3.Close;
          end;}
        end
     else if controle = 'IMOBILIZADOMARCA' then
        begin
{           with frmmanativofixo do
           begin
              lblcodmarcaproduto.text:= querysql6.FieldByName('codigo_marca').AsString;
              lblnomedamarca.Caption:=querysql6.FieldByName('descricao_marca').AsString;
              lblcodmarcaproduto.Refresh; lblnomedamarca.Refresh;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end;}
        end
     else if controle = 'BUSCAMARCACADMARCA' then
        begin
        {  with frmmarcas do
          begin
            lblcodmarca.text:= querysql6.FieldByName('codigo_marca').AsString;
            lbldescricao.Text:= querysql6.FieldByName('descricao_marca').AsString;
            lblcodmarca.Refresh; lbldescricao.Refresh;
            lblprocurarpor.Clear; frmconsulta3.Close;
          end;}
        end
     else if controle = 'IMOBILIZADOSTATUS' then
        begin
        {  with modulo_dados, frmmanativofixo do
          begin
            lblstatusdobem.Text:=querysql6.fieldbyname('codigo_status_bem').AsString;
            lblnomestatusdobem.Caption := querysql6.FieldByName('descricao_status_bem').AsString;
            lblstatusdobem.Refresh; lblnomestatusdobem.refresh;
            lblprocurarpor.Clear; frmconsulta3.Close;
          end;}
        end
     else if controle = 'GEOCADCARTADOCREDITO' then
        begin
          { with modulo_dados, frmgafincadcartao do
           begin
              lblbconumcartao.text:= querysql.FieldByName('geobconum').AsString;
              lblnomedobanco.Caption := querysql.FieldByName('geobconome').AsString;
              lblbconumcartao.Refresh; lblnomedobanco.Refresh;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end }
        end
     else if controle = 'BUSCAENTPADRAOOCORAPOLO' then
        begin
           with modulo_dados, frmconfig do
           begin
              lblentidade.Text:= fdquerysql9.FieldByName('entcod').AsString;
              lblnome_entidade.Caption := fdquerysql9.FieldByName('entnome').AsString;
              lblprocurarpor.Clear; lblentidade.Refresh; lblnome_entidade.Refresh;
              frmconsulta3.Close;
           end;
        end
     else if controle = 'BUSCAENTPADRAOOCORGEOAPOLO' then
        begin
           with modulo_dados, frmconfig do
           begin
              lblentidade.Text:= fdquerysql9.FieldByName('geoentcod').AsString;
              lblnome_entidade.Caption := fdquerysql9.FieldByName('geoentnome').AsString;
              lblprocurarpor.Clear; lblentidade.Refresh; lblnome_entidade.Refresh;
              frmconsulta3.Close;
           end;
        end
     else if controle = 'BUSCASOLOCORAPOLO' then
       begin
          with modulo_dados, frmconfig do
          begin
             lbltiposolucaoocorrencia.text:= fdquerysql7.FieldByName('tiposolocorcod').AsString;
             lbldescricaosolucaoocorrencia.Caption := fdquerysql7.FieldByName('tiposolocornome').AsString;
             lblprocurarpor.Clear; lbltiposolucaoocorrencia.Refresh; lbldescricaosolucaoocorrencia.Refresh;
             frmconsulta3.Close;
          end;
       end
     else if controle = 'BUSCASOLOCORGEOAPOLO' then
        begin
           showmessage('AINDA NÃO HÁ OPÇÃO DESENVOLVIDA DE OCORRÊNCIA NATIVA AO GEOAPOLO');
        end
     else if controle = 'TIPOCAMPANHA' then
        begin
{           with modulo_dados, frmcampanhas do
           begin
              lbltipocampanha.Text:= querysql2.FieldByName('tipocampcod').AsString;
              lbltipocampdescricao.Caption:= querysql2.FieldByName('tipocampnome').AsString;
              lblprocurarpor.Clear; lbltipocampanha.Refresh; lbltipocampdescricao.Refresh;
              frmconsulta3.Close;
           end;}
        end
     else if controle = 'GEOTIPOCAMPANHA' then
        begin
{           with modulo_dados, frmcampanhas do
           begin
              lbltipocampanha.text:= querysql2.FieldByName('codigo_tipocampanha').AsString;
              lbltipocampdescricao.Caption:= querysql2.FieldByName('descricaotipocamp').AsString;
              lblprocurarpor.Clear; lbltipocampanha.Refresh; lbltipocampdescricao.Refresh;
              frmconsulta3.Close;
           end;}
        end
     else if controle = 'CATEGORIAPADRAOFORNECEDORES' then
        begin
           with modulo_dados, frmconfig do
           begin
              if (frmprincipal.integraentidadesapolo = 'Integra') or (frmprincipal.integraentidadesapolo = 'Mescla') then
                 begin
                    lblcategcodestrpadraofornecedores.Text := fdquerysql9.FieldByName('categcodestr').AsString;
                    lblcategnomepadraofornecedores.Caption:= fdquerysql9.FieldByName('categnome').AsString;
                 end
              else if (frmprincipal.integraentidadesapolo = 'Não Integra')  then
                 begin
                    lblcategcodestrpadraofornecedores.text := fdquerysql9.FieldByName('geocategcodestr').AsString;
                    lblcategnomepadraofornecedores.Caption:= fdquerysql9.FieldByName('geocategnome').AsString;
                 end;
              lblprocurarpor.Clear; lblcategcodestrpadraofornecedores.Refresh; lblcategnomepadraofornecedores.Refresh;
              frmconsulta3.Close;
           end;
        end
     else if controle = 'GEOLCTOCARTOES' then
        begin
      {     with modulo_dados, frmgactasapagardocfin do
           begin
              if (frmprincipal.integraentidadesapolo = 'Integra') or (frmprincipal.integraentidadesapolo = 'Mescla')  then
                 begin
                    lblentcod.text := querysql4.fieldbyname('entcod').asstring;
                    lblentnome.Caption := querysql4.fieldbyname('entnome').asstring;
                    lblentcod.Refresh; lblentnome.refresh;
                 end
              else if (frmprincipal.integraentidadesapolo = 'Não Integra') then
                 begin
                    lblentcod.text := querysql4.fieldbyname('geoentcod').asstring;
                    lblentnome.Caption := querysql4.fieldbyname('geoentnome').asstring;
                    lblentcod.Refresh; lblentnome.refresh;
                 end ;
              lblprocurarpor.clear; lblentcod.Refresh; lblentnome.refresh;
              frmconsulta3.close;
           end; }
        end
     else if controle = 'GEOBUSCACARTAOCREDITO' then
        begin
           {with modulo_dados, frmgactasapagardocfin do
           begin
             lblcodcartao.text := querysql4.FieldByName('cartao').asstring;
             lblnomecartao.Caption:=querysql4.fieldbyname('geobandeira').asstring;
             lblcodcartao.Refresh; lblnomecartao.Refresh;
             frmconsulta3.close;
           end;}
        end
     else if controle = 'PLANO_CTA_DEBXCRED' then
        begin
           {with modulo_dados, frmdebxcred do
           begin
              lblcodredconta.text:=querysql.fieldbyname('planoctacodred').asstring;
              lblnomecontacontabil.Caption:= querysql.FieldByName('PlanoCtaNome').AsString;
              lblprocurarpor.Clear; lblcodredconta.Refresh; lblnomecontacontabil.Refresh;
              frmconsulta3.Close;
           end; }
        end
     else if controle = 'TIPOLANC_VENDASCUPONS' then
        begin
           {with modulo_dados, frmcorrigecuponsnomeados do
           begin
              lbltipolanccod.text := querysql7.FieldByName('tipolanccod').AsString;
              lbltipolancnome.caption := querysql7.FieldByName('tipolancnome').AsString;
              lbltipolanccod.Refresh; lbltipolancnome.refresh;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end; }
        end
     else if controle = 'CAMPANHASEMAIL-APOLO' then
        begin
{           with modulo_dados, frmapocrmmailmkt do
           begin
              lblcodcampanha.text:= querysql4.FieldByName('campnum').AsString;
              lblnomecampanha.Caption := querysql4.FieldByName('campnome').AsString;
              lblcodcampanha.Refresh; lblnomecampanha.Refresh;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end;}
        end
     else if controle = 'CAMPANHASEMAIL-GEOAPOLO' then
        begin
 {          with modulo_dados, frmapocrmmailmkt do
           begin
              lblcodcampanha.text:= querysql4.FieldByName('codigo_campanha').AsString;
              lblnomecampanha.Caption := querysql4.FieldByName('nome_campanha').AsString;
              lblcodcampanha.Refresh; lblnomecampanha.Refresh;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end;}
        end
     else if controle = 'ENTCIDCODCONTATO' then
        begin
          { with modulo_dados, frmcadentidade do
           begin


              lblprocurarpor.Clear; frmconsulta3.Close;
           end;}
        end
     else if controle = 'BUSCAENTIDADECONSUMIDORFINALAPOLO' then
        begin
          { with modulo_dados, frmconfig do
           begin
              lblentcodconsumidorfinal.text:= querysql18.fieldbyname('entcod').AsString;
              lblentnomeconsumidorfinal.Caption := querysql18.FieldByName('entnome').AsString;
              lblentcodconsumidorfinal.Refresh; lblentnomeconsumidorfinal.Refresh;
              lblprocurarpor.Clear; frmconsulta3.Close;
           end;  }
        end
     else if controle = 'GEOCLASSELCTOCARTOES' then
        begin
         { with modulo_dados, frmgactasapagardocfin do
          begin
             lblclasserecdespcodestr.text := querysql10.fieldbyname('classerecdespcodestr').asstring;
             lblclasserecdespnome.caption := querysql10.fieldbyname('classerecdespnome').asstring;
             lblclasserecdespcodestr.Refresh; lblclasserecdespnome.Refresh;
             lblprocurarpor.clear; frmconsulta3.close;
          end;}
        end;
   end;
end;

end.
