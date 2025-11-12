"""
Popula o banco com dados de demonstração:
- 15 lançamentos variados (receitas e despesas)
- Parcelas com diferentes prazos (1, 3, 6, 12, 24, 48)
- Algumas parcelas pagas, outras vencidas e em aberto
- Datas de vencimento incluindo anos futuros (2027)

Uso:
  .venv/Scripts/python.exe seed_demo_data.py [email_opcional]

Se um email for passado, os dados serão criados para esse usuário.
Caso contrário, será usado o primeiro usuário encontrado; se não houver, cria um usuário demo.
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
import sys
import random

from app.main import (
    SessionLocal, User, Assinatura, FormaPagamento,
    Lancamento, Parcela
)
from app.auth import get_password_hash


def get_or_create_user(db, email: str | None):
    if email:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise SystemExit(f"Usuário com email {email} não encontrado. Informe um email existente.")
        return user
    # sem email: pegar primeiro usuário
    user = db.query(User).order_by(User.id.asc()).first()
    if user:
        return user
    # criar usuário demo
    demo_email = "demo@example.com"
    user = User(
        email=demo_email,
        nome="Usuário Demo",
        senha_hash=get_password_hash("Demo@1234!"),
        ativo=True,
        admin=False,
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    # criar assinatura trial
    hoje = date.today()
    ass = Assinatura(
        usuario_id=user.id,
        status="trial",
        data_inicio=hoje,
        proximo_vencimento=hoje + timedelta(days=30),
        valor_mensal=Decimal("0.00"),
        trial_ate=hoje + timedelta(days=14),
        created_at=hoje
    )
    db.add(ass)
    db.commit()
    print(f"✓ Usuário demo criado: {demo_email} (senha: Demo@1234!)")
    return user


def ensure_formas_pagamento(db, usuario_id: int) -> list[FormaPagamento]:
    existentes = db.query(FormaPagamento).filter(FormaPagamento.usuario_id == usuario_id, FormaPagamento.ativo == True).all()
    if existentes:
        return existentes
    hoje = date.today()
    formas = [
        FormaPagamento(usuario_id=usuario_id, nome="Conta Corrente Itaú", tipo="conta", banco="Itaú", ativo=True, created_at=hoje),
        FormaPagamento(usuario_id=usuario_id, nome="Cartão Nubank", tipo="cartao_credito", banco="Nubank", limite_credito=Decimal("5000.00"), ativo=True, created_at=hoje),
        FormaPagamento(usuario_id=usuario_id, nome="PIX Caixa", tipo="pix", banco="Caixa", ativo=True, created_at=hoje),
        FormaPagamento(usuario_id=usuario_id, nome="Dinheiro", tipo="dinheiro", banco=None, ativo=True, created_at=hoje),
    ]
    for f in formas:
        db.add(f)
    db.commit()
    print("✓ Formas de pagamento criadas (4)")
    return db.query(FormaPagamento).filter(FormaPagamento.usuario_id == usuario_id).all()


def month_add(d: date, months: int) -> date:
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    # manter dia seguro
    day = min(d.day, [31,29 if y%4==0 and (y%100!=0 or y%400==0) else 28,31,30,31,30,31,31,30,31,30,31][m-1])
    return date(y, m, day)


def create_lancamento(db, usuario_id: int, tipo: str, fornecedor: str, valor_total: Decimal,
                      data_lancamento: date, primeiro_venc: date, n_parcelas: int, formas: list[FormaPagamento],
                      pagar_ratio: float = 0.5, pagar_primeiras: bool = True):
    valor_parcela = (valor_total / n_parcelas).quantize(Decimal("0.01"))
    l = Lancamento(
        usuario_id=usuario_id,
        data_lancamento=data_lancamento,
        tipo=tipo,
        fornecedor=fornecedor,
        valor_total=valor_total,
        data_primeiro_vencimento=primeiro_venc,
        numero_parcelas=n_parcelas,
        valor_medio_parcelas=valor_parcela,
        observacao=None
    )
    db.add(l)
    db.commit()
    db.refresh(l)

    total_pagar = int(n_parcelas * pagar_ratio)
    forma_ids = [f.id for f in formas]
    hoje = date.today()
    for i in range(n_parcelas):
        venc = month_add(primeiro_venc, i)
        parcela = Parcela(
            usuario_id=usuario_id,
            lancamento_id=l.id,
            numero_parcela=i+1,
            data_vencimento=venc,
            valor=valor_parcela,
            paga=0,
            data_pagamento=None,
            valor_pago=None,
            forma_pagamento_id=None,
            observacao_pagamento=None
        )
        db.add(parcela)
        db.flush()
        # definir pagos
        marcar = False
        if total_pagar > 0:
            if pagar_primeiras and i < total_pagar:
                marcar = True
            elif not pagar_primeiras and i % 2 == 0 and (i // 2) < total_pagar:
                marcar = True
        if marcar:
            parcela.paga = 1
            # data_pagamento perto do vencimento, respeitando passado/futuro
            dp = venc if venc <= hoje else hoje
            parcela.data_pagamento = dp
            parcela.valor_pago = valor_parcela
            parcela.forma_pagamento_id = random.choice(forma_ids) if forma_ids else None
    db.commit()
    return l


def main():
    email = sys.argv[1] if len(sys.argv) > 1 else None
    db = SessionLocal()
    try:
        user = get_or_create_user(db, email)
        print(f"Seeding dados para usuário: {user.email} (id={user.id})")
        formas = ensure_formas_pagamento(db, user.id)

        hoje = date.today()
        base_passado = hoje - timedelta(days=200)
        base_futuro = hoje + timedelta(days=60)

        specs = [
            ("despesa", "Aluguel Escritório", Decimal("24000.00"), 12, base_passado.replace(day=5), 0.9, True),
            ("despesa", "Conta de Luz", Decimal("600.00"), 6, base_passado.replace(day=10), 0.6, True),
            ("despesa", "Internet", Decimal("1200.00"), 12, base_passado.replace(day=12), 0.5, True),
            ("receita", "Cliente A - Projeto X", Decimal("15000.00"), 3, base_passado.replace(day=20), 0.66, True),
            ("receita", "Cliente B - Consultoria", Decimal("8000.00"), 4, base_passado.replace(day=25), 0.5, False),
            ("despesa", "Cartão Crédito - Equipamentos", Decimal("4800.00"), 8, base_passado.replace(day=15), 0.5, True),
            ("despesa", "Seguro", Decimal("1200.00"), 12, base_passado.replace(day=1), 0.25, True),
            ("receita", "Assinaturas Mensais", Decimal("3600.00"), 12, base_passado.replace(day=2), 0.75, True),
            ("despesa", "Curso Online", Decimal("960.00"), 12, base_futuro.replace(day=7), 0.0, True),
            ("despesa", "Empréstimo", Decimal("24000.00"), 24, base_passado.replace(day=6), 0.4, True),
            ("receita", "Venda Equipamentos", Decimal("5000.00"), 2, base_passado.replace(day=18), 1.0, True),
            ("despesa", "Software Licenças", Decimal("2880.00"), 12, base_passado.replace(day=11), 0.5, True),
            ("receita", "Cliente C - Retainer", Decimal("24000.00"), 12, base_passado.replace(day=9), 0.5, True),
            # longo até 2027+ (48 parcelas)
            ("despesa", "Financiamento Veículo", Decimal("96000.00"), 48, date(2024, 6, 15), 0.35, True),
            # futuro 2027
            ("despesa", "Reserva Servidor 2027", Decimal("12000.00"), 12, date(2027, 1, 10), 0.0, True),
        ]

        created = 0
        for tipo, fornecedor, valor, nparc, prv, ratio, first in specs:
            dl = prv - timedelta(days=10)
            create_lancamento(db, user.id, tipo, fornecedor, valor, dl, prv, nparc, formas, ratio, first)
            created += 1

        print(f"✓ {created} lançamentos criados com parcelas distribuídas (incluindo vencimentos até 2027)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
