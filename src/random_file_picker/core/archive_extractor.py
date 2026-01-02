"""Extração de imagens de arquivos compactados (ZIP/RAR) e PDF."""

import io
import zipfile
from pathlib import Path
from typing import Optional, Tuple, Callable

import rarfile
from PIL import Image

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
    
    def __init__(self, log_callback=None):
        """Inicializa o extrator com callback opcional para logs."""
        self.log_callback = log_callback
    
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
            'zip', 'rar', 'rar5', '7z', 'pdf' ou None.
        """
        if len(file_data) < 10:
            return None
        
        # ZIP: 50 4B (PK)
        if file_data[:2] == b'PK':
            return 'zip'
        # RAR 1.5-4.x: 52 61 72 21 1A 07 (Rar!)
        elif file_data[:4] == b'Rar!':
            return 'rar'
        # RAR 5+: 52 61 72 21 1A 07 01 00
        elif file_data[:8] == b'Rar!\x1a\x07\x01\x00':
            return 'rar5'
        # 7-Zip: 37 7A BC AF 27 1C
        elif file_data[:6] == b'7z\xbc\xaf\x27\x1c':
            return '7z'
        # PDF: 25 50 44 46 (%PDF)
        elif file_data[:4] == b'%PDF':
            return 'pdf'
        
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
        
        # RAR - VALIDA BUFFER ANTES DE EXTRAIR
        if file_ext in ['.rar', '.cbr'] or detected_format in ['rar', 'rar5']:
            self._log("📦 Detectado arquivo RAR/CBR")
            
            # Valida se o buffer é válido antes de tentar extrair
            if not validate_rar_buffer(file_data, self.log_callback):
                self._log("⚠ Buffer RAR inválido - arquivo não totalmente sincronizado")
                return (None, 0, 'SYNCING')
            
            image, page_count, status = self.extract_from_rar(file_data)
            return (image, page_count, status)
        
        # ZIP - VALIDA BUFFER ANTES DE EXTRAIR
        if file_ext in ['.zip', '.cbz'] or detected_format == 'zip':
            self._log("📦 Detectado arquivo ZIP/CBZ")
            
            # Valida se o buffer é válido antes de tentar extrair
            if not validate_zip_buffer(file_data, self.log_callback):
                self._log("⚠ Buffer ZIP inválido - arquivo não totalmente sincronizado")
                return (None, 0, 'SYNCING')
            
            image, page_count = self.extract_from_zip(file_data)
            return (image, page_count, None)
        
        # Formato não suportado
        if detected_format == '7z':
            return (None, 0, '7Z_NOT_SUPPORTED')
        
        return (None, 0, 'UNKNOWN_FORMAT')
