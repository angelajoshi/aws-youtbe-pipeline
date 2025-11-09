-- ============================================================
-- STEP 1️⃣ : USE YOUR ACCOUNT ROLE AND CONTEXT
-- ============================================================
USE ROLE ACCOUNTADMIN;
USE WAREHOUSE COMPUTE_WH;
USE DATABASE SNOWFLAKE_LEARNING_DB;
USE SCHEMA DEVANSHU5_LOAD_SAMPLE_DATA_FROM_S3;

-- ============================================================
-- STEP 2️⃣ : CREATE STORAGE INTEGRATION (ONE TIME SETUP)
-- ============================================================
-- ⚠️ Make sure this matches your AWS IAM role and external ID
CREATE OR REPLACE STORAGE INTEGRATION s3_integration
TYPE = EXTERNAL_STAGE
STORAGE_PROVIDER = S3
ENABLED = TRUE
STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::939794643989:role/s3-integration-role'
STORAGE_ALLOWED_LOCATIONS = ('s3://youtube-data-analysis-aws/')
STORAGE_AWS_EXTERNAL_ID = 'MXYRHPT-KV51575';

-- Verify integration
DESC INTEGRATION s3_integration;

-- ============================================================
-- STEP 3️⃣ : CREATE FILE FORMAT FOR PARQUET
-- ============================================================
CREATE OR REPLACE FILE FORMAT parquet_format
TYPE = PARQUET
COMPRESSION = SNAPPY;

-- ============================================================
-- STEP 4️⃣ : CREATE STAGE LINKED TO S3 BUCKET
-- ============================================================
CREATE OR REPLACE STAGE my_stage
URL = 's3://youtube-data-analysis-aws/processed_data/'
STORAGE_INTEGRATION = s3_integration
FILE_FORMAT = parquet_format;

-- Verify the stage
LIST @my_stage;

-- ============================================================
-- STEP 5️⃣ : CREATE TARGET TABLE IN SNOWFLAKE
-- ============================================================
CREATE OR REPLACE TABLE youtube_trending (
    video_id STRING,
    title STRING,
    channel_title STRING,
    published_at TIMESTAMP_NTZ,
    views NUMBER,
    likes NUMBER,
    comments NUMBER
);

-- ============================================================
-- STEP 6️⃣ : LOAD DATA FROM PARQUET (TRANSFORMATION)
-- ============================================================
COPY INTO youtube_trending
FROM (
    SELECT 
        $1:videoId::STRING AS video_id,
        $1:title::STRING AS title,
        $1:channelTitle::STRING AS channel_title,
        TRY_TO_TIMESTAMP_NTZ($1:publishedAt::STRING) AS published_at,
        $1:viewCount::NUMBER AS views,
        $1:likeCount::NUMBER AS likes,
        $1:commentCount::NUMBER AS comments
    FROM @my_stage
)
FILE_FORMAT = (FORMAT_NAME = parquet_format);

-- ============================================================
-- STEP 7️⃣ : VERIFY DATA LOAD
-- ============================================================
SELECT COUNT(*) AS total_rows FROM youtube_trending;

SELECT * 
FROM youtube_trending
ORDER BY views DESC
LIMIT 10;
