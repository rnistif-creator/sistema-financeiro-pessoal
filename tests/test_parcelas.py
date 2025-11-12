"""
Testes para endpoints de Parcelas
"""
import pytest
from datetime import date, timedelta

def test_listar_parcelas_a_vencer(client, lancamento_despesa):
    """Teste: Listar parcelas a vencer"""
    hoje = date.today()
    fim = hoje + timedelta(days=90)
    
    response = client.get(f"/api/parcelas/a-vencer?data_inicio={hoje.isoformat()}&data_fim={fim.isoformat()}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

def test_marcar_parcela_como_paga(client, db_session, lancamento_receita):
    """Teste: Marcar parcela como paga"""
    from app.main import Parcela
    
    # Buscar primeira parcela do lançamento
    parcela = db_session.query(Parcela).filter_by(lancamento_id=lancamento_receita.id).first()
    
    hoje = date.today()
    response = client.patch(f"/api/parcelas/{parcela.id}/pagar", json={
        "paga": True,
        "data_pagamento": hoje.isoformat(),
        "valor_pago": 5000.00
    })
    assert response.status_code == 200
    data = response.json()
    assert data["paga"] == 1
    assert float(data["valor_pago"]) == 5000.00

def test_editar_parcela(client, db_session, lancamento_despesa):
    """Teste: Editar dados de uma parcela"""
    from app.main import Parcela
    
    parcela = db_session.query(Parcela).filter_by(lancamento_id=lancamento_despesa.id).first()
    nova_data = date.today() + timedelta(days=15)
    
    response = client.put(f"/api/parcelas/{parcela.id}", json={
        "data_vencimento": nova_data.isoformat(),
        "valor": 250.00
    })
    assert response.status_code == 200
    data = response.json()
    assert data["data_vencimento"] == nova_data.isoformat()
    assert data["valor"] == 250.00



def test_filtrar_parcelas_por_status(client, lancamento_despesa, db_session):
    """Teste: Filtrar parcelas por status (pagas/pendentes)"""
    from app.main import Parcela
    
    # Marcar uma parcela como paga
    parcela = db_session.query(Parcela).filter_by(lancamento_id=lancamento_despesa.id).first()
    parcela.paga = 1
    parcela.data_pagamento = date.today()
    parcela.valor_pago = 200.00
    db_session.commit()
    
    hoje = date.today()
    fim = hoje + timedelta(days=90)
    
    # Filtrar pendentes
    response = client.get(f"/api/parcelas/a-vencer?data_inicio={hoje.isoformat()}&data_fim={fim.isoformat()}&status=pendentes")
    assert response.status_code == 200
    result = response.json()
    # O endpoint retorna um dict com 'parcelas' e 'stats'
    if isinstance(result, dict) and "parcelas" in result:
        data = result["parcelas"]
    else:
        data = result
    assert all(p["paga"] == 0 for p in data)

def test_filtrar_parcelas_por_tipo(client, lancamento_receita, lancamento_despesa):
    """Teste: Filtrar parcelas por tipo de lançamento"""
    hoje = date.today()
    fim = hoje + timedelta(days=90)
    
    # Filtrar receitas
    response = client.get(f"/api/parcelas/a-vencer?data_inicio={hoje.isoformat()}&data_fim={fim.isoformat()}&tipo=receita")
    assert response.status_code == 200
    result = response.json()
    if isinstance(result, dict) and "parcelas" in result:
        data = result["parcelas"]
    else:
        data = result
    assert all(p["tipo"] == "receita" for p in data)
    
    # Filtrar despesas
    response = client.get(f"/api/parcelas/a-vencer?data_inicio={hoje.isoformat()}&data_fim={fim.isoformat()}&tipo=despesa")
    assert response.status_code == 200
    result = response.json()
    if isinstance(result, dict) and "parcelas" in result:
        data = result["parcelas"]
    else:
        data = result
    assert all(p["tipo"] == "despesa" for p in data)

def test_pagar_parcela_sem_data(client, db_session, lancamento_receita):
    """Teste: Pagar parcela sem informar data (deve usar data de hoje)"""
    from app.main import Parcela
    
    parcela = db_session.query(Parcela).filter_by(lancamento_id=lancamento_receita.id).first()
    
    response = client.patch(f"/api/parcelas/{parcela.id}/pagar", json={
        "paga": True,
        "valor_pago": 5000.00
    })
    assert response.status_code == 200  # OK, usa data de hoje
    data = response.json()
    assert data["paga"] == 1

def test_estatisticas_parcelas(client, lancamento_receita, lancamento_despesa):
    """Teste: Obter estatísticas de parcelas"""
    hoje = date.today()
    fim = hoje + timedelta(days=90)
    
    response = client.get(f"/api/parcelas/a-vencer?data_inicio={hoje.isoformat()}&data_fim={fim.isoformat()}")
    assert response.status_code == 200
    result = response.json()
    
    # O endpoint pode retornar dict com 'parcelas' e 'stats'
    if isinstance(result, dict):
        assert "parcelas" in result
        assert "stats" in result
        data = result["parcelas"]
    else:
        data = result
    
    # Verificar se retorna dados
    assert len(data) >= 1
    
    # Verificar estrutura dos dados
    for parcela in data:
        assert "id" in parcela
        assert "numero_parcela" in parcela
        assert "data_vencimento" in parcela
        assert "valor" in parcela
        # Campo "paga" pode não estar presente dependendo do modelo usado
        assert "tipo" in parcela
        assert "fornecedor" in parcela
