import tkinter as tk
from tkinter import ttk, messagebox
import dao

class RecipeWindow(tk.Toplevel):
    # Добавили параметр recipe_id (по умолчанию None)
    def __init__(self, parent, on_save_callback, recipe_id=None):
        super().__init__(parent)
        self.recipe_id = recipe_id # Если None - создаем, если число - редактируем
        self.on_save_callback = on_save_callback
        
        if self.recipe_id:
            self.title("Редактирование рецепта")
        else:
            self.title("Добавление рецепта")
            
        self.geometry("600x650")
        self.grab_set()
        
        self.current_ingredients = [] # Список кортежей (ing_id, amount)

        # --- 1. Основная информация ---
        frame_top = tk.LabelFrame(self, text="Основная информация", padx=10, pady=10)
        frame_top.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(frame_top, text="Название:").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_title = tk.Entry(frame_top, width=40)
        self.entry_title.grid(row=0, column=1, pady=2, sticky="w")

        tk.Label(frame_top, text="Категория:").grid(row=1, column=0, sticky="w", pady=2)
        self.combo_category = ttk.Combobox(frame_top, state="readonly", width=37)
        self.combo_category.grid(row=1, column=1, pady=2, sticky="w")
        self.load_categories()

        tk.Label(frame_top, text="Порций по умолч.:").grid(row=2, column=0, sticky="w", pady=2)
        self.entry_servings = tk.Entry(frame_top, width=10)
        self.entry_servings.grid(row=2, column=1, pady=2, sticky="w")

        # --- 2. Добавление ингредиентов ---
        frame_mid = tk.LabelFrame(self, text="Добавить ингредиент в состав", padx=10, pady=10)
        frame_mid.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(frame_mid, text="Ингредиент:").grid(row=0, column=0, sticky="w")
        self.combo_ingredient = ttk.Combobox(frame_mid, state="readonly", width=25)
        self.combo_ingredient.grid(row=0, column=1, padx=5)
        self.load_ingredients()

        tk.Label(frame_mid, text="Количество:").grid(row=0, column=2, sticky="w", padx=5)
        self.entry_amount = tk.Entry(frame_mid, width=10)
        self.entry_amount.grid(row=0, column=3, padx=5)

        tk.Button(frame_mid, text="Добавить", command=self.add_ingredient_to_list).grid(row=0, column=4, padx=5)

        # --- 3. Таблица состава ---
        frame_table = tk.Frame(self)
        frame_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(frame_table, columns=("Name", "Amount", "Unit"), show="headings")
        self.tree.heading("Name", text="Ингредиент")
        self.tree.heading("Amount", text="Кол-во")
        self.tree.heading("Unit", text="Ед.")
        self.tree.column("Name", width=200)
        self.tree.column("Amount", width=80)
        self.tree.column("Unit", width=80)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Button(frame_table, text="Удалить\nиз состава", command=self.remove_ingredient).pack(side=tk.RIGHT, padx=5, fill=tk.Y)

        # --- 4. Кнопка сохранения ---
        btn_text = "СОХРАНИТЬ ИЗМЕНЕНИЯ" if self.recipe_id else "СОХРАНИТЬ РЕЦЕПТ"
        tk.Button(self, text=btn_text, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), 
                  command=self.save_recipe).pack(fill=tk.X, padx=10, pady=10)

        # Если это редактирование — заполняем поля старыми данными
        if self.recipe_id:
            self.load_recipe_data()

    def load_categories(self):
        self.categories_data = dao.CategoryDAO.get_all()
        cat_names = [row["name"] for row in self.categories_data]
        self.combo_category['values'] = cat_names

    def load_ingredients(self):
        self.ingredients_data = dao.IngredientDAO.get_all()
        ing_names = [f"{row['name']} ({row['unit']})" for row in self.ingredients_data]
        self.combo_ingredient['values'] = ing_names

    def load_recipe_data(self):
        """Заполняет поля, если мы открыли окно для редактирования."""
        recipe = dao.RecipeDAO.get_by_id(self.recipe_id)
        if not recipe:
            return

        self.entry_title.insert(0, recipe["title"])
        self.entry_servings.insert(0, str(recipe["default_servings"]))

        # Выбираем категорию в выпадающем списке
        if recipe["category_id"]:
            for i, cat in enumerate(self.categories_data):
                if cat["id"] == recipe["category_id"]:
                    self.combo_category.current(i)
                    break
        elif len(self.categories_data) > 0:
            self.combo_category.current(0)

        # Загружаем состав рецепта
        ingredients = dao.RecipeIngredientDAO.get_by_recipe(self.recipe_id)
        for ing in ingredients:
            self.current_ingredients.append((ing["id"], ing["amount"]))
            self.tree.insert("", tk.END, values=(ing["name"], ing["amount"], ing["unit"]))

    def add_ingredient_to_list(self):
        if not self.combo_ingredient.get():
            return
        
        ing_index = self.combo_ingredient.current()
        ing_row = self.ingredients_data[ing_index]
        ing_id = ing_row["id"]
        
        try:
            amount = float(self.entry_amount.get().replace(',', '.'))
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите положительное число в количестве!", parent=self)
            return

        for item in self.current_ingredients:
            if item[0] == ing_id:
                messagebox.showwarning("Внимание", "Этот ингредиент уже добавлен!", parent=self)
                return

        self.current_ingredients.append((ing_id, amount))
        self.tree.insert("", tk.END, values=(ing_row["name"], amount, ing_row["unit"]))
        self.entry_amount.delete(0, tk.END)

    def remove_ingredient(self):
        selected = self.tree.selection()
        if not selected:
            return
        item_index = self.tree.index(selected[0])
        self.tree.delete(selected[0])
        del self.current_ingredients[item_index]

    def save_recipe(self):
        title = self.entry_title.get().strip()
        if not title:
            messagebox.showerror("Ошибка", "Название рецепта обязательно!", parent=self)
            return

        try:
            servings = int(self.entry_servings.get())
            if servings <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество порций должно быть целым числом > 0!", parent=self)
            return

        if not self.current_ingredients:
            messagebox.showerror("Ошибка", "Добавьте хотя бы один ингредиент в состав!", parent=self)
            return

        cat_index = self.combo_category.current()
        cat_id = None
        if cat_index != -1:
            cat_id = self.categories_data[cat_index]["id"]

        try:
            # Если есть ID — обновляем, если нет — создаем
            if self.recipe_id:
                dao.RecipeDAO.update(
                    recipe_id=self.recipe_id,
                    title=title, 
                    description="", 
                    category_id=cat_id, 
                    servings=servings, 
                    ingredients_list=self.current_ingredients
                )
                messagebox.showinfo("Успех", "Рецепт обновлён!", parent=self)
            else:
                dao.RecipeDAO.insert(
                    title=title, 
                    description="", 
                    category_id=cat_id, 
                    servings=servings, 
                    ingredients_list=self.current_ingredients
                )
                messagebox.showinfo("Успех", "Рецепт успешно сохранён!", parent=self)
                
            self.on_save_callback() # Обновляем главное окно
            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка БД", f"Не удалось сохранить рецепт:\n{e}", parent=self)