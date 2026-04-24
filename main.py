import os
import httpx
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

@app.post("/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()
    return {"status": "ok"}

@app.api_route("/feedback", methods=["GET", "POST"])
async def handle_feedback(request: Request):
    if request.method == "GET":
        name = request.query_params.get("name")
        email = request.query_params.get("email")
        category = request.query_params.get("category")
        subject = request.query_params.get("subject")
        message = request.query_params.get("message")
    else:
        try:
            data = await request.json()
        except Exception:
            data = await request.form()
        
        name = data.get("name")
        email = data.get("email")
        category = data.get("category")
        subject = data.get("subject")
        message = data.get("message")

    if not all([name, email, category, subject, message]):
        raise HTTPException(status_code=400, detail="Missing required parameters.")

    bot_token = os.environ.get("bot_token")
    admin_id = os.environ.get("admin_id")

    if not bot_token or not admin_id:
        raise HTTPException(status_code=500, detail="Environment variables not set.")

    text = f"A new feedback has been submitted by the users. Name: {name}, email: {email}, feedback category: {category}, feedback subject: {subject}, message: {message}."
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": admin_id,
        "text": text
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to send message to Telegram.")

    return {"success": True, "message": "Feedback successfully forwarded to admin."}