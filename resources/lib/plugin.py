# -*- coding: utf-8 -*-

import routing
import logging
import xbmcaddon
import xbmcgui
import xbmcvfs
import xbmc
import xbmcplugin
from resources.lib import kodiutils
from resources.lib import kodilogging
from resources.lib import ids
from resources.lib import xxtea
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, addDirectoryItems, endOfDirectory, setResolvedUrl, setContent
from distutils.version import LooseVersion

import pytz
import tzlocal
import html2text
import codecs
import base64

try:
    import inputstreamhelper
    inputstream = True
except ImportError:
    inputstream = False

try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

try:
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError
    from urllib.parse import quote, unquote, urlparse, parse_qs, urlencode
except ImportError:
    from urllib import quote, unquote, urlencode
    from urllib2 import Request, urlopen, HTTPError, URLError
    from urlparse import urlparse, parse_qs

try:
    from multiprocessing.pool import ThreadPool
    multiprocess = True
except ImportError:
    multiprocess = False

import locale
import time
from datetime import date, datetime, timedelta
import hashlib
import json
import gzip
import sys
import re

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))
kodilogging.config()
plugin = routing.Plugin()

__profile__ = xbmc.translatePath(ADDON.getAddonInfo('profile'))

if not xbmcvfs.exists(__profile__):
    xbmcvfs.mkdirs(__profile__)

favorites_file_path = __profile__+'favorites.json'
favorites = {}

icon_path = ADDON.getAddonInfo('path')+'/resources/logos/{0}.png'

setContent(plugin.handle, '')

@plugin.route('/')
def index():
    icon = get_url(ids.overview_url)
    live_icon = ''
    highlights_icon = ''
    mediathek_icon = ''
    tv_programm_icon = ''
    search_icon = ''
    search_query = ids.search_query
    settings_icon = ''
    if icon != '':
        icon_json = json.loads(icon)
        for element in icon_json:
            if u'navigations' in element and element['navigations'] != None and len(element['navigations']) > 0:
                for bar in element['navigations']:
                    if 'navigation_type' in bar and bar['navigation_type'] == 'bottom_tab_bar' and 'nav_items' in bar:
                        for icons in bar['nav_items']:
                            if icons['title'] == 'Live' and 'assets' in icons and 'icon' in icons['assets']:
                                live_icon = icons['assets']['icon']
                            if icons['title'] == 'Highlights' and 'assets' in icons and 'icon' in icons['assets']:
                                highlights_icon = icons['assets']['icon']
                            if icons['title'] == 'Mediathek' and 'assets' in icons and 'icon' in icons['assets']:
                                live_icon = icons['assets']['icon']
                            if icons['title'] == 'mediathek_icon' and 'assets' in icons and 'icon' in icons['assets']:
                                live_icon = icons['assets']['icon']
                            if icons['title'] == 'TV Programm' and 'assets' in icons and 'icon' in icons['assets']:
                                tv_programm_icon = icons['assets']['icon']
                    if 'navigation_type' in bar and bar['navigation_type'] == 'navigation_bar' and 'nav_items' in bar:
                        for icons in bar['nav_items']:
                            if icons['title'] == 'Search' and 'assets' in icons and 'icon' in icons['assets']:
                                search_icon = icons['assets']['icon']
                                if 'data' in icons and 'source' in icons['data'] and icons['data']['source'] != None:
                                    qs = get_query(icons['data']['source'])
                                    if 'reactProps[baseSearchUrl]' in qs:
                                        search_query = get_query(base64.b64decode(qs['reactProps[baseSearchUrl]'][0]).decode('UTF-8'))
                            if icons['title'] == 'Settings' and 'assets' in icons and 'icon' in icons['assets']:
                                settings_icon = icons['assets']['icon']
    else:
        kodiutils.notification('ERROR getting URL', 'using saved values')
    listitem = ListItem('Live')
    listitem.setArt({'icon': live_icon, 'thumb': live_icon, 'poster': live_icon})
    addDirectoryItem(plugin.handle, plugin.url_for(
        show_category, 'livestream'), listitem, True)
    listitem = ListItem('Highlights')
    listitem.setArt({'icon': highlights_icon, 'thumb': highlights_icon, 'poster': highlights_icon})
    addDirectoryItem(plugin.handle, plugin.url_for(
        show_category, 'highlights'), listitem, True)
    listitem = ListItem('Mediathek')
    listitem.setArt({'icon': mediathek_icon, 'thumb': mediathek_icon, 'poster': mediathek_icon})
    addDirectoryItem(plugin.handle, plugin.url_for(
        show_category, 'mediathek'), listitem, True)
    listitem = ListItem('TV Programm')
    listitem.setArt({'icon': tv_programm_icon, 'thumb': tv_programm_icon, 'poster': tv_programm_icon})
    addDirectoryItem(plugin.handle, plugin.url_for(
        show_category, 'tvprogramm'), listitem, True)
    listitem = ListItem(kodiutils.get_string(32001))
    listitem.setArt({'icon': search_icon, 'thumb': search_icon, 'poster': search_icon})
    addDirectoryItem(plugin.handle, plugin.url_for(
        show_search, json.dumps(search_query)), listitem, True)
    addDirectoryItem(plugin.handle, plugin.url_for(
        show_category, 'favorites'), ListItem(kodiutils.get_string(32002)), True)
    listitem = ListItem(kodiutils.get_string(32003))
    listitem.setArt({'icon': settings_icon, 'thumb': settings_icon, 'poster': settings_icon})
    addDirectoryItem(plugin.handle, plugin.url_for(
        open_settings), listitem)
    endOfDirectory(plugin.handle)

@plugin.route('/info')
def show_info():
    xbmc.executebuiltin('Action(Info)')

@plugin.route('/settings')
def open_settings():
    kodiutils.show_settings()

