from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# تخزين المنتجات مؤقتًا في قائمة
products = []

# الصفحة الرئيسية
@app.route('/')
def index():
    return render_template('index.html', products=products)

# صفحة إضافة منتج
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        image = request.form['image']  # اسم ملف الصورة
        products.append({'name': name, 'price': price, 'image': image})
        return redirect(url_for('index'))
    return render_template('add_product.html')

# لوحة الأدمن
@app.route('/admin')
def admin():
    return render_template('admin.html', products=products)

# صفحة تسجيل دخول الأدمن
@app.route('/admin_login')
def admin_login():
    return render_template('admin_login.html')

if __name__ == '__main__':
    app.run(debug=True)
