from flask import Flask, render_template, url_for

app = Flask(__name__)


@app.route('/')
@app.route('/BRICASH-APP/Dashboard')
def home_page():
    return render_template('dashboard.html')


@app.route('/BRICASH-APP/Auth')
def login_page():
    return render_template('login.html')


@app.route('/BRICASH-APP/BarangMasuk')
def barang_masuk_page():
    return render_template('barang_masuk.html')


if __name__ == '__main__':
    app.run(host="localhost", port=3200, debug=True)
