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
from xbmcplugin import addDirectoryItem, endOfDirectory, setResolvedUrl, setContent
from distutils.version import LooseVersion

import codecs

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
    from urllib.error import HTTPError
    from urllib.parse import quote, unquote
except ImportError:
    from urllib import quote, unquote
    from urllib2 import Request, urlopen, HTTPError

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

favorites_file_path = __profile__+"favorites.json"
favorites = {}

icon_path = ADDON.getAddonInfo('path')+"/resources/logos/{0}.png"

setContent(plugin.handle, '')

@plugin.route('/')
def index():
    icon = get_url(ids.collections_request_url.format(id=ids.icon_id, page="1"))
    live_icon = ""
    highlights_icon = ""
    highlights_id = ids.highlights_id
    mediathek_icon = ""
    mediathek_id = ids.mediathek_id
    tv_programm_icon = ""
    tv_programm_id = ids.tv_programm_id
    if icon != "":
        icon_json = json.loads(icon)
        for element in icon_json["results"]:
            if element["promotion_name"] == "Live":
                image_json = json.loads(element["images_json"])
                live_icon = image_json["menu_icon"]
            elif element["promotion_name"] == "Highlights":
                image_json = json.loads(element["images_json"])
                highlights_icon = image_json["menu_icon"]
                highlights_id = element["id"]
            elif element["promotion_name"] == "Mediathek":
                image_json = json.loads(element["images_json"])
                mediathek_icon = image_json["menu_icon"]
                mediathek_id = element["id"]
            elif element["promotion_name"] == "TV Programm":
                image_json = json.loads(element["images_json"])
                tv_programm_icon = image_json["menu_icon"]
    else:
        kodiutils.notification("ERROR getting URL", "using saved values")
    icon_search = get_url(ids.collections_request_url.format(id=ids.search_icon_id, page="1"))
    search_icon = ""
    settings_icon = ""
    if icon_search != "":
        icon_search_json = json.loads(icon_search)
        for item in icon_search_json["results"]:
            images = json.loads(item["images_json"])
            if item["name"] == "Search":
                if "navbar_icon" in images:
                    search_icon = images["navbar_icon"]
            elif item["name"] == "Service":
                if "navbar_icon" in images:
                    settings_icon = images["navbar_icon"]
    else:
        kodiutils.notification("ERROR getting URL", "using saved values")
    addDirectoryItem(plugin.handle, plugin.url_for(
        show_category, "livestream"), ListItem("Live", iconImage=live_icon, thumbnailImage=live_icon), True)
    addDirectoryItem(plugin.handle, plugin.url_for(
        get_by_collection, collection_id=highlights_id, page="1", recursive="True"), ListItem("Highlights", iconImage=highlights_icon, thumbnailImage=highlights_icon), True)
    addDirectoryItem(plugin.handle, plugin.url_for(
        show_mediathek, mediathek_id), ListItem("Mediathek", iconImage=mediathek_icon, thumbnailImage=mediathek_icon), True)
    addDirectoryItem(plugin.handle, plugin.url_for(
        show_category, "tvprogramm"), ListItem("TV Programm", iconImage=tv_programm_icon, thumbnailImage=tv_programm_icon), True)
    addDirectoryItem(plugin.handle, plugin.url_for(
        show_search), ListItem(kodiutils.get_string(32001), iconImage=search_icon, thumbnailImage=search_icon), True)
    addDirectoryItem(plugin.handle, plugin.url_for(
        show_category, "favorites"), ListItem(kodiutils.get_string(32002)), True)
    addDirectoryItem(plugin.handle, plugin.url_for(
        open_settings), ListItem(kodiutils.get_string(32003), iconImage=settings_icon, thumbnailImage=settings_icon))
    endOfDirectory(plugin.handle)

@plugin.route('/settings')
def open_settings():
    kodiutils.show_settings()

