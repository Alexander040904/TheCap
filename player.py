import pygame
import os
pygame.mixer.pre_init(44100, -16, 2, 512) 
pygame.init()

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 28)
        self.sprite_offset_x = -26 
        self.sprite_offset_y = -4
        self.spawn_pos = (x, y)
        self.vel_y = 0
        self.vel_x = 4.5
        self.gravedad = 1
        self.en_suelo = False
        self.animaciones = {}
        self.estado = "reposo"
        self.frame_actual = 0
        self.velocidad_animacion = 0.15
        self.direccion_derecha = True
        self._cargar_imagenes()
        self.image = self.animaciones[self.estado][0]
        try:
            
            self.sonido_salto = pygame.mixer.Sound(os.path.join("assets", "sounds", "saltar.mpeg"))
            self.sonido_espada = pygame.mixer.Sound(os.path.join("assets", "sounds", "espada.mpeg"))
            self.sonido_muerte_player = pygame.mixer.Sound(os.path.join("assets", "sounds", "muerte_player.mpeg"))

            self.sonido_salto.set_volume(0.4) # Volumen de 0 a 1
            self.sonido_espada.set_volume(0.3) # Volumen de 0 a 1
            self.sonido_muerte_player.set_volume(0.4) # Volumen de 0 a 1
        except:
            print("No se encontró el sonido de ataque")
            self.sonido_salto = None

    def _cargar_imagenes(self):
        ruta_base = os.path.join("assets", "sprites", "player", "Sprites")
        for estado in ["reposo", "correr", "saltar", "pegar", "dead"]:
            ruta_estado = os.path.join(ruta_base, estado)
            self.animaciones[estado] = []
            if os.path.exists(ruta_estado):
                archivos = sorted(f for f in os.listdir(ruta_estado) if f.endswith('.png'))
                for archivo in archivos:
                    self.animaciones[estado].append(pygame.image.load(os.path.join(ruta_estado, archivo)).convert_alpha())

    def actualizar(self, bloques_solidos, bloques_daño):
        if self.estado == "dead":
            if self.sonido_muerte_player:
                self.sonido_muerte_player.play()
            self.frame_actual += self.velocidad_animacion
            if self.frame_actual >= len(self.animaciones["dead"]): self.respawn()
            else: self.image = self.animaciones["dead"][int(self.frame_actual)]
            return

        keys = pygame.key.get_pressed()
        dx = 0
        if self.estado != "pegar":
            if keys[pygame.K_a]:
                dx -= self.vel_x
                self.direccion_derecha = False
                if self.en_suelo: self.estado = "correr"
            elif keys[pygame.K_d]:
                dx += self.vel_x
                self.direccion_derecha = True
                if self.en_suelo: self.estado = "correr"
            else:
                if self.en_suelo: self.estado = "reposo"

            if keys[pygame.K_SPACE] and self.en_suelo:
                if self.sonido_salto:
                    self.sonido_salto.play()
                self.vel_y = -12
                self.en_suelo = False
                self.estado = "saltar"


            if keys[pygame.K_j]:
                if self.sonido_espada:
                    self.sonido_espada.play()
                self.estado = "pegar"
                self.frame_actual = 0

        self.vel_y += self.gravedad
        dy = self.vel_y
        
        # Colisiones
        self.rect.x += dx
        for bloque in bloques_solidos:
            if self.rect.colliderect(bloque):
                if dx > 0: self.rect.right = bloque.left
                elif dx < 0: self.rect.left = bloque.right

        self.en_suelo = False
        self.rect.y += dy
        for bloque in bloques_solidos:
            if self.rect.colliderect(bloque):
                if self.vel_y > 0:
                    self.rect.bottom = bloque.top
                    self.vel_y = 0
                    self.en_suelo = True
                elif self.vel_y < 0:
                    self.rect.top = bloque.bottom
                    self.vel_y = 0

        for trampa in bloques_daño:
            if self.rect.colliderect(trampa):
                self.estado = "dead"
                self.frame_actual = 0

        # Animación
        if not self.en_suelo and self.estado != "pegar": self.estado = "saltar"
        self.frame_actual += self.velocidad_animacion
        if self.frame_actual >= len(self.animaciones[self.estado]):
            if self.estado == "pegar": self.estado = "reposo"
            self.frame_actual = 0
        self.image = self.animaciones[self.estado][int(self.frame_actual)]

    def respawn(self):
        self.rect.x, self.rect.y = self.spawn_pos
        self.estado = "reposo"
        self.vel_y = 0

    def dibujar(self, surface, scroll_x):
            # 1. Dibujar el Sprite (tu código original)
        img = pygame.transform.flip(self.image, True, False) if not self.direccion_derecha else self.image
        surface.blit(img, (self.rect.x - scroll_x + self.sprite_offset_x, self.rect.y + self.sprite_offset_y))

