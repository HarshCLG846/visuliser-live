from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import json
import os
import io
import shutil
import uuid
from typing import Dict, Any

# Import existing backend logic
from backend.architectural_visualizer import (
    PRODUCT_CATALOG,
    validate_selection,
    build_backend_products_json,
    edit_image,
    generate_and_save_mask
)

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# STATIC FILES SERVING (Frontend Integration)
# -----------------------------------------------------------------------------
# Mount the static directory (built frontend) to /static
# We explicitly check if directory exists to avoid crashes during development if not built yet
if os.path.isdir("static"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

# Serve index.html for root path and any other path (SPA routing)
# We will define this at the END of the file to avoid conflicts.



# -----------------------------------------------------------------------------
# PRODUCT MAPPING LAYER
# -----------------------------------------------------------------------------
# Maps Frontend "Product Name" -> Backend Product ID
FRONTEND_TO_BACKEND_MAP = {
    # Trim
    "Ridge Cap": 1,
    "Rake & Corner": 2,  # Maps to "Rake Corner"
    "J Channel": 3,      # Maps to "J-Channel"
    "Corner Trim": 4,    # Map to "Rake Corner" (best fit)
    # "Fascia Board": 4,   # Map to "Metal Trim" (best fit)

    # Roofing
    "Leakguard Panel": 5,
    "Legacy Panel": 6,
    "Classic Panel": 7,  # Ambiguity: Frontend has Classic Panel in both lists.
                         # Context usually handles it, but unique names preferred.
                         # If in "Roofing" category, it maps to 7.
    "Standing Seam": 8,  # Maps to "Standing Seam Panel"

    # Siding (Check `architectural_visualizer.py` IDs 9-12)
    # 9: Wood Grain (Light), 10: Wood Grain (Dark), 11: Board & Batten (Grey), 12: Concealed Fastener
    "Board & Batten": 11,
    "Concealed Fastener Board & Batten": 12,
    "Traditional Panel": 9, # Correctly maps to "Traditional Panel" (Light Wood) in backend
    # "Classic Panel" (Siding) -> handled in logic by checking category?
}

def resolve_frontend_selection(user_selections: Dict[str, Any]) -> Dict[str, int]:
    """
    Translates frontend selections (names/structure) to backend format (category -> ID).
    Expected Frontend user_selections structure:
    {
       "roof": { "product_name": "Legacy Panel", ... },
       "siding": { "product_name": "Board & Batten", ... },
       "trim": { "product_name": "Ridge Cap", ... }
    }
    """
    backend_selection = {}

    for category, item_data in user_selections.items():
        # Frontend sends lowercase categories: 'roof', 'siding', 'trim'
        # item_data is dict with 'product_name'
        if not item_data or 'product_name' not in item_data:
            continue

        p_name = item_data['product_name']
        p_id = FRONTEND_TO_BACKEND_MAP.get(p_name)

        # Special handling for "Classic Panel" which appears in both keys
        if p_name == "Classic Panel":
            if category == "roof":
                p_id = 7
            elif category == "siding":
                p_id = 10 # Mapping Siding Classic Panel to Classic Panel (Dark Wood - ID 10)

        if p_id:
            backend_selection[category] = p_id
        else:
            print(f"⚠️ Warning: Could not map frontend product '{p_name}' in category '{category}'")

    return backend_selection

# -----------------------------------------------------------------------------
# ENDPOINTS
# -----------------------------------------------------------------------------

@app.get("/")
def home():
    # Serve React Frontend
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "Backend running, but frontend not built. Run render-build.sh"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze-exterior")
async def analyze_exterior_endpoint(
    file: UploadFile = File(...),
    user_selections: str = Form("{}")
):
    """
    Mock analysis endpoint to satisfy frontend requirement.
    Real analysis happens during edit in current architectural_visualizer logic.
    """
    return {
        "valid_exterior_image": True,
        # "image_analysis": {
        #     "roof": {"detected": True, "confidence": 0.95},
        #     "siding": {"detected": True, "confidence": 0.90},
        #     "trim": {"detected": True, "confidence": 0.85}
        # }
    }

@app.post("/edit-image")
async def edit_image_api(
    file: UploadFile = File(...),
    analysis_results: str = Form(default="{}"), # Not used by current backend logic
    user_selections: str = Form(...)
):
    temp_input_path = f"temp_{uuid.uuid4()}.jpg"
    temp_mask_path = f"mask_{uuid.uuid4()}.png"

    try:
        # 1. Save uploaded file
        with open(temp_input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Parse selections & Resolve IDs
        selections_dict = json.loads(user_selections)
        print(f"📥 Received Selections: {selections_dict}")

        backend_selection_ids = resolve_frontend_selection(selections_dict)
        print(f"🔄 Mapped to Backend IDs: {backend_selection_ids}")

        if not backend_selection_ids:
             raise HTTPException(status_code=400, detail="No valid products selected.")

        # 3. Validate & Build Products JSON (using existing backend logic)
        ok, msg, resolved = validate_selection(backend_selection_ids)
        if not ok:
            raise HTTPException(status_code=400, detail=f"Selection validation failed: {msg}")

        products_json = build_backend_products_json(resolved)

        # 4. Generate Mask (Using existing AI Logic)
        print("🤖 Generating mask...")
        generate_and_save_mask(temp_input_path, products_json, temp_mask_path)
        
        # Ensure 'mask.png' exists for edit_image if it hardcodes it (it does in line 431)
        # We need to temporarily rename or copy our mask to 'mask.png' if function isn't flexible
        # Checking architectural_visualizer.py line 431: open("mask.png", "rb")
        # I must overwrite "mask.png" in CWD or patch the function.
        # Since strict rule "Do NOT rewrite architectural_visualizer logic", I must put the file where it expects.
        if os.path.exists("mask.png"):
             os.remove("mask.png")
        shutil.copy(temp_mask_path, "mask.png")

        # 5. Edit Image (Using existing AI Logic)
        print("🎨 Editing image...")
        output_image_bytes = edit_image(temp_input_path, products_json)

        # 6. Return Result
        return StreamingResponse(
            io.BytesIO(output_image_bytes),
            media_type="image/jpeg"
        )

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)
        if os.path.exists(temp_mask_path):
            os.remove(temp_mask_path)
        # Optional: keep or delete standard 'mask.png'

# -----------------------------------------------------------------------------
# SPA CATCH-ALL ROUTE (MUST BE LAST)
# -----------------------------------------------------------------------------
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    # This matches any path not matched by specific API routes above.
    # Try to find a static file first (in case it wasn't in /assets)
    potential_file_path = os.path.join("static", full_path)
    if os.path.isfile(potential_file_path):
        return FileResponse(potential_file_path)
        
    # Otherwise return index.html for client-side routing
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return {"error": "Frontend not found"}

