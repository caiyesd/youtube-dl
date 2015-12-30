# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor

from ..utils import (
    float_or_none,
    unescapeHTML,
)


class RteIE(InfoExtractor):
    IE_NAME = 'rte'
    IE_DESC = 'Raidió Teilifís Éireann TV'
    _VALID_URL = r'https?://(?:www\.)?rte\.ie/player/[^/]{2,3}/show/[^/]+/(?P<id>[0-9]+)'
    _TEST = {
        'url': 'http://www.rte.ie/player/ie/show/iwitness-862/10478715/',
        'info_dict': {
            'id': '10478715',
            'ext': 'flv',
            'title': 'Watch iWitness  online',
            'thumbnail': 're:^https?://.*\.jpg$',
            'description': 'iWitness : The spirit of Ireland, one voice and one minute at a time.',
            'duration': 60.046,
        },
        'params': {
            'skip_download': 'f4m fails with --test atm'
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        title = self._og_search_title(webpage)
        description = self._html_search_meta('description', webpage, 'description')
        duration = float_or_none(self._html_search_meta(
            'duration', webpage, 'duration', fatal=False), 1000)

        thumbnail_id = self._search_regex(
            r'<meta name="thumbnail" content="uri:irus:(.*?)" />', webpage, 'thumbnail')
        thumbnail = 'http://img.rasset.ie/' + thumbnail_id + '.jpg'

        feeds_url = self._html_search_meta("feeds-prefix", webpage, 'feeds url') + video_id
        json_string = self._download_json(feeds_url, video_id)

        # f4m_url = server + relative_url
        f4m_url = json_string['shows'][0]['media:group'][0]['rte:server'] + json_string['shows'][0]['media:group'][0]['url']
        f4m_formats = self._extract_f4m_formats(f4m_url, video_id)

        return {
            'id': video_id,
            'title': title,
            'formats': f4m_formats,
            'description': description,
            'thumbnail': thumbnail,
            'duration': duration,
        }



class RteRadioIE(InfoExtractor):
    IE_NAME = 'rte:radio'
    IE_DESC = 'Raidió Teilifís Éireann radio'
    # Radioplayer URLs have the specifier #!rii=<channel_id>:<id>:<playable_item_id>:<date>:
    # where the IDs are int/empty, the date is DD-MM-YYYY, and the specifier may be truncated.
    # An <id> uniquely defines an individual recording, and is the only part we require.
    _VALID_URL = r'https?://(?:www\.)?rte\.ie/radio/utils/radioplayer/rteradioweb\.html#!rii=(?:[0-9]*)(?:%3A|:)(?P<id>[0-9]+)'

    _TEST = {
        'url': 'http://www.rte.ie/radio/utils/radioplayer/rteradioweb.html#!rii=16:10507902:2414:27-12-2015:',
        'info_dict': {
            'id': '10507902',
            'ext': 'flv',
            'title': 'Gloria',
            'thumbnail': 're:^https?://.*\.jpg$',
            'description': 'Tim Thurston guides you through a millennium of sacred music featuring Gregorian chant, pure solo voices and choral masterpieces, framed around the glorious music of J.S. Bach.',
            'duration': 7230.0,
        },
        'params': {
            'skip_download': 'f4m fails with --test atm'
        }
    }

    def _real_extract(self, url):
        item_id = self._match_id(url)
        feeds_url = 'http://www.rte.ie/rteavgen/getplaylist/?type=web&format=json&id=' + item_id
        json_string = self._download_json(feeds_url, item_id)

        # NB the string values in the JSON are stored using XML escaping(!)
        show = json_string['shows'][0]
        title = unescapeHTML(show['title'])
        description = unescapeHTML(show.get('description'))
        thumbnail = show.get('thumbnail')
        duration = float_or_none(show.get('duration'), 1000)

        mg = show['media:group'][0]

        formats = []

        if mg.get('url') and not mg['url'].startswith('rtmpe:'):
            formats.append({'url': mg.get('url')})

        if mg.get('hls_server') and mg.get('hls_url'):
            hls_url = mg['hls_server'] +  mg['hls_url']
            hls_formats = self._extract_m3u8_formats(
                    hls_url, item_id, 'mp4', m3u8_id='hls', fatal=False)
            formats.extend(hls_formats)

        if mg.get('hds_server') and mg.get('hds_url'):
            f4m_url = mg['hds_server'] + mg['hds_url']
            f4m_formats = self._extract_f4m_formats(
                    f4m_url, item_id, f4m_id='hds', fatal=False)
            formats.extend(f4m_formats)

        return {
            'id': item_id,
            'title': title,
            'formats': formats,
            'description': description,
            'thumbnail': thumbnail,
            'duration': duration,
        }
