# server/main.py
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import uvicorn

from auth import create_code, verify_code, create_session, get_email_by_token
from mailer import send_code

app = FastAPI()

_connections: dict[str, WebSocket] = {}


class EmailReq(BaseModel):
    email: str
    chat_id: str


class CodeReq(BaseModel):
    email: str
    code: str


@app.get("/")
def root():
    return {"status": "lemon messenger alive"}


@app.post("/auth/send-code")
def send_code_endpoint(req: EmailReq):
    email = req.email.strip().lower()
    chat_id = req.chat_id.strip()
    if "@" not in email:
        raise HTTPException(400, "bad email")
    if not chat_id:
        raise HTTPException(400, "chat_id required")

    code = create_code(email, chat_id)
    ok = send_code(chat_id, code)
    if not ok:
        raise HTTPException(500, "telegram send fail")
    return {"ok": True}


@app.post("/auth/verify")
def verify_endpoint(req: CodeReq):
    email = req.email.strip().lower()
    if not verify_code(email, req.code.strip()):
        raise HTTPException(401, "bad code")
    token = create_session(email)
    return {"ok": True, "token": token, "email": email}


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket, token: str = ""):
    email = get_email_by_token(token)
    if not email:
        await ws.close(code=4001)
        return

    await ws.accept()
    _connections[email] = ws

    try:
        while True:
            data = await ws.receive_text()
            for e, conn in _connections.items():
                if e != email:
                    try:
                        await conn.send_text(f"{email}: {data}")
                    except Exception:
                        pass
    except WebSocketDisconnect:
        pass
    finally:
        _connections.pop(email, None)


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)