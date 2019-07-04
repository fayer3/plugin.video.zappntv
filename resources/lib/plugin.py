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

import hashlib
import json
import gzip
import sys

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))
kodilogging.config()
plugin = routing.Plugin()

__profile__ = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))

if not xbmcvfs.exists(__profile__):
    xbmcvfs.mkdirs(__profile__)

favorites_file_path = __profile__+"favorites.json"
favorites = {}

setContent(plugin.handle, '')

@plugin.route('/')
def index():
    icon = get_url(ids.collections_request_url % (ids.icon_id, "1"))
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
    icon_search = get_url(ids.collections_request_url % (ids.search_icon_id, "1"))
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
        show_category, "livestream"), ListItem("Live", iconImage=live_icon), True)
    addDirectoryItem(plugin.handle, plugin.url_for(
        get_by_collection, collection_id=highlights_id, page="1", recursive="True"), ListItem("Highlights", iconImage=highlights_icon), True)
    addDirectoryItem(plugin.handle, plugin.url_for(
        show_mediathek, mediathek_id), ListItem("Mediathek", iconImage=mediathek_icon), True)
    addDirectoryItem(plugin.handle, plugin.url_for(
        show_category, "tvprogramm"), ListItem("TV Programm", iconImage=tv_programm_icon), True)
    addDirectoryItem(plugin.handle, plugin.url_for(
        show_search), ListItem(kodiutils.get_string(32010), iconImage=search_icon), True)
    addDirectoryItem(plugin.handle, plugin.url_for(
        show_category, "favorites"), ListItem(kodiutils.get_string(32006)), True)
    addDirectoryItem(plugin.handle, plugin.url_for(
        open_settings), ListItem(kodiutils.get_string(32008), iconImage=settings_icon))
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
            play_livestream, "popuptv"), get_listitem(name="Popup TV", channel=channel, no_puls4=False))
        channel = get_channel(json_data, "ATV")
        addDirectoryItem(plugin.handle, plugin.url_for(
            play_livestream, "atv"), get_listitem(name="ATV", channel=channel))
        channel = get_channel(json_data, "ATV2")
        addDirectoryItem(plugin.handle, plugin.url_for(
            play_livestream, "atv2"), get_listitem(name="ATV 2", channel=channel))
        addDirectoryItem(plugin.handle, plugin.url_for(
            show_category, "austria"), ListItem("Austria"), True)
        addDirectoryItem(plugin.handle, plugin.url_for(
            show_category, "germany"), ListItem("Germany"), True)
        addDirectoryItem(plugin.handle, plugin.url_for(
            show_category, "switzerland"), ListItem("Switzerland"), True)
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
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "kabeleins"+id), listitem=get_listitem(name="Kabel eins"+name))
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "kabeleinsdoku"+id), listitem=get_listitem(name="Kabel1Doku"+name))
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "prosieben"+id), listitem=get_listitem(name="ProSieben"+name))
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "prosiebenmaxx"+id), listitem=get_listitem(name="ProSiebenMaxx"+name))
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "sat1"+id), listitem=get_listitem(name="SAT.1"+name))
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "sat1gold"+id), listitem=get_listitem(name="SAT.1 Gold"+name))
        addDirectoryItem(plugin.handle, url=plugin.url_for(
            play_livestream, "sixx"+id), listitem=get_listitem(name="Sixx"+name))

    elif category_id == "favorites":
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
        global favorites
        if not favorites and xbmcvfs.exists(favorites_file_path):
            favorites_file = xbmcvfs.File(favorites_file_path)
            favorites = json.load(favorites_file)
            favorites_file.close()

        for item in favorites:
            listitem = ListItem(favorites[item]["name"], iconImage=favorites[item]["icon"])
            listitem.setArt({'fanart' : favorites[item]["fanart"]})
            addDirectoryItem(plugin.handle, url=item,
                listitem=listitem, isFolder=True)
    else:
        addDirectoryItem(plugin.handle, "", ListItem(kodiutils.get_string(32000)), False)
    endOfDirectory(plugin.handle)

@plugin.route('/category/mediathek/id=<mediathek_id>')
def show_mediathek(mediathek_id):
    sort()
    get_by_collection(mediathek_id, "1")
    endOfDirectory(plugin.handle)

