unit unt_splash;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls,
  Dialogs, Menus, ComCtrls, forms,Buttons, ToolWin, Registry, StdCtrls,jpeg,
  ExtCtrls, shellapi;

type
  TfrmSplash = class(TForm)
    Image1: TImage;
    lbl_versao: TLabel;
    lblnumeroversao: TLabel;
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  frmSplash: TfrmSplash;
  sql:string;

implementation

uses funcoes, unt_principal, unt_dados;

{$R *.DFM}


end.
