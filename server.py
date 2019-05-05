from flask import Flask, request, render_template
from diff_tpl_text import run

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        wksid = request.form.get('wksid')
        subid = request.form.get('subid')
        msg_text = request.form.get('text')
        data, tpl_type = run(wksid, subid, msg_text)
        data[0] = '<div>匹配的最佳模版的id为:' + data[0] + '({})</div>'.format(tpl_type)
        data[1] = '<div>匹配的最佳模版内容为:' + data[1] + '</div>'
        data[2] = '<div>原始的输入文本内容为:' + data[2] + '</div>'
        content = """
                    <div>绿色部分: 模版变量匹配正确<br>
                         红色部分: 模版内容匹配错误<br>
                         黄色部分: 模版内容应有的内容被删除，短信文本中找不到<br>
                         蓝色部分: 模版中不应出现的内容，短信文本中出现了<br><br><hr>
                    </div>
                  """
        content = content + '<br>'.join(
            data) + '<br><form action="/" method="get"><button type="submit" style="font-size: 16px">返回</button></form>'
        return content
    return render_template('index.html')


@app.errorhandler(500)
def server_handler(e):
    return render_template('500err.html'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9995)
