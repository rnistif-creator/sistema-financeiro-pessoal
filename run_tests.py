"""
Script para executar todos os testes
"""
import subprocess
import sys

def run_tests():
    """Executa os testes com pytest"""
    print("🧪 Executando testes automatizados...")
    print("=" * 60)
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-v", "--tb=short"],
        cwd="."
    )
    
    print("=" * 60)
    if result.returncode == 0:
        print("✅ Todos os testes passaram!")
    else:
        print("❌ Alguns testes falharam")
        
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_tests())
