function navTo(pageId) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(`page-${pageId}`).classList.add('active');
}

function showToast(msg, isError = false) {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.className = "toast show" + (isError ? " error" : "");
  setTimeout(() => { toast.classList.remove("show"); }, 3000);
}

const fmtSize = (b) => b < 1024*1024 ? (b/1024).toFixed(1) + " KB" : (b/1024/1024).toFixed(2) + " MB";

// ==========================================
// 1. FITUR KOMPRES & PUTAR (Single PDF)
// ==========================================
let jobIdC = null;
let currentAngle = 0;

const fileC = document.getElementById("file-c");
const dropZone = document.getElementById("view-upload-c");
const btnTriggerC = document.getElementById("btn-trigger-c");

btnTriggerC.addEventListener("click", (e) => { e.stopPropagation(); fileC.click(); });
dropZone.addEventListener("click", (e) => { if (e.target !== btnTriggerC) fileC.click(); });
dropZone.addEventListener("dragover", e => { e.preventDefault(); dropZone.style.borderColor = "var(--primary)"; });
dropZone.addEventListener("dragleave", e => { e.preventDefault(); dropZone.style.borderColor = "var(--border)"; });
dropZone.addEventListener("drop", e => { e.preventDefault(); dropZone.style.borderColor = "var(--border)"; if(e.dataTransfer.files.length > 0) handleUploadC(e.dataTransfer.files[0]); });
fileC.addEventListener("change", () => { if (fileC.files.length > 0) handleUploadC(fileC.files[0]); });

async function handleUploadC(file) {
  if (!file.name.toLowerCase().endsWith(".pdf")) return showToast("File harus PDF!", true);
  document.getElementById("view-upload-c").style.display = "none";
  document.getElementById("view-work-c").style.display = "grid";
  document.getElementById("ui-filename-c").textContent = "Memproses: " + file.name;
  document.getElementById("img-preview-c").style.display = "none";
  document.getElementById("img-loading-c").style.display = "block";

  const fd = new FormData(); fd.append("file", file);
  try {
    const res = await fetch("/upload", { method: "POST", body: fd });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    jobIdC = data.job_id;
    document.getElementById("ui-filename-c").textContent = file.name;
    document.getElementById("img-preview-c").src = `/outputs/${jobIdC}_original.png`;
    showToast("File berhasil diunggah!");
  } catch (err) {
    showToast("Gagal upload: " + err.message, true);
    document.getElementById("view-upload-c").style.display = "block";
    document.getElementById("view-work-c").style.display = "none";
  }
}

document.getElementById("btn-rotate").addEventListener("click", async () => {
  currentAngle = (currentAngle + 90) % 360;
  document.getElementById("img-preview-c").style.transform = `rotate(${currentAngle}deg)`;
  const fd = new FormData(); fd.append("job_id", jobIdC); fd.append("action", "rotate"); fd.append("angle", 90);
  await fetch("/quick-action", { method: "POST", body: fd });
  showToast("Halaman diputar!");
});

const modal = document.getElementById("modal-wm");
document.getElementById("btn-watermark").addEventListener("click", () => modal.classList.add("active"));
document.getElementById("wm-cancel").addEventListener("click", () => modal.classList.remove("active"));
document.getElementById("wm-save").addEventListener("click", async () => {
  const text = document.getElementById("wm-text").value;
  modal.classList.remove("active");
  document.getElementById("img-preview-c").style.opacity = "0.5";
  const fd = new FormData(); fd.append("job_id", jobIdC); fd.append("action", "watermark"); fd.append("text", text);
  await fetch("/quick-action", { method: "POST", body: fd });
  document.getElementById("img-preview-c").style.opacity = "1";
  document.getElementById("img-preview-c").src = `/outputs/${jobIdC}_original.png?t=${Date.now()}`;
  document.getElementById("img-preview-c").style.transform = `rotate(${currentAngle}deg)`;
  showToast("Watermark ditambahkan!");
});

document.querySelectorAll(".radio-item").forEach(item => {
  item.addEventListener("click", () => {
    item.parentElement.querySelectorAll(".radio-item").forEach(i => i.classList.remove("selected"));
    item.classList.add("selected"); item.querySelector("input").checked = true;
  });
});

