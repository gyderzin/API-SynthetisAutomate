from fastapi import FastAPI
from routes import auth
from routes import teste_db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="API Synthetis",
    description="API do software de automaçao Synthetis",
    version="1.0.0"
)

# Configuração de CORS
origins = [
    "http://localhost:5173",  # Frontend Vue
    "http://127.0.0.1:5173",  # Caso use esse também
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Or use ["*"] para liberar tudo (não recomendado em produção)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(teste_db.router)
