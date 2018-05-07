from utils import read_prefs_data
import urllib2
import json
import csv
import json
import io


PREF_CSV_PATH = './data/prefs2080423.csv'
FIXED_PREF_CSV_PATH = './data/prefs2080423REPAIRED.csv'
DEVICE_PREF_LOG = './data/device_preference_log.json';


def write_csv(preference_data):
    with open(FIXED_PREF_CSV_PATH, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(('resource_id', 'user_id', 'item_id', 'pref', 'synced_timestamp', 'timestamp'))
        for p in preference_data:
            writer.writerow((p['resource_id'], p['user_id'], p['item_id'], p['pref'], p['synced_timestamp'], p['timestamp']))

def read_device_prefs(pref_json_src):
    shaped_jason_data = []
    with open(pref_json_src) as data_file:
        json_data = json.load(data_file)

    # Convert data into rows
    for session_id, user_prefs_list in json_data.items():
        for r in user_prefs_list:
            pref = True
            if (r['pref'] == 'n'):
                pref = False
            shaped_record = {'item_id': r['artid'], 'user_id': session_id, 'pref': pref}
            shaped_jason_data.append(shaped_record)
    return shaped_jason_data

def fix_false_records(device_prefs, service_prefs):
    fixed_count = 0
    for p_device in device_prefs:
        if p_device['pref'] == True:
            continue

        p_device_user = p_device['user_id']
        p_device_item = p_device['item_id']

        p_service_idx = 0
        for p_service in service_prefs:
            if p_device['user_id'] == p_service['user_id'] and p_device['item_id'] == p_service['item_id']:
                service_prefs[p_service_idx]['pref'] = False
                fixed_count += 1
                break

            p_service_idx  += 1

    print "%s records repaired" % fixed_count  # Should be 697 ?
    return service_prefs



def main():
    print 'Starting Process to fix Preferences Recorded as boolean True but were sent as "n"'
    device_prefs = read_device_prefs(DEVICE_PREF_LOG)
    pref_data = read_prefs_data(PREF_CSV_PATH, skip_admin_survey=False)

    fixed_records = fix_false_records(device_prefs, pref_data)

    write_csv(fixed_records)

    # Next get the set of records that are n

    # Load in the existing data

    # Convert to map

    # For each n, replace that record


if __name__ == "__main__":
    main()