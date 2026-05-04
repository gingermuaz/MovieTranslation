import os
import sys
from faster_whisper import WhisperModel
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore")

# --- AGGRESSIVE WINDOWS DLL INJECTION ---
venv_dir = os.path.dirname(os.path.dirname(sys.executable))
site_packages_dir = os.path.join(venv_dir, "Lib", "site-packages")
cublas_bin = os.path.join(site_packages_dir, "nvidia", "cublas", "bin")
cudnn_bin = os.path.join(site_packages_dir, "nvidia", "cudnn", "bin")

os.environ["PATH"] = f"{cublas_bin};{cudnn_bin};" + os.environ.get("PATH", "")
if hasattr(os, 'add_dll_directory'):
    if os.path.exists(cublas_bin): os.add_dll_directory(cublas_bin)
    if os.path.exists(cudnn_bin): os.add_dll_directory(cudnn_bin)


# ----------------------------------------

def format_timestamp(seconds: float):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


# Added 'model_size' and 'task' parameters
def translate_movie(video_path, source_language, output_file, model_size="large-v3", task="translate",
                    progress_callback=None, cancel_check=None):
    if progress_callback: progress_callback(0, 100, f"Loading '{model_size}' model onto RTX 3070...")

    model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")

    if progress_callback: progress_callback(0, 100, "Extracting audio and analyzing...")

    lang_param = None if source_language == "auto" else source_language

    # Engine now respects the task (transcribe vs translate)
    segments, info = model.transcribe(video_path, task=task, language=lang_param, vad_filter=True)
    total_duration = round(info.duration, 2)

    srt_content = ""

    with tqdm(total=total_duration, unit="sec",
              bar_format="{l_bar}{bar}| {n:.1f}/{total:.1f} [{elapsed}<{remaining}]") as pbar:
        for index, segment in enumerate(segments, start=1):

            if cancel_check and cancel_check():
                if progress_callback: progress_callback(0, 100, "Process Canceled.")
                print("\nProcess aborted by user.")
                return

            start_time = format_timestamp(segment.start)
            end_time = format_timestamp(segment.end)

            srt_content += f"{index}\n"
            srt_content += f"{start_time} --> {end_time}\n"
            srt_content += f"{segment.text.strip()}\n\n"

            pbar.update(segment.end - pbar.n)

            if progress_callback:
                percentage = round((segment.end / total_duration) * 100, 1)
                action_text = "Translating" if task == "translate" else "Transcribing"
                progress_callback(segment.end, total_duration, f"{action_text}... {percentage}%")

    if progress_callback: progress_callback(100, 100, "Saving file...")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(srt_content)

    if progress_callback: progress_callback(100, 100, "Success! Subtitles saved.")


if __name__ == "__main__":
    print("Please run GUI.py to start the application.")