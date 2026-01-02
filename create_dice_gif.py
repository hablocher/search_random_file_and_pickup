
import random
from PIL import Image, ImageDraw, ImageFont

def create_dice_gif(output_path="dice.gif", size=100, frames=30, bg_color="white", dice_color="black"):
    """
    Cria um GIF animado de um dado de seis lados girando.

    Args:
        output_path (str): Caminho para salvar o arquivo GIF.
        size (int): Tamanho da imagem do GIF em pixels (largura e altura).
        frames (int): Número total de quadros na animação.
        bg_color (str): Cor de fundo.
        dice_color (str): Cor do dado (texto).
    """
    # Unicode para as faces do dado
    dice_faces = ['\u2680', '\u2681', '\u2682', '\u2683', '\u2684', '\u2685']
    
    images = []
    
    # Tenta encontrar uma fonte comum. Se não encontrar, usa a padrão.
    try:
        font = ImageFont.truetype("arial.ttf", size=int(size * 0.8))
    except IOError:
        print("Fonte Arial não encontrada, usando a fonte padrão.")
        font = ImageFont.load_default()

    # Simula o giro do dado: rápido no início, depois desacelera
    for i in range(frames):
        # Cria uma nova imagem para o quadro
        image = Image.new("RGB", (size, size), bg_color)
        draw = ImageDraw.Draw(image)
        
        # Escolhe uma face aleatória para cada quadro para simular o giro
        face = random.choice(dice_faces)
        
        # Calcula a posição para centralizar o texto
        text_width, text_height = draw.textsize(face, font=font)
        x = (size - text_width) / 2
        y = (size - text_height) / 2
        
        # Desenha a face do dado no quadro
        draw.text((x, y), face, fill=dice_color, font=font)
        
        images.append(image)

    # Escolhe o resultado final do dado
    final_face = random.choice(dice_faces)
    
    # Adiciona alguns quadros do resultado final para o dado "parar"
    for _ in range(10):
        image = Image.new("RGB", (size, size), bg_color)
        draw = ImageDraw.Draw(image)
        text_width, text_height = draw.textsize(final_face, font=font)
        x = (size - text_width) / 2
        y = (size - text_height) / 2
        draw.text((x, y), final_face, fill=dice_color, font=font)
        images.append(image)
        
    # Define a duração de cada quadro (em milissegundos)
    # Quadros de giro são rápidos, resultado final é mais lento
    durations = [50] * (frames - 1) + [1000] * 11

    # Salva os quadros como um GIF animado
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0  # 0 significa loop infinito
    )
    print(f"GIF animado salvo em: {output_path}")

if __name__ == "__main__":
    create_dice_gif()
