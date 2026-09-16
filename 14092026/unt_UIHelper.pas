unit unt_UIHelper;

interface

uses
  Vcl.Forms, System.SysUtils;

type
  TUIHelper = class
  public
    // Abre qualquer formulário de forma padronizada
    class procedure OpenForm<T: TForm>(var AFormInstance: T; const ALogMsg: string = '');
  end;

implementation

class procedure TUIHelper.OpenForm<T>(var AFormInstance: T; const ALogMsg: string);
begin
  // Cria apenas se não estiver instanciado
  if not Assigned(AFormInstance) then
    Application.CreateForm(TFormClass(T), AFormInstance);

  try
    // =========================================================================
    // LÓGICA DE BANCO/LOG (Comentada)
    // =========================================================================
    {
      if ALogMsg <> '' then
        GravaLog(CodigoUsuarioGlobal, DateToStr(Date), ALogMsg);
    }

    AFormInstance.ShowModal;
  finally
    // Limpa a memória após o fechamento (boa prática para ShowModal)
    FreeAndNil(AFormInstance);
  end;
end;

end.
