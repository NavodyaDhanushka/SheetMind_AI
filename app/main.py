import zipfile
import os
from fastapi import FastAPI, Request, UploadFile, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles

from app.excel_reader import read_excel, row_to_context
from app.llm import generate_ai_output
from app.pdf_generator import generate_pdf

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
ZIP_DIR = "zips"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ZIP_DIR, exist_ok=True)

app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")
app.mount("/zips", StaticFiles(directory=ZIP_DIR), name="zips")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate")
async def generate(file: UploadFile, model: str = Form(...), prompt: str = Form(...)):
    # Save uploaded Excel
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Read Excel rows
    users = read_excel(file_path)
    if not users:
        return {"error": "No users found in the Excel"}

    pdf_files = []
    for user in users:
        context = row_to_context(user)
        ai_output = generate_ai_output(model, prompt, context)

        username = user.get("name", "user")
        pdf_path = generate_pdf(username, ai_output, OUTPUT_DIR)
        pdf_files.append(os.path.basename(pdf_path))  # store only filenames

    # Create a ZIP of all PDFs
    zip_filename = "generated_pdfs.zip"
    zip_path = os.path.join(ZIP_DIR, zip_filename)
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for pdf_file in pdf_files:
            zipf.write(os.path.join(OUTPUT_DIR, pdf_file), pdf_file)

    # Return JSON with ZIP and individual PDF URLs
    return {
        "zip": f"/zips/{zip_filename}",
        "pdfs": [f"/outputs/{pdf}" for pdf in pdf_files]
    }
