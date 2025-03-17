# views/teacher_views.py
from flask import Blueprint, render_template, flash, redirect, url_for
from forms import AccountForm, ScoreForm
from db_sqlite import get_sql, update_data

teacher_bp = Blueprint('teacher_bp', __name__)

@teacher_bp.route('/<int:tno>', methods=['GET'])
def profile(tno):
    return render_template('teacher.html', tno=tno)

#老师个人信息
@teacher_bp.route('/<int:tno>/account', methods=['GET', 'POST'])
def teacher_account(tno):
    form = AccountForm()

    # 查询教师个人信息
    result, _ = get_sql("select * from teacher where tno='%s'" % tno)
    if not result:
        flash(u'教师信息不存在', 'danger')
        return redirect(url_for('some_error_page'))  # 可修改为适当的页面

    teacher_info = {
        'tno': result[0][0],
        'name': result[0][1],
        'gender': result[0][3],
        'college': result[0][4]
    }

    if form.is_submitted():
        if form.secret.data == result[0][2]:  # 确保原密码正确
            data = dict(
                tno=tno,
                name=result[0][1],
                password=form.password.data
            )
            update_data(data, "teacher")
            flash(u'修改成功！', 'success')
        else:
            flash(u'原密码错误', 'warning')

    return render_template('teacher_account.html', **teacher_info, form=form)


#老师课程信息
@teacher_bp.route('/<int:tno>/course', methods=['GET'])
def teacher_course(tno):
    result_course, _ = get_sql("SELECT * FROM course WHERE tno='%s'" % tno)

    messages = []
    for course in result_course:
        message = []
        result_student_course, _ = get_sql("SELECT sno FROM student_course WHERE cno='%s'" % course[0])  # 课程号匹配学生

        if not result_student_course:
            continue  # 如果课程没人选，跳过
        else:
            for student in result_student_course:
                result_student, _ = get_sql("SELECT * FROM student WHERE sno='%s'" % student[0])
                row = {
                    'cno': course[0],          # 课程号
                    'cname': course[1],        # 课程名
                    'sno': result_student[0][0],  # 学号
                    'name': result_student[0][1], # 学生姓名
                    'gender': result_student[0][3],  # 性别（索引 3）
                    'college': result_student[0][4], # 学院（索引 4）
                    'major': result_student[0][5]   # 专业（索引 5）
                }
                message.append(row)
        messages.append(message)

    titles = [
        ('sno', '学员号'),
        ('name', '学员姓名'),
        ('gender', '性别'),
        ('college', '学院'),  
        ('major', '专业')
    ]

    return render_template('teacher_course.html', tno=tno, messages=messages, titles=titles)

#班级正确率查询
@teacher_bp.route('/<int:tno>/score', methods=['GET', 'POST'])
def teacher_score(tno):
    # 查询该教师所教授的课程
    result_course, _ = get_sql("SELECT * FROM course WHERE tno='%s'" % tno)

    messages = []
    
    for course in result_course:
        cno = course[0]  # 课程号
        cname = course[1]  # 课程名

        # 统计每个章节的答题正确率
        result_chapters, _ = get_sql(f"""
            SELECT q.qname, SUM(sa.correctcnt) AS total_correct, SUM(sa.allcnt) AS total_attempts
            FROM student_answer sa
            JOIN question q ON sa.qid = q.qid
            WHERE sa.cno = '{cno}'
            GROUP BY q.qname
        """)

        message = []
        for chapter in result_chapters:
            qname = chapter[0]  # 章节名
            total_correct = chapter[1] or 0
            total_attempts = chapter[2] or 1  # 避免除零错误
            accuracy = round((total_correct / total_attempts) * 100, 2)  # 计算正确率，保留两位小数

            row = {'cname': cname, 'cno': cno, 'qname': qname, 'accuracy': f"{accuracy}%"}
            message.append(row)

        messages.append(message)

    titles = [('qname', '章节名称'), ('accuracy', '正确率')]

    return render_template('teacher_score.html', tno=tno, messages=messages, titles=titles)