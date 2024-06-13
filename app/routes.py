from flask import render_template, flash, redirect, url_for, request
from functools import wraps
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, AddCategoryForm, AddProductForm, ResetPasswordForm
from flask_login import current_user, login_user, logout_user, login_required, LoginManager
import sqlalchemy as sa
from app.models import User, Product, Category, CartItem, Order, OrderItem
from urllib.parse import urlsplit
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os

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

@app.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.country = form.country.data
        current_user.street = form.street.data
        current_user.postal_number = form.postal_number.data
        current_user.house_number = form.house_number.data
        current_user.bus_number = form.bus_number.data
        db.session.commit()  
        flash('Your changes have been saved.')  
        return redirect(url_for('index')) 

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

@app.route('/add_data', methods=['GET'])
def add_data():
    category_choices = [(c.id, c.name) for c in Category.query.all()]
    product_form = AddProductForm()
    product_form.category.choices = category_choices
    category_form = AddCategoryForm()
    return render_template('add_data.html', title='Add Data', product_form=product_form, category_form=category_form, category_choices=category_choices)

@app.route('/add_category', methods=['POST'])
def add_category():
    category_form = AddCategoryForm()
    if category_form.validate_on_submit():
        category = Category(name=category_form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!')
        return redirect(url_for('add_data'))
    return render_template('add_data.html', title='Add Data', category_form=category_form)

@app.route('/add_product', methods=['POST'])
def add_product():
    category_choices = [(c.id, c.name) for c in Category.query.all()]
    product_form = AddProductForm()
    product_form.category.choices = category_choices
    if product_form.validate_on_submit():
        image_file = request.files['image']  # Haal het bestand op uit het verzoek
        if image_file:  # Controleer of er een bestand is geüpload
            filename = secure_filename(image_file.filename)  # Genereer een veilige bestandsnaam
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Sla het bestand op in de uploadmap
        else:
            filename = 'default_product_image.jpg'  # Als er geen afbeelding is geüpload, gebruik een standaardafbeelding

        # Maak een nieuw productobject aan met de ontvangen gegevens en de bestandsnaam van de afbeelding
        product = Product(
            name=product_form.name.data,
            description=product_form.description.data,
            price=product_form.price.data,
            category_id=product_form.category.data,
            image_filename=filename  # Koppel de bestandsnaam van de afbeelding aan het product
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!')
        return redirect(url_for('add_data'))
    return render_template('add_data.html', title='Add Data', product_form=product_form, category_choices=category_choices)



@app.route('/delete_data')
@login_required
@admin_required
def delete_data():
    categories = Category.query.all()
    products = Product.query.all()
    return render_template('delete_data.html', categories=categories, products=products)

@app.route('/delete_category/<int:category_id>', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    
    flash('Category deleted successfully!')
    return redirect(url_for('delete_data'))

@app.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted successfully!')
    return redirect(url_for('delete_data'))

@app.route('/product/<int:product_id>')
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

@app.route('/add_to_cart/<int:product_id>', methods=['GET', 'POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        if current_user.is_authenticated:
            cart_item = CartItem(user_id=current_user.id, product_id=product_id)
            db.session.add(cart_item)
            db.session.commit()
            flash('Item added to cart successfully!')
        else:
            flash('You need to log in to add items to the cart.', 'error')
            return redirect(url_for('login'))
        return redirect(url_for('index'))
    else:
        # Handle GET request if needed
        return redirect(url_for('index'))



@app.route('/cart')
@login_required
def view_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


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
    return render_template('checkout.html', cart_items=cart_items, total_price=total_price)



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




