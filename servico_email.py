import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import json

with open('config.json', mode='r') as f:
    config = json.load(f)



class Email:
    def __init__(self, remetente: str) -> None:
        self.remetente = remetente
        self.senha: str | None = None

    def definir_senha(self, senha: str):
        self.senha = senha

    def enviar(self, assunto: str, mensagem: str, destinatarios: str | list[str], anexos: list | None=None):

        msg = MIMEMultipart()
        msg['Subject'] = assunto
        msg['From'] = self.remetente
        msg['To'] = ', '.join(destinatarios)

        corpo = MIMEText(mensagem, 'plain')
        msg.attach(corpo)

        if anexos:
            for caminho_arquivo in anexos:
                if os.path.exists(caminho_arquivo):
                    with open(caminho_arquivo, 'rb') as f:
                        parte = MIMEApplication(f.read(), Name=os.path.basename(caminho_arquivo))
                        parte['Content-Disposition'] = f'attachment; filename="{os.path.basename(caminho_arquivo)}"'
                        msg.attach(parte)
                else:
                    print(f"Atenção: Arquivo '{caminho_arquivo}' não encontrado e não foi anexado.")

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            if self.senha:
                smtp_server.login(self.remetente, self.senha)
                smtp_server.sendmail(self.remetente, destinatarios, msg.as_string())
        print("Email enviado com sucesso.")


def fazer_envio_email():
    email = Email(
        remetente='joabealvesyt@gmail.com',
    )
    email.definir_senha(config['senha_email'])
    corpo_email = (
        "Olá,\n\n"
        "Segue em anexo a fatura de energia referente ao período atual, "
        "contendo o detalhamento de consumo, tarifas aplicadas e o valor total a pagar.\n\n"
        "Por favor, verifique as informações e, em caso de qualquer dúvida ou divergência, "
        "fico à disposição para esclarecimentos.\n\n"
        "Atenciosamente,\n"
        "Joabe Alves"
    )
    email.enviar(assunto=f'[EMAIL TESTE] - Fatura de Energia – Valor a Pagar', mensagem=corpo_email, destinatarios=['joabealvesyt@gmail.com', 'maksuellyalves46@gmail.com'], anexos=['faturas/fatura_suellen.pdf'])

fazer_envio_email()