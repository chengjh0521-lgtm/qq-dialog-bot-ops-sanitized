"""信息部门：对用户数据、行情元数据与不透明信号进行持久化。"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from public_reference.contracts import ManualOperationIn, MinuteBarIn, OpaqueSignalIn, PositionOut


class InformationRepository:
    def __init__(self, database: Path = Path("runtime/operations.db")) -> None:
        database.parent.mkdir(parents=True, exist_ok=True)
        self.database = database
        self._initialize()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database)
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS minute_bars (
                    instrument TEXT NOT NULL, observed_at TEXT NOT NULL, close TEXT NOT NULL,
                    PRIMARY KEY (instrument, observed_at)
                );
                CREATE TABLE IF NOT EXISTS opaque_signals (
                    signal_id TEXT PRIMARY KEY, produced_at TEXT NOT NULL, payload_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS operations (
                    id INTEGER PRIMARY KEY, user_id TEXT NOT NULL, occurred_at TEXT NOT NULL,
                    side TEXT NOT NULL, quantity INTEGER NOT NULL, price TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS positions (
                    user_id TEXT NOT NULL, instrument TEXT NOT NULL, quantity INTEGER NOT NULL,
                    updated_at TEXT NOT NULL, PRIMARY KEY (user_id, instrument)
                );
                """
            )

    def save_minute_bar(self, bar: MinuteBarIn) -> None:
        with self._connection() as conn:
            conn.execute("INSERT OR REPLACE INTO minute_bars VALUES (?, ?, ?)", (bar.instrument, bar.observed_at.isoformat(), str(bar.close)))

    def store_opaque_signal(self, signal: OpaqueSignalIn) -> None:
        with self._connection() as conn:
            conn.execute("INSERT OR REPLACE INTO opaque_signals VALUES (?, ?, ?)", (signal.signal_id, signal.produced_at.isoformat(), json.dumps(signal.payload)))

    def record_operation(self, user_id: str, instrument: str, operation: ManualOperationIn) -> PositionOut:
        delta = operation.quantity if operation.side == "BUY" else -operation.quantity
        now = datetime.now(timezone.utc).isoformat()
        with self._connection() as conn:
            conn.execute("INSERT INTO operations (user_id, occurred_at, side, quantity, price) VALUES (?, ?, ?, ?, ?)", (user_id, operation.occurred_at.isoformat(), operation.side, operation.quantity, str(operation.price)))
            existing = conn.execute("SELECT quantity FROM positions WHERE user_id = ? AND instrument = ?", (user_id, instrument)).fetchone()
            quantity = (existing[0] if existing else 0) + delta
            if quantity < 0:
                raise ValueError("insufficient position")
            conn.execute("INSERT OR REPLACE INTO positions VALUES (?, ?, ?, ?)", (user_id, instrument, quantity, now))
        return PositionOut(user_id=user_id, instrument=instrument, quantity=quantity, updated_at=datetime.fromisoformat(now))

    def get_position(self, user_id: str, instrument: str) -> PositionOut:
        with self._connection() as conn:
            row = conn.execute("SELECT quantity, updated_at FROM positions WHERE user_id = ? AND instrument = ?", (user_id, instrument)).fetchone()
        if not row:
            return PositionOut(user_id=user_id, instrument=instrument, quantity=0, updated_at=datetime.fromtimestamp(0, tz=timezone.utc))
        return PositionOut(user_id=user_id, instrument=instrument, quantity=row[0], updated_at=datetime.fromisoformat(row[1]))
