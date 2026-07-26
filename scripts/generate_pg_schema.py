"""根据当前 ORM 模型生成 PostgreSQL 建表语句, 输出到 scripts/schema_pg.sql.

用法 (在项目根目录执行):
    uv run python scripts/generate_pg_schema.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

from caibotlite.models import Base


def main() -> None:
    dialect = postgresql.dialect()
    lines = ["-- 由 scripts/generate_pg_schema.py 根据 ORM 模型自动生成, 请勿手改\n"]
    for table in Base.metadata.sorted_tables:
        lines.append(str(CreateTable(table).compile(dialect=dialect)).strip() + ";\n")
        for index in table.indexes:
            lines.append(str(CreateIndex(index).compile(dialect=dialect)).strip() + ";")
        lines.append("")
    out = Path(__file__).parent / "schema_pg.sql"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[*] 已生成 {out}")


if __name__ == "__main__":
    main()
