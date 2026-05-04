import os
import threading
import ctypes
from tkinter import filedialog, messagebox

import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES

import main
import hardware

# --- Configuration & Constants ---
LANGUAGES = [
    "Arabic (ar)",
    "Bengali (bn)",
    "Chinese (zh)",
    "Dutch (nl)",
    "English (en)",
    "French (fr)",
    "German (de)",
    "Hindi (hi)",
    "Hungarian (hu)",
    "Indonesian (id)",
    "Italian (it)",
    "Japanese (ja)",
    "Korean (ko)",
    "Polish (pl)",
    "Portuguese (pt)",
    "Russian (ru)",
    "Spanish (es)",
    "Turkish (tr)",
    "Urdu / Pakistani (ur)",
    "Auto-Detect (auto)"
]

MODELS = [
    "tiny (Fastest / Low Accuracy)",
    "base (Fast / Basic Accuracy)",
    "small (Balanced)",
    "medium (Slower / High Accuracy)",
    "large-v3 (Slowest / Best Accuracy)"
]

# --- UI Theme Setup ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

cancel_event = threading.Event()


def set_title_bar_dark(window):
    """Tells Windows to render the title bar in dark mode."""
    try:
        # Ask Windows to update the title bar for DWM
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20

        # Enable Dark Mode for the window handle
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(ctypes.c_int(1)),
            ctypes.sizeof(ctypes.c_int(4))
        )
    except Exception:
        pass  # Silently continue if the platform doesn't support the Windows API


def browse_video():
    """Opens a file dialog to select the source video."""
    filepath = filedialog.askopenfilename(
        title="Select Video File",
        filetypes=[("MP4 Videos", "*.mp4"), ("All Files", "*.*")]
    )
    if filepath:
        process_selected_file(filepath)


def browse_save():
    """Opens a file dialog to select where to save the output .srt file."""
    filepath = filedialog.asksaveasfilename(
        title="Save Subtitle File As",
        defaultextension=".srt",
        filetypes=[("SRT Subtitles", "*.srt"), ("All Files", "*.*")]
    )
    if filepath:
        save_path_var.set(filepath)


def process_selected_file(filepath):
    """Handles the path generation for both browsing and drag-and-drop."""
    video_path_var.set(filepath)
    directory = os.path.dirname(filepath)
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    auto_save_path = os.path.join(directory, f"{base_name}_subtitle.srt")
    save_path_var.set(auto_save_path)


def drop_event(event):
    """Triggers when a file is dragged and dropped onto the app."""
    # tkinterdnd2 returns string paths with curly braces on Windows sometimes; strip them
    filepath = event.data.strip('{}')
    if filepath.lower().endswith('.mp4'):
        process_selected_file(filepath)
    else:
        messagebox.showwarning("Invalid File", "Please drop an MP4 video file.")


def update_gui_progress(current, total, status_text):
    """Updates the progress bar and status text safely from the worker thread."""
    percent = current / total if total > 0 else 0
    root.after(0, lambda: progress_bar.set(percent))
    root.after(0, lambda: status_var.set(status_text))


def check_cancel():
    """Checks if the user has requested to cancel the process."""
    return cancel_event.is_set()


def cancel_process():
    """Triggers the cancellation event."""
    cancel_event.set()
    status_var.set("Canceling... Please wait.")
    cancel_button.configure(state="disabled")


def run_translation_thread(video, lang_code, save, model_sz, task_type):
    """Background thread to handle the translation process without freezing the UI."""
    try:
        main.translate_movie(
            video_path=video,
            source_language=lang_code,
            output_file=save,
            model_size=model_sz,
            task=task_type,
            progress_callback=update_gui_progress,
            cancel_check=check_cancel
        )
    except Exception as e:
        update_gui_progress(0, 100, f"Error: {str(e)}")
    finally:
        root.after(0, lambda: start_button.configure(state="normal"))
        root.after(0, lambda: cancel_button.configure(state="disabled"))


def start_process():
    """Validates inputs and starts the translation thread."""
    video = video_path_var.get()
    save = save_path_var.get()
    lang = lang_var.get()
    model = model_var.get()
    task = task_var.get()

    if not video or not save:
        messagebox.showwarning("Missing Information", "Please select both a video file and a save location.")
        return

    # Parse dropdown selections for the backend
    lang_code = lang.split("(")[-1].replace(")", "")
    model_code = model.split(" ")[0].lower()
    task_code = "translate" if "Translate" in task else "transcribe"

    # Reset UI and clear previous cancellation events
    cancel_event.clear()
    start_button.configure(state="disabled")
    cancel_button.configure(state="normal")
    progress_bar.set(0)

    # Launch the process
    threading.Thread(
        target=run_translation_thread,
        args=(video, lang_code, save, model_code, task_code),
        daemon=True
    ).start()


