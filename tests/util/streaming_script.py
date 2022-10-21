# For use with tests in test_python3.py
import datetime
import time
for number in range(5):
    print(number)
    time.sleep(1)
with open("./output/output.txt", "w") as f:
    f.write("Success")
