object frmConsulta3: TfrmConsulta3
  Left = 223
  Top = 237
  BorderIcons = [biSystemMenu]
  Caption = 'Consultas Avan'#231'adas'
  ClientHeight = 454
  ClientWidth = 1017
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'MS Sans Serif'
  Font.Style = []
  KeyPreview = True
  PopupMenu = PopupMenu1
  Position = poMainFormCenter
  OnActivate = FormActivate
  OnClose = FormClose
  TextHeight = 13
  object lblmensagem: TLabel
    Left = 11
    Top = 455
    Width = 192
    Height = 16
    Caption = 'F3 - Para retornar com os dados'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clBlue
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentFont = False
  end
  object GroupBox7: TGroupBox
    Left = 8
    Top = 8
    Width = 993
    Height = 65
    Ctl3D = False
    ParentCtl3D = False
    TabOrder = 0
    object lblcampo: TLabel
      Left = 472
      Top = 16
      Width = 42
      Height = 17
      Caption = 'Campo'
      Font.Charset = ANSI_CHARSET
      Font.Color = clWindowText
      Font.Height = -15
      Font.Name = 'Times New Roman'
      Font.Style = []
      ParentFont = False
    end
    object lblordem: TLabel
      Left = 680
      Top = 16
      Width = 115
      Height = 17
      Caption = 'Ordem de Pesquisa'
      Font.Charset = ANSI_CHARSET
      Font.Color = clWindowText
      Font.Height = -15
      Font.Name = 'Times New Roman'
      Font.Style = []
      ParentFont = False
    end
    object lblperiodo: TLabel
      Left = 262
      Top = 11
      Width = 51
      Height = 17
      Caption = 'Per'#237'odo'
      Font.Charset = ANSI_CHARSET
      Font.Color = clWindowText
      Font.Height = -15
      Font.Name = 'Times New Roman'
      Font.Style = [fsBold]
      ParentFont = False
    end
    object lbla: TLabel
      Left = 362
      Top = 36
      Width = 11
      Height = 17
      Caption = #192
      Font.Charset = ANSI_CHARSET
      Font.Color = clWindowText
      Font.Height = -15
      Font.Name = 'Times New Roman'
      Font.Style = []
      ParentFont = False
    end
    object lblprocurarpor: TLabeledEdit
      Left = 10
      Top = 34
      Width = 255
      Height = 23
      EditLabel.Width = 78
      EditLabel.Height = 17
      EditLabel.Caption = 'Procurar por:'
      EditLabel.Font.Charset = ANSI_CHARSET
      EditLabel.Font.Color = clWindowText
      EditLabel.Font.Height = -15
      EditLabel.Font.Name = 'Times New Roman'
      EditLabel.Font.Style = []
      EditLabel.ParentFont = False
      Font.Charset = ANSI_CHARSET
      Font.Color = clWindowText
      Font.Height = -15
      Font.Name = 'Times New Roman'
      Font.Style = []
      ParentFont = False
      TabOrder = 0
      Text = ''
      OnKeyUp = lblprocurarporKeyUp
    end
    object cbocampo: TComboBox
      Left = 470
      Top = 32
      Width = 201
      Height = 21
      Style = csDropDownList
      Sorted = True
      TabOrder = 1
      OnChange = cbocampoChange
      OnKeyUp = cbocampoKeyUp
    end
    object cbordem: TComboBox
      Left = 680
      Top = 32
      Width = 201
      Height = 21
      Style = csDropDownList
      Sorted = True
      TabOrder = 2
      OnKeyUp = cbordemKeyUp
    end
    object rdgcrescente: TRadioButton
      Left = 891
      Top = 15
      Width = 85
      Height = 17
      Caption = 'Crescente'
      Checked = True
      Font.Charset = ANSI_CHARSET
      Font.Color = clWindowText
      Font.Height = -15
      Font.Name = 'Times New Roman'
      Font.Style = []
      ParentFont = False
      TabOrder = 3
      TabStop = True
      OnClick = rdgcrescenteClick
    end
    object rdgdecrescente: TRadioButton
      Left = 891
      Top = 37
      Width = 97
      Height = 17
      Caption = 'Decrescente'
      Font.Charset = ANSI_CHARSET
      Font.Color = clWindowText
      Font.Height = -15
      Font.Name = 'Times New Roman'
      Font.Style = []
      ParentFont = False
      TabOrder = 4
      OnClick = rdgdecrescenteClick
    end
    object datainicial: TDateTimePicker
      Left = 271
      Top = 33
      Width = 83
      Height = 21
      Date = 43924.000000000000000000
      Time = 0.705206516198813900
      TabOrder = 5
    end
    object datafinal: TDateTimePicker
      Left = 383
      Top = 33
      Width = 83
      Height = 21
      Date = 43924.000000000000000000
      Time = 0.705206516198813900
      TabOrder = 6
    end
  end
  object GroupBox1: TGroupBox
    Left = 8
    Top = 80
    Width = 985
    Height = 361
    Ctl3D = False
    ParentCtl3D = False
    TabOrder = 1
    object gridconsulta: TDBGrid
      Left = 3
      Top = -1
      Width = 969
      Height = 344
      Options = [dgTitles, dgIndicator, dgColumnResize, dgColLines, dgRowLines, dgTabs, dgConfirmDelete, dgCancelOnExit]
      TabOrder = 0
      TitleFont.Charset = DEFAULT_CHARSET
      TitleFont.Color = clWindowText
      TitleFont.Height = -11
      TitleFont.Name = 'MS Sans Serif'
      TitleFont.Style = []
      OnDblClick = gridconsultaDblClick
      OnKeyUp = gridconsultaKeyUp
    end
  end
  object StatusBar1: TStatusBar
    Left = 0
    Top = 435
    Width = 1017
    Height = 19
    Panels = <
      item
        Text = 'Banco Apolo'
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
        Text = 'Computador: '
        Width = 100
      end
      item
        Width = 100
      end>
    ExplicitTop = 426
    ExplicitWidth = 962
  end
  object PopupMenu1: TPopupMenu
    Left = 736
    Top = 144
    object gravaropcoes: TMenuItem
      Caption = '&Grava Configura'#231#245'es'
      ShortCut = 16449
      OnClick = gravaropcoesClick
    end
  end
end
