from fastapi import FastAPI, File, UploadFile, Request, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from werkzeug.utils import secure_filename
import logging
import uvicorn
import os
import sys
import rvlib
from llama_attn_replace import replace_llama_attn
# import pdfplumber

handler = logging.StreamHandler(sys.stdout)
logging.basicConfig(level=logging.DEBUG, handlers=[handler])

# Define CORS configuration before creating the FastAPI application instance
origins = [
    "http://localhost:3000",
    "http://128.253.51.12:3000",
    "http://localhost:3001",
    "http://128.253.51.12:3001"
    "http://localhost:8080",
    "http://128.253.51.12:8080"
]

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up directories for file uploads and JSON processing
upload_directory = 'uploads'
json_directory = 'json'
offloaded_directory = 'offloaded_weights_folder'

# Ensure directories exist, create if they do not
for directory in [upload_directory, json_directory, offloaded_directory]:
    if not os.path.exists(directory):
        os.makedirs(directory)

replace_llama_attn(inference=True)
prompt_generator = rvlib.PromptGenerator()
review_generator = rvlib.ReviewGenerator()

# Check if the uploaded file has an allowed extension
async def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['pdf']

@app.post("/submit-pdf-text")
async def upload_file(request: Request, pdfFile: UploadFile = File(...), version: str = Form("default")):
    logging.info("Uploading PDF file...")
    if not pdfFile:
        return JSONResponse(content={"error": "No file uploaded"}, status_code=400)

    filename = secure_filename(pdfFile.filename)
    temp_pdf_path = os.path.join('./', filename)
    logging.debug(f"PDF path: {temp_pdf_path}, filename: {filename}")
    
    with open(temp_pdf_path, "wb") as buffer:
        buffer.write(await pdfFile.read())

    try:
        # with pdfplumber.open(temp_pdf_path) as pdf:
        #     paper_content = ""
        #     for page in pdf.pages:
        #         paper_content += page.extract_text()
        json_path = rvlib.parse_pdf_to_json(temp_pdf_path, json_directory)
        if json_path is None or isinstance(json_path, tuple):
            raise ValueError("Failed to parse PDF into JSON")

        paper_content = rvlib.parse_paper_content(json_path)
        print("Paper Content:", paper_content)
        # paper_content = rvlib.load_pdf_file_pypdf(temp_pdf_path)
        gen_prompt = prompt_generator.generate_prompt(paper_content, version)
        result = {"state": "success", "gen_prompt": gen_prompt, "paper_content": paper_content}
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        logging.error(f"Error processing PDF: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    # try:
    #     test_results = rvlib.TestApi()
    #     version_data = test_results[version]
    #     result = {
    #         "state": "success",
    #         "gen_prompt": version_data["prompt"],
    #         "paper_content": "Simulated paper content for demonstration purposes."
    #     }
    #     return JSONResponse(content=result, status_code=200)
    # except Exception as e:
    #     logging.error(f"Simulated error processing PDF: {e}")
    #     return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/generate-review")
async def generate_review(request: Request):
    body = await request.json()
    paper_content = body.get("paper_content", "")
    prompt = body.get("prompt", "")
    version = body.get("version", "default")

    logging.info(f"Received request to generate review with version: {version}")
    try:
        gen_review = review_generator.generate_review(paper_content, prompt, version)
        return JSONResponse(content={"gen_review": gen_review}, status_code=200)
    except Exception as e:
        logging.error(f"Error generating review: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    # try:
    #     test_results = rvlib.TestApi()
    #     version_data = test_results[version]
    #     return JSONResponse(content={"gen_review": version_data["review"]}, status_code=200)
    # except Exception as e:
    #     logging.error(f"Error generating review: {e}")
    #     return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3001, log_level="debug")
