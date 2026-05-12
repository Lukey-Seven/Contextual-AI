import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as filedialog
import keyboard
import pyautogui
import requests
import base64
import io
import threading
import queue
import sys
import os
import json
import re
import webbrowser
from PIL import Image, ImageTk, ImageDraw

# --- CONFIGURATION ---
app_queue = queue.Queue()

# Global States
side_panel = None
loading_panel = None
prompt_win = None
disclosure_win = None
snip_win = None
drawn_rectangles = []
step_cards =[]
animation_active = False

initial_screenshot = None

# --- LOCALIZATION DICTIONARY ---
LANG_DICT = {
    "EN": {
        "title": "Blueprint Lens",
        "instruction": "Enter your question below or select a specific area to get an AI-guided step-by-step overlay.",
        "placeholder": "Enter your question for the AI here!",
        "locate": "Locate",
        "snip": "Ask a specific area",
        "cancel": "Cancel",
        "done": "Done",
        "search": "Search Web",
        "step": "Step",
        "ai_guide": "AI Guide",
        "thinking": "Blueprint Lens is thinking",
        "disc_title": "Privacy & Data Consent",
        "disc_msg": "Just a heads up from the developer!\n\nThis is a student project. To analyze your request, your screenshot is sent to Google Gemini (using my paid plan, so your data is NOT used for training). If my paid limit is reached, the system may fallback to OpenAI as a backup, where data may be used for model training.\n\nBy continuing, you help the AI learn to recognize UI patterns for better guides in the future. No personal data is stored permanently.",
        "accept": "Accept & Analyze",
        "go_back": "Go Back",
        "log_start": "Initializing AI Vision Engine...",
        "log_upload": "Uploading image to secure server...",
        "log_analyze": "Analyzing spatial UI coordinates...",
        "log_generate": "Generating step-by-step guide...",
        "log_done": "Complete! Rendering overlay...",
    },
    "VI": {
        "title": "Blueprint Lens",
        "instruction": "Nhập câu hỏi của bạn bên dưới hoặc chọn một khu vực cụ thể để nhận hướng dẫn chi tiết từ AI.",
        "placeholder": "Hãy nhập câu hỏi cho AI tại đây!",
        "locate": "Tìm kiếm",
        "snip": "Chọn khu vực",
        "cancel": "Hủy",
        "done": "Hoàn tất",
        "search": "Tìm trên Web",
        "step": "Bước",
        "ai_guide": "Hướng dẫn AI",
        "thinking": "AI đang suy nghĩ",
        "disc_title": "Quyền riêng tư & Dữ liệu",
        "disc_msg": "Thông báo nhỏ từ người phát triển!\n\n Đây là dự án của sinh viên. Để phân tích yêu cầu, ảnh chụp màn hình sẽ được gửi đến Google Gemini. Nếu hạn mức trả phí hết, hệ thống có thể chuyển sang OpenAI.\n\n Bằng cách tiếp tục, bạn đang giúp AI học cách nhận diện giao diện tốt hơn trong tương lai.",
        "accept": "Chấp nhận & Phân tích",
        "go_back": "Quay lại",
        "log_start": "Đang khởi tạo Động cơ Thị giác AI...",
        "log_upload": "Đang tải hình ảnh lên máy chủ bảo mật...",
        "log_analyze": "Đang phân tích tọa độ không gian UI...",
        "log_generate": "Đang tạo hướng dẫn từng bước...",
        "log_done": "Hoàn thành! Đang hiển thị lớp phủ...",
    }
}

current_lang = "EN"

def t(key):
    return LANG_DICT[current_lang].get(key, key)

# ==========================================
# ASYNC IMAGE LOADER (MARKDOWN PARSING)
# ==========================================
def load_and_display_image(url, label):
    """Downloads an image in the background and safely renders it in the Tkinter label."""
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        img_data = resp.content
        img = Image.open(io.BytesIO(img_data))
        
        max_width = 320
        ratio = max_width / float(img.width)
        new_height = int(float(img.height) * float(ratio))
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        tk_img = ImageTk.PhotoImage(img)
        
        label.after(0, lambda: label.config(image=tk_img, text=""))
        label.image = tk_img 
    except Exception as e:
        label.after(0, lambda: label.config(text="[Image failed to load]", fg="#EF4444"))


