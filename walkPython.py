import sys, ast

depth = 0
cppcode = ["#include <cmath>",
		  	"#include <iostream>",
			"#include <cstdlib>",
			"#include <string>",
			"using namespace std;"]

parents = []

literals = ['Num', 'Str', 'Bytes', 'Name', 'NameConstant', 'float', 'int', 'List']
variables = []

def tokenize(node):
	if (type(node).__name__ == 'Num'):
		return node.n
	elif (type(node).__name__ == 'Str' or type(node).__name__ == 'Bytes'):
		return node.s
	elif (type(node).__name__ == 'Name'):
		if (node.id == 'True'):
			return 'true'
		elif (node.id == 'False'):
			return 'false'
		else:
			return node.id

"""NOTE: FUNCTIONS THAT CALL THIS ALREADY HAVE LISTS WITHIN THEIR FUNCTIONS; THE 'a' VARIABLE IS NOT NEEDED"""
def tokenizeNode(node):
	a = []
	global literals, depth
	if (type(node).__name__ in literals):
		a.append(tokenize(node))
	else:
		depth += 1
		print "DEPTH", depth
		a.append(NodeWalker().generic_visit(node))
	return a

def get_Type(node):
	if (type(node).__name__ in literals):
		if (type(node).__name__ == 'Num'):
			return type(node.n).__name__
		elif (type(node).__name__ == 'List'):
			return type(node).__name__
		else:
			return type(node).__name__
	elif (type(node).__name__ == 'Compare'):
		return 'NameConstant'
	elif (type(node).__name__ == 'UnaryOp'):
		return get_Type(node.operand)
	elif (type(node).__name__ == 'BinOp'):
		left = get_Type(node.left)
		right = get_Type(node.right)
		if left == 'Str' or left == 'NameConstant':
			return left
		elif (left == 'float' or right == 'float'):
			return type(1.2).__name__ #float
		else:
		 	return type(1).__name__ #int

def visit_Assign(node):
	''' TODO
		- double pointers
		- arrays
		- commas (a, b = 1)
	'''
	global depth, variables
	a = []	
	
#	print get_Type(node.value)
	variableType = get_Type(node.value)

	for t in node.targets:
		if (type(t).__name__ == 'Name'):
			if t.id not in variables:
				if (variableType == 'NameConstant'):
					a.append("bool " + str(t.id) + ";\n")
				elif (variableType == 'Str'):
					a.append("string " + str(t.id) + ";\n")
				elif (variableType == 'float'):
					a.append("double " + str(t.id) + ";\n")
				elif (variableType == 'int'):
					a.append("int " + str(t.id) + ";")
				elif (variableType == 'List'):
					l = []
					''' declare the list '''
					if (len(node.value.elts) > 0):
						arrayType = get_Type(node.value.elts[0])
						''' put down the corresponding type declaration for the arrayType '''
					
						if (arrayType == 'float' or arrayType == 'int'):
							l.append('double ')
						elif (arrayType == 'Str'):
							l.append('string ')

						''' put down the variable name '''
						l.append(str(t.id))
						l.append('[' + str(len(node.value.elts))+ ']={')
						l.append(tokenizeNode(node.value.elts[0]))
						for e in range(1, len(node.value.elts)):
							l.append(',')
							l.append(tokenizeNode(node.value.elts[e]))
						
						l.append('};')
					a.append(l)	
					continue
				variables.append(t.id)
		else:	
			if t.id not in variables:
				if (variableType == 'NameConstant'):
					a.append("bool* " + str(t.id) + ";\n")
				elif (variableType == 'Str'):
					a.append("string* " + str(t.id) + ";\n")
				elif (variableType == 'float'):
					a.append("double* " + str(t.id) + ";\n")
				elif (variableType == 'int'):
					a.append("int* " + str(t.id) + ";")
				variables.append(t.id)

	for t in node.targets:
		if (type(node.value).__name__ != 'List'):
			a.append(t.id + ' = ' )
	if (type(node.value).__name__ in literals):
		if ((type(node.value).__name__ == 'Num')):
			a.append(node.value.n)
		elif (type(node.value).__name__ == 'List'):
			pass
		elif (node.value.id == 'True'):
			a.append("true")
		elif (node.value.id == "False"):
			a.append("false")
		else:
			a.append(node.value.s)
	else:
		depth += 1
		a.append(NodeWalker().generic_visit(node.value))
#	a.append(";")	

	return a
				

