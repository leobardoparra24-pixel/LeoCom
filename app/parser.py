from defusedxml import ElementTree as ET
from hashlib import sha256

def a(node,*names):
    if node is None:return None
    for name in names:
        if name in node.attrib:return node.attrib[name]
    return None

def local(tag): return tag.split("}")[-1]
def child(node,name):
    return next((x for x in list(node) if local(x.tag)==name),None)
def children(node,name):
    return [x for x in list(node) if local(x.tag)==name]
def number(v):
    try:return float(v) if v not in (None,"") else None
    except:return None

def parse_cfdi(data,source):
    root=ET.fromstring(data)
    if local(root.tag)!="Comprobante": raise ValueError("El XML no es un CFDI")
    em=child(root,"Emisor"); rec=child(root,"Receptor"); comp=child(root,"Complemento")
    stamp=None
    if comp is not None:
        stamp=next((x for x in comp.iter() if local(x.tag)=="TimbreFiscalDigital"),None)
    uuid=a(stamp,"UUID")
    if not uuid: raise ValueError("CFDI sin Timbre Fiscal Digital/UUID")
    inv=dict(uuid=uuid.upper(),sha256=sha256(data).hexdigest(),source_file=source,
      version=a(root,"Version","version"),serie=a(root,"Serie","serie"),folio=a(root,"Folio","folio"),
      issue_date=a(root,"Fecha","fecha"),stamp_date=a(stamp,"FechaTimbrado"),voucher_type=a(root,"TipoDeComprobante","tipoDeComprobante"),
      issuer_rfc=a(em,"Rfc","rfc"),issuer_name=a(em,"Nombre","nombre"),issuer_regime=a(em,"RegimenFiscal","regimenFiscal"),
      receiver_rfc=a(rec,"Rfc","rfc"),receiver_name=a(rec,"Nombre","nombre"),receiver_regime=a(rec,"RegimenFiscalReceptor"),
      receiver_zip=a(rec,"DomicilioFiscalReceptor"),cfdi_use=a(rec,"UsoCFDI"),currency=a(root,"Moneda","moneda"),
      exchange_rate=a(root,"TipoCambio","tipoCambio"),subtotal=number(a(root,"SubTotal","subTotal")),discount=number(a(root,"Descuento","descuento")),
      total=number(a(root,"Total","total")),payment_form=a(root,"FormaPago","formaDePago"),payment_method=a(root,"MetodoPago","metodoDePago"),
      expedition_place=a(root,"LugarExpedicion","lugarExpedicion"),export_code=a(root,"Exportacion"),pac_rfc=a(stamp,"RfcProvCertif"))
    cons=[]; cn=child(root,"Conceptos")
    for i,c in enumerate(children(cn,"Concepto") if cn is not None else [],1):
        vals={"vat_base":0,"vat_rate":None,"vat_transferred":0,"vat_withheld":0,"isr_withheld":0,"ieps_transferred":0}
        taxes=child(c,"Impuestos")
        if taxes is not None:
            for group,withheld in (("Traslados",False),("Retenciones",True)):
                g=child(taxes,group)
                if g is None: continue
                for t in list(g):
                    imp=a(t,"Impuesto"); amount=number(a(t,"Importe")) or 0
                    if imp=="002" and not withheld:
                        vals["vat_base"]+=(number(a(t,"Base")) or 0); vals["vat_rate"]=number(a(t,"TasaOCuota")); vals["vat_transferred"]+=amount
                    elif imp=="002": vals["vat_withheld"]+=amount
                    elif imp=="001": vals["isr_withheld"]+=amount
                    elif imp=="003" and not withheld: vals["ieps_transferred"]+=amount
        cons.append(dict(line_no=i,product_key=a(c,"ClaveProdServ"),identification=a(c,"NoIdentificacion"),quantity=number(a(c,"Cantidad")),
         unit_key=a(c,"ClaveUnidad"),unit=a(c,"Unidad"),description=a(c,"Descripcion"),unit_value=number(a(c,"ValorUnitario")),
         amount=number(a(c,"Importe")),discount=number(a(c,"Descuento")),tax_object=a(c,"ObjetoImp"),**vals))
    if not cons: cons=[dict(line_no=1)]
    return inv,cons
