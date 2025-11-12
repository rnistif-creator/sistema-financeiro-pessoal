#!/usr/bin/env python3
"""
Script de Smoke Test para validar ambientes Staging e Produção.

Valida:
- Health checks (/health e /api/health)
- Endpoints principais (login, dashboard, etc.)
- Tempos de resposta
- Status codes

Uso:
    python smoke_test.py --staging
    python smoke_test.py --production
    python smoke_test.py --all
"""

import sys
import time
from typing import Dict, List, Tuple
from datetime import datetime
try:
    import httpx as requests  # Usar httpx que já está no requirements.txt
except ImportError:
    print("Erro: httpx não encontrado. Instale com: pip install httpx")
    sys.exit(1)

# URLs dos ambientes
ENVIRONMENTS = {
    "staging": "https://sistema-financeiro-pessoal-staging.onrender.com",
    "production": "https://seu-app-producao.onrender.com"  # Atualizar quando disponível
}

# Timeout padrão para requisições (segundos)
REQUEST_TIMEOUT = 30

# Limite de tempo de resposta aceitável (segundos)
RESPONSE_TIME_THRESHOLD = 5.0


class Colors:
    """Códigos ANSI para cores no terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Imprime cabeçalho formatado"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")


def print_success(text: str):
    """Imprime mensagem de sucesso"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text: str):
    """Imprime mensagem de erro"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text: str):
    """Imprime mensagem de aviso"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_info(text: str):
    """Imprime mensagem informativa"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")


def test_health_check(base_url: str) -> Tuple[bool, float]:
    """Testa o endpoint /health"""
    try:
        start_time = time.time()
        response = requests.get(
            f"{base_url}/health",
            timeout=REQUEST_TIMEOUT
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                print_success(f"/health: OK ({elapsed:.2f}s)")
                return True, elapsed
            else:
                print_error(f"/health: Status inválido: {data}")
                return False, elapsed
        else:
            print_error(f"/health: Status code {response.status_code}")
            return False, elapsed
    except requests.exceptions.Timeout:
        print_error(f"/health: Timeout após {REQUEST_TIMEOUT}s")
        return False, REQUEST_TIMEOUT
    except Exception as e:
        print_error(f"/health: Erro - {str(e)}")
        return False, 0


def test_api_health_check(base_url: str) -> Tuple[bool, float]:
    """Testa o endpoint /api/health"""
    try:
        start_time = time.time()
        response = requests.get(
            f"{base_url}/api/health",
            timeout=REQUEST_TIMEOUT
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok" and "time" in data:
                print_success(f"/api/health: OK ({elapsed:.2f}s)")
                return True, elapsed
            else:
                print_error(f"/api/health: Resposta inválida: {data}")
                return False, elapsed
        else:
            print_error(f"/api/health: Status code {response.status_code}")
            return False, elapsed
    except requests.exceptions.Timeout:
        print_error(f"/api/health: Timeout após {REQUEST_TIMEOUT}s")
        return False, REQUEST_TIMEOUT
    except Exception as e:
        print_error(f"/api/health: Erro - {str(e)}")
        return False, 0


def test_login_page(base_url: str) -> Tuple[bool, float]:
    """Testa se a página de login está acessível"""
    try:
        start_time = time.time()
        response = requests.get(
            f"{base_url}/login",
            timeout=REQUEST_TIMEOUT
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            # Verificar se a resposta contém elementos esperados da página de login
            if "login" in response.text.lower() and "senha" in response.text.lower():
                print_success(f"/login: Página carregada ({elapsed:.2f}s)")
                return True, elapsed
            else:
                print_warning(f"/login: Página carregada mas sem conteúdo esperado ({elapsed:.2f}s)")
                return True, elapsed
        else:
            print_error(f"/login: Status code {response.status_code}")
            return False, elapsed
    except requests.exceptions.Timeout:
        print_error(f"/login: Timeout após {REQUEST_TIMEOUT}s")
        return False, REQUEST_TIMEOUT
    except Exception as e:
        print_error(f"/login: Erro - {str(e)}")
        return False, 0


def test_static_files(base_url: str) -> Tuple[bool, float]:
    """Testa se arquivos estáticos são servidos corretamente"""
    static_files = [
        "/static/components.css",
        "/static/components.js",
        "/static/sw.js",
        "/static/manifest.json"
    ]
    
    all_ok = True
    total_time = 0
    
    for file_path in static_files:
        try:
            start_time = time.time()
            response = requests.get(
                f"{base_url}{file_path}",
                timeout=REQUEST_TIMEOUT
            )
            elapsed = time.time() - start_time
            total_time += elapsed
            
            if response.status_code == 200:
                print_success(f"{file_path}: OK ({elapsed:.2f}s)")
            else:
                print_error(f"{file_path}: Status code {response.status_code}")
                all_ok = False
        except Exception as e:
            print_error(f"{file_path}: Erro - {str(e)}")
            all_ok = False
    
    return all_ok, total_time


def run_smoke_test(env_name: str, base_url: str) -> Dict[str, any]:
    """Executa todos os testes para um ambiente"""
    print_header(f"SMOKE TEST - {env_name.upper()}")
    print_info(f"URL: {base_url}")
    print_info(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    results = {
        "environment": env_name,
        "url": base_url,
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "total_time": 0,
        "passed": 0,
        "failed": 0
    }
    
    # Teste 1: Health Check
    print_info("Testando health checks...")
    success, elapsed = test_health_check(base_url)
    results["tests"]["health_check"] = {"success": success, "time": elapsed}
    results["total_time"] += elapsed
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Teste 2: API Health Check
    success, elapsed = test_api_health_check(base_url)
    results["tests"]["api_health_check"] = {"success": success, "time": elapsed}
    results["total_time"] += elapsed
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    print()
    
    # Teste 3: Página de Login
    print_info("Testando páginas públicas...")
    success, elapsed = test_login_page(base_url)
    results["tests"]["login_page"] = {"success": success, "time": elapsed}
    results["total_time"] += elapsed
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    print()
    
    # Teste 4: Arquivos Estáticos
    print_info("Testando arquivos estáticos...")
    success, elapsed = test_static_files(base_url)
    results["tests"]["static_files"] = {"success": success, "time": elapsed}
    results["total_time"] += elapsed
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Verificar tempo de resposta
    avg_time = results["total_time"] / len(results["tests"])
    if avg_time > RESPONSE_TIME_THRESHOLD:
        print()
        print_warning(f"Tempo médio de resposta alto: {avg_time:.2f}s (limite: {RESPONSE_TIME_THRESHOLD}s)")
    
    return results


def print_summary(results_list: List[Dict]):
    """Imprime resumo dos testes"""
    print_header("RESUMO DOS TESTES")
    
    total_passed = 0
    total_failed = 0
    
    for results in results_list:
        env = results["environment"]
        passed = results["passed"]
        failed = results["failed"]
        total_time = results["total_time"]
        total_tests = passed + failed
        
        total_passed += passed
        total_failed += failed
        
        print(f"\n{Colors.BOLD}{env.upper()}:{Colors.RESET}")
        print(f"  URL: {results['url']}")
        print(f"  Testes: {passed}/{total_tests} passaram")
        print(f"  Tempo total: {total_time:.2f}s")
        
        if failed > 0:
            print_error(f"  {failed} teste(s) falharam")
        else:
            print_success(f"  Todos os testes passaram!")
    
    print(f"\n{Colors.BOLD}TOTAL GERAL:{Colors.RESET}")
    print(f"  Testes passaram: {total_passed}")
    print(f"  Testes falharam: {total_failed}")
    print()
    
    if total_failed > 0:
        print_error("ALGUNS TESTES FALHARAM - Verifique os logs acima")
        return False
    else:
        print_success("TODOS OS TESTES PASSARAM!")
        return True


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Smoke test para ambientes Staging e Produção")
    parser.add_argument(
        "--staging",
        action="store_true",
        help="Testar apenas ambiente de staging"
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Testar apenas ambiente de produção"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Testar todos os ambientes"
    )
    
    args = parser.parse_args()
    
    # Se nenhuma opção for especificada, testar todos
    if not (args.staging or args.production or args.all):
        args.all = True
    
    results_list = []
    
    try:
        if args.staging or args.all:
            results = run_smoke_test("staging", ENVIRONMENTS["staging"])
            results_list.append(results)
        
        if args.production or args.all:
            if ENVIRONMENTS["production"].startswith("https://seu-app"):
                print_warning("\nURL de produção ainda não configurada. Pulando testes de produção.")
            else:
                results = run_smoke_test("production", ENVIRONMENTS["production"])
                results_list.append(results)
        
        # Imprimir resumo
        all_passed = print_summary(results_list)
        
        # Retornar código de saída apropriado
        sys.exit(0 if all_passed else 1)
        
    except KeyboardInterrupt:
        print()
        print_warning("Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print()
        print_error(f"Erro inesperado: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
