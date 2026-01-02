import re
import json
import random
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import os
from random_file_picker.core.file_picker import (
    pick_random_file_with_zip_support,
    list_files_in_zip,
    extract_file_from_zip,
    get_temp_extraction_dir,
)


class SequentialFileTracker:
    """Rastreador de arquivos lidos em sequência."""
    
    def __init__(self, tracker_file: str = "read_files_tracker.json"):
        self.tracker_file = Path(tracker_file)
        self.data = self._load_tracker()
    
    def _load_tracker(self) -> Dict:
        """Carrega o arquivo de rastreamento."""
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_tracker(self):
        """Salva o arquivo de rastreamento."""
        try:
            with open(self.tracker_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar rastreamento: {e}")
    
    def mark_as_read(self, file_path: str):
        """Marca um arquivo como lido."""
        folder = str(Path(file_path).parent)
        if folder not in self.data:
            self.data[folder] = []
        
        filename = Path(file_path).name
        if filename not in self.data[folder]:
            self.data[folder].append(filename)
            self._save_tracker()
    
    def is_read(self, file_path: str) -> bool:
        """Verifica se um arquivo já foi lido."""
        folder = str(Path(file_path).parent)
        filename = Path(file_path).name
        return folder in self.data and filename in self.data[folder]
    
    def get_read_files(self, folder: str) -> List[str]:
        """Retorna lista de arquivos lidos em uma pasta."""
        return self.data.get(str(folder), [])
    
    def reset_folder(self, folder: str):
        """Reseta o rastreamento de uma pasta."""
        folder_str = str(folder)
        if folder_str in self.data:
            del self.data[folder_str]
            self._save_tracker()


def extract_number_from_filename(filename: str) -> Optional[Tuple[float, str]]:
    """
    Extrai número de ordenação do nome do arquivo.
    Suporta diversos formatos: 001, #001, 01 de 10, Cap 1, I, II, III, etc.
    
    Args:
        filename: Nome do arquivo
        
    Returns:
        Tupla (número, tipo) onde tipo indica o formato encontrado, ou None
    """
    # Remove extensão
    name_without_ext = Path(filename).stem
    
    # Padrões de numeração
    patterns = [
        # Números decimais puros: 001, 01, 1
        (r'^(\d+)', 'decimal'),
        # Com prefixo #: #001, #01, #1
        (r'#(\d+)', 'hash_decimal'),
        # Padrão "X de Y" ou "X of Y": 01 de 10, 1 of 10
        (r'(\d+)\s*(?:de|of|/)\s*\d+', 'x_of_y'),
        # Capítulo/Chapter/Cap/Ch seguido de número
        (r'(?:cap(?:itulo)?|ch(?:apter)?)[.\s-]*(\d+)', 'chapter'),
        # Volume/Vol seguido de número
        (r'(?:vol(?:ume)?)[.\s-]*(\d+)', 'volume'),
        # Parte/Part seguido de número
        (r'(?:part(?:e)?)[.\s-]*(\d+)', 'part'),
        # Episódio/Episode/Ep seguido de número
        (r'(?:ep(?:isode)?|episodio)[.\s-]*(\d+)', 'episode'),
    ]
    
    # Tenta cada padrão
    for pattern, type_name in patterns:
        match = re.search(pattern, name_without_ext, re.IGNORECASE)
        if match:
            try:
                number = float(match.group(1))
                return (number, type_name)
            except:
                continue
    
    # Tenta números romanos (I, II, III, IV, V, etc.)
    roman_pattern = r'\b(M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3}))\b'
    match = re.search(roman_pattern, name_without_ext, re.IGNORECASE)
    if match:
        roman_str = match.group(1).upper()
        decimal = roman_to_decimal(roman_str)
        if decimal:
            return (decimal, 'roman')
    
    # Tenta encontrar qualquer número no nome
    numbers = re.findall(r'\d+', name_without_ext)
    if numbers:
        # Usa o primeiro número encontrado
        try:
            return (float(numbers[0]), 'fallback')
        except:
            pass
    
    return None


def roman_to_decimal(roman: str) -> Optional[int]:
    """Converte número romano para decimal."""
    roman_values = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50,
        'C': 100, 'D': 500, 'M': 1000
    }
    
    try:
        total = 0
        prev_value = 0
        
        for char in reversed(roman.upper()):
            if char not in roman_values:
                return None
            
            value = roman_values[char]
            if value < prev_value:
                total -= value
            else:
                total += value
            prev_value = value
        
        return total
    except:
        return None


