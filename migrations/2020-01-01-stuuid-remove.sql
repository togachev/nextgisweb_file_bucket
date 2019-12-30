ALTER TABLE public.file_bucket DROP COLUMN stuuid;

ALTER TABLE public.file_bucket_file
ALTER COLUMN fileobj_id SET NOT NULL;
