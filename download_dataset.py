
from pathlib import Path
from urllib.request import urlopen

URL = (
    "https://huggingface.co/datasets/"
    "maharshipandya/spotify-tracks-dataset/"
    "resolve/main/dataset.csv"
)

OUTPUT_PATH = Path("data/raw/spotify_tracks.csv")


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if OUTPUT_PATH.exists():
        print(f"File already exists: {OUTPUT_PATH.resolve()}")
        print("Keeping it unchanged. Inspect or rename it before downloading again.")
        return

    print("Downloading Spotify Tracks Dataset...")
    print("Source: Hugging Face")
    
    with urlopen(URL, timeout=60) as response:
        with OUTPUT_PATH.open("wb") as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)

    size_mb = OUTPUT_PATH.stat().st_size / (1024 * 1024)

    if size_mb < 1:
        OUTPUT_PATH.unlink(missing_ok=True)
        raise RuntimeError(
            "Downloaded file is unexpectedly small. "
            "The file was removed; check the source URL."
        )

    print(f"Download complete: {OUTPUT_PATH.resolve()}")
    print(f"File size: {size_mb:.2f} MB")


if __name__ == "__main__":
    main()
