"""
Módulo de Autenticação e Segurança
Gerencia usuários, passwords, tokens JWT e sessões
"""
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import Session
import secrets
import os

# Configurações de segurança
# Em produção, SECRET_KEY deve vir do ambiente. Para ambiente local, geramos um valor volátil.
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
_ENV_SECRET = os.getenv("SECRET_KEY")
if ENVIRONMENT == "production" and not _ENV_SECRET:
    # Falhar cedo em produção se não houver SECRET_KEY
    raise RuntimeError("SECRET_KEY não definido em ambiente de produção")
SECRET_KEY = _ENV_SECRET or secrets.token_urlsafe(32)
ALGORITHM = "HS256"
# Tempo de expiração do token/sessão (minutos)
# Requisito: sessão ativa por 30 minutos (admin e usuário)
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class UserBase(BaseModel):
    email: EmailStr
    nome: str = Field(..., min_length=2, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=50)

class UserUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)

class UserOut(UserBase):
    id: int
    ativo: bool
    admin: bool
    created_at: datetime
    ultimo_acesso: Optional[datetime]

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
    require_password_change: bool = False

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# ============================================================================
# FUNÇÕES DE SEGURANÇA
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    # Bcrypt trabalha com bytes
    password_bytes = plain_password.encode('utf-8')
    # hashed_password pode ser string ou bytes
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera hash bcrypt da senha"""
    # Bcrypt trabalha com bytes e retorna bytes
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Retornar como string para armazenar no banco
    return hashed.decode('utf-8')

def validate_password_strength(password: str) -> bool:
    """Valida força mínima da senha: >=8, maiúscula, minúscula, dígito, símbolo"""
    import re
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[^A-Za-z0-9]", password):
        return False
    return True

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria token JWT"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[TokenData]:
    """Decodifica e valida token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        email: str = payload.get("email")
        
        if user_id is None:
            return None
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            return None
        
        return TokenData(user_id=user_id_int, email=email)
    except JWTError:
        return None

# Nota: O modelo User SQLAlchemy está definido em app.main.
# Para evitar importações circulares, importamos localmente dentro das funções.

# ============================================================================
# FUNÇÕES DE CRUD - USER
# ============================================================================

def create_user(db: Session, user_create: UserCreate, is_admin: bool = False):
    """Cria novo usuário no banco"""
    from app.main import User  # import local para evitar ciclo
    # Verificar se email já existe
    existing_user = db.query(User).filter(User.email == user_create.email).first()
    if existing_user:
        # Evitar enumeração de usuários
        raise ValueError("Não foi possível completar o registro")
    
    # Criar usuário
    # Política de senha
    if not validate_password_strength(user_create.password):
        raise ValueError("Senha não atende aos requisitos mínimos")
    hashed_password = get_password_hash(user_create.password)
    
    db_user = User(
        email=user_create.email,
        nome=user_create.nome,
        senha_hash=hashed_password,
        admin=is_admin,
        ativo=True,
        created_at=datetime.utcnow()
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def get_user_by_email(db: Session, email: str):
    """Busca usuário por email"""
    from app.main import User  # import local para evitar ciclo
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    """Busca usuário por ID"""
    from app.main import User  # import local para evitar ciclo
    return db.query(User).filter(User.id == user_id).first()

def authenticate_user(db: Session, email: str, password: str):
    """Autentica usuário (login)"""
    from app.main import User  # import local para evitar ciclo
    user = get_user_by_email(db, email)
    
    if not user:
        return None
    
    if not user.ativo:
        return None
    
    if not verify_password(password, user.senha_hash):
        return None
    
    # Atualizar último acesso
    user.ultimo_acesso = datetime.utcnow()
    db.commit()
    
    return user

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    """Atualiza dados do usuário"""
    from app.main import User  # import local para evitar ciclo
    user = get_user_by_id(db, user_id)
    
    if not user:
        return None
    
    if user_update.nome is not None:
        user.nome = user_update.nome
    
    if user_update.email is not None:
        # Verificar se novo email já existe
        existing = db.query(User).filter(
            User.email == user_update.email,
            User.id != user_id
        ).first()
        
        if existing:
            raise ValueError("Não foi possível completar a atualização")
        
        user.email = user_update.email
    
    if user_update.password is not None:
        if not validate_password_strength(user_update.password):
            raise ValueError("Senha não atende aos requisitos mínimos")
        user.senha_hash = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(user)
    
    return user

def deactivate_user(db: Session, user_id: int) -> bool:
    """Desativa usuário (soft delete)"""
    from app.main import User  # import local para evitar ciclo
    user = get_user_by_id(db, user_id)
    
    if not user:
        return False
    
    user.ativo = False
    db.commit()
    
    return True

def list_users(db: Session, skip: int = 0, limit: int = 100, only_active: bool = True):
    """Lista todos os usuários"""
    from app.main import User  # import local para evitar ciclo
    query = db.query(User)
    
    if only_active:
        query = query.filter(User.ativo == True)
    
    return query.offset(skip).limit(limit).all()

# ============================================================================
# EXTENSÕES PARA TROCA DE SENHA ADMIN
# ============================================================================

def password_in_use_by_other_non_admin(db: Session, password: str, exclude_user_id: int) -> bool:
    """Verifica se a senha proposta está em uso por algum outro usuário não-admin.
    NOTA: bcrypt possui salt, então precisamos verificar provando a senha contra cada hash.
    Retorna True se encontrar outro usuário não-admin usando a mesma senha clara.
    Escopo pequeno espera-se número limitado de usuários, aceitável iterar.
    """
    from app.main import User
    candidates = db.query(User).filter(User.id != exclude_user_id, User.admin == False, User.ativo == True).all()
    for u in candidates:
        try:
            if verify_password(password, u.senha_hash):
                return True
        except Exception:
            continue
    return False

def change_admin_password(db: Session, user_id: int, current_password: str, new_password: str):
    """Altera senha de usuário admin com validações de segurança.
    Regras:
    - Usuário deve existir e ser admin.
    - current_password deve corresponder ao hash atual.
    - new_password deve atender validate_password_strength (mínimo já reforçado externamente se desejado).
    - new_password não pode ser igual à senha atual.
    - new_password não pode estar em uso por outro usuário ativo não-admin.
    """
    from app.main import User
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.admin or not user.ativo:
        raise ValueError("Usuário inválido ou não autorizado")
    if not verify_password(current_password, user.senha_hash):
        raise ValueError("Senha atual incorreta")
    if current_password == new_password:
        raise ValueError("Nova senha não pode ser igual à senha atual")
    # Reforçar requisitos mais fortes que mínimo (>=12)
    if len(new_password) < 12 or not validate_password_strength(new_password):
        raise ValueError("Senha fraca: mínimo 12 caracteres, maiúscula, minúscula, dígito e símbolo")
    if password_in_use_by_other_non_admin(db, new_password, exclude_user_id=user.id):
        raise ValueError("Senha já utilizada por outro usuário. Escolha uma diferente.")
    # Atualizar hash
    user.senha_hash = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return user
