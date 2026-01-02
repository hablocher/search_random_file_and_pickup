"""Extração de imagens de arquivos compactados (ZIP/RAR), PDF e vídeos."""

import io
import zipfile
import random
import shutil
import os
from pathlib import Path
from typing import Optional, Tuple, Callable

import rarfile
from PIL import Image

# Configurar UnRAR automaticamente
def _setup_unrar():
    """Detecta e configura o UnRAR automaticamente."""
    # Tenta encontrar UnRAR em locais comuns
    possible_paths = [
        r"C:\Program Files\WinRAR\UnRAR.exe",
        r"C:\Program Files (x86)\WinRAR\UnRAR.exe",
        shutil.which("unrar"),  # PATH do sistema
        shutil.which("UnRAR"),
        shutil.which("unrar.exe"),
    ]
    
    for path in possible_paths:
        if path and Path(path).exists():
            rarfile.UNRAR_TOOL = path
            return True
    
    # Se não encontrou, tenta usar a ferramenta padrão
    return False

_HAS_UNRAR = _setup_unrar()

try:
    import ffmpeg
    HAS_FFMPEG = True
except ImportError:
    HAS_FFMPEG = False

try:
    from ..utils.movie_poster import MoviePosterFetcher
    HAS_MOVIE_POSTER = True
except ImportError:
    HAS_MOVIE_POSTER = False

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False


def validate_rar_buffer(file_data: bytes, log_callback: Optional[Callable] = None) -> bool:
    """Valida se o buffer contém um arquivo RAR válido completo.
    
    Args:
        file_data: Bytes do arquivo RAR.
        log_callback: Função de log opcional.
        
    Returns:
        True se é um RAR válido e completo, False caso contrário.
    """
    def _log(msg):
        if log_callback:
            log_callback(msg)
    
    try:
        _log("🔍 Validando buffer RAR...")
        archive_file = rarfile.RarFile(io.BytesIO(file_data))
        file_list = archive_file.namelist()
        
        # Tenta ler UMA imagem para validar conteúdo real
        for filename in sorted(file_list):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                try:
                    _log(f"   Testando leitura de: {filename}")
                    with archive_file.open(filename) as img_file:
                        # Tenta ler apenas 1KB para validação
                        test_read = img_file.read(1024)
                        _log(f"   Lidos {len(test_read)} bytes de teste")
                        if len(test_read) < 100:  # Placeholder tem ~52 bytes
                            _log("   ✗ Buffer inválido (placeholder detectado)")
                            archive_file.close()
                            return False
                        # Buffer parece válido
                        _log("   ✓ Buffer RAR válido!")
                        archive_file.close()
                        return True
                except rarfile.BadRarFile as e:
                    _log(f"   ✗ BadRarFile durante validação: {e}")
                    archive_file.close()
                    return False
                except Exception as e:
                    _log(f"   ✗ Erro durante validação: {e}")
                    archive_file.close()
                    return False
        
        archive_file.close()
        _log("   ✓ Buffer RAR parece válido (nenhuma imagem para testar)")
        return True
    except Exception as e:
        _log(f"   ✗ Erro ao validar RAR: {e}")
        return False


def validate_zip_buffer(file_data: bytes, log_callback: Optional[Callable] = None) -> bool:
    """Valida se o buffer contém um arquivo ZIP válido completo.
    
    Args:
        file_data: Bytes do arquivo ZIP.
        log_callback: Função de log opcional.
        
    Returns:
        True se é um ZIP válido e completo, False caso contrário.
    """
    def _log(msg):
        if log_callback:
            log_callback(msg)
    
    try:
        _log("🔍 Validando buffer ZIP...")
        archive_file = zipfile.ZipFile(io.BytesIO(file_data))
        file_list = archive_file.namelist()
        
        # Tenta ler UMA imagem para validar conteúdo real
        for filename in sorted(file_list):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                try:
                    with archive_file.open(filename) as img_file:
                        test_read = img_file.read(1024)
                        if len(test_read) < 100:
                            _log("   ✗ Buffer inválido (placeholder detectado)")
                            archive_file.close()
                            return False
                        _log("   ✓ Buffer ZIP válido!")
                        archive_file.close()
                        return True
                except Exception:
                    archive_file.close()
                    return False
        
        archive_file.close()
        return True
    except Exception:
        return False


