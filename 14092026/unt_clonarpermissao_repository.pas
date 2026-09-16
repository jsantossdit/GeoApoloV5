unit unt_clonarpermissao_repository;

{
  Repositório FireDAC para Clonagem e Gestão de Permissões de Usuários.
  Executa consultas parametrizadas, hints WITH (NOLOCK) e inserções idempotentes via NOT EXISTS.
}

interface

uses
  System.SysUtils, System.Classes, Data.DB,
  FireDAC.Comp.Client, FireDAC.Stan.Param,
  unt_clonarpermissao_types;

type
  TClonarPermissaoRepository = class
  private
    FConn: TFDConnection;
    function ExecutarComando(const ASQL: string; const AParams: array of const): Integer;
  public
    constructor Create(AConnection: TFDConnection);

    function ListarUsuariosAtivos: TArray<TUsuarioResumoDTO>;
    function UsuarioTemDireitos(const AUsuarioCod: string): Boolean;

    // Operações de Clonagem de Permissões
    function ClonarDireitosSistema(const AOrigem, ADestino: string): Integer;
    function ClonarRelatorios(const AOrigem, ADestino: string): Integer;
    function ClonarContasFinanceiras(const AOrigem, ADestino: string): Integer;
    function ClonarFormularios(const AOrigem, ADestino: string): Integer;
    function ClonarCategoriasEntidades(const AOrigem, ADestino: string): Integer;
    function ClonarTipoPagarReceber(const AOrigem, ADestino: string): Integer;
    function ClonarGruposUsuario(const AOrigem, ADestino: string): Integer;
    function ClonarFavoritos(const AOrigem, ADestino: string): Integer;
    function ClonarTourUsuario(const AOrigem, ADestino: string): Integer;
    function ClonarEmpresasFiliais(const AOrigem, ADestino: string): Integer;
  end;

implementation

constructor TClonarPermissaoRepository.Create(AConnection: TFDConnection);
begin
  inherited Create;
  FConn := AConnection;
end;

function TClonarPermissaoRepository.ListarUsuariosAtivos: TArray<TUsuarioResumoDTO>;
var
  Qry: TFDQuery;
  Lista: TArray<TUsuarioResumoDTO>;
  Count: Integer;
