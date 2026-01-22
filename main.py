from fastapi import FastAPI
from routes import auth, automate, aplication
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="API Synthetis",
    description="API do software de automaçao Synthetis",
    version="1.0.0"
)

# IP local e localhost

# CORS - apenas UMA vez
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # ou ["*"] no desenvolvimento
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# Rotas
app.include_router(auth.router)
app.include_router(automate.router)
app.include_router(aplication.router)
