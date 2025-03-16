# views/student_views.py
from flask import Blueprint, render_template, flash, redirect, url_for
from forms import AccountForm, SelectForm, DeleteForm, ScoreForm
from db_sqlite import get_sql, update_data, insert_data, delete_data_by_id
from datetime import datetime

student_bp = Blueprint('student_bp', __name__)

@student_bp.route('/<int:sno>', methods=['GET'])
def profile(sno):
    return render_template('student.html', sno=sno)

@student_bp.route('/<int:sno>/account', methods=['GET', 'POST'])
def student_account(sno):
    form = AccountForm()

    result, _ = get_sql("select * from student where sno='%s'" % sno)
    name = result[0][1]
    gender = result[0][2]
    birthday = result[0][3]
    birthtime = datetime.fromtimestamp(result[0][3] / 1000.0).strftime('%Y-%m-%d')
    major = result[0][4]

    if form.validate_on_submit():
        result, _ = get_sql("select * from student where sno='%s'" % sno)
        if form.secret.data == result[0][5]:
            data = dict(
                sno=sno,
                name=name,
                gender=gender,
                birthday=birthday,
                major=major,
                password=form.password.data
            )
            update_data(data, "student")
            flash(u'修改成功！', 'success')
        else:
            flash(u'原密码错误', 'warning')

    return render_template('student_account.html', sno=sno, name=name, gender=gender, birthday=birthtime,
                           major=major, form=form)

@student_bp.route('/<int:sno>/course_select', methods=['GET', 'POST'])
def student_course_select(sno):
    form = SelectForm()

    result_course, _ = get_sql("select * from course")

    messages = []
    for i in result_course:
        result_teacher = get_sql("select name from teacher where tno='%s'" % i[2])
        result_score = get_sql("select count(*) from score where cno='%s'" % i[0])
        message = {'cno': i[0], 'name': i[1], 'tname': result_teacher[0][0][0], 'count': result_score[0][0][0]}
        messages.append(message)

    titles = [('cno', '课程号'), ('name', '课程名'), ('tname', '任课教师'), ('count', '已选课人数')]

    if form.validate_on_submit():
        if not form.title.data:
            flash(u'请填写课程号', 'warning')
        else:
            result, _ = get_sql("select * from course where cno='%s'" % form.title.data)
            if not result:
                flash(u'课程不存在', 'warning')
            else:
                result, _ = get_sql("select * from score where sno='%s' and cno='%s'" % (sno, form.title.data))
                if result:
                    flash(u'课程选过了', 'warning')
                else:
                    data = dict(
                        sno=sno,
                        cno=form.title.data
                    )
                    insert_data(data, "score")
                    flash('选课成功', 'success')

    return render_template('student_course_select.html', sno=sno, messages=messages, titles=titles, form=form)


@student_bp.route('/<int:sno>/course_delete', methods=['GET', 'POST'])
def student_course_delete(sno):
    form = DeleteForm()

    result_score, _ = get_sql("select * from score where sno='%s'" % sno)

    messages = []
    for i in result_score:
        result_course, _ = get_sql("select * from course where cno='%s'" % i[1])
        result_teacher, _ = get_sql("select * from teacher where tno='%s'" % result_course[0][2])
        message = {'cno': i[1], 'cname': result_course[0][1], 'tname': result_teacher[0][1]}
        messages.append(message)

    titles = [('cno', '已选课程号'), ('cname', '课程名'), ('tname', '任课教师')]

    if form.validate_on_submit():
        if not form.title.data:
            flash(u'请填写课程号', 'warning')
        else:
            result, _ = get_sql("select * from score where cno='%s' and sno='%s'" % (form.title.data, sno))
            if not result:
                flash(u'课程不存在', 'warning')
            else:
                delete_data_by_id('sno', 'cno', sno, form.title.data, "score")
                flash('退课成功', 'success')
                return redirect(url_for('student_course_delete', sno=sno, messages=messages, titles=titles,
                                        form=form))

    return render_template('student_course_delete.html', sno=sno, messages=messages, titles=titles, form=form)

# 学生成绩查询功能
@student_bp.route('/<int:sno>/score', methods=['GET', 'POST'])
def student_score(sno):
    result_score, _ = get_sql("select * from score where sno='%s'" % sno)

    messages = []
    for i in result_score:
        result_course, _ = get_sql("select * from course where cno='%s'" % i[1])
        result_teacher, _ = get_sql("select * from teacher where tno='%s'" % result_course[0][2])
        if not i[2]:
            message = {'cno': i[1], 'cname': result_course[0][1], 'tname': result_teacher[0][1], 'score': '无成绩'}
        else:
            message = {'cno': i[1], 'cname': result_course[0][1], 'tname': result_teacher[0][1], 'score': i[2]}
        messages.append(message)

    titles = [('cno', '已选课程号'), ('cname', '课程名'), ('tname', '任课教师'), ('score', '成绩')]

    return render_template('student_score.html', sno=sno, messages=messages, titles=titles)
