"""Módulo para buscar capas de filmes usando TMDb API.

Este módulo permite buscar capas (posters) de filmes na internet usando
a API do The Movie Database (TMDb). É usado como fallback antes de extrair
frames de vídeos, melhorando a qualidade das prévias visuais.

Para usar este módulo:
1. Registre-se em https://www.themoviedb.org/signup
2. Obtenha uma API key em https://www.themoviedb.org/settings/api
3. Configure a chave no arquivo config.json: "tmdb_api_key": "sua_chave_aqui"
"""

import re
import requests
from typing import Optional, Tuple
from PIL import Image
from io import BytesIO
from pathlib import Path


class MoviePosterFetcher:
    """Busca capas de filmes usando TMDb API."""
    
    # URL base da API do TMDb (v3)
    TMDB_API_BASE = "https://api.themoviedb.org/3"
    TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"  # Tamanho médio (500px)
    
    def __init__(self, api_key: Optional[str] = None, log_callback=None):
        """
        Inicializa o fetcher com API key opcional.
        
        Args:
            api_key: Chave da API do TMDb (opcional).
            log_callback: Função para logging (opcional).
        """
        self.api_key = api_key
        self.log_callback = log_callback
        self.enabled = bool(api_key and api_key.strip())
    
    def _log(self, message: str, level: str = "info"):
        """Log interno."""
        if self.log_callback:
            self.log_callback(message, level)
    
    def _clean_movie_name(self, filename: str) -> Tuple[str, Optional[int]]:
        """
        Extrai nome do filme e ano do nome do arquivo.
        
        Remove informações técnicas como:
        - Qualidade: 1080p, 720p, 4K, BluRay, WEB-DL, etc.
        - Codec: x264, x265, HEVC, H264, etc.
        - Audio: AAC, AC3, DTS, etc.
        - Grupo: YIFY, RARBG, etc.
        - Extensão: .mp4, .mkv, .avi, etc.
        
        Args:
            filename: Nome do arquivo de vídeo.
            
        Returns:
            Tupla (nome_limpo, ano_opcional).
            
        Exemplos:
            "The Matrix (1999) [1080p].mkv" -> ("The Matrix", 1999)
            "Avatar.2009.BluRay.x264-YIFY.mp4" -> ("Avatar", 2009)
            "Inception.mkv" -> ("Inception", None)
        """
        # Remove extensão
        name = Path(filename).stem
        
        # Substitui separadores por espaços ANTES de extrair o ano
        # Isso ajuda a encontrar anos grudados com underscores
        name = re.sub(r'[_\.]', ' ', name)
        
        # Extrai ano (4 dígitos entre 1900-2099)
        year_match = re.search(r'\b(19|20)\d{2}\b', name)
        year = int(year_match.group()) if year_match else None
        
        # Remove ano
        if year:
            name = name.replace(str(year), '')
        
        # Padrões de qualidade/codec/grupo para remover
        patterns_to_remove = [
            r'\b(1080p|720p|480p|2160p|4K|UHD)\b',  # Resolução
            r'\b(BluRay|BRRip|BDRip|WEB-DL|WEBRip|HDRip|DVDRip)\b',  # Source
            r'\b(x264|x265|H\.?264|H\.?265|HEVC|XviD|DivX)\b',  # Codec
            r'\b(AAC|AC3|DTS|MP3|FLAC|Atmos)\b',  # Audio
            r'\b(YIFY|RARBG|ETRG|YTS|SPARKS|DEFLATE)\b',  # Grupos
            r'\[.*?\]',  # Tudo entre colchetes
            r'\(.*?\)',  # Tudo entre parênteses (exceto ano já removido)
        ]
        
        for pattern in patterns_to_remove:
            name = re.sub(pattern, ' ', name, flags=re.IGNORECASE)
        
        # Remove pontuação isolada e espaços múltiplos
        name = re.sub(r'\s*[-:;,]\s*', ' ', name)  # Remove hífens e pontuação isolados
        name = re.sub(r'\s+', ' ', name).strip()
        
        return (name, year)
    
    def search_movie(self, movie_name: str, year: Optional[int] = None) -> Optional[dict]:
        """
        Busca filme na API do TMDb.
        
        Args:
            movie_name: Nome do filme.
            year: Ano opcional para refinar busca.
            
        Returns:
            Dicionário com informações do filme ou None se não encontrar.
        """
        if not self.enabled:
            self._log("⚠ TMDb API key não configurada", "warning")
            return None
        
        try:
            params = {
                'api_key': self.api_key,
                'query': movie_name,
                'language': 'pt-BR'  # Prioriza resultados em português
            }
            
            if year:
                params['year'] = year
            
            self._log(f"🔍 Buscando: {movie_name}" + (f" ({year})" if year else ""), "info")
            
            response = requests.get(
                f"{self.TMDB_API_BASE}/search/movie",
                params=params,
                timeout=5
            )
            
            if response.status_code != 200:
                self._log(f"✗ Erro na API TMDb: {response.status_code}", "error")
                return None
            
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                self._log("✗ Nenhum resultado encontrado", "warning")
                return None
            
            # Retorna o primeiro resultado (mais relevante)
            movie = results[0]
            self._log(f"✓ Encontrado: {movie.get('title', 'N/A')} ({movie.get('release_date', 'N/A')[:4]})", "success")
            return movie
            
        except requests.RequestException as e:
            self._log(f"✗ Erro de rede: {e}", "error")
            return None
        except Exception as e:
            self._log(f"✗ Erro ao buscar filme: {type(e).__name__}: {e}", "error")
            return None
    
    def download_poster(self, poster_path: str) -> Optional[Image.Image]:
        """
        Baixa a capa do filme.
        
        Args:
            poster_path: Caminho da imagem retornado pela API (ex: "/abc123.jpg").
            
        Returns:
            Imagem PIL ou None se falhar.
        """
        if not poster_path:
            self._log("✗ Sem caminho de imagem", "warning")
            return None
        
        try:
            url = f"{self.TMDB_IMAGE_BASE}{poster_path}"
            self._log(f"⬇ Baixando capa...", "info")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                self._log(f"✗ Erro ao baixar capa: {response.status_code}", "error")
                return None
            
            # Carrega imagem na memória
            image = Image.open(BytesIO(response.content))
            self._log(f"✓ Capa baixada: {image.size}", "success")
            return image
            
        except requests.RequestException as e:
            self._log(f"✗ Erro de rede ao baixar capa: {e}", "error")
            return None
        except Exception as e:
            self._log(f"✗ Erro ao processar capa: {type(e).__name__}: {e}", "error")
            return None
    
    def get_movie_poster(self, video_filename: str) -> Optional[Image.Image]:
        """
        Busca e baixa capa do filme a partir do nome do arquivo.
        
        Este é o método principal que deve ser usado. Ele:
        1. Limpa o nome do arquivo
        2. Busca o filme na API
        3. Baixa a capa
        
        Args:
            video_filename: Nome do arquivo de vídeo.
            
        Returns:
            Imagem PIL da capa ou None se não encontrar.
            
        Exemplo:
            >>> fetcher = MoviePosterFetcher(api_key="sua_chave")
            >>> poster = fetcher.get_movie_poster("The Matrix (1999) 1080p.mkv")
            >>> if poster:
            >>>     poster.show()
        """
        if not self.enabled:
            return None
        
        # Limpa nome do arquivo
        movie_name, year = self._clean_movie_name(video_filename)
        
        if not movie_name:
            self._log("✗ Não foi possível extrair nome do filme", "warning")
            return None
        
        # Busca filme
        movie = self.search_movie(movie_name, year)
        
        if not movie:
            return None
        
        # Baixa capa
        poster_path = movie.get('poster_path')
        if not poster_path:
            self._log("✗ Filme encontrado mas sem capa disponível", "warning")
            return None
        
        return self.download_poster(poster_path)


# Função auxiliar para uso rápido
def get_poster_for_video(
    video_filename: str,
    api_key: Optional[str] = None,
    log_callback=None
) -> Optional[Image.Image]:
    """
    Função auxiliar para buscar capa de um vídeo.
    
    Args:
        video_filename: Nome do arquivo de vídeo.
        api_key: Chave da API do TMDb.
        log_callback: Função para logging.
        
    Returns:
        Imagem PIL da capa ou None.
    """
    fetcher = MoviePosterFetcher(api_key, log_callback)
    return fetcher.get_movie_poster(video_filename)
