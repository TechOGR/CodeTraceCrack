import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime

DB_NAME = "codes.db"
FULL_DB_PATH = Path.joinpath(Path.cwd(), "db", DB_NAME)

# Estados posibles para los códigos
STATUS_DISPONIBLE = "disponible"  # En stock y sin editar
STATUS_PENDIENTE = "pendiente"    # Pendiente a ser pedido
STATUS_PEDIDO = "pedido"          # Ya pedido, por bajar al picking
STATUS_ULTIMO = "ultimo"          # Últimos productos de ese código
STATUS_PERDIDO = "perdido"        # Caja perdida, no se encuentra
STATUS_NO_HAY_MAS = "no_hay_mas"  # Agotado, no hay más en stock

ALL_STATUSES = [STATUS_DISPONIBLE, STATUS_PENDIENTE, STATUS_PEDIDO, STATUS_ULTIMO, STATUS_PERDIDO, STATUS_NO_HAY_MAS]
STATUS_LABELS = {
    STATUS_DISPONIBLE: "Disponible",
    STATUS_PENDIENTE: "Pendiente",
    STATUS_PEDIDO: "Pedido",
    STATUS_ULTIMO: "Último",
    STATUS_PERDIDO: "Perdido",
    STATUS_NO_HAY_MAS: "No hay más",
}