document.getElementById("btn-process-c").addEventListener("click", async () => {
  document.getElementById("btn-process-c").style.display = "none";
  document.getElementById("loading-c").style.display = "flex";
  const level = document.querySelector('input[name="level"]:checked').value;
  const fd = new FormData(); fd.append("job_id", jobIdC); fd.append("level", level);
  try {
    const res = await fetch("/compress", { method: "POST", body: fd });
    const data = await res.json();
    document.getElementById("loading-c").style.display = "none";
    document.getElementById("result-c").style.display = "block";
    document.getElementById("res-size-c").textContent = fmtSize(data.new_sz);
    document.getElementById("res-ratio-c").textContent = data.ratio + "%";
    document.getElementById("btn-download-c").href = `/download/${jobIdC}`;
    showToast("Kompresi selesai!");
  } catch(e) { showToast("Gagal kompres!", true); }
});

// ==========================================
// 2. FITUR MERGE PDF
// ==========================================
const filesMerge = document.getElementById("files-merge");
document.getElementById("btn-trigger-merge").addEventListener("click", () => filesMerge.click());
let mergeJobId = null;
let mergeFilesData = [];

filesMerge.addEventListener("change", async () => {
  if(filesMerge.files.length < 2) return showToast("Pilih minimal 2 file PDF.", true);
  document.getElementById("view-upload-merge").style.display = "none";
  document.getElementById("view-work-merge").style.display = "block";
  document.getElementById("grid-merge").innerHTML = "<p style='color:white'>Mengekstrak halaman...</p>";
  
  const fd = new FormData();
  for(let f of filesMerge.files) fd.append("files", f);
  
  try {
    const res = await fetch("/preview-merge", { method: "POST", body: fd });
    const data = await res.json();
    mergeJobId = data.job_id;
    const grid = document.getElementById("grid-merge");
    grid.innerHTML = "";
    data.previews.forEach((item, index) => {
      const div = document.createElement("div");
      div.className = "merge-item";
      div.innerHTML = `<img src="${item.img_url}" id="img-${index}" style="transform: rotate(0deg);" /><span class="page-num">File ${item.file_index + 1}</span><button class="btn-rotate-small" onclick="rotateMergeItem(${index})">↻</button>`;
      grid.appendChild(div);
      mergeFilesData.push({ file_index: item.file_index, rotate: 0 });
    });
  } catch(e) { showToast("Gagal ekstrak halaman.", true); }
});

function rotateMergeItem(index) {
  const img = document.getElementById(`img-${index}`);
  const newRot = (mergeFilesData[index].rotate + 90) % 360;
  mergeFilesData[index].rotate = newRot;
  img.style.transform = `rotate(${newRot}deg)`;
}

document.getElementById("btn-do-merge").addEventListener("click", async () => {
  document.getElementById("btn-do-merge").style.display = "none";
  document.getElementById("loading-merge").style.display = "flex";
  const fd = new FormData(); fd.append("job_id", mergeJobId); fd.append("order_json", JSON.stringify(mergeFilesData));
  try {
    const res = await fetch("/merge", { method: "POST", body: fd });
    const data = await res.json();
    document.getElementById("loading-merge").style.display = "none";
    document.getElementById("result-merge").style.display = "block";
    document.getElementById("btn-download-merge").href = `/download/${data.job_id}`;
    showToast("PDF berhasil digabung!");
  } catch(e) { showToast("Gagal gabung!", true); }
});

// ==========================================
// 3. FITUR JPG TO PDF
// ==========================================
const filesJpg = document.getElementById("files-jpg");
document.getElementById("btn-trigger-jpg").addEventListener("click", () => filesJpg.click());
let jpgJobId = null;
let jpgFilesData = [];

filesJpg.addEventListener("change", async () => {
  if(filesJpg.files.length === 0) return;
  document.getElementById("view-upload-jpg").style.display = "none";
  document.getElementById("view-work-jpg").style.display = "block";
  document.getElementById("grid-jpg").innerHTML = "<p style='color:white'>Memuat gambar...</p>";
  
  const fd = new FormData();
  for(let f of filesJpg.files) fd.append("files", f);
  
  try {
    const res = await fetch("/preview-image", { method: "POST", body: fd });
    const data = await res.json();
    jpgJobId = data.job_id;
    const grid = document.getElementById("grid-jpg");
    grid.innerHTML = "";
    data.previews.forEach((item, index) => {
      const div = document.createElement("div");
      div.className = "merge-item";
      div.innerHTML = `<img src="${item.img_url}" id="img-jpg-${index}" style="transform: rotate(0deg);" /><span class="page-num">Gambar ${index + 1}</span><button class="btn-rotate-small" onclick="rotateJpgItem(${index})">↻</button>`;
      grid.appendChild(div);
      jpgFilesData.push({ file_index: item.file_index, ext: item.ext, rotate: 0 });
    });
  } catch(e) { showToast("Gagal memuat gambar.", true); }
});

