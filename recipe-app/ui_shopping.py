import tkinter as tk
from tkinter import ttk, messagebox
import dao

class ShoppingWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Список покупок")
        self.geometry("800x600")
        self.grab_set()

        # Данные о рецептах и выбранных порциях
        self.recipes_data = []

        # --- Левая часть: выбор рецептов ---
        frame_left = tk.Frame(self)
        frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(frame_left, text="Выберите рецепты (двойной клик для изменения порций):", font=("Arial", 10, "bold")).pack(anchor="w")

        self.tree_recipes = ttk.Treeview(frame_left, columns=("Title", "Servings"), show="headings", height=15)
        self.tree_recipes.heading("Title", text="Рецепт")
        self.tree_recipes.heading("Servings", text="Порций")
        self.tree_recipes.column("Title", width=250)
        self.tree_recipes.column("Servings", width=60, anchor="center")
        self.tree_recipes.pack(fill=tk.BOTH, expand=True, pady=5)
        self.tree_recipes.bind("<Double-1>", self.edit_servings)

        self.load_recipes()

        tk.Button(frame_left, text="Сформировать список", bg="#2196F3", fg="white", font=("Arial", 11, "bold"), 
                  command=self.generate_list).pack(fill=tk.X, pady=10)

        # --- Правая часть: итоговый список ---
        frame_right = tk.Frame(self)
        frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(frame_right, text="Итоговый список покупок:", font=("Arial", 10, "bold")).pack(anchor="w")

        self.tree_shopping = ttk.Treeview(frame_right, columns=("Name", "Amount", "Unit"), show="headings", height=15)
        self.tree_shopping.heading("Name", text="Ингредиент")
        self.tree_shopping.heading("Amount", text="Итого")
        self.tree_shopping.heading("Unit", text="Ед.")
        self.tree_shopping.column("Name", width=200)
        self.tree_shopping.column("Amount", width=80, anchor="center")
        self.tree_shopping.column("Unit", width=60, anchor="center")
        self.tree_shopping.pack(fill=tk.BOTH, expand=True, pady=5)

    def load_recipes(self):
        self.recipes_data.clear()
        for row in dao.RecipeDAO.get_all():
            # Сохраняем словарь с данными рецепта. По умолчанию ставим его стандартные порции.
            self.recipes_data.append({
                "id": row["id"], 
                "title": row["title"], 
                "servings": row["default_servings"]
            })
            self.tree_recipes.insert("", tk.END, values=(row["title"], row["default_servings"]))

    def edit_servings(self, event):
        selected = self.tree_recipes.selection()
        if not selected:
            return
        
        item_index = self.tree_recipes.index(selected[0])
        recipe = self.recipes_data[item_index]

        # Запрашиваем новое число порций
        from tkinter import simpledialog
        new_servings = simpledialog.askinteger("Порции", f"На сколько порций готовим '{recipe['title']}'?", 
                                               initialvalue=recipe['servings'], parent=self)
        
        if new_servings and new_servings > 0:
            # Обновляем данные
            self.recipes_data[item_index]['servings'] = new_servings
            # Обновляем таблицу
            self.tree_recipes.item(selected[0], values=(recipe['title'], new_servings))

    def generate_list(self):
        selected = self.tree_recipes.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выделите хотя бы один рецепт для генерации списка!", parent=self)
            return

        # Формируем список ID и порций для SQL-запроса
        recipes_to_shop = []
        for item in selected:
            index = self.tree_recipes.index(item)
            recipes_to_shop.append(self.recipes_data[index])

        try:
            # Вызываем наш сложный DAO-метод
            result = dao.RecipeIngredientDAO.generate_shopping_list(recipes_to_shop)
            
            # Очищаем старый список
            for i in self.tree_shopping.get_children():
                self.tree_shopping.delete(i)

            # Заполняем новыми данными
            for row in result:
                # Округляем до 2 знаков, чтобы не было 0.300000000004
                amount = round(row["total_amount"], 2)
                self.tree_shopping.insert("", tk.END, values=(row["name"], amount, row["unit"]))

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сформировать список:\n{e}", parent=self)