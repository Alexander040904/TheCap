import pygame
import os

class Proyectil:
    def __init__(self, x, y, direccion):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.velocidad = 6 * direccion
        self.imagenes = []
        self.frame = 0
        ruta = os.path.join("assets", "sprites", "enemigos", "totem", "bala")
        if os.path.exists(ruta):
            archivos = sorted(f for f in os.listdir(ruta) if f.endswith(".png"))
            self.imagenes = [pygame.image.load(os.path.join(ruta, f)).convert_alpha() for f in archivos]

    def actualizar(self):
        self.rect.x += self.velocidad
        if self.imagenes:
            self.frame = (self.frame + 0.2) % len(self.imagenes)

    def dibujar(self, surface, scroll_x):
        if self.imagenes:
            img = self.imagenes[int(self.frame)]
            if self.velocidad < 0: img = pygame.transform.flip(img, True, False)
            surface.blit(img, (self.rect.x - scroll_x, self.rect.y))

class TotemHead:
    def __init__(self, x, y, tipo_cabeza):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.tipo = tipo_cabeza
        self.vida = 3
        self.estado = "reposo"
        self.frame_actual = 0
        self.animaciones = {}
        self.ultimo_disparo = 0
        self.cadencia = 3000
        self.muerto = False
        self.animacion_finalizada = False # <-- NUEVA VARIABLE
        self.timer_hurt = 0
        self.mirando_derecha = False
        self.bala_lanzada = False
        self._cargar_animaciones()
        self.image = self.animaciones["reposo"][0]
        try:

            self.sonido_lanza = pygame.mixer.Sound(os.path.join("assets", "sounds", "lanza.mpeg"))


            self.sonido_lanza.set_volume(0.3) # Volumen de 0 a 1

        except:
            print("No se encontró el sonido de ataque")
            self.sonido_lanza = None

    def _cargar_animaciones(self):
        ruta_base = os.path.join("assets", "sprites", "enemigos", "totem", self.tipo)
        for estado in ["reposo", "disparo", "dead", "hurt"]:
            self.animaciones[estado] = []
            ruta_estado = os.path.join(ruta_base, estado)
            if os.path.exists(ruta_estado):
                archivos = sorted(f for f in os.listdir(ruta_estado) if f.endswith(".png"))
                for f in archivos:
                    self.animaciones[estado].append(pygame.image.load(os.path.join(ruta_estado, f)).convert_alpha())

    def recibir_daño(self):
        if self.muerto or self.estado == "hurt": return
        self.vida -= 1
        self.estado = "hurt"
        self.frame_actual = 0
        self.timer_hurt = pygame.time.get_ticks()
        if self.vida <= 0:
            self.muerto = True
            self.estado = "dead"

    def actualizar(self, jugador_rect, tiempo_actual, lista_balas):
        if self.muerto:
            self.estado = "dead"
            # Lógica para avanzar la animación de muerte
            if self.animaciones["dead"]:
                self.frame_actual += 0.1 # Velocidad de la animación de muerte
                if self.frame_actual >= len(self.animaciones["dead"]):
                    self.frame_actual = len(self.animaciones["dead"]) - 1
                    self.animacion_finalizada = True # <-- MARCAMOS PARA BORRAR
                self.image = self.animaciones["dead"][int(self.frame_actual)]
            return # Salimos para no ejecutar la IA si está muerto
        elif self.estado == "hurt":
            if tiempo_actual - self.timer_hurt > 500: self.estado = "reposo"
        else:
            distancia_x = jugador_rect.centerx - self.rect.centerx
            self.mirando_derecha = distancia_x > 0
            if abs(distancia_x) < 250:
                if tiempo_actual - self.ultimo_disparo > self.cadencia:
                    self.estado = "disparo"
                    self.frame_actual = 0
                    self.bala_lanzada = False
                    self.ultimo_disparo = tiempo_actual

        if self.estado == "disparo":
            if self.sonido_lanza and not self.bala_lanzada:
                self.sonido_lanza.play()
            if int(self.frame_actual) == 2 and not self.bala_lanzada:
                dir_b = 1 if self.mirando_derecha else -1
                lista_balas.append(Proyectil(self.rect.centerx, self.rect.y + 8, dir_b))
                self.bala_lanzada = True
            if self.frame_actual >= len(self.animaciones["disparo"]) - 1: self.estado = "reposo"

        if self.animaciones[self.estado]:
            self.frame_actual += 0.1
            if self.frame_actual >= len(self.animaciones[self.estado]):
                if self.estado == "dead": self.frame_actual = len(self.animaciones["dead"]) - 1
                else: self.frame_actual = 0
            self.image = self.animaciones[self.estado][int(self.frame_actual)]

    def dibujar(self, surface, scroll_x):
        img = self.image
        if self.mirando_derecha: img = pygame.transform.flip(img, True, False)
        surface.blit(img, (self.rect.x - scroll_x, self.rect.y))


# =======================
# CREAR TOTEM COMPLETO
# =======================
def crear_totem_completo(x_base, y_base):
    h1 = TotemHead(x_base, y_base + 5, "cabeza_base")
    h2 = TotemHead(x_base - 5, y_base - 17, "cabeza_media")
    h3 = TotemHead(x_base - 10, y_base - 36, "cabeza_superior")
    return [h1, h2, h3]
