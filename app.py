import sqlite3, os, hashlib, functools
from flask import Flask, render_template, request, redirect, url_for, flash, session, g

# Work out where this file lives so paths are always correct

BASE_DIR = os.path.dirname(os.path.abspath(**file**))
TEMPLATE_DIR = os.path.join(BASE_DIR, ‘templates’)
STATIC_DIR   = os.path.join(BASE_DIR, ‘static’)
DB_PATH      = os.path.join(BASE_DIR, ‘instance’, ‘neyo.db’)
os.makedirs(os.path.join(BASE_DIR, ‘instance’), exist_ok=True)

app = Flask(**name**,
template_folder=TEMPLATE_DIR,
static_folder=STATIC_DIR)
app.secret_key = os.environ.get(‘SECRET_KEY’, ‘neyo-secret-key-2024-change-in-production’)

# ─── DB HELPERS ───────────────────────────────────────────────────────────────

def get_db():
if ‘db’ not in g:
g.db = sqlite3.connect(DB_PATH)
g.db.row_factory = sqlite3.Row
g.db.execute(“PRAGMA foreign_keys = ON”)
return g.db

@app.teardown_appcontext
def close_db(e=None):
db = g.pop(‘db’, None)
if db: db.close()

def q(sql, params=(), one=False):
db = get_db()
cur = db.execute(sql, params)
db.commit()
rv = cur.fetchall()
return (rv[0] if rv else None) if one else rv

def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()
def check_pw(pw, h): return hash_pw(pw) == h

def current_user():
uid = session.get(‘user_id’)
if uid:
return q(‘SELECT * FROM users WHERE id=?’, (uid,), one=True)
return None

def login_required(f):
@functools.wraps(f)
def decorated(*args, **kwargs):
if not session.get(‘user_id’):
return redirect(url_for(‘login’))
return f(*args, **kwargs)
return decorated

def admin_required(f):
@functools.wraps(f)
def decorated(*args, **kwargs):
uid = session.get(‘user_id’)
if not uid:
return redirect(url_for(‘admin_login’))
user = q(‘SELECT * FROM users WHERE id=? AND role=“admin”’, (uid,), one=True)
if not user:
return redirect(url_for(‘index’))
return f(*args, **kwargs)
return decorated

@app.context_processor
def inject_user():
return dict(current_user=current_user())

# ─── INIT DB ──────────────────────────────────────────────────────────────────

