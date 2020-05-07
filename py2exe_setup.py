from distutils.core import setup
import py2exe

INCLUDES = []
options = {
    "py2exe" :
        {
            "compressed" : 1, # 压缩   
            "optimize" : 2,
            "includes" : INCLUDES,
            "bundle_files": 2,
            "excludes": ["pdb",]
        }
}

setup(
    name = "护肝神器demo.exe",
    zipfile = None,
    windows = [
        {
            "version" : '0.1.0',
            "description" : '护肝神器_demo',
            "script": "AutoPlay.py",
            "icon_resources": [(1, "my_icon.ico")]
        }
    ],
)