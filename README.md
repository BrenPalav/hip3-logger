# HIP-3 daily logger

Guarda todos los dias, automaticamente, una fila por mercado HIP-3 de Hyperliquid
en un Google Sheet. Corre en GitHub Actions a las 00:05 UTC. Gratis.

## Configuracion (una sola vez, ~15 minutos)

### 1. Crear una cuenta de servicio de Google
1. Entra a https://console.cloud.google.com y crea un proyecto (nombre libre, ej. `hip3-logger`).
2. Menu "APIs y servicios" > "Biblioteca": habilita **Google Sheets API** y **Google Drive API**.
3. Menu "IAM y administracion" > "Cuentas de servicio" > "Crear cuenta de servicio".
   Nombre libre. No hace falta darle roles. Crear.
4. Entra a la cuenta creada > pestana "Claves" > "Agregar clave" > "Crear clave nueva" > JSON.
   Se descarga un archivo `.json`. Guardalo; es una contrasena.
5. Copia el email de la cuenta de servicio (termina en `@...iam.gserviceaccount.com`).

### 2. Compartir el Sheet con la cuenta de servicio
Abri tu Sheet "HIP3 daily log" > Compartir > pega el email de la cuenta de servicio > rol **Editor**.

El ID del Sheet es la parte larga de la URL:
`https://docs.google.com/spreadsheets/d/`**`ESTE_TRAMO`**`/edit`

### 3. Crear el repositorio en GitHub
1. https://github.com/new > nombre `hip3-logger` > **Private** > Create.
2. Subi estos 4 archivos respetando las carpetas:
   - `hip3_logger.py`
   - `requirements.txt`
   - `README.md`
   - `.github/workflows/daily.yml`
   (Podes hacerlo desde la web: "Add file" > "Upload files"; para la carpeta
   `.github/workflows` usa "Add file" > "Create new file" y escribi la ruta completa
   `.github/workflows/daily.yml` en el nombre.)

### 4. Cargar los secretos
Repo > Settings > Secrets and variables > Actions > "New repository secret":
- `SHEET_ID` = el ID del Sheet del paso 2.
- `GOOGLE_SERVICE_ACCOUNT_JSON` = el contenido COMPLETO del archivo `.json` del paso 1
  (abrilo con un editor de texto, selecciona todo, copia, pega).

### 5. Probar
Repo > pestana **Actions** > "HIP-3 daily logger" > "Run workflow" > Run.
En un minuto deberia aparecer en verde. Abri el log y vas a ver el resumen del dia.
Revisa el Sheet: si ya habia filas de hoy (por la corrida en Colab), dice "Nada que hacer";
si no, agrega las filas.

A partir de ahi corre solo todos los dias. No hay que tocar nada mas.

## Si algo falla
- **Error 403 / PERMISSION_DENIED**: falta compartir el Sheet con el email de la cuenta de servicio (paso 2).
- **SpreadsheetNotFound**: el `SHEET_ID` esta mal copiado.
- **JSONDecodeError en credenciales**: el secreto `GOOGLE_SERVICE_ACCOUNT_JSON` no tiene el JSON completo.
- **API not enabled**: falta habilitar Sheets API o Drive API (paso 1.2).

## Nota
GitHub puede retrasar los cron unos minutos en horas de carga; el logger tolera eso
porque `dayNtlVlm` es una ventana movil de 24h. Si un dia no corre, se puede disparar a mano
desde Actions.
