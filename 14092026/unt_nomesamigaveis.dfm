object frmNomesAmigaveis: TfrmNomesAmigaveis
  Left = 0
  Top = 0
  Caption = 'Defini'#231#227'o de Nomes Amig'#225'veis'
  ClientHeight = 360
  ClientWidth = 600
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  Position = poScreenCenter
  OnCreate = FormCreate
  TextHeight = 13
  object lblInstrucao: TLabel
    Left = 8
    Top = 8
    Width = 469
    Height = 13
    Caption = 
      'Edite o nome amig'#225'vel e a categoria de cada objeto. A coluna "Ob' +
      'jeto T'#233'cnico" '#233' somente leitura.'
  end
  object grdObjetos: TStringGrid
    Left = 8
    Top = 32
    Width = 584
    Height = 280
    DefaultColWidth = 180
    DefaultRowHeight = 18
    GridLineWidth = 4
    Options = [goFixedVertLine, goFixedHorzLine, goVertLine, goHorzLine, goEditing]
    TabOrder = 0
    OnSetEditText = grdObjetosSetEditText
    RowHeights = (
      18
      17
      18
      18
      18)
  end
  object btnGerarSugestao: TButton
    Left = 8
    Top = 320
    Width = 140
    Height = 25
    Caption = 'Gerar sugest'#227'o'
    TabOrder = 1
    OnClick = btnGerarSugestaoClick
  end
  object btnFechar: TButton
    Left = 432
    Top = 320
    Width = 75
    Height = 25
    Caption = 'Fechar'
    TabOrder = 2
    OnClick = btnFecharClick
  end
  object btnSalvar: TButton
    Left = 517
    Top = 320
    Width = 75
    Height = 25
    Caption = 'Salvar'
    TabOrder = 3
    OnClick = btnSalvarClick
  end
end
