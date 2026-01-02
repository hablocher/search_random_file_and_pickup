import os
import random
import subprocess
import platform
from pathlib import Path
from typing import List, Tuple, Optional
import time
import zipfile
import tempfile
import shutil

from .cache_manager import CacheManager


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


def list_files_in_zip(zip_path: str, exclude_prefix: str = "_L_", keywords: List[str] = None) -> List[str]:
    """
    Lista todos os arquivos dentro de um arquivo ZIP, aplicando filtros.
    
    Args:
        zip_path: Caminho do arquivo ZIP
        exclude_prefix: Prefixo a ser excluído dos resultados
        keywords: Lista de palavras-chave para filtrar arquivos
        
    Returns:
        Lista com os nomes dos arquivos válidos dentro do ZIP
    """
    valid_files = []
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            for file_info in zip_file.filelist:
                # Ignora diretórios
                if file_info.is_dir():
                    continue
                
                file_name = os.path.basename(file_info.filename)
                
                # Verifica prefixo
                if file_name.startswith(exclude_prefix):
                    continue
                
                # Ignora pastas ocultas (com '.')
                path_parts = file_info.filename.split('/')
                if any(part.startswith('.') for part in path_parts[:-1]):
                    continue
                
                # Filtra por palavras-chave se fornecidas
                if keywords:
                    file_name_lower = file_name.lower()
                    if not any(keyword in file_name_lower for keyword in keywords):
                        continue
                
                valid_files.append(file_info.filename)
    
    except (zipfile.BadZipFile, FileNotFoundError, PermissionError) as e:
        print(f"Erro ao acessar ZIP '{zip_path}': {e}")
        return []
    
    return valid_files


def extract_file_from_zip(zip_path: str, file_in_zip: str, temp_dir: str = None) -> str:
    """
    Extrai um arquivo específico de um ZIP para uma pasta temporária.
    
    Args:
        zip_path: Caminho do arquivo ZIP
        file_in_zip: Nome do arquivo dentro do ZIP
        temp_dir: Diretório temporário (se None, cria um novo)
        
    Returns:
        Caminho completo do arquivo extraído
        
    Raises:
        Exception: Se houver erro na extração
    """
    try:
        # Cria diretório temporário se não fornecido
        if temp_dir is None:
            temp_dir = tempfile.mkdtemp(prefix="zip_extract_")
        
        # Abre o ZIP e extrai o arquivo
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            # Extrai o arquivo
            extracted_path = zip_file.extract(file_in_zip, temp_dir)
            return extracted_path
    
    except Exception as e:
        raise Exception(f"Erro ao extrair arquivo do ZIP: {e}")


def get_temp_extraction_dir() -> str:
    """
    Cria e retorna o caminho de um diretório temporário para extração de ZIPs.
    
    Returns:
        Caminho do diretório temporário criado
    """
    return tempfile.mkdtemp(prefix="random_file_picker_")


def cleanup_temp_dir(temp_dir: str):
    """
    Remove um diretório temporário e todo seu conteúdo.
    
    Args:
        temp_dir: Caminho do diretório a ser removido
    """
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Aviso: Não foi possível remover diretório temporário '{temp_dir}': {e}")



