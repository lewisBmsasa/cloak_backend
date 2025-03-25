# -*- mode: python ; coding: utf-8 -*-
#import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)

a = Analysis(
    ['fast_server.py'],
    pathex=[],
    binaries=[('./ollama', 'bin')],
    datas=[
        ('./models', 'models'),
        ('/opt/anaconda3/lib/python3.12/site-packages/ollama/', 'ollama'),
        ('/opt/anaconda3/lib/python3.12/site-packages/spacy', 'spacy'),
       
        ('/opt/anaconda3/lib/python3.12/site-packages/presidio_analyzer', 'presidio_analyzer'),
        ('/opt/anaconda3/lib/python3.12/site-packages/presidio_anonymizer', 'presidio_anonymizer'),
        ('/opt/anaconda3/lib/python3.12/site-packages/presidio_structured', 'presidio_structured'),
        ('/opt/anaconda3/lib/python3.12/site-packages/presidio_image_redactor', 'presidio_image_redactor'),
        ('/opt/anaconda3/lib/python3.12/site-packages/en_core_web_sm', 'en_core_web_sm')
    ],
    hiddenimports=['ollama', 'ollama._client',
        'spacy',
        'presidio_analyzer',
        'spacy.lang.en',
        'spacy.pipeline',
        'en_core_web_sm'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)


exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='fast_server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)