# ==========================================
# AI PROCESSING CORE
# ==========================================
def execute_analysis(user_prompt, image_obj, snip_coords, screen_size):
    try:
        app_queue.put({"log": t("log_upload")})
        
        buffer = io.BytesIO()
        image_obj.save(buffer, format="JPEG", quality=85)
        img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        proxy_url = "https://dms.onl/s4106115/proxy.php" 
        
        payload = {
            "image": img_b64,
            "mimeType": "image/jpeg",
            "prompt": user_prompt,
            "hasHighlight": bool(snip_coords),
            "language": current_lang,
            "detailLevel": "detailed",
            "modelBackend": "smart"  
        }
        
        headers = {
            "X-Project-Secret": "SUPaSecureD_Key123!#"
        }

        app_queue.put({"log": t("log_analyze")})
        response = requests.post(proxy_url, json=payload, headers=headers, timeout=90)
        
        try:
            data = response.json()
        except Exception:
            raise ValueError("Invalid server response. Check proxy URL.")
            
        if response.status_code != 200 or "error" in data:
            raise ValueError(data.get("error", "Unknown server error."))
            
        unique_steps =[]
        seen_titles = set()
        for step in data.get('steps',[]):
            title = step.get('title', '').strip().lower()
            if title not in seen_titles:
                seen_titles.add(title)
                unique_steps.append(step)
        data['steps'] = unique_steps
        
        # --- LOCAL HISTORY SAVING ---
        try:
            history_file = "saved_history.json"
            history_data =[]
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
            
            history_data.append({
                "prompt": user_prompt,
                "data": data,
                "image": img_b64
            })
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save history: {e}")
        
        app_queue.put({"log": t("log_done")})
        app_queue.put({"data": data})
        
    except Exception as e:
        app_queue.put({"error": str(e)})

def check_queue():
    try:
        while True:
            msg = app_queue.get_nowait()
            if "data" in msg:
                draw_overlay(msg["data"])
            elif "log" in msg:
                update_terminal_log(msg["log"])
            elif "error" in msg:
                update_terminal_log(f"ERROR: {msg['error']}", is_error=True)
    except queue.Empty:
        pass
    root.after(100, check_queue)


# ==========================================
# TKINTER CORE
# ==========================================
root = tk.Tk()
root.title("Blueprint Lens UI Guide")
root.attributes('-fullscreen', True)
root.attributes('-topmost', True)

bg_color = 'magenta'
if sys.platform == "win32":
    root.config(bg=bg_color)
    root.attributes('-transparentcolor', bg_color)
else:
    root.config(bg='systemTransparent')
    root.wm_attributes('-transparent', True)

canvas = tk.Canvas(root, bg=bg_color, highlightthickness=0)
canvas.pack(fill='both', expand=True)

def reset_to_prompt():
    """Resets the overlay and goes back to the prompt window."""
    global side_panel, loading_panel, disclosure_win, initial_screenshot
    canvas.delete("all")
    root.withdraw()
    
    if side_panel: side_panel.destroy(); side_panel = None
    if loading_panel: loading_panel.destroy(); loading_panel = None
    if disclosure_win: disclosure_win.destroy(); disclosure_win = None
    
    initial_screenshot = None 
    show_prompt_window()


