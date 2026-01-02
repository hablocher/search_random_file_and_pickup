"""
Teste unitário para reproduzir o bug de seleção de Volume 02 quando Volume 01 existe sem prefixo.
"""
import os
import tempfile
import shutil
from pathlib import Path
from sequential_selector import (
    analyze_folder_sequence, 
    get_next_unread_file,
    SequentialFileTracker,
    extract_number_from_filename
)


def test_volume_sequence_bug():
    """
    Reproduz o bug: programa escolhe Volume 02 quando Volume 01 existe sem prefixo '_L_'
    """
    # Cria um diretório temporário
    temp_dir = tempfile.mkdtemp(prefix="test_sequence_")
    
    try:
        # Cria arquivos de teste
        files = [
            "A Floresta - Volume 01.cbz",
            "A Floresta - Volume 02.cbz",
            "A Floresta - Volume 03.cbz",
        ]
        
        for file in files:
            file_path = Path(temp_dir) / file
            file_path.touch()
        
        print(f"Diretório de teste: {temp_dir}")
        print(f"Arquivos criados: {files}")
        
        # Testa extração de números
        print("\n=== Teste de Extração de Números ===")
        for file in files:
            result = extract_number_from_filename(file)
            print(f"{file}: {result}")
        
        # Analisa a sequência
        print("\n=== Análise de Sequência ===")
        sequences = analyze_folder_sequence(Path(temp_dir), exclude_prefix="_L_", keywords=None)
        
        print(f"Sequências detectadas: {len(sequences)}")
        for i, seq in enumerate(sequences):
            print(f"\nSequência {i+1}:")
            print(f"  Coleção: {seq['collection']}")
            print(f"  Tipo: {seq['type']}")
            print(f"  Total: {seq['count']}")
            print(f"  Arquivos: {[f['filename'] for f in seq['files']]}")
        
        # Testa seleção do próximo não lido
        print("\n=== Seleção do Próximo Não Lido ===")
        tracker = SequentialFileTracker()
        
        # Nenhum arquivo marcado como lido ainda
        result = get_next_unread_file(sequences, tracker, keywords=None)
        
        if result:
            next_file, selected_sequence, file_info = result
            print(f"Arquivo selecionado: {Path(next_file).name}")
            print(f"Número do arquivo: {file_info['number']}")
            
            expected = "A Floresta - Volume 01.cbz"
            actual = Path(next_file).name
            
            if actual == expected:
                print(f"\n✅ TESTE PASSOU: {actual} foi selecionado")
                return True
            else:
                print(f"\n❌ TESTE FALHOU!")
                print(f"   Esperado: {expected}")
                print(f"   Obtido: {actual}")
                return False
        else:
            print("❌ TESTE FALHOU: Nenhum arquivo foi selecionado")
            return False
            
    finally:
        # Limpa o diretório temporário
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_volume_with_prefix():
    """
    Testa quando Volume 01 tem prefixo '_L_' e deve selecionar Volume 02
    """
    temp_dir = tempfile.mkdtemp(prefix="test_sequence_prefix_")
    
    try:
        # Cria arquivos de teste (Volume 01 com prefixo)
        files = [
            "_L_A Floresta - Volume 01.cbz",
            "A Floresta - Volume 02.cbz",
            "A Floresta - Volume 03.cbz",
        ]
        
        for file in files:
            file_path = Path(temp_dir) / file
            file_path.touch()
        
        print(f"\n\n=== TESTE COM PREFIXO ===")
        print(f"Diretório de teste: {temp_dir}")
        print(f"Arquivos criados: {files}")
        
        # Analisa a sequência
        sequences = analyze_folder_sequence(Path(temp_dir), exclude_prefix="_L_", keywords=None)
        
        print(f"\nSequências detectadas: {len(sequences)}")
        for seq in sequences:
            print(f"  Arquivos: {[f['filename'] for f in seq['files']]}")
        
        # Testa seleção do próximo não lido
        tracker = SequentialFileTracker()
        result = get_next_unread_file(sequences, tracker, keywords=None)
        
        if result:
            next_file, selected_sequence, file_info = result
            actual = Path(next_file).name
            expected = "A Floresta - Volume 02.cbz"
            
            print(f"\nArquivo selecionado: {actual}")
            
            if actual == expected:
                print(f"✅ TESTE PASSOU: {actual} foi selecionado (correto)")
                return True
            else:
                print(f"❌ TESTE FALHOU!")
                print(f"   Esperado: {expected}")
                print(f"   Obtido: {actual}")
                return False
        else:
            print("❌ TESTE FALHOU: Nenhum arquivo foi selecionado")
            return False
            
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_volume_already_read():
    """
    Testa quando Volume 01 já foi lido (rastreado) e deve selecionar Volume 02
    """
    temp_dir = tempfile.mkdtemp(prefix="test_sequence_read_")
    
    try:
        # Cria arquivos de teste
        files = [
            "A Floresta - Volume 01.cbz",
            "A Floresta - Volume 02.cbz",
            "A Floresta - Volume 03.cbz",
        ]
        
        for file in files:
            file_path = Path(temp_dir) / file
            file_path.touch()
        
        print(f"\n\n=== TESTE COM ARQUIVO JÁ LIDO ===")
        print(f"Diretório de teste: {temp_dir}")
        
        # Analisa a sequência
        sequences = analyze_folder_sequence(Path(temp_dir), exclude_prefix="_L_", keywords=None)
        
        # Marca Volume 01 como lido
        tracker = SequentialFileTracker()
        volume_01_path = str(Path(temp_dir) / "A Floresta - Volume 01.cbz")
        tracker.mark_as_read(volume_01_path)
        print(f"Volume 01 marcado como lido")
        
        # Testa seleção do próximo não lido
        result = get_next_unread_file(sequences, tracker, keywords=None)
        
        if result:
            next_file, selected_sequence, file_info = result
            actual = Path(next_file).name
            expected = "A Floresta - Volume 02.cbz"
            
            print(f"Arquivo selecionado: {actual}")
            
            if actual == expected:
                print(f"✅ TESTE PASSOU: {actual} foi selecionado (correto)")
                return True
            else:
                print(f"❌ TESTE FALHOU!")
                print(f"   Esperado: {expected}")
                print(f"   Obtido: {actual}")
                return False
        else:
            print("❌ TESTE FALHOU: Nenhum arquivo foi selecionado")
            return False
            
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    print("=" * 80)
    print("TESTES UNITÁRIOS - BUG DE SEQUÊNCIA")
    print("=" * 80)
    
    test1 = test_volume_sequence_bug()
    test2 = test_volume_with_prefix()
    test3 = test_volume_already_read()
    
    print("\n" + "=" * 80)
    print("RESUMO DOS TESTES")
    print("=" * 80)
    print(f"Teste 1 (Bug Original): {'✅ PASSOU' if test1 else '❌ FALHOU'}")
    print(f"Teste 2 (Com Prefixo): {'✅ PASSOU' if test2 else '❌ FALHOU'}")
    print(f"Teste 3 (Já Lido): {'✅ PASSOU' if test3 else '❌ FALHOU'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM - BUG CONFIRMADO")
