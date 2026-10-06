object frmmapeamento_savic_entidade: Tfrmmapeamento_savic_entidade
  Left = 0
  Top = 0
  Caption = 'Diretrizes de Mapeamento de Campos: SAVIC x Cadastro de Entidades GeoAlvo'
  ClientHeight = 650
  ClientWidth = 1100
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -12
  Font.Name = 'Segoe UI'
  Font.Style = []
  Position = poScreenCenter
  OnShow = FormShow
  TextHeight = 15
  object PanelTop: TPanel
    Left = 0
    Top = 0
    Width = 1100
    Height = 52
    Align = alTop
    BevelOuter = bvNone
    Color = clWhite
    ParentBackground = False
    TabOrder = 0
    object lblstatus: TLabel
      Left = 580
      Top = 18
      Width = 260
      Height = 15
      Caption = 'Mapeamento carregado com sucesso.'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clGreen
      Font.Height = -12
      Font.Name = 'Segoe UI'
      Font.Style = [fsBold]
      ParentFont = False
    end
    object spbsalvardiretriz: TBitBtn
      Left = 10
      Top = 8
      Width = 135
      Height = 36
      Caption = '&Salvar Diretrizes'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -12
      Font.Name = 'Segoe UI'
      Font.Style = [fsBold]
      ParentFont = False
      TabOrder = 0
      OnClick = spbsalvardiretrizClick
    end
    object spbrestaurarpadrao: TBitBtn
      Left = 155
      Top = 8
      Width = 135
      Height = 36
      Caption = '&Restaurar Padr'#227'o'
      TabOrder = 1
      OnClick = spbrestaurarpadraoClick
    end
    object spblimparassociacao: TBitBtn
      Left = 300
      Top = 8
      Width = 135
      Height = 36
      Caption = '&Limpar Associa'#231#227'o'
      TabOrder = 2
      OnClick = spblimparassociacaoClick
    end
    object spbfechar: TBitBtn
      Left = 445
      Top = 8
      Width = 100
      Height = 36
      Caption = '&Fechar'
      TabOrder = 3
      OnClick = spbfecharClick
    end
  end
  object PanelMain: TPanel
    Left = 0
    Top = 52
    Width = 1100
    Height = 598
    Align = alClient
    BevelOuter = bvNone
    TabOrder = 1
    object GroupBoxSavic: TGroupBox
      Left = 0
      Top = 0
      Width = 310
      Height = 598
      Align = alLeft
      Caption = ' 1. Campos SAVIC (Origem) '
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -12
      Font.Name = 'Segoe UI'
      Font.Style = [fsBold]
      ParentFont = False
      TabOrder = 0
      object lblDetalheSavic: TLabel
        Left = 10
        Top = 565
        Width = 290
        Height = 25
        AutoSize = False
        Caption = 'Selecione um campo para associar'
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clGray
        Font.Height = -11
        Font.Name = 'Segoe UI'
        Font.Style = []
        ParentFont = False
        WordWrap = True
      end
      object rgOrigemSavic: TRadioGroup
        Left = 8
        Top = 20
        Width = 294
        Height = 45
        Columns = 3
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -11
        Font.Name = 'Segoe UI'
        Font.Style = []
        ItemIndex = 0
        Items.Strings = (
          'Todos'
          'Grupos'
          'Coorden.')
        ParentFont = False
        TabOrder = 0
        OnClick = rgOrigemSavicClick
      end
      object lbCamposSavic: TListBox
        Left = 8
        Top = 72
        Width = 294
        Height = 485
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -12
        Font.Name = 'Segoe UI'
        Font.Style = []
        ItemHeight = 15
        ParentFont = False
        TabOrder = 1
        OnClick = lbCamposSavicClick
      end
    end
    object GroupBoxEntidade: TGroupBox
      Left = 780
      Top = 0
      Width = 320
      Height = 598
      Align = alRight
      Caption = ' 2. Destino no Cadastro de Entidades '
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -12
      Font.Name = 'Segoe UI'
      Font.Style = [fsBold]
      ParentFont = False
      TabOrder = 1
      object lblTabelaDestino: TLabel
        Left = 12
        Top = 30
        Width = 154
        Height = 15
        Caption = 'Tabela de Destino (GeoAlvo):'
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -12
        Font.Name = 'Segoe UI'
        Font.Style = []
        ParentFont = False
      end
      object lblCampoDestino: TLabel
        Left = 12
        Top = 85
        Width = 154
        Height = 15
        Caption = 'Campo da Tabela Destino:'
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -12
        Font.Name = 'Segoe UI'
        Font.Style = []
        ParentFont = False
      end
      object lblRegraConversao: TLabel
        Left = 12
        Top = 145
        Width = 114
        Height = 15
        Caption = 'Regra de Convers'#227'o:'
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -12
        Font.Name = 'Segoe UI'
        Font.Style = []
        ParentFont = False
      end
      object cbotabelaentidade: TComboBox
        Left = 12
        Top = 50
        Width = 294
        Height = 23
        Style = csDropDownList
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -12
        Font.Name = 'Segoe UI'
        Font.Style = []
        ParentFont = False
        TabOrder = 0
        OnChange = cbotabelaentidadeChange
      end
      object cbocampoentidade: TComboBox
        Left = 12
        Top = 105
        Width = 294
        Height = 23
        Style = csDropDownList
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -12
        Font.Name = 'Segoe UI'
        Font.Style = []
        ParentFont = False
        TabOrder = 1
      end
      object cboregraconversao: TComboBox
        Left = 12
        Top = 165
        Width = 294
        Height = 23
        Style = csDropDownList
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -12
        Font.Name = 'Segoe UI'
        Font.Style = []
        ItemIndex = 0
        Items.Strings = (
          'Direto'
          'CPF/CNPJ Limpo'
          'Lookup Cidade/UF'
          'Data ISO (YYYY-MM-DD)'
          'Tratamento Auto (Sr./Sra./Srta.)')
        ParentFont = False
        TabOrder = 2
        Text = 'Direto'
      end
      object btnassociar: TBitBtn
        Left = 12
        Top = 205
        Width = 294
        Height = 38
        Caption = '<-- Associar ao Campo Selecionado'
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -12
        Font.Name = 'Segoe UI'
        Font.Style = [fsBold]
        ParentFont = False
        TabOrder = 3
        OnClick = btnassociarClick
      end
    end
    object GroupBoxMapeamento: TGroupBox
      Left = 310
      Top = 0
      Width = 470
      Height = 598
      Align = alClient
      Caption = ' 3. Diretrizes Ativas de Mapeamento '
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -12
      Font.Name = 'Segoe UI'
      Font.Style = [fsBold]
      ParentFont = False
      TabOrder = 2
      object gridmapeamento: TStringGrid
        Left = 2
        Top = 18
        Width = 466
        Height = 578
        Align = alClient
        ColCount = 6
        DefaultRowHeight = 24
        FixedCols = 0
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -11
        Font.Name = 'Segoe UI'
        Font.Style = []
        Options = [goFixedVertLine, goFixedHorzLine, goVertLine, goHorzLine, goRangeSelect, goRowSelect]
        ParentFont = False
        TabOrder = 0
        OnSelectCell = gridmapeamentoSelectCell
      end
    end
  end
end
