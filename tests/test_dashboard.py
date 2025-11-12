"""
Testes para endpoints de Dashboard e Relatórios
"""
import pytest
from datetime import date, timedelta

def test_dashboard_totalizadores(client, lancamento_receita, lancamento_despesa):
    """Teste: Obter totalizadores do dashboard"""
    hoje = date.today()
    fim = hoje + timedelta(days=90)
    
    response = client.get(f"/api/dashboard?tipo_data=lancamento&data_inicio={hoje.isoformat()}&data_fim={fim.isoformat()}")
    assert response.status_code == 200
    data = response.json()
    
    assert "totalizadores" in data
    assert "receitas" in data["totalizadores"]
    assert "despesas" in data["totalizadores"]
    assert "saldo" in data["totalizadores"]
    assert "qtd_receitas" in data["totalizadores"]
    assert "qtd_despesas" in data["totalizadores"]

def test_dashboard_por_tipo(client, lancamento_receita, lancamento_despesa):
    """Teste: Obter dados do dashboard agrupados por tipo"""
    hoje = date.today()
    fim = hoje + timedelta(days=90)
    
    response = client.get(f"/api/dashboard?tipo_data=lancamento&data_inicio={hoje.isoformat()}&data_fim={fim.isoformat()}")
    assert response.status_code == 200
    data = response.json()
    
    assert "receitas_por_tipo" in data
    assert "despesas_por_tipo" in data
    assert isinstance(data["receitas_por_tipo"], list)
    assert isinstance(data["despesas_por_tipo"], list)

def test_dashboard_filtro_natureza(client, lancamento_receita, lancamento_despesa):
    """Teste: Filtrar dashboard por natureza"""
    hoje = date.today()
    fim = hoje + timedelta(days=90)
    
    # Filtrar apenas receitas
    response = client.get(f"/api/dashboard?tipo_data=lancamento&data_inicio={hoje.isoformat()}&data_fim={fim.isoformat()}&natureza=receita")
    assert response.status_code == 200
    data = response.json()
    assert data["totalizadores"]["despesas"] == 0
    
    # Filtrar apenas despesas
    response = client.get(f"/api/dashboard?tipo_data=lancamento&data_inicio={hoje.isoformat()}&data_fim={fim.isoformat()}&natureza=despesa")
    assert response.status_code == 200
    data = response.json()
    assert data["totalizadores"]["receitas"] == 0

def test_dashboard_tipo_data_vencimento(client, lancamento_receita):
    """Teste: Dashboard com tipo de data = vencimento"""
    hoje = date.today()
    fim = hoje + timedelta(days=90)
    
    response = client.get(f"/api/dashboard?tipo_data=vencimento&data_inicio={hoje.isoformat()}&data_fim={fim.isoformat()}")
    assert response.status_code == 200
    data = response.json()
    assert data["periodo"]["tipo_data"] == "vencimento"

def test_dashboard_tipo_data_pagamento(client, lancamento_receita, db_session):
    """Teste: Dashboard com tipo de data = pagamento"""
    from app.main import Parcela
    
    # Marcar parcela como paga
    parcela = db_session.query(Parcela).filter_by(lancamento_id=lancamento_receita.id).first()
    hoje = date.today()
    parcela.paga = 1
    parcela.data_pagamento = hoje
    parcela.valor_pago = 5000.00
    db_session.commit()
    
    fim = hoje + timedelta(days=90)
    
    response = client.get(f"/api/dashboard?tipo_data=pagamento&data_inicio={hoje.isoformat()}&data_fim={fim.isoformat()}")
    assert response.status_code == 200
    data = response.json()
    assert data["periodo"]["tipo_data"] == "pagamento"
    assert data["totalizadores"]["receitas"] > 0

def test_tabela_anual(client, lancamento_receita, lancamento_despesa):
    """Teste: Obter tabela anual por tipo"""
    ano_atual = date.today().year
    
    response = client.get(f"/api/dashboard/tabela-anual?ano={ano_atual}&tipo_data=vencimento")
    assert response.status_code == 200
    data = response.json()
    
    assert "ano" in data
    assert data["ano"] == ano_atual
    assert "tipo_data" in data
    assert "tipos" in data
    assert isinstance(data["tipos"], list)

def test_evolucao_mensal(client, lancamento_receita, lancamento_despesa):
    """Teste: Obter evolução mensal"""
    response = client.get("/api/dashboard/evolucao?meses=6&tipo_data=vencimento")
    assert response.status_code == 200
    data = response.json()
    
    assert "labels" in data
    assert "receitas" in data
    assert "despesas" in data
    assert len(data["labels"]) == 6
    assert len(data["receitas"]) == 6
    assert len(data["despesas"]) == 6

def test_exportar_tabela_anual_pdf(client, lancamento_receita, lancamento_despesa):
    """Teste: Exportar tabela anual em PDF"""
    ano_atual = date.today().year
    
    response = client.get(f"/api/relatorios/tabela-anual-pdf?ano={ano_atual}&tipo_data=vencimento")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0

def test_exportar_lancamentos_excel(client, lancamento_receita, lancamento_despesa):
    """Teste: Exportar lançamentos em Excel"""
    response = client.get("/api/relatorios/lancamentos-excel")
    assert response.status_code == 200
    assert "spreadsheet" in response.headers["content-type"]
    assert len(response.content) > 0

def test_exportar_parcelas_excel(client, lancamento_receita, lancamento_despesa):
    """Teste: Exportar parcelas em Excel"""
    hoje = date.today()
    fim = hoje + timedelta(days=90)
    
    response = client.get(f"/api/relatorios/parcelas-excel?data_inicio={hoje.isoformat()}&data_fim={fim.isoformat()}")
    assert response.status_code == 200
    assert "spreadsheet" in response.headers["content-type"]
    assert len(response.content) > 0

def test_dashboard_sem_dados(client):
    """Teste: Dashboard sem dados no período"""
    # Período no passado distante sem dados
    inicio = date(2020, 1, 1)
    fim = date(2020, 1, 31)
    
    response = client.get(f"/api/dashboard?tipo_data=lancamento&data_inicio={inicio.isoformat()}&data_fim={fim.isoformat()}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["totalizadores"]["receitas"] == 0
    assert data["totalizadores"]["despesas"] == 0
    assert data["totalizadores"]["saldo"] == 0

def test_exportar_sem_dados(client):
    """Teste: Tentar exportar sem dados"""
    # Período sem dados
    inicio = date(2020, 1, 1)
    fim = date(2020, 1, 31)
    
    response = client.get(f"/api/relatorios/lancamentos-excel?data_inicio={inicio.isoformat()}&data_fim={fim.isoformat()}")
    assert response.status_code == 404
    
    response = client.get(f"/api/relatorios/parcelas-excel?data_inicio={inicio.isoformat()}&data_fim={fim.isoformat()}")
    assert response.status_code == 404
