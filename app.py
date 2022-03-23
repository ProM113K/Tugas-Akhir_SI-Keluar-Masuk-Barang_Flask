from flask import Flask, render_template, url_for, request, session, redirect, flash
from flaskext.mysql import MySQL

from flask_session import Session
from mysql_env import *

app = Flask(__name__)
app.secret_key = 'f5c50af369fac1ec902'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# setting mysql
mysql = MySQL()
app.config['SECRET_KEY'] = 'ec9439cfc6c796ae2029594d'
app.config['MYSQL_DATABASE_USER'] = db_user
app.config['MYSQL_DATABASE_PASSWORD'] = db_password
app.config['MYSQL_DATABASE_DB'] = db_name
app.config['MYSQL_DATABASE_HOST'] = db_host
mysql.init_app(app)
conn = mysql.connect()


@app.route('/')
@app.route('/BRICASH-APP/Dashboard')
def home_page():
    if not session.get('username'):
        return redirect(url_for('login_page'))
    return render_template('dashboard.html')


@app.route('/BRICASH-APP/Auth', methods=['GET', 'POST'])
def login_page():
    _username = request.form.get('user')
    _password = request.form.get('pass')

    if request.method == 'POST':
        sql = 'SELECT * FROM user WHERE username=%s'

        cursor = conn.cursor()
        cursor.execute(sql, _username)
        result = cursor.fetchone()
        akun_cek = cursor.rowcount

        if akun_cek != 0 and _username == result[1] and _password == result[2]:
            session['username'] = request.form['user']
            flash(f'Anda login sebagai {result[3]}', category='success')
            return redirect(url_for('home_page'))
        elif not result:
            return redirect(url_for('login_page'))
        else:
            return redirect(url_for('login_page'))

    if 'username' in session:
        username = session['username']
        return redirect(url_for('home_page', username=username))
    return render_template('login.html')


@app.route('/BRICASH-APP/Auth/Logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login_page'))


@app.route('/BRICASH-APP/DataCenter', methods=['GET', 'POST'])
def data_center():
    # Show data sparepart
    sql_show_sparepart = "SELECT * FROM sparepart ORDER BY date_createAt DESC"

    cursor_show = conn.cursor()
    cursor_show.execute(sql_show_sparepart)
    sparepart_data = cursor_show.fetchall()

    # Show data vendor
    sql_show_vendor = "SELECT * FROM vendor ORDER BY vendor_name ASC"

    cursor_show = conn.cursor()
    cursor_show.execute(sql_show_vendor)
    vendor_data = cursor_show.fetchall()

    if not session.get('username'):
        return redirect(url_for('login_page'))
    else:
        return render_template('pusat_data.html', sparepart_data=sparepart_data, vendor_data=vendor_data)


@app.route("/BRICASH-APP/DataCenter/AddSparepart", methods=["GET", "POST"])
def add_data_sparepart():
    if not session.get('username'):
        return redirect(url_for('login_page'))
    else:
        # Insert data sparepart
        _sparepartName = request.values.get("sparepart_name")
        _machineType = request.values.get("machine_type")
        _brand = request.values.get("brand")
        _machineSeries = request.values.get("machine_series")
        _sparepartCode = request.values.get("sparepart_code")

        sql_insert = "INSERT INTO sparepart VALUES (null, %s, %s, %s, %s, %s, null)"
        data = (_sparepartName.upper(), _machineType.upper(), _brand.upper(), _machineSeries.upper(), _sparepartCode.upper())

        cursor = conn.cursor()
        cursor.execute(sql_insert, data)
        conn.commit()

        return redirect(url_for('data_center'))


@app.route("/BRICASH-APP/DataCenter/DeleteSparepart/<_id>")
def delete_data_sparepart(_id):
    sql = "DELETE FROM sparepart WHERE id_sparepart = %s"

    data = _id
    cursor = conn.cursor()
    cursor.execute(sql, data)
    conn.commit()

    return redirect(url_for("data_center"))


@app.route("/BRICASH-APP/DataCenter/UpdateSparepart/<_id>", methods=['GET', 'POST'])
def update_data_sparepart(_id):
    # Update data
    _idTemp = request.values.get('temp_id')
    _sparepartName = request.values.get("sparepart_name")
    _machineType = request.values.get("machine_type")
    _brand = request.values.get("brand")
    _machineSeries = request.values.get("machine_series")
    _sparepartCode = request.values.get("sparepart_code")

    sql = "UPDATE sparepart SET sparepart_name=%s, machine_type=%s, brand=%s, machine_series=%s, kd_sparepart=%s WHERE id_sparepart=%s"
    update_data = (_sparepartName.upper(), _machineType.upper(), _brand.upper(), _machineSeries.upper(), _sparepartCode.upper(), _idTemp)
    cursor_update = conn.cursor()
    cursor_update.execute(sql, update_data)
    conn.commit()

    return redirect(url_for('data_center'))


@app.route("/BRICASH-APP/DataCenter/TambahVendor", methods=['GET', 'POST'])
def add_data_vendor():
    if not session.get('username'):
        return redirect(url_for('login_page'))
    else:
        # Insert data vendor
        _vendorName = request.values.get("vendor_name")

        sql_insert = "INSERT INTO vendor VALUES (null, %s)"
        data = (_vendorName.upper())

        cursor = conn.cursor()
        cursor.execute(sql_insert, data)
        conn.commit()

        return redirect(url_for('data_center'))


@app.route("/BRICASH-APP/DataCenter/UpdateVendor/<_id>", methods=['GET', 'POST'])
def update_data_vendor(_id):
    # Update data
    _idTemp = request.values.get('temp_id')
    _vendorName = request.values.get("vendor_name")

    sql = "UPDATE vendor SET vendor_name=%s WHERE id_vendor=%s"
    update_data = (_vendorName, _idTemp)
    cursor_update = conn.cursor()
    cursor_update.execute(sql, update_data)
    conn.commit()

    return redirect(url_for('data_center'))


@app.route('/BRICASH-APP/BarangMasuk')
def barang_masuk_page():
    if not session.get('username'):
        return redirect(url_for('login_page'))
    return render_template('barang_masuk.html')


@app.route('/BRICASH-APP/BarangKeluar')
def barang_keluar_page():
    if not session.get('username'):
        return redirect(url_for('login_page'))
    return render_template('barang_keluar.html')


@app.route('/BRICASH-APP/Report')
def report_page():
    if not session.get('username'):
        return redirect(url_for('login_page'))
    return 'Halaman report'


if __name__ == '__main__':
    app.run(host="localhost", port=3200, debug=True)
