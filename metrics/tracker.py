# tracker.py - Coleta e comparacao de metricas de desempenho

from typing import Any


class MetricsTracker:
    def _build_rescuer_metrics(self, name: str, rescuer: Any) -> dict:
        steps = getattr(rescuer, "steps_taken", 0)
        victims = getattr(rescuer, "victims_rescued", 0)
        ratio = (steps / victims) if victims > 0 else None
        return {
            "name": name,
            "steps": steps,
            "victims": victims,
            "ratio": ratio,
        }

    def snapshot(self, sequential, optimizer) -> dict:
        metrics = {
            "sequential": self._build_rescuer_metrics("Sequential", sequential),
            "optimizer": self._build_rescuer_metrics("Optimizer", optimizer),
        }

        seq_ratio = metrics["sequential"]["ratio"]
        opt_ratio = metrics["optimizer"]["ratio"]
        best_rescuer = None
        if seq_ratio is not None and opt_ratio is not None:
            best_rescuer = "sequential" if seq_ratio <= opt_ratio else "optimizer"

        metrics["best_rescuer"] = best_rescuer
        return metrics