@plugin.route('/category/<category_id>')
def show_category(category_id):
    #setContent(plugin.handle, 'albums')
    if category_id == "livestream":
        channels = get_url(ids.overview_url)
        json_data = {}
        if channels != "":
            json_data = json.loads(channels)
        else:
            kodiutils.notification("ERROR GETTING LIVESTREAM INFO", "using saved values")
        # current = ListItem("ORF 1")
        # current.setInfo(type="Video")
        # current.setProperty('IsPlayable', 'true')
        # orf1
        channel = get_channel(json_data, "orf1")
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "orf1"), listitem=get_listitem(name="ORF 1", channel=channel))
        channel = get_channel(json_data, "orf2")
        addDirectoryItem(plugin.handle, plugin.url_for(
            play_livestream, "orf2"), get_listitem(name="ORF 2", channel=channel))
        channel = get_channel(json_data, "Puls4")
        addDirectoryItem(plugin.handle, plugin.url_for(
            play_livestream, "puls4_at"), get_listitem(name="PULS 4", channel=channel, no_puls4=False))
        channel = get_channel(json_data, "Popup")
        addDirectoryItem(plugin.handle, plugin.url_for(
            play_livestream, "popuptv"), get_listitem(name="Puls 24", channel=channel, no_puls4=False))
        channel = get_channel(json_data, "ATV")
        addDirectoryItem(plugin.handle, plugin.url_for(
            play_livestream, "atv"), get_listitem(name="ATV", channel=channel))
        channel = get_channel(json_data, "ATV2")
        addDirectoryItem(plugin.handle, plugin.url_for(
            play_livestream, "atv2"), get_listitem(name="ATV 2", channel=channel))
        channel = get_channel(json_data, "servustv")
        addDirectoryItem(plugin.handle, plugin.url_for(
            play_livestream, "servustv"), get_listitem(name="Servus TV Österreich", channel=channel))
        channel = get_channel(json_data, "schautv")
        addDirectoryItem(plugin.handle, plugin.url_for(
            play_livestream, "schautv"), get_listitem(name="SchauTV", channel=channel))
        channel = get_channel(json_data, "ric")
        addDirectoryItem(plugin.handle, plugin.url_for(
            play_livestream, "ric"), get_listitem(name="RIC", channel=channel))
        channel = get_channel(json_data, "popuptv")
        addDirectoryItem(plugin.handle, plugin.url_for(
            play_livestream, "popuptv2"), get_listitem(name="CineplexxTV", channel=channel))
        addDirectoryItem(plugin.handle, plugin.url_for(
            play_livestream, "kronehittv"), get_listitem(name="Kronehit TV"))
        addDirectoryItem(plugin.handle, plugin.url_for(
            show_category, "austria"), ListItem(kodiutils.get_string(32026)), True)
        addDirectoryItem(plugin.handle, plugin.url_for(
            show_category, "germany"), ListItem(kodiutils.get_string(32027)), True)
        addDirectoryItem(plugin.handle, plugin.url_for(
            show_category, "switzerland"), ListItem(kodiutils.get_string(32028)), True)
    elif category_id == "austria":
        channels = get_url(ids.overview_url)
        json_data = {}
        if channels != "":
            json_data = json.loads(channels)
        else:
            kodiutils.notification("ERROR GETTING LIVESTREAM INFO", "using saved values")
        channel = get_channel(json_data, "kabel eins")
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "kabeleins_at"), listitem=get_listitem(name="Kabel eins AT", channel=channel))
        channel = get_channel(json_data, "Kabel1Doku")
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "kabeleinsdoku_at"), listitem=get_listitem(name="Kabel1Doku AT", channel=channel))
        channel = get_channel(json_data, "ProSieben")
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "prosieben_at"), listitem=get_listitem(name="ProSieben AT", channel=channel))
        channel = get_channel(json_data, "ProSiebenMaxx")
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "prosiebenmaxx_at"), listitem=get_listitem(name="ProSiebenMaxx AT", channel=channel))
        channel = get_channel(json_data, "SAT.1")
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "sat1_at"), listitem=get_listitem(name="SAT.1 AT", channel=channel))
        channel = get_channel(json_data, "SAT.1 Gold")
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "sat1gold_at"), listitem=get_listitem(name="SAT.1 Gold AT", channel=channel))
        channel = get_channel(json_data, "Sixx")
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "sixx_at"), listitem=get_listitem(name="Sixx AT", channel=channel))
    elif category_id == "germany" or category_id == "switzerland":
        if category_id == "germany":
            id = "_de"
            name = " DE"
        else:
            id = "_ch"
            name = " CH"
        listitem = get_listitem(name="Kabel eins"+name)
        listitem.setArt({'icon': icon_path.format("kabeleins"), 'thumb': icon_path.format("kabeleins"), 'poster': icon_path.format("kabeleins")})
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "kabeleins"+id), listitem=listitem)
        listitem = get_listitem(name="Kabel1Doku"+name)
        listitem.setArt({'icon': icon_path.format("kabeleinsdoku"), 'thumb': icon_path.format("kabeleinsdoku"), 'poster': icon_path.format("kabeleinsdoku")})
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "kabeleinsdoku"+id), listitem=listitem)
        listitem = get_listitem(name="ProSieben"+name)
        listitem.setArt({'icon': icon_path.format("prosieben"), 'thumb': icon_path.format("prosieben"), 'poster': icon_path.format("prosieben")})
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "prosieben"+id), listitem=listitem)
        listitem = get_listitem(name="ProSiebenMaxx"+name)
        listitem.setArt({'icon': icon_path.format("prosiebenmaxx"), 'thumb': icon_path.format("prosiebenmaxx"), 'poster': icon_path.format("prosiebenmaxx")})
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "prosiebenmaxx"+id), listitem=listitem)
        listitem = get_listitem(name="SAT.1"+name)
        listitem.setArt({'icon': icon_path.format("sat1"), 'thumb': icon_path.format("sat1"), 'poster': icon_path.format("sat1")})
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "sat1"+id), listitem=listitem)
        listitem = get_listitem(name="SAT.1 Gold"+name)
        listitem.setArt({'icon': icon_path.format("sat1gold"), 'thumb': icon_path.format("sat1gold"), 'poster': icon_path.format("sat1gold")})
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "sat1gold"+id), listitem=listitem)
        listitem = get_listitem(name="Sixx"+name)
        listitem.setArt({'icon': icon_path.format("sixx"), 'thumb': icon_path.format("sixx"), 'poster': icon_path.format("sixx")})
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "sixx"+id), listitem=listitem)

    elif category_id == "favorites":
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
        global favorites
        if not favorites and xbmcvfs.exists(favorites_file_path):
            favorites_file = xbmcvfs.File(favorites_file_path)
            favorites = json.load(favorites_file)
            favorites_file.close()

        for item in favorites:
            listitem = ListItem(favorites[item]["name"])
            listitem.setArt({'icon': favorites[item]["icon"], 'thumb':favorites[item]["icon"], 'poster':favorites[item]["icon"], 'fanart' : favorites[item]["fanart"]})
            add_favorites_context_menu(listitem, item, favorites[item]['name'], favorites[item]['icon'], favorites[item]['fanart'])
            addDirectoryItem(plugin.handle, url=item,
                listitem=listitem, isFolder=True)
    elif category_id == "tvprogramm":
        channels = get_url(ids.collections_request_url.format(id=ids.epg_id, page = "1"), critical=True)
        channels_json = json.loads(channels)
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
        for channel in channels_json["results"]:
            listitem = ListItem(channel["name"])
            if listitem.getLabel() != "Puls4 TV":
                listitem.setLabel(listitem.getLabel().replace("Puls4 ", ""))
            images = json.loads(channel["images_json"])
            icon = ""
            if "image_base" in images and images["image_base"]:
                icon = images["image_base"]
            else:
                icon = images["icon_1"]
            listitem.setArt({'icon': icon, 'thumb': icon, 'poster': icon})
            addDirectoryItem(plugin.handle, url=plugin.url_for(
                show_epg, channel_id=channel["id"], icon=quote(icon)), listitem=listitem, isFolder=True)

    else:
        addDirectoryItem(plugin.handle, "", ListItem(kodiutils.get_string(32004)), False)
    endOfDirectory(plugin.handle)

