-- Query to create manually the category table used in the pantry
-- This table is based on production table ste__ingredient_categories,
-- however the names have been modified to optimise functionallity in scripts

--DROP TABLE kp_ingredient_categories;
--TRUNCATE TABLE kp_ingredient_categories;

CREATE TABLE kp_ingredient_categories (
  id INT NOT NULL,
  name VARCHAR(128) NOT NULL,
  PRIMARY KEY(id),
  UNIQUE(name)
);

--Fill values manually
INSERT INTO kp_ingredient_categories (id, name)
VALUES
  (101, 'fish-seafood'),
	(102, 'meat-poultry'),
	(103, 'vegetables'),
	(105, 'nuts-seeds'),
	(107, 'dairy-eggs'),
	(108, 'fruits'),
	(109, 'grains-rice-pasta-noodles'),
	(110, 'oils-vinegars'),
	(113, 'fungi'),
	(144, 'deli'),
	(148, 'herbs-spices');
