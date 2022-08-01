-- Query to create an empty table for the taxonomy

-- DROP TABLE pantry__taxonomy;
-- TRUNCATE TABLE pantry__taxonomy;

CREATE TABLE pantry__taxonomy (
  id INT NOT NULL AUTO_INCREMENT,
  ingredient_name VARCHAR(255) NOT NULL,
  category_id INT NOT NULL,
  taxonomy VARCHAR(1023),
  PRIMARY KEY(id),
  UNIQUE(ingredient_name)
);
