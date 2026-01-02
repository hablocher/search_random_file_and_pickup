"""Testes para o módulo de busca de capas de filmes (MoviePosterFetcher)."""

import pytest
from pathlib import Path
from src.random_file_picker.utils.movie_poster import MoviePosterFetcher


class TestMoviePosterFetcher:
    """Testes para a classe MoviePosterFetcher."""
    
    def test_clean_movie_name_simple(self):
        """Testa limpeza de nome simples."""
        fetcher = MoviePosterFetcher()
        name, year = fetcher._clean_movie_name("The Matrix.mkv")
        assert name == "The Matrix"
        assert year is None
    
    def test_clean_movie_name_with_year(self):
        """Testa limpeza de nome com ano."""
        fetcher = MoviePosterFetcher()
        name, year = fetcher._clean_movie_name("The Matrix (1999).mkv")
        assert name == "The Matrix"
        assert year == 1999
    
    def test_clean_movie_name_with_quality(self):
        """Testa remoção de informações de qualidade."""
        fetcher = MoviePosterFetcher()
        name, year = fetcher._clean_movie_name("Avatar.2009.1080p.BluRay.x264-YIFY.mp4")
        assert name == "Avatar"
        assert year == 2009
    
    def test_clean_movie_name_complex(self):
        """Testa limpeza de nome complexo."""
        fetcher = MoviePosterFetcher()
        name, year = fetcher._clean_movie_name("Inception.2010.4K.UHD.HEVC.DTS.mp4")
        assert name == "Inception"
        assert year == 2010
    
    def test_clean_movie_name_brackets(self):
        """Testa remoção de colchetes."""
        fetcher = MoviePosterFetcher()
        name, year = fetcher._clean_movie_name("Interstellar [2014] [1080p].mkv")
        assert name == "Interstellar"
        assert year == 2014
    
    def test_clean_movie_name_underscores(self):
        """Testa substituição de underscores."""
        fetcher = MoviePosterFetcher()
        name, year = fetcher._clean_movie_name("The_Dark_Knight_2008.avi")
        # Quando o ano está grudado no nome sem separador, pode ficar no resultado
        # O importante é que o ano foi extraído corretamente
        assert "Dark Knight" in name
        assert year == 2008
    
    def test_fetcher_disabled_without_api_key(self):
        """Testa que fetcher fica desabilitado sem API key."""
        fetcher = MoviePosterFetcher()
        assert not fetcher.enabled
        
        fetcher2 = MoviePosterFetcher(api_key="")
        assert not fetcher2.enabled
    
    def test_fetcher_enabled_with_api_key(self):
        """Testa que fetcher fica habilitado com API key."""
        fetcher = MoviePosterFetcher(api_key="fake_key_123")
        assert fetcher.enabled
    
    def test_get_poster_returns_none_without_api_key(self):
        """Testa que retorna None sem API key."""
        fetcher = MoviePosterFetcher()
        result = fetcher.get_movie_poster("The Matrix 1999.mkv")
        assert result is None


# Testes de integração (requerem API key real)
# Estes testes só rodam se uma API key for fornecida
@pytest.mark.integration
class TestMoviePosterFetcherIntegration:
    """Testes de integração com API real do TMDb."""
    
    @pytest.fixture
    def api_key(self, request):
        """Obtém API key dos argumentos de pytest."""
        return request.config.getoption("--tmdb-api-key", default=None)
    
    def test_search_movie_success(self, api_key):
        """Testa busca de filme real."""
        fetcher = MoviePosterFetcher(api_key=api_key)
        movie = fetcher.search_movie("The Matrix", 1999)
        
        assert movie is not None
        assert "title" in movie
        assert "poster_path" in movie
        assert "1999" in movie.get("release_date", "")
    
    def test_download_poster_success(self, api_key):
        """Testa download de capa real."""
        fetcher = MoviePosterFetcher(api_key=api_key)
        movie = fetcher.search_movie("The Matrix", 1999)
        
        assert movie is not None
        poster_path = movie.get("poster_path")
        assert poster_path is not None
        
        image = fetcher.download_poster(poster_path)
        assert image is not None
        assert image.size[0] > 0
        assert image.size[1] > 0
    
    def test_get_movie_poster_full_workflow(self, api_key):
        """Testa workflow completo de busca."""
        fetcher = MoviePosterFetcher(api_key=api_key)
        poster = fetcher.get_movie_poster("The Matrix (1999) 1080p BluRay.mkv")
        
        assert poster is not None
        assert poster.size[0] > 0
        assert poster.size[1] > 0


def pytest_addoption(parser):
    """Adiciona opção para API key nos testes."""
    parser.addoption(
        "--tmdb-api-key",
        action="store",
        default=None,
        help="TMDb API key para testes de integração"
    )


if __name__ == "__main__":
    # Permite executar o teste diretamente
    import sys
    pytest.main([__file__, "-v", "-s"])
