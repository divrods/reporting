from utils import read_prefs_data
import urllib2
import json
import csv
from utils import read_artwork_data
from utils import read_prefs_data
from math import sqrt

PREF_CSV_PATH = './data/prefs2080423.csv'
ARTWORK_CSV_PATH = './data/artwork_data.csv'

ARTWORK_PREF_MAP = {}
USER_PREF_MAP = {}


def stddev(lst):
    mean = float(sum(lst)) / len(lst)
    return sqrt(sum((x - mean)**2 for x in lst) / len(lst))

def build_title_map():
    artwork_data = read_artwork_data(ARTWORK_CSV_PATH)
    title_map = {}
    for art in artwork_data:
        title_map[art['id']] = art['title']
    return title_map

def populate_maps(pref_data):
    for pref in pref_data:
        val = ARTWORK_PREF_MAP.get(pref['item_id'], 0)
        ARTWORK_PREF_MAP[pref['item_id']] = val + 1

        val = USER_PREF_MAP.get(pref['user_id'], 0)
        USER_PREF_MAP[pref['user_id']] = val + 1

    print USER_PREF_MAP


def main():

    pref_data = read_prefs_data(PREF_CSV_PATH, skip_admin_survey=False)
    print 'Read %s preferences from csv' % len(pref_data)

    title_map = build_title_map()
    populate_maps(pref_data)

    print "General Stats"
    print "* Total Preferences %s " % len(pref_data)
    print "* Total Users %s " % len(USER_PREF_MAP)
    print "* Total Artworks %s " % len(ARTWORK_PREF_MAP)

    sorted_by_pref_art = sorted(ARTWORK_PREF_MAP, key=ARTWORK_PREF_MAP.__getitem__)
    print "* Top Preferenced Artwork Title: %s - ID: %s - Total Prefs: %s " % (title_map[sorted_by_pref_art[-1]], sorted_by_pref_art[-1], ARTWORK_PREF_MAP[sorted_by_pref_art[-1]])
    print "* Least Preferenced Artwork Title: %s - ID: %s - Total Prefs: %s " % (title_map[sorted_by_pref_art[0]], sorted_by_pref_art[0], ARTWORK_PREF_MAP[sorted_by_pref_art[0]])


    sorted_by_pref_user = sorted(USER_PREF_MAP, key=USER_PREF_MAP.__getitem__)
    print "* Top Preferenced User - ID: %s - Total Prefs: %s " % (sorted_by_pref_user[-1], USER_PREF_MAP[sorted_by_pref_user[-1]])
    print "* Least Preferenced User - ID: %s - Total Prefs: %s " % (sorted_by_pref_user[0], USER_PREF_MAP[sorted_by_pref_user[0]])
    print "* Mean Preferences per User (Average Session size): %s" % float(sum(USER_PREF_MAP.values()) / float(len(USER_PREF_MAP.values())))
    print "* Standard Deviation: %s " % (stddev(USER_PREF_MAP.values()))

if __name__ == "__main__":
    main()