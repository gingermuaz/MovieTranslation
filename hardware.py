import psutil
import platform
import subprocess


def scan_system():
    """Scans CPU, RAM, and GPU, returning a formatted report string and a model recommendation."""
    # 1. Get CPU
    cpu_name = platform.processor() or "Unknown CPU"

    # 2. Get RAM
    ram_bytes = psutil.virtual_memory().total
    ram_gb = round(ram_bytes / (1024 ** 3))

    # 3. Get NVIDIA GPU
    gpu_name = "No NVIDIA GPU detected"
    vram_gb = 0
    has_gpu = False

    try:
        # Pings the NVIDIA driver directly to get the name and VRAM
        smi_output = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'],
            encoding='utf-8'
        )
        if smi_output.strip():
            parts = smi_output.strip().split(', ')
            gpu_name = parts[0]
            # Convert Megabytes to Gigabytes
            vram_mb = int(parts[1].replace(' MiB', '').replace(' MB', ''))
            vram_gb = round(vram_mb / 1024)
            has_gpu = True
    except Exception:
        pass  # Will skip if no NVIDIA driver is found

    # 4. Recommendation Logic
    rec_model = "tiny (Fastest / Low Accuracy)"  # Safe default

    if has_gpu:
        if vram_gb >= 8:
            rec_model = "large-v3 (Slowest / Best Accuracy)"
        elif vram_gb >= 4:
            rec_model = "small (Balanced)"
        else:
            rec_model = "base (Fast / Basic Accuracy)"
    elif ram_gb >= 16:
        rec_model = "base (Fast / Basic Accuracy)"

    # 5. Format the Text Box Output
    report_text = (
        f"--- System Hardware Scan ---\n"
        f"CPU: {cpu_name}\n"
        f"RAM: {ram_gb} GB\n"
        f"GPU: {gpu_name} ({vram_gb} GB VRAM)\n\n"
        f"Recommendation: Auto-selected the '{rec_model.split(' ')[0]}' model based on your VRAM."
    )

    return report_text, rec_model