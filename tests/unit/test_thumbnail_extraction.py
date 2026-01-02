"""Testes para extração de miniaturas de arquivos ZIP/CBR."""
import pytest
from pathlib import Path
import zipfile
import rarfile
import io
from PIL import Image
import tempfile
import os


@pytest.fixture
def sample_cbr_file():
    """Cria um arquivo CBR de teste com uma imagem."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Cria uma imagem de teste
        img = Image.new('RGB', (100, 150), color='red')
        img_path = Path(temp_dir) / "page001.jpg"
        img.save(img_path, 'JPEG')
        
        # Cria o arquivo CBR (que é um ZIP)
        cbr_path = Path(temp_dir) / "test_comic.cbr"
        with zipfile.ZipFile(cbr_path, 'w') as zip_file:
            zip_file.write(img_path, "page001.jpg")
        
        yield cbr_path


def test_extract_first_image_from_cbr_with_sample(sample_cbr_file):
    """Testa extração da primeira imagem de um arquivo CBR criado para teste."""
    file_path = sample_cbr_file
    
    # Tenta abrir como ZIP
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_file:
            # Lista todos os arquivos
            file_list = zip_file.namelist()
            print(f"\nTotal de arquivos no ZIP: {len(file_list)}")
            
            # Procura pela primeira imagem jpg ou png
            image_found = None
            for filename in sorted(file_list):
                lower_name = filename.lower()
                if lower_name.endswith(('.jpg', '.jpeg', '.png')) and not filename.startswith('__MACOSX'):
                    print(f"\nImagem encontrada: {filename}")
                    
                    # Extrai o arquivo para memória
                    with zip_file.open(filename) as image_file:
                        image_data = image_file.read()
                        image = Image.open(io.BytesIO(image_data))
                        image_found = image
                        print(f"Imagem carregada com sucesso!")
                        print(f"  Formato: {image.format}")
                        print(f"  Tamanho: {image.size}")
                        print(f"  Modo: {image.mode}")
                        break
            
            assert image_found is not None, "Nenhuma imagem JPG/PNG encontrada no arquivo"
            assert image_found.size == (100, 150), "Tamanho da imagem incorreto"
            
    except zipfile.BadZipFile as e:
        pytest.fail(f"Erro ao abrir arquivo como ZIP: {e}")
    except Exception as e:
        pytest.fail(f"Erro inesperado: {e}")


def test_extract_first_image_from_real_cbr():
    """Testa extração da primeira imagem de um arquivo CBR real."""
    file_path = r"K:\OneDrive\LIVROS\Quadrinhos_2\02. DC\Milestone Forever\Milestone Forever - 01 de 02.cbr"
    
    # Verifica se o arquivo existe
    if not Path(file_path).exists():
        pytest.skip(f"Arquivo de teste não encontrado: {file_path}")
    
    # Verifica se o arquivo está disponível (não é placeholder)
    try:
        file_size = Path(file_path).stat().st_size
        if file_size < 1000:  # Arquivo muito pequeno, provavelmente é placeholder
            pytest.skip(f"Arquivo parece ser um placeholder do OneDrive (tamanho: {file_size} bytes)")
    except:
        pytest.skip("Não foi possível obter informações do arquivo")
    
    # Tenta abrir como RAR primeiro (CBR é RAR)
    archive_file = None
    try:
        print(f"\nTentando abrir como RAR...")
        archive_file = rarfile.RarFile(file_path, 'r')
        file_list = archive_file.namelist()
        print(f"Arquivo RAR aberto com sucesso!")
        print(f"Total de arquivos: {len(file_list)}")
        print(f"Primeiros 10 arquivos:")
        for i, filename in enumerate(sorted(file_list)[:10]):
            print(f"  {i+1}. {filename}")
        
    except rarfile.BadRarFile:
        print("Não é um arquivo RAR válido, tentando ZIP...")
        # Tenta como ZIP
        try:
            archive_file = zipfile.ZipFile(file_path, 'r')
            file_list = archive_file.namelist()
            print(f"Arquivo ZIP aberto com sucesso!")
            print(f"Total de arquivos: {len(file_list)}")
        except zipfile.BadZipFile as e:
            pytest.skip(f"Arquivo não é RAR nem ZIP válido: {e}")
    except Exception as e:
        pytest.skip(f"Erro ao abrir arquivo: {e}")
    
    if archive_file is None:
        pytest.skip("Não foi possível abrir o arquivo")
    
    # Procura pela primeira imagem jpg ou png
    image_found = None
    for filename in sorted(file_list):
        lower_name = filename.lower()
        if lower_name.endswith(('.jpg', '.jpeg', '.png')) and not filename.startswith('__MACOSX'):
            print(f"\nImagem encontrada: {filename}")
            
            # Extrai o arquivo para memória
            with archive_file.open(filename) as image_file:
                image_data = image_file.read()
                image = Image.open(io.BytesIO(image_data))
                image_found = image
                print(f"Imagem carregada com sucesso!")
                print(f"  Formato: {image.format}")
                print(f"  Tamanho: {image.size}")
                print(f"  Modo: {image.mode}")
                break
    
    archive_file.close()
    assert image_found is not None, "Nenhuma imagem JPG/PNG encontrada no arquivo"


if __name__ == "__main__":
    # Permite executar o teste diretamente
    import sys
    pytest.main([__file__, "-v", "-s"])
