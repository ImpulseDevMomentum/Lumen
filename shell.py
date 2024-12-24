import lang, os
from colorama import init, Fore, Style
init()

os.system('cls')
print()
while True:
	text = input(f'{Fore.GREEN}shell -> {Style.RESET_ALL}')
	if text.strip() == "": continue
	
	if text.startswith('RUN("') and text.endswith('")'):
		filename = text[5:-2]
		if not filename.endswith('.lum'):
			print(f"{Fore.RED}Error: Only .lum files are supported{Style.RESET_ALL}")
			continue
		if not os.path.exists(filename):
			print(f"{Fore.RED}Error: File {filename} not found{Style.RESET_ALL}")
			continue
			
	result, error = lang.run('<stdin>', text)

	if error:
		print(error.as_string())
	elif result:
		if len(result.elements) == 1:
			print(f"{Fore.CYAN}{repr(result.elements[0])}{Style.RESET_ALL}")
		else:
			print(f"{Fore.CYAN}{repr(result)}{Style.RESET_ALL}")
