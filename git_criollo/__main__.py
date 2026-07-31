import os
import sys
import logging
import subprocess

from git import Repo, InvalidGitRepositoryError

from git_criollo.ui import GitCriolloApp


def _verificar_repo() -> str:
    """Devuelve la ruta con un repo git, o pide inicializar/clonar/salir."""
    path = os.getcwd()
    try:
        Repo(path, search_parent_directories=True)
        return path
    except InvalidGitRepositoryError:
        pass

    while True:
        print("\nNo hay un repositorio Git en este directorio.")
        print("[i] Inicializar git init")
        print("[c] Clonar repositorio (URL)")
        print("[q] Salir")
        opcion = input("Opción: ").strip().lower()

        if opcion == "i":
            nombre = input("Nombre del directorio (Enter = actual): ").strip()
            target = os.path.join(path, nombre) if nombre else path
            if nombre:
                os.makedirs(target, exist_ok=True)
            result = subprocess.run(["git", "init", target],
                                    capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error: {result.stderr.strip()}")
                continue
            print("Repositorio inicializado.")
            return target

        elif opcion == "c":
            url = input("URL del repositorio a clonar: ").strip()
            if not url:
                print("URL vacía.")
                continue
            result = subprocess.run(["git", "clone", url],
                                    capture_output=True, text=True, cwd=path)
            if result.returncode != 0:
                print(f"Error: {result.stderr.strip()}")
                continue
            dir_name = url.rstrip("/").rsplit("/", 1)[-1]
            if dir_name.endswith(".git"):
                dir_name = dir_name[:-4]
            print("Repositorio clonado.")
            return os.path.join(path, dir_name)

        elif opcion == "q":
            sys.exit(0)

        else:
            print("Opción inválida.")


def main() -> None:
    os.makedirs(os.path.expanduser("~/.gitcriollo"), exist_ok=True)
    logging.basicConfig(
        filename=os.path.expanduser("~/.gitcriollo/debug.log"),
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    path = _verificar_repo()
    GitCriolloApp(start_path=path).run()


if __name__ == "__main__":
    main()
