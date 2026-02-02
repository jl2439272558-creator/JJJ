import PyInstaller.__main__
import os

def build():
    work_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    main_path = os.path.join(work_dir, "app", "main.py")
    
    PyInstaller.__main__.run([
        main_path,
        '--name=WarmWorkLog',
        '--windowed',
        '--onefile',
        f'--paths={work_dir}',
        f'--add-data={os.path.join(work_dir, "assets")}{os.pathsep}assets',
        '--clean',
        '--noconfirm',
    ])

if __name__ == "__main__":
    build()
