/* change PK to unique */
ALTER TABLE public.file_bucket_file
DROP CONSTRAINT file_bucket_file_pkey;

ALTER TABLE public.file_bucket_file
ADD CONSTRAINT file_bucket_file_file_bucket_id_name_key
UNIQUE (file_bucket_id, "name");

/* add id PK */
ALTER TABLE public.file_bucket_file
ADD COLUMN id serial NOT NULL;

ALTER TABLE public.file_bucket_file
ADD PRIMARY KEY (id);

/* add file_storage relation */
ALTER TABLE public.file_bucket_file
ADD COLUMN fileobj_id integer;

ALTER TABLE public.file_bucket_file
ADD CONSTRAINT file_bucket_file_fileobj_id_fkey
FOREIGN KEY (fileobj_id)
REFERENCES public.fileobj (id) MATCH SIMPLE
ON UPDATE NO ACTION
ON DELETE NO ACTION;
