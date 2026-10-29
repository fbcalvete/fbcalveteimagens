import json, time, urllib.request, urllib.parse, ssl, sys

def get(url, params=None, tries=12, timeout=90, fatal=(499, 403, 400, 404)):
    if params:
        url = url + ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                txt = r.read().decode('utf-8')
            d = json.loads(txt)
            if isinstance(d, dict) and 'error' in d:
                last = d["error"]
                if d["error"].get("code") in fatal: raise ValueError(str(d["error"]))
                raise RuntimeError(str(d['error'])[:200])
            return d
        except ValueError:
            raise
        except Exception as e:
            last = e
            w = min(60, 3 * (i + 1))
            print(f'  retry {i+1} in {w}s: {str(e)[:120]}', file=sys.stderr)
            time.sleep(w)
    raise RuntimeError(f'failed {url}: {last}')

if __name__ == '__main__':
    print(json.dumps(get(sys.argv[1]), indent=1)[:int(sys.argv[2]) if len(sys.argv) > 2 else 5000])
