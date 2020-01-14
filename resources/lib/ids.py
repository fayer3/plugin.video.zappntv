# -*- coding: utf-8 -*-

import json
import xbmc
import xbmcaddon
import xbmcvfs
import logging
logger = logging.getLogger(xbmcaddon.Addon().getAddonInfo(u'id'))

__profile__ = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo(u'profile'))

if not xbmcvfs.exists(__profile__):
    xbmcvfs.mkdirs(__profile__)

cache_file_path = __profile__+u'livestream_config_cache.json'
tag_file_path = __profile__+u'livestream_tag_cache.json'

# data for requests
live_channel_ids = {
#vas_live_channel_id_
    u'dmax_de': u'dmax-de-24x7',
    u'edge': u'7sports-edge-24x7',
    u'kabeleins_at': u'kabeleins-at-24x7',
    u'kabeleins_ch': u'kabeleins-ch-24x7',
    u'kabeleins_de': u'kabeleins-de-24x7',
    u'kabeleinsdoku_at': u'kabeleinsdoku-at-24x7',
    u'kabeleinsdoku_ch': u'kabeleinsdoku-ch-24x7',
    u'kabeleinsdoku_de': u'kabeleinsdoku-de-24x7',
    u'prosieben_at': u'prosieben-at-24x7',
    u'prosieben_ch': u'prosieben-ch-24x7',
    u'prosieben_de': u'prosieben-de-24x7',
    u'prosiebenmaxx_at': u'prosiebenmaxx-at-24x7',
    u'prosiebenmaxx_ch': u'prosiebenmaxx-ch-24x7',
    u'prosiebenmaxx_de': u'prosiebenmaxx-de-24x7',
    u'sat1_at': u'sat1-at-24x7',
    u'sat1_ch': u'sat1-ch-24x7',
    u'sat1_de': u'sat1-de-24x7',
    u'sat1gold_at': u'sat1gold-at-24x7',
    u'sat1gold_ch': u'sat1gold-ch-24x7',
    u'sat1gold_de': u'sat1gold-de-24x7',
    u'sixx_at': u'sixx-at-24x7',
    u'sixx_ch': u'sixx-ch-24x7',
    u'sixx_de': u'sixx-de-24x7',
    u'tlc_de': u'tlc-de-24x7',
    u'popuptv': u'popuptv-24x7', # puls24
    u'puls4_at': u'puls4-24x7',
    u'servustv': u'servustv-at',
    u'schautv': u'schautv-at-hd',
    u'ric': u'ric-at',
    u'kronehittv': u'kronehittv-at',
    u'popuptv2': u'popuptv2',
    u'orf1': u'orf1-at',
    u'orf2': u'orf2-at',
    u'atv': u'atv-24x7',
    u'atv2': u'atv2-24x7'
}

live_config_url = u'https://config.native-player.p7s1.io/'

live_config_ids = {
#psdpp_vvs_player_
    u'austrian_tv': u'9c4595b4013182a170105f9c932f0f27.json',
    u'edge_sport': u'03f1febe795076ded678c2e1a089e52c.json',
    u'kabel1_at': u'1729302c1ab02b5ed729ab4d77817476.json',
    u'kabel1_ch': u'42258e4c34c502594f3eb08f3e4db04c.json',
    u'kabel1_de': u'6313a7c678ac4cc780f3cf0e187a07bf.json',
    u'kabel1doku_at': u'e09d5e737dc377a7240d281e3e57391f.json',
    u'kabel1doku_ch': u'91658c532cadd697d27b97d8134b9d12.json',
    u'kabel1doku_de': u'49bf22fb18a1ca3ea74d046ba037362d.json',
    u'orf': u'bcded72ce0797d12bc8aae2a35632e0f.json',
    u'prosieben_at': u'da5e8ccf91cfca4faf909b9c776a16a9.json',
    u'prosieben_ch': u'ab207b671776058520507d7f6b1f200e.json',
    u'prosieben_de': u'0a5d0b2f7385bc9a182230b7af2fb57e.json',
    u'prosieben_maxx_at': u'67c549ac44eaba5514a348f075721f8d.json',
    u'prosieben_maxx_ch': u'63a1d9e00ad0295fa98446e11bb16f97.json',
    u'prosieben_maxx_de': u'112704630df905fe4a8fe430cf3cd831.json',
    u'puls4_and_atv_at': u'dcb397f1ce8c1badb4a87762c344ce96.json',
    u'puls4_at': u'8419cba4529653601a75bb2e7c5822c6.json',
    u'ran_de': u'f42fb1e71a8a3b83d792c93f3b687a8b.json',
    u'sat1_at': u'bf9e20b43fc8b3debf2f2a6685180f19.json',
    u'sat1_ch': u'f80e1b4a3347831335d3248c79a1e937.json',
    u'sat1_de': u'24e9653a36b3b1303077a3529b7946a8.json',
    u'sat1_gold_at': u'56ccb4151a44461b97f3a88628daedc2.json',
    u'sat1_gold_ch': u'a0cee1b32f2d40827ca7f2d766c1b7b6.json',
    u'sat1_gold_de': u'f17de0c4d910e4991fd1daa41a646e5f.json',
    u'seventv': u'fd4d204f9c8a85e26b9d0642b192a4fa.json',
    u'sixx_at': u'0c8c362a7296d337c976abf23f6ed892.json',
    u'sixx_ch': u'a860c9ab59aa67942b2bd7cfeee40bd8.json',
    u'sixx_de': u'309a95dfec873a9bf57334714ca1d74a.json'
}

