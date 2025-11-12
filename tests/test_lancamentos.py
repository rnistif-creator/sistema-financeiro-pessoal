"""
Testes para endpoints de Lançamentos
"""
import pytest
from datetime import date, timedelta

def test_criar_lancamento(client, tipo_receita):
    """Teste: Criar lançamento financeiro"""
    hoje = date.today()
    response = client.post("/api/lancamentos", json={
        "data_lancamento": hoje.isoformat(),
        "tipo": "receita",
        "tipo_lancamento_id": tipo_receita.id,
        "fornecedor": "Empresa Teste",
        "valor_total": 3000.00,
        "data_primeiro_vencimento": (hoje + timedelta(days=5)).isoformat(),
        "numero_parcelas": 1,
        "valor_medio_parcelas": 3000.00,
        "observacao": "Teste de lançamento"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["fornecedor"] == "Empresa Teste"
    assert data["valor_total"] == 3000.00
    assert data["numero_parcelas"] == 1

def test_listar_lancamentos(client, lancamento_receita, lancamento_despesa):
    """Teste: Listar todos os lançamentos"""
    response = client.get("/api/lancamentos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

def test_obter_lancamento_por_id(client, lancamento_receita):
    """Teste: Obter lançamento por ID"""
    response = client.get(f"/api/lancamentos/{lancamento_receita.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == lancamento_receita.id
    assert data["fornecedor"] == "Empresa XYZ"

def test_obter_lancamento_com_parcelas(client, lancamento_despesa):
    """Teste: Obter lançamento com suas parcelas"""
    response = client.get(f"/api/lancamentos/{lancamento_despesa.id}?incluir_parcelas=true")
    assert response.status_code == 200
    data = response.json()
    assert "parcelas" in data
    assert len(data["parcelas"]) == 3

def test_atualizar_lancamento(client, lancamento_receita, tipo_receita):
    """Teste: Atualizar lançamento"""
    response = client.put(f"/api/lancamentos/{lancamento_receita.id}", json={
        "data_lancamento": lancamento_receita.data_lancamento.isoformat(),
        "tipo": "receita",
        "tipo_lancamento_id": tipo_receita.id,
        "fornecedor": "Empresa Atualizada",
        "valor_total": 5000.00,
        "data_primeiro_vencimento": lancamento_receita.data_primeiro_vencimento.isoformat(),
        "numero_parcelas": 1,
        "valor_medio_parcelas": 5000.00,
        "observacao": "Observação atualizada"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["fornecedor"] == "Empresa Atualizada"
    assert data["observacao"] == "Observação atualizada"

def test_deletar_lancamento(client, db_session, tipo_receita, test_user):
    """Teste: Deletar lançamento"""
    from app.main import Lancamento, Parcela
    
    # Criar lançamento temporário
    hoje = date.today()
    lancamento = Lancamento(
        usuario_id=test_user.id,
        data_lancamento=hoje,
        tipo="receita",
        tipo_lancamento_id=tipo_receita.id,
        fornecedor="Temporário",
        valor_total=1000.00,
        data_primeiro_vencimento=hoje + timedelta(days=5),
        numero_parcelas=1,
        valor_medio_parcelas=1000.00
    )
    db_session.add(lancamento)
    db_session.commit()
    db_session.refresh(lancamento)
    
    # Criar parcela
    parcela = Parcela(
        usuario_id=test_user.id,
        lancamento_id=lancamento.id,
        numero_parcela=1,
        data_vencimento=lancamento.data_primeiro_vencimento,
        valor=lancamento.valor_medio_parcelas,
        paga=0
    )
    db_session.add(parcela)
    db_session.commit()
    
    # Deletar
    response = client.delete(f"/api/lancamentos/{lancamento.id}")
    assert response.status_code == 200
    
    # Verificar se foi deletado
    response = client.get(f"/api/lancamentos/{lancamento.id}")
    assert response.status_code == 404

def test_criar_lancamento_sem_dados_obrigatorios(client):
    """Teste: Tentar criar lançamento sem dados obrigatórios"""
    response = client.post("/api/lancamentos", json={
        "tipo": "receita"
    })
    assert response.status_code == 422

def test_criar_lancamento_parcelado(client, tipo_despesa):
    """Teste: Criar lançamento parcelado e verificar parcelas"""
    hoje = date.today()
    response = client.post("/api/lancamentos", json={
        "data_lancamento": hoje.isoformat(),
        "tipo": "despesa",
        "tipo_lancamento_id": tipo_despesa.id,
        "fornecedor": "Loja XYZ",
        "valor_total": 1200.00,
        "data_primeiro_vencimento": (hoje + timedelta(days=30)).isoformat(),
        "numero_parcelas": 4,
        "valor_medio_parcelas": 300.00,
        "observacao": "Compra parcelada"
    })
    assert response.status_code == 200
    data = response.json()
    
    # Verificar lançamento
    assert data["numero_parcelas"] == 4
    assert data["valor_total"] == 1200.00
    
    # Buscar lançamento com parcelas
    lancamento_id = data["id"]
    response = client.get(f"/api/lancamentos/{lancamento_id}?incluir_parcelas=true")
    data = response.json()
    
    # Verificar parcelas criadas
    assert len(data["parcelas"]) == 4
    for i, parcela in enumerate(data["parcelas"]):
        assert parcela["numero_parcela"] == i + 1
        assert parcela["valor"] == 300.00
        assert parcela["paga"] == 0

def test_filtrar_lancamentos_por_tipo(client, lancamento_receita, lancamento_despesa):
    """Teste: Filtrar lançamentos por tipo"""
    response = client.get("/api/lancamentos?tipo=receita")
    assert response.status_code == 200
    data = response.json()
    assert all(l["tipo"] == "receita" for l in data)
    
    response = client.get("/api/lancamentos?tipo=despesa")
    assert response.status_code == 200
    data = response.json()
    assert all(l["tipo"] == "despesa" for l in data)

def test_filtrar_lancamentos_por_periodo(client, lancamento_receita):
    """Teste: Filtrar lançamentos por período"""
    hoje = date.today()
    ontem = hoje - timedelta(days=1)
    amanha = hoje + timedelta(days=1)
    
    response = client.get(f"/api/lancamentos?data_inicio={ontem.isoformat()}&data_fim={amanha.isoformat()}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
