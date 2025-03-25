# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['fast_server.py'],
    pathex=[],
    binaries=[('./ollama', 'bin')],
    datas=[
        ('./models', 'models'),
        ('/home/lewis-chase/.conda/envs/cloak/lib/python3.10/site-packages/ollama/', 'ollama'),
        ('/home/lewis-chase/.conda/envs/cloak/lib/python3.10/site-packages/spacy', 'spacy'),
        ('/home/lewis-chase/.conda/envs/cloak/lib/libpython3.10.so.1.0', '.'),
        ('/home/lewis-chase/.conda/envs/cloak/lib/python3.10/site-packages/presidio_analyzer', 'presidio_analyzer'),
        ('/home/lewis-chase/.conda/envs/cloak/lib/python3.10/site-packages/presidio_anonymizer', 'presidio_anonymizer'),
        ('/home/lewis-chase/.conda/envs/cloak/lib/python3.10/site-packages/presidio_structured', 'presidio_structured'),
        ('/home/lewis-chase/.conda/envs/cloak/lib/python3.10/site-packages/presidio_image_redactor', 'presidio_image_redactor'),
        ('/home/lewis-chase/.conda/envs/cloak/lib/python3.10/site-packages/en_core_web_sm', 'en_core_web_sm')
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


# exe = EXE(
#     pyz,
#     a.scripts,
#     a.binaries,
#     a.datas,
#     name='fast_server',
#     debug=False,
#     bootloader_ignore_signals=False,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     runtime_tmpdir=None,
#     console=True,
#     disable_windowed_traceback=False,
#     argv_emulation=False,
#     target_arch=None,
#     codesign_identity=None,
#     entitlements_file=None,
# )

exe = EXE(
    pyz,
    a.scripts,
    [],  # No binaries or datas here; they go in COLLECT
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

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='cloak_server'
)

