-- Query to build taxonomy table in db

-- DROP TABLE kp_ingredient_taxonomy;
-- TRUNCATE TABLE kp_ingredient_taxonomy;

CREATE TABLE kp_ingredient_taxonomy (
  id INT NOT NULL AUTO_INCREMENT,
  ingredient_name VARCHAR(255) NOT NULL,
  category_id INT NOT NULL,
  category_name VARCHAR(255),
  taxonomy VARCHAR(1023),
  PRIMARY KEY(id),
  UNIQUE(ingredient_name)
);
