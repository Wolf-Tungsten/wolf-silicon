import datetime
import subprocess
import threading
import queue

class WolfSiliconEnv(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(WolfSiliconEnv, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        self._team_log = []

    def set_workpath(self, workpath):
        self._workpath = workpath
    
    def get_workpath(self):
        return self._workpath

    def update_log(self, role, message):
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._team_log.append(f"{role}@{time}: {message}")
    
    def read_log(self):
        # 截取最后10条日志，拼接成字符串返回
        return "\n".join(self._team_log[-10:])
    
    def common_write_file(self, filename, content, overwrite=True):
        # 打开 {self._workpath}/{filename}，默认覆盖写入 content
        # 如果 overwrite 为 False，追加写入 content
        with open(f"{self._workpath}/{filename}", "w" if overwrite else "a") as f:
            f.write(content)
    
    def common_read_file(self, filename):
        # 判断 {self._workpath}/{filename} 是否存在，不存在返回 None
        try:
            with open(f"{self._workpath}/{filename}", "r") as f:
                return f.read()
        except FileNotFoundError:
            return "File not found."
    
    def execute_command(command, timeout_sec):
        def target(q):
            # 创建子进程
            proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
            try:
                # 捕获输出和错误
                stdout, stderr = proc.communicate()
                # 将结果和进程对象放入.queue
                q.put((stdout, stderr, proc))
            except Exception as e:
                q.put((None, str(e), proc))

        q = queue.Queue()
        thread = threading.Thread(target=target, args=(q,))
        thread.start()
        thread.join(timeout_sec)

        if thread.is_alive():
            # 如果线程还活着，则说明超时了
            try:
                stdout, stderr, proc = q.get_nowait()
            except queue.Empty:
                return "*****Process timed out without output*****"
            # 终止进程
            proc.terminate()
            thread.join()
            return f"""=====stdout======
            {stdout}
            =====stderr======
            {stderr}
            *****Process timed out****"""

        try:
            # 获取结果
            stdout, stderr, _ = q.get_nowait()
        except queue.Empty:
            return "*****Process failed without output*****"

        if stderr:
            return f"""=====stdout======
            {stdout}
            =====stderr======
            {stderr}
            ================="""
        else:
            return f"""=====stdout======
            {stdout}
            ================="""