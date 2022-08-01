-- Query to extract all ingredient groups

SELECT T1.id AS ingredient_id,
    ingredient_name,
    T2.name AS category,
    CAST(energy_quantity AS DECIMAL(19, 2)) AS energy_quantity,
    CAST(protein_quantity AS DECIMAL(19, 2)) AS protein_quantity
-- SELECT COUNT(*)
FROM
	(SELECT name AS ingredient_name,
		category_id,
		id
	FROM ste__ingredients
	WHERE created BETWEEN '2021-01-01' AND '2022-04-30'
    	AND category_id IN (101, 102, 103, 107, 108, 110)) T1
LEFT JOIN
	ste__ingredient_categories T2
ON T1.category_id = T2.id
LEFT JOIN
    (SELECT id,
        nutrition_id
    FROM ste__edibles) T3
ON T1.id = T3.id
LEFT JOIN
    (SELECT id,
        energy_id,
        protein_id
    FROM ste__nutrition) T4
ON T3.nutrition_id = T4.id
LEFT JOIN
    (SELECT id,
        quantity AS energy_quantity,
        unit AS energy_unit
    FROM ste__nutrition_values) T5
ON T4.energy_id = T5.id
LEFT JOIN
    (SELECT id,
        quantity AS protein_quantity,
        unit AS protein_unit
    FROM ste__nutrition_values) T6
ON T4.protein_id = T6.id
WHERE energy_unit = 'kcal'
    AND protein_unit = 'g';
