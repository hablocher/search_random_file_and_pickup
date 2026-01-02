# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Coleta todos os dados necessários
added_files = [
    ('assets/roulette.png', 'assets'),
    ('assets/spinning.gif', 'assets'),
]

a = Analysis(
    ['src/random_file_picker/gui/app.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'random_file_picker.core.file_picker',
        'random_file_picker.core.sequential_selector',
        'random_file_picker.core.config_manager',
        'random_file_picker.core.archive_extractor',
        'random_file_picker.core.thumbnail_generator',
        'random_file_picker.core.file_analyzer',
        'random_file_picker.utils.movie_poster',
        'random_file_picker.utils.system_utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MediaFinder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sem janela de console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Você pode adicionar um ícone .ico aqui
)
