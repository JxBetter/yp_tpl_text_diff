import json
import difflib
import requests


def get_tpls_pages(wksid, subid):
    """

    :param wksid: wk session id
    :param subid: 子账号
    :return:
    """
    cookie = {
        '__wksid': wksid
    }
    data = {
        'pageNo': 1,
        'pageSize': 100,
        'subAccountId': subid
    }
    r = requests.post('https://www.yunpian.com/api/domestic/template/search',
                      cookies=cookie,
                      json=data)
    return json.loads(r.text)['data']['pagin']['pageCount']


def get_all_tpls(wksid, subid, pages):
    """
    获取子账号下所有模版
    :param wksid: wk session id
    :param subid: 子账号
    :param pages: 模版页数
    :return:
    """
    tpls = []
    for i in range(1, pages + 1):
        cookie = {
            '__wksid': wksid
        }
        data = {
            'pageNo': i,
            'pageSize': 100,
            'subAccountId': subid
        }
        r = requests.post('https://www.yunpian.com/api/domestic/template/search',
                          cookies=cookie,
                          json=data)
        tpl_list = json.loads(r.text)['data']['records']
        for tpl in tpl_list:
            if tpl['checkStatus'] == 0:
                tpls.append({
                    'tpl_id': tpl['id'],
                    'tpl_content': tpl['content']
                })
    return tpls


def match_best_tpl(tpls, text):
    """
    根据短信文本匹配最佳模版
    :param tpls: 所有的模版
    :param text: 短信文本
    :return:
    """
    best_ratio = 0
    best_tpl = ''
    best_tpl_id = ''
    for tpl in tpls:
        ratio = difflib.SequenceMatcher(None, tpl['tpl_content'], text).quick_ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_tpl = tpl['tpl_content']
            best_tpl_id = tpl['tpl_id']
    return best_tpl, best_tpl_id


def get_match_operations(wksid, subid, tpl, text):
    """
    获取匹配的操作内容
    :param wksid: wk session id
    :param subid: 子账号
    :param tpl: 匹配的最佳模版
    :param text: 短信文本
    :return:
    """
    cookie = {
        '__wksid': wksid
    }
    data = {
        'subAccountId': subid,
        'tplContent': tpl,
        'testContent': text
    }
    r = requests.post('https://www.yunpian.com/api/domestic/template/test', json=data, cookies=cookie)
    if json.loads(r.text)['code'] == -1:
        return -1, json.loads(json.loads(r.text)['data'])
    elif json.loads(r.text)['code'] == 0:
        return 0, json.loads(r.text)['msg']
    else:
        return json.loads(r.text)['code'], json.loads(r.text)['msg']


