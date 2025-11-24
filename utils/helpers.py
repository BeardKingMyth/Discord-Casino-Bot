import asyncpg
from datetime import datetime
from dotenv import load_dotenv
import os


# ----------------- DATABASE CONNECTION -----------------
load_dotenv()  # loads .env variables
DB_DSN = os.getenv("SUPABASE_DB_URL")
if not DB_DSN:
    raise ValueError("SUPABASE_DB_URL env var is not set!")

async def get_connection():
    return await asyncpg.connect(dsn=DB_DSN)

# ----------------- INITIALIZATION -----------------
async def init_db():
    conn = await get_connection()
    # Balances table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS balances (
            user_id TEXT PRIMARY KEY,
            balance BIGINT NOT NULL
        )
    """)
    # Daily claims table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS daily_claims (
            user_id TEXT PRIMARY KEY,
            last_claim TIMESTAMP
        )
    """)
    # User status table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS user_status (
            user_id TEXT PRIMARY KEY,
            frozen BOOLEAN DEFAULT FALSE,
            banned BOOLEAN DEFAULT FALSE
        )
    """)
    await conn.close()

# ----------------- BALANCES -----------------
async def load_balances() -> dict:
    conn = await get_connection()
    rows = await conn.fetch("SELECT user_id, balance FROM balances")
    await conn.close()
    return {row["user_id"]: row["balance"] for row in rows}

async def save_balances(balances: dict):
    conn = await get_connection()
    for user_id, balance in balances.items():
        await conn.execute("""
            INSERT INTO balances(user_id, balance)
            VALUES($1, $2)
            ON CONFLICT(user_id) DO UPDATE SET balance=EXCLUDED.balance
        """, user_id, balance)
    await conn.close()

async def get_balance(user_id: str) -> int:
    conn = await get_connection()
    row = await conn.fetchrow("SELECT balance FROM balances WHERE user_id=$1", user_id)
    await conn.close()
    return row["balance"] if row else 0

async def set_balance(user_id: str, amount: int):
    conn = await get_connection()
    await conn.execute("""
        INSERT INTO balances(user_id, balance)
        VALUES($1, $2)
        ON CONFLICT(user_id) DO UPDATE SET balance=EXCLUDED.balance
    """, user_id, amount)
    await conn.close()

# ----------------- DAILY CLAIMS -----------------
async def load_claims() -> dict:
    conn = await get_connection()
    rows = await conn.fetch("SELECT user_id, last_claim FROM daily_claims")
    await conn.close()
    claims = {}
    for row in rows:
        claims[row["user_id"]] = row["last_claim"] if row["last_claim"] else None
    return claims

async def save_claims(claims: dict):
    conn = await get_connection()
    for user_id, last_claim in claims.items():
        await conn.execute("""
            INSERT INTO daily_claims(user_id, last_claim)
            VALUES($1, $2)
            ON CONFLICT(user_id) DO UPDATE SET last_claim=EXCLUDED.last_claim
        """, user_id, last_claim)
    await conn.close()

async def get_last_claim(user_id: str):
    conn = await get_connection()
    row = await conn.fetchrow("SELECT last_claim FROM daily_claims WHERE user_id=$1", user_id)
    await conn.close()
    return row["last_claim"] if row and row["last_claim"] else None

async def set_last_claim(user_id: str, claim_time: datetime):
    conn = await get_connection()
    await conn.execute("""
        INSERT INTO daily_claims(user_id, last_claim)
        VALUES($1, $2)
        ON CONFLICT(user_id) DO UPDATE SET last_claim=EXCLUDED.last_claim
    """, user_id, claim_time)
    await conn.close()

# ----------------- USER STATUS -----------------
async def is_user_frozen(user_id: str) -> bool:
    conn = await get_connection()
    row = await conn.fetchrow("SELECT frozen FROM user_status WHERE user_id=$1", user_id)
    await conn.close()
    return bool(row["frozen"]) if row else False

async def is_user_banned(user_id: str) -> bool:
    conn = await get_connection()
    row = await conn.fetchrow("SELECT banned FROM user_status WHERE user_id=$1", user_id)
    await conn.close()
    return bool(row["banned"]) if row else False

async def set_user_frozen(user_id: str, frozen: bool):
    conn = await get_connection()
    await conn.execute("""
        INSERT INTO user_status(user_id, frozen)
        VALUES($1, $2)
        ON CONFLICT(user_id) DO UPDATE SET frozen=EXCLUDED.frozen
    """, user_id, frozen)
    await conn.close()

async def set_user_banned(user_id: str, banned: bool):
    conn = await get_connection()
    await conn.execute("""
        INSERT INTO user_status(user_id, banned)
        VALUES($1, $2)
        ON CONFLICT(user_id) DO UPDATE SET banned=EXCLUDED.banned
    """, user_id, banned)
    await conn.close()
