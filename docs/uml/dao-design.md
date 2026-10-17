# Проектирование DAO-слоя и SQL-запросы

## 1. DAO-классы (CRUD-операции)

### 1.1. CategoryDAO (таблица categories)
| Метод | Входные параметры | Возвращаемое значение | SQL-запрос |
|-------|-------------------|------------------------|------------|
| getAll() | — | Список категорий | `SELECT id, name FROM categories ORDER BY name;` |
| getById(id) | id: целое | Категория | `SELECT id, name FROM categories WHERE id = ?;` |
| insert(entity) | Категория | id (целое) | `INSERT INTO categories (name) VALUES (?);` |
| update(entity) | Категория | bool | `UPDATE categories SET name = ? WHERE id = ?;` |
| delete(id) | id: целое | bool | `DELETE FROM categories WHERE id = ?;` |

### 1.2. RecipeDAO (таблица recipes)
| Метод | Входные параметры | Возвращаемое значение | SQL-запрос |
|-------|-------------------|------------------------|------------|
| getAll() | — | Список рецептов | `SELECT id, title, description, category_id, default_servings, created_at FROM recipes ORDER BY title;` |
| getById(id) | id: целое | Рецепт | `SELECT id, title, description, category_id, default_servings, created_at FROM recipes WHERE id = ?;` |
| insert(entity) | Рецепт | id (целое) | `INSERT INTO recipes (title, description, category_id, default_servings) VALUES (?, ?, ?, ?);` |
| update(entity) | Рецепт | bool | `UPDATE recipes SET title=?, description=?, category_id=?, default_servings=? WHERE id=?;` |
| delete(id) | id: целое | bool | `DELETE FROM recipes WHERE id = ?;` |

### 1.3. IngredientDAO (таблица ingredients)
| Метод | Входные параметры | Возвращаемое значение | SQL-запрос |
|-------|-------------------|------------------------|------------|
| getAll() | — | Список ингредиентов | `SELECT id, name, unit FROM ingredients ORDER BY name;` |
| getById(id) | id: целое | Ингредиент | `SELECT id, name, unit FROM ingredients WHERE id = ?;` |
| insert(entity) | Ингредиент | id (целое) | `INSERT INTO ingredients (name, unit) VALUES (?, ?);` |
| update(entity) | Ингредиент | bool | `UPDATE ingredients SET name=?, unit=? WHERE id=?;` |
| delete(id) | id: целое | bool | `DELETE FROM ingredients WHERE id = ?;` |

### 1.4. RecipeIngredientDAO (таблица recipe_ingredients)
| Метод | Входные параметры | Возвращаемое значение | SQL-запрос |
|-------|-------------------|------------------------|------------|
| getByRecipeId(recipe_id) | recipe_id: целое | Список состава рецепта | `SELECT ri.recipe_id, ri.ingredient_id, ri.amount, i.name, i.unit FROM recipe_ingredients ri JOIN ingredients i ON i.id = ri.ingredient_id WHERE ri.recipe_id = ?;` |
| insert(entity) | Состав рецепта | bool | `INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount) VALUES (?, ?, ?);` |
| update(entity) | Состав рецепта | bool | `UPDATE recipe_ingredients SET amount = ? WHERE recipe_id = ? AND ingredient_id = ?;` |
| delete(recipe_id, ingredient_id) | recipe_id, ingredient_id | bool | `DELETE FROM recipe_ingredients WHERE recipe_id = ? AND ingredient_id = ?;` |
| deleteByRecipeId(recipe_id) | recipe_id: целое | bool | `DELETE FROM recipe_ingredients WHERE recipe_id = ?;` |

---

## 2. Бизнес-операции (сложные SQL-запросы)

### 2.1. Поиск и фильтрация рецептов
**Описание:** Возвращает рецепты, отфильтрованные по названию и категории.
**Параметры:** `search_text` (строка), `category_id` (целое).
**SQL-запрос:**
```sql
SELECT id, title, description, category_id, default_servings, created_at
FROM recipes
WHERE (title LIKE '%' || ? || '%' OR ? = '')
  AND (category_id = ? OR ? IS NULL)
ORDER BY title;