@plugin.route('/category/epg/id=<channel_id>')
def show_epg(channel_id):
    icon = ""
    if 'icon' in plugin.args:
        icon = plugin.args['icon'][0]
    today = date.today()
    # past epg
    addDirectoryItem(plugin.handle, plugin.url_for(
        show_epg_past, channel_id=channel_id, icon=icon), ListItem(kodiutils.get_string(32014)), True)
    # show epg from today
    addDirectoryItem(plugin.handle, plugin.url_for(
        show_epg_programm, channel_id=channel_id, date=today.strftime("%Y%m%d"), icon=icon),
        ListItem(kodiutils.get_string(32015).format(kodiutils.get_string(32017))), True)
    # future epg
    for i in range(1, 14, 1):
        future_date = today + timedelta(days = i)
        addDirectoryItem(plugin.handle, plugin.url_for(
            show_epg_programm, channel_id=channel_id, date=future_date.strftime("%Y%m%d"), icon=icon),
            ListItem(kodiutils.get_string(32015).format(future_date.strftime("%d.%m.%Y"))), True)
    endOfDirectory(plugin.handle)

@plugin.route('/category/epg/id=<channel_id>/past')
def show_epg_past(channel_id):
    icon = ""
    if 'icon' in plugin.args:
        icon = plugin.args['icon'][0]
    today = date.today()
    # past epg
    for i in range(-1,-60, -1):
        past_date = today + timedelta(days = i)
        #show_epg_programm(channel_id, past_date.strftime("%Y%m%d"), icon)
        addDirectoryItem(plugin.handle, plugin.url_for(
            show_epg_programm, channel_id=channel_id, date=past_date.strftime("%Y%m%d"), icon=icon),
            ListItem(kodiutils.get_string(32015).format(past_date.strftime("%d.%m.%Y"))), True)
    endOfDirectory(plugin.handle)



@plugin.route('/category/epg/id=<channel_id>/date=<date>')
def show_epg_programm(channel_id, date):
    icon = ""
    if 'icon' in plugin.args:
        icon = unquote(plugin.args['icon'][0])
    setContent(plugin.handle, 'tvshows')
    programs = json.loads(get_url(ids.epg_request_url.format(channel_id=channel_id, date=date), critical=True))
    for program in programs["programs"]:
        startDATES = datetime(*(time.strptime(program['starts_at'].split(' +')[0], '%Y/%m/%d %H:%M:%S')[0:6])) # 2019/06/23 14:10:00 +0000
        LOCALstart = utc_to_local(startDATES)
        startTIMES = LOCALstart.strftime('%H:%M')
        goDATE =  LOCALstart.strftime('%d.%m.%Y')

        endDATES = datetime(*(time.strptime(program['ends_at'].split(' +')[0], '%Y/%m/%d %H:%M:%S')[0:6])) # 2019/06/23 14:10:00 +0000
        LOCALend = utc_to_local(endDATES)
        endTIMES = LOCALend.strftime('%H:%M')

        if '\n' in program["name"]:
            name = program["name"].split('\n')[1]
        else:
            name = program["name"]

        listitem = ListItem("[COLOR chartreuse]"+startTIMES+": [/COLOR]"+program["name"].replace("\n", ": "))
        listitem.setInfo(type='Video', infoLabels={'Title': name,
            'Plot': kodiutils.get_string(32016).format(goDATE, startTIMES, endTIMES)+program["description"],
            'mediatype': 'video', 'TvShowTitle': program["name"].split('\n')[0], 'Date': goDATE,
            'Duration': (LOCALend-LOCALstart).total_seconds()})
        images = json.loads(program["images_json"])
        if "image_base" in images:
            listitem.setArt({'icon': images["image_base"], 'thumb': images["image_base"], 'poster': images["image_base"], 'fanart': images["image_base"]})
        else:
            listitem.setArt({'icon': unquote(icon), 'thumb': unquote(icon), 'poster': unquote(icon), 'fanart': unquote(icon)})
        addDirectoryItem(plugin.handle, url=None, listitem=listitem)
    endOfDirectory(plugin.handle)

@plugin.route('/category/mediathek/id=<mediathek_id>')
def show_mediathek(mediathek_id):
    get_by_collection(mediathek_id, "1")
    endOfDirectory(plugin.handle)

