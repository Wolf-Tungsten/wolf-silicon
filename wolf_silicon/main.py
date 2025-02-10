from agent import WolfSiliconAgent
import argparse
import os
import datetime

def create_workspace(rootpath):
    # 在rootpath创建一个以日期时间编号的 wksp_YYYYMMDD_HHMMSS 文件夹
    workpath = os.path.join(rootpath, f"wksp_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
    workpath = os.path.abspath(workpath)
    os.makedirs(workpath)
    return workpath

if __name__ == "__main__":
    # 设置可选参数 --req 
    parser = argparse.ArgumentParser()
    parser.add_argument("--req", type=str, help="User requirements file path")
    args = parser.parse_args()
    # 在指定目录下创建工作目录
    workpath = create_workspace("./playground")
    # 创建 WolfSiliconAgent
    agent = WolfSiliconAgent(workspace_path=workpath, user_requirements_path=args.req)
    agent.run()