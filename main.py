import pygame
import sys

from environment.cell import CellState
from environment.city_grid import CityGrid
from environment.city_grid_service import CityGridService  # ajuste o nome se necessário

# Configurações
GRID_SIZE = 20
CELL_SIZE = 30
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE

# Cores
COLORS = {
    CellState.NORMAL: (255, 255, 255),
    CellState.FIRE: (255, 0, 0),
    CellState.VICTIM: (0, 0, 255),
    CellState.FIRE_AND_VICTIM: (128, 0, 128),
    CellState.HOSPITAL: (0, 255, 0)
}

# Inicialização
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("City Grid Simulation")
clock = pygame.time.Clock()

# Instâncias
grid = CityGrid(GRID_SIZE)
service = CityGridService(grid)

# Loop principal
running = True
while running:
    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Clique do mouse para interagir
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            x = mx // CELL_SIZE
            y = my // CELL_SIZE

            # Botão esquerdo → fogo
            if event.button == 1:
                service.spawn_fire(x, y)
            # Botão direito → vítima
            elif event.button == 3:
                service.spawn_victim(x, y)

    # Atualização automática
    service.update()

    # Desenho
    screen.fill((0, 0, 0))

    for y in range(grid.get_size()):
        for x in range(grid.get_size()):
            state = grid.get_cell_state(x, y)
            color = COLORS[state]

            rect = pygame.Rect(
                x * CELL_SIZE,
                y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (50, 50, 50), rect, 1)  # grid

    pygame.display.flip()
    clock.tick(10)  # FPS mais baixo pra ver a simulação

pygame.quit()
sys.exit()