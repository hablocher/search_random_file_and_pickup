"""
Utilitários específicos para Linux.
Identifica aplicativos padrão para abrir arquivos.
"""
import subprocess
import mimetypes
from pathlib import Path
from typing import Dict, Optional
import configparser
import os


def get_default_app_info(file_path: str) -> Dict[str, str]:
    """
    Obtém informações sobre o aplicativo padrão que abrirá o arquivo no Linux.
    
    Args:
        file_path: Caminho completo do arquivo
        
    Returns:
        Dicionário com informações do aplicativo:
        - name: Nome do executável
        - path: Caminho completo do executável (se disponível)
        - display_name: Nome amigável do aplicativo
        - extension: Extensão do arquivo
        - mime_type: Tipo MIME do arquivo
    """
    file_ext = Path(file_path).suffix.lower()
    
    result = {
        'name': 'Desconhecido',
        'path': '',
        'display_name': 'Aplicativo padrão do Linux',
        'extension': file_ext,
        'mime_type': ''
    }
    
    # Obtém o tipo MIME
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        result['mime_type'] = mime_type
    
    try:
        # Método 1: Usa xdg-mime query para obter o .desktop file
        if mime_type:
            desktop_result = subprocess.run(
                ['xdg-mime', 'query', 'default', mime_type],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if desktop_result.returncode == 0 and desktop_result.stdout.strip():
                desktop_file = desktop_result.stdout.strip()
                
                # Procura o arquivo .desktop
                desktop_info = find_desktop_file(desktop_file)
                if desktop_info:
                    result.update(desktop_info)
                    result['extension'] = file_ext
                    result['mime_type'] = mime_type
                    return result
        
        # Método 2: Tenta com gio (GNOME)
        gio_result = subprocess.run(
            ['gio', 'mime', mime_type if mime_type else file_ext],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if gio_result.returncode == 0 and gio_result.stdout:
            # Procura por "Default application:" na saída
            for line in gio_result.stdout.split('\n'):
                if 'Default application:' in line or 'application:' in line:
                    app_name = line.split(':', 1)[1].strip()
                    result['display_name'] = app_name
                    result['name'] = app_name.split()[0] if app_name else 'Desconhecido'
                    break
        
        # Método 3: Tenta através do mimeapps.list
        if result['name'] == 'Desconhecido' and mime_type:
            mimeapps_info = get_app_from_mimeapps(mime_type)
            if mimeapps_info:
                result.update(mimeapps_info)
                
    except Exception as e:
        result['display_name'] = f"Aplicativo padrão para {file_ext}"
    
    return result


def find_desktop_file(desktop_filename: str) -> Optional[Dict[str, str]]:
    """
    Procura e analisa um arquivo .desktop.
    
    Args:
        desktop_filename: Nome do arquivo .desktop (ex: firefox.desktop)
        
    Returns:
        Dicionário com informações do aplicativo ou None
    """
    # Diretórios comuns para arquivos .desktop
    search_paths = [
        Path.home() / '.local' / 'share' / 'applications',
        Path('/usr/share/applications'),
        Path('/usr/local/share/applications'),
        Path('/var/lib/snapd/desktop/applications'),
        Path('/var/lib/flatpak/exports/share/applications'),
    ]
    
    for search_path in search_paths:
        desktop_path = search_path / desktop_filename
        if desktop_path.exists():
            try:
                info = parse_desktop_file(str(desktop_path))
                if info:
                    return info
            except:
                continue
    
    return None


def parse_desktop_file(desktop_path: str) -> Optional[Dict[str, str]]:
    """
    Analisa um arquivo .desktop para extrair informações.
    
    Args:
        desktop_path: Caminho para o arquivo .desktop
        
    Returns:
        Dicionário com informações do aplicativo ou None
    """
    try:
        config = configparser.ConfigParser()
        config.read(desktop_path, encoding='utf-8')
        
        if 'Desktop Entry' in config:
            entry = config['Desktop Entry']
            
            name = entry.get('Name', 'Desconhecido')
            exec_cmd = entry.get('Exec', '')
            
            # Remove parâmetros do comando
            if exec_cmd:
                # Remove %u, %f, %F, %U e outros placeholders
                exec_cmd = exec_cmd.replace('%u', '').replace('%f', '').replace('%F', '').replace('%U', '')
                exec_cmd = exec_cmd.replace('%d', '').replace('%D', '').replace('%n', '').replace('%N', '')
                exec_cmd = exec_cmd.replace('%i', '').replace('%c', '').replace('%k', '')
                exec_cmd = exec_cmd.strip()
                
                # Pega o primeiro comando
                cmd_parts = exec_cmd.split()
                if cmd_parts:
                    exe_name = cmd_parts[0]
                    
                    # Tenta encontrar o caminho completo
                    exe_path = find_executable(exe_name)
                    
                    return {
                        'name': exe_name,
                        'path': exe_path if exe_path else '',
                        'display_name': name
                    }
    except Exception as e:
        pass
    
    return None


def find_executable(exe_name: str) -> Optional[str]:
    """
    Procura o caminho completo de um executável.
    
    Args:
        exe_name: Nome do executável
        
    Returns:
        Caminho completo ou None
    """
    try:
        which_result = subprocess.run(
            ['which', exe_name],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if which_result.returncode == 0 and which_result.stdout.strip():
            return which_result.stdout.strip()
    except:
        pass
    
    return None


def get_app_from_mimeapps(mime_type: str) -> Optional[Dict[str, str]]:
    """
    Busca o aplicativo padrão através do mimeapps.list.
    
    Args:
        mime_type: Tipo MIME (ex: application/pdf)
        
    Returns:
        Dicionário com informações do aplicativo ou None
    """
    mimeapps_paths = [
        Path.home() / '.config' / 'mimeapps.list',
        Path.home() / '.local' / 'share' / 'applications' / 'mimeapps.list',
        Path('/usr/share/applications/mimeapps.list'),
    ]
    
    for mimeapps_path in mimeapps_paths:
        if mimeapps_path.exists():
            try:
                config = configparser.ConfigParser()
                config.read(mimeapps_path, encoding='utf-8')
                
                for section in ['Default Applications', 'Added Associations']:
                    if section in config and mime_type in config[section]:
                        desktop_file = config[section][mime_type].split(';')[0]
                        
                        desktop_info = find_desktop_file(desktop_file)
                        if desktop_info:
                            return desktop_info
            except:
                continue
    
    return None
