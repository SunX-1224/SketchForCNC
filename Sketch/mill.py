from window import *

def main():
    WIN = Window()
    while not WIN.EXIT:
        WIN.get_events()
        WIN.draw()
        WIN.update()
    WIN.destroy()



if __name__ == "__main__":
    main()