@plugin.route('/category/<category_id>')
def show_category(category_id):
    #setContent(plugin.handle, 'albums')
    if category_id == 'livestream':
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
        result = get_url(ids.api_brands_url, headers = ids.api_headers)
        if result:
            channels = json.loads(result)
            streams = []
            if multiprocess:
                threads = []
                pool = ThreadPool(processes=len(channels['response']['data']))
                for brand in channels['response']['data']:
                        thread = pool.apply_async(get_livestream, (brand['channelId'], brand['title'], brand['id']))
                        thread.name = brand['channelId']
                        thread.daemon = True
                        threads.append(thread)
                for thread in threads:
                    streams.append(thread.get())
                    pool.close()
                    pool.join()
            else:
                for brand in channels['response']['data']:
                    streams.update(get_livestream(brand['channelId'], brand['title'], brand['id']))
            addDirectoryItems(plugin.handle, streams)
        else:
            kodiutils.notification('ERROR GETTING LIVESTREAM INFO', 'using saved values')
            add_default_streams()
        addDirectoryItem(plugin.handle, plugin.url_for(
            show_category, 'germany'), ListItem(kodiutils.get_string(32027)), True)
        addDirectoryItem(plugin.handle, plugin.url_for(
            show_category, 'switzerland'), ListItem(kodiutils.get_string(32028)), True)
    elif category_id == 'germany' or category_id == 'switzerland':
        if category_id == 'germany':
            id = '_de'
            name = ' DE'
        else:
            id = '_ch'
            name = ' CH'
        for stream in ids.streams_pro7sat1:
            addDirectoryItem(plugin.handle, url=plugin.url_for(
                play_livestream, stream[0]+id), listitem=get_listitem(stream[1]+name, icon = icon_path.format(stream[0])))

    elif category_id == 'favorites':
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
        global favorites
        if not favorites and xbmcvfs.exists(favorites_file_path):
            favorites_file = xbmcvfs.File(favorites_file_path)
            favorites = json.load(favorites_file)
            favorites_file.close()
        for item in favorites:
            legacy=''
            if 'by_category' in item:
                legacy = ' | legacy'
            listitem = ListItem(favorites[item]['name']+legacy)
            listitem.setArt({'icon': favorites[item]['icon'], 'thumb':favorites[item]['icon'], 'poster':favorites[item]['icon'], 'fanart' : favorites[item]['fanart']})
            add_favorites_context_menu(listitem, item, favorites[item]['name'], favorites[item]['icon'], favorites[item]['fanart'])
            addDirectoryItem(plugin.handle, url=item,
                listitem=listitem, isFolder=True)
    elif category_id == 'tvprogramm':
        channels = get_url(ids.api_brands_url, headers = ids.api_headers)
        if channels:
            channels_json = json.loads(channels)
            xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
            for channel in channels_json['response']['data']:
                listitem = ListItem(channel['title'])
                icon = get_channel_icon(channel['channelId'])
                listitem.setArt({'icon': icon, 'thumb': icon, 'poster': icon})
                addDirectoryItem(plugin.handle, url=plugin.url_for(
                    show_epg, channel_id=channel['channelId'], icon=quote(icon)), listitem=listitem, isFolder=True)
    elif category_id == 'mediathek':
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            show_mediathek_popular), listitem=ListItem(kodiutils.get_string(32034)), isFolder=True)
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            show_mediathek_genre), listitem=ListItem(kodiutils.get_string(32035)), isFolder=True)
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            show_mediathek_channel), listitem=ListItem(kodiutils.get_string(32036)), isFolder=True)
    elif category_id == 'genres':
        genres = get_url(ids.api_genres_url, headers = ids.api_headers)
        if genres:
            genres = json.loads(genres)
            for genre in genres['response']['data']:
                addDirectoryItem(plugin.handle, url=plugin.url_for(
                    show_a_z, ids.api_tvshows_genre_query.format(genres=genre['id'])), listitem=ListItem(genre['title']), isFolder=True)
    elif category_id == 'highlights':
        add_tvshows('', sub_page = ids.api_highlights_url, limit = 100)
        endOfDirectory(plugin.handle)
    else:
        addDirectoryItem(plugin.handle, '', ListItem(kodiutils.get_string(32004)), False)
    endOfDirectory(plugin.handle)

@plugin.route('/category/epg/id=<channel_id>')
def show_epg(channel_id):
    icon = ''
    if 'icon' in plugin.args:
        icon = plugin.args['icon'][0]
    today = date.today()
    # past epg
    addDirectoryItem(plugin.handle, plugin.url_for(
        show_epg_past, channel_id=channel_id, icon=icon), ListItem(kodiutils.get_string(32014)), True)
    # show epg from today
    addDirectoryItem(plugin.handle, plugin.url_for(
        show_epg_programm, channel_id=channel_id, dates=today.strftime('%Y-%m-%d'), icon=icon),
        ListItem(kodiutils.get_string(32015).format(kodiutils.get_string(32017))), True)
    # future epg
    # get last day available
    result = get_url(ids.api_epg_url + ids.api_epg_last.format(channelId=channel_id, start=(today.strftime('%Y-%m-%d')+'T00:00')), headers = ids.api_headers)
    last_date = ''
    if result:
        result = json.loads(result)
        if len(result['response']['data']) > 0:
            last = result['response']['data'][0]
            if 'startTime' in last and last['startTime'] != None:
                try:
                    local_tz = tzlocal.get_localzone()
                    startDATE = datetime(1970, 1, 1) + timedelta(seconds=last['startTime'])
                    startDATE = pytz.utc.localize(startDATE)
                    startDATE = startDATE.astimezone(local_tz)
                    last_date = startDATE.date()
                except: pass
    if last_date:
        i = 1
        future_date = today + timedelta(days = i)
        while future_date <= last_date:
            addDirectoryItem(plugin.handle, plugin.url_for(
                show_epg_programm, channel_id=channel_id, dates=future_date.strftime('%Y-%m-%d'), icon=icon),
                ListItem(kodiutils.get_string(32015).format(future_date.strftime('%d.%m.%Y'))), True)
            i += 1
            future_date = today + timedelta(days = i)
    else:
        for i in range(1, 14, 1):
            future_date = today + timedelta(days = i)
            addDirectoryItem(plugin.handle, plugin.url_for(
                show_epg_programm, channel_id=channel_id, dates=future_date.strftime('%Y-%m-%d'), icon=icon),
                ListItem(kodiutils.get_string(32015).format(future_date.strftime('%d.%m.%Y'))), True)
    endOfDirectory(plugin.handle)

@plugin.route('/category/epg/id=<channel_id>/past')
def show_epg_past(channel_id):
    icon = ''
    if 'icon' in plugin.args:
        icon = plugin.args['icon'][0]
    today = date.today()
    
    result = get_url(ids.api_epg_url + ids.api_epg_first.format(channelId=channel_id), headers = ids.api_headers)
    first_date = ''
    if result:
        result = json.loads(result)
        if len(result['response']['data']) > 0:
            first = result['response']['data'][0]
            if 'startTime' in first and first['startTime'] != None:
                try:
                    local_tz = tzlocal.get_localzone()
                    startDATE = datetime(1970, 1, 1) + timedelta(seconds=first['startTime'])
                    startDATE = pytz.utc.localize(startDATE)
                    startDATE = startDATE.astimezone(local_tz)
                    first_date = startDATE.date()
                except: pass
    # past epg
    if first_date:
        i = -1
        past_date = today + timedelta(days = i)
        while past_date >= first_date:
            #show_epg_programm(channel_id, past_date.strftime('%Y%m%d'), icon)
            addDirectoryItem(plugin.handle, plugin.url_for(
                show_epg_programm, channel_id=channel_id, dates=past_date.strftime('%Y-%m-%d'), icon=icon),
                ListItem(kodiutils.get_string(32015).format(past_date.strftime('%d.%m.%Y'))), True)
            i -= 1
            past_date = today + timedelta(days = i)
    else:
        for i in range(-1,-60, -1):
            past_date = today + timedelta(days = i)
            #show_epg_programm(channel_id, past_date.strftime('%Y%m%d'), icon)
            addDirectoryItem(plugin.handle, plugin.url_for(
                show_epg_programm, channel_id=channel_id, dates=past_date.strftime('%Y-%m-%d'), icon=icon),
                ListItem(kodiutils.get_string(32015).format(past_date.strftime('%d.%m.%Y'))), True)
    endOfDirectory(plugin.handle)