@plugin.route('/search')
def show_search():
    query = xbmcgui.Dialog().input(kodiutils.get_string(32001))
    if query != "":
        search_id = ids.search_id
        channels = json.loads(get_url(ids.categories_request_url.format(id=search_id), critical=True))
        shows = {}
        if multiprocess:
            threads = []
            pool = ThreadPool(processes=len(channels["category"]["children"]))
        for channel in channels["category"]["children"]:
            if multiprocess:
                thread = pool.apply_async(search_channel, [channel["id"]])
                thread.name = channel["id"]
                thread.daemon = True
                threads.append(thread)
            else:
                shows.update(search_channel(channel["id"]))
        if multiprocess:
            for thread in threads:
                shows.update(thread.get())
                pool.close()
                pool.join()
        result = {}
        for show in shows.keys():
            if query.lower() in show.lower():
                result.update({show+" | "+shows[show]["top_level_category"]["name"] : shows[show]})
        for show in result:
            icon = ""
            fanart = ""
            if "images_json" in result[show]:
                images = json.loads(result[show]["images_json"])
                if "image_base" in images:
                    icon = images["image_base"]
                if "image_show_big" in images:
                    fanart = images["image_show_big"]
            listitem = ListItem(result[show]["name"]+" | "+result[show]["top_level_category"]["name"])
            listitem.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'fanart' : fanart})
            add_favorites_context_menu(listitem, plugin.url_for(get_by_category, result[show]["id"]), result[show]["name"], icon, fanart)
            addDirectoryItem(plugin.handle, url=plugin.url_for(get_by_category, result[show]["id"]),
                listitem=listitem, isFolder=True)
    endOfDirectory(plugin.handle)

def search_channel(channel_id):
    shows = {}
    channel_shows = json.loads(get_url(ids.categories_request_url.format(id=channel_id), critical=True))
    for show in channel_shows["category"]["children"]:
        shows.update({show["name"]+" | "+show["top_level_category"]["name"] : show})
    return shows

@plugin.route('/category/livestream/<livestream_id>')
def play_livestream(livestream_id):
    config_url = ids.get_livestream_config_url(livestream_id)
    config = json.loads(get_url(config_url, cache=True, critical=True))
    mdslive = config["mdsclient"]["mdsLive"]
    client_token = get_livestream_client_token(access_token=mdslive["accessToken"], client_location=mdslive["clientLocation"], salt=mdslive["salt"], property_name=ids.get_livestream_channel_id(livestream_id))
    protocols_url = mdslive["baseUrl"]+"live/1.0/getprotocols?access_token="+mdslive["accessToken"]+"&client_location="+mdslive["clientLocation"]+"&client_token="+client_token+"&property_name="+ids.get_livestream_channel_id(livestream_id)
    resp_prot = get_url(protocols_url, critical=True)
    protocols = json.loads(resp_prot)

    if LooseVersion('18.0') > LooseVersion(xbmc.getInfoLabel('System.BuildVersion')):
        log("version is: " + xbmc.getInfoLabel('System.BuildVersion'))
        kodiutils.notification('ERROR', kodiutils.get_string(32025))
        setResolvedUrl(plugin.handle, False, ListItem('none'))
        return

    protocol = ""
    drm = ""
    if kodiutils.get_setting("drm") == "0":
        protocol = "dash:widevine"
        drm_name = "widevine"
        drm = 'com.widevine.alpha'
    else:
        protocol = "dash:playready"
        drm_name = "playready"
        drm = 'com.microsoft.playready'
    log("drm: "+drm)

    client_server_token = get_livestream_server_client_token(access_token=mdslive["accessToken"], client_location=mdslive["clientLocation"], salt=mdslive["salt"], property_name=ids.get_livestream_channel_id(livestream_id), protocols=protocol, server_token=protocols["server_token"])
    urls_url = mdslive["baseUrl"]+"live/1.0/geturls?access_token="+mdslive["accessToken"]+"&client_location="+mdslive["clientLocation"]+"&client_token="+client_server_token+"&property_name="+ids.get_livestream_channel_id(livestream_id)+"&protocols="+protocol+"&secure_delivery=true"+"&server_token="+protocols["server_token"]
    resp_url = get_url(urls_url, critical=True)
    urls = json.loads(resp_url)
    log("Available formats: " + str(urls))

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
        if LooseVersion(version) < LooseVersion("2.2.2"):
            # inputstream to old cannot play mpd
            xbmcgui.Dialog().ok(heading=kodiutils.get_string(32023), line1=kodiutils.get_string(32024))
            setResolvedUrl(plugin.handle, False, ListItem(label='none'))
        else:
            playitem = ListItem(label=xbmc.getInfoLabel('Container.ShowTitle'), path=urls["urls"]["dash"][drm_name]["url"]+"|User-Agent=vvs-native-android/1.0.10 (Linux;Android 7.1.1) ExoPlayerLib/2.8.1")
            playitem.setProperty('inputstreamaddon', is_helper.inputstream_addon)
            playitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
            playitem.setProperty('inputstream.adaptive.license_type', drm)
            playitem.setProperty("inputstream.adaptive.manifest_update_parameter", "full")
            playitem.setProperty('inputstream.adaptive.license_key', urls["urls"]["dash"][drm_name]["drm"]["licenseAcquisitionUrl"] + "?token=" + urls["urls"]["dash"][drm_name]["drm"]["token"] +"|User-Agent=vvs-native-android/1.0.10 (Linux;Android 7.1.1) ExoPlayerLib/2.8.1" +'|R{SSM}|')
            setResolvedUrl(plugin.handle, True, playitem)
    else:
        kodiutils.notification('ERROR', kodiutils.get_string(32019).format(drm))
        setResolvedUrl(plugin.handle, False, playitem)
    #xbmc.Player().play(item=urls["urls"]["dash"]["widevine"]["url"], listitem=playitem)

