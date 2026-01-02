"""
Testes para verificar se analyze_folder_sequence respeita extensões ignoradas
"""

import unittest
from pathlib import Path
import tempfile
import shutil
from src.random_file_picker.core.sequential_selector import analyze_folder_sequence


class TestSequentialIgnoredExtensions(unittest.TestCase):
    """Testes para verificar que analyze_folder_sequence ignora extensões especificadas"""

    def setUp(self):
        """Cria pasta temporária para testes"""
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Remove pasta temporária"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_analyze_folder_sequence_ignores_srt_files(self):
        """Testa que analyze_folder_sequence ignora arquivos .srt quando especificado"""
        # Cria arquivos de vídeo em sequência
        video1 = self.temp_dir / "Movie Episode 01.mkv"
        video2 = self.temp_dir / "Movie Episode 02.mkv"
        video3 = self.temp_dir / "Movie Episode 03.mkv"
        
        # Cria arquivos de legenda (que devem ser ignorados)
        sub1 = self.temp_dir / "Movie Episode 01.srt"
        sub2 = self.temp_dir / "Movie Episode 02.srt"
        sub3 = self.temp_dir / "Movie Episode 03.srt"
        
        # Cria todos os arquivos
        for file in [video1, video2, video3, sub1, sub2, sub3]:
            file.touch()
        
        # Analisa sem ignorar extensões - deve encontrar 6 arquivos (3 vídeos + 3 legendas)
        sequences_no_filter = analyze_folder_sequence(self.temp_dir, exclude_prefix="_L_", ignored_extensions=None)
        
        # Analisa ignorando .srt - deve encontrar apenas 3 vídeos
        sequences_with_filter = analyze_folder_sequence(
            self.temp_dir, 
            exclude_prefix="_L_", 
            ignored_extensions=['srt']
        )
        
        # Sem filtro, deve haver 2 coleções (Movie Episode com vídeos e legendas)
        # ou 1 coleção com 6 arquivos (dependendo de como são agrupados)
        self.assertIsNotNone(sequences_no_filter, "Deve detectar sequência sem filtro")
        
        # Com filtro, deve detectar apenas os vídeos
        self.assertIsNotNone(sequences_with_filter, "Deve detectar sequência com vídeos")
        
        # Verifica que os arquivos na sequência NÃO incluem .srt
        all_files_filtered = []
        for seq in sequences_with_filter:
            all_files_filtered.extend([f['filename'] for f in seq['files']])
        
        # Nenhum arquivo .srt deve estar na lista
        for filename in all_files_filtered:
            self.assertFalse(filename.endswith('.srt'), f"Arquivo {filename} não deveria estar na sequência")
        
        # Todos os arquivos devem ser .mkv
        for filename in all_files_filtered:
            self.assertTrue(filename.endswith('.mkv'), f"Arquivo {filename} deveria ser .mkv")

    def test_analyze_folder_sequence_ignores_multiple_extensions(self):
        """Testa que analyze_folder_sequence ignora múltiplas extensões"""
        # Cria arquivos de vídeo em sequência (3 arquivos para garantir detecção)
        video1 = self.temp_dir / "Series Episode 01.mp4"
        video2 = self.temp_dir / "Series Episode 02.mp4"
        video3 = self.temp_dir / "Series Episode 03.mp4"
        
        # Cria arquivos que devem ser ignorados
        sub1 = self.temp_dir / "Series Episode 01.srt"
        sub2 = self.temp_dir / "Series Episode 02.sub"
        sub3 = self.temp_dir / "Series Episode 03.srt"
        nfo = self.temp_dir / "Series.nfo"
        txt = self.temp_dir / "readme.txt"
        
        # Cria todos os arquivos
        for file in [video1, video2, video3, sub1, sub2, sub3, nfo, txt]:
            file.touch()
        
        # Analisa ignorando múltiplas extensões
        sequences = analyze_folder_sequence(
            self.temp_dir,
            exclude_prefix="_L_",
            ignored_extensions=['srt', 'sub', 'nfo', 'txt']
        )
        
        # Deve detectar sequência apenas com vídeos
        self.assertIsNotNone(sequences, "Deve detectar sequência com vídeos")
        
        # Verifica que apenas arquivos .mp4 estão na sequência
        all_files = []
        for seq in sequences:
            all_files.extend([f['filename'] for f in seq['files']])
        
        self.assertEqual(len(all_files), 3, "Deve ter apenas 3 arquivos (os vídeos)")
        
        for filename in all_files:
            self.assertTrue(filename.endswith('.mp4'), f"Arquivo {filename} deveria ser .mp4")

    def test_analyze_folder_sequence_case_insensitive(self):
        """Testa que a comparação de extensões é case-insensitive"""
        # Cria arquivos com extensões em diferentes casos
        video = self.temp_dir / "Movie 01.mkv"
        sub_lower = self.temp_dir / "Movie 01.srt"
        sub_upper = self.temp_dir / "Movie 02.SRT"
        sub_mixed = self.temp_dir / "Movie 03.Srt"
        
        for file in [video, sub_lower, sub_upper, sub_mixed]:
            file.touch()
        
        # Analisa ignorando 'srt' (minúsculo)
        sequences = analyze_folder_sequence(
            self.temp_dir,
            exclude_prefix="_L_",
            ignored_extensions=['srt']
        )
        
        # Deve ter apenas o arquivo de vídeo (se houver sequência)
        # Como temos apenas 1 vídeo, pode não detectar sequência
        # Vamos criar mais vídeos
        video2 = self.temp_dir / "Movie 02.mkv"
        video2.touch()
        
        sequences = analyze_folder_sequence(
            self.temp_dir,
            exclude_prefix="_L_",
            ignored_extensions=['srt']
        )
        
        if sequences:
            all_files = []
            for seq in sequences:
                all_files.extend([f['filename'] for f in seq['files']])
            
            # Nenhum arquivo .srt (em qualquer caso) deve estar presente
            for filename in all_files:
                self.assertFalse(
                    filename.lower().endswith('.srt'),
                    f"Arquivo {filename} com extensão .srt não deveria estar na sequência"
                )


if __name__ == '__main__':
    unittest.main()
