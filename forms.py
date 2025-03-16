#Flask 表单定义

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo




class HelloForm(FlaskForm):
    username = StringField(u'用户名', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField(u'密码', validators=[Length(0, 10)])
    select = SelectField(u'身份', choices=[('student', 'Student'), ('teacher', 'Teacher')])
    submit = SubmitField(u'登录')

class RegisterForm(FlaskForm):
    identity = SelectField('注册身份', choices=[('student', '学生'), ('teacher', '老师')], validators=[DataRequired()])
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password', message="两次密码必须一致")])
    submit = SubmitField('注册')

class AccountForm(FlaskForm):
    secret = PasswordField(u'旧密码', validators=[DataRequired(), Length(0, 10)], render_kw={'placeholder': '旧密码'})
    password = PasswordField(u'新密码', validators=[DataRequired(), Length(0, 10)], render_kw={'placeholder': '新密码'})
    submit = SubmitField(u'修改密码')

class SelectForm(FlaskForm):
    title = StringField(u'课程号', render_kw={'placeholder': '课程号'})
    submit = SubmitField(u'选课')

class DeleteForm(FlaskForm):
    title = StringField(u'课程号', render_kw={'placeholder': '课程号'})
    submit = SubmitField(u'退课')

class ScoreForm(FlaskForm):
    title_sno = StringField(u'学生号', render_kw={'placeholder': '学生号'})
    title_cno = StringField(u'课程号', render_kw={'placeholder': '课程号'})
    title_score = StringField(u'分数', render_kw={'placeholder': '分数'})
    submit = SubmitField(u'录入')
