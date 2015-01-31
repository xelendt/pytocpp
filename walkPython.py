import sys, ast

libraries = ["#include <cmath>",
		  	"#include <iostream>",
			"#include <cstdlib>"]

cppcode = "".join(libraries)

parents = []

def dummy():
	print "Hello"


def visit_BinOp(node, i):
	if i == 0:
		return node.n
	elif i == 1:
		return type(node).__name__ 
	else:
		return node.n

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
	
	def visit_for(self, node, i):
		'''target'''
		if (i == 0):
			cppcode += ''
		'''iteration '''
		if (i == 1):
			cppcode += ''
		'''body'''
		if (i == 2):
			cppcode += ''

    def generic_visit(self, node):
		global cppcode
		if (type(node).__name__ == 'Assign'):
			parents.append("Assign")
			for kid in ast.iter_child_nodes(node):
				self.visit(kid)
		elif (type(node).__name__ == 'BinOp'):
			children = []
			i = 0
			for kid in ast.iter_child_nodes(node):
				children.append(visit_BinOp(kid, i))
				i += 1
			print children[1]
			if (children[1] == 'Add'):
				cppcode += str(children[0])
				cppcode += '+'
				cppcode += str(children[2])
			elif (children[1] == 'Sub'):
				cppcode += str(children[0])
				cppcode += '-'
				cppcode += str(children[2])
			elif (children[1] == 'Mult'):
				cppcode += str(children[0])
				cppcode += '*'
				cppcode += str(children[2])
			elif (children[1] == 'MatMult'):
				pass
			elif (children[1] == 'Div'):
				cppcode += str(children[0])
				cppcode += '/'
				cppcode += str(children[2])
			elif (children[1]== 'Pow'):
				cppcode += 'pow('
				cppcode += str(children[0]) + ', ' + str(children[2])
				cppcode += ')'
			elif (children[1]== 'LShift'):
				cppcode += str(children[0])
				cppcode += '<<'
				cppcode += str(children[2])
			elif (children[1] == 'RShift'):
				cppcode += str(children[0])
				cppcode += '>>'
				cppcode += str(children[2])
				
#	elif (type(node).__name__ == 
		else:
			self.visitChildren(node)
		print self.indent, 'Generic visit', node, type(node).__name__

pycode = ast.parse(open(sys.argv[1]).read(), sys.argv[1])
NodeWalker().visit(pycode)

print cppcode