@plugin.route('/category/video/<video_id>/<channel>')
def play_video(video_id, channel):
    # remove channel number if available
    if "_" in video_id:
        video_id = video_id.split("_")[1]
    config_url = ""
    if channel == "All Channels Feed" or channel == "":
        # no channel info guess by id
        if not video_id.isdigit():
            #probalby a video from puls4 or atv
            config_url = ids.get_livestream_config_url("puls4_and_atv_at")
        else:
            config_url = ids.get_livestream_config_url("austrian_tv")
    else:
        if channel == "PULS 4" or channel == "ATV":
            config_url = ids.get_livestream_config_url("puls4_and_atv_at")
        else:
            config_url = ids.get_livestream_config_url("austrian_tv")
    config = json.loads(get_url(config_url, cache=True, critical=True))
    mdsV2 = config["mdsclient"]["mdsV2"]
    sources_request_url = mdsV2["baseUrl"]+"vas/live/v2/videos?access_token=%s&client_location=null&client_name=%s&ids=%s" % (mdsV2["accessToken"], mdsV2["clientName"], video_id)
    sources_request = json.loads(get_url(sources_request_url, critical=True))
    log("sources_request: " + str(sources_request))
    protected = sources_request[0]["is_protected"]
    mpd_id = 0
    m3u8_id = 0
    ism_id = 0
    mp4_id = 0
    protocol = ""
    for source in sources_request[0]["sources"]:
        if source["mimetype"] == "text/xml":
            ism_id = source["id"]
        if source["mimetype"] == "application/x-mpegURL":
            m3u8_id = source["id"]
        if source["mimetype"] == "application/dash+xml":
            mpd_id = source["id"]
        if source["mimetype"] == "video/mp4":
            mp4_id = source["id"]
    drm = None
    if not protected:
        if kodiutils.get_setting_as_int('non_drm_format') == 0:
            source_id = mpd_id
            protocol = "mpd"
        elif kodiutils.get_setting_as_int('non_drm_format') == 3:
            source_id = mp4_id
            protocol = "mp4"
        else:
            source_id = m3u8_id
            protocol = "hls"
    else:
        if kodiutils.get_setting("drm") == "0":
            source_id = mpd_id
            protocol = "mpd"
            drm_name = "widevine"
            drm = 'com.widevine.alpha'
        else:
            source_id = ism_id
            protocol = "ism"
            drm_name = "playready"
            drm = 'com.microsoft.playready'

    if protected and LooseVersion('18.0') > LooseVersion(xbmc.getInfoLabel('System.BuildVersion')):
        log("version is: " + xbmc.getInfoLabel('System.BuildVersion'))
        kodiutils.notification('ERROR', kodiutils.get_string(32025))
        setResolvedUrl(plugin.handle, False, ListItem('none'))
        return

    server_request_token = get_video_server_request_token(access_token=mdsV2["accessToken"], client_location="null", client_name=mdsV2["clientName"], video_id=video_id, salt=mdsV2["salt"])
    server_request_url = mdsV2["baseUrl"]+"vas/live/v2/videos/%s/sources?access_token=%s&client_id=%s&client_location=null&client_name=%s" % (video_id, mdsV2["accessToken"], server_request_token, mdsV2["clientName"])
    server_request = json.loads(get_url(server_request_url, critical=True))
    server_id = server_request["server_id"]

    start = ""
    end = ""
    if protected and kodiutils.get_setting("drm") == "0" and kodiutils.get_setting_as_bool("oldformat"):
        start = "0"
        end = "999999999"

    source_url_request_token = get_video_source_request_token(access_token=mdsV2["accessToken"], client_location="null", client_name=mdsV2["clientName"], server_id= server_id, source_id=source_id, video_id=video_id, salt=mdsV2["salt"], start=start, end=end)
    source_url_request_url = mdsV2["baseUrl"]+"vas/live/v2/videos/%s/sources/url?access_token=%s&client_id=%s&client_location=null&client_name=%s&secure_delivery=true&server_id=%s&source_ids=%s" % (video_id, mdsV2["accessToken"], source_url_request_token, mdsV2["clientName"], server_id, source_id)

    if protected and kodiutils.get_setting("drm") == "0"and kodiutils.get_setting_as_bool("oldformat"):
        source_url_request_url += "&subclip_start=0&subclip_end=999999999"

    source_url_request = json.loads(get_url(source_url_request_url, critical=True))
    if not "status_code" in source_url_request or source_url_request["status_code"] != 0:
        log("error on video request: " + str(source_url_request))
        return sys.exit(0)

    playitem = ListItem('none')
    log("selected non drm format: " + kodiutils.get_setting('non_drm_format'))
    log("media url: " + source_url_request["sources"][0]["url"])
    if not protected and (kodiutils.get_setting_as_int('non_drm_format') == 2 or kodiutils.get_setting_as_int('non_drm_format') == 3):
        playitem = ListItem(label=xbmc.getInfoLabel('Container.ShowTitle'), path=source_url_request["sources"][0]["url"]+"|User-Agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36")
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
            if not protected and kodiutils.get_setting_as_int('non_drm_format') == 0 and LooseVersion(version) < LooseVersion("2.2.2"):
                # inputstream to old cannot play mpd
                # switch to hls
                kodiutils.set_setting('non_drm_format', 1)
                play_video(video_id, channel)
            elif protected and LooseVersion(version) < LooseVersion("2.2.2"):
                # inputstream to old cannot play mpd
                xbmcgui.Dialog().ok(heading=kodiutils.get_string(32023), line1=kodiutils.get_string(32024))
                setResolvedUrl(plugin.handle, False, ListItem(label='none'))
            else:
                playitem = ListItem(label=xbmc.getInfoLabel('Container.ShowTitle'), path=source_url_request["sources"][0]["url"]+"|User-Agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36")
                playitem.setProperty('inputstreamaddon', is_helper.inputstream_addon)
                playitem.setProperty('inputstream.adaptive.manifest_type', protocol)
                if protected:
                    playitem.setProperty('inputstream.adaptive.license_type', drm)
                    playitem.setProperty('inputstream.adaptive.license_key', source_url_request["drm"]["licenseAcquisitionUrl"] + "?token=" + source_url_request["drm"]["token"] +"|User-Agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36" +'|R{SSM}|')
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


