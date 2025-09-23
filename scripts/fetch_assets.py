# scripts/fetch_assets.py
# Usage:
#   python scripts/fetch_assets.py --locale en_US --out-dir assets --use-latest
#
# Writes:
#   data/tft_classes.json   (ordered names -> class ids)
#   data/tft.yaml           (YOLO dataset header w/ names list)
#   assets/champions/*.png
#   assets/items/*.png
#   assets/traits/*.png

import json, re, argparse, pathlib, sys, unicodedata
from urllib.parse import urljoin
import requests
from tqdm import tqdm

CDRAGON_BASE = "https://raw.communitydragon.org/"
# We’ll use “latest” so you don’t have to bump versions manually.
CDRAGON_LATEST = urljoin(CDRAGON_BASE, "latest/")
RCPLGD = "plugins/rcp-be-lol-game-data/global/default"
V1_DIR = f"{CDRAGON_LATEST}{RCPLGD}/v1/"
GAME_DIR = f"{CDRAGON_LATEST}game/"

DDRAGON_VERSIONS = "https://ddragon.leagueoflegends.com/api/versions.json"  # helpful for patch pinning

FILEMAP_URL = f"{CDRAGON_LATEST}filemap.json"

# Anything that isn't a playable unit usually contains one of these tokens:
NON_UNIT_TOKENS = [
    "damageTracker", "wraith", "dummy", "crab", "spawn", "plant",
    "tutorial", "chest", "armory", "augment", "prop", "tracker"
]
def load_filemap():
    """
    filemap.json lists every file path CDragon serves. We'll use it to discover
    the exact icon filenames for the current set.
    """
    return get(FILEMAP_URL).json()

def find_tft_icon_path(filemap, set_number, base_name):
    """
    Try to find a shop splash OR square icon for a given unit.
    Looks for filenames like:
      game/assets/ux/tft/championsplashes/tft15_ahri.tft_set15.png
      game/assets/ux/tft/champions/tft15_ahri_square.tft_set15.png
    Returns a full raw URL or None.
    """
    set_str = str(set_number)
    bn = base_name.lower()

    candidates = []
    for p in filemap:
        if not isinstance(p, str):
            continue
        lp = p.lower()
        if "game/assets/ux/tft/" not in lp:
            continue
        if f"tft{set_str}_" not in lp:
            continue
        if f"tft{set_str}_{bn}" not in lp:
            continue
        # prefer championsplashes over square if both exist
        if "championsplashes" in lp:
            candidates.insert(0, p)
        else:
            candidates.append(p)

    if candidates:
        # filemap paths are relative to /latest/
        return urljoin(CDRAGON_LATEST, candidates[0].lstrip("/"))
    return None

def api_to_basename(api_name: str) -> str:
    # "TFT15_Ahri" -> "ahri"
    if not api_name:
        return ""
    lower = api_name.lower()
    base = lower.split("_", 1)[-1] if "_" in lower else lower
    return base


def slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_").lower()
    return s

def map_lol_asset_path_to_cdragon(raw_path: str) -> str:
    """
    CDragon doc: '/lol-game-data/assets/<PATH>' -> 'plugins/rcp-be-lol-game-data/global/default/<lowercased-path>'
    https://www.communitydragon.org/documentation/assets  (see 'Mapping paths from JSON files')
    """
    assert raw_path.startswith("/lol-game-data/assets/"), f"Unexpected asset path: {raw_path}"
    lower = raw_path[len("/lol-game-data/assets/"):].lower()
    return f"{CDRAGON_LATEST}{RCPLGD}/{lower}"

def get(url: str):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r