xxtea_key = u'3543373833383336354337383634363635433738363633383236354337383330363435393543373833393335323435433738363533393543373833383332334635433738363633333344334235433738333836363335'

default_streams = [('orf1','ORF 1'),
    ('orf2','ORF 2'),
    ('puls4_at','PULS 4'),
    ('popuptv','Puls 24'),
    ('atv','ATV'),
    ('atv2','ATV 2'),
    ('servustv','Servus TV Österreich'),
    ('schautv','SchauTV'),
    ('ric','RIC'),
    ('popuptv2','CineplexxTV'),
    ('kronehittv','Kronehit TV')]

streams_pro7sat1 = [('kabeleins','Kabel eins'),
    ('kabeleinsdoku','Kabel1Doku'),
    ('prosieben','ProSieben'),
    ('prosiebenmaxx','ProSiebenMaxx'),
    ('sat1','SAT.1'),
    ('sat1gold','SAT.1 Gold'),
    ('sixx','Sixx')]

legacy_categories_request_url =  u'https://admin.applicaster.com/v12/accounts/357/broadcasters/410/categories/{id}.json?&api[ver]=1.2&api[bundle]=at.zappn&api[bver]=2.0.3&api[os_type]=android&api[os_version]=25&api[store]=android'

overview_url = u'https://assets-secure.applicaster.com/zapp/accounts/5818cf82279a4a000ff1b6aa/apps/at.zappn/google_play/2.0.3/rivers/rivers.json'

api_url = u'https://middleware.p7s1.io/zappn/v1'
api_limit = 500
api_tvshows_url = api_url + u'/tvshows'
api_popular_url = u'/popular'
api_highlights_url = u'/highlights'
api_tvshows_query = u'?selection={data{id,channelId,brand,titles{default},descriptions{default},metaDescriptions{default},shortDescriptions{default},images{url,subType}}}&limit='
api_tvshows_genre_query = u'genres={genres}'
api_tvshows_tvshow_query = u'&ids={id}'

api_videos_url = api_url + u'/videos?sortBy=latest&sortAscending=false&selection={data{id,subType,descriptions{default},titles{default},duration,createdAt,tvShow{channelId,titles{default}},season{number},episode{airdates,number,metaDescriptions{default}},images{url,subType},credits{name,role},parentalRating{description},copyright,visibilities}}&limit=' + str(api_limit)
api_videos_query = u'&tvShowId={id}'
api_videos_episode_url = u'&subType=Hauptfilm'
api_videos_clip_url = u'&subType=Clip'
api_videos_bonus_url = u'&subType=Bonusmaterial'
api_videos_vorschau_url = u'&subType=Preview'

api_genres_url = api_url + u'/genres'

api_brands_url = api_url + u'/brands'
api_epg_url = api_url + u'/epg?selection={data{title,description,id,startTime,tvShow{title},channelId,tvChannelName,endTime,images(subType:"cover"){url}}}&showrunning=true'
api_epg_from = u'&sortAscending=true&channelId={channelId}&from={start}&limit=25' # time format 2020-01-08T20:25:46+01:00
api_epg_from_to = u'&sortAscending=true&channelId={channelId}&from={start}&to={to}&limit=5000' # time format 2020-01-08T20:25:46+01:00
api_epg_last = u'&sortAscending=false&channelId={channelId}&from={start}&limit=1' # time format 2020-01-08T20:25:46+01:00
api_epg_first = u'&sortAscending=true&channelId={channelId}&limit=1'

