unit unt_fra_StatusBar;

interface

uses
  System.Classes, Vcl.Controls, vcl.Forms, Vcl.ComCtrls, Vcl.ExtCtrls, System.SysUtils;

type
  TFrameStatusBar= class(TFrame)
    StatusBarApp: TStatusBar;
    procedure TimerRelogioTimer(Sender: TObject);
  public
    procedure AtualizarInfo(const Servidor, Banco: string);
  end;

implementation

{$R *.dfm}

procedure TFrameStatusBar.AtualizarInfo(const Servidor, Banco: string);
begin
  StatusBarApp.Panels[1].Text := Servidor;
  StatusBarApp.Panels[3].Text := Banco;
  // Outras atualizações necessárias
end;

procedure TFrameStatusBar.TimerRelogioTimer(Sender: TObject);
begin
  StatusBarApp.Panels[7].Text := FormatDateTime('hh:nn:ss', Now);
end;

end.
