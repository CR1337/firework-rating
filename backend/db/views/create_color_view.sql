CREATE VIEW IF NOT EXISTS color_view
AS
SELECT
	color.name AS color_name,
  colorxproduct.product_id AS product_id
FROM
	color
JOIN
	colorxproduct
ON
	color.id_=colorxproduct.color_id;