class ArchiveExtractor:
    """Extrai imagens de arquivos ZIP, RAR e PDF."""
    
    def __init__(self, log_callback=None, tmdb_api_key=None):
        """Inicializa o extrator com callback opcional para logs."""
        self.log_callback = log_callback
        self.tmdb_api_key = tmdb_api_key
        
        # Inicializa fetcher de capas se disponível
        if HAS_MOVIE_POSTER and tmdb_api_key:
            self.poster_fetcher = MoviePosterFetcher(tmdb_api_key, log_callback)
        else:
            self.poster_fetcher = None
    
    def _log(self, message: str, level: str = "info"):
        """Log interno."""
        if self.log_callback:
            self.log_callback(message, level)
    
    @staticmethod
    def detect_format(file_data: bytes) -> Optional[str]:
        """Detecta formato do arquivo pela assinatura (magic bytes).
        
        Args:
            file_data: Primeiros bytes do arquivo.
            
        Returns:
            'zip', 'rar', 'rar4', 'rar5', '7z', 'pdf', 'mp4', 'avi', 'mkv', 'webm', 'flv', 'mov', 'wmv', 'mp3', 'flac', 'ogg', 'wav' ou None.
        """
        if len(file_data) < 10:
            return None
        
        # ZIP: 50 4B (PK)
        if file_data[:2] == b'PK':
            return 'zip'
        # RAR 5+: 52 61 72 21 1A 07 01 00
        elif len(file_data) >= 8 and file_data[:8] == b'Rar!\x1a\x07\x01\x00':
            return 'rar5'
        # RAR 4.x: 52 61 72 21 1A 07 00
        elif len(file_data) >= 7 and file_data[:7] == b'Rar!\x1a\x07\x00':
            return 'rar4'
        # RAR 1.5-3.x: 52 61 72 21 1A 07 (Rar!)
        elif file_data[:6] == b'Rar!\x1a\x07':
            return 'rar'
        # 7-Zip: 37 7A BC AF 27 1C
        elif file_data[:6] == b'7z\xbc\xaf\x27\x1c':
            return '7z'
        # PDF: 25 50 44 46 (%PDF)
        elif file_data[:4] == b'%PDF':
            return 'pdf'
        # MP4/M4V/M4A: ftyp
        elif len(file_data) >= 12 and file_data[4:8] == b'ftyp':
            return 'mp4'
        # AVI: RIFF....AVI
        elif file_data[:4] == b'RIFF' and len(file_data) >= 12 and file_data[8:12] == b'AVI ':
            return 'avi'
        # MKV/WEBM: 1A 45 DF A3
        elif file_data[:4] == b'\x1a\x45\xdf\xa3':
            # Detecta se é MKV ou WEBM pelo doctype
            if b'webm' in file_data[:100].lower():
                return 'webm'
            return 'mkv'
        # FLV: 46 4C 56
        elif file_data[:3] == b'FLV':
            return 'flv'
        # MOV/QT: moov/mdat/free
        elif len(file_data) >= 8 and file_data[4:8] in [b'moov', b'mdat', b'free', b'wide']:
            return 'mov'
        # WMV/WMA/ASF: 30 26 B2 75
        elif file_data[:4] == b'\x30\x26\xb2\x75':
            return 'wmv'
        # MP3: FF FB ou FF F3 ou FF F2 ou ID3
        elif (file_data[:2] in [b'\xff\xfb', b'\xff\xf3', b'\xff\xf2'] or file_data[:3] == b'ID3'):
            return 'mp3'
        # FLAC: 66 4C 61 43
        elif file_data[:4] == b'fLaC':
            return 'flac'
        # OGG: 4F 67 67 53
        elif file_data[:4] == b'OggS':
            return 'ogg'
        # WAV: RIFF....WAVE
        elif file_data[:4] == b'RIFF' and len(file_data) >= 12 and file_data[8:12] == b'WAVE':
            return 'wav'
        
        return None
    
    def extract_from_zip(self, file_data: bytes) -> Tuple[Optional[Image.Image], int]:
        """Extrai primeira imagem de arquivo ZIP.
        
        Args:
            file_data: Dados do arquivo ZIP na memória.
            
        Returns:
            Tupla (imagem_PIL, contagem_de_imagens). Se falhar, retorna (None, 0).
        """
        try:
            self._log("Abrindo arquivo ZIP...")
            with zipfile.ZipFile(io.BytesIO(file_data), 'r') as zip_file:
                file_list = zip_file.namelist()
                page_count = len([f for f in file_list if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                self._log(f"Encontradas {page_count} imagens no ZIP")
                
                # Procura pela primeira imagem (ordem alfabética)
                for filename in sorted(file_list):
                    lower_name = filename.lower()
                    if lower_name.endswith(('.jpg', '.jpeg', '.png')) and not filename.startswith('__MACOSX'):
                        self._log(f"Tentando extrair primeira imagem: {filename}")
                        # Tenta extrair APENAS esta primeira imagem
                        try:
                            with zip_file.open(filename) as image_file:
                                image_data = image_file.read()
                                self._log(f"Lidos {len(image_data)} bytes, criando imagem PIL...")
                                image = Image.open(io.BytesIO(image_data))
                                self._log(f"✓ Imagem extraída: {image.size}")
                                return (image, page_count)
                        except Exception as e:
                            self._log(f"✗ Erro ao extrair primeira imagem: {type(e).__name__}: {e}")
                            # Se falhar na primeira, retorna erro
                            return (None, page_count)
                
                # Não encontrou imagens
                self._log("Nenhuma imagem encontrada no ZIP")
                return (None, 0)
                
        except zipfile.BadZipFile:
            return (None, 0)
        except Exception:
            return (None, 0)
    
    def extract_from_rar(self, file_data: bytes) -> Tuple[Optional[Image.Image], int, Optional[str]]:
        """Extrai primeira imagem de arquivo RAR.
        
        Args:
            file_data: Dados do arquivo RAR na memória.
            
        Returns:
            Tupla (imagem_PIL, contagem_de_imagens, status).
            status pode ser None (sucesso/erro normal), 'SYNCING' (arquivo sincronizando do OneDrive).
        """
        # Tenta abrir o arquivo RAR
        try:
            self._log("Abrindo arquivo RAR...")
            archive_file = rarfile.RarFile(io.BytesIO(file_data), 'r')
            self._log("RAR aberto com sucesso")
        except rarfile.BadRarFile as e:
            self._log(f"BadRarFile ao abrir: {e}")
            # Se não consegue abrir o RAR, pode estar sincronizando
            return (None, 0, 'SYNCING')
        except Exception as e:
            self._log(f"Erro ao abrir RAR: {e}")
            # Outro erro ao abrir
            return (None, 0, None)
        
        try:
            file_list = archive_file.namelist()
            page_count = len([f for f in file_list if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            self._log(f"Encontradas {page_count} imagens no RAR")
            
            # Procura pela primeira imagem (ordem alfabética)
            for filename in sorted(file_list):
                lower_name = filename.lower()
                if lower_name.endswith(('.jpg', '.jpeg', '.png')) and not filename.startswith('__MACOSX'):
                    self._log(f"Tentando extrair primeira imagem: {filename}")
                    # Tenta extrair APENAS esta primeira imagem
                    try:
                        with archive_file.open(filename) as image_file:
                            self._log(f"Arquivo aberto, lendo dados...")
                            image_data = image_file.read()
                            self._log(f"Lidos {len(image_data)} bytes, criando imagem PIL...")
                            image = Image.open(io.BytesIO(image_data))
                            self._log(f"✓ Imagem extraída: {image.size}")
                            archive_file.close()
                            return (image, page_count, None)
                    except rarfile.BadRarFile as e:
                        self._log(f"✗ BadRarFile ao extrair primeira imagem: {e}")
                        # BadRarFile indica arquivo não totalmente sincronizado (OneDrive/GDrive)
                        archive_file.close()
                        return (None, page_count, 'SYNCING')
                    except Exception as e:
                        self._log(f"✗ Erro ao extrair primeira imagem: {type(e).__name__}: {e}")
                        # Outro erro - retorna sem status SYNCING
                        archive_file.close()
                        return (None, page_count, None)
            
            # Não encontrou imagens
            self._log("Nenhuma imagem encontrada no RAR")
            archive_file.close()
            return (None, 0, None)
            
        except Exception as e:
            self._log(f"Erro geral ao processar RAR: {type(e).__name__}: {e}")
            try:
                archive_file.close()
            except:
                pass
            return (None, 0, None)
    
    def extract_from_pdf(self, file_data: bytes) -> Tuple[Optional[Image.Image], int]:
        """Extrai primeira página de arquivo PDF como imagem.
        
        Args:
            file_data: Dados do arquivo PDF na memória.
            
        Returns:
            Tupla (imagem_PIL, contagem_de_páginas). Se falhar, retorna (None, 0).
        """
        if not HAS_PYMUPDF:
            self._log("PyMuPDF não está instalado")
            return (None, 0)
        
        try:
            self._log("Abrindo arquivo PDF...")
            doc = fitz.open(stream=file_data, filetype="pdf")
            
            if len(doc) == 0:
                self._log("PDF vazio (0 páginas)")
                doc.close()
                return (None, 0)
            
            page_count = len(doc)
            self._log(f"PDF com {page_count} páginas")
            
            # Pega a primeira página
            page = doc[0]
            
            # Renderiza a página como imagem (zoom = 2 para melhor qualidade)
            self._log("Renderizando primeira página...")
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat)
            
            # Converte pixmap para PIL Image
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            self._log(f"✓ Página extraída: {image.size}")
            
            doc.close()
            return (image, page_count)
            
        except Exception as e:
            self._log(f"✗ Erro ao extrair PDF: {type(e).__name__}: {e}")
            return (None, 0)
    
    def extract_first_image(
        self,
        file_path: str,
        file_data: bytes
    ) -> Tuple[Optional[Image.Image], int, Optional[str]]:
        """Extrai primeira imagem de arquivo (detecta formato automaticamente).
        
        Args:
            file_path: Caminho do arquivo (para detectar extensão).
            file_data: Dados do arquivo na memória.
            
        Returns:
            Tupla (imagem_PIL, contagem, status).
            status pode ser None (sucesso), 'SYNCING' (sincronizando), ou mensagem de erro.
        """
        # Detecta formato pela assinatura
        detected_format = ArchiveExtractor.detect_format(file_data)
        file_ext = Path(file_path).suffix.lower()
        
        # PDF
        if file_ext == '.pdf' or detected_format == 'pdf':
            image, page_count = self.extract_from_pdf(file_data)
            return (image, page_count, None)
        
        # RAR
        if file_ext in ['.rar', '.cbr'] or detected_format in ['rar', 'rar5']:
            self._log("📦 Detectado arquivo RAR/CBR")
            image, page_count, status = self.extract_from_rar(file_data)
            return (image, page_count, status)
        
        # ZIP
        if file_ext in ['.zip', '.cbz'] or detected_format == 'zip':
            self._log("📦 Detectado arquivo ZIP/CBZ")
            image, page_count = self.extract_from_zip(file_data)
            return (image, page_count, None)
        
        # Formato não suportado
        if detected_format == '7z':
            return (None, 0, '7Z_NOT_SUPPORTED')
        
        return (None, 0, 'UNKNOWN_FORMAT')
    
    def extract_from_video(self, file_path: str) -> Tuple[Optional[Image.Image], float]:
        """Extrai um frame aleatório da metade do vídeo (±5 minutos).
        
        Args:
            file_path: Caminho do arquivo de vídeo.
            
        Returns:
            Tupla (imagem_PIL, duração_em_segundos). Se falhar, retorna (None, 0).
        """
        if not HAS_FFMPEG:
            self._log("⚠ ffmpeg-python não instalado", "warning")
            return (None, 0)
        
        # Verifica se ffmpeg está instalado no sistema
        import shutil
        if not shutil.which('ffmpeg'):
            self._log("⚠ FFmpeg não está instalado no sistema", "warning")
            self._log("💡 Para extrair frames de vídeos, instale o FFmpeg:", "info")
            self._log("   Windows: https://www.gyan.dev/ffmpeg/builds/", "info")
            self._log("   Ou use: winget install Gyan.FFmpeg", "info")
            return (None, 0)
        
        try:
            self._log(f"📹 Extraindo frame do vídeo...", "info")
            
            # Obtém informações do vídeo
            probe = ffmpeg.probe(file_path)
            video_info = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
            
            if not video_info:
                self._log("⚠ Nenhuma stream de vídeo encontrada", "warning")
                return (None, 0)
            
            # Duração em segundos
            duration = float(probe['format'].get('duration', 0))
            if duration <= 0:
                self._log("⚠ Não foi possível determinar duração do vídeo", "warning")
                return (None, 0)
            
            self._log(f"Duração: {duration:.1f}s ({duration/60:.1f} min)", "info")
            
            # Calcula janela de tempo: metade ±5 minutos
            middle = duration / 2
            window_start = max(0, middle - 300)  # 5 minutos = 300 segundos
            window_end = min(duration, middle + 300)
            
            # Escolhe tempo aleatório na janela
            seek_time = random.uniform(window_start, window_end)
            self._log(f"Extraindo frame em {seek_time:.1f}s (janela: {window_start:.1f}s - {window_end:.1f}s)", "info")
            
            # Extrai frame
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                tmp_path = tmp.name
            
            try:
                # Usa ffmpeg para extrair frame
                (
                    ffmpeg
                    .input(file_path, ss=seek_time)
                    .output(tmp_path, vframes=1, format='image2', vcodec='mjpeg')
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True, quiet=True)
                )
                
                # Carrega imagem e copia para memória antes de fechar o arquivo
                with Image.open(tmp_path) as img:
                    # Força carregar todos os pixels na memória
                    image = img.copy()
                
                self._log(f"✓ Frame extraído: {image.size}", "success")
                return (image, duration)
                
            finally:
                # Remove arquivo temporário
                try:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                except PermissionError:
                    # Se ainda estiver em uso, tenta novamente após pequeno delay
                    import time
                    time.sleep(0.1)
                    try:
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)
                    except:
                        pass  # Ignora se não conseguir deletar
        
        except FileNotFoundError as e:
            self._log("❌ FFmpeg não encontrado no sistema", "error")
            self._log("💡 Instale o FFmpeg para extrair frames de vídeos:", "info")
            self._log("   Windows: winget install Gyan.FFmpeg", "info")
            self._log("   Ou baixe em: https://www.gyan.dev/ffmpeg/builds/", "info")
            return (None, 0)
        except ffmpeg.Error as e:
            stderr = e.stderr.decode() if e.stderr else str(e)
            self._log(f"✗ Erro ffmpeg: {stderr}", "error")
            return (None, 0)
        except Exception as e:
            self._log(f"✗ Erro ao extrair frame: {type(e).__name__}: {e}", "error")
            return (None, 0)
    
    def extract_first_image_from_file(
        self,
        file_path: str
    ) -> Tuple[Optional[Image.Image], int, Optional[str]]:
        """Extrai primeira imagem lendo diretamente do arquivo (sem buffer).
        Detecta o tipo analisando o conteúdo (magic bytes), não a extensão.
        
        Args:
            file_path: Caminho do arquivo.
            
        Returns:
            Tupla (imagem_PIL, contagem, status).
        """
        try:
            # Lê os primeiros bytes para detectar o formato
            with open(file_path, 'rb') as f:
                header = f.read(32)
            
            detected_format = ArchiveExtractor.detect_format(header)
            self._log(f"🔍 Formato detectado: {detected_format}")
            
            # VÍDEOS
            video_formats = ['mp4', 'avi', 'mkv', 'webm', 'flv', 'mov', 'wmv']
            if detected_format in video_formats:
                self._log(f"📹 Processando arquivo de vídeo ({detected_format.upper()})")
                
                # Tenta buscar capa do filme primeiro (se configurado)
                poster_image = None
                if self.poster_fetcher and self.poster_fetcher.enabled:
                    self._log("🎬 Tentando buscar capa do filme online...")
                    poster_image = self.poster_fetcher.get_movie_poster(Path(file_path).name)
                
                if poster_image:
                    # Usa capa encontrada
                    self._log("✓ Usando capa do filme encontrada", "success")
                    return (poster_image, 0, None)
                else:
                    # Fallback: extrai frame do vídeo
                    if self.poster_fetcher and self.poster_fetcher.enabled:
                        self._log("⚠ Capa não encontrada, extraindo frame do vídeo...", "warning")
                    image, duration = self.extract_from_video(file_path)
                    if image:
                        # Retorna duração como "page_count" para mostrar info
                        return (image, int(duration), None)
                    else:
                        return (None, 0, 'VIDEO_ERROR')
            
            # ÁUDIO (apenas mostra mensagem, não extrai imagem)
            audio_formats = ['mp3', 'flac', 'ogg', 'wav']
            if detected_format in audio_formats:
                self._log(f"🎵 Arquivo de áudio ({detected_format.upper()}) - sem prévia visual")
                return (None, 0, 'AUDIO_FILE')
            
            # PDF
            if detected_format == 'pdf':
                self._log("📦 Processando arquivo PDF")
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                image, page_count = self.extract_from_pdf(file_data)
                return (image, page_count, None)
            
            # RAR (todas as versões: 1.5-3.x, 4.x, 5.x)
            if detected_format in ['rar', 'rar4', 'rar5']:
                self._log(f"📦 Processando arquivo RAR ({detected_format.upper()})")
                
                # Verifica se UnRAR está disponível
                if not _HAS_UNRAR:
                    self._log("⚠ UnRAR não encontrado! Instale WinRAR para extrair arquivos RAR", "warning")
                    self._log("  Download: https://www.win-rar.com/download.html", "info")
                    return (None, 0, None)
                
                try:
                    with rarfile.RarFile(file_path) as archive:
                        file_list = archive.namelist()
                        page_count = sum(1 for f in file_list 
                                       if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')))
                        
                        for filename in sorted(file_list):
                            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                                try:
                                    with archive.open(filename) as img_file:
                                        image_data = img_file.read()
                                        image = Image.open(io.BytesIO(image_data))
                                        self._log(f"✓ Imagem extraída do RAR: {image.size}")
                                        return (image, page_count, None)
                                except Exception as e:
                                    error_msg = str(e)
                                    if "Cannot find working tool" in error_msg:
                                        self._log("⚠ UnRAR não encontrado! Instale WinRAR", "warning")
                                        return (None, page_count, None)
                                    self._log(f"✗ Erro ao extrair {filename}: {e}")
                                    continue
                        
                        return (None, page_count, None)
                except Exception as e:
                    if "Cannot find working tool" in str(e):
                        self._log("⚠ UnRAR não encontrado! Instale WinRAR", "warning")
                    return (None, 0, None)
            
            # ZIP
            if detected_format == 'zip':
                self._log("📦 Processando arquivo ZIP")
                with zipfile.ZipFile(file_path) as archive:
                    file_list = archive.namelist()
                    page_count = sum(1 for f in file_list 
                                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')))
                    
                    for filename in sorted(file_list):
                        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                            try:
                                with archive.open(filename) as img_file:
                                    image_data = img_file.read()
                                    image = Image.open(io.BytesIO(image_data))
                                    self._log(f"✓ Imagem extraída do ZIP: {image.size}")
                                    return (image, page_count, None)
                            except Exception as e:
                                self._log(f"✗ Erro ao extrair {filename}: {e}")
                                continue
                    
                    return (None, page_count, None)
            
            # 7z não suportado
            if detected_format == '7z':
                self._log("⚠ Arquivo é 7-Zip, formato não suportado")
                return (None, 0, '7Z_NOT_SUPPORTED')
            
            self._log(f"⚠ Formato desconhecido: {detected_format}")
            return (None, 0, 'UNKNOWN_FORMAT')
            
        except Exception as e:
            self._log(f"✗ Erro ao processar arquivo: {type(e).__name__}: {e}")
            return (None, 0, 'ERROR')