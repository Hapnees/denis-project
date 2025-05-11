import PyInstaller.__main__

PyInstaller.__main__.run([
    'run.py',
    '--name=BookSearch',
    '--onefile',
    '--add-data=templates:templates',
    '--add-data=static:static',
    '--hidden-import=jinja2',
    '--hidden-import=uvicorn.loops.auto',
    '--hidden-import=uvicorn.protocols.http.auto',
])