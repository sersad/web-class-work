import os
from datetime import datetime

from flask import Flask, render_template, redirect, make_response, request, session, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session, news_api, news_resources
from data.news import News
from data.users import User
from forms.news import NewsForm
from forms.user import RegisterForm, LoginForm

from flask_restful import reqparse, abort, Api, Resource

from waitress import serve

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

api = Api(app)
# для списка объектов
api.add_resource(news_resources.NewsListResource, '/api/v2/news')

# для одного объекта
api.add_resource(news_resources.NewsResource, '/api/v2/news/<int:news_id>')




# Затем сразу после создания приложения flask инициализируем LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

# Чтобы продлить жизнь сессии
# app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)


@login_manager.user_loader
def load_user(user_id):
    """
    функция для получения пользователя, украшенная декоратором login_manager.user_loader
    """
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def add_user(db_sess):
    user1 = User(name="Пользователь 1",
                 about="биография пользователя 1",
                 email="email1@email.ru")
    user2 = User(name="Пользователь 2",
                 about="биография пользователя 2",
                 email="email2@email.ru")
    user3 = User(name="Пользователь 3",
                 about="биография пользователя 3",
                 email="email3@email.ru")
    db_sess.add(user1)
    db_sess.add(user2)
    db_sess.add(user3)
    db_sess.commit()


def add_news(db_sess):
    user1 = db_sess.query(User).filter(User.id == 1).first()

    user2 = db_sess.query(User).filter(User.id == 2).first()
    news1 = News(title="Первая новость", content="Привет блог!",
                 user=user1, is_private=False)
    news2 = News(title="Вторая новость", content="Привет блог!",
                 user=user2, is_private=False)
    news3 = News(title="Третья новость", content="Привет блог!",
                 user=user1, is_private=False)
    news4 = News(title="Приватная новость", content="Привет блог!",
                 user=user1, is_private=False)
    db_sess.add(news1)
    db_sess.add(news2)
    db_sess.add(news3)
    db_sess.add(news4)
    db_sess.commit()

    # # И самый удобный на наш взгляд вариант — использовать то,
    # # что через объект класса User мы можем взаимодействовать с
    # # его записями в таблице News почти как со списком:
    news = News(title="Личная запись", content="Эта запись личная",
                is_private=True)
    user1.news.append(news)
    db_sess.commit()


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route("/session_test")
def session_test():
    """
    Сессии во Flask очень похожи на куки, но имеют большое преимущество:
    гарантируется, что содержимое сессии не может быть изменено пользователем
    (если у него нет нашего секретного ключа).
    Для работы с сессиями есть специальный объект flask.session
    :return:
    """
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Если форма логина прошла валидацию, мы находим пользователя с введенной почтой,
    проверяем, введен ли для него правильный пароль, если да,
    вызываем функцию login_user модуля flask-login и передаем туда объект
    нашего пользователя, а также значение галочки «Запомнить меня».
    После чего перенаправляем пользователя на главную страницу нашего приложения."""
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/news',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        # мы изменили текущего пользователя с помощью метода merge
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/news/<id_>', methods=['GET', 'POST'])
@login_required
def edit_news(id_):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id_,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id_,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id_>', methods=['GET', 'POST'])
@login_required
def news_delete(id_):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id_,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


# @app.errorhandler(404)
# def not_found(error):
#     """при передаче неправильного параметра ответ от сервера будет приходить в формате JSON,
#     и клиентское приложение не будет падать
#     """
#     return make_response(jsonify({'error': 'Not found'}), 404)


def main():
    db_session.global_init("db/blogs.db")
    db_sess = db_session.create_session()
    # # add_user(db_sess)
    # # add_news(db_sess)

    #  регистрация схемы в которую добавили обработчик
    app.register_blueprint(news_api.blueprint)

    # news = db_sess.query(News).get(1)
    #
    # print(news.title)
    # print(news.user)
    #
    # user = db_sess.query(User).get(1)
    # print(user.news)
    # app.run(port="8080", host="127.0.0.1")

    port = int(os.environ.get('PORT', 5000))
    # с дефаултными значениями будет не более 4 потов
    serve(app, port=port, host="0.0.0.0")


if __name__ == '__main__':
    main()