@plugin.route('/search')
def show_search():
    sort()
    query = xbmcgui.Dialog().input(kodiutils.get_string(32010))
    if query != "":
        search_id = ids.search_id
        channels = json.loads(get_url(ids.categories_request_url % search_id, critical=True))
        shows = {}
        for channel in channels["category"]["children"]:
            channel_shows = json.loads(get_url(ids.categories_request_url % channel["id"], critical=True))
            for show in channel_shows["category"]["children"]:
                shows.update({show["name"]+" | "+show["top_level_category"]["name"] : show})
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
            listitem = ListItem(result[show]["name"]+" | "+result[show]["top_level_category"]["name"], iconImage=icon)
            listitem.setArt({"fanart" : fanart})
            addDirectoryItem(plugin.handle, url=plugin.url_for(get_by_category, result[show]["id"]),
                listitem=listitem, isFolder=True)
    endOfDirectory(plugin.handle)

@plugin.route('/category/livestream/<livestream_id>')
def play_livestream(livestream_id):
    config_url = ids.get_livestream_config_url(livestream_id)
    config = json.loads(get_url(config_url, cache=True, critical=True))
    mdslive = config["mdsclient"]["mdsLive"]
    client_token = get_livestream_client_token(access_token=mdslive["accessToken"], client_location=mdslive["clientLocation"], salt=mdslive["salt"], property_name=ids.get_livestream_channel_id(livestream_id))
    protocols_url = mdslive["baseUrl"]+"live/1.0/getprotocols?access_token="+mdslive["accessToken"]+"&client_location="+mdslive["clientLocation"]+"&client_token="+client_token+"&property_name="+ids.get_livestream_channel_id(livestream_id)
    resp_prot = get_url(protocols_url, critical=True)
    protocols = json.loads(resp_prot)

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
    logger.critical("drm: "+drm)

    client_server_token = get_livestream_server_client_token(access_token=mdslive["accessToken"], client_location=mdslive["clientLocation"], salt=mdslive["salt"], property_name=ids.get_livestream_channel_id(livestream_id), protocols=protocol, server_token=protocols["server_token"])
    urls_url = mdslive["baseUrl"]+"live/1.0/geturls?access_token="+mdslive["accessToken"]+"&client_location="+mdslive["clientLocation"]+"&client_token="+client_server_token+"&property_name="+ids.get_livestream_channel_id(livestream_id)+"&protocols="+protocol+"&secure_delivery=true"+"&server_token="+protocols["server_token"]
    resp_url = get_url(urls_url, critical=True)
    urls = json.loads(resp_url)
    logger.critical(str(urls))

    playitem = ListItem('none')

    if inputstream and drm_name != "playready":
        is_helper = inputstreamhelper.Helper('mpd', drm=drm)
        if is_helper.check_inputstream():
            playitem = ListItem(label=xbmc.getInfoLabel('Container.ShowTitle'), path=urls["urls"]["dash"][drm_name]["url"]+"|User-Agent=vvs-native-android/1.0.10 (Linux;Android 7.1.1) ExoPlayerLib/2.8.1")
            playitem.setProperty('inputstreamaddon', is_helper.inputstream_addon)
            playitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
            playitem.setProperty('inputstream.adaptive.license_type', drm)
            playitem.setProperty("inputstream.adaptive.manifest_update_parameter", "full")
            playitem.setProperty('inputstream.adaptive.license_key', urls["urls"]["dash"][drm_name]["drm"]["licenseAcquisitionUrl"] + "?token=" + urls["urls"]["dash"][drm_name]["drm"]["token"] +"|User-Agent=vvs-native-android/1.0.10 (Linux;Android 7.1.1) ExoPlayerLib/2.8.1" +'|R{SSM}|')
    else:
        playitem = ListItem(label=xbmc.getInfoLabel('Container.ShowTitle'), path=urls["urls"]["dash"][drm_name]["url"]+"|User-Agent=vvs-native-android/1.0.10 (Linux;Android 7.1.1) ExoPlayerLib/2.8.1")
        playitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
        playitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
        playitem.setProperty('inputstream.adaptive.license_type', drm)
        playitem.setProperty("inputstream.adaptive.manifest_update_parameter", "full")
        playitem.setProperty('inputstream.adaptive.license_key', urls["urls"]["dash"][drm_name]["drm"]["licenseAcquisitionUrl"] + "?token=" + urls["urls"]["dash"][drm_name]["drm"]["token"] +"|User-Agent=vvs-native-android/1.0.10 (Linux;Android 7.1.1) ExoPlayerLib/2.8.1" +'|R{SSM}|')
    setResolvedUrl(plugin.handle, True, playitem)
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
    logger.critical(str(sources_request))
    protected = sources_request[0]["is_protected"]
    mpd_id = 0
    m3u8_id = 0
    ism_id = 0
    protocol = ""
    for source in sources_request[0]["sources"]:
        if source["mimetype"] == "text/xml":
            ism_id = source["id"]
        if source["mimetype"] == "application/x-mpegURL":
            m3u8_id = source["id"]
        if source["mimetype"] == "application/dash+xml":
            mpd_id = source["id"]
    drm = None
    if not protected:
        if mpd_id != 0:
            source_id = mpd_id
            protocol = "mpd"
        elif m3u8_id != 0:
            source_id = m3u8_id
            protocol = "hls"
        else:
            source_id = ism_id
            protocol = "ism"
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
        logger.critical("error on video request: " + str(source_url_request))
        return sys.exit(0)
    playitem = ListItem('none')
    if inputstream and kodiutils.get_setting("drm") == "0":
        is_helper = inputstreamhelper.Helper(protocol, drm=drm)
        if is_helper.check_inputstream():
            playitem = ListItem(label=xbmc.getInfoLabel('Container.ShowTitle'), path=source_url_request["sources"][0]["url"]+"|User-Agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36")
            playitem.setProperty('inputstreamaddon', is_helper.inputstream_addon)
            playitem.setProperty('inputstream.adaptive.manifest_type', protocol)
            if protected:
                playitem.setProperty('inputstream.adaptive.license_type', drm)
                playitem.setProperty('inputstream.adaptive.license_key', source_url_request["drm"]["licenseAcquisitionUrl"] + "?token=" + source_url_request["drm"]["token"] +"|User-Agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36" +'|R{SSM}|')
    else:
        playitem = ListItem(label=xbmc.getInfoLabel('Container.ShowTitle'), path=source_url_request["sources"][0]["url"]+"|User-Agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36")
        playitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
        playitem.setProperty('inputstream.adaptive.manifest_type', protocol)
        if protected:
            playitem.setProperty('inputstream.adaptive.license_type', drm)
            playitem.setProperty('inputstream.adaptive.license_key', source_url_request["drm"]["licenseAcquisitionUrl"] + "?token=" + source_url_request["drm"]["token"] +"|User-Agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36" +'|R{SSM}|')
    setResolvedUrl(plugin.handle, True, playitem)

