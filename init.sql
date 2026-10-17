PRAGMA foreign_keys = ON;

-- Категории рецептов
CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Рецепты
CREATE TABLE IF NOT EXISTS recipes (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    title            TEXT NOT NULL,
    description      TEXT,
    category_id      INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    default_servings INTEGER NOT NULL CHECK (default_servings > 0),
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Справочник ингредиентов
CREATE TABLE IF NOT EXISTS ingredients (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    unit TEXT NOT NULL
);

-- Состав рецепта (связь M:N)
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_id     INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE RESTRICT,
    amount        REAL NOT NULL CHECK (amount > 0),
    PRIMARY KEY (recipe_id, ingredient_id)
);

-- Индексы для ускорения поиска и связей
CREATE INDEX IF NOT EXISTS idx_recipes_title    ON recipes(title);
CREATE INDEX IF NOT EXISTS idx_recipes_category ON recipes(category_id);
CREATE INDEX IF NOT EXISTS idx_ri_recipe        ON recipe_ingredients(recipe_id);
CREATE INDEX IF NOT EXISTS idx_ri_ingredient    ON recipe_ingredients(ingredient_id);
CREATE INDEX IF NOT EXISTS idx_ingredients_name ON ingredients(name);
