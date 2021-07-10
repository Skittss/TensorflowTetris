from pynput import keyboard

def on_press(key):
    print(f"press: {key}")
    print(type(key))

def on_release(key):
    print(f"release: {key}")

with keyboard.Listener(on_press = on_press, on_release=on_release) as listener:
    listener.join()
