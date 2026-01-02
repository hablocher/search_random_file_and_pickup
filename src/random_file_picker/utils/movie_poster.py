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
        - Informações de legendas e áudio
        
        Args:
            filename: Nome do arquivo de vídeo.
            
        Returns:
            Tupla (nome_limpo, ano_opcional).
            
        Exemplos:
            "The Matrix (1999) [1080p].mkv" -> ("The Matrix", 1999)
            "Avatar.2009.BluRay.x264-YIFY.mp4" -> ("Avatar", 2009)
            "O Poderoso Chefão (1972) Dual Audio.mkv" -> ("O Poderoso Chefão", 1972)
            "Inception.mkv" -> ("Inception", None)
        """
        # Remove extensão
        name = Path(filename).stem
        
        # Remove padrões com pontos ANTES de substituir pontos por espaços
        # Isso evita que "DDP5.1" vire "DDP5 1"
        audio_patterns_with_dots = [
            r'\b(DDP|DD\+|DD)?5\.1\b',
            r'\b(DDP|DD\+|DD)?7\.1\b',
            r'\b(DDP|DD\+|DD)?2\.0\b',
        ]
        for pattern in audio_patterns_with_dots:
            name = re.sub(pattern, ' ', name, flags=re.IGNORECASE)
        
        # Substitui separadores por espaços ANTES de extrair o ano
        # Isso ajuda a encontrar anos grudados com underscores
        name = re.sub(r'[_\.]', ' ', name)
        
        # Extrai ano (4 dígitos entre 1900-2099)
        year_match = re.search(r'\b(19|20)\d{2}\b', name)
        year = int(year_match.group()) if year_match else None
        
        # Remove ano
        if year:
            name = name.replace(str(year), '')
        
        # Padrões de qualidade/codec/grupo para remover (ordem importa!)
        patterns_to_remove = [
            # Informações de áudio/legenda em português
            r'\b(Dual Audio|Dublado|Legendado|Nacional|PTBR|PT-BR|BR)\b',
            
            # Versões especiais e formatos de exibição
            r'\b(IMAX|3D|HFR|Directors Cut|DC|EXTENDED|UNRATED|REMASTERED|PROPER|LIMITED)\b',
            
            # Resolução e qualidade
            r'\b(1080p|720p|480p|2160p|4K|UHD|HD|FHD|QHD|SD)\b',
            
            # Source/Release
            r'\b(BluRay|BRRip|BDRip|WEB-DL|WEBRip|HDRip|DVDRip|DVDScr|CAM|TS|TC)\b',
            
            # Codec de vídeo
            r'\b(x264|x265|H\.?264|H\.?265|HEVC|XviD|DivX|AVC|VP9|AV1)\b',
            
            # Codec de áudio
            r'\b(AAC|AC3|DTS|DTS-HD|TrueHD|MP3|FLAC|Atmos|DD|DD\+|DDP|E-AC3)\b',
            
            # HDR e color
            r'\b(HDR|HDR10|Dolby Vision|DV|SDR|10bit|8bit)\b',
            
            # Release groups
            r'\b(YIFY|RARBG|ETRG|YTS|SPARKS|DEFLATE|FGT|AMZN|NF|iNTERNAL|REPACK)\b',
            
            # Informações de canal (restante, os com pontos já foram removidos)
            r'\b(Stereo|Mono)\b',
            
            # Tudo entre colchetes
            r'\[.*?\]',
            
            # Tudo entre parênteses (exceto ano já removido)
            r'\(.*?\)',
        ]
        
        for pattern in patterns_to_remove:
            name = re.sub(pattern, ' ', name, flags=re.IGNORECASE)
        
        # Remove hífens isolados que geralmente precedem release group
        # Ex: "Filme - YIFY" -> "Filme"
        name = re.sub(r'\s*-\s*$', '', name)
        
        # Remove pontuação isolada e espaços múltiplos
        name = re.sub(r'\s*[-:;,]\s*', ' ', name)  # Remove hífens e pontuação isolados
        name = re.sub(r'\s+', ' ', name).strip()
        
        return (name, year)
    
    def _calculate_relevance_score(self, movie: dict, query: str, year: Optional[int] = None) -> float:
        """
        Calcula score de relevância do resultado.
        
        Args:
            movie: Dados do filme retornado pela API.
            query: Query de busca original.
            year: Ano esperado (opcional).
            
        Returns:
            Score de relevância (maior = mais relevante).
        """
        score = 0.0
        
        # Popularidade (0-100, normalizado para 0-50)
        popularity = movie.get('popularity', 0)
        score += min(popularity / 2, 50)
        
        # Match exato no título (peso alto: +100)
        title = movie.get('title', '').lower()
        original_title = movie.get('original_title', '').lower()
        query_lower = query.lower()
        
        if query_lower == title or query_lower == original_title:
            score += 100
        elif query_lower in title or query_lower in original_title:
            score += 50
        
        # Correspondência de ano (peso médio: +30)
        if year:
            release_date = movie.get('release_date', '')
            if release_date and release_date.startswith(str(year)):
                score += 30
        
        # Voto médio (0-10, peso baixo: 0-20)
        vote_average = movie.get('vote_average', 0)
        vote_count = movie.get('vote_count', 0)
        if vote_count > 100:  # Só considera se tiver votos suficientes
            score += vote_average * 2
        
        return score
    
    def _search_with_language(self, movie_name: str, year: Optional[int], language: str) -> list:
        """
        Realiza busca com linguagem específica.
        
        Args:
            movie_name: Nome do filme.
            year: Ano opcional.
            language: Código de linguagem (ex: 'pt-BR', 'en-US').
            
        Returns:
            Lista de resultados da API.
        """
        try:
            params = {
                'api_key': self.api_key,
                'query': movie_name,
                'language': language,
                'include_adult': False
            }
            
            if year:
                params['year'] = year
            
            response = requests.get(
                f"{self.TMDB_API_BASE}/search/movie",
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
        except:
            pass
        
        return []
    
    def search_movie(self, movie_name: str, year: Optional[int] = None) -> Optional[dict]:
        """
        Busca filme na API do TMDb com estratégia inteligente.
        
        Estratégia de busca:
        1. Busca em português (pt-BR)
        2. Se não encontrar ou tiver poucos resultados, busca em inglês (en-US)
        3. Combina resultados e seleciona o mais relevante baseado em:
           - Popularidade
           - Correspondência de título
           - Correspondência de ano
           - Avaliação
        
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
            self._log(f"🔍 Buscando: {movie_name}" + (f" ({year})" if year else ""), "info")
            
            # Busca em português
            results_pt = self._search_with_language(movie_name, year, 'pt-BR')
            
            # Busca em inglês (para capturar títulos originais)
            results_en = self._search_with_language(movie_name, year, 'en-US')
            
            # Combina resultados removendo duplicatas (por ID)
            all_results = {}
            for movie in results_pt + results_en:
                movie_id = movie.get('id')
                if movie_id and movie_id not in all_results:
                    all_results[movie_id] = movie
            
            if not all_results:
                self._log("✗ Nenhum resultado encontrado (pt-BR e en-US)", "warning")
                return None
            
            # Calcula score de relevância para cada resultado
            scored_results = []
            for movie in all_results.values():
                score = self._calculate_relevance_score(movie, movie_name, year)
                scored_results.append((score, movie))
            
            # Ordena por score (maior primeiro)
            scored_results.sort(key=lambda x: x[0], reverse=True)
            
            # Seleciona o melhor resultado
            best_score, best_movie = scored_results[0]
            
            title = best_movie.get('title', 'N/A')
            original_title = best_movie.get('original_title', '')
            release_year = best_movie.get('release_date', 'N/A')[:4]
            
            # Log detalhado
            title_info = title
            if original_title and original_title != title:
                title_info += f" [{original_title}]"
            
            self._log(
                f"✓ Encontrado: {title_info} ({release_year}) "
                f"[score: {best_score:.1f}, popularidade: {best_movie.get('popularity', 0):.1f}]",
                "success"
            )
            
            # Log dos outros resultados relevantes (top 3)
            if len(scored_results) > 1:
                self._log(f"  Outras opções consideradas:", "info")
                for i, (score, movie) in enumerate(scored_results[1:4], 1):
                    alt_title = movie.get('title', 'N/A')
                    alt_year = movie.get('release_date', 'N/A')[:4]
                    self._log(f"    {i+1}. {alt_title} ({alt_year}) [score: {score:.1f}]", "info")
            
            return best_movie
            
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
