import os
import subprocess


def install_requirements():
    subprocess.check_call(["python", "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call(
        ["python", "-m", 'pip', 'install', '-r', os.path.join(os.path.dirname(__file__), "requirements_sac.txt")])


def main():
    install_requirements()


if __name__ == '__main__':
    main()

