-- Query to extract ingredients given a date range.
-- It depends on the taxonomy table to exclude the categories not present in the current taxonomy.

SELECT ingredient_id,
	ingredient_name
FROM
	(SELECT id AS ingredient_id,
		name AS ingredient_name,
		category_id
	FROM ste__ingredients
	WHERE created BETWEEN '2021-01-01' AND '2022-05-31') T1
INNER JOIN
	(SELECT DISTINCT category_id
	FROM pantry__taxonomy) T2
ON T1.category_id = T2.category_id
;
