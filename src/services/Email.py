from  fastapi_mail import FastMail , MessageSchema , MessageType
from src.utils.email import conf, render_template


class EmailService:
    
    async  def  send_email(
        self,
        email:str,
        subject:str,
        template_name:str,
        **kwargs
    ):
        html = render_template(template_name, **kwargs)
        
        message = MessageSchema(
            subject=subject,
            recipients=[email],
            body=html,
            subtype=MessageType.html,
        )
        
        fm = FastMail(conf)
        await fm.send_message(message)
        
        return True