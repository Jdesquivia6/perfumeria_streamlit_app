from flask_mail import Mail, Message
from flask import current_app

mail = Mail()

def enviar_correo_bienvenida(email, username):
    with current_app.app_context():
        msg = Message(
            "Bienvenido a la aplicación",
            sender="jsef1023@gmail.com",
            recipients=[email],
        )
        msg.body = f"Hola, {username}. Gracias por unirte a nuestra aplicación."

        mail.send(msg)
