import getopt
import io

import stack, parse, state

def main(argv):
	state.stack = stack.Stack()
	try:
		opts, args = getopt.gnu_getopt(argv[1:], 's:c:ifru:b:')
	except getopt.GetoptError as err:
		print(err)
		usage()
		raise SystemExit(1)
	infile = None
	interactive = False
	encoding = None
	for o, a in opts:
		if o in ("-s", "--stack"): # starting stack: comma separated, left is top of the stack
			source = ' '.join(a.split(',')[::-1])
			tokens = parse.parse(source)
			for token in tokens:
				state.stack.apply(token)
		if o in ("-c", "--commands"): # input is this string
			if interactive or infile or encoding:
				print("Conflicting arguments")
				usage()
				raise SystemExit(1)
			infile = io.StringIO(a)
		if o in ("-i", "--interactive"):
			if interactive or infile or encoding:
				print("Conflicting arguments")
				usage()
				raise SystemExit(1)
			interactive = True
		if o in ("-f", "--float"): # parse float literals as FFloats, not FRationals
			state.float_parse = True
		if o in ("-r", "--rational"): # parse float literals as FRationals, default
			state.float_parse = False
		if o in ("-u", "--unicode"):
			if interactive or infile or encoding:
				print("Conflicting arguments")
				usage()
				raise SystemExit(1)
			encoding = "r"
		if o in ("-b", "--fiddle"):
			if interactive or infile or encoding:
				print("Conflicting arguments")
				usage()
				raise SystemExit(1)
			encoding = "rb"
	if interactive or (not infile and len(args) == 0):
		state.argv = args
		try:
			while True:
				source = input(">>> ")
				for token in parse.parse(source):
					token.apply(state.stack)
		except EOFError:
			if state.hasprinted:
				pass
			else:
				print(str(state.stack))
			raise SystemExit(0)
	else:
		if infile:
			state.argv = args
			#
		else:
			infile = open(args[0], encoding or "rb")
			state.argv = args[1:]
		source = infile.read()
		infile.close()
		for token in parse.parse(source):
			token.apply(state.stack)
		if state.hasprinted:
			pass
		else:
			print(str(state.stack))
		

if __name__ == "__main__":
	import sys
	main(sys.argv)
