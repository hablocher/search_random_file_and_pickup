import os
import random
import subprocess
import platform
from pathlib import Path
from typing import List
import time


def is_file_accessible(file_path: Path) -> bool:
    """
    Verifica se um arquivo está realmente acessível (não apenas disponível online).
    
    Args:
        file_path: Caminho do arquivo a verificar
        
    Returns:
        True se o arquivo está acessível, False caso contrário
    """
    try:
        # Tenta acessar informações básicas do arquivo
        file_stat = file_path.stat()
        
        # Verifica se o tamanho é acessível (arquivos só online podem retornar 0)
        if file_stat.st_size == 0:
            # Verifica se realmente é um arquivo vazio ou se está só na nuvem
            try:
                with open(file_path, 'rb') as f:
                    # Tenta ler 1 byte para confirmar acesso
                    f.read(1)
            except (OSError, PermissionError, IOError):
                return False
        
        return True
    except (OSError, PermissionError, FileNotFoundError):
        return False


def collect_files(folders: List[str], exclude_prefix: str = "_L_", check_accessibility: bool = False, keywords: List[str] = None) -> List[str]:
    """
    Coleta todos os arquivos das pastas e subpastas informadas,
    excluindo arquivos que começam com o prefixo especificado.
    Inclui arquivos em nuvem mesmo que não estejam sincronizados localmente.
    Ignora pastas que começam com '.' (pastas ocultas).
    
    Args:
        folders: Lista de caminhos das pastas para buscar
        exclude_prefix: Prefixo a ser excluído dos resultados
        check_accessibility: Se True, verifica se arquivos estão acessíveis localmente
        keywords: Lista de palavras-chave. Se fornecida, apenas arquivos que contenham
                 ao menos uma palavra-chave no nome serão incluídos.
        
    Returns:
        Lista com os caminhos completos dos arquivos válidos
    """
    valid_files = []
    files_skipped = 0
    
    for folder in folders:
        folder_path = Path(folder)
        
        if not folder_path.exists():
            print(f"Aviso: A pasta '{folder}' não existe ou não está disponível. Ignorando...")
            continue
            
        if not folder_path.is_dir():
            print(f"Aviso: '{folder}' não é um diretório. Ignorando...")
            continue
        
        print(f"Escaneando: {folder}...")
        
        # Percorre recursivamente todos os arquivos
        try:
            for file_path in folder_path.rglob('*'):
                try:
                    # Verifica se é um arquivo (mesmo que esteja só na nuvem)
                    if not file_path.is_file():
                        continue
                    
                    # Verifica se alguma parte do caminho é uma pasta que começa com '.'
                    if any(part.startswith('.') for part in file_path.relative_to(folder_path).parts[:-1]):
                        continue
                    
                    # Verifica se o nome do arquivo não começa com o prefixo
                    if file_path.name.startswith(exclude_prefix):
                        continue
                    
                    # Filtra por palavras-chave se fornecidas
                    if keywords:
                        file_name_lower = file_path.name.lower()
                        # Verifica se ao menos UMA palavra-chave está no nome do arquivo
                        if not any(keyword in file_name_lower for keyword in keywords):
                            continue
                    
                    # Verifica acessibilidade apenas se solicitado
                    if check_accessibility:
                        if not is_file_accessible(file_path):
                            files_skipped += 1
                            continue
                    
                    valid_files.append(str(file_path))
                    
                except (OSError, PermissionError) as e:
                    # Ignora arquivos inacessíveis silenciosamente
                    files_skipped += 1
                    continue
                    
        except (OSError, PermissionError) as e:
            print(f"Aviso: Erro ao acessar '{folder}': {e}")
            continue
    
    if files_skipped > 0 and check_accessibility:
        print(f"\nAviso: {files_skipped} arquivo(s) ignorado(s) (não disponíveis localmente)")
    
    return valid_files


