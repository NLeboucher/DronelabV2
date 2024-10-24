from threading import Thread
import mainD
# import mainO

if __name__ == "__main__":
    # Create threads
    thread1 = Thread(target=mainD.main)
    # thread2 = Thread(target=mainO.main)

    # Start threads
    thread1.start()
    # thread2.start()

    # Wait for both threads to finish
    thread1.join()
    # thread2.join()

    print("Both scripts completed")