def collect_files(folders: List[str], exclude_prefix: str = "_L_", check_accessibility: bool = False, keywords: List[str] = None, use_cache: bool = True, process_zip: bool = False) -> List[str]:
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
        use_cache: Se True, usa cache para acelerar buscas (padrão: True)
        
    Returns:
        Lista com os caminhos completos dos arquivos válidos
    """
    # DEBUG: Log para verificar se função é chamada
    import datetime
    debug_log = Path.cwd() / "debug_cache.log"
    with open(debug_log, 'a', encoding='utf-8') as f:
        f.write(f"\n[{datetime.datetime.now()}] collect_files chamado\n")
        f.write(f"  use_cache={use_cache}\n")
        f.write(f"  process_zip={process_zip}\n")
        f.write(f"  folders={len(folders)}\n")
    
    cache_manager = CacheManager()
    
    # Tenta usar cache se habilitado
    if use_cache and cache_manager.is_cache_valid(
        folders, exclude_prefix, ".", keywords or [], False
    ):
        print("✓ Usando cache de arquivos (busca instantânea)...")
        cached_files = cache_manager.get_cached_files()
        
        # Filtra por palavras-chave se necessário (cache pode ter todas)
        if keywords:
            keyword_lower = [k.lower() for k in keywords]
            valid_files = [
                f['path'] for f in cached_files 
                if any(kw in Path(f['path']).name.lower() for kw in keyword_lower)
            ]
        else:
            valid_files = [f['path'] for f in cached_files]
        
        cache_info = cache_manager.get_cache_info()
        if cache_info:
            cache_size = cache_info.get('file_size', 0) / 1024
            print(f"  Cache: {len(cached_files)} arquivos ({cache_size:.1f} KB)")
        
        return valid_files
    
    # Busca normal se cache não disponível/inválido
    if use_cache:
        print("⏳ Criando novo cache (primeira busca pode demorar)...")
    
    valid_files = []
    file_data = []  # Para salvar no cache
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
                    
                    file_str = str(file_path)
                    valid_files.append(file_str)
                    
                    # Armazena dados para cache
                    try:
                        file_stat = file_path.stat()
                        file_data.append({
                            'path': file_str,
                            'size': file_stat.st_size,
                            'mtime': file_stat.st_mtime,
                            'name': file_path.name
                        })
                    except (OSError, PermissionError):
                        # Se não conseguir stat, adiciona só o path
                        file_data.append({
                            'path': file_str,
                            'name': file_path.name
                        })
                    
                except (OSError, PermissionError) as e:
                    # Ignora arquivos inacessíveis silenciosamente
                    files_skipped += 1
                    continue
                    
        except (OSError, PermissionError) as e:
            print(f"Aviso: Erro ao acessar '{folder}': {e}")
            continue
    
    if files_skipped > 0 and check_accessibility:
        print(f"\nAviso: {files_skipped} arquivo(s) ignorado(s) (não disponíveis localmente)")
    
    # Salva cache se habilitado
    if use_cache and len(file_data) > 0:
        # DEBUG
        with open(debug_log, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.datetime.now()}] Tentando salvar cache\n")
            f.write(f"  file_data count={len(file_data)}\n")
        
        success = cache_manager.save_cache(
            file_data, folders, exclude_prefix, ".", keywords or [], process_zip
        )
        
        # DEBUG
        with open(debug_log, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.datetime.now()}] save_cache result={success}\n")
            f.write(f"  cache_file={cache_manager.cache_file}\n")
        
        print(f"✓ Cache criado: {len(file_data)} arquivos")
    
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
    result = pick_random_file_with_zip_support(folders, exclude_prefix, check_accessibility, keywords)
    return result['file_path']


def pick_random_file_with_zip_support(folders: List[str], exclude_prefix: str = "_L_", 
                                       check_accessibility: bool = False, 
                                       keywords: List[str] = None, process_zip: bool = True,
                                       use_cache: bool = True) -> dict:
    """
    Seleciona aleatoriamente um arquivo das pastas informadas, com suporte a arquivos ZIP.
    Se um arquivo ZIP for selecionado, continua a busca dentro do ZIP.
    
    Args:
        folders: Lista de caminhos das pastas para buscar
        exclude_prefix: Prefixo a ser excluído dos resultados
        check_accessibility: Se True, verifica se arquivos estão acessíveis localmente
        keywords: Lista de palavras-chave para filtrar arquivos
        process_zip: Se True, processa arquivos ZIP; se False, trata ZIPs como arquivos normais
        use_cache: Se True, usa cache para acelerar busca (padrão: True)
        
    Returns:
        Dicionário com:
            - file_path: Caminho do arquivo selecionado (extraído se veio de ZIP)
            - is_from_zip: True se o arquivo veio de um ZIP
            - zip_path: Caminho do ZIP original (se is_from_zip for True)
            - file_in_zip: Nome do arquivo dentro do ZIP (se is_from_zip for True)
            - temp_dir: Diretório temporário usado (se is_from_zip for True)
        
    Raises:
        ValueError: Se nenhum arquivo válido for encontrado
    """
    valid_files = collect_files(folders, exclude_prefix, check_accessibility, keywords, use_cache, process_zip)
    
    if not valid_files:
        if keywords:
            raise ValueError(f"Nenhum arquivo válido encontrado com as palavras-chave: {', '.join(keywords)}")
        raise ValueError("Nenhum arquivo válido encontrado nas pastas informadas.")
    
    # Usa SystemRandom para maior aleatoriedade
    secure_random = random.SystemRandom()
    
    # Embaralha a lista para aumentar a aleatoriedade
    secure_random.shuffle(valid_files)
    
    # Seleciona um arquivo aleatório
    selected_file = secure_random.choice(valid_files)
    
    # Verifica se é um arquivo ZIP e se deve processá-lo
    if process_zip and selected_file.lower().endswith('.zip'):
        print(f"Arquivo ZIP detectado: {os.path.basename(selected_file)}")
        print("Explorando conteúdo do ZIP...")
        
        # Lista arquivos dentro do ZIP
        files_in_zip = list_files_in_zip(selected_file, exclude_prefix, keywords)
        
        if not files_in_zip:
            if keywords:
                print(f"Nenhum arquivo válido encontrado no ZIP com as palavras-chave especificadas.")
            else:
                print(f"Nenhum arquivo válido encontrado no ZIP.")
            # Retorna o próprio ZIP se não houver arquivos válidos dentro
            return {
                'file_path': selected_file,
                'is_from_zip': False,
                'zip_path': None,
                'file_in_zip': None,
                'temp_dir': None
            }
        
        # Seleciona aleatoriamente um arquivo do ZIP
        selected_file_in_zip = secure_random.choice(files_in_zip)
        print(f"Arquivo selecionado do ZIP: {os.path.basename(selected_file_in_zip)}")
        
        # Cria diretório temporário
        temp_dir = get_temp_extraction_dir()
        
        try:
            # Extrai o arquivo
            print(f"Extraindo para pasta temporária...")
            extracted_path = extract_file_from_zip(selected_file, selected_file_in_zip, temp_dir)
            
            return {
                'file_path': extracted_path,
                'is_from_zip': True,
                'zip_path': selected_file,
                'file_in_zip': selected_file_in_zip,
                'temp_dir': temp_dir
            }
        except Exception as e:
            # Limpa o diretório temporário em caso de erro
            cleanup_temp_dir(temp_dir)
            raise
    
    # Arquivo normal (não-ZIP)
    return {
        'file_path': selected_file,
        'is_from_zip': False,
        'zip_path': None,
        'file_in_zip': None,
        'temp_dir': None
    }



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