@plugin.route('/category/by_category/id=<category_id>')
def get_by_category(category_id):
    dir = get_url(ids.categories_request_url.format(id=category_id), critical=False)
    dir_json = {}
    if dir:
        dir_json = json.loads(dir)
    special = ['ganze folgen', 'clips', 'bonus']
    if dir_json and "children" in dir_json["category"]:
        setContent(plugin.handle, 'tvshows')
        icon = ""
        fanart = ""
        if "images_json" in dir_json["category"]:
            images_parent = json.loads(dir_json["category"]["images_json"])
            if "image_base" in images_parent and images_parent["image_base"] != None:
                icon = images_parent["image_base"]
            if "image_show_big" in images_parent and images_parent["image_show_big"] != None:
                fanart = images_parent["image_show_big"]
        for child in dir_json["category"]["children"]:
            name = child["name"]
            icon_child = icon
            fanart_child = fanart
            if not any(x in child["name"].lower() for x in special):
                icon_child = ""
                fanart_child = ""
                if "images_json" in child:
                    images_child = json.loads(child["images_json"])
                    if "image_base" in images_child:
                        icon_child = images_child["image_base"]
                    if "image_show_big" in images_child:
                        fanart_child = images_child["image_show_big"]
            listitem = ListItem(name)
            listitem.setArt({'icon': icon_child, 'thumb': icon_child, 'poster': icon_child, 'fanart': fanart_child})
            plot = ""
            if 'description' in child and child['description'] != None:
                try:
                    startDATES = datetime(*(time.strptime(child['description'].split(', ')[1], '%d.%m.%y')[0:6])) # Do, 04.07.19
                    locale.setlocale(locale.LC_ALL, '')
                    lastTIMES = startDATES.strftime('%A - %d.%m.%Y')
                    plot = kodiutils.get_string(32006).format(str(lastTIMES))
                except: pass
            listitem.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot})
            add_favorites_context_menu(listitem, plugin.url_for(get_by_category, child["id"]), name, icon_child, fanart_child)
            addDirectoryItem(plugin.handle, url=plugin.url_for(get_by_category, child["id"]),
                listitem=listitem, isFolder=True)
        add_favorites_folder(plugin.url_for(get_by_category, dir_json["category"]["id"]),
            dir_json["category"]["name"], icon, fanart)
    if dir_json and "vod_items" in dir_json["category"]:
        if kodiutils.get_setting("sort") == "1":
            xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
            xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_DURATION)
            xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_EPISODE)
        setContent(plugin.handle, 'tvshows')
        for vod in dir_json["category"]["vod_items"]:
            goDATE = None
            startTIMES = ""
            Note_1 = ""
            Note_2 = vod["summary"]
            if not Note_2:
                Note_2 = ""
            if 'order_date' in vod and not str(vod['order_date']).startswith('1970') and vod['order_date'] != None:
                try:
                    startDATES = datetime(*(time.strptime(vod['order_date'].split(' +')[0], '%Y/%m/%d %H:%M:%S')[0:6])) # 2019/06/23 14:10:00 +0000
                    LOCALstart = utc_to_local(startDATES)
                    startTIMES = LOCALstart.strftime('%d.%m.%Y - %H:%M')
                    goDATE =  LOCALstart.strftime('%d.%m.%Y')
                except: pass
            if startTIMES != "": Note_1 = kodiutils.get_string(32005).format(str(startTIMES))
            if goDATE and kodiutils.get_setting("sort") == "1": xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
            if vod['title'].lower().find('staffel') > -1 or vod['title'].lower().find('episode') > -1 or vod['title'].lower().find('folge') > -1:
                try: vod['season'] = re.search('Staffel\s*(\d+)', vod['title']).group(1)
                except: pass
                try: vod['episode'] = re.search('Episode\s*(\d+)', vod['title']).group(1)
                except:
                    try:vod['episode'] = re.search('Folge\s*(\d+)', vod['title']).group(1)
                    except: pass
                if not kodiutils.get_setting_as_bool('keep_episode_number'):
                    try: vod['cleantitle'] = re.search(':\s*(.*)', vod['title']).group(1)
                    except: pass
                if vod.get('season', -1) != -1 or vod.get('episode', -1) != -1:
                    vod['mediatype'] = 'episode'
            log("Title: "+vod["title"])
            images = json.loads(vod["images_json"])
            listitem = ListItem(vod["title"])
            listitem.setArt({'icon': images["image_base"], 'thumb': images["image_base"], 'fanart': images["image_base"], 'poster': images["image_base"]})
            listitem.setProperty('IsPlayable', 'true')
            listitem.setInfo(type='Video', infoLabels={'Title': vod.get('cleantitle', vod["title"]), 'Plot': Note_1+Note_2, 'TvShowTitle': vod['show_name'], 'Season': vod.get('season', "-1"), 'episode': vod.get('episode', "-1"), 'Duration': vod['duration'], 'Date': goDATE, 'mediatype': vod.get('mediatype', 'video')})
            listitem.addContextMenuItems([('Queue', 'Action(Queue)')])
            addDirectoryItem(plugin.handle, url=plugin.url_for(play_video, vod["external_id"], vod["top_level_category"]["name"]),
                listitem=listitem)
    if not dir_json:
        add_favorites_folder(plugin.url_for(get_by_category, category_id),
            'no name', '', '')
    endOfDirectory(plugin.handle)