def maybe_download(url: str, dest: pathlib.Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return False
    r = get(url)
    with open(dest, "wb") as f:
        f.write(r.content)
    return True

def load_tft_json(locale="en_us"):
    # CDragon ships prebuilt TFT JSONs here (champions/items/traits lists)
    champs = get(f"{V1_DIR}tftchampions.json").json()      # unit list & metadata
    items  = get(f"{V1_DIR}tftitems.json").json()          # item list & metadata
    traits = get(f"{V1_DIR}tfttraits.json").json()         # trait list & metadata
    return champs, items, traits

def extract_classes(champs_json, set_number_hint=None):
    """
    Build a stable class list from CDragon tftchampions.json without relying on `tier`.
    Keep entries whose apiName looks like TFT<SET>_<Name> and exclude junk by token blacklist.
    """
    def is_probable_unit(u):
        api = (u.get("apiName") or "").lower()
        if not api.startswith("tft"):
            return False
        # optional: scope to a specific set if provided (e.g., 15)
        if set_number_hint:
            if not api.startswith(f"tft{set_number_hint}".lower()):
                return False
        return not any(tok in api for tok in NON_UNIT_TOKENS)

    names = []
    seen = set()
    for u in champs_json:
        if not is_probable_unit(u):
            continue
        disp = (u.get("name") or u.get("displayName") or "").strip()
        if not disp:
            # derive from apiName: TFT15_Ahri -> Ahri
            api = u.get("apiName", "")
            base = api.split("_", 1)[-1] if "_" in api else api
            disp = base  # keep as-is; you can title-case if you prefer
        if disp and disp not in seen:
            seen.add(disp)
            names.append(disp)
    return names

def download_icons(champs, items, traits, out_dir: pathlib.Path, set_number=15, verbose=False, force=False):
    champ_dir = out_dir / "champions"
    item_dir  = out_dir / "items"
    trait_dir = out_dir / "traits"
    champ_dir.mkdir(parents=True, exist_ok=True)
    item_dir.mkdir(parents=True, exist_ok=True)
    trait_dir.mkdir(parents=True, exist_ok=True)

    print(f"[paths] champions -> {champ_dir.resolve()}")
    print(f"[paths] items     -> {item_dir.resolve()}")
    print(f"[paths] traits    -> {trait_dir.resolve()}")

    filemap = load_filemap()

    saved = {"champs": 0, "items": 0, "traits": 0}

    def _save(url, dest: pathlib.Path, bucket_key: str, name_for_log: str):
        if not url:
            if verbose:
                print(f"[miss] url missing for: {name_for_log}")
            return
        if not force and dest.exists() and dest.stat().st_size > 0:
            if verbose:
                print(f"[skip] exists: {dest.name}")
            return
        try:
            r = get(url)
            dest.write_bytes(r.content)
            saved[bucket_key] += 1
            if verbose:
                print(f"[ok] {name_for_log} -> {dest.name}")
        except Exception as e:
            print(f"[warn] {name_for_log}: {e}")

    # Champions
    print("Downloading champion icons…")
    for u in tqdm(champs, ncols=100):
        api = (u.get("apiName") or "").strip()
        if not api or any(tok in api.lower() for tok in NON_UNIT_TOKENS):
            continue
        # resolve preferred icon url
        url = None
        icon_path = u.get("icon")
        if icon_path and icon_path.startswith("/lol-game-data/assets/"):
            url = map_lol_asset_path_to_cdragon(icon_path)
        if not url:
            url = find_tft_icon_path(filemap, set_number, api_to_basename(api))

        name_for_file = (u.get("name") or u.get("displayName") or api).strip()
        dest = (out_dir / "champions" / f"{slug(name_for_file)}.png")
        _save(url, dest, "champs", name_for_file)

    # Items
    print("Downloading item icons…")
    for it in tqdm(items, ncols=100):
        name = it.get("name") or it.get("displayName") or it.get("apiName") or "item"
        icon = it.get("icon")
        url = map_lol_asset_path_to_cdragon(icon) if icon and icon.startswith("/lol-game-data/assets/") else None
        dest = item_dir / f"{slug(name)}.png"
        _save(url, dest, "items", name)

    # Traits
    print("Downloading trait icons…")
    for tr in tqdm(traits, ncols=100):
        name = tr.get("name") or tr.get("displayName") or tr.get("apiName") or "trait"
        icon = tr.get("icon")
        url = map_lol_asset_path_to_cdragon(icon) if icon and icon.startswith("/lol-game-data/assets/") else None
        dest = trait_dir / f"{slug(name)}.png"
        _save(url, dest, "traits", name)

    print(f"[summary] saved -> champions: {saved['champs']}, items: {saved['items']}, traits: {saved['traits']}")
    return saved

def write_yolo_config(names, data_dir: pathlib.Path):
    names_map = {i: n for i, n in enumerate(names)}
    # Persist both a plain list (for code) and YOLO-style yaml
    with open(data_dir / "tft_classes.json", "w", encoding="utf-8") as f:
        json.dump({"names": names, "map": names_map}, f, ensure_ascii=False, indent=2)

    yaml = [
        "path: data",
        "train: synth/images,real_pseudo/images",
        "val:   val/images",
        "",
        "names:"
    ] + [f"  {i}: {n}" for i, n in enumerate(names)]
    (data_dir / "tft.yaml").write_text("\n".join(yaml), encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--locale", default="en_US")
    ap.add_argument("--out-dir", default="assets")
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--use-latest", action="store_true",
                    help="Always use CDragon 'latest' (recommended).")
    args = ap.parse_args()

    out_dir = pathlib.Path(args.out_dir)
    data_dir = pathlib.Path(args.data_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    # (Optional) check current ddragon version for your logs/pinning purposes
    try:
        versions = get(DDRAGON_VERSIONS).json()  # newest first
        current_ddragon = versions[0] if versions else "unknown"
        print(f"[info] Latest Data Dragon version: {current_ddragon}")
    except Exception as e:
        print(f"[warn] Could not fetch ddragon versions: {e}")

    champs, items, traits = load_tft_json(locale=args.locale.lower())
    # If you know the current set (15), pass it here for tighter filtering:
    names = extract_classes(champs, set_number_hint=15)
    print(f"[info] Units discovered: {len(names)}")

    download_icons(champs, items, traits, out_dir=out_dir, set_number=15, verbose=True, force=False)

    write_yolo_config(names, data_dir=data_dir)
    print("[done] Assets + class map written.")

if __name__ == "__main__":
    sys.exit(main())
