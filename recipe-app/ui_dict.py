import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import dao

class DictionaryWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Справочники")
        self.geometry("700x500")
        self.grab_set() # Блокирует главное окно, пока открыто это

        # Создаем вкладки (Категории и Ингредиенты)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_categories = ttk.Frame(self.notebook)
        self.tab_ingredients = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_categories, text="Категории")
        self.notebook.add(self.tab_ingredients, text="Ингредиенты")

        self.setup_categories_tab()
        self.setup_ingredients_tab()

    # ================= ВКЛАДКА КАТЕГОРИЙ =================
    def setup_categories_tab(self):
        # Таблица
        self.tree_cat = ttk.Treeview(self.tab_categories, columns=("ID", "Name"), show="headings")
        self.tree_cat.heading("ID", text="ID")
        self.tree_cat.heading("Name", text="Название категории")
        self.tree_cat.column("ID", width=50)
        self.tree_cat.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Кнопки
        btn_frame = tk.Frame(self.tab_categories)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(btn_frame, text="Добавить", command=self.add_category).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_category).pack(side=tk.LEFT, padx=5)

        self.load_categories()

    def load_categories(self):
        # Очищаем таблицу
        for i in self.tree_cat.get_children():
            self.tree_cat.delete(i)
        # Загружаем из БД
        for row in dao.CategoryDAO.get_all():
            self.tree_cat.insert("", tk.END, values=(row["id"], row["name"]))

    def add_category(self):
        name = simpledialog.askstring("Новая категория", "Введите название категории:", parent=self)
        if name:
            try:
                dao.CategoryDAO.insert(name)
                self.load_categories()
            except Exception as e:
                messagebox.showerror("Ошибка", "Такая категория уже существует!", parent=self)

    def delete_category(self):
        selected = self.tree_cat.selection()
        if not selected:
            return
        cat_id = self.tree_cat.item(selected[0])['values'][0]
        if messagebox.askyesno("Подтверждение", "Удалить категорию? У рецептов она станет пустой (NULL).", parent=self):
            dao.CategoryDAO.delete(cat_id)
            self.load_categories()

    # ================= ВКЛАДКА ИНГРЕДИЕНТОВ =================
    def setup_ingredients_tab(self):
        self.tree_ing = ttk.Treeview(self.tab_ingredients, columns=("ID", "Name", "Unit"), show="headings")
        self.tree_ing.heading("ID", text="ID")
        self.tree_ing.heading("Name", text="Название")
        self.tree_ing.heading("Unit", text="Ед. изм.")
        self.tree_ing.column("ID", width=50)
        self.tree_ing.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        btn_frame = tk.Frame(self.tab_ingredients)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(btn_frame, text="Добавить", command=self.add_ingredient).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_ingredient).pack(side=tk.LEFT, padx=5)

        self.load_ingredients()

    def load_ingredients(self):
        for i in self.tree_ing.get_children():
            self.tree_ing.delete(i)
        for row in dao.IngredientDAO.get_all():
            self.tree_ing.insert("", tk.END, values=(row["id"], row["name"], row["unit"]))

    def add_ingredient(self):
        name = simpledialog.askstring("Новый ингредиент", "Введите название (например, Сахар):", parent=self)
        if not name: return
        unit = simpledialog.askstring("Новый ингредиент", "Введите единицу измерения (г, мл, шт):", parent=self)
        if not unit: return
        
        try:
            dao.IngredientDAO.insert(name, unit)
            self.load_ingredients()
        except Exception as e:
            messagebox.showerror("Ошибка", "Такой ингредиент уже существует!", parent=self)

    def delete_ingredient(self):
        selected = self.tree_ing.selection()
        if not selected:
            return
        ing_id = self.tree_ing.item(selected[0])['values'][0]
        if messagebox.askyesno("Подтверждение", "Удалить ингредиент?", parent=self):
            try:
                dao.IngredientDAO.delete(ing_id)
                self.load_ingredients()
            except Exception as e:
                # Здесь сработает наш ON DELETE RESTRICT из базы
                messagebox.showerror("Ошибка удаления", str(e), parent=self)