@plugin.route('/category/by_category/<category_id>')
def get_by_category(category_id):
    sort()
    dir = get_url(ids.categories_request_url % category_id, critical=True)
    dir_json = json.loads(dir)
    if "children" in dir_json["category"]:
        for child in dir_json["category"]["children"]:
            icon = ""
            fanart = ""
            if "images_json" in child:
                images = json.loads(child["images_json"])
                if "image_base" in images:
                    icon = images["image_base"]
                if "image_show_big" in images:
                    fanart = images["image_show_big"]
            listitem = ListItem(child["name"], iconImage=icon)
            listitem.setArt({"fanart" : fanart})
            addDirectoryItem(plugin.handle, url=plugin.url_for(get_by_category, child["id"]),
                listitem=listitem, isFolder=True)
        images = json.loads(dir_json["category"]["images_json"])
        icon = ""
        if "image_base" in images:
            icon = images["image_base"]
        fanart = ""
        if "image_show_big" in images:
            fanart = images["image_show_big"]
        add_favorites_folder(plugin.url_for(get_by_category, dir_json["category"]["id"]),
            dir_json["category"]["name"],
            icon,
            fanart)
    if "vod_items" in dir_json["category"]:
        setContent(plugin.handle, 'videos')
        for vod in dir_json["category"]["vod_items"]:
            images = json.loads(vod["images_json"])
            listitem = ListItem(vod["title"], iconImage=images["image_base"])
            listitem.setProperty('IsPlayable', 'true')
            listitem.setInfo("video", {'mediatype':'video', "plot":vod["summary"], "tvshowtitle" : vod["show_name"], "duration": vod["duration"]})
            listitem.addContextMenuItems([('Queue', 'Action(Queue)')])
            addDirectoryItem(plugin.handle, url=plugin.url_for(play_video, vod["external_id"], vod["top_level_category"]["name"]),
                listitem=listitem)
    endOfDirectory(plugin.handle)

@plugin.route('/category/by_collection/<collection_id>&page=<page>')
def get_by_collection(collection_id, page):
    sort()
    recursive = False
    if 'recursive' in plugin.args:
        recursive = plugin.args['recursive'][0] == "True"
    add_directories(collection_id, page, recursive)
    endOfDirectory(plugin.handle)


