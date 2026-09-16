unit unt_statusbarclock;

interface

uses
  System.Classes, Vcl.ExtCtrls, Vcl.ComCtrls, SysUtils;

type
  TStatusBarClock = class
  private
    FTimer: TTimer;
    FStatusBar: TStatusBar;
    FPanelIndex: Integer;
    FFormat: string;
    procedure DoTimer(Sender: TObject);
    procedure UpdateTime;
  public
    constructor Create(AStatusBar: TStatusBar; APanelIndex: Integer = 0; AFormat: string = 'hh:nn:ss');
    destructor Destroy; override;

    procedure Start;
    procedure Stop;

    property FormatStr: string read FFormat write FFormat;
  end;

implementation

{ TStatusBarClock }

constructor TStatusBarClock.Create(AStatusBar: TStatusBar; APanelIndex: Integer = 0; AFormat: string = 'hh:nn:ss');
begin
  inherited Create;
  if AStatusBar = nil then
    raise Exception.Create('A StatusBar não pode ser nula.');

  FStatusBar := AStatusBar;
  FPanelIndex := APanelIndex;
  FFormat := AFormat;

  FTimer := TTimer.Create(nil);
  FTimer.Interval := 1000; // 1 segundo
  FTimer.OnTimer := DoTimer;
  FTimer.Enabled := False;

  // Atualiza imediatamente
  UpdateTime;
end;

destructor TStatusBarClock.Destroy;
begin
  if Assigned(FTimer) then
  begin
    FTimer.Enabled := False;
    FTimer.Free;
  end;
  inherited;
end;

procedure TStatusBarClock.DoTimer(Sender: TObject);
begin
  UpdateTime;
end;

procedure TStatusBarClock.Start;
begin
  if Assigned(FTimer) then
    FTimer.Enabled := True;
end;

procedure TStatusBarClock.Stop;
begin
  if Assigned(FTimer) then
    FTimer.Enabled := False;
end;

procedure TStatusBarClock.UpdateTime;
var
  s: string;
begin
  s := FormatDateTime(FFormat, Now);
  try
    // Protege se o índice de painel estiver fora do intervalo
    if (FPanelIndex >= 0) and (FPanelIndex < FStatusBar.Panels.Count) then
      FStatusBar.Panels[FPanelIndex].Text := s
    else
      FStatusBar.SimpleText := s;
  except
    // evitar exceção em tempo de atualização se form for destruído
  end;
end;

end.

