# Procesador interno de CFDI

MVP multiusuario para cargar XML o ZIP, procesar CFDI 3.3/4.0 y exportar un Excel con una sola hoja y una fila por concepto.

## Inicio rápido

1. Instale Docker Desktop o Docker Engine con Compose.
2. Cambie las contraseñas y `SECRET_KEY` en `docker-compose.yml`.
3. Ejecute:

```bash
docker compose up -d --build
```

4. Abra `http://localhost:8000`.

## Alcance incluido

- Carga de XML y ZIP.
- Procesamiento asíncrono con Celery y Redis.
- PostgreSQL como base central.
- CFDI 3.3 y 4.0: comprobante, emisor, receptor, timbre, conceptos e impuestos principales.
- Duplicados por UUID.
- Excel de una sola hoja, una fila por concepto.
- Columna `Total CFDI para suma` para evitar totales repetidos.
- Protección básica contra XML externo mediante `defusedxml` y límite de 50 MB por XML dentro de ZIP.

## Antes de producción

Este MVP debe endurecerse antes de utilizarse con información fiscal real:

- Integrar inicio de sesión corporativo con Microsoft Entra ID o Active Directory.
- Agregar roles: administrador, operador, consulta y auditor.
- Activar HTTPS y restringir acceso a red interna/VPN.
- Cambiar secretos y almacenarlos en un vault.
- Añadir auditoría, antivirus, cuotas de carga, retención y respaldo cifrado.
- Implementar complementos específicos: Pagos 2.0, Nómina, Carta Porte y Comercio Exterior.
- Añadir filtros de exportación y generación asíncrona de archivos grandes.
- Agregar división automática en varios XLSX de una sola hoja si se rebasa 1,048,575 filas de datos.
- No guardar exportaciones indefinidamente.

## Estructura

- `app/main.py`: interfaz y carga.
- `app/tasks.py`: procesamiento en segundo plano.
- `app/parser.py`: extracción XML.
- `app/models.py`: esquema de base de datos.
- `app/exporter.py`: Excel de una sola hoja.
