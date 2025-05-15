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

app = Flask(__name__)

# Variable global para almacenar los procesos
process_data = []
ordenamiento = "cpu"  # opciones: nombre, cpu, memoria
forma = "desc"            # opciones: asc, desc

# Función para actualizar los procesos en segundo plano
def actualizar_procesos():
    global process_data
    while True:
        process_data = get_processes()
        time.sleep(1)  # Actualizar cada segundo



def ordenar_por_nombre(lista):
    return sorted(lista, key=lambda x: x['name'].lower())

def ordenar_por_cpu(lista):
    return sorted(lista, key=lambda x: x['cpu'])

def ordenar_por_memoria(lista):
    return sorted(lista, key=lambda x: x['memory'])

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

    # Ordenar según la variable global
    global ordenamiento, forma
    if ordenamiento == "nombre":
        process_list = ordenar_por_nombre(process_list)
    elif ordenamiento == "cpu":
        process_list = ordenar_por_cpu(process_list)
    elif ordenamiento == "memoria":
        process_list = ordenar_por_memoria(process_list)

    if forma == "desc":
        process_list.reverse()

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

            # Crear una imagen con transparencia
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
    # Iniciar el hilo para actualizar los procesos
    hilo = Thread(target=actualizar_procesos, daemon=True)
    hilo.start()

    # Iniciar la aplicación Flask
    app.run(debug=True)
