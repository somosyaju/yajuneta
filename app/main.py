from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import pandas as pd
import tempfile
import os
import pdfplumber
from openai import OpenAI
from fastapi.templating import Jinja2Templates
from fastapi import Request

client = OpenAI()

app = FastAPI()

templates = Jinja2Templates(directory="templates")



@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/check")
async def check(pdf: UploadFile = File(...), excel: UploadFile = File(...)):
    try:
        # ---------- Guardar archivos ----------
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_tmp:
            pdf_tmp.write(await pdf.read())
            pdf_path = pdf_tmp.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as xls_tmp:
            xls_tmp.write(await excel.read())
            excel_path = xls_tmp.name

        # ---------- Extraer texto del PDF ----------
        pdf_text = ""
        with pdfplumber.open(pdf_path) as pdf_file:
            for page in pdf_file.pages:
                pdf_text += page.extract_text() + "\n"

        # ---------- Leer Excel ----------
        df = pd.read_excel(excel_path)
        excel_text = df.to_string(index=False)

        # ---------- Prompt a la IA ----------
        prompt = f"""
Tenés dos fuentes de datos:

PDF (ofertas):
{pdf_text}

Excel (datos correctos):
{excel_text}

Tarea:
Compará precios entre el PDF y el Excel.
Respondé SOLO si hay errores de precio.
Si hay errores, describilos.
Si no hay errores, decilo explícitamente.
Respondé en UN SOLO PÁRRAFO, en español.
No hagas listas.
"""

        # ---------- Llamada a la IA ----------
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sos un auditor de precios muy preciso."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        result_text = response.choices[0].message.content.strip()

        return {"ok": True, "message": result_text}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e)}
        )

    finally:
        try:
            os.remove(pdf_path)
            os.remove(excel_path)
        except:
            pass
