# views/teacher_views.py
from flask import Blueprint, render_template, flash, redirect, url_for ,request
from forms import AccountForm, ScoreForm, ChangeInfoForm,ChangePasswordForm
from db_sqlite import get_sql, update_data

teacher_bp = Blueprint('teacher_bp', __name__)

@teacher_bp.route('/<int:tno>', methods=['GET'])
def profile(tno):
    # 查询教师个人信息
    result, _ = get_sql("SELECT * FROM teacher WHERE tno='%s'" % tno)
    if not result:
        flash(u'教师信息不存在', 'danger')
        return redirect(url_for('some_error_page'))

    teacher_info = {
        'tno': result[0][0],
        'name': result[0][1],
        'password': result[0][2],
        'gender': result[0][3],
        'college': result[0][4]
    }

    # 查询教师所教授的课程
    result_course, _ = get_sql("SELECT * FROM course WHERE tno='%s'" % tno)
    courses = []
    for course in result_course:
        courses.append({
            'cno': course[0],
            'cname': course[1],
        })

    # 查询班级正确率数据
    scores = []
    for course in result_course:
        cno = course[0]
        result_chapters, _ = get_sql(f"""
            SELECT q.qname, 
                   SUM(sa.correctcnt) AS total_correct, 
                   SUM(sa.allcnt) AS total_attempts
            FROM student_answer sa
            JOIN question q ON sa.qid = q.qid
            WHERE sa.cno = '{cno}'
            GROUP BY q.qname
        """)

        for chapter in result_chapters:
            qname = chapter[0]
            total_correct = chapter[1] or 0
            total_attempts = chapter[2] or 1
            accuracy = round((total_correct / total_attempts) * 100, 2)
            scores.append({
                'cno': cno,
                'qname': qname,
                'accuracy': f"{accuracy}%",
            })

    return render_template('teacher.html', 
                           name=teacher_info['name'], 
                           tno=teacher_info['tno'], 
                           gender=teacher_info['gender'], 
                           college=teacher_info['college'],
                           courses=courses,
                           scores=scores)
#老师个人信息
@teacher_bp.route('/<int:tno>/account', methods=['GET', 'POST'])
def teacher_account(tno):
    # 查询教师个人信息
    result, _ = get_sql("SELECT * FROM teacher WHERE tno='%s'" % tno)
    if not result:
        flash(u'教师信息不存在', 'danger')
        return redirect(url_for('some_error_page'))  # 可修改为适当的页面

    teacher_info = {
        'tno': result[0][0],
        'name': result[0][1],
        'password': result[0][2],  # 需要用于密码验证
        'gender': result[0][3],
        'college': result[0][4]
    }

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_info':
            # 获取用户提交的新信息
            new_name = request.form.get('name')
            new_gender = request.form.get('gender')
            new_college = request.form.get('college')

            if new_name and new_gender and new_college:  # 确保数据有效
                data = {
                    'tno': tno,
                    'name': new_name,
                    'gender': new_gender,
                    'college': new_college,
                    'password': teacher_info['password']  # 保持原密码不变
                }
                update_data(data, "teacher")  # 更新数据库
                flash(u'个人信息修改成功！', 'success')

            else:
                flash(u'请填写完整信息', 'warning')

        elif action == 'update_password':
            # 获取用户输入的密码
            secret = request.form.get('secret')  # 原密码
            new_password = request.form.get('password')  # 新密码

            if secret == teacher_info['password']:  # 验证原密码
                data = {
                    'tno': tno,
                    'name': teacher_info['name'],  # 保持原姓名
                    'gender': teacher_info['gender'],  # 保持原性别
                    'college': teacher_info['college'],  # 保持原学院
                    'password': new_password  # 更新密码
                }
                update_data(data, "teacher")  # 更新数据库
                flash(u'密码修改成功！', 'success')
            else:
                flash(u'原密码错误', 'warning')

        # **更新数据库后，重新查询最新的教师信息**
        result, _ = get_sql("SELECT * FROM teacher WHERE tno='%s'" % tno)
        teacher_info.update({
            'name': result[0][1],
            'password': result[0][2],
            'gender': result[0][3],
            'college': result[0][4]
        })

    return render_template('teacher_account.html', **teacher_info)


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

        # 统计每个章节的答题正确率，总答题数和正确答题数
        result_chapters, _ = get_sql(f"""
            SELECT q.qname, 
                   SUM(sa.correctcnt) AS total_correct, 
                   SUM(sa.allcnt) AS total_attempts
            FROM student_answer sa
            JOIN question q ON sa.qid = q.qid
            WHERE sa.cno = '{cno}'
            GROUP BY q.qname
        """)

        message = []
        for chapter in result_chapters:
            qname = chapter[0]  # 章节名
            total_correct = chapter[1] or 0  # 如果为None，则赋值为0
            total_attempts = chapter[2] or 1  # 避免除零错误

            # 计算正确率
            accuracy = round((total_correct / total_attempts) * 100, 2)

            # 将结果存入行中
            row = {
                'cname': cname, 
                'cno': cno, 
                'qname': qname, 
                'total_correct': total_correct,  # 正确答题数
                'total_attempts': total_attempts,  # 总答题数
                'accuracy': f"{accuracy}%"  # 正确率
            }
            message.append(row)

        messages.append(message)

    titles = [('qname', '章节名称'), 
              ('total_attempts', '总答题数'),
              ('total_correct', '正确答题数'),
              ('accuracy', '正确率')]

    return render_template('teacher_score.html', tno=tno, messages=messages, titles=titles)