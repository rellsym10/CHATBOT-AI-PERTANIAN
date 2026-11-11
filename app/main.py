from fastapi import FastAPI
from app.routes.whatsapp_webhook import router
from app.routes.dashboard import router as dashboard_router

    
app = FastAPI()

app.include_router(router)
app.include_router(dashboard_router)  

@app.get("/")
def home():
    return {"status": "Chatbot AI Pertanian Aktif"}

