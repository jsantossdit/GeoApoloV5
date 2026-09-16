object frmconfigperfil: Tfrmconfigperfil
  Left = 0
  Top = 0
  Caption = 'Configura'#231#227'o de Perfil de Acesso'
  ClientHeight = 480
  ClientWidth = 760
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  Position = poScreenCenter
  OnActivate = FormActivate
  OnClose = FormClose
  OnCreate = FormCreate
  OnKeyUp = FormKeyUp
  TextHeight = 13
  object lblmsg1: TLabel
    Left = 8
    Top = 442
    Width = 3
    Height = 13
  end
  object panelmenu: TPanel
    Left = 0
    Top = 0
    Width = 760
    Height = 41
    Align = alTop
    BevelOuter = bvNone
    TabOrder = 0
    ExplicitWidth = 754
    DesignSize = (
      760
      41)
    object spbsalvar: TSpeedButton
      Left = 8
      Top = 6
      Width = 90
      Height = 28
      Caption = '&Salvar'
      OnClick = spbsalvarClick
    end
    object spblimpar: TSpeedButton
      Left = 104
      Top = 6
      Width = 90
      Height = 28
      Caption = 'Limpar'
      OnClick = spblimparClick
    end
    object spbdeletar: TSpeedButton
      Left = 200
      Top = 6
      Width = 90
      Height = 28
      Caption = 'Deletar'
    end
    object spblocalizar: TSpeedButton
      Left = 296
      Top = 6
      Width = 90
      Height = 28
      Caption = 'Localizar'
    end
    object spbrenomear: TSpeedButton
      Left = 392
      Top = 6
      Width = 100
      Height = 28
      Caption = 'Renomear'
      OnClick = spbrenomearClick
    end
    object spbretornar: TSpeedButton
      Left = 606
      Top = 6
      Width = 98
      Height = 28
      Anchors = [akTop, akRight]
      Caption = 'Retornar (F10)'
      OnClick = spbretornarClick
      ExplicitLeft = 654
    end
  end
  object GroupBox1: TGroupBox
    Left = 8
    Top = 49
    Width = 744
    Height = 56
    Caption = ' Sele'#231#227'o '
    TabOrder = 1
    object lblgrupo: TLabel
      Left = 16
      Top = 24
      Width = 29
      Height = 13
      Caption = 'Grupo'
    end
    object lblcategoria: TLabel
      Left = 304
      Top = 24
      Width = 47
      Height = 13
      Caption = 'Categoria'
    end
    object cbogrupo: TComboBox
      Left = 56
      Top = 21
      Width = 220
      Height = 21
      Style = csDropDownList
      TabOrder = 0
      OnChange = cbogrupoChange
    end
    object cbocategoria: TComboBox
      Left = 360
      Top = 21
      Width = 241
      Height = 21
      Style = csDropDownList
      TabOrder = 1
      OnChange = cbocategoriaChange
    end
  end
  object pnlDisponiveis: TPanel
    Left = 8
    Top = 113
    Width = 300
    Height = 320
    BevelOuter = bvNone
    TabOrder = 2
    object lblcompdispo: TLabel
      Left = 0
      Top = 0
      Width = 300
      Height = 13
      Align = alTop
      Alignment = taCenter
      Caption = 'N'#227'o Permitido'
      ExplicitWidth = 66
    end
    object lstDisponiveis: TListBox
      Left = 0
      Top = 13
      Width = 300
      Height = 307
      Align = alClient
      ItemHeight = 13
      TabOrder = 0
      OnDblClick = lstDisponiveisDblClick
      OnKeyUp = lstDisponiveisKeyUp
    end
  end
  object pnlBotoes: TPanel
    Left = 314
    Top = 113
    Width = 110
    Height = 320
    BevelOuter = bvNone
    TabOrder = 3
    object btnLiberar: TButton
      Left = 10
      Top = 120
      Width = 90
      Height = 25
      Caption = '>>'
      TabOrder = 0
      OnClick = btnLiberarClick
    end
    object btnRevogar: TButton
      Left = 10
      Top = 150
      Width = 90
      Height = 25
      Caption = '<<'
      TabOrder = 1
      OnClick = btnRevogarClick
    end
    object btnLiberarTodos: TButton
      Left = 10
      Top = 185
      Width = 90
      Height = 25
      Caption = '>> Todos'
      TabOrder = 2
      OnClick = btnLiberarTodosClick
    end
    object btnRevogarTodos: TButton
      Left = 10
      Top = 215
      Width = 90
      Height = 25
      Caption = '<< Todos'
      TabOrder = 3
      OnClick = btnRevogarTodosClick
    end
  end
  object pnlLiberados: TPanel
    Left = 430
    Top = 113
    Width = 300
    Height = 320
    BevelOuter = bvNone
    TabOrder = 4
    object lblliberado: TLabel
      Left = 0
      Top = 0
      Width = 300
      Height = 13
      Align = alTop
      Alignment = taCenter
      Caption = 'Permitido'
      ExplicitWidth = 44
    end
    object lstLiberados: TListBox
      Left = 0
      Top = 13
      Width = 300
      Height = 307
      Align = alClient
      ItemHeight = 13
      TabOrder = 0
      OnDblClick = lstLiberadosDblClick
      OnKeyUp = lstLiberadosKeyUp
    end
  end
  object StatusBar1: TStatusBar
    Left = 0
    Top = 461
    Width = 760
    Height = 19
    Panels = <
      item
        Width = 100
      end
      item
        Width = 100
      end
      item
        Width = 100
      end
      item
        Width = 100
      end>
    ExplicitTop = 452
    ExplicitWidth = 754
  end
end
