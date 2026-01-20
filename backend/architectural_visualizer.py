"""
Architectural Visualization System - Single File Implementation

Complete backend catalog management and OpenAI Image Edit API integration
for professional house/garage exterior renovations.

Usage:
1. Run: python architectural_visualizer.py
2. Follow prompts to select products and edit image
"""

import os
import base64
import json
# import importlib.util
from PIL import Image
from io import BytesIO
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from openai import OpenAI
# import requests

# =============================================================================
# PRODUCT CATALOG
# =============================================================================
PRODUCT_CATALOG = {
    1: {
        "name": "Ridge Cap",
        "category": "trim",
        "region": "ridge",
        "editable": True,
        "prompt": {
            "color": "dark charcoal black",
            "texture": "smooth metal surface",
            "finish": "matte to low sheen",
            "look": "clean sharp folded edges"
        }
    },

    2: {
        "name": "Rake & Corner",
        "category": "trim",
        "region": "rake",
        "editable": True,
        "prompt": {
            "color": "dark charcoal black",
            "texture": "smooth with slight linear folds",
            "finish": "matte",
            "look": "defined corner profile"
        }
    },

    3: {
        "name": "J Channel",
        "category": "trim",
        "region": "trim_edge",
        "editable": True,
        "prompt": {
            "color": "black",
            "texture": "smooth flat metal",
            "finish": "matte",
            "look": "simple clean edge trim"
        }
    },

    4: {
        "name": "Corner Trim",
        "category": "trim",
        "region": "trim_edge",
        "editable": True,
        "prompt": {
            "color": "black",
            "texture": "smooth surface",
            "finish": "matte",
            "look": "straight flat flashing"
        }
    },

    5: {
        "name": "Leakguard Panel",
        "category": "roofing",
        "region": "roof",
        "editable": True,
        "prompt": {
            "color": "maroon brick red",
            "texture": "ribbed metal profile",
            "finish": "matte painted coating",
            "look": "traditional exposed fastener metal panel"
        }
    },

    6: {
        "name": "Legacy Panel",
        "category": "roofing",
        "region": "roof",
        "editable": True,
        "prompt": {
            "color": "dark green",
            "texture": "deep ribbed metal pattern",
            "finish": "matte",
            "look": "strong industrial appearance"
        }
    },

    7: {
        "name": "Classic Panel",
        "category": "roofing",
        "region": "roof",
        "editable": True,
        "prompt": {
            "color": "rust red",
            "texture": "symmetrical raised ribs",
            "finish": "matte",
            "look": "classic metal roofing style"
        }
    },

    8: {
        "name": "Standing Seam",
        "category": "roofing",
        "region": "roof",
        "editable": True,
        "prompt": {
            "color": "light grey",
            "texture": "smooth vertical seams",
            "finish": "matte soft satin",
            "look": "modern premium clean lines"
        }
    },

    9: {
        "name": "Traditional Panel",
        "category": "siding",
        "region": "siding",
        "editable": True,
        "prompt": {
            "color": "light golden oak honey wood tone",
            "texture": "printed wood grain with vertical lines",
            "finish": "matte",
            "look": "natural wood appearance on metal panel"
        }
    },

    10: {
        "name": "Classic Panel",
        "category": "siding",
        "region": "siding",
        "editable": True,
        "prompt": {
            "color": "rust red",
            "texture": "symmetrical raised ribs",
            "finish": "matte",
            "look": "classic metal siding style"
        }
    },
    11: {
        "name": "Board & Batten",
        "category": "siding",
        "region": "siding",
        "editable": True,
        "prompt": {
            "color": "light grey",
            "texture": "vertical board and batten pattern with subtle grain",
            "finish": "matte",
            "look": "modern architectural board and batten metal siding"
        }
    },12: {
        "name": "Concealed Fastener Board & Batten",
        "category": "siding",
        "region": "siding",
        "editable": True,
        "prompt": {
            "color": "dark brown woodgrain with reddish undertone",
            "texture": "detailed wood grain with vertical flow",
            "finish": "matte",
            "look": "premium concealed fastener board and batten metal siding"
        }
    },
    # Hardware (not visually editable)
    13: {
        "name": "Roofing Screw (Washer Head)",
        "category": "hardware",
        "region": "hardware",
        "editable": False,
        "prompt": {
            "color": "silver",
            "texture": "metallic",
            "finish": "matte",
            "look": "standard roofing screw"
        }
    },

    14: {
        "name": "Fastener Screw (Wood Screw)",
        "category": "hardware",
        "region": "hardware",
        "editable": False,
        "prompt": {
            "color": "silver",
            "texture": "metallic",
            "finish": "matte",
            "look": "standard wood screw"
        }
    },

    15: {
        "name": "Concealed Fastener Clip",
        "category": "hardware",
        "region": "hardware",
        "editable": False,
        "prompt": {
            "color": "silver",
            "texture": "metallic",
            "finish": "matte",
            "look": "concealed fastener clip"
        }
    },

    16: {
        "name": "Roof Sealant / Adhesive Cartridge",
        "category": "hardware",
        "region": "hardware",
        "editable": False,
        "prompt": {
            "color": "clear",
            "texture": "gel",
            "finish": "glossy",
            "look": "sealant cartridge"
        }
    }
}

