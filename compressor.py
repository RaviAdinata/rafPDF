import io, os, subprocess, pikepdf
from PIL import Image
import pymupdf

def compress_level(input_path: str, output_path: str, level: str) -> None:
    if level == "extreme": gs_setting, dpi = "/screen", 72
    elif level == "recommended": gs_setting, dpi = "/ebook", 150
    else: gs_setting, dpi = "/printer", 300
    cmd = ["gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.5", f"-dPDFSETTINGS={gs_setting}", "-dNOPAUSE", "-dQUIET", "-dBATCH", f"-dColorImageResolution={dpi}", f"-dGrayImageResolution={dpi}", "-dMonoImageResolution=150", "-dJPEGQ=75", "-dCompressFonts=true", "-dSubsetFonts=true", f"-sOutputFile={output_path}", input_path]
    try: subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError: pass

def rotate_pdf(input_path: str, output_path: str, angle: int = 90) -> None:
    with pikepdf.open(input_path) as pdf:
        for page in pdf.pages: page.Rotate = (page.get('/Rotate', 0) + angle) % 360
        pdf.save(output_path)

def add_watermark(input_path: str, output_path: str, text: str) -> None:
    doc = pymupdf.open(input_path)
    for page in doc:
        page.insert_textbox(page.rect, text, fontsize=50, rotate=45, align=1, color=(0.6, 0.6, 0.6), fill_opacity=0.3)
    doc.save(output_path)
    doc.close()

def extract_pages_to_preview(pdf_path: str, out_dir: str, prefix: str) -> list:
    doc = pymupdf.open(pdf_path)
    img_files = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=pymupdf.Matrix(0.5, 0.5))
        img_name = f"{prefix}_page_{i}.png"
        pix.save(os.path.join(out_dir, img_name))
        img_files.append(img_name)
    doc.close()
    return img_files

def merge_pdfs_with_rotation(file_paths: list[str], rotations: list[int], output_path: str) -> None:
    pdf = pikepdf.Pdf.new()
    for path, rot in zip(file_paths, rotations):
        with pikepdf.open(path) as src:
            for page in src.pages:
                new_page = pdf.pages.append(page)
                new_page.Rotate = (new_page.get('/Rotate', 0) + rot) % 360
    pdf.save(output_path)

def rotate_image(image_path: str, angle: int) -> None:
    if angle == 0: return
    img = Image.open(image_path)
    rotated = img.rotate(-angle, expand=True)
    rotated.save(image_path)

def images_to_pdf(image_paths: list[str], output_path: str) -> None:
    images = []
    for path in image_paths:
        img = Image.open(path)
        if img.mode == "RGBA": img = img.convert("RGB")
        images.append(img)
    if images: images[0].save(output_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:])

def generate_preview(pdf_path: str, output_img_path: str) -> None:
    doc = pymupdf.open(pdf_path)
    if len(doc) > 0:
        pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(1.0, 1.0))
        pix.save(output_img_path)
    doc.close()

# --- FUNGSI BARU: HAPUS HALAMAN ---
def delete_pdf_pages(input_path: str, output_path: str, pages_to_keep: list[int]) -> None:
    with pikepdf.open(input_path) as pdf:
        # Hitung halaman yang harus dihapus (yang tidak ada di pages_to_keep)
        total_pages = len(pdf.pages)
        pages_to_delete = [i for i in range(total_pages) if i not in pages_to_keep]
        
        # Hapus dari belakang ke depan agar index tidak bergeser
        for i in reversed(pages_to_delete):
            del pdf.pages[i]
            
        pdf.save(output_path)
