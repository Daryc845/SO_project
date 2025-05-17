from threading import Thread
import time
from model.Modelo import Modelo
from view.TaskManager import TaskManagerApp

class Controlador:
    def __init__(self):
        self.modelo = Modelo()
        self.vista = TaskManagerApp()
        
        # Iniciar el hilo de actualización
        self.start_update_thread()
        
    def start_update_thread(self):
        def update_and_refresh():
            while True:
                data = self.modelo.get_processes()
                self.vista.after(0, lambda d=data: self.vista.insert_values(d))
                time.sleep(1)

        thread = Thread(target=update_and_refresh, daemon=True)
        thread.start()
        
    def run(self):
        self.vista.mainloop()

if __name__ == "__main__":
    controlador = Controlador()
    controlador.run()