# =============================================================================
# BACKEND CATALOG MANAGEMENT
# =============================================================================

UI_CATEGORIES = ("roof", "siding", "trim", "hardware")

_CATEGORY_UI_MAP = {
    "roofing": "roof",
    "siding": "siding",
    "trim": "trim",
    "roof_trim": "trim",
    "hardware": "hardware",
}

@dataclass
class ResolvedProduct:
    id: int
    name: str
    ui_category: str
    region: str
    prompt: Dict

def _to_ui_category(product_category: str) -> Optional[str]:
    return _CATEGORY_UI_MAP.get(product_category)

def get_catalog_options() -> Dict[str, List[Dict]]:
    options = {"roof": [], "siding": [], "trim": [], "hardware": []}
    for pid, p in PRODUCT_CATALOG.items():
        ui_cat = _to_ui_category(p.get("category", ""))
        if ui_cat in options:
            options[ui_cat].append({"id": pid, "name": p["name"]})
    for k in options:
        options[k].sort(key=lambda x: x["name"].lower())
    return options

def _resolve_product(pid: int) -> Optional[ResolvedProduct]:
    p = PRODUCT_CATALOG.get(pid)
    if not p or not p.get("editable", False):
        return None
    ui_cat = _to_ui_category(p.get("category", ""))
    if ui_cat not in UI_CATEGORIES:
        return None
    return ResolvedProduct(
        id=pid,
        name=p["name"],
        ui_category=ui_cat,
        region=p.get("region", ui_cat),
        prompt=p.get("prompt", {}),
    )

def validate_selection(selection: Dict[str, int]) -> Tuple[bool, str, Dict[str, ResolvedProduct]]:
    resolved = {}
    for key in selection.keys():
        if key not in UI_CATEGORIES:
            return False, f"Invalid selection key '{key}'. Allowed: {', '.join(UI_CATEGORIES)}", {}
    for ui_cat in UI_CATEGORIES:
        pid = selection.get(ui_cat)
        if pid is None:
            continue
        rp = _resolve_product(pid)
        if rp is None:
            return False, f"Invalid or non-editable product id {pid} for category '{ui_cat}'", {}
        if rp.ui_category != ui_cat:
            return False, f"Product '{rp.name}' (id {pid}) does not belong to '{ui_cat}' category", {}
        resolved[ui_cat] = rp
    VISUAL_CATEGORIES = ("roof", "siding", "trim")
    has_visual = any(k in resolved for k in VISUAL_CATEGORIES)
    if not has_visual:
        return False, "Select at least one visual product (roof, siding, trim).", {}
    return True, "Selection is valid.", resolved

def build_backend_products_json(resolved: Dict[str, ResolvedProduct]) -> Dict:
    payload = {"roof": None, "siding": None, "trim": None, "hardware": None}
    for ui_cat, rp in resolved.items():
        p = rp.prompt or {}
        payload[ui_cat] = {
            "product_id": rp.id,
            "product_name": rp.name,
            "region": rp.region,
            "attributes": {
                "color": p.get("color"),
                "texture": p.get("texture"),
                "finish": p.get("finish"),
                "pattern_or_look": p.get("look"),
            },
        }
    return payload

# =============================================================================
# OPENAI IMAGE EDIT INTEGRATION
# =============================================================================

# Initialize OpenAI client (lazy loading)
_client = None

def get_openai_client():
    global _client
    if _client is None:
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set")
        _client = OpenAI()
    return _client

