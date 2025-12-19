import pygame
import pytmx
import os

class MapaTiled:
    def __init__(self, ruta_mapa, tw, th):
        self.tw = tw
        self.th = th
        self.mapa = pytmx.load_pygame(ruta_mapa, pixelalpha=True)
        self.width_px = self.mapa.width * tw
        
        self.bloques_solidos = []
        self.bloques_daño = []
        self.puntos_spawn_enemigos = []
        self.zonas_transicion = [] 
        self.punto_destino = None  
        self.puntos_spawn_fierce = []
        self.puntos_gano = [] # NUEVA LISTA PARA LA CAPA GANO
        self.puntos_banderas = []
        self.spawn_pos = (100, 100)
        
        self._extraer_datos()

    def _extraer_datos(self):
        for layer in self.mapa.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if gid == 0: continue
                    
                    img = self.mapa.get_tile_image_by_gid(gid)
                    off_y = img.get_height() - self.th
                    off_x = (img.get_width() - self.tw) // 2
                    
                    # Ajuste de offset para capas lógicas
                    if layer.name in ["plataforma", "nubes", "fondo", "newmap", "closemap", "ventanas", "bandera", "spawenemigos", "gano"]:
                        off_x = 0
                    
                    rect = pygame.Rect((x * self.tw) - off_x, (y * self.th) - off_y, 
                                       img.get_width(), img.get_height())
                    
                    if layer.name in ["plataforma", "palmera_front"]:
                        self.bloques_solidos.append(rect)
                    
                    elif layer.name in ["puas", "cangrejoMalo"]:
                        # ... (tu lógica de daño se mantiene igual) ...
                        area_daño = rect.copy()
                        if layer.name == "cangrejoMalo":
                            area_daño = rect.inflate(-10, -12)
                            area_daño.bottom = rect.bottom
                        else:
                            area_daño = rect.inflate(-4, -4)
                        self.bloques_daño.append(area_daño)
                    
                    elif layer.name == "bandera":
                        # EVITAR DUPLICADOS: Si ya hay una bandera muy cerca, no la agregamos
                        existe = False
                        for p in self.puntos_banderas:
                            if abs(p[0] - rect.x) < 5 and abs(p[1] - rect.y) < 5:
                                existe = True
                                break
                        if not existe:
                            self.puntos_banderas.append((rect.x, rect.y))
                    
                    elif layer.name == "spawenemigos":
                        self.puntos_spawn_enemigos.append((rect.x, rect.y))
                    elif layer.name == "newmap":
                        self.zonas_transicion.append(rect)
                    elif layer.name == "closemap":
                        self.punto_destino = (rect.x, rect.y)
                    elif layer.name == "spawtwoenemigos":
                        self.puntos_spawn_fierce.append((rect.x, rect.y))
                    elif layer.name == "gano":
                        self.puntos_gano.append(rect)

        # --- IMPORTANTE: ORDENAR LAS BANDERAS POR X DESPUÉS DE LEER TODO ---
        self.puntos_banderas.sort(key=lambda p: p[0])
        
        # Ahora que están ordenadas, la spawn_pos real es la primera bandera
        if self.puntos_banderas:
            self.spawn_pos = self.puntos_banderas[0]
        else:
            self.spawn_pos = (100, 100) # Por si no hay banderas

    def dibujar(self, surface, scroll_x, tiempo_actual):
        for layer in self.mapa.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                # No dibujamos las capas de lógica (opcional, para que no se vean los activadores)
              
                
                for x, y, gid in layer:
                    img = self.mapa.get_tile_image_by_gid(gid)
                    if not img: continue
                    
                    props = self.mapa.get_tile_properties_by_gid(gid)
                    if props and 'frames' in props and len(props['frames']) > 0:
                        ciclo = sum(int(f.duration) for f in props['frames'])
                        if ciclo > 0:
                            t_en_ciclo = tiempo_actual % ciclo
                            acum = 0
                            for f in props['frames']:
                                acum += int(f.duration)
                                if t_en_ciclo < acum:
                                    img = self.mapa.get_tile_image_by_gid(f.gid)
                                    break

                    off_y = img.get_height() - self.th
                    off_x = (img.get_width() - self.tw) // 2
                    if layer.name in ["plataforma", "nubes", "fondo", "newmap", "ventanas", "closemap", "bandera", "spawenemigos"]:
                        off_x = 0

                    p_x = (x * self.tw) - off_x - scroll_x
                    p_y = (y * self.th) - off_y
                    
                    if layer.name == "cangrejoMalo": p_y += 3
                    if layer.name == "veladoras": p_y += 10
                    
                    if -img.get_width() < p_x < surface.get_width():
                        surface.blit(img, (p_x, p_y))