@plugin.route('/category/epg/id=<channel_id>/date=<dates>')
def show_epg_programm(channel_id, dates):
    icon = ''
    if 'icon' in plugin.args:
        icon = unquote(plugin.args['icon'][0])
    setContent(plugin.handle, 'tvshows')
    result = get_url(ids.api_epg_url + ids.api_epg_from_to.format(channelId=channel_id, start=dates+'T00:00', to=dates+'T23:59'), headers = ids.api_headers)
    if result:
        programs = json.loads(result)
        for program in programs['response']['data']:
            startTIMES = ''
            startDATE = date.today()
            endTIMES = ''
            endDATE = startDATE
            goDATE = None
            name = ''
            if 'startTime' in program and program['startTime'] != None:
                try:
                    local_tz = tzlocal.get_localzone()
                    startDATE = datetime(1970, 1, 1) + timedelta(seconds=program['startTime'])
                    startDATE = pytz.utc.localize(startDATE)
                    startDATE = startDATE.astimezone(local_tz)
                    goDATE =  startDATE.strftime('%d.%m.%Y')
                    startTIMES = startDATE.strftime('%H:%M')
                except: pass

            if 'endTime' in program and program['endTime'] != None:
                try:
                    local_tz = tzlocal.get_localzone()
                    endDATE = datetime(1970, 1, 1) + timedelta(seconds=program['endTime'])
                    endDATE = pytz.utc.localize(endDATE)
                    endDATE = endDATE.astimezone(local_tz)
                    endTIMES = endDATE.strftime('%H:%M')
                except: pass
            
            if 'title' in program and program['title'] != None:
                if '\n' in program['title']:
                    name = program['title'].replace('\n', ': ')
                else:
                    name = program['title']
            elif 'tvShow' in program and program['tvShow'] != None and 'title' in program['tvShow'] and program['tvShow']['title'] != None:
                name = program['tvShow']['title']
            
            description = ''
            if 'description' in program and program['description'] != None:
                description = program['description']
            tvShow = ''
            if 'tvShow' in program and program['tvShow'] != None and 'title' in program['tvShow'] and program['tvShow']['title'] != None:
                tvShow = program['tvShow']['title']
                if name != tvShow:
                    name = tvShow + ': ' + name

            listitem = ListItem('[COLOR chartreuse]'+startTIMES+': [/COLOR]'+name)
            listitem.setInfo(type='Video', infoLabels={'Title': name,
                'Plot': kodiutils.get_string(32016).format(goDATE, startTIMES, endTIMES) + description,
                'mediatype': 'video', 'TvShowTitle': tvShow, 'Date': goDATE,
                'Duration': (endDATE-startDATE).total_seconds()})
            if 'images' in program and program['images'] != None and len(program['images']) > 0:
                image = ids.api_image_url.format(program['images'][0]['url'])
                listitem.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': image})
            else:
                listitem.setArt({'icon': unquote(icon), 'thumb': unquote(icon), 'poster': unquote(icon), 'fanart': unquote(icon)})
            addDirectoryItem(plugin.handle, url=plugin.url_for(show_info), listitem=listitem)
    endOfDirectory(plugin.handle)

@plugin.route('/category/mediathek/popular')
def show_mediathek_popular():
    add_tvshows('', sub_page = ids.api_popular_url, limit = 100)
    endOfDirectory(plugin.handle)

@plugin.route('/category/mediathek/genre')
def show_mediathek_genre():
    addDirectoryItem(plugin.handle, url=plugin.url_for(
        show_category, 'genres'), listitem=ListItem(kodiutils.get_string(32037)), isFolder=True)
    overview = get_url(ids.overview_url)
    if overview:
        overview = json.loads(overview)
        for element in overview:
            if 'name' not in element or element['name'] != 'Mediathek':
                continue
            if 'ui_components' in element:
                for ui in element['ui_components']:
                    if 'data' in ui and ui['data'] != None and 'source' in ui['data'] and ui['data']['source'] != None:
                        query_source = get_query(ui['data']['source'])
                        if 'url' in query_source:
                            query = get_query(base64.b64decode(query_source['url'][0]).decode('WINDOWS-1252').encode('UTF-8'))
                            if not 'genres' in query:
                                continue
                            if 'type' in query:
                                query.pop('type', None)
                            addDirectoryItem(plugin.handle, url=plugin.url_for(
                                show_a_z, urlencode(query, doseq=True)), listitem=ListItem(query['title'][0]), isFolder=True)
    endOfDirectory(plugin.handle)

@plugin.route('/category/mediathek/channel')
def show_mediathek_channel():
    overview = get_url(ids.overview_url)
    if overview:
        overview = json.loads(overview)
        for element in overview:
            if 'name' not in element or element['name'] != 'Mediathek':
                continue
            if 'ui_components' in element:
                for ui in element['ui_components']:
                    if 'data' in ui and ui['data'] != None and 'source' in ui['data'] and ui['data']['source'] != None:
                        query_source = get_query(ui['data']['source'])
                        if 'url' in query_source:
                            query = get_query(base64.b64decode(query_source['url'][0]).decode('WINDOWS-1252').encode('UTF-8'))
                            if not 'channelId' in query:
                                continue
                            icon = get_channel_icon(query['channelId'][0])
                            if 'type' in query:
                                query.pop('type', None)
                            listitem = ListItem(query['title'][0])
                            listitem.setArt({'icon': icon, 'thumb': icon, 'poster': icon})
                            addDirectoryItem(plugin.handle, url=plugin.url_for(
                                show_a_z, urlencode(query, doseq=True)), listitem=listitem, isFolder=True)
    endOfDirectory(plugin.handle)

@plugin.route('/category/mediathek/a-z/query=<query>')
def show_a_z(query):
    setContent(plugin.handle, 'tvshows')
    log(u'show_a_z with: {0}'.format(query))
    addDirectoryItem(plugin.handle, url=plugin.url_for(
        show_tvshows, query, '', False, ids.api_limit), listitem=ListItem('A-Z'), isFolder=True)
    add_tvshows(query, sub_page=ids.api_popular_url, limit = 100)
    endOfDirectory(plugin.handle)

@plugin.route('/category/search/search=<search>')
def show_search(search):
    setContent(plugin.handle, 'tvshows')
    search = json.loads(search)
    log(u'show_search with: {0}'.format(search))
    if 'type' in search:
        search.pop('type', None)
    for key, value in search.items():
        if value[0] == '':
            if key == 'search':
                value[0] = xbmcgui.Dialog().input(kodiutils.get_string(32001))
            else:
                value[0] = xbmcgui.Dialog().input(key)
    add_tvshows(urlencode(search, doseq=True))
    endOfDirectory(plugin.handle)

