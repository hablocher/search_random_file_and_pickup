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
    
    def create_thumbnail(self, image: Image.Image, fit_mode: str = 'thumbnail') -> Image.Image:
        """Cria thumbnail mantendo proporção da imagem.
        
        Args:
            image: Imagem PIL original.
            fit_mode: Modo de ajuste - 'thumbnail' (reduz mantendo proporção) 
                     ou 'contain' (ajusta para caber mantendo proporção completa).
            
        Returns:
            Imagem redimensionada.
        """
        if fit_mode == 'contain':
            # Calcula proporções para caber exatamente no espaço
            img_width, img_height = image.size
            max_width, max_height = self.max_size
            
            # Calcula fator de escala mantendo proporção
            width_ratio = max_width / img_width
            height_ratio = max_height / img_height
            scale = min(width_ratio, height_ratio)
            
            # Calcula novo tamanho
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Redimensiona mantendo proporção exata
            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            # Modo padrão: thumbnail (reduz mantendo proporção dentro do limite)
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
        
        # Trata texto multilinha
        lines = message.split('\n')
        line_height = 15  # Altura aproximada de cada linha
        total_height = len(lines) * line_height
        y = (self.max_size[1] - total_height) // 2
        
        # Desenha cada linha centralizada
        for line in lines:
            if line.strip():  # Ignora linhas vazias para o cálculo
                bbox = draw.textbbox((0, 0), line)
                text_width = bbox[2] - bbox[0]
                x = (self.max_size[0] - text_width) // 2
                draw.text((x, y), line, fill='#666666')
            y += line_height
        
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
