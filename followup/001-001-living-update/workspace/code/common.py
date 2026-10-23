"""Shared paths and helpers for study 001-living-update."""
import os, json, hashlib, time

SHARED = "/workspace/eval/followup_staging/shared-data"
ROOT = "/workspace/eval/followup/001-001-living-update"
RESULTS = os.path.join(ROOT, "results")
WORK = os.path.join(ROOT, "workspace")
CKPT = os.path.join(WORK, "checkpoints")
ENGINE_DIR = "/workspace/eval/replication/codebase/reimpl"

os.makedirs(RESULTS, exist_ok=True)
os.makedirs(CKPT, exist_ok=True)


def sha256(path, buf=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(buf)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def done(block):
    with open(os.path.join(CKPT, f"{block}.done"), "w") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S"))


def is_done(block):
    return os.path.exists(os.path.join(CKPT, f"{block}.done"))


def write_json(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, default=float)