@plugin.route('/category/tvshows/query=<path:add_query>/sub=<path:sub_page>/channel=<show_channel>/limit=<limit>')
def show_tvshows(add_query, sub_page='', show_channel=False, limit = ids.api_limit):
    add_tvshows(add_query, sub_page, show_channel, limit)
    endOfDirectory(plugin.handle)
    
def add_tvshows(add_query, sub_page = '', show_channel = False, limit = ids.api_limit):
    setContent(plugin.handle, 'tvshows')
    result = get_url(ids.api_tvshows_url + sub_page + ids.api_tvshows_query + str(limit) + '&' + add_query, headers = ids.api_headers)
    if result:
        tvshows = json.loads(result)
        if len(tvshows['response']['data']) == ids.api_limit and kodiutils.get_setting_as_bool('limit_warning'):
            kodiutils.notification(kodiutils.get_string(32038), kodiutils.get_string(32039))
        for tvshow in tvshows['response']['data']:
            if show_channel == True:
                listitem = ListItem(tvshow['titles']['default']+' | '+tvshow['brand'])
            else:
                listitem = ListItem(tvshow['titles']['default'])
            icon = ''
            thumb = ''
            fanart = ''
            poster = ''
            no_image = True
            other_image = ''
            for image in tvshow['images']:
                if image['subType'] == 'Teaser':
                    icon = ids.api_image_url.format(image['url'])
                    thumb = icon
                    poster = icon
                    no_image = False
                elif image['subType'] == 'Cover Big':
                    fanart = ids.api_image_url.format(image['url'])
                else:
                    other_image = ids.api_image_url.format(image['url'])
            if no_image:
                icon = other_image
                thumb = other_image
                poster = other_image
                fanart = other_image
            listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': poster, 'fanart' : fanart})
            
            plot = ''
            log(tvshow['titles']['default'])
            html = html2text.HTML2Text()
            html.body_width  = 0
            if 'descriptions' in tvshow and tvshow['descriptions']['default'] and tvshow['descriptions']['default'] != None:
                plot = html.handle(tvshow['descriptions']['default'])
            elif 'metaDescriptions' in tvshow and tvshow['metaDescriptions']['default'] and tvshow['metaDescriptions']['default'] != None:
                plot = tvshow['metaDescriptions']['default']
            elif 'shortDescriptions' in tvshow and tvshow['shortDescriptions']['default'] and tvshow['shortDescriptions']['default'] != None:
                plot = tvshow['shortDescriptions']['default']
            
            listitem.setInfo(type='Video', infoLabels={'Title': tvshow['titles']['default'], 'Plot': plot,'mediatype': 'episode'})
            
            add_favorites_context_menu(listitem, plugin.url_for(show_tvshow, tvshow['id']), tvshow['titles']['default'], icon, fanart)
            addDirectoryItem(plugin.handle, url=plugin.url_for(show_tvshow, tvshow['id']),
                listitem=listitem, isFolder=True)


@plugin.route('/category/tvshow/id=<id>')
def show_tvshow(id):
    setContent(plugin.handle, 'tvshows')
    icon = ''
    thumb = ''
    fanart = ''
    poster = ''
    title = ''
    result = get_url(ids.api_tvshows_url + ids.api_tvshows_query + '1' + '&' + ids.api_tvshows_tvshow_query.format(id=id), headers = ids.api_headers)
    if result:
        tvshow = json.loads(result)['response']['data']
        if len(tvshow) > 0:
            title = tvshow[0]['titles']['default']
            no_image = True
            other_image = ''
            for image in tvshow[0]['images']:
                if image['subType'] == 'Teaser':
                    icon = ids.api_image_url.format(image['url'])
                    thumb = icon
                    poster = icon
                    no_image = False
                elif image['subType'] == 'Cover Big':
                    fanart = ids.api_image_url.format(image['url'])
                else:
                    other_image = ids.api_image_url.format(image['url'])
            if no_image:
                icon = other_image
                thumb = other_image
                poster = other_image
                fanart = other_image
    
    for typeurl in [(kodiutils.get_string(32030), ids.api_videos_episode_url), (kodiutils.get_string(32031), ids.api_videos_clip_url), (kodiutils.get_string(32032), ids.api_videos_bonus_url), (kodiutils.get_string(32033), ids.api_videos_vorschau_url)]:
        result = get_url(ids.api_videos_url + ids.api_videos_query.format(id=id) + typeurl[1], headers = ids.api_headers)
        if result:
            videos = json.loads(result)
            if len(videos['response']['data']) > 0:
                listitem = ListItem(typeurl[0])
                listitem.setArt({'icon': icon,'thumb': thumb, 'poster': poster, 'fanart': fanart})
                addDirectoryItem(plugin.handle, url=plugin.url_for(show_tvshow_videos, id, typeurl[1]), listitem=listitem, isFolder=True)
    add_favorites_folder(plugin.url_for(show_tvshow, id), title, icon, fanart)
    endOfDirectory(plugin.handle)

