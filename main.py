import pygame
import sys

from agents import agentService, commander, firefighter, rescuer_sequential
from environment.hospital import Hospital
from environment.cell import CellState
from environment.city_grid import CityGrid
from environment.city_grid_service import CityGridService  # ajuste o nome se necessário
from agents.agentService import AgentService
from agents.drone import Drone
from agents.commander import Commander
from agents.firefighter import Firefighter
from agents.rescuer_sequential import RescuerSequential
from agents.rescuer_optimizer import RescuerOptimizer
from metrics.tracker import MetricsTracker
from visualization.dashboard import draw_metrics_panel
from config import (
    GRID_SIZE,
    CELL_SIZE,
    FPS,
    EVENT_PROBABILITY,
    normalized_event_weights,
    validated_active_rescuer,
)


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

#funções auxiliares
def _scaled_coord(ratio: float) -> int:
    value = int(round((GRID_SIZE - 1) * ratio))
    return max(0, min(GRID_SIZE - 1, value))


def _scaled_pos(x_ratio: float, y_ratio: float) -> tuple[int, int]:
    return (_scaled_coord(x_ratio), _scaled_coord(y_ratio))

# Instânciando
grid = CityGrid(GRID_SIZE)
fire_w, victim_w, fire_victim_w = normalized_event_weights()
service = CityGridService(
    grid,
    event_probability=EVENT_PROBABILITY,
    fire_probability=fire_w,
    victim_probability=victim_w,
    fire_victim_probability=fire_victim_w,
)
agent_service = AgentService()
hospital = Hospital(GRID_SIZE//2, GRID_SIZE//2)

# Inicializando agentes
drone_x, drone_y = _scaled_pos(0.25, 0.25)
drone1 = Drone(id=1, pos_x=drone_x, pos_y=drone_y, view_range=2)
commander = Commander(id=2, grid_size=GRID_SIZE)
ff1_x, ff1_y = _scaled_pos(0.15, 0.15)
ff2_x, ff2_y = _scaled_pos(0.15, 0.80)
ff3_x, ff3_y = _scaled_pos(0.80, 0.15)
ff4_x, ff4_y = _scaled_pos(0.80, 0.80)
resc_seq_x, resc_seq_y = _scaled_pos(0.75, 0.75)
resc_opt_x, resc_opt_y = _scaled_pos(0.50, 0.50)

fire_fighter = Firefighter(id=3, pos_x=ff1_x, pos_y=ff1_y, quadrant=1)
fire_fighter2 = Firefighter(id=6, pos_x=ff2_x, pos_y=ff2_y, quadrant=3)
fire_fighter3 = Firefighter(id=7, pos_x=ff3_x, pos_y=ff3_y, quadrant=2)
fire_fighter4 = Firefighter(id=8, pos_x=ff4_x, pos_y=ff4_y, quadrant=4)
rescuer = RescuerSequential(id=4, pos_x=resc_seq_x, pos_y=resc_seq_y, hospital_pos=hospital.get_position())
rescuer_optimizer = RescuerOptimizer(id=5, pos_x=resc_opt_x, pos_y=resc_opt_y, hospital_pos=hospital.get_position())
commander.register_drones(drone1)
commander.register_firefighter(1, fire_fighter)
commander.register_firefighter(2, fire_fighter3)
commander.register_firefighter(3, fire_fighter2)
commander.register_firefighter(4, fire_fighter4)
commander.register_rescuers(rescuer, rescuer_optimizer)
commander.set_active_rescuer(validated_active_rescuer())
metrics_tracker = MetricsTracker()

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

    # Desenha a grid
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

    ### Desenhando agentes
    # Hospital
    hx, hy = hospital.get_position()
    center_x = hx * CELL_SIZE + CELL_SIZE // 2
    center_y = hy * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(
        screen,
        (0, 255, 0),  # verde
        (center_x, center_y), # posição central
        CELL_SIZE // 3 # raio do círculo
    )

    # Drone
    dx, dy = drone1.get_position()

    center_x = dx * CELL_SIZE + CELL_SIZE // 2
    center_y = dy * CELL_SIZE + CELL_SIZE // 2

    pygame.draw.circle(
        screen,
        (255, 255, 0),  # amarelo
        (center_x, center_y), # posição central
        CELL_SIZE // 3 # raio do círculo
    )
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for drone in commander.drones.values():
        visible_cells = drone.perceive_environment(grid)
        for x, y, _ in visible_cells:
            rect = pygame.Rect(
                x * CELL_SIZE,
                y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
            pygame.draw.rect(overlay, (255, 255, 0, 50), rect)

    screen.blit(overlay, (0, 0))

    # Bombeiro
    fx, fy = fire_fighter.get_position()
    center_x = fx * CELL_SIZE + CELL_SIZE // 2
    center_y = fy * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(
        screen,
        (0, 255, 255),  # ciano
        (center_x, center_y), # posição central
        CELL_SIZE // 3 # raio do círculo
    )

    # Bombeiro 2
    fx, fy = fire_fighter2.get_position()
    center_x = fx * CELL_SIZE + CELL_SIZE // 2
    center_y = fy * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(
        screen,
        (0, 255, 255),  # ciano
        (center_x, center_y), # posição central
        CELL_SIZE // 3 # raio do círculo
    )


    # Bombeiro 3
    fx, fy = fire_fighter3.get_position()
    center_x = fx * CELL_SIZE + CELL_SIZE // 2
    center_y = fy * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(
        screen,
        (0, 255, 255),  # ciano
        (center_x, center_y), # posição central
        CELL_SIZE // 3 # raio do círculo
    )

    # Bombeiro 4
    fx, fy = fire_fighter4.get_position()
    center_x = fx * CELL_SIZE + CELL_SIZE // 2
    center_y = fy * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(
        screen,
        (0, 255, 255),  # ciano
        (center_x, center_y), # posição central
        CELL_SIZE // 3 # raio do círculo
    )

    # Socorrista
    rx, ry = rescuer.get_position()
    center_x = rx * CELL_SIZE + CELL_SIZE // 2
    center_y = ry * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(
        screen,
        (255, 0, 255),  # magenta
        (center_x, center_y), # posição central
        CELL_SIZE // 3 # raio do círculo
    )

    # Otimizador
    rox, roy = rescuer_optimizer.get_position()
    center_x = rox * CELL_SIZE + CELL_SIZE // 2
    center_y = roy * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(
        screen,
        (255, 165, 0),  # laranja
        (center_x, center_y), # posição central
        CELL_SIZE // 3 # raio do círculo
    )

    #funcionamento dos agentes
    commander.update(service)
    metrics = metrics_tracker.snapshot(rescuer, rescuer_optimizer)
    draw_metrics_panel(screen, metrics, position=(10, 10))


    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
