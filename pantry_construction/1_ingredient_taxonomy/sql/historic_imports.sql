-- Query to extract all ingredients imported between Jan 2021 and mid May 2022 by category

SELECT created_date,
	category_id,
	T2.name AS category,
	ingredient_name
FROM
	(SELECT id,
		name AS ingredient_name,
		created AS created_date,
		category_id
	FROM ste__ingredients
	WHERE created BETWEEN '2021-01-01' AND '2022-05-15') T1
LEFT JOIN
	ste__ingredient_categories T2
ON T1.category_id = T2.id;
