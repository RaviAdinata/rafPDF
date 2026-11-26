import os, uuid, shutil, json, time, threading, time, threading
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from compressor import *

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UP_DIR, OUT_DIR = os.path.join(BASE_DIR, "uploads"), os.path.join(BASE_DIR, "outputs")
os.makedirs(UP_DIR, exist_ok=True); os.makedirs(OUT_DIR, exist_ok=True)

def cleanup_old_files():
    """Menghapus file yang lebih tua dari 1 jam."""
    now = time.time()
    for folder in [UP_DIR, OUT_DIR]:
        if not os.path.exists(folder): continue
        for f in os.listdir(folder):
            fpath = os.path.join(folder, f)
            # Abaikan file .gitkeep
            if os.path.isfile(fpath) and not f.endswith(".gitkeep"):
                if os.stat(fpath).st_mtime < now - 3600: # 3600 detik = 1 jam
                    try: os.remove(fpath)
                    except: pass

def run_cleanup_bg():
    while True:
        cleanup_old_files()
        time.sleep(1800) # Cek setiap 30 menit

@app.on_event("startup")
def startup_event():
    threading.Thread(target=run_cleanup_bg, daemon=True).start()

def cleanup_old_files():
    """Menghapus file yang lebih tua dari 1 jam."""
    now = time.time()
    for folder in [UP_DIR, OUT_DIR]:
        for f in os.listdir(folder):
            fpath = os.path.join(folder, f)
            if os.path.isfile(fpath) and os.stat(fpath).st_mtime < now - 3600:
                try: os.remove(fpath)
                except: pass

def run_cleanup_bg():
    while True:
        cleanup_old_files()
        time.sleep(600) # Cek tiap 10 menit

@app.on_event("startup")
def startup_event():
    threading.Thread(target=run_cleanup_bg, daemon=True).start()

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
app.mount("/outputs", StaticFiles(directory=OUT_DIR), name="outputs")
app.mount("/uploads", StaticFiles(directory=UP_DIR), name="uploads")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    job_id = uuid.uuid4().hex
    in_path = os.path.join(UP_DIR, f"{job_id}.pdf")
    out_img = os.path.join(OUT_DIR, f"{job_id}_original.png")
    with open(in_path, "wb") as f: shutil.copyfileobj(file.file, f)
    generate_preview(in_path, out_img)
    return JSONResponse({"job_id": job_id, "filename": file.filename, "size": os.path.getsize(in_path)})

# --- ENDPOINT HAPUS HALAMAN ---
@app.post("/preview-pages")
async def preview_pages(file: UploadFile = File(...)):
    job_id = uuid.uuid4().hex
    temp_path = os.path.join(UP_DIR, f"{job_id}.pdf")
    with open(temp_path, "wb") as f: shutil.copyfileobj(file.file, f)
    imgs = extract_pages_to_preview(temp_path, OUT_DIR, f"{job_id}")
    previews = [{"index": i, "img_url": f"/outputs/{img}"} for i, img in enumerate(imgs)]
    return JSONResponse({"job_id": job_id, "previews": previews})

@app.post("/delete-pages")
async def delete_pages(job_id: str = Form(...), keep_json: str = Form(...)):
    keep_indices = json.loads(keep_json)
    in_path = os.path.join(UP_DIR, f"{job_id}.pdf")
    out_path = os.path.join(OUT_DIR, f"{job_id}_result.pdf")
    delete_pdf_pages(in_path, out_path, keep_indices)
    return JSONResponse({"job_id": job_id})

# --- ENDPOINT MERGE ---
@app.post("/preview-merge")
async def preview_merge(files: List[UploadFile] = File(...)):
    job_id = uuid.uuid4().hex
    all_previews = []
    for idx, file in enumerate(files):
        temp_path = os.path.join(UP_DIR, f"{job_id}_{idx}.pdf")
        with open(temp_path, "wb") as f: shutil.copyfileobj(file.file, f)
        imgs = extract_pages_to_preview(temp_path, OUT_DIR, f"{job_id}_{idx}")
        for img in imgs:
            all_previews.append({"file_index": idx, "img_url": f"/outputs/{img}"})
    return JSONResponse({"job_id": job_id, "previews": all_previews})

@app.post("/merge")
async def merge(job_id: str = Form(...), order_json: str = Form(...)):
    order_data = json.loads(order_json)
    file_paths, rotations = [], []
    for item in order_data:
        file_paths.append(os.path.join(UP_DIR, f"{job_id}_{item['file_index']}.pdf"))
        rotations.append(item.get("rotate", 0))
    out_path = os.path.join(OUT_DIR, f"{job_id}_result.pdf")
    merge_pdfs_with_rotation(file_paths, rotations, out_path)
    return JSONResponse({"job_id": job_id})

