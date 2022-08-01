-- Query to build ingredient base to pantry
-- All records correspond to real ingredients in the Kafoodle kitchen DB

-- DROP TABLE kp_ingredients_base_pantry;
-- TRUNCATE TABLE kp_ingredients_base_pantry;

CREATE TABLE kp_ingredients_base_pantry AS (
	SELECT T1.ingredient_id,
		T1.category_id,
		T1.ingredient_name,
		T1.date_created
	FROM
		(SELECT id AS ingredient_id,
			category_id,
			name AS ingredient_name,
			created AS date_created
		FROM ste__ingredients
		WHERE created BETWEEN '2021-01-01' AND '2022-05-31') T1
	INNER JOIN
		(SELECT DISTINCT category_id
		FROM kp_ingredient_taxonomy) T2
		ON T1.category_id = T2.category_id
);
