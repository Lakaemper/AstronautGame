"""Web server for the Astro Game: python serve.py [port]   (default 8000, serves this folder)

Like http.server, but
  * it tells the browser to re-check every file on each load, so updates show up on reload, and
  * it relays the moves of ONLINE games between two browsers (no accounts, no extra software, standard library only).

How an online game works: the browsers run the same rules, so the server only keeps, per room, the list of moves and hands every new move
to the other player. A room is created with POST /api/new (the host chooses a colour, or gets a random one, and also the piece setup and the colour that starts), a friend joins with POST /api/join and gets
the other colour (anyone after that can only watch), moves go to POST /api/move, and GET /api/events is a Server-Sent-Events stream that
replays the old moves and then delivers new ones live. Move order is checked by turn (the starting colour moves first, then they alternate).
Rooms are kept in rooms.json, so a restart of the server does not end running games; rooms older than 14 days are dropped.
"""
import functools, http.server, json, os, re, secrets, socket, sys, threading, time, urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
ROOMS_FILE = os.path.join(ROOT, 'rooms.json')
MAX_ROOMS, MAX_AGE, KEEPALIVE = 500, 14 * 24 * 3600, 15
cond = threading.Condition()
present = {}                                           # room -> [connected Blue streams, connected Red streams]

def load():
    try:
        with open(ROOMS_FILE, encoding='utf8') as f: rooms = json.load(f)
    except (OSError, ValueError): rooms = {}
    now = time.time()
    return {k: v for k, v in rooms.items() if now - v.get('created', now) < MAX_AGE}
rooms = load()

def save():                                            # call with the lock held
    tmp = ROOMS_FILE + '.tmp'
    with open(tmp, 'w', encoding='utf8') as f: json.dump(rooms, f)
    os.replace(tmp, ROOMS_FILE)

def seat_for(room, token):                             # 0 Blue, 1 Red, 2 watcher, None = unknown token
    return room['tokens'].get(token)

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def log_message(self, fmt, *args):
        if '/api/events' not in str(args[0] if args else ''): super().log_message(fmt, *args)      # the event streams would flood the log

    # ---------- helpers
    def reply(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code); self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(body))); self.end_headers()
        self.wfile.write(body)

    def body(self):
        n = int(self.headers.get('Content-Length') or 0)
        if n > 4096: raise ValueError('too big')
        return json.loads(self.rfile.read(n) or b'{}')

    @staticmethod
    def options(room):                                     # what the guest needs to build the same game (older rooms: the default game)
        return {'setup': room.get('setup', '4111'), 'start': room.get('start', 0), 'host': room.get('host', 0)}

    # ---------- POST /api/new, /api/join, /api/move
    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        try: data = self.body()
        except ValueError: return self.reply(400, {'error': 'bad request'})
        with cond:
            if path == '/api/new':
                if len(rooms) >= MAX_ROOMS: return self.reply(503, {'error': 'too many games running'})
                rid, tok = secrets.token_urlsafe(5).replace('-', 'x').replace('_', 'y'), secrets.token_urlsafe(12)
                colour = data['color'] if data.get('color') in (0, 1) else secrets.randbelow(2)          # the host picks a colour, or gets a random one
                setup = data['setup'] if re.fullmatch(r'[24][01]{3}', str(data.get('setup', ''))) else '4111'   # astronauts, rover, drone, shield
                start = 1 if data.get('start') == 1 else 0                                                 # the colour that moves first
                rooms[rid] = {'created': time.time(), 'moves': [], 'tokens': {tok: colour}, 'setup': setup, 'start': start, 'host': colour}
                save(); return self.reply(200, {'room': rid, 'token': tok, 'color': colour, **self.options(rooms[rid])})
            room = rooms.get(str(data.get('room', '')))
            if room is None: return self.reply(404, {'error': 'unknown game'})
            if path == '/api/join':
                tok = str(data.get('token') or '')
                if tok in room['tokens']: return self.reply(200, {'token': tok, 'color': room['tokens'][tok], **self.options(room)})
                taken = [c for c in room['tokens'].values() if c < 2]
                colour = 1 - taken[0] if len(taken) == 1 else 2                  # the friend gets the other colour, later visitors only watch
                tok = secrets.token_urlsafe(12)
                if len(room['tokens']) < 60: room['tokens'][tok] = colour
                save(); cond.notify_all(); return self.reply(200, {'token': tok, 'color': colour, **self.options(room)})
            if path == '/api/move':
                colour = seat_for(room, str(data.get('token') or ''))
                sig, i = str(data.get('sig', '')), data.get('i')
                if colour is None or colour > 1: return self.reply(403, {'error': 'you are only watching'})
                if i != len(room['moves']) or colour != (len(room['moves']) + room.get('start', 0)) % 2 or not sig or len(sig) > 60:
                    return self.reply(409, {'error': 'out of sync', 'n': len(room['moves'])})      # not your turn, or a move was missed
                room['moves'].append(sig); save(); cond.notify_all()
                return self.reply(200, {'ok': True, 'n': len(room['moves'])})
        self.reply(404, {'error': 'unknown request'})

    # ---------- GET /api/events (Server-Sent Events), everything else is a plain file
    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path != '/api/events': return super().do_GET()
        q = urllib.parse.parse_qs(u.query); rid = (q.get('room') or [''])[0]; tok = (q.get('token') or [''])[0]
        with cond:
            room = rooms.get(rid); colour = seat_for(room, tok) if room else None
        if room is None or colour is None: return self.reply(404, {'error': 'unknown game or seat'})
        last = self.headers.get('Last-Event-ID')
        nxt = int(last) + 1 if last and last.isdigit() else 0                  # the browser sends Last-Event-ID when it reconnects
        self.send_response(200); self.send_header('Content-Type', 'text/event-stream'); self.send_header('Connection', 'keep-alive'); self.end_headers()
        with cond:
            pr = present.setdefault(rid, [0, 0])
            if colour < 2: pr[colour] += 1
            cond.notify_all()
        sent_presence, first = None, True
        try:
            while True:
                with cond:
                    while True:
                        moves = room['moves'][nxt:]; pres = [pr[0] > 0, pr[1] > 0]
                        if moves or pres != sent_presence or first: break
                        if not cond.wait(KEEPALIVE): break                      # timed out: send a keep-alive line
                out = ''
                for k, sig in enumerate(moves): out += 'id: %d\nevent: move\ndata: %s\n\n' % (nxt + k, json.dumps({'i': nxt + k, 'sig': sig}))
                nxt += len(moves)
                if first: first = False; out += 'event: ready\ndata: %s\n\n' % json.dumps({'n': nxt})   # the old moves are through: from here on they are live
                if pres != sent_presence: sent_presence = pres; out += 'event: presence\ndata: %s\n\n' % json.dumps({'present': pres})
                if not out: out = ': keep-alive\n\n'
                self.wfile.write(out.encode()); self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
            pass
        finally:
            with cond:
                if colour < 2: pr[colour] -= 1
                cond.notify_all()

class DualStackServer(http.server.ThreadingHTTPServer):    # listens on IPv4 and IPv6 (a browser may try the IPv6 address of "localhost" first)
    address_family = socket.AF_INET6
    daemon_threads = True
    def server_bind(self):
        self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        super().server_bind()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    handler = functools.partial(Handler, directory=ROOT)
    try: server = DualStackServer(('::', port), handler)
    except OSError:                                         # no IPv6 on this machine
        server = http.server.ThreadingHTTPServer(('', port), handler); server.daemon_threads = True
    print('Astro Game server on port', port, '(%d rooms loaded)' % len(rooms))
    server.serve_forever()