# ==========================================
# --- Main Application Initialization ---
# ==========================================
if __name__ == "__main__":

    # 1. Root Window Setup (Using TkinterDnD)
    root = TkinterDnD.Tk()
    root.title("SubtitleSmith")
    root.geometry("780x620")
    root.resizable(False, False)

    # 2. Apply Theme Attributes
    root.attributes('-alpha', 1.0)  # Forces window refresh
    try:
        root.tk_setPalette(background='#2b2b2b', foreground='#ffffff')
    except Exception:
        pass

    # 3. Variable Initialization
    video_path_var = ctk.StringVar()
    save_path_var = ctk.StringVar()
    lang_var = ctk.StringVar(value=LANGUAGES[0])
    model_var = ctk.StringVar(value=MODELS[-1])
    task_var = ctk.StringVar(value="Translate to English")
    status_var = ctk.StringVar(value="Ready")

    # 4. Drag & Drop Setup
    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', drop_event)

    # 5. Main Layout Frame
    frame = ctk.CTkFrame(root)
    frame.pack(pady=20, padx=20, fill="both", expand=True)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(3, weight=1)

    # --- UI Elements ---

    # Row 0: Video Selection
    ctk.CTkLabel(frame, text="Video File:", width=100).grid(row=0, column=0, padx=10, pady=(20, 10), sticky="e")
    ctk.CTkEntry(frame, textvariable=video_path_var, width=400).grid(row=0, column=1, pady=(20, 10))
    ctk.CTkButton(frame, text="Browse", width=80, command=browse_video).grid(row=0, column=2, padx=10, pady=(20, 10))

    # Row 1: Save Location
    ctk.CTkLabel(frame, text="Save .srt To:", width=100).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    ctk.CTkEntry(frame, textvariable=save_path_var, width=400).grid(row=1, column=1, pady=10)
    ctk.CTkButton(frame, text="Browse", width=80, command=browse_save).grid(row=1, column=2, padx=10, pady=10)

    # Row 2: Language & Model Options
    options_frame = ctk.CTkFrame(frame, fg_color="transparent")
    options_frame.grid(row=2, column=0, columnspan=4, pady=10)

    ctk.CTkLabel(options_frame, text="Source Language:").pack(side="left", padx=(0, 5))
    ctk.CTkOptionMenu(options_frame, variable=lang_var, values=LANGUAGES, width=170).pack(side="left", padx=(0, 25))

    ctk.CTkLabel(options_frame, text="AI Model:").pack(side="left", padx=(0, 5))
    ctk.CTkOptionMenu(options_frame, variable=model_var, values=MODELS, width=240).pack(side="left")

    # Row 3: Action / Task Toggle
    action_frame = ctk.CTkFrame(frame, fg_color="transparent")
    action_frame.grid(row=3, column=0, columnspan=4, pady=10)

    ctk.CTkLabel(action_frame, text="Action:").pack(side="left", padx=10)
    ctk.CTkSegmentedButton(
        action_frame,
        variable=task_var,
        values=["Translate to English", "Keep Original Language"],
        width=320
    ).pack(side="left", padx=10)

    # Row 4: Status Text & Progress Bar
    status_frame = ctk.CTkFrame(frame, fg_color="transparent")
    status_frame.grid(row=4, column=0, columnspan=4, pady=(15, 0))

    ctk.CTkLabel(status_frame, textvariable=status_var, text_color="gray").pack(pady=(0, 5))
    progress_bar = ctk.CTkProgressBar(status_frame, width=460)
    progress_bar.set(0)
    progress_bar.pack()

    # Row 5: Action Buttons
    button_frame = ctk.CTkFrame(frame, fg_color="transparent")
    button_frame.grid(row=5, column=0, columnspan=4, pady=(20, 10))

    start_button = ctk.CTkButton(button_frame, text="Start Processing", command=start_process, fg_color="#28a745",
                                 hover_color="#218838")
    start_button.pack(side="left", padx=15)

    cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=cancel_process, fg_color="#dc3545",
                                  hover_color="#c82333", state="disabled")
    cancel_button.pack(side="left", padx=15)

    # Row 6: Hardware Info Box
    hw_frame = ctk.CTkFrame(frame, fg_color="transparent")
    hw_frame.grid(row=6, column=0, columnspan=4, pady=(5, 10))

    hw_textbox = ctk.CTkTextbox(hw_frame, width=600, height=140, text_color="#28a745", fg_color="#1e1e1e")
    hw_textbox.pack()

    # Run the hardware scan
    try:
        report, recommended_model = hardware.scan_system()
        hw_textbox.insert("0.0", report)
        model_var.set(recommended_model)
    except Exception as e:
        hw_textbox.insert("0.0", f"Could not perform hardware scan.\nError: {e}")

    hw_textbox.configure(state="disabled")

    # Apply final system attributes and start main loop
    set_title_bar_dark(root)
    root.mainloop()