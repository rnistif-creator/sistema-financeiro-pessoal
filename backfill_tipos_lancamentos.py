#!/usr/bin/env python3
"""
Script para criar tipos e subtipos apropriados e atribuir aos lançamentos sem tipo
"""
from app.main import SessionLocal, Lancamento, TipoLancamento, SubtipoLancamento

def criar_tipos_e_subtipos(db, usuario_id):
    """Cria tipos e subtipos comuns se não existirem"""
    from datetime import date
    
    tipos_config = {
        'receita': [
            'Salário',
            'Freelance',
            'Consultoria',
            'Venda de Produtos',
            'Investimentos',
            'Outros Recebimentos'
        ],
        'despesa': [
            'Moradia',
            'Contas',
            'Alimentação',
            'Transporte',
            'Educação',
            'Saúde',
            'Lazer',
            'Empréstimos',
            'Seguros',
            'Tecnologia',
            'Outros Gastos'
        ]
    }
    
    tipos_criados = {}
    
    for natureza, subtipos in tipos_config.items():
        # Buscar ou criar tipo principal
        tipo_nome = f"{natureza.upper()} - Geral"
        tipo_obj = db.query(TipoLancamento).filter(
            TipoLancamento.usuario_id == usuario_id,
            TipoLancamento.nome == tipo_nome
        ).first()
        
        if not tipo_obj:
            tipo_obj = TipoLancamento(
                usuario_id=usuario_id,
                nome=tipo_nome,
                natureza=natureza,
                created_at=date.today()
            )
            db.add(tipo_obj)
            db.flush()
            print(f"✓ Criado tipo: {tipo_obj.nome}")
        
        tipos_criados[natureza.upper()] = tipo_obj
        
        # Criar subtipos
        for subtipo_nome in subtipos:
            subtipo_obj = db.query(SubtipoLancamento).filter(
                SubtipoLancamento.usuario_id == usuario_id,
                SubtipoLancamento.tipo_lancamento_id == tipo_obj.id,
                SubtipoLancamento.nome == subtipo_nome
            ).first()
            
            if not subtipo_obj:
                subtipo_obj = SubtipoLancamento(
                    usuario_id=usuario_id,
                    tipo_lancamento_id=tipo_obj.id,
                    nome=subtipo_nome,
                    ativo=True,
                    created_at=date.today()
                )
                db.add(subtipo_obj)
                print(f"  ✓ Criado subtipo: {subtipo_nome}")
    
    db.commit()
    return tipos_criados

def mapear_lancamento_para_subtipo(lancamento, db, tipos):
    """Mapeia um lançamento para o subtipo mais apropriado"""
    
    fornecedor_lower = lancamento.fornecedor.lower()
    # Converter tipo do lançamento para maiúscula
    tipo_key = lancamento.tipo.upper()
    tipo_lancamento = tipos[tipo_key]
    
    # Mapeamento baseado em palavras-chave
    mapeamentos = {
        'RECEITA': {
            'salario': 'Salário',
            'salário': 'Salário',
            'cliente': 'Consultoria',
            'projeto': 'Consultoria',
            'consultoria': 'Consultoria',
            'freelance': 'Freelance',
            'assinatura': 'Outros Recebimentos',
            'assinaturas': 'Outros Recebimentos',
            'venda': 'Venda de Produtos',
            'equipamento': 'Venda de Produtos',
            'equipamentos': 'Venda de Produtos',
            'retainer': 'Consultoria',
        },
        'DESPESA': {
            'aluguel': 'Moradia',
            'luz': 'Contas',
            'internet': 'Contas',
            'conta': 'Contas',
            'cartao': 'Outros Gastos',
            'cartão': 'Outros Gastos',
            'credito': 'Outros Gastos',
            'crédito': 'Outros Gastos',
            'supermercado': 'Alimentação',
            'loja': 'Outros Gastos',
            'curso': 'Educação',
            'emprestimo': 'Empréstimos',
            'empréstimo': 'Empréstimos',
            'financiamento': 'Empréstimos',
            'seguro': 'Seguros',
            'software': 'Tecnologia',
            'servidor': 'Tecnologia',
            'licenca': 'Tecnologia',
            'licença': 'Tecnologia',
            'licenças': 'Tecnologia',
            'veiculo': 'Transporte',
            'veículo': 'Transporte',
            'reserva': 'Tecnologia',
        }
    }
    
    # Tentar encontrar subtipo baseado em palavra-chave
    subtipo_nome = None
    tipo_upper = lancamento.tipo.upper()
    for palavra, subtipo in mapeamentos.get(tipo_upper, {}).items():
        if palavra in fornecedor_lower:
            subtipo_nome = subtipo
            break
    
    # Se não encontrou, usar "Outros"
    if not subtipo_nome:
        subtipo_nome = 'Outros Recebimentos' if lancamento.tipo.upper() == 'RECEITA' else 'Outros Gastos'
    
    # Buscar subtipo
    subtipo = db.query(SubtipoLancamento).filter(
        SubtipoLancamento.tipo_lancamento_id == tipo_lancamento.id,
        SubtipoLancamento.nome == subtipo_nome,
        SubtipoLancamento.usuario_id == lancamento.usuario_id
    ).first()
    
    return subtipo

def main():
    db = SessionLocal()
    try:
        print("🔧 Iniciando backfill de tipos de lançamento...\n")
        
        # Buscar lançamentos sem tipo
        lancamentos_sem_tipo = db.query(Lancamento).filter(
            Lancamento.tipo_lancamento_id == None
        ).all()
        
        print(f"📊 Encontrados {len(lancamentos_sem_tipo)} lançamentos sem tipo\n")
        
        if not lancamentos_sem_tipo:
            print("✅ Nenhum lançamento precisa de backfill!")
            return
        
        # Agrupar por usuário
        usuarios_ids = set(l.usuario_id for l in lancamentos_sem_tipo)
        
        for usuario_id in usuarios_ids:
            print(f"\n👤 Processando usuário ID {usuario_id}...")
            
            # Criar tipos e subtipos para este usuário
            print("📝 Criando tipos e subtipos...")
            tipos = criar_tipos_e_subtipos(db, usuario_id)
            print()
            
            # Buscar lançamentos deste usuário
            lancs_usuario = [l for l in lancamentos_sem_tipo if l.usuario_id == usuario_id]
            
            # Atribuir tipos
            print(f"🔄 Atribuindo tipos a {len(lancs_usuario)} lançamentos...")
            for lanc in lancs_usuario:
                subtipo = mapear_lancamento_para_subtipo(lanc, db, tipos)
                
                if subtipo:
                    lanc.tipo_lancamento_id = subtipo.tipo_lancamento_id
                    lanc.subtipo_lancamento_id = subtipo.id
                    print(f"  ✓ ID {lanc.id}: {lanc.fornecedor} → {subtipo.nome}")
                else:
                    print(f"  ✗ ID {lanc.id}: {lanc.fornecedor} - Não foi possível mapear")
            
            db.commit()
        
        print(f"\n✅ Backfill concluído! {len(lancamentos_sem_tipo)} lançamentos atualizados.")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
