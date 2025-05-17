import tkinter as tk
from tkinter import ttk, Menu
from PIL import Image, ImageTk

class TaskManagerApp(tk.Tk):
    def __init__(self, set_order_method, set_order_cryteria, set_search_cryteria):
        super().__init__()
        self.title("Task Manager")
        self.geometry("950x540")
        self.configure(bg="#f7f9fa")
        self.set_order_method = set_order_method
        self.set_order_cryteria = set_order_cryteria
        self.set_search_cryteria = set_search_cryteria
        self.icon_images = {}  # Para almacenar los íconos
        self.create_widgets()

    def create_widgets(self):
        # Cabecera
        header = tk.Frame(self, bg="#2d3e50", height=70)
        header.pack(fill=tk.X, side=tk.TOP)

        #Botones de cabecera
        self.add_buttons(header)
        
        # Barra de búsqueda centrada
        self.set_search_section(header)
        
        # Tabla de procesos
        self.set_process_table_style()

        # Menú contextual para la tabla
        self.set_process_table_structure()
        
    def set_process_table_structure(self):
        self.context_menu = Menu(self, tearoff=0, bg="#f7f9fa", fg="#222", font=("Segoe UI", 10))
        self.context_menu.add_command(label="Reanudar proceso")
        self.context_menu.add_command(label="Pausar proceso")
        self.context_menu.add_command(label="Finalizar proceso")
        self.tree.bind("<Button-3>", self.show_context_menu)
        
    def set_process_table_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e0e0e0", foreground="#222")
        style.configure("Treeview", font=("Segoe UI", 10), background="#f7f9fa", foreground="#222", rowheight=28, fieldbackground="#f7f9fa")
        style.map("Treeview", background=[("selected", "#b3d1ff")])

        columns = ("PID", "Icono", "Nombre", "Estado", "%CPU", "%RAM", "Tiempo de ejecución")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=140)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))
    
    def set_search_section(self, header):
        search_frame = tk.Frame(header, bg="#2d3e50")
        searchButton = SpecialButton(search_frame, "🔍", 50, "#4A90E2", "#00E1FF", self.set_search_cryteria)
        
        searchButton.pack(side=tk.LEFT, padx=5)
        search_entry_frame = tk.Frame(search_frame, bg="#242424")
        search_entry_frame.pack(side=tk.LEFT, padx=10, pady=20)
        search_entry = tk.Entry(
            search_entry_frame,
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
        searchButton.bind("<Button-1>", lambda event: self.set_search_cryteria(search_entry.get()))
        
        self.add_placeholder(search_entry)
        
        search_entry.pack()
        search_frame.place(relx=0, rely=0.5, anchor=tk.W)
        
    def add_placeholder(self, search_entry):
        search_entry.insert(0, "Digite el PID o nombre del proceso...")  # Placeholder inicial

        def on_entry_focus_in(event):
            if search_entry.get() == "Digite el PID o nombre del proceso...":
                search_entry.delete(0, tk.END)
                search_entry.config(fg="#ffffff")

        def on_entry_focus_out(event):
            if not search_entry.get():
                search_entry.insert(0, "Digite el PID o nombre del proceso...")
                search_entry.config(fg="#ffffff")

        search_entry.bind("<FocusIn>", on_entry_focus_in)
        search_entry.bind("<FocusOut>", on_entry_focus_out)
    
    def add_buttons(self, header):
        filterButton = SpecialButton(header, "🧹 Filtrar", 120, "#AA4AE2", "#FF00EA", self.set_order_cryteria)
        filterButton.add_commands({"Por PID":"pid", "Por Nombre":"name", "Por %CPU":"cpu", "Por Tiempo de ejecución":"time", "Por %RAM":"ram"})
        filterButton.pack(side=tk.RIGHT, padx=7, pady=10)
        
        orderButton = SpecialButton(header, "↕ Ordenar", 120, "#FF9900", "#E2DF4A", self.set_order_method)
        orderButton.add_commands({"Descendente":"desc", "Ascendente":"asc"})
        orderButton.pack(side=tk.RIGHT, padx=7, pady=10)
    
    def insert_values(self, matrix):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for row in matrix:
            pid, icon, name, status, cpu, memory, uptime = row
            # Convertir la imagen PIL a PhotoImage
            if isinstance(icon, Image.Image):
                photo = ImageTk.PhotoImage(icon)
                self.icon_images[pid] = photo
                self.tree.insert("", tk.END, values=(pid, "", name, status, cpu, memory, uptime), image=photo)
            else:
                self.tree.insert("", tk.END, values=row)

    def show_context_menu(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.context_menu.tk_popup(event.x_root, event.y_root)
            
class SpecialButton(tk.Menubutton):
    def __init__(self, root, text, width, primary_color, secondary_color, method_action):
        self.gradient_photo = self.create_gradient_image(width, 36, primary_color, secondary_color)
        self.gradient_photo_hover = self.create_gradient_image(width, 36, "#505050", "#292929")
        self.method_action = method_action
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
        self.set_events()
        
        self.menu = Menu(self, relief=tk.FLAT, tearoff=0, bg="#111111", fg="#ffffff", font=("Segoe UI", 10))
        self["menu"] = self.menu
        
    def set_events(self):
        def on_enter(event):
            self.config(image=self.gradient_photo_hover)

        def on_leave(event):
            self.config(image=self.gradient_photo)

        self.bind("<Enter>", on_enter)
        self.bind("<Leave>", on_leave)
        
    def add_commands(self, commands):
        bold_font = ("Segoe UI", 10, "bold")  # Fuente en negrita
        for label, value in commands.items():
            self.menu.add_command(
                label=label,
                background="#111111",
                foreground="#ffffff",
                activebackground="#333333",
                activeforeground=self.secondary_color,
                font=bold_font, 
                command=lambda v=value: self.method_action(v)
            )
        
    def create_gradient_image(self, width, height, color1, color2):
        base = Image.new('RGB', (width, height), color1)
        top = Image.new('RGB', (width, height), color2)
        mask = Image.new('L', (width, height))
        for x in range(width):
            for y in range(height):
                mask.putpixel((x, y), int(255 * (x / width)))
        base.paste(top, (0, 0), mask)
        return ImageTk.PhotoImage(base)


if __name__ == "__main__":
    app = TaskManagerApp()
    app.mainloop()