def open_folder(file_path: str):
    """
    Abre a pasta que contém o arquivo no explorador do sistema.
    Funciona mesmo com arquivos em nuvem não sincronizados.
    
    Args:
        file_path: Caminho completo do arquivo
    """
    folder_path = str(Path(file_path).parent)
    system = platform.system()
    
    try:
        if system == "Windows":
            # Tenta abrir o explorador e selecionar o arquivo
            # Mesmo que o arquivo esteja só na nuvem, isso funciona
            result = subprocess.run(['explorer', '/select,', file_path], 
                                   capture_output=True, text=True, timeout=5)
            # Nota: explorer não retorna erro mesmo se falhar, então não tentamos novamente
                
        elif system == "Darwin":  # macOS
            subprocess.run(['open', folder_path])
        elif system == "Linux":
            subprocess.run(['xdg-open', folder_path])
        else:
            print(f"Sistema operacional '{system}' não suportado para abrir pasta automaticamente.")
    except subprocess.TimeoutExpired:
        print("Tempo esgotado ao abrir pasta, mas o explorador deve ter sido aberto.")
    except Exception as e:
        print(f"Erro ao abrir pasta: {e}")


def pick_random_file(folders: List[str], exclude_prefix: str = "_L_", check_accessibility: bool = False, keywords: List[str] = None) -> str:
    """
    Seleciona aleatoriamente um arquivo das pastas informadas
    usando um gerador de números aleatórios criptograficamente seguro.
    Funciona com arquivos em nuvem mesmo não sincronizados localmente.
    
    Args:
        folders: Lista de caminhos das pastas para buscar
        exclude_prefix: Prefixo a ser excluído dos resultados
        check_accessibility: Se True, verifica se arquivos estão acessíveis localmente
        keywords: Lista de palavras-chave para filtrar arquivos
        
    Returns:
        Caminho completo do arquivo selecionado
        
    Raises:
        ValueError: Se nenhum arquivo válido for encontrado
    """
    valid_files = collect_files(folders, exclude_prefix, check_accessibility, keywords)
    
    if not valid_files:
        if keywords:
            raise ValueError(f"Nenhum arquivo válido encontrado com as palavras-chave: {', '.join(keywords)}")
        raise ValueError("Nenhum arquivo válido encontrado nas pastas informadas.")
    
    # Usa SystemRandom para maior aleatoriedade
    secure_random = random.SystemRandom()
    
    # Embaralha a lista para aumentar a aleatoriedade
    secure_random.shuffle(valid_files)
    
    # Seleciona um índice aleatório
    return secure_random.choice(valid_files)


def main():
    """Função principal para demonstrar o uso do programa."""
    # Exemplo de uso - modifique estas pastas conforme necessário
    folders_to_search = [
        r"L:\Meu Drive\Quadrinhos_1",
        r"K:\OneDrive\LIVROS\Quadrinhos_2",
        # Adicione mais pastas aqui
    ]
    
    print("=" * 70)
    print("SELECIONADOR ALEATÓRIO DE ARQUIVOS")
    print("Inclui arquivos em nuvem não sincronizados")
    print("=" * 70)
    print(f"\nPastas: {folders_to_search}")
    print("Excluindo arquivos com prefixo: _L_")
    print("Ignorando pastas com prefixo: .")
    print("\nBuscando arquivos...\n")
    
    try:
        start_time = time.time()
        
        # Seleciona um arquivo aleatório (incluindo arquivos em nuvem)
        selected_file = pick_random_file(folders_to_search, check_accessibility=False)
        
        elapsed_time = time.time() - start_time
        print(f"\n{'='*70}")
        print(f"Tempo de busca: {elapsed_time:.2f} segundos")
        
        # Obtém informações do arquivo
        file_path = Path(selected_file)
        
        # Tenta obter tamanho, mas não falha se não conseguir
        try:
            file_size = file_path.stat().st_size
            size_str = f"{file_size / (1024*1024):.2f} MB" if file_size > 0 else "Não sincronizado"
        except:
            size_str = "Não sincronizado"
        
        print(f"\nArquivo selecionado:")
        print(f"  Nome: {file_path.name}")
        print(f"  Caminho: {selected_file}")
        print(f"  Tamanho: {size_str}")
        
        # Abre a pasta que contém o arquivo
        print(f"\n{'='*70}")
        print("Abrindo pasta no explorador...")
        open_folder(selected_file)
        print(f"{'='*70}")
        
    except ValueError as e:
        print(f"\n{'='*70}")
        print(f"Erro: {e}")
        print("\nDicas:")
        print("  - Verifique se as pastas existem e estão acessíveis")
        print("  - Certifique-se de que há arquivos nas pastas informadas")
        print("  - Verifique se há arquivos sem o prefixo _L_")
        print(f"{'='*70}")
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"Erro inesperado: {e}")
        print(f"{'='*70}")


if __name__ == "__main__":
    main()
