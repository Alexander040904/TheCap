import pygame
import os
import sys
from mapa import MapaTiled
from player import Player
from enemigo import crear_totem_completo
from transicion import PantallaTransicion
from enemigo_fierce import EnemigoFierce
from interfaz import PantallaVictoria 

def main():
    # Configuración para que los píxeles se vean nítidos al estirar la pantalla
    os.environ['SDL_RENDER_SCALE_QUALITY'] = '0'

    try:
        pygame.mixer.pre_init(44100, -16, 2, 256) 
    except:
        print("No se pudo pre-inicializar el mixer")
    
    pygame.init()
    
    try:
        pygame.mixer.music.load(os.path.join("assets", "sounds", "fondo.mpeg"))
        pygame.mixer.music.set_volume(0.3) 
        pygame.mixer.music.play(-1) 
    except:
        print("No se pudo cargar la música de fondo")

    # --- CONFIGURACIÓN DE PANTALLA ---
    ANCHO_VIRTUAL, ALTO_VIRTUAL = 640, 32 * 8  # Resolución original del juego
    
    info = pygame.display.Info()
    ANCHO_REAL, ALTO_REAL = info.current_w, info.current_h

    # Ventana en pantalla completa con escalado automático
    screen = pygame.display.set_mode((ANCHO_REAL, ALTO_REAL), pygame.FULLSCREEN | pygame.SCALED)
    
    # Superficie de dibujo (Lienzo)
    lienzo = pygame.Surface((ANCHO_VIRTUAL, ALTO_VIRTUAL))
    
    pygame.display.set_caption("The Cap - Adventure")
    clock = pygame.time.Clock()

    # 1. Carga de escenario
    ruta_mapa = os.path.join('assets', 'tiled', 'mapa.tmx')
    escenario = MapaTiled(ruta_mapa, 32, 32)
    
    # 2. Pantallas e Interfaz
    fade = PantallaTransicion(ANCHO_VIRTUAL, ALTO_VIRTUAL)
    interfaz_victoria = PantallaVictoria(ANCHO_VIRTUAL, ALTO_VIRTUAL)
    
    haciendo_transicion = False
    ganaste = False
    running = True

    # --- FUNCIONES DE APOYO ---
    def obtener_checkpoint_cercano(pos_jugador, lista_banderas):
        if not lista_banderas:
            return escenario.spawn_pos 
        
        # Ordenar por X y filtrar las ya superadas
        banderas_ordenadas = sorted(lista_banderas, key=lambda b: b[0])
        banderas_pasadas = [b for b in banderas_ordenadas if b[0] <= pos_jugador[0] + 10]
        
        if not banderas_pasadas:
            return banderas_ordenadas[0]
        
        # Retornar la última bandera superada
        return max(banderas_pasadas, key=lambda b: b[0])

    def reset_nivel(posicion_respawn):
        nonlocal enemigos_totem, enemigos_fierce, balas_enemigas, bola, ganaste
        ganaste = False
        balas_enemigas = []
        
        # Crear nuevo jugador en el punto indicado
        bola = Player(posicion_respawn[0], posicion_respawn[1])
        
        # Regenerar todos los enemigos
        enemigos_totem = []
        for pos in escenario.puntos_spawn_enemigos:
            enemigos_totem.extend(crear_totem_completo(pos[0], pos[1]))
        
        enemigos_fierce = []
        if hasattr(escenario, 'puntos_spawn_fierce'):
            for pos in escenario.puntos_spawn_fierce:
                enemigos_fierce.append(EnemigoFierce(pos[0], pos[1]))

    # --- INICIALIZACIÓN INICIAL ---
    enemigos_totem = []
    enemigos_fierce = []
    balas_enemigas = []
    bola = None
    reset_nivel(escenario.spawn_pos)

    while running:
        tiempo = pygame.time.get_ticks()
        
        # --- EVENTOS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # Salida rápida
                    running = False

            if event.type == pygame.MOUSEBUTTONDOWN and ganaste:
                accion = interfaz_victoria.check_clic(event.pos)
                if accion == "regresar":
                    # Reintentar desde la PRIMERA bandera del mapa
                    punto_inicio = escenario.puntos_banderas[0] if escenario.puntos_banderas else escenario.spawn_pos
                    reset_nivel(punto_inicio)
                elif accion == "salir":
                    running = False

        # --- LÓGICA DE MUERTE ---
        if bola.estado == "dead" and int(bola.frame_actual) >= len(bola.animaciones["dead"]) - 1:
            punto = obtener_checkpoint_cercano((bola.rect.x, bola.rect.y), escenario.puntos_banderas)
            reset_nivel(punto)

        # --- TRANSICIONES DE MAPA ---
        if not haciendo_transicion and not ganaste and bola.estado != "dead":
            for zona in escenario.zonas_transicion:
                if bola.rect.colliderect(zona):
                    haciendo_transicion = True
                    fade.iniciar("oscurecer")
                    break

        if haciendo_transicion:
            termino_oscurecer = fade.actualizar()
            if termino_oscurecer:
                if escenario.punto_destino:
                    bola.rect.x, bola.rect.y = escenario.punto_destino
                fade.iniciar("aclarar")
                haciendo_transicion = False
        
        elif not ganaste: 
            # Actualizar Jugador y Colisiones
            solidos_totem = [e.rect for e in enemigos_totem if not e.muerto]
            solidos_fierce = [f.rect for f in enemigos_fierce if not f.muerto]
            bola.actualizar(escenario.bloques_solidos + solidos_totem + solidos_fierce, escenario.bloques_daño)

            # Victoria
            for punto_victoria in escenario.puntos_gano:
                if bola.rect.colliderect(punto_victoria):
                    ganaste = True

            # --- SISTEMA DE ATAQUE (CORREGIDO) ---
            area_ataque = None
            if bola.estado == "pegar" and int(bola.frame_actual) == 2:
                if bola.direccion_derecha:
                    area_ataque = pygame.Rect(bola.rect.right, bola.rect.y, 25, bola.rect.height)
                else:
                    area_ataque = pygame.Rect(bola.rect.left - 25, bola.rect.y, 25, bola.rect.height)
                
                for e in enemigos_totem:
                    if area_ataque.colliderect(e.rect): e.recibir_daño()
                for f in enemigos_fierce:
                    if area_ataque.colliderect(f.rect): f.recibir_daño()

            # Actualizar Enemigos
            for e in enemigos_totem:
                e.actualizar(bola.rect, tiempo, balas_enemigas)
            
            for f in enemigos_fierce:
                f.actualizar(bola.rect, escenario.bloques_solidos, tiempo)
                if not f.muerto and f.estado == "atacar":
                    if f.rect.inflate(10, 2).colliderect(bola.rect) and bola.estado != "dead":
                        bola.estado = "dead"
                        bola.frame_actual = 0

            # Actualizar Proyectiles
            for b in balas_enemigas[:]:
                b.actualizar()
                if b.rect.colliderect(bola.rect) and bola.estado != "dead":
                    bola.estado = "dead"
                    bola.frame_actual = 0
                    balas_enemigas.remove(b)
                elif abs(b.rect.x - bola.rect.x) > 800:
                    balas_enemigas.remove(b)

            # Limpieza de memoria
            enemigos_totem = [e for e in enemigos_totem if not e.animacion_finalizada]
            enemigos_fierce = [f for f in enemigos_fierce if not f.animacion_finalizada]

        # --- CÁMARA ---
        scroll_x = max(0, min(bola.rect.centerx - ANCHO_VIRTUAL // 2, escenario.width_px - ANCHO_VIRTUAL))

        # --- DIBUJADO (A LIENZO) ---
        lienzo.fill((56, 54, 54))
        escenario.dibujar(lienzo, scroll_x, tiempo)
        
        for e in enemigos_totem: e.dibujar(lienzo, scroll_x)
        for f in enemigos_fierce: f.dibujar(lienzo, scroll_x)
        for b in balas_enemigas: b.dibujar(lienzo, scroll_x)
        
        bola.dibujar(lienzo, scroll_x)
        
        if ganaste:
            interfaz_victoria.dibujar(lienzo)
        
        fade.actualizar() 
        fade.dibujar(lienzo)
        
        # --- ESCALADO FINAL A PANTALLA ---
        # Se toma el lienzo pequeño y se estira al tamaño de la pantalla real
        screen.blit(pygame.transform.scale(lienzo, screen.get_size()), (0, 0))
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()