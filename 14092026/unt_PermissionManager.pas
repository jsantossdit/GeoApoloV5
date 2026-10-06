unit unt_PermissionManager;

interface

uses
  Winapi.Windows, System.Classes, System.SysUtils, Vcl.Forms, Vcl.Controls, Vcl.Menus,
  Vcl.Buttons, Vcl.StdCtrls, Vcl.ComCtrls,
  System.Generics.Collections, FireDAC.Comp.Client, unt_dados;

type
  TPermissionManager = class
  private
    class procedure AjustarMenusPai(Item: TMenuItem);
  public
    class procedure ApplyPermissions(AForm: TForm; const CodigoUsuario: string);
  end;

implementation

class procedure TPermissionManager.AjustarMenusPai(Item: TMenuItem);
var
  j: Integer;
  TemFilhoVisivel: Boolean;
begin
  if Item = nil then Exit;
  if Item.Count = 0 then Exit;

  TemFilhoVisivel := False;
  for j := 0 to Item.Count - 1 do
  begin
    AjustarMenusPai(Item.Items[j]);
    if Item.Items[j].Visible then
      TemFilhoVisivel := True;
  end;

  // Se nenhum filho está visível, oculta e desabilita o item pai
  if not TemFilhoVisivel then
  begin
    Item.Visible := False;
    Item.Enabled := False;
  end;
end;

class procedure TPermissionManager.ApplyPermissions(AForm: TForm; const CodigoUsuario: string);
var
  DictPermissions : TDictionary<string, Boolean>;
  qryGrupos, qryObjetos : TFDQuery;
  i, j            : Integer;
  Comp            : TComponent;
  AcessoPermitido : Boolean;
  Grupos          : string;
  NomeObj         : string;
  UsuLimpo        : string;
