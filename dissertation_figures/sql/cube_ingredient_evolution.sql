-- Query to extract all ingredient groups

SELECT EXTRACT(YEAR_MONTH FROM created_date) AS yearmonth,
    category_id,
    T2.name AS category,
    count(*) AS ingredient_count
FROM
	(SELECT created AS created_date,
		category_id
	FROM ste__ingredients
	WHERE created BETWEEN '2021-01-01' AND '2022-05-31') T1
LEFT JOIN
	ste__ingredient_categories T2
ON T1.category_id = T2.id
GROUP BY yearmonth,
    category_id,
    category;
