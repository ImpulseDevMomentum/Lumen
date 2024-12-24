import basic, os

os.system('cls')
print()
while True:
	text = input('shell -> ')
	if text.strip() == "": continue
	
	if text.startswith('RUN("') and text.endswith('")'):
		filename = text[5:-2]
		if not filename.endswith('.lum'):
			print("Error: Only .lum files are supported")
			continue
		if not os.path.exists(filename):
			print(f"Error: File {filename} not found")
			continue
			
	result, error = basic.run('<stdin>', text)

	if error:
		print(error.as_string())
	elif result:
		if len(result.elements) == 1:
			print(repr(result.elements[0]))
		else:
			print(repr(result))
