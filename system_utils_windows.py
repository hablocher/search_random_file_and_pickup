"""
Utilitários específicos para Windows.
Identifica aplicativos padrão para abrir arquivos.
"""
import subprocess
import winreg
from pathlib import Path
from typing import Dict, Optional


def get_default_app_info(file_path: str) -> Dict[str, str]:
    """
    Obtém informações sobre o aplicativo padrão que abrirá o arquivo no Windows.
    
    Args:
        file_path: Caminho completo do arquivo
        
    Returns:
        Dicionário com informações do aplicativo:
        - name: Nome do executável
        - path: Caminho completo do executável
        - display_name: Nome amigável do aplicativo
        - extension: Extensão do arquivo
    """
    file_ext = Path(file_path).suffix.lower()
    
    result = {
        'name': 'Desconhecido',
        'path': '',
        'display_name': 'Aplicativo padrão do Windows',
        'extension': file_ext
    }
    
    if not file_ext:
        return result
    
    try:
        # Método 1: Usa assoc e ftype para obter o comando
        assoc_result = subprocess.run(
            ['assoc', file_ext], 
            capture_output=True, 
            text=True, 
            timeout=2,
            shell=True
        )
        
        if assoc_result.returncode == 0 and assoc_result.stdout:
            # Obtém o tipo de arquivo (ex: "Applications.cbr")
            file_type = assoc_result.stdout.strip().split('=')[1] if '=' in assoc_result.stdout else None
            
            if file_type:
                # Obtém o comando associado ao tipo
                ftype_result = subprocess.run(
                    ['ftype', file_type], 
                    capture_output=True, 
                    text=True, 
                    timeout=2,
                    shell=True
                )
                
                if ftype_result.returncode == 0 and ftype_result.stdout:
                    # Extrai o caminho do executável
                    command = ftype_result.stdout.strip().split('=', 1)[1] if '=' in ftype_result.stdout else None
                    
                    if command:
                        # Remove aspas e parâmetros
                        if '"' in command:
                            exe_path = command.split('"')[1]
                        else:
                            exe_path = command.split()[0]
                        
                        if Path(exe_path).exists():
                            result['path'] = exe_path
                            result['name'] = Path(exe_path).name
                            
                            # Tenta obter o nome amigável do registro
                            try:
                                display_name = get_app_display_name_from_registry(exe_path)
                                if display_name:
                                    result['display_name'] = display_name
                                else:
                                    result['display_name'] = Path(exe_path).stem
                            except:
                                result['display_name'] = Path(exe_path).stem
                        else:
                            result['name'] = Path(exe_path).name
                            result['display_name'] = Path(exe_path).stem
        
        # Método 2: Tenta através do registro do Windows
        if result['name'] == 'Desconhecido':
            try:
                reg_info = get_app_from_registry(file_ext)
                if reg_info:
                    result.update(reg_info)
            except:
                pass
                
    except Exception as e:
        result['display_name'] = f"Aplicativo padrão para {file_ext}"
    
    return result


def get_app_from_registry(file_ext: str) -> Optional[Dict[str, str]]:
    """
    Busca o aplicativo padrão através do registro do Windows.
    
    Args:
        file_ext: Extensão do arquivo (ex: .cbr)
        
    Returns:
        Dicionário com informações do aplicativo ou None
    """
    try:
        # Abre a chave do registro para a extensão
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, file_ext) as key:
            # Obtém o ProgID
            prog_id = winreg.QueryValue(key, None)
            
            if prog_id:
                # Abre a chave do ProgID
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\shell\\open\\command") as cmd_key:
                    command = winreg.QueryValue(cmd_key, None)
                    
                    if command:
                        # Extrai o executável
                        if '"' in command:
                            exe_path = command.split('"')[1]
                        else:
                            exe_path = command.split()[0]
                        
                        if Path(exe_path).exists():
                            return {
                                'name': Path(exe_path).name,
                                'path': exe_path,
                                'display_name': Path(exe_path).stem,
                                'extension': file_ext
                            }
    except:
        pass
    
    return None


def get_app_display_name_from_registry(exe_path: str) -> Optional[str]:
    """
    Tenta obter o nome amigável do aplicativo do registro do Windows.
    
    Args:
        exe_path: Caminho do executável
        
    Returns:
        Nome amigável ou None
    """
    try:
        # Tenta através do App Paths
        exe_name = Path(exe_path).name
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{exe_name}") as key:
            # Tenta obter o nome do registro
            try:
                display_name = winreg.QueryValueEx(key, "")[0]
                if display_name and display_name != exe_path:
                    return Path(display_name).stem
            except:
                pass
    except:
        pass
    
    # Tenta pelo nome do executável sem extensão
    try:
        return Path(exe_path).stem.replace('_', ' ').replace('-', ' ').title()
    except:
        return None


def get_app_version(exe_path: str) -> Optional[str]:
    """
    Tenta obter a versão do aplicativo (funcionalidade futura).
    
    Args:
        exe_path: Caminho do executável
        
    Returns:
        Versão ou None
    """
    # Pode ser implementado usando pywin32 ou outras bibliotecas
    return None
