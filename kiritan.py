import json
import flask
import tweepy
import pickle
from PIL import Image
from datetime import datetime

app = flask.Flask(__name__)

defaultStyle = [
	"本体/服",
	"顔効果/なし",
	"腕/普通/通常服用",
	"口/閉じ",
	"目/普通",
	"眉/普通",
	"きりたんぽ/きりたんぽノーマル",
	"アクセサリ/包丁"
]

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_TOKEN = ''
ACCESS_SECRET = ''

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
twitter = tweepy.API(auth)

try:
	with open('library.pickle', 'rb') as f:
		library = pickle.load(f)
except:
	library = {}

@app.route('/', methods=['GET'])
def get():
	vals = list(library.values())
	init = vals[-1] if len(vals) else defaultStyle
	return flask.render_template('index.html', lib=library, init=init, host=flask.request.host)

@app.route('/', methods=['POST'])
def post():
	canvas = Image.new('RGB', (500, 775), (255, 255, 255))
	
	for img in json.loads(flask.request.form['data']):
		img = Image.open('static/%s.png' % img, 'r')
		canvas.paste(img, (0, 0), img)
	
	canvas = canvas.resize((canvas.size[0] * 3, canvas.size[1] * 3), Image.BICUBIC)
	header = canvas.crop((0, 1100, 0 + 1500, 1100 + 500))
	icon = canvas.crop((310, 390, 310 + 710, 390 + 710))
	
	#canvas.save('canvas.png', 'png')
	header.save('header.png', 'png')
	icon.save('icon.png', 'png')
	
	twitter.update_profile_banner('header.png')
	twitter.update_profile_image('icon.png')
	
	with open('library.pickle', 'wb') as f:
		date = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
		library[date] = flask.request.form['data']
		pickle.dump(library, f)
	
	return flask.redirect('/', code=302)
	
@app.route('/icon.png')
def icon():
	return flask.send_from_directory('./', 'icon.png')
	
if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=55555)
