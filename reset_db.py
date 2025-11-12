"""
Script de limpeza do banco de dados (reset) para começar do zero.

O que este script faz (por padrão):
- Cria um backup do banco atual em backups/ (por segurança)
- Apaga os registros de: Parcelas -> Lançamentos -> Subtipos -> Tipos (nesta ordem)

Uso (PowerShell):
  # Executar com confirmação interativa
  python reset_db.py

  # Executar sem perguntar (atenção!)
  python reset_db.py --yes

  # Limpar apenas partes específicas (ex.: somente parcelas e tipos)
  python reset_db.py --only parcelas tipos

Observação:
- O caminho do banco é definido pela variável de ambiente DB_PATH (padrão: lancamentos.db)
- Este script NÃO apaga usuários, metas e recorrentes. Se desejar, podemos estender.
"""
from __future__ import annotations

import os
import sys
from typing import Iterable, List
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    # Reutiliza os modelos e a sessão do app
    from app.main import (
        SessionLocal,
        Parcela,
        Lancamento,
        SubtipoLancamento,
        TipoLancamento,
        LancamentoRecorrente,
        Meta,
        criar_backup,
        DB_PATH,
    )
except Exception as e:
    print("Erro ao importar app.main:", e)
    print("Certifique-se de executar a partir da raiz do projeto.")
    sys.exit(1)


def parse_args(argv: List[str]):
    """Parse argumentos simples: --yes, --only <lista>, --db <caminho>, --drop-recreate."""
    yes = False
    only: List[str] | None = None
    db_override: str | None = None
    drop_recreate = False

    if "--yes" in argv:
        yes = True
        argv = [a for a in argv if a != "--yes"]

    if "--only" in argv:
        idx = argv.index("--only")
        only = []
        for val in argv[idx + 1 :]:
            if val.startswith("-"):
                break
            only.append(val.lower())

    if "--db" in argv:
        idx = argv.index("--db")
        if idx + 1 < len(argv):
            db_override = argv[idx + 1]

    if "--drop-recreate" in argv:
        drop_recreate = True

    return yes, only, db_override, drop_recreate


def should_clear(target: str, only: List[str] | None) -> bool:
    if not only:
        return True
    return target.lower() in only


def main():
    yes, only, db_override, drop_recreate = parse_args(sys.argv[1:])

    # Determinar o caminho do DB efetivo
    env_db_path = os.getenv("DB_PATH")
    effective_db_path = db_override or env_db_path or DB_PATH
    abs_db_path = str(Path(effective_db_path).resolve())

    print("\n=== Limpeza do Banco de Dados ===")
    print(f"DB_PATH (efetivo): {abs_db_path}")
    if env_db_path and env_db_path != DB_PATH:
        print(f"(Info) DB_PATH do ambiente difere do app.main: env='{env_db_path}', app.main='{DB_PATH}'")
    if only:
        print("Alvos limitados a:", ", ".join(only))
    else:
        print("Alvos: parcelas, lancamentos, recorrentes, metas, subtipos, tipos")

    if not yes:
        resp = input("\nIsso irá APAGAR DEFINITIVAMENTE os dados selecionados. Deseja continuar? (digite 'SIM' para confirmar) ").strip()
        if resp.lower() not in {"sim", "s", "yes", "y", "confirmar", "confirm", "ok"}:
            print("Operação cancelada.")
            return

    # Backup antes de alterar
    print("\nCriando backup do banco...")
    try:
        # criar_backup usa DB_PATH do app; se o destino for diferente, faremos um backup manual simples
        if abs_db_path != str(Path(DB_PATH).resolve()):
            # Backup manual do arquivo alvo
            src = Path(abs_db_path)
            if src.exists():
                from datetime import datetime
                backups_dir = Path(__file__).resolve().parent / "backups"
                backups_dir.mkdir(exist_ok=True)
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                dst = backups_dir / f"backup_manual_{ts}.db"
                import shutil
                shutil.copy2(src, dst)
                print("Backup manual criado:", dst.name, f"({round(dst.stat().st_size/(1024*1024),2)} MB)")
                result = {"success": True, "filename": dst.name, "path": str(dst)}
            else:
                result = {"success": False, "error": f"Arquivo não encontrado: {abs_db_path}"}
        else:
            result = criar_backup()
        if result.get("success"):
            print("Backup criado:", result.get("filename"), f"({result.get('size_mb')} MB)")
        else:
            print("Aviso: não foi possível criar backup:", result.get("error"))
    except Exception as e:
        print("Aviso: falha ao criar backup:", e)

    # Abrir sessão para o banco efetivo
    if abs_db_path == str(Path(DB_PATH).resolve()):
        db = SessionLocal()
    else:
        engine = create_engine(f"sqlite:///{abs_db_path}", connect_args={"check_same_thread": False})
        LocalSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
        db = LocalSession()
    try:
        # Contagens atuais
        counts_before = {
            "parcelas": db.query(Parcela).count(),
            "lancamentos": db.query(Lancamento).count(),
            "recorrentes": db.query(LancamentoRecorrente).count(),
            "metas": db.query(Meta).count(),
            "subtipos": db.query(SubtipoLancamento).count(),
            "tipos": db.query(TipoLancamento).count(),
        }
        print("\nRegistros antes:")
        for k, v in counts_before.items():
            print(f"- {k}: {v}")

        # Drop & recreate (opcional)
        if drop_recreate:
            from sqlalchemy import text
            print("\nExecutando drop & recreate das tabelas principais...")
            # Remover registros via delete para evitar restos e então recriar estruturas desejadas via app.main
            db.query(Parcela).delete(synchronize_session=False)
            db.query(Lancamento).delete(synchronize_session=False)
            db.query(LancamentoRecorrente).delete(synchronize_session=False)
            db.query(Meta).delete(synchronize_session=False)
            db.query(SubtipoLancamento).delete(synchronize_session=False)
            db.query(TipoLancamento).delete(synchronize_session=False)
            db.commit()
            print("✓ Registros removidos. (Estruturas mantidas)")

        # Ordem segura de deleção
        if should_clear("parcelas", only):
            db.query(Parcela).delete(synchronize_session=False)
            print("✓ Parcelas apagadas")

        if should_clear("lancamentos", only):
            db.query(Lancamento).delete(synchronize_session=False)
            print("✓ Lançamentos apagados")

        # Tabelas auxiliares independentes
        if should_clear("recorrentes", only):
            db.query(LancamentoRecorrente).delete(synchronize_session=False)
            print("✓ Recorrentes apagados")

        if should_clear("metas", only):
            db.query(Meta).delete(synchronize_session=False)
            print("✓ Metas apagadas")

        if should_clear("subtipos", only):
            db.query(SubtipoLancamento).delete(synchronize_session=False)
            print("✓ Subtipos apagados")

        if should_clear("tipos", only):
            db.query(TipoLancamento).delete(synchronize_session=False)
            print("✓ Tipos apagados")

        db.commit()

        # Contagens após
        counts_after = {
            "parcelas": db.query(Parcela).count(),
            "lancamentos": db.query(Lancamento).count(),
            "recorrentes": db.query(LancamentoRecorrente).count(),
            "metas": db.query(Meta).count(),
            "subtipos": db.query(SubtipoLancamento).count(),
            "tipos": db.query(TipoLancamento).count(),
        }
        print("\nRegistros após:")
        for k, v in counts_after.items():
            print(f"- {k}: {v}")

        print("\nConcluído.")
    except Exception as e:
        db.rollback()
        print("Erro durante a limpeza:", e)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
