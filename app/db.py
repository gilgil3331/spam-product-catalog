import psycopg2
import psycopg2.extras
from flask import g, current_app
from app.logger import get_logger

logger = get_logger(__name__)


def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(current_app.config["DATABASE_URL"])
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query(sql, params=()):
    """SELECT — params always sent separately from SQL. (DB-3)"""
    conn = get_db()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def execute(sql, params=()):
    """INSERT/UPDATE/DELETE — params always sent separately from SQL. (DB-3)"""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, params)
    conn.commit()
