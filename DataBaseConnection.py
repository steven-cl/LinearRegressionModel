import sqlite3
from pathlib import Path
from typing import Optional, Tuple, Any
from difflib import SequenceMatcher
import json

DB_PATH = Path(__file__).with_name("regressionModel.db")

def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)

def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_closest_model(target_name: str) -> Optional[Tuple[int, str]]:
    """"
    Devuelve (id, model_name) del nombre más parecido a target_name.
    """
    if not target_name:
        return None
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, model_name FROM regression_model")
        rows = cur.fetchall()
    if not rows:
        return None
    best_row = None
    best_score = -1.0
    for mid, mname in rows:
        score = _similarity(target_name, mname)
        if score > best_score:
            best_score = score
            best_row = (mid, mname)
    return best_row

def get_xy_by_id(model_id: int) -> Optional[Tuple[Any, Any]]:
    """
    Devuelve (x, y) para el id dado. Intenta parsear JSON; si falla devuelve texto crudo.
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT x, y FROM regression_model WHERE id = ?", (model_id,))
        row = cur.fetchone()
    if not row:
        return None
    x_text, y_text = row
    def _parse(value: str):
        try:
            return json.loads(value)
        except Exception:
            return value
    return _parse(x_text), _parse(y_text)

# Ejemplos de uso (eliminar si no se necesitan):
if __name__ == "__main__":
    print(find_closest_model("modelo prueba"))
    print(get_xy_by_id(1))