# --- ENDPOINT JPG TO PDF ---
@app.post("/preview-image")
async def preview_image(files: List[UploadFile] = File(...)):
    job_id = uuid.uuid4().hex
    all_previews = []
    for idx, file in enumerate(files):
        ext = os.path.splitext(file.filename)[1].lower()
        temp_path = os.path.join(UP_DIR, f"{job_id}_{idx}{ext}")
        with open(temp_path, "wb") as f: shutil.copyfileobj(file.file, f)
        all_previews.append({"file_index": idx, "ext": ext, "img_url": f"/uploads/{job_id}_{idx}{ext}"})
    return JSONResponse({"job_id": job_id, "previews": all_previews})

@app.post("/convert-images")
async def convert_images(job_id: str = Form(...), order_json: str = Form(...)):
    order_data = json.loads(order_json)
    file_paths = []
    for item in order_data:
        path = os.path.join(UP_DIR, f"{job_id}_{item['file_index']}{item['ext']}")
        rotate_image(path, item.get("rotate", 0))
        file_paths.append(path)
    out_path = os.path.join(OUT_DIR, f"{job_id}_result.pdf")
    images_to_pdf(file_paths, out_path)
    return JSONResponse({"job_id": job_id})


# --- TAMBAH NOMOR HALAMAN ---
@app.post("/add-numbers")
async def add_numbers(job_id: str = Form(...), position: str = Form("bottom")):
    in_path, out_path = os.path.join(UP_DIR, f"{job_id}.pdf"), os.path.join(OUT_DIR, f"{job_id}_result.pdf")
    add_page_numbers(in_path, out_path, position)
    return JSONResponse({"job_id": job_id})

# --- PROTEKSI PASSWORD ---
@app.post("/protect")
async def protect(job_id: str = Form(...), password: str = Form(...)):
    in_path, out_path = os.path.join(UP_DIR, f"{job_id}.pdf"), os.path.join(OUT_DIR, f"{job_id}_result.pdf")
    protect_pdf(in_path, out_path, password)
    return JSONResponse({"job_id": job_id})


# --- SPLIT PDF ---
@app.post("/split")
async def split(job_id: str = Form(...), page_num: int = Form(...)):
    in_path, out_path = os.path.join(UP_DIR, f"{job_id}.pdf"), os.path.join(OUT_DIR, f"{job_id}_result.pdf")
    try:
        split_pdf(in_path, out_path, page_num - 1) # user input 1-based, code 0-based
        return JSONResponse({"job_id": job_id})
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)

# --- UNLOCK PDF ---
@app.post("/unlock")
async def unlock(job_id: str = Form(...), password: str = Form(...)):
    in_path, out_path = os.path.join(UP_DIR, f"{job_id}.pdf"), os.path.join(OUT_DIR, f"{job_id}_result.pdf")
    try:
        unlock_pdf(in_path, out_path, password)
        return JSONResponse({"job_id": job_id})
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)

# --- ENDPOINT LAINNYA ---
@app.post("/quick-action")
async def quick_action(job_id: str = Form(...), action: str = Form(...), angle: int = Form(90), text: str = Form("")):
    in_path, temp_out = os.path.join(UP_DIR, f"{job_id}.pdf"), os.path.join(OUT_DIR, f"{job_id}_temp.pdf")
    if action == "rotate": rotate_pdf(in_path, temp_out, angle)
    elif action == "watermark": add_watermark(in_path, temp_out, text)
    shutil.move(temp_out, in_path) 
    return JSONResponse({"success": True})

@app.post("/compress")
async def compress(job_id: str = Form(...), level: str = Form(...)):
    in_path, out_path = os.path.join(UP_DIR, f"{job_id}.pdf"), os.path.join(OUT_DIR, f"{job_id}_result.pdf")
    compress_level(in_path, out_path, level)
    orig_sz, new_sz = os.path.getsize(in_path), os.path.getsize(out_path)
    return JSONResponse({"new_sz": new_sz, "ratio": round((1-new_sz/orig_sz)*100, 1) if orig_sz else 0})

@app.get("/download/{job_id}")
async def download(job_id: str):
    return FileResponse(os.path.join(OUT_DIR, f"{job_id}_result.pdf"), media_type="application/pdf", filename="RafPDF_Hasil.pdf")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
