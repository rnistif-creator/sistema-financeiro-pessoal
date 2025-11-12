"""Script de teste para o endpoint de geração de PDF"""
import requests
import sys

def test_pdf_endpoint():
    url = "http://127.0.0.1:8001/api/relatorios/tabela-anual-pdf"
    params = {
        "ano": 2025,
        "tipo_data": "vencimento"
    }
    
    print(f"🧪 Testando endpoint: {url}")
    print(f"📋 Parâmetros: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            # Salvar PDF
            filename = "test_relatorio.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ PDF gerado com sucesso! Salvo como: {filename}")
            print(f"📦 Tamanho: {len(response.content)} bytes")
            return True
        elif response.status_code == 404:
            print(f"⚠️  Erro 404: {response.json()}")
            return False
        else:
            print(f"❌ Erro: {response.status_code}")
            try:
                print(f"📝 Resposta: {response.json()}")
            except:
                print(f"📝 Resposta: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("💡 Certifique-se que o servidor está rodando na porta 8001")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_endpoint()
    sys.exit(0 if success else 1)
