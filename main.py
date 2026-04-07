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
agent_service = AgentService()
hospital = Hospital(GRID_SIZE//2, GRID_SIZE//2)
# Inicializando agentes
drone1 = Drone(id=1, pos_x=5, pos_y=5, view_range=2)
commander = Commander(id=2, grid_size=GRID_SIZE)
fire_fighter = Firefighter(id=3, pos_x=3, pos_y=3, quadrant=1)
fire_fighter2 = Firefighter(id=6, pos_x=3, pos_y=16, quadrant=3)
fire_fighter3 = Firefighter(id=7, pos_x=16, pos_y=3, quadrant=2)
fire_fighter4 = Firefighter(id=8, pos_x=16, pos_y=16, quadrant=4)
rescuer = RescuerSequential(id=4, pos_x=15, pos_y=15, hospital_pos=hospital.get_position())
rescuer_optimizer = RescuerOptimizer(id=5, pos_x=10, pos_y=10, hospital_pos=hospital.get_position())
commander.register_firefighter(1, fire_fighter)
commander.register_firefighter(2, fire_fighter3)
commander.register_firefighter(3, fire_fighter2)
commander.register_firefighter(4, fire_fighter4)
commander.register_rescuers(rescuer_optimizer) 
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

    # update nos bombeiros:
    #result = fire_fighter.update(service)
    #if result is not None:
    #    commander.register_extinguished_fire(result)
    #
    #result = fire_fighter2.update(service)
    #if result is not None:
    #    commander.register_extinguished_fire(result)

    #result = fire_fighter3.update(service)
    #if result is not None:
    #    commander.register_extinguished_fire(result)

    #result = fire_fighter4.update(service)
    #if result is not None:
    #    commander.register_extinguished_fire(result)

    # Campo de visão do drone
    drone1.patrol(grid)
    visible_cells = drone1.perceive_environment(grid)
    agent_service.send_message(drone1, commander, visible_cells)
    commander.update(service)
    #print(commander.desires.get("fire_to_extinguish"))
    #print(commander.beliefs)
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

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


    # if commander.intentions.get("fire_to_extinguish"):
    #     agent_service.send_message(commander, fire_fighter, commander.intentions.get("fire_to_extinguish")[0])
    # if commander.intentions.get("victims_to_save"):
    #     agent_service.send_message(commander, rescuer, commander.intentions.get("victims_to_save"))
    # if commander.intentions.get("victims_to_save"):
    #     agent_service.send_message(commander, rescuer_optimizer, commander.intentions.get("victims_to_save"))

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
 
    #print(f'1:{fire_fighter.state} 2:{fire_fighter2.state}')
    #print(f'1:{fire_fighter.target} 2:{fire_fighter2.target}')
    #print(f'3:{fire_fighter3.state}')
    #print(f'3:{fire_fighter3.target}')
    #print(commander.victims_saved)
    print(f"Rescuer: {rescuer.rescue_queue}")
    print(f"Rescuer Optimizer: {rescuer_optimizer.rescue_queue}")

    #print()
    # rescuer.update(service)
    # print(rescuer.status)
    # print(rescuer.rescue_queue)
    #print(rescuer.victims_rescued)
    #print(commander.desires.get("victims_to_save"))
    #print(commander.desires.get("fire_to_extinguish"))
    #if rescuer.current_target is not None:
        #print(rescuer.current_target[0], rescuer.current_target[1])

    # socorrista otimizado
    metrics = metrics_tracker.snapshot(rescuer, rescuer_optimizer)
    draw_metrics_panel(screen, metrics, position=(10, 10))


    pygame.display.flip()
    clock.tick(5)  # FPS mais baixo pra ver a simulação

pygame.quit()
sys.exit()
