from flask import Flask, render_template, request, redirect
from flask_caching import Cache
import sqlite3
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'

# إعداد الكاش
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 60})

# إنشاء قاعدة البيانات إذا ما كانت موجودة
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT NOT NULL,
    name TEXT
)''')
c.execute('''CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT,
    price REAL,
    description TEXT,
    image TEXT
)''')
conn.commit()
conn.close()

# الصفحة الرئيسية مع كاش
@app.route('/')
@cache.cached(timeout=60)  # الكاش لمدة 60 ثانية
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products ORDER BY id DESC")
    products = c.fetchall()
    conn.close()
    return render_template('index.html', products=products)

# صفحة إضافة منتج
@app.route('/add', methods=['GET','POST'])
def add_product():
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        description = request.form['description']
        phone = request.form['phone']
        image = request.files['image']

        # حفظ الصورة
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(image_path)

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        # إضافة المستخدم إذا ما موجود
        c.execute("SELECT id FROM users WHERE phone=?", (phone,))
        user = c.fetchone()
        if user:
            user_id = user[0]
        else:
            c.execute("INSERT INTO users (phone) VALUES (?)", (phone,))
            user_id = c.lastrowid

        # إضافة المنتج
        c.execute("INSERT INTO products (user_id, title, price, description, image) VALUES (?,?,?,?,?)",
                  (user_id, title, price, description, image.filename))
        conn.commit()
        conn.close()
        cache.clear()  # تنظيف الكاش بعد إضافة المنتج
        return redirect('/')
    return render_template('add_product.html')

# لوحة الادمن (عرض جميع المنتجات مع حذف)
@app.route('/admin')
def admin():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products ORDER BY id DESC")
    products = c.fetchall()
    conn.close()
    return render_template('admin.html', products=products)

@app.route('/delete/<int:id>')
def delete_product(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id=?", (id,))
    conn.commit()
    conn.close()
    cache.clear()  # تنظيف الكاش بعد حذف المنتج
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)
