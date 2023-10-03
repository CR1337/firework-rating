CREATE VIEW IF NOT EXISTS tag_view
AS
SELECT
	tag.name AS tag_name,
  tagxproduct.product_id AS product_id
FROM
	tag
JOIN
	tagxproduct
ON
	tag.id_=tagxproduct.tag_id;
