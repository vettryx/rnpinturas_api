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

def export_requirements():
    """
    Gera o requirements.txt usando o próprio pip do ambiente virtual,
    ignorando a frescura de plugin do Poetry.
    """
    try:
        with open("requirements.txt", "w", encoding="utf-8") as f:
            # sys.executable garante que estamos usando o Python do ambiente virtual atual (já com as libs de dev)
            subprocess.run([sys.executable, "-m", "pip", "freeze"], stdout=f, check=True)
    except Exception as e:
        print(f"Erro crítico ao gerar requirements.txt: {e}")
        sys.exit(1)

def update_packages():
    print("--- Verificando dependências do projeto RN Pinturas ---")

    poetry_exe = get_poetry_executable()

    print("Simulando atualização para verificar viabilidade...")
    simulation_output = run_poetry_command(
        poetry_exe, ["update", "--dry-run"], check=False
    )

    if "No dependencies to install or update" in simulation_output or \
       "0 installs, 0 updates" in simulation_output:

        print("\nTudo limpo! Nenhuma atualização pendente.")

        print("Regenerando requirements.txt para garantir integridade...")
        export_requirements()
        print("Processo concluído.")
        return

    print("\nAtualizações disponíveis e viáveis encontradas:")
    print(simulation_output.strip())
    print("-" * 40)

    confirm = input("Deseja aplicar essas atualizações? (s/n): ").lower()
    if confirm != 's':
        print("Cancelado.")
        return

    print("\nIniciando atualização real...")
    run_poetry_command(poetry_exe, ["update"])

    print("\nRegenerando requirements.txt (incluindo desenvolvimento)...")
    export_requirements()

    print("\nProcesso concluído com sucesso!")

if __name__ == "__main__":
    update_packages()