begin
  SetLength(Lista, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT usucod, ISNULL(usunome, usucod) AS usunome ' +
      'FROM usuario WITH (NOLOCK) ' +
      'WHERE UsuStat = ''Ativo'' ' +
      'ORDER BY usucod ASC';
    Qry.Open;
    Count := 0;
    while not Qry.Eof do
    begin
      SetLength(Lista, Count + 1);
      Lista[Count].Codigo := Qry.FieldByName('usucod').AsString;
      Lista[Count].Nome   := Qry.FieldByName('usunome').AsString;
      Inc(Count);
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
  Result := Lista;
end;

function TClonarPermissaoRepository.UsuarioTemDireitos(const AUsuarioCod: string): Boolean;
var
  Qry: TFDQuery;
begin
  Result := False;
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT TOP 1 1 FROM dir_usuario WITH (NOLOCK) WHERE usucod = :usucod';
    Qry.ParamByName('usucod').AsString := AUsuarioCod;
    Qry.Open;
    Result := not Qry.IsEmpty;
  finally
    Qry.Free;
  end;
end;

function TClonarPermissaoRepository.ClonarDireitosSistema(const AOrigem, ADestino: string): Integer;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'INSERT INTO dir_usuario (tabsistcod, usucod, dirusuacesso, dirusuinclui, dirusuexclui, dirusualtera, dirusuconsulta, dirusuvisualfront) ' +
      'SELECT d.tabsistcod, :destino, d.dirusuacesso, d.dirusuinclui, d.dirusuexclui, d.dirusualtera, d.dirusuconsulta, d.dirusuvisualfront ' +
      'FROM dir_usuario d WITH (NOLOCK) ' +
      'WHERE d.usucod = :origem ' +
      '  AND NOT EXISTS ( ' +
      '      SELECT 1 FROM dir_usuario dest WITH (NOLOCK) ' +
      '      WHERE dest.usucod = :destino AND dest.tabsistcod = d.tabsistcod ' +
      '  )';
    Qry.ParamByName('destino').AsString := ADestino;
    Qry.ParamByName('origem').AsString  := AOrigem;
    Qry.ExecSQL;
    Result := Qry.RowsAffected;
  finally
    Qry.Free;
  end;
end;

function TClonarPermissaoRepository.ClonarRelatorios(const AOrigem, ADestino: string): Integer;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'INSERT INTO dir_rel_usuario (relcod, usucod) ' +
      'SELECT d.relcod, :destino ' +
      'FROM dir_rel_usuario d WITH (NOLOCK) ' +
      'WHERE d.usucod = :origem ' +
      '  AND NOT EXISTS ( ' +
      '      SELECT 1 FROM dir_rel_usuario dest WITH (NOLOCK) ' +
      '      WHERE dest.usucod = :destino AND dest.relcod = d.relcod ' +
      '  )';
    Qry.ParamByName('destino').AsString := ADestino;
    Qry.ParamByName('origem').AsString  := AOrigem;
    Qry.ExecSQL;
    Result := Qry.RowsAffected;
  finally
    Qry.Free;
  end;
end;

function TClonarPermissaoRepository.ClonarContasFinanceiras(const AOrigem, ADestino: string): Integer;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'INSERT INTO relac_ctasfin_usuario (ctasfincod, usucod) ' +
      'SELECT r.ctasfincod, :destino ' +
      'FROM relac_ctasfin_usuario r WITH (NOLOCK) ' +
      'WHERE r.usucod = :origem ' +
      '  AND NOT EXISTS ( ' +
      '      SELECT 1 FROM relac_ctasfin_usuario dest WITH (NOLOCK) ' +
      '      WHERE dest.usucod = :destino AND dest.ctasfincod = r.ctasfincod ' +
      '  )';
    Qry.ParamByName('destino').AsString := ADestino;
    Qry.ParamByName('origem').AsString  := AOrigem;
    Qry.ExecSQL;
    Result := Qry.RowsAffected;
  finally
    Qry.Free;
  end;
end;

function TClonarPermissaoRepository.ClonarFormularios(const AOrigem, ADestino: string): Integer;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'INSERT INTO ctrl_forms (empcod, tabsistcod, usucod, ctrlformsnome) ' +
      'SELECT f.empcod, f.tabsistcod, :destino, f.ctrlformsnome ' +
      'FROM ctrl_forms f WITH (NOLOCK) ' +
      'WHERE f.usucod = :origem ' +
      '  AND NOT EXISTS ( ' +
      '      SELECT 1 FROM ctrl_forms dest WITH (NOLOCK) ' +
      '      WHERE dest.usucod = :destino AND dest.empcod = f.empcod AND dest.tabsistcod = f.tabsistcod ' +
      '  )';
    Qry.ParamByName('destino').AsString := ADestino;
    Qry.ParamByName('origem').AsString  := AOrigem;
    Qry.ExecSQL;
    Result := Qry.RowsAffected;
  finally
    Qry.Free;
  end;
end;

function TClonarPermissaoRepository.ClonarCategoriasEntidades(const AOrigem, ADestino: string): Integer;
var
  Qry: TFDQuery;
  Total: Integer;
begin
  Total := 0;
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    // 1. Clonar vínculos de categoria
    Qry.SQL.Text :=
      'INSERT INTO usuario_categ (usucod, categcodestr, usucategtodasent) ' +
      'SELECT :destino, uc.categcodestr, uc.usucategtodasent ' +
      'FROM usuario_categ uc WITH (NOLOCK) ' +
      'WHERE uc.usucod = :origem ' +
      '  AND NOT EXISTS ( ' +
      '      SELECT 1 FROM usuario_categ dest WITH (NOLOCK) ' +
      '      WHERE dest.usucod = :destino AND dest.categcodestr = uc.categcodestr ' +
      '  )';
    Qry.ParamByName('destino').AsString := ADestino;
    Qry.ParamByName('origem').AsString  := AOrigem;
    Qry.ExecSQL;
    Total := Total + Qry.RowsAffected;

    // 2. Clonar vínculos com entidades das categorias
    Qry.SQL.Text :=
      'INSERT INTO usuario_ent (usucod, entcod, usuentrelacavulso) ' +
      'SELECT :destino, ec.entcod, ''N'' ' +
      'FROM usuario_categ uc WITH (NOLOCK) ' +
      'INNER JOIN entidade_categ ec WITH (NOLOCK) ' +
      '        ON ec.categcodestr = uc.categcodestr ' +
      'WHERE uc.usucod = :origem ' +
      '  AND NOT EXISTS ( ' +
      '      SELECT 1 FROM usuario_ent ue WITH (NOLOCK) ' +
      '      WHERE ue.usucod = :destino AND ue.entcod = ec.entcod ' +
      '  )';
    Qry.ParamByName('destino').AsString := ADestino;
    Qry.ParamByName('origem').AsString  := AOrigem;
    Qry.ExecSQL;
    Total := Total + Qry.RowsAffected;

    Result := Total;
  finally
    Qry.Free;
  end;
end;

function TClonarPermissaoRepository.ClonarTipoPagarReceber(const AOrigem, ADestino: string): Integer;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'INSERT INTO tipo_pag_rec_usuario (tipopagreccod, usucod) ' +
      'SELECT t.tipopagreccod, :destino ' +
      'FROM tipo_pag_rec_usuario t WITH (NOLOCK) ' +
      'WHERE t.usucod = :origem ' +
      '  AND NOT EXISTS ( ' +
      '      SELECT 1 FROM tipo_pag_rec_usuario dest WITH (NOLOCK) ' +
      '      WHERE dest.usucod = :destino AND dest.tipopagreccod = t.tipopagreccod ' +
      '  )';
    Qry.ParamByName('destino').AsString := ADestino;
    Qry.ParamByName('origem').AsString  := AOrigem;
    Qry.ExecSQL;
    Result := Qry.RowsAffected;
  finally
    Qry.Free;
  end;
end;

function TClonarPermissaoRepository.ClonarGruposUsuario(const AOrigem, ADestino: string): Integer;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'INSERT INTO grp_x_usuario (grpusucod, usucod, grpususuperv) ' +
      'SELECT g.grpusucod, :destino, g.grpususuperv ' +
      'FROM grp_x_usuario g WITH (NOLOCK) ' +
      'WHERE g.usucod = :origem ' +
      '  AND NOT EXISTS ( ' +
      '      SELECT 1 FROM grp_x_usuario dest WITH (NOLOCK) ' +
      '      WHERE dest.usucod = :destino AND dest.grpusucod = g.grpusucod ' +
      '  )';
    Qry.ParamByName('destino').AsString := ADestino;
    Qry.ParamByName('origem').AsString  := AOrigem;
    Qry.ExecSQL;
    Result := Qry.RowsAffected;
  finally
    Qry.Free;
  end;
end;

function TClonarPermissaoRepository.ClonarFavoritos(const AOrigem, ADestino: string): Integer;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'INSERT INTO ctrl_favoritos_usu (empcod, tabsistcod, usucod, ctrlfavususistema) ' +
      'SELECT f.empcod, f.tabsistcod, :destino, f.ctrlfavususistema ' +
      'FROM ctrl_favoritos_usu f WITH (NOLOCK) ' +
      'WHERE f.usucod = :origem ' +
      '  AND NOT EXISTS ( ' +
      '      SELECT 1 FROM ctrl_favoritos_usu dest WITH (NOLOCK) ' +
      '      WHERE dest.usucod = :destino AND dest.empcod = f.empcod AND dest.tabsistcod = f.tabsistcod ' +
      '  )';
    Qry.ParamByName('destino').AsString := ADestino;
    Qry.ParamByName('origem').AsString  := AOrigem;
    Qry.ExecSQL;
    Result := Qry.RowsAffected;
  finally
    Qry.Free;
  end;
end;

function TClonarPermissaoRepository.ClonarTourUsuario(const AOrigem, ADestino: string): Integer;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'INSERT INTO tour_usuario (idtour, usucod) ' +
      'SELECT t.idtour, :destino ' +
      'FROM tour_usuario t WITH (NOLOCK) ' +
      'WHERE t.usucod = :origem ' +
      '  AND NOT EXISTS ( ' +
      '      SELECT 1 FROM tour_usuario dest WITH (NOLOCK) ' +
      '      WHERE dest.usucod = :destino AND dest.idtour = t.idtour ' +
      '  )';
    Qry.ParamByName('destino').AsString := ADestino;
    Qry.ParamByName('origem').AsString  := AOrigem;
    Qry.ExecSQL;
    Result := Qry.RowsAffected;
  finally
    Qry.Free;
  end;
end;

function TClonarPermissaoRepository.ClonarEmpresasFiliais(const AOrigem, ADestino: string): Integer;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'INSERT INTO emp_fil_usuario (empcod, usucod, empfilusupermacessist, empfilusupermverdet) ' +
      'SELECT ef.empcod, :destino, ef.empfilusupermacessist, ef.empfilusupermverdet ' +
      'FROM emp_fil_usuario ef WITH (NOLOCK) ' +
      'WHERE ef.usucod = :origem ' +
      '  AND NOT EXISTS ( ' +
      '      SELECT 1 FROM emp_fil_usuario dest WITH (NOLOCK) ' +
      '      WHERE dest.usucod = :destino AND dest.empcod = ef.empcod ' +
      '  )';
    Qry.ParamByName('destino').AsString := ADestino;
    Qry.ParamByName('origem').AsString  := AOrigem;
    Qry.ExecSQL;
    Result := Qry.RowsAffected;
  finally
    Qry.Free;
  end;
end;

end.
