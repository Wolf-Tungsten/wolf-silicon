import subprocess

command = "verilator -Wno-TIMESCALEMOD -Wno-DECLFILENAME --lint-only /mount/hdd0/gaoruihao/project/wolf-silicon/playground/wksp_20250211_185838/design/dut.v -I/mount/hdd0/gaoruihao/project/wolf-silicon/playground/wksp_20250211_185838/design"
with subprocess.Popen(command.split(' '), 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE,
                      text=True) as process:
    stdout, stderr = process.communicate()
    print((stdout + stderr).rstrip())