def extract_collection_name(filename: str) -> str:
    """
    Extrai o nome base da coleção, removendo a numeração.
    
    Args:
        filename: Nome do arquivo
        
    Returns:
        Nome base da coleção
    """
    # Remove extensão
    name_without_ext = Path(filename).stem
    
    # Padrões para remover (em ordem de prioridade)
    patterns_to_remove = [
        r'#\d+.*$',  # Remove #001 e tudo depois
        r'\d+\s*(?:de|of|/)\s*\d+.*$',  # Remove "01 de 10" e tudo depois
        r'(?:cap(?:itulo)?|ch(?:apter)?)[.\s-]*\d+.*$',  # Remove Chapter 1 e tudo depois
        r'(?:vol(?:ume)?)[.\s-]*\d+.*$',  # Remove Volume 1 e tudo depois
        r'(?:part(?:e)?)[.\s-]*\d+.*$',  # Remove Parte 1 e tudo depois
        r'(?:ep(?:isode)?|episodio)[.\s-]*\d+.*$',  # Remove Episódio 1 e tudo depois
        r'\b(M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3}))\b.*$',  # Remove romanos
        r'\d+.*$',  # Remove números no final
    ]
    
    collection_name = name_without_ext
    
    for pattern in patterns_to_remove:
        match = re.search(pattern, collection_name, re.IGNORECASE)
        if match:
            collection_name = collection_name[:match.start()].strip()
            break
    
    # Remove caracteres comuns de separação no final
    collection_name = re.sub(r'[\s\-_.#]+$', '', collection_name)
    
    return collection_name if collection_name else name_without_ext


def analyze_folder_sequence(folder_path: Path, exclude_prefix: str = "_L_", keywords: List[str] = None) -> Optional[List[Dict]]:
    """
    Analisa se os arquivos em uma pasta seguem uma sequência ordenada.
    Agrupa arquivos por coleção (nome base) para suportar múltiplas coleções na mesma pasta.
    
    Args:
        folder_path: Caminho da pasta
        exclude_prefix: Prefixo de arquivos a ignorar
        keywords: Lista de palavras-chave para filtrar arquivos
        
    Returns:
        Lista de dicionários com informações das sequências por coleção, ou None se não houver padrão
    """
    files_with_numbers = []
    
    try:
        # Lista todos os arquivos da pasta (não recursivo)
        for file_path in folder_path.iterdir():
            if not file_path.is_file():
                continue
            
            filename = file_path.name
            
            # Ignora arquivos com prefixo de exclusão
            if filename.startswith(exclude_prefix):
                continue
            
            # Filtra por palavras-chave se fornecidas
            if keywords:
                file_name_lower = filename.lower()
                # Verifica se ao menos UMA palavra-chave está no nome do arquivo
                if not any(keyword in file_name_lower for keyword in keywords):
                    continue
            
            # Tenta extrair número e nome da coleção
            result = extract_number_from_filename(filename)
            if result:
                number, num_type = result
                collection_name = extract_collection_name(filename)
                
                files_with_numbers.append({
                    'path': str(file_path),
                    'filename': filename,
                    'number': number,
                    'type': num_type,
                    'collection': collection_name
                })
        
        # Precisa ter pelo menos 2 arquivos para considerar uma sequência
        if len(files_with_numbers) < 2:
            return None
        
        # Agrupa arquivos por coleção
        collections = {}
        for item in files_with_numbers:
            collection_name = item['collection']
            if collection_name not in collections:
                collections[collection_name] = []
            collections[collection_name].append(item)
        
        # Analisa cada coleção separadamente
        valid_sequences = []
        
        for collection_name, collection_files in collections.items():
            # Precisa ter pelo menos 2 arquivos na coleção
            if len(collection_files) < 2:
                continue
            
            # Verifica se há um tipo dominante de numeração na coleção
            type_counts = {}
            for item in collection_files:
                num_type = item['type']
                type_counts[num_type] = type_counts.get(num_type, 0) + 1
            
            # Tipo mais comum
            dominant_type = max(type_counts.items(), key=lambda x: x[1])[0]
            
            # Filtra apenas arquivos do tipo dominante
            sequence_files = [f for f in collection_files if f['type'] == dominant_type]
            
            # Ordena por número
            sequence_files.sort(key=lambda x: x['number'])
            
            # Adiciona a sequência válida
            if len(sequence_files) >= 2:
                valid_sequences.append({
                    'folder': str(folder_path),
                    'collection': collection_name,
                    'type': dominant_type,
                    'files': sequence_files,
                    'count': len(sequence_files)
                })
        
        # Retorna as sequências válidas (pode haver múltiplas coleções)
        return valid_sequences if valid_sequences else None
        
    except Exception as e:
        print(f"Erro ao analisar pasta {folder_path}: {e}")
    
    return None


