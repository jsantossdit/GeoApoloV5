object frmdebxcred: Tfrmdebxcred
  Left = 0
  Top = 0
  Caption = 'D'#233'bito x Cr'#233'dito Cont'#225'bil'
  ClientHeight = 720
  ClientWidth = 1180
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Segoe UI'
  Font.Style = []
  KeyPreview = True
  OldCreateOrder = False
  Position = poScreenCenter
  OnClose = FormClose
  OnCreate = FormCreate
  OnKeyUp = FormKeyUp
  PixelsPerInch = 96
  TextHeight = 13
  object panelmenu: TPanel
    Left = 0
    Top = 0
    Width = 1180
    Height = 52
    Align = alTop
    TabOrder = 0
    object spbexecutar: TSpeedButton
      Left = 8
      Top = 10
      Width = 100
      Height = 30
      Caption = 'Executar'
      Glyph.Data = {
        76010000424D7601000000000000760000002800000020000000100000000100
        04000000000000010000120B0000120B00001000000000000000000000000000
        80000080000000808000800000008000800080800000C0C0C000808080000000
        FF0000FF000000FFFF00FF000000FF00FF00FFFF0000FFFFFF00333338083333
        33333FFFFFFFFFFFFFFF000000B08000000088888888888888880FFFFF0B088F
        FFF08F3FF3FF3FF3FFF80F8F0000B088FF808F883883883888380FFF0BBBBB08
        8FF08F3FF3FF3FF3FFF80F8FF0FB000FFF808F883883883888380FFFFF0FF088
        FFF08F3FF3FF3FF3FFF80F8F0000BB08FF808F883883883888380FFF0FFBFBB0
        8FF08F3FF3FF3FF3FFF80F8FF0FFB00088808F883883883888380FFFFF0FFB08
        8FF08FFFFFFFFFFFFFF80CCCCC00FFB044C08888888888888888077777700000
        08708FF8888888888FF800000000000000008888888888888888333333333333
        3333333333333333333333333333333333333333333333333333}
      NumGlyphs = 2
      OnClick = spbexecutarClick
    end
    object spbexportaexcel: TSpeedButton
      Left = 114
      Top = 10
      Width = 120
      Height = 30
      Caption = 'Exportar Excel'
      Glyph.Data = {
        F6000000424DF600000000000000760000002800000010000000100000000100
        0400000000008000000000000000000000001000000010000000000000000000
        BF0000BF000000BFBF00BF000000BF00BF00BFBF0000C0C0C000808080000000
        FF0000FF000000FFFF00FF000000FF00FF00FFFF0000FFFFFF00DDDDDDDDDDDD
        DDDDDDDDDDDDDDDDDDDDDDDDDDDDDD00000DD00000000006660DD08888880E00
        000DD000000000EEE080DD07778E0EEE0080DDD078E0EEE07700DDDD0E0EEE00
        0000DDD0E0EEE080DDDDDD0E0EEE07080DDDD0E0EEE0777080DD0E0EEE0D0777
        080D00EEE0DDD077700D00000DDDDD00000DDDDDDDDDDDDDDDDD}
      OnClick = spbexportaexcelClick
    end
    object spblimpar: TSpeedButton
      Left = 240
      Top = 10
      Width = 100
      Height = 30
      Caption = 'Limpar'
      Glyph.Data = {
        F6000000424DF600000000000000760000002800000010000000100000000100
        04000000000080000000CE0E0000C40E00001000000000000000000000000000
        80000080000000808000800000008000800080800000C0C0C000808080000000
        FF0000FF000000FFFF00FF000000FF00FF00FFFF0000FFFFFF00222222222222
        2222222222222222222222222222222222222800000082222222207777770022
        2222207777770802222228077777088022222207F7F7F088022222207F7F7F08
        8022222207F7F7F088822222207F7F7F080222222207F7F7F802222222207F7F
        7702222222228000088222222222222222222222222222222222}
      OnClick = spblimparClick
    end
    object spbretornar: TSpeedButton
      Left = 346
      Top = 10
      Width = 100
      Height = 30
      Caption = '&Retornar'
      Glyph.Data = {
        76010000424D7601000000000000760000002800000020000000100000000100
        04000000000000010000120B0000120B00001000000000000000000000000000
        800000800000008080008000000080008000808000007F7F7F00BFBFBF000000
        FF0000FF000000FFFF00FF000000FF00FF00FFFF0000FFFFFF00330000000000
        03333377777777777F333301BBBBBBBB033333773F3333337F3333011BBBBBBB
        0333337F73F333337F33330111BBBBBB0333337F373F33337F333301110BBBBB
        0333337F337F33337F333301110BBBBB0333337F337F33337F333301110BBBBB
        0333337F337F33337F333301110BBBBB0333337F337F33337F333301110BBBBB
        0333337F337F33337F333301110BBBBB0333337F337FF3337F33330111B0BBBB
        0333337F337733337F333301110BBBBB0333337F337F33337F333301110BBBBB
        0333337F3F7F33337F333301E10BBBBB0333337F7F7F33337F333301EE0BBBBB
        0333337F777FFFFF7F3333000000000003333377777777777333}
      NumGlyphs = 2
      OnClick = spbretornarClick
    end
  end
  object GroupBox1: TGroupBox
    Left = 0
    Top = 52
    Width = 1180
    Height = 120
    Align = alTop
    Caption = 'Filtros da Consulta'
    TabOrder = 1
    object lbldatainicial: TLabel
      Left = 16
      Top = 28
      Width = 57
      Height = 13
      Caption = 'Data Inicial'
    end
    object lbldatafinal: TLabel
      Left = 128
      Top = 28
      Width = 52
      Height = 13
      Caption = 'Data Final'
    end
    object spbuscacontacontabil: TSpeedButton
      Left = 366
      Top = 48
      Width = 30
      Height = 23
      Caption = '...'
      OnClick = spbuscacontacontabilClick
    end
    object lblnomecontacontabil: TLabel
      Left = 410
      Top = 52
      Width = 9
      Height = 13
      Caption = '...'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -11
      Font.Name = 'Segoe UI'
      Font.Style = [fsBold]
      ParentFont = False
    end
    object btnLimparFiltro: TSpeedButton
      Left = 560
      Top = 84
      Width = 100
      Height = 25
      Caption = 'Limpar Filtro'
      OnClick = btnLimparFiltroClick
    end
    object lblContadorRegistros: TLabel
      Left = 410
      Top = 15
      Width = 9
      Height = 13
      Caption = '...'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -11
      Font.Name = 'Segoe UI'
      Font.Style = [fsBold]
      ParentFont = False
    end
    object mskdtinicial: TMaskEdit
      Left = 16
      Top = 48
      Width = 100
      Height = 21
      EditMask = '!99/99/0000;1;_'
      MaxLength = 10
      TabOrder = 0
      Text = '  /  /    '
      OnKeyUp = mskdtinicialKeyUp
    end
    object mskdtfinal: TMaskEdit
      Left = 128
      Top = 48
      Width = 100
      Height = 21
      EditMask = '!99/99/0000;1;_'
      MaxLength = 10
      TabOrder = 1
      Text = '  /  /    '
      OnEnter = mskdtfinalEnter
      OnKeyUp = mskdtfinalKeyUp
    end
    object lblcodredconta: TLabeledEdit
      Left = 240
      Top = 48
      Width = 120
      Height = 21
      EditLabel.Width = 82
      EditLabel.Height = 13
      EditLabel.Caption = 'Conta Reduzida'
      TabOrder = 2
      OnEnter = lblcodredcontaEnter
      OnKeyUp = lblcodredcontaKeyUp
    end
    object cbCampoFiltro: TComboBox
      Left = 16
      Top = 88
      Width = 150
      Height = 21
      Style = csDropDownList
      TabOrder = 3
    end
    object edtFiltroTexto: TEdit
      Left = 176
      Top = 88
      Width = 180
      Height = 21
      TabOrder = 4
      OnChange = edtFiltroTextoChange
    end
    object chkSomenteDiverg: TCheckBox
      Left = 374
      Top = 92
      Width = 180
      Height = 17
      Caption = 'Mostrar Apenas Diverg'#234'ncias'
      TabOrder = 5
      OnClick = chkSomenteDivergClick
    end
  end
  object GroupBox2: TGroupBox
    Left = 0
    Top = 172
    Width = 1180
    Height = 459
    Align = alClient
    Caption = 'Resultado da Consulta'
    TabOrder = 2
    object dbgValores: TDBGrid
      Left = 2
      Top = 15
      Width = 1176
      Height = 442
      DataSource = dsDebxCred
      DefaultDrawing = False
      Options = [dgTitles, dgIndicator, dgColumnResize, dgColLines, dgRowLines, dgTabs, dgRowSelect]
      ReadOnly = True
      TabOrder = 0
      TitleFont.Charset = DEFAULT_CHARSET
      TitleFont.Color = clWindowText
      TitleFont.Height = -11
      TitleFont.Name = 'Segoe UI'
      TitleFont.Style = []
      OnDrawColumnCell = dbgValoresDrawColumnCell
    end
  end
  object pnlTotais: TPanel
    Left = 0
    Top = 650
    Width = 1180
    Height = 70
    Align = alBottom
    BevelOuter = bvNone
    Color = clWhite
    ParentBackground = False
    TabOrder = 3
    object lblTotalDebito: TLabel
      Left = 16
      Top = 13
      Width = 117
      Height = 13
      Caption = 'TOTAL D'#201'BITO: R$ 0,00'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -11
      Font.Name = 'Segoe UI'
      Font.Style = [fsBold]
      ParentFont = False
    end
    object lblTotalCredito: TLabel
      Left = 16
      Top = 32
      Width = 124
      Height = 13
      Caption = 'TOTAL CR'#201'DITO: R$ 0,00'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -11
      Font.Name = 'Segoe UI'
      Font.Style = [fsBold]
      ParentFont = False
    end
    object lblSaldo: TLabel
      Left = 16
      Top = 52
      Width = 79
      Height = 13
      Caption = 'SALDO: R$ 0,00'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -11
      Font.Name = 'Segoe UI'
      Font.Style = [fsBold]
      ParentFont = False
    end
  end
  object StatusBar1: TStatusBar
    Left = 0
    Top = 631
    Width = 1180
    Height = 19
    Panels = <>
  end
  object mtDebxCred: TFDMemTable
    FetchOptions.AssignedValues = [evMode]
    FetchOptions.Mode = fmAll
    ResourceOptions.AssignedValues = [rvSilentMode]
    ResourceOptions.SilentMode = True
    UpdateOptions.AssignedValues = [uvCheckRequired, uvAutoCommitUpdates]
    UpdateOptions.CheckRequired = False
    UpdateOptions.AutoCommitUpdates = True
    Left = 920
    Top = 32
  end
  object dsDebxCred: TDataSource
    DataSet = mtDebxCred
    Left = 980
    Top = 32
  end
end
