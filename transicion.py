import pygame

class PantallaTransicion:
    def __init__(self, ancho, alto):
        self.rect = pygame.Rect(0, 0, ancho, alto)
        self.superficie = pygame.Surface((ancho, alto))
        self.superficie.fill((0, 0, 0)) # Color negro
        self.alpha = 0  # 0 es transparente, 255 es negro total
        self.velocidad = 5
        self.modo = None # "oscurecer" o "aclarar"

    def iniciar(self, modo="oscurecer"):
        self.modo = modo
        if modo == "oscurecer": self.alpha = 0
        else: self.alpha = 255

    def actualizar(self):
        if self.modo == "oscurecer":
            self.alpha += self.velocidad
            if self.alpha >= 255:
                self.alpha = 255
                return True # Terminó de oscurecer
        elif self.modo == "aclarar":
            self.alpha -= self.velocidad
            if self.alpha <= 0:
                self.alpha = 0
                self.modo = None
        return False

    def dibujar(self, pantalla):
        if self.alpha > 0:
            self.superficie.set_alpha(self.alpha)
            pantalla.blit(self.superficie, (0, 0))