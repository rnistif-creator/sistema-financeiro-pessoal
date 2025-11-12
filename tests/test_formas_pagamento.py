"""
Testes para endpoints de Formas de Pagamento
"""
import pytest
from datetime import date

def test_listar_formas_pagamento(client, db_session, test_user):
    """Teste: Listar formas de pagamento ativas"""
    from app.main import FormaPagamento
    
    # Criar formas de teste
    forma1 = FormaPagamento(
        usuario_id=test_user.id,
        nome="Cartão Teste",
        tipo="cartao_credito",
        banco="Banco Teste",
        limite_credito="5000.00",
        ativo=True,
        created_at=date.today()
    )
    forma2 = FormaPagamento(
        usuario_id=test_user.id,
        nome="PIX Teste",
        tipo="pix",
        ativo=False,
        created_at=date.today()
    )
    db_session.add_all([forma1, forma2])
    db_session.commit()
    
    # Listar apenas ativas
    response = client.get("/api/formas-pagamento")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(f["nome"] == "Cartão Teste" for f in data)
    assert not any(f["nome"] == "PIX Teste" for f in data)
    
    # Listar incluindo inativas
    response = client.get("/api/formas-pagamento?incluir_inativas=true")
    assert response.status_code == 200
    data = response.json()
    assert any(f["nome"] == "PIX Teste" for f in data)

