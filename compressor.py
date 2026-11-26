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


def add_page_numbers(input_path: str, output_path: str, position: str = "bottom") -> None:
    doc = pymupdf.open(input_path)
    for i, page in enumerate(doc):
        text = f"{i + 1}"
        rect = page.rect
        fontsize = 12
        
        # Gunakan insert_textbox untuk rata tengah
        if position == "bottom":
            text_rect = pymupdf.Rect(rect.width/2 - 50, rect.height - 25, rect.width/2 + 50, rect.height - 10)
            page.insert_textbox(text_rect, text, fontsize=fontsize, align=1, color=(0, 0, 0))
        elif position == "bottom-right":
            text_rect = pymupdf.Rect(rect.width - 60, rect.height - 25, rect.width - 10, rect.height - 10)
            page.insert_textbox(text_rect, text, fontsize=fontsize, align=2, color=(0, 0, 0))
    doc.save(output_path)
    doc.close()

def protect_pdf(input_path: str, output_path: str, password: str) -> None:
    with pikepdf.open(input_path) as pdf:
        # Enkripsi PDF dengan password
        pdf.save(output_path, encryption=pikepdf.Encryption(owner=password, user=password, R=6))


def unlock_pdf(input_path: str, output_path: str, password: str) -> None:
    try:
        with pikepdf.open(input_path, password=password) as pdf:
            pdf.save(output_path) # Simpan tanpa enkripsi
    except pikepdf.PasswordError:
        raise ValueError("Password salah! Tidak dapat membuka dokumen.")

def split_pdf(input_path: str, output_path: str, page_num: int) -> None:
    check_encryption(input_path)
    with pikepdf.open(input_path) as pdf:
        new_pdf = pikepdf.Pdf.new()
        # page_num adalah index (0, 1, 2), jadi kurangi 1 dari input user
        if page_num < 0 or page_num >= len(pdf.pages):
            raise ValueError("Nomor halaman tidak valid.")
        new_pdf.pages.append(pdf.pages[page_num])
        new_pdf.save(output_path)

def generate_preview(pdf_path: str, output_img_path: str) -> None:
    try:
        doc = pymupdf.open(pdf_path)
        if len(doc) > 0:
            pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(1.0, 1.0))
            pix.save(output_img_path)
        doc.close()
    except Exception as e:
        print(f"Gagal buat preview (mungkin PDF terkunci): {e}")
        # Buat gambar placeholder jika PDF terkunci
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (400, 500), color='#181b21')
        d = ImageDraw.Draw(img)
        d.text((150, 250), "PDF Terkunci", fill="white")
        img.save(output_img_path)

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