def build_edit_prompt(products_json: Dict[str, Any]) -> str:
    # SYSTEM INTENT
    system_intent = (
        "You are a professional architectural renovation AI specializing in house and garage exterior visualization. "
        "You create realistic renovation previews by applying construction products to specific architectural regions."
    )

    # TASK INSTRUCTIONS
    task_parts = []
    if products_json.get("roof"):
        roof = products_json["roof"]
        attrs = roof["attributes"]
        task_parts.append(f"Change the roof to {attrs['color']} {attrs['texture']} {attrs['finish']} {attrs['pattern_or_look']}. Apply only to roof surfaces.")
    if products_json.get("siding"):
        siding = products_json["siding"]
        attrs = siding["attributes"]
        task_parts.append(f"Change the siding/walls to {attrs['color']} {attrs['texture']} {attrs['finish']} {attrs['pattern_or_look']}. Apply only to wall/siding areas.")
    if products_json.get("trim"):
        trim = products_json["trim"]
        attrs = trim["attributes"]
        task_parts.append(f"Change the trim (fascia, edges, corners, rake, ridge) to {attrs['color']} {attrs['texture']} {attrs['finish']} {attrs['pattern_or_look']}. Apply only to trim regions.")

    task_instructions = " ".join(task_parts) if task_parts else "No changes requested."

    # STRICT RULES
    strict_rules = (
    # "REGION LOCK RULE: "
    # "Treat the input image as a locked real photograph. "
    # "Only repaint pixels belonging to the specified architectural surfaces. "
    # "Do NOT reinterpret, redraw, or regenerate any object. "

    # "STRUCTURE PRESERVATION RULE: "
    # "The building structure must remain EXACTLY as in the original image. "
    # "No geometry changes, no added or removed elements, no redesign. "

    # "MATERIAL CHANGE ONLY RULE: "
    # "Only replace surface material appearance (color, texture, finish). "
    # "No shape, depth, or structural changes. "

    # "SIDING ORIENTATION RULE: "
    # "Preserve original siding direction exactly. "

    # "BACKGROUND LOCK RULE: "
    # "Cars, sky, trees, ground, driveway, windows, doors, shadows, reflections "
    # "must remain pixel-identical to the original image. "

    # "EDIT MODE ONLY: "
    # "This is NOT an image generation task. "
    # "This is an in-place material overlay on an existing photo. "

    # "If a region is unclear or not visible, do not modify it."
    "Apply edits strictly only to the provided mask regions."
    "Preserve original house geometry, perspective, camera angle, natural lighting, shadows. "
    "Do not modify sky, ground, driveway, plants, trees, or background elements."
    "Match product attributes exactly. Clean edges, realistic blending, professional contractor-level output. "
    "Real exterior renovation preview, no artistic or illustrated styles. "
    "If any region is unclear or not visible, do not modify it."
)

    # Combine all parts
    full_prompt = f"{system_intent}\n\nTASK: {task_instructions}\n\nRULES: {strict_rules}"

    # Logging for debugging
    print(f"Generated prompt: {full_prompt}")

    return full_prompt

# def edit_image(image_path: str, products_json: Dict[str, Any]) -> bytes:
    # if not os.path.exists(image_path):
    #     raise ValueError(f"Image file not found: {image_path}")

    # prompt = build_edit_prompt(products_json)
    # client = get_openai_client()

    # with open(image_path, "rb") as img_file:
    #     response = client.images.edit(
    #         model="gpt-image-1",
    #         prompt=prompt,
    #         image=img_file,
    #         size="1024x1024"
    #     )

    # image_base64 = response.data[0].b64_json
    # return base64.b64decode(image_base64)
def edit_image(image_path: str, products_json: Dict[str, Any]) -> bytes:
    if not os.path.exists(image_path):
        raise ValueError(f"Image file not found: {image_path}")

    # 🔹 Read original image size
    original_img = Image.open(image_path)
    original_width, original_height = original_img.size

    prompt = build_edit_prompt(products_json)
    client = get_openai_client()

    with open(image_path, "rb") as img_file, open("mask.png", "rb") as mask_file:
        response = client.images.edit(
            model="gpt-image-1",
            prompt=prompt,
            image=img_file,
             mask=mask_file
        )

    image_base64 = response.data[0].b64_json
    edited_bytes = base64.b64decode(image_base64)

    # 🔹 Resize back to original size (no AI look)
    edited_img = Image.open(BytesIO(edited_bytes))
    edited_img = edited_img.resize(
        (original_width, original_height),
        Image.LANCZOS
    )

    final_buffer = BytesIO()
    edited_img.save(final_buffer, format="JPEG", quality=95)

    return final_buffer.getvalue()


def save_edited_image(image_bytes: bytes, output_path: str) -> None:
    with open(output_path, "wb") as f:
        f.write(image_bytes)

def preview_image(image_path: str) -> None:
    """Open the image file with default system viewer."""
    try:
        import subprocess
        import platform
        if platform.system() == "Windows":
            subprocess.run(["start", image_path], shell=True, check=True)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", image_path], check=True)
        else:  # Linux
            subprocess.run(["xdg-open", image_path], check=True)
        print(f"✅ Image opened for preview: {image_path}")
    except Exception as e:
        print(f"⚠️  Could not auto-open image: {e}")
        print(f"📁 Please manually open: {image_path}")


