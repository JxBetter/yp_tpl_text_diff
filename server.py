from flask import Flask, request
from diff_tpl_text import run

app = Flask(__name__)


@app.route('/')
def index():
    wksid = request.args.get('wksid')
    subid = request.args.get('subid')
    msg_text = request.args.get('text')
    data = run(wksid, subid, msg_text)
    data[0] = '<div>匹配的最佳模版的id为: ' + data[0] + '</div>'
    data[1] = '<div>匹配的最佳模版的内容为: ' + data[1] + '</div>'
    data[2] = '<div>原始的输入文本内容为:' + data[2] + '</div>'
    content = """
                <div>绿色部分: 模版变量匹配正确<br>
                     红色部分: 模版内容匹配错误<br>
                     黄色部分: 模版内容应有的内容被删除，短信文本中找不到<br>
                     蓝色部分: 模版中不应出现的内容，短信文本中出现了<br><br><hr>
                </div>
              """
    content = content + '<br>'.join(data)
    return content


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9995)
