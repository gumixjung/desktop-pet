# Desktop Pet 🐱

แมวเดินบน desktop ด้วย Python + pywebview (WKWebView)

## Requirements

```bash
python3 -m venv venv
source venv/bin/activate
pip install pywebview Pillow
```

## วิธีใช้

### 1. เตรียม Sprites

วาง `image.png` (sprite sheet 4 frame แนวนอน) ไว้ใน folder นี้ แล้วรัน:

```bash
python3 import_sprites.py
```

จะสร้างไฟล์ใน `sprites/` อัตโนมัติ:
- `walk_r_1.png` ถึง `walk_r_4.png` (เดินขวา)
- `walk_l_1.png` ถึง `walk_l_4.png` (เดินซ้าย — flip อัตโนมัติ)
- `sit_1.png`, `sit_2.png` (นั่ง + กะพริบตา)

### 2. รัน Desktop Pet

```bash
source venv/bin/activate
python3 desktop_pet.py
```

## การใช้งาน

| Action | ผล |
|--------|-----|
| ลากแมว | ย้ายตำแหน่ง |
| ปิด | ปิด terminal หรือ Ctrl+C |

## ปรับแต่ง

แก้ค่าต้นไฟล์ `desktop_pet.py`:

| ค่า | default | ความหมาย |
|-----|---------|----------|
| `CAT_H` | `120` | ขนาดแมว (px) |
| `SPEED` | `4` | ความเร็วเดิน |
| `FPS` | `8` | ความเร็ว animation |

## Prompt สำหรับ generate รูปแมว

```
Cute chibi orange tabby cat walking cycle, 4 frames side view,
transparent background, flat vector style, simple shapes,
sprite sheet layout 4 columns 1 row, PNG format
```

## โครงสร้างไฟล์

```
desktop-pet/
├── desktop_pet.py      # main app
├── import_sprites.py   # slice sprite sheet → sprites/
├── make_sprites.py     # สร้าง pixel art sprite (ถ้าไม่มีรูป)
├── image.png           # sprite sheet ต้นฉบับ
└── sprites/
    ├── walk_r_1.png … walk_r_4.png
    ├── walk_l_1.png … walk_l_4.png
    └── sit_1.png, sit_2.png
```
