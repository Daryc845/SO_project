import tkinter as tk
from tkinter import ttk, Menu
from PIL import Image, ImageTk

class TaskManagerApp(tk.Tk):
    """
    Ventana principal de la aplicación Task Manager.
    Permite visualizar, filtrar, ordenar y gestionar procesos del sistema operativo.
    """

    def __init__(self, set_order_method, set_order_cryteria, set_search_cryteria, 
                 resume_process, suspend_process, terminate_process):
        """
        Inicializa la ventana principal y sus componentes.

        Args:
            set_order_method (callable): Callback de evento para cambiar el método de ordenamiento.
            set_order_cryteria (callable): Callback de evento para cambiar el criterio de ordenamiento.
            set_search_cryteria (callable): Callback de evento para buscar procesos.
            resume_process (callable): Callback de evento para reanudar un proceso.
            suspend_process (callable): Callback de evento para pausar un proceso.
            terminate_process (callable): Callback de evento para finalizar un proceso.
        """
        super().__init__()
        self.title("Task Manager")
        self.geometry("950x540")
        self.iconbitmap("static/icon.ico")
        self.configure(bg="#0f0f0f")
        self.set_initial_values(set_order_method, set_order_cryteria, set_search_cryteria, 
                 resume_process, suspend_process, terminate_process)
        self.create_widgets()

    def set_initial_values(self, set_order_method, set_order_cryteria, set_search_cryteria, 
                 resume_process, suspend_process, terminate_process):
        """
        Asigna los callbacks para poder ser llamados desde la clase y tambien inicializa el arreglo de iconos de procesos.

        Args:
            set_order_method (callable): Callback para cambiar el método de ordenamiento.
            set_order_cryteria (callable): Callback para cambiar el criterio de ordenamiento.
            set_search_cryteria (callable): Callback para buscar procesos.
            resume_process (callable): Callback para reanudar un proceso.
            suspend_process (callable): Callback para pausar un proceso.
            terminate_process (callable): Callback para finalizar un proceso.
        """
        self.set_order_method = set_order_method
        self.set_order_cryteria = set_order_cryteria
        self.set_search_cryteria = set_search_cryteria
        self.resume_process = resume_process
        self.suspend_process = suspend_process
        self.terminate_process = terminate_process
        self.icon_images = {}

    def create_widgets(self):
        """
        Crea y organiza los widgets(elementos) principales de la interfaz, estos son:
        la cabecera, botones de la cabecera, barra de búsqueda de la cabecera, tabla de procesos del contenido y el mensaje inicial.
        """
        # Cabecera
        header = tk.Frame(self, bg="#2d3e50", height=70)
        header.pack(fill=tk.X, side=tk.TOP)

        #Botones de cabecera
        self.add_buttons(header)
        
        # Barra de búsqueda
        self.set_search_section(header)
        
        # Tabla de procesos
        self.set_process_table_style()
        
        #Mensaje de inicio
        self.set_initial_label()
    
    def add_buttons(self, header):
        """
        Organiza y agrega el botón para filtrar y el botón para ordenar procesos en la cabecera.

        Args:
            header (tk.Frame): Contenedor donde se colocan los botones.
        """
        self.filterButton = SpecialButton(header, "🧹 Filtrar", 120, "#AA4AE2", "#FF00EA", self.set_order_cryteria, "cpu")
        self.filterButton.add_commands({"Por PID":"pid", "Por Nombre":"name", "Por %CPU":"cpu", "Por Tiempo de ejecución":"time", "Por %RAM":"ram"})
        self.filterButton.pack(side=tk.RIGHT, padx=7, pady=10)
        
        self.orderButton = SpecialButton(header, "↕ Ordenar", 120, "#FF9900", "#E2DF4A", self.set_order_method, "desc")
        self.orderButton.add_commands({"Descendente":"desc", "Ascendente":"asc"})
        self.orderButton.pack(side=tk.RIGHT, padx=7, pady=10)
    
    def set_search_section(self, header):
        """
        Organiza y crea la barra de búsqueda y la coloca en la cabecera.

        Args:
            header (tk.Frame): Contenedor donde se coloca la barra de búsqueda.
        """
        search_frame = tk.Frame(header, bg="#2d3e50")
        searchButton = SpecialButton(search_frame, "🔍", 50, "#4A90E2", "#00E1FF", self.set_search_cryteria)
        
        searchButton.pack(side=tk.LEFT, padx=5)
        self.search_entry_frame = tk.Frame(search_frame, bg="#242424")
        self.search_entry_frame.pack(side=tk.LEFT, padx=1, pady=20)
        self.search_entry = tk.Entry(
            self.search_entry_frame,
            width=38,
            font=("Segoe UI", 11),
            bg="#242424",
            fg="#d1d1d1",
            relief=tk.FLAT,
            bd=2,
            highlightthickness=2,
            highlightbackground="#00eeff",
            highlightcolor="#FFC400",
            insertbackground="#ffffff"
        )
        searchButton.bind("<Button-1>", lambda event: self.set_search_cryteria(self.search_entry.get()))
        
        self.add_placeholder(self.search_entry)
        
        self.search_entry.pack()
        search_frame.place(relx=0, rely=0.5, anchor=tk.W)
    
    def add_placeholder(self, search_entry):
        """
        Diseña y añade el efecto de placeholder al campo de búsqueda y gestiona su comportamiento al cuando el elemento esta focus o no.

        Args:
            self.search_entry (tk.Entry): Campo de entrada de búsqueda.
        """
        self.search_entry.insert(0, "Digite el PID o nombre del proceso...")  # Placeholder inicial
        self.search_entry.bind("<FocusIn>", self.on_entry_focus_in)
        self.search_entry.bind("<FocusOut>", self.on_entry_focus_out)
    
    def on_entry_focus_in(self, event):
        """
        Limpia el placeholder cuando esta en estado focus.
        """
        if self.search_entry.get() == "Digite el PID o nombre del proceso...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="#ffffff")

    def on_entry_focus_out(self, event):
        """
        Restaura el placeholder si el campo queda vacío al perder el estado focus.
        """
        if not self.search_entry.get():
            self.search_entry.insert(0, "Digite el PID o nombre del proceso...")
            self.search_entry.config(fg="#ffffff")
        
    def set_process_table_style(self):
        """
        Configura el estilo visual de la tabla de procesos (Treeview) y define la estructura de sus columnas.
        """
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#0f0f0f", foreground="#ffffff")
        style.configure("Treeview", font=("Segoe UI", 10), background="#1b1b1b", foreground="#FFFFFF", rowheight=28, fieldbackground="#1b1b1b")
        style.map("Treeview", background=[("selected", "#0e0e0e"), ("active", "#0e0e0e")])
        style.map("Treeview.Heading", background=[("active", "#333333")], foreground=[("active", "#00E1FF")])

        columns = ("PID", "Nombre", "Estado", "%CPU", "%RAM", "Tiempo de ejecución")
        self.tree = ttk.Treeview(self, columns=columns, show="tree headings", height=15)
        self.tree.heading("#0", text="Icono", anchor=tk.CENTER)
        self.tree.column("#0", width=50, anchor=tk.CENTER)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=140)
            
        # Estructura de la tabla
        self.set_process_table_structure()
    
    def set_process_table_structure(self):
        """
        Crea el menú contextual para la tabla de procesos, define la estructura de la tabla y asocia los comandos(callbacks) de gestión de procesos.
        """
        self.context_menu = Menu(self, tearoff=0, bg="#111111", fg="#ffffff", font=("Segoe UI", 10))
        self.context_menu.add_command(
            label="Reanudar proceso",
            command=self.resume_selected_process
        )
        self.context_menu.add_command(
            label="Pausar proceso",
            command=self.suspend_selected_process
        )
        self.context_menu.add_command(
            label="Finalizar proceso",
            command=self.terminate_selected_process
        )
        self.tree.bind("<Button-3>", self.show_context_menu)
    
    def set_initial_label(self):
        """
        Muestra un mensaje inicial centrado en la parte inferior de la ventana.
        """
        self.empty_label = tk.Label(self, text="Espere un momento por favor...", font=("Segoe UI", 12, "bold"), fg="#888", bg="#0f0f0f")
        self.empty_label.pack(side=tk.BOTTOM, fill=tk.Y, expand=True, pady=20)
    
    def insert_values(self, matrix):
        """
        Inserta o actualiza los valores de la tabla de procesos, los inserta cuando es la
        primera vez que se añaden valores, en el caso que la tabla tenga filas actualiza los
        valores de las filas. Si detecta que la cantidad de valores que llegan de matrix es menor
        que la cantidad de filas de la tabla entonces elimina las filas sobrantes, en 
        el caso contrario inserta nuevas filas. Basicamente, inserta valores dinamicamente.
        Si la tabla está vacía, muestra el mensaje inicial.
        Si hay filas, oculta el mensaje.

        Args:
            matrix (list): Matriz con los datos de los procesos, donde cada fila corresponde 
            a cada proceso y cada columna corresponde a los atributos de ese proceso.
        """
        current_iids = list(self.tree.get_children())
        num_current = len(current_iids)
        num_new = len(matrix)
        
        if num_new == 0:
            self.empty_label.pack(side=tk.BOTTOM, fill=tk.Y, expand=True, pady=20)
            self.tree.pack_forget()
        else:
            self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))
            self.empty_label.config(text="Ningun proceso cumple el criterio de busqueda. Pruebe cambiando el nombre o PID en la barra de busqueda...")
            self.empty_label.pack_forget()

        # Reutiliza filas existentes y actualiza sus valores
        for idx, row in enumerate(matrix):
            pid, icon, name, status, cpu, memory, uptime = row
            photo = None
            if isinstance(icon, Image.Image):
                photo = ImageTk.PhotoImage(icon)
                self.icon_images[pid] = photo

            values = (pid, name, status, cpu, memory, uptime)

            if idx < num_current:
                iid = current_iids[idx]
                self.tree.item(iid, values=values, image=photo, text="")
            else:
                # Si hay más datos nuevos que filas, inserta nuevas filas
                self.tree.insert("", tk.END, text="", values=values, image=photo)

        # Si hay más filas que datos nuevos, elimina las filas sobrantes
        for iid in current_iids[num_new:]:
            self.tree.delete(iid)     
    
    def set_selected_order_method(self, order_method):
        """
        Actualiza el método de ordenamiento seleccionado en el menu del botón de orden de procesos,
        esto con el fin que se actualice el radiobutton seleccionado.

        Args:
            order_method (str): Método de ordenamiento seleccionado.
        """
        self.orderButton.set_active_command(order_method) 
        
    def set_selected_order_cryteria(self, order_cryteria):
        """
        Actualiza el criterio de ordenamiento seleccionado en el menu del botón de filtro de procesos, 
        esto con el fin de que se actualice el radiobutton seleccionado.

        Args:
            order_cryteria (str): Criterio de ordenamiento seleccionado.
        """
        self.filterButton.set_active_command(order_cryteria)        

    def show_context_menu(self, event):
        """
        Muestra el menú contextual con las opciones de gestión de eventos al hacer clic derecho sobre una fila de la tabla.
        Es posible visualizar las 3 opciones de gestión para la fila(proceso) seleccionado, es decir: pausar, reanudar y finalizar.

        Args:
            event (tk.Event): Evento de clic derecho recibido.
        """
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.context_menu.tk_popup(event.x_root, event.y_root)
    
    def get_selected_pid(self):
        """
        Obtiene el PID del proceso seleccionado en la tabla(la fila con focus).

        Returns:
            int or None: PID del proceso seleccionado, o None si no hay selección.
        """
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            return int(item['values'][0])
        return None

    def resume_selected_process(self):
        """
        Llama al callback para reanudar el proceso seleccionado(la fila en focus).
        """
        pid = self.get_selected_pid()
        if pid:
            self.resume_process(pid)

    def suspend_selected_process(self):
        """
        Llama al callback para pausar el proceso seleccionado(la fila en focus).
        """
        pid = self.get_selected_pid()
        if pid:
            self.suspend_process(pid)

    def terminate_selected_process(self):
        """
        Llama al callback para finalizar el proceso seleccionado(la fila en focus).
        """
        pid = self.get_selected_pid()
        if pid:
            self.terminate_process(pid)
            
