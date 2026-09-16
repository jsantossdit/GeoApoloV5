unit unt_PermissionManager;

interface

uses
  System.Classes, System.SysUtils, Vcl.Forms, Vcl.Controls, Vcl.Menus,
  System.Generics.Collections, FireDAC.Comp.Client, unt_dados;

type
  TPermissionManager = class
  public
    class procedure ApplyPermissions(AForm: TForm; const CodigoUsuario: string);
  end;

implementation

class procedure TPermissionManager.ApplyPermissions(AForm: TForm; const CodigoUsuario: string);
var
  DictPermissions : TDictionary<string, Boolean>;
  qryGrupos, qryObjetos : TFDQuery;
  i               : Integer;
  Comp            : TComponent;
  AcessoPermitido : Boolean;
  Grupos          : string;
  NomeObj         : string;
begin
  DictPermissions := TDictionary<string, Boolean>.Create;
  qryGrupos  := TFDQuery.Create(nil);
  qryObjetos := TFDQuery.Create(nil);
  try
    qryGrupos.Connection  := modulo_dados.fdbanco;
    qryObjetos.Connection := modulo_dados.fdbanco;

    // 1) Grupos aos quais o usu�rio pertence
    qryGrupos.SQL.Text := 'SELECT codigo_grupo FROM USER_geoapolo_grupousuario WHERE usucod = :pusucod';
    qryGrupos.ParamByName('pusucod').AsString := CodigoUsuario;
    qryGrupos.Open;

    if qryGrupos.IsEmpty then
      Exit; // sem grupo cadastrado -> mant�m visibilidade padr�o do .dfm

    Grupos := '';
    qryGrupos.First;
    while not qryGrupos.Eof do
    begin
      Grupos := Grupos + QuotedStr(qryGrupos.FieldByName('codigo_grupo').AsString) + ',';
      qryGrupos.Next;
    end;
    Delete(Grupos, Length(Grupos), 1); // remove v�rgula final

    // 2) Status de acesso por objeto, para todos os grupos do usu�rio
    qryObjetos.SQL.Text :=
      'SELECT ugo.nome_objeto, uggo.statusacesso ' +
      'FROM USER_geoapolo_grupobjetos uggo WITH(NOLOCK) ' +
      'INNER JOIN USER_geoapolo_objetos ugo ON uggo.codigo_objeto = ugo.codigo_objeto ' +
      'WHERE uggo.codigo_grupo IN (' + Grupos + ') ' +
      'ORDER BY uggo.statusacesso DESC'; // 'N' antes de 'A' -> 'A' sobrescreve por �ltimo
    qryObjetos.Open;

    qryObjetos.First;
    while not qryObjetos.Eof do
    begin
      NomeObj         := Trim(qryObjetos.FieldByName('nome_objeto').AsString);
      AcessoPermitido := qryObjetos.FieldByName('statusacesso').AsString = 'A';
      // AddOrSetValue (n�o "s� adiciona se n�o existe"): preserva a regra de que,
      // se o usu�rio est� em v�rios grupos, basta UM 'A' para liberar o objeto.
      DictPermissions.AddOrSetValue(NomeObj, AcessoPermitido);
      qryObjetos.Next;
    end;

    // 3) Varredura din�mica do formul�rio
    for i := 0 to AForm.ComponentCount - 1 do
    begin
      Comp := AForm.Components[i];
      if DictPermissions.TryGetValue(Comp.Name, AcessoPermitido) then
      begin
        if Comp is TMenuItem then
          TMenuItem(Comp).Visible := AcessoPermitido
        else if Comp is TControl then
          TControl(Comp).Visible := AcessoPermitido;
      end;
    end;
  finally
    qryGrupos.Free;
    qryObjetos.Free;
    DictPermissions.Free;
  end;
end;

end.
