"""
Configuração e fixtures para testes
"""
import pytest
import os
import sys
from pathlib import Path
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app, Base, get_db, TipoLancamento, Lancamento, Parcela, User
from app.middleware import get_current_active_user, get_current_admin_user, get_db as middleware_get_db

# Banco de dados de teste em arquivo temporário
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="function")
def db_engine():
    """Cria engine de banco de dados de teste"""
    # Remove arquivo se existir
    if os.path.exists("test.db"):
        os.remove("test.db")
    
    # Cria engine com check_same_thread=False para permitir uso em múltiplas threads
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    
    # Cleanup
    if os.path.exists("test.db"):
        os.remove("test.db")

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Cria sessão de banco de dados de teste"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def test_user(db_session):
    """Usuário autenticado padrão para testes"""
    user = User(
        email="test@example.com",
        nome="Usuário Teste",
        senha_hash="x",
        ativo=True,
        admin=False,
        created_at=date.today(),
        ultimo_acesso=None,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def client(db_session, test_user):
    """Cliente de teste com banco de dados mockado e usuário autenticado"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_active_user():
        return test_user

    def override_admin_user():
        # Promove o mesmo usuário a admin quando necessário
        test_user.admin = True
        db_session.commit()
        return test_user
    
    app.dependency_overrides[get_db] = override_get_db
    # Importante: também sobrescrever o get_db do middleware, usado por ensure_subscription
    app.dependency_overrides[middleware_get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_active_user
    app.dependency_overrides[get_current_admin_user] = override_admin_user

    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def tipo_receita(db_session, test_user):
    """Fixture: Tipo de lançamento receita"""
    tipo = TipoLancamento(
        usuario_id=test_user.id,
        nome="Salário",
        natureza="receita",
        created_at=date.today()
    )
    db_session.add(tipo)
    db_session.commit()
    db_session.refresh(tipo)
    return tipo

@pytest.fixture
def tipo_despesa(db_session, test_user):
    """Fixture: Tipo de lançamento despesa"""
    tipo = TipoLancamento(
        usuario_id=test_user.id,
        nome="Supermercado",
        natureza="despesa",
        created_at=date.today()
    )
    db_session.add(tipo)
    db_session.commit()
    db_session.refresh(tipo)
    return tipo

@pytest.fixture
def lancamento_receita(db_session, tipo_receita, test_user):
    """Fixture: Lançamento de receita"""
    lancamento = Lancamento(
        usuario_id=test_user.id,
        data_lancamento=date.today(),
        tipo="receita",
        tipo_lancamento_id=tipo_receita.id,
        fornecedor="Empresa XYZ",
        valor_total=5000.00,
        data_primeiro_vencimento=date.today() + timedelta(days=5),
        numero_parcelas=1,
        valor_medio_parcelas=5000.00,
        observacao="Salário mensal"
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
    
    return lancamento

@pytest.fixture
def lancamento_despesa(db_session, tipo_despesa, test_user):
    """Fixture: Lançamento de despesa parcelada"""
    lancamento = Lancamento(
        usuario_id=test_user.id,
        data_lancamento=date.today(),
        tipo="despesa",
        tipo_lancamento_id=tipo_despesa.id,
        fornecedor="Supermercado ABC",
        valor_total=600.00,
        data_primeiro_vencimento=date.today() + timedelta(days=10),
        numero_parcelas=3,
        valor_medio_parcelas=200.00,
        observacao="Compras do mês"
    )
    db_session.add(lancamento)
    db_session.commit()
    db_session.refresh(lancamento)
    
    # Criar parcelas
    for i in range(3):
        parcela = Parcela(
            usuario_id=test_user.id,
            lancamento_id=lancamento.id,
            numero_parcela=i + 1,
            data_vencimento=lancamento.data_primeiro_vencimento + timedelta(days=30*i),
            valor=lancamento.valor_medio_parcelas,
            paga=0
        )
        db_session.add(parcela)
    db_session.commit()
    
    return lancamento
