"""Gerenciamento de configuração da aplicação."""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class ConfigManager:
    """Gerencia carregamento, salvamento e validação de configurações."""
    
    def __init__(self, config_file: Path):
        """Inicializa o gerenciador de configuração.
        
        Args:
            config_file: Caminho para o arquivo de configuração JSON.
        """
        self.config_file = config_file
        self.initial_config: Dict[str, Any] = {}
        
    def load_config(self) -> Dict[str, Any]:
        """Carrega a configuração do arquivo.
        
        Returns:
            Dicionário com a configuração carregada.
        """
        if not self.config_file.exists():
            return self._get_default_config()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
            return self._get_default_config()
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Salva a configuração no arquivo.
        
        Args:
            config: Dicionário com a configuração a salvar.
            
        Returns:
            True se salvou com sucesso, False caso contrário.
        """
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
            return False
    
    def store_initial_config(self, config: Dict[str, Any]):
        """Armazena configuração inicial para comparação.
        
        Args:
            config: Configuração a ser armazenada.
        """
        self.initial_config = config.copy()
    
    def has_changed(self, current_config: Dict[str, Any]) -> bool:
        """Verifica se a configuração foi alterada.
        
        Args:
            current_config: Configuração atual para comparar.
            
        Returns:
            True se houve mudanças, False caso contrário.
        """
        return current_config != self.initial_config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna configuração padrão.
        
        Returns:
            Dicionário com valores padrão.
        """
        return {
            "folders": [],
            "exclude_prefix": "_L_",
            "open_folder": True,
            "open_file": True,
            "use_sequence": True,
            "history_limit": 5,
            "keywords": "",
            "process_zip": True,
            "file_history": [],
            "last_opened_folder": None
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Valida e corrige configuração se necessário.
        
        Args:
            config: Configuração a validar.
            
        Returns:
            Configuração validada e corrigida.
        """
        default = self._get_default_config()
        validated = {}
        
        # Valida cada campo
        validated['folders'] = config.get('folders', default['folders'])
        if not isinstance(validated['folders'], list):
            validated['folders'] = default['folders']
        
        validated['exclude_prefix'] = config.get('exclude_prefix', default['exclude_prefix'])
        if not isinstance(validated['exclude_prefix'], str):
            validated['exclude_prefix'] = default['exclude_prefix']
        
        validated['open_folder'] = config.get('open_folder', default['open_folder'])
        if not isinstance(validated['open_folder'], bool):
            validated['open_folder'] = default['open_folder']
        
        validated['open_file'] = config.get('open_file', default['open_file'])
        if not isinstance(validated['open_file'], bool):
            validated['open_file'] = default['open_file']
        
        validated['use_sequence'] = config.get('use_sequence', default['use_sequence'])
        if not isinstance(validated['use_sequence'], bool):
            validated['use_sequence'] = default['use_sequence']
        
        validated['history_limit'] = config.get('history_limit', default['history_limit'])
        if not isinstance(validated['history_limit'], int) or not (1 <= validated['history_limit'] <= 50):
            validated['history_limit'] = default['history_limit']
        
        validated['keywords'] = config.get('keywords', default['keywords'])
        if not isinstance(validated['keywords'], str):
            validated['keywords'] = default['keywords']
        
        validated['process_zip'] = config.get('process_zip', default['process_zip'])
        if not isinstance(validated['process_zip'], bool):
            validated['process_zip'] = default['process_zip']
        
        validated['file_history'] = config.get('file_history', default['file_history'])
        if not isinstance(validated['file_history'], list):
            validated['file_history'] = default['file_history']
        
        validated['last_opened_folder'] = config.get('last_opened_folder', default['last_opened_folder'])
        
        return validated
