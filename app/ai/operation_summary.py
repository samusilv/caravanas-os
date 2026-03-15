"""AI-ready helpers for deterministic operational summaries in Spanish."""

from __future__ import annotations


def summarize_lot_validation(
    *,
    scanned_count: int,
    unknown_count: int,
    duplicate_count: int,
    missing_count: int,
) -> str:
    """Build a short Spanish summary from lot validation metrics."""
    duplicado_label = "duplicado" if duplicate_count == 1 else "duplicados"
    return (
        f"Se leyeron {scanned_count} animales, "
        f"hay {unknown_count} desconocidos, "
        f"{duplicate_count} {duplicado_label} "
        f"y faltan {missing_count} respecto al lote esperado."
    )
