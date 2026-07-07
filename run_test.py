import subprocess
import time
import sys

p = subprocess.Popen(
    ["npx", "next", "start", "-p", "3001"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd="/root/openmeet/apps/web"
)

# wait 5s
time.sleep(5)

# read output
stdout, stderr = "", ""
while True:
    line = p.stdout.readline()
    if not line: break
    stdout += line
    if "Ready" in line or "start" in line:
        break

# check if dead
ret = p.poll()
if ret is not None:
    print(f"PROCESS EXITED WITH {ret}")
    print("STDOUT:")
    print(stdout)
    print("STDERR:")
    print(p.stderr.read())
else:
    print("PROCESS RUNNING")
    p.terminate()
