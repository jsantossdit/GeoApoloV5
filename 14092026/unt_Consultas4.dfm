object FrmConsulta4: TFrmConsulta4
  Left = 0
  Top = 0
  BorderStyle = bsDialog
  Caption = 'Consulta de Contas Financeiras'
  ClientHeight = 460
  ClientWidth = 520
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -12
  Font.Name = 'Segoe UI'
  Font.Style = []
  KeyPreview = True
  OldCreateOrder = True
  Position = poMainFormCenter
  OnCreate = FormCreate
  OnKeyDown = FormKeyDown
  PixelsPerInch = 96
  TextHeight = 15
  object pnlTopo: TPanel
    Left = 0
    Top = 0
    Width = 520
    Height = 64
    Align = alTop
    BevelOuter = bvNone
    Color = clWhite
    TabOrder = 0
    object lblTitulo: TLabel
      Left = 12
      Top = 8
      Width = 123
      Height = 19
      Caption = 'Contas Financeiras'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -14
      Font.Name = 'Segoe UI'
      Font.Style = [fsBold]
      ParentFont = False
    end
    object lblFiltro: TLabel
      Left = 12
      Top = 38
      Width = 53
      Height = 15
      Caption = 'Pesquisar:'
    end
    object edtFiltro: TEdit
      Left = 71
      Top = 35
      Width = 430
      Height = 23
      TabOrder = 0
      OnChange = edtFiltroChange
    end
  end
  object pnlRodape: TPanel
    Left = 0
    Top = 418
    Width = 520
    Height = 42
    Align = alBottom
    BevelOuter = bvNone
    TabOrder = 1
    object btnOK: TButton
      Left = 340
      Top = 8
      Width = 80
      Height = 26
      Caption = 'OK'
      Default = True
      TabOrder = 0
      OnClick = btnOKClick
    end
    object btnCancelar: TButton
      Left = 428
      Top = 8
      Width = 80
      Height = 26
      Cancel = True
      Caption = 'Cancelar'
      TabOrder = 1
      OnClick = btnCancelarClick
    end
  end
  object DBGrid1: TDBGrid
    Left = 0
    Top = 64
    Width = 520
    Height = 354
    Align = alClient
    DataSource = DataSource1
    Options = [dgTitles, dgIndicator, dgColumnResize, dgColLines, dgRowLines, dgTabs, dgRowSelect, dgAlwaysShowSelection, dgConfirmDelete, dgCancelOnExit, dgTitleClick, dgTitleHotTrack]
    ReadOnly = True
    TabOrder = 2
    TitleFont.Charset = DEFAULT_CHARSET
    TitleFont.Color = clWindowText
    TitleFont.Height = -12
    TitleFont.Name = 'Segoe UI'
    TitleFont.Style = []
    OnDblClick = DBGrid1DblClick
    Columns = <
      item
        Expanded = False
        FieldName = 'CODIGO'
        Title.Caption = 'C'#243'digo'
        Width = 90
        Visible = True
      end
      item
        Expanded = False
        FieldName = 'NOME'
        Title.Caption = 'Nome da Conta'
        Width = 340
        Visible = True
      end>
  end
  object DataSource1: TDataSource
    Left = 240
    Top = 240
  end
end
