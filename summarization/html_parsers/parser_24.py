from datetime import datetime
from typing import Optional, Set

import dateparser
from bs4 import BeautifulSoup

from summarization.html_parsers.parser_base import ParserBase
from summarization.utils.assertion import assert_has_article, assert_has_title


class Parser24(ParserBase):
    def get_title(self, url, soup) -> str:
        title = soup.find('h1', class_="o-post__title")
        if title is None:
            # old css class
            title = soup.find('h1', class_="post-title")
        assert_has_title(title, url)
        return title.get_text(' ').strip()

    def get_lead(self, soup) -> Optional[str]:
        lead = soup.find('div', class_="lead")
        return "" if lead is None else lead.get_text(' ').strip()

    def get_article_text(self, url, soup) -> str:
        article = soup.find('div', class_="post-body")
        assert_has_article(article, url)
        return article.get_text(' ').strip()

    def get_date_of_creation(self, soup) -> Optional[datetime]:
        date = soup.find('div', class_='author-content')
        if date and date.p:
            return dateparser.parse(date.p.get_text(' '))

        date = soup.find('span', class_='o-post__date')
        if date:
            date_text = date.get_text(' ')
            if 'FRISS' in date.get_text(' '):
                date_text = date_text.split("FRISS")[0]
            return dateparser.parse(date_text)

        if not date:
            date = soup.find('span', class_='m-author__catDateTitulusCreateDate')

        if not date:
            date = soup.find('div', class_='m-author__wrapCatDateTitulus')

        if not date:
            return None

        return dateparser.parse(date.get_text(' '))

    def get_tags(self, soup) -> Set[str]:
        tag = soup.find('a', class_='o-articleHead__catWrap')
        if tag is None:
            # old css class
            tag = soup.find('a', class_='tag')
        return set() if tag is None else set(tag)

    def remove_captions(self, soup) -> BeautifulSoup:
        to_remove = []
        to_remove.extend(soup.find_all('blockquote', class_='instagram-media'))
        to_remove.extend(soup.find_all('blockquote', class_='twitter-tweet'))
        to_remove.extend(soup.find_all('div', class_='fb-post'))
        to_remove.extend(soup.find_all('span', class_='a-imgSource'))
        to_remove.extend(soup.find_all('div', class_='m-authorRecommend'))
        to_remove.extend(soup.find_all('div', class_='o-cegPostCnt'))
        to_remove.extend(soup.find_all('div', class_='article-recommendation-container'))
        to_remove.extend(soup.find_all('div', class_='wpb_content_element'))
        to_remove.extend(soup.find_all('div', class_='m-newsletter'))
        to_remove.extend(soup.find_all('figure', class_='wp-caption'))
        # mischievous pages contains text in the sidebar
        to_remove.extend(soup.find_all('div', class_='sidebar'))
        to_remove.extend(soup.find_all('span', class_='category titulus'))
        for r in to_remove:
            r.decompose()
        return soup
