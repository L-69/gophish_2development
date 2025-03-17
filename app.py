# app.py
import subprocess,os,re
from collections import defaultdict
from flask import Flask, render_template, request, g, send_file,jsonify
from datetime import datetime
import io,requests,json

app = Flask(__name__)

# 配置 API 相关信息
API_KEY = "bd870f3e5dd55d951807e2e3d6d5644e4d0db554498815a62b0da09957d017"  # 你的 Gophish API 密钥
GOPHISH_URL = "https://14.22.15.2:8891/api/campaigns/"
# 关闭 SSL 证书验证（如果你的 Gophish 运行在自签名证书下）
VERIFY_SSL = False  

# 请求头，包含 API 认证信息
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

@app.before_request
def get_campaigns():
    try:
        response = requests.get(GOPHISH_URL, headers=headers, verify=VERIFY_SSL)
        if response.status_code == 200:
            g.campaigns = response.json()
        else:
            g.campaigns = []
            print(f"❌ 获取 campaigns 失败，状态码: {response.status_code}")
            print(response.text)
    except requests.RequestException as e:
        g.campaigns = []
        print(f"请求失败: {e}")

@app.route('/')
def index():
    campaigns_num = len(g.campaigns)
    return render_template('index.html', campaigns=g.campaigns, campaigns_num=campaigns_num)

@app.route('/create_campaign', methods=['POST'])
def create_campaign():
    # 从表单获取数据
    campaign_name = request.form.get('campaign_name')
    campaign_template_name = request.form.get('campaign_template_name')
    campaign_url = request.form.get('campaign_url')
    campaign_landing_page = request.form.get('campaign_landing_page')
    campaign_smtp = request.form.get('campaign_smtp')
    campaign_groups = request.form.get('campaign_groups')
    execution_time = request.form.get('execution_time')
    # 如果没有选择时间，设置为当前时间
    if execution_time is None or execution_time == '':
        launch_by_date = None
    else:
        launch_by_date = execution_time  # 这里可以转换为 ISO 8601 格式的时间
    # 创建请求数据
    campaign_data = {
        "name": f"Campaign {campaign_name}",
        "template": {"name": f"{campaign_template_name}"},
        "url": f"{campaign_url}",
        "page": {"name": f"{campaign_landing_page}"},
        "smtp": {"name": f"{campaign_smtp}"},
        "launch_by_date":launch_by_date,
        "groups": [{"name": f"{campaign_groups}"}],
    }

    try:
        # 向目标服务器发送创建 campaign 的请求
        response = requests.post(GOPHISH_URL, headers=headers, data=json.dumps(campaign_data), verify=VERIFY_SSL)

        # 解析响应
        if response.status_code == 201:
            status_message = "Campaign created successfully!"
        else:
            status_message = f"Failed to create campaign. Status Code: {response.status_code}"
    except requests.RequestException as e:
        status_message = f"Request failed: {e}"

    # 返回 HTML 页面并带上状态信息
    return render_template('index.html', status_message=status_message, campaigns=g.campaigns, campaigns_num=len(g.campaigns))

def extract_browser_info(details_string):
    # 尝试提取浏览器信息
    if not details_string:
        return "Unknown"
    
    # 常见浏览器的正则表达式匹配模式
    browser_patterns = {
        'Chrome': r'Chrome\/[\d\.]+',
        'Firefox': r'Firefox\/[\d\.]+',
        'Safari': r'Safari\/[\d\.]+',
        'Edge': r'Edge\/[\d\.]+',
        'IE': r'MSIE|Trident',
        'Opera': r'Opera\/[\d\.]+|OPR\/[\d\.]+',
    }
    
    for browser, pattern in browser_patterns.items():
        if re.search(pattern, details_string):
            return browser
    
    # 如果没有找到匹配的浏览器，检查是否包含移动设备信息
    if re.search(r'Mobile|Android|iPhone|iPad', details_string):
        return "Mobile"
    
    return "Other"

@app.route('/chart')
def get_chart():
    task_times = []  # 存储每个时间点的所有事件
    status_count_by_time = {}  # 存储每个时间点各个事件的数量
    valid_statuses = [
        'Email Sent', 'Email Opened', 'Clicked Link', 
        'Submitted Data', 'Email Reported', 'Campaign Created'
    ]
    
    # 汇总每个状态的总数
    total_status_count = {
        'Campaign Created': 0,
        'Email Sent': 0,
        'Email Opened': 0,
        'Clicked Link': 0,
        'Submitted Data': 0,
        'Email Reported': 0
    }
    
    # 添加浏览器统计信息
    browser_stats = {}
    
    for campaign in g.campaigns:
        for event in campaign['timeline']:
            event_time = event['time'][:19]  # 只取到秒级别
            event_message = event['message']
            
            # 如果事件状态不在预定义的有效状态中，跳过此事件
            if event_message not in valid_statuses:
                continue

            # 如果时间点尚未添加到字典中，先初始化它
            if event_time not in status_count_by_time:
                status_count_by_time[event_time] = {
                    'Campaign Created': 0,
                    'Email Sent': 0,
                    'Email Opened': 0,
                    'Clicked Link': 0,
                    'Submitted Data': 0,
                    'Email Reported': 0
                }
            
            # 更新该时间点的状态计数
            status_count_by_time[event_time][event_message] += 1
            total_status_count[event_message] += 1
            
            # 提取浏览器信息并更新浏览器统计（主要从Clicked Link和Submitted Data事件中提取）
            if event_message in ['Clicked Link', 'Submitted Data', 'Email Opened'] and 'details' in event:
                browser = extract_browser_info(event['details'])
                if browser in browser_stats:
                    browser_stats[browser] += 1
                else:
                    browser_stats[browser] = 1
    
    # 如果没有浏览器数据，添加一些默认值以避免图表出错
    if not browser_stats:
        browser_stats = {
            "Unknown": 1
        }

    return render_template('chart.html', 
                           status_count_by_time=status_count_by_time, 
                           total_status_count=total_status_count,
                           browser_stats=browser_stats)

@app.route('/generate-report', methods=['POST'])
def generate_report():
    campaign_name = request.form.get('campaign_name')
    campaign_id = request.form.get('campaign_id')
    report_format = request.form.get('report_format')
    print(campaign_id,campaign_name,report_format)

    if not campaign_name or not campaign_id or not report_format:
        return jsonify({"error": "缺少必要参数"}), 400
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    goreport_path = os.path.join(current_dir, "GoReport.py")
    print(goreport_path)
    command = f"python3 {goreport_path} --id {campaign_id} --format {report_format}"

    result = subprocess.run(command, shell=True)
    if report_format == "word":
        report_format = "docx"  # 修正文件扩展名
    elif report_format == "pdf":
        report_format = "pdf"  # 修正文件扩展名
    else:
        report_format = "excel"  # 修正文件扩展名
    report_file_name = f"Gophish Results for {campaign_name}.{report_format}"

    return send_file(report_file_name, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)