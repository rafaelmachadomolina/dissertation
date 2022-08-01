-- Query to create an empty table for the vectorised taxonomy

-- DROP TABLE pantry__taxonomy_vector;
-- TRUNCATE TABLE pantry__taxonomy_vector;

CREATE TABLE pantry__taxonomy_vector (
  id INT NOT NULL AUTO_INCREMENT,
  taxonomy_id INT NOT NULL,
  ingredient_name VARCHAR(255) NOT NULL,
  vector_representation TEXT,
  PRIMARY KEY(id)
);
