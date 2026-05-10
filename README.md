# Neyo Integrated Farm Services — Website

## Stack
- **Backend:** Flask (Python) + SQLite (built-in, zero dependencies)
- **Frontend:** Jinja2 templates, vanilla CSS/JS
- **Auth:** Session-based (no external libraries needed)

## Quick Start

```bash
pip install flask gunicorn
python app.py
```

App runs at: **http://localhost:5050**

## Admin Panel
**URL:** http://localhost:5050/admin/login
- Email: `admin@neyo.com.ng`
- Password: `NeyoAdmin2024!`

> Change the admin password after first login.

## Pages
| Page | URL |
|------|-----|
| Home | / |
| About | /about |
| Services | /services |
| Shop | /shop |
| Shop by category | /shop?category=crops (or poultry/fish/snails/pig) |
| Blog | /blog |
| Contact | /contact |
| Login | /login |
| Register | /register |
| Admin Dashboard | /admin |
| Admin Products | /admin/products |
| Admin Orders | /admin/orders |
| Admin Messages | /admin/messages |
| Admin Blog | /admin/blog |
| Admin Users | /admin/users |

## Features
- 5 product categories: crops, poultry, fish, snails, pig
- Order placement with customer details
- Contact form with admin message inbox
- Blog with category tagging
- User registration & login (session-based)
- Full admin panel: manage products, orders, messages, blog posts, users
- Seed data: 10 products + 3 blog posts pre-loaded

## Production Deployment (Render / Railway / VPS)

1. **Switch to PostgreSQL** (optional):
   Install `psycopg2` and update `DB_PATH` to use `os.environ.get('DATABASE_URL')`

2. **Set environment variables:**
   ```
   SECRET_KEY=your-random-secret-key-here
   ```

3. **Run with gunicorn:**
   ```bash
   gunicorn wsgi:app
   ```

4. **Point** `neyo.com.ng` to your server IP via DNS A record.

## File Structure
```
neyo/
├── app.py              # Main Flask app (routes + DB logic)
├── wsgi.py             # Gunicorn entry point
├── Procfile            # For Heroku/Render
├── requirements.txt
├── instance/
│   └── neyo.db         # SQLite database (auto-created)
├── static/
│   ├── css/main.css
│   └── js/main.js
└── templates/
    ├── base.html
    ├── index.html
    ├── about.html
    ├── services.html
    ├── shop.html
    ├── product_detail.html
    ├── order.html
    ├── blog.html
    ├── blog_post.html
    ├── contact.html
    ├── login.html
    ├── register.html
    └── admin/
        ├── base.html
        ├── login.html
        ├── dashboard.html
        ├── products.html
        ├── orders.html
        ├── messages.html
        ├── blog.html
        └── users.html
```
