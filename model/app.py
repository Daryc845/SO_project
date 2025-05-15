from flask import Flask, render_template, jsonify, send_file
import psutil
import os
from win32gui import DestroyIcon
from win32ui import CreateDCFromHandle, CreateBitmap
from win32con import SRCCOPY
import ctypes
from PIL import Image
import io
import win32gui

app = Flask(__name__)

# Obtener los procesos del sistema
def get_processes():
    process_list = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'exe']):
        try:
            info = proc.info
            process_list.append({
                'pid': info['pid'],
                'name': info['name'],
                'cpu': info['cpu_percent'],
                'memory': round(info['memory_info'].rss / (1024 * 1024), 2),  # en MB
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return process_list

# Extraer el ícono de un ejecutable
def get_icon_from_exe(exe_path):
    try:
        large, _ = win32gui.ExtractIconEx(exe_path, 0)
        if large:
            ico = large[0]
            hdc = CreateDCFromHandle(ctypes.windll.user32.GetDC(0))
            bmp = CreateBitmap()
            bmp.CreateCompatibleBitmap(hdc, 32, 32)
            hdc_mem = hdc.CreateCompatibleDC()
            hdc_mem.SelectObject(bmp)
            win32gui.DrawIconEx(hdc_mem.GetSafeHdc(), 0, 0, ico, 32, 32, 0, None, 3)
            bmpinfo = bmp.GetInfo()
            bmpstr = bmp.GetBitmapBits(True)
            img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
            DestroyIcon(ico)
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            return buffer
    except Exception as e:
        print(f"Error obteniendo icono: {e}")
    return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/procesos")
def procesos():
    return jsonify(get_processes())

@app.route("/icon/<int:pid>")
def icon(pid):
    try:
        p = psutil.Process(pid)
        exe = p.exe()
        if os.path.exists(exe):
            icon = get_icon_from_exe(exe)
            if icon:
                return send_file(icon, mimetype="image/png")
    except:
        pass
    return send_file("static/default.png", mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)
