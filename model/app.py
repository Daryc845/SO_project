from flask import Flask, render_template, jsonify, send_file
import psutil
import os
from threading import Thread
import time
from win32gui import DestroyIcon
from win32ui import CreateDCFromHandle, CreateBitmap
from win32con import SRCCOPY
import ctypes
from PIL import Image
import io
import win32gui
import datetime

app = Flask(__name__)

# Variables globales
process_data = []
ordenamiento = "nombre"  # opciones: nombre, cpu, memoria
forma = "desc"        # opciones: asc, desc

# Actualización de procesos en segundo plano
def actualizar_procesos():
    global process_data
    while True:
        process_data = get_processes()
        time.sleep(1)

# Ordenamientos
def get_processes():
    process_matrix = []
    estado_traducciones = {
        "running": "En ejecución",
        "sleeping": "Durmiendo",
        "stopped": "Detenido",
        "zombie": "Zombie",
        "idle": "Inactivo",
        "dead": "Muerto",
        "waiting": "Esperando"
    }

    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'exe', 'create_time', 'status']):
        try:
            info = proc.info
            pid = info['pid']
            name = info['name']
            status = estado_traducciones.get(info['status'], "Desconocido")  # Traducir el estado
            cpu = info['cpu_percent']
            memory = round(info['memory_info'].rss / (1024 * 1024), 2)
            icon_path = f"/icon/{pid}"
            create_time = info['create_time']
            now = time.time()
            uptime = int(now - create_time)  # Tiempo de ejecución en segundos

            # Agregar el estado después del nombre
            process_matrix.append([pid, icon_path, name, status, cpu, memory, uptime])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    global ordenamiento, forma
    sort_index = {
        "pid": 0,
        "nombre": 2,
        "estado": 3,
        "cpu": 4,
        "memoria": 5,
        "tiempo": 6  # Nuevo índice para ordenar por tiempo de ejecución
    }.get(ordenamiento, 4)

    process_matrix.sort(key=lambda x: x[sort_index], reverse=(forma == "desc"))
    return process_matrix

# Extraer ícono del ejecutable
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
            img = Image.frombuffer('RGBA', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRA', 0, 1)

            DestroyIcon(ico)
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            return buffer
    except Exception as e:
        print(f"Error obteniendo icono: {e}")
    return None

# Rutas Flask
@app.route("/")
def index():
    global process_data
    return render_template("index.html", procesos=process_data)

@app.route("/procesos")
def procesos():
    global process_data
    return jsonify(process_data)

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

@app.route("/boton", methods=["POST"])
def boton():
    print("presionado")
    return jsonify({"status": "Botón presionado"})

if __name__ == "__main__":
    hilo = Thread(target=actualizar_procesos, daemon=True)
    hilo.start()
    app.run(debug=True)
