"""
Testes para verificar se analyze_folder_sequence e get_next_unread_file respeitam o modo AND/OR de palavras-chave
"""

import unittest
from pathlib import Path
import tempfile
import shutil
from src.random_file_picker.core.sequential_selector import analyze_folder_sequence, get_next_unread_file, SequentialFileTracker


class TestSequentialKeywordModes(unittest.TestCase):
    """Testes para verificar que analyze_folder_sequence respeita modos AND e OR"""

    def setUp(self):
        """Cria pasta temporária para testes"""
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Remove pasta temporária"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_keyword_mode_or_finds_any_match(self):
        """Testa modo OR - deve encontrar arquivos que tenham QUALQUER palavra-chave"""
        # Cria arquivos que formam sequências válidas
        file1 = self.temp_dir / "Marvel Team-Up Episode 01.cbr"
        file2 = self.temp_dir / "Marvel Team-Up Episode 02.cbr"
        file3 = self.temp_dir / "Marvel Team-Up Episode 03.cbr"
        file4 = self.temp_dir / "Capitão Marvel Episode 01.cbr"  # Tem MARVEL mas não TEAM-UP
        file5 = self.temp_dir / "Capitão Marvel Episode 02.cbr"
        file6 = self.temp_dir / "Spider-Man Episode 01.cbr"  # Não tem nenhuma palavra-chave
        file7 = self.temp_dir / "Spider-Man Episode 02.cbr"
        
        for file in [file1, file2, file3, file4, file5, file6, file7]:
            file.touch()
        
        # Modo OR - deve encontrar arquivos com MARVEL ou TEAM-UP
        sequences_or = analyze_folder_sequence(
            self.temp_dir,
            exclude_prefix="_L_",
            keywords=['MARVEL', 'TEAM-UP'],
            keywords_match_all=False  # Modo OR
        )
        
        # Deve encontrar file1, file2, file3, file4, file5 (5 arquivos, excluindo Spider-Man)
        self.assertIsNotNone(sequences_or, "Deve detectar sequências no modo OR")
        
        all_files = []
        for seq in sequences_or:
            all_files.extend([f['filename'] for f in seq['files']])
        
        # Deve ter 5 arquivos (excluindo Spider-Man)
        self.assertEqual(len(all_files), 5, f"Modo OR deve encontrar 5 arquivos, encontrou {len(all_files)}")
        
        # Verifica que Spider-Man não está na lista
        spider_files = [f for f in all_files if 'Spider-Man' in f]
        self.assertEqual(len(spider_files), 0, "Spider-Man não deveria estar na lista (não tem palavras-chave)")

    def test_keyword_mode_and_requires_all_matches(self):
        """Testa modo AND - deve encontrar APENAS arquivos que tenham TODAS as palavras-chave"""
        # Cria arquivos que formam sequências válidas
        file1 = self.temp_dir / "Marvel Team-Up Episode 01.cbr"  # Tem MARVEL e TEAM-UP
        file2 = self.temp_dir / "Marvel Team-Up Episode 02.cbr"  # Tem MARVEL e TEAM-UP
        file3 = self.temp_dir / "Marvel Team-Up Episode 03.cbr"  # Tem MARVEL e TEAM-UP
        file4 = self.temp_dir / "Capitão Marvel Episode 01.cbr"  # Tem MARVEL mas não TEAM-UP
        file5 = self.temp_dir / "Capitão Marvel Episode 02.cbr"
        file6 = self.temp_dir / "Spider-Man Team-Up Episode 01.cbr"  # Tem TEAM-UP mas não MARVEL
        file7 = self.temp_dir / "Spider-Man Team-Up Episode 02.cbr"
        
        for file in [file1, file2, file3, file4, file5, file6, file7]:
            file.touch()
        
        # Modo AND - deve encontrar APENAS arquivos com MARVEL E TEAM-UP
        sequences_and = analyze_folder_sequence(
            self.temp_dir,
            exclude_prefix="_L_",
            keywords=['MARVEL', 'TEAM-UP'],
            keywords_match_all=True  # Modo AND
        )
        
        # Deve encontrar apenas file1, file2, file3 (3 arquivos)
        self.assertIsNotNone(sequences_and, "Deve detectar sequência no modo AND")
        
        all_files = []
        for seq in sequences_and:
            all_files.extend([f['filename'] for f in seq['files']])
        
        # Deve ter apenas 3 arquivos (Marvel Team-Up 01, 02, 03)
        self.assertEqual(len(all_files), 3, f"Modo AND deve encontrar apenas 3 arquivos, encontrou {len(all_files)}: {all_files}")
        
        # Verifica que todos têm MARVEL e TEAM-UP
        for filename in all_files:
            self.assertIn('Marvel Team-Up', filename, f"Arquivo {filename} deveria ter 'Marvel Team-Up'")
        
        # Verifica que Capitão Marvel não está na lista
        capitao_files = [f for f in all_files if 'Capitão Marvel' in f]
        self.assertEqual(len(capitao_files), 0, "Capitão Marvel não deveria estar na lista (falta TEAM-UP)")
        
        # Verifica que Spider-Man Team-Up não está na lista
        spiderman_files = [f for f in all_files if 'Spider-Man' in f]
        self.assertEqual(len(spiderman_files), 0, "Spider-Man Team-Up não deveria estar na lista (falta MARVEL)")

    def test_keyword_mode_and_case_insensitive(self):
        """Testa que o modo AND é case-insensitive"""
        # Cria arquivos com mesmo nome mas variações nas palavras-chave
        file1 = self.temp_dir / "Marvel Team-Up Episode 01.cbr"
        file2 = self.temp_dir / "Marvel Team-Up Episode 02.cbr"
        file3 = self.temp_dir / "Marvel Team-Up Episode 03.cbr"
        
        for file in [file1, file2, file3]:
            file.touch()
        
        # Modo AND com palavras-chave em diferentes casos
        # Deve encontrar arquivos independente da capitalização da palavra-chave
        sequences_upper = analyze_folder_sequence(
            self.temp_dir,
            exclude_prefix="_L_",
            keywords=['MARVEL', 'TEAM-UP'],  # MAIÚSCULAS
            keywords_match_all=True
        )
        
        sequences_lower = analyze_folder_sequence(
            self.temp_dir,
            exclude_prefix="_L_",
            keywords=['marvel', 'team-up'],  # minúsculas
            keywords_match_all=True
        )
        
        sequences_mixed = analyze_folder_sequence(
            self.temp_dir,
            exclude_prefix="_L_",
            keywords=['MaRvEl', 'TeAm-Up'],  # case misto
            keywords_match_all=True
        )
        
        self.assertIsNotNone(sequences_upper, "Deve detectar sequência com keywords em MAIÚSCULAS")
        self.assertIsNotNone(sequences_lower, "Deve detectar sequência com keywords em minúsculas")
        self.assertIsNotNone(sequences_mixed, "Deve detectar sequência com keywords em case misto")
        
        # Todos devem retornar o mesmo número de arquivos
        files_upper = []
        for seq in sequences_upper:
            files_upper.extend([f['filename'] for f in seq['files']])
        
        files_lower = []
        for seq in sequences_lower:
            files_lower.extend([f['filename'] for f in seq['files']])
        
        files_mixed = []
        for seq in sequences_mixed:
            files_mixed.extend([f['filename'] for f in seq['files']])
        
        # Deve encontrar todos os 3 arquivos em cada caso
        self.assertEqual(len(files_upper), 3, "Deve encontrar 3 arquivos com keywords em MAIÚSCULAS")
        self.assertEqual(len(files_lower), 3, "Deve encontrar 3 arquivos com keywords em minúsculas")
        self.assertEqual(len(files_mixed), 3, "Deve encontrar 3 arquivos com keywords em case misto")

    def test_get_next_unread_file_respects_and_mode(self):
        """Testa que get_next_unread_file respeita o modo AND"""
        # Cria arquivos
        file1 = self.temp_dir / "Marvel Team-Up Episode 01.cbr"
        file2 = self.temp_dir / "Marvel Team-Up Episode 02.cbr"
        file3 = self.temp_dir / "Capitão Marvel Episode 01.cbr"
        file4 = self.temp_dir / "Capitão Marvel Episode 02.cbr"
        
        for file in [file1, file2, file3, file4]:
            file.touch()
        
        # Analisa sem keywords para obter todas as sequências
        sequences = analyze_folder_sequence(
            self.temp_dir,
            exclude_prefix="_L_",
            keywords=None,
            keywords_match_all=False
        )
        
        self.assertIsNotNone(sequences, "Deve detectar sequências")
        
        # Cria tracker vazio (nenhum arquivo lido)
        tracker = SequentialFileTracker()
        
        # Teste modo AND - deve encontrar apenas Marvel Team-Up
        result_and = get_next_unread_file(sequences, tracker, keywords=['MARVEL', 'TEAM-UP'], keywords_match_all=True)
        
        self.assertIsNotNone(result_and, "Deve encontrar arquivo no modo AND")
        next_file, selected_sequence, file_info = result_and
        
        # O arquivo deve ser Marvel Team-Up (não Capitão Marvel)
        self.assertIn('Marvel Team-Up', Path(next_file).name, "Arquivo deve ser Marvel Team-Up")
        self.assertNotIn('Capitão Marvel', Path(next_file).name, "Arquivo não deve ser Capitão Marvel")
        
        # Teste modo OR - deve aceitar tanto Marvel Team-Up quanto Capitão Marvel
        result_or = get_next_unread_file(sequences, tracker, keywords=['MARVEL', 'TEAM-UP'], keywords_match_all=False)
        
        self.assertIsNotNone(result_or, "Deve encontrar arquivo no modo OR")
        next_file_or, _, _ = result_or
        
        # Deve conter MARVEL (ambos contêm)
        self.assertIn('Marvel', Path(next_file_or).name, "Arquivo deve conter 'Marvel'")

    def test_keyword_mode_and_with_single_keyword(self):
        """Testa que modo AND com uma única palavra funciona como OR"""
        file1 = self.temp_dir / "Marvel Episode 01.cbr"
        file2 = self.temp_dir / "Marvel Episode 02.cbr"
        file3 = self.temp_dir / "DC Episode 01.cbr"
        
        for file in [file1, file2, file3]:
            file.touch()
        
        # Modo AND com apenas uma palavra-chave
        sequences = analyze_folder_sequence(
            self.temp_dir,
            exclude_prefix="_L_",
            keywords=['MARVEL'],
            keywords_match_all=True
        )
        
        self.assertIsNotNone(sequences, "Deve detectar sequência")
        
        all_files = []
        for seq in sequences:
            all_files.extend([f['filename'] for f in seq['files']])
        
        # Deve encontrar apenas 2 arquivos Marvel
        self.assertEqual(len(all_files), 2, "Deve encontrar apenas arquivos com MARVEL")
        
        for filename in all_files:
            self.assertIn('Marvel', filename, f"Arquivo {filename} deveria ter 'Marvel'")


if __name__ == '__main__':
    unittest.main()
