import random
import sys
import time
import pygame

# ------------------------------------------------------------------------------
# Configuración e Inicialización de Pygame
# ------------------------------------------------------------------------------
pygame.init()
pygame.font.init()

# Dimensiones de la ventana
WIDTH, HEIGHT = 1024, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Visualizador Interactivo Merge Sort (Divide y Vencerás)")

# Paleta de Colores (Tema Oscuro Profesional)
COLOR_BG = (24, 25, 38)            # Fondo principal (#181926)
COLOR_PANEL = (36, 39, 58)         # Panel de estadísticas (#24273a)
COLOR_TEXT = (202, 211, 245)       # Texto general
COLOR_SUBTEXT = (165, 173, 203)    # Texto secundario
COLOR_BORDER = (73, 77, 100)       # Bordes de paneles

# Estados visuales de las barras
COLOR_DEFAULT = (138, 173, 244)    # Azul: Elemento no seleccionado (#8aatf4)
COLOR_SPLIT = (198, 160, 246)      # Púrpura: Rango activo de división (#c6a0f6)
COLOR_COMPARE = (238, 212, 159)    # Amarillo: Elementos siendo comparados (#eed49f)
COLOR_MERGE = (237, 135, 150)      # Rojo/Rosa: Elemento siendo insertado (#ed8796)
COLOR_SORTED = (166, 218, 149)     # Verde: Sublista ordenada o completada (#a6da95)

# Tipografías
FONT_TITLE = pygame.font.SysFont("Segoe UI", 18, bold=True)
FONT_BODY = pygame.font.SysFont("Segoe UI", 14)
FONT_SMALL = pygame.font.SysFont("Segoe UI", 12)