channel_icon_url = u'https://psdmw.prosiebensat1puls4.tv/zappn/channel/{channelId}.json'

api_image_url = u'{0}/profile:original'

api_headers = {u'key': u'e1fb40dab69950eed0b1bcf242cc92d7', 'Referer': 'zappPipes'}

search_query = {'type': ['shows'], 'search': ['']}

config_cache = {}
config_tag = {}

def get_livestream_config_url(livestream_id):
    livestream_id=convert_channel(livestream_id)
    if livestream_id == u'orf1' or livestream_id == u'orf2' or livestream_id == u'kronehittv':
        return live_config_url+live_config_ids[u'orf']
    elif (livestream_id == u'atv' 
        or livestream_id == u'atv2' 
        or livestream_id == u'puls4_at' 
        or livestream_id == u'popuptv' 
        or livestream_id == u'popuptv2' 
        or livestream_id == u'servustv' 
        or livestream_id == u'schautv' 
        or livestream_id == u'ric'):
        return live_config_url+live_config_ids[u'puls4_and_atv_at']
    elif u'kabeleins' in livestream_id:
        return live_config_url+live_config_ids[livestream_id.replace(u'kabeleins', u'kabel1')]
    elif u'prosiebenmaxx' in livestream_id:
        return live_config_url+live_config_ids[livestream_id.replace(u'prosiebenmaxx', u'prosieben_maxx')]
    elif u'sat1gold' in livestream_id:
        return live_config_url+live_config_ids[livestream_id.replace(u'sat1gold', u'sat1_gold')]
    else:
        return live_config_url+live_config_ids[livestream_id]

def get_livestream_channel_id(livestream_id):
    return live_channel_ids[convert_channel(livestream_id)]

def convert_channel(livestream_id):
    if livestream_id == u'puls4':
        return u'puls4_at'
    if livestream_id == u'puls24':
        return u'popuptv'
    if livestream_id == u'ProSieben':
        return u'prosieben_at'
    if livestream_id == u'SAT.1':
        return u'sat1_at'
    if livestream_id == u'kabel eins':
        return u'kabeleins_at'
    if livestream_id == u'Sixx':
        return u'sixx_at'
    if livestream_id == u'ProSiebenMaxx':
        return u'prosiebenmaxx_at'
    if livestream_id == u'SAT.1 Gold':
        return u'sat1gold_at'
    if livestream_id == u'kabel eins Doku':
        return u'kabeleinsdoku_at'
    return livestream_id

def get_livestream_config_cache(url):
    global config_cache
    if not config_cache and xbmcvfs.exists(cache_file_path):
        cache_file = xbmcvfs.File(cache_file_path)
        config_cache = json.load(cache_file)
        cache_file.close()
    if url in config_cache:
        return config_cache[url]
    return u''

def get_livestream_config_tag(url):
    global config_tag
    if not config_tag and xbmcvfs.exists(tag_file_path):
        tag_file = xbmcvfs.File(tag_file_path)
        config_tag = json.load(tag_file)
        tag_file.close()
    if url in config_tag:
        return config_tag[url]
    return u''

def set_livestream_config_cache(url, data, tag):
    global config_cache
    if not config_cache and xbmcvfs.exists(cache_file_path):
        cache_file = xbmcvfs.File(cache_file_path)
        config_cache = json.load(cache_file)
        cache_file.close()
    config_cache.update({url : data})
    global config_tag
    if not config_tag and xbmcvfs.exists(tag_file_path):
        tag_file = xbmcvfs.File(tag_file_path)
        config_tag = json.load(tag_file)
        tag_file.close()
    config_tag.update({url : tag})
    #save dictionary
    cache_file = xbmcvfs.File(cache_file_path, u'w')
    json.dump(config_cache, cache_file, indent=2)
    cache_file.close()
    tag_file = xbmcvfs.File(tag_file_path, u'w')
    json.dump(config_tag, tag_file, indent=2)
    cache_file.close()
