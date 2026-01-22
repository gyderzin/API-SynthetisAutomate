from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models.modelo import Modelo, Base
from models.relatorio import Relatorio
from fastapi.responses import StreamingResponse
import zipfile
import re
from io import BytesIO
from xml.etree import ElementTree as ET
from core.security import get_current_user
import os


router = APIRouter(prefix="/app", tags=["Modelos"])

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --------------------------------------------------------
# LISTA MODELOS
# --------------------------------------------------------
@router.get("/modelos")
def listar_modelos(
    equipe: str = Query(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    modelos = db.query(Modelo).filter(Modelo.equipe == equipe).all()
    return [
        {
            "id": m.id,
            "titulo": m.titulo,
            "descriçao": m.descriçao,
            "equipe": m.equipe,
            "modelo_automacao": m.modelo_automacao,
            "termografia": m.termografia
        }
        for m in modelos
    ]


# --------------------------------------------------------
# EXTRAI VARIÁVEIS {{ }}
# --------------------------------------------------------
@router.post("/extrair-variaveis")
async def extrair_variaveis(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    if not file.filename.endswith(".docx"):
        return {"erro": "Formato inválido. Envie um arquivo .docx"}

    content = await file.read()
    textos = []

    with zipfile.ZipFile(BytesIO(content)) as docx:
        partes = [
            "word/document.xml",
            *[f"word/header{i}.xml" for i in range(1, 6)],
            *[f"word/footer{i}.xml" for i in range(1, 6)],
        ]

        for parte in partes:
            if parte in docx.namelist():
                try:
                    xml = docx.read(parte)
                    root = ET.fromstring(xml)
                    textos += [
                        node.text for node in root.iter()
                        if node.tag.endswith("}t") and node.text
                    ]
                except ET.ParseError:
                    continue

    texto_completo = " ".join(textos)
    variaveis = re.findall(r"\{\{(.*?)\}\}", texto_completo)

    vistos = set()
    variaveis_ordenadas = []

    for v in variaveis:
        var = v.strip()
        if var not in vistos:
            vistos.add(var)
            variaveis_ordenadas.append(var)

    return {"variaveis": variaveis_ordenadas}


# --------------------------------------------------------
# CRIA MODELO
# --------------------------------------------------------
@router.post("/novoModelo")
async def criar_modelo(
    titulo: str = Form(...),
    equipe: str = Form(...),
    descriçao: str = Form(...),
    modelo_automacao: str = Form(...),
    documento_modelo: UploadFile = File(...),
    termografia: bool = Form(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    if not documento_modelo.filename.endswith(".docx"):
        return {"erro": "O arquivo deve estar no formato .docx"}

    conteudo_doc = await documento_modelo.read()

    novo_modelo = Modelo(
        titulo=titulo.strip(),
        equipe=equipe.strip(),
        descriçao=descriçao.strip(),
        modelo_automacao=modelo_automacao.strip(),
        documento_modelo=conteudo_doc,
        termografia=termografia
    )

    db.add(novo_modelo)
    db.commit()
    db.refresh(novo_modelo)

    return {"mensagem": "Modelo criado com sucesso", "id": novo_modelo.id}


# --------------------------------------------------------
# LISTA RELATÓRIOS DO USUÁRIO
# --------------------------------------------------------
@router.get("/recuperarRelatorios")
def recuperar_relatorios(
    equipe: str = Query(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    query = db.query(Relatorio).filter(Relatorio.emissor == current_user)

    if equipe:
        query = query.filter(Relatorio.equipe == equipe)

    relatorios = query.order_by(Relatorio.emitido_em.desc()).all()

    if not relatorios:
        return False

    return [
        {
            "id": r.id,
            "modelo": r.modelo,
            "emissor": r.emissor,
            "equipe": r.equipe,
            "nome_arquivo": r.nome_arquivo,
            "emitido_em": r.emitido_em,
            "item_pendente": r.item_pendente
        }
        for r in relatorios
    ]


# --------------------------------------------------------
# BAIXAR RELATÓRIO (LENDO DO DISCO)
# --------------------------------------------------------
@router.get("/baixarRelatorio/{relatorio_id}")
def baixar_relatorio(
    relatorio_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    relatorio = db.query(Relatorio).filter(Relatorio.id == relatorio_id).first()

    if not relatorio:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")

    if relatorio.emissor != current_user:
        raise HTTPException(status_code=403, detail="Acesso negado")

    caminho = relatorio.caminho_arquivo

    if not os.path.exists(caminho):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado no servidor")

    file_stream = open(caminho, "rb")


    nome_download = relatorio.nome_arquivo
    print("Enviando header:", nome_download)

    if not nome_download.lower().endswith(".docx"):
        nome_download += ".docx"

    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f"attachment; filename=\"{nome_download}\""
        }
    )

