from werkzeug.utils import secure_filename
from PIL import Image
import os
from app import app, db, ALLOWED_EXTENSIONS
from app.models import User, Goods, Category, Order, Order_items
from flask import render_template
from flask import url_for
from flask import redirect
from flask import request
from flask import flash
from flask import session
from forms import LoginForm, RegistrationForm
from forms import CategoryCreationForm, GoodsCreationForm, ChangeCategoryForm, ChangeItmForm, CheckoutForm, ConfirmForm
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from sqlalchemy import select
from werkzeug.urls import url_parse


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    goods = Goods.query.all()
    return render_template('index.html', goods=goods)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title="Sing In", form=form)


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
        user = User(username=form.username.data, email=form.email.data, user_role=1)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form)


def crop_img(filename):
    img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    width, height = img.size
    if width > height:
        left = ((width - height) / 2)
        top = 0
        right = ((width - height) / 2) + height
        bottom = height
        img.crop((left, top, right, bottom)).save('/home/winda/flask/eshop/app/static/img_good/' + filename)
    elif width < height:
        left = 0
        top = ((height - width) / 2)
        right = width
        bottom = ((height - width) / 2) + width
        img.crop((left, top, right, bottom)).save('/home/winda/flask/eshop/app/static/img_good/' + filename)


@app.route('/newgood', methods=['GET', 'POST'])
@login_required
def new_good():
    form = GoodsCreationForm()
    form.set_cat_choices()
    if form.validate_on_submit():
        filename = secure_filename(form.image.data.filename)
        form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        crop_img(filename)
        goods = Goods(name=form.name.data, category=int(form.category.data), price=form.price.data,
                      image=form.image.data.filename, description=form.description.data)
        db.session.add(goods)
        db.session.commit()
        flash('New good created')
        os.path.join(app.config['UPLOAD_FOLDER'], filename)

        return redirect(url_for('index'))
    return render_template('admin/newgood.html', title="New Good", form=form)


@app.route('/newcategory', methods=['GET', 'POST'])
@login_required
def new_category():
    form = CategoryCreationForm()
    form.set_cat_choices()
    if form.validate_on_submit():
        category = Category(category=form.name.data,
                            description=form.description.data, parents=form.parents.data)
        db.session.add(category)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('admin/newcategory.html', title="New Category", form=form)


@app.route('/good/<id>', methods=['GET', 'POST'])
def good(id):
    items = session.get('cart')
    goods = Goods.query.filter_by(id=id).first_or_404()
    count = 1
    if items is not None:
        for x in items:
            count = x.get(id)
            if count is not None:
                goods.__dict__['counts'] = count
                break
            else:
                count = 1
    return render_template('good.html', goods=goods, count=count)


@app.route('/categories', methods=['GET', 'POST'])
def categories():
    cat = Category.query.all()
    inherited = Category.query.filter_by(parents=id)
    return render_template('categories.html', category=cat)


@app.route('/category/<id>', methods=['GET', 'POST'])
def category(id):
    cat = Category.query.filter_by(id=id).first_or_404()
    goods = Goods.query.filter_by(category=id).all()
    inherited = Category.query.filter_by(parents=id).all()
    print(goods)
    i = 0
    if inherited is not None:
        for x in inherited:
            good = Goods.query.filter_by(category=inherited[i].id).all()
            for z in good:
                goods.append(z)
            i = i + 1
    print(goods)
    return render_template('category.html', category=cat, goods=goods, inherited=inherited)


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    items = session.get('cart')
    id_s = []
    count_s = []
    goods = []
    totalprice = 0
    if items is not None or []:
        for x in items:
            id_s += x.keys()
            count_s += x.values()
        i = 0
        for x in id_s:
            goods.append(Goods.query.filter_by(id=id_s[i]).first())
            i = i + 1
        i = 0
        for g in goods:
            g.__dict__['count'] = count_s[i]
            i = i + 1
            totalprice += g.price * g.count
    else:
        return render_template('cart/emptycart.html')
    return render_template('cart/cart.html', goods=goods, count=count_s, totalprice=totalprice)


@app.route('/change_qty/', methods=['GET', 'POST'])
def change_qty():
    itm_id = str(request.form['itm_id'])
    qty = int(request.form['count'])
    if 'cart' in session:
        if any(itm_id in d for d in session['cart']):
            for d in session['cart']:
                d.update((k, qty) for k, v in d.items() if k == itm_id)
                session.modified = True
            print(session['cart'])
    return redirect(url_for('cart'))


@app.route('/more_qty/', methods=['GET', 'POST'])
def more_qty():
    itm_id = str(request.form['itm_id'])
    qty = int(request.form['count'])
    qty = qty + 1
    if 'cart' in session:
        if any(itm_id in d for d in session['cart']):
            for d in session['cart']:
                d.update((k, qty) for k, v in d.items() if k == itm_id)
                session.modified = True
            print(session['cart'])
    return redirect(url_for('cart'))


@app.route('/less_qty/', methods=['GET', 'POST'])
def less_qty():
    itm_id = str(request.form['itm_id'])
    qty = int(request.form['count'])
    qty = qty - 1
    if 'cart' in session:
        if any(itm_id in d for d in session['cart']):
            for d in session['cart']:
                d.update((k, qty) for k, v in d.items() if k == itm_id)
                session.modified = True
            print(session['cart'])
    return redirect(url_for('cart'))


