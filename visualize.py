from encoding import page

width = 32

def main():
	print('   ',*('  _'+hex(i)[-1] for i in range(16)))
	for r in range(12):
		print(''+hex(r)[-1]+'_ ',end='')
		for c in range(16):
			ch = page[c+16*r]
			if ch == ' ':
				print('\x1b[32m' + 'SP'.rjust(5) + '\x1b[0m',end='')
			elif ch.isprintable():
				print(ch.rjust(5), end='')
			else:
				print('\x1b[31m' + repr(ch)[1:-1].rjust(5), end='\x1b[0m')
		print()
	for p in range(16):
		inp = input('continue?')[:1].lower()
		if inp == 'n':
			return
		elif inp == 's':
			break
		print('     ' + ' '.join(hex(c)[2:].rjust(2) for c in range(width)))
		for r in range(512//width):
			print(hex(width*r+512*p)[2:].rjust(4),end='')
			for c in range(width):
				ch = chr(p*512+r*width+c)
				if ch == ' ':
					print('\x1b[32m SP\x1b[0m', end='')
				elif ch.isprintable():
					print(ch.rjust(3), end='')
				else:
					rp = repr(ch)[1:-1]
					print('\x1b[31m' + rp[-3:].ljust(3), end='\x1b[0m')
			print()
	for p in range(16, 2048):
		inp = input('continue?')[:1].lower()
		if inp == 'n':
			return
		elif inp == 's':
			break
		print('      ' + ' '.join(hex(c)[2:].rjust(2) for c in range(32)))
		for r in range(16):
			print(hex(32*r+512*p)[2:].rjust(5),end='')
			for c in range(32):
				ch = chr(p*512+r*32+c)
				if ch == ' ':
					print('\x1b[32m SP\x1b[0m', end='')
				elif ch.isprintable():
					print(ch.rjust(3), end='')
				else:
					rp = repr(ch)[1:-1]
					print('\x1b[31m' + rp[-3:].ljust(3), end='\x1b[0m')
			print()
	for p in range(2048, 2176):
		inp = input('continue?')[:1].lower()
		if inp == 'n':
			return
		elif inp == 's':
			break
		print('      ' + ' '.join(hex(c)[2:].rjust(2) for c in range(32)))
		for r in range(16):
			print(hex(32*r+512*p)[2:].rjust(6),end='')
			for c in range(32):
				ch = chr(p*512+r*32+c)
				if ch == ' ':
					print('\x1b[32m SP\x1b[0m', end='')
				elif ch.isprintable():
					print(ch.rjust(3), end='')
				else:
					rp = repr(ch)[1:-1]
					print('\x1b[31m' + rp[-3:].ljust(3), end='\x1b[0m')
			print()
	
if __name__ == '__main__':
	import sys
	if len(sys.argv) > 1:
		width = 2**(int(sys.argv[1]).bit_length() - 1)
	try:
		main()
	except (EOFError, KeyboardInterrupt):
		print()