@plugin.route('/category/tvshow/id=<id>/videos/category=<category_query>')
def show_tvshow_videos(id, category_query):
    setContent(plugin.handle, 'tvshows')
    if kodiutils.get_setting('sort') == '1':
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_DURATION)
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_EPISODE)
    result = get_url(ids.api_videos_url + ids.api_videos_query.format(id=id) + category_query, headers = ids.api_headers)
    if result:
        videos = json.loads(result)
        if len(videos['response']['data']) == ids.api_limit:
            kodiutils.notification(kodiutils.get_string(32038), kodiutils.get_string(32039))
        for video in videos['response']['data']:
            airDATE = None
            airTIMES = u''
            endTIMES = u''
            Note_1 = u''
            Note_2 = u''
            if u'metaDescriptions' in video['episode'] and video['episode']['metaDescriptions']['default'] and video['episode']['metaDescriptions']['default'] != None:
                Note_2 = video['episode']['metaDescriptions']['default']
            elif u'descriptions' in video:
                Note_2 = video['descriptions']['default']
            if not Note_2:
                Note_2 = u''
            
            if 'copyright' in video and video['copyright'] != None:
                Note_2 += u'[CR][CR]©' + video['copyright']
            
            cast = []
            director = []
            
            for person in video['credits']:
                if person['role'] == 'director':
                    director.append(person['name'])
                else:
                    cast.append(person['name'])
                    
            log(cast)
            log(director)
            if 'airdates' in video['episode'] and video['episode']['airdates'] != None and len(video['episode']['airdates']) > 0 and video['episode']['airdates'][0]['date'] != 0:
                try:
                    local_tz = tzlocal.get_localzone()
                    airDATES = datetime(1970, 1, 1) + timedelta(seconds=video['episode']['airdates'][0]['date'])
                    airDATES = pytz.utc.localize(airDATES)
                    airDATES = airDATES.astimezone(local_tz)
                    airTIMES = airDATES.strftime('%d.%m.%Y - %H:%M')
                    airDATE = airDATES.strftime('%d.%m.%Y')
                except: pass
            if 'visibilities' in video and video['visibilities'] != None and len(video['visibilities']) > 0 and video['visibilities'][0]['endsAt'] != None:
                try:
                    local_tz = tzlocal.get_localzone()
                    endDATES = datetime(1970, 1, 1) + timedelta(seconds=video['visibilities'][0]['endsAt'])
                    endDATES = pytz.utc.localize(endDATES)
                    endDATES = endDATES.astimezone(local_tz)
                    endTIMES = endDATES.strftime('%d.%m.%Y - %H:%M')
                except: pass
            if airTIMES != u'': Note_1 = kodiutils.get_string(32005).format(str(airTIMES))
            if endTIMES != u'': Note_1 += kodiutils.get_string(32029).format(str(endTIMES))
            if Note_1 != '': Note_1 += '[CR]'
            if airDATE and kodiutils.get_setting('sort') == '1': xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_DATE)
            
            season = -1
            episode = -1
            if 'episode' in video  and 'number' in video['episode'] and video['episode']['number'] != None:
                episode = video['episode']['number']
            if 'season' in video and 'number' in video['season'] and video['season']['number'] != None:
                season = video['season']['number']
            elif video['titles']['default'].lower().find('staffel') > -1 or video['titles']['default'].lower().find('episode') > -1 or video['titles']['default'].lower().find('folge') > -1:
                try: season = re.search('Staffel\s*(\d+)', video['titles']['default']).group(1)
                except: pass
                try: episode = re.search('Episode\s*(\d+)', video['titles']['default']).group(1)
                except:
                    try: episode = re.search('Folge\s*(\d+)', video['titles']['default']).group(1)
                    except: pass
            if not kodiutils.get_setting_as_bool('keep_episode_number') and (video['titles']['default'].lower().find('staffel') > -1 or video['titles']['default'].lower().find('episode') > -1 or video['titles']['default'].lower().find('folge') > -1):
                try: video['cleantitle'] = re.search(':\s*(.*)', video['titles']['default']).group(1)
                except: pass
            if season != -1 or episode != -1:
                video['mediatype'] = 'episode'
            
            log('Title: '+video['titles']['default'])
            listitem = ListItem(video['titles']['default'])
            
            if len(video['images']) > 0:
                icon = ids.api_image_url.format(video['images'][0]['url'])
                listitem.setArt({'icon': icon, 'thumb': icon, 'fanart': icon, 'poster': icon})
            listitem.setProperty('IsPlayable', 'true')
            listitem.setInfo(type='Video', infoLabels={'Title': video.get('cleantitle', video['titles']['default']), 'Plot': Note_1+Note_2, 'TvShowTitle': video['tvShow']['titles']['default'], 'Season': season, 'episode': episode, 'Duration': video['duration']/1000, 'Date': airDATE, 'cast': cast, 'director': director, 'mediatype': video.get('mediatype', 'movie')})
            listitem.addContextMenuItems([('Queue', 'Action(Queue)')])
            addDirectoryItem(plugin.handle, url=plugin.url_for(play_video, video['id'], ''), listitem=listitem)
    endOfDirectory(plugin.handle)
    

@plugin.route('/category/livestream/<livestream_id>')
def play_livestream(livestream_id):
    config_url = ids.get_livestream_config_url(livestream_id)
    config = json.loads(get_url(config_url, cache=True, critical=True))
    mdslive = config['mdsclient']['mdsLive']
    client_token = get_livestream_client_token(access_token=mdslive['accessToken'], client_location=mdslive['clientLocation'], salt=mdslive['salt'], property_name=ids.get_livestream_channel_id(livestream_id))
    protocols_url = mdslive['baseUrl']+'live/1.0/getprotocols?access_token='+mdslive['accessToken']+'&client_location='+mdslive['clientLocation']+'&client_token='+client_token+'&property_name='+ids.get_livestream_channel_id(livestream_id)
    resp_prot = get_url(protocols_url, critical=True)
    protocols = json.loads(resp_prot)

    if LooseVersion('18.0') > LooseVersion(xbmc.getInfoLabel('System.BuildVersion')):
        log('version is: ' + xbmc.getInfoLabel('System.BuildVersion'))
        kodiutils.notification('ERROR', kodiutils.get_string(32025))
        setResolvedUrl(plugin.handle, False, ListItem('none'))
        return

    protocol = ''
    drm = ''
    if kodiutils.get_setting('drm') == '0':
        protocol = 'dash:widevine'
        drm_name = 'widevine'
        drm = 'com.widevine.alpha'
    else:
        protocol = 'dash:playready'
        drm_name = 'playready'
        drm = 'com.microsoft.playready'
    log('drm: '+drm)

    client_server_token = get_livestream_server_client_token(access_token=mdslive['accessToken'], client_location=mdslive['clientLocation'], salt=mdslive['salt'], property_name=ids.get_livestream_channel_id(livestream_id), protocols=protocol, server_token=protocols['server_token'])
    urls_url = mdslive['baseUrl']+'live/1.0/geturls?access_token='+mdslive['accessToken']+'&client_location='+mdslive['clientLocation']+'&client_token='+client_server_token+'&property_name='+ids.get_livestream_channel_id(livestream_id)+'&protocols='+protocol+'&secure_delivery=true'+'&server_token='+protocols['server_token']
    resp_url = get_url(urls_url, critical=True)
    urls = json.loads(resp_url)
    log('Available formats: ' + str(urls))

    playitem = ListItem('none')
    is_helper = None
    try:
        is_helper = inputstreamhelper.Helper('mpd', drm=drm)
    except Exception as e:
        if str(e) == 'UnsupportedDRMScheme' and drm == 'com.microsoft.playready':
            is_helper = inputstreamhelper.Helper('mpd', drm=None)
            pass
        else:
            kodiutils.notification('ERROR', kodiutils.get_string(32018).format(drm))
    #check for inputstream_addon
    inputstream_installed = False
    if is_helper:
        inputstream_installed = is_helper._has_inputstream()

    if is_helper and not inputstream_installed:
        # ask to install inputstream
        xbmc.executebuiltin('InstallAddon({})'.format(is_helper.inputstream_addon), True)
        inputstream_installed = is_helper._has_inputstream()

    if is_helper and inputstream_installed and is_helper.check_inputstream():
        version = xbmcaddon.Addon('inputstream.adaptive').getAddonInfo('version')
        if LooseVersion(version) < LooseVersion('2.2.2'):
            # inputstream to old cannot play mpd
            xbmcgui.Dialog().ok(heading=kodiutils.get_string(32023), line1=kodiutils.get_string(32024))
            setResolvedUrl(plugin.handle, False, ListItem(label='none'))
        else:
            playitem = ListItem(label=xbmc.getInfoLabel('Container.ShowTitle'), path=urls['urls']['dash'][drm_name]['url']+'|User-Agent=vvs-native-android/1.0.10 (Linux;Android 7.1.1) ExoPlayerLib/2.8.1')
            playitem.setProperty('inputstreamaddon', is_helper.inputstream_addon)
            playitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
            playitem.setProperty('inputstream.adaptive.license_type', drm)
            playitem.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
            playitem.setProperty('inputstream.adaptive.license_key', urls['urls']['dash'][drm_name]['drm']['licenseAcquisitionUrl'] + '?token=' + urls['urls']['dash'][drm_name]['drm']['token'] +'|User-Agent=vvs-native-android/1.0.10 (Linux;Android 7.1.1) ExoPlayerLib/2.8.1' +'|R{SSM}|')
            setResolvedUrl(plugin.handle, True, playitem)
    else:
        kodiutils.notification('ERROR', kodiutils.get_string(32019).format(drm))
        setResolvedUrl(plugin.handle, False, playitem)
    #xbmc.Player().play(item=urls['urls']['dash']['widevine']['url'], listitem=playitem)
    
