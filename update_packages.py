# update_packages.py

import shutil
import subprocess
import sys


def get_poetry_executable() -> str:
    """
    Busca o caminho absoluto do executável do Poetry e valida se é seguro.
    """
    path = shutil.which("poetry")

    if path is None:
        print("Erro crítico: 'poetry' não encontrado no PATH.")
        sys.exit(1)

    return path


def run_poetry_command(executable: str, args: list[str], check: bool = True) -> str:
    """
    Executa comandos do poetry de forma encapsulada.
    """
    try:
        # O comando é montado com o executável validado + argumentos
        result = subprocess.run(
            [executable, *args],
            capture_output=True,
            text=True,
            check=check,
            shell=False
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar comando: {' '.join([executable, *args])}")
        print(f"Detalhes: {e.stderr}")
        sys.exit(1)


def update_packages():
    print("--- Verificando dependências do projeto RN Pinturas ---")

    poetry_exe = get_poetry_executable()

    # 1. Verificar pacotes desatualizados
    print("Buscando pacotes desatualizados...")
    # check=False pois se não houver output, não é erro de execução
    outdated_output = run_poetry_command(
        poetry_exe, ["show", "--outdated"], check=False
    ).strip()

    if not outdated_output:
        print("Tudo limpo! Não há pacotes desatualizados.")
        return

    num_outdated = len(outdated_output.splitlines())
    print(f"\nPacotes desatualizados encontrados: {num_outdated}")
    print(outdated_output)
    print("-" * 40)

    confirm = input("Deseja prosseguir com a atualização em massa? (s/n): ").lower()
    if confirm != 's':
        print("Cancelado.")
        return

    # 2. Atualizar dependências
    print("\nIniciando atualização...")
    run_poetry_command(poetry_exe, ["update"])

    # 3. Exportar requirements.txt
    print("\nRegenerando requirements.txt...")
    run_poetry_command(poetry_exe, [
        "export",
        "-f", "requirements.txt",
        "--output", "requirements.txt",
        "--without-hashes"
    ])

    print("\nProcesso concluído com sucesso!")


if __name__ == "__main__":
    update_packages()
