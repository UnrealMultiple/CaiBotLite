from caibotlite.services.sensitive_words_filter import SensitiveWordsFilter
from caibotlite.services.url_filter import UrlFilter
from caibotlite.utils.tag import replace_item_tag, remove_color_tag


def filter_all(text: str):
    # return UrlFilter.replace_urls(SensitiveWordsFilter.replace(text))
    return SensitiveWordsFilter.replace(text)


def check_text_ok(text: str):
    # if UrlFilter.has_url(text):
    #     return False
    if SensitiveWordsFilter.has_sensitive(text):
        return False

    return True


def replace_all_tag(text: str):
    return replace_item_tag(remove_color_tag(text))


from typing import Dict


def build_rank(rank_lines: Dict[str, str], page: int, max_lines_one_page: int = 10) -> str:
    if len(rank_lines) == 0:
        return "啥都没有呢~"

    format_rank_lines = []
    for rank, (name, data) in enumerate(rank_lines.items(), start=1):
        format_rank_lines.append(f"{rank}. {name}: {data}")

    total_lines = len(format_rank_lines)
    total_pages = max(1, (total_lines + max_lines_one_page - 1) // max_lines_one_page)
    page = max(1, min(page, total_pages))

    start_idx = (page - 1) * max_lines_one_page
    end_idx = min(start_idx + max_lines_one_page, total_lines)
    page_lines = format_rank_lines[start_idx:end_idx]

    min_display_lines = 3
    if len(page_lines) < min_display_lines:
        page_lines += ["-"] * (min_display_lines - len(page_lines))

    page_info = f"\n· 第 {page} 页 / 共 {total_pages} 页 · "

    return "\n".join(page_lines) + page_info
