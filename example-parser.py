file_reader = open("gps.txt")

with open("output.txt", 'a') as out:
    
    for line in file_reader:
        print(line)
        out.write(line + '\n')

file_reader.close()
    
# fh = open("sample.txt", "r")
# print (fh.read())    

