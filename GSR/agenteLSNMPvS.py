import time
import json
import socket
from modules.mod_arCondicionado import ArCondicionado
from modules.mod_iluminacao import Iluminacao

class AgenteLSNMPvS:
    message_counter = 0

    def __init__(self, mib_filepath, host='localhost', port=54321):
        self.mib_filepath = mib_filepath
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((host, port))
        

    @classmethod
    def _generate_message_id(cls):
        cls.message_counter += 1
        return f"id-{cls.message_counter}"
    
    VALIDACOES = {
        "estado": ["True", "False"],
        "modo": ["refrigeracao", "aquecimento", "ventilacao"],
        "intensidade": lambda x: 0 <= int(x) <= 100,
        "temperatura": lambda x: 16 <= int(x) <= 25,
        "tipo": ["ar_condicionado","iluminacao"],
        "zona": ["sala", "escritorio", "cozinha", "quarto"]
    }



    def iniciarAgente(self):
        print("Agente L-SNMPvS iniciado.")
        while True:
            data, address = self.server_socket.recvfrom(4096)
            message = json.loads(data.decode())
            print("Processando mensagem:", message)
            
            if message["tipo"] == "GET":
                response = self.process_get(message["ids"], message["dispositivo_id"])
            elif message["tipo"] == "SET":
                response = self.process_set(message["ids"], message["dispositivo_id"], message["valores"])
            else:
                response = {
                    "tag": "response",
                    "tipo": "ERROR",
                    "timestamp": time.strftime('%d:%m:%Y:%H:%M:%S', time.gmtime(time.time())),
                    "message_id": message["message_id"],
                    "erros": ["Tipo de mensagem desconhecido"]
                }
            self.server_socket.sendto(json.dumps(response).encode(), address)

    def process_get(self, ids, dispositivo_id):
        response = {
            "tag": "response",
            "tipo": "GET-RESPONSE",
            "timestamp": time.strftime('%d:%m:%Y:%H:%M:%S', time.gmtime(time.time())),
            "message_id": self._generate_message_id(),
            "ids": ids,
            "dispositivo_id": dispositivo_id,
            "valores": {},
            "erros": []
        }
        dispositivos = self.ler_dispositivos()
        atributos = dispositivos.get(dispositivo_id, {})
        for id in ids:
            valor = atributos.get(id)
            if valor is not None:
                response["valores"][id] = valor
            else:
                response["valores"][id] = None
                response["erros"].append(f"Atributo {id} não encontrado para o dispositivo {dispositivo_id}")
        return response


    def process_set(self, ids, dispositivo_id, valores):
        response = {
            "tag": "response",
            "tipo": "SET-RESPONSE",
            "timestamp": time.strftime('%d:%m:%Y:%H:%M:%S', time.gmtime(time.time())),
            "message_id": self._generate_message_id(),
            "ids": ids,
            "dispositivo_id": dispositivo_id,
            "valores": [],
            "erros": []
        }
        dispositivos = self.ler_dispositivos()
        atributos = dispositivos.get(dispositivo_id, {})
        
        for id, valor in zip(ids, valores):
            if id == "tipo":
                response["valores"].append(None)
                response["erros"].append("Não é permitido alterar o tipo de dispositivo.")
                continue
            
            validacao = self.VALIDACOES.get(id)
            if validacao is not None:
                if (isinstance(validacao, list) and valor in validacao) or \
                (callable(validacao) and validacao(valor)):
                    atributos[id] = str(valor)
                    self.atualizar_dispositivo(dispositivo_id, atributos)
                    response["valores"].append(valor)
                else:
                    response["valores"].append(None)
                    response["erros"].append(f"Valor {valor} inválido para o atributo {id}")
            else:
                response["valores"].append(None)
                response["erros"].append(f"Atributo {id} não encontrado para o dispositivo {dispositivo_id}")
        
        return response


    def ler_dispositivos(self):
        dispositivos = {}
        with open('dispositivos.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if line:
                    parts = line.split('|')
                    if len(parts) == 2:
                        dispositivo_id = parts[0].strip()
                        attributes_str = parts[1].strip()
                        attributes = {}
                        for attr in attributes_str.split(';'):
                            if ':' in attr:
                                key, value = attr.split(':')
                                attributes[key.strip()] = value.strip()
                        dispositivos[dispositivo_id] = attributes
        print("Dispositivos lidos:", dispositivos)  # Debugging
        return dispositivos




    def atualizar_dispositivo(self, dispositivo_id, novos_atributos):
        dispositivos = self.ler_dispositivos()
        dispositivos[dispositivo_id] = novos_atributos
        with open(self.mib_filepath, 'w') as file:
            for id, atributos in dispositivos.items():
                atributos_str = '; '.join([f'{k}:{v}' for k, v in atributos.items()])
                file.write(f'{id} | {atributos_str}\n')

if __name__ == "__main__":
    agente = AgenteLSNMPvS(mib_filepath='dispositivos.txt')
    agente.iniciarAgente()