@plugin.route('/category/video/<video_id>')
@plugin.route('/category/video/<video_id>/<channel>')
def play_video(video_id, channel=''):
    # remove channel number if available
    if '_' in video_id:
        video_id = video_id.split('_')[1]
    config_url = ''
    if channel == 'All Channels Feed' or channel == '':
        # no channel info guess by id
        if not video_id.isdigit():
            #probalby a video from puls4 or atv
            config_url = ids.get_livestream_config_url('puls4_and_atv_at')
        else:
            config_url = ids.get_livestream_config_url('austrian_tv')
    else:
        if channel == 'PULS 4' or channel == 'ATV':
            config_url = ids.get_livestream_config_url('puls4_and_atv_at')
        else:
            config_url = ids.get_livestream_config_url('austrian_tv')
    config = json.loads(get_url(config_url, cache=True, critical=True))
    mdsV2 = config['mdsclient']['mdsV2']
    sources_request_url = mdsV2['baseUrl']+'vas/live/v2/videos?access_token=%s&client_location=null&client_name=%s&ids=%s' % (mdsV2['accessToken'], mdsV2['clientName'], video_id)
    sources_request = json.loads(get_url(sources_request_url, critical=True))
    log('sources_request: ' + str(sources_request))
    protected = sources_request[0]['is_protected']
    mpd_id = 0
    m3u8_id = 0
    ism_id = 0
    mp4_id = 0
    protocol = ''
    for source in sources_request[0]['sources']:
        if source['mimetype'] == 'text/xml':
            ism_id = source['id']
        if source['mimetype'] == 'application/x-mpegURL':
            m3u8_id = source['id']
        if source['mimetype'] == 'application/dash+xml':
            mpd_id = source['id']
        if source['mimetype'] == 'video/mp4':
            mp4_id = source['id']
    drm = None
    if not protected:
        if kodiutils.get_setting_as_int('non_drm_format') == 0:
            source_id = mpd_id
            protocol = 'mpd'
        elif kodiutils.get_setting_as_int('non_drm_format') == 3:
            source_id = mp4_id
            protocol = 'mp4'
        else:
            source_id = m3u8_id
            protocol = 'hls'
    else:
        if kodiutils.get_setting('drm') == '0':
            source_id = mpd_id
            protocol = 'mpd'
            drm_name = 'widevine'
            drm = 'com.widevine.alpha'
        else:
            source_id = ism_id
            protocol = 'ism'
            drm_name = 'playready'
            drm = 'com.microsoft.playready'

    if protected and LooseVersion('18.0') > LooseVersion(xbmc.getInfoLabel('System.BuildVersion')):
        log('version is: ' + xbmc.getInfoLabel('System.BuildVersion'))
        kodiutils.notification('ERROR', kodiutils.get_string(32025))
        setResolvedUrl(plugin.handle, False, ListItem('none'))
        return

    server_request_token = get_video_server_request_token(access_token=mdsV2['accessToken'], client_location='null', client_name=mdsV2['clientName'], video_id=video_id, salt=mdsV2['salt'])
    server_request_url = mdsV2['baseUrl']+'vas/live/v2/videos/%s/sources?access_token=%s&client_id=%s&client_location=null&client_name=%s' % (video_id, mdsV2['accessToken'], server_request_token, mdsV2['clientName'])
    server_request = json.loads(get_url(server_request_url, critical=True))
    server_id = server_request['server_id']

    start = ''
    end = ''
    if protected and kodiutils.get_setting('drm') == '0' and kodiutils.get_setting_as_bool('oldformat'):
        start = '0'
        end = '999999999'

    source_url_request_token = get_video_source_request_token(access_token=mdsV2['accessToken'], client_location='null', client_name=mdsV2['clientName'], server_id= server_id, source_id=source_id, video_id=video_id, salt=mdsV2['salt'], start=start, end=end)
    source_url_request_url = mdsV2['baseUrl']+'vas/live/v2/videos/%s/sources/url?access_token=%s&client_id=%s&client_location=null&client_name=%s&secure_delivery=true&server_id=%s&source_ids=%s' % (video_id, mdsV2['accessToken'], source_url_request_token, mdsV2['clientName'], server_id, source_id)

    if protected and kodiutils.get_setting('drm') == '0'and kodiutils.get_setting_as_bool('oldformat'):
        source_url_request_url += '&subclip_start=0&subclip_end=999999999'

    source_url_request = json.loads(get_url(source_url_request_url, critical=True))
    if not 'status_code' in source_url_request or source_url_request['status_code'] != 0:
        log('error on video request: ' + str(source_url_request))
        return sys.exit(0)

    playitem = ListItem('none')
    log('selected non drm format: ' + kodiutils.get_setting('non_drm_format'))
    log('media url: ' + source_url_request['sources'][0]['url'])
    if not protected and (kodiutils.get_setting_as_int('non_drm_format') == 2 or kodiutils.get_setting_as_int('non_drm_format') == 3):
        playitem = ListItem(label=xbmc.getInfoLabel('Container.ShowTitle'), path=source_url_request['sources'][0]['url']+'|User-Agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36')
        setResolvedUrl(plugin.handle, True, playitem)
    else:
        is_helper = None
        try:
            is_helper = inputstreamhelper.Helper(protocol, drm=drm)
        except Exception as e:
            if str(e) == 'UnsupportedDRMScheme' and drm == 'com.microsoft.playready':
                is_helper = inputstreamhelper.Helper(protocol, drm=None)
                pass
            else:
                kodiutils.notification('ERROR', kodiutils.get_string(32018).format(drm))
        #check for inputstream_addon
        inputstream_installed = False
        if is_helper:
            inputstream_installed = is_helper._has_inputstream()

        if is_helper and not inputstream_installed:
            # ask to install inputstream
            xbmc.executebuiltin('InstallAddon({})'.format(is_helper.inputstream_addon), True)
            inputstream_installed = is_helper._has_inputstream()

        if is_helper and inputstream_installed and is_helper.check_inputstream():
            version = xbmcaddon.Addon('inputstream.adaptive').getAddonInfo('version')
            if not protected and kodiutils.get_setting_as_int('non_drm_format') == 0 and LooseVersion(version) < LooseVersion('2.2.2'):
                # inputstream to old cannot play mpd
                # switch to hls
                kodiutils.set_setting('non_drm_format', 1)
                play_video(video_id, channel)
            elif protected and LooseVersion(version) < LooseVersion('2.2.2'):
                # inputstream to old cannot play mpd
                xbmcgui.Dialog().ok(heading=kodiutils.get_string(32023), line1=kodiutils.get_string(32024))
                setResolvedUrl(plugin.handle, False, ListItem(label='none'))
            else:
                playitem = ListItem(label=xbmc.getInfoLabel('Container.ShowTitle'), path=source_url_request['sources'][0]['url']+'|User-Agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36')
                playitem.setProperty('inputstreamaddon', is_helper.inputstream_addon)
                playitem.setProperty('inputstream.adaptive.manifest_type', protocol)
                if protected:
                    playitem.setProperty('inputstream.adaptive.license_type', drm)
                    playitem.setProperty('inputstream.adaptive.license_key', source_url_request['drm']['licenseAcquisitionUrl'] + '?token=' + source_url_request['drm']['token'] +'|User-Agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36' +'|R{SSM}|')
                setResolvedUrl(plugin.handle, True, playitem)
        else:
            if drm:
                kodiutils.notification('ERROR', kodiutils.get_string(32019).format(drm))
                setResolvedUrl(plugin.handle, False, playitem)
            else:
                if xbmcgui.Dialog().yesno(heading=kodiutils.get_string(32020), line1=kodiutils.get_string(32021), line2=kodiutils.get_string(32022).format(kodiutils.get_string(32110))):
                    if LooseVersion('18.0') > LooseVersion(xbmc.getInfoLabel('System.BuildVersion')):
                        kodiutils.set_setting('non_drm_format', 3)
                    else:
                        kodiutils.set_setting('non_drm_format', 2)
                    play_video(video_id, channel)
                else:
                    setResolvedUrl(plugin.handle, False, playitem)

