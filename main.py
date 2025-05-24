from controller.Controller import Controller

"""
Aplicación de Administrador de Tareas
-----------------------------------
Esta aplicación permite visualizar y gestionar los procesos en ejecución del sistema.
Implementa un patrón MVC (Modelo-Vista-Controlador) para separar la lógica de negocio
de la interfaz de usuario.

Características principales:
- Listar procesos en tiempo real
- Mostrar información detallada de cada proceso (CPU, RAM, tiempo de ejecución)
- Ordenar procesos por diferentes criterios
- Buscar procesos por nombre o PID
- Gestionar procesos (pausar, reanudar, terminar)
- Mostrar íconos de los procesos
"""

def main():
    """
    Función principal que inicia la aplicación del Administrador de Tareas.
    Crea una instancia del controlador y comienza la ejecución del bucle principal.
    
    La aplicación se ejecutará hasta que el usuario la cierre manualmente.
    """
    try:
        # Crear y ejecutar la aplicación
        app = Controller()
        app.run()
    except Exception as e:
        print(f"Error iniciando la aplicación: {e}")
        
if __name__ == "__main__":
    main()
