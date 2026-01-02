"""Geração de thumbnails e imagens padrão."""

from PIL import Image, ImageDraw
from typing import Tuple


class ThumbnailGenerator:
    """Gera thumbnails e imagens padrão para exibição."""
    
    def __init__(self, max_size: Tuple[int, int] = (200, 280)):
        """Inicializa o gerador de thumbnails.
        
        Args:
            max_size: Tamanho máximo da thumbnail (largura, altura).
        """
        self.max_size = max_size
    
    def create_thumbnail(self, image: Image.Image) -> Image.Image:
        """Cria thumbnail mantendo proporção da imagem.
        
        Args:
            image: Imagem PIL original.
            
        Returns:
            Imagem redimensionada.
        """
        # Cria uma cópia para não modificar o original
        thumbnail = image.copy()
        thumbnail.thumbnail(self.max_size, Image.Resampling.LANCZOS)
        return thumbnail
    
    def create_default_thumbnail(self, message: str = "Prévia não disponível") -> Image.Image:
        """Cria imagem padrão com mensagem.
        
        Args:
            message: Texto a exibir na imagem.
            
        Returns:
            Imagem PIL com mensagem centralizada.
        """
        # Cria uma imagem cinza com texto
        img = Image.new('RGB', self.max_size, color='#e0e0e0')
        draw = ImageDraw.Draw(img)
        
        # Adiciona borda
        draw.rectangle([0, 0, self.max_size[0]-1, self.max_size[1]-1], 
                      outline='#999999', width=2)
        
        # Adiciona texto no centro (usa fonte padrão)
        bbox = draw.textbbox((0, 0), message)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (self.max_size[0] - text_width) // 2
        y = (self.max_size[1] - text_height) // 2
        
        draw.text((x, y), message, fill='#666666')
        
        return img
    
    def create_syncing_thumbnail(self) -> Image.Image:
        """Cria thumbnail para arquivo sincronizando.
        
        Returns:
            Imagem PIL indicando sincronização.
        """
        return self.create_default_thumbnail(
            "Sincronizando\ndo OneDrive...\n\nTente novamente\nem alguns minutos"
        )
    
    def create_error_thumbnail(self) -> Image.Image:
        """Cria thumbnail para erro.
        
        Returns:
            Imagem PIL indicando erro.
        """
        return self.create_default_thumbnail("Erro ao\ncarregar")
    
    def create_format_not_supported_thumbnail(self, format_name: str) -> Image.Image:
        """Cria thumbnail para formato não suportado.
        
        Args:
            format_name: Nome do formato (ex: "7-Zip").
            
        Returns:
            Imagem PIL indicando formato não suportado.
        """
        return self.create_default_thumbnail(
            f"{format_name}\nnão suportado"
        )