def utc_to_local(dt):
    if time.localtime().tm_isdst: return dt - timedelta(seconds=time.altzone)
    else: return dt - timedelta(seconds=time.timezone)

def add_favorites_folder(path, name, icon, fanart):
    global favorites
    if not favorites and xbmcvfs.exists(favorites_file_path):
        favorites_file = xbmcvfs.File(favorites_file_path)
        favorites = json.load(favorites_file)
        favorites_file.close()

    if not favorites or path not in favorites:
        # add favorites folder
        #addDirectoryItem(plugin.handle, url=plugin.url_for(add_favorite, query='%s***%s###%s###%s' % (path, name, icon, fanart)), listitem=ListItem(kodiutils.get_string(32004)))
        listitem = ListItem(kodiutils.get_string(32008))
        listitem.setArt({'icon': icon,'thumb': icon, 'poster': icon, 'fanart': fanart})
        addDirectoryItem(plugin.handle, url=plugin.url_for(add_favorite, path=quote(codecs.encode(path, 'UTF-8')), name=quote(codecs.encode(name, 'UTF-8')), icon=quote(codecs.encode(icon, 'UTF-8')), fanart=quote(codecs.encode(fanart, 'UTF-8'))), listitem=listitem)
    else:
        # remove favorites
        listitem = ListItem(kodiutils.get_string(32009))
        listitem.setArt({'icon': icon,'thumb': icon, 'poster': icon, 'fanart': fanart})
        addDirectoryItem(plugin.handle, url=plugin.url_for(remove_favorite, query=quote(codecs.encode(path, 'UTF-8'))),
            listitem=listitem)

def add_favorites_context_menu(listitem, path, name, icon, fanart):
    global favorites
    if not favorites and xbmcvfs.exists(favorites_file_path):
        favorites_file = xbmcvfs.File(favorites_file_path)
        favorites = json.load(favorites_file)
        favorites_file.close()

    if not favorites or path not in favorites:
        # add favorites
        listitem.addContextMenuItems([(kodiutils.get_string(32008), 'RunScript('+ADDON.getAddonInfo('id')+
            ',add,' + quote(codecs.encode(path, 'UTF-8')) + ',' + quote(codecs.encode(name, 'UTF-8')) +
            ',' + quote(codecs.encode(icon, 'UTF-8')) + ',' + quote(codecs.encode(fanart, 'UTF-8')) + ')')])
    else:
        # remove favorites
        listitem.addContextMenuItems([(kodiutils.get_string(32009), 'RunScript('+ADDON.getAddonInfo('id') + ',remove,'+ quote(codecs.encode(path, 'UTF-8'))+')')])
    return listitem

@plugin.route('/add_fav')
def add_favorite():
    #data = plugin.args['query'][0].split('***')
    path = plugin.args['path'][0]
    name = plugin.args['name'][0]
    icon = ''
    if 'icon' in plugin.args:
        icon = plugin.args['icon'][0]
    fanart = ''
    if 'fanart' in plugin.args:
        fanart = plugin.args['fanart'][0]
        
    if sys.version_info[0] < 3:
        # decode utf-8
        path = path.encode('ascii')
        name = name.encode('ascii')
        icon = icon.encode('ascii')
        fanart = fanart.encode('ascii')
    
    path = unquote(path)
    name = unquote(name)
    icon = unquote(icon)
    fanart = unquote(fanart)
    
    if sys.version_info[0] < 3:
        # decode utf-8
        path = path.decode('utf-8')
        name = name.decode('utf-8')
        icon = icon.decode('utf-8')
        fanart = fanart.decode('utf-8')
    
    # load favorites
    global favorites
    if not favorites and xbmcvfs.exists(favorites_file_path):
        favorites_file = xbmcvfs.File(favorites_file_path)
        favorites = json.load(favorites_file)
        favorites_file.close()

    #favorites.update({data[0] : data[1]})
    favorites.update({path : {'name' : name, 'icon' : icon, 'fanart' : fanart}})
    # load favorites
    favorites_file = xbmcvfs.File(favorites_file_path, 'w')
    json.dump(favorites, favorites_file, indent=2)
    favorites_file.close()

    
    kodiutils.notification(kodiutils.get_string(32010), kodiutils.get_string(32011).format(name))
    xbmc.executebuiltin('Container.Refresh')
    setResolvedUrl(plugin.handle, True, ListItem('none'))