def get_next_unread_file(sequences: List[Dict], tracker: SequentialFileTracker, keywords: List[str] = None) -> Optional[Tuple[str, Dict]]:
    """
    Retorna o próximo arquivo não lido em uma das sequências.
    Seleciona aleatoriamente uma coleção com arquivos não lidos.
    
    Args:
        sequences: Lista de sequências detectadas
        tracker: Rastreador de arquivos lidos
        keywords: Lista de palavras-chave para filtrar arquivos
        
    Returns:
        Tupla (caminho do arquivo, info da sequência) ou None se não houver
    """
    if not sequences:
        return None
    
    # Encontra coleções com arquivos não lidos
    collections_with_unread = []
    
    for sequence in sequences:
        # Procura o primeiro arquivo não lido nesta coleção
        for file_info in sequence['files']:
            file_path = file_info['path']
            
            # Verifica se já foi lido
            if tracker.is_read(file_path):
                continue
            
            # Filtra por palavras-chave se fornecidas
            if keywords:
                file_name = Path(file_path).name.lower()
                # Verifica se ao menos UMA palavra-chave está no nome do arquivo
                if not any(keyword in file_name for keyword in keywords):
                    continue
            
            # Arquivo válido encontrado
            collections_with_unread.append({
                'sequence': sequence,
                'next_file': file_path,
                'file_info': file_info
            })
            break  # Encontrou, passa para próxima coleção
    
    if not collections_with_unread:
        return None
    
    # Seleciona aleatoriamente uma coleção com arquivos não lidos
    selected = random.choice(collections_with_unread)
    
    return selected['next_file'], selected['sequence'], selected['file_info']


def select_file_with_sequence_logic(folders: List[str], exclude_prefix: str = "_L_", 
                                    use_sequence: bool = True, keywords: List[str] = None,
                                    process_zip: bool = True) -> Tuple[Dict, Dict]:
    """
    Seleciona um arquivo considerando lógica de sequência, com suporte a ZIP.
    
    Args:
        folders: Lista de pastas para buscar
        exclude_prefix: Prefixo de arquivos a ignorar
        use_sequence: Se True, usa lógica de sequência quando detectada
        keywords: Lista de palavras-chave para filtrar arquivos
        process_zip: Se True, processa arquivos ZIP; se False, trata ZIPs como arquivos normais
        
    Returns:
        Tupla (dicionário com info do arquivo, informações sobre a seleção)
        O dicionário do arquivo contém:
            - file_path: Caminho do arquivo selecionado
            - is_from_zip: True se veio de um ZIP
            - zip_path: Caminho do ZIP original (se aplicável)
            - file_in_zip: Nome do arquivo dentro do ZIP (se aplicável)
            - temp_dir: Diretório temporário (se aplicável)
    """
    tracker = SequentialFileTracker()
    info = {
        'method': 'random',
        'sequence_detected': False,
        'folder': None,
        'sequence_info': None,
        'total_files_found': 0
    }
    
    # Coleta todas as pastas únicas (não recursivo para lógica de sequência)
    unique_folders = set()
    
    for base_folder in folders:
        base_path = Path(base_folder)
        if not base_path.exists() or not base_path.is_dir():
            continue
        
        # Adiciona a pasta base
        unique_folders.add(base_path)
        
        # Adiciona subpastas
        try:
            for item in base_path.rglob('*'):
                if item.is_dir() and not any(part.startswith('.') for part in item.parts):
                    unique_folders.add(item)
        except (OSError, PermissionError):
            continue
    
    if not unique_folders:
        return {'file_path': None, 'is_from_zip': False, 'zip_path': None, 'file_in_zip': None, 'temp_dir': None}, info
    
    # Converte para lista e embaralha
    folder_list = list(unique_folders)
    random.shuffle(folder_list)
    
    # Se usar lógica de sequência, tenta encontrar pastas com sequências e arquivos não lidos
    if use_sequence:
        for folder in folder_list:
            sequences = analyze_folder_sequence(folder, exclude_prefix, keywords)
            
            if sequences:
                # Há sequências detectadas (pode haver múltiplas coleções)
                result = get_next_unread_file(sequences, tracker, keywords)
                
                if result:
                    # Encontrou próximo arquivo não lido em alguma coleção
                    next_file, selected_sequence, file_info = result
                    
                    info['method'] = 'sequential'
                    info['sequence_detected'] = True
                    info['folder'] = str(folder)
                    info['sequence_info'] = {
                        'type': selected_sequence['type'],
                        'collection': selected_sequence['collection'],
                        'total_files': selected_sequence['count'],
                        'file_number': file_info['number']
                    }
                    
                    # Verifica se é um arquivo ZIP
                    file_result = _process_file_selection(next_file, exclude_prefix, keywords, is_zip_check=process_zip)
                    
                    if file_result:
                        tracker.mark_as_read(next_file)
                        return file_result, info
    
    # Se não encontrou com lógica de sequência, seleciona aleatoriamente
    # Coleta todos os arquivos válidos
    all_files = []
    for folder in folder_list:
        try:
            for file_path in folder.iterdir():
                if not file_path.is_file():
                    continue
                
                if file_path.name.startswith(exclude_prefix):
                    continue
                
                # Filtra por palavras-chave se fornecidas
                if keywords:
                    file_name_lower = file_path.name.lower()
                    # Verifica se ao menos UMA palavra-chave está no nome do arquivo
                    if not any(keyword in file_name_lower for keyword in keywords):
                        continue
                
                all_files.append(str(file_path))
        except (OSError, PermissionError):
            continue
    
    if all_files:
        info['total_files_found'] = len(all_files)
        selected = random.choice(all_files)
        info['folder'] = str(Path(selected).parent)
        
        # IMPORTANTE: Verifica se o arquivo aleatório faz parte de uma sequência
        # e se há um arquivo anterior não lido
        selected_folder = Path(selected).parent
        folder_sequences = analyze_folder_sequence(selected_folder, exclude_prefix, keywords)
        
        if folder_sequences:
            # O arquivo aleatório faz parte de uma sequência!
            # Vamos buscar o primeiro não lido da sequência
            temp_tracker = SequentialFileTracker()
            seq_result = get_next_unread_file(folder_sequences, temp_tracker, keywords)
            
            if seq_result:
                # Encontrou um arquivo não lido anterior na sequência
                next_file, selected_sequence, file_info = seq_result
                
                # Atualiza info para indicar que sequência foi detectada
                info['method'] = 'sequential'
                info['sequence_detected'] = True
                info['sequence_info'] = {
                    'type': selected_sequence['type'],
                    'collection': selected_sequence['collection'],
                    'total_files': selected_sequence['count'],
                    'file_number': file_info['number']
                }
                
                print(f"Arquivo aleatório '{Path(selected).name}' faz parte de sequência '{selected_sequence['collection']}'")
                print(f"Selecionando primeiro não lido: '{Path(next_file).name}'")
                
                # Usa o arquivo da sequência em vez do aleatório
                selected = next_file
        
        # Verifica se é um arquivo ZIP
        file_result = _process_file_selection(selected, exclude_prefix, keywords, is_zip_check=process_zip)
        
        if file_result:
            return file_result, info
    
    return {'file_path': None, 'is_from_zip': False, 'zip_path': None, 'file_in_zip': None, 'temp_dir': None}, info


