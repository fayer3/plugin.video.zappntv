import json
import xbmc
import xbmcaddon
import xbmcvfs
import logging
logger = logging.getLogger(xbmcaddon.Addon().getAddonInfo('id'))

__profile__ = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))

if not xbmcvfs.exists(__profile__):
    xbmcvfs.mkdirs(__profile__)

cache_file_path = __profile__+"livestream_config_cache.json"
tag_file_path = __profile__+"livestream_tag_cache.json"

# data for requests
live_channel_ids = {
#vas_live_channel_id_
    "dmax_de": "dmax-de-24x7",
    "edge": "7sports-edge-24x7",
    "kabeleins_at": "kabeleins-at-24x7",
    "kabeleins_ch": "kabeleins-ch-24x7",
    "kabeleins_de": "kabeleins-de-24x7",
    "kabeleinsdoku_at": "kabeleinsdoku-at-24x7",
    "kabeleinsdoku_ch": "kabeleinsdoku-ch-24x7",
    "kabeleinsdoku_de": "kabeleinsdoku-de-24x7",
    "prosieben_at": "prosieben-at-24x7",
    "prosieben_ch": "prosieben-ch-24x7",
    "prosieben_de": "prosieben-de-24x7",
    "prosiebenmaxx_at": "prosiebenmaxx-at-24x7",
    "prosiebenmaxx_ch": "prosiebenmaxx-ch-24x7",
    "prosiebenmaxx_de": "prosiebenmaxx-de-24x7",
    "sat1_at": "sat1-at-24x7",
    "sat1_ch": "sat1-ch-24x7",
    "sat1_de": "sat1-de-24x7",
    "sat1gold_at": "sat1gold-at-24x7",
    "sat1gold_ch": "sat1gold-ch-24x7",
    "sat1gold_de": "sat1gold-de-24x7",
    "sixx_at": "sixx-at-24x7",
    "sixx_ch": "sixx-ch-24x7",
    "sixx_de": "sixx-de-24x7",
    "tlc_de": "tlc-de-24x7",
    "popuptv": "popuptv-24x7", # puls24
    "puls4_at": "puls4-24x7",
    "servustv": "servustv-at",
    "schautv": "schautv-at-hd",
    "ric": "ric-at",
    "kronehittv": "kronehittv-at",
    "popuptv2": "popuptv2",
    "orf1": "orf1-at",
    "orf2": "orf2-at",
    "atv": "atv-24x7",
    "atv2": "atv2-24x7"
}

live_config_url = "https://config.native-player.p7s1.io/"

live_config_ids = {
#psdpp_vvs_player_
    "austrian_tv": "9c4595b4013182a170105f9c932f0f27.json",
    "edge_sport": "03f1febe795076ded678c2e1a089e52c.json",
    "kabel1_at": "1729302c1ab02b5ed729ab4d77817476.json",
    "kabel1_ch": "42258e4c34c502594f3eb08f3e4db04c.json",
    "kabel1_de": "6313a7c678ac4cc780f3cf0e187a07bf.json",
    "kabel1doku_at": "e09d5e737dc377a7240d281e3e57391f.json",
    "kabel1doku_ch": "91658c532cadd697d27b97d8134b9d12.json",
    "kabel1doku_de": "49bf22fb18a1ca3ea74d046ba037362d.json",
    "orf": "bcded72ce0797d12bc8aae2a35632e0f.json",
    "prosieben_at": "da5e8ccf91cfca4faf909b9c776a16a9.json",
    "prosieben_ch": "ab207b671776058520507d7f6b1f200e.json",
    "prosieben_de": "0a5d0b2f7385bc9a182230b7af2fb57e.json",
    "prosieben_maxx_at": "67c549ac44eaba5514a348f075721f8d.json",
    "prosieben_maxx_ch": "63a1d9e00ad0295fa98446e11bb16f97.json",
    "prosieben_maxx_de": "112704630df905fe4a8fe430cf3cd831.json",
    "puls4_and_atv_at": "dcb397f1ce8c1badb4a87762c344ce96.json",
    "puls4_at": "8419cba4529653601a75bb2e7c5822c6.json",
    "ran_de": "f42fb1e71a8a3b83d792c93f3b687a8b.json",
    "sat1_at": "bf9e20b43fc8b3debf2f2a6685180f19.json",
    "sat1_ch": "f80e1b4a3347831335d3248c79a1e937.json",
    "sat1_de": "24e9653a36b3b1303077a3529b7946a8.json",
    "sat1_gold_at": "56ccb4151a44461b97f3a88628daedc2.json",
    "sat1_gold_ch": "a0cee1b32f2d40827ca7f2d766c1b7b6.json",
    "sat1_gold_de": "f17de0c4d910e4991fd1daa41a646e5f.json",
    "seventv": "fd4d204f9c8a85e26b9d0642b192a4fa.json",
    "sixx_at": "0c8c362a7296d337c976abf23f6ed892.json",
    "sixx_ch": "a860c9ab59aa67942b2bd7cfeee40bd8.json",
    "sixx_de": "309a95dfec873a9bf57334714ca1d74a.json"
}

