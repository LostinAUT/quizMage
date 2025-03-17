# views/student_views.py
from flask import Blueprint, render_template, flash, redirect, url_for
from forms import AccountForm, SelectForm, DeleteForm, ScoreForm
from db_sqlite import get_sql, update_data, insert_data, delete_data_by_id
from datetime import datetime

student_bp = Blueprint('student_bp', __name__)

@student_bp.route('/<int:sno>', methods=['GET'])
def profile(sno):
    return render_template('student.html', sno=sno)


#查询个人信息，修改密码
@student_bp.route('/<int:sno>/account', methods=['GET', 'POST'])
def student_account(sno):
    form = AccountForm()


    result, _ = get_sql("SELECT sno, name, password, gender, college, major FROM student WHERE sno='%s'" % sno)
    
    if not result:
        flash("学生信息不存在", "danger")
        return redirect(url_for("student_bp.profile", sno=sno))

    sno, name, password, gender, college, major = result[0]  # 按照顺序解析数据

    if form.validate_on_submit():
        # 检查原密码是否正确
        if form.secret.data == password:
            data = dict(
                sno=sno,
                name=name,
                gender=gender,
                college=college,
                major=major,
                password=form.password.data  # 更新新密码
            )
            update_data(data, "student")
            flash("修改成功！", "success")
        else:
            flash("原密码错误", "warning")

    return render_template('student_account.html', sno=sno, name=name, gender=gender, college=college, major=major, form=form)


#选课
@student_bp.route('/<int:sno>/course_select', methods=['GET', 'POST'])
def student_course_select(sno):
    form = SelectForm()

    # 查询所有课程信息（course表）
    result_course, _ = get_sql("SELECT * FROM course")

    messages = []
    for i in result_course:
        # 查询任课教师姓名（teacher表）
        result_teacher, _ = get_sql("SELECT name FROM teacher WHERE tno='%s'" % i[2])
        tname = result_teacher[0][0] if result_teacher else "未知"

        # 查询该课程已选人数（student_course表）
        result_count, _ = get_sql("SELECT COUNT(*) FROM student_course WHERE cno='%s'" % i[0])
        count = result_count[0][0] if result_count else 0

        message = {'cno': i[0], 'name': i[1], 'tname': tname, 'count': count}
        messages.append(message)

    titles = [('cno', '课程号'), ('name', '课程名'), ('tname', '任课教师'), ('count', '已选课人数')]

    if form.validate_on_submit():
        if not form.title.data:
            flash(u'请填写课程号', 'warning')
        else:
            result, _ = get_sql("SELECT * FROM course WHERE cno='%s'" % form.title.data)
            if not result:
                flash(u'课程不存在', 'warning')
            else:
                result, _ = get_sql("SELECT * FROM student_course WHERE sno='%s' AND cno='%s'" % (sno, form.title.data))
                if result:
                    flash(u'课程选过了', 'warning')
                else:
                    data = dict(
                        sno=sno,
                        cno=form.title.data
                    )
                    insert_data(data, "student_course")
                    flash('选课成功', 'success')

    return render_template('student_course_select.html', sno=sno, messages=messages, titles=titles, form=form)

#退课
@student_bp.route('/<int:sno>/course_delete', methods=['GET', 'POST'])
@student_bp.route('/<int:sno>/course_delete', methods=['GET', 'POST'])
def student_course_delete(sno):
    form = DeleteForm()

    # 查询该学生已选课程信息
    result_student_courses, _ = get_sql("SELECT * FROM student_course WHERE sno='%s'" % sno)

    messages = []
    for i in result_student_courses:
        result_course, _ = get_sql("SELECT * FROM course WHERE cno='%s'" % i[1])
        if not result_course:
            continue  # 避免因数据库数据不一致导致的错误

        result_teacher, _ = get_sql("SELECT name FROM teacher WHERE tno='%s'" % result_course[0][2])
        tname = result_teacher[0][0] if result_teacher else "未知"

        message = {'cno': i[1], 'cname': result_course[0][1], 'tname': tname}
        messages.append(message)

    titles = [('cno', '已选课程号'), ('cname', '课程名'), ('tname', '任课教师')]

    if form.validate_on_submit():
        if not form.title.data:
            flash(u'请填写课程号', 'warning')
        else:
            result, _ = get_sql("SELECT * FROM student_course WHERE cno='%s' AND sno='%s'" % (form.title.data, sno))
            if not result:
                flash(u'你未选该课程', 'warning')
            else:
                delete_data_by_id('sno', 'cno', sno, form.title.data, "student_course")
                flash('退课成功', 'success')
                return redirect(url_for('student_course_delete', sno=sno))  # 重新加载页面，刷新数据

    return render_template('student_course_delete.html', sno=sno, messages=messages, titles=titles, form=form)

# 学生答题正确率查询功能
@student_bp.route('/<int:sno>/accuracy', methods=['GET'])
def student_accuracy(sno):
    # 获取学生选课记录
    result_score, _ = get_sql("select * from student_course where sno='%s'" % sno)

    messages = {}
    for i in result_score:
        # 获取课程信息
        result_course, _ = get_sql("select * from course where cno='%s'" % i[1])
        result_teacher, _ = get_sql("select * from teacher where tno='%s'" % result_course[0][2])

        # 获取学生答题记录
        result_answers, _ = get_sql("select qid, allcnt, correctcnt from student_answer where sno='%s' and cno='%s'" % (sno, i[1]))

        for answer in result_answers:
            # 获取章节名
            result_question, _ = get_sql("select qname from question where qid='%s'" % answer[0])

            # 将章节名作为key
            key = (i[1], result_question[0][0])  # 课程号和章节名为唯一键

            if key not in messages:
                messages[key] = {
                    'cno': i[1],  # 课程号
                    'cname': result_course[0][1],  # 课程名
                    'tname': result_teacher[0][1],  # 任课教师
                    'qname': result_question[0][0],  # 章节名
                    'allcnt': answer[1],  # 总答题次数
                    'correctcnt': answer[2],  # 正确答题次数
                }
            else:
                # 合并答题数据
                messages[key]['allcnt'] += answer[1]
                messages[key]['correctcnt'] += answer[2]

    # 计算每个章节的正确率
    for key, message in messages.items():
        if message['allcnt'] > 0:
            message['accuracy'] = f"{(message['correctcnt'] / message['allcnt']) * 100:.2f}%"
        else:
            message['accuracy'] = "0.00%"

    # 转换字典为列表
    final_messages = list(messages.values())

    titles = [('cno', '课程号'), ('cname', '课程名'), ('tname', '任课教师'), ('qname', '章节名'), 
              ('allcnt', '总答题数'), ('correctcnt', '正确答题数'), ('accuracy', '正确率')]

    return render_template('student_accuracy.html', sno=sno, messages=final_messages, titles=titles)