def init_db():
db = sqlite3.connect(DB_PATH)
db.executescript(’’’
CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE NOT NULL,
email TEXT UNIQUE NOT NULL,
password_hash TEXT NOT NULL,
role TEXT DEFAULT “customer”,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS products (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
category TEXT NOT NULL,
description TEXT,
price REAL NOT NULL,
unit TEXT DEFAULT “kg”,
stock INTEGER DEFAULT 0,
image_url TEXT,
available INTEGER DEFAULT 1,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS orders (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
email TEXT NOT NULL,
phone TEXT,
address TEXT,
product_id INTEGER,
quantity INTEGER DEFAULT 1,
total_price REAL,
status TEXT DEFAULT “pending”,
notes TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (product_id) REFERENCES products(id)
);
CREATE TABLE IF NOT EXISTS contacts (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
email TEXT NOT NULL,
phone TEXT,
subject TEXT,
message TEXT NOT NULL,
responded INTEGER DEFAULT 0,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS blog_posts (
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT NOT NULL,
slug TEXT UNIQUE NOT NULL,
content TEXT NOT NULL,
excerpt TEXT,
category TEXT,
image_url TEXT,
published INTEGER DEFAULT 0,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
‘’’)
db.commit()
admin = db.execute(‘SELECT id FROM users WHERE role=“admin”’).fetchone()
if not admin:
db.execute(‘INSERT INTO users (username,email,password_hash,role) VALUES (?,?,?,?)’,
(‘admin’,‘admin@neyo.com.ng’, hash_pw(‘NeyoAdmin2024!’),‘admin’))
products = [
(‘Fresh Yam Tubers’,‘crops’,‘Premium quality yam tubers, freshly harvested from our fertile farmlands.’,4500,‘bag (50kg)’,200,‘https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400’,1),
(‘Dried Pepper (Tatashe)’,‘crops’,‘Sun-dried red pepper, rich in flavour and nutrients.’,2800,‘kg’,150,‘https://images.unsplash.com/photo-1526346698789-22fd84314424?w=400’,1),
(‘Fresh Maize (Corn)’,‘crops’,‘Sweet, tender maize from our open-field farms.’,1500,‘bag (100 cobs)’,300,‘https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=400’,1),
(‘Live Broiler Chicken’,‘poultry’,‘Healthy, well-fed broiler chickens raised in our modern poultry facility.’,6500,‘bird’,500,‘https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?w=400’,1),
(‘Fresh Table Eggs (Crate)’,‘poultry’,‘Fresh, large-grade eggs from our laying hens. 30 eggs per crate.’,3200,‘crate’,1000,‘https://images.unsplash.com/photo-1518569656558-1f25e69d2fd4?w=400’,1),
(‘Fresh Catfish (Clarias)’,‘fish’,‘Live or dressed catfish from our well-maintained fish ponds.’,3800,‘kg’,400,‘https://images.unsplash.com/photo-1534482421-64566f976cfa?w=400’,1),
(‘Tilapia Fish’,‘fish’,‘Fresh tilapia, responsibly farmed in clean water systems.’,2900,‘kg’,350,‘https://images.unsplash.com/photo-1580476262798-bddd9f4b7369?w=400’,1),
(‘Live Giant African Snails’,‘snails’,‘Healthy, well-grown giant African land snails.’,2000,‘dozen’,600,‘https://images.unsplash.com/photo-1589803568827-c1c58f668d7d?w=400’,1),
(‘Live Pigs (Weaner)’,‘pig’,‘Healthy weaner pigs from our biosecure pig farm.’,35000,‘head’,80,‘https://images.unsplash.com/photo-1604848698030-c434ba08ece1?w=400’,1),
(‘Pork (Dressed)’,‘pig’,‘Fresh dressed pork from our organically raised pigs.’,5500,‘kg’,120,‘https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=400’,1),
]
db.executemany(‘INSERT INTO products (name,category,description,price,unit,stock,image_url,available) VALUES (?,?,?,?,?,?,?,?)’, products)
posts = [
(‘Why Integrated Farming is the Future of Nigerian Agriculture’,‘integrated-farming-future-nigeria’,
‘Integrated farming combines multiple agricultural activities on a single farm, reducing waste and maximising land use. At Neyo, we have pioneered this model in Nigeria.’,
‘Discover how integrated farming is transforming Nigerian agriculture.’,‘farming’,
‘https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=600’,1),
(‘Top Tips for Buying Quality Catfish in Nigeria’,‘buying-quality-catfish-nigeria’,
‘Look for clear eyes, firm flesh, and fresh smell. At Neyo Fish, we guarantee freshness in every order.’,
‘Expert guide to choosing the freshest catfish.’,‘fish’,
‘https://images.unsplash.com/photo-1534482421-64566f976cfa?w=600’,1),
(‘Snail Farming: The Quiet Gold Mine in Nigerian Agriculture’,‘snail-farming-nigeria-gold-mine’,
‘Giant African snails require minimal space and have exceptionally high protein content. Neyo Snails supplies restaurants and households across Nigeria.’,
‘Learn why snail farming is one of Nigeria's most lucrative ventures.’,‘snails’,
‘https://images.unsplash.com/photo-1589803568827-c1c58f668d7d?w=600’,1),
]
db.executemany(‘INSERT INTO blog_posts (title,slug,content,excerpt,category,image_url,published) VALUES (?,?,?,?,?,?,?)’, posts)
db.commit()
db.close()

# Initialise DB on startup

with app.app_context():
init_db()

# ─── PUBLIC ROUTES ─────────────────────────────────────────────────────────────

@app.route(’/’)
def index():
products = q(‘SELECT * FROM products WHERE available=1 LIMIT 8’)
posts = q(‘SELECT * FROM blog_posts WHERE published=1 ORDER BY created_at DESC LIMIT 3’)
return render_template(‘index.html’, products=products, posts=posts)

@app.route(’/about’)
def about():
return render_template(‘about.html’)

@app.route(’/services’)
def services():
return render_template(‘services.html’)

@app.route(’/shop’)
def shop():
cat = request.args.get(‘category’,’’)
if cat:
products = q(‘SELECT * FROM products WHERE available=1 AND category=?’, (cat,))
else:
products = q(‘SELECT * FROM products WHERE available=1’)
return render_template(‘shop.html’, products=products, active_category=cat)

@app.route(’/shop/<int:pid>’)
def product_detail(pid):
product = q(‘SELECT * FROM products WHERE id=?’, (pid,), one=True)
if not product: return redirect(url_for(‘shop’))
related = q(‘SELECT * FROM products WHERE category=? AND id!=? AND available=1 LIMIT 4’, (product[‘category’],pid))
return render_template(‘product_detail.html’, product=product, related=related)

@app.route(’/order/<int:pid>’, methods=[‘GET’,‘POST’])
def order(pid):
product = q(‘SELECT * FROM products WHERE id=?’, (pid,), one=True)
if not product: return redirect(url_for(‘shop’))
if request.method == ‘POST’:
qty = int(request.form.get(‘quantity’,1))
total = product[‘price’] * qty
q(‘INSERT INTO orders (name,email,phone,address,product_id,quantity,total_price,notes) VALUES (?,?,?,?,?,?,?,?)’,
(request.form[‘name’], request.form[‘email’], request.form.get(‘phone’),
request.form.get(‘address’), pid, qty, total, request.form.get(‘notes’)))
flash(‘Order placed successfully! We will contact you shortly.’, ‘success’)
return redirect(url_for(‘shop’))
return render_template(‘order.html’, product=product)

@app.route(’/blog’)
def blog():
posts = q(‘SELECT * FROM blog_posts WHERE published=1 ORDER BY created_at DESC’)
return render_template(‘blog.html’, posts=posts)

@app.route(’/blog/<slug>’)
def blog_post(slug):
post = q(‘SELECT * FROM blog_posts WHERE slug=? AND published=1’, (slug,), one=True)
if not post: return redirect(url_for(‘blog’))
return render_template(‘blog_post.html’, post=post)

@app.route(’/contact’, methods=[‘GET’,‘POST’])
def contact():
if request.method == ‘POST’:
q(‘INSERT INTO contacts (name,email,phone,subject,message) VALUES (?,?,?,?,?)’,
(request.form[‘name’], request.form[‘email’], request.form.get(‘phone’),
request.form.get(‘subject’), request.form[‘message’]))
flash(‘Message sent! We will get back to you soon.’, ‘success’)
return redirect(url_for(‘contact’))
return render_template(‘contact.html’)

@app.route(’/register’, methods=[‘GET’,‘POST’])
def register():
if request.method == ‘POST’:
if q(‘SELECT id FROM users WHERE email=?’, (request.form[‘email’],), one=True):
flash(‘Email already registered.’, ‘danger’)
return redirect(url_for(‘register’))
q(‘INSERT INTO users (username,email,password_hash) VALUES (?,?,?)’,
(request.form[‘username’], request.form[‘email’], hash_pw(request.form[‘password’])))
user = q(‘SELECT * FROM users WHERE email=?’, (request.form[‘email’],), one=True)
session[‘user_id’] = user[‘id’]
flash(‘Account created!’, ‘success’)
return redirect(url_for(‘index’))
return render_template(‘register.html’)

@app.route(’/login’, methods=[‘GET’,‘POST’])
def login():
if request.method == ‘POST’:
user = q(‘SELECT * FROM users WHERE email=?’, (request.form[‘email’],), one=True)
if user and check_pw(request.form[‘password’], user[‘password_hash’]):
session[‘user_id’] = user[‘id’]
return redirect(url_for(‘index’))
flash(‘Invalid credentials.’, ‘danger’)
return render_template(‘login.html’)

@app.route(’/logout’)
def logout():
session.clear()
return redirect(url_for(‘index’))

# ─── ADMIN ─────────────────────────────────────────────────────────────────────

@app.route(’/admin/login’, methods=[‘GET’,‘POST’])
def admin_login():
if request.method == ‘POST’:
user = q(‘SELECT * FROM users WHERE email=? AND role=“admin”’, (request.form[‘email’],), one=True)
if user and check_pw(request.form[‘password’], user[‘password_hash’]):
session[‘user_id’] = user[‘id’]
return redirect(url_for(‘admin_dashboard’))
flash(‘Invalid admin credentials.’, ‘danger’)
return render_template(‘admin/login.html’)

@app.route(’/admin’)
@admin_required
def admin_dashboard():
stats = {
‘products’: q(‘SELECT COUNT(*) as c FROM products’, one=True)[‘c’],
‘orders’: q(’SELECT COUNT(*) as c FROM orders’, one=True)[‘c’],
‘pending_orders’: q(‘SELECT COUNT(*) as c FROM orders WHERE status=“pending”’, one=True)[‘c’],
‘messages’: q(’SELECT COUNT(*) as c FROM contacts WHERE responded=0’, one=True)[‘c’],
‘users’: q(‘SELECT COUNT(*) as c FROM users’, one=True)[‘c’],
}
recent_orders = q(’’’SELECT o.*, p.name as product_name FROM orders o
LEFT JOIN products p ON o.product_id=p.id
ORDER BY o.created_at DESC LIMIT 10’’’)
return render_template(‘admin/dashboard.html’, stats=stats, recent_orders=recent_orders)

@app.route(’/admin/products’, methods=[‘GET’,‘POST’])
@admin_required
def admin_products():
if request.method == ‘POST’:
q(‘INSERT INTO products (name,category,description,price,unit,stock,image_url,available) VALUES (?,?,?,?,?,?,?,?)’,
(request.form[‘name’], request.form[‘category’], request.form.get(‘description’),
float(request.form[‘price’]), request.form.get(‘unit’,‘kg’),
int(request.form.get(‘stock’,0)), request.form.get(‘image_url’),
1 if request.form.get(‘available’) else 0))
flash(‘Product added.’, ‘success’)
products = q(‘SELECT * FROM products ORDER BY created_at DESC’)
return render_template(‘admin/products.html’, products=products)

@app.route(’/admin/products/delete/<int:pid>’)
@admin_required
def delete_product(pid):
q(‘DELETE FROM products WHERE id=?’, (pid,))
flash(‘Product deleted.’, ‘success’)
return redirect(url_for(‘admin_products’))

@app.route(’/admin/orders’)
@admin_required
def admin_orders():
orders = q(’’‘SELECT o.*, p.name as product_name FROM orders o
LEFT JOIN products p ON o.product_id=p.id
ORDER BY o.created_at DESC’’’)
return render_template(‘admin/orders.html’, orders=orders)

@app.route(’/admin/orders/update/<int:oid>/<status>’)
@admin_required
def update_order_status(oid, status):
q(‘UPDATE orders SET status=? WHERE id=?’, (status, oid))
flash(f’Order #{oid} marked as {status}.’, ‘success’)
return redirect(url_for(‘admin_orders’))

@app.route(’/admin/messages’)
@admin_required
def admin_messages():
messages = q(‘SELECT * FROM contacts ORDER BY created_at DESC’)
return render_template(‘admin/messages.html’, messages=messages)

@app.route(’/admin/blog’, methods=[‘GET’,‘POST’])
@admin_required
def admin_blog():
if request.method == ‘POST’:
slug = request.form[‘title’].lower().replace(’ ‘,’-’).replace(’/’,’-’)[:80]
q(‘INSERT INTO blog_posts (title,slug,content,excerpt,category,image_url,published) VALUES (?,?,?,?,?,?,?)’,
(request.form[‘title’], slug, request.form[‘content’], request.form.get(‘excerpt’),
request.form.get(‘category’), request.form.get(‘image_url’),
1 if request.form.get(‘published’) else 0))
flash(‘Blog post created.’, ‘success’)
posts = q(‘SELECT * FROM blog_posts ORDER BY created_at DESC’)
return render_template(‘admin/blog.html’, posts=posts)

@app.route(’/admin/users’)
@admin_required
def admin_users():
users = q(‘SELECT * FROM users ORDER BY created_at DESC’)
return render_template(‘admin/users.html’, users=users)

if **name** == ‘**main**’:
app.run(debug=True, port=5050)