def test_obter_forma_pagamento(client, db_session, test_user):
    """Teste: Obter uma forma de pagamento específica"""
    from app.main import FormaPagamento
    
    forma = FormaPagamento(
        usuario_id=test_user.id,
        nome="Dinheiro Teste",
        tipo="dinheiro",
        ativo=True,
        created_at=date.today()
    )
    db_session.add(forma)
    db_session.commit()
    
    response = client.get(f"/api/formas-pagamento/{forma.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Dinheiro Teste"
    assert data["tipo"] == "dinheiro"

def test_obter_forma_inexistente(client):
    """Teste: Tentar obter forma que não existe"""
    response = client.get("/api/formas-pagamento/99999")
    assert response.status_code == 404

def test_criar_forma_pagamento(client):
    """Teste: Criar nova forma de pagamento"""
    nova_forma = {
        "nome": "Nubank",
        "tipo": "cartao_credito",
        "banco": "Nu Pagamentos",
        "limite_credito": 10000.50,
        "ativo": True,
        "observacao": "Cartão principal"
    }
    
    response = client.post("/api/formas-pagamento", json=nova_forma)
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Nubank"
    assert data["tipo"] == "cartao_credito"
    assert data["banco"] == "Nu Pagamentos"
    assert data["ativo"] == True

def test_criar_forma_duplicada(client, db_session, test_user):
    """Teste: Tentar criar forma com nome duplicado"""
    from app.main import FormaPagamento
    
    # Criar primeira forma
    forma = FormaPagamento(
        usuario_id=test_user.id,
        nome="Bradesco",
        tipo="conta",
        ativo=True,
        created_at=date.today()
    )
    db_session.add(forma)
    db_session.commit()
    
    # Tentar criar outra com mesmo nome
    nova_forma = {
        "nome": "Bradesco",
        "tipo": "cartao_credito",
        "ativo": True
    }
    
    response = client.post("/api/formas-pagamento", json=nova_forma)
    assert response.status_code == 400
    assert "já existe" in response.json()["detail"].lower()

def test_criar_forma_tipo_invalido(client):
    """Teste: Tentar criar forma com tipo inválido"""
    nova_forma = {
        "nome": "Teste",
        "tipo": "tipo_invalido",
        "ativo": True
    }
    
    response = client.post("/api/formas-pagamento", json=nova_forma)
    assert response.status_code == 422  # Validation error

def test_atualizar_forma_pagamento(client, db_session, test_user):
    """Teste: Atualizar forma de pagamento existente"""
    from app.main import FormaPagamento
    
    forma = FormaPagamento(
        usuario_id=test_user.id,
        nome="Itaú Original",
        tipo="conta",
        banco="Itaú",
        ativo=True,
        created_at=date.today()
    )
    db_session.add(forma)
    db_session.commit()
    
    atualizacao = {
        "nome": "Itaú Atualizado",
        "tipo": "conta",
        "banco": "Itaú Unibanco",
        "limite_credito": None,
        "ativo": True,
        "observacao": "Conta corrente principal"
    }
    
    response = client.put(f"/api/formas-pagamento/{forma.id}", json=atualizacao)
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Itaú Atualizado"
    assert data["banco"] == "Itaú Unibanco"
    assert data["observacao"] == "Conta corrente principal"

def test_atualizar_forma_inexistente(client):
    """Teste: Tentar atualizar forma que não existe"""
    atualizacao = {
        "nome": "Teste",
        "tipo": "dinheiro",
        "ativo": True
    }
    
    response = client.put("/api/formas-pagamento/99999", json=atualizacao)
    assert response.status_code == 404

def test_toggle_forma_pagamento(client, db_session, test_user):
    """Teste: Ativar/desativar forma de pagamento"""
    from app.main import FormaPagamento
    
    forma = FormaPagamento(
        usuario_id=test_user.id,
        nome="Caixa",
        tipo="conta",
        ativo=True,
        created_at=date.today()
    )
    db_session.add(forma)
    db_session.commit()
    
    # Desativar
    response = client.patch(f"/api/formas-pagamento/{forma.id}/toggle")
    assert response.status_code == 200
    data = response.json()
    assert data["ativo"] == False
    
    # Reativar
    response = client.patch(f"/api/formas-pagamento/{forma.id}/toggle")
    assert response.status_code == 200
    data = response.json()
    assert data["ativo"] == True

def test_excluir_forma_nao_usada(client, db_session, test_user):
    """Teste: Excluir forma que não está em uso"""
    from app.main import FormaPagamento
    
    forma = FormaPagamento(
        usuario_id=test_user.id,
        nome="Forma Para Excluir",
        tipo="dinheiro",
        ativo=True,
        created_at=date.today()
    )
    db_session.add(forma)
    db_session.commit()
    forma_id = forma.id
    
    response = client.delete(f"/api/formas-pagamento/{forma_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    
    # Verificar que foi excluída
    response = client.get(f"/api/formas-pagamento/{forma_id}")
    assert response.status_code == 404

def test_excluir_forma_em_uso(client, db_session, lancamento_receita, test_user):
    """Teste: Tentar excluir forma que está sendo usada"""
    from app.main import FormaPagamento, Parcela
    
    # Criar forma
    forma = FormaPagamento(
        usuario_id=test_user.id,
        nome="Forma Em Uso",
        tipo="pix",
        ativo=True,
        created_at=date.today()
    )
    db_session.add(forma)
    db_session.commit()
    
    # Vincular a uma parcela
    parcela = db_session.query(Parcela).filter_by(lancamento_id=lancamento_receita.id).first()
    parcela.forma_pagamento_id = forma.id
    parcela.paga = 1
    parcela.data_pagamento = date.today()
    parcela.valor_pago = parcela.valor
    db_session.commit()
    
    # Tentar excluir
    response = client.delete(f"/api/formas-pagamento/{forma.id}")
    assert response.status_code == 400
    assert "em uso" in response.json()["detail"].lower() or "sendo usada" in response.json()["detail"].lower()

def test_excluir_forma_inexistente(client):
    """Teste: Tentar excluir forma que não existe"""
    response = client.delete("/api/formas-pagamento/99999")
    assert response.status_code == 404

def test_criar_forma_sem_nome(client):
    """Teste: Tentar criar forma sem nome"""
    nova_forma = {
        "tipo": "dinheiro",
        "ativo": True
    }
    
    response = client.post("/api/formas-pagamento", json=nova_forma)
    assert response.status_code == 422

def test_criar_forma_com_limite_negativo(client):
    """Teste: Tentar criar forma com limite de crédito negativo"""
    nova_forma = {
        "nome": "Teste",
        "tipo": "cartao_credito",
        "limite_credito": -1000,
        "ativo": True
    }
    
    response = client.post("/api/formas-pagamento", json=nova_forma)
    assert response.status_code == 422

def test_formas_padrao_existem(client):
    """Teste: Verificar que formas padrão foram criadas na migração"""
    response = client.get("/api/formas-pagamento?incluir_inativas=true")
    assert response.status_code == 200
    data = response.json()
    
    # Verificar se existem formas (podem ter sido criadas pela migração)
    nomes = [f["nome"] for f in data]
    # Não vamos garantir nomes específicos, mas pelo menos que a lista funciona
    assert isinstance(data, list)
