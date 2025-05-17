from threading import Thread
import time
from model.Model import Model
from view.TaskManager import TaskManagerApp

class Controller:
    def __init__(self):
        self.model = Model()
        self.view = TaskManagerApp(self.set_order_method, self.set_order_cryteria, self.set_search_cryteria)
        
        # Iniciar el hilo de actualización
        self.start_update_thread()
        
    def start_update_thread(self):
        def update_and_refresh():
            while True:
                data = self.model.get_processes()
                self.view.after(0, lambda d=data: self.view.insert_values(d))
                time.sleep(1)

        thread = Thread(target=update_and_refresh, daemon=True)
        thread.start()
        
    def run(self):
        self.view.mainloop()
        
    def set_order_method(self, order_method):
        self.model.set_order_method(order_method)
        self.update_view_once()
        
    def set_order_cryteria(self, order_cryteria):
        self.model.set_order_cryteria(order_cryteria)
        self.update_view_once()
        
    def set_search_cryteria(self, search_cryteria):
        self.model.set_search_cryteria(search_cryteria)
    
    
        
    def update_view_once(self):
        data = self.model.get_processes()
        self.view.after(0, lambda d=data: self.view.insert_values(d))