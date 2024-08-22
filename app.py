from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = os.path.join('/tmp', 'database.db')

# Database setup
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS master (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            master_id INTEGER,
            detail TEXT NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY (master_id) REFERENCES master(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# CREATE and READ operations for Master
@app.route('/master', methods=['GET', 'POST'])
def master():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        cursor.execute('INSERT INTO master (name, description) VALUES (?, ?)', (name, description))
        conn.commit()
        return redirect(url_for('master'))

    cursor.execute('SELECT * FROM master')
    masters = cursor.fetchall()
    conn.close()

    return render_template('master.html', masters=masters)

# UPDATE and DELETE operations for Master
@app.route('/edit_master/<int:id>', methods=['GET', 'POST'])
def edit_master(id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        cursor.execute('UPDATE master SET name = ?, description = ? WHERE id = ?', (name, description, id))
        conn.commit()
        return redirect(url_for('master'))

    cursor.execute('SELECT * FROM master WHERE id = ?', (id,))
    master = cursor.fetchone()
    conn.close()

    return render_template('edit_master.html', master=master)

@app.route('/delete_master/<int:id>')
def delete_master(id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM master WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('master'))

# CREATE and READ operations for Transaksi
@app.route('/transaksi', methods=['GET', 'POST'])
def transaksi():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if request.method == 'POST':
        master_id = request.form['master_id']
        detail = request.form['detail']
        amount = request.form['amount']
        cursor.execute('INSERT INTO transaksi (master_id, detail, amount) VALUES (?, ?, ?)', (master_id, detail, amount))
        conn.commit()
        return redirect(url_for('transaksi'))

    cursor.execute('SELECT * FROM master')
    masters = cursor.fetchall()
    cursor.execute('SELECT transaksi.id, master.name, transaksi.detail, transaksi.amount FROM transaksi JOIN master ON transaksi.master_id = master.id')
    transaksi_list = cursor.fetchall()
    conn.close()

    return render_template('transaksi.html', masters=masters, transaksi_list=transaksi_list)

# UPDATE and DELETE operations for Transaksi
@app.route('/edit_transaksi/<int:id>', methods=['GET', 'POST'])
def edit_transaksi(id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if request.method == 'POST':
        master_id = request.form['master_id']
        detail = request.form['detail']
        amount = request.form['amount']
        cursor.execute('UPDATE transaksi SET master_id = ?, detail = ?, amount = ? WHERE id = ?', (master_id, detail, amount, id))
        conn.commit()
        return redirect(url_for('transaksi'))

    cursor.execute('SELECT * FROM transaksi WHERE id = ?', (id,))
    transaksi = cursor.fetchone()
    cursor.execute('SELECT * FROM master')
    masters = cursor.fetchall()
    conn.close()

    return render_template('edit_transaksi.html', transaksi=transaksi, masters=masters)

@app.route('/delete_transaksi/<int:id>')
def delete_transaksi(id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transaksi WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('transaksi'))

# Report route
@app.route('/report')
def report():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT master.name, master.description, transaksi.detail, transaksi.amount
        FROM transaksi
        JOIN master ON transaksi.master_id = master.id
    ''')
    report_data = cursor.fetchall()
    conn.close()

    return render_template('report.html', report_data=report_data)

if __name__ == '__main__':
    app.run(debug=True)
