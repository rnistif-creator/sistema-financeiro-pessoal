from app.main import SessionLocal, TipoLancamento, SubtipoLancamento, Parcela, Base, engine, User
from app.auth import get_password_hash
from datetime import date

def criar_tabelas():
    """Cria todas as tabelas no banco de dados"""
    print("Criando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")

def criar_tipos_iniciais():
    db = SessionLocal()
    try:
        # Tipos de Receita
        receitas = [
            {"nome": "Salário", "natureza": "receita"},
            {"nome": "Freelance", "natureza": "receita"},
            {"nome": "Investimentos", "natureza": "receita"},
        ]
        
        # Tipos de Despesa
        despesas = [
            {"nome": "Aluguel", "natureza": "despesa"},
            {"nome": "Supermercado", "natureza": "despesa"},
            {"nome": "Transporte", "natureza": "despesa"},
        ]
        
        tipos_criados = 0
        tipos_existentes = 0
        
        # Inserir todos os tipos (apenas se não existirem)
        for tipo in receitas + despesas:
            # Verificar se já existe
            tipo_existente = db.query(TipoLancamento).filter(
                TipoLancamento.nome == tipo["nome"],
                TipoLancamento.natureza == tipo["natureza"]
            ).first()
            
            if not tipo_existente:
                db_tipo = TipoLancamento(
                    nome=tipo["nome"],
                    natureza=tipo["natureza"],
                    created_at=date.today()
                )
                db.add(db_tipo)
                tipos_criados += 1
            else:
                tipos_existentes += 1
        
        db.commit()
        print(f"Tipos de lançamento: {tipos_criados} criados, {tipos_existentes} já existiam")
    
    except Exception as e:
        print(f"Erro ao criar tipos de lançamento: {e}")
        db.rollback()
    finally:
        db.close()

def criar_usuario_admin():
    """Cria um usuário administrador padrão se não existir"""
    db = SessionLocal()
    try:
        # Verificar se já existe algum usuário admin
        admin_existente = db.query(User).filter(User.admin == True).first()
        
        if not admin_existente:
            # Criar usuário admin padrão
            admin = User(
                email="admin@sistema.com",
                nome="Administrador",
                senha_hash=get_password_hash("admin123"),
                ativo=True,
                admin=True
            )
            db.add(admin)
            db.commit()
            print("\n" + "="*60)
            print("✓ Usuário admin criado com sucesso!")
            print("  Email: admin@sistema.com")
            print("  Senha: admin123")
            print("  ⚠️  ALTERE A SENHA IMEDIATAMENTE APÓS O PRIMEIRO LOGIN!")
            print("="*60 + "\n")
        else:
            print(f"Usuário admin já existe: {admin_existente.email}")
    
    except Exception as e:
        print(f"Erro ao criar usuário admin: {e}")
        db.rollback()
    finally:
        db.close()

def criar_subtipos_iniciais():
    """Cria subtipos padrão para os tipos existentes"""
    db = SessionLocal()
    try:
        # Mapeamento de subtipos por tipo
        subtipos_por_tipo = {
            "Alimentação": ["Restaurante", "Supermercado", "Delivery", "Lanchonete", "Padaria"],
            "Transporte": ["Combustível", "Uber/Taxi", "Ônibus", "Manutenção", "Estacionamento"],
            "Moradia": ["Aluguel", "Condomínio", "Energia", "Água", "Gás", "Internet", "IPTU"],
            "Saúde": ["Farmácia", "Consultas", "Exames", "Plano de Saúde", "Academia"],
            "Lazer": ["Cinema", "Shows", "Viagens", "Streaming", "Jogos"],
            "Educação": ["Cursos", "Livros", "Material Escolar", "Mensalidade"],
            "Vestuário": ["Roupas", "Calçados", "Acessórios"],
            "Supermercado": ["Alimentos", "Limpeza", "Higiene"],
            "Transporte": ["Combustível", "Manutenção", "Seguro", "IPVA"],
            "Aluguel": ["Residencial", "Comercial"],
            "Salário": ["CLT", "Freelance", "Bônus"],
            "Freelance": ["Projetos", "Consultorias", "Serviços"],
            "Investimentos": ["Dividendos", "Rendimentos", "Lucros"]
        }
        
        subtipos_criados = 0
        subtipos_existentes = 0
        
        # Buscar todos os tipos
        tipos = db.query(TipoLancamento).all()
        
        for tipo in tipos:
            # Verificar se há subtipos predefinidos para este tipo
            if tipo.nome in subtipos_por_tipo:
                for subtipo_nome in subtipos_por_tipo[tipo.nome]:
                    # Verificar se já existe
                    subtipo_existente = db.query(SubtipoLancamento).filter(
                        SubtipoLancamento.tipo_lancamento_id == tipo.id,
                        SubtipoLancamento.nome == subtipo_nome
                    ).first()
                    
                    if not subtipo_existente:
                        db_subtipo = SubtipoLancamento(
                            tipo_lancamento_id=tipo.id,
                            nome=subtipo_nome,
                            ativo=True,
                            created_at=date.today()
                        )
                        db.add(db_subtipo)
                        subtipos_criados += 1
                    else:
                        subtipos_existentes += 1
        
        db.commit()
        print(f"Subtipos de lançamento: {subtipos_criados} criados, {subtipos_existentes} já existiam")
    
    except Exception as e:
        print(f"Erro ao criar subtipos de lançamento: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    criar_tabelas()
    criar_tipos_iniciais()
    criar_subtipos_iniciais()
    criar_usuario_admin()