from objetos.Item import ORGANICOS, MINERAIS
 
class Inventario:
    def __init__(self):
        self.itens = {
            # orgânicos
            "Plasma":             0,
            "Essencia Fantasmal": 0,
            "Esporos":            0,
            "Nucleo de Esporos":  0,
            "Chapeu de Cogumelo": 0,
            "Gosma":              0,
            "Musgo":              0,
            "Olho de Goblin":     0,
            # minerais
            "Minerio Comum":      0,
            "Minerio Raro":       0,
            "Cristais":           0,
            "Madeira":            0,
        }
 
    def adicionar(self, tipo, quantidade=1):
        if tipo in self.itens:
            self.itens[tipo] += quantidade
 
    def remover(self, tipo, quantidade=1):
        if tipo in self.itens and self.itens[tipo] >= quantidade:
            self.itens[tipo] -= quantidade
            return True
        return False
 
    def tem(self, tipo, quantidade=1):
        return self.itens.get(tipo, 0) >= quantidade
 
    def organicos(self):
        return {k: v for k, v in self.itens.items() if k in ORGANICOS}
 
    def minerais(self):
        return {k: v for k, v in self.itens.items() if k in MINERAIS}