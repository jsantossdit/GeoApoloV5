object frmcadmarcas: Tfrmcadmarcas
  Left = 0
  Top = 0
  BorderIcons = [biSystemMenu]
  BorderStyle = bsSingle
  Caption = 'Cadastro de Marcas de Produtos'
  ClientHeight = 398
  ClientWidth = 766
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  KeyPreview = True
  Position = poScreenCenter
  OnActivate = FormActivate
  OnClose = FormClose
  OnDestroy = FormDestroy
  OnKeyUp = FormKeyUp
  TextHeight = 13
  object panelmenu: TPanel
    Left = 0
    Top = 0
    Width = 766
    Height = 49
    Align = alTop
    BevelOuter = bvNone
    Color = clWhite
    ParentBackground = False
    TabOrder = 0
    object spbsalvar: TSpeedButton
      Left = 14
      Top = 4
      Width = 40
      Height = 40
      Hint = 'Salvar Marca <F3>'
      Flat = True
      ParentShowHint = False
      ShowHint = True
      OnClick = spbsalvarClick
    end
    object spbsair: TSpeedButton
      Left = 160
      Top = 4
      Width = 40
      Height = 40
      Hint = 'Sair <ESC>'
      Flat = True
      ParentShowHint = False
      ShowHint = True
      OnClick = spbsairClick
    end
    object lblsair: TLabel
      Left = 164
      Top = 33
      Width = 35
      Height = 11
      Caption = 'SAIR - F9'
      Font.Charset = ANSI_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Times New Roman'
      Font.Style = []
      ParentFont = False
    end
    object spblimpar: TSpeedButton
      Left = 60
      Top = 4
      Width = 40
      Height = 40
      Hint = 'Limpar / Novo <F2>'
      Flat = True
      ParentShowHint = False
      ShowHint = True
      OnClick = spblimparClick
    end
    object spbexcluir: TSpeedButton
      Left = 110
      Top = 4
      Width = 40
      Height = 40
      Hint = 'Excluir Marca <F5>'
      Flat = True
      ParentShowHint = False
      ShowHint = True
      OnClick = spbexcluirClick
    end
  end
  object GroupBox1: TGroupBox
    Left = 8
    Top = 51
    Width = 753
    Height = 318
    Ctl3D = False
    Font.Charset = ANSI_CHARSET
    Font.Color = clWindowText
    Font.Height = -15
    Font.Name = 'Times New Roman'
    Font.Style = []
    ParentCtl3D = False
    ParentFont = False
    TabOrder = 1
    object lblcodmarca: TLabeledEdit
      Left = 16
      Top = 40
      Width = 121
      Height = 23
      EditLabel.Width = 83
      EditLabel.Height = 17
      EditLabel.Caption = 'C'#243'digo Marca'
      MaxLength = 8
      TabOrder = 0
      Text = ''
    end
    object lbldescricao: TLabeledEdit
      Left = 176
      Top = 40
      Width = 521
      Height = 23
      CharCase = ecUpperCase
      EditLabel.Width = 118
      EditLabel.Height = 17
      EditLabel.Caption = 'Descri'#231#227'o da Marca'
      MaxLength = 60
      TabOrder = 1
      Text = ''
      OnKeyUp = lbldescricaoKeyUp
    end
    object gridmarcas: TStringGrid
      Left = 16
      Top = 88
      Width = 721
      Height = 209
      ColCount = 2
      FixedCols = 0
      Options = [goFixedVertLine, goFixedHorzLine, goVertLine, goHorzLine, goRangeSelect, goRowSizing, goColSizing]
      TabOrder = 2
      OnDblClick = gridmarcasDblClick
      OnKeyUp = gridmarcasKeyUp
      ColWidths = (
        100
        600)
    end
  end
  object StatusBar1: TStatusBar
    Left = 0
    Top = 379
    Width = 766
    Height = 19
    Panels = <
      item
        Text = 'Banco Alvo'
        Width = 100
      end
      item
        Width = 100
      end
      item
        Text = 'Banco GeoApolo'
        Width = 100
      end
      item
        Width = 100
      end
      item
        Text = 'Servidor:'
        Width = 80
      end
      item
        Width = 100
      end>
  end
end
