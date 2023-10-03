CREATE VIEW IF NOT EXISTS product_view
AS
SELECT
	name AS product_name,
  price,
  raw_shot_count AS shot_count,
  duration,
  fan,
  nem,
  rating,
  color_name,
  tag_name,
	product.id_ AS product_id,
  url,
  youtube_handle,
  min_height,
  max_height,
  availability,
  is_new
FROM
	product
JOIN
	color_view
ON
	product.id_=color_view.product_id
JOIN
	tag_view
ON
	product.id_=tag_view.product_id;