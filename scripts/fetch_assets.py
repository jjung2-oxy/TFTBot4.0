# scripts/asset_sync.py
import json, os, sys, shutil, re
from pathlib import Path
from urllib.request import urlretrieve, urlopen

# ---- Config ----
CDRAGON_TFT_JSON = "https://raw.communitydragon.org/latest/cdragon/tft/en_us.json"
# Square icons (small) live under this base; some paths are embedded in the JSON.
CDRAGON_BASE_RAW = "https://raw.communitydragon.org/latest"

ASSETS_DIR = Path("assets")
ICON_DIR = ASSETS_DIR / "champions" / "icons"
CARD_DIR = ASSETS_DIR / "champions" / "cards"
UI_DIR   = ASSETS_DIR / "ui"
META_OUT = ASSETS_DIR / "tft_meta.json"
CLASSES  = Path("training-files") / "classes.txt"
LABELMAP = Path("training-files") / "label_map.json"

ICON_DIR.mkdir(parents=True, exist_ok=True)
CARD_DIR.mkdir(parents=True, exist_ok=True)
UI_DIR.mkdir(parents=True, exist_ok=True)
META_OUT.parent.mkdir(parents=True, exist_ok=True)
CLASSES.parent.mkdir(parents=True, exist_ok=True)

def fetch_json(url):
    with urlopen(url) as r:
        return json.load(r)

def safe_name(name):
    return re.sub(r"[^A-Za-z0-9_]+", "_", name.strip())

    

def main():
    print("[asset_sync] Fetching TFT JSON from CommunityDragon...")
    tft = fetch_json(CDRAGON_TFT_JSON)
    # --- after you've loaded `tft` from CDragon ---

    def safe_name(name):
        import re
        return re.sub(r"[^A-Za-z0-9_]+", "_", name.strip())

    def is_playable_champion(u: dict) -> bool:
        # Must have a positive shop cost and at least one trait
        cost = u.get("cost", 0)
        if not isinstance(cost, (int, float)) or cost <= 0:
            return False
        traits = u.get("traits") or []
        if not isinstance(traits, list) or len(traits) == 0:
            return False

        # Exclude obvious NPC/summons/minions/plants/test artifacts
        name_l = (u.get("name") or "").lower()
        api_l  = (u.get("apiName") or u.get("characterName") or "").lower()
        bad_kw = [
            "dummy", "training", "scuttler", "golem", "minion", "plant",
            "spine", "root", "test", "mech_core", "mercenary", "chest",
            "anvil", "tome", "artifact", "component", "support_item"
        ]
        if any(k in name_l or k in api_l for k in bad_kw):
            return False

        return True

    # CDragon sets structure is a dict keyed by set number strings
    sets_raw = tft.get("sets", {})
    if not sets_raw:
        raise SystemExit("No sets found in TFT JSON; abort.")

    sets = list(sets_raw.values()) if isinstance(sets_raw, dict) else sets_raw
    latest = sorted(sets, key=lambda s: s.get("number", 0))[-1]
    set_num = latest.get("number")
    meta = {"set_number": set_num, "count": len(classes_uni), "champions": champ_meta}


    # Some versions use "champions", others "units"
    units = latest.get("champions") or latest.get("units") or []

    # Filter to playable champs only
    playable = [u for u in units if isinstance(u, dict) and is_playable_champion(u)]
    if not playable:
        raise SystemExit("No playable champions found; check schema/filters.")

    # Build classes + meta
    classes = []
    champ_meta = []  # to write champ_meta.json

    for u in playable:
        name = u.get("name") or u.get("characterName") or u.get("apiName")
        if not name:
            continue
        cname = safe_name(name)

        classes.append(cname)
        champ_meta.append({
            "characterName": u.get("characterName") or u.get("apiName"),
            "apiName": u.get("apiName") or u.get("characterName"),
            "name": name,
            "cost": u.get("cost"),
            "traits": u.get("traits") or []
        })

    # Dedup while preserving order
    seen = set(); classes_uni = []
    for c in classes:
        if c not in seen:
            seen.add(c); classes_uni.append(c)

    # Write classes.txt (champions only)
    from pathlib import Path, PurePosixPath
    Path("training-files").mkdir(parents=True, exist_ok=True)
    Path("assets").mkdir(parents=True, exist_ok=True)

    with open("training-files/classes.txt", "w", encoding="utf-8") as f:
        for c in classes_uni:
            f.write(c + "\n")

    # Write champ_meta.json with characterName, cost, traits
    import json
    with open("training-files/champ_meta.json", "w", encoding="utf-8") as f:
        json.dump({
            "set_number": set_num,
            "count": len(classes_uni),
            "champions": champ_meta
        }, f, indent=2)

    print(f"[asset_sync] Set {set_num}: wrote {len(classes_uni)} champions to training-files/classes.txt")
    print("[asset_sync] Champ metadata at training-files/champ_meta.json")

if __name__ == "__main__":
    main()
