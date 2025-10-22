from abc import ABC, abstractmethod
from utils import MetaSingleton
from datetime import datetime
import uuid

# Interface para os canais de notificação
class NotificationChannel(ABC):
    @abstractmethod
    def send(self, user, subject, message, data=None):
        pass

# Serviço externo de email 
class EmailService:
    def __init__(self):
        self.server = "smtp.example.com"
        self.port = 587
        self.username = "cinema@example.com"
        self.password = "password123"  
    
    def send_email(self, to_email, subject, body, html=None):
        print(f"\n[EMAIL SERVICE] Enviando email para {to_email}")
        print(f"Assunto: {subject}")
        print(f"Conteúdo: {body}")
        print(f"De: {self.username}")
        print("-" * 50)
        
        return {
            "status": "sent",
            "message_id": f"email-{uuid.uuid4()}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

# Serviço externo de SMS
class SMSService:
    def __init__(self):
        self.api_key = "sms-api-key-123"
        self.sender_id = "CINEMA"
        self.api_url = "https://api.smsservice.example.com/send"
    
    def send_sms(self, phone_number, message):
        print(f"\n[SMS SERVICE] Enviando SMS para {phone_number}")
        print(f"Mensagem: {message}")
        print(f"Remetente: {self.sender_id}")
        print("-" * 50)
        
        return {
            "status": "delivered",
            "message_id": f"sms-{uuid.uuid4()}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

# Serviço de notificações push
class PushNotificationService:
    def __init__(self):
        self.api_key = "push-api-key-456"
        self.api_url = "https://api.pushnotifications.example.com/send"
    
    def send_push(self, device_token, title, body, data=None):
        print(f"\n[PUSH SERVICE] Enviando notificação push para dispositivo {device_token[:8]}...")
        print(f"Título: {title}")
        print(f"Mensagem: {body}")
        if data:
            print(f"Dados: {data}")
        print("-" * 50)
        
        return {
            "status": "sent",
            "message_id": f"push-{uuid.uuid4()}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

# Adaptador para o serviço de email
class EmailNotificationAdapter(NotificationChannel):
    def __init__(self, email_service=None):
        self.email_service = email_service or EmailService()
        self.sent_messages = []
    
    def send(self, user, subject, message, data=None):
        email_body = message
        if data:
            email_body += "\n\nDetalhes adicionais:\n"
            for key, value in data.items():
                email_body += f"- {key}: {value}\n"
        
        result = self.email_service.send_email(
            to_email=user.email,
            subject=f"Cinema App: {subject}",
            body=email_body
        )
        
        self.sent_messages.append({
            "user_id": user.id,
            "email": user.email,
            "subject": subject,
            "message": message,
            "data": data,
            "result": result,
            "timestamp": datetime.now()
        })
        
        return result

# Adaptador para o serviço de SMS
class SMSNotificationAdapter(NotificationChannel):
    def __init__(self, sms_service=None):
        self.sms_service = sms_service or SMSService()
        self.sent_messages = []
    
    def send(self, user, subject, message, data=None):
        if not hasattr(user, 'phone') or not user.phone:
            print(f"Usuário {user.name} não possui número de telefone cadastrado.")
            return {"status": "error", "message": "No phone number available"}
        
        sms_text = f"{subject}: {message}"
        if len(sms_text) > 160:
            sms_text = sms_text[:157] + "..."
        
        result = self.sms_service.send_sms(
            phone_number=user.phone,
            message=sms_text
        )
        
        self.sent_messages.append({
            "user_id": user.id,
            "phone": user.phone,
            "subject": subject,
            "message": message,
            "data": data,
            "result": result,
            "timestamp": datetime.now()
        })
        
        return result

# Adaptador para o serviço de notificações push
class PushNotificationAdapter(NotificationChannel):
    def __init__(self, push_service=None):
        self.push_service = push_service or PushNotificationService()
        self.sent_messages = []
    
    def send(self, user, subject, message, data=None):
        if not hasattr(user, 'device_token') or not user.device_token:
            print(f"Usuário {user.name} não possui token de dispositivo cadastrado.")
            return {"status": "error", "message": "No device token available"}
        
        result = self.push_service.send_push(
            device_token=user.device_token,
            title=subject,
            body=message,
            data=data
        )
        
        self.sent_messages.append({
            "user_id": user.id,
            "device_token": user.device_token,
            "subject": subject,
            "message": message,
            "data": data,
            "result": result,
            "timestamp": datetime.now()
        })
        
        return result