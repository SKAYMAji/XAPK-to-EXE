import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def extract_apk() -> Path:
    bundled_apk = Path(__file__).with_suffix(".apk")
    if not bundled_apk.exists():
        bundled_apk = next(Path(__file__).parent.glob("*.apk"), None)
    if not bundled_apk or not bundled_apk.exists():
        raise FileNotFoundError("Bundled APK not found.")

    temp_dir = Path(tempfile.mkdtemp(prefix="apk_bundle_"))
    target = temp_dir / bundled_apk.name
    shutil.copy(bundled_apk, target)
    return target


def main() -> int:
    try:
        apk_path = extract_apk()
    except OSError as exc:
        print(f"Failed to extract APK: {exc}", file=sys.stderr)
        return 1

    print(f"APK extracted to: {apk_path}")
    print("You can install this APK on an Android device using adb or an emulator.")
    adb_path = shutil.which("adb")
    if adb_path:
        choice = input("Install APK via adb now? (y/N): ").strip().lower()
        if choice == "y":
            try:
                subprocess.run([adb_path, "install", str(apk_path)], check=True)
            except subprocess.CalledProcessError as exc:
                print(f"adb install failed: {exc}", file=sys.stderr)
                return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
