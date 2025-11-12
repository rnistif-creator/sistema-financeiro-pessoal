"""
Testes para endpoints de Tipos de Lançamentos
"""
import pytest
from datetime import date

def test_criar_tipo_lancamento(client):
    """Teste: Criar tipo de lançamento"""
    response = client.post("/api/tipos", json={
        "nome": "Aluguel",
        "natureza": "despesa"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Aluguel"
    assert data["natureza"] == "despesa"
    assert "id" in data
    assert "created_at" in data

def test_listar_tipos_lancamentos(client, tipo_receita, tipo_despesa):
    """Teste: Listar todos os tipos de lançamentos"""
    response = client.get("/api/tipos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert any(t["nome"] == "Salário" for t in data)
    assert any(t["nome"] == "Supermercado" for t in data)

def test_deletar_tipo_lancamento(client, db_session, test_user):
    """Teste: Deletar tipo de lançamento sem lançamentos associados"""
    # Criar tipo temporário
    from app.main import TipoLancamento
    tipo = TipoLancamento(
        usuario_id=test_user.id,
        nome="Tipo Temporário",
        natureza="despesa",
        created_at=date.today()
    )
    db_session.add(tipo)
    db_session.commit()
    db_session.refresh(tipo)
    
    # Deletar tipo
    response = client.delete(f"/api/tipos/{tipo.id}")
    assert response.status_code == 200

def test_criar_tipo_sem_nome(client):
    """Teste: Tentar criar tipo sem nome"""
    response = client.post("/api/tipos", json={
        "natureza": "receita"
    })
    assert response.status_code == 422  # Validation error

def test_criar_tipo_natureza_invalida(client):
    """Teste: Tentar criar tipo com natureza inválida"""
    response = client.post("/api/tipos", json={
        "nome": "Teste",
        "natureza": "invalida"
    })
    assert response.status_code == 422
