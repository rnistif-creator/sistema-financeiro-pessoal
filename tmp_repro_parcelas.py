from fastapi.testclient import TestClient
from app.main import app, SessionLocal, TipoLancamento
from datetime import date, timedelta

client = TestClient(app)

# Ensure at least one Tipo exists
s = SessionLocal()
try:
    tipo = s.query(TipoLancamento).filter_by(natureza="despesa").first()
    if not tipo:
        tipo = TipoLancamento(nome="Compras Teste", natureza="despesa", created_at=date.today())
        s.add(tipo)
        s.commit()
        s.refresh(tipo)
    tipo_id = tipo.id
finally:
    s.close()

payload = {
    "data_lancamento": date.today().isoformat(),
    "tipo": "despesa",
    "tipo_lancamento_id": tipo_id,
    "fornecedor": "Teste Loja",
    "valor_total": 1000.00,
    "data_primeiro_vencimento": (date.today() + timedelta(days=1)).isoformat(),
    "numero_parcelas": 3,
    "valor_medio_parcelas": 333.33,
    "observacao": "Compra teste"
}

resp = client.post("/api/lancamentos", json=payload)
print("status:", resp.status_code)
print("body:", resp.text)
