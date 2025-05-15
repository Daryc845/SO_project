import psutil

class AdministradorDeTareas:
    def __init__(self):
        print("Inicializando Administrador de Tareas...\n")

    def mostrar_procesos(self):
        print(f"{'PID':<10} {'Nombre':<25} {'CPU (%)':<10} {'RAM (%)':<10}")
        print("-" * 60)
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pid = proc.info['pid']
                nombre = proc.info['name']
                cpu = proc.info['cpu_percent']
                ram = proc.info['memory_percent']
                print(f"{pid:<10} {nombre:<25} {cpu:<10} {ram:<10.2f}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

# Uso
if __name__ == "__main__":
    administrador = AdministradorDeTareas()
    administrador.mostrar_procesos()
