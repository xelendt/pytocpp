import sys, ast

depth = 0
cppcode = ["#include <cmath>",
		  	"#include <iostream>",
			"#include <cstdlib>"]

parents = []

literals = ['Num', 'Str', 'Bytes', 'Name']

def tokenize(node):
	if (type(node).__name__ == 'Num'):
		return node.n
	elif (type(node).__name__ == 'Str' or type(node).__name__ == 'Bytes'):
		return node.s
	elif (type(node).__name__ == 'Name'):
		print node.id
		return node.id

def visit_BinOp(node):
	global depth
	''' TODO 
		- matmult
		- floor div
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
		else:
			self.visitChildren(node)

		if (depth == 0):
			cppcode += a
		else:
		 	depth -=1
		return a


pycode = ast.parse(open(sys.argv[1]).read(), sys.argv[1])

print ast.dump(pycode)
#NodeWalker().visit(pycode)
cppcode += NodeWalker().generic_visit(pycode)
print cppcode
