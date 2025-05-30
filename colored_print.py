from colorama import init, Fore, Style
init(autoreset=True)

def print_title(title: str) -> None:
    print(Fore.YELLOW + Style.BRIGHT + title + Style.RESET_ALL)

def print_subtitle(subtitle: str) -> None:
    print(Fore.CYAN + Style.BRIGHT + subtitle + Style.RESET_ALL)

def print_info(info: str) -> None:
    print(Fore.CYAN + info + Style.RESET_ALL)

def print_warning(warning: str) -> None:
    print(Fore.YELLOW + Style.BRIGHT + warning + Style.RESET_ALL)

def print_error(error: str) -> None:
    print(Fore.RED + Style.BRIGHT + error + Style.RESET_ALL)

def print_success(success: str) -> None:
    print(Fore.GREEN + Style.BRIGHT + success + Style.RESET_ALL)

def print_debug(debug: str, end='\n', flush=False) -> None:
    print(Fore.MAGENTA + debug + Style.RESET_ALL, end=end, flush=flush)