class SpecialButton(tk.Menubutton):
    """
    Botón especial con gradiente, efecto hover y menú desplegable.
    """

    def __init__(self, root, text, width, primary_color, secondary_color, method_action, active_command=None):
        """
        Inicializa el botón especial con gradiente y menú.

        Args:
            root (tk.Widget): Contenedor padre.
            text (str): Texto del botón.
            width (int): Ancho del botón.
            primary_color (str): Color principal del gradiente.
            secondary_color (str): Color secundario del gradiente.
            method_action (callable): Acción a ejecutar al seleccionar una opción(radiobutton).
            active_command (str, optional): Comando activo por defecto, es decir el radiobutton seleccionado por defecto en el menu.
        """
        self.gradient_photo = self.create_gradient_image(width, 36, primary_color, secondary_color)
        self.gradient_photo_hover = self.create_gradient_image(width, 36, "#505050", "#292929")
        self.method_action = method_action
        self.active_command = active_command
        super().__init__(
            root,
            text=text,
            relief=tk.FLAT,
            bg="#FFFFFF",
            fg="white",
            activebackground=secondary_color,
            activeforeground=secondary_color,
            font=("Segoe UI", 11, "bold"),
            bd=0,
            cursor="hand2",
            image=self.gradient_photo,
            compound="center",
            padx=2, 
            pady=2 
        )
        
        self.secondary_color = secondary_color;
        
        #Asigna los eventos de hover
        self.set_events()
        
        self.menu = Menu(self, relief=tk.FLAT, tearoff=0, bg="#111111", fg="#ffffff", font=("Segoe UI", 10))
        self["menu"] = self.menu
        
    def set_events(self):
        """
        Configura el evento de hover para cambiar la imagen de fondo del botón, segun salga y entre el cursor.
        """
        

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event):
        """
        Cambia la imagen de fondo al pasar el mouse sobre el botón.
        """
        self.config(image=self.gradient_photo_hover)

    def on_leave(self, event):
        """
        Restaura la imagen de fondo al quitar el mouse del botón.
        """
        self.config(image=self.gradient_photo)
    
    def set_active_command(self, active_command):
        """
        Cambia el comando activo del botón, es decir el radiobutton seleccionado.

        Args:
            active_command (str): Nuevo comando activo.
        """
        self.active_command = active_command
        
    def add_commands(self, commands):
        """
        Agrega las opciones de commands al menú desplegable del botón como radiobuttons, 
        donde cada opción tiene una clave(valor visible en la interfaz) y un valor por cada opción.

        Args:
            commands (dict): Diccionario de opciones {etiqueta: valor}.
        """
        self.order_var = tk.StringVar(value=self.active_command)
        bold_font = ("Segoe UI", 10, "bold")
        for label, value in commands.items():
            self.menu.add_radiobutton(
            label=label,
            variable=self.order_var,
            value=value,
            background="#E4E4E4",
            foreground="#000000",
            activebackground="#333333",
            activeforeground=self.secondary_color,
            font=bold_font,
            command=lambda v=value: self.method_action(v)
    )
        
    def create_gradient_image(self, width, height, color1, color2):
        """
        Crea una imagen con gradiente basada en un color principal y uno secundario para usar como fondo del botón.

        Args:
            width (int): Ancho de la imagen.
            height (int): Alto de la imagen.
            color1 (str): Color inicial del gradiente.
            color2 (str): Color final del gradiente.

        Returns:
            ImageTk.PhotoImage: Imagen generada con gradiente.
        """
        base = Image.new('RGB', (width, height), color1)
        top = Image.new('RGB', (width, height), color2)
        mask = Image.new('L', (width, height))
        for x in range(width):
            for y in range(height):
                mask.putpixel((x, y), int(255 * (x / width)))
        base.paste(top, (0, 0), mask)
        return ImageTk.PhotoImage(base)