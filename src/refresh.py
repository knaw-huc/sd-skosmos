# -*- coding: utf-8 -*-
from flask import Flask,render_template,request

app = Flask(__name__)

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/refresh', methods=['POST'])
def refresh():
    open('/tmp/refresh','w')
    return render_template('done.html')

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=80)

