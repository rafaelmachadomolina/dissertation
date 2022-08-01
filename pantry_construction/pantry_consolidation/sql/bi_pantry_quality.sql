-- Query to build matched ingredient table for BI purposes

-- DROP TABLE kp_bi_pantry_quality;
-- TRUNCATE TABLE kp_bi_pantry_quality;

CREATE TABLE kp_bi_pantry_quality (
  id INT NOT NULL AUTO_INCREMENT,
  matched_ingredient_id INT NOT NULL,
  property_type VARCHAR(31),
  property VARCHAR(31),
  number_data_points INT,
  reference_value DECIMAL(19, 6),
  mean_absolute_deviation DECIMAL(19, 6),
  data_source VARCHAR(63),
  PRIMARY KEY(id)
);
