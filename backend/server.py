"""
Phantom Folders — FastAPI Backend Server
Provides REST endpoints for the encrypted file explorer.
Cross-platform: Windows, macOS, Linux.
"""

import io
import os
import sys
import platform
import subprocess
import tempfile
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, Header, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel
from typing import Optional

from . import auth, vault_manager

app = FastAPI(title="Phantom Folders API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory tracking of opened vaults per session
# token -> { vault_id: { "password": str, "is_decoy": bool } }
opened_vaults = {}


def get_session(x_session_token: str = Header(None)):
    if not x_session_token or not auth.validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return x_session_token


# --- Request Models ---

class SetupRequest(BaseModel):
    password: str

class LoginRequest(BaseModel):
    password: str

class VaultCreateRequest(BaseModel):
    name: str
    password: str
    decoy_password: Optional[str] = None

class VaultOpenRequest(BaseModel):
    password: str

class VaultDeleteRequest(BaseModel):
    password: str

class FolderCreateRequest(BaseModel):
    name: str
    parent_id: str

class RenameRequest(BaseModel):
    name: str

class DecoyRequest(BaseModel):
    current_password: str
    decoy_password: str

class DecoyRemoveRequest(BaseModel):
    password: str


# --- Auth Endpoints ---

@app.get("/api/ping")
async def ping():
    return {"status": "ok", "platform": platform.system()}


@app.get("/api/system/profile")
async def get_system_profile():
    """
    Returns isolated system hardware profile and local enclave telemetry.
    """
    from .storage_path import get_system_identity
    return get_system_identity()


@app.get("/api/auth/status")
async def auth_status(x_session_token: str = Header(None)):
    is_set = auth.is_master_set()
    is_auth = False
    if x_session_token:
        is_auth = auth.validate_session(x_session_token)
    return {"master_set": is_set, "authenticated": is_auth}


@app.post("/api/auth/setup")
async def auth_setup(req: SetupRequest):
    try:
        auth.setup_master_password(req.password)
        token = auth.verify_master_password(req.password)
        return {"token": token, "status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/login")
async def auth_login(req: LoginRequest):
    try:
        token = auth.verify_master_password(req.password)
        return {"token": token}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/api/auth/logout")
async def auth_logout(token: str = Depends(get_session)):
    auth.invalidate_session(token)
    opened_vaults.pop(token, None)
    return {"status": "success"}


# --- Vault Endpoints ---

@app.get("/api/vaults")
async def list_vaults(token: str = Depends(get_session)):
    return await vault_manager.list_vaults()


@app.get("/api/storage/metrics")
async def get_storage_metrics(token: str = Depends(get_session)):
    """
    Returns 2.0 TB Cluster storage telemetry, usage metrics, and file/vault stats.
    """
    try:
        return await vault_manager.get_storage_metrics()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/vaults")
async def create_vault(req: VaultCreateRequest, token: str = Depends(get_session)):
    try:
        res = await vault_manager.create_vault(req.name, req.password, req.decoy_password)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/vaults/{vault_id}/open")
async def open_vault(vault_id: str, req: VaultOpenRequest, token: str = Depends(get_session)):
    try:
        info = await vault_manager.open_vault(vault_id, req.password)
        if token not in opened_vaults:
            opened_vaults[token] = {}
        opened_vaults[token][vault_id] = {
            "password": req.password,
            "is_decoy": info["is_decoy"]
        }
        return {"is_decoy": info["is_decoy"]}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/api/vaults/{vault_id}/lock")
async def lock_vault(vault_id: str, token: str = Depends(get_session)):
    if token in opened_vaults and vault_id in opened_vaults[token]:
        del opened_vaults[token][vault_id]
    await vault_manager.lock_vault(vault_id)
    return {"status": "success"}


@app.delete("/api/vaults/{vault_id}")
async def delete_vault(vault_id: str, req: VaultDeleteRequest, token: str = Depends(get_session)):
    try:
        await vault_manager.delete_vault(vault_id, req.password)
        if token in opened_vaults:
            opened_vaults[token].pop(vault_id, None)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _get_vault_ctx(token: str, vault_id: str):
    if token not in opened_vaults or vault_id not in opened_vaults[token]:
        raise HTTPException(status_code=403, detail="Vault is locked")
    return opened_vaults[token][vault_id]


# --- File Endpoints ---

@app.get("/api/vaults/{vault_id}/files")
async def list_files(vault_id: str, parent_id: str = "root", token: str = Depends(get_session)):
    ctx = _get_vault_ctx(token, vault_id)
    try:
        files = await vault_manager.list_files(vault_id, parent_id, ctx["password"], ctx["is_decoy"])
        return files
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/vaults/{vault_id}/files/folder")
async def create_folder(vault_id: str, req: FolderCreateRequest, token: str = Depends(get_session)):
    ctx = _get_vault_ctx(token, vault_id)
    try:
        res = await vault_manager.create_folder(vault_id, req.name, req.parent_id, ctx["password"], ctx["is_decoy"])
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/vaults/{vault_id}/files/import")
async def import_file(vault_id: str, parent_id: str = Form(...), file: UploadFile = File(...), token: str = Depends(get_session)):
    """Direct in-memory stream import. Zero bytes are written to local disk unencrypted."""
    ctx = _get_vault_ctx(token, vault_id)
    file_bytes = await file.read()

    try:
        res = await vault_manager.import_file_data(
            vault_id=vault_id,
            filename=file.filename,
            data=file_bytes,
            parent_id=parent_id,
            password=ctx["password"],
            is_decoy=ctx["is_decoy"]
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/vaults/{vault_id}/files/{file_id}/data")
async def get_file_data(vault_id: str, file_id: str, token: str = Depends(get_session)):
    """Stream decrypted bytes directly from in-memory stream."""
    ctx = _get_vault_ctx(token, vault_id)
    try:
        data = await vault_manager.get_file_bytes(vault_id, file_id, ctx["password"], ctx["is_decoy"])
        return StreamingResponse(
            io.BytesIO(data),
            media_type="application/octet-stream",
            headers={"Content-Length": str(len(data))}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def _open_file_native(filepath: str):
    """Open a file with the default system application. Cross-platform."""
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(filepath)
        elif system == "Darwin":
            subprocess.Popen(["open", filepath])
        else:
            subprocess.Popen(["xdg-open", filepath])
    except Exception:
        pass


@app.post("/api/vaults/{vault_id}/files/{file_id}/open_system")
async def open_file_system(vault_id: str, file_id: str, token: str = Depends(get_session)):
    """Decrypts file to an ephemeral temp location and opens with the default system application."""
    ctx = _get_vault_ctx(token, vault_id)
    try:
        vdata = vault_manager._vault_cache.get(vault_id)
        if not vdata:
            await vault_manager.open_vault(vault_id, ctx["password"])
            vdata = vault_manager._vault_cache[vault_id]

        file_entry = vdata.get("files", {}).get(file_id)
        if not file_entry:
            raise ValueError("File entry not found")

        filename = file_entry.get("name", "preview_file")
        data = await vault_manager.get_file_bytes(vault_id, file_id, ctx["password"], ctx["is_decoy"])

        temp_dir = Path(tempfile.gettempdir()) / "phantom_view"
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_path = temp_dir / filename
        temp_path.write_bytes(data)

        _open_file_native(str(temp_path))
        return {"status": "success", "file": filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/vaults/{vault_id}/files/{file_id}/export")
async def export_file(vault_id: str, file_id: str, token: str = Depends(get_session)):
    return await get_file_data(vault_id, file_id, token)


@app.put("/api/vaults/{vault_id}/files/{file_id}")
async def rename_item(vault_id: str, file_id: str, req: RenameRequest, token: str = Depends(get_session)):
    ctx = _get_vault_ctx(token, vault_id)
    try:
        await vault_manager.rename_item(vault_id, file_id, req.name, ctx["password"], ctx["is_decoy"])
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/vaults/{vault_id}/files/{file_id}")
async def delete_item(vault_id: str, file_id: str, token: str = Depends(get_session)):
    ctx = _get_vault_ctx(token, vault_id)
    try:
        await vault_manager.delete_item(vault_id, file_id, ctx["password"], ctx["is_decoy"])
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Decoy Endpoints ---

@app.post("/api/vaults/{vault_id}/decoy")
async def set_decoy(vault_id: str, req: DecoyRequest, token: str = Depends(get_session)):
    try:
        await vault_manager.set_decoy_password(vault_id, req.current_password, req.decoy_password)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/vaults/{vault_id}/decoy")
async def remove_decoy(vault_id: str, req: DecoyRemoveRequest, token: str = Depends(get_session)):
    try:
        await vault_manager.remove_decoy(vault_id, req.password)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/system/exit")
async def system_exit():
    os._exit(0)


# --- Serve pre-built frontend from dist/ ---
dist_dir = Path(__file__).resolve().parent.parent / "dist"
if dist_dir.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="static")
