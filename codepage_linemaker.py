from sys import argv
from encoding import page, encode

def main(code: int) -> None:
	char = chr(code)
	print(char+',', ((char in page) and hex(page.find(char)) or 'N/A') + ',', ' '.join(hex(b) for b in encode(char)) + ': ')

if __name__ == '__main__':
	if len(argv) > 1:
		for arg in argv[1:]:
			main(int(arg))
	else:
		raise ValueError("This program needs an argument.")
