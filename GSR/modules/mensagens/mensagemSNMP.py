import time
import random
from datetime import datetime

class MensagemSNMP:
    message_counter = 0

    def __init__(self, tipo, ids, dispositivo_id, valores=None):
        self.tag = "request"
        self.tipo = tipo
        self.timestamp = self._get_timestamp()
        self.message_id = self._generate_message_id()
        self.ids = ids
        self.dispositivo_id = dispositivo_id
        self.valores = valores if valores is not None else []
        self.erros = []

        
    def _generate_tag(self):
        return f"msg-{self.message_counter}"
    
    def _generate_message_id(self):
        MensagemSNMP.message_counter += 1
        return f"id-{MensagemSNMP.message_counter}"

    def _get_timestamp(self):
        now = datetime.now()
        return now.strftime("%d:%m:%Y:%H:%M:%S:%f")[:-3]


    def to_dict(self):
        return {
            "tag": self.tag,
            "tipo": self.tipo,
            "timestamp": self.timestamp,
            "message_id": self.message_id,
            "ids": self.ids,
            "dispositivo_id": self.dispositivo_id,
            "valores": self.valores,
            "erros": self.erros
        }

    @classmethod
    def from_dict(cls, mensagem_dict):
        mensagem = cls(
            tipo=mensagem_dict['tipo'],
            ids=mensagem_dict['ids'],
            zona=mensagem_dict['zona'],
            valores=mensagem_dict.get('valores', [])
        )
        mensagem.erros = mensagem_dict.get('erros', [])
        return mensagem