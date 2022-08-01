-- Query to create an empty table for stopwords

-- DROP TABLE pantry__stopwords;
-- TRUNCATE TABLE pantry__stopwords;

CREATE TABLE pantry__stopwords (
  id INT NOT NULL AUTO_INCREMENT,
  stopword VARCHAR(255) NOT NULL,
  PRIMARY KEY(id),
  UNIQUE(stopword)
);