begin
  if (AForm = nil) then Exit;

  UsuLimpo := UpperCase(Trim(CodigoUsuario));
  if UsuLimpo = '' then Exit;

  // Administrador tem acesso irrestrito total a todos os objetos do sistema
  if UsuLimpo = 'ADMIN' then
  begin
    for i := 0 to AForm.ComponentCount - 1 do
    begin
      Comp := AForm.Components[i];
      if Comp is TMenuItem then
      begin
        TMenuItem(Comp).Visible := True;
        TMenuItem(Comp).Enabled := True;
      end
      else if Comp is TControl then
      begin
        TControl(Comp).Visible := True;
        TControl(Comp).Enabled := True;
      end;
    end;
    if AForm.HandleAllocated then
      DrawMenuBar(AForm.Handle);
    Exit;
  end;

  DictPermissions := TDictionary<string, Boolean>.Create;
  qryGrupos  := TFDQuery.Create(nil);
  qryObjetos := TFDQuery.Create(nil);
  try
    qryGrupos.Connection  := modulo_dados.fdbanco;
    qryObjetos.Connection := modulo_dados.fdbanco;

    // 1) Grupos aos quais o usuário pertence
    // Busca por usucod ou por login
    qryGrupos.SQL.Text :=
      'SELECT DISTINCT gu.codigo_grupo ' +
      'FROM USER_geoapolo_grupousuario gu WITH(NOLOCK) ' +
      'WHERE UPPER(gu.usucod) = :pusu1 ' +
      '   OR UPPER(gu.usucod) IN (SELECT UPPER(u.usucod) FROM USER_geoapolo_usuarios u WITH(NOLOCK) WHERE UPPER(u.login) = :pusu2)';
    qryGrupos.ParamByName('pusu1').AsString := UsuLimpo;
    qryGrupos.ParamByName('pusu2').AsString := UsuLimpo;
    qryGrupos.Open;

    if qryGrupos.IsEmpty then
    begin
      // Usuário comum sem grupo cadastrado não possui nenhuma permissão
      for i := 0 to AForm.ComponentCount - 1 do
      begin
        Comp := AForm.Components[i];
        if (Comp is TMenuItem) and (TMenuItem(Comp).Count = 0) and (TMenuItem(Comp).Caption <> '-') then
        begin
          TMenuItem(Comp).Visible := False;
          TMenuItem(Comp).Enabled := False;
        end
        else if (Comp is TSpeedButton) or (Comp is TToolButton) or (Comp is TButton) then
        begin
          if not (SameText(Comp.Name, 'spbsair') or SameText(Comp.Name, 'btn_sair') or SameText(Comp.Name, 'lblf10sair')) then
          begin
            TControl(Comp).Visible := False;
            TControl(Comp).Enabled := False;
          end;
        end;
      end;

      if AForm.Menu <> nil then
      begin
        for i := 0 to AForm.Menu.Items.Count - 1 do
          AjustarMenusPai(AForm.Menu.Items[i]);
      end;
      if AForm.HandleAllocated then
        DrawMenuBar(AForm.Handle);
      Exit;
    end;

    Grupos := '';
    qryGrupos.First;
    while not qryGrupos.Eof do
    begin
      Grupos := Grupos + QuotedStr(qryGrupos.FieldByName('codigo_grupo').AsString) + ',';
      qryGrupos.Next;
    end;
    Delete(Grupos, Length(Grupos), 1); // remove vírgula final

    // 2) Status de acesso por objeto, para todos os grupos do usuário
    // ORDER BY 'N' antes de 'A' (ou seja, DESC: 'N' > 'A') para que 'A' sobrescreva por último se usuário estiver em múltiplos grupos
    qryObjetos.SQL.Text :=
      'SELECT ugo.nome_objeto, uggo.statusacesso ' +
      'FROM USER_geoapolo_grupobjetos uggo WITH(NOLOCK) ' +
      'INNER JOIN USER_geoapolo_objetos ugo WITH(NOLOCK) ON uggo.codigo_objeto = ugo.codigo_objeto ' +
      'WHERE uggo.codigo_grupo IN (' + Grupos + ') ' +
      'ORDER BY uggo.statusacesso DESC';
    qryObjetos.Open;

    qryObjetos.First;
    while not qryObjetos.Eof do
    begin
      NomeObj         := LowerCase(Trim(qryObjetos.FieldByName('nome_objeto').AsString));
      AcessoPermitido := (UpperCase(Trim(qryObjetos.FieldByName('statusacesso').AsString)) = 'A');
      DictPermissions.AddOrSetValue(NomeObj, AcessoPermitido);
      qryObjetos.Next;
    end;

    // 3) Varredura dinâmica do formulário:
    // Modelo restritivo rigoroso — "deve ser seguido as permissões e somente liberar o que estiver liberado"
    for i := 0 to AForm.ComponentCount - 1 do
    begin
      Comp := AForm.Components[i];

      if Comp is TMenuItem then
      begin
        // Item folha de menu (ação direta)
        if (TMenuItem(Comp).Count = 0) and (TMenuItem(Comp).Caption <> '-') then
        begin
          if DictPermissions.TryGetValue(LowerCase(Comp.Name), AcessoPermitido) and AcessoPermitido then
          begin
            TMenuItem(Comp).Visible := True;
            TMenuItem(Comp).Enabled := True;
          end
          else
          begin
            TMenuItem(Comp).Visible := False;
            TMenuItem(Comp).Enabled := False;
          end;
        end
        else if TMenuItem(Comp).Count > 0 then
        begin
          // Menus pais com subitens iniciam visíveis e serão ajustados recursivamente por AjustarMenusPai
          TMenuItem(Comp).Visible := True;
          TMenuItem(Comp).Enabled := True;
        end;
      end
      else if (Comp is TSpeedButton) or (Comp is TToolButton) or (Comp is TButton) then
      begin
        // Sair do sistema permanece liberado a menos que bloqueado explicitamente
        if SameText(Comp.Name, 'spbsair') or SameText(Comp.Name, 'btn_sair') then
        begin
          if DictPermissions.TryGetValue(LowerCase(Comp.Name), AcessoPermitido) then
          begin
            TControl(Comp).Visible := AcessoPermitido;
            TControl(Comp).Enabled := AcessoPermitido;
          end
          else
          begin
            TControl(Comp).Visible := True;
            TControl(Comp).Enabled := True;
          end;
        end
        else
        begin
          // Demais botões da barra: SOMENTE liberados se constarem explicitamente com status 'A'
          if DictPermissions.TryGetValue(LowerCase(Comp.Name), AcessoPermitido) and AcessoPermitido then
          begin
            TControl(Comp).Visible := True;
            TControl(Comp).Enabled := True;
          end
          else
          begin
            TControl(Comp).Visible := False;
            TControl(Comp).Enabled := False;
          end;
        end;
      end;
    end;

    // 4) Ajuste recursivo de menus pais que ficaram sem nenhum item visível
    if AForm.Menu <> nil then
    begin
      for i := 0 to AForm.Menu.Items.Count - 1 do
        AjustarMenusPai(AForm.Menu.Items[i]);
    end;

    // Também verifica outros TMainMenu presentes no form se houver
    for i := 0 to AForm.ComponentCount - 1 do
    begin
      if (AForm.Components[i] is TMainMenu) and (AForm.Components[i] <> AForm.Menu) then
      begin
        for j := 0 to TMainMenu(AForm.Components[i]).Items.Count - 1 do
          AjustarMenusPai(TMainMenu(AForm.Components[i]).Items[j]);
      end;
    end;

    // 5) Força redesenho imediato da barra de menu no Windows Win32
    if AForm.HandleAllocated then
      DrawMenuBar(AForm.Handle);

  finally
    qryGrupos.Free;
    qryObjetos.Free;
    DictPermissions.Free;
  end;
end;

end.
