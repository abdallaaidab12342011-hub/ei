from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, AdminUser, Product, Customer, Order, OrderItem
from datetime import datetime, timezone
from markupsafe import Markup
import os
from werkzeug.utils import secure_filename
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'meidab-plastic-2024-secure-key-xK9pL2mN')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plastic_company.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# ── FIX BUG-2c: guarantee the uploads directory exists on startup ──────────────
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. CENTRAL TRANSLATION DICTIONARY
# ─────────────────────────────────────────────────────────────────────────────
TRANSLATIONS = {
    'en': {
        # Navigation
        'nav_home': 'Home',
        'nav_about': 'About Us',
        'nav_products': 'Products',
        'nav_contact': 'Contact',
        'nav_cart': 'Cart',

        # Home & Hero
        'hero_badge': 'Trusted Since 2005 | ISO Certified',
        'hero_title': 'Leading Plastic Products Manufacturer & Supplier',
        'hero_subtitle': 'High Quality Plastic Products For Homes, Businesses, Retailers And Industries. From household essentials to heavy industrial solutions.',
        'view_products': 'View Products →',
        'contact_us': 'Contact Us',
        'stat_products': 'Products',
        'stat_clients': 'Clients',
        'stat_experience': 'Years Exp.',
        'featured_eyebrow': 'Top Picks',
        'featured_title': 'Featured Products',
        'featured_sub': 'Our most popular, best-selling products trusted by thousands of customers.',
        'featured_badge': 'Featured',
        'browse_all': 'Browse All Products →',
        'advantages_eyebrow': 'Our Advantages',
        'why_choose_us': 'Why Choose Us',
        'feat_quality_title': 'Premium Quality',
        'feat_quality_desc': 'We use 100% pure, durable plastic material built to last for generations.',
        'feat_delivery_title': 'Fast Shipping',
        'feat_delivery_desc': 'Reliable global logistics network ensuring your bulk orders arrive safely and on time.',
        'footer_rights': 'All Rights Reserved.',

        # Product Catalog Page
        'search_placeholder': 'Search products...',
        'all_categories': 'All Categories',
        'sort_by': 'Sort By',
        'sort_name': 'Name (A-Z)',
        'sort_price_asc': 'Price (Low to High)',
        'sort_price_desc': 'Price (High to Low)',
        'no_products': 'No products found in this section.',
        'filter_btn': 'Filter',
        'view_details': 'View Details →',

        # Product Detail Page
        'specifications': 'Specifications',
        'sku': 'SKU',
        'material': 'Material',
        'weight': 'Weight',
        'dimensions': 'Dimensions',
        'color': 'Color',
        'category': 'Category',
        'in_stock': '✓ In Stock ({qty} units)',
        'low_stock': '⚠ Low Stock (Only {qty} left)',
        'out_of_stock': '✕ Out of Stock',
        'add_to_cart': '🛒 Add to Cart',
        'related_products': 'Related Products',
        'you_may_also_like': 'You May Also Like',

        # Cart Page
        'cart_title': 'Your Shopping Cart',
        'cart_item': 'Product',
        'cart_qty': 'Quantity',
        'cart_subtotal': 'Subtotal',
        'cart_total': 'Grand Total Amount',
        'cart_empty': 'Your shopping cart is currently empty.',
        'continue_shopping': '← Continue Shopping',
        'checkout_btn': 'Proceed to Checkout →',
        'remove_item': 'Remove',

        # Checkout Page
        'checkout_title': 'Secure Checkout',
        'billing_details': 'Shipping & Delivery Details',
        'field_name': 'Full Name *',
        'field_phone': 'Phone Number *',
        'field_email': 'Email Address',
        'field_address': 'Full Delivery Address *',
        'field_city': 'City / State *',
        'field_notes': 'Additional Order Notes (Optional)',
        'place_order': 'Confirm & Place Order 👍',
        'order_summary': 'Your Order Summary',

        # Order Success Page
        'success_title': 'Order Placed Successfully!',
        'success_msg': 'Thank you! Your order has been securely received and is being processed by our team.',
        'order_number': 'Your Order Number:',
        'back_home': 'Return to Homepage',

        # Flash Messages & Alerts
        'flash_contact_success': 'Thank you for your message! We will contact you within 24 hours.',
        'flash_qty_error': 'Cannot add requested quantity. Only {qty} units available in stock.',
        'flash_cart_added': 'Product added to cart successfully!',
        'flash_stock_dropped': 'Order failed. Stock level dropped for item: {name}. Only {qty} units remaining.',
        'flash_required_fields': 'Please fill in all required fields marked with (*).',
        'flash_order_error': 'An error occurred while processing your order. Please try again.',
    },
    'ar': {
        # Navigation
        'nav_home': 'الرئيسية',
        'nav_about': 'من نحن',
        'nav_products': 'المنتجات',
        'nav_contact': 'اتصل بنا',
        'nav_cart': 'السلة',

        # Home & Hero
        'hero_badge': 'موثوق به منذ 2010 | معتمد من ISO',
        'hero_title': 'الشركة الرائدة في تصنيع وتوريد المنتجات البلاستيكية',
        'hero_subtitle': 'منتجات بلاستيكية عالية الجودة للمنازل، الشركات، تجار التجزئة والمصانع. من المستلزمات المنزلية الأساسية إلى الحلول الصناعية الثقيلة.',
        'view_products': 'عرض المنتجات ←',
        'contact_us': 'اتصل بنا',
        'stat_products': 'منتج',
        'stat_clients': 'عميل',
        'stat_experience': 'عام خبرة',
        'featured_eyebrow': 'أفضل الاختيارات',
        'featured_title': 'المنتجات المميزة',
        'featured_sub': 'منتجاتنا الأكثر شعبية والأكثر مبيعاً والموثوقة من قبل آلاف العملاء.',
        'featured_badge': 'مميز',
        'browse_all': 'تصفح جميع المنتجات ←',
        'advantages_eyebrow': 'ميزاتنا',
        'why_choose_us': 'لماذا تختارنا؟',
        'feat_quality_title': 'جودة ممتازة',
        'feat_quality_desc': 'نحن نستخدم مواد بلاستيكية نقية ومتينة بنسبة ١٠٠٪ تدوم لأجيال.',
        'feat_delivery_title': 'شحن سريع',
        'feat_delivery_desc': 'شبكة لوجستية عالمية موثوقة تضمن وصول طلباتك بالجملة بأمان وفي الوقت المحدد.',
        'footer_rights': 'جميع الحقوق محفوظة.',

        # Product Catalog Page
        'search_placeholder': 'ابحث عن المنتجات...',
        'all_categories': 'جميع الفئات',
        'sort_by': 'ترتيب حسب',
        'sort_name': 'الاسم (أبجدي)',
        'sort_price_asc': 'السعر (من الأقل للأعلى)',
        'sort_price_desc': 'السعر (من الأعلى للأقل)',
        'no_products': 'لم يتم العثور على أي منتجات في هذا القسم.',
        'filter_btn': 'تصفية',
        'view_details': 'عرض التفاصيل ←',

        # Product Detail Page
        'specifications': 'المواصفات الفنية',
        'sku': 'رمز المنتج (SKU)',
        'material': 'المادة المصنعة',
        'weight': 'الوزن',
        'dimensions': 'الأبعاد',
        'color': 'اللون',
        'category': 'الفئة',
        'in_stock': '✓ متوفر في المخزن ({qty} وحدة)',
        'low_stock': '⚠ مخزون منخفض (متبقي {qty} قطع فقط)',
        'out_of_stock': '✕ غير متوفر في المخزن',
        'add_to_cart': '🛒 أضف إلى السلة',
        'related_products': 'منتجات ذات صلة',
        'you_may_also_like': 'قد يعجبك أيضاً',

        # Cart Page
        'cart_title': 'سلة التسوق الخاصة بك',
        'cart_item': 'المنتج',
        'cart_qty': 'الكمية',
        'cart_subtotal': 'المجموع الفرعي',
        'cart_total': 'إجمالي المبلغ الحسابي',
        'cart_empty': 'سلة التسوق الخاصة بك فارغة حالياً.',
        'continue_shopping': '← العودة لمواصلة التسوق',
        'checkout_btn': 'الانتقال لإتمام الدفع ←',
        'remove_item': 'حذف',

        # Checkout Page
        'checkout_title': 'إتمام عملية الشراء وآمن',
        'billing_details': 'تفاصيل الشحن والتوصيل للطلب',
        'field_name': 'الاسم الكامل *',
        'field_phone': 'رقم الهاتف للتواصل *',
        'field_email': 'البريد الإلكتروني',
        'field_address': 'عنوان التوصيل بالكامل *',
        'field_city': 'المدينة / الولاية *',
        'field_notes': 'ملاحظات إضافية حول الطلب (اختياري)',
        'place_order': 'تأكيد وإرسال الطلب 👍',
        'order_summary': 'ملخص طلبك الحالي',

        # Order Success Page
        'success_title': 'تم إرسال طلبك بنجاح تام!',
        'success_msg': 'شكراً جزيلاً لتعاملك معنا! تم استلام طلبك بأمان ويجري العمل على تجهيزه وشحنه الآن.',
        'order_number': 'رقم الطلب الخاص بك هو:',
        'back_home': 'العودة إلى الصفحة الرئيسية',

        # Flash Messages & Alerts
        'flash_contact_success': 'نشكرك على رسالتك! سيقوم فريقنا بالتواصل معك خلال 24 ساعة القادمة.',
        'flash_qty_error': 'لا يمكن إضافة الكمية المطلوبة. المتوفر في المخزن هو {qty} قطع فقط.',
        'flash_cart_added': 'تمت إضافة المنتج إلى سلة التسوق بنجاح!',
        'flash_stock_dropped': 'فشلت العملية. نفد المخزن أثناء الطلب للمنتج: {name}. الكمية المتبقية: {qty} قطع.',
        'flash_required_fields': 'يرجى ملء جميع الحقول الإلزامية المطلوبة المميّزة بعلامة (*).',
        'flash_order_error': 'حدث خطأ غير متوقع أثناء معالجة طلبك الكلي. يرجى إعادة المحاولة.',
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. GLOBAL CONTEXT PROCESSOR & TEMPLATE FILTER
# ─────────────────────────────────────────────────────────────────────────────

@app.context_processor
def inject_translations():
    lang = session.get('lang', 'en')
    return dict(
        t=TRANSLATIONS.get(lang, TRANSLATIONS['en']),
        current_lang=lang,
    )


@app.template_filter('sdg')
def format_sdg(value):
    try:
        formatted_price = f"{float(value):.2f}"
        return Markup(f'{formatted_price} <span class="currency-label">SDG</span>')
    except (ValueError, TypeError):
        return Markup('0.00 <span class="currency-label">SDG</span>')


db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(AdminUser, int(user_id))


def generate_order_number():
    return 'MEP-' + ''.join(random.choices(string.digits, k=8))


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    featured = Product.query.filter_by(is_featured=True, is_active=True).limit(8).all()
    categories = (
        db.session.query(Product.category, db.func.count(Product.id))
        .filter_by(is_active=True)
        .group_by(Product.category)
        .all()
    )
    stats = {
        'products': Product.query.filter_by(is_active=True).count(),
        'orders': Order.query.count(),
        'customers': Customer.query.count(),
        'categories': len(categories),
    }
    return render_template('index.html', featured=featured, categories=categories, stats=stats)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/products')
def products():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    search = request.args.get('search', '').strip()
    sort = request.args.get('sort', 'name')
    per_page = 12

    query = Product.query.filter_by(is_active=True)
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))

    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.name.asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    categories = db.session.query(Product.category).filter_by(is_active=True).distinct().all()

    return render_template(
        'products.html',
        products=pagination.items,
        pagination=pagination,
        categories=[c[0] for c in categories],
        current_category=category,
        search=search,
        sort=sort,
    )


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = db.session.get(Product, product_id)
    if not product or not product.is_active:
        return redirect(url_for('products'))
    related = (
        Product.query.filter_by(category=product.category, is_active=True)
        .filter(Product.id != product_id)
        .limit(4)
        .all()
    )
    return render_template('product_detail.html', product=product, related=related)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    lang = session.get('lang', 'en')
    if request.method == 'POST':
        flash(TRANSLATIONS[lang]['flash_contact_success'], 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')


# ─────────────────────────────────────────────────────────────────────────────
# LANGUAGE TOGGLE ROUTE
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in ['en', 'ar']:
        session['lang'] = lang
        session.modified = True
    return redirect(request.referrer or url_for('index'))


# ─────────────────────────────────────────────────────────────────────────────
# CART ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/cart')
def cart():
    cart_items = session.get('cart', {})
    products_in_cart = []
    total = 0
    for pid, qty in list(cart_items.items()):
        p = db.session.get(Product, int(pid))
        if p and p.is_active:
            subtotal = p.price * qty
            total += subtotal
            products_in_cart.append({'product': p, 'quantity': qty, 'subtotal': subtotal})
        else:
            cart_items.pop(pid, None)
            session['cart'] = cart_items

    return render_template('cart.html', cart_items=products_in_cart, total=total)


@app.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    lang = session.get('lang', 'en')
    product = db.session.get(Product, product_id)
    if not product or not product.is_active:
        return redirect(url_for('products'))

    qty = max(1, int(request.form.get('quantity', 1)))
    cart_session = session.get('cart', {})
    key = str(product_id)
    current_qty = cart_session.get(key, 0)

    if current_qty + qty > product.stock:
        err_msg = TRANSLATIONS[lang]['flash_qty_error'].format(qty=product.stock)
        flash(err_msg, 'error')
        return redirect(request.referrer or url_for('product_detail', product_id=product_id))

    cart_session[key] = current_qty + qty
    session['cart'] = cart_session
    flash(TRANSLATIONS[lang]['flash_cart_added'], 'success')
    return redirect(request.referrer or url_for('products'))


@app.route('/cart/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    lang = session.get('lang', 'en')
    product = db.session.get(Product, product_id)
    if not product:
        return redirect(url_for('cart'))

    qty = int(request.form.get('quantity', 1))
    cart_session = session.get('cart', {})

    if qty <= 0:
        cart_session.pop(str(product_id), None)
    elif qty > product.stock:
        err_msg = TRANSLATIONS[lang]['flash_qty_error'].format(qty=product.stock)
        flash(err_msg, 'error')
        cart_session[str(product_id)] = product.stock
    else:
        cart_session[str(product_id)] = qty

    session['cart'] = cart_session
    return redirect(url_for('cart'))


@app.route('/cart/remove/<int:product_id>')
def remove_from_cart(product_id):
    cart_session = session.get('cart', {})
    cart_session.pop(str(product_id), None)
    session['cart'] = cart_session
    return redirect(url_for('cart'))


@app.route('/cart/count')
def cart_count():
    cart_session = session.get('cart', {})
    return jsonify({'count': sum(max(0, int(v)) for v in cart_session.values())})


# ─────────────────────────────────────────────────────────────────────────────
# CHECKOUT ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    lang = session.get('lang', 'en')
    cart_items = session.get('cart', {})
    if not cart_items:
        return redirect(url_for('cart'))

    products_in_cart = []
    total = 0
    for pid, qty in cart_items.items():
        p = db.session.get(Product, int(pid))
        if p and p.is_active:
            subtotal = p.price * qty
            total += subtotal
            products_in_cart.append({'product': p, 'quantity': qty, 'subtotal': subtotal})

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        notes = request.form.get('notes', '').strip()

        if not name or not phone or not address or not city:
            flash(TRANSLATIONS[lang]['flash_required_fields'], 'error')
            return render_template('checkout.html', cart_items=products_in_cart, total=total)

        for item in products_in_cart:
            if item['product'].stock < item['quantity']:
                err_stock = TRANSLATIONS[lang]['flash_stock_dropped'].format(
                    name=item['product'].name, qty=item['product'].stock
                )
                flash(err_stock, 'error')
                return render_template('checkout.html', cart_items=products_in_cart, total=total)

        try:
            customer = Customer(
                name=name, phone=phone, email=email, address=address, city=city
            )
            db.session.add(customer)
            db.session.flush()

            order_num = generate_order_number()
            order = Order(
                order_number=order_num,
                customer_id=customer.id,
                total_amount=total,
                notes=notes,
            )
            db.session.add(order)
            db.session.flush()

            for item in products_in_cart:
                item['product'].stock -= item['quantity']
                oi = OrderItem(
                    order_id=order.id,
                    product_id=item['product'].id,
                    quantity=item['quantity'],
                    unit_price=item['product'].price,
                    subtotal=item['subtotal'],
                )
                db.session.add(oi)

            db.session.commit()
            session['cart'] = {}
            session['last_order'] = order_num
            return redirect(url_for('order_success', order_number=order_num))

        except Exception:
            db.session.rollback()
            flash(TRANSLATIONS[lang]['flash_order_error'], 'error')
            return render_template('checkout.html', cart_items=products_in_cart, total=total)

    return render_template('checkout.html', cart_items=products_in_cart, total=total)


@app.route('/order/success/<order_number>')
def order_success(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template('order_success.html', order=order)


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = AdminUser.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials.', 'error')
    return render_template('admin/login.html')


@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))


@app.route('/admin')
@login_required
def admin_dashboard():
    stats = {
        'total_products': Product.query.filter_by(is_active=True).count(),
        'total_orders': Order.query.count(),
        'total_customers': Customer.query.count(),
        'pending_orders': Order.query.filter_by(status='Pending').count(),
        'total_revenue': db.session.query(db.func.sum(Order.total_amount)).scalar() or 0,
    }
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html', stats=stats, recent_orders=recent_orders)


# ── FIX BUG-4a: filter is_active=True so soft-deleted products never appear ──
@app.route('/admin/products')
@login_required
def admin_products():
    products_list = (
        Product.query
        .filter_by(is_active=True)
        .order_by(Product.created_at.desc())
        .all()
    )
    return render_template('admin/admin_products.html', products=products_list)


# ── FIX BUG-1a/1b (category field) + BUG-2a (request.files for image) ────────
@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    categories = [
        'Plastic Chairs', 'Plastic Tables', 'Plastic Buckets',
        'Plastic Containers', 'Storage Products', 'Household Products',
        'Industrial Products',
    ]
    if request.method == 'POST':
        # ── Image upload: read from request.files, not request.form ──────────
        image_filename = 'default.jpg'
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            image_filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        # ── Convert empty SKU string to None to avoid UNIQUE constraint hits ─
        raw_sku = request.form.get('sku', '').strip()

        p = Product(
            name=request.form.get('name', '').strip(),
            name_ar=request.form.get('name_ar', '').strip() or None,
            category=request.form.get('category'),          # ← now present in form
            description=request.form.get('description', '').strip() or None,
            price=float(request.form.get('price', 0) or 0),
            stock=int(request.form.get('stock', 0) or 0),
            sku=raw_sku or None,
            weight=request.form.get('weight', '').strip() or None,
            dimensions=request.form.get('dimensions', '').strip() or None,
            color=request.form.get('color', '').strip() or None,
            image=image_filename,
            is_featured=bool(request.form.get('is_featured')),
            is_active=True,
        )
        db.session.add(p)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin_products'))

    return render_template('admin/product_form.html', product=None, categories=categories, action='Add')


# ── FIX BUG-1c (all fields) + BUG-2b (image upload in edit) ─────────────────
@app.route('/admin/products/edit/<int:pid>', methods=['GET', 'POST'])
@login_required
def admin_edit_product(pid):
    product = db.session.get(Product, pid)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('admin_products'))

    categories = [
        'Plastic Chairs', 'Plastic Tables', 'Plastic Buckets',
        'Plastic Containers', 'Storage Products', 'Household Products',
        'Industrial Products',
    ]

    if request.method == 'POST':
        # ── Update every editable field ──────────────────────────────────────
        product.name = request.form.get('name', '').strip()
        product.name_ar = request.form.get('name_ar', '').strip() or None
        product.category = request.form.get('category')
        product.description = request.form.get('description', '').strip() or None
        product.price = float(request.form.get('price', 0) or 0)
        product.stock = int(request.form.get('stock', 0) or 0)
        product.sku = request.form.get('sku', '').strip() or None
        product.weight = request.form.get('weight', '').strip() or None
        product.dimensions = request.form.get('dimensions', '').strip() or None
        product.color = request.form.get('color', '').strip() or None
        product.is_featured = bool(request.form.get('is_featured'))

        # ── Image: only replace if a new file was actually uploaded ──────────
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            image_filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            product.image = image_filename

        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_products'))

    return render_template('admin/product_form.html', product=product, categories=categories, action='Edit')