@app.route('/add_to_cart/', methods=['GET', 'POST'])
def add_to_cart():
    itm_id = request.form['itm_id']
    qty = int(request.form['count'])
    if 'cart' in session:
        if not any(itm_id in d for d in session['cart']):
            session['cart'].append({itm_id: qty})
            session.modified = True
        elif any(itm_id in d for d in session['cart']):
            for d in session['cart']:
                d.update((k, qty) for k, v in d.items() if k == itm_id)
                session.modified = True
    else:
        session['cart'] = [{itm_id: qty}]
        session.modified = True
    print(session['cart'])
    return redirect(request.referrer)


@app.route('/delete_item/', methods=['GET', 'POST'])
def delete_item():
    items = session.get('cart')
    itm_id = str(request.form['itm_id'])
    qty = int(request.form['count'])
    id_s = []
    c = 0
    for x in items:
        id_s += x.keys()
        if id_s[c] == itm_id:
            items.remove({itm_id: qty})
            break
        c = c + 1
    if items == []:
        session.pop('cart')
    else:
        session['cart'] = items
    return redirect(url_for('cart'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/admin/goods')
@login_required
def admin_goods():
    goods = Goods.query.all()
    return render_template('admin/goods.html', goods=goods)


@app.route('/admin_delete_item/', methods=['GET', 'POST'])
@login_required
def admin_delete_item():
    print(request.form['itm_id'])
    itm_id = str(request.form['itm_id'])
    Goods.query.filter_by(id=itm_id).delete()
    db.session.commit()
    return redirect(request.referrer)


@app.route('/admin/categories')
@login_required
def admin_categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)


@app.route('/admin_delete_category/', methods=['GET', 'POST'])
@login_required
def admin_delete_category():
    print(request.form['cat_id'])
    cat_id = str(request.form['cat_id'])
    Category.query.filter_by(id=cat_id).delete()
    db.session.commit()
    return redirect(request.referrer)


@app.route('/admin/category/<id>', methods=['GET', 'POST'])
@login_required
def admin_category(id):
    form = ChangeCategoryForm()
    form.set_cat_choices()
    category = Category.query.filter_by(id=id).first_or_404()
    if form.validate_on_submit():
        category.category = form.name.data
        category.parents = form.parents.data
        category.description = form.description.data
        db.session.commit()
        return redirect(request.referrer)
    elif request.method == 'GET':
        form.parents.default = category.parents
        form.process()
        form.name.data = category.category
        form.description.data = category.description

    return render_template('admin/change_category.html', category=category, form=form)


@app.route('/admin/good/<id>', methods=['GET', 'POST'])
@login_required
def admin_good(id):
    form = ChangeItmForm()
    form.set_cat_choices()
    good = Goods.query.filter_by(id=id).first_or_404()
    if form.validate_on_submit():
        good.name = form.name.data
        good.category = form.category.data
        good.price = form.price.data
        good.description = form.description.data
        if form.image.data.filename != '':
            good.image = form.image.data.filename
            filename = secure_filename(form.image.data.filename)
            crop_img(filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            os.path.join(app.config['UPLOAD_FOLDER'], filename)
        db.session.commit()
        return redirect(request.referrer)
    elif request.method == 'GET':
        form.category.default = good.category
        form.image.default = good.image
        form.process()
        form.name.data = good.name
        form.price.data = good.price
        form.description.data = good.description
    return render_template('admin/change_good.html', goods=good, form=form)


@app.route('/checkout/', methods=['GET', 'POST'])
def checkout():
    current_order = Order.query.filter_by(user_id=current_user.id).filter_by(finished=0).first()
    if current_order is not None:
        return redirect(url_for('confirm_checkout'))
    else:
        items = session.get('cart')
        form = CheckoutForm()
        id_s = []
        count_s = []
        goods = []
        totalprice = 0
        if items is not None or []:
            for x in items:
                id_s += x.keys()
                count_s += x.values()
            i = 0
            for x in id_s:
                goods.append(Goods.query.filter_by(id=id_s[i]).first())
                i = i + 1
            i = 0
            for g in goods:
                g.__dict__['count'] = count_s[i]
                i = i + 1
                totalprice += g.price * g.count
        else:
            return render_template('cart/emptycart.html')
        if form.validate_on_submit():
            address = form.city.data + " " + form.address.data
            order = Order(user_id=current_user.id, address=address, fname=form.firstname.data, lname=form.lastname.data, payment=form.payment.data, phone=form.phone.data, finished=0, totalprice=totalprice)
            db.session.add(order)
            db.session.commit()
            return redirect(url_for('confirm_checkout'))
    return render_template('cart/checkout.html', goods=goods, count=count_s, totalprice=totalprice, form=form)


@app.route('/confirmcheckout/', methods=['GET', 'POST'])
def confirm_checkout():
    form = ConfirmForm()
    current_order = Order.query.filter_by(user_id=current_user.id).filter_by(finished=0).first()
    items = session.get('cart')
    id_s = []
    count_s = []
    goods = []
    totalprice = 0
    if items is not None or []:
        for x in items:
            id_s += x.keys()
            count_s += x.values()
        i = 0
        for x in id_s:
            goods.append(Goods.query.filter_by(id=id_s[i]).first())
            i = i + 1
        i = 0
        for g in goods:
            g.__dict__['count'] = count_s[i]
            i = i + 1
            totalprice += g.price * g.count
        current_order.totalprice = totalprice
        db.session.commit()
    orderid = current_order.id
    if form.validate_on_submit():
        current_order.finished = 1
        current_order.totalprice = totalprice
        db.session.commit()
        for g in goods:
            orderitm = Order_items(order_id=orderid, good_id=g.id, count=g.count)
            db.session.add(orderitm)
            db.session.commit()
        session.pop('cart')
        return redirect(url_for('index'))
    return render_template('/cart/confirmcheckout.html', order=current_order, goods=goods, totalprice=totalprice, count=count_s,form=form)

