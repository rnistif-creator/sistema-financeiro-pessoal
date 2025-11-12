import pytest
from datetime import date


def test_filtro_valor_min_max_em_parcelas_pagas(client, db_session, lancamento_receita, lancamento_despesa):
    """Valida filtros valor_min e valor_max em /api/parcelas/pagas"""
    from app.main import Parcela

    # Marcar duas parcelas como pagas com valores diferentes
    p1 = db_session.query(Parcela).filter_by(lancamento_id=lancamento_receita.id).first()
    p1.paga = 1
    p1.data_pagamento = date.today()
    p1.valor_pago = 200.00

    p2 = db_session.query(Parcela).filter_by(lancamento_id=lancamento_despesa.id).first()
    p2.paga = 1
    p2.data_pagamento = date.today()
    p2.valor_pago = 1000.00
    db_session.commit()

    # valor_min=500 deve trazer apenas a de 1000
    r = client.get(f"/api/parcelas/pagas?valor_min=500")
    assert r.status_code == 200
    data = r.json()
    valores = sorted([(it.get("valor_pago") or it.get("valor")) for it in data.get("parcelas", [])])
    assert all(v is not None for v in valores)
    assert len(valores) >= 1
    assert valores[0] >= 500

    # valor_max=300 deve trazer a de 200
    r2 = client.get(f"/api/parcelas/pagas?valor_max=300")
    assert r2.status_code == 200
    data2 = r2.json()
    valores2 = sorted([(it.get("valor_pago") or it.get("valor")) for it in data2.get("parcelas", [])])
    assert len(valores2) >= 1
    assert valores2[-1] <= 300
