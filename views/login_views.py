# views/login_views.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from forms import HelloForm , RegisterForm
from db_sqlite import get_sql,insert_data

login_bp = Blueprint('login_bp', __name__)

@login_bp.route('/', methods=['GET', 'POST'])
def index():
    form = HelloForm()
    if request.method == "GET":
        return render_template('index.html', form=form)

    if form.validate_on_submit():
        if form.select.data == 'student':
            result, _ = get_sql("select * from student where sno='%s'" % form.username.data)
            if not result:
                flash(u'用户名不存在', 'warning')
                return render_template('index.html', form=form)

            if result[0][2] == form.password.data:
                return redirect(url_for('student_bp.profile', sno=form.username.data))
            else:
                flash(u'密码错误', 'warning')
                return render_template('index.html', form=form)

        if form.select.data == 'teacher':
            result, _ = get_sql("select * from teacher where tno='%s'" % form.username.data)
            if not result:
                flash(u'用户名不存在', 'warning')
                return render_template('index.html', form=form)

            if result[0][2] == form.password.data:
                return redirect(url_for('teacher_bp.profile', tno=form.username.data))
            else:
                flash(u'密码错误', 'warning')
                return render_template('index.html', form=form)

@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        identity = form.identity.data  # 选择身份（学生 or 老师）
        username = form.username.data  # 用户名
        password = form.password.data  # 密码

        # 确定数据库表和主键字段
        table = 'student' if identity == 'student' else 'teacher'
        column = 'sno' if identity == 'student' else 'tno'

        # 检查用户名是否已存在
        existing_user, _ = get_sql(f"SELECT * FROM {table} WHERE {column} = '{username}'")
        if existing_user:
            flash('用户名已存在，请选择其他用户名', 'warning')
            return render_template('register.html', form=form)

        # 插入用户数据
        insert_data({column: username, 'password': password}, table)

        flash('注册成功，请登录', 'success')
        return redirect(url_for('login_bp.index'))

    return render_template('register.html', form=form)