from flask import Flask, render_template, url_for

app = Flask(__name__)


@app.route('/')
def home_page():
    return render_template('dashboard.html')


@app.route('/QualityControl')
def barang_masuk_page():
    return render_template('barang_masuk.html')


if __name__ == '__main__':
    app.run(host="localhost", port=3200, debug=True)
