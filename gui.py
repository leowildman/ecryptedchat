import customtkinter
import tkinter
import tkinter.messagebox
from main import chat
import threading

customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("green")

app = customtkinter.CTk()
app.geometry("450x600")
app.title("Encrypted Messaging")


def flip_states(widgets:list):
    for widget in widgets:
        if widget._state == tkinter.NORMAL:
            widget.configure(state=tkinter.DISABLED)
        elif widget._state == tkinter.DISABLED:
            widget.configure(state=tkinter.NORMAL)


def start_server():
    if address.get() == "": add_text("Invalid Address\n", "error"); return
    if port.get() == "": add_text("Invalid Port\n", "error"); return
    
    global reciever
    ready_radio.configure(border_color="yellow")
    ready_radio.update()
    try:
        global chat_obj
        chat_obj = chat(is_server=switch1.get(), address=address.get(), port=int(port.get()), logging=add_text)
        chat_obj.start()
        
        reciever = threading.Thread(target=recieve_messages).start()
        flip_states([connect_btn, switch1, port, address, close_conn_btn, send_btn, message_inp, clear_btn])
        ready_radio.configure(border_color="green")
    except Exception as e:
        add_text(message=str(e)+"\n", identifier="error")
        ready_radio.configure(border_color="red")
    
def send_message():
    chat_obj.send_message(message_inp.get())
    add_text(message=(f"Me: {message_inp.get()}\n"), identifier="me")
    
def recieve_messages():
    while 1:
        message = chat_obj.recieve_message()
        if type(message) is str:
            print(type(message))
            add_text((f"{message}\n"), "other")
        else:
            add_text(f"Conn Closed {message}\n", "error")
            close_connection()
            break
    return
def close_connection():
    ready_radio.configure(border_color="yellow")
    flip_states([connect_btn, switch1, port, address, close_conn_btn, send_btn, message_inp, clear_btn])
    chat_obj.close_connection()
    ready_radio.configure(border_color="red")

def add_text(message, identifier):
    messages.configure(state=tkinter.NORMAL)
    messages.insert(tkinter.END, message, identifier)
    messages.configure(state=tkinter.DISABLED)
    messages.yview("end")
    
def clear_chat():
    messages.configure(state=tkinter.NORMAL)
    messages.delete(1.0, tkinter.END)
    messages.configure(state=tkinter.DISABLED)

top_info_frame = customtkinter.CTkFrame(master=app)
top_info_frame.pack(side=customtkinter.TOP, fill='x')

address = customtkinter.CTkEntry(master=top_info_frame, placeholder_text="Address: ")
address.pack(padx=5, pady=10, side=customtkinter.LEFT, fill='x', expand=True)

switch1 = customtkinter.CTkSwitch(master=top_info_frame, text="Server", onvalue=True, offvalue=False)
switch1.pack(padx=10, pady=10, side=customtkinter.RIGHT)

port = customtkinter.CTkEntry(master=top_info_frame, placeholder_text="Port: ", )
port.pack(padx=5, pady=10, side=customtkinter.RIGHT, fill='x', expand=True)

connection_frame = customtkinter.CTkFrame(master=app)
connection_frame.pack(fill='x')

close_conn_btn = customtkinter.CTkButton(master=connection_frame, text="Close Connection", command=close_connection, state=tkinter.DISABLED)
close_conn_btn.pack(padx=10, pady=10, side=customtkinter.RIGHT, fill='x', expand=True)

ready_radio = customtkinter.CTkRadioButton(master=connection_frame, border_color="red", text=None, hover=False, state=tkinter.DISABLED)
ready_radio.pack(padx=10, pady=10, side=tkinter.RIGHT)

connect_btn = customtkinter.CTkButton(master=connection_frame, text="Connect!", command=start_server)
connect_btn.pack(padx=10, pady=10, side=customtkinter.RIGHT, fill='x', expand=True)

send_frame = customtkinter.CTkFrame(master=app)
send_frame.pack(fill='x')

clear_btn = customtkinter.CTkButton(master=send_frame, text="Clear Chat", command=clear_chat, state=tkinter.DISABLED)
clear_btn.pack(padx=10, pady=10, fill='x', side=tkinter.TOP)

message_inp = customtkinter.CTkEntry(master=send_frame, placeholder_text="Message: ", state=tkinter.DISABLED)
message_inp.pack(padx=10, pady=10, side=tkinter.LEFT, fill='x', expand=True)

send_btn = customtkinter.CTkButton(master=send_frame, text="Send", command=send_message, state=tkinter.DISABLED)
send_btn.pack(padx=10, pady=10, side=tkinter.RIGHT)

vertical_scroll = customtkinter.CTkScrollbar(master=app, orientation='vertical')
vertical_scroll.pack(side=tkinter.RIGHT, fill = 'y')

messages = customtkinter.CTkTextbox(master=app, yscrollcommand=vertical_scroll.set, state=tkinter.DISABLED, font=("roberto", 13))
messages.tag_config(tagName="me", foreground="blue")
messages.tag_config(tagName="error", foreground="red")
messages.tag_config(tagName="log", foreground="orange")
messages.tag_config(tagName="other", foreground="green")
vertical_scroll.configure(command=messages.yview)
messages.pack(padx=10, pady=10, fill="both", expand=True)

app.mainloop()
