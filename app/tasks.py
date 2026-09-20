import os, zipfile
from pathlib import Path
from celery import Celery
from sqlalchemy.exc import IntegrityError
from .db import SessionLocal
from .models import Job,Invoice,Concept
from .parser import parse_cfdi
celery=Celery("cfdi",broker=os.getenv("CELERY_BROKER_URL","redis://localhost:6379/0"))

def entries(path):
    p=Path(path)
    if p.suffix.lower()==".zip":
        with zipfile.ZipFile(p) as z:
            bad=z.testzip()
            if bad: raise ValueError(f"ZIP dañado: {bad}")
            for info in z.infolist():
                if info.is_dir() or not info.filename.lower().endswith(".xml"): continue
                if info.file_size>50*1024*1024: raise ValueError(f"XML demasiado grande: {info.filename}")
                yield info.filename,z.read(info)
    else: yield p.name,p.read_bytes()
def process_job(job_id):
    db=SessionLocal(); job=db.get(Job,job_id)
    try:
        items=list(entries(job.stored_path)); job.total=len(items); job.status="processing"; db.commit()
        for name,data in items:
            try:
                invd,cons=parse_cfdi(data,name)
                if db.query(Invoice).filter(Invoice.uuid==invd["uuid"]).first(): job.duplicates+=1
                else:
                    inv=Invoice(**invd); db.add(inv); db.flush()
                    for c in cons: db.add(Concept(invoice_id=inv.id,**c))
                    job.valid+=1
            except Exception as e:
                db.rollback(); job=db.get(Job,job_id); job.errors+=1; job.message=(job.message or "")+f"{name}: {e}\n"
            job.processed+=1; db.commit()
        job.status="completed"; db.commit()
    except Exception as e:
        job.status="failed"; job.message=str(e); db.commit()
    finally: db.close()
