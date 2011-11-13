import simplejson
import urllib
import urlparse

def get_codes(line):
    """Return mnc, mcc, lac 3-tuple."""
    d = urlparse.parse_qs(line.split("window.open( 'map.php?")[1].split("'")[0])
    return int(d['MNC'][0]), int(d['MCC'][0]), d['LAC'][0]
    
def get_base_numbers(mnc, mcc, lac):
    if lac.rfind(',') != -1:
        lac = lac.split(',')
    else:
        lac = [lac]

    base_numbers = set()
    signals = set()
    for l in lac:
        url = "http://www.cellmapper.net/api/v2/json.php?action=getTowers&data[MCC]=%s&data[MNC]=%s&data[LAC]=%s" \
            % (mcc, mnc, l)
        result = simplejson.loads(urllib.urlopen(url).read())
        for data in result['data']:
            base = data['base']
            url = "http://www.cellmapper.net/api/v2/json.php?action=getBaseStation&data[MCC]=%s&data[MNC]=%s&data[LAC]=%s&data[base]=%s" \
                % (mcc, mnc, l, base)
            result = simplejson.loads(urllib.urlopen(url).read())
            try:
                if not result['data'].has_key('signals'):
                    continue
                x = result['data']['signals'].split(',')
                for s in x:
                    signals.add(int(s))
            except:
                pass
    return signals


if __name__ == '__main__':
    process = False
    f = open('coordinates.csv', 'w')
    for line in open('data.html').read().split('\n'):
        val = ''
        if line.startswith('window.open('):
            mnc, mcc, lac = get_codes(line)
            if mcc in [404, 405]:
                process = True
                print 'Processing mcc %s' % mcc
                signals = get_base_numbers(mnc, mcc, lac)
                if len(signals) == 0:
                    val = "-9999,-9999,"
                else:
                    val = '%s,%s,' % (min(signals), max(signals))
                f.write(val)
                print val,
        if process and line.startswith('position: new google.maps.LatLng('):
            process = False
            lat, lng = line.split('(')[1].split(')')[0].split(',')
            val += '%s,%s\n' % (lat.strip(),lng.strip())
            f.write(val)
            f.flush()
            print val
    f.close()
        
        
