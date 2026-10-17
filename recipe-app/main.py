import tkinter as tk
from tkinter import ttk, messagebox
import db
import dao
from ui_dict import DictionaryWindow
from ui_recipe import RecipeWindow
from ui_shopping import ShoppingWindow

def main():
    if not db.init_db():
        return

    root = tk.Tk()
    root.title("Кулинарная книга — Мои рецепты")
    root.geometry("1000x700")
    root.configure(bg="#f4f4f4")
    
    # --- Верхняя панель ---
    top_frame = tk.Frame(root, bg="#f4f4f4")
    top_frame.pack(fill=tk.X, padx=15, pady=15)

    tk.Label(top_frame, text="Моя кулинарная книга", font=("Arial", 20, "bold"), bg="#f4f4f4").pack(side=tk.LEFT)
    
    tk.Button(top_frame, text="+ Добавить рецепт", font=("Arial", 12), bg="#4CAF50", fg="white", relief=tk.FLAT,
              command=lambda: RecipeWindow(root, load_recipes)).pack(side=tk.RIGHT, padx=5)
              
    tk.Button(top_frame, text="🛒 Список покупок", font=("Arial", 12), bg="#2196F3", fg="white", relief=tk.FLAT,
              command=lambda: ShoppingWindow(root)).pack(side=tk.RIGHT, padx=5)
              
    tk.Button(top_frame, text="Справочники", font=("Arial", 12), bg="#e0e0e0", relief=tk.FLAT,
              command=lambda: DictionaryWindow(root)).pack(side=tk.RIGHT, padx=5)

    # --- Таблица рецептов ---
    tree_frame = tk.Frame(root)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

    tree = ttk.Treeview(tree_frame, columns=("ID", "Title", "Category", "Servings"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Title", text="Название рецепта")
    tree.heading("Category", text="Категория")
    tree.heading("Servings", text="Порций")
    tree.column("ID", width=50)
    tree.column("Title", width=500)
    tree.column("Category", width=200)
    tree.column("Servings", width=100, anchor="center")
    
    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def load_recipes():
        for i in tree.get_children():
            tree.delete(i)
        for row in dao.RecipeDAO.get_all():
            cat_name = row["category_name"] if row["category_name"] else "Без категории"
            tree.insert("", tk.END, values=(row["id"], row["title"], cat_name, row["default_servings"]))

    # --- Нижняя панель (кнопки действий) ---
    bottom_frame = tk.Frame(root, bg="#f4f4f4")
    bottom_frame.pack(fill=tk.X, padx=15, pady=10)

    def delete_recipe():
        selected = tree.selection()
        if not selected:
            return
        recipe_id = tree.item(selected[0])['values'][0]
        title = tree.item(selected[0])['values'][1]
        if messagebox.askyesno("Подтверждение", f"Удалить рецепт '{title}'?"):
            dao.RecipeDAO.delete(recipe_id)
            load_recipes()

    def edit_recipe():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Сначала выберите рецепт в таблице!")
            return
        recipe_id = tree.item(selected[0])['values'][0]
        # Открываем окно с переданным ID
        RecipeWindow(root, load_recipes, recipe_id=recipe_id)

    # Кнопки
    tk.Button(bottom_frame, text="✎ Редактировать рецепт", font=("Arial", 10), bg="#e0e0e0", relief=tk.FLAT, 
              command=edit_recipe).pack(side=tk.LEFT, padx=5)
              
    tk.Button(bottom_frame, text="Удалить выбранный рецепт", font=("Arial", 10), fg="red", relief=tk.FLAT, 
              bg="#f4f4f4", command=delete_recipe).pack(side=tk.LEFT, padx=5)

    load_recipes()
    root.mainloop()

if __name__ == "__main__":
    main()