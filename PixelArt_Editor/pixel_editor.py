import tkinter as tk
from tkinter import colorchooser, simpledialog, filedialog
from collections import deque
from PIL import Image

class PixelArtEditor:
    def __init__(self, root, rows=64, cols=64, pixel_size=10):
        self.root = root
        self.root.title("Editor de Pixel Art")

        self.rows = rows
        self.cols = cols
        self.pixel_size = pixel_size

        # Estado
        self.current_color = "#000000"
        self.tool = "pencil"   # pencil, eraser, fill, eyedropper
        self.drawing = False

        # Histórico
        self.undo_stack = deque()
        self.redo_stack = deque()

        self.create_widgets()
        self.create_grid()
        self.save_state()

        # atalhos
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())

    # =====================================================================
    def create_widgets(self):

        # --- BARRA DE FERRAMENTAS ---
        toolbar = tk.Frame(self.root)
        toolbar.pack(side=tk.TOP, anchor="w", padx=5, pady=5)

        # QUADRADO DE COR ATUAL (botão invisível, só fundo)
        self.color_button = tk.Button(
            toolbar,
            bg=self.current_color,
            width=2,
            height=1,
            command=self.choose_color
        )
        self.color_button.pack(side=tk.LEFT, padx=3)

        # BOTÕES DE FERRAMENTAS
        self.pencil_button = tk.Button(
            toolbar, text="Lápis", command=lambda: self.set_tool("pencil"))
        self.pencil_button.pack(side=tk.LEFT, padx=3)

        self.eraser_button = tk.Button(
            toolbar, text="Borracha", command=lambda: self.set_tool("eraser"))
        self.eraser_button.pack(side=tk.LEFT, padx=3)

        self.fill_button = tk.Button(
            toolbar, text="Balde", command=lambda: self.set_tool("fill"))
        self.fill_button.pack(side=tk.LEFT, padx=3)

        self.eyedrop_button = tk.Button(
            toolbar, text="Conta-gotas", command=lambda: self.set_tool("eyedropper"))
        self.eyedrop_button.pack(side=tk.LEFT, padx=3)

        # UNDO / REDO
        tk.Button(toolbar, text="<", command=self.undo).pack(side=tk.LEFT)
        tk.Button(toolbar, text=">", command=self.redo).pack(side=tk.LEFT)

        # OUTRAS FUNÇÕES
        tk.Button(toolbar, text="Limpar", command=self.clear).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Salvar PNG", command=self.save_png).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Redim. Grade", command=self.resize_grid).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Zoom +", command=lambda: self.set_zoom(1)).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Zoom -", command=lambda: self.set_zoom(-1)).pack(side=tk.LEFT)

        # ------------ CANVAS + BARRAS DE ROLAGEM ------------------
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            canvas_frame,
            width=self.cols * self.pixel_size,
            height=self.rows * self.pixel_size,
            bg="white"
        )
        self.canvas.config(scrollregion=(0, 0, self.cols * self.pixel_size, self.rows * self.pixel_size))
        self.canvas.grid(row=0, column=0, sticky="nsew")

        v_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)

        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)
        self.canvas.bind("<B1-Motion>", self.drag_draw)

        self.update_tool_buttons()

    # =====================================================================
    def create_grid(self):
        self.pixels = []
        self.canvas.delete("all")

        for r in range(self.rows):
            line = []
            for c in range(self.cols):
                x1 = c * self.pixel_size
                y1 = r * self.pixel_size
                rect = self.canvas.create_rectangle(
                    x1, y1,
                    x1 + self.pixel_size, y1 + self.pixel_size,
                    outline="#ddd", fill="white"
                )
                line.append(rect)
            self.pixels.append(line)

        # DEFINIR LIMITE DO CANVAS PRA PODER ROLAR
        self.canvas.config(
            scrollregion=(0, 0, self.cols * self.pixel_size, self.rows * self.pixel_size)
        )


    # =====================================================================
    def set_tool(self, tool):
        self.tool = tool
        self.update_tool_buttons()

    # =====================================================================
    def update_tool_buttons(self):
        # reset
        for btn in [self.pencil_button, self.eraser_button, self.fill_button, self.eyedrop_button]:
            btn.config(relief=tk.RAISED)

        if self.tool == "pencil":
            self.pencil_button.config(relief=tk.SUNKEN)
        elif self.tool == "eraser":
            self.eraser_button.config(relief=tk.SUNKEN)
        elif self.tool == "fill":
            self.fill_button.config(relief=tk.SUNKEN)
        elif self.tool == "eyedropper":
            self.eyedrop_button.config(relief=tk.SUNKEN)

    # =====================================================================
    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.current_color = color
            self.color_button.config(bg=color)

    # =====================================================================
    def color_pixel(self, r, c):
        rect = self.pixels[r][c]
        if self.tool == "pencil":
            self.canvas.itemconfig(rect, fill=self.current_color)
        elif self.tool == "eraser":
            self.canvas.itemconfig(rect, fill="white")
        elif self.tool == "eyedropper":
            self.current_color = self.canvas.itemcget(rect, "fill")
            self.color_button.config(bg=self.current_color)
            self.set_tool("pencil")

    # =====================================================================
    def flood_fill(self, r, c, target_color, new_color):
        if target_color == new_color:
            return

        stack = [(r, c)]
        while stack:
            y, x = stack.pop()
            if 0 <= y < self.rows and 0 <= x < self.cols:
                rect = self.pixels[y][x]
                color = self.canvas.itemcget(rect, "fill")
                if color == target_color:
                    self.canvas.itemconfig(rect, fill=new_color)
                    stack.extend([
                        (y-1, x), (y+1, x),
                        (y, x-1), (y, x+1)
                    ])

    # =====================================================================
    def save_state(self):
        grid = []
        for r in range(self.rows):
            line = []
            for c in range(self.cols):
                line.append(self.canvas.itemcget(self.pixels[r][c], "fill"))
            grid.append(line)
        self.undo_stack.append(grid)
        self.redo_stack.clear()

    # =====================================================================
    def undo(self):
        if len(self.undo_stack) > 1:
            self.redo_stack.append(self.undo_stack.pop())
            self.apply_state(self.undo_stack[-1])

    def redo(self):
        if self.redo_stack:
            state = self.redo_stack.pop()
            self.undo_stack.append(state)
            self.apply_state(state)

    def apply_state(self, state):
        for r in range(self.rows):
            for c in range(self.cols):
                self.canvas.itemconfig(self.pixels[r][c], fill=state[r][c])

    # =====================================================================
    def clear(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.canvas.itemconfig(self.pixels[r][c], fill="white")
        self.save_state()

    # =====================================================================
    def save_png(self):
        img = Image.new("RGB", (self.cols, self.rows), "white")
        for r in range(self.rows):
            for c in range(self.cols):
                color = self.canvas.itemcget(self.pixels[r][c], "fill")
                img.putpixel((c, r), Image.new("RGB", (1,1), color).getpixel((0,0)))
        path = filedialog.asksaveasfilename(defaultextension=".png")
        if path:
            img.save(path)

    # =====================================================================
    def resize_grid(self):
        new_size = simpledialog.askinteger("Nova grade", "Novo tamanho (ex.: 64):")
        if new_size:
            self.rows = self.cols = new_size
            self.canvas.delete("all")
            self.create_grid()
            self.save_state()

    # =====================================================================
    def set_zoom(self, direction):
        if direction == 1:
            self.pixel_size += 1
        elif direction == -1 and self.pixel_size > 1:
            self.pixel_size -= 1

        self.canvas.delete("all")
        self.create_grid()
        self.apply_state(self.undo_stack[-1])
        self.canvas.config(scrollregion=(0, 0, self.cols * self.pixel_size, self.rows * self.pixel_size))


    # =====================================================================
    def start_draw(self, event):
        self.drawing = True
        r, c = event.y // self.pixel_size, event.x // self.pixel_size
        if 0 <= r < self.rows and 0 <= c < self.cols:
            if self.tool == "fill":
                target_color = self.canvas.itemcget(self.pixels[r][c], "fill")
                self.flood_fill(r, c, target_color, self.current_color)
            else:
                self.color_pixel(r, c)

    def stop_draw(self, event):
        if self.drawing:
            self.save_state()
        self.drawing = False

    def drag_draw(self, event):
        if not self.drawing or self.tool in ("fill", "eyedropper"):
            return
        r, c = event.y // self.pixel_size, event.x // self.pixel_size
        if 0 <= r < self.rows and 0 <= c < self.cols:
            self.color_pixel(r, c)


# ================================
# EXECUÇÃO
# ================================
if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap("./icons/icone.ico")
    app = PixelArtEditor(root)
    root.mainloop()
