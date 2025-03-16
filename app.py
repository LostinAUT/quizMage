# app.py
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

# 初始化 Flask 应用
app = Flask(__name__)
app.secret_key = 'dev'

# 配置数据库
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

# 初始化扩展
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

# 导入视图
from views.login_views import login_bp
from views.student_views import student_bp
from views.teacher_views import teacher_bp

# 注册蓝图
app.register_blueprint(login_bp, url_prefix='/')
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(teacher_bp, url_prefix='/teacher')

if __name__ == '__main__':
    app.run(debug=True)
