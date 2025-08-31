from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="Log Server API Section", version="0.1")

@app.get("/")
def root():
    return {"message": "Server API is running now!"}

class APILog(BaseModel):
    log_type: str
    log_message: str
    hostname: Optional[str] = None
    created_at: Optional[datetime] = None

LogItem = APILog

_STORE: List[dict] = [
    {
        "log_type": "INFO",
        "log_message": "API server started",
        "hostname": "local-api",
        "created_at": datetime.utcnow()
    }
]

@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.utcnow()}

@app.get("/api/logs", response_model=List[LogItem])
def get_logs():
    return _STORE

@app.get("/api/logs_wrapped")
def get_logs_wrapped():
    return {"data": _STORE}

@app.post("/api/logs")
def post_logs(items: List[APILog]):
    level = 0
    for item in items:
        d = item.dict()
        if d.get("created_at") is None:
            d["created_at"] = datetime.utcnow()
        _STORE.append(d)
        level += 1
    return {"inserted": level}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="127.0.0.1", port=8000, reload=True) #default local