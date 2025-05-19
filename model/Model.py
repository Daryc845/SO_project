import psutil
import time
from win32gui import DestroyIcon
from win32ui import CreateDCFromHandle, CreateBitmap
import ctypes
from PIL import Image
import io
import win32gui
import os

class Model:
    def __init__(self):
        self.process_data = []
        self.order_cryteria = "cpu"
        self.order_method = "desc"
        self.search_cryteria = ""
        self.icon_cache = {}
        self.previous_process_data = {}
        self.default_icon_img = None
        self.set_default_icon()
        
    def set_default_icon(self):
        try:
            self.default_icon_img = Image.open("static/default.png").convert("RGBA")
            self.default_icon_img = self.default_icon_img.resize((26, 26), Image.LANCZOS)
        except Exception as e2:
            print(f"Error cargando icono por defecto: {e2}")
        
    def get_icon_from_exe(self, exe_path, pid, process_name):
        key = (pid, process_name)
        if key in self.icon_cache:
            return self.icon_cache[key]
            
        try:
            large, _ = win32gui.ExtractIconEx(exe_path, 0)
            if large:
                ico = large[0]
                hdc = CreateDCFromHandle(ctypes.windll.user32.GetDC(0))
                bmp = CreateBitmap()
                bmp.CreateCompatibleBitmap(hdc, 32, 32)
                hdc_mem = hdc.CreateCompatibleDC()
                hdc_mem.SelectObject(bmp)
                win32gui.DrawIconEx(hdc_mem.GetSafeHdc(), 0, 0, ico, 26, 26, 0, None, 3)

                bmpinfo = bmp.GetInfo()
                bmpstr = bmp.GetBitmapBits(True)
                img = Image.frombuffer('RGBA', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRA', 0, 1)

                DestroyIcon(ico)
                self.icon_cache[key] = img
                return img
            else:
                # Forzar excepción si no hay icono extraído
                raise Exception("No se pudo extraer el icono")
        except Exception as e:
            print(f"Error obteniendo ícono para {exe_path}: {e}")
            self.icon_cache[key] = self.default_icon_img
            return self.default_icon_img
        

    def get_processes(self):
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

        search = str(self.search_cryteria).lower().strip()

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'exe', 'create_time', 'status']):
            try:
                info = proc.info
                pid = info['pid']
                name = info['name']
                status = estado_traducciones.get(info['status'], "Desconocido")
                cpu = info['cpu_percent']
                memory = round(info['memory_info'].rss / (1024 * 1024), 2)
                icon = self.get_icon_from_exe(info['exe'], pid, name)
                create_time = info['create_time']
                now = time.time()
                uptime_seconds = int(now - create_time)
                uptime = f"{uptime_seconds // 60}:{uptime_seconds % 60:02d}"

                current_process_data[pid] = (name, icon, status, cpu, memory, uptime)

                # FILTRO: solo agrega si search está en el PID o en el nombre
                if search:
                    if search in str(pid).lower() or search in str(name).lower():
                        if pid not in self.previous_process_data or self.previous_process_data[pid] != current_process_data[pid]:
                            process_matrix.append([pid, icon, name, status, cpu, memory, uptime])
                else:
                    if pid not in self.previous_process_data or self.previous_process_data[pid] != current_process_data[pid]:
                        process_matrix.append([pid, icon, name, status, cpu, memory, uptime])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        for pid in list(self.previous_process_data.keys()):
            if pid not in current_process_data:
                del self.previous_process_data[pid]

        self.previous_process_data = current_process_data

        sort_index = {
            "pid": 0,
            "name": 2,
            "cpu": 4,
            "ram": 5,
            "time": 6,
        }.get(self.order_cryteria, 3)

        process_matrix.sort(key=lambda x: x[sort_index], reverse=(self.order_method == "desc"))

        return process_matrix
    
    def set_order_method(self, order_method):
        self.order_method = order_method
        
    def set_order_cryteria(self, order_cryteria):
        self.order_cryteria = order_cryteria
        
    def set_search_cryteria(self, search_cryteria):
        self.search_cryteria = search_cryteria

    def resume_process(self, pid):
        try:
            process = psutil.Process(pid)
            process.resume()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"Error al reanudar proceso {pid}: {e}")
            return False

    def suspend_process(self, pid):
        try:
            process = psutil.Process(pid)
            process.suspend()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"Error al pausar proceso {pid}: {e}")
            return False

    def terminate_process(self, pid):
        try:
            process = psutil.Process(pid)
            process.terminate()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"Error al terminar proceso {pid}: {e}")
            return False