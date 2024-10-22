from cx_Freeze import setup, Executable

setup(
    name="ProgressApp",
    version="0.1",
    description="A simple progress bar application",
    executables=[Executable("progress_app.py")],
)