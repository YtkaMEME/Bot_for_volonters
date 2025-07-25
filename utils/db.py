import aiosqlite
from pathlib import Path
from typing import Union, Optional, Dict, Any

class AsyncDB:
    def __init__(self, db_path: Union[str, Path]):
        self.db_path = db_path
        self.conn: Optional[aiosqlite.Connection] = None

    async def connect(self):
        if self.conn is None:
            self.conn = await aiosqlite.connect(self.db_path)
            await self.create_table()

    async def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS user_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            username TEXT,
            name TEXT,
            direction TEXT,
            step TEXT,
            photo_checkin TEXT,
            date TEXT,
            time_checkin TEXT,
            checkin_datetime TEXT
        )
        """
        await self.conn.execute(query)
        await self.conn.commit()

    async def get_state(self, user_id: str) -> Optional[tuple]:
        await self.connect()
        query = "SELECT * FROM user_states WHERE user_id = ?"
        async with self.conn.execute(query, (user_id,)) as cursor:
            result = await cursor.fetchone()
        return result

    async def save_state(self, user_id: str, data: Dict[str, Any]):
        await self.connect()
        existing = await self.get_state(user_id)
        if existing:
            query = """
            UPDATE user_states SET
                username = ?,
                name = ?,
                direction = ?,
                step = ?,
                photo_checkin = ?,
                date = ?,
                time_checkin = ?,
                checkin_datetime = ?
            WHERE user_id = ?
            """
            await self.conn.execute(query, (
                data.get("username"),
                data.get("name"),
                data.get("direction"),
                data.get("step"),
                data.get("photo_checkin"),
                data.get("date"),
                data.get("time_checkin"),
                data.get("checkin_datetime"),
                user_id
            ))
        else:
            query = """
            INSERT INTO user_states (
                user_id, username, name, direction, step,
                photo_checkin, date, time_checkin, checkin_datetime
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            await self.conn.execute(query, (
                user_id,
                data.get("username"),
                data.get("name"),
                data.get("direction"),
                data.get("step"),
                data.get("photo_checkin"),
                data.get("date"),
                data.get("time_checkin"),
                data.get("checkin_datetime")
            ))
        await self.conn.commit()

    async def delete_state(self, user_id: str):
        await self.connect()
        await self.conn.execute("DELETE FROM user_states WHERE user_id = ?", (user_id,))
        await self.conn.commit()

    async def get_all_states(self):
        await self.connect()
        async with self.conn.execute("SELECT * FROM user_states") as cursor:
            return await cursor.fetchall()

    async def close(self):
        if self.conn:
            await self.conn.close()
            self.conn = None