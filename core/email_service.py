"""
Serviço Seguro de Envio de E-mails via SMTP com TLS/SSL.
Utiliza bibliotecas nativas de Python (smtplib, email.mime) e credenciais seguras.
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Optional, List

logger = logging.getLogger(__name__)


class EmailService:
    """Gerenciador de envio de e-mails corporativos do sistema GeoAlvo."""

    def __init__(
        self,
        servidor: Optional[str] = None,
        porta: Optional[int] = None,
        usuario: Optional[str] = None,
        senha: Optional[str] = None,
        remetente: Optional[str] = None,
    ):
        self.servidor = servidor or os.environ.get("SMTP_SERVER", "smtp.office365.com")
        self.porta = porta or int(os.environ.get("SMTP_PORT", 587))
        self.usuario = usuario or os.environ.get("SMTP_USER", "")
        self.senha = senha or os.environ.get("SMTP_PASSWORD", "")
        self.remetente = remetente or os.environ.get("SMTP_FROM", self.usuario)

    def enviar(
        self,
        destinatario: str,
        assunto: str,
        corpo_html: str,
        anexos: Optional[List[str]] = None,
    ) -> bool:
        """Envia e-mail formatado via conexão segura STARTTLS."""
        if not destinatario or not destinatario.strip():
            logger.warning("Tentativa de envio de e-mail sem destinatário.")
            return False

        if not self.usuario or not self.senha:
            logger.warning("Credenciais de SMTP não configuradas no ambiente. Envio cancelado.")
            return False

        msg = MIMEMultipart("mixed")
        msg["From"] = self.remetente
        msg["To"] = destinatario
        msg["Subject"] = assunto

        # Adiciona corpo HTML
        parte_html = MIMEText(corpo_html, "html", "utf-8")
        msg.attach(parte_html)

        # Adiciona anexos, se houver
        if anexos:
            for caminho in anexos:
                if os.path.exists(caminho):
                    nome_arquivo = os.path.basename(caminho)
                    with open(caminho, "rb") as f:
                        part = MIMEApplication(f.read(), Name=nome_arquivo)
                        part["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'
                        msg.attach(part)

        try:
            with smtplib.SMTP(self.servidor, self.porta, timeout=15) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.usuario, self.senha)
                server.sendmail(self.remetente, [destinatario], msg.as_string())
            logger.info("E-mail enviado com sucesso para: %s", destinatario)
            return True
        except Exception as exc:
            logger.error("Falha ao enviar e-mail para %s: %s", destinatario, exc)
            return False
