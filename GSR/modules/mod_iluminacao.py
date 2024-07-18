class Iluminacao:
    def __init__(self, zona):
        self.zona = zona
        self.estado = False
        self.intensidade = 0

    def ligarLuz(self, intensidade=100):
        self.estado = True
        self.intensidade = intensidade
        print(f"Luz da zona {self.zona} ligada com intensidade {intensidade}%.")

    def desligarLuz(self):
        self.estado = False
        self.intensidade = 0
        print(f"Luz da zona {self.zona} desligada.")

    def ajustarIntensidade(self, intensidade):
        if self.estado:
            self.intensidade = intensidade
            print(f"Intensidade da luz na zona {self.zona} ajustada para {intensidade}%.")
        else:
            print(f"A luz na zona {self.zona} está desligada.")

    def to_string(self):
        return f"tipo:iluminacao; zona:{self.zona}; estado:{self.estado}; intensidade:{self.intensidade}"

    @staticmethod
    def from_string(data):
        atributos = dict(attr.split(':') for attr in data.split('; ') if ':' in attr)
        if 'zona' not in atributos:
            raise ValueError(f"Atributo 'zona' não encontrado em {data}")
        luz = Iluminacao(atributos['zona'])
        luz.estado = atributos.get('estado', 'False') == 'True'
        luz.intensidade = int(atributos.get('intensidade', 0))
        return luz