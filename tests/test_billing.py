import pytest
from datetime import date, timedelta

from app.main import app, User, Assinatura
from app.middleware import get_current_active_user


def make_user(db_session, email="teste@example.com", nome="Usuário Teste"):
    # Cria usuário simples (sem usar fluxo de auth) para testes
    u = User(
        email=email,
        nome=nome,
        senha_hash="x",  # não usado nos testes
        ativo=True,
        admin=False,
        created_at=date.today(),
        ultimo_acesso=None,
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


def override_user(user):
    def _ovr():
        return user
    return _ovr


@pytest.mark.parametrize("valor_pagamento", [29.90])
def test_trial_is_created_on_first_access(client, db_session, valor_pagamento):
    user = make_user(db_session)
    # Override de autenticação para retornar nosso usuário
    app.dependency_overrides[get_current_active_user] = override_user(user)
    
    # Ao consultar a assinatura pela 1ª vez, a ensure_subscription cria TRIAL automática se necessário
    r = client.get("/api/billing/assinatura")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in ("trial", "ativa")
    # Em geral será trial e terá trial_ate definido
    if data["status"] == "trial":
        assert data.get("trial_ate") is not None

    # Limpar override para não vazar para outros testes
    app.dependency_overrides.pop(get_current_active_user, None)


def test_overdue_blocks_write_then_payment_allows_write(client, db_session):
    user = make_user(db_session, email="overdue@example.com")
    app.dependency_overrides[get_current_active_user] = override_user(user)

    # Criar uma assinatura vencida
    vencida = Assinatura(
        usuario_id=user.id,
        status="ativa",
        data_inicio=date.today() - timedelta(days=40),
        proximo_vencimento=date.today() - timedelta(days=5),
        valor_mensal="29.90",
        trial_ate=None,
        created_at=date.today() - timedelta(days=40),
    )
    db_session.add(vencida)
    db_session.commit()

    # 1) Tentar escrever (ex.: criar forma de pagamento) deve retornar 402
    payload = {
        "nome": "Cartão Teste",
        "tipo": "cartao_credito",
        "banco": "Banco X",
        "limite_credito": 1000.00,
        "ativo": True
    }
    r1 = client.post("/api/formas-pagamento", json=payload)
    assert r1.status_code == 402

    # 2) Registrar pagamento
    pay = {"valor": 29.90, "metodo": "manual"}
    r2 = client.post("/api/billing/pagamentos", json=pay)
    assert r2.status_code == 200

    # 3) Tentar novamente a criação: agora deve permitir (201)
    r3 = client.post("/api/formas-pagamento", json=payload)
    assert r3.status_code == 201
    body = r3.json()
    assert body["nome"] == "Cartão Teste"

    app.dependency_overrides.pop(get_current_active_user, None)
