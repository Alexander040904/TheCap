import pygame
import os

class EnemigoFierce:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y , 32, 32)
        self.vida = 5
        self.estado = "reposo"
        self.frame_actual = 0
        self.animaciones = {}
        self.velocidad = 2
        self.direccion = -1
        self.mirando_derecha = False
        
        self.muerto = False
        self.animacion_finalizada = False
        self.timer_hurt = 0
        
        # --- LÓGICA DE DETECCIÓN ---
        self.despierto = False        # Nuevo: Empieza dormido
        self.rango_vision = 250       # Píxeles a los que te detecta
        
        self.ultimo_ataque = 0        
        self.espera_ataque = 3000     
        
        self.sprite_offset_x = -15 
        self.sprite_offset_y = 4 
        
        # Gravedad
        self.vel_y = 0
        self.gravedad = 0.8
        self.en_suelo = False

        self._cargar_animaciones()
        self.image = self.animaciones["reposo"][0]
        try:
            self.sonido_mordisco = pygame.mixer.Sound(os.path.join("assets", "sounds", "mordida.mpeg"))
            self.sonido_mordisco.set_volume(0.2)
        except:
            self.sonido_mordisco = None

    # ... (_cargar_animaciones y recibir_daño se mantienen igual) ...
    def _cargar_animaciones(self):
        ruta_base = os.path.join("assets", "sprites", "enemigos", "fierce")
        estados = ["reposo", "correr", "atacar", "hurt", "dead"]
        for estado in estados:
            self.animaciones[estado] = []
            ruta_estado = os.path.join(ruta_base, estado)
            if os.path.exists(ruta_estado):
                archivos = sorted(f for f in os.listdir(ruta_estado) if f.endswith(".png"))
                for f in archivos:
                    img = pygame.image.load(os.path.join(ruta_estado, f)).convert_alpha()
                    self.animaciones[estado].append(img)
            else:
                surf = pygame.Surface((32, 32)); surf.fill((255, 0, 0))
                self.animaciones[estado].append(surf)

    def recibir_daño(self):
        if self.muerto or self.estado == "hurt": return
        self.despierto = True # Si le pegas, se despierta sí o sí
        self.vida -= 1
        self.estado = "hurt"
        self.frame_actual = 0
        self.timer_hurt = pygame.time.get_ticks()
        if self.vida <= 0:
            self.muerto = True; self.estado = "dead"; self.frame_actual = 0

    def actualizar(self, jugador_rect, bloques_solidos, tiempo_actual):
        # 1. Aplicar Gravedad (siempre cae, incluso dormido)
        self.vel_y += self.gravedad
        self.rect.y += self.vel_y
        self.en_suelo = False 

        for bloque in bloques_solidos:
            if self.rect.colliderect(bloque):
                if self.vel_y > 0:
                    self.rect.bottom = bloque.top
                    self.vel_y = 0
                    self.en_suelo = True
                elif self.vel_y < 0:
                    self.rect.top = bloque.bottom
                    self.vel_y = 0

        if self.muerto:
            self.estado = "dead"
            self.frame_actual += 0.1
            if self.frame_actual >= len(self.animaciones["dead"]):
                self.frame_actual = len(self.animaciones["dead"]) - 1
                self.animacion_finalizada = True
            self.image = self.animaciones["dead"][int(self.frame_actual)]
            return

        # --- LÓGICA DE DESPERTAR ---
        distancia_x = jugador_rect.centerx - self.rect.centerx
        distancia_y = abs(jugador_rect.centery - self.rect.centery)

        if not self.despierto:
            # Solo se despierta si estás en rango X y a una altura similar (Y)
            if abs(distancia_x) < self.rango_vision and distancia_y < 100:
                self.despierto = True
            else:
                self.estado = "reposo" # Se queda quieto
        
        # --- COMPORTAMIENTO SI ESTÁ DESPIERTO ---
        if self.despierto:
            if self.estado == "hurt":
                if tiempo_actual - self.timer_hurt > 400:
                    self.estado = "reposo"
            elif self.estado == "atacar":
                pass 
            else:
                # Lógica de ataque
                if tiempo_actual - self.ultimo_ataque > self.espera_ataque:
                    self.estado = "atacar"
                    self.frame_actual = 0
                    self.ultimo_ataque = tiempo_actual
                    if abs(distancia_x) < 80 and self.sonido_mordisco:
                        self.sonido_mordisco.play()
                else:
                    # Persecución activa
                    if abs(distancia_x) < 300: # Rango de persecución
                        self.mirando_derecha = True if distancia_x > 0 else False
                        self.direccion = 1 if self.mirando_derecha else -1
                        
                        if abs(distancia_x) < 30:
                            self.estado = "reposo"
                        else:
                            self.estado = "correr"
                            self.rect.x += self.direccion * (self.velocidad + 1)
                    else:
                        # Si te alejas mucho, vuelve a patrullar o se queda en reposo
                        self.estado = "correr"
                        self.rect.x += self.direccion * self.velocidad
                        self.mirando_derecha = True if self.direccion > 0 else False

                # Colisión con paredes (Patrulla)
                for bloque in bloques_solidos:
                    if self.rect.colliderect(bloque):
                        if self.direccion > 0: self.rect.right = bloque.left
                        else: self.rect.left = bloque.right
                        self.direccion *= -1
                        break

        # Manejo de animaciones
        anim = self.animaciones[self.estado]
        self.frame_actual += 0.15
        if self.frame_actual >= len(anim):
            if self.estado == "atacar":
                self.estado = "reposo"
            self.frame_actual = 0
        self.image = anim[int(self.frame_actual)]

    def dibujar(self, surface, scroll_x):
        img = self.image
        if self.mirando_derecha:
            img = pygame.transform.flip(self.image, True, False)
        
        surface.blit(img, (self.rect.x - scroll_x + self.sprite_offset_x, 
                           self.rect.y + self.sprite_offset_y))