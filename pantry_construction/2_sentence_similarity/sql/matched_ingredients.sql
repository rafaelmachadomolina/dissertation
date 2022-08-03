-- Query to build table with matched taxonomy ingredients

-- DROP TABLE kp_ingredients_matched;
-- TRUNCATE TABLE kp_ingredients_matched;

CREATE TABLE kp_ingredients_matched (
  id INT NOT NULL AUTO_INCREMENT,
  ingredient_id INT NOT NULL,
  original_ingredient_name VARCHAR(255) NOT NULL,
  adapted_ingredient VARCHAR(255) NOT NULL,
  matched_ingredient VARCHAR(255) NOT NULL,
  matched_score DECIMAL(19, 6) NOT NULL,
  ingredient_category_id INT NOT NULL,
  taxonomy_ingredient_id INT NOT NULL,
  taxonomy_category_id INT NOT NULL,
  PRIMARY KEY(id),
  UNIQUE(ingredient_id)
);
