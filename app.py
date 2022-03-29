import math

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
    else:
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
    else:
        return render_template('login.html')


@app.route('/BRICASH-APP/Auth/Logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login_page'))


@app.route('/BRICASH-APP/DataCenter/Sparepart', methods=['GET'], defaults={'page': 1})
@app.route('/BRICASH-APP/DataCenter/Sparepart/Page/<int:page>')
def data_center_sparepart(page):
    # Pagination
    limit = 10
    offset = page * limit - limit

    cursor_page = conn.cursor()
    cursor_page.execute("SELECT * FROM sparepart")
    total_row = cursor_page.rowcount
    total_page = math.ceil(total_row / limit)

    _next = page + 1
    _prev = page - 1

    # Show data sparepart
    cursor_show = conn.cursor()
    cursor_show.execute("SELECT * FROM sparepart ORDER BY date_createAt DESC LIMIT %s OFFSET %s", (limit, offset))
    sparepart_data = cursor_show.fetchall()

    if not session.get('username'):
        return redirect(url_for('login_page'))
    else:
        return render_template('pusat_data_sparepart.html', sparepart_data=sparepart_data, page=total_page, next=_next,
                               prev=_prev)


@app.route('/BRICASH-APP/DataCenter/Vendor', methods=['GET'], defaults={'page': 1})
@app.route('/BRICASH-APP/DataCenter/Vendor/Page/<int:page>')
def data_center_vendor(page):
    # Pagination
    limit = 10
    offset = page * limit - limit

    cursor_page = conn.cursor()
    cursor_page.execute("SELECT * FROM vendor")
    total_row = cursor_page.rowcount
    total_page = math.ceil(total_row / limit)

    _next = page + 1
    _prev = page - 1

    # Show data vendor
    cursor_show = conn.cursor()
    cursor_show.execute("SELECT * FROM vendor ORDER BY vendor_name ASC LIMIT %s OFFSET %s", (limit, offset))
    vendor_data = cursor_show.fetchall()

    if not session.get('username'):
        return redirect(url_for('login_page'))
    else:
        return render_template('pusat_data_vendor.html', vendor_data=vendor_data, row=total_row, page=total_page,
                               next=_next,
                               prev=_prev)


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

        data = (_sparepartName.upper(), _machineType.upper(), _brand.upper(), _machineSeries.upper(),
                _sparepartCode.upper())

        cursor = conn.cursor()
        cursor.execute("INSERT INTO sparepart VALUES (null, %s, %s, %s, %s, %s, null)", data)
        conn.commit()

        # i = 1
        # while i <= int(_totalAdd):
        #     sql_insert = "INSERT INTO sparepart VALUES (null, %s, %s, %s, %s, %s, null)"
        #     data = (_sparepartName.upper(), _machineType.upper(), _brand.upper(), _machineSeries.upper(),
        #             _sparepartCode.upper())
        #
        #     cursor = conn.cursor()
        #     cursor.execute(sql_insert, data)
        #     conn.commit()
        #     i = i + 1

        return redirect(url_for('data_center_sparepart'))


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
    update_data = (
        _sparepartName.upper(), _machineType.upper(), _brand.upper(), _machineSeries.upper(), _sparepartCode.upper(),
        _idTemp)
    cursor_update = conn.cursor()
    cursor_update.execute(sql, update_data)
    conn.commit()

    return redirect(url_for('data_center_sparepart'))


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

        return redirect(url_for('data_center_vendor'))


@app.route("/BRICASH-APP/DataCenter/UpdateVendor/<_id>", methods=['GET', 'POST'])
def update_data_vendor(_id):
    # Update data
    _idTemp = request.values.get('temp_id')
    _vendorName = request.values.get("vendor_name")

    sql = "UPDATE vendor SET vendor_name=%s WHERE id_vendor=%s"
    update_data = (_vendorName.upper(), _idTemp)
    cursor_update = conn.cursor()
    cursor_update.execute(sql, update_data)
    conn.commit()

    return redirect(url_for('data_center_vendor'))


