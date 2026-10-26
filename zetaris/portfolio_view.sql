-- Federate an organisation's scattered name data into one Zetaris view NameScout can query.
-- Run each statement once in the Zetaris SQL editor (admin), adjusting source names to your instance.
-- 1) Register sources (examples: a Postgres CRM, a CSV product catalogue on S3/file, a REST vendor API)
--    CREATE LIGHTNING DATABASE crm USING POSTGRES OPTIONS (url "jdbc:postgresql://host/crm", user "...", password "...");
--    CREATE LIGHTNING FILESTORE catalogue USING CSV OPTIONS (path "s3://bucket/products.csv", header "true");
-- 2) One unified view across them
CREATE SCHEMASTORE VIEW namescout.brand_portfolio AS
  SELECT account_name AS name, 'customer' AS kind, 'crm' AS system, owner AS owner FROM crm.public.accounts
  UNION ALL
  SELECT product_name, 'product', 'catalogue', team FROM catalogue.products
  UNION ALL
  SELECT vendor_name, 'vendor', 'erp', buyer FROM erp.public.vendors;
