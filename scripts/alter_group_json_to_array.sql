-- 将已上线 PG 库中 group.admins / group.black_list 从 JSON 原地转换为 VARCHAR[]
-- 适用于在 "改数组" 版本之前就完成迁移的库; 全新迁移的库无需执行 (建表即为数组)
-- 用法: psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f scripts/alter_group_json_to_array.sql
-- 注意: 执行前请先停止机器人

BEGIN;

-- USING 不允许子查询, 借助临时函数转换; WITH ORDINALITY 保证元素顺序不变
-- (admins[1] 是群主, 顺序不能乱)
CREATE FUNCTION pg_temp.json_to_text_array(j json) RETURNS varchar[]
LANGUAGE sql IMMUTABLE AS
$$ SELECT coalesce(array_agg(x ORDER BY ord), '{}')
   FROM json_array_elements_text(j) WITH ORDINALITY AS t(x, ord) $$;

ALTER TABLE "group"
  ALTER COLUMN admins TYPE VARCHAR[] USING pg_temp.json_to_text_array(admins),
  ALTER COLUMN black_list TYPE VARCHAR[] USING pg_temp.json_to_text_array(black_list);

COMMIT;
