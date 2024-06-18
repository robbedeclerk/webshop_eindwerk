from flask import render_template, flash, redirect, url_for, request
from functools import wraps
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, AddCategoryForm, AddProductForm, ResetPasswordForm, AddToCartForm
from flask_login import current_user, login_user, logout_user, login_required, LoginManager
import sqlalchemy as sa
from app.models import User, Product, Category, CartItem, Order, OrderItem
from urllib.parse import urlsplit
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os
from sqlalchemy import func


UPLOAD_FOLDER = 'app/static/assets/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

login_manager = LoginManager()
login_manager.init_app(app)

def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.admin_rights:
            # Redirect to a suitable page when admin rights are required
            return redirect(url_for('error_page'))
        return func(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@app.route('/index')
def index():
    categories = Category.query.all()
    products = Product.query.all()
    return render_template('index.html', categories=categories, products=products)

if __name__=='__main__':
    app.run(debug=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            country=form.country.data,
            street=form.street.data,
            postal_number=form.postal_number.data,
            house_number=form.house_number.data,
            bus_number=form.bus_number.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/profile',methods=['GET'])
@login_required
def profile():
    username=current_user.username
    user_data=db.session.scalar(sa.select(User).where(User.username==username))
    return render_template('profile.html',user=user_data)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()  # Create an instance of your form class

    if form.validate_on_submit():
        try:
            current_user.email = form.email.data
            current_user.country = form.country.data
            current_user.street = form.street.data
            current_user.postal_number = form.postal_number.data
            current_user.house_number = form.house_number.data
            current_user.bus_number = form.bus_number.data

            db.session.commit()  # Commit changes to the database

            flash('Your changes have been saved.')
            return redirect(url_for('index'))
        
        except Exception as e:
            db.session.rollback()  # Rollback changes on error
            flash(f'Error saving changes: {str(e)}', 'error')
            # Optionally, print or log the error for debugging
            print(f'Error saving changes: {str(e)}')

    elif request.method == 'GET':
        form.email.data = current_user.email
        form.country.data = current_user.country
        form.street.data = current_user.street
        form.postal_number.data = current_user.postal_number
        form.house_number.data = current_user.house_number
        form.bus_number.data = current_user.bus_number

    return render_template('edit_profile.html', title='Edit Profile', form=form, user=current_user)

@app.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password_hash, form.old_password.data):
            new_password_hash = generate_password_hash(form.new_password.data)
            current_user.password_hash = new_password_hash
            db.session.commit()
            flash('Your password has been reset successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Old password is incorrect. Please try again.', 'error')
    return render_template('reset_password.html', form=form)

@app.route('/manage_shop_data', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_shop_data():
    category_choices = [(c.id, c.name) for c in Category.query.all()]
    product_form = AddProductForm()
    product_form.category.choices = category_choices
    category_form = AddCategoryForm()

    if request.method == 'POST':
        if 'add_category' in request.form:
            if category_form.validate_on_submit():
                category = Category(name=category_form.name.data)
                db.session.add(category)
                db.session.commit()
                flash('Category added successfully!')
                return redirect(url_for('manage_shop_data'))

        if 'add_product' in request.form:
            if product_form.validate_on_submit():
                image_file = request.files['image']
                if image_file:
                    filename = secure_filename(image_file.filename)
                    image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    filename = 'default_product_image.jpg'

                product = Product(
                    name=product_form.name.data,
                    description=product_form.description.data,
                    price=product_form.price.data,
                    category_id=product_form.category.data,
                    image_filename=filename
                )
                db.session.add(product)
                db.session.commit()
                flash('Product added successfully!')
                return redirect(url_for('manage_shop_data'))

        if 'delete_category' in request.form:
            category_id = request.form.get('category_id')
            if category_id:
                category = Category.query.get_or_404(category_id)
                db.session.delete(category)
                db.session.commit()
                flash('Category deleted successfully!')
                return redirect(url_for('manage_shop_data'))

        if 'delete_product' in request.form:
            product_id = request.form.get('product_id')
            if product_id:
                product = Product.query.get_or_404(product_id)
                db.session.delete(product)
                db.session.commit()
                flash('Product deleted successfully!')
                return redirect(url_for('manage_shop_data'))

    categories = Category.query.all()
    products = Product.query.all()

    return render_template('manage_shop_data.html', title='Manage Shop Data', 
                           product_form=product_form, category_form=category_form, 
                           categories=categories, products=products)


@app.route('/product/<int:product_id>')
def product(product_id):
    product = Product.query.get_or_404(product_id)
    form = AddToCartForm()
    return render_template('product.html', product=product, form=form)

@app.route('/add_to_cart/<int:product_id>', methods=['GET', 'POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('index'))

    form = AddToCartForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            quantity = form.quantity.data
            cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
            if cart_item:
                cart_item.quantity += quantity
            else:
                cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
                db.session.add(cart_item)
            db.session.commit()
            flash('Item added to cart successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('You need to log in to add items to the cart.', 'error')
            return redirect(url_for('login'))

    else:
        flash('Failed to add item to cart. Please check the quantity.', 'error')

    return redirect(url_for('product', product_id=product_id))




@app.route('/cart')
@login_required
def view_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    total_price_formatted = "{:.2f}".format(total_price)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price_formatted)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login'))

@app.route('/remove_from_cart/<int:cart_item_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_item_id):
    cart_item = CartItem.query.get_or_404(cart_item_id)
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart successfully!')
    else:
        flash('Item not found in cart.', 'error')
    return redirect(url_for('view_cart'))

@app.route('/update_cart/<int:cart_item_id>', methods=['POST'])
@login_required
def update_cart(cart_item_id):
    cart_item = CartItem.query.get_or_404(cart_item_id)
    new_quantity = request.form.get('quantity', type=int)
    if new_quantity is not None and new_quantity > 0:
        cart_item.quantity = new_quantity
        db.session.commit()
        flash('Item updated successfully!')
    else:
        flash('Invalid quantity.', 'error')
    return redirect(url_for('view_cart'))



@app.route('/checkout', methods=['GET'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    total_price_formatted = "{:.2f}".format(total_price)
    return render_template('checkout.html', cart_items=cart_items, total_price=total_price_formatted)




from flask import request

@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty.', 'error')
        return redirect(url_for('index'))
    
    # Controleer of alternatieve adresgegevens zijn ingevuld
    alt_country = request.form.get('alt_country')
    alt_street = request.form.get('alt_street')
    alt_postal_number = request.form.get('alt_postal_number')
    alt_house_number = request.form.get('alt_house_number')
    alt_bus_number = request.form.get('alt_bus_number')
    
    # Gebruik standaardadresgegevens van de huidige gebruiker
    country = current_user.country
    street = current_user.street
    postal_number = current_user.postal_number
    house_number = current_user.house_number
    bus_number = current_user.bus_number
    
    # Gebruik alternatieve adresgegevens als deze zijn ingevuld
    if alt_country:
        country = alt_country
    if alt_street:
        street = alt_street
    if alt_postal_number:
        postal_number = alt_postal_number
    if alt_house_number:
        house_number = alt_house_number
    if alt_bus_number:
        bus_number = alt_bus_number
    
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    # Create the order with address details
    order = Order(
        user_id=current_user.id,
        total_price=total_price,
        country=country,
        street=street,
        postal_number=postal_number,
        house_number=house_number,
        bus_number=bus_number
    )
    db.session.add(order)
    db.session.commit()  # Commit to get the order id
    
    # Create order items
    for item in cart_items:
        order_item = OrderItem(order_id=order.id, product_id=item.product.id, quantity=item.quantity)
        db.session.add(order_item)
        db.session.delete(item)  # Remove the item from the cart
    
    db.session.commit()
    
    flash('Your order has been placed successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/statistics')
@admin_required
def statistics():
    products = Product.query.all()
    product_stats = []

    for product in products:
        total_sold = db.session.query(db.func.sum(OrderItem.quantity)).filter_by(product_id=product.id).scalar() or 0
        product_stats.append({
            'name': product.name,
            'total_sold': total_sold
        })

    return render_template('statistics.html', products=product_stats)

@app.route('/orders', methods=['GET'])
@admin_required
def orders():
    status = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = 5
    search_term = request.args.get('search', '')

    if status == 'complete':
        query = Order.query.filter_by(complete=True)
    elif status == 'not_complete':
        query = Order.query.filter_by(complete=False)
    else:
        query = Order.query

    if search_term:
        if search_term.isdigit():
            query = query.filter(Order.id == int(search_term))
        else:
            flash('Please enter a valid order ID for search.', 'error')
            return redirect(url_for('orders'))

    orders = query.order_by(Order.date_ordered.desc()).paginate(page=page, per_page=per_page, error_out=False)

    prev_page = url_for('orders', page=orders.prev_num, status=status, search=search_term) if orders.has_prev else None
    next_page = url_for('orders', page=orders.next_num, status=status, search=search_term) if orders.has_next else None

    return render_template('orders.html', orders=orders, prev_page=prev_page, next_page=next_page, status=status, search_term=search_term)


@app.route('/order/<int:order_id>')
@admin_required
def order_details(order_id):
    order = Order.query.get_or_404(order_id)
    order_items = OrderItem.query.filter_by(order_id=order_id).all()
    return render_template('order_details.html', order=order, order_items=order_items)

@app.route('/toggle_order_status/<int:order_id>', methods=['POST'])
def toggle_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    order.complete = not order.complete 
    db.session.commit()
    return redirect(url_for('order_details', order_id=order_id))

@app.route('/popular_items')
def popular_items():
    popular_items = db.session.query(Product, db.func.count(OrderItem.product_id).label('total_orders')) \
                    .join(OrderItem, Product.id == OrderItem.product_id) \
                    .group_by(Product.id) \
                    .order_by(db.desc('total_orders')) \
                    .limit(4) \
                    .all()

    categories = Category.query.all()

    return render_template('popular_items.html', popular_items=popular_items, categories=categories)

@app.route('/new_items')
def new_items():
    new_items = Product.query.order_by(Product.created_at.desc()).limit(4).all()

    categories = Category.query.all() 

    return render_template('new_items.html', new_items=new_items, categories=categories)