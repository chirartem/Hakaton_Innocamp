from flask import Flask, render_template, url_for, redirect, request, g
import sqlite3

app = Flask(__name__)
ips = {}

def get_db(daba):
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = sqlite3.connect(daba)
	return db

@app.route('/')
def index():
	return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		return render_template('autorisation.html')
	elif request.method == 'POST':
		curs = get_db('users.db').cursor()
		req = request.form
		lp = dict(curs.execute('SELECT * FROM Users').fetchall())
		if req['name'] in lp:
			if req['password'] == lp[req['name']]:
				ip_addr = request.remote_addr
				ips[ip_addr] = req['name']
				return redirect(url_for('info'))
		return redirect(url_for('login'))

@app.route('/info', methods=['GET', 'POST'])
def info():
	if request.method == 'GET':
		ip_addr = request.remote_addr
		if ip_addr in ips:
			curs = get_db('info.db').cursor()
			data = curs.execute('SELECT * FROM info').fetchall()
			print(data)
			return render_template('general.html',data=data)
		else:
			return redirect(url_for('login'))
	elif request.method == 'POST':
		return redirect(url_for('info'))
if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True, use_reloader=True)