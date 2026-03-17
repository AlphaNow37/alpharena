import subprocess
import pathlib

actual_path = pathlib.Path(__file__).parent.absolute()

def main():
    start_server()
    start_client()
    start_client()

def start_client():
    command = f"{actual_path}/client/client.sh"
    subprocess.run(command, shell=True)

def start_server():
    command = f"{actual_path}/server/server.sh"
    print(command)
    subprocess.run(command, shell=True)
