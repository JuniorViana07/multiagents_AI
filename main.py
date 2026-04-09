from turtle import heading

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
#COLORS = {
#    CellState.NORMAL: (255, 255, 255),
#    CellState.FIRE: (255, 0, 0),
#    CellState.VICTIM: (0, 0, 255),
#    CellState.FIRE_AND_VICTIM: (128, 0, 128),
#    CellState.HOSPITAL: (0, 255, 0)
#}

# Emojis dos eventos:
EMOJIS = {
    CellState.FIRE: "🔥",
    CellState.VICTIM: "❤️",
    CellState.FIRE_AND_VICTIM: "❤️‍🔥",
}
# Inicialização
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("City Grid Simulation")
clock = pygame.time.Clock()

# Emojis
emoji_font = pygame.font.SysFont("Segoe UI Emoji", CELL_SIZE)

#funções auxiliares
def _scaled_coord(ratio: float) -> int:
    value = int(round((GRID_SIZE - 1) * ratio))
    return max(0, min(GRID_SIZE - 1, value))


def _scaled_pos(x_ratio: float, y_ratio: float) -> tuple[int, int]:
    return (_scaled_coord(x_ratio), _scaled_coord(y_ratio))

def draw_emoji(screen, emoji, grid_x, grid_y):
    center_x = grid_x * CELL_SIZE + CELL_SIZE // 2
    center_y = grid_y * CELL_SIZE + CELL_SIZE // 2

    surface = emoji_font.render(emoji, True, (255, 255, 255))
    rect = surface.get_rect(center=(center_x, center_y))

    screen.blit(surface, rect)

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
rescuer = RescuerSequential(id=4, pos_x=hospital.get_position()[0], pos_y=hospital.get_position()[1], hospital_pos=hospital.get_position())
rescuer_optimizer = RescuerOptimizer(id=5, pos_x=hospital.get_position()[0], pos_y=hospital.get_position()[1], hospital_pos=hospital.get_position())
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
            rect = pygame.Rect(
                    x * CELL_SIZE,
                    y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
            if state != CellState.NORMAL:
                emoji = EMOJIS[state]
                pygame.draw.rect(screen, (255, 255, 255), rect)
                draw_emoji(screen, emoji, x, y)
            else:
                pygame.draw.rect(screen, (255, 255, 255), rect)
            #pygame.draw.rect(screen, color, rect)
            #pygame.draw.rect(screen, (50, 50, 50), rect, 1)  # grid

    ### Desenhando agentes
    # Drone
    dx, dy = drone1.get_position()
    surface = emoji_font.render("🚁", True, (255,255,255))
    if drone1.heading == "right":
        surface = pygame.transform.flip(surface, True, False)
    screen.blit(surface, (dx * CELL_SIZE, dy * CELL_SIZE))    
    #draw_emoji(screen, "🚁", dx, dy)

    # Overlay (mantém igual)
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

    # Bombeiros
    for ff in [fire_fighter, fire_fighter2, fire_fighter3, fire_fighter4]:
        fx, fy = ff.get_position()
        draw_emoji(screen, "🧑‍🚒", fx, fy)

    # Socorrista
    rx, ry = rescuer.get_position()
    draw_emoji(screen, "⛑️", rx, ry)

    # Otimizador
    rox, roy = rescuer_optimizer.get_position()
    surface = emoji_font.render("🚑", True, (255,255,255))

    if rescuer_optimizer.heading == "right":
        surface = pygame.transform.flip(surface, True, False)
    screen.blit(surface, (rox * CELL_SIZE, roy * CELL_SIZE))

    # Hospital
    hx, hy = hospital.get_position()
    rect = pygame.Rect(
                hx * CELL_SIZE,
                hy * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
    pygame.draw.rect(screen, (255, 255, 255), rect)
    draw_emoji(screen, "🏥", hx, hy)

    #funcionamento dos agentes
    commander.update(service)
    metrics = metrics_tracker.snapshot(rescuer, rescuer_optimizer)
    draw_metrics_panel(screen, metrics, position=(10, 10))


    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
