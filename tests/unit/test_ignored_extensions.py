"""Testes para funcionalidade de extensões ignoradas."""

import pytest
import tempfile
from pathlib import Path
from src.random_file_picker.core.file_picker import collect_files, list_files_in_zip


class TestIgnoredExtensions:
    """Testes para verificar filtragem por extensões ignoradas."""
    
    def test_collect_files_ignores_extensions(self):
        """Testa que collect_files ignora extensões especificadas."""
        # Cria pasta temporária com arquivos de diferentes extensões
        with tempfile.TemporaryDirectory() as tmpdir:
            test_folder = Path(tmpdir)
            
            # Cria arquivos de teste
            (test_folder / "video.mp4").touch()
            (test_folder / "video.mkv").touch()
            (test_folder / "subtitle.srt").touch()
            (test_folder / "subtitle.sub").touch()
            (test_folder / "readme.txt").touch()
            (test_folder / "info.nfo").touch()
            
            # Busca sem ignorar extensões
            all_files = collect_files(
                folders=[str(test_folder)],
                use_cache=False
            )
            assert len(all_files) == 6, "Deve encontrar todos os 6 arquivos"
            
            # Busca ignorando legendas e textos
            filtered_files = collect_files(
                folders=[str(test_folder)],
                use_cache=False,
                ignored_extensions=['srt', 'sub', 'txt', 'nfo']
            )
            assert len(filtered_files) == 2, "Deve encontrar apenas os 2 vídeos"
            
            # Verifica que apenas vídeos foram retornados
            filtered_names = [Path(f).name for f in filtered_files]
            assert 'video.mp4' in filtered_names
            assert 'video.mkv' in filtered_names
            assert 'subtitle.srt' not in filtered_names
            assert 'subtitle.sub' not in filtered_names
            assert 'readme.txt' not in filtered_names
            assert 'info.nfo' not in filtered_names
    
    def test_ignored_extensions_case_insensitive(self):
        """Testa que extensões ignoradas são case-insensitive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_folder = Path(tmpdir)
            
            # Cria arquivos com extensões em diferentes cases
            (test_folder / "file1.SRT").touch()
            (test_folder / "file2.srt").touch()
            (test_folder / "file3.Srt").touch()
            (test_folder / "video.mp4").touch()
            
            # Ignora .srt em minúscula
            filtered_files = collect_files(
                folders=[str(test_folder)],
                use_cache=False,
                ignored_extensions=['srt']
            )
            
            assert len(filtered_files) == 1, "Deve ignorar todos os .srt independente do case"
            assert Path(filtered_files[0]).name == 'video.mp4'
    
    def test_ignored_extensions_with_dot(self):
        """Testa que extensões podem ser especificadas com ou sem ponto."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_folder = Path(tmpdir)
            
            (test_folder / "subtitle.srt").touch()
            (test_folder / "video.mp4").touch()
            
            # Testa com ponto
            filtered1 = collect_files(
                folders=[str(test_folder)],
                use_cache=False,
                ignored_extensions=['.srt']
            )
            
            # Testa sem ponto
            filtered2 = collect_files(
                folders=[str(test_folder)],
                use_cache=False,
                ignored_extensions=['srt']
            )
            
            # Ambos devem dar o mesmo resultado
            assert len(filtered1) == 1
            assert len(filtered2) == 1
            assert filtered1 == filtered2
    
    def test_ignored_extensions_empty_list(self):
        """Testa que lista vazia não ignora nada."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_folder = Path(tmpdir)
            
            (test_folder / "file1.txt").touch()
            (test_folder / "file2.srt").touch()
            
            # Lista vazia não deve ignorar nada
            files = collect_files(
                folders=[str(test_folder)],
                use_cache=False,
                ignored_extensions=[]
            )
            
            assert len(files) == 2
    
    def test_ignored_extensions_none(self):
        """Testa que None não ignora nada."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_folder = Path(tmpdir)
            
            (test_folder / "file1.txt").touch()
            (test_folder / "file2.srt").touch()
            
            # None não deve ignorar nada
            files = collect_files(
                folders=[str(test_folder)],
                use_cache=False,
                ignored_extensions=None
            )
            
            assert len(files) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