# ==========================================
# UI: HISTORY WINDOW
# ==========================================
def show_history_window():
    hist_win = tk.Toplevel(root)
    hist_win.title("Local History")
    hist_win.geometry("500x400")
    hist_win.configure(bg="#111827")
    hist_win.attributes('-topmost', True)
    hist_win.overrideredirect(True)
    
    x = (root.winfo_screenwidth() // 2) - 250
    y = (root.winfo_screenheight() // 2) - 200
    hist_win.geometry(f"+{x}+{y}")
    
    header = tk.Frame(hist_win, bg="#111827", cursor="fleur")
    header.pack(fill=tk.X, padx=20, pady=(15, 10))
    
    def start_move(e): hist_win.x, hist_win.y = e.x, e.y
    def stop_move(e): hist_win.x = hist_win.y = None
    def do_move(e): hist_win.geometry(f"+{hist_win.winfo_x() + (e.x - hist_win.x)}+{hist_win.winfo_y() + (e.y - hist_win.y)}")

    header.bind("<ButtonPress-1>", start_move)
    header.bind("<ButtonRelease-1>", stop_move)
    header.bind("<B1-Motion>", do_move)
    
    tk.Label(header, text="Local History", bg="#111827", fg="#00ffcc", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
    
    def close_history():
        hist_win.destroy()
        show_prompt_window()
        
    tk.Button(header, text="Close", bg="#EF4444", fg="white", font=("Arial", 9, "bold"), relief=tk.FLAT, command=close_history, cursor="hand2").pack(side=tk.RIGHT)
    
    list_frame = tk.Frame(hist_win, bg="#111827")
    list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
    
    hist_canvas = tk.Canvas(list_frame, bg="#111827", highlightthickness=0)
    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=hist_canvas.yview)
    scrollable_frame = tk.Frame(hist_canvas, bg="#111827")
    
    scrollable_frame.bind("<Configure>", lambda e: hist_canvas.configure(scrollregion=hist_canvas.bbox("all")))
    canvas_window = hist_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    hist_canvas.bind("<Configure>", lambda e: hist_canvas.itemconfig(canvas_window, width=e.width))
    hist_canvas.configure(yscrollcommand=scrollbar.set)
    
    hist_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    try:
        if os.path.exists("saved_history.json"):
            with open("saved_history.json", 'r', encoding='utf-8') as f:
                history_data = json.load(f)
                
            for item in reversed(history_data):
                prompt_text = item.get("prompt", "Unknown query")
                
                def load_item(item_data=item.get("data"), img_b64=item.get("image")):
                    global initial_screenshot
                    if img_b64:
                        try:
                            img_bytes = base64.b64decode(img_b64)
                            initial_screenshot = Image.open(io.BytesIO(img_bytes))
                        except Exception as e:
                            print("Error loading image from history:", e)
                    
                    hist_win.destroy()
                    draw_overlay(item_data)
                
                btn = tk.Button(scrollable_frame, text=prompt_text, bg="#1F2937", fg="white", font=("Arial", 11), relief=tk.FLAT, cursor="hand2", anchor="w", padx=10, pady=8, command=lambda data=item.get("data"), img=item.get("image"): load_item(data, img))
                btn.pack(fill=tk.X, pady=5)
        else:
            tk.Label(scrollable_frame, text="No history found.", bg="#111827", fg="#D1D5DB", font=("Arial", 11)).pack(pady=20)
    except Exception as e:
        tk.Label(scrollable_frame, text=f"Error loading history: {e}", bg="#111827", fg="#EF4444", font=("Arial", 11)).pack(pady=20)


# ==========================================
# UI: PROMPT WINDOW
# ==========================================
def show_prompt_window():
    global prompt_win, initial_screenshot, current_lang
    if prompt_win:
        prompt_win.destroy()
        
    if not initial_screenshot:
        initial_screenshot = pyautogui.screenshot()
        
    prompt_win = tk.Toplevel(root)
    prompt_win.title("Blueprint Lens")
    prompt_win.geometry("620x300")
    prompt_win.configure(bg="#111827")
    prompt_win.attributes('-topmost', True)
    prompt_win.overrideredirect(True)
    
    x = (root.winfo_screenwidth() // 2) - 310
    y = (root.winfo_screenheight() // 2) - 150
    prompt_win.geometry(f"+{x}+{y}")
    
    lang_var = tk.StringVar(value=current_lang)
    def switch_lang(*args):
        global current_lang
        current_lang = lang_var.get()
        prompt_win.destroy()
        show_prompt_window()
        
    lang_var.trace("w", switch_lang)

    header_frame = tk.Frame(prompt_win, bg="#111827", cursor="fleur")
    header_frame.pack(fill=tk.X, padx=20, pady=(15, 0))
    
    def start_move(e): prompt_win.x, prompt_win.y = e.x, e.y
    def stop_move(e): prompt_win.x = prompt_win.y = None
    def do_move(e): prompt_win.geometry(f"+{prompt_win.winfo_x() + (e.x - prompt_win.x)}+{prompt_win.winfo_y() + (e.y - prompt_win.y)}")

    header_frame.bind("<ButtonPress-1>", start_move)
    header_frame.bind("<ButtonRelease-1>", stop_move)
    header_frame.bind("<B1-Motion>", do_move)
    
    title_lbl = tk.Label(header_frame, text=t("title"), bg="#111827", fg="#00ffcc", font=("Arial", 16, "bold"), cursor="fleur")
    title_lbl.pack(side=tk.LEFT)
    title_lbl.bind("<ButtonPress-1>", start_move)
    title_lbl.bind("<ButtonRelease-1>", stop_move)
    title_lbl.bind("<B1-Motion>", do_move)

    lang_menu = ttk.Combobox(header_frame, textvariable=lang_var, values=["EN", "VI"], state="readonly", width=4)
    lang_menu.pack(side=tk.RIGHT)
    
    tk.Label(prompt_win, text=t("instruction"), bg="#111827", fg="#9CA3AF", font=("Arial", 11), wraplength=550, justify=tk.LEFT).pack(padx=20, pady=(10, 15), anchor="w")
    
    entry = tk.Entry(prompt_win, font=("Arial", 14), bg="#1F2937", fg="white", insertbackground="white", relief=tk.FLAT)
    entry.insert(0, t("placeholder"))
    entry.bind("<FocusIn>", lambda e: entry.delete(0, tk.END) if entry.get() == t("placeholder") else None)
    entry.pack(fill=tk.X, padx=20, pady=5, ipady=8)
    entry.focus()
    
    # 2-Row Layout for cleaner UI
    btn_frame1 = tk.Frame(prompt_win, bg="#111827")
    btn_frame1.pack(fill=tk.X, padx=20, pady=(15, 5))
    
    btn_frame2 = tk.Frame(prompt_win, bg="#111827")
    btn_frame2.pack(fill=tk.X, padx=20, pady=(5, 10))
    
    def on_locate():
        text = entry.get().strip()
        if text and text != t("placeholder"):
            prompt_win.destroy()
            show_disclosure_window(text, None, initial_screenshot)
            
    def on_snip():
        text = entry.get().strip()
        if text and text != t("placeholder"):
            prompt_win.destroy()
            begin_snipping_mode(text)
            
    def on_cancel():
        global initial_screenshot
        initial_screenshot = None
        prompt_win.destroy()
        root.withdraw()
        
    def open_history():
        prompt_win.destroy()
        show_history_window()
        
    def on_import():
        file_path = filedialog.askopenfilename(filetypes=[("Blueprint Lens Guide", "*.cguide"), ("JSON Files", "*.json")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_pkg = json.load(f)
                
                global initial_screenshot
                img_b64 = imported_pkg.get("image")
                data = imported_pkg.get("data")
                if img_b64 and data:
                    img_bytes = base64.b64decode(img_b64)
                    initial_screenshot = Image.open(io.BytesIO(img_bytes))
                    prompt_win.destroy()
                    root.deiconify() 
                    draw_overlay(data)
            except Exception as e:
                print(f"Error importing guide: {e}")
                
    def on_quick_inspect():
        prompt_win.destroy()
        begin_quick_inspect()

    # ROW 1
    tk.Button(btn_frame1, text=t("cancel"), bg="#EF4444", fg="white", font=("Arial", 10, "bold"), relief=tk.FLAT, command=on_cancel, cursor="hand2", padx=10, pady=5).pack(side=tk.LEFT)
    tk.Button(btn_frame1, text=t("locate"), bg="#00ffcc", fg="black", font=("Arial", 10, "bold"), relief=tk.FLAT, command=on_locate, cursor="hand2", padx=10, pady=5).pack(side=tk.RIGHT, padx=(10,0))
    tk.Button(btn_frame1, text=t("snip"), bg="#374151", fg="white", font=("Arial", 10, "bold"), relief=tk.FLAT, command=on_snip, cursor="hand2", padx=10, pady=5).pack(side=tk.RIGHT)

    # ROW 2
    tk.Button(btn_frame2, text="View History", bg="#8B5CF6", fg="white", font=("Arial", 10, "bold"), relief=tk.FLAT, command=open_history, cursor="hand2", padx=10, pady=5).pack(side=tk.LEFT)
    tk.Button(btn_frame2, text="Import Guide", bg="#10B981", fg="white", font=("Arial", 10, "bold"), relief=tk.FLAT, command=on_import, cursor="hand2", padx=10, pady=5).pack(side=tk.LEFT, padx=(10, 0))
    tk.Button(btn_frame2, text="Quick Inspect", bg="#F59E0B", fg="white", font=("Arial", 10, "bold"), relief=tk.FLAT, command=on_quick_inspect, cursor="hand2", padx=10, pady=5).pack(side=tk.RIGHT)


# ==========================================
# UI: SNIPPING & QUICK INSPECT
# ==========================================
def begin_quick_inspect():
    global snip_win
    snip_win = tk.Toplevel(root)
    snip_win.attributes('-fullscreen', True)
    snip_win.attributes('-topmost', True)
    snip_win.configure(cursor="crosshair")
    
    tk_img = ImageTk.PhotoImage(initial_screenshot)
    snip_canvas = tk.Canvas(snip_win, highlightthickness=0)
    snip_canvas.pack(fill='both', expand=True)
    snip_canvas.create_image(0, 0, image=tk_img, anchor='nw')
    snip_canvas.image = tk_img 
    
    def on_click(e):
        snip_win.destroy()
        
        # Define 150x150 boundary (bound to screen edges)
        x1 = max(0, e.x - 75)
        y1 = max(0, e.y - 75)
        x2 = min(root.winfo_screenwidth(), e.x + 75)
        y2 = min(root.winfo_screenheight(), e.y + 75)
        
        snip_coords = (x1, y1, x2, y2)
        prompt_text = "Identify the specific UI button or element at these exact coordinates and explain what it does."
        
        show_loading_ui()
        screen_size = (root.winfo_screenwidth(), root.winfo_screenheight())
        
        full_img_to_send = initial_screenshot.copy()
        draw = ImageDraw.Draw(full_img_to_send)
        draw.rectangle(snip_coords, outline="red", width=6)
        
        threading.Thread(target=execute_analysis, args=(prompt_text, full_img_to_send, snip_coords, screen_size), daemon=True).start()

    snip_canvas.bind("<ButtonRelease-1>", on_click)
    snip_win.bind("<Escape>", lambda e:[snip_win.destroy(), show_prompt_window()])

def begin_snipping_mode(prompt_text):
    global snip_win
    snip_win = tk.Toplevel(root)
    snip_win.attributes('-fullscreen', True)
    snip_win.attributes('-topmost', True)
    snip_win.configure(cursor="crosshair")
    
    tk_img = ImageTk.PhotoImage(initial_screenshot)
    snip_canvas = tk.Canvas(snip_win, highlightthickness=0)
    snip_canvas.pack(fill='both', expand=True)
    snip_canvas.create_image(0, 0, image=tk_img, anchor='nw')
    snip_canvas.image = tk_img 
    
    rect_id = None
    start_x = start_y = 0
    
    def on_press(e):
        nonlocal start_x, start_y, rect_id
        start_x, start_y = e.x, e.y
        rect_id = snip_canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="red", width=3, dash=(4, 4))
        
    def on_drag(e):
        snip_canvas.coords(rect_id, start_x, start_y, e.x, e.y)
        
    def on_release(e):
        x1, y1, x2, y2 = min(start_x, e.x), min(start_y, e.y), max(start_x, e.x), max(start_y, e.y)
        snip_win.destroy()
        
        if abs(x2 - x1) > 15 and abs(y2 - y1) > 15:
            show_disclosure_window(prompt_text, (x1, y1, x2, y2), initial_screenshot)
        else:
            show_prompt_window()

    snip_canvas.bind("<ButtonPress-1>", on_press)
    snip_canvas.bind("<B1-Motion>", on_drag)
    snip_canvas.bind("<ButtonRelease-1>", on_release)
    snip_win.bind("<Escape>", lambda e:[snip_win.destroy(), show_prompt_window()])


# ==========================================
# UI: DISCLOSURE & PREVIEW
# ==========================================
def show_disclosure_window(prompt_text, snip_coords, original_img):
    global disclosure_win
    disclosure_win = tk.Toplevel(root)
    disclosure_win.title("Consent")
    disclosure_win.geometry("450x580")
    disclosure_win.configure(bg="#111827")
    disclosure_win.attributes('-topmost', True)
    disclosure_win.overrideredirect(True)
    
    x = (root.winfo_screenwidth() // 2) - 225
    y = (root.winfo_screenheight() // 2) - 290 
    disclosure_win.geometry(f"+{x}+{y}")
    
    tk.Label(disclosure_win, text=t("disc_title"), bg="#111827", fg="#00ffcc", font=("Arial", 14, "bold")).pack(pady=(20, 10))
    
    full_img_to_send = original_img.copy()
    if snip_coords:
        draw = ImageDraw.Draw(full_img_to_send)
        draw.rectangle(snip_coords, outline="red", width=6)
        
    thumb_img = full_img_to_send.copy()
    thumb_img.thumbnail((350, 200), Image.Resampling.LANCZOS)
    tk_thumb = ImageTk.PhotoImage(thumb_img)
    
    img_lbl = tk.Label(disclosure_win, image=tk_thumb, bg="#1F2937", bd=2, relief=tk.SOLID)
    img_lbl.image = tk_thumb
    img_lbl.pack(pady=10)
    
    tk.Label(disclosure_win, text=t("disc_msg"), bg="#111827", fg="#D1D5DB", font=("Arial", 10), wraplength=380, justify=tk.LEFT).pack(padx=20, pady=(15, 25))
    
    btn_frame = tk.Frame(disclosure_win, bg="#111827")
    btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
    
    def on_accept():
        disclosure_win.destroy()
        show_loading_ui()
        screen_size = (root.winfo_screenwidth(), root.winfo_screenheight())
        threading.Thread(target=execute_analysis, args=(prompt_text, full_img_to_send, snip_coords, screen_size), daemon=True).start()
        
    def on_back():
        disclosure_win.destroy()
        show_prompt_window()
        
    tk.Button(btn_frame, text=t("go_back"), bg="#374151", fg="white", font=("Arial", 10, "bold"), relief=tk.FLAT, bd=0, command=on_back, cursor="hand2", padx=10, pady=8).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
    tk.Button(btn_frame, text=t("accept"), bg="#00ffcc", fg="black", font=("Arial", 10, "bold"), relief=tk.FLAT, bd=0, command=on_accept, cursor="hand2", padx=10, pady=8).pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0))


# ==========================================
# UI: LOADING & LOG CONSOLE
# ==========================================
log_text_widget = None
dots_label = None
dots_counter = 0

def show_loading_ui():
    global loading_panel, log_text_widget, dots_label, animation_active
    
    loading_panel = tk.Toplevel(root)
    loading_panel.title("Processing")
    loading_panel.geometry("400x220")
    loading_panel.configure(bg="#1E1E1E")
    loading_panel.attributes('-topmost', True)
    loading_panel.overrideredirect(True)
    
    x = (root.winfo_screenwidth() // 2) - 200
    y = (root.winfo_screenheight() // 2) - 110
    loading_panel.geometry(f"+{x}+{y}")
    
    header_frame = tk.Frame(loading_panel, bg="#1E1E1E")
    header_frame.pack(fill=tk.X, pady=(15, 5))
    
    tk.Label(header_frame, text=t("thinking"), bg="#1E1E1E", fg="#00ffcc", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=(20, 0))
    dots_label = tk.Label(header_frame, text="", bg="#1E1E1E", fg="#00ffcc", font=("Arial", 12, "bold"), width=3, anchor="w")
    dots_label.pack(side=tk.LEFT)
    
    log_frame = tk.Frame(loading_panel, bg="#000000", bd=1, relief=tk.SOLID)
    log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 20))
    
    log_text_widget = tk.Text(log_frame, bg="#0A0A0A", fg="#A3A3A3", font=("Consolas", 9), height=6, relief=tk.FLAT, state=tk.DISABLED)
    log_text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    app_queue.put({"log": t("log_start")})
    
    animation_active = True
    animate_dots()

def animate_dots():
    global dots_counter, animation_active
    if not animation_active or not loading_panel or not loading_panel.winfo_exists():
        return
    dots_label.config(text="." * (dots_counter % 4))
    dots_counter += 1
    root.after(400, animate_dots)

def update_terminal_log(msg, is_error=False):
    if log_text_widget and log_text_widget.winfo_exists():
        log_text_widget.config(state=tk.NORMAL)
        color = "red" if is_error else "#A3A3A3"
        log_text_widget.insert(tk.END, f"> {msg}\n")
        log_text_widget.see(tk.END)
        log_text_widget.config(state=tk.DISABLED)


# ==========================================
# SPOTLIGHT & SIDEBAR RENDERING
# ==========================================
active_spotlight_idx = -1
spotlight_color_toggle = True

def animate_spotlight():
    global spotlight_color_toggle
    if not drawn_rectangles:
        return
        
    color = "#00ffcc" if spotlight_color_toggle else "#ffffff"
    spotlight_color_toggle = not spotlight_color_toggle
    
    for i, item in enumerate(drawn_rectangles):
        if i == active_spotlight_idx:
            canvas.itemconfig(item["rect"], outline=color)
            
    root.after(500, animate_spotlight)

def highlight_box(selected_idx):
    global active_spotlight_idx
    
    # Toggle Mechanism
    if active_spotlight_idx == selected_idx:
        active_spotlight_idx = -1
        for item in drawn_rectangles:
            canvas.itemconfig(item["rect"], state="hidden")
            canvas.itemconfig(item["badge"], state="hidden")
            canvas.itemconfig(item["text"], state="hidden")
            
        for card_dict in step_cards:
            card_dict['main'].configure(bg="#1F2937")
            card_dict['title_frame'].configure(bg="#1F2937")
            card_dict['title_lbl'].configure(bg="#1F2937")
            card_dict['desc_lbl'].configure(bg="#1F2937")
            card_dict['num_lbl'].configure(bg="#D1D5DB", fg="#111827")
            if card_dict.get('btns_frame'):
                card_dict['btns_frame'].configure(bg="#1F2937")
        return

    # Normal Activation
    active_spotlight_idx = selected_idx
    
    for i, item in enumerate(drawn_rectangles):
        state = "normal" if i == selected_idx else "hidden"
        canvas.itemconfig(item["rect"], state=state, outline="#00ffcc")
        canvas.itemconfig(item["badge"], state=state)
        canvas.itemconfig(item["text"], state=state)
        
    for i, card_dict in enumerate(step_cards):
        if i == selected_idx:
            card_dict['main'].configure(bg="#374151")
            card_dict['title_frame'].configure(bg="#374151")
            card_dict['title_lbl'].configure(bg="#374151")
            card_dict['desc_lbl'].configure(bg="#374151")
            card_dict['num_lbl'].configure(bg="#00ffcc", fg="black")
            if card_dict.get('btns_frame'):
                card_dict['btns_frame'].configure(bg="#374151")
        else:
            card_dict['main'].configure(bg="#1F2937")
            card_dict['title_frame'].configure(bg="#1F2937")
            card_dict['title_lbl'].configure(bg="#1F2937")
            card_dict['desc_lbl'].configure(bg="#1F2937")
            card_dict['num_lbl'].configure(bg="#D1D5DB", fg="#111827")
            if card_dict.get('btns_frame'):
                card_dict['btns_frame'].configure(bg="#1F2937")

def open_web_search(query):
    webbrowser.open(f"https://www.google.com/search?q={requests.utils.quote(query)}")

def open_youtube_search(query):
    webbrowser.open(f"https://www.youtube.com/results?search_query={requests.utils.quote(query)}")

def draw_overlay(data):
    global side_panel, loading_panel, drawn_rectangles, step_cards, animation_active, initial_screenshot, active_spotlight_idx
    
    animation_active = False
    active_spotlight_idx = -1
    
    if loading_panel:
        loading_panel.destroy()
        loading_panel = None
        
    root.deiconify()
    canvas.delete("all")
    drawn_rectangles =[]
    step_cards =[]
    
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    
    steps = data.get('steps',[])
    for idx, step in enumerate(steps):
        bbox = step.get('bbox', {})
        x1_norm = bbox.get('x1', 0)
        y1_norm = bbox.get('y1', 0)
        x2_norm = bbox.get('x2', 0)
        y2_norm = bbox.get('y2', 0)
        
        x1 = (x1_norm / 1000.0) * screen_w
        y1 = (y1_norm / 1000.0) * screen_h
        x2 = (x2_norm / 1000.0) * screen_w
        y2 = (y2_norm / 1000.0) * screen_h
        
        step['calc_x1'] = x1
        step['calc_y1'] = y1
        step['calc_x2'] = x2
        step['calc_y2'] = y2
        
        rect_id = canvas.create_rectangle(x1, y1, x2, y2, outline="#00ffcc", width=4, state="hidden")
        badge_bg = canvas.create_oval(x1-14, y1-14, x1+14, y1+14, fill="#00ffcc", outline="", state="hidden")
        badge_text = canvas.create_text(x1, y1, text=str(idx+1), fill="black", font=("Arial", 11, "bold"), state="hidden")
        
        drawn_rectangles.append({"rect": rect_id, "badge": badge_bg, "text": badge_text})

    if side_panel: side_panel.destroy()
        
    side_panel = tk.Toplevel(root)
    side_panel.title("AI Guide")
    panel_width = 400
    panel_height = min(800, screen_h - 100)
    side_panel.geometry(f"{panel_width}x{panel_height}+{screen_w - panel_width - 20}+50")
    side_panel.configure(bg="#111827")
    side_panel.attributes('-topmost', True)
    side_panel.overrideredirect(True)
    
    # --- RESIZABLE BORDER ---
    resizer = tk.Frame(side_panel, bg="#374151", width=5, cursor="sb_h_double_arrow")
    resizer.pack(side=tk.LEFT, fill=tk.Y)
    
    def start_resize(e):
        side_panel._resize_start_x = e.x_root
        side_panel._start_width = side_panel.winfo_width()
        side_panel._start_xpos = side_panel.winfo_x()

    def do_resize(e):
        dx = e.x_root - side_panel._resize_start_x
        new_width = side_panel._start_width - dx
        new_x = side_panel._start_xpos + dx
        if new_width > 300 and new_width < screen_w - 50:
            side_panel.geometry(f"{new_width}x{side_panel.winfo_height()}+{new_x}+{side_panel.winfo_y()}")

    resizer.bind("<ButtonPress-1>", start_resize)
    resizer.bind("<B1-Motion>", do_resize)
    
    # --- MAIN CONTENT WRAPPER ---
    main_content = tk.Frame(side_panel, bg="#111827")
    main_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def start_move(e): side_panel.x, side_panel.y = e.x, e.y
    def stop_move(e): side_panel.x = side_panel.y = None
    def do_move(e): side_panel.geometry(f"+{side_panel.winfo_x() + (e.x - side_panel.x)}+{side_panel.winfo_y() + (e.y - side_panel.y)}")

    header = tk.Frame(main_content, bg="#111827", height=45, cursor="fleur")
    header.pack(fill=tk.X)
    header.bind("<ButtonPress-1>", start_move)
    header.bind("<ButtonRelease-1>", stop_move)
    header.bind("<B1-Motion>", do_move)
    
    tk.Label(header, text=t("ai_guide"), bg="#111827", fg="#00ffcc", font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=15, pady=10)

    canvas_container = tk.Canvas(main_content, bg="#111827", highlightthickness=0)
    scrollbar = ttk.Scrollbar(main_content, orient="vertical", command=canvas_container.yview)
    scrollable_frame = tk.Frame(canvas_container, bg="#111827")

    scrollable_frame.bind("<Configure>", lambda e: canvas_container.configure(scrollregion=canvas_container.bbox("all")))
    canvas_window = canvas_container.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas_container.bind("<Configure>", lambda e: canvas_container.itemconfig(canvas_window, width=e.width))
    canvas_container.configure(yscrollcommand=scrollbar.set)

    canvas_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=(10,0))
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    for idx, step in enumerate(steps):
        card = tk.Frame(scrollable_frame, bg="#1F2937", bd=0, cursor="hand2")
        card.pack(fill=tk.X, pady=8, padx=10)
        
        def make_handler(i): return lambda e: highlight_box(i)
        handler = make_handler(idx)
        card.bind("<Button-1>", handler)
        
        title_frame = tk.Frame(card, bg="#1F2937")
        title_frame.pack(fill=tk.X, padx=15, pady=(12, 5))
        title_frame.bind("<Button-1>", handler)
        
        num_lbl = tk.Label(title_frame, text=str(idx+1), bg="#D1D5DB", fg="#111827", font=("Arial", 10, "bold"), width=2)
        num_lbl.pack(side=tk.LEFT)
        num_lbl.bind("<Button-1>", handler)
        
        title_lbl = tk.Label(title_frame, text=step.get('title', 'Action'), bg="#1F2937", fg="white", font=("Arial", 11, "bold"), wraplength=180, justify=tk.LEFT)
        title_lbl.pack(side=tk.LEFT, padx=10)
        title_lbl.bind("<Button-1>", handler)
        
        btns_frame = tk.Frame(title_frame, bg="#1F2937")
        btns_frame.pack(side=tk.RIGHT)
        
        yt_term = step.get('youtube_search_term')
        if yt_term:
            yt_btn = tk.Button(btns_frame, text="▶ YouTube", bg="#EF4444", fg="white", font=("Arial", 8, "bold"), relief=tk.FLAT, command=lambda q=yt_term: open_youtube_search(q), cursor="hand2")
            yt_btn.pack(side=tk.LEFT, padx=(0, 5))
            
        g_term = step.get('google_search_1')
        if g_term:
            g_btn = tk.Button(btns_frame, text="🔍 Web", bg="#3B82F6", fg="white", font=("Arial", 8, "bold"), relief=tk.FLAT, command=lambda q=g_term: open_web_search(q), cursor="hand2")
            g_btn.pack(side=tk.LEFT)
            
        if initial_screenshot:
            try:
                img_w, img_h = initial_screenshot.size
                pad = 10
                crop_x1 = max(0, min(step['calc_x1'] - pad, img_w - 1))
                crop_y1 = max(0, min(step['calc_y1'] - pad, img_h - 1))
                crop_x2 = max(0, min(step['calc_x2'] + pad, img_w))
                crop_y2 = max(0, min(step['calc_y2'] + pad, img_h))
                
                if crop_x2 > crop_x1 and crop_y2 > crop_y1:
                    cropped_img = initial_screenshot.crop((crop_x1, crop_y1, crop_x2, crop_y2))
                    max_w = 250
                    
                    if cropped_img.width > max_w:
                        ratio = max_w / float(cropped_img.width)
                        new_h = int(float(cropped_img.height) * ratio)
                        cropped_img = cropped_img.resize((max_w, new_h), Image.Resampling.LANCZOS)
                        
                    tk_thumb = ImageTk.PhotoImage(cropped_img)
                    img_lbl = tk.Label(card, image=tk_thumb, bg="#111827", bd=2, relief=tk.SOLID)
                    img_lbl.image = tk_thumb 
                    img_lbl.pack(fill=tk.X, padx=15, pady=(5, 5))
                    img_lbl.bind("<Button-1>", handler)
            except Exception as e:
                print(f"Failed to generate cropped image: {e}")
        
        desc_text = step.get('description', '')
        img_matches = re.findall(r'!\[.*?\]\((.*?)\)', desc_text)
        clean_desc = re.sub(r'!\[.*?\]\(.*?\)', '', desc_text).strip()
        clean_desc = re.sub(r'\*\*(.*?)\*\*', r'\1', clean_desc) 
        clean_desc = re.sub(r'\*(.*?)\*', r'\1', clean_desc)     
        
        desc_lbl = tk.Label(card, text=clean_desc, bg="#1F2937", fg="#D1D5DB", font=("Arial", 10), justify=tk.LEFT, wraplength=310)
        desc_lbl.pack(fill=tk.X, padx=15, pady=(0, 5) if img_matches else (0, 12), anchor="w")
        desc_lbl.bind("<Button-1>", handler)

        if img_matches:
            img_frame = tk.Frame(card, bg="#1F2937")
            img_frame.pack(fill=tk.X, padx=15, pady=(0, 12))
            img_frame.bind("<Button-1>", handler)
            
            for url in img_matches:
                md_img_lbl = tk.Label(img_frame, text="Loading image...", bg="#1F2937", fg="#9CA3AF", font=("Arial", 9, "italic"))
                md_img_lbl.pack(pady=4)
                md_img_lbl.bind("<Button-1>", handler)
                threading.Thread(target=load_and_display_image, args=(url, md_img_lbl), daemon=True).start()

        step_cards.append({
            'main': card, 'title_frame': title_frame, 'num_lbl': num_lbl, 
            'title_lbl': title_lbl, 'btns_frame': btns_frame, 'desc_lbl': desc_lbl
        })

    def on_export():
        file_path = filedialog.asksaveasfilename(defaultextension=".cguide", filetypes=[("Blueprint Lens Guide", "*.cguide")])
        if file_path:
            try:
                buffer = io.BytesIO()
                initial_screenshot.save(buffer, format="JPEG", quality=85)
                img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                export_pkg = {
                    "data": data,
                    "image": img_b64
                }
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_pkg, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Error exporting guide: {e}")

    footer = tk.Frame(main_content, bg="#111827")
    footer.pack(fill=tk.X, pady=10, padx=15)
    tk.Button(footer, text="Export Guide", bg="#10B981", fg="white", font=("Arial", 10, "bold"), relief=tk.FLAT, command=on_export, cursor="hand2", pady=5).pack(fill=tk.X, pady=(0, 5))
    tk.Button(footer, text=t("done"), bg="#EF4444", fg="white", font=("Arial", 11, "bold"), relief=tk.FLAT, command=reset_to_prompt, cursor="hand2", pady=8).pack(fill=tk.X)

    def _on_mousewheel(event):
        canvas_container.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas_container.bind_all("<MouseWheel>", _on_mousewheel)

    if steps:
        highlight_box(0)
        animate_spotlight()


def on_hotkey():
    global initial_screenshot
    initial_screenshot = None
    root.after(0, show_prompt_window)

# Init
root.withdraw()
print("[*] Blueprint Lens Bridge active.")
print("[*] Listening for Ctrl+Shift+Q ...")

keyboard.add_hotkey('ctrl+shift+q', on_hotkey)

root.after(100, check_queue)
root.mainloop()