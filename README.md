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