class CodeRepository:
    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = Path(db_path) if db_path else Path(FULL_DB_PATH)
        try:
            if Path.exists(FULL_DB_PATH):
                self.db_path = Path(db_path) if db_path else Path(FULL_DB_PATH)
                self.conn = sqlite3.connect(str(self.db_path))
                self.conn.row_factory = sqlite3.Row
                self._init_db()
            else:
                Path.mkdir(FULL_DB_PATH.parent, parents=True, exist_ok=True)
                self.conn = sqlite3.connect(str(self.db_path))
                self.conn.row_factory = sqlite3.Row
                self._init_db()
                self.db_path = Path(db_path) if db_path else Path(FULL_DB_PATH)        
        except Exception as e:
            print(f"Error al conectar o inicializar la base de datos: {e}")
            raise
    
    def _init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                created_at TEXT NOT NULL,
                annotated INTEGER NOT NULL DEFAULT 0,
                duplicate INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'disponible'
            )
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_codes_code ON codes(code)")
        # Migrar tablas existentes agregando columna status si no existe
        try:
            cur.execute("ALTER TABLE codes ADD COLUMN status TEXT NOT NULL DEFAULT 'disponible'")
        except sqlite3.OperationalError:
            pass  # La columna ya existe
        self.conn.commit()

    def add_codes(self, codes: List[Tuple[str, bool, Optional[datetime], Optional[str]]]) -> None:
        cur = self.conn.cursor()
        for item in codes:
            code = item[0]
            annotated = item[1]
            created_at = item[2] if len(item) > 2 else None
            status = item[3] if len(item) > 3 else STATUS_DISPONIBLE
            cur.execute(
                "INSERT INTO codes(code, created_at, annotated, duplicate, status) VALUES (?, ?, ?, ?, ?)",
                (code, (created_at or datetime.utcnow()).isoformat(), int(annotated), 0, status or STATUS_DISPONIBLE),
            )
        self.conn.commit()
        self._refresh_duplicates()

    def list_codes(self,
                   annotated: Optional[bool] = None,
                   duplicates_only: Optional[bool] = None,
                   search: Optional[str] = None,
                   status: Optional[str] = None,
                   order_by: str = "created_at",
                   order_dir: str = "DESC") -> List[sqlite3.Row]:
        query = "SELECT id, code, created_at, annotated, duplicate, status FROM codes"
        conditions = []
        params: List[Any] = []

        if annotated is not None:
            conditions.append("annotated = ?")
            params.append(1 if annotated else 0)
        if duplicates_only:
            conditions.append("duplicate = 1")
        if search:
            conditions.append("code LIKE ?")
            params.append(f"%{search.upper()}%")
        if status:
            conditions.append("status = ?")
            params.append(status)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        allowed_order = {"created_at", "code", "annotated", "duplicate", "status"}
        if order_by not in allowed_order:
            order_by = "created_at"
        order_dir = "ASC" if order_dir.upper() == "ASC" else "DESC"
        query += f" ORDER BY {order_by} {order_dir}"

        cur = self.conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()

    def update_annotated(self, code_id: int, annotated: bool) -> None:
        cur = self.conn.cursor()
        cur.execute("UPDATE codes SET annotated = ? WHERE id = ?", (int(annotated), code_id))
        self.conn.commit()

    def update_status(self, code_id: int, status: str) -> None:
        cur = self.conn.cursor()
        cur.execute("UPDATE codes SET status = ? WHERE id = ?", (status, code_id))
        self.conn.commit()

    def update_code(self, code_id: int, code: str, annotated: Optional[bool] = None, status: Optional[str] = None) -> None:
        cur = self.conn.cursor()
        if annotated is None and status is None:
            cur.execute("UPDATE codes SET code = ? WHERE id = ?", (code, code_id))
        elif status is None:
            cur.execute("UPDATE codes SET code = ?, annotated = ? WHERE id = ?", (code, int(annotated), code_id))
        elif annotated is None:
            cur.execute("UPDATE codes SET code = ?, status = ? WHERE id = ?", (code, status, code_id))
        else:
            cur.execute("UPDATE codes SET code = ?, annotated = ?, status = ? WHERE id = ?", (code, int(annotated), status, code_id))
        self.conn.commit()
        self._refresh_duplicates()

    def delete_code(self, code_id: int) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM codes WHERE id = ?", (code_id,))
        self.conn.commit()
        self._refresh_duplicates()

    def remove_all(self) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM codes")
        self.conn.commit()
        self._refresh_duplicates()

    def _refresh_duplicates(self) -> None:
        cur = self.conn.cursor()
        cur.execute("UPDATE codes SET duplicate = 0")
        cur.execute(
            """
            UPDATE codes
            SET duplicate = 1
            WHERE code IN (
                SELECT code FROM codes GROUP BY code HAVING COUNT(*) > 1
            )
            """
        )
        self.conn.commit()

    def stats(self) -> Dict[str, int]:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) AS c FROM codes")
        total = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) AS c FROM codes WHERE annotated = 1")
        annotated = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) AS c FROM codes WHERE duplicate = 1")
        duplicates = cur.fetchone()["c"]
        # Stats por status
        status_counts = {}
        for st in ALL_STATUSES:
            cur.execute("SELECT COUNT(*) AS c FROM codes WHERE status = ?", (st,))
            status_counts[st] = cur.fetchone()["c"]
        return {"total": total, "annotated": annotated, "duplicates": duplicates, **status_counts}

    def get_all_codes_for_autocomplete(self) -> List[str]:
        """Retorna todos los códigos únicos para autocompletado."""
        cur = self.conn.cursor()
        cur.execute("SELECT DISTINCT code FROM codes ORDER BY code")
        return [row["code"] for row in cur.fetchall()]

    def search_codes_prefix(self, prefix: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Busca códigos que empiecen con el prefijo dado, retorna código y status."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT DISTINCT code, status FROM codes WHERE code LIKE ? ORDER BY code LIMIT ?",
            (f"{prefix.upper()}%", limit)
        )
        return [{"code": row["code"], "status": row["status"]} for row in cur.fetchall()]

    def codes_exist(self, codes: List[str]) -> List[str]:
        """Verifica cuáles códigos ya existen en la base de datos.
        Retorna lista de códigos que ya existen (duplicados)."""
        if not codes:
            return []
        cur = self.conn.cursor()
        placeholders = ",".join("?" * len(codes))
        cur.execute(
            f"SELECT DISTINCT code FROM codes WHERE code IN ({placeholders})",
            [c.upper() for c in codes]
        )
        return [row["code"] for row in cur.fetchall()]

    def get_codes_with_status(self, codes: List[str]) -> Dict[str, str]:
        """Retorna un diccionario {codigo: status} para los códigos que existen."""
        if not codes:
            return {}
        cur = self.conn.cursor()
        placeholders = ",".join("?" * len(codes))
        cur.execute(
            f"SELECT code, status FROM codes WHERE code IN ({placeholders})",
            [c.upper() for c in codes]
        )
        return {row["code"]: row["status"] for row in cur.fetchall()}

    def update_status_if_default(self, code: str, new_status: str) -> bool:
        """
        Actualiza el status de un código SOLO si su status actual es 'disponible'.
        Retorna True si se actualizó, False si no.
        """
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE codes SET status = ? WHERE code = ? AND status = ?",
            (new_status, code.upper(), STATUS_DISPONIBLE)
        )
        self.conn.commit()
        return cur.rowcount > 0
