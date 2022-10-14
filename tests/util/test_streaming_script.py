# For use with tests in test_python3.py
import datetime
import time
print("attempting to print timestamps every second")
for _ in range(5):
    message = datetime.datetime.utcnow().isoformat() + "Z"
    print(message)
    time.sleep(1)
with open("./output/output.txt", "w") as f:
    f.write("Success")
