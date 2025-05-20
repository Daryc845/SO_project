from threading import Thread
import time
from model.Model import Model
from view.TaskManager import TaskManagerApp

class Controller:
    """
    Controlador principal de la aplicación.
    Coordina la comunicación entre el modelo y la vista, y maneja los eventos de la interfaz.
    """

    def __init__(self):
        """
        Inicializa el controlador creando instancias del modelo y la vista,
        y configura los callbacks para la comunicación entre ellos.
        """
        self.model = Model()
        self.view = TaskManagerApp(
            self.set_order_method,
            self.set_order_cryteria,
            self.set_search_cryteria,
            self.resume_process,
            self.suspend_process,
            self.terminate_process
        )
        self.start_update_thread()
        
    def start_update_thread(self):
        """
        Inicia un hilo secundario para actualizar periódicamente la lista de procesos en la vista.
        El hilo se ejecuta en modo daemon para terminar cuando se cierre la aplicación.
        """
        def update_and_refresh():
            while True:
                data = self.model.get_processes()
                self.view.after(0, lambda d=data: self.view.insert_values(d))
                time.sleep(1)

        thread = Thread(target=update_and_refresh, daemon=True)
        thread.start()
        
    def run(self):
        """
        Inicia la ejecución de la aplicación mostrando la ventana principal.
        """
        self.view.mainloop()
        
    def set_order_method(self, order_method):
        """
        Callback para cambiar el método de ordenamiento de los procesos.
        
        Args:
            order_method (str): Método de ordenamiento a aplicar
        """
        self.model.set_order_method(order_method)
        
    def set_order_cryteria(self, order_cryteria):
        """
        Callback para cambiar el criterio de ordenamiento de los procesos.
        
        Args:
            order_cryteria (str): Criterio de ordenamiento a aplicar
        """
        self.model.set_order_cryteria(order_cryteria)
        
    def set_search_cryteria(self, search_cryteria):
        """
        Callback para aplicar un filtro de búsqueda a los procesos.
        
        Args:
            search_cryteria (str): Texto para filtrar procesos
        """
        self.model.set_search_cryteria(search_cryteria)
        
    def update_view_once(self):
        """
        Actualiza la vista una única vez con los datos más recientes del modelo.
        Se usa después de operaciones que modifican los procesos.
        """
        data = self.model.get_processes()
        self.view.after(0, lambda d=data: self.view.insert_values(d))
        
    def resume_process(self, pid):
        """
        Callback para reanudar un proceso pausado.
        
        Args:
            pid (int): ID del proceso a reanudar
        """
        success = self.model.resume_process(pid)
        if success:
            self.update_view_once()

    def suspend_process(self, pid):
        """
        Callback para pausar un proceso en ejecución.
        
        Args:
            pid (int): ID del proceso a pausar
        """
        success = self.model.suspend_process(pid)
        if success:
            self.update_view_once()

    def terminate_process(self, pid):
        """
        Callback para terminar un proceso.
        
        Args:
            pid (int): ID del proceso a terminar
        """
        success = self.model.terminate_process(pid)
        if success:
            self.update_view_once()