@plugin.route('/remove_fav')
def remove_favorite():
    data = unquote(plugin.args['query'][0])
    # load favorites
    global favorites
    if not favorites and xbmcvfs.exists(favorites_file_path):
        favorites_file = xbmcvfs.File(favorites_file_path)
        favorites = json.load(favorites_file)
        favorites_file.close()

    name = favorites[data]['name']
    del favorites[data]
    # load favorites
    favorites_file = xbmcvfs.File(favorites_file_path, 'w')
    json.dump(favorites, favorites_file, indent=2)
    favorites_file.close()

    kodiutils.notification(kodiutils.get_string(32010), kodiutils.get_string(32012).format(name))
    xbmc.executebuiltin('Container.Refresh')
    setResolvedUrl(plugin.handle, True, ListItem('none'))

def get_url(url, headers={}, cache=False, critical=False):
    log(url)
    new_headers = {}
    new_headers.update(headers)
    if cache == True:
        cache_tag = ids.get_livestream_config_tag(url)
        if cache_tag != None:
            new_headers.update({'If-None-Match': cache_tag})
    new_headers.update({'User-Agent':'okhttp/3.12.1', 'Accept-Encoding':'gzip'})
    try:
        request = urlopen(Request(url, headers=new_headers))
    except HTTPError as e:
        if cache and e.code == 304:
            return ids.get_livestream_config_cache(url)
        failure = str(e)
        if hasattr(e, 'code'):
            log('(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########'.format(url, failure))
        elif hasattr(e, 'reason'):
            log('(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########'.format(url, failure))
        if critical:
            kodiutils.notification('ERROR GETTING URL', failure)
            return sys.exit(0)
        else:
            return ''
    except URLError as e:
        kodiutils.notification('ERROR GETTING URL', str(e))
        if critical:
            return sys.exit(0)
        else:
            return ''

    if request.info().get('Content-Encoding') == 'gzip':
        # decompress content
        buffer = StringIO(request.read())
        deflatedContent = gzip.GzipFile(fileobj=buffer)
        data = deflatedContent.read()
    else:
        data = request.read()

    if cache:
        data = xxtea.decryptBase64StringToStringss(data, ids.xxtea_key)
        ids.set_livestream_config_cache(url, data, request.info().get('ETag'))
    return data

def get_livestream_client_token(access_token='', client_location='', salt='', property_name=''):
    token = property_name + salt + access_token + client_location
    return '01'+hashlib.sha1(token.encode('UTF-8')).hexdigest()

def get_livestream_server_client_token(access_token='', client_location='', salt='', property_name='', protocols='', server_token=''):
    token = property_name + salt + access_token + server_token + client_location + protocols
    return '01'+hashlib.sha1(token.encode('UTF-8')).hexdigest()

def get_video_server_request_token(access_token='', client_location='', client_name='', video_id=0, salt=''):
    token = str(video_id) + salt + access_token + client_location + salt + client_name
    return '01'+hashlib.sha1(token.encode('UTF-8')).hexdigest()

def get_video_source_request_token(access_token='', client_location='', client_name='', server_id='', source_id=0, video_id=0, salt='', start='', end=''):
    token = salt + str(video_id) + access_token + server_id + client_location + str(source_id) + salt + client_name + start + end
    return '01'+hashlib.sha1(token.encode('UTF-8')).hexdigest()

def get_listitem(name='', icon='', fanart=''):
    listitem = ListItem(name)
    listitem.setProperty('IsPlayable', 'true')
    listitem.setInfo(type='Video', infoLabels={'mediatype': 'video'})
    if icon != '':
        listitem.setArt({'icon':icon, 'thumb':icon, 'poster':icon})
    if fanart != '':
        listitem.setArt({'fanart':fanart})
    return listitem

def get_channel(json_data, channel):
    if json_data:
        for channels in json_data['account']['channels']:
            if channels['ui_tag'] == channel:
                return channels
    return {}

def get_query(url):
    #log(u'{0}'.format(url))
    source = urlparse(url)
    log(u'{0}'.format(source))
    return parse_qs(source[4], keep_blank_values=True)

def get_channel_icon(channelId):
    result = get_url(ids.channel_icon_url.format(channelId = channelId), headers=ids.api_headers)
    icon = ''
    if result:
        result = json.loads(result)
        try:
            icon = result['png']['tv']['1']
        except:
            icon = result['png']['default']['1']
    return icon

def get_livestream(channelId, title, id):
    listitem =ListItem(title)
    listitem.setProperty('IsPlayable', 'true')
    icon = get_channel_icon(channelId)
    listitem.setArt({'icon': icon, 'thumb': icon, 'poster': icon})
    
    result = get_url(ids.api_epg_url + ids.api_epg_from.format(channelId = channelId, start = datetime.now().strftime('%Y-%m-%dT%H:%M:%S%z')), headers=ids.api_headers)
    
    if result:
        epg = json.loads(result)
        if len(epg['response']['data']) > 0:
            #'Title': channel['name']
            next = epg['response']['data'][0]
            if 'title' in next and next['title'] != None:
                if '\n' in next['title']:
                    name = next['title'].replace('\n', ': ')
                else:
                    name = next['title']
            elif 'tvShow' in next and next['tvShow'] != None and 'title' in next['tvShow'] and next['tvShow']['title'] != None:
                name = next['tvShow']['title']
            
            description = ''
            if 'description' in next and next['description'] != None:
                description = next['description']
            tvShow = ''
            if 'tvShow' in next and next['tvShow'] != None and 'title' in next['tvShow'] and next['tvShow']['title'] != None:
                tvShow = next['tvShow']['title']
                if name != tvShow:
                    name = tvShow + ': ' + name
            
            listitem.setInfo(type='Video', infoLabels={'Title': listitem.getLabel(), 'Plot': name + '[CR]'+ description, 'mediatype': 'episode'})
            if 'images' in next and next['images'] != None and len(next['images']) > 1:
                listitem.setArt({'fanart' : ids.api_image_url.format(next['images'][0]['url'])})
        else:
            listitem.setInfo(type='Video', infoLabels={'Title': listitem.getLabel(), 'mediatype': 'video'})
    return (plugin.url_for(play_livestream, id), listitem)

def add_default_streams():
    for stream in ids.default_streams:
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, stream[0]), listitem=get_listitem(stream[1]))
    for stream in ids.streams_pro7sat1:
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, stream[0]+'_at'), listitem=get_listitem(stream[1]+' AT'))

@plugin.route('/category/by_category/id=<id>')
def legacy_category(id):
    result = get_url(ids.legacy_categories_request_url.format(id=id))
    if result:
        data = json.loads(result)
        if 'category' in data and data['category'] != None and 'external_id' in data['category'] and data['category']['external_id'] != None:
            if '_' in data['category']['external_id']:
                data['category']['external_id'] = data['category']['external_id'].split('_')[1]
            addDirectoryItem(plugin.handle, url=plugin.url_for(show_tvshow, id = data['category']['external_id']), listitem=ListItem(kodiutils.get_string(32040)), isFolder=True)
    add_favorites_folder(plugin.url_for(legacy_category, id), '', '', '')
    endOfDirectory(plugin.handle)

def run():
    plugin.run()

def log(info):
    if kodiutils.get_setting_as_bool('debug'):
        logger.warning(info)
