"""Testes para suporte a múltiplos formatos de arquivo compactado (ZIP, RAR, 7-Zip)."""
import pytest
from pathlib import Path
import zipfile
import rarfile
import io
from PIL import Image
import tempfile
import os


@pytest.fixture
def sample_zip_file():
    """Cria um arquivo ZIP de teste."""
    with tempfile.TemporaryDirectory() as temp_dir:
        img = Image.new('RGB', (100, 150), color='blue')
        img_path = Path(temp_dir) / "page001.jpg"
        img.save(img_path, 'JPEG')
        
        zip_path = Path(temp_dir) / "test_comic.cbz"
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            zip_file.write(img_path, "page001.jpg")
        
        yield zip_path


@pytest.fixture
def sample_7z_file():
    """Cria um arquivo 7-Zip de teste."""
    try:
        import py7zr
    except ImportError:
        pytest.skip("py7zr não está instalado")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        img = Image.new('RGB', (100, 150), color='green')
        img_path = Path(temp_dir) / "page001.jpg"
        img.save(img_path, 'JPEG')
        
        sz_path = Path(temp_dir) / "test_comic.cb7"
        with py7zr.SevenZipFile(sz_path, 'w') as sz_file:
            sz_file.write(img_path, "page001.jpg")
        
        yield sz_path


def test_detect_zip_format():
    """Testa detecção de arquivo ZIP."""
    file_path = r"K:\OneDrive\LIVROS\Quadrinhos_2\02. DC\Milestone Forever\Milestone Forever - 01 de 02.cbr"
    
    if not Path(file_path).exists():
        pytest.skip("Arquivo de teste não encontrado")
    
    print(f"\nAnalisando arquivo: {Path(file_path).name}")
    
    # Tenta ZIP
    try:
        with zipfile.ZipFile(file_path, 'r') as zf:
            print(f"✓ Arquivo é ZIP válido ({len(zf.namelist())} arquivos)")
            return
    except zipfile.BadZipFile:
        print("✗ Não é ZIP")
    
    # Tenta RAR
    try:
        with rarfile.RarFile(file_path, 'r') as rf:
            print(f"✓ Arquivo é RAR válido ({len(rf.namelist())} arquivos)")
            return
    except rarfile.BadRarFile:
        print("✗ Não é RAR")
    
    # Tenta 7-Zip
    try:
        import py7zr
        with py7zr.SevenZipFile(file_path, 'r') as sz:
            print(f"✓ Arquivo é 7-Zip válido ({len(sz.getnames())} arquivos)")
            return
    except ImportError:
        print("✗ py7zr não instalado, não pode verificar 7-Zip")
    except Exception as e:
        print(f"✗ Não é 7-Zip: {e}")
    
    pytest.fail("Arquivo não é ZIP, RAR nem 7-Zip")


def test_extract_from_zip(sample_zip_file):
    """Testa extração de imagem de arquivo ZIP."""
    with zipfile.ZipFile(sample_zip_file, 'r') as zf:
        files = zf.namelist()
        assert len(files) > 0
        
        for fname in files:
            if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                with zf.open(fname) as img_file:
                    img_data = img_file.read()
                    img = Image.open(io.BytesIO(img_data))
                    assert img.size == (100, 150)
                    print(f"✓ ZIP: Imagem extraída com sucesso")
                    return
    
    pytest.fail("Nenhuma imagem encontrada no ZIP")


def test_extract_from_7z(sample_7z_file):
    """Testa extração de imagem de arquivo 7-Zip."""
    try:
        import py7zr
    except ImportError:
        pytest.skip("py7zr não está instalado")
    
    with py7zr.SevenZipFile(sample_7z_file, 'r') as sz:
        files = sz.getnames()
        assert len(files) > 0
        
        for fname in files:
            if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                # py7zr extrai para dict
                extracted = sz.read([fname])
                img_data = extracted[fname].read()
                img = Image.open(io.BytesIO(img_data))
                assert img.size == (100, 150)
                print(f"✓ 7-Zip: Imagem extraída com sucesso")
                return
    
    pytest.fail("Nenhuma imagem encontrada no 7-Zip")


def test_real_file_format():
    """Identifica o formato do arquivo real."""
    file_path = r"K:\OneDrive\LIVROS\Quadrinhos_2\02. DC\Milestone Forever\Milestone Forever - 01 de 02.cbr"
    
    if not Path(file_path).exists():
        pytest.skip("Arquivo de teste não encontrado")
    
    print(f"\n{'='*70}")
    print(f"Identificando formato de: {Path(file_path).name}")
    print(f"Tamanho: {Path(file_path).stat().st_size:,} bytes")
    print(f"{'='*70}")
    
    # Lê os primeiros bytes para identificar a assinatura
    with open(file_path, 'rb') as f:
        magic = f.read(10)
        print(f"\nAssinatura (hex): {magic[:10].hex()}")
        
        # ZIP: 50 4B (PK)
        if magic[:2] == b'PK':
            print("✓ Assinatura: ZIP (PK)")
        # RAR: 52 61 72 21 (Rar!)
        elif magic[:4] == b'Rar!':
            print("✓ Assinatura: RAR")
        # 7-Zip: 37 7A BC AF 27 1C
        elif magic[:6] == b'7z\xbc\xaf\x27\x1c':
            print("✓ Assinatura: 7-Zip")
        else:
            print(f"? Assinatura desconhecida")


if __name__ == "__main__":
    import sys
    pytest.main([__file__, "-v", "-s"])
