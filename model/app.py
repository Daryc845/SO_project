from flask import Flask, render_template, jsonify, send_file
import psutil
import os
import sys
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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from view.TaskManager import TaskManagerApp

app = Flask(__name__)

# Variables globales
process_data = []
ordenamiento = "cpu"  # opciones: nombre, cpu, memoria, tiempo
forma = "desc"           # opciones: asc, desc
icon_cache = {}          # Caché global para íconos
previous_process_data = {}  # Caché para datos de procesos anteriores

# Obtener ícono del ejecutable
def get_icon_from_exe(exe_path, pid, process_name):
    key = (pid, process_name)  # Usar una combinación de PID y nombre como clave
    if key in icon_cache:  # Si el ícono ya está en caché, úsalo
        return icon_cache[key]
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
            icon_cache[key] = buffer  # Almacenar en caché
            return buffer
    except Exception as e:
        print(f"Error obteniendo icono: {e}")
    return None

# Obtener procesos
def get_processes():
    global previous_process_data, ordenamiento, forma
    current_process_data = {}
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
            status = estado_traducciones.get(info['status'], "Desconocido")
            cpu = info['cpu_percent']
            memory = round(info['memory_info'].rss / (1024 * 1024), 2)
            icon_path = f"/icon/{pid}"
            create_time = info['create_time']
            now = time.time()
            uptime_seconds = int(now - create_time)
            uptime = f"{uptime_seconds // 60}:{uptime_seconds % 60:02d}"  # Formato minutos:segundos

            # Crear un hash único para el proceso actual
            current_process_data[pid] = (name, status, cpu, memory, uptime)

            # Actualizar o agregar procesos
            if pid not in previous_process_data or previous_process_data[pid] != current_process_data[pid]:
                process_matrix.append([pid, icon_path, name, status, cpu, memory, uptime])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Eliminar procesos que ya no existen
    for pid in list(previous_process_data.keys()):
        if pid not in current_process_data:
            del previous_process_data[pid]

    # Actualizar el estado anterior
    previous_process_data = current_process_data

    # Ordenar solo si el ordenamiento ha cambiado
    sort_index = {
        "pid": 0,
        "nombre": 2,
        "estado": 3,
        "cpu": 4,
        "memoria": 5,
        "tiempo": 6
    }.get(ordenamiento, 4)

    if ordenamiento != "tiempo" or forma != "desc":
        process_matrix.sort(key=lambda x: x[sort_index], reverse=(forma == "desc"))

    return process_matrix

# Actualización de procesos en segundo plano
def actualizar_procesos():
    global process_data
    while True:
        process_data = get_processes()
        time.sleep(1)


