import tkinter as tk
from tkinter import ttk, Menu
from PIL import Image, ImageTk

class TaskManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Task Manager")
        self.geometry("950x540")
        self.configure(bg="#f7f9fa")
        self.create_widgets()

    def create_widgets(self):
        # Cabecera
        header = tk.Frame(self, bg="#2d3e50", height=70)
        header.pack(fill=tk.X, side=tk.TOP)

        # Botón 2 con menú desplegable (De mayor a menor, De menor a mayor)
        filterButton = SpecialButton(header, "🧹 Filtrar", 120, "#AA4AE2", "#FF00EA")
        filterButton.add_commands(("PID", "Nombre", "Tiempo de ejecución", "CPU", "RAM"))
        filterButton.pack(side=tk.RIGHT, padx=7, pady=10)
        
        orderButton = SpecialButton(header, "↕ Ordenar", 120, "#FF9900", "#E2DF4A")
        orderButton.add_commands(("Descendente", "Ascendente"))
        orderButton.pack(side=tk.RIGHT, padx=7, pady=10)
        
        # Barra de búsqueda centrada
        search_frame = tk.Frame(header, bg="#2d3e50")
        
        searchButton = SpecialButton(search_frame, "🔍", 50, "#4A90E2", "#00E1FF")
        searchButton.pack(side=tk.LEFT, padx=5)
        
        search_entry = tk.Entry(
            search_frame,
            width=38,
            font=("Segoe UI", 11),
            bg="#f7f9fa",
            fg="#222",
            relief=tk.FLAT,
            bd=2,
            highlightthickness=1,
            highlightbackground="#b0b0b0"
        )
        search_entry.pack(side=tk.LEFT, padx=5, pady=10)
        
        search_frame.place(relx=0, rely=0.5, anchor=tk.W)

        # Tabla de procesos
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e0e0e0", foreground="#222")
        style.configure("Treeview", font=("Segoe UI", 10), background="#f7f9fa", foreground="#222", rowheight=28, fieldbackground="#f7f9fa")
        style.map("Treeview", background=[("selected", "#b3d1ff")])

        columns = ("PID", "Icono", "Nombre", "Estado", "CPU", "RAM", "Tiempo de ejecución")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=140)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))

        # Ejemplo de datos
        example_data = [
            (1234, "chrome.exe", "Activo", "12%", "200MB", "00:10:23"),
            (5678, "python.exe", "Suspendido", "5%", "150MB", "00:05:12"),
            (9101, "explorer.exe", "Activo", "2%", "100MB", "00:20:45"),
        ]
        for row in example_data:
            self.tree.insert("", tk.END, values=row)

        # Menú contextual para la tabla
        self.context_menu = Menu(self, tearoff=0, bg="#f7f9fa", fg="#222", font=("Segoe UI", 10))
        self.context_menu.add_command(label="Reanudar proceso")
        self.context_menu.add_command(label="Pausar proceso")
        self.context_menu.add_command(label="Finalizar proceso")
        self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.context_menu.tk_popup(event.x_root, event.y_root)
            
class SpecialButton(tk.Menubutton):
    def __init__(self, root, text, width, primaryColor, secondaryColor):
        #.---------------------------------------
        self.gradient_photo = self.create_gradient_image(width, 36, primaryColor, secondaryColor)
        self.gradient_photo_hover = self.create_gradient_image(width, 36, "#505050", "#292929")
        super().__init__(
            root,
            text=text,
            relief=tk.FLAT,
            bg="#FFFFFF",
            fg="white",
            activebackground=secondaryColor,
            activeforeground=secondaryColor,
            font=("Segoe UI", 11, "bold"),
            bd=0,
            cursor="hand2",
            image=self.gradient_photo,
            compound="center",
            padx=2, 
            pady=2 
        )
        def on_enter(event):
            self.config(image=self.gradient_photo_hover)

        def on_leave(event):
            self.config(image=self.gradient_photo)

        self.bind("<Enter>", on_enter)
        self.bind("<Leave>", on_leave)
        
        self.menu = Menu(self, relief=tk.FLAT, tearoff=0, bg="#f7f9fa", fg="#222", font=("Segoe UI", 10))
        self["menu"] = self.menu
        
    def add_commands(self, commands):
        for command in commands:
            self.menu.add_command(label=command)
        
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