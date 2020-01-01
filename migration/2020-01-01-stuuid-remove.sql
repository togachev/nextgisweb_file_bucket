-- Temporary constraint: check all rows have stuuid is NULL
ALTER TABLE file_bucket
    ADD CONSTRAINT file_bucket_check_stuuid_is_null
        CHECK (stuuid IS NULL);

-- Drop temporary constraint
ALTER TABLE file_bucket
    DROP CONSTRAINT file_bucket_check_stuuid_is_null;

ALTER TABLE file_bucket DROP COLUMN stuuid;

ALTER TABLE file_bucket_file
    ALTER COLUMN fileobj_id SET NOT NULL;
