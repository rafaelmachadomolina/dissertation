-- Query to extract ingredient properties from matched taxonomy names.
-- It is formatted to input threshold externally. Therefore, this query should not run in a SQL interpreter.

SELECT ingredient_id,
    taxonomy_id,
    matched_score,
    nutrition_id,
    CASE
        WHEN T3.id IS NULL THEN 0
        ELSE 1
    END AS has_nutrition_data,
    energy_quantity,
    energy_unit,
    fibre_quantity,
    fibre_unit,
    protein_quantity,
    protein_unit,
    salt_quantity,
    salt_unit,
    fat_quantity,
    fat_unit,
    saturated_fat_quantity,
    saturated_fat_unit,
    carbohydrate_quantity,
    carbohydrate_unit,
    sugar_quantity,
    sugar_unit,
    GLUTEN,
    GLUTEN_WHEAT,
    GLUTEN_RYE,
    GLUTEN_BARLEY,
    GLUTEN_OATS,
    CRUSTACEANS,
    EGGS,
    FISH,
    PEANUTS,
    SOYA,
    MILK,
    NUTS,
    NUTS_ALMONDS,
    NUTS_HAZELNUTS,
    NUTS_WALNUTS,
    NUTS_CASHEWS,
    NUTS_PECANS,
    NUTS_BRAZIL,
    NUTS_PISTACHIOS,
    NUTS_MACADAMIA,
    SESAME_SEEDS,
    SULPHUR_DIOXIDE,
    MOLLUSCS,
    CELERY,
    MUSTARD,
    LUPIN
-- SELECT *
FROM
    (SELECT ingredient_id,
        taxonomy_id,
        matched_score
    FROM pantry__ingredients_scored
    WHERE matched_score >= ?) T1
LEFT JOIN
    (SELECT id,
        nutrition_id,
        (IF(((allergen_bytes_sequence & 1) = 1) = 1, 1, 0)) AS GLUTEN,
        (IF(((allergen_bytes_sequence & 65536) = 65536) = 1, 1, 0)) AS GLUTEN_WHEAT,
        (IF(((allergen_bytes_sequence & 131072) = 131072) = 1, 1, 0)) AS GLUTEN_RYE,
        (IF(((allergen_bytes_sequence & 262144) = 262144) = 1, 1, 0)) AS GLUTEN_BARLEY,
        (IF(((allergen_bytes_sequence & 524288) = 524288) = 1, 1, 0)) AS GLUTEN_OATS,
        (IF(((allergen_bytes_sequence & 2) = 2) = 1, 1, 0)) AS CRUSTACEANS,
        (IF(((allergen_bytes_sequence & 4) = 4) = 1, 1, 0)) AS EGGS,
        (IF(((allergen_bytes_sequence & 8) = 8) = 1, 1, 0)) AS FISH,
        (IF(((allergen_bytes_sequence & 16) = 16) = 1, 1, 0)) AS PEANUTS,
        (IF(((allergen_bytes_sequence & 32) = 32) = 1, 1, 0)) AS SOYA,
        (IF(((allergen_bytes_sequence & 64) = 64) = 1, 1, 0)) AS MILK,
        (IF(((allergen_bytes_sequence & 128) = 128) = 1, 1, 0)) AS NUTS,
        (IF(((allergen_bytes_sequence & 1048576) = 1048576) = 1, 1, 0)) AS NUTS_ALMONDS,
        (IF(((allergen_bytes_sequence & 2097152) = 2097152) = 1, 1, 0)) AS NUTS_HAZELNUTS,
        (IF(((allergen_bytes_sequence & 4194304) = 4194304) = 1, 1, 0)) AS NUTS_WALNUTS,
        (IF(((allergen_bytes_sequence & 8388608) = 8388608) = 1, 1, 0)) AS NUTS_CASHEWS,
        (IF(((allergen_bytes_sequence & 16777216) = 16777216) = 1, 1, 0)) AS NUTS_PECANS,
        (IF(((allergen_bytes_sequence & 33554432) = 33554432) = 1, 1, 0)) AS NUTS_BRAZIL,
        (IF(((allergen_bytes_sequence & 67108864) = 67108864) = 1, 1, 0)) AS NUTS_PISTACHIOS,
        (IF(((allergen_bytes_sequence & 134217728) = 134217728) = 1, 1, 0)) AS NUTS_MACADAMIA,
        (IF(((allergen_bytes_sequence & 256) = 256) = 1, 1, 0)) AS SESAME_SEEDS,
        (IF(((allergen_bytes_sequence & 512) = 512) = 1, 1, 0)) AS SULPHUR_DIOXIDE,
        (IF(((allergen_bytes_sequence & 1024) = 1024) = 1, 1, 0)) AS MOLLUSCS,
        (IF(((allergen_bytes_sequence & 2048) = 2048) = 1, 1, 0)) AS CELERY,
        (IF(((allergen_bytes_sequence & 4096) = 4096) = 1, 1, 0)) AS MUSTARD,
        (IF(((allergen_bytes_sequence & 8192) = 8192) = 1, 1, 0)) AS LUPIN
    FROM ste__edibles) T2
ON T1.ingredient_id = T2.id
LEFT JOIN
    (SELECT id,
        energy_id,
        fibre_id,
        protein_id,
        salt_id,
        fat_id,
        saturated_fat_id,
        carbohydrate_id,
        sugar_id
    FROM ste__nutrition) T3
ON T2.nutrition_id = T3.id
LEFT JOIN
    (SELECT id,
        quantity AS energy_quantity,
        unit AS energy_unit
    FROM ste__nutrition_values) T4
ON T3.energy_id = T4.id
LEFT JOIN
    (SELECT id,
        quantity AS fibre_quantity,
        unit AS fibre_unit
    FROM ste__nutrition_values) T5
ON T3.fibre_id = T5.id
LEFT JOIN
    (SELECT id,
        quantity AS protein_quantity,
        unit AS protein_unit
    FROM ste__nutrition_values) T6
ON T3.protein_id = T6.id
LEFT JOIN
    (SELECT id,
        quantity AS salt_quantity,
        unit AS salt_unit
    FROM ste__nutrition_values) T7
ON T3.salt_id = T7.id
LEFT JOIN
    (SELECT id,
        quantity AS fat_quantity,
        unit AS fat_unit
    FROM ste__nutrition_values) T8
ON T3.fat_id = T8.id
LEFT JOIN
    (SELECT id,
        quantity AS saturated_fat_quantity,
        unit AS saturated_fat_unit
    FROM ste__nutrition_values) T9
ON T3.saturated_fat_id = T9.id
LEFT JOIN
    (SELECT id,
        quantity AS carbohydrate_quantity,
        unit AS carbohydrate_unit
    FROM ste__nutrition_values) T10
ON T3.carbohydrate_id = T10.id
LEFT JOIN
    (SELECT id,
        quantity AS sugar_quantity,
        unit AS sugar_unit
    FROM ste__nutrition_values) T11
ON T3.sugar_id = T11.id;