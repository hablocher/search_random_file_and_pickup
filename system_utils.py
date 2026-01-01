"""
Módulo unificado de utilitários de sistema.
Detecta o sistema operacional e importa a biblioteca apropriada.
"""
import platform
from typing import Dict

# Detecta o sistema operacional
_system = platform.system()

if _system == "Windows":
    from system_utils_windows import get_default_app_info
elif _system == "Linux":
    from system_utils_linux import get_default_app_info
else:
    # Fallback para sistemas não suportados (macOS, etc)
    def get_default_app_info(file_path: str) -> Dict[str, str]:
        """
        Fallback para sistemas não suportados.
        
        Args:
            file_path: Caminho completo do arquivo
            
        Returns:
            Dicionário com informações básicas
        """
        from pathlib import Path
        file_ext = Path(file_path).suffix.lower()
        
        return {
            'name': 'Desconhecido',
            'path': '',
            'display_name': f'Aplicativo padrão do {_system}',
            'extension': file_ext
        }


def format_app_info_for_log(app_info: Dict[str, str]) -> str:
    """
    Formata as informações do aplicativo para exibição no log.
    
    Args:
        app_info: Dicionário com informações do aplicativo
        
    Returns:
        String formatada para log
    """
    lines = []
    
    if app_info.get('display_name'):
        lines.append(f"  Aplicativo: {app_info['display_name']}")
    
    if app_info.get('name') and app_info['name'] != 'Desconhecido':
        lines.append(f"  Executável: {app_info['name']}")
    
    if app_info.get('path'):
        lines.append(f"  Caminho: {app_info['path']}")
    
    if app_info.get('mime_type'):
        lines.append(f"  Tipo MIME: {app_info['mime_type']}")
    
    if app_info.get('extension'):
        lines.append(f"  Extensão: {app_info['extension']}")
    
    return '\n'.join(lines) if lines else "  Informações não disponíveis"


__all__ = ['get_default_app_info', 'format_app_info_for_log']
