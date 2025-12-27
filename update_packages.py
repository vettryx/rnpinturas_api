# update_packages.py

import subprocess
import sys


def run_command(command):
    """
    Executa um comando no terminal e retorna o resultado.

    Args:
        command (str): O comando a ser executado no terminal.

    Returns:
        str: Saída do comando.
    """
    try:
        # Adicionei capture_output=True que é mais moderno que stdout=PIPE
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o comando '{command}':")
        print(e.stderr)
        sys.exit(1)

def update_packages():
    """
    Verifica pacotes desatualizados via Poetry, realiza a atualização segura
    e exporta um requirements.txt para compatibilidade (caso necessário).
    """
    print("--- Verificando dependências do projeto RN Pinturas ---")

    # 1. Verificar pacotes desatualizados
    # O comando 'poetry show --outdated' lista o que pode ser atualizado
    # dentro das restrições do seu pyproject.toml
    try:
        # check=False pois se não houver nada desatualizado, o poetry pode não retornar nada
        # mas não é erro.
        result = subprocess.run(
            "poetry show --outdated",
            capture_output=True,
            text=True,
            shell=True
        )
        outdated_output = result.stdout.strip()
    except Exception as e:
        print(f"Erro ao verificar pacotes: {e}")
        return

    if not outdated_output:
        print("Tudo limpo! Não há pacotes desatualizados conforme o pyproject.toml.")
        return

    # Conta quantas linhas (pacotes) existem
    num_outdated = len(outdated_output.splitlines())
    print(f"\nPacotes desatualizados encontrados: {num_outdated}")
    print("Lista de pacotes a serem atualizados:")
    print(outdated_output)
    print("-" * 40)

    # Pergunta de segurança (opcional, pode remover se quiser automação total)
    confirm = input("Deseja prosseguir com a atualização em massa? (s/n): ").lower()
    if confirm != 's':
        print("Atualização cancelada.")
        return

    # 2. Atualizando os pacotes
    # No Poetry, usamos 'poetry update'. Ele atualiza o poetry.lock
    # respeitando as regras do pyproject.toml.
    print("\nIniciando atualização das dependências (isso resolve o grafo de dependências)...")
    run_command("poetry update")

    # 3. Regenerar o requirements.txt (Opcional no fluxo Poetry, mas útil para deploy)
    # Nota: Requer o plugin de exportação em versões mais novas do Poetry,
    # ou o comando built-in dependendo da versão.
    print("\nExportando requirements.txt atualizado (para compatibilidade/deploy)...")
    # --without-hashes deixa o arquivo mais limpo, similar ao pip freeze antigo
    run_command("poetry export -f requirements.txt --output requirements.txt --without-hashes")

    print("\nProcesso concluído! O arquivo 'poetry.lock' e 'requirements.txt' foram atualizados.")

if __name__ == "__main__":
    update_packages()
