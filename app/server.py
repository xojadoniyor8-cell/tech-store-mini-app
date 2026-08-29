import os
import sqlite3
import uuid
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

BASE_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = BASE_DIR / "web"
UPLOAD_DIR = BASE_DIR / "uploads"
DB_PATH = BASE_DIR / "products.db"

UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Tech Store")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT DEFAULT '',
            image TEXT DEFAULT ''
        )
    """)

    conn.commit()
    conn.close()


init_db()

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/")
async def home():
    index = WEB_DIR / "index.html"

    if index.exists():
        return FileResponse(index)

    return {
        "status": "online",
        "message": "Tech Store API ishlayapti"
    }


@app.get("/api/products")
async def get_products():
    conn = get_db()

    products = conn.execute(
        "SELECT * FROM products ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return [dict(product) for product in products]


@app.post("/api/products")
async def add_product(
    name: str = Form(...),
    price: str = Form(...),
    category: str = Form(...),
    description: str = Form(""),
    image: UploadFile | None = File(None)
):
    image_url = ""

    if image and image.filename:
        extension = Path(image.filename).suffix.lower()

        allowed = {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        }

        if extension not in allowed:
            return {
                "success": False,
                "error": "Faqat JPG, JPEG, PNG yoki WEBP rasm yuklash mumkin."
            }

        filename = f"{uuid.uuid4().hex}{extension}"
        file_path = UPLOAD_DIR / filename

        content = await image.read()

        with open(file_path, "wb") as f:
            f.write(content)

        image_url = f"/uploads/{filename}"

    conn = get_db()

    cursor = conn.execute(
        """
        INSERT INTO products
        (name, price, category, description, image)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            name,
            price,
            category,
            description,
            image_url
        )
    )

    conn.commit()

    product_id = cursor.lastrowid

    conn.close()

    return {
        "success": True,
        "id": product_id,
        "message": "Mahsulot qo‘shildi"
    }


@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int):
    conn = get_db()

    product = conn.execute(
        "SELECT image FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if not product:
        conn.close()

        return {
            "success": False,
            "error": "Mahsulot topilmadi"
        }

    if product["image"]:
        image_path = BASE_DIR / product["image"].lstrip("/")

        if image_path.exists():
            image_path.unlink()

    conn.execute(
        "DELETE FROM products WHERE id = ?",
        (product_id,)
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Mahsulot o‘chirildi"
    }


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }
