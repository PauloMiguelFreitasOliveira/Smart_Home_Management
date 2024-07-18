class Monitorizacao:
    def __init__(self):
        self.dados = {}
    
    def getIntensidadeLuz(self,zona):
        return self.dados.get(zona,{}).get('intensidade_luz', None)
    
    def getTemperatura(self, zona):
        return self.dados.get(zona, {}).get('temperatura', None)
    
    def atualizarLeituras(self, zona, luz, temperatura):
        if zona not in self.dados:
            self.dados[zona] = {}
        self.dados[zona]['intensidade_luz'] = luz
        self.dados[zona]['temperatura'] = temperatura
        print(f"Leituras atualizadas na zona {zona}: Luz = {luz} lúmens, Temperatura = {temperatura} ºC")
