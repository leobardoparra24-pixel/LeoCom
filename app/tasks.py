import os, zipfile
import pandas as pd    
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

    d**= SessionLocal()
    job = db.get**ob, job_id)

    try:

        it**s = list(entries(job.stored_path)**
        job.total = len(items)
 **     job.status = "processing"

 **     db.commit()

        for nam** data in items:

            try:**                invd, cons = pars**cfdi(data, name)

               **f db.query(Invoice).filter(
     **             Invoice.uuid == invd**uuid"]
                ).first():**                    job.duplicate**+= 1

                else:

    **              inv = Invoice(**inv**

                    db.add(inv)**                   db.flush()

  **                for c in cons:
  **                    db.add(
     **                     Concept(
   **                           invoic**id=inv.id,
                      **        **c
                     **     )
                        )
**                   job.valid += 1**            except Exception as e**
                import traceback**               print(traceback.fo**at_exc())

                db.rol**ack()

                job = db.g**(Job, job_id)

                jo**errors += 1

                job.**ssage = (
                    job**essage or ""
                ) + **{name}: {e}\n"

            job.p**cessed += 1
            db.commit**

        job.status = "completed**        db.commit()

    except E**eption as e:

        import trac**ack
        print(traceback.forma**exc())

        job.status = "failed"
        job.message = str(e)

        db.commit()

    finally:

        db.close()
