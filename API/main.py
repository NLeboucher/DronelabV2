import threading
import mainD
import mainO

if __name__ == "__main__":
    # Create threads
    thread1 = threading.Thread(target=mainD.main)
    thread2 = threading.Thread(target=mainO.main)

    # Start threads
    thread1.start()
    thread2.start()

    # Wait for both threads to finish
    thread1.join()
    thread2.join()

    print("Both scripts completed")