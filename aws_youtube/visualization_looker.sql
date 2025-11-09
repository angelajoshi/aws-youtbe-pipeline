-- Top 10 channels by total views
SELECT channel_title, SUM(views) AS total_views
FROM youtube_trending
GROUP BY channel_title
ORDER BY total_views DESC
LIMIT 10;

-- Daily trending view count
SELECT DATE(published_at) AS publish_date, SUM(views) AS total_views
FROM youtube_trending
GROUP BY publish_date
ORDER BY publish_date;

-- Engagement ratio
SELECT 
  title,
  ROUND(likes / NULLIF(views, 0), 3) AS like_to_view_ratio
FROM youtube_trending
ORDER BY like_to_view_ratio DESC
LIMIT 10;
