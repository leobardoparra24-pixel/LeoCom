import os
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill
from openpyxl.utils import get_column_letter
from sqlalchemy import select
from .db import SessionLocal
from .models import Invoice,Concept
HEADERS = [
"f_id",
"f_rfc",
"f_razon_social",
"f_folio",
"f_cert_cfdi",
"f_importe",
"f_descuento",
"f_ieps",
"f_iva",
"f_ret_iva",
"f_ret_isr",
"f_total",
"f_mn_cfdi",
"f_mpago_cfdi",
"f_fpago_cfdi",
"f_uso_cfdi",
"f_uuid",

"p_uuid",
"p_id",
"p_fecha_pago",
"p_forma_pago",
"p_moneda",
"p_num_parcialidad",
"p_imp_saldo_ant",
"p_imp_pagado",
"p_sal_insoluto",
"p_fecha_emision",
"pagos_agrupados",

"d_cant",
"d_desc",
"d_pu",
"d_importe",
"d_dcto",
"d_ieps",
"d_iva",
"d_ret_iva",
"d_ret_isr",
"d_total",
"d_t_ieps",
"d_t_iva",
"d_t_ret_iva",
"d_t_ret_isr",
"d_sat_prod",
"d_sat_unid"
]
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
