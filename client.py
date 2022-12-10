from main import chat

sut = chat(is_server=False, address="localhost", port=9999, message_bytes=2048)
print("Ready")
sut.start()

while 1:
    message = sut.recieve_message()
    if message is not None:
        print(message)
    else:
        print("Conn closed")
        break