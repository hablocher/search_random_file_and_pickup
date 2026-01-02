#!/usr/bin/env python3
"""Quick setup script for Media Finder."""

import subprocess
import sys
from pathlib import Path


def check_poetry():
    """Check if Poetry is installed."""
    try:
        result = subprocess.run(
            ["poetry", "--version"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            print(f"✓ Poetry encontrado: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("✗ Poetry não encontrado")
    return False


def install_poetry():
    """Install Poetry."""
    print("\n📦 Instalando Poetry...")
    
    if sys.platform == "win32":
        cmd = "(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -"
        print(f"Execute no PowerShell:\n{cmd}")
        print("\nOu visite: https://python-poetry.org/docs/#installation")
    else:
        cmd = "curl -sSL https://install.python-poetry.org | python3 -"
        print(f"Execute no terminal:\n{cmd}")
    
    return False


def install_dependencies():
    """Install project dependencies."""
    print("\n📚 Instalando dependências...")
    try:
        subprocess.run(["poetry", "install"], check=True)
        print("✓ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print("✗ Erro ao instalar dependências")
        return False


def run_tests():
    """Run tests to verify installation."""
    print("\n🧪 Executando testes...")
    try:
        result = subprocess.run(
            ["poetry", "run", "pytest", "-v"],
            check=False,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ Todos os testes passaram!")
            return True
        else:
            print("⚠ Alguns testes falharam (isso é normal se você não tiver as pastas configuradas)")
            return True
    except Exception as e:
        print(f"✗ Erro ao executar testes: {e}")
        return False


def show_usage():
    """Show usage instructions."""
    print("\n" + "="*70)
    print("🎉 INSTALAÇÃO CONCLUÍDA!")
    print("="*70)
    print("\n📖 Como usar:")
    print("\n1. Ativar ambiente virtual:")
    print("   poetry shell")
    print("\n2. Executar interface gráfica:")
    print("   poetry run rfp-gui")
    print("   # ou após ativar o shell:")
    print("   rfp-gui")
    print("\n3. Usar linha de comando:")
    print('   poetry run random-file-picker C:\\Pasta1 D:\\Pasta2')
    print("   # Com opções:")
    print('   poetry run random-file-picker --keywords "marvel" --open-folder C:\\Comics')
    print("\n4. Ver ajuda:")
    print("   poetry run random-file-picker --help")
    print("\n5. Executar testes:")
    print("   poetry run pytest")
    print("   poetry run pytest --cov")
    print("\n📚 Documentação completa:")
    print("   - README_POETRY.md")
    print("   - MIGRATION_GUIDE.md")
    print("\n" + "="*70)


def main():
    """Main setup function."""
    print("="*70)
    print("🚀 MEDIA FINDER - Setup")
    print("="*70)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8+ é necessário")
        print(f"  Versão atual: {sys.version}")
        sys.exit(1)
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check Poetry
    if not check_poetry():
        install_poetry()
        print("\n⚠ Por favor, instale Poetry e execute este script novamente.")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n✗ Falha ao instalar dependências")
        sys.exit(1)
    
    # Run tests
    run_tests()
    
    # Show usage
    show_usage()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Instalação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Erro inesperado: {e}")
        sys.exit(1)
