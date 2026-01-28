import zipfile
import os
from fastapi import FastAPI, Request, UploadFile, Form
from fastapi.templating import Jinja2Templates
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

    for index, user in enumerate(users, start=1):
        context = row_to_context(user)
        ai_output = generate_ai_output(model, prompt, context)

        # Safe name handling
        raw_name = str(user.get("name", f"user_{index}")).strip()
        safe_name = raw_name.replace(" ", "_") if raw_name else f"user_{index}"

        pdf_filename = f"{safe_name}_{index}.pdf"
        # generate_pdf now returns the full path
        pdf_path = generate_pdf(pdf_filename.replace(".pdf",""), ai_output, OUTPUT_DIR)

        # Store the full path for zipping
        pdf_files.append(pdf_path)

    # Create ZIP
    zip_filename = "generated_pdfs.zip"
    zip_path = os.path.join(ZIP_DIR, zip_filename)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for pdf_path in pdf_files:
            if os.path.exists(pdf_path):  # safe check
                zipf.write(pdf_path, arcname=os.path.basename(pdf_path))
            else:
                print(f"Warning: {pdf_path} not found, skipping")

    return {
        "zip": f"/zips/{zip_filename}",
        "pdfs": [f"/outputs/{os.path.basename(pdf)}" for pdf in pdf_files]
    }


