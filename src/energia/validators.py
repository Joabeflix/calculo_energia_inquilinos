from typing import Any

from energia.exceptions import ValidationError


def to_float(value: Any, field_name: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"O campo '{field_name}' deve ser numerico.") from exc


def validate_non_negative(value: float, field_name: str) -> float:
    if value < 0:
        raise ValidationError(f"O campo '{field_name}' nao pode ser negativo.")
    return value


def validate_meter_readings(previous: Any, current: Any) -> tuple[float, float]:
    previous_value = validate_non_negative(to_float(previous, "consumo_anterior"), "consumo_anterior")
    current_value = validate_non_negative(to_float(current, "consumo_atual"), "consumo_atual")
    if current_value < previous_value:
        raise ValidationError("A leitura atual nao pode ser menor que a leitura anterior.")
    return previous_value, current_value


def validate_name(name: Any) -> str:
    normalized = str(name).strip()
    if not normalized:
        raise ValidationError("O nome do inquilino nao pode ser vazio.")
    return normalized
