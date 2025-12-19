import pygame
class PantallaVictoria:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        # Fondo oscuro semitransparente
        self.overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        self.overlay.fill((20, 15, 10, 200)) # Un marrón muy oscuro transparente
        
        self.ORO = (255, 215, 0)
        self.MARFIL = (245, 245, 220)
        
        # Rectángulos de botones
        self.rect_regresar = pygame.Rect(ancho//2 - 100, alto//2 + 20, 200, 45)
        self.rect_salir = pygame.Rect(ancho//2 - 100, alto//2 + 80, 200, 45)

    def dibujar(self, screen):
        screen.blit(self.overlay, (0, 0))
        
        # Fuente default si no tienes la pirata
        font_titulo = pygame.font.SysFont("Impact", 45)
        font_sub = pygame.font.SysFont("Verdana", 22, italic=True)
        
        # Dibujar Textos
        txt1 = font_titulo.render("¡VIAJE SUPERADO!", True, self.ORO)
        txt2 = font_sub.render("Ya puedes navegar a nuevas tierras", True, self.MARFIL)
        
        screen.blit(txt1, (self.ancho//2 - txt1.get_width()//2, self.alto//2 - 80))
        screen.blit(txt2, (self.ancho//2 - txt2.get_width()//2, self.alto//2 - 30))

        # Dibujar Botones con borde de oro
        for rect, texto in [(self.rect_regresar, "REINTENTAR"), (self.rect_salir, "SALIR")]:
            pygame.draw.rect(screen, (60, 40, 20), rect) # Café madera
            pygame.draw.rect(screen, self.ORO, rect, 2) # Borde oro
            
            t = pygame.font.SysFont("Arial Black", 18).render(texto, True, self.MARFIL)
            screen.blit(t, (rect.centerx - t.get_width()//2, rect.centery - t.get_height()//2))

    def check_clic(self, pos):
        if self.rect_regresar.collidepoint(pos): return "regresar"
        if self.rect_salir.collidepoint(pos): return "salir"
        return None