def utc_to_local(dt):
    if time.localtime().tm_isdst: return dt - timedelta(seconds=time.altzone)
    else: return dt - timedelta(seconds=time.timezone)

@plugin.route('/category/by_collection/id=<collection_id>/page=<page>')
def get_by_collection(collection_id, page):
    recursive = False
    if 'recursive' in plugin.args:
        recursive = plugin.args['recursive'][0] == "True"
    add_directories(collection_id, page, recursive)
    endOfDirectory(plugin.handle)


def add_directories(id, page = "1", recursive=False, prefix=""):
    dir = get_url(ids.collections_request_url.format(id=id, page=page), critical=True)
    dir_json = json.loads(dir)
    for item in dir_json["results"]:
        setContent(plugin.handle, 'tvshows')
        images = json.loads(item["images_json"])
        if item["type"] == "Category":
            name = item["name"]
            if "top_level_category" in item:
                if item["top_level_category"]["name"].lower() == item["name"].lower():
                    name = item["promotion_name"]
            listitem = ListItem(name)
            listitem.setArt({'icon': images["image_base"],'thumb': images["image_base"], 'poster': images["image_base"]})
            fanart = ""
            if "image_show_big" in images:
                fanart = images["image_show_big"]
                listitem.setArt({"fanart" : images["image_show_big"]})
            plot = ""
            if 'description' in item and item['description'] != None:
                try:
                    startDATES = datetime(*(time.strptime(item['description'].split(', ')[1], '%d.%m.%y')[0:6])) # Do, 04.07.19
                    locale.setlocale(locale.LC_ALL, '')
                    lastTIMES = startDATES.strftime('%A - %d.%m.%Y')
                    plot = kodiutils.get_string(32006).format(str(lastTIMES))
                except: pass
            listitem.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot})
            add_favorites_context_menu(listitem, plugin.url_for(get_by_category, item["id"]), name, images["image_base"], fanart)
            addDirectoryItem(plugin.handle, url=plugin.url_for(get_by_category, item["id"]),
                listitem=listitem, isFolder=True)
        elif item["type"] == "Collection":
            if item["ui_tag"] == "":
                add_directories(item["id"], prefix=item["title"]+" ")
            elif recursive:
                add_directories(item["id"])
            else:
                icon = ""
                if "image_base" in images:
                    icon = images["image_base"]
                addDirectoryItem(plugin.handle, url=plugin.url_for(get_by_collection, item["id"], "1"),
                    listitem=ListItem(prefix+item["title"], iconImage=icon, thumbnailImage=icon), isFolder=True)
    if int(dir_json["pagination"]["page"]) * int(dir_json["pagination"]["items_per_page"]) < int(dir_json["pagination"]["total_items"]):
        if kodiutils.get_setting_as_bool("limitlist"):
            addDirectoryItem(plugin.handle, url=plugin.url_for(get_by_collection, id, str(int(page)+1)),
                listitem=ListItem(kodiutils.get_string(32007).format(str(int(page)+1))), isFolder=True)
        else:
            get_by_collection(id, str(int(page)+1))

def add_favorites_folder(path, name, icon, fanart):
    global favorites
    if not favorites and xbmcvfs.exists(favorites_file_path):
        favorites_file = xbmcvfs.File(favorites_file_path)
        favorites = json.load(favorites_file)
        favorites_file.close()

    if not favorites or path not in favorites:
        # add favorites folder
        #addDirectoryItem(plugin.handle, url=plugin.url_for(add_favorite, query="%s***%s###%s###%s" % (path, name, icon, fanart)), listitem=ListItem(kodiutils.get_string(32004)))
        addDirectoryItem(plugin.handle, url=plugin.url_for(add_favorite, path=quote(codecs.encode(path, 'UTF-8')), name=quote(codecs.encode(name, 'UTF-8')), icon=quote(codecs.encode(icon, 'UTF-8')), fanart=quote(codecs.encode(fanart, 'UTF-8'))), listitem=ListItem(kodiutils.get_string(32008)))
    else:
        # remove favorites
        addDirectoryItem(plugin.handle, url=plugin.url_for(remove_favorite, query=quote(codecs.encode(path, 'UTF-8'))),
            listitem=ListItem(kodiutils.get_string(32009)))

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
    icon = ""
    if 'icon' in plugin.args:
        icon = plugin.args['icon'][0]
    fanart = ""
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
    favorites.update({path : {"name" : name, "icon" : icon, "fanart" : fanart}})
    # load favorites
    favorites_file = xbmcvfs.File(favorites_file_path, 'w')
    json.dump(favorites, favorites_file, indent=2)
    favorites_file.close()

    
    kodiutils.notification(kodiutils.get_string(32010), kodiutils.get_string(32011).format(name))
    xbmc.executebuiltin('Container.Refresh')
    setResolvedUrl(plugin.handle, True, ListItem("none"))

