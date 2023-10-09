import os

homeItems = os.listdir('C:/Users/nyakno.okon/Desktop/basic-web-app-tutorial/Refactored')
homeContents = {"files": {}, "directories": {}}

#for contents in homeContents:
 #   print(contents)


fullPath = [os.path.join('C:/Users/nyakno.okon/Desktop/basic-web-app-tutorial/Refactored', items) for items in homeItems]
print(fullPath)