@app.route('/admin/update-order/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'Done'  # Update the database field
    db.session.commit()    # Save the change
    return redirect(url_for('admin_dashboard')) # Redirect back to the dashboard
@app.route('/admin/order/<int:order_id>')
@login_required
def admin_order_details(order_id):
    # 1. Get the main order
    order = db.session.get(Order, order_id)
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('admin_dashboard'))
        
    # 2. Get the customer details
    customer = db.session.get(Customer, order.customer_id)
    
    # 3. Get the items and match them with product names
    items = OrderItem.query.filter_by(order_id=order_id).all()
    
    order_details = []
    for item in items:
        product = db.session.get(Product, item.product_id)
        order_details.append({
            'name': product.name if product else 'Unknown Product',
            'sku': product.sku if product else 'N/A',
            'quantity': item.quantity,
            'price': item.unit_price,
            'subtotal': item.subtotal
        })
        
    return render_template('admin/admin_order_details.html', 
                           order=order, 
                           customer=customer, 
                           order_details=order_details)

@app.route('/admin/products/delete/<int:pid>', methods=['POST'])
@login_required
def admin_delete_product(pid):
    product = db.session.get(Product, pid)
    if product:
        product.is_active = False          # soft-delete: invisible after route fix
        db.session.commit()
        flash('Product deleted.', 'success')
    return redirect(url_for('admin_products'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
