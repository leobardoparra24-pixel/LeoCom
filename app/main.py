import os,shutil,uuid,time
from pathlib import Path
from fastapi import FastAPI,Request,UploadFile,File,Depends,HTTPException
from fastapi.responses import HTMLResponse,FileResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from .db import Base,engine,SessionLocal
from .models import Job
from .tasks import process_job
from .exporter import create_export
app=FastAPI(title="Procesador CFDI")
templates=Jinja2Templates(directory="app/templates")
@app.on_event("startup")
def startup():
    for _ in range(20):
        try: Base.metadata.create_all(engine); return
        except Exception: time.sleep(2)
def db():
    s=SessionLocal()
    try: yield s
    finally:s.close()
@app.get("/",response_class=HTMLResponse)
def home(request:Request,s=Depends(db)):
    jobs=s.scalars(select(Job).order_by(Job.id.desc()).limit(30)).all()
    return templates.TemplateResponse("index.html",{"request":request,"jobs":jobs})
@app.post("/upload")
def upload(
    xmlfile: UploadFile = File(...),
    auxfile: UploadFile = File(...),
    s=Depends(db)
):
    ext = Path(xmlfile.filename or "").suffix.lower()

    if ext not in (".xml",".zip"):
        raise HTTPException(
            400,
            "Solo se permiten XML o ZIP"
        )

        data_dir = Path(
        os.getenv("DATA_DIR","/tmp")
    ) / "uploads"

        data_dir.mkdir(
        parents=True,
        exist_ok=True
    )

        path = data_dir / f"{uuid.uuid4().hex}{ext}"

        with path.open("wb") as f:
        shutil.copyfileobj(
            xmlfile.file,
            f
        )

        aux_path = (
        data_dir /
        f"aux_{uuid.uuid4().hex}.xlsx"
    )

        with open(aux_path,"wb") as f:
        shutil.copyfileobj(
            auxfile.file,
            f
        )

        job = Job(
        filename=xmlfile.filename,
        stored_path=str(path),
        aux_file=str(aux_path)
    )

        s.add(job)
    s.commit()
    s.refresh(job)

        process_job(job.id)

        return RedirectResponse("/",303)
@app.get("/export")
def export_all():
    path=create_export(); return FileResponse(path,filename="Detalle_CFDI.xlsx")
@app.get("/health")
def health(): return {"status":"ok"}
