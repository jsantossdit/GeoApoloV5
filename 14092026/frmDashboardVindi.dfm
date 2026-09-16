object frmDashboardVindi: TfrmDashboardVindi
  Left = 0
  Top = 0
  Caption = 'Dashboard - Concilia'#231#227'o Vindi/Yapay'
  ClientHeight = 542
  ClientWidth = 888
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -12
  Font.Name = 'Segoe UI'
  Font.Style = []
  Position = poScreenCenter
  OnCreate = FormCreate
  TextHeight = 15
  object pnlTop: TPanel
    Left = 0
    Top = 0
    Width = 888
    Height = 49
    Align = alTop
    BevelOuter = bvNone
    Color = clWhite
    ParentBackground = False
    TabOrder = 0
    ExplicitWidth = 882
    object lblAnoInicial: TLabel
      Left = 16
      Top = 17
      Width = 59
      Height = 15
      Caption = 'Ano Inicial:'
    end
    object seAnoInicial: TSpinEdit
      Left = 90
      Top = 13
      Width = 80
      Height = 24
      MaxValue = 2100
      MinValue = 2000
      TabOrder = 0
      Value = 2020
    end
    object btnAtualizar: TButton
      Left = 186
      Top = 12
      Width = 100
      Height = 25
      Caption = 'Atualizar'
      TabOrder = 1
      OnClick = btnAtualizarClick
    end
  end
  object pgcGraficos: TPageControl
    Left = 0
    Top = 49
    Width = 888
    Height = 493
    ActivePage = tsEvolucaoAnual
    Align = alClient
    TabOrder = 1
    ExplicitWidth = 882
    ExplicitHeight = 484
    object tsEvolucaoAnual: TTabSheet
      Caption = 'Evolu'#231#227'o Anual'
      object ChartEvolucaoAnual: TChart
        Left = 0
        Top = 0
        Width = 880
        Height = 463
        Title.Text.Strings = (
          'Evolu'#231#227'o Anual - Valor Pago x Taxa')
        Align = alClient
        Color = clWhite
        TabOrder = 0
        ExplicitWidth = 874
        ExplicitHeight = 454
        DefaultCanvas = 'TGDIPlusCanvas'
        ColorPaletteIndex = 13
      end
    end
    object tsEvolucaoMensal: TTabSheet
      Caption = 'Evolu'#231#227'o Mensal'
      ImageIndex = 1
      object ChartEvolucaoMensal: TChart
        Left = 0
        Top = 0
        Width = 880
        Height = 463
        Legend.Visible = False
        Title.Text.Strings = (
          'Evolu'#231#227'o Mensal')
        Align = alClient
        Color = clWhite
        TabOrder = 0
        DefaultCanvas = 'TGDIPlusCanvas'
        ColorPaletteIndex = 13
      end
    end
    object tsMeioPagamento: TTabSheet
      Caption = 'Meio de Pagamento'
      ImageIndex = 2
      object ChartMeioPagamento: TChart
        Left = 0
        Top = 0
        Width = 880
        Height = 463
        Title.Text.Strings = (
          'Distribui'#231#227'o por Meio de Pagamento')
        Align = alClient
        Color = clWhite
        TabOrder = 0
        DefaultCanvas = 'TGDIPlusCanvas'
        ColorPaletteIndex = 13
      end
    end
    object tsStatus: TTabSheet
      Caption = 'Status'
      ImageIndex = 3
      object ChartStatus: TChart
        Left = 0
        Top = 0
        Width = 880
        Height = 463
        Title.Text.Strings = (
          'Distribui'#231#227'o por Status')
        Align = alClient
        Color = clWhite
        TabOrder = 0
        DefaultCanvas = 'TGDIPlusCanvas'
        ColorPaletteIndex = 13
      end
    end
    object tsTicketMedio: TTabSheet
      Caption = 'Ticket M'#233'dio'
      ImageIndex = 4
      object ChartTicketMedio: TChart
        Left = 0
        Top = 0
        Width = 880
        Height = 463
        Legend.Visible = False
        Title.Text.Strings = (
          'Ticket M'#233'dio Anual')
        Align = alClient
        Color = clWhite
        TabOrder = 0
        DefaultCanvas = 'TGDIPlusCanvas'
        ColorPaletteIndex = 13
      end
    end
    object tsTaxaEfetiva: TTabSheet
      Caption = 'Taxa Efetiva'
      ImageIndex = 5
      object ChartTaxaEfetiva: TChart
        Left = 0
        Top = 0
        Width = 880
        Height = 463
        Legend.Visible = False
        Title.Text.Strings = (
          'Taxa Efetiva Anual')
        Align = alClient
        Color = clWhite
        TabOrder = 0
        DefaultCanvas = 'TGDIPlusCanvas'
        ColorPaletteIndex = 13
      end
    end
    object tsTopClientes: TTabSheet
      Caption = 'Top Clientes'
      ImageIndex = 6
      object ChartTopClientes: TChart
        Left = 0
        Top = 0
        Width = 880
        Height = 463
        Legend.Visible = False
        Title.Text.Strings = (
          'Top 10 Clientes por Valor Pago')
        Align = alClient
        Color = clWhite
        TabOrder = 0
        DefaultCanvas = 'TGDIPlusCanvas'
        ColorPaletteIndex = 13
      end
    end
  end
end
