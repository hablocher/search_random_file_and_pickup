"""Testes para validação da lógica de keywords AND/OR."""

import unittest
from pathlib import Path


class TestKeywordFiltering(unittest.TestCase):
    """Testa a lógica de filtragem por keywords."""
    
    def test_keyword_and_logic(self):
        """Testa se o modo AND requer todas as keywords."""
        file_name = "John Wick Chapter 1.mkv"
        file_name_lower = file_name.lower()
        
        # Teste 1: Ambas as palavras presentes - deve passar
        keywords = ["john", "wick"]
        keywords_lower = [kw.lower() for kw in keywords]
        result = all(kw in file_name_lower for kw in keywords_lower)
        self.assertTrue(result, "Deveria encontrar arquivo com 'john' E 'wick'")
        
        # Teste 2: Apenas uma palavra presente - NÃO deve passar
        keywords = ["john", "rambo"]
        keywords_lower = [kw.lower() for kw in keywords]
        result = all(kw in file_name_lower for kw in keywords_lower)
        self.assertFalse(result, "NÃO deveria encontrar arquivo sem 'rambo'")
        
        # Teste 3: Nenhuma palavra presente - NÃO deve passar
        keywords = ["matrix", "neo"]
        keywords_lower = [kw.lower() for kw in keywords]
        result = all(kw in file_name_lower for kw in keywords_lower)
        self.assertFalse(result, "NÃO deveria encontrar arquivo sem 'matrix' nem 'neo'")
        
        # Teste 4: Três palavras, todas presentes - deve passar
        keywords = ["john", "wick", "chapter"]
        keywords_lower = [kw.lower() for kw in keywords]
        result = all(kw in file_name_lower for kw in keywords_lower)
        self.assertTrue(result, "Deveria encontrar arquivo com 'john' E 'wick' E 'chapter'")
        
        # Teste 5: Três palavras, falta uma - NÃO deve passar
        keywords = ["john", "wick", "part"]
        keywords_lower = [kw.lower() for kw in keywords]
        result = all(kw in file_name_lower for kw in keywords_lower)
        self.assertFalse(result, "NÃO deveria encontrar arquivo sem 'part'")
    
    def test_keyword_or_logic(self):
        """Testa se o modo OR requer pelo menos uma keyword."""
        file_name = "John Wick Chapter 1.mkv"
        file_name_lower = file_name.lower()
        
        # Teste 1: Ambas as palavras presentes - deve passar
        keywords = ["john", "wick"]
        keywords_lower = [kw.lower() for kw in keywords]
        result = any(kw in file_name_lower for kw in keywords_lower)
        self.assertTrue(result, "Deveria encontrar arquivo com 'john' OU 'wick'")
        
        # Teste 2: Apenas uma palavra presente - deve passar
        keywords = ["john", "rambo"]
        keywords_lower = [kw.lower() for kw in keywords]
        result = any(kw in file_name_lower for kw in keywords_lower)
        self.assertTrue(result, "Deveria encontrar arquivo com 'john' (mesmo sem 'rambo')")
        
        # Teste 3: Nenhuma palavra presente - NÃO deve passar
        keywords = ["matrix", "neo"]
        keywords_lower = [kw.lower() for kw in keywords]
        result = any(kw in file_name_lower for kw in keywords_lower)
        self.assertFalse(result, "NÃO deveria encontrar arquivo sem 'matrix' nem 'neo'")
        
        # Teste 4: Três palavras, todas presentes - deve passar
        keywords = ["john", "wick", "chapter"]
        keywords_lower = [kw.lower() for kw in keywords]
        result = any(kw in file_name_lower for kw in keywords_lower)
        self.assertTrue(result, "Deveria encontrar arquivo com qualquer das palavras")
        
        # Teste 5: Três palavras, apenas uma presente - deve passar
        keywords = ["john", "matrix", "rambo"]
        keywords_lower = [kw.lower() for kw in keywords]
        result = any(kw in file_name_lower for kw in keywords_lower)
        self.assertTrue(result, "Deveria encontrar arquivo com 'john'")
    
    def test_case_insensitive(self):
        """Testa se a busca é case-insensitive."""
        file_name = "John Wick Chapter 1.mkv"
        file_name_lower = file_name.lower()
        
        # Teste com maiúsculas
        keywords = ["JOHN", "WICK"]
        keywords_lower = [kw.lower() for kw in keywords]
        result = all(kw in file_name_lower for kw in keywords_lower)
        self.assertTrue(result, "Deveria ser case-insensitive")
        
        # Teste com minúsculas
        keywords = ["john", "wick"]
        keywords_lower = [kw.lower() for kw in keywords]
        result = all(kw in file_name_lower for kw in keywords_lower)
        self.assertTrue(result, "Deveria ser case-insensitive")
        
        # Teste com mistura
        keywords = ["JoHn", "WiCk"]
        keywords_lower = [kw.lower() for kw in keywords]
        result = all(kw in file_name_lower for kw in keywords_lower)
        self.assertTrue(result, "Deveria ser case-insensitive")
    
    def test_partial_match(self):
        """Testa se aceita correspondência parcial (substring)."""
        file_name = "Batman_vs_Superman_2016.mkv"
        file_name_lower = file_name.lower()
        
        # Teste com palavra completa
        keywords = ["batman"]
        keywords_lower = [kw.lower() for kw in keywords]
        result = any(kw in file_name_lower for kw in keywords_lower)
        self.assertTrue(result, "Deveria encontrar 'batman'")
        
        # Teste com prefixo
        keywords = ["bat"]
        keywords_lower = [kw.lower() for kw in keywords]
        result = any(kw in file_name_lower for kw in keywords_lower)
        self.assertTrue(result, "Deveria encontrar 'bat' como prefixo de 'batman'")
        
        # Teste com sufixo
        keywords = ["man"]
        keywords_lower = [kw.lower() for kw in keywords]
        result = any(kw in file_name_lower for kw in keywords_lower)
        self.assertTrue(result, "Deveria encontrar 'man' como sufixo de 'batman' e 'superman'")
        
        # Teste com substring no meio
        keywords = ["super"]
        keywords_lower = [kw.lower() for kw in keywords]
        result = any(kw in file_name_lower for kw in keywords_lower)
        self.assertTrue(result, "Deveria encontrar 'super' em 'superman'")
    
    def test_special_characters(self):
        """Testa se lida bem com caracteres especiais."""
        file_name = "Spider-Man_Home.Coming.2017.1080p.mkv"
        file_name_lower = file_name.lower()
        
        # Teste com hífen
        keywords = ["spider", "man"]
        keywords_lower = [kw.lower() for kw in keywords]
        result = all(kw in file_name_lower for kw in keywords_lower)
        self.assertTrue(result, "Deveria encontrar 'spider' e 'man' separados por hífen")
        
        # Teste com underscore
        keywords = ["home", "coming"]
        keywords_lower = [kw.lower() for kw in keywords]
        result = all(kw in file_name_lower for kw in keywords_lower)
        self.assertTrue(result, "Deveria encontrar 'home' e 'coming' com underscore/ponto")
        
        # Teste com número
        keywords = ["2017"]
        keywords_lower = [kw.lower() for kw in keywords]
        result = any(kw in file_name_lower for kw in keywords_lower)
        self.assertTrue(result, "Deveria encontrar '2017'")


if __name__ == '__main__':
    unittest.main()
