# For use with tests in test_python3.py
import time
print("==> Begin streamed lines <==")
for number in range(5):
    print(number)
    time.sleep(1)
print("==> End streamed lines <==")
with open("./output/output.txt", "w") as f:
    f.write("Success")