xxtea_key = "3543373833383336354337383634363635433738363633383236354337383330363435393543373833393335323435433738363533393543373833383332334635433738363633333344334235433738333836363335"

overview_url="https://admin.applicaster.com/v12/accounts/357.json?&include_voucher_templates=false&api[store]=android&api[ver]=1.2&api[bundle]=at.zappn&api[bver]=1.0.10"

collections_request_url = "https://admin.applicaster.com/v12/accounts/357/broadcasters/410/collections/{id}/items.json?&page={page}"
categories_request_url =  "https://admin.applicaster.com/v12/accounts/357/broadcasters/410/categories/{id}.json?&api[ver]=1.2&api[bundle]=at.zappn&api[bver]=1.0.10&api[os_type]=android&api[os_version]=25&api[store]=android"

epg_request_url = "http://admin.applicaster.com/v12/accounts/357/channels/{channel_id}/programs.json?date={date}" #date=YYYYMMDD

#from https://admin.applicaster.com/v12/accounts/357/broadcasters/410/collections.json
icon_id = "7617" #Bottom Tab Navigation Collection - Android
search_icon_id = "3551" #Nav Bar Collection

highlights_id = "6764"
mediathek_id = "6625"
tv_programm_id = "97407"
search_id = "80740"

epg_id = "7263"

config_cache = {}
config_tag = {}

def get_livestream_config_url(livestream_id):
    if livestream_id == "orf1" or livestream_id == "orf2" or livestream_id == "kronehittv":
        return live_config_url+live_config_ids["orf"]
    elif (livestream_id == "atv" 
        or livestream_id == "atv2" 
        or livestream_id == "puls4_at" 
        or livestream_id == "popuptv" 
        or livestream_id == "popuptv2" 
        or livestream_id == "servustv" 
        or livestream_id == "schautv" 
        or livestream_id == "ric"):
        return live_config_url+live_config_ids["puls4_and_atv_at"]
    elif "kabeleins" in livestream_id:
        return live_config_url+live_config_ids[livestream_id.replace("kabeleins", "kabel1")]
    elif "prosiebenmaxx" in livestream_id:
        return live_config_url+live_config_ids[livestream_id.replace("prosiebenmaxx", "prosieben_maxx")]
    elif "sat1gold" in livestream_id:
        return live_config_url+live_config_ids[livestream_id.replace("sat1gold", "sat1_gold")]
    else:
        return live_config_url+live_config_ids[livestream_id]

def get_livestream_channel_id(livestream_id):
    return live_channel_ids[livestream_id]

def get_livestream_config_cache(url):
    global config_cache
    if not config_cache and xbmcvfs.exists(cache_file_path):
        cache_file = xbmcvfs.File(cache_file_path)
        config_cache = json.load(cache_file)
        cache_file.close()
    if url in config_cache:
        return config_cache[url]
    return ""

def get_livestream_config_tag(url):
    global config_tag
    if not config_tag and xbmcvfs.exists(tag_file_path):
        tag_file = xbmcvfs.File(tag_file_path)
        config_tag = json.load(tag_file)
        tag_file.close()
    if url in config_tag:
        return config_tag[url]
    return ""

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
    cache_file = xbmcvfs.File(cache_file_path, 'w')
    json.dump(config_cache, cache_file, indent=2)
    cache_file.close()
    tag_file = xbmcvfs.File(tag_file_path, 'w')
    json.dump(config_tag, tag_file, indent=2)
    cache_file.close()
