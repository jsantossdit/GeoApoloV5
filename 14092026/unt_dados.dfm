object modulo_dados: Tmodulo_dados
  OnCreate = DataModuleCreate
  Height = 851
  Width = 1339
  PixelsPerInch = 120
  object fdbanco: TFDConnection
    ConnectionName = 'Banco'
    Params.Strings = (
      'Password=1phL28PlSJIGWr$ad@U4'
      'User_Name=sa'
      'Server=10.120.104.29'
      'Database=RCC'
      'MARS=Yes'
      'DriverID=MSSQL'
      'Address=10.120.104.29'
      'ApplicationName=GeoApolo'
      'Encrypt=No')
    FormatOptions.AssignedValues = [fvInlineDataSize]
    FormatOptions.InlineDataSize = 50
    LoginPrompt = False
    Left = 20
    Top = 46
  end
  object fdquerysql: TFDQuery
    Connection = fdbanco
    Left = 124
    Top = 36
  end
  object dtsfdquerysql: TDataSource
    DataSet = fdquerysql
    Left = 124
    Top = 112
  end
  object dtsquerysve: TDataSource
    Left = 1173
    Top = 484
  end
  object dtsquerybanco: TDataSource
    Left = 1061
    Top = 500
  end
  object fdquerysql10: TFDQuery
    Left = 118
    Top = 196
  end
  object dtsfdquerysql10: TDataSource
    DataSet = fdquerysql10
    Left = 124
    Top = 281
  end
  object fdquerysql3: TFDQuery
    Connection = fdbanco
    Left = 484
    Top = 34
  end
  object dtsfdquerysql3: TDataSource
    DataSet = fdquerysql10
    Left = 470
    Top = 112
  end
  object fdquerysql4: TFDQuery
    Connection = fdbanco
    FetchOptions.AssignedValues = [evRecordCountMode]
    FetchOptions.RecordCountMode = cmFetched
    Left = 590
    Top = 24
  end
  object dtsfdquerysql4: TDataSource
    DataSet = fdquerysql4
    Left = 582
    Top = 112
  end
  object fdqueryentidade: TFDQuery
    Connection = fdbanco
    Left = 608
    Top = 414
  end
  object dtsfdqueryentidade: TDataSource
    DataSet = fdqueryentidade
    Left = 600
    Top = 514
  end
  object fdquerysql6: TFDQuery
    Connection = fdbanco
    Left = 810
    Top = 28
  end
  object dtsfdquerysql6: TDataSource
    DataSet = fdquerysql6
    Left = 826
    Top = 112
  end
  object fdquerysql16: TFDQuery
    Connection = fdbanco
    Left = 884
    Top = 230
  end
  object dtsfdquerysql16: TDataSource
    DataSet = fdquerysql16
    Left = 881
    Top = 322
  end
  object dtsfdquerysql14: TDataSource
    DataSet = fdquerysql14
    Left = 642
    Top = 298
  end
  object fdquerysql14: TFDQuery
    Connection = fdbanco
    Left = 640
    Top = 228
  end
  object fdquerysql1: TFDQuery
    Connection = fdbanco
    Left = 262
    Top = 36
  end
  object dtsfdquerysql1: TDataSource
    DataSet = fdquerysql1
    Left = 245
    Top = 110
  end
  object fdcomando: TFDCommand
    Connection = fdbanco
    Left = 780
    Top = 576
  end
  object dtsfdquerysql12: TDataSource
    DataSet = fdquerysql12
    Left = 389
    Top = 292
  end
  object fdquerysql12: TFDQuery
    Connection = fdbanco
    Left = 379
    Top = 214
  end
  object fdquerysql7: TFDQuery
    Connection = fdbanco
    Left = 940
    Top = 36
  end
  object dtsfdquerysql7: TDataSource
    DataSet = fdquerysql7
    Left = 956
    Top = 114
  end
  object fdquerysql22: TFDQuery
    Connection = fdbanco
    Left = 295
    Top = 422
  end
  object dtsfdquerysql22: TDataSource
    DataSet = fdquerysql22
    Left = 293
    Top = 493
  end
  object dtsfdquerysql23: TDataSource
    DataSet = fdquerysql23
    Left = 426
    Top = 494
  end
  object fdquerysql23: TFDQuery
    Connection = fdbanco
    Left = 428
    Top = 414
  end
  object dtsfdquerysql11: TDataSource
    DataSet = fdquerysql11
    Left = 256
    Top = 280
  end
  object fdquerysql11: TFDQuery
    Connection = fdbanco
    Left = 244
    Top = 204
  end
  object dtsfdquerysql17: TDataSource
    DataSet = fdquerysql11
    Left = 1000
    Top = 312
  end
  object fdquerysql17: TFDQuery
    Connection = fdbanco
    Left = 994
    Top = 234
  end
  object fdquerysql18: TFDQuery
    Connection = fdbanco
    Left = 1128
    Top = 244
  end
  object dtsfdquerysql18: TDataSource
    DataSet = fdquerysql18
    Left = 1142
    Top = 322
  end
  object fdquerysql8: TFDQuery
    Connection = fdbanco
    Left = 1070
    Top = 38
  end
  object dtsfdquerysql8: TDataSource
    DataSet = fdquerysql8
    Left = 1070
    Top = 114
  end
  object fdquerysql2: TFDQuery
    Connection = fdbanco
    Left = 361
    Top = 34
  end
  object dtsfdquerysql2: TDataSource
    DataSet = fdquerysql22
    Left = 359
    Top = 111
  end
  object fdquerysql19: TFDQuery
    Connection = fdbanco
    Left = 1250
    Top = 254
  end
  object dtsfdquerysql19: TDataSource
    DataSet = fdquerysql4
    Left = 1258
    Top = 332
  end
  object fdquerysql20: TFDQuery
    Connection = fdbanco
    Left = 114
    Top = 380
  end
  object dtsfdquerysql20: TDataSource
    DataSet = fdquerysql20
    Left = 117
    Top = 458
  end
  object fdquerysql15: TFDQuery
    Connection = fdbanco
    Left = 754
    Top = 228
  end
  object dtsfdquerysql15: TDataSource
    DataSet = fdquerysql15
    Left = 766
    Top = 298
  end
  object fdquerysql9: TFDQuery
    Connection = fdbanco
    Left = 1172
    Top = 38
  end
  object dtsfdquerysql9: TDataSource
    DataSet = fdquerysql9
    Left = 1186
    Top = 114
  end
  object fdquerysql13: TFDQuery
    Connection = fdbanco
    Left = 505
    Top = 224
  end
  object dtsfdquerysql13: TDataSource
    DataSet = fdquerysql13
    Left = 515
    Top = 294
  end
  object dtsfdconsulta: TDataSource
    Left = 932
    Top = 506
  end
  object fdquerysql5: TFDQuery
    Connection = fdbanco
    Left = 694
    Top = 24
  end
  object dtsfdquerysql5: TDataSource
    DataSet = fdquerysql5
    Left = 706
    Top = 106
  end
  object fdbancosqlite: TFDConnection
    ConnectionName = 'fdbancosqlite'
    Params.Strings = (
      'Password=1phL28PlSJIGWr$ad@U4'
      'User_Name=sa'
      'Server=10.120.104.29'
      'Database=RCC'
      'MARS=Yes'
      'DriverID=SQLite'
      'Address=10.120.104.29'
      'ApplicationName=GeoApolo'
      'Encrypt=No')
    FormatOptions.AssignedValues = [fvInlineDataSize]
    FormatOptions.InlineDataSize = 50
    LoginPrompt = False
    Left = 68
    Top = 646
  end
end
