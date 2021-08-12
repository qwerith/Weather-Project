from datetime import datetime
def test():
    date = datetime.now().strftime('%Y%m%d %H%M%S')
    with open ("/mnt/c/Users/Yura/documents/weather_project/data/" + date +".text", "w") as f:
        f.write("test" + date)
    
test()

