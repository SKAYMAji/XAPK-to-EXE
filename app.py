import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox


def extract_apk_from_xapk(xapk_path: Path, output_dir: Path) -> Path:
    if not xapk_path.exists():
        raise FileNotFoundError(f"File not found: {xapk_path}")
    if not zipfile.is_zipfile(xapk_path):
        raise ValueError("XAPK file is not a valid ZIP archive.")

    with zipfile.ZipFile(xapk_path, "r") as archive:
        apk_infos = [info for info in archive.infolist() if info.filename.lower().endswith(".apk")]
        if not apk_infos:
            raise ValueError("No APK file found inside the XAPK archive.")

        selected = max(apk_infos, key=lambda info: info.file_size)
        with archive.open(selected) as source, tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfileobj(source, temp_file)
            temp_apk_path = Path(temp_file.name)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / Path(selected.filename).name
    shutil.move(str(temp_apk_path), output_path)
    return output_path


def build_exe_from_apk(apk_path: Path, output_dir: Path) -> Path:
    if not apk_path.exists():
        raise FileNotFoundError(f"File not found: {apk_path}")

    pyinstaller_path = shutil.which("pyinstaller")
    if not pyinstaller_path:
        raise RuntimeError(
            "PyInstaller is not installed. Install it with 'pip install pyinstaller' and try again."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    work_dir = Path(tempfile.mkdtemp(prefix="apk_to_exe_"))

    wrapper_source = Path(__file__).parent / "apk_wrapper.py"
    wrapper_copy = work_dir / "apk_wrapper.py"
    shutil.copy(wrapper_source, wrapper_copy)

    apk_copy = work_dir / apk_path.name
    shutil.copy(apk_path, apk_copy)

    data_sep = ";" if os.name == "nt" else ":"
    add_data_arg = f"{apk_copy}{data_sep}."
    exe_name = f"{apk_path.stem}_installer"

    command = [
        pyinstaller_path,
        "--onefile",
        "--noconsole",
        "--name",
        exe_name,
        "--distpath",
        str(output_dir),
        "--workpath",
        str(work_dir / "build"),
        "--specpath",
        str(work_dir),
        "--add-data",
        add_data_arg,
        str(wrapper_copy),
    ]

    subprocess.run(command, check=True)
    exe_path = output_dir / (exe_name + (".exe" if os.name == "nt" else ""))
    if not exe_path.exists():
        raise RuntimeError("PyInstaller finished, but the output EXE was not found.")
    return exe_path


class ConverterApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("XAPK ↔ APK ↔ EXE Converter")
        self.geometry("520x280")
        self.resizable(False, False)

        header = tk.Label(self, text="XAPK to APK and APK to EXE", font=("Arial", 14, "bold"))
        header.pack(pady=12)

        self.status_var = tk.StringVar(value="Select an option to start.")

        xapk_frame = tk.LabelFrame(self, text="XAPK → APK", padx=12, pady=12)
        xapk_frame.pack(fill="x", padx=16, pady=8)
        tk.Button(
            xapk_frame,
            text="Choose XAPK and Convert",
            command=self.handle_xapk_to_apk,
            width=28,
        ).pack(side="left")

        apk_frame = tk.LabelFrame(self, text="APK → EXE", padx=12, pady=12)
        apk_frame.pack(fill="x", padx=16, pady=8)
        tk.Button(
            apk_frame,
            text="Choose APK and Convert",
            command=self.handle_apk_to_exe,
            width=28,
        ).pack(side="left")

        status_label = tk.Label(self, textvariable=self.status_var, wraplength=480, fg="#333")
        status_label.pack(pady=8)

        note = tk.Label(
            self,
            text="APK → EXE requires PyInstaller and is intended for Windows installers.",
            font=("Arial", 9),
            fg="#555",
        )
        note.pack(pady=4)

    def handle_xapk_to_apk(self) -> None:
        xapk_path = filedialog.askopenfilename(
            title="Select XAPK File",
            filetypes=[("XAPK Files", "*.xapk"), ("ZIP Files", "*.zip"), ("All Files", "*")],
        )
        if not xapk_path:
            return

        output_dir = filedialog.askdirectory(title="Select Output Folder")
        if not output_dir:
            return

        try:
            output_path = extract_apk_from_xapk(Path(xapk_path), Path(output_dir))
        except (OSError, ValueError) as exc:
            messagebox.showerror("Conversion Failed", str(exc))
            self.status_var.set("Conversion failed. Check the file and try again.")
            return

        messagebox.showinfo("Success", f"APK created at: {output_path}")
        self.status_var.set(f"APK saved to {output_path}")

    def handle_apk_to_exe(self) -> None:
        apk_path = filedialog.askopenfilename(
            title="Select APK File",
            filetypes=[("APK Files", "*.apk"), ("All Files", "*")],
        )
        if not apk_path:
            return

        output_dir = filedialog.askdirectory(title="Select Output Folder")
        if not output_dir:
            return

        try:
            output_path = build_exe_from_apk(Path(apk_path), Path(output_dir))
        except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
            messagebox.showerror("Conversion Failed", str(exc))
            self.status_var.set("Conversion failed. Ensure dependencies are installed.")
            return

        messagebox.showinfo("Success", f"EXE created at: {output_path}")
        self.status_var.set(f"EXE saved to {output_path}")


if __name__ == "__main__":
    app = ConverterApp()
    app.mainloop()