def build_mask_prompt(products_json: Dict[str, Any]) -> str:
    parts = []
    if products_json.get("roof"):
        parts.append("Highlight roof areas in solid white.")
    if products_json.get("siding"):
        parts.append("Highlight wall and siding areas in solid white.")
    if products_json.get("trim"):
        parts.append("Highlight trim, fascia, rake, ridge edges in solid white.")

    task = " ".join(parts)

    return (
        "Generate a black and white segmentation mask image. "
        "White = editable architectural regions. "
        "Black = everything else (sky, ground, background). "
        f"{task} "
        "No textures, no colors, no shading. Flat binary mask."
    )
# def generate_and_save_mask(image_path: str, products_json: Dict[str, Any], mask_path: str) -> None:
    # client = get_openai_client()
    # prompt = build_mask_prompt(products_json)

    # with open(image_path, "rb") as img_file:
    #     response = client.images.edit(
    #         model="gpt-image-1",
    #         prompt=prompt,
    #         image=img_file,
    #         size="1024x1024"
    #     )

    # mask_base64 = response.data[0].b64_json
    # mask_bytes = base64.b64decode(mask_base64)

    # with open(mask_path, "wb") as f:
    #     f.write(mask_bytes)

    # print(f"🩶 Mask image saved to {mask_path}")
def generate_and_save_mask(image_path: str, products_json: Dict[str, Any], mask_path: str) -> None:
    client = get_openai_client()
    prompt = build_mask_prompt(products_json)

    original_img = Image.open(image_path)
    original_width, original_height = original_img.size

    with open(image_path, "rb") as img_file:
        response = client.images.edit(
            model="gpt-image-1",
            prompt=prompt,
            image=img_file
        )

    mask_base64 = response.data[0].b64_json
    mask_bytes = base64.b64decode(mask_base64)

    # Convert to RGBA
    mask_img = Image.open(BytesIO(mask_bytes)).convert("RGBA")
    mask_img = mask_img.resize((original_width, original_height), Image.NEAREST)

    pixels = mask_img.load()
    for y in range(mask_img.height):
        for x in range(mask_img.width):
            r, g, b, a = pixels[x, y]
            if r > 200 and g > 200 and b > 200:
                pixels[x, y] = (255, 255, 255, 255)  # editable
            else:
                pixels[x, y] = (0, 0, 0, 0)          # transparent lock

    mask_img.save(mask_path, format="PNG")
    print(f"🩶 Mask image saved to {mask_path} (RGBA)")


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    print("=== Architectural Visualization System ===\n")

    # Show options
    options = get_catalog_options()
    print("Available Products:")
    for category, products in options.items():
        print(f"\n{category.upper()}:")
        for product in products:
            print(f"  {product['id']}: {product['name']}")

    # Get user selection
    selection = {}
    for cat in ["roof", "siding", "trim", "hardware"]:
        while True:
            try:
                pid = int(input(f"\nEnter {cat} product ID (or 0 to skip): "))
                if pid == 0:
                    break
                if any(p['id'] == pid for p in options[cat]):
                    selection[cat] = pid
                    break
                else:
                    print("Invalid ID for this category.")
            except ValueError:
                print("Please enter a number.")

    # Validate
    ok, msg, resolved = validate_selection(selection)
    if not ok:
        print(f"Selection error: {msg}")
        return

    print(f"\nSelection valid: {msg}")

    # Build products JSON
    products_json = build_backend_products_json(resolved)
    print("\nProducts JSON:")
    print(json.dumps(products_json, indent=2))

    # Image editing
    image_path = "sample.png"
    if not image_path:
        print("No image provided.")
        return

    try:
        print("🩶 Generating automatic mask...")
        mask_path = "mask.png"
        generate_and_save_mask(image_path, products_json, mask_path)

        print("🎨 Editing image with OpenAI...")
        edited_bytes = edit_image(image_path, products_json)

        output_path = "edited_sample.jpg"
        save_edited_image(edited_bytes, output_path)

        print(f"✅ Edited image saved to {output_path}")
        print(f"✅ Mask image saved to {mask_path}")

        preview_choice = input("Preview edited image now? (y/n, default: y): ").strip().lower()
        if preview_choice in ['', 'y', 'yes']:
            preview_image(output_path)

    except Exception as e:
        print(f"❌ Image editing failed: {e}")


if __name__ == "__main__":
    main()
