import os
import shutil

source = r"C:\Users\mmandziej001\Desktop\Projects\EMIS\OUTPUT_API\JSONS_REGISTER\\"
dest = r"C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\POLAND_DANE\REGISTER\Operational\ALL\\"
"C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\POLAND_DANE\REGISTER\Operational\ALL\JSONS_REGISTER"

a = os.listdir(source)
b = os.listdir(dest)

destination = shutil.move(r"C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\POLAND_DANE\REGISTER\Operational\ALL\JSONS_REGISTER", r"C:\Users\mmandziej001\Desktop\Projects\EMIS\OUTPUT_API")

test = a[:]

count = 0
error_cnt = 0
errors = []
for file in test:
    try:
        shutil.move(source + file, dest)
        count += 1
        print("Move files: ", count)
    except:
        errors.append(file)
        error_cnt += 1
        print("Errors: ", error_cnt)