def visit_BoolOp(node):
	a = []
	global depth
	for t in node.values:
		print "Node name", type(t).__name__
		if (type(t).__name__ in literals):
			a.append(tokenize(t))
		else:
			depth += 1
			a.append(generic_visit(t))
	
	print node.op
	if (type(node.op).__name__ == 'And'):
		a = a[0] + "&&" + a[1]
	elif (type(node.op).__name__ == 'Or'):
		a = a[0] + '||' + a[1]
	return a
		
def visit_BinOp(node):
	global depth
	''' TODO 
		- matmult
		- floor div
		- brackets for recursive calls
	'''
	a = []
	''' left side '''
	if (type(node.left).__name__ in literals):
		a.append(tokenize(node.left))
	else:
		depth += 1
		a.append(NodeWalker().generic_visit(node.left))
	''' right side '''
	if (type(node.right).__name__ in literals):
		a.append(tokenize(node.right))
	else:
		depth += 1
		a.append(NodeWalker().generic_visit(node.right))
	''' operator FUN '''
	if (type(node.op).__name__ == 'Add'):
		a.insert(1, ' + ')
	elif (type(node.op).__name__ == 'Sub'):
		a.insert(1, ' - ')
	elif (type(node.op).__name__ == 'Mult'):
		a.insert(1, ' * ')
	elif (type(node.op).__name__ == 'Div'):
		a.insert(1, ' / ')
	elif (type(node.op).__name__ == 'Mod'):
		a.insert(1, ' % ')
	elif (type(node.op).__name__ == 'LShift'):
		a.insert(1, ' << ')
	elif (type(node.op).__name__ == 'RShift'):
		a.insert(1, ' >> ')
	elif (type(node.op).__name__ == 'BitOr'):
		a.insert(1, ' | ')
	elif (type(node.op).__name__ == 'BitXor'):
		a.insert(1, ' ^ ')
	elif (type(node.op).__name__ == 'BitAnd'):
		a.insert(1, ' & ')
	elif (type(node.op).__name__ == 'Pow'):
		a.insert(0, 'Pow(')
		a.insert(len(a), ')')

	return a

"""NOTE: THIS IMPLEMENTATION DOES NOT TAKE INTO ACCOUNT TO THE SEMI-COLONS INSIDE THE IF STRUCTURE!!!"""
def visit_If(node, state):
	global depth
#depth -= 1
	a = []
	if (state == 'if' or state == 'elif'):
		''' say the test'''
		if (state == 'if'):
			a.append('if')
		else:
			a.append('else if')
		a.append('(')
		a.append(tokenizeNode(node.test))
		a.append(')')

		''' say the body '''
		a.append('{')
		for b in node.body:
			a.append(tokenizeNode(b))
			a.append(';\n')
		a.append('}')

		''' check for orelse '''

		if(node.orelse != []):
			if (type(node.orelse[0]).__name__ == 'If'):
				for stmt in node.orelse:
					a.append(visit_If(stmt, 'elif'))
			else:
				a.append(visit_If(node.orelse, 'else'))
	elif (state == 'else'):
		''' only need to state the body and then return a '''
		a.append('else')
		a.append('{')
		for stmt in node:
			a.append(tokenizeNode(stmt))
			a.append(';\n')
		a.append('}')
		
	return a

def visit_Comparison(node):
	a = []
	global depth
	''' we take in the 'left' '''

	a.append(tokenizeNode(node.left))
	if (type(node.ops[0]).__name__ == 'Eq'):
		a.append('==')
	elif (type(node.ops[0]).__name__ == 'NotEq'):
		a.append('!=')
	elif (type(node.ops[0]).__name__ == 'Lt'):
		a.append('<')
	elif (type(node.ops[0]).__name__ == 'LtE'):
		a.append('<=')
	elif (type(node.ops[0]).__name__ == 'Gt'):
		a.append('>')
	elif (type(node.ops[0]).__name__ == 'GtE'):
		a.append('>=')
	a.append(tokenizeNode(node.comparators[0]))

	for i in range (0,len(node.ops)-1):
		a.append("&&")
		a.append(tokenizeNode(node.comparators[i]))
		if (type(node.ops[i+1]).__name__ == 'Eq'):
			a.append('==')
		elif (type(node.ops[i+1]).__name__ == 'NotEq'):
			a.append('!=')
		elif (type(node.ops[i+1]).__name__ == 'Lt'):
			a.append('<')
		elif (type(node.ops[i+1]).__name__ == 'LtE'):
			a.append('<=')
		elif (type(node.ops[i+1]).__name__ == 'Gt'):
			a.append('>')
		elif (type(node.ops[i+1]).__name__ == 'GtE'):
			a.append('>=')
