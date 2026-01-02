"""Testes para validar as melhorias na busca do TMDb."""

import pytest
from src.random_file_picker.utils.movie_poster import MoviePosterFetcher


class TestMovieNameCleaning:
    """Testes para limpeza de nomes de arquivos."""
    
    def test_clean_name_with_portuguese_terms(self):
        """Testa remoção de termos em português."""
        fetcher = MoviePosterFetcher()
        
        test_cases = [
            ("O Poderoso Chefão (1972) Dual Audio.mkv", "O Poderoso Chefão", 1972),
            ("Cidade de Deus 2002 Dublado 1080p.mp4", "Cidade de Deus", 2002),
            ("Tropa de Elite (2007) Nacional BluRay.avi", "Tropa de Elite", 2007),
            ("Matrix (1999) Legendado PTBR.mkv", "Matrix", 1999),
        ]
        
        for filename, expected_name, expected_year in test_cases:
            name, year = fetcher._clean_movie_name(filename)
            assert name == expected_name, f"Failed for {filename}: got '{name}', expected '{expected_name}'"
            assert year == expected_year, f"Failed year for {filename}: got {year}, expected {expected_year}"
    
    def test_clean_name_with_special_formats(self):
        """Testa remoção de formatos especiais."""
        fetcher = MoviePosterFetcher()
        
        test_cases = [
            ("Avatar.2009.4K.HDR10.HEVC.mkv", "Avatar", 2009),
            ("Inception 2010 IMAX 1080p x265-RARBG.mp4", "Inception", 2010),
            ("Interstellar.2014.2160p.WEB-DL.DDP5.1.Atmos.mkv", "Interstellar", 2014),
        ]
        
        for filename, expected_name, expected_year in test_cases:
            name, year = fetcher._clean_movie_name(filename)
            assert name == expected_name, f"Failed for {filename}: got '{name}', expected '{expected_name}'"
            assert year == expected_year
    
    def test_clean_name_without_year(self):
        """Testa limpeza de nome sem ano."""
        fetcher = MoviePosterFetcher()
        
        name, year = fetcher._clean_movie_name("Inception 1080p BluRay.mkv")
        assert name == "Inception"
        assert year is None


class TestRelevanceScoring:
    """Testes para cálculo de score de relevância."""
    
    def test_exact_match_gets_high_score(self):
        """Testa que match exato recebe score alto."""
        fetcher = MoviePosterFetcher()
        
        movie = {
            'title': 'Matrix',
            'original_title': 'The Matrix',
            'popularity': 50.0,
            'release_date': '1999-03-31',
            'vote_average': 8.7,
            'vote_count': 20000
        }
        
        score = fetcher._calculate_relevance_score(movie, 'Matrix', 1999)
        
        # Score deve ser alto: popularidade(25) + match exato(100) + ano(30) + votos(17.4) = ~172
        assert score > 150, f"Score muito baixo: {score}"
    
    def test_partial_match_lower_score(self):
        """Testa que match parcial recebe score menor."""
        fetcher = MoviePosterFetcher()
        
        movie = {
            'title': 'Matrix Reloaded',
            'original_title': 'The Matrix Reloaded',
            'popularity': 40.0,
            'release_date': '2003-05-15',
            'vote_average': 7.2,
            'vote_count': 15000
        }
        
        score = fetcher._calculate_relevance_score(movie, 'Matrix', 1999)
        
        # Score menor: popularidade(20) + match parcial(50) + ano errado(0) + votos(14.4) = ~84
        assert score < 100, f"Score muito alto: {score}"
    
    def test_year_match_adds_bonus(self):
        """Testa que ano correto adiciona bônus."""
        fetcher = MoviePosterFetcher()
        
        movie = {
            'title': 'Avatar',
            'original_title': 'Avatar',
            'popularity': 60.0,
            'release_date': '2009-12-18',
            'vote_average': 7.8,
            'vote_count': 25000
        }
        
        score_with_year = fetcher._calculate_relevance_score(movie, 'Avatar', 2009)
        score_without_year = fetcher._calculate_relevance_score(movie, 'Avatar', None)
        
        # Score com ano deve ser 30 pontos maior
        assert score_with_year - score_without_year == 30


class TestSearchStrategy:
    """Testes para estratégia de busca (requer API key)."""
    
    @pytest.fixture
    def api_key(self, request):
        """Obtém API key dos argumentos ou pula teste."""
        return request.config.getoption("--tmdb-api-key", default=None)
    
    @pytest.mark.skipif(True, reason="Requer API key - executar manualmente")
    def test_search_portuguese_movie(self, api_key):
        """Testa busca de filme com nome em português."""
        if not api_key:
            pytest.skip("TMDb API key não fornecida")
        
        fetcher = MoviePosterFetcher(api_key=api_key)
        
        # Busca "Cidade de Deus" deve encontrar o filme
        movie = fetcher.search_movie("Cidade de Deus", 2002)
        
        assert movie is not None
        assert movie['title'] == 'Cidade de Deus' or movie['original_title'] == 'City of God'
    
    @pytest.mark.skipif(True, reason="Requer API key - executar manualmente")
    def test_search_finds_original_title(self, api_key):
        """Testa busca por título original quando nome é português."""
        if not api_key:
            pytest.skip("TMDb API key não fornecida")
        
        fetcher = MoviePosterFetcher(api_key=api_key)
        
        # Busca "Matrix" deve encontrar "The Matrix"
        movie = fetcher.search_movie("Matrix", 1999)
        
        assert movie is not None
        assert 'Matrix' in movie['original_title'] or 'Matrix' in movie['title']


def pytest_addoption(parser):
    """Adiciona opção de linha de comando para API key."""
    parser.addoption(
        "--tmdb-api-key",
        action="store",
        default=None,
        help="TMDb API key para testes de integração"
    )


if __name__ == '__main__':
    # Executa testes de limpeza de nome (não precisam de API)
    pytest.main([__file__, '-v', '-k', 'TestMovieNameCleaning or TestRelevanceScoring'])
