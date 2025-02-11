import datetime
import subprocess
import threading
import queue
import os

class WolfSiliconEnv(object):
    
    def __init__(self, doc_path:str, cmodel_path:str, design_path:str, verification_path:str):
        self._doc_path = doc_path
        self._cmodel_path = cmodel_path
        self._design_path = design_path
        self._verification_path = verification_path

        self._user_requirements_path = os.path.join(self._doc_path, "user_requirements.md")
        self._spec_path = os.path.join(self._doc_path, "spec.md")
        self._cmodel_code_path = os.path.join(self._cmodel_path, "cmodel.cpp")
        self._cmodel_binary_path = os.path.join(self._cmodel_path, "cmodel")
        self._design_code_path = os.path.join(self._design_path, "dut.v")
        self._verification_code_path = os.path.join(self._verification_path, "tb.sv")
        self._verification_binary_path = os.path.join(self._verification_path, "obj_dir","Vtb")
        self._verification_report_path = os.path.join(self._doc_path, "verification_report.md")

    def write_user_requirements(self, requirements:str):
        # 将 requirements 写入 {self._doc_path}/user_requirements.md，固定为 overwrite
        with open(self._user_requirements_path, "w") as f:
            f.write(requirements+"\n")
    
    def get_user_requirements(self) -> tuple[bool, float, str]:
        # 返回 user requirements 的内容和修改时间
        if os.path.exists(self._user_requirements_path):
            mtime = os.path.getmtime(self._user_requirements_path)
            with open(self._user_requirements_path, "r") as f:
                return True, mtime, f.read()
        else:
            return False, 0, "No user requirements found."
        
    def write_spec(self, spec:str, overwrite:bool=False):
        # 将 spec 写入 {self._doc_path}/spec.md，如果 overwrite 为 False，追加写入
        with open(self._spec_path, "w" if overwrite else "a") as f:
            f.write(spec+"\n")
    
    def get_spec(self) -> tuple[bool, float, str]:
        if os.path.exists(self._spec_path):
            mtime = os.path.getmtime(self._spec_path)
            with open(self._spec_path, "r") as f:
                return True, mtime, f.read()
        else:
            return False, 0, "No spec found."
    
    def write_cmodel_code(self, code:str):
        # 将 cmodel code 写入 {self._cmodel_path}/cmodel.cpp, 固定为 overwrite
        with open(self._cmodel_code_path, "w") as f:
            f.write(code+"\n")
    
    def get_cmodel_code(self) -> tuple[bool, float, str]:
        # 返回 cmodel code 的内容和修改时间
        if os.path.exists(self._cmodel_code_path):
            mtime = os.path.getmtime(self._cmodel_code_path)
            with open(self._cmodel_code_path, "r") as f:
                return True, mtime, f.read()
        else:
            return False, 0, "No cmodel code found."
    
    def delete_cmodel_binary(self):
        # 删除 {self._cmodel_path}/cmodel
        if os.path.exists(self._cmodel_binary_path):
            os.remove(self._cmodel_binary_path)
    
    def is_cmodel_binary_exist(self) -> bool:
        # 判断 {self._cmodel_path}/cmodel 是否存在
        return os.path.exists(self._cmodel_binary_path)
    
    def compile_cmodel(self) -> str:
        # 获取 codebase 中所有 .cpp 文件
        cpp_files = []
        for filename in os.listdir(self._cmodel_path):
            if filename.endswith('.cpp'):
                cpp_files.append(os.path.join(self._cmodel_path,filename))
        result = WolfSiliconEnv.execute_command(f"g++  {' '.join(cpp_files)} -I{self._cmodel_path} -o {self._cmodel_path}/cmodel", 300)
        return result[-4*1024:]
    
    def run_cmodel(self, timeout_sec:int=180) -> str:
        # 运行 cmodel binary
        result = WolfSiliconEnv.execute_command(self._cmodel_binary_path, timeout_sec)
        return result[-4*1024:]
    
    def compile_and_run_cmodel(self):
        self.delete_cmodel_binary()
        compiler_output = self.compile_cmodel()
        if not self.is_cmodel_binary_exist():
            return f"# No cmodel binary found. Compile failed.\n Here is the compiler output \n{compiler_output}"
        else:
            cmodel_output = self.run_cmodel()
            return f"# CModel compiled successfully. Please review the output from the run. \n{cmodel_output}"
    
    def write_design_code(self, code:str):
        # 将 design code 写入 {self._design_path}/dut.v, 固定为 overwrite
        with open(self._design_code_path, "w") as f:
            f.write(code+"\n")
    
    def get_design_code(self) -> tuple[bool, float, str]:
        # 返回 design code 的内容和修改时间
        if os.path.exists(self._design_code_path):
            mtime = os.path.getmtime(self._design_code_path)
            with open(self._design_code_path, "r") as f:
                return True, mtime, f.read()
        else:
            return False, 0, "No design code found."
    
    def lint_design(self) -> str:
        # 获取 codebase 中所有 .v 文件
        v_files = []
        for filename in os.listdir(self._design_path):
            if filename.endswith('.v'):
                v_files.append(os.path.join(self._design_path,filename))
        return WolfSiliconEnv.execute_command(f"verilator -Wno-TIMESCALEMOD -Wno-DECLFILENAME --lint-only {' '.join(v_files)} -I{self._design_path}", 60)
    
    def write_verification_code(self, code:str):
        # 将 verification code 写入 {self._verification_path}/tb.sv, 固定为 overwrite
        with open(self._verification_code_path, "w") as f:
            f.write(code+"\n")
        
    def get_verification_code(self) -> tuple[bool, float, str]:
        # 返回 verification code 的内容和修改时间
        if os.path.exists(self._verification_code_path):
            mtime = os.path.getmtime(self._verification_code_path)
            with open(self._verification_code_path, "r") as f:
                return True, mtime, f.read()
        else:
            return False, 0, "No verification code found."
    
    def compile_verification(self) -> str:
        code_file = []
        for filename in os.listdir(self._verification_path):
            if filename.endswith('.v') or filename.endswith('.sv'):
                code_file.append(os.path.join(self._verification_path, filename))
        for filename in os.listdir(self._design_path):
            if filename.endswith('.v'):
                code_file.append(os.path.join(self._design_path, filename))
        result = WolfSiliconEnv.execute_command(f"verilator -Wno-TIMESCALEMOD -Wno-DECLFILENAME --binary --build --timing {' '.join(code_file)} --top-module tb -I{self._verification_path} -I{self._design_code_path}  --sv -CFLAGS \"-fcoroutines\" --Mdir {self._verification_path}/obj_dir", 300)
        return result[-4*1024:]

    def run_verification(self, timeout_sec:int=10) -> str:
        if not os.path.exists(self._verification_binary_path):
            return "There is no Vtb executable. Please check if compile successfully."
        result = WolfSiliconEnv.execute_command(self._verification_binary_path, timeout_sec)
        return result[-4*1024:]
    
    def write_verification_report(self, report:str):
        # 将 verification report 写入 {self._doc_path}/verification_report.md，固定为 overwrite
        with open(self._verification_report_path, "w") as f:
            f.write(report+"\n")
    
    def get_verification_report(self) -> tuple[bool, float, str]:
        # 返回 verification report 的内容和修改时间
        if os.path.exists(self._verification_report_path):
            mtime = os.path.getmtime(self._verification_report_path)
            with open(self._verification_report_path, "r") as f:
                return True, mtime, f.read()
        else:
            return False, 0, "No verification report found."
    
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
                proc.terminate()
                thread.join()
                return "**Process timed out without output**"
            # 终止进程
            proc.terminate()
            thread.join()
            return f""" 
            # stdout
            ```
            {stdout}
            ```
            # stderr
            ```
            {stderr}
            ```
            **Process timed out**
            """

        try:
            # 获取结果
            stdout, stderr, _ = q.get_nowait()
        except queue.Empty:
            return "**Process failed without output**"

        if stderr:
            return f"""# stdout\n```\n{stdout}\n```\n# stderr\n```\n{stderr}\n```"""
        else:
            return f"# stdout\n```\n{stdout}\n```"