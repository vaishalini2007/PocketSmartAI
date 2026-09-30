import json
from app.database import get_db

def save_history(user_id, planner, input_data, result):
    with get_db() as db:
        db.execute("INSERT INTO history(user_id,planner,input_json,result_json) VALUES(?,?,?,?)",(user_id,planner,json.dumps(input_data),result.model_dump_json()))

def get_history(user_id, limit=30):
    with get_db() as db:
        rows=db.execute("SELECT id,planner,input_json,result_json,created_at FROM history WHERE user_id=? ORDER BY id DESC LIMIT ?",(user_id,limit)).fetchall()
    return [dict(r) for r in rows]
