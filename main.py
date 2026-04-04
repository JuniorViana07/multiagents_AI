# main.py — Ponto de entrada, loop principal Pygame

import pygame
import sys

# Inicializa o pygame
pygame.init()

# Configurações da tela
largura = 800
altura = 600
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Loop Principal")

# Controle de FPS
clock = pygame.time.Clock()

# Variável de controle
rodando = True

# Loop principal
while rodando:
    # 1. Captura de eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    # 2. Atualização (lógica do jogo)
    # Aqui você atualiza posições, física, etc.

    # 3. Renderização (desenho na tela)
    tela.fill((0, 0, 0))  # limpa a tela com preto

    # Exemplo: desenhar algo
    pygame.draw.circle(tela, (255, 0, 0), (400, 300), 50)

    # Atualiza a tela
    pygame.display.flip()

    # Define FPS (ex: 60)
    clock.tick(60)

# Finaliza o pygame
pygame.quit()
sys.exit()