def _process_file_selection(file_path: str, exclude_prefix: str, keywords: List[str], is_zip_check: bool = True) -> Optional[Dict]:
    """
    Processa a seleção de um arquivo, verificando se é ZIP e extraindo se necessário.
    
    Args:
        file_path: Caminho do arquivo selecionado
        exclude_prefix: Prefixo a ser excluído
        keywords: Lista de palavras-chave para filtrar
        is_zip_check: Se True, verifica se é ZIP e processa
        
    Returns:
        Dicionário com informações do arquivo ou None se não for válido
    """
    # Se não for ZIP ou não devemos verificar, retorna arquivo normal
    if not is_zip_check or not file_path.lower().endswith('.zip'):
        return {
            'file_path': file_path,
            'is_from_zip': False,
            'zip_path': None,
            'file_in_zip': None,
            'temp_dir': None
        }
    
    # É um arquivo ZIP, processa
    print(f"Arquivo ZIP detectado: {os.path.basename(file_path)}")
    print("Explorando conteúdo do ZIP...")
    
    files_in_zip = list_files_in_zip(file_path, exclude_prefix, keywords)
    
    if not files_in_zip:
        if keywords:
            print(f"Nenhum arquivo válido encontrado no ZIP com as palavras-chave especificadas.")
        else:
            print(f"Nenhum arquivo válido encontrado no ZIP.")
        # Retorna o próprio ZIP
        return {
            'file_path': file_path,
            'is_from_zip': False,
            'zip_path': None,
            'file_in_zip': None,
            'temp_dir': None
        }
    
    # Seleciona aleatoriamente um arquivo do ZIP
    selected_file_in_zip = random.choice(files_in_zip)
    print(f"Arquivo selecionado do ZIP: {os.path.basename(selected_file_in_zip)}")
    
    # Cria diretório temporário
    temp_dir = get_temp_extraction_dir()
    
    try:
        # Extrai o arquivo
        print(f"Extraindo para pasta temporária...")
        extracted_path = extract_file_from_zip(file_path, selected_file_in_zip, temp_dir)
        
        return {
            'file_path': extracted_path,
            'is_from_zip': True,
            'zip_path': file_path,
            'file_in_zip': selected_file_in_zip,
            'temp_dir': temp_dir
        }
    except Exception as e:
        print(f"Erro ao extrair arquivo do ZIP: {e}")
        # Retorna o próprio ZIP em caso de erro
        return {
            'file_path': file_path,
            'is_from_zip': False,
            'zip_path': None,
            'file_in_zip': None,
            'temp_dir': None
        }
