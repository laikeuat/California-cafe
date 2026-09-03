import os
import sys
import re
import smtplib
import email.message

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from infraestrutura.repositorio_usuario import RepositorioUsuario


class usuarioAplicacao:
    def __init__(self):
        self.repositorio_usuario = RepositorioUsuario()

    def validarEmail(self, email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    def verificaEmail(self, email):
        return self.repositorio_usuario.buscar_usuario(email) is None

    def enviarEmail(self, emailDestinatario):
        corpo_email = """
        <p>Olá,</p>
        <p>Você se cadastrou no sistema de controle de estoque.</p>
        <p>Para ativar sua conta, clique no link abaixo.</p>
        """

        msg = email.message.EmailMessage()
        msg["Subject"] = "Ativação de conta"
        msg["From"] = "camilafcarvalho07@gmail.com"
        msg["To"] = emailDestinatario
        password = "fiwa ymbj mvpf daox"  
      
        msg.add_alternative(corpo_email, subtype="html")

        try:
            s = smtplib.SMTP("smtp.gmail.com", 587)
            s.starttls()
            s.login(msg["From"], password)
            s.send_message(msg)
            print("Email enviado com sucesso!")
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")
        finally:
            s.quit()
