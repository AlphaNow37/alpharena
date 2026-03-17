import subprocess
import pathlib

actual_path = pathlib.Path(__file__).parent.absolute()

def main():
    start_server()
    start_client()
    start_client()

def start_client():
    command = f"start cmd /c {actual_path}/client/client.bat"
    subprocess.run(command, shell=True)

def start_server():
    command = f"start cmd /c {actual_path}/server/server.bat"
    subprocess.run(command, shell=True)