#	elif (type(node.ops[i]).__name__ == 'Is'):
#			a.append('==')
		a.append(tokenizeNode(node.comparators[i+1]))

	''' for a < b < c < d < e, you have to do a == b && b == c && c == d etc ... '''

	return a

def visit_UnaryOp(node):
    #Creating a list that represents the string to be outputted
#	print "entered unary op"
	a = []
    #First, adding the unary operator to the list
	if(type(node.op).__name__ == "UAdd"):
		a.append("+")
	elif(type(node.op).__name__ == "USub"):
		a.append("-")
	elif(type(node.op).__name__ == "Invert"):
		a.append("!")
	elif(type(node.op).__name__ == "Not"):
		a.append("~")
    #Next, add the operand to the list
	if(type(node.operand).__name__ in literals):
#	print type(node.operand).__name__, type(node.op).__name__
		a.append(tokenize(node.operand))
	else:
		depth += 1
		a.append(NodeWalker().generic_visit(node.operand))

	return a

def visit_While(node):
	a = []
	global depth
#	depth -=1
	''' first declare the test '''
	a.append('while(')
	a.append(tokenizeNode(node.test))
	a.append(')')
	a.append('{')
	for stmt in node.body:
		a.append(tokenizeNode(stmt))
		a.append(';\n')
	a.append('}')

	return a

def visit_For(node):
	a = []
	'''
	if (type(node.iter).__name__ == "Call"):
		print node.iter.func, "WHY OH WHY"
		if (node.iter.func.id == 'range'):
			print "WHY DOES THIS HAPPEN", tokenizeNode(node.iter.args[0])[0]
			node.iter = ast.expr()
			node.iter.range(tokenizeNode(node.iter.args[0])[0], tokenizeNode(node.iter.args[1])[0], tokenizeNode(node.iter.args[2])[0]))
	'''
	assignop = ast.Assign()
	assignop.targets = [ast.Name(id = 'forlist', ctx=ast.Store())]
	assignop.value = node.iter

	a.append(visit_Assign(assignop))

	arrayType = a[0][0][0]

	a.append('for(int pyceptionlol = 0; pyceptionlol < forlist.size();pyceptionlol ++)')
	a.append('{')
	a.append(str(arrayType) + str(node.target.id) + '=forlist[pyceptionlol]')
	for b in node.body:
		a.append(tokenizeNode(b))
	a.append('}')

	return a

class NodeWalker(ast.NodeVisitor):
    def __init__(self):
        self.indent=''
    def visit_Import(self, node):
        print self.indent, 'Process Import'
        self.visitChildren(node)
    def visit_Str(self, node):
        print self.indent, 'String:', repr(node.s)

    def visitChildren(self, node):
        old_indent = self.indent
        self.indent += '  '
        for kid in ast.iter_child_nodes(node):
            self.visit(kid)
        self.indent = old_indent
	
    def generic_visit(self, node):
		global cppcode, depth
		print self.indent, 'Generic visit', node, type(node).__name__
		a = []
		if (type(node).__name__ == 'BinOp'):
			a += visit_BinOp(node)
			print a
		elif (type(node).__name__ == 'UnaryOp'):
			a += visit_UnaryOp(node)
		elif (type(node).__name__ == 'Assign'):
			a += visit_Assign(node)
		elif (type(node).__name__ == 'BoolOp'):
			a += visit_BoolOp(node)
		elif (type(node).__name__ == 'Compare'):
			a += visit_Comparison(node)
		elif (type(node).__name__ == 'If'):
			a += visit_If(node, 'if')
		elif (type(node).__name__ == 'While'):
			a += visit_While(node)
		elif (type(node).__name__ == 'For'):
			a += visit_For(node)
		else:
			self.visitChildren(node)

		if (depth == 0):
			cppcode += a + [';\n']
		else:
#	a.append(')')
#		 	a = ['('] + a[:len(a)]
		 	depth -=1
		return a

def printArray(a):
	string = ""
	for i in a:
		if (type(i).__name__ == 'List'):
			string += printArray(i)
		else:
			string += str(i)
	return string

pycode = ast.parse(open(sys.argv[1]).read(), sys.argv[1])

#print ast.dump(pycode)
#NodeWalker().visit(pycode)
cppcode += NodeWalker().generic_visit(pycode)
#print cppcode
#for elmt in cppcode:
#	print elmt
