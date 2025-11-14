"""
Módulo de notificações de segurança
Gerencia envio de alertas via SMS, WhatsApp e Email para tentativas de login
"""
import os
import smtplib
import ssl
from datetime import datetime, timedelta
from email.message import EmailMessage
from sqlalchemy.orm import Session

def send_login_alert_sms(phone: str, email: str, ip: str, success: bool) -> bool:
    """Envia alerta de tentativa de login via SMS usando Twilio"""
    try:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_phone = os.getenv("TWILIO_PHONE_NUMBER")
        
        if not all([account_sid, auth_token, from_phone]):
            print("⚠️  Twilio não configurado (SMS)")
            return False
        
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        
        status = "SUCESSO" if success else "FALHA"
        message_body = f"[DOMO360] Tentativa de login {status}\nEmail: {email}\nIP: {ip}\nHorário: {datetime.utcnow().strftime('%d/%m %H:%M UTC')}"
        
        message = client.messages.create(
            body=message_body,
            from_=from_phone,
            to=phone
        )
        print(f"✓ SMS enviado: {message.sid}")
        return True
    except Exception as e:
        print(f"✗ Erro ao enviar SMS: {e}")
        return False

def send_login_alert_whatsapp(phone: str, email: str, ip: str, success: bool) -> bool:
    """Envia alerta de tentativa de login via WhatsApp usando Twilio"""
    try:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_whatsapp = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")  # Twilio Sandbox default
        
        if not all([account_sid, auth_token]):
            print("⚠️  Twilio não configurado (WhatsApp)")
            return False
        
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        
        # Garantir formato whatsapp:+XXXXXXXXXX
        to_whatsapp = phone if phone.startswith("whatsapp:") else f"whatsapp:{phone}"
        
        status = "✅ SUCESSO" if success else "❌ FALHA"
        message_body = f"*[DOMO360 Alerta de Segurança]*\n\n{status} Tentativa de login Admin\n\n📧 Email: {email}\n🌐 IP: {ip}\n🕐 Horário: {datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC')}"
        
        message = client.messages.create(
            body=message_body,
            from_=from_whatsapp,
            to=to_whatsapp
        )
        print(f"✓ WhatsApp enviado: {message.sid}")
        return True
    except Exception as e:
        print(f"✗ Erro ao enviar WhatsApp: {e}")
        return False

def send_login_alert_email(to_email: str, login_email: str, ip: str, user_agent: str, success: bool) -> bool:
    """Envia alerta de tentativa de login via e-mail"""
    try:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        from_email = os.getenv("SMTP_FROM", smtp_user)
        
        if not smtp_user or not smtp_password:
            print("⚠️  SMTP não configurado")
            return False
        
        status_text = "BEM-SUCEDIDA" if success else "FALHOU"
        status_emoji = "✅" if success else "❌"
        
        msg = EmailMessage()
        msg["Subject"] = f"[DOMO360] {status_emoji} Tentativa de Login Admin - {status_text}"
        msg["From"] = from_email
        msg["To"] = to_email
        
        body = f"""Tentativa de login administrativo detectada:

Status: {status_text}
Email: {login_email}
Endereço IP: {ip}
Navegador: {user_agent or 'Desconhecido'}
Data/Hora: {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S UTC')}

{"Se você não reconhece esta atividade, altere sua senha imediatamente." if success else "Tentativa falhou. Se você não tentou fazer login, sua conta está segura."}

---
Sistema de Segurança DOMO360
"""
        msg.set_content(body)
        
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        print(f"✓ Email de alerta enviado para {to_email}")
        return True
    except Exception as e:
        print(f"✗ Erro ao enviar email de alerta: {e}")
        return False

def check_and_notify_login_attempt(db: Session, email: str, ip: str, user_agent: str, success: bool, is_admin: bool = False) -> dict:
    """Registra tentativa de login e envia notificações. Retorna status de bloqueio."""
    from app.main import LoginAttempt
    from app.auth import get_user_by_email
    
    user = get_user_by_email(db, email)
    user_id = user.id if user else None
    
    # Registrar tentativa
    attempt = LoginAttempt(
        email=email,
        user_id=user_id,
        ip_address=ip,
        user_agent=user_agent,
        success=success,
        is_admin_attempt=is_admin,
        created_at=datetime.utcnow()
    )
    db.add(attempt)
    db.commit()
    
    # Contar falhas recentes (últimos 30 minutos)
    cutoff = datetime.utcnow() - timedelta(minutes=30)
    recent_failures = db.query(LoginAttempt).filter(
        LoginAttempt.email == email,
        LoginAttempt.success == False,
        LoginAttempt.is_admin_attempt == is_admin,
        LoginAttempt.created_at >= cutoff
    ).count()
    
    # Bloquear após 4 tentativas falhas
    blocked = False
    blocked_until = None
    if recent_failures >= 4 and not success:
        blocked = True
        blocked_until = datetime.utcnow() + timedelta(minutes=30)
        attempt.blocked_until = blocked_until
        db.commit()
    
    # Enviar notificações apenas para tentativas admin
    if is_admin and user and user.admin:
        # Obter telefone/whatsapp das env vars ou de configuração do usuário
        admin_phone = os.getenv("ADMIN_ALERT_PHONE")  # Formato: +5511999999999
        admin_whatsapp = os.getenv("ADMIN_ALERT_WHATSAPP")  # Formato: whatsapp:+5511999999999 ou +5511999999999
        admin_email = os.getenv("ADMIN_ALERT_EMAIL", user.email)
        
        # Enviar notificações em background (não bloquear request)
        if admin_phone:
            send_login_alert_sms(admin_phone, email, ip, success)
        if admin_whatsapp:
            send_login_alert_whatsapp(admin_whatsapp, email, ip, success)
        if admin_email:
            send_login_alert_email(admin_email, email, ip, user_agent, success)
    
    return {
        "blocked": blocked,
        "blocked_until": blocked_until,
        "recent_failures": recent_failures,
        "attempt_id": attempt.id
    }
