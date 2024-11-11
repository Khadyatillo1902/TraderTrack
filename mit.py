import os
import sys
import time

logo = '''\n\n\n\n\n\n\n
                               
                                                                MMMMMMMM               MMMMMMMM     IIIIIIIIII     TTTTTTTTTTTTTTTTTTTTTTT
                                                                M:::::::M             M:::::::M     I::::::::I     T:::::::::::::::::::::T
                                                                M::::::::M           M::::::::M     I::::::::I     T:::::::::::::::::::::T
                                                                M:::::::::M         M:::::::::M     II::::::II     T:::::TT:::::::TT:::::T
                                                                M::::::::::M       M::::::::::M       I::::I       TTTTTT  T:::::T  TTTTTT
                                                                M:::::::::::M     M:::::::::::M       I::::I               T:::::T        
                                                                M:::::::M::::M   M::::M:::::::M       I::::I               T:::::T        
                                                                M::::::M M::::M M::::M M::::::M       I::::I               T:::::T        
                                                                M::::::M  M::::M::::M  M::::::M       I::::I               T:::::T        
                                                                M::::::M   M:::::::M   M::::::M       I::::I               T:::::T        
                                                                M::::::M    M:::::M    M::::::M       I::::I               T:::::T        
                                                                M::::::M     MMMMM     M::::::M       I::::I               T:::::T        
                                                                M::::::M               M::::::M     II::::::II           TT:::::::TT      
                                                                M::::::M               M::::::M     I::::::::I           T:::::::::T      
                                                                M::::::M               M::::::M     I::::::::I           T:::::::::T      
                                                                MMMMMMMM               MMMMMMMM     IIIIIIIIII           TTTTTTTTTTT        
    \n\n'''

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def set_text_color(r, g, b):
    sys.stdout.write(f"\033[38;2;{r};{g};{b}m")

def reset_text_color():
    sys.stdout.write("\033[0m")

def print_colored_logo():
    for char in logo:
        if char == 'M' or char == 'T':
            set_text_color(227, 34, 53)
            sys.stdout.write(char)
            reset_text_color()
        else:
            # set_text_color(148, 148, 143)
            sys.stdout.write(char)

def print_loading_bar(progress):
    bar_width = 50
    filled_blocks = int(progress / 100 * bar_width)
    empty_blocks = bar_width - filled_blocks
    # set_text_color(255, 0, 0)
    sys.stdout.write(f"\r\t\t\t\t\t\t\t\tSuccess: [{'█' * filled_blocks}{'░' * empty_blocks}] {progress:.1f}%")
    reset_text_color()

clear_screen()
print_colored_logo()

for i in range(101):
    print_loading_bar(i)
    time.sleep(0.05)

print()
