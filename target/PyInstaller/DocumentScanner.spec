# -*- mode: python -*-

block_cipher = None


a = Analysis(['/home/thinh/projects/Document_Scanner/src/main/python/main.py'],
             pathex=['/home/thinh/projects/Document_Scanner/target/PyInstaller'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=['/home/thinh/.pyenv/versions/3.6.12/envs/document_scanner/lib/python3.6/site-packages/fbs/freeze/hooks'],
             runtime_hooks=['/home/thinh/projects/Document_Scanner/target/PyInstaller/fbs_pyinstaller_hook.py'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='DocumentScanner',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='DocumentScanner')
