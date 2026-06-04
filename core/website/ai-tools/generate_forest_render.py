#!/usr/bin/env python3
"""
Generate: Mycelium Dome in a Forest — via Stable Horde (free, no key needed).
"""

import urllib.request, urllib.error, json, time, base64, os, sys

OUTPUT = "/mnt/c/Users/SajcS/Desktop/Living works by the word/living_architecture_images/08_mycelium_dome_forest.png"
API    = "https://stablehorde.net/api/v2"
APIKEY = "0000000000"   # anonymous guest key — always free

PROMPT = (
    "A breathtaking architectural masterpiece: a living mycelium dome house nestled inside "
    "a primeval ancient forest at golden hour. The dome is a translucent organic hemisphere "
    "made entirely of glowing bioluminescent mycelium threads and root networks, "
    "fibonacci spirals visible in its structure, amber and teal light pulsing softly through "
    "the interwoven fungal web walls. Inside the dome, warmly lit living spaces are visible "
    "through the semi-transparent skin. Massive ancient oak and redwood trees surround the dome, "
    "their roots merging seamlessly with the dome's root system below the earth. "
    "Ferns, moss, and forest undergrowth grow right up to and through the base of the structure. "
    "Shafts of golden forest light filter through the forest canopy overhead. "
    "Photorealistic, cinematic, lush colors, 8k, highly detailed, concept architecture art, "
    "octane render, dramatic atmosphere"
)

NEG = (
    "ugly, blurry, rectangular, square building, concrete, steel, industrial, "
    "cartoon, flat, low quality, block house, grid windows, dead materials"
)

print("Submitting to Stable Horde (free tier)…")
print(f"Model: SDXL  |  Size: 1024×1024\n")

payload = {
    "prompt": f"{PROMPT} ### {NEG}",
    "params": {
        "width":           1024,
        "height":          1024,
        "steps":           35,
        "cfg_scale":       7.5,
        "sampler_name":    "k_euler_a",
        "n":               1,
    },
    "models":       ["SDXL 1.0"],
    "r2":           False,
    "shared":       False,
    "slow_workers": True,
}

headers = {
    "Content-Type": "application/json",
    "apikey":       APIKEY,
    "Client-Agent": "livingworks:1.0:sage",
}

# ── Submit ───────────────────────────────────────────────────────────────────
req = urllib.request.Request(
    f"{API}/generate/async",
    data=json.dumps(payload).encode(),
    headers=headers,
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"Submission failed {e.code}: {body}")
    sys.exit(1)

job_id = result.get("id")
if not job_id:
    print("No job ID returned:", result)
    sys.exit(1)

print(f"Job submitted  →  ID: {job_id}")
print("Polling for completion (may take 1–4 min on free tier)…\n")

# ── Poll ─────────────────────────────────────────────────────────────────────
check_url = f"{API}/generate/check/{job_id}"
dot = 0
while True:
    time.sleep(6)
    try:
        with urllib.request.urlopen(check_url, timeout=15) as r:
            status = json.loads(r.read())
    except Exception as e:
        print(f"  (poll error: {e}) — retrying…")
        continue

    done     = status.get("done", False)
    waiting  = status.get("wait_time", "?")
    queue_pos= status.get("queue_position", "?")
    proc     = status.get("processing", 0)

    dot += 1
    bar = "." * dot
    if done:
        print(f"\r{bar} Done!                           ")
        break
    elif proc:
        print(f"\r{bar} Generating… (GPU active, ~{waiting}s left)", end="", flush=True)
    else:
        print(f"\r{bar} Queued (pos {queue_pos}, wait ~{waiting}s)", end="", flush=True)

# ── Retrieve ─────────────────────────────────────────────────────────────────
print("Downloading result…")
status_url = f"{API}/generate/status/{job_id}"
with urllib.request.urlopen(status_url, timeout=30) as r:
    final = json.loads(r.read())

generations = final.get("generations", [])
if not generations:
    print("No generations returned:", final)
    sys.exit(1)

gen   = generations[0]
img_b64 = gen.get("img", "")

if not img_b64:
    print("Empty image data:", gen)
    sys.exit(1)

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
with open(OUTPUT, "wb") as f:
    f.write(base64.b64decode(img_b64))

size_kb = os.path.getsize(OUTPUT) // 1024
print(f"\nSaved: {OUTPUT}  ({size_kb} KB)")
print("Open the file to view your mycelium dome in the forest!")
