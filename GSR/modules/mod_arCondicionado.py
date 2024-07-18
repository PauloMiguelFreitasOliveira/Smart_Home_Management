class ArCondicionado:
    def __init__(self, zona):
        self.zona = zona
        self.estado = False
        self.modo = None
        self.intensidade = 0
        self.temperatura = None

    def ligarAC(self, modo='refrigeracao', intensidade=100):
        if modo not in ['refrigeracao', 'aquecimento']:
            print(f"Modo {modo} inválido. Use 'refrigeracao' ou 'aquecimento'.")
            return
        self.estado = True
        self.modo = modo
        self.intensidade = intensidade
        print(f"Ar condicionado da zona {self.zona} ligado no modo de {modo} com intensidade {intensidade}%.")

    def desligarAC(self):
        self.estado = False
        self.modo = None
        self.intensidade = 0
        print(f"Ar condicionado da zona {self.zona} desligado.")

    def ajustarIntensidadeAC(self, intensidade):
        if self.estado:
            self.intensidade = intensidade
            print(f"Intensidade do ar condicionado na zona {self.zona} ajustada para {intensidade}%.")
        else:
            print(f"O ar condicionado na zona {self.zona} encontra-se desligado.")

    def alterarModoAC(self, modo):
        if modo not in ['refrigeracao', 'aquecimento']:
            print(f"Modo {modo} inválido. Use 'refrigeracao' ou 'aquecimento'.")
            return
        if self.estado:
            self.modo = modo
            print(f"Modo do ar condicionado na zona {self.zona} alterado para {modo}.")
        else:
            print(f"O ar condicionado na zona {self.zona} encontra-se desligado.")

    def to_string(self):
        return f"tipo:ar_condicionado; zona:{self.zona}; estado:{self.estado}; modo:{self.modo}; intensidade:{self.intensidade}; temperatura:{self.temperatura}"

    @staticmethod
    def from_string(data):
        atributos = dict(attr.split(':') for attr in data.split('; ') if ':' in attr)
        if 'zona' not in atributos:
            raise ValueError(f"Atributo 'zona' não encontrado em {data}")
        ac = ArCondicionado(atributos['zona'])
        ac.estado = atributos.get('estado', 'False') == 'True'
        ac.modo = atributos.get('modo', None)
        ac.intensidade = int(atributos.get('intensidade', 0))
        ac.temperatura = int(atributos.get('temperatura', '0')) if atributos.get('temperatura', 'None') != 'None' else None
        return ac