安装python3-venv:
python3 apt-get install python3-venv

创建虚拟环境：
python3 -m venv venv

启动虚拟环境命令：

windows命令:
venv\Scripts\activate

mac命令:
source venv/bin/activate

若已激活了虚拟环境，命令行会显示为：
(venv) $

安装依赖：
pip install -r requirements.txt

网页：
FR4/FR5/FR7：汇总关键指标（出勤、压力、按时提交）和近期调查。
FR7/FR8：最近的福祉调查记录（stress/睡眠等近期 check-in）。
FR1/FR10：高风险学生列表（早期预警/连续高压力或低出勤的学生）。