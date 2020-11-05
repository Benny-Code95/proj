from flask import Flask, render_template, request

# first program


app = Flask(__name__)


# # 装饰器实现路由
# @app.route('/')  # website 127.0.0.1/5000
# def index():
#     return 'This is the index!'  # response
#
#
# # 具体路径
# @app.route('/page')  # website 127.0.0.1/5000/page
# def page():
#     return 'This is the page!'


# # 返回html文件
# @app.route('/')  # website 127.0.0.1/5000
# def index():
#     # 在templates文件下下查找first.html文件并返回
#     return render_template('first.html')

# 将变量交给html文件
@app.route('/')  # website 127.0.0.1/5000
def index():
    var_non_iter = 'hello test'
    var_iter = ['1', '2', '3']
    # 在html中用{{non_it}}和{{it}}接收该变量
    return render_template('first.html', non_it=var_non_iter, it=var_iter)


# 页面传递参数给flask
# 显示登录界面
@app.route('/login')  # website 127.0.0.1/5000/login
def login():
    return render_template('login.html')


# 接收传递数据
@app.route('/response', methods=['post']) # website 127.0.0.1/5000/response
def resp():
    usn = request.form.get('username')
    pwd = request.form.get('password')
    show_new = request.form.get('show_new')
    if usn == 'benny' and pwd == 'chan':
        return 'success'
    elif show_new is '':
        # 返回原登录界面
        return render_template('login.html', message='failed, input again')
    else:
        return 'failed'


if __name__ == '__main__':
    app.run()  # 启动应用程序
