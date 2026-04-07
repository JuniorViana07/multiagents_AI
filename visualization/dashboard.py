# dashboard.py - Painel lateral com metricas e logs

import pygame


def _format_ratio(value):
    if value is None:
        return "N/A"
    return f"{value:.2f}"


def draw_metrics_panel(screen, metrics, position=(10, 10)):
    panel_width = 320
    panel_height = 170
    panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel_surface.fill((20, 20, 20, 180))
    screen.blit(panel_surface, position)

    font_title = pygame.font.SysFont("consolas", 18, bold=True)
    font_text = pygame.font.SysFont("consolas", 16)

    title = font_title.render("Rescuer Efficiency", True, (255, 255, 255))
    screen.blit(title, (position[0] + 10, position[1] + 8))

    base_y = position[1] + 38
    gap = 62
    best = metrics.get("best_rescuer")

    for idx, key in enumerate(("sequential", "optimizer")):
        item = metrics[key]
        is_best = best == key
        color = (120, 255, 140) if is_best else (230, 230, 230)
        y = base_y + (idx * gap)

        line1 = font_text.render(item["name"], True, color)
        line2 = font_text.render(f"Steps: {item['steps']} | Victims: {item['victims']}", True, color)
        line3 = font_text.render(
            f"Efficiency (steps/victim): {_format_ratio(item['ratio'])}",
            True,
            color,
        )

        screen.blit(line1, (position[0] + 10, y))
        screen.blit(line2, (position[0] + 10, y + 20))
        screen.blit(line3, (position[0] + 10, y + 40))
