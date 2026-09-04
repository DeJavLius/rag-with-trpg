from conftest import EXPECTED_PAGES, URL_KEYWORD

from rag_with_trpg.crawl.crawl import enroll_all_links

"""
title: claude 작성 python script — 테스트 본문
content: D-20 조건부 (2026-09-04 개정). 「무엇을 잠그나」와 기대값은 직접 정하고,
         pytest 문법·assert 표현은 AI 가 적었다.
         수집(crawl.py) 소관. 변환(convert.py) 테스트는 test_convert.py 에 있다.
"""


def test_enroll_all_links_collects_every_page(home_html):
    """홈 한 장에서 39개가 나온다 — 재귀 크롤링이 필요 없다는 전제를 잠근다.

    1주차 완료 조건 「raw/ 에 HTML 39개」의 회귀 가드다.
    """
    links = enroll_all_links(home_html, URL_KEYWORD)

    assert len(links) == EXPECTED_PAGES


def test_enroll_all_links_is_deduped_and_sorted(home_html):
    links = enroll_all_links(home_html, URL_KEYWORD)

    assert links == sorted(set(links))


def test_enroll_all_links_drops_external(home_html):
    """사이트 밖 링크가 섞이면 크롤이 남의 서버를 때린다."""
    links = enroll_all_links(home_html, URL_KEYWORD)

    assert all(link.startswith(URL_KEYWORD) for link in links)


def test_enroll_all_links_keeps_hyphens(home_html):
    """슬러그의 하이픈이 링크 단계에서는 살아 있다.

    raw 파일명은 `replace('-', '')` 로 하이픈을 지우므로 (비가역),
    원본 슬러그를 얻을 수 있는 곳은 여기와 og:url 뿐이다 — meta_mapped.slug_of 참조.
    """
    links = enroll_all_links(home_html, URL_KEYWORD)

    assert any("-" in link.removeprefix(URL_KEYWORD) for link in links)
