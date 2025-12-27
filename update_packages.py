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

    # 1. Verificar pacotes REAIS que podem ser atualizados (Simulação)
    print("Simulando atualização para verificar viabilidade...")

    simulation_output = run_poetry_command(
        poetry_exe, ["update", "--dry-run"], check=False
    )

    # CORREÇÃO AQUI:
    # Agora verificamos se o output contém "0 installs, 0 updates".
    # Isso cobre o caso onde ele lista tudo como "Skipped".
    if "No dependencies to install or update" in simulation_output or \
       "0 installs, 0 updates" in simulation_output:

        print("\nTudo limpo! Nenhuma atualização pendente.")

        # Regenera o requirements.txt para garantir que as libs de dev estejam lá
        print("Regenerando requirements.txt para garantir integridade...")
        run_poetry_command(poetry_exe, [
            "export",
            "-f", "requirements.txt",
            "--output", "requirements.txt",
            "--without-hashes",
            "--with", "dev"
        ])
        print("Processo concluído.")
        return

    # Se chegou aqui, é porque TEM atualização real (números diferentes de 0)
    print("\nAtualizações disponíveis e viáveis encontradas:")
    print(simulation_output.strip())
    print("-" * 40)

    confirm = input("Deseja aplicar essas atualizações? (s/n): ").lower()
    if confirm != 's':
        print("Cancelado.")
        return

    # 2. Atualizar dependências (Agora é pra valer)
    print("\nIniciando atualização real...")
    run_poetry_command(poetry_exe, ["update"])

    # 3. Exportar requirements.txt (COM DEV)
    print("\nRegenerando requirements.txt (incluindo desenvolvimento)...")
    run_poetry_command(poetry_exe, [
        "export",
        "-f", "requirements.txt",
        "--output", "requirements.txt",
        "--without-hashes",
        "--with", "dev"
    ])

    print("\nProcesso concluído com sucesso!")


if __name__ == "__main__":
    update_packages()
