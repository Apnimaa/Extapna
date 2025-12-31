import getserver

def connect_server():
    try:
        getserver.connect_v1()
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    connect_server()




