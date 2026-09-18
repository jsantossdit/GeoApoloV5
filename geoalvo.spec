# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# Lista de todos os módulos e pacotes de domínio do GeoAlvo
hidden_imports = [
    'ativo_imobilizado',
    'autenticacao',
    'categorias',
    'configcod',
    'configuracoes',
    'consultas',
    'contabilidade',
    'core',
    'core.validators',
    'core.viacep',
    'core.email_service',
    'core.recursos',
    'core.criptografia',
    'cores',
    'crm',
    'departamentos',
    'dioceses',
    'empresas',
    'entidades',
    'entidades.database',
    'estacoes',
    'eventos',
    'fiscal',
    'licenciamento',
    'localidades',
    'matchcode',
    'nomesamigaveis',
    'permissoes',
    'relatorios',
    'usuarios',
    'vindi',
    'config_banco',
    'toolbar_geoalvo',
    'logon',
    'splash',
    'geoalvo',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'pyodbc',
    'requests',
    'sqlite3',
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
]

# Dados e ativos adicionais (imagens, logos, fundos)
datas = [
    ('Imagens', 'Imagens'),
]

a = Analysis(
    ['splash.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['test', 'tests'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GeoAlvo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='GeoApolo_Icon.ico',
)
