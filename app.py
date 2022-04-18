import math

import pdfkit
from flask import Flask, render_template, url_for, request, session, redirect, flash, make_response
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
    # Show data income
    cursor_income = conn.cursor()
    cursor_income.execute(
        "SELECT pengiriman.date_send,vendor.vendor_name,pengiriman.nama_petugas,list_barang.no_po,list_barang.no_do,sparepart.sparepart_name,list_barang.serial_number FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor = vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender = pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart = sparepart.id_sparepart WHERE pengiriman.status_barang = 'masuk' AND MONTH(pengiriman.date_send) = MONTH(CURRENT_DATE()) AND YEAR(pengiriman.date_send) = YEAR(CURRENT_DATE()) ORDER BY pengiriman.date_send DESC;")
    data_income = cursor_income.fetchall()
    cursor_income.close()

    # Show data outcome
    cursor_outcome = conn.cursor()
    cursor_outcome.execute(
        "SELECT pengiriman.date_send,vendor.vendor_name,pengiriman.nama_petugas,list_barang.no_po,sparepart.sparepart_name,list_barang.serial_number FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor = vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender = pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart = sparepart.id_sparepart WHERE pengiriman.status_barang = 'keluar' AND MONTH(pengiriman.date_send) = MONTH(CURRENT_DATE()) AND YEAR(pengiriman.date_send) = YEAR(CURRENT_DATE()) ORDER BY pengiriman.date_send DESC;")
    data_outcome = cursor_outcome.fetchall()
    cursor_outcome.close()

    # Show total income
    cursor_income_total = conn.cursor()
    cursor_income_total.execute(
        "SELECT COUNT(*) FROM pengiriman WHERE status_barang = 'masuk' AND MONTH(pengiriman.date_send) = MONTH(CURRENT_DATE()) AND YEAR(pengiriman.date_send) = YEAR(CURRENT_DATE())")
    data_income_total = cursor_income_total.fetchall()[0][0]

    # Show total outcome
    cursor_outcome_total = conn.cursor()
    cursor_outcome_total.execute(
        "SELECT COUNT(*) FROM pengiriman WHERE status_barang = 'keluar' AND MONTH(pengiriman.date_send) = MONTH(CURRENT_DATE()) AND YEAR(pengiriman.date_send) = YEAR(CURRENT_DATE())")
    data_outcome_total = cursor_outcome_total.fetchall()[0][0]

    if not session.get('username'):
        return redirect(url_for('login_page'))
    else:
        return render_template('dashboard.html', data_income=data_income, data_outcome=data_outcome,
                               data_income_total=data_income_total, data_outcome_total=data_outcome_total,
                               data_total=data_income_total + data_outcome_total)


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
    cursor_show.execute(
        "SELECT * FROM sparepart ORDER BY sparepart_name ASC LIMIT %s OFFSET %s", (limit, offset))
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
    cursor_show.execute(
        "SELECT * FROM vendor ORDER BY vendor_name ASC LIMIT %s OFFSET %s", (limit, offset))
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
        cursor.execute(
            "INSERT INTO sparepart VALUES (null, %s, %s, %s, %s, %s, null)", data)
        conn.commit()

        return redirect(url_for('data_center_sparepart'))


