
import os
import shutil
from pathlib import Path
import time

# >>>>> KONFIGURATION <<<<<
SOURCE_ROOT = Path("/Volumes/Musik/iTunes Media/Music")
DEST_ROOT = Path("/Users/tillo/iTunesMusic")
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".flac"}
RETRY_COUNT = 3  # Anzahl der Wiederholungen bei Fehler
RETRY_DELAY = 2  # Sekunden zwischen Wiederholungen

failed_files = []


def is_music_file(file_path: Path) -> bool:
    return file_path.suffix.lower() in ALLOWED_EXTENSIONS


def copy_file_with_retries(source_file: Path, dest_file: Path):
    temp_dest = dest_file.with_suffix(dest_file.suffix + ".part")
    for attempt in range(RETRY_COUNT):
        try:
            temp_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, temp_dest)
            temp_dest.rename(dest_file)
            print(f"✅ Kopiert: {source_file} -> {dest_file}")
            return
        except Exception as e:
            print(f"❌ Fehler ({attempt+1}/{RETRY_COUNT}) beim Kopieren von {source_file}: {e}")
            time.sleep(RETRY_DELAY)

    failed_files.append(source_file)


def copy_music_folder_by_artist(source_root: Path, dest_root: Path):
    if not source_root.exists():
        print(f"❌ Quellverzeichnis nicht gefunden: {source_root}")
        return

    artist_folders = sorted(source_root.iterdir())

    for artist_folder in artist_folders:
        if not artist_folder.is_dir():
            continue

        print(f"\n🎵 Bearbeite Künstler: {artist_folder.name}")
        for root, _, files in os.walk(artist_folder):
            root_path = Path(root)
            for file_name in files:
                source_file = root_path / file_name
                if not is_music_file(source_file):
                    continue

                relative_path = source_file.relative_to(source_root)
                dest_file = dest_root / relative_path

                if dest_file.exists() and dest_file.stat().st_size > 0:
                    print(f"⏩ Übersprungen (existiert): {dest_file}")
                    continue

                copy_file_with_retries(source_file, dest_file)


if __name__ == "__main__":
    try:
        print("🎶 Starte Musik-Kopieprozess...\n")
        copy_music_folder_by_artist(SOURCE_ROOT, DEST_ROOT)
        if failed_files:
            print("\n⚠️ Nicht kopierbare Dateien:")
            for f in failed_files:
                print(f" - {f}")
        else:
            print("\n🎉 Alle Dateien erfolgreich kopiert.")
    except KeyboardInterrupt:
        print("\n⏹️ Manuell abgebrochen.")
    except Exception as e:
        print(f"\n❗ Unerwarteter Fehler: {e}")