@plugin.route('/remove_fav')
def remove_favorite():
    data = unquote(plugin.args['query'][0])
    # load favorites
    global favorites
    if not favorites and xbmcvfs.exists(favorites_file_path):
        favorites_file = xbmcvfs.File(favorites_file_path)
        favorites = json.load(favorites_file)
        favorites_file.close()

    name = favorites[data]["name"]
    del favorites[data]
    # load favorites
    favorites_file = xbmcvfs.File(favorites_file_path, 'w')
    json.dump(favorites, favorites_file, indent=2)
    favorites_file.close()

    kodiutils.notification(kodiutils.get_string(32010), kodiutils.get_string(32012).format(name))
    xbmc.executebuiltin('Container.Refresh')
    setResolvedUrl(plugin.handle, True, ListItem("none"))

def get_url(url, headers={}, cache=False, critical=False):
    log(url)
    new_headers = {}
    new_headers.update(headers)
    if cache == True:
        cache_tag = ids.get_livestream_config_tag(url)
        if cache_tag != None:
            new_headers.update({"If-None-Match": cache_tag})
    new_headers.update({"User-Agent":"okhttp/3.10.0", "Accept-Encoding":"gzip"})
    try:
        request = urlopen(Request(url, headers=new_headers))
    except HTTPError as e:
        if cache and e.code == 304:
            return ids.get_livestream_config_cache(url)
        failure = str(e)
        if hasattr(e, 'code'):
            log("(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
        elif hasattr(e, 'reason'):
            log("(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
        if critical:
            kodiutils.notification("ERROR GETTING URL", failure)
            return sys.exit(0)
        else:
            return ""

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

def get_livestream_client_token(access_token="", client_location="", salt="", property_name=""):
    token = property_name + salt + access_token + client_location
    return "01"+hashlib.sha1(token.encode('UTF-8')).hexdigest()

def get_livestream_server_client_token(access_token="", client_location="", salt="", property_name="", protocols="", server_token=""):
    token = property_name + salt + access_token + server_token + client_location + protocols
    return "01"+hashlib.sha1(token.encode('UTF-8')).hexdigest()

def get_video_server_request_token(access_token="", client_location="", client_name="", video_id=0, salt=""):
    token = str(video_id) + salt + access_token + client_location + salt + client_name
    return "01"+hashlib.sha1(token.encode('UTF-8')).hexdigest()

def get_video_source_request_token(access_token="", client_location="", client_name="", server_id="", source_id=0, video_id=0, salt="", start="", end=""):
    token = salt + str(video_id) + access_token + server_id + client_location + str(source_id) + salt + client_name + start + end
    return "01"+hashlib.sha1(token.encode('UTF-8')).hexdigest()

def get_listitem(name="", icon="", fanart="", channel={}, no_puls4=True):
    if channel:
        if name:
            listitem = ListItem(name)
        else:
            listitem = ListItem(channel["name"])
        listitem.setProperty('IsPlayable', 'true')
        if no_puls4:
            listitem.setLabel(listitem.getLabel().replace("Puls4 ", ""))
        images = json.loads(channel["images_json"])
        if images:
            if "image_base" in images and images["image_base"]:
                listitem.setArt({'icon':images["image_base"], 'thumb':images["image_base"], 'poster':images["image_base"]})
            else:
                listitem.setArt({'icon':images["icon_1"], 'thumb':images["icon_1"], 'poster':images["icon_1"]})
        if "next_program" in channel:
            if channel["next_program"] != None:
                #'Title': channel["name"]
                listitem.setInfo(type='Video', infoLabels={'Title': listitem.getLabel(), 'Plot': channel["next_program"]["name"]+'[CR]'+(channel["next_program"]["description"] if channel["next_program"]["description"] != None else ""), 'mediatype': 'video'})
                program_images = json.loads(channel["next_program"]["images_json"])
                if program_images:
                    listitem.setArt({'fanart' : program_images["image_base"]})
            else:
                listitem.setInfo(type='Video', infoLabels={'Title': listitem.getLabel(), 'mediatype': 'video'})
    else:
        listitem = ListItem(name)
        listitem.setProperty('IsPlayable', 'true')
        listitem.setInfo(type='Video', infoLabels={'mediatype': 'video'})
        if icon != "":
            listitem.setArt({'icon':icon, 'thumb':icon, 'poster':icon})
        if fanart != "":
            listitem.setArt({'fanart':fanart})
    return listitem

def get_channel(json_data, channel):
    if json_data:
        for channels in json_data["account"]["channels"]:
            if channels["ui_tag"] == channel:
                return channels
    return {}

def run():
    plugin.run()

def log(info):
    if kodiutils.get_setting_as_bool("debug"):
        logger.warning(info)