function rotateJpgItem(index) {
  const img = document.getElementById(`img-jpg-${index}`);
  const newRot = (jpgFilesData[index].rotate + 90) % 360;
  jpgFilesData[index].rotate = newRot;
  img.style.transform = `rotate(${newRot}deg)`;
}

document.getElementById("btn-do-jpg").addEventListener("click", async () => {
  document.getElementById("btn-do-jpg").style.display = "none";
  document.getElementById("loading-jpg").style.display = "flex";
  const fd = new FormData(); fd.append("job_id", jpgJobId); fd.append("order_json", JSON.stringify(jpgFilesData));
  try {
    const res = await fetch("/convert-images", { method: "POST", body: fd });
    const data = await res.json();
    document.getElementById("loading-jpg").style.display = "none";
    document.getElementById("result-jpg").style.display = "block";
    document.getElementById("btn-download-jpg").href = `/download/${data.job_id}`;
    showToast("Konversi ke PDF berhasil!");
  } catch(e) { showToast("Gagal konversi!", true); }
});

// ==========================================
// 4. FITUR HAPUS HALAMAN (DELETE)
// ==========================================
const fileDelete = document.getElementById("file-delete");
document.getElementById("btn-trigger-delete").addEventListener("click", () => fileDelete.click());
let delJobId = null;
let delPagesData = []; // Array of boolean (true = keep, false = delete)

fileDelete.addEventListener("change", async () => {
  if(fileDelete.files.length === 0) return;
  document.getElementById("view-upload-delete").style.display = "none";
  document.getElementById("view-work-delete").style.display = "block";
  document.getElementById("grid-delete").innerHTML = "<p style='color:white'>Mengekstrak halaman...</p>";
  
  const fd = new FormData(); fd.append("file", fileDelete.files[0]);
  
  try {
    const res = await fetch("/preview-pages", { method: "POST", body: fd });
    const data = await res.json();
    delJobId = data.job_id;
    const grid = document.getElementById("grid-delete");
    grid.innerHTML = "";
    data.previews.forEach((item, index) => {
      const div = document.createElement("div");
      div.className = "merge-item";
      div.id = `del-item-${index}`;
      div.onclick = () => toggleDeletePage(index);
      div.innerHTML = `<img src="${item.img_url}" /><span class="page-num">Hal ${index + 1}</span>`;
      grid.appendChild(div);
      delPagesData.push(true); // Default: simpan semua
    });
  } catch(e) { showToast("Gagal ekstrak halaman.", true); }
});

function toggleDeletePage(index) {
  delPagesData[index] = !delPagesData[index]; // Toggle
  const item = document.getElementById(`del-item-${index}`);
  if (delPagesData[index]) {
    item.classList.remove("selected-for-delete");
  } else {
    item.classList.add("selected-for-delete");
  }
}

document.getElementById("btn-do-delete").addEventListener("click", async () => {
  // Cari index yang nilainya true (disimpan)
  const keepIndices = delPagesData.map((keep, i) => keep ? i : -1).filter(i => i !== -1);
  if(keepIndices.length === 0) return showToast("Minimal simpan 1 halaman!", true);
  
  document.getElementById("btn-do-delete").style.display = "none";
  document.getElementById("loading-delete").style.display = "flex";
  
  const fd = new FormData(); 
  fd.append("job_id", delJobId); 
  fd.append("keep_json", JSON.stringify(keepIndices));
  
  try {
    const res = await fetch("/delete-pages", { method: "POST", body: fd });
    const data = await res.json();
    document.getElementById("loading-delete").style.display = "none";
    document.getElementById("result-delete").style.display = "block";
    document.getElementById("btn-download-delete").href = `/download/${data.job_id}`;
    showToast("Halaman berhasil dihapus!");
  } catch(e) { showToast("Gagal menghapus halaman!", true); }
});