def show_diff(operations, tpl):
    """
    匹配差异，颜色标示出来
    :param operations: 操作列表
    :param tpl: 最佳模版
    :return:
    """
    check_tpl = tpl
    check_text = ''
    description = []

    html_check_tpl = '<div>比较差异后的模版为: {}</div>'.format(tpl)
    html_check_text = '比较差异后的文本为: '

    # 错误匹配为红色
    red = "\033[31m"
    html_red = '<span style=color:red>{}</span>'

    # 变量正确匹配为绿色
    green = "\033[32m"
    html_green = '<span style=color:green>{}</span>'

    # 内容被删除为黄色
    yellow = "\033[33m"
    html_yellow = '<span style=color:yellow>{}</span>'

    # 内容被增加为蓝色
    blue = "\033[35m"
    html_blue = '<span style=color:blue>{}</span>'

    tail = "\033[0m"

    op_size = len(operations)

    for index in range(op_size):
        if operations[index]['operation'] == 'EQUAL':
            check_text += operations[index]['text']
            html_check_text += operations[index]['text']
        elif operations[index]['operation'] == 'DELETE':
            if (index != op_size - 1) and (operations[index + 1]['operation'] == 'INSERT'):
                # 当前删除操作不是最后一个操作，并且下一个操作是插入操作，说明某个内容被替换了
                if operations[index]['text'].startswith('#') and operations[index]['text'].endswith('#'):
                    # 变量正确匹配,模版中的变量标绿
                    check_tpl = check_tpl.replace(operations[index]['text'],
                                                  (green + operations[index]['text'] + tail))
                    html_check_tpl = html_check_tpl.replace(operations[index]['text'],
                                                            html_green.format(operations[index]['text']))
                    description.append('模版中的变量"{}",正确匹配了"{}"'.format(operations[index]['text'],
                                                                     operations[index + 1]['text']))
                else:
                    # 模版中的某个内容被错误匹配,模版中的内容标红
                    check_tpl = check_tpl.replace(operations[index]['text'],
                                                  red + operations[index]['text'] + tail)
                    html_check_tpl = html_check_tpl.replace(operations[index]['text'],
                                                            html_red.format(operations[index]['text']))
                    description.append('模版中的"{}",错误匹配了"{}"'.format(operations[index]['text'],
                                                                   operations[index + 1]['text']))
            else:
                # 当前删除操作是最后一个，或者下一个操作不是删除操作，说明某个内容单纯被删除了
                check_tpl = check_tpl.replace(operations[index]['text'],
                                              yellow + operations[index]['text'] + tail)
                html_check_tpl = html_check_tpl.replace(operations[index]['text'],
                                                        html_yellow.format(operations[index]['text']))
                description.append('模版中的"{}"被删除了,在短信文本中找不到'.format(operations[index]['text']))
        elif operations[index]['operation'] == 'INSERT':
            if (index != 0) and (operations[index - 1]['operation'] == 'DELETE'):
                # 当前插入操作不是第一个操作，并且前一个操作是删除操作，说明内容被替换了
                if operations[index - 1]['text'].startswith('#') and operations[index - 1]['text'].endswith('#'):
                    # 变量被正确替换，替换的内容标绿
                    t = (green + operations[index]['text'] + tail)
                    check_text += t
                    html_check_text += html_green.format(operations[index]['text'])
                else:
                    t = (red + operations[index]['text'] + tail)
                    check_text += t
                    html_check_text += html_red.format(operations[index]['text'])
            else:
                # 当前增加操作是第一个，或者上一个操作不是删除操作，说明某个内容被直接增加了
                t = (blue + operations[index]['text'] + tail)
                check_text += t
                html_check_text += html_blue.format(operations[index]['text'])
                description.append('短信文本与模版相比多了"{}"内容'.format(operations[index]['text']))
    html_check_text = '<div>' + html_check_text + '</div>'
    html_description = '<div>' + '比较差异的描述内容为: ' + ';'.join(description) + '</div>'
    return check_tpl, check_text, ';'.join(description), html_check_tpl, html_check_text, html_description


def run(wksid, subid, msg_text):
    """
    终端打印，返回html渲染文本
    :param wksid:
    :param subid:
    :param msg_text:
    :return:
    """
    # 1.获取子账号下的模版页数，用来获取所有的模版
    page_num = get_tpls_pages(wksid, subid)

    # 2.获取子账号下的所有模版
    all_tpls_list = get_all_tpls(wksid, subid, page_num)

    # 3.根据短信文本，匹配最相似的模版
    best_tpl, best_tpl_id = match_best_tpl(all_tpls_list, msg_text)

    # 4.获取最匹配的模版和短信内容之间的转换操作
    f, data = get_match_operations(wksid, subid, best_tpl, msg_text)

    if f == -1:
        operations_list = data
        # 5.根据转换操作输出模版和短信内容之间的差异
        output_tpl, output_text, output_des, output_html_tpl, output_html_text, output_html_des = show_diff(
            operations_list, best_tpl)
        print('匹配的最佳模版的id为: {}'.format(best_tpl_id))

        print('匹配的最佳模版为: {}'.format(best_tpl))

        print('输入的短信文本为: {}'.format(msg_text))

        print('比较差异后的模版为: {}'.format(output_tpl))

        print('比较差异后的文本为: {}'.format(output_text))

        print('比较差异的描述内容为: {}'.format(output_des))

        return [best_tpl_id, best_tpl, msg_text, output_html_tpl, output_html_text, output_html_des]
    elif f == 0:
        print('短信文本和模版匹配正确，没有错误')
        return ['', '', '', '<div>比较差异后的模版为: </div>', '<div>比较差异后的文本为: </div>', '<div>比较差异的描述内容为: 短信文本和模版匹配正确，没有错误</div>']
    else:
        print(data)
        return ['', '', '', '<div>比较差异后的模版为: </div>', '<div>比较差异后的文本为: </div>', '<div>比较差异的描述内容为: {}</div>'.format(data)]


if __name__ == '__main__':
    wksid = 'n-095A46EF54044376A44A654661C22BDD'
    subid = '890000000020585122'
    msg_text = '【顾金鑫测试】尊敬的用户，您的帐号于20190202成功充值33元，如有疑问请联系客'
    run(wksid, subid, msg_text)
