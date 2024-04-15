from flask import render_template,flash,redirect,url_for,request
from app import app,db
from app.forms import LoginForm,RegistrationForm,EditProfileForm,AddCategoryForm,AddProductForm
from flask_login import current_user, login_user,logout_user,login_required
import sqlalchemy as sa
from app.models import User,Product,Category
from urllib.parse import urlsplit

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
    return render_template('add_data.html', title='Add Data', category_form=category_form,)

@app.route('/add_product', methods=['POST'])
def add_product():
    category_choices = [(c.id, c.name) for c in Category.query.all()]
    product_form = AddProductForm()
    product_form.category.choices = category_choices
    if product_form.validate():
        product = Product(
            name=product_form.name.data,
            description=product_form.description.data,
            price=product_form.price.data,
            category_id=product_form.category.data 
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!')
        return redirect(url_for('add_data'))
    return render_template('add_data.html', title='Add Data', product_form=product_form, category_choices=category_choices)

@app.route('/delete_data')
def delete_data():
    categories = Category.query.all()
    products = Product.query.all()
    return render_template('delete_data.html', categories=categories, products=products)



@app.route('/delete_category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    
    flash('Category deleted successfully!')
    return redirect(url_for('delete_data'))

@app.route('/delete_product/<int:product_id>', methods=['POST'])
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
