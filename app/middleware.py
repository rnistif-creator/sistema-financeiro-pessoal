"""
Middleware de Autenticação
Dependências para proteger rotas
"""
from fastapi import Depends, HTTPException, status, Cookie, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, Any
from app.auth import decode_access_token, get_user_by_id, TokenData
from datetime import date, timedelta
import os

# Security scheme para Bearer token
security = HTTPBearer(auto_error=False)

# ============================================================================
# DEPENDÊNCIA DE BANCO (lazy import para evitar ciclo)
# ============================================================================

def get_db():
    """Fornece uma sessão de banco via import tardio para evitar importação circular."""
    from app.main import SessionLocal  # import local
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# DEPENDÊNCIAS DE AUTENTICAÇÃO
# ============================================================================

async def get_current_user_from_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    token: Optional[str] = Cookie(None, alias="access_token"),
    db: Session = Depends(get_db)
) -> Optional[Any]:
    """
    Obtém usuário atual do token JWT
    Aceita token via:
    1. Header Authorization: Bearer <token>
    2. Cookie: access_token
    """
    # Tentar obter token do header ou cookie
    token_str = None
    
    if credentials:
        token_str = credentials.credentials
    elif token:
        token_str = token
    
    if not token_str:
        return None
    
    # Decodificar token
    token_data: Optional[TokenData] = decode_access_token(token_str)
    
    if token_data is None or token_data.user_id is None:
        return None
    
    # Buscar usuário no banco
    user = get_user_by_id(db, token_data.user_id)
    
    if user is None or not user.ativo:
        return None
    
    return user

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    token: Optional[str] = Cookie(None, alias="access_token"),
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtém usuário atual (obrigatório)
    Retorna 401 se não autenticado
    """
    user = await get_current_user_from_token(credentials, token, db)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_active_user(
    current_user: Any = Depends(get_current_user)
) -> Any:
    """
    Obtém usuário ativo (obrigatório)
    Retorna 403 se usuário desativado
    """
    if not current_user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário desativado"
        )
    
    return current_user

async def get_current_admin_user(
    current_user: Any = Depends(get_current_active_user)
) -> Any:
    """
    Obtém usuário administrador (obrigatório)
    Retorna 403 se não for admin
    """
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    return current_user

# ============================================================================
# RESTRIÇÃO POR IP PARA ÁREA ADMINISTRATIVA (opcional via env ADMIN_ALLOWED_IPS)
# ============================================================================

async def ensure_admin_ip_allowed(request: Request) -> bool:
    """
    Se ADMIN_ALLOWED_IPS estiver definido (lista separada por vírgula),
    valida se o IP do cliente está permitido para acessar rotas administrativas.
    Aceita também cabeçalho X-Forwarded-For (primeiro IP) quando presente.
    """
    ips_env = os.getenv("ADMIN_ALLOWED_IPS", "").strip()
    if not ips_env:
        return True  # sem restrição configurada

    allowed = {ip.strip() for ip in ips_env.split(',') if ip.strip()}
    client_ip = None
    # Respeita proxy/reverso quando presente
    fwd = request.headers.get("x-forwarded-for") or request.headers.get("X-Forwarded-For")
    if fwd:
        client_ip = fwd.split(',')[0].strip()
    elif request.client:
        client_ip = request.client.host

    if client_ip not in allowed:
        raise HTTPException(status_code=403, detail="Computador não autorizado para área administrativa")
    return True

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    token: Optional[str] = Cookie(None, alias="access_token"),
    db: Session = Depends(get_db)
) -> Optional[Any]:
    """
    Obtém usuário se autenticado, senão retorna None
    Não retorna erro se não autenticado
    Útil para rotas que funcionam com ou sem autenticação
    """
    try:
        return await get_current_user_from_token(credentials, token, db)
    except:
        return None

# ============================================================================
# DECORATORS AUXILIARES (para usar em funções)
# ============================================================================

def require_auth(func):
    """
    Decorator para funções que requerem autenticação
    Uso: @require_auth
    """
    async def wrapper(*args, current_user: Any = Depends(get_current_user), **kwargs):
        return await func(*args, current_user=current_user, **kwargs)
    return wrapper

def require_admin(func):
    """
    Decorator para funções que requerem admin
    Uso: @require_admin
    """
    async def wrapper(*args, current_user: Any = Depends(get_current_admin_user), **kwargs):
        return await func(*args, current_user=current_user, **kwargs)
    return wrapper

# ============================================================================
# COBRANÇA / ASSINATURA
# ============================================================================

async def ensure_subscription(
    current_user: Any = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Garante que o usuário possui assinatura em dia para operações de escrita.
    - Se não houver assinatura, cria uma de avaliação (trial) de 14 dias a partir de hoje.
    - Se vencida, retorna 402 Payment Required com detalhes do status.
    """
    # Import local para evitar ciclo
    from app.main import Assinatura

    # Buscar assinatura do usuário
    sub = db.query(Assinatura).filter(Assinatura.usuario_id == current_user.id).first()

    hoje = date.today()

    if not sub:
        # Criar assinatura em TRIAL de 14 dias
        trial_ate = hoje + timedelta(days=14)
        sub = Assinatura(
            usuario_id=current_user.id,
            status="trial",
            data_inicio=hoje,
            proximo_vencimento=trial_ate,
            valor_mensal=None,
            trial_ate=trial_ate,
            created_at=hoje
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)

    # Verificar vencimento
    if sub.proximo_vencimento and sub.proximo_vencimento < hoje and sub.status not in ("cancelada",):
        # Marcar como inadimplente caso ainda não esteja
        if sub.status != "inadimplente":
            sub.status = "inadimplente"
            db.commit()
        raise HTTPException(
            status_code=402,
            detail={
                "message": "Assinatura vencida. Regularize o pagamento para continuar.",
                "status": sub.status,
                "proximo_vencimento": sub.proximo_vencimento.isoformat() if sub.proximo_vencimento else None,
                "trial_ate": sub.trial_ate.isoformat() if sub.trial_ate else None
            }
        )

    return current_user

def require_subscription(func):
    """
    Decorator para funções (endpoints) que requerem assinatura em dia para execução.
    Uso: @require_subscription
    """
    async def wrapper(*args, current_user: Any = Depends(ensure_subscription), **kwargs):
        return await func(*args, current_user=current_user, **kwargs)
    return wrapper