@app.route('/BRICASH-APP/BarangMasuk')
def barang_masuk_page():
    # Vendor list
    cursor_vList = conn.cursor()
    cursor_vList.execute("SELECT * FROM vendor ORDER BY vendor_name ASC")
    vList = cursor_vList.fetchall()

    # Sparepart list
    cursor_sList = conn.cursor()
    cursor_sList.execute("SELECT * FROM sparepart ORDER BY sparepart_name ASC")
    sList = cursor_sList.fetchall()

    # Show data
    sql_showData = "SELECT barang_masuk.id_sender, barang_masuk.date_send, vendor.id_vendor, vendor.vendor_name, barang_masuk.nama_pengirim, barang_masuk.jabatan, list_barang_masuk.no_po, list_barang_masuk.no_do, sparepart.id_sparepart, sparepart.sparepart_name, list_barang_masuk.serial_number FROM barang_masuk INNER JOIN vendor ON barang_masuk.id_vendor = vendor.id_vendor INNER JOIN list_barang_masuk ON list_barang_masuk.id_sender = barang_masuk.id_sender INNER JOIN sparepart ON list_barang_masuk.id_sparepart = sparepart.id_sparepart;"
    cursor_showData = conn.cursor()
    cursor_showData.execute(sql_showData)
    showData = cursor_showData.fetchall()

    if not session.get('username'):
        return redirect(url_for('login_page'))
    else:
        return render_template('barang_masuk.html', vList=vList, sList=sList, showData=showData)


@app.route('/BRICASH-APP/BarangMasuk/Tambah', methods=['POST'])
def add_data_income():
    _date = request.values.get('date_achieve')
    _vendorName = request.values.get('vendor_name')
    _courierName = request.values.get('courier_name')
    _positionWorker = request.values.get('position_worker')
    _noPO = request.values.get('purchase_order')
    _noDO = request.values.get('delivery_order')
    _sparepart = request.values.get('sparepart_name')
    _serialNumber = request.values.get('serial_number')
    _totalAdd = request.values.get('total_add')

    cursor = conn.cursor()

    if 'addSingle' in request.form:
        cursor.execute("BEGIN;")
        cursor.execute("INSERT INTO barang_masuk VALUES (null, %s, %s, %s, %s);",
                       (_vendorName, _date, _courierName, _positionWorker))
        cursor.execute("SELECT LAST_INSERT_ID() INTO @id_terakhir")
        cursor.execute("INSERT INTO list_barang_masuk VALUES (null, @id_terakhir, %s, %s, %s, %s)",
                       (_noPO, _noDO, _sparepart, _serialNumber))
        cursor.execute("COMMIT")
        conn.commit()
    elif 'addMultiple' in request.form:
        print('Ini tambah sekaligus')

    return redirect(url_for('barang_masuk_page'))


# @app.route('/BRICASH-APP/BarangMasuk/Update/<_id>', methods=['GET', 'POST'])
# def update_data_income(_id):

@app.route('/BRICASH-APP/BarangMasuk/Hapus/<_id>')
def delete_data_income(_id):
    data = _id

    cursor = conn.cursor()
    cursor.execute("DELETE FROM barang_masuk WHERE id_sender=%s", data)
    conn.commit()

    return redirect(url_for('barang_masuk_page'))


@app.route('/BRICASH-APP/BarangKeluar')
def barang_keluar_page():
    if not session.get('username'):
        return redirect(url_for('login_page'))
    else:
        return render_template('barang_keluar.html')


@app.route('/BRICASH-APP/Report')
def report_page():
    if not session.get('username'):
        return redirect(url_for('login_page'))
    else:
        return 'Halaman report'


if __name__ == '__main__':
    app.run(host="localhost", port=3200, debug=True)
