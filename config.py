# config.py - Configuracoes globais da simulacao

GRID_SIZE = 20
CELL_SIZE = 30
FPS = 5

EVENT_PROBABILITY = 0.05
FIRE_PROBABILITY = 0.4
VICTIM_PROBABILITY = 0.4
FIRE_VICTIM_PROBABILITY = 0.2

# Escolha fixa por execucao: "sequential", "optimizer" ou "both"
ACTIVE_RESCUER = "both"


def _clamp_non_negative(value: float) -> float:
    return max(0.0, float(value))


def normalized_event_weights() -> tuple[float, float, float]:
    fire = _clamp_non_negative(FIRE_PROBABILITY)
    victim = _clamp_non_negative(VICTIM_PROBABILITY)
    fire_victim = _clamp_non_negative(FIRE_VICTIM_PROBABILITY)
    total = fire + victim + fire_victim

    if total <= 0:
        return (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)

    return (fire / total, victim / total, fire_victim / total)


def validated_active_rescuer() -> str:
    mode = str(ACTIVE_RESCUER).strip().lower()
    if mode not in ("sequential", "optimizer", "both"):
        return "optimizer"
    return mode
