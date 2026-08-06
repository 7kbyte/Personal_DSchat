# -*- mode: python ; coding: utf-8 -*-
"""DeepSeek Chat — PyInstaller 打包配置（单文件 EXE）"""

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 前端静态资源（HTML/CSS/JS/vendor/字体）整体打包
        ('ui/static', 'ui/static'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DeepSeekChat',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='ds.ico',
)
