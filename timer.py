from colorama import init, Fore, Back, Style
init()

print(Style.BRIGHT + "UP" + Style.RESET_ALL)
string = "1"
string = string.replace("1", Back.YELLOW + Fore.YELLOW + "██" + Style.RESET_ALL + " " + Back.CYAN + Fore.CYAN + "██" + Style.RESET_ALL)
print(string)