def add_directories(id, page = "1", recursive=False, prefix=""):
    dir = get_url(ids.collections_request_url % (id, page), critical=True)
    dir_json = json.loads(dir)
    for item in dir_json["results"]:
        images = json.loads(item["images_json"])
        if item["type"] == "Category":
            name = item["name"]
            if "top_level_category" in item:
                if item["top_level_category"]["name"].lower() == item["name"].lower():
                    name = item["promotion_name"]
            listitem = ListItem(name, iconImage=images["image_base"])
            if "image_show_big" in images:
                listitem.setArt({ "fanart" : images["image_show_big"]})
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
                    listitem=ListItem(prefix+item["title"], iconImage=icon), isFolder=True)
    if int(dir_json["pagination"]["page"]) * int(dir_json["pagination"]["items_per_page"]) < int(dir_json["pagination"]["total_items"]):
        if kodiutils.get_setting_as_bool("limitlist"):
            addDirectoryItem(plugin.handle, url=plugin.url_for(get_by_collection, id, str(int(page)+1)),
                listitem=ListItem(kodiutils.get_string(32003)+" "+str(int(page)+1)), isFolder=True)
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
        addDirectoryItem(plugin.handle, url=plugin.url_for(add_favorite, path=quote(codecs.encode(path, 'UTF-8')), name=quote(codecs.encode(name, 'UTF-8')), icon=quote(codecs.encode(icon, 'UTF-8')), fanart=quote(codecs.encode(fanart, 'UTF-8'))), listitem=ListItem(kodiutils.get_string(32004)))
    else:
        # remove favorites
        addDirectoryItem(plugin.handle, url=plugin.url_for(remove_favorite, query=quote(codecs.encode(path, 'UTF-8'))),
            listitem=ListItem(kodiutils.get_string(32005)))

@plugin.route('/add_fav/')
def add_favorite():
    #data = plugin.args['query'][0].split('***')
    path = unquote(plugin.args['path'][0])
    name = unquote(plugin.args['name'][0])
    icon = ""
    if 'icon' in plugin.args:
        icon = unquote(plugin.args['icon'][0])
    fanart = ""
    if 'fanart' in plugin.args:
        fanart = unquote(plugin.args['fanart'][0])
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

    try:
        kodiutils.notification(kodiutils.get_string(32015), kodiutils.get_string(32016) % codecs.decode(name, 'utf-8'))
    except TypeError:
        kodiutils.notification(kodiutils.get_string(32015), kodiutils.get_string(32016) % codecs.decode(bytes(name, 'utf-8'), 'utf-8'))
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

    kodiutils.notification(kodiutils.get_string(32015), kodiutils.get_string(32017) % name)
    xbmc.executebuiltin('Container.Refresh')
    setResolvedUrl(plugin.handle, True, ListItem("none"))

def get_url(url, headers={}, cache=False, critical=False):
    #logger.critical(url)
    new_headers = {}
    new_headers.update(headers)
    if cache == True:
        new_headers.update({"If-None-Match": ids.get_livestream_config_tag(url)})
    new_headers.update({"User-Agent":"okhttp/3.10.0", "Accept-Encoding":"gzip"})
    try:
        request = urlopen(Request(url, headers=new_headers))
    except HTTPError as e:
        if cache and e.code == 304:
            return ids.get_livestream_config_cache(url)
        failure = str(e)
        if hasattr(e, 'code'):
            logger.critical("(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
        elif hasattr(e, 'reason'):
            logger.critical("(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
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
        listitem = ListItem(channel["name"])
        listitem.setProperty('IsPlayable', 'true')
        if no_puls4:
            listitem.setLabel(listitem.getLabel().replace("Puls4 ", ""))
        images = json.loads(channel["images_json"])
        if images:
            if "image_base" in images and images["image_base"]:
                listitem.setArt({"icon":images["image_base"]})
            else:
                listitem.setArt({"icon":images["icon_1"]})
        if "next_program" in channel:
            #'Title': channel["name"]
            listitem.setInfo(type='Video', infoLabels={'mediatype':'video', 'plot': channel["next_program"]["name"]+'\n'+channel["next_program"]["description"]})
            program_images = json.loads(channel["next_program"]["images_json"])
            if program_images:
                listitem.setArt({"fanart" : program_images["image_base"]})
    else:
        listitem = ListItem(name)
        listitem.setProperty('IsPlayable', 'true')
        listitem.setInfo(type='Video', infoLabels={'mediatype':'video'})
        if icon != "":
            listitem.setArt({"icon":icon})
        if fanart != "":
            listitem.setArt({"fanart":fanart})
    return listitem

def get_channel(json_data, channel):
    if json_data:
        for channels in json_data["account"]["channels"]:
            if channels["ui_tag"] == channel:
                return channels
    return {}

def sort():
    sort = kodiutils.get_setting("sort")
    if sort == "0":
        return
    elif sort == "1":
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)

def run():
    plugin.run()
