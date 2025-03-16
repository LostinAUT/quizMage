# views/teacher_views.py
from flask import Blueprint, render_template, flash, redirect, url_for
from forms import AccountForm, ScoreForm
from db_sqlite import get_sql, update_data

teacher_bp = Blueprint('teacher_bp', __name__)

@teacher_bp.route('/<int:tno>', methods=['GET'])
def profile(tno):
    return render_template('teacher.html', tno=tno)

@teacher_bp.route('/<int:tno>/account', methods=['GET', 'POST'])
def teacher_account(tno):
    form = AccountForm()

    if form.is_submitted():
        result, _ = get_sql("select * from teacher where tno='%s'" % tno)
        if form.secret.data == result[0][2]:
            data = dict(
                tno=tno,
                name=result[0][1],
                password=form.password.data
            )
            update_data(data, "teacher")
            flash(u'修改成功！', 'success')
        else:
            flash(u'原密码错误', 'warning')

    return render_template('teacher_account.html', tno=tno, form=form)

@teacher_bp.route('/<int:tno>/course', methods=['GET'])
def teacher_course(tno):
    result_course, _ = get_sql("SELECT * FROM course WHERE tno='%s'" % tno)

    messages = []
    for i in result_course:
        message = []
        result_score, _ = get_sql("SELECT sno FROM score WHERE cno='%s'" % i[0])
        if not result_score:
            continue
        else:
            for j in result_score:
                result_student, _ = get_sql("select * from student where sno='%s'" % j[0])
                row = {'cno': i[0], 'cname': i[1], 'sno': result_student[0][0], 'name': result_student[0][1],
                       'gender': result_student[0][2], 'major': result_student[0][4], }
                message.append(row)
        messages.append(message)

    titles = [('sno', '学员号'), ('name', '学员姓名'), ('gender', '性别'), ('major', '专业')]
    return render_template('teacher_course.html', tno=tno, messages=messages, titles=titles)


@teacher_bp.route('/<int:tno>/score', methods=['GET', 'POST'])
def teacher_score(tno):
    form = ScoreForm()

    result_course, _ = get_sql("SELECT * FROM course WHERE tno='%s'" % tno)

    messages = []
    for i in result_course:
        message = []
        result_score, _ = get_sql("SELECT * FROM score WHERE cno='%s'" % i[0])
        for j in result_score:
            result_student, _ = get_sql("select name from student where sno='%s'" % j[0])
            row = {'cname': i[1], 'cno': i[0], 'sno': j[0], 'name': result_student[0][0], 'score': j[2]}
            message.append(row)
        messages.append(message)

    titles = [('sno', '学员号'), ('name', '学员姓名'), ('score', '成绩')]

    if form.validate_on_submit():
        if not (form.title_cno.data and form.title_sno.data and form.title_score.data):
            flash(u'输入不完整', 'warning')
        else:
            result, _ = get_sql(
                "select * from score where cno='%s' and sno='%s'" % (form.title_cno.data, form.title_sno.data))
            if result:
                data = dict(
                    sno=form.title_sno.data,
                    cno=form.title_cno.data,
                    score=form.title_score.data
                )
                update_data(data, "score")
                flash(u'录入成功！', 'success')
                return redirect(url_for('teacher_score', tno=tno, messages=messages, titles=titles, form=form))
            else:
                flash(u'该学生未选课', 'warning')

    return render_template('teacher_score.html', tno=tno, messages=messages, titles=titles, form=form)
