import os
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill
from openpyxl.utils import get_column_letter
from sqlalchemy import select
from .db import SessionLocal
from .models import Invoice,Concept
HEADERS=["UUID","Archivo XML","Versión","Serie","Folio","Fecha emisión","Fecha timbrado","Tipo CFDI","RFC emisor","Nombre emisor","Régimen emisor","RFC receptor","Nombre receptor","Régimen receptor","CP receptor","Uso CFDI","Moneda","Tipo cambio","Subtotal CFDI","Descuento CFDI","Total CFDI","Forma pago","Método pago","Lugar expedición","Exportación","RFC PAC","Núm. concepto","Clave producto/servicio","No. identificación","Cantidad","Clave unidad","Unidad","Descripción","Valor unitario","Importe concepto","Descuento concepto","Objeto impuesto","Base IVA","Tasa IVA","IVA trasladado","IVA retenido","ISR retenido","IEPS trasladado","Es primera fila CFDI","Total CFDI para suma"]
def row(i,c,first):
    return [i.uuid,i.source_file,i.version,i.serie,i.folio,i.issue_date,i.stamp_date,i.voucher_type,i.issuer_rfc,i.issuer_name,i.issuer_regime,i.receiver_rfc,i.receiver_name,i.receiver_regime,i.receiver_zip,i.cfdi_use,i.currency,i.exchange_rate,i.subtotal,i.discount,i.total,i.payment_form,i.payment_method,i.expedition_place,i.export_code,i.pac_rfc,c.line_no,c.product_key,c.identification,c.quantity,c.unit_key,c.unit,c.description,c.unit_value,c.amount,c.discount,c.tax_object,c.vat_base,c.vat_rate,c.vat_transferred,c.vat_withheld,c.isr_withheld,c.ieps_transferred,1 if first else 0,i.total if first else 0]
def create_export():
    out=Path(os.getenv("DATA_DIR","/tmp"))/"exports"; out.mkdir(parents=True,exist_ok=True)
    path=out/"detalle_cfdi.xlsx"; wb=Workbook(write_only=True); ws=wb.create_sheet("Detalle_CFDI")
    ws.append(HEADERS); db=SessionLocal(); last=None
    q=select(Invoice,Concept).join(Concept,Concept.invoice_id==Invoice.id).order_by(Invoice.id,Concept.line_no)
    for i,c in db.execute(q).yield_per(2000):
        first=i.id!=last; ws.append(row(i,c,first)); last=i.id
    db.close(); wb.save(path); return path
