"""把 data/bot.db (SQLite) 中的数据迁移到 PostgreSQL.

用法 (在项目根目录执行):
    uv run python scripts/migrate_sqlite_to_pg.py
    uv run python scripts/migrate_sqlite_to_pg.py --pg postgresql+asyncpg://user:pass@host:5432/caibotlite
    uv run python scripts/migrate_sqlite_to_pg.py --force   # 目标库已有数据时先清空再迁移

说明:
    - 会先在 PG 中按当前 ORM 模型建表 (create_all), 再逐表复制数据
    - 只迁移 ORM 模型中定义的表, SQLite 里的备份表 (如 _login_uuid_old_*) 会被跳过
    - 迁移完成后自动校正各表主键自增序列, 并逐表核对行数
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine

from caibotlite.models import Base

DEFAULT_SQLITE_URL = "sqlite+aiosqlite:///data/bot.db"
DEFAULT_PG_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://caibot:caibot@localhost:5432/caibotlite"
)
CHUNK_SIZE = 1000


async def migrate(sqlite_url: str, pg_url: str, force: bool) -> None:
    src = create_async_engine(sqlite_url)
    dst = create_async_engine(pg_url)
    tables = Base.metadata.sorted_tables  # 按外键依赖排好序

    try:
        async with dst.begin() as dconn:
            await dconn.run_sync(Base.metadata.create_all)

            # 目标表非空时拒绝迁移, 防止重复导入
            non_empty = []
            for table in tables:
                count = await dconn.scalar(
                    text(f'SELECT COUNT(*) FROM "{table.name}"')
                )
                if count:
                    non_empty.append(f"{table.name}({count})")
            if non_empty:
                if not force:
                    print(f"[!] 目标库以下表已有数据: {', '.join(non_empty)}")
                    print("[!] 如需清空后重新迁移, 请加 --force")
                    sys.exit(1)
                names = ", ".join(f'"{t.name}"' for t in tables)
                await dconn.execute(
                    text(f"TRUNCATE {names} RESTART IDENTITY CASCADE")
                )
                print(f"[*] --force: 已清空目标表 {', '.join(non_empty)}")

            # 历史脏数据: 个别 group.open_id 尾部带换行符, 且都是干净 open_id 的
            # 重复行, 无任何表引用它们 -> 直接跳过这些 group 及其 group_config
            skipped_open_ids: set[str] = set()
            skipped_counts: dict[str, int] = {}

            async with src.connect() as sconn:
                for table in tables:
                    rows = [
                        dict(r)
                        for r in (await sconn.execute(select(table))).mappings()
                    ]

                    if table.name == "group":
                        bad = [r for r in rows if r["open_id"] != r["open_id"].strip()]
                        skipped_open_ids = {r["open_id"] for r in bad}
                        rows = [r for r in rows if r["open_id"] not in skipped_open_ids]
                        if bad:
                            skipped_counts["group"] = len(bad)
                            print(f"[*] group: 跳过 {len(bad)} 行 open_id 含换行符的重复垃圾数据")
                    elif table.name == "group_config":
                        before = len(rows)
                        rows = [
                            r for r in rows if r["group_open_id"] not in skipped_open_ids
                        ]
                        if before != len(rows):
                            skipped_counts["group_config"] = before - len(rows)
                            print(f"[*] group_config: 跳过 {before - len(rows)} 行对应的配置")
                    elif table.name == "user":
                        for row in rows:
                            if row["name"] is not None and len(row["name"]) > 32:
                                print(f"[*] user id={row['id']}: 名字超长, 截断为 32 字符")
                                row["name"] = row["name"][:32]

                    # group 表特殊处理:
                    # 1. 历史数据中 parent_open_id 存在空字符串, 规范化为 NULL
                    # 2. 自引用外键要求父行先插入, 故先全部按无父群插入, 再回填
                    parent_fixups = []
                    if table.name == "group":
                        empty = 0
                        for row in rows:
                            if row["parent_open_id"] == "":
                                row["parent_open_id"] = None
                                empty += 1
                            elif row["parent_open_id"] is not None:
                                parent_fixups.append(
                                    {"row_id": row["id"], "parent": row["parent_open_id"]}
                                )
                                row["parent_open_id"] = None
                        if empty:
                            print(f"[*] group: {empty} 行空字符串 parent_open_id 已规范化为 NULL")

                    for i in range(0, len(rows), CHUNK_SIZE):
                        await dconn.execute(table.insert(), rows[i : i + CHUNK_SIZE])

                    if parent_fixups:
                        await dconn.execute(
                            text('UPDATE "group" SET parent_open_id = :parent WHERE id = :row_id'),
                            parent_fixups,
                        )
                        print(f"[*] group: 已回填 {len(parent_fixups)} 行 parent_open_id")

                    print(f"[*] {table.name}: 已复制 {len(rows)} 行")

            # 数据是带 id 插入的, 需要把自增序列拨到 max(id) 之后
            for table in tables:
                for col in table.primary_key.columns:
                    if col.autoincrement is not True and col.name != "id":
                        continue
                    await dconn.execute(
                        text(
                            f"SELECT setval("
                            f"pg_get_serial_sequence('\"{table.name}\"', '{col.name}'), "
                            f'COALESCE((SELECT MAX("{col.name}") FROM "{table.name}"), 0) + 1, '
                            f"false)"
                        )
                    )

        # 核对行数
        ok = True
        async with src.connect() as sconn, dst.connect() as dconn:
            for table in tables:
                src_count = await sconn.scalar(
                    text(f'SELECT COUNT(*) FROM "{table.name}"')
                )
                dst_count = await dconn.scalar(
                    text(f'SELECT COUNT(*) FROM "{table.name}"')
                )
                expected = src_count - skipped_counts.get(table.name, 0)
                mark = "OK" if expected == dst_count else "MISMATCH"
                if expected != dst_count:
                    ok = False
                skipped = skipped_counts.get(table.name)
                extra = f" (跳过 {skipped} 行脏数据)" if skipped else ""
                print(f"[=] {table.name}: sqlite={src_count} pg={dst_count}{extra} {mark}")

        if not ok:
            print("[!] 存在行数不一致的表, 请检查!")
            sys.exit(1)
        print("[*] 迁移完成")
    finally:
        await src.dispose()
        await dst.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate SQLite data to PostgreSQL")
    parser.add_argument("--sqlite", default=DEFAULT_SQLITE_URL, help="源 SQLite URL")
    parser.add_argument("--pg", default=DEFAULT_PG_URL, help="目标 PostgreSQL URL")
    parser.add_argument(
        "--force", action="store_true", help="目标表非空时先 TRUNCATE 再迁移"
    )
    args = parser.parse_args()
    print(f"[*] 源库: {args.sqlite}")
    print(f"[*] 目标库: {args.pg}")
    asyncio.run(migrate(args.sqlite, args.pg, args.force))


if __name__ == "__main__":
    main()
