-- Query to consult the size of the ingredients table in the database.

SELECT COUNT(*) AS ingredients,
    COUNT(DISTINCT business_id) AS clients,
    COUNT(DISTINCT created_by) AS users,
    COUNT(DISTINCT category_id) AS categories,
    COUNT(DISTINCT supplier_id) AS suppliers,
    MIN(created) AS min_date,
    MAX(created) AS max_date
FROM `ste__ingredients`
WHERE created BETWEEN '2021-01-01' AND '2022-05-31';