class MergeSortVisualizer:
    def __init__(self, num_elements=50):
        self.num_elements = num_elements
        self.array = []
        self.bar_colors = []
        
        # Estadísticas del algoritmo
        self.comparisons = 0
        self.array_accesses = 0
        self.start_time = None
        self.elapsed_time = 0.0
        
        # Control de ejecución y animación
        self.fps = 30
        self.is_paused = True
        self.step_mode = False
        self.algorithm_finished = False
        self.status_message = "Listo para iniciar (Presiona ESPACIO)"
        
        # Generador de pasos de Merge Sort
        self.generator = None
        self.reset_array()

    def reset_array(self):
        """Genera un nuevo arreglo aleatorio y reinicia los contadores."""
        self.array = [random.randint(15, 380) for _ in range(self.num_elements)]
        self.bar_colors = [COLOR_DEFAULT] * self.num_elements
        self.comparisons = 0
        self.array_accesses = 0
        self.start_time = None
        self.elapsed_time = 0.0
        self.is_paused = True
        self.step_mode = False
        self.algorithm_finished = False
        self.status_message = "Arreglo reiniciado. Presiona ESPACIO para iniciar."
        self.generator = self.merge_sort_animated(0, len(self.array) - 1)

    def merge_sort_animated(self, left, right):
        """
        Algoritmo Merge Sort implementado como un generador.
        Entrega estados intermedios para renderizar cada frame sin bloquear Pygame.
        """
        if left >= right:
            return

        mid = (left + right) // 2

        # Resaltar el rango actual que se dividirá
        for i in range(left, right + 1):
            if self.bar_colors[i] != COLOR_SORTED:
                self.bar_colors[i] = COLOR_SPLIT
        
        self.status_message = f"Dividiendo sublista en rangos [{left}..{mid}] y [{mid+1}..{right}]"
        yield

        # Llamadas recursivas a la sublista izquierda y derecha
        yield from self.merge_sort_animated(left, mid)
        yield from self.merge_sort_animated(mid + 1, right)

        # Proceso de Mezcla (Merge)
        yield from self.merge_animated(left, mid, right)

        # Si hemos completado todo el arreglo
        if left == 0 and right == len(self.array) - 1:
            for i in range(len(self.array)):
                self.bar_colors[i] = COLOR_SORTED
            self.algorithm_finished = True
            self.is_paused = True
            self.status_message = "¡Ordenamiento completado con éxito!"
            yield

    def merge_animated(self, left, mid, right):
        """Mezcla dos sublistas ordenadas generando estados visuales paso a paso."""
        left_sub = self.array[left:mid + 1]
        right_sub = self.array[mid + 1:right + 1]

        i = 0  # Índice sublista izquierda
        j = 0  # Índice sublista derecha
        k = left  # Índice en el arreglo principal

        self.status_message = f"Mezclando sublistas ordenadas en rango [{left}..{right}]"

        while i < len(left_sub) and j < len(right_sub):
            # Marcar elementos en comparación
            idx_left = left + i
            idx_right = mid + 1 + j
            
            self.bar_colors[idx_left] = COLOR_COMPARE
            self.bar_colors[idx_right] = COLOR_COMPARE
            self.comparisons += 1
            self.array_accesses += 2
            yield

            if left_sub[i] <= right_sub[j]:
                self.array[k] = left_sub[i]
                self.bar_colors[k] = COLOR_MERGE
                i += 1
            else:
                self.array[k] = right_sub[j]
                self.bar_colors[k] = COLOR_MERGE
                j += 1

            self.array_accesses += 2
            k += 1
            yield

        # Copiar elementos restantes de la izquierda
        while i < len(left_sub):
            self.array[k] = left_sub[i]
            self.bar_colors[k] = COLOR_MERGE
            self.array_accesses += 2
            i += 1
            k += 1
            yield

        # Copiar elementos restantes de la derecha
        while j < len(right_sub):
            self.array[k] = right_sub[j]
            self.bar_colors[k] = COLOR_MERGE
            self.array_accesses += 2
            j += 1
            k += 1
            yield

        # Marcar la subsección como ordenada temporalmente
        for idx in range(left, right + 1):
            self.bar_colors[idx] = COLOR_SORTED
        yield

    def update(self):
        """Avanza la animación un paso si no está en pausa."""
        if not self.is_paused and not self.algorithm_finished:
            if self.start_time is None:
                self.start_time = time.time()
            
            self.elapsed_time = time.time() - self.start_time
            
            try:
                next(self.generator)
            except StopIteration:
                self.algorithm_finished = True
                self.is_paused = True
                self.status_message = "¡Ordenamiento Merge Sort Finalizado!"

    def step(self):
        """Ejecuta exactamente un paso del algoritmo (Modo Paso a Paso)."""
        if not self.algorithm_finished:
            if self.start_time is None:
                self.start_time = time.time()
            try:
                next(self.generator)
                self.elapsed_time = time.time() - self.start_time
            except StopIteration:
                self.algorithm_finished = True
                self.is_paused = True
                self.status_message = "¡Ordenamiento Merge Sort Finalizado!"

    def draw(self, surface):
        """Renderiza la interfaz gráfica completa en pantalla."""
        surface.fill(COLOR_BG)
        
        # 1. Dibujar Panel Superior (Información y Métricas)
        panel_rect = pygame.Rect(15, 15, WIDTH - 30, 90)
        pygame.draw.rect(surface, COLOR_PANEL, panel_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_BORDER, panel_rect, width=1, border_radius=8)

        # Título y Estado
        title_surf = FONT_TITLE.render("Merge Sort (Divide y Vencerás) — Complejidad O(N log N)", True, COLOR_TEXT)
        status_surf = FONT_BODY.render(f"Estado: {self.status_message}", True, COLOR_SUBTEXT)
        surface.blit(title_surf, (30, 25))
        surface.blit(status_surf, (30, 55))

        # Métricas a la derecha
        comp_surf = FONT_BODY.render(f"Comparaciones: {self.comparisons}", True, COLOR_TEXT)
        acc_surf = FONT_BODY.render(f"Accesos a Memoria: {self.array_accesses}", True, COLOR_TEXT)
        time_surf = FONT_BODY.render(f"Tiempo Transcurrido: {self.elapsed_time:.2f} s", True, COLOR_TEXT)
        
        surface.blit(comp_surf, (680, 25))
        surface.blit(acc_surf, (680, 48))
        surface.blit(time_surf, (680, 71))

        # 2. Dibujar Área del Arreglo (Barras Verticales)
        margin_x = 30
        margin_bottom = 70
        available_width = WIDTH - (margin_x * 2)
        available_height = HEIGHT - 200
        
        bar_width = available_width / self.num_elements

        for i, val in enumerate(self.array):
            x = margin_x + i * bar_width
            bar_height = (val / 400.0) * available_height
            y = HEIGHT - margin_bottom - bar_height

            rect = pygame.Rect(x + 1, y, max(1, bar_width - 2), bar_height)
            pygame.draw.rect(surface, self.bar_colors[i], rect, border_radius=3)

        # 3. Dibujar Leyenda de Colores
        legend_items = [
            ("Sin Procesar", COLOR_DEFAULT),
            ("División (Rango)", COLOR_SPLIT),
            ("Comparación", COLOR_COMPARE),
            ("Inserción / Mezcla", COLOR_MERGE),
            ("Ordenado", COLOR_SORTED)
        ]
        
        start_x = 30
        for label, color in legend_items:
            box_rect = pygame.Rect(start_x, HEIGHT - 50, 14, 14)
            pygame.draw.rect(surface, color, box_rect, border_radius=2)
            lbl_surf = FONT_SMALL.render(label, True, COLOR_SUBTEXT)
            surface.blit(lbl_surf, (start_x + 20, HEIGHT - 52))
            start_x += 180

        # 4. Dibujar Barra de Controles Inferior
        controls_text = "Controles: [ESPACIO] Pausa/Reanudar | [FLECHA DER] Paso a Paso | [R] Reiniciar | [FLECHAS ARRIBA/ABAJO] Velocidad FPS"
        controls_surf = FONT_SMALL.render(controls_text, True, COLOR_TEXT)
        fps_surf = FONT_SMALL.render(f"Velocidad: {self.fps} FPS", True, COLOR_SUBTEXT)
        
        surface.blit(controls_surf, (30, HEIGHT - 25))
        surface.blit(fps_surf, (WIDTH - 150, HEIGHT - 25))


# ------------------------------------------------------------------------------
# Bucle Principal de la Aplicación Pygame
# ------------------------------------------------------------------------------
def main():
    clock = pygame.time.Clock()
    visualizer = MergeSortVisualizer(num_elements=60)

    running = True
    while running:
        # Control del ratio de refresco según los FPS configurados
        clock.tick(visualizer.fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    visualizer.is_paused = not visualizer.is_paused
                    if visualizer.is_paused:
                        visualizer.status_message = "Pausado. Presiona ESPACIO para reanudar."
                    else:
                        visualizer.status_message = "Ejecutando ordenamiento..."

                elif event.key == pygame.K_RIGHT:
                    visualizer.is_paused = True
                    visualizer.step()

                elif event.key == pygame.K_r:
                    visualizer.reset_array()

                elif event.key == pygame.K_UP:
                    visualizer.fps = min(120, visualizer.fps + 5)

                elif event.key == pygame.K_DOWN:
                    visualizer.fps = max(1, visualizer.fps - 5)

        # Actualizar estado de animación
        visualizer.update()

        # Renderizar gráfico
        visualizer.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()