@app.route("/BRICASH-APP/DataCenter/UpdateSparepart/<_id>", methods=['GET', 'POST'])
def update_data_sparepart(_id):
    # Update data
    _idTemp = _id
    _sparepartName = request.values.get("sparepart_name")
    _machineType = request.values.get("machine_type")
    _brand = request.values.get("brand")
    _machineSeries = request.values.get("machine_series")
    _sparepartCode = request.values.get("sparepart_code")

    sql = "UPDATE sparepart SET sparepart_name=%s, machine_type=%s, brand=%s, machine_series=%s, kd_sparepart=%s WHERE id_sparepart=%s"
    update_data = (
        _sparepartName.upper(), _machineType.upper(), _brand.upper(
        ), _machineSeries.upper(), _sparepartCode.upper(),
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
    _idTemp = _id
    _vendorName = request.values.get("vendor_name")

    sql = "UPDATE vendor SET vendor_name=%s WHERE id_vendor=%s"
    update_data = (_vendorName.upper(), _idTemp)
    cursor_update = conn.cursor()
    cursor_update.execute(sql, update_data)
    conn.commit()

    return redirect(url_for('data_center_vendor'))


@app.route('/BRICASH-APP/BarangMasuk', methods=['GET'])
@app.route('/BRICASH-APP/BarangMasuk/Search', methods=['GET'], defaults={'page': 1})
@app.route('/BRICASH-APP/BarangMasuk/Page/<int:page>')
def barang_masuk_page(page):
    # Vendor list
    cursor_vList = conn.cursor()
    cursor_vList.execute("SELECT * FROM vendor ORDER BY vendor_name ASC")
    vList = cursor_vList.fetchall()

    # Sparepart list
    cursor_sList = conn.cursor()
    cursor_sList.execute("SELECT * FROM sparepart ORDER BY sparepart_name ASC")
    sList = cursor_sList.fetchall()

    # Pagination
    limit = 10
    offset = page * limit - limit

    cursor_page = conn.cursor()
    cursor_page.execute("SELECT * FROM sparepart")
    total_row = cursor_page.rowcount
    total_page = math.ceil(total_row / limit)

    _next = page + 1
    _prev = page - 1

    # Show data
    _category = request.values.get('kategori')
    _search = request.values.get('search_box')

    sql_showData = None
    if _category == "tgl":
        sql_showData = "SELECT pengiriman.id_sender, pengiriman.date_send AS tanggal, vendor.id_vendor, vendor.vendor_name AS nama_vendor, pengiriman.nama_petugas AS petugas, list_barang.no_po AS surat_PO, list_barang.no_do AS surat_DO, sparepart.id_sparepart, sparepart.sparepart_name AS nama_sparepart, list_barang.serial_number AS SN, list_barang.id_list_barang FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor = vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender = pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart = sparepart.id_sparepart WHERE pengiriman.status_barang = 'masuk' AND pengiriman.nama_petugas LIKE '%%' AND pengiriman.date_send LIKE '%" + \
                       _search + "%' AND vendor.vendor_name LIKE '%%' AND sparepart.sparepart_name LIKE '%%' AND list_barang.no_po LIKE '%%' AND list_barang.no_do LIKE '%%' AND list_barang.serial_number LIKE '%%'ORDER BY pengiriman.date_send DESC LIMIT " + \
                       str(limit) + " OFFSET " + str(offset) + ";"
    elif _category == "sender":
        sql_showData = "SELECT pengiriman.id_sender, pengiriman.date_send AS tanggal, vendor.id_vendor, vendor.vendor_name AS nama_vendor, pengiriman.nama_petugas AS petugas, list_barang.no_po AS surat_PO, list_barang.no_do AS surat_DO, sparepart.id_sparepart, sparepart.sparepart_name AS nama_sparepart, list_barang.serial_number AS SN, list_barang.id_list_barang FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor = vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender = pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart = sparepart.id_sparepart WHERE pengiriman.status_barang = 'masuk' AND pengiriman.nama_petugas LIKE '%" + \
                       _search + "%' AND pengiriman.date_send LIKE '%""%' AND vendor.vendor_name LIKE '%%' AND sparepart.sparepart_name LIKE '%%' AND list_barang.no_po LIKE '%%' AND list_barang.no_do LIKE '%%' AND list_barang.serial_number LIKE '%%'ORDER BY pengiriman.date_send DESC LIMIT " + \
                       str(limit) + " OFFSET " + str(offset) + ";"
    elif _category == "po":
        sql_showData = "SELECT pengiriman.id_sender, pengiriman.date_send AS tanggal, vendor.id_vendor, vendor.vendor_name AS nama_vendor, pengiriman.nama_petugas AS petugas, list_barang.no_po AS surat_PO, list_barang.no_do AS surat_DO, sparepart.id_sparepart, sparepart.sparepart_name AS nama_sparepart, list_barang.serial_number AS SN, list_barang.id_list_barang FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor = vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender = pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart = sparepart.id_sparepart WHERE pengiriman.status_barang = 'masuk' AND pengiriman.nama_petugas LIKE '%%' AND pengiriman.date_send LIKE '%""%' AND vendor.vendor_name LIKE '%%' AND sparepart.sparepart_name LIKE '%%' AND list_barang.no_po LIKE '%" + \
                       _search + "%' AND list_barang.no_do LIKE '%%' AND list_barang.serial_number LIKE '%%'ORDER BY pengiriman.date_send DESC LIMIT " + \
                       str(limit) + " OFFSET " + str(offset) + ";"
    elif _category == "do":
        sql_showData = "SELECT pengiriman.id_sender, pengiriman.date_send AS tanggal, vendor.id_vendor, vendor.vendor_name AS nama_vendor, pengiriman.nama_petugas AS petugas, list_barang.no_po AS surat_PO, list_barang.no_do AS surat_DO, sparepart.id_sparepart, sparepart.sparepart_name AS nama_sparepart, list_barang.serial_number AS SN, list_barang.id_list_barang FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor = vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender = pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart = sparepart.id_sparepart WHERE pengiriman.status_barang = 'masuk' AND pengiriman.nama_petugas LIKE '%%' AND pengiriman.date_send LIKE '%""%' AND vendor.vendor_name LIKE '%%' AND sparepart.sparepart_name LIKE '%%' AND list_barang.no_po LIKE '%%' AND list_barang.no_do LIKE '%" + \
                       _search + "%' AND list_barang.serial_number LIKE '%%'ORDER BY pengiriman.date_send DESC LIMIT " + \
                       str(limit) + " OFFSET " + str(offset) + ";"
    elif _category == "sparepart":
        sql_showData = "SELECT pengiriman.id_sender, pengiriman.date_send AS tanggal, vendor.id_vendor, vendor.vendor_name AS nama_vendor, pengiriman.nama_petugas AS petugas, list_barang.no_po AS surat_PO, list_barang.no_do AS surat_DO, sparepart.id_sparepart, sparepart.sparepart_name AS nama_sparepart, list_barang.serial_number AS SN, list_barang.id_list_barang FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor = vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender = pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart = sparepart.id_sparepart WHERE pengiriman.status_barang = 'masuk' AND pengiriman.nama_petugas LIKE '%%' AND pengiriman.date_send LIKE '%""%' AND vendor.vendor_name LIKE '%%' AND sparepart.sparepart_name LIKE '%" + \
                       _search + "%' AND list_barang.no_po LIKE '%%' AND list_barang.no_do LIKE '%%' AND list_barang.serial_number LIKE '%%'ORDER BY pengiriman.date_send DESC LIMIT " + \
                       str(limit) + " OFFSET " + str(offset) + ";"
    elif _category == "sn":
        sql_showData = "SELECT pengiriman.id_sender, pengiriman.date_send AS tanggal, vendor.id_vendor, vendor.vendor_name AS nama_vendor, pengiriman.nama_petugas AS petugas, list_barang.no_po AS surat_PO, list_barang.no_do AS surat_DO, sparepart.id_sparepart, sparepart.sparepart_name AS nama_sparepart, list_barang.serial_number AS SN, list_barang.id_list_barang FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor = vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender = pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart = sparepart.id_sparepart WHERE pengiriman.status_barang = 'masuk' AND pengiriman.nama_petugas LIKE '%%' AND pengiriman.date_send LIKE '%""%' AND vendor.vendor_name LIKE '%%' AND sparepart.sparepart_name LIKE '%%' AND list_barang.no_po LIKE '%%' AND list_barang.no_do LIKE '%%' AND list_barang.serial_number LIKE '%" + \
                       _search + "%'ORDER BY pengiriman.date_send DESC LIMIT " + \
                       str(limit) + " OFFSET " + str(offset) + ";"
    elif _category == "vendor":
        sql_showData = "SELECT pengiriman.id_sender, pengiriman.date_send AS tanggal, vendor.id_vendor, vendor.vendor_name AS nama_vendor, pengiriman.nama_petugas AS petugas, list_barang.no_po AS surat_PO, list_barang.no_do AS surat_DO, sparepart.id_sparepart, sparepart.sparepart_name AS nama_sparepart, list_barang.serial_number AS SN, list_barang.id_list_barang FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor = vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender = pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart = sparepart.id_sparepart WHERE pengiriman.status_barang = 'masuk' AND pengiriman.nama_petugas LIKE '%%' AND pengiriman.date_send LIKE '%""%' AND vendor.vendor_name LIKE '%" + \
                       _search + "%' AND sparepart.sparepart_name LIKE '%%' AND list_barang.no_po LIKE '%%' AND list_barang.no_do LIKE '%%' AND list_barang.serial_number LIKE '%%'ORDER BY pengiriman.date_send DESC LIMIT " + \
                       str(limit) + " OFFSET " + str(offset) + ";"
    else:
        sql_showData = "SELECT pengiriman.id_sender, pengiriman.date_send AS tanggal, vendor.id_vendor, vendor.vendor_name AS nama_vendor, pengiriman.nama_petugas AS petugas, list_barang.no_po AS surat_PO, list_barang.no_do AS surat_DO, sparepart.id_sparepart, sparepart.sparepart_name AS nama_sparepart, list_barang.serial_number AS SN, list_barang.id_list_barang FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor = vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender = pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart = sparepart.id_sparepart WHERE pengiriman.status_barang = 'masuk' AND pengiriman.nama_petugas LIKE '%%' AND pengiriman.date_send LIKE '%%' AND vendor.vendor_name LIKE '%%' AND sparepart.sparepart_name LIKE '%%' AND list_barang.no_po LIKE '%%' AND list_barang.no_do LIKE '%%' AND list_barang.serial_number LIKE '%%'ORDER BY pengiriman.date_send DESC LIMIT " + \
                       str(limit) + " OFFSET " + str(offset) + ";"

    cursor_showData = conn.cursor()
    cursor_showData.execute(sql_showData)
    showData = cursor_showData.fetchall()

    if not session.get('username'):
        return redirect(url_for('login_page'))
    else:
        return render_template('barang_masuk.html', vList=vList, sList=sList, showData=showData, page=total_page,
                               next=_next,
                               prev=_prev)


@app.route('/BRICASH-APP/BarangMasuk/Tambah', methods=['POST'])
def add_data_income():
    _date = request.values.get('date_achieve')
    _vendorName = request.values.get('vendor_name')
    _courierName = request.values.get('courier_name')
    _noPO = request.values.get('purchase_order')
    _noDO = request.values.get('delivery_order')
    _sparepart = request.values.get('sparepart_name')
    _serialNumber = request.values.get('serial_number')

    cursor = conn.cursor()

    if 'addSingle' in request.form:
        cursor.execute("BEGIN;")
        cursor.execute("INSERT INTO pengiriman VALUES (null, %s, %s, %s, 'masuk');",
                       (_vendorName, _date, _courierName))
        cursor.execute("SELECT LAST_INSERT_ID() INTO @id_terakhir")
        cursor.execute("INSERT INTO list_barang VALUES (null, @id_terakhir, %s, %s, %s, %s, null)",
                       (_noPO.upper(), _noDO.upper(), _sparepart, _serialNumber.upper()))
        cursor.execute("COMMIT")
        conn.commit()

    return redirect(url_for('barang_masuk_page'))


@app.route('/BRICASH-APP/BarangMasuk/Update/<_idsender>/<_idlist>', methods=['GET', 'POST'])
def update_data_income(_idsender, _idlist):
    # Update data
    _idTemp = _idsender
    _idTempListBarang = _idlist
    _date = request.values.get('date_achieve')
    _vendorName = request.values.get('vendor_name')
    _courierName = request.values.get('courier_name')
    _noPO = request.values.get('purchase_order')
    _noDO = request.values.get('delivery_order')
    _sparepart = request.values.get('sparepart_name')
    _serialNumber = request.values.get('serial_number')

    cursor = conn.cursor()
    cursor.execute("BEGIN;")
    cursor.execute(
        'UPDATE list_barang SET no_po=%s, no_do=%s, id_sparepart=%s, serial_number=%s WHERE id_list_barang=%s;',
        (_noPO.upper(), _noDO.upper(), _sparepart, _serialNumber.upper(), _idTempListBarang))
    cursor.execute("UPDATE pengiriman SET id_vendor=%s, date_send=%s, nama_petugas=%s WHERE id_sender=%s;",
                   (_vendorName, _date, _courierName, _idTemp))
    cursor.execute("COMMIT;")
    conn.commit()

    return redirect(url_for('barang_masuk_page'))


@app.route('/BRICASH-APP/BarangMasuk/Hapus/<_id>')
def delete_data_income(_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pengiriman WHERE id_sender=%s", _id)
    conn.commit()

    return redirect(url_for('barang_masuk_page'))


@app.route('/BRICASH-APP/BarangKeluar', methods=['GET'])
@app.route('/BRICASH-APP/BarangKeluar/Search', methods=['GET'], defaults={'page': 1})
@app.route('/BRICASH-APP/BarangKeluar/Page/<int:page>')
def barang_keluar_page(page):
    # Vendor list
    cursor_vList = conn.cursor()
    cursor_vList.execute("SELECT * FROM vendor ORDER BY vendor_name ASC")
    vList = cursor_vList.fetchall()

    # Sparepart list
    cursor_sList = conn.cursor()
    cursor_sList.execute("SELECT * FROM sparepart ORDER BY sparepart_name ASC")
    sList = cursor_sList.fetchall()

    # Pagination
    limit = 10
    offset = page * limit - limit

    cursor_page = conn.cursor()
    cursor_page.execute("SELECT * FROM sparepart")
    total_row = cursor_page.rowcount
    total_page = math.ceil(total_row / limit)

    _next = page + 1
    _prev = page - 1

    # Show data
    _category = request.values.get('kategori')
    _search = request.values.get('search_box')

    sql_showData = None
    if _category == "tgl":
        sql_showData = "SELECT pengiriman.id_sender, pengiriman.date_send, vendor.id_vendor, vendor.vendor_name, pengiriman.nama_petugas, list_barang.no_po, sparepart.id_sparepart, sparepart.sparepart_name, list_barang.serial_number, list_barang.id_list_barang, list_barang.keterangan FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor = vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender = pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart = sparepart.id_sparepart WHERE pengiriman.status_barang = 'keluar' AND pengiriman.nama_petugas LIKE '%%' AND pengiriman.date_send LIKE '%" + \
                       _search + "%' AND vendor.vendor_name LIKE '%%' AND sparepart.sparepart_name LIKE '%%' AND list_barang.no_po LIKE '%%' AND list_barang.no_do LIKE '%%' AND list_barang.serial_number LIKE '%%'ORDER BY pengiriman.date_send DESC LIMIT " + \
                       str(limit) + " OFFSET " + str(offset) + ";"
    elif _category == "sender":
        sql_showData = "SELECT pengiriman.id_sender, pengiriman.date_send, vendor.id_vendor, vendor.vendor_name, pengiriman.nama_petugas, list_barang.no_po, sparepart.id_sparepart, sparepart.sparepart_name, list_barang.serial_number, list_barang.id_list_barang, list_barang.keterangan FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor = vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender = pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart = sparepart.id_sparepart WHERE pengiriman.status_barang = 'keluar' AND pengiriman.nama_petugas LIKE '%" + \
                       _search + "%' AND pengiriman.date_send LIKE '%""%' AND vendor.vendor_name LIKE '%%' AND sparepart.sparepart_name LIKE '%%' AND list_barang.no_po LIKE '%%' AND list_barang.no_do LIKE '%%' AND list_barang.serial_number LIKE '%%'ORDER BY pengiriman.date_send DESC LIMIT " + \
                       str(limit) + " OFFSET " + str(offset) + ";"
    elif _category == "po":
        sql_showData = "SELECT pengiriman.id_sender, pengiriman.date_send, vendor.id_vendor, vendor.vendor_name, pengiriman.nama_petugas, list_barang.no_po, sparepart.id_sparepart, sparepart.sparepart_name, list_barang.serial_number, list_barang.id_list_barang, list_barang.keterangan FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor = vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender = pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart = sparepart.id_sparepart WHERE pengiriman.status_barang = 'keluar' AND pengiriman.nama_petugas LIKE '%%' AND pengiriman.date_send LIKE '%""%' AND vendor.vendor_name LIKE '%%' AND sparepart.sparepart_name LIKE '%%' AND list_barang.no_po LIKE '%" + \
                       _search + "%' AND list_barang.no_do LIKE '%%' AND list_barang.serial_number LIKE '%%'ORDER BY pengiriman.date_send DESC LIMIT " + \
                       str(limit) + " OFFSET " + str(offset) + ";"
    elif _category == "ket":
        sql_showData = "SELECT pengiriman.id_sender, pengiriman.date_send, vendor.id_vendor, vendor.vendor_name, pengiriman.nama_petugas, list_barang.no_po, sparepart.id_sparepart, sparepart.sparepart_name, list_barang.serial_number, list_barang.id_list_barang, list_barang.keterangan FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor = vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender = pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart = sparepart.id_sparepart WHERE pengiriman.status_barang = 'keluar' AND pengiriman.nama_petugas LIKE '%%' AND pengiriman.date_send LIKE '%""%' AND vendor.vendor_name LIKE '%%' AND sparepart.sparepart_name LIKE '%%' AND list_barang.no_po LIKE '%%' AND list_barang.keterangan LIKE '%" + \
                       _search + "%' AND list_barang.serial_number LIKE '%%'ORDER BY pengiriman.date_send DESC LIMIT " + \
                       str(limit) + " OFFSET " + str(offset) + ";"
    elif _category == "sparepart":
        sql_showData = "SELECT pengiriman.id_sender, pengiriman.date_send, vendor.id_vendor, vendor.vendor_name, pengiriman.nama_petugas, list_barang.no_po, sparepart.id_sparepart, sparepart.sparepart_name, list_barang.serial_number, list_barang.id_list_barang, list_barang.keterangan FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor = vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender = pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart = sparepart.id_sparepart WHERE pengiriman.status_barang = 'keluar' AND pengiriman.nama_petugas LIKE '%%' AND pengiriman.date_send LIKE '%""%' AND vendor.vendor_name LIKE '%%' AND sparepart.sparepart_name LIKE '%" + \
                       _search + "%' AND list_barang.no_po LIKE '%%' AND list_barang.no_do LIKE '%%' AND list_barang.serial_number LIKE '%%'ORDER BY pengiriman.date_send DESC LIMIT " + \
                       str(limit) + " OFFSET " + str(offset) + ";"
    elif _category == "sn":
        sql_showData = "SELECT pengiriman.id_sender, pengiriman.date_send, vendor.id_vendor, vendor.vendor_name, pengiriman.nama_petugas, list_barang.no_po, sparepart.id_sparepart, sparepart.sparepart_name, list_barang.serial_number, list_barang.id_list_barang, list_barang.keterangan FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor = vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender = pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart = sparepart.id_sparepart WHERE pengiriman.status_barang = 'keluar' AND pengiriman.nama_petugas LIKE '%%' AND pengiriman.date_send LIKE '%""%' AND vendor.vendor_name LIKE '%%' AND sparepart.sparepart_name LIKE '%%' AND list_barang.no_po LIKE '%%' AND list_barang.no_do LIKE '%%' AND list_barang.serial_number LIKE '%" + \
                       _search + "%'ORDER BY pengiriman.date_send DESC LIMIT " + \
                       str(limit) + " OFFSET " + str(offset) + ";"
    elif _category == "vendor":
        sql_showData = "SELECT pengiriman.id_sender, pengiriman.date_send, vendor.id_vendor, vendor.vendor_name, pengiriman.nama_petugas, list_barang.no_po, sparepart.id_sparepart, sparepart.sparepart_name, list_barang.serial_number, list_barang.id_list_barang, list_barang.keterangan FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor = vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender = pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart = sparepart.id_sparepart WHERE pengiriman.status_barang = 'keluar' AND pengiriman.nama_petugas LIKE '%%' AND pengiriman.date_send LIKE '%""%' AND vendor.vendor_name LIKE '%" + \
                       _search + "%' AND sparepart.sparepart_name LIKE '%%' AND list_barang.no_po LIKE '%%' AND list_barang.no_do LIKE '%%' AND list_barang.serial_number LIKE '%%'ORDER BY pengiriman.date_send DESC LIMIT " + \
                       str(limit) + " OFFSET " + str(offset) + ";"
    else:
        sql_showData = "SELECT pengiriman.id_sender, pengiriman.date_send, vendor.id_vendor, vendor.vendor_name, pengiriman.nama_petugas, list_barang.no_po, sparepart.id_sparepart, sparepart.sparepart_name, list_barang.serial_number, list_barang.id_list_barang, list_barang.keterangan FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor = vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender = pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart = sparepart.id_sparepart WHERE pengiriman.status_barang = 'keluar' AND pengiriman.nama_petugas LIKE '%%' AND pengiriman.date_send LIKE '%%' AND vendor.vendor_name LIKE '%%' AND sparepart.sparepart_name LIKE '%%' AND list_barang.no_po LIKE '%%' AND list_barang.serial_number LIKE '%%'ORDER BY pengiriman.date_send DESC LIMIT " + \
                       str(limit) + " OFFSET " + str(offset) + ";"

    cursor_showData = conn.cursor()
    cursor_showData.execute(sql_showData)
    showData = cursor_showData.fetchall()

    if not session.get('username'):
        return redirect(url_for('login_page'))
    else:
        return render_template('barang_keluar.html', vList=vList, sList=sList, showData=showData, page=total_page,
                               next=_next,
                               prev=_prev)


@app.route('/BRICASH-APP/BarangKeluar/Tambah', methods=['POST'])
def add_data_outcome():
    _date = request.values.get('date_achieve')
    _vendorName = request.values.get('vendor_name')
    _courierName = request.values.get('courier_name')
    _noPO = request.values.get('purchase_order')
    _sparepart = request.values.get('sparepart_name')
    _serialNumber = request.values.get('serial_number')
    _keterangan = request.values.get('keterangan')

    cursor = conn.cursor()

    cursor.execute("BEGIN;")
    cursor.execute("INSERT INTO pengiriman VALUES (null, %s, %s, %s, 'keluar');",
                   (_vendorName, _date, _courierName))
    cursor.execute("SELECT LAST_INSERT_ID() INTO @id_terakhir")
    cursor.execute("INSERT INTO list_barang VALUES (null, @id_terakhir, %s, '-', %s, %s, %s)",
                   (_noPO.upper(), _sparepart, _serialNumber.upper(), _keterangan))
    cursor.execute("COMMIT")
    conn.commit()

    return redirect(url_for('barang_keluar_page'))


@app.route('/BRICASH-APP/BarangKeluar/Update/<_idsender>/<_idlist>', methods=['POST'])
def update_data_outcome(_idsender, _idlist):
    # Update data
    _idTemp = _idsender
    _idTempListBarang = _idlist
    _date = request.values.get('date_achieve')
    _vendorName = request.values.get('vendor_name')
    _courierName = request.values.get('courier_name')
    _noPO = request.values.get('purchase_order')
    _sparepart = request.values.get('sparepart_name')
    _serialNumber = request.values.get('serial_number')
    _keterangan = request.values.get('keterangan')

    cursor = conn.cursor()
    cursor.execute("BEGIN;")
    cursor.execute(
        'UPDATE list_barang SET no_po=%s, id_sparepart=%s, serial_number=%s, keterangan=%s WHERE id_list_barang=%s;',
        (_noPO.upper(), _sparepart, _serialNumber.upper(), _keterangan, _idTempListBarang))
    cursor.execute("UPDATE pengiriman SET id_vendor=%s, date_send=%s, nama_petugas=%s WHERE id_sender=%s;",
                   (_vendorName, _date, _courierName, _idTemp))
    cursor.execute("COMMIT;")
    conn.commit()

    return redirect(url_for('barang_keluar_page'))


@app.route('/BRICASH-APP/BarangKeluar/Hapus/<_id>')
def delete_data_outcome(_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pengiriman WHERE id_sender=%s", _id)
    conn.commit()

    return redirect(url_for('barang_keluar_page'))


@app.route('/BRICASH-APP/Report', defaults={'_btn': ''})
@app.route('/BRICASH-APP/Report/Search/<_btn>', methods=['POST'])
@app.route('/BRICASH-APP/Report/Cat/<_btn>', methods=['GET'])
def report_page(_btn):
    cursor = conn.cursor()
    data = None
    global data_filter

    date_start = request.values.get('date_start')
    date_end = request.values.get('date_end')

    # Show data
    if _btn == "Keluar":
        cursor.execute(
            'SELECT pengiriman.date_send, vendor.vendor_name, pengiriman.nama_petugas, list_barang.no_po, sparepart.sparepart_name, list_barang.serial_number, list_barang.keterangan FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor = vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender = pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart = sparepart.id_sparepart WHERE pengiriman.status_barang = "keluar" ORDER BY pengiriman.date_send DESC;')
        data = cursor.fetchall()
        data_filter = data

    elif _btn == "Masuk":
        cursor.execute(
            'SELECT pengiriman.date_send, vendor.vendor_name, pengiriman.nama_petugas, list_barang.no_po, list_barang.no_do, sparepart.sparepart_name, list_barang.serial_number, list_barang.keterangan FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor=vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender=pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart=sparepart.id_sparepart WHERE pengiriman.status_barang="masuk" ORDER BY pengiriman.date_send DESC;')
        data = cursor.fetchall()
        data_filter = data

    else:
        return render_template('laporan.html')

    if request.method == 'POST':
        if _btn == "Masuk":
            cursor.execute(
                'SELECT pengiriman.date_send, vendor.vendor_name, pengiriman.nama_petugas, list_barang.no_po, list_barang.no_do, sparepart.sparepart_name, list_barang.serial_number FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor = vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender = pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart = sparepart.id_sparepart WHERE pengiriman.status_barang = "masuk" AND pengiriman.date_send BETWEEN %s AND %s ORDER BY pengiriman.date_send DESC;',
                (date_start, date_end))
            data = cursor.fetchall()
            data_filter = data
        elif _btn == "Keluar":
            cursor.execute(
                'SELECT pengiriman.date_send, vendor.vendor_name, pengiriman.nama_petugas, list_barang.no_po, sparepart.sparepart_name, list_barang.serial_number, list_barang.keterangan FROM pengiriman INNER JOIN vendor ON pengiriman.id_vendor = vendor.id_vendor INNER JOIN list_barang ON list_barang.id_sender = pengiriman.id_sender INNER JOIN sparepart ON list_barang.id_sparepart = sparepart.id_sparepart WHERE pengiriman.status_barang = "keluar" AND pengiriman.date_send BETWEEN %s AND %s ORDER BY pengiriman.date_send DESC;',
                (date_start, date_end))
            data = cursor.fetchall()
            data_filter = data

    if not session.get('username'):
        return redirect(url_for('login_page'))
    else:
        return render_template('laporan.html', btn=_btn, data=data)


@app.route('/BRICASH-APP/Report/Download/<_btn>')
def download_report(_btn):
    rendered = render_template('pdf_template.html', data=data_filter, btn=_btn)
    pdf = pdfkit.from_string(rendered, False)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    if _btn == "Keluar":
        response.headers['Content-Disposition'] = 'attachment; filename=Laporan_Barang_Keluar.pdf'
    elif _btn == "Masuk":
        response.headers['Content-Disposition'] = 'attachment; filename=Laporan_Barang_Masuk.pdf'

    return response


if __name__ == '__main__':
    app.run(host="localhost", port=3200, debug=False)
