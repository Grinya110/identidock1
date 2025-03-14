from flask import Flask, Response, request
import requests
import hashlib
import redis
app = Flask(__name__)
cache = redis.StrictRedis(host='redis', port=6379, db=0)
salt = "UNIQUE_SALT"
default_name = "Specter Center"

def get_name_vars(name: str):
    salted_name = salt + name
    return name, hashlib.sha256(salted_name.encode()).hexdigest()

@app.route('/', methods=['GET', 'POST'])
def mainpage():
    name, name_hash = get_name_vars(request.form['name'] if request.method == 'POST' else default_name)

    header = "<html><head><title>Identidock</title></head><body>"
    body = '''<form method="POST">
    Hello <input type="text" name="name" value="{0}">
    <input type="submit" value="submit">
    </form>
    <p>You look like a:
    <img src="/avatar/{1}"/>
    '''.format(name, name_hash)
    footer = '</body></html>'

    return header + body + footer

@app.route('/avatar/<name>')
def get_identicon(name):
    image = cache.get(name)
    if image is None:
        print("Cache miss", flush=True)
        r = requests.get('http://dnmonster:8080/monster/'+name+'?size=80')
        image = r.content
        cache.set(name, image)

    return Response(image, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')