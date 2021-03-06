from xyzMath import Vec,Mat,Xform,RAD,projperp,SYMTET,SYMOCT
import itertools,re,os,inspect
from pymol_util import cgo_cyl,pymol


symelem_nshow = 0
class SymElem(object):
	"""docstring for SymElem"""
	def __init__(self, kind, axis=Vec(0,0,1), cen=Vec(0,0,0), axis2=Vec(1,0,0), col=None,input_xform=None):
		super(SymElem, self).__init__()
		self.kind = kind
		self.axis = axis.normalized()
		self.cen = cen
		self.axis2 = axis2.normalized()
		self.col=col
		self.frames = []
		self.input_xform = input_xform
		if self.kind == "Z":
			self.frames = [
				Xform( Mat( Vec( 1, 0, 0), Vec( 0, 1, 0), Vec( 0, 0, 1) ), Vec(0,0,0) ),
				Xform( Mat( Vec( 1, 0, 0), Vec( 0, 1, 0), Vec( 0, 0, 1) ), cen ), ]
			#identity & translation by cen
		elif self.kind.startswith("C"):
			assert not input_xform
			self.nfold = int(self.kind[1:])
			for i in range(self.nfold):
				deg = i*360.0/self.nfold
				self.frames.append( RAD(self.axis,deg,cen) )
		elif self.kind.startswith("D"):
			assert not input_xform
			self.nfold = int(self.kind[1:])
			assert abs(axis.dot(axis2)) < 0.00001
			for i in range(self.nfold):
				deg = i*360.0/self.nfold
				cx = RAD(self.axis,deg,cen)
				self.frames.append( cx )
				self.frames.append( RAD(self.axis2,180.0,cen) * cx )
		elif self.kind == "T":
			self.frames = [
				Xform( Mat( Vec( 1, 0, 0), Vec( 0, 1, 0), Vec( 0, 0, 1) ), Vec(0,0,0) ),
				Xform( Mat( Vec( 0, 0, 1), Vec( 1, 0, 0), Vec( 0, 1, 0) ), Vec(0,0,0) ),
				Xform( Mat( Vec( 0, 0, 1), Vec(-1, 0, 0), Vec( 0,-1, 0) ), Vec(0,0,0) ),
				Xform( Mat( Vec( 0, 0,-1), Vec( 1, 0, 0), Vec( 0,-1, 0) ), Vec(0,0,0) ),
				Xform( Mat( Vec( 0, 0,-1), Vec(-1, 0, 0), Vec( 0, 1, 0) ), Vec(0,0,0) ),
				Xform( Mat( Vec( 0, 1, 0), Vec( 0, 0, 1), Vec( 1, 0, 0) ), Vec(0,0,0) ),
				Xform( Mat( Vec( 0, 1, 0), Vec( 0, 0,-1), Vec(-1, 0, 0) ), Vec(0,0,0) ),
				Xform( Mat( Vec( 0,-1, 0), Vec( 0, 0, 1), Vec(-1, 0, 0) ), Vec(0,0,0) ),
				Xform( Mat( Vec( 0,-1, 0), Vec( 0, 0,-1), Vec( 1, 0, 0) ), Vec(0,0,0) ),
				Xform( Mat( Vec( 1, 0, 0), Vec( 0,-1, 0), Vec( 0,-0,-1) ), Vec(0,0,0) ),
				Xform( Mat( Vec(-1, 0, 0), Vec( 0, 1, 0), Vec( 0, 0,-1) ), Vec(0,0,0) ),
				Xform( Mat( Vec(-1, 0, 0), Vec( 0,-1, 0), Vec( 0, 0, 1) ), Vec(0,0,0) )
			]
			if input_xform: xc = Xform(cen) * input_xform
			else:           xc = Xform(cen)
			for i,x in enumerate(self.frames):
				self.frames[i] = xc*x*(~xc)
		elif self.kind == "O":
			self.frames = [
				Xform( Mat( Vec(+1,+0,-0), Vec(+0,+1,+0), Vec(+0,-0,+1) ), Vec(0,0,0) ),
				Xform( Mat( Vec(+0,+1,+0), Vec(+1,+0,-0), Vec(-0,+0,-1) ), Vec(0,0,0) ),
				Xform( Mat( Vec(+0,-0,+1), Vec(+1,+0,-0), Vec(-0,+1,+0) ), Vec(0,0,0) ),
				Xform( Mat( Vec(+1,+0,-0), Vec(+0,-0,+1), Vec(+0,-1,-0) ), Vec(0,0,0) ),
				Xform( Mat( Vec(-0,+0,-1), Vec(+0,+1,+0), Vec(+1,-0,-0) ), Vec(0,0,0) ),
				Xform( Mat( Vec(-0,+1,+0), Vec(+0,-0,+1), Vec(+1,+0,-0) ), Vec(0,0,0) ),
				Xform( Mat( Vec(+0,+1,+0), Vec(-0,+0,-1), Vec(-1,+0,+0) ), Vec(0,0,0) ),
				Xform( Mat( Vec(+0,-0,+1), Vec(-0,+1,+0), Vec(-1,-0,+0) ), Vec(0,0,0) ),
				Xform( Mat( Vec(+0,-1,-0), Vec(+1,+0,+0), Vec(+0,-0,+1) ), Vec(0,0,0) ),
				Xform( Mat( Vec(+1,-0,-0), Vec(-0,+0,-1), Vec(+0,+1,+0) ), Vec(0,0,0) ),
				Xform( Mat( Vec(+1,+0,+0), Vec(+0,-1,-0), Vec(-0,+0,-1) ), Vec(0,0,0) ),
				Xform( Mat( Vec(-0,+0,-1), Vec(+1,-0,-0), Vec(-0,-1,-0) ), Vec(0,0,0) ),
				Xform( Mat( Vec(-1,+0,+0), Vec(+0,+1,-0), Vec(-0,+0,-1) ), Vec(0,0,0) ),
				Xform( Mat( Vec(-1,-0,+0), Vec(+0,+0,+1), Vec(-0,+1,+0) ), Vec(0,0,0) ),
				Xform( Mat( Vec(+0,-0,+1), Vec(+0,-1,-0), Vec(+1,+0,+0) ), Vec(0,0,0) ),
				Xform( Mat( Vec(+0,+1,-0), Vec(-1,+0,+0), Vec(+0,-0,+1) ), Vec(0,0,0) ),
				Xform( Mat( Vec(+0,+0,+1), Vec(-1,-0,+0), Vec(+0,-1,-0) ), Vec(0,0,0) ),
				Xform( Mat( Vec(+0,-1,-0), Vec(-0,-0,+1), Vec(-1,-0,-0) ), Vec(0,0,0) ),
				Xform( Mat( Vec(-0,-1,-0), Vec(-0,+0,-1), Vec(+1,-0,-0) ), Vec(0,0,0) ),
				Xform( Mat( Vec(-0,+0,-1), Vec(-1,+0,+0), Vec(+0,+1,-0) ), Vec(0,0,0) ),
				Xform( Mat( Vec(+0,+0,-1), Vec(-0,-1,-0), Vec(-1,+0,+0) ), Vec(0,0,0) ),
				Xform( Mat( Vec(-1,+0,+0), Vec(-0,+0,-1), Vec(-0,-1,+0) ), Vec(0,0,0) ),
				Xform( Mat( Vec(-1,-0,-0), Vec(+0,-1,-0), Vec(-0,-0,+1) ), Vec(0,0,0) ),
				Xform( Mat( Vec(+0,-1,-0), Vec(-1,-0,-0), Vec(+0,+0,-1) ), Vec(0,0,0) ),
			]
			if input_xform: xc = Xform(cen) * input_xform
			else:           xc = Xform(cen)
			for i,x in enumerate(self.frames):
				self.frames[i] = (xc)*x*(~xc)

		assert self.frames
		if not self.frames[0] == Xform():
			print self.kind,self.frames[0].pretty()
			assert self.frames[0] == Xform()
	def show(self, label=None, **kwargs):
		if not label:
			global symelem_nshow
			label = "SymElem_%i"%symelem_nshow
			symelem_nshow += 1
		pymol.cmd.delete(label)
		v = pymol.cmd.get_view()
		CGO = self.cgo(**kwargs)
		pymol.cmd.load_cgo(CGO,label)
		pymol.cmd.set_view(v)
	def cgo(self, length=20.0, radius=0.5, sphereradius=1.5, col=None,showshape=0,**kwargs):
		if not col and self.col: col = self.col
		CGO = []
		x = Xform()
		if "xform" in kwargs:
			x = kwargs["xform"]
		if self.kind[0] in "CD":
			if not col:
				if   self.kind is "C2": col = (1.0,0.0,0.0)
				elif self.kind is "C3": col = (0.0,1.0,0.0)
				elif self.kind is "C4": col = (0.0,0.0,1.0)
				elif self.kind is "C5": col = (1.0,0.7,0.8)
				elif self.kind is "C6": col = (1.0,1.0,0.0)
				elif self.kind is "D2": col = (1.0,0.0,1.0)
				elif self.kind is "D3": col = (0.0,1.0,1.0)
				elif self.kind is "D4": col = (1.0,0.5,0.0)
				elif self.kind is "D6": col = (0.5,1.0,0.0)
				else: raise NotImplementedError("unknown symelem kind "+self.kind)
			a = self.axis * length/2.0
			c = self.cen
			c1, c2 = self.cen - a, self.cen + a
			c  = x*c; c1 = x*c1; c2 = x*c2	
			c.round0(); c1.round0(); c2.round0()
			CGO.extend([
				#pymol.cgo.BEGIN, pymol.cgo.LINES,
				#pymol.cgo.COLOR, col[0], col[1],col[2],
				#pymol.cgo.VERTEX, self.cen.x-a.x, self.cen.y-a.y, self.cen.z-a.z,
				#pymol.cgo.VERTEX, self.cen.x+a.x, self.cen.y+a.y, self.cen.z+a.z,
				#pymol.cgo.END,
				pymol.cgo.CYLINDER, c1.x,     c1.y,     c1.z,      c2.x,     c2.y,     c2.z, radius,
				# pymol.cgo.CYLINDER, 0,     50,    0,      0,    -50,     0, radius,
				col[0], col[1], col[2],
				col[0], col[1], col[2],
				pymol.cgo.SPHERE,
				c.x, c.y, c.z, sphereradius 
			])
			if self.kind.startswith("D"):
				for i in range(self.nfold):
					xtmp = self.frames[2*i].R
					if self.nfold==2 and i==1:
						xtmp = RAD(self.axis,90)
					a = xtmp*self.axis2 * length/2.0
					c = self.cen
					c1, c2 = self.cen - a, self.cen + a
					if "xform" in kwargs:
						x = kwargs["xform"]
						c  = x*c; c1 = x*c1; c2 = x*c2	
					c.round0(); c1.round0(); c2.round0()
					r = radius if self.nfold==2 else radius
					CGO.extend( [
						pymol.cgo.CYLINDER, c1.x,     c1.y,     c1.z,      c2.x,     c2.y,     c2.z, r,
						col[0], col[1], col[2],
						col[0], col[1], col[2],
					] )
		elif self.kind == "T":
			cen = x*self.cen
			cen.round0(); 
			CGO.extend( cgo_sphere(cen,1.6*sphereradius,col=(0.5,0.5,1)) )
			seen2,seen3 = list(),list()
			for f in self.frames:
				c2b = x.R*f.R*( Vec(1,0,0).normalized()*length/2.0)
				c3a = x.R*f.R*(-Vec(1,1,1).normalized()*length/2.0)
				c3b = x.R*f.R*( Vec(1,1,1).normalized()*length/2.0)
				c2b.round0(); c3a.round0(); c3b.round0()
				if not c2b in seen2:
					CGO.extend( cgo_cyl(cen,cen+c2b,radius,col=(1,0,0)) )
					seen2.append(c2b)
				if not c3a in seen3:
					CGO.extend( cgo_cyl(cen+c3a,cen+c3b,radius,col=(0,1,0)) )
					seen3.append(c3a)
					seen3.append(c3b)					
		elif self.kind == "O":
			cen = x*self.cen
			cen.round0(); 
			CGO.extend( cgo_sphere(cen,1.6*sphereradius,col=(0.5,0.5,1)) )
			seen2,seen3,seen4 = list(),list(),list()
			for f in self.frames:
				c2a = x.R*f.R*(-Vec(1,1,0).normalized()*length/2.0)
				c2b = x.R*f.R*( Vec(1,1,0).normalized()*length/2.0)
				c3a = x.R*f.R*(-Vec(1,1,1).normalized()*length/2.0)
				c3b = x.R*f.R*( Vec(1,1,1).normalized()*length/2.0)
				c4a = x.R*f.R*(-Vec(1,0,0).normalized()*length/2.0)
				c4b = x.R*f.R*( Vec(1,0,0).normalized()*length/2.0)
				c2a.round0(); c2b.round0(); c3a.round0(); c3b.round0(); c4a.round0(); c4b.round0();
				if not c2b in seen2:
					CGO.extend( cgo_cyl(cen+c2a,cen+c2b,radius,col=(1,0,0)) )
					seen2.append(c2a)
					seen2.append(c2b)
				if not c3a in seen3:
					CGO.extend( cgo_cyl(cen+c3a,cen+c3b,radius,col=(0,1,0)) )
					seen3.append(c3a)
					seen3.append(c3b)					
				if not c4a in seen4:
					CGO.extend( cgo_cyl(cen+c4a,cen+c4b,radius,col=(0,0,1)) )
					seen4.append(c4a)
					seen4.append(c4b)
		if showshape:
			if self.kind=="C2":
				axs = x.R*self.axis
				cen = x*self.cen
				p1 = x.R*projperp(self.axis,Vec(7,3,1)).normalized()*30.0
				p2 = RAD(axs,180.0)*p1
				p3 = x.R*projperp(self.axis,Vec(1,3,7)).normalized()*30.0
				p4 = RAD(axs,180.0)*p3
				p1 = cen + p1; p2 = cen + p2; p3 = cen + p3; p4 = cen + p4;
				axs.round0(); p1.round0(); p2.round0(); p3.round0(); p4.round0()
				# print p1,p2,p3,p4
				CGO.extend([
					pymol.cgo.BEGIN, pymol.cgo.TRIANGLES, pymol.cgo.COLOR, col[0], col[1], col[2], pymol.cgo.ALPHA, 1,
						pymol.cgo.NORMAL, axs.x, axs.y, axs.z, pymol.cgo.VERTEX,  p1.x+axs.x/10.0, p1.y+axs.y/10.0, p1.z+axs.z/10.0,
						pymol.cgo.NORMAL, axs.x, axs.y, axs.z, pymol.cgo.VERTEX,  p2.x+axs.x/10.0, p2.y+axs.y/10.0, p2.z+axs.z/10.0,
						pymol.cgo.NORMAL, axs.x, axs.y, axs.z, pymol.cgo.VERTEX,  p3.x+axs.x/10.0, p3.y+axs.y/10.0, p3.z+axs.z/10.0,
						pymol.cgo.NORMAL, axs.x, axs.y, axs.z, pymol.cgo.VERTEX,  p1.x+axs.x/10.0, p1.y+axs.y/10.0, p1.z+axs.z/10.0, 
						pymol.cgo.NORMAL, axs.x, axs.y, axs.z, pymol.cgo.VERTEX,  p2.x+axs.x/10.0, p2.y+axs.y/10.0, p2.z+axs.z/10.0,
						pymol.cgo.NORMAL, axs.x, axs.y, axs.z, pymol.cgo.VERTEX,  p4.x+axs.x/10.0, p4.y+axs.y/10.0, p4.z+axs.z/10.0,
						 pymol.cgo.COLOR, 1-col[0], 1-col[1], 1-col[2], 
						pymol.cgo.NORMAL, -axs.x, -axs.y, -axs.z, pymol.cgo.VERTEX,  p1.x-axs.x/10.0, p1.y-axs.y/10.0, p1.z-axs.z/10.0,
						pymol.cgo.NORMAL, -axs.x, -axs.y, -axs.z, pymol.cgo.VERTEX,  p2.x-axs.x/10.0, p2.y-axs.y/10.0, p2.z-axs.z/10.0,
						pymol.cgo.NORMAL, -axs.x, -axs.y, -axs.z, pymol.cgo.VERTEX,  p3.x-axs.x/10.0, p3.y-axs.y/10.0, p3.z-axs.z/10.0,
						pymol.cgo.NORMAL, -axs.x, -axs.y, -axs.z, pymol.cgo.VERTEX,  p1.x-axs.x/10.0, p1.y-axs.y/10.0, p1.z-axs.z/10.0, 
						pymol.cgo.NORMAL, -axs.x, -axs.y, -axs.z, pymol.cgo.VERTEX,  p2.x-axs.x/10.0, p2.y-axs.y/10.0, p2.z-axs.z/10.0,
						pymol.cgo.NORMAL, -axs.x, -axs.y, -axs.z, pymol.cgo.VERTEX,  p4.x-axs.x/10.0, p4.y-axs.y/10.0, p4.z-axs.z/10.0,
					pymol.cgo.END,
				])
			if self.kind=="C3":
				axs = x.R*self.axis
				cen = x*self.cen
				p1 = projperp(axs,Vec(1,2,3)).normalized()*35.0
				p2 = RAD(axs,120.0)*p1
				p3 = RAD(axs,240.0)*p1
				p1 = cen + p1; p2 = cen + p2; p3 = cen + p3;
				CGO.extend([
					pymol.cgo.BEGIN, pymol.cgo.TRIANGLES, pymol.cgo.COLOR, col[0], col[1], col[2], pymol.cgo.ALPHA, 1,
						pymol.cgo.NORMAL, axs.x, axs.y, axs.z, pymol.cgo.VERTEX,  p1.x+axs.x/10.0, p1.y+axs.y/10.0, p1.z+axs.z/10.0, 
						pymol.cgo.NORMAL, axs.x, axs.y, axs.z, pymol.cgo.VERTEX,  p2.x+axs.x/10.0, p2.y+axs.y/10.0, p2.z+axs.z/10.0,
						pymol.cgo.NORMAL, axs.x, axs.y, axs.z, pymol.cgo.VERTEX,  p3.x+axs.x/10.0, p3.y+axs.y/10.0, p3.z+axs.z/10.0,
						 pymol.cgo.COLOR, 1-col[0], 1-col[1], 1-col[2], 
						pymol.cgo.NORMAL, -axs.x, -axs.y, -axs.z, pymol.cgo.VERTEX,  p1.x-axs.x/10.0, p1.y-axs.y/10.0, p1.z-axs.z/10.0, 
						pymol.cgo.NORMAL, -axs.x, -axs.y, -axs.z, pymol.cgo.VERTEX,  p2.x-axs.x/10.0, p2.y-axs.y/10.0, p2.z-axs.z/10.0,
						pymol.cgo.NORMAL, -axs.x, -axs.y, -axs.z, pymol.cgo.VERTEX,  p3.x-axs.x/10.0, p3.y-axs.y/10.0, p3.z-axs.z/10.0,
					pymol.cgo.END,
				])
		return CGO
	def __eq__(self,other):
		return self.kind==other.kind and self.cen==other.cen and self.axis==other.axis and self.axis2==other.axis2
	def __str__(self):
		return self.kind+" "+str(self.axis)

class SymElemPosition(object):
	"""docstring for SymElemPosition"""
	def __init__(self, symelem, xform):
		super(SymElemPosition, self).__init__()
		self.symelem = symelem
		self.xform = xform
	def __eq__(self,other):
		return self.symelem==other.symelem and self.xform==other.xform
		

class SymElemGroupManager(object):
	"""docstring for SymElemGroupManager"""
	def __init__(self):
		super(SymElemGroupManager, self).__init__()
		self.node2elems = dict()
		self.elem2nodes = dict()
	def add_symelem(self,symelem,xform,node):
		xelem = SymElemPosition(symelem,xform)
		seenit = False
		for oldelem in self.elem2nodes.keys():
			if oldelem == xelem:
				xelem = oldelem
				assert not seenit
				seenit = True
		if xelem not in self.elem2nodes.keys():
			self.elem2nodes[xelem] = list()
		self.elem2nodes[xelem].append(node)
		if node not in self.node2elems.keys():
			self.node2elems[node] = list()
		self.node2elem[node].append(xelem)

class SymTrieNode(object):
	"""docstring for SymTrieNode"""
	def __init__(self, generators, ielem, iframe, depth, position):
		super(SymTrieNode, self).__init__()
		self.generators = generators
		self.ielem = ielem
		self.iframe = iframe
		self.depth = depth
		self.children = []
		self.parent = None
		self.position = position
	def add_child(self,node):
		self.children.append(node)
	def visit(self,visitor,depth=0,xform=Xform()):
		parentxform = xform
		if self.parent:
			if not self.parent.position == parentxform:
				print "parentxform mismatch!",self.parent.position.pretty()
				print "parentxform mismatch!",parentxform.pretty()
				assert self.parent.position == parentxform
		xform = parentxform * self.generators[self.ielem].frames[self.iframe]
		visitor(self,depth=depth,xform=xform,parentxform=parentxform)
		for c in self.children:
			c.visit(visitor,depth=depth+1,xform=xform)
	def __str__(self):
		return "elem %2i frame %2i depth %2i nchild %2i" % (self.ielem,self.iframe,self.depth,len(self.children))

class SymTrieSanityCheckVisitor(object):
	"""docstring for SymTrieSanityCheckVisitor"""
	def __init__(self):
		super(SymTrieSanityCheckVisitor, self).__init__()
		self.seenit = list() #[ Xform() ]
	def __call__(self,STN,**kwargs):
		assert STN.position not in self.seenit
		self.seenit.append(STN.position)
		for c in STN.children:
			assert c.parent is STN
		if STN.parent:
			assert STN in STN.parent.children

def generate_sym_trie_recurse(generators,depth,opts,body,heads,newheads,igen):
	if depth<1: return
	print "GEN SYM TRIE","depth",depth,"igen",igen,"heads",len(heads),"newheads",len(newheads)
	newnewheads = []
	# for ielem, elem in enumerate(generators):
	ielem = igen
	elem = generators[igen]
	for iframe, frame in enumerate(elem.frames):
		if iframe is 0: continue # skip identity
		# print "FRAME",frame.pretty()
		for head, xpos in itertools.chain(newheads,heads):
			candidate = xpos * frame
			# print candidate.pretty()
			seenit = False
			for seennode, seenframe in itertools.chain(newnewheads,newheads,heads,body):
				if candidate == seenframe:
					seenit = True
					# assert ~candidate * seenframe == Xform()
					break
			if not seenit:
				newhead = SymTrieNode(generators,ielem,iframe,head.depth+1,position=candidate)
				head.add_child( newhead )
				newhead.parent = head
				newnewheads.append( (newhead,candidate) )
				# print "NEWHEAD",candidate

	newheads.extend(newnewheads)
	
	if igen+1 == len(generators):
		body.extend(heads)
		heads = newheads
		newheads = []

	# print len(newheads),igen,len(generators)
	if depth > 1:# and newheads:
		generate_sym_trie_recurse( generators, depth-1, opts, body, heads, newheads, (igen+1)%len(generators) )

def generate_sym_trie(generators,depth=10,opts=None):
	if opts is None: opts = dict()
	print "NEW SYM TRIE"
	root = SymTrieNode(generators,0,0,0,Xform())
	heads = [(root,Xform()),]
	body = list()
	newheads = list()
	generate_sym_trie_recurse(generators,depth,opts,body,heads,newheads,0)
	sanity_check = SymTrieSanityCheckVisitor()
	root.visit(sanity_check)
	return root

	

################################################################################################################
################################################################################################################
####################################### move the above to SymTrie!!! ###########################################
################################################################################################################
################################################################################################################



newpath = os.path.dirname(inspect.getfile(inspect.currentframe())) # script directory
import sys
if not newpath in sys.path: sys.path.append(newpath)
from xyzMath import Vec,Mat,Xform,RAD,projperp,Ux,Uy,Uz
from pymol_util import cgo_sphere,cgo_segment,cgo_cyl
#from SymTrie import SymElem, SymTrieNode, generate_sym_trie
import itertools, random, functools

# run /Users/sheffler/pymol/una.py; make_d3oct("test*","o33*",depth=3)
def makesym(frames0,sele="all",newobj="MAKESYM",depth=None,maxrad=9e9,n=9e9):
	v = cmd.get_view()
	cmd.delete(newobj)
	sele = "(("+sele + ") and (not TMP_makesym_*))"
	selechains = cmd.get_chains(sele)
	print selechains
	if not depth:
		frames = frames0
	else:
		frames = expand_xforms(frames0,N=depth,maxrad=maxrad)

	# order on COM transform dis
	cen = com(sele)
	frames = sorted( frames, key=lambda x: cen.distance(x*cen) )

	# make new objs
	for i,x in enumerate(frames):
		if i >= n: break
		# print i, x.pretty()
		tmpname = "TMP_makesym_%i"%i
		cmd.create(tmpname,sele)
		for j,c in enumerate(selechains):
			cmd.alter(tmpname+" and chain "+c,"chain='%s'"%ROSETTA_CHAINS[len(selechains)*i+j])
		xform(tmpname,x)
	cmd.create(newobj,"TMP_makesym_*")
	cmd.delete("TMP_makesym_*")
	cmd.set_view(v)
	util.cbc()
def makecx(sel = 'all',name="TMP",n = 5,axis=Uz):
	v = cmd.get_view()
	cmd.delete("TMP__C%i_*"%n)
	chains = ROSETTA_CHAINS
	for i in range(n): cmd.create("TMP__C%i_%i"%(n, i), sel+" and (not TMP__C%i_*)"%n)
	for i in range(n): rot("TMP__C%i_%i"%(n, i), axis, -360.0*float(i)/float(n))
	for i in range(n): cmd.alter("TMP__C%i_%i"%(n, i), "chain = '%s'"%chains[i])
	util.cbc("TMP__C*")
	# for i in range(n): cmd.alter("TMP__C%i_%i"%(n, i),"resi=str(int(resi)+%i)"%(1000*i));
	# util.cbc("TMP__C*")
	cmd.create(name,"TMP__*")
	cmd.delete("TMP__*")
	cmd.set_view(v)
	cmd.disable(sel)
	cmd.enable(name)
def makedx(sel = 'all', n = 2, name=None):
	if not name:	name = sel.replace("+","").replace(" ","")+"_D%i"%n
	cmd.delete(name)
	v = cmd.get_view()
	cmd.delete("_TMP_D%i_*"%n)
	ALLCHAIN = ROSETTA_CHAINS
	chains = cmd.get_chains(sel)
	for i in range(n):
		dsel  = "_TMP_D%i_%i"%(n,  i)
		dsel2 = "_TMP_D%i_%i"%(n,n+i)
		cmd.create(dsel , sel+" and (not _TMP_D%i_*)"%n)
		rot       (dsel , Uz, 360.0*float(i)/float(n))
		cmd.create(dsel2, dsel )
		rot       (dsel2, Ux, 180.0 )
		for ic,c in enumerate(chains):
			cmd.alter ("((%s) and chain %s )"%(dsel ,c), "chain = '%s'"%ALLCHAIN[len(chains)*(i  )+ic])
			cmd.alter ("((%s) and chain %s )"%(dsel2,c), "chain = '%s'"%ALLCHAIN[len(chains)*(i+n)+ic])
	cmd.create(name,"_TMP_D*")
	util.cbc(name)
	cmd.delete("_TMP_D*")
	cmd.set_view(v)
	cmd.disable(sel)
	cmd.enable(name)
for i in range(2,21):
		globals()['makec%i'%i] = functools.partial(makecx,n=i)
for i in range(2,21):
		globals()['maked%i'%i] = functools.partial(makedx,n=i)
def makecxauto():
	for o in cmd.get_object_list():
		n = int(re.search("_C\d+_", o).group(0)[2:-1])
		makecx(o, n)
def maketet(sel,name="TET",n=12):
	makesym( frames0=SYMTET, sele=sel, newobj=name, n=n )
def maketet3(sel,name="TET3",n=12):
	makesym( frames0=SYMTET3, sele=sel, newobj=name, n=n)
def makeoct(sel,name="OCT",n=24):
	makesym( frames0=SYMOCT, sele=sel, newobj=name, n=n )
def makeicos(sel,name="ICOS",n=60):
	makesym( frames0=SYMICS, sele=sel, newobj=name, n=n )
def make_d3oct(d3,cage,cage_trimer_chain="A", depth=4, maxrad=9e9):
	print cmd.super("(("+cage+") and (chain "+cage_trimer_chain+"))" ,"(("+d3+") and (chain B))")
	zcagecen = com(cage+" and name ca").z
	print zcagecen
	#return
	x = alignvectors(Vec(1,1,1),Vec(1,-1,0),Vec(0,0,1),Vec(1,0,0))
	# print x * Vec(1,1,1), x*Vec(1,-1,0)
	# RAD(Ux,180), RAD(Uy,120),
	G=[ RAD(Ux,180), RAD(Uz,120), RAD(x*Vec(1,0,0),90,Vec(0,0,zcagecen)), RAD(x*Vec(1,1,0),180,Vec(0,0,zcagecen)), ]
	makesym(G,sele="(("+d3+") and ((chain A+B) and name CA))",depth=depth,maxrad=maxrad)
	cmd.show("sph","MAKESYM")
	# cmd.disable("all")
	cmd.enable("MAKESYM")

def make_d4oct(d4,cage,cage_tetramer_chain="A", depth=2, maxrad=9e9):
	print cmd.super("(("+cage+") and (chain "+cage_tetramer_chain+"))" ,"(("+d4+") and (chain A))")
	zcagecen = com(cage+" and name ca").z
	print zcagecen
	#return
	x = alignvectors(Vec(1,1,1),Vec(1,0,-1),Vec(0,0,1),Vec(1,0,0))
	# print x * Vec(1,1,1), x*Vec(1,-1,0)

	s1 = SymElem( "D4", cen=Vec(0.0,0.0,0.0)) 
	s2 = SymElem( "O" , cen=Vec(0.0,0.0,zcagecen), input_xform=RAD(Uz,45) )
	G = s1.frames + s2.frames
	# RAD(Ux,180), RAD(Uy,120),
#	G=[ RAD(Ux,180), RAD(Uz,90), RAD(x*Vec(1,0,0),90,Vec(0,0,zcagecen)), RAD(x*Vec(1,1,0),180,Vec(0,0,zcagecen)), ]
	makesym(G,sele="(("+d4+") and ((chain A+B) and name CA))",depth=depth,maxrad=maxrad)
	cmd.show("sph","MAKESYM")
	# cmd.disable("all")
	cmd.enable("MAKESYM")



def make_d3tet(d3,cage,cage_trimer_chain="A", depth=4, maxrad=9e9):
	print cmd.super("(("+cage+") and (chain "+cage_trimer_chain+"))" ,"(("+d3+") and (chain A))")
	zcagecen = com(cage+" and name ca").z
	print zcagecen
	#return
	x = alignvectors(Vec(1,1,1),Vec(1,-1,0),Vec(0,0,1),Vec(1,0,0))
	# print x * Vec(1,1,1), x*Vec(1,-1,0)
	# RAD(Ux,180), RAD(Uy,120),
	G=[ RAD(Ux,180), RAD(Uz,120), RAD(x*Vec(1,0,0),180,Vec(0,0,zcagecen)), ]
	makesym(G,sele="(("+d3+") and ((chain A+B) and name CA))",depth=depth,maxrad=maxrad)
	cmd.show("sph","MAKESYM")
	# cmd.disable("all")
	cmd.enable("MAKESYM")
def print_node(node,**kwargs):
	print kwargs['depth']*"    ", node, kwargs['xform'].pretty()
def show_node(node,**kwargs):
	if node.iframe == 1:
		node.show(xform=kwargs['xform'])

class CountFrames(object):
	"""docstring for CountFrames"""
	def __init__(self):
		super(CountFrames, self).__init__()
		self.count = 0
	def __call__(self,*args,**kwkwargs):
		self.count += 1

def cgo_cyl_arrow(c1,c2,r,col=(1,1,1),col2=None,arrowlen=4.0):
	if not col2: col2 = col
	CGO = []
	c1.round0(); c2.round0()
	CGO.extend( cgo_cyl( c1, c2+randnorm()*0.0001, r=r, col=col, col2=col2 ) )
	dirn = (c2-c1).normalized()
	perp = projperp( dirn, Vec(0.2340790923,0.96794275,0.52037438472304783) ).normalized()
	arrow1 = c2 - dirn*arrowlen + perp*2.0
	arrow2 = c2 - dirn*arrowlen - perp*2.0
	CGO.extend( cgo_cyl( c2-dirn*3.0, arrow1-dirn*3.0, r=r, col=col2 ) ) # -dirn to shift to sphere surf
	CGO.extend( cgo_cyl( c2-dirn*3.0, arrow2-dirn*3.0, r=r, col=col2 ) ) # -dirn to shift to sphere surf
	return CGO

class BuildCGO(object):
	"""docstring for BuildCGO"""
	def __init__(self, nodes, maxrad=9e9, origin=Vec(0,0,0), bbox=(Vec(-9e9,-9e9,-9e9),Vec(9e9,9e9,9e9)),
				 showlinks=False, showelems=True, label="BuildCGO", arrowlen=10.0,**kwargs):
		super(BuildCGO, self).__init__()
		self.nodes = nodes
		self.CGO = cgo_sphere(Vec(0,0,0),3.0)
		self.jumps = set()
		self.maxrad = maxrad
		self.origin = origin
		self.bbox = bbox
		self.bbox[0].x, self.bbox[1].x = min(self.bbox[0].x, self.bbox[1].x), max(self.bbox[0].x, self.bbox[1].x)
		self.bbox[0].y, self.bbox[1].y = min(self.bbox[0].y, self.bbox[1].y), max(self.bbox[0].y, self.bbox[1].y)
		self.bbox[0].z, self.bbox[1].z = min(self.bbox[0].z, self.bbox[1].z), max(self.bbox[0].z, self.bbox[1].z)
		self.showlinks = showlinks
		self.showelems = showelems
		self.label = label
		self.arrowlen = arrowlen
		self.colors = list()
		self.colors = [
			(1,1,0),
			(0,1,1),
			(1,0,1),
			(0.5,0.5,0.5),
		]
		self.kwargs = kwargs
	def bounds_check(self,v):
		if self.origin.distance(v) > self.maxrad:	return False
		if not self.bbox[0].x <= v.x <= self.bbox[1].x: return False
		if not self.bbox[0].y <= v.y <= self.bbox[1].y: return False
		if not self.bbox[0].z <= v.z <= self.bbox[1].z: return False				
		return True
	def __call__(self,node,**kwargs):
		x = kwargs["xform"]

		cencen = Vec(0,0,0)
		px = kwargs["parentxform"]
		if self.nodes:
			pcen = px*self.nodes[-1]
			# pcen = px*self.nodes[0]			

		# show "nodes"
		for icen,cen in enumerate(self.nodes):
			xcen = x*cen
			if pcen:
				self.jumps.add(pcen.distance(xcen))
			if self.showlinks:
				if self.bounds_check(pcen) or self.bounds_check(xcen):
					# print "DEBUG",icen,px.pretty(),px==Xform()
					if icen != 0 or node.parent: # skip node 0 for root
						self.add_segment( pcen, xcen, icen )
			if self.bounds_check(xcen):
				self.add_sphere( x*(cen+Vec(0,0,0)), 2.0, text="%s%i"%("ABCD"[icen],node.depth), icol=icen )
				self.add_sphere( x*(cen+Vec(2,0,0)), 2.0, text="%s%i"%("ABCD"[icen],node.depth), icol=icen )
				self.add_sphere( x*(cen+Vec(0,2,0)), 2.0, text="%s%i"%("ABCD"[icen],node.depth), icol=icen )
			pcen = xcen

		# show symelems
		if self.showelems:
			for elem in node.generators:
				if self.bounds_check(x*elem.cen):
					mergeargs = dict(kwargs.items()+self.kwargs.items())
					self.add_symelem(elem,x,**mergeargs)
	def add_symelem(self,elem,x,**kwargs):
		# should add duplicate checks here
		self.CGO.extend(elem.cgo(**kwargs))
	def add_sphere(self,cen,rad,text="",icol=0):
		# should add duplicate checks here		
		cen.round0()
		if text:
			pos = [cen.x+1.0,cen.y+1.0,cen.z+1.0]
			v = cmd.get_view()
			axes = [ [v[0],v[3],v[6]], [v[1],v[4],v[7]], [v[2],v[5],v[8]]  ]
			# pymol.cgo.wire_text(self.CGO,pymol.vfont.plain,pos,text,axes)
		self.CGO.extend( cgo_sphere(cen,rad,col=self.colors[icol] ) )
	def add_segment(self,c1,c2,icol):
		# should add duplicate checks here
		if c1.distance(c2) < 1.0: return
		self.CGO.extend( cgo_cyl_arrow(c1,c2,r=0.5,col=self.colors[max(0,icol-1)], col2=self.colors[icol]) )
	def show(self,**kwargs):
		v = cmd.get_view()
		cmd.delete(self.label)
		cmd.load_cgo(self.CGO,self.label)
		cmd.set_view(v)
		# for i,c in enumerate(self.nodes):
			# showsphere(c,1.5,col=self.colors[i])
		print self.jumps

# TODO move to xyzMath
class VecDict(object):
	"""docstring for VecDict"""
	def __init__(self):
		super(VecDict, self).__init__()
		self.keys_ = list()
		self.values_ = list()
	def keys(self):
		return tuple(self.keys_)
	def values(self):
		return tuple(self.values_)
	def items(self):
		return itertools.izip(self.keys_,self.values_)
	def __getitem__(self,key):
		i = self.keys_.index(key)
		return self.values_[i]
	def __setitem__(self,key,val):
		try:
			i = self.keys_.index(key)
			self.values_[i] = val
		except ValueError:
			assert len(self.keys_) == len(self.values_)
			self.keys_.append(key)
			self.values_.append(val)

class ComponentCenterVisitor(object):
	"""docstring for ComponentCenterVisitor"""
	def __init__(self, symelems, extranodes=[], label="NODES", colors=list(),**kwargs):
		super(ComponentCenterVisitor, self).__init__()
		# if len(symelems) > 2:
		# 	raise NotImplementedError("num components > 2 not working yet... BFS fails")
		self.symelems = symelems
		CCs = [ elem.cen for elem in symelems ]
		CCs.extend(extranodes)
		self.primaryCCs = CCs
		self.label = label
		self.priCCtoCClist = VecDict()
		self.priCCtoCCframes = VecDict()
		for n in self.primaryCCs:
			assert xyz.isvec(n)
			self.priCCtoCClist[n] = [n]
			self.priCCtoCCframes[n] = VecDict()
		self.parentmap = None
		self.childmap = None		
		self.colors = colors
		self.colors.extend( ( (1,1,0), (0,1,1), (1,0,1), (0.7,0.7,0.7) ) )
	def __call__(self,sym_trie_node,xform,parentxform,**kwargs):
		assert self.priCCtoCCframes.keys() == self.priCCtoCClist.keys()
		for priCC in self.priCCtoCClist.keys():
			CC = xform * priCC
			CClist = self.priCCtoCClist[priCC]
			CCframes = self.priCCtoCCframes[priCC]
			if not CC in CClist: CClist.append(CC)
			if not CC in CCframes.keys(): CCframes[CC] = list()
			CCframes[CC].append(sym_trie_node)
	def makeCCtree(self,dhint=1.001):
		root = self.priCCtoCClist[self.primaryCCs[0]][0]
		self.parentmap = VecDict()
		self.parentmap[root] = None
		self.childmap = dict()
		visited, queue = list(), [ root ]
		lowest_d = 9e9
		while queue:
			CCparent = queue.pop(0)
			# print "NEW VERTEX",CCparent
			if CCparent in visited: continue
			assert CCparent not in visited
			visited.append(CCparent)
			closedist,closest = 9e9,list()
			for priCC,CClist in self.priCCtoCClist.items():
				for CC in CClist:
					if CC in self.parentmap.keys(): continue
					d = CC.distance(CCparent)
					if closedist - d > 0.01:
						# print "  new closedist",d
						closest,closedist = list(),d
					if abs(closedist-d) < 0.01:
						closest.append(CC)
			lowest_d = min(lowest_d,closedist)
			for v in visited: assert v not in closest
			# print "  ",CCparent,closedist,len(closest)
			if closedist > lowest_d*dhint: continue
			queue.extend( closest )
			for CC in closest:
				assert CC not in self.parentmap.keys()
				self.parentmap[CC] = CCparent
				if not CCparent in self.childmap: self.childmap[CCparent] = list()
				self.childmap[CCparent].append(CC)
	def check_jumps(self):
		if not self.parentmap: self.makeCCtree()
		jset = VecDict()
		for c,p in self.parentmap.items():
			if p:
				jset[c-p] = True
		jsetsort = VecDict()
		for k in jset.keys():
			xyz = sorted((abs(round(k.x,5)),abs(round(k.y,5)),abs(round(k.z,5))))
			# print xyz
			jsetsort[ Vec(xyz[0],xyz[1],xyz[2]) ] = True
		print "UNIQUE PERMUTED JUMPS:"
		for k in jsetsort.keys():
			print "  ",k

	def sanity_check(self):
		if not self.parentmap: self.makeCCtree()
		self.check_jumps()
		assert self.priCCtoCCframes.keys() == self.priCCtoCClist.keys()
		for priCC in self.primaryCCs: assert priCC in self.priCCtoCClist.keys()
		for priCC in self.priCCtoCClist.keys(): assert priCC in self.primaryCCs
		for priCC,CClist in self.priCCtoCClist.items():
			for i1,n1 in enumerate(CClist):
				if n1 not in self.parentmap.keys():
					print "NOT IN PARENTMAP:",n1
				for i2,n2 in enumerate(CClist):
					assert (i1==i2) == (n1==n2) # xor
		for priCC,CCframes in self.priCCtoCCframes.items():
			for CC,STNs in CCframes.items():
				for stn in STNs:
					assert stn.position*priCC == CC
	def show(self,component_pos=(Vec(3,11,9),Vec(11,3,9),Vec(11,9,3),Vec(9,3,11)),showframes=True,**kwargs):
		self.sanity_check()
		if not self.parentmap: self.makeCCtree()
		CGO = []
		for ipn,itms in enumerate(self.priCCtoCClist.items()):
			pn,CClist = itms
			for n in CClist:
				CGO.extend( cgo_sphere(n, r=2.2, col=self.colors[ipn] ) )
				if n in self.parentmap.keys() and self.parentmap[n]:
					CGO.extend( cgo_cyl_arrow( self.parentmap[n], n, r=0.8, col=self.colors[ipn] ) )
				if showframes and ipn < len(component_pos):
					for stn in self.priCCtoCCframes[pn][n]:
						cn  = stn.position*(pn+component_pos[ipn])
						cnx = stn.position*(pn+component_pos[ipn]+Vec(3,0,0))
						cny = stn.position*(pn+component_pos[ipn]+Vec(0,2,0))
						CGO.extend( cgo_sphere(cn , r=2.5, col=self.colors[ipn] ) )
						CGO.extend( cgo_sphere(cnx, r=1.7, col=self.colors[ipn] ) )
						CGO.extend( cgo_sphere(cny, r=1.2, col=self.colors[ipn] ) )
						CGO.extend( cgo_cyl_arrow(n,cn, r=0.3, col=self.colors[ipn], arrowlen=2.0 ) )
		v = cmd.get_view()
		cmd.delete(self.label)
		cmd.load_cgo(CGO,self.label)
		cmd.set_view(v)
	def make_symdef(self,**kwargs):
		XYZ_TEMPLATE = r"xyz  %-30s  %+012.9f,%+012.9f,%+012.9f  %+012.9f,%+012.9f,%+012.9f  %+014.9f,%+014.9f,%+014.9f" + "\n"
		if not self.parentmap: self.makeCCtree()
		scale = 1.0
		if "symdef_scale" in kwargs: scale = kwargs['symdef_scale']
		# for k,v in self.parentmap.items(): print "parentmap:",k,v
		node2num = VecDict()
		for ip,val in enumerate(self.priCCtoCCframes.items()):
			priCC,CCframes = val
			for icc,val2 in enumerate(CCframes.items()):
				CC,STNs = val2
				node2num[CC] = (ip,icc)
		Sxyz = ""
		edges = list()
		celldofjumps = list()
		compdofjumps = [list() for i in self.symelems]
		SUBAs = list()
		SUBs = [list() for i in self.symelems]
		for ip,val in enumerate(self.priCCtoCCframes.items()):
			if ip >= len(self.symelems): continue
			priCC,CCframes = val
			for icc,val2 in enumerate(CCframes.items()):
				Sxyz += "# virtuals for comp%i cen%i\n"%(ip,icc)
				CC,STNs = val2
				assert len(STNs) > 0
				PCC = None if not CC in self.parentmap.keys() else self.parentmap[CC]
				if  PCC: PCCName       = "CMP%02i_CEN%03i" %node2num[PCC]
				if  PCC: PCCDofBegName = PCCName+"_CELLDofBeg_%i_%i"%(icc,ip) # NOTE icc FIRST!!!!
				if  PCC: PCCDofEndName = PCCName+"_CELLDofEnd_%i_%i"%(icc,ip) # NOTE icc FIRST!!!
				if True: CCDofBegName  = "CMP%02i_CEN%03i"%(ip,icc)
				if True: CCDofEndName  = "CMP%02i_CEN%03i_CmpDofEnd"%(ip,icc)
				# if True: CCDOFName  = "CMP%02i_CEN%03i_COMPDOF" %(ip,icc)
				if  PCC: DIR  = (CC-PCC).normalized()
				if  PCC: DIR2 = projperp(DIR,Vec(1,2,3)).normalized()
				if True: ELEMDIR  = STNs[0].position.R * self.symelems[ip].axis
				if True: ELEMDIR2 = projperp(ELEMDIR,Vec(1,2,3)).normalized()
				if  PCC: Sxyz += (XYZ_TEMPLATE % ( PCCDofBegName,DIR.x,DIR.y,DIR.z, DIR2.x,DIR2.y,DIR2.z, PCC.x*scale,PCC.y*scale,PCC.z*scale ) )
				if  PCC: Sxyz += (XYZ_TEMPLATE % ( PCCDofEndName,DIR.x,DIR.y,DIR.z, DIR2.x,DIR2.y,DIR2.z,  CC.x*scale, CC.y*scale, CC.z*scale ) )
				if True: Sxyz += (XYZ_TEMPLATE % ( CCDofBegName, ELEMDIR.x,ELEMDIR.y,ELEMDIR.z, ELEMDIR2.x,ELEMDIR2.y,ELEMDIR2.z, CC.x*scale, CC.y*scale, CC.z*scale ) )
				if True: Sxyz += (XYZ_TEMPLATE % ( CCDofEndName, ELEMDIR.x,ELEMDIR.y,ELEMDIR.z, ELEMDIR2.x,ELEMDIR2.y,ELEMDIR2.z, CC.x*scale, CC.y*scale, CC.z*scale ) )
				if  PCC: edges.append( (PCCName      ,PCCDofBegName) )
				if  PCC: edges.append( (PCCDofBegName,PCCDofEndName) )
				if  PCC: edges.append( (PCCDofEndName, CCDofBegName) )				
				if True: edges.append( (CCDofBegName, CCDofEndName) )								
				# if True: edges.append( (CCDofEndName, CCDOFName) )					
				if  PCC: celldofjumps.append( (PCCDofBegName, PCCDofEndName) )
				if True: compdofjumps[ip].append( (CCDofBegName, CCDofEndName) )					
				for isub,stn in enumerate(STNs):
					SUBName = "CMP%02i_CEN%03i_SUB%03i" %(ip,icc,isub)
					if ip==0: SUBAs.append(SUBName)
					SUBs[ip].append((SUBName,stn.position))
					# edges.append( (CCDOFName , SUBName) )
					edges.append( (CCDofEndName , SUBName) )					
					# edges.append( (SUBName, "SUBUNIT %s"%("ABCDEFG"[ip]) ) )
					SX = stn.position.R * Vec(1,0,0)
					SY = stn.position.R * Vec(0,1,0)
					SO = stn.position * priCC
					Sxyz += (XYZ_TEMPLATE % ( SUBName,SX.x,SX.y,SX.z, SY.x,SY.y,SY.z, SO.x*scale, SO.y*scale, SO.z*scale ) )
				edges.append((None,None)) # spacer
				Sxyz += "\n"

		# dummy jumps, sometimes needed by dumb rosetta protocols
		Sxyz += "xyz DUMMY_VIRT 1,0,0 0,1,0 0,0,0\n\n" # for stupid reasons

		celldofjumps = sorted(celldofjumps)

		s = "symmetry_name FUBAR\n\nsubunits %i\n\nnumber_of_interfaces %i\n\n" % (len(SUBAs),len(SUBAs)-1)
		s += "E = 2*%s"%SUBAs[0]
		for suba in SUBAs[1:]:
			s += " + 1*(%s:%s)"%(SUBAs[0],suba)
		s += "\n\nanchor_residue COM\n\n"


		s += "#####################################################################################\n"
		s += "########################## Virtual Coordinate Frames ################################\n"
		s += "#####################################################################################\n\n"
		s += "virtual_coordinates_start\n\n"
		s += Sxyz
		s += "virtual_coordinates_stop\n\n"

		s += "#####################################################################################\n"
		s += "##################################### Jumps #########################################\n"
		s += "#####################################################################################\n\n"
		for p,c in edges:
			if p and c:
				s += "connect_virtual %-57s %-25s %-25s\n" % ("JUMP__%s__to__%s"%(p,c.replace(" ","")),p,c)
			else:
				s += "\n"

		s += "################# SUBUNIT Jumps ############################\n\n"
		subunit_group_map = dict()
		for SUBname,x in SUBs[0]:
			p = SUBname
			c = "SUBUNIT A"
			jname = "JUMP__%s__to__%s"%(p,c.replace(" ",""))
			s += "connect_virtual %-57s %-25s %-25s\n" % (jname,p,c)
			if not "A" in subunit_group_map: subunit_group_map["A"] = list()
			subunit_group_map["A"].append(jname)
		s += "\n"
		for icomp,subs in enumerate(SUBs):
			if icomp==0: continue
			for SUBname0,x0 in SUBs[0]:
				for SUBname,x in subs:				
					if x != x0: continue
					p = SUBname
					chain = "ABCDEFG"[icomp]
					c = "SUBUNIT " + chain
					jname = "JUMP__%s__to__%s"%(p,c.replace(" ",""))
					s += "connect_virtual %-57s %-25s %-25s %s\n" % (jname,p,c,"")# "# shares xform with primary "+SUBname0 )
					if not chain in subunit_group_map: subunit_group_map[chain] = list()
					subunit_group_map[chain].append(jname)
			s += "\n"


		s += "#####################################################################################\n"
		s += "##################################### DOFs ##########################################\n"
		s += "#####################################################################################\n\n"

		s += "########################### stupid dummy DOF ################################\n\n"
		s += "connect_virtual DUMMY_JUMP CMP00_CEN000 DUMMY_VIRT\n"
		s += "set_dof DUMMY_JUMP x\n\n"

		s += "################# CELL DOFs ############################\n\n"
		s += "set_dof   JUMP__%s__to__%s   x\n\n" % celldofjumps[0]

		s += "################# COMPONENT DOFs ############################\n\n"
		for icomp,dofs in enumerate(compdofjumps):
			if not dofs: continue
			if self.symelems[icomp].kind[0]!="C":
				s += "#NOTCYCLIC# "
			s += "set_dof   JUMP__%s__to__%s   x angle_x\n\n" % dofs[0]

		s += "#####################################################################################\n"
		s += "################################## JUMP GROUPS ######################################\n"
		s += "#####################################################################################\n\n"

		s += "################# CELL DOF JUMP GROUPS ############################\n\n"

		s += "set_jump_group   GROUP_CELLDOF"
		for p,c in celldofjumps:
			s += "   JUMP__%s__to__%s"%(p,c)
		s += "\n\n"

		s += "################# COMPONENT DOF JUMP GROUPS ############################\n\n"

		for idof,dofs in enumerate(compdofjumps):
			if not dofs: continue
			s += "set_jump_group   GROUP_COMP_%i_DOF"%idof
			for p,c in dofs:
				s += "   JUMP__%s__to__%s"%(p,c)
			s += "\n\n"

		s += "################# SUBUNIT JUMP GROUPS ############################\n\n"

		for chain,jumps in subunit_group_map.items():
			s += "set_jump_group GROUP_SUBUNT_%s"%chain
			for jump in sorted(jumps):
				s += "  %s"%jump
			s += "\n\n"

		# #################################################################################
		# # for debugging, make sure subunit jump names are in alphabetical order for Rosetta??
		# #################################################################################
		# for chain,jumps in subunit_group_map.items():
		# 	for ijump,jump in enumerate(jumps):
		# 		svname = jump.split("__")[1]
		# 		s = s.replace(svname,"S%sO%03i_%s"%(chain,ijump,svname))

		if 'generic_names' in kwargs and kwargs['generic_names']:
			# rename some jumps
			s = s.replace( "JUMP__%s__to__%s" % celldofjumps[0], "CELL_DOF" )
			for icomp,dofs in enumerate(compdofjumps):
				if not dofs: continue
				s = s.replace( "JUMP__%s__to__%s" % dofs[0], "COMP_DOF_%i"%(icomp+1) )

		return s


class RosettaSymDef(object):
	"""docstring for RosettaSymDef"""
	def __init__(self, virtuals=None, edges=None):
		super(RosettaSymDef, self).__init__()
		if not virtuals: virtuals = dict()
		if not edges: edges = dict()
		self.virtuals = virtuals
		self.edges = edges
	def add_virt(self,name,X,Y,O):
		self.virtuals[name] = (X.normalized(),Y.normalized(),O)
	def add_edge(self,name,v1name,v2name):
		self.edges[name] = (v1name,v2name)
	def parse(self,s):
		for line in s.split("\n"):
			print line
			if line.startswith("xyz"):
				dummy,name,X,Y,O = re.split(r"\s+",line.strip())
				X = X.split(",")
				X = Vec(float(X[0]),float(X[1]),float(X[2]))
				Y = Y.split(",")
				Y = Vec(float(Y[0]),float(Y[1]),float(Y[2]))
				O = O.split(",")
				O = Vec(float(O[0]),float(O[1]),float(O[2]))
				self.add_virt(name,X,Y,O)
			elif line.startswith("connect_virtual"):
				line = line.replace("SUBUNIT ","SUBUNIT")
				splt = re.split(r'\s+',line.strip())
				# print "SPLT:", splt
				dummy,name,v1name,v2name = splt[:4]
				self.add_edge(name,v1name,v2name)
	def displaycen(self,name,virt,offset=5.0):
		if   re.match(".*DofBeg.*",name): return virt[2] + offset*virt[0] # shift +X only 
		elif re.match(".*DofEnd.*",name): return virt[2] - offset*virt[0] # shift -X only
		return virt[2]+offset*virt[0]+offset*virt[1]
	def sanity_check(self):
		for name,vnames in self.edges.items():
			v1name,v2name = vnames
			v1 = self.virtuals[v1name]
			if not v2name.startswith("SUBUNIT"):
				v2 = self.virtuals[v2name]
				if v1[2].distance(v2[2]) < 0.0001:
					continue # overlapping virts, check makes no sense
				jdir = (v2[2]-v1[2]).normalized()
				v1x = v1[0].normalized()
				if jdir.distance(v1x) > 0.0001:
					print "connect_virtual ERROR", name, v1name, v2name
					print "  jdir", jdir
					print "  v1x ", v1x
					raise ValueError
	def show(self,tag="SYMDEF",XYlen=5.0,r=3.0,**kwargs):
		self.sanity_check()
		seenit = []
		CGO = []
		for name,xyo in self.virtuals.items():
			X,Y,O = xyo
			# CGO.extend( cgo_sphere(c=O,r=r) )
			cen = self.displaycen(name,xyo,offset=XYlen)
			if cen in seenit:
				print "ERROR overlapping display center", cen
				# assert not cen in seenit
			seenit.append(cen)
			CGO.extend( cgo_lineabs( cen, cen+X*XYlen, col=(1,0,0) ) )
			CGO.extend( cgo_lineabs( cen, cen+Y*XYlen, col=(0,1,0) ) )
		for name,vnames in self.edges.items():
			v1name,v2name = vnames
			v1 = self.virtuals[v1name]
			v2 = v1
			if not v2name.startswith("SUBUNIT"):
				v2 = self.virtuals[v2name]
			cen1 = self.displaycen(name,v1,offset=XYlen)
			cen2 = self.displaycen(name,v2,offset=XYlen)			
			CGO.extend( cgo_lineabs( cen1, cen2, (1,1,1) ) )
			upmid = (cen1 + 3.0*cen2)/4.0
			CGO.extend( cgo_sphere( upmid ))
			v = cmd.get_view()
			axes = [ [v[0],v[3],v[6]], [v[1],v[4],v[7]], [v[2],v[5],v[8]]  ]
			# pymol.cgo.wire_text(CGO,pymol.vfont.plain,[upmid[0],upmid[1],upmid[2]],name)

		cmd.load_cgo(CGO,tag)
		


def test_D2TET(depth=6,cell=60, **kwargs):
	G = [
		# SymElem("C2",axis=Vec( 1,0,0),cen=Vec(    0    ,cell/2.0, cell/4.0)),	
		# SymElem("C3",axis=Vec(-1,1,1),cen=Vec(-cell/6.0,cell/6.0,-cell/3.0)),
		# SymElem("C2",axis=Vec(1,1,0),cen=cell*Vec(0,0.0,0.0)),	
		# SymElem("C3",axis=Vec(-1,1,1),cen=Vec(0,0,0)),	
		# SymElem("C2",axis=Vec(0,1,0)),
		SymElem("C3",axis=Vec(1,1,1)),
		# SymElem("C2",axis=Vec(0,1,0),cen=Vec(1,1,1)*cell/2.0), # other T
		# SymElem("C3",axis=Vec(1,1,1),cen=Vec(1,1,1)*cell/2.0), # other T
		# SymElem("C4",axis=Vec(1,0,0),cen=Vec(1,1,1)*cell/2.0),
		SymElem("D2",cen=Vec(0,0,cell/2.0)),
		# SymElem("D2",cen=Vec(0,cell/2.0,cell/2.0)), # other D2
	]
	# for elem in G: print elem
	symtrie = generate_sym_trie(G,depth=depth)
	buildcgo = BuildCGO( nodes=[ ], origin=Vec(0.5,0.5,0.5)*cell, **kwargs )
	# buildcgo = BuildCGO( nodes=[ Vec(6,6,30), ] )
	symtrie.visit(buildcgo)
	buildcgo.show()
	cube( Vec(0,0,0), cell*Vec(1,1,1) )
	for g in G:
		print "show",g
		g.show(radius=2.0,sphereradius=4.0)
def test_D4OCT(depth=4):
	CELL = 30
	G = [
		# SymElem("C2",axis=Vec( 1,0,0),cen=Vec(    0    ,CELL/2.0, CELL/4.0)),	
		# SymElem("C3",axis=Vec(-1,1,1),cen=Vec(-CELL/6.0,CELL/6.0,-CELL/3.0)),
		# SymElem("C2",axis=Vec(1,1,0),cen=CELL*Vec(0,0.0,0.0)),	
		# SymElem("C3",axis=Vec(-1,1,1),cen=Vec(0,0,0)),	
		SymElem("C2",axis=Vec(1,1,0),cen=Vec(0,0,CELL)),
		SymElem("C3",axis=Vec(1,1,1),cen=Vec(0,0,CELL)),
		SymElem("C4",axis=Vec(1,0,0),cen=Vec(0,0,CELL)),		
		SymElem("C4",axis=Vec(0,0,1)),
		SymElem("C2",axis=Vec(1,0,0)),
		SymElem("C2",axis=Vec(0,1,0)),				
	]
	# for elem in G: print elem
	symtrie = generate_sym_trie(G,depth=depth)
	# buildcgo = BuildCGO( nodes=[ Vec(2,4,3), Vec(-6,-2,35), ] )
	buildcgo = BuildCGO( nodes=[ Vec(-6,-2,CELL+5), Vec(2,4,3), ] )	
	# buildcgo = BuildCGO( nodes=[ Vec(-6,-2,35), ] )	
	# buildcgo = BuildCGO( nodes=[ Vec(2,4,3), ] )
	symtrie.visit(buildcgo)
	buildcgo.show()

def test_xtal(G,cell,depth=4,mindepth=0,symdef=1,shownodes=1,**kwargs):
	v = cmd.get_view()
	CEN = [g.cen for g in G]
	FN = list()
	tag = "test" if not "tag" in kwargs else kwargs['tag']
	for d in range(mindepth,depth+1):
		symtrie = generate_sym_trie(G,depth=d)
		# buildcgo = BuildCGO( nodes=[ CEN1+Vec(2,3,4), CEN2+Vec(2,4,3), ] )	
		nodes = []
		# if "component_pos" in kwargs.keys():
			# nodes = kwargs["component_pos"][:1]
		buildcgo = BuildCGO( nodes=nodes, label=tag+"_DEPTH%i"%d,**kwargs )
		symtrie.visit(buildcgo)
		buildcgo.show()
		if shownodes:
			find_nodes = ComponentCenterVisitor(symelems=G,label=tag+"_NODES%i"%d,**kwargs)
			symtrie.visit(find_nodes)
			FN.append(find_nodes)
			if symdef:
				sdef_string = FN[-1].make_symdef(**kwargs)
				print "==================== SYMDEF (dump to "+tag+"_"+str(d)+".sym) ===================="
				print sdef_string
				print "====================================================================="
				with open(tag+"_"+str(d)+".sym","w") as out:
					out.write(sdef_string)
				if 'symdef_check' in kwargs and kwargs['symdef_check']:
					sdef = RosettaSymDef()
					sdef.parse(sdef_string)
					sdef.show("SYMDEF_"+tag)
	for fn in FN:
		fn.show(**kwargs) # dumb order hack for pymol up/dn	
	cmd.disable("all")
	cmd.enable(tag+"_DEPTH%i"%(depth))
	cmd.enable(tag+"_NODES%i"%(depth))
	count = CountFrames()
	symtrie.visit(count)
	print "N Frames:",count.count
	cmd.set_view(v)

###### WORKING ONE-COMPONENT SYMDEF FILES ######
###### WORKING ONE-COMPONENT SYMDEF FILES ######
###### WORKING ONE-COMPONENT SYMDEF FILES ######
###### WORKING ONE-COMPONENT SYMDEF FILES ######
###### WORKING ONE-COMPONENT SYMDEF FILES ######
#### TESTING - F432 - O ####
#def test_P432_O(cell=80,**kwargs): ###can't do this with only one octahedron
#	# delete all; run ~/pymol/symgen.py; test_F432_2O()
#	G = [
#			SymElem( "O", cen=cell*Vec(0,0,0), axis=Vec(1,-1,1) ),	 
#			SymElem( "O", cen=cell*(Vec(-0.5,0,0.5)-Vec(-1,1,1)*0.25), axis=Vec(-1,1,1) ),
#	     ]
#	test_xtal(G,cell,tag='test_F432_O',**kwargs)

def test_F432_OO(cell=80,**kwargs): ###can't do this with only one octahedron
	# delete all; run ~/pymol/symgen.py; test_F432_2O()
	G = [
			SymElem( "O", cen=cell*Vec(-1,-1,+0) ),	 
			SymElem( "O", cen=cell*Vec(+1,-1,+1) ),
	     ]
	test_xtal(G,cell,tag='test_F432_O',**kwargs)

def test_F432_OT(cell=80,**kwargs): ###can't do this with only one octahedron
	# delete all; run ~/pymol/symgen.py; test_F432_2O()
	G = [
			SymElem( "O",  cen=cell*Vec(0,0,0) ),	 
			SymElem( "T", cen=cell*Vec(1,1,1), axis=Vec(0,0,1), axis2=Vec(1,-1,0)  ),
	     ]
	test_xtal(G,cell,tag='test_F432_OT',**kwargs)

# def test_F432_OT(cell=80,**kwargs): ###can't do this with only one octahedron
# 	# delete all; run ~/pymol/symgen.py; test_F432_2O()
# 	G = [
# 			SymElem( "O",  cen=cell*Vec(0,0,0) ),	 
# 			SymElem( "T", cen=cell*Vec(1,1,1), axis=Vec(1,1,1), axis2=Vec(1,-1,0)  ),
# 	     ]
# 	test_xtal(G,cell,tag='test_F432_OT',**kwargs)





############################### O one component #########################

def test_F432_OD2_will(cell=80,**kwargs): ###MAKE THIS SYMDEF
	# delete all; run ~/pymol/symgen.py; test_F432_2O()
	G = [
			SymElem( "O",  cen=cell*Vec(0,0,0) ),	 
			SymElem( "D2", cen=cell*Vec(1,1,0), axis=Vec(1,1,0), axis2=Vec(0,0,1)  ),
	     ]
	test_xtal(G,cell,tag='F432_OD2_will',**kwargs)


def test_I432_OD3_will(cell=80,**kwargs): ###MAKE THIS SYMDEF
	# delete all; run ~/pymol/symgen.py; test_F432_2O()
	G = [
			SymElem( "O",  cen=cell*Vec(0,0,0) ),	 
			SymElem( "D3", cen=cell*Vec(1,1,1), axis=Vec(1,1,1), axis2=Vec(1,-1,0)  ),
	     ]
	cube(Vec(-0,-0, -0), 2*Vec(cell,cell,cell) )
	test_xtal(G,cell,tag='I432_OD3_will',**kwargs)


def test_P432_OD4_will(cell=80,**kwargs): ###MAKE THIS SYMDEF
	# delete all; run ~/pymol/symgen.py; test_F432_2O()
	G = [
			SymElem( "O",  cen=cell*Vec(0,0,0) ),	 
			SymElem( "D4", cen=cell*Vec(1,0,0), axis=Vec(1,0,0), axis2=Vec(0,1,0)  ),
	     ]
	cube(Vec(-0,-0, -0), 2*Vec(cell,cell,cell) )
	test_xtal(G,cell,tag='P432_OD4_will',**kwargs)


################################## T one component #########################

def test_F4132_TD3_will(cell=80,**kwargs): ###MAKE THIS SYMDEF
	# delete all; run ~/pymol/symgen.py; test_F432_2O()
	G = [
			SymElem( "T",  cen=cell*Vec(0,0,0) ),	 
			SymElem( "D3", cen=cell*Vec(1,1,1), axis=Vec(1,1,1), axis2=Vec(1,-1,0)  ),
	     ]
	cube( 4*Vec(-cell,-cell, 0), 4*Vec(cell,cell,2*cell) )
	test_xtal(G,cell,tag='F4132_TD3_will',**kwargs)


def test_P23_TD2_will(cell=80,**kwargs): ###MAKE THIS SYMDEF
	# delete all; run ~/pymol/symgen.py; test_F432_2O()
	G = [
			SymElem( "T",  cen=cell*Vec(0,0,0) ),	 
			SymElem( "D2", cen=cell*Vec(1,0,0), axis=Vec(1,0,0), axis2=Vec(0,1,0)  ),
	     ]
	cube(Vec(-0,-0, -0), 2*Vec(cell,cell,cell) )
	test_xtal(G,cell,tag='P23_TD2_will',**kwargs)


def test_F23_TT_will(cell=80,**kwargs): ###MAKE THIS SYMDEF
	# delete all; run ~/pymol/symgen.py; test_F432_2O()
	G = [
			SymElem( "T",  cen=cell*Vec(0,0,0) ),	 
			SymElem( "T", cen=cell*Vec(1,1,1)  ),
	     ]
	cube( 2*Vec(-cell,0, -cell), 2*Vec(cell,2*cell,cell) )
	test_xtal(G,cell,tag='F23_TT_will',**kwargs)


def test_I23_TD2_will(cell=80,**kwargs): 
	# delete all; run ~/pymol/symgen.py; test_F432_2O()
	G = [
			SymElem( "T",  cen=cell*Vec(0,0,0) ),	 
			SymElem( "T", cen=cell*Vec(1,1,0.5), input_xform=RAD(Uz,90)  ),
	     ]
	cube( 2*Vec(-cell,0, -cell), 2*Vec(cell,2*cell,cell) )
	test_xtal(G,cell,tag='I23_TD2_will',**kwargs)




#### TESTING - I432 - O ####
def test_I432_OD3(cell=120,**kwargs): ## 8 connections ##
	X = alignvectors(Vec(1,1,1),Vec(1,0,-1),Vec(0,0,1),Vec(1,0,0))	
	# G = [ SymElem( "O" , cen=cell*Vec(0.0,0.0,0.0) ),
		  # SymElem( "D3", cen=cell*Vec(0.25,0.25,0.25), axis=Vec(1,1,1), axis2=Vec(1,-1,0) ), ]
	# cube( cell*Vec(-0.5,-0.5,-0.5), cell*Vec(0.5,0.5,0.5) )
	G = [ SymElem( "D3", cen=cell*Vec(0.0,0.0,0.0) ),
		  SymElem( "O" , cen=cell*Vec(0.0,0.0,sqrt(3.0)/4.0), input_xform=X ),		]
	cube( cell*Vec(-0.25,-0.25,-0.25), cell*Vec(0.75,0.75,0.75), xform=X )
	test_xtal(G,cell,tag="test_I432_O",**kwargs)

def test_F4132_T(cell=80,**kwargs):
	G = [ SymElem( 'T', cen=cell*(Vec ( -0.5,0,0.5 )), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(0.866025,-0.5,0) 
 		),
		  SymElem( 'T', cen=cell*(Vec ( -0.25,0.25,0.75 )), axis=Vec(-0.57735,-0.57735,-0.57735), #axis2=Vec(0.866025,-0.5,0) 
 		),
 	    ]
 	test_xtal(G,cell,tag='test_F4132_T',**kwargs)

# def test_F23_T(cell=80,**kwargs):
# 	G = [ SymElem( 'T', cen=cell*(Vec ( -0.5,-0.5,0 )), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(0.866025,-0.5,0) 
#  		),
# 		  SymElem( 'T', cen=cell*(Vec ( -0.5,0,0.5 )), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(0.866025,-0.5,0) 
#  		),
#  	    ]
#  	test_xtal(G,cell,tag='test_F23_T',**kwargs)

 # def test_F23_T_T(cell=80,**kwargs):
	# # delete all; run ~/pymol/symgen.py; test_F23_T_T( depth=4, cell=100, symdef_scale=0.000001, generic_names=1 )
	# G = [ SymElem( "T", cen=cell*Vec(0,0,0), axis=Vec(1,1,1) ),	
	# 	  SymElem( "T", cen=cell*Vec(-1,1,-1)*0.25, axis=Vec(1,-1,1) ),
	#      ]
	# test_xtal(G,cell,tag='test_F23_2T',**kwargs)

def test_I23_T(cell=80,**kwargs):
	G = [ SymElem( 'T', cen=cell*(Vec ( -0.5,-0.5,0 )), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(0.866025,-0.5,0) 
 		),
		  SymElem( 'T', cen=cell*(Vec ( -0.5,0,0.5 )), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(0.866025,-0.5,0) 
 		),
 	    ]
 	test_xtal(G,cell,tag='test_F23_T',**kwargs)

###### WORKING TWO-COMPONENT SYMDEF FILES ######
###### WORKING TWO-COMPONENT SYMDEF FILES ######
###### WORKING TWO-COMPONENT SYMDEF FILES ######
###### WORKING TWO-COMPONENT SYMDEF FILES ######
###### WORKING TWO-COMPONENT SYMDEF FILES ######

## work on for Harley ##
def test_P321_C3_C3(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_P312_D3_D3(cell=100, depth=2)
	G = [ SymElem( 'C3', cen=cell*( Vec ( 0,0,0 ) ), axis=Vec(0,0,1), axis2=Vec(0.866025,0.5,0) 
		),
	      SymElem( 'C3', cen=cell*Vec(-0.333333,0.333333,-0.5), axis=Vec(0,0,1), axis2=Vec(0.866025,-0.5,0) 
	    ), ]
	test_xtal(G,cell,tag='test_P321_C3_C3',**kwargs)

## work on for Harley ##
def test_P321_C3_C3_will(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_P312_D3_D3(cell=100, depth=2)
	G = [ SymElem( 'C3', cen=cell*( Vec ( 0,0,0 ) ), axis=Vec(0,0,1), #axis2=Vec(0.866025,0.5,0) 
		),
	      SymElem( 'C2', cen=cell*Vec( 0,1,0), axis=Vec(1,0,0), #axis2=Vec(0.866025,-0.5,0) 
	      	),
	      #SymElem( 'Z', cen=cell*Vec( 0,0,2 ) ),
	    ]
	test_xtal(G,cell,tag='test_P321_C3_C3',**kwargs)

## maybe correct ###
def test_P432_C3_D4(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C3_D4(cell=100, depth=2)
	G = [  
	      SymElem( 'O', cen=cell*( Vec ( 0.5,0.5,0 ) ), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
		),

	      SymElem( 'D4', cen=cell*Vec(0,0,0), axis=Vec(0,0,1), axis2=Vec(1,0,0) 
	    ),]
	test_xtal(G,cell,tag='test_P432_C3_D4',**kwargs)

###### WORKING F4222 - D2 x D2 - SYMDEF #######
def test_P4222_D2_D2(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_P4222_D2_D2(cell=100, depth=2)
	G = [ SymElem( 'D2', cen=cell*( Vec ( 0,0,0 ) ), axis=Vec(0,0,1), axis2=Vec(1,0,0) 
		),
	      SymElem( 'D2', cen=cell*Vec(0.5, 0.5, 1.1), axis=Vec(0,0,1), axis2=Vec(1,0,0) 
	    ), ]
	test_xtal(G,cell,tag='test_P4222_D2_D2',**kwargs)
###### WORKING F4222 - D2 x D2 - SYMDEF #######

###### WORKING F222 - D2 x D2 - SYMDEF #######
def test_F222_D2_D2(cell=100,**kwargs):
#delete all ; run ~/pymolscripts/symgen.py; test_F222_D2_D2(cell=100, depth=6, symdef_scale=0.000001, generic_names=1)
	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,0.25,0.25 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), axis2=Vec(1,0,0) 
		),
	      SymElem( 'D2', cen=cell*Vec(0,0,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
	    ), ]
	test_xtal(G,cell,tag='test_F222_D2_D2',**kwargs)
###### WORKING F222 - D2 x D2 - SYMDEF #######
	
#### WORKING P6222 - D2 x D2 ####
def test_P6222_D2_D2(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_P6222_D2_D2(cell=100, depth=2)
	G = [ SymElem( 'D2', cen=cell*Vec(0,0,0), axis=Vec(0,0,1), axis2=Vec(1,0,0) 
		),
	    SymElem( 'D2', cen=cell*( Vec ( 0,-0.5,-0.166667 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), axis2=Vec(0.5,0.866025,0) 
		), ]
	test_xtal(G,cell,tag='test_P6222_D2_D2',**kwargs)
#x=alignvectors(Vec(0,0,1),Vec(1,0,0),Vec(0,0,1),Vec(0.5,0.866025,0))
#xform("vis",x)

# def test_P6222_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6222_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), axis2=Vec(0.5,0.866025,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,0.5,0.166667), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6222_D2_D2',**kwargs)
#### WORKING P6222 - D2 x D2 ####

#### WORKING P23 - D2 x T - SYMDEF ####
def test_P23_TD2A(cell=200,**kwargs):
	# delete all; run ~/pymol/symgen.py; test_P23_TD2B( depth=2, cell=200, symdef_scale=0.000001, generic_names=1 )
	G = [ SymElem( "D2", cen=cell*Vec(0.0,0.0,0.0) ),
	      SymElem( "T" , cen=cell*Vec(0.0,0.0,0.5) ),	]
	component_pos=[ Vec(-8,-7,6), Vec(-7,0,-11), ]
	test_xtal(G,cell,component_pos=component_pos,tag="P23_TD2A",**kwargs)
	cube( cell*Vec(0,0,-0.5), cell*Vec(1,1,0.5) )

def test_P23_TD2B(depth=3,cell=150,**kwargs):
	# delete all; run ~/pymol/symgen.py; test_P23_TD2B( depth=2, cell=200, symdef_scale=0.000001, generic_names=1 )
	G = [
		SymElem( "D2", cen=cell*Vec(0.0,0.0,0.0) ),
	    SymElem( "T" , cen=cell*Vec(0.0,0.5,0.5) ),
	]
	component_pos=[ Vec(3,7,6), Vec(0,-7,-11), ]
	test_xtal(G,cell,component_pos=component_pos,tag="P23_TD2B",**kwargs)
	cube( cell*Vec(0,-0.5,-0.5), cell*Vec(1,0.5,0.5) )
#### WORKING P23 - D2 x T - SYMDEF ####

#### WORKING F432 - D2 x T - SYMDEF #### looks similar to P23_TD2A
def test_F432_TD2(cell=150,**kwargs):
	# delete all; run ~/pymol/symgen.py; test_F432_TD2( depth=2, cell=200, symdef_scale=0.000001, generic_names=1 )
	G = [ SymElem( "D2", cen=cell*Vec(0.0,0.0,0.0) ), # , axis2=Vec(1,1,0) ),
	      SymElem( "T" , cen=cell*Vec(0.0,0.0,0.25), input_xform=RAD(Uz,45) ),	
	      # SymElem( "O" , cen=cell*Vec(0.5,0.5,0.0) ),	
    ]
	component_pos=[ Vec(2,4,8), Vec(2,5,-12), Vec(4,6,8) ]
	test_xtal(G,cell,component_pos=component_pos,tag="F432_TD2",**kwargs)
	cube( cell*Vec(-0.5,-0.5,-0.25), cell*Vec(0.5,0.5,0.75), xform=RAD(Uz,45) )
#### WORKING F432 - D2 x T - SYMDEF ####

#### WORKING - F4132 - D3 x T ####
def test_F4132_TD3(cell=200,**kwargs):
	#G = [ SymElem( "T" , cen=cell*Vec(0.0,0.0,0.0) ),
	#SymElem( "D3", cen=cell*Vec(0.25,0.25,0.25), axis=Vec(1,1,1), axis2=Vec(1,-1,0) ), ]
	#cube( cell*Vec(-0.5,-0.5,-0.5), cell*Vec(0.5,0.5,0.5) )
	X = alignvectors(Vec(1,1,1),Vec(1,0,-1),Vec(0,0,1),Vec(1,0,0))
	G = [ SymElem( "D3", cen=cell*Vec(0.0,0.0,0.0), axis=Vec(0,0,1), axis2=Vec(1,0,0) ),
		  SymElem( "T" , cen=cell*Vec(0.0,0.0,sqrt(3.0)/8.0), input_xform=X ),]
	cube( cell*Vec(-0.5,-0.5,-0.5), cell*Vec(0.5,0.5,0.5), xform=X )
	test_xtal(G,cell,tag="F4132_TD3",**kwargs)
#### WORKING - F4132 - D3 x T ####

#### WORKING - I432 - D3 x O ####
def test_I432_OD3(cell=120,**kwargs): ## 8 connections ##
	X = alignvectors(Vec(1,1,1),Vec(1,0,-1),Vec(0,0,1),Vec(1,0,0))	
	# G = [ SymElem( "O" , cen=cell*Vec(0.0,0.0,0.0) ),
		  # SymElem( "D3", cen=cell*Vec(0.25,0.25,0.25), axis=Vec(1,1,1), axis2=Vec(1,-1,0) ), ]
	# cube( cell*Vec(-0.5,-0.5,-0.5), cell*Vec(0.5,0.5,0.5) )
	G = [ SymElem( "D3", cen=cell*Vec(0.0,0.0,0.0) ),
		  SymElem( "O" , cen=cell*Vec(0.0,0.0,sqrt(3.0)/4.0), input_xform=X ),		]
	cube( cell*Vec(-0.25,-0.25,-0.25), cell*Vec(0.75,0.75,0.75), xform=X )
	test_xtal(G,cell,tag="test_I432_OD3",**kwargs)
#### WORKING - I432 - D3 x O ####




#### TESTING - I432 - O ####
def test_I432_O(cell=120,**kwargs): ## 8 connections ##
	X = alignvectors(Vec(1,1,1),Vec(1,0,-1),Vec(0,0,1),Vec(1,0,0))	
	# G = [ SymElem( "O" , cen=cell*Vec(0.0,0.0,0.0) ),
		  # SymElem( "D3", cen=cell*Vec(0.25,0.25,0.25), axis=Vec(1,1,1), axis2=Vec(1,-1,0) ), ]
	# cube( cell*Vec(-0.5,-0.5,-0.5), cell*Vec(0.5,0.5,0.5) )
	G = [ SymElem( "D3", cen=cell*Vec(0.0,0.0,0.0) ),
		  SymElem( "O" , cen=cell*Vec(0.0,0.0,sqrt(3.0)/4.0), input_xform=X ),		]
	cube( cell*Vec(-0.25,-0.25,-0.25), cell*Vec(0.75,0.75,0.75), xform=X )
	test_xtal(G,cell,tag="test_I432_O",**kwargs)
#### TESTING - I432 - D3 x O ####
#I432	O	0.57735,0.57735,0.57735	-	0,0,0	0.57735,0.57735,0.57735	-	0.5,0.5,0.5	0	1.92E-16	0.866025
#I432	O	0.57735,0.57735,0.57735	-	0,0,0	-0.57735,0.57735,0.57735	-	0.5,0.5,0.5	70.5288	0	0

#### TESTING - F432 - O ####
# def test_F432_O(cell=80,**kwargs): ###can't do this with only one octahedron
# 	# delete all; run ~/pymol/symgen.py; test_F432_2O()
# 	G = [
# 			SymElem( "O", cen=cell*Vec(0,0,0), axis=Vec(1,-1,1) ),	 
# 			SymElem( "O", cen=cell*(Vec(-0.5,0,0.5)-Vec(-1,1,1)*0.25), axis=Vec(-1,1,1) ),
# 	     ]
# 	test_xtal(G,cell,tag='test_F432_O',**kwargs)
#### TESTING - F432 - O ####
#F432	O	-0.57735,0.57735,0.57735	-	0.5,0.5,0	0.57735,-0.57735,0.57735	-	0,0.5,0.5	70.5288	0.353553	0
#F432	O	-0.57735,0.57735,0.57735	-	0.5,0.5,0	-0.57735,0.57735,0.57735	-	0.5,1,0.5	0	0.408248	0.57735
#F432	O	-0.57735,0.57735,0.57735	-	0.5,0.5,0	0.57735,-0.57735,0.57735	-	0,1,1	70.5288	0	0

#### EXMAPLE - F23 - T x T ####
# def test_F23_T_T(cell=80,**kwargs):
# 	# delete all; run ~/pymol/symgen.py; test_F23_T_T( depth=4, cell=100, symdef_scale=0.000001, generic_names=1 )
# 	G = [ SymElem( "T", cen=cell*Vec(0,0,0), axis=Vec(1,1,1) ),	
# 		  SymElem( "T", cen=cell*Vec(-1,1,-1)*0.25, axis=Vec(1,-1,1) ),
# 	     ]
# 	test_xtal(G,cell,tag='test_F23_2T',**kwargs)
#### EXAMPLE - F23 - T x T ####






#### WORKING - P432 - D4 x O ####
def test_P432_OD4(cell=80,**kwargs):
	G = [ SymElem( "D4", cen=cell*Vec(0.0,0.0,0.0),  ),
	      SymElem( "O" , cen=cell*Vec(0.0,0.0,0.5),  ),	]
	test_xtal(G,cell,tag="P432_OD4",**kwargs)
#### WORKING - P432 - D4 x O ####

#### WORKING??? - I432 - D2 x O - doublecheck ####
def test_I432_D2_O(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_O(cell=100, depth=2)
	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0.25,0 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), axis2=Vec(0.707107,0,0.707107) 
		),
	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
	    ), ]
	test_xtal(G,cell,tag='test_I432_D2_O',**kwargs)
#### WORKING??? - I432 - D2 x O - doublecheck ####

#### WORKING - F23 - T x T ####
def test_F23_T_T(cell=80,**kwargs):
	# delete all; run ~/pymol/symgen.py; test_F23_T_T( depth=4, cell=100, symdef_scale=0.000001, generic_names=1 )
	G = [ SymElem( "T", cen=cell*Vec(0,0,0), axis=Vec(1,1,1) ),	
		  SymElem( "T", cen=cell*Vec(-1,1,-1)*0.25, axis=Vec(1,-1,1) ),
	     ]
	test_xtal(G,cell,tag='test_F23_2T',**kwargs)
#### WORKING - F23 - T x T ####

#### WORKING - F432 - O x O ####
def test_F432_O_O(cell=80,**kwargs): ###can't do this with only one octahedron
	# delete all; run ~/pymol/symgen.py; test_F432_2O()
	G = [
			SymElem( "O", cen=cell*Vec(0,0,0), axis=Vec(1,-1,1) ),	 
			SymElem( "O", cen=cell*(Vec(-0.5,0,0.5)-Vec(-1,1,1)*0.25), axis=Vec(-1,1,1) ),
	     ]
	test_xtal(G,cell,tag='test_F432_2O',**kwargs)
#### WORKING - F432 - O x O ####

#### WORKING - P432 - O x O ####
def test_P432_O_O(cell=80,**kwargs):
	# delete all; run ~/pymol/symgen.py; test_myst_O_O()
	G = [ SymElem( "O", cen=cell*Vec(0  ,0,0), axis=Vec(1,1,1) ),
	      SymElem( "O", cen=cell*Vec(0.5,0,0)                   , axis=Vec(1,1,1) ),	
	     ]
	test_xtal(G,cell,tag='test_P432_2O',**kwargs)
#### WORKING - P432 - O x O ####

#### WORKING !!!! -- seems to work ###
def test_P4132_C2_C3(cell=80,**kwargs):
	# delete all; run ~/pymol/symgen.py; test_P4( depth=4, cell=100, symdef_scale=0.000001, generic_names=1 )
	G = [ SymElem( "C2", cen=cell*(Vec(0.375,-0.125,0.375)), axis=Vec(1,1,1) ),
	      SymElem( "C3", cen=cell*Vec(0.0,0.0,0.0), axis=Vec(0,0,1) ),	
	     ]
	test_xtal(G,cell,tag='test_P4132_C2_C3',**kwargs)
#### WORKING !!!! ###

### WORKING !!! --doublecheck ###
def test_P6222_C2_D2(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_P6222_C2_D2(cell=100, depth=2)
	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,-0.5,-0.333333 ) - Vec ( 0.866025,0.5,0 ) *0.5 ), axis=Vec(0.866025,0.5,0), #axis2=Vec(-,-,-) 
		),
	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.5,-0.166667), axis=Vec(0,0,1), #axis2=Vec(,,) 
	    ), ]
	test_xtal(G,cell,tag='test_P6222_C2_D2',**kwargs)
### WORKING !!! ###

### WORKING !!!!-- I think this works ###
def test_I432_C2_C4(cell=200,**kwargs):
	# delete all; run ~/pymol/symgen.py; test_P4( depth=4, cell=100, symdef_scale=0.000001, generic_names=1 )
	G = [ SymElem( "C4", cen=cell*(Vec(0,0,0)-Vec(0,0,1)*0.75), axis=Vec(0,0,1) ),
		  SymElem( "C2", cen=cell*(Vec(-0.25,-0.25,-0.25)-Vec(-1,0.0,1)*0.25), axis=Vec(-1,0.0,1) ),
	     ]
	test_xtal(G,cell,tag='test_I432_24',**kwargs)
### WORKING !!!! ###

### WORKING !!!! --doublecheck ###
def test_I432_C2_D2(cell=100,**kwargs):
	# delete all; run ~/pymol/symgen.py; test_P4( depth=4, cell=100, symdef_scale=0.000001, generic_names=1 )
	G = [ SymElem( "C2", cen=cell*(Vec(-0.25,-0.25,-0.25)-Vec(0,-1,1)*0.5), axis=Vec(0,-1,1) ),
	      SymElem( "D2", cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), axis2=Vec(1,0,1) ),	
	     ]
	test_xtal(G,cell,tag='test_I432_2D2',**kwargs)
### WORKING !!!! ###

### WORKING --doublecheck ###
def test_I432_D3_D4(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D4(cell=100, depth=2)
	G = [ SymElem( 'D3', cen=cell*( Vec ( 0,0,0 )), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.57735,0.57735,0.57735) 
		),
	      SymElem( 'D4', cen=cell*Vec(-0.25,-0.75,-0.25), axis=Vec(0,0,1), #axis2=Vec(,,) 
	    ), ]
	test_xtal(G,cell,tag='test_I432_D3_D4',**kwargs)


###### IN PROGRESS SYMDEF FILES ######
###### IN PROGRESS SYMDEF FILES ######
###### IN PROGRESS SYMDEF FILES ######
###### IN PROGRESS SYMDEF FILES ######
###### IN PROGRESS SYMDEF FILES ######




# def test_P23_TD2A(cell=200,**kwargs):
# 	# delete all; run ~/pymol/symgen.py; test_P23_TD2B( depth=2, cell=200, symdef_scale=0.000001, generic_names=1 )
# 	G = [ SymElem( "D2", cen=cell*Vec(0.0,0.0,0.0) ),
# 	      SymElem( "T" , cen=cell*Vec(0.0,0.0,0.5) ),	]
# 	component_pos=[ Vec(-8,-7,6), Vec(-7,0,-11), ]
# 	test_xtal(G,cell,component_pos=component_pos,tag="P23_TD2A",**kwargs)
# 	cube( cell*Vec(0,0,-0.5), cell*Vec(1,1,0.5) )





# def test_F432_OTD2(depth=3,cell=80,**kwargs):
# 	# delete all; run /Users/sheffler/pymol/symgen.py; test_P23(depth=1,mindepth=1)
# 	# ODT 96
# 	# TDO 96
# 	G = [ 
# 	      SymElem( "O" , cen=cell*Vec(0.5,0.5,0.0) ),	
# 		  SymElem( "D2", cen=cell*Vec(0.0,0.0,0.0), axis2=Vec(1,1,0) ),
# 	      SymElem( "T" , cen=cell*Vec(0.0,0.0,-0.5) ),	
# 	    ]
# 	component_pos=[ Vec(2,4,8), Vec(2,5,-12), Vec(4,6,8) ]
# 	extranodes = [ cell*Vec(0.0,0.5,0.0)]
# 	test_xtal(G,cell,component_pos=component_pos,tag="F432_TD2",extranodes=extranodes,**kwargs)
# 	cube( cell*Vec(-1,-1,-0.5), cell*Vec(1,1,1.5) )

# def test_I432_OD4(cell=80,**kwargs):
# 	# delete all; run /Users/sheffler/pymol/symgen.py; test_F432_OD4( depth=3, cell=200, symdef_scale=0.000001, generic_names=1 )
# 	# G = [ SymElem( "D2", cen=cell*Vec(0.0,0.0,0.0), axis2=Vec(1,1,0) ),
# 	#       # SymElem( "T" , cen=cell*Vec(0.0,0.0,-0.5) ),	
# 	#       SymElem( "O" , cen=cell*Vec(0.5,0.5,0.0) ),	
# 	#     ]
# 	G = [ SymElem( "D4", cen=cell*Vec(0.0,0.0,0.0)) , 
# 	      # SymElem( "T" , cen=cell*Vec(0.0,0.0,-0.5) ),	
# 	      SymElem( "O" , cen=cell*Vec(0.0,0.0,0.5), input_xform=RAD(Uz,45) ),	
# 	    ]
# 	component_pos=[ Vec(2,4,8), Vec(2,5,-12), Vec(4,6,8) ]
# 	test_xtal(G,cell,component_pos=component_pos,tag="I432_OD4",**kwargs)
# 	cube( cell*Vec(-1,-1,-0.5), cell*Vec(1,1,1.5) )


# def test_P4(cell=80,**kwargs):
# 	# delete all; run ~/pymol/symgen.py; test_P4( depth=4, cell=100, symdef_scale=0.000001, generic_names=1 )
# 	G = [ SymElem( "C4", cen=cell*Vec(0.0,0.0,0.0) ),
# 	      SymElem( "C2", cen=cell*Vec(0.5,0.0,0.0) ),	
# 	     ]
# 	test_xtal(G,cell,tag='test_P4_42',**kwargs)
# 	G = [ SymElem( "C4", cen=cell*Vec(0.0,0.0,0.0) ),
# 	      SymElem( "C4", cen=cell*Vec(0.5,0.0,0.0) ),	# moved lattice WRP C2!!!!!
# 	     ]
# 	test_xtal(G,cell,tag='test_P4_44',**kwargs)

## NOT WORKING ####
def test_I213_C2_C3(cell=100,**kwargs):
# 	# delete all; run ~/pymol/symgen.py; test_P4( depth=4, cell=100, symdef_scale=0.000001, generic_names=1 )
 	G = [ SymElem( "C2", cen=cell*(Vec(0.0,-0.25,0.0)-Vec(0,0,1)*0.5), axis=Vec(0,0,1) ),
	      SymElem( "C3", cen=cell*Vec(0.1667,-0.1667,0.3333), axis=Vec(-1,1,1) ),	
 	     ]
 	test_xtal(G,cell,tag='test_I213_23',**kwargs)

 # def test_P4132_C2_C3(cell=80,**kwargs):
 # 	# delete all; run ~/pymol/symgen.py; test_P4( depth=4, cell=100, symdef_scale=0.000001, generic_names=1 )
 # 	G = [ SymElem( "C2", cen=cell*(Vec(-0.125,-0.125,-0.125)-Vec(0,-1,1)*0.25), axis=Vec(0,-1,1) ),
 # 	      SymElem( "C3", cen=cell*Vec(-0.5,0.0,-0.5), axis=Vec(-1,-1,1) ),	
 # 	     ]
 # 	test_xtal(G,cell,tag='test_P4132_C2_C3',**kwargs)

# def test_P4132_C2_C3(cell=80,**kwargs): ## ORIGINAL
# 	# delete all; run ~/pymol/symgen.py; test_P4( depth=4, cell=100, symdef_scale=0.000001, generic_names=1 )
# 	G = [ SymElem( "C2", cen=cell*(Vec(0.375,-0.125,0.375)-Vec(0,-1,1)*0.5), axis=Vec(0,-1,1) ),
# 	      SymElem( "C3", cen=cell*Vec(0.0,0.0,0.0), axis=Vec(-1,-1,1) ),	
# 	     ]
# 	test_xtal(G,cell,tag='test_P4132_C2_C3',**kwargs)







def test_P4332_C2_C3(cell=100,**kwargs):
	# delete all; run ~/pymol/symgen.py; test_P4( depth=4, cell=100, symdef_scale=0.000001, generic_names=1 )
	G = [ SymElem( "C2", cen=cell*(Vec(-0.375,0.125,0.125)-Vec(0,-1,1)*0), axis=Vec(0,-1,1) ),
	      SymElem( "C3", cen=cell*Vec(0.333,0.16667,-0.16667), axis=Vec(1,-1,1) ),	
	     ]
	test_xtal(G,cell,tag='test_P4332_23',**kwargs)

#### ORIGINAL #### works to depth=6 #####
# def test_F23_C2_T(cell=100,**kwargs): 
# 	# delete all; run ~/pymol/symgen.py; test_P4( depth=4, cell=100, symdef_scale=0.000001, generic_names=1 )
# 	G = [ SymElem( "C2", cen=cell*(Vec(0.25,-0.25,0.0)-Vec(0,0,1)*0.5), axis=Vec(0,0,1) ),
# 	      SymElem( "T", cen=cell*Vec(0.0,-0.5,-0.5), axis=Vec(-1,1,1) ),	
# 	     ]
# 	test_xtal(G,cell,tag='test_F23_C2_T',**kwargs)

#### THIS WORKS WITH T AS COMP 1 ####
# def test_F23_C2_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen.py; test_F23_C2_T(cell=100, depth=2)
# 	G = [ SymElem( 'T', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), 
# 	      SymElem( 'C2', cen=cell*( Vec ( 0.25,-0.25,0 ) - Vec ( 0,0,1 ) *0.5), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      ]
# 	test_xtal(G,cell,tag='test_F23_C2_T',**kwargs)

#### T IS CENTERED, C2 IS MOVED, NEED TO ROTATE by 45/2 ####
def test_F23_C2_T(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen.py; test_F23_C2_T(cell=100, depth=2)
	G = [ SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(-1,1,1), #axis2=Vec(,,) 
	    ), 
	      SymElem( 'C2', cen=cell*( Vec ( 0.25,0.25,0 )), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
		),
	      ]
	test_xtal(G,cell,tag='test_F23_C2_T',**kwargs)

#### T IS CENTERED, C2 IS MOVED, NEED TO ROTATE by 45/2-- TESTING ####
# def test_F23_C2_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen.py; test_F23_C2_T(cell=100, depth=2)
# 	G = [ SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), 
# 	      SymElem( 'C2', cen=cell*( Vec ( 0.25,0.25,0 )), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      ]
# 	test_xtal(G,cell,tag='test_F23_C2_T',**kwargs)

# def test_F23_C2_T(cell=100,**kwargs):
# 	# delete all; run ~/pymol/symgen.py; test_F23_C2_T( depth=2, cell=100, symdef_scale=0.000001, generic_names=1 )
# 	G = [ SymElem( "T", cen=cell*Vec(0.0,0.0,0.0), axis=Vec(-1,1,1) ),	
# 	      SymElem( "C2", cen=cell*(Vec(0.25,-0.2,0.5)-Vec(0,0,1)*0.5), axis=Vec(0,0,1) ),
# 	     ]
# 	test_xtal(G,cell,tag='test_F23_C2_T',**kwargs)

def test_F4132_C2_T(cell=100,**kwargs):
	# delete all; run ~/pymol/symgen.py; test_P4( depth=4, cell=100, symdef_scale=0.000001, generic_names=1 )
	G = [ SymElem( "C2", cen=cell*(Vec(-0.375,0.125,-0.125)-Vec(0,1,1)*0.75), axis=Vec(0,1,1) ),
	      SymElem( "T", cen=cell*Vec(-0.5,0,-0.5), axis=Vec(1,-1,1) ),	
	     ]
	test_xtal(G,cell,tag='test_F4132_C2_T',**kwargs)







# def test_P432_C4_C4(cell=80,**kwargs):
# 	# delete all; run ~/pymol/symgen.py; test_P4( depth=4, cell=100, symdef_scale=0.000001, generic_names=1 )
# 	G = [ SymElem( "C4", cen=cell*Vec(0.0,0.0,0.3) ),
# 	      SymElem( "C4", cen=cell*Vec(-0.5,0.0,0.5), axis=Vec(0,1,0) ),	
# 	     ]
# 	test_xtal(G,cell,tag='test_P432_44',**kwargs)

# def test_P432_C4_C4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C4_C4(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,0,0 ) -  Vec (0,0,1) * 0.5 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'C4', cen=cell*Vec(-0.5,0,0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C4_C4',**kwargs)


def test_P432_C4_C4(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C4_C4(cell=100, depth=2)
	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,0,0 )  ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
		),
	      SymElem( 'C4', cen=cell*Vec(0.5,0.5,0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
	    ),
	      SymElem( 'C3', cen=cell*Vec( 0,0,0 ), axis=Vec(1,1,1), #axis2=Vec(,,) 
	    ), ]
	component_pos=[ Vec(1,1,50), Vec(1,50,1), Vec ( 0,0,0 )]

	test_xtal(G,cell,tag='test_P432_C4_C4',component_pos=component_pos,**kwargs)


def test_F432_C3_D2(cell=80,**kwargs):
	# delete all; run ~/pymol/symgen.py; test_P4( depth=4, cell=100, symdef_scale=0.000001, generic_names=1 )
	G = [ SymElem( "C3", cen=cell*(Vec(0.0,-0.5,0.5)-Vec(-1,1,1)*0.15), axis=Vec(-1,1,1) ),
	      SymElem( "D2", cen=cell*Vec(0.25,-0.5,0.25), axis=Vec(1,0,1), axis2=Vec(0,1,0)),	
	     ]
	test_xtal(G,cell,tag='test_F432_3D2',**kwargs)

# def test_P213_C3_C3_1(cell=80,**kwargs): ## NOT P213 ... why isn't this P213??
# 	# delete all; run ~/pymol/symgen.py; test_P4( depth=4, cell=100, symdef_scale=0.000001, generic_names=1 )
# 	G = [ SymElem( "C3", cen=cell*Vec(-0.333,-0.1667,0.333), axis =Vec(1,-1,1) ),
# 	      SymElem( "C3", cen=cell*(Vec(-0.1667,0.1667,-0.333)-Vec(-1,1,1)*0.1), axis=Vec(-1,1,1) ),	
# 	     ]
# 	test_xtal(G,cell,tag='test_P213_33',**kwargs)

# def test_P213_C3_C3_2(cell=80,**kwargs):
# 	# delete all; run ~/pymol/symgen.py; test_P4( depth=4, cell=100, symdef_scale=0.000001, generic_names=1 )
# 	G = [ SymElem( "C3", cen=cell*Vec(0,0,0), axis =Vec(1,-1,1) ),
# 	      SymElem( "C3", cen=cell*(Vec(0.1663,0.3334,-0.666)-Vec(-1,1,1)*0.1), axis=Vec(-1,1,1) ),	
# 	     ]
# 	test_xtal(G,cell,tag='test_P213_33',**kwargs)

# def test_P213_C3_C3_real(cell=80,**kwargs):
# 	# delete all; run ~/pymol/symgen.py; test_P4( depth=4, cell=100, symdef_scale=0.000001, generic_names=1 )
# 	G = [ SymElem( "C3", cen=cell*Vec(0,0,0), axis=Vec(-1,1,2) ),
# 	      SymElem( "C3", cen=cell*(Vec(0,0.5,0)), axis=Vec(1,-1,2 ) ),	
# 	     ]
# 	test_xtal(G,cell,tag='test_P213_33',**kwargs)


#### MIGHT BE CORRECT ####
def test_P213_C3_C3_start(cell=80,**kwargs):
	# delete all; run ~/pymol/symgen.py; test_P4( depth=4, cell=100, symdef_scale=0.000001, generic_names=1 )
	G = [ SymElem( "C3", cen=cell*Vec(0,0,0), axis=Vec(-1,1,2) ),
	      SymElem( "C3", cen=cell*(Vec(0,0.5,0)), axis=Vec(1,-1,2 ) ),	
	     ]
	test_xtal(G,cell,tag='test_P213_33',**kwargs)
#### MIGHT BE CORRECT ####

#### With Will ####
def test_P213_C3_C3_will(cell=80,**kwargs):
	# delete all; run ~/pymol/symgen.py; test_P4( depth=4, cell=100, symdef_scale=0.000001, generic_names=1 )
	G = [ SymElem( "C3", cen=cell*Vec(0,0,0), axis=Vec(-1,1,2) ),
	      SymElem( "C3", cen=cell*(Vec(0,0.5,0)), axis=Vec(1,-1,2 ) ),	
	     ]
	test_xtal(G,cell,tag='test_P213_33',**kwargs)



def test_I4132(cell=100,**kwargs):
	# delete all; test_I4132(depth=7,shownodes=0,cell=200,maxrad=180); run /Users/sheffler/pymol/misc/G222.py; gyroid(200,r=180)
	G = [ 
		SymElem( "D3", cen=cell*Vec(0.625,0.625,0.625), axis=Vec(1,1,1), axis2=Vec(1,-1,0), col=(0,1,0) ),
		SymElem( "D2", cen=cell*Vec(0.625,0.500,0.750), axis=Vec(1,0,0), axis2=Vec(0,-1,1), col=(0,1,1) ),
		SymElem( "D3", cen=cell*Vec(0.375,0.375,0.375), axis=Vec(1,1,1), axis2=Vec(1,-1,0), col=(1,0,0) ),
		SymElem( "D2", cen=cell*Vec(0.375,0.500,0.250), axis=Vec(1,0,0), axis2=Vec(0,-1,1), col=(1,1,0) ),
	# 	SymElem( "D3", cen=cell*Vec(0.125,0.125,0.125), axis=Vec(1,1,1), axis2=Vec(1,-1,0), col=(0,1,0) ),
	# 	SymElem( "D2", cen=cell*Vec(0.125,0.000,0.250), axis=Vec(1,0,0), axis2=Vec(0,-1,1), col=(0,1,1) ),
	# 	SymElem( "D3", cen=cell*Vec(-0.125,-0.125,-0.125), axis=Vec(1,1,1), axis2=Vec(1,-1,0), col=(1,0,0) ),
	# 	SymElem( "D2", cen=cell*Vec(-0.125,0.000,-0.250), axis=Vec(1,0,0), axis2=Vec(0,-1,1), col=(1,1,0) ),
	# 	SymElem( "C3", axis=Vec(1,1,1) ),
	# 	SymElem( "C2", axis=Vec(1,1,0), cen=cell*Vec(-1, 1, 1)/8.0 ),
	# 	SymElem( "C2", axis=Vec(1,1,0), cen=cell*Vec( 1,-1,-1)/8.0, col=(1,1,0) ),
	]
	component_pos=[ Vec(-8,-7,6), Vec(-7,0,-11), ]
	test_xtal(G,cell,component_pos=component_pos,tag="I4132",origin=cell*Vec(0.5,0.5,0.5),showshape=0,**kwargs)
	# cube( cell*Vec(-0.5,-0.5,-0.5), cell*Vec(0.5,0.5,0.5) )
	cube( cell*Vec(0,0,0), cell*Vec(1,1,1) )


def test_I213(depth=16,cell=100,maxrad=9e9):
	#C3 and C2 at angle = 54.7356 offset = 0.176777
	#     C3 axis=[-0.57735,0.57735,0.57735]  origin=[-0.166667,0.166667,-0.333333]
	#     C2 axis=[1,0,0]  origin=[0,0.5,0.25]
	# AXS = [ Vec(-1,1,1),
	#         Vec( 1,0,0) ]
	# CEN = [ cell * Vec(-1,1,-2)/6.0 ,
	#         cell * Vec(0,0.5,0.25) ]
	AXS = [ Vec(1,1,1),
			Vec(1,0,0) ]
	CEN = [ cell * Vec(0,0,0) ,
			cell * Vec(0,0,0.25) ]
	G = [
		SymElem( "C3", axis=AXS[0], cen=CEN[0] ),
		SymElem( "C2", axis=AXS[1], cen=CEN[1] )
	]
	symtrie = generate_sym_trie(G,depth=depth)
	# buildcgo = BuildCGO( nodes=[ CEN1+Vec(2,3,4), CEN2+Vec(2,4,3), ] )	
	nodes = [
		CEN[0]+projperp(AXS[0],randnorm())*8.0,
		CEN[1]+projperp(AXS[1],randnorm())*8.0
		]
	buildcgo = BuildCGO( nodes=nodes, maxrad=maxrad, origin=cell*Vec(0.5,0.5,0.5), showlinks=True )		
	symtrie.visit(buildcgo)
	buildcgo.show()
	cube( Vec(0,0,0), cell*Vec(1,1,1) )
	for g in G:
		print "show",g
		g.show(radius=2.0,sphereradius=4.0)
	return AXS,CEN

def test_P213(depth=8,cell=50,maxrad=100):
	#C3 and C3 at angle = 70.5288 offset = 0.353553
	    #C3 axis=[-0.57735,-0.57735,0.57735]  origin=[-0.5,0,-0.5]
	    #C3 axis=[ 0.57735,-0.57735,0.57735]  origin=[-0.333333,-0.166667,0.166667]
	AXS = [ Vec( 1, 1, 1),
			Vec( 1, 1,-1) ]
	CEN = [ cell * Vec(0,0,0),
			cell * Vec(0.5,0,0.0) ]
	AXS = [ Vec(-1,-1, 1),
	        Vec( 1,-1, 1) ]
	CEN = [ cell * Vec(-0.5,0,-0.5),
	        cell * Vec(-1./3,-1./6, 1./6) ]
	G = [
		SymElem( "C3", axis=AXS[0], cen=CEN[0] ),
		SymElem( "C3", axis=AXS[1], cen=CEN[1] ),
	]
	symtrie = generate_sym_trie(G,depth=depth)
	#buildcgo = BuildCGO( nodes=[ CEN1+Vec(2,3,4), CEN2+Vec(2,4,3), ] )	
	cencell = cell/2.0 * Vec(1,1,1)
	buildcgo = BuildCGO( nodes=[ CEN[1]+randnorm()*5.0, CEN[0]+randnorm()*8.0 ], origin=cencell, maxrad=maxrad, showlinks=False, showelems=True )		
	symtrie.visit(buildcgo)
	buildcgo.show()

	cube( Vec(0,0,0), cell*Vec(1,1,1) )
	for g in G:
		print "show",g
		g.show(radius=2.0,sphereradius=4.0)
	return AXS,CEN

# def test_P4132(depth=8,cell=50,maxrad=80):
# 	#**** P4132 ****
# 	#C2 and C3 at angle = 35.2644 offset = 0.176777
# 	#     C2 axis=[-0.707107,0.707107,0]  origin=[-0.125,-0.125,-0.125]
# 	#     C3 axis=[0.57735,-0.57735,0.57735]  origin=[0,-0.5,-0.5]
# 	AXS = [ Vec( 1, 1, 0) ,
# 		   Vec(  1, 1, 1) ]
# 	CEN = [ cell * ( Vec(1,1,1)/8.0 - Vec(0,4,4)/8.0 ),
# 			cell * Vec(0,0,0)  ]
# 	# AXS = [ Vec(-1, 1, 0) ,
# 	#         Vec( 1, 1, 1) ]
# 	# CEN = [ cell * Vec(1,1,1)/-8.0,
# 	#         cell * Vec(0,0,0) ]
# 	G = [
# 		SymElem( "C2", axis=AXS[0], cen=CEN[0] ),
# 		SymElem( "C3", axis=AXS[1], cen=CEN[1] ),
# 	]
# 	symtrie = generate_sym_trie(G,depth=depth)
# 	# buildcgo = BuildCGO( nodes=[ CEN1+Vec(2,3,4), CEN2+Vec(2,4,3), ] )	
# 	cencell = cell/2.0 * Vec(1,1,1)
# 	buildcgo = BuildCGO( nodes=[ CEN[1]+randnorm()*5.0, CEN[0]+randnorm()*8.0 ], origin=cencell, maxrad=maxrad, showlinks=False, showelems=True )		
# 	symtrie.visit(buildcgo)
# 	buildcgo.show()

# 	cube( Vec(0,0,0), cell*Vec(1,1,1) )
# 	for g in G:
# 		print "show",g
# 		g.show(radius=2.0,sphereradius=4.0)
# 	return AXS,CEN
# def test_F432(depth=6,cell=100,maxrad=90):
# 	#C3 and D2 at angle = 35.2644 offset = 0
# 	#     C3 axis=[0.57735,0.57735,0.57735]  origin=[0,0,0]
# 	#     D2 axis=[1,0,0]  axis2=[0,-0.707107,0.707107]  origin=[0,0.25,0.25]
# 	AXS = [ Vec(1,1,1),
# 			Vec(1,0,0) ]
# 	CEN = [ cell * Vec(0,0,0) ,
# 			cell * Vec(0,0.25,0.25) ]
# 	G = [
# 		SymElem( "C2", axis=Vec(1,1,0), cen=Vec(0,0,0) ),
# 		SymElem( "C3", axis=AXS[0], cen=CEN[0] ),
# 		SymElem( "C4", axis=Vec(1,0,0), cen=Vec(0,0,0) ),
# 		SymElem( "D2", axis=AXS[1], axis2=Vec(0,-1,1), cen=CEN[1] )
# 	]
# 	symtrie = generate_sym_trie(G,depth=depth)
# 	# buildcgo = BuildCGO( nodes=[ CEN1+Vec(2,3,4), CEN2+Vec(2,4,3), ] )	
# 	nodes = [
# 		CEN[0]+projperp(AXS[0],randnorm())*8.0,
# 		CEN[1]+projperp(AXS[1],randnorm())*8.0
# 		]
# 	buildcgo = BuildCGO( nodes=nodes, maxrad=maxrad, origin=cell*Vec(0.5,0.5,0.5), showlinks=False )		
# 	symtrie.visit(buildcgo)
# 	buildcgo.show()
# 	cube( Vec(0,0,0), cell*Vec(1,1,1) )
# 	for g in G:
# 		print "show",g
# 		g.show(radius=2.0,sphereradius=4.0)
# 	return AXS,CEN
def test_quasi( depth=8, cell=20.0, maxrad=9e9 ):
	G = [ 
		SymElem( "C2", axis=Vec(1,0,0) ),
		SymElem( "C2", axis=Vec(0,1,0) ),
		SymElem( "C2", axis=Vec(0,0,1) ),
		SymElem( "C3", axis=Vec(+1,+1,+1) ),
		SymElem( "C3", axis=Vec(+1,-1,-1) ),
		SymElem( "C3", axis=Vec(-1,+1,-1) ),
		SymElem( "C3", axis=Vec(-1,-1,+1) ),
		SymElem( "C2", axis=Vec(2,-1,-1), cen=cell*Vec(1,1,1) ),
	]
	nodes = [ ]
	symtrie = generate_sym_trie(G,depth=depth)
	symtrie.visit(print_node)
	print symtrie
	buildcgo = BuildCGO( nodes=nodes, maxrad=maxrad, origin=cell*Vec(0.5,0.5,0.5), showlinks=False, showelems=True )		
	symtrie.visit(buildcgo)
	buildcgo.show()
def test_I432( depth=6, cell=50, **kwargs ):
	#**** I432 ****
	#C2 and D3 at angle = 35.2644 offset = 0.353553
	#     C2 axis=[-0.707107,0.707107,0]  origin=[0.25,0.25,0.25]
	#     D3 axis=[-0.57735,0.57735,0.57735]  axis2=[0.707107,0.707107,0]  origin=[0,0,0]
	G = [
		SymElem( "C2", axis=Vec(-1,1,0), cen=Vec(1,1,1)/4.0*cell ),
		SymElem( "D3", axis=Vec(-1,1,1), axis2=Vec(1,1,0) )
	]
	symtrie = generate_sym_trie(G,depth=depth)
	# buildcgo = BuildCGO( nodes=[ CEN1+Vec(2,3,4), CEN2+Vec(2,4,3), ] )	
	nodes = []
	buildcgo = BuildCGO( nodes=nodes, origin=cell*Vec(0.5,0.5,0.5), showlinks=False, **kwargs )		
	symtrie.visit(buildcgo)
	buildcgo.show()
	cube( Vec(0,0,0), cell*Vec(1,1,1) )
	for g in G:
		print "show",g
		g.show(radius=2.0,sphereradius=4.0)
def test_icos( depth=3, cell=30, **kwargs ):
	# dodec
	# (+-1, +-1, +-1)
	# (0, +-1/p, +-p)
	# (+-1/p, +-p, 0)
	# (+-p, 0, +-1/p)
	# icos
	# (0, +-1, +-p)
	# (+-1, +-p, 0)
	# (+-p, 0, +-1)
	p = (1.0+sqrt(5.0))/2.0
	q = 1.0/p
	v33a = ( Vec(1,1,1).normalized() - Vec(q,p,0).normalized() ).normalized()
	v33b = ( Vec(1,1,1).normalized() - Vec(p,0,q).normalized() ).normalized()
	v33c = ( Vec(1,1,1).normalized() - Vec(0,q,p).normalized() ).normalized()
	icsang = angle_degrees( Vec(1,1,1),V0, v33a )
	tetang = 180.0-math.acos(-1.0/3.0)*180.0/math.pi
	print icsang, tetang
	delta_deg = icsang-tetang
	v33a = RAD(v33a.cross(Vec(1,1,1)),delta_deg) * v33a
	v33b = RAD(v33b.cross(Vec(1,1,1)),delta_deg) * v33b
	v33c = RAD(v33c.cross(Vec(1,1,1)),delta_deg) * v33c
	print angle_degrees(Vec(1,1,1),V0,v33a)
	print angle_degrees(Vec(1,1,1),V0,v33b)
	print angle_degrees(Vec(1,1,1),V0,v33c)
	G = [
		# icos 3folds
		SymElem("C3",Vec(+1,+1,+1)),
		SymElem("C3",Vec(+1,+1,-1)),
		SymElem("C3",Vec(+1,-1,+1)),
		SymElem("C3",Vec(-1,+1,+1)),
		SymElem("C3",Vec( 0,+q,+p)),
		SymElem("C3",Vec( 0,+q,-p)),
		SymElem("C3",Vec(+q,+p, 0)),
		SymElem("C3",Vec(+q,-p, 0)),
		SymElem("C3",Vec(+p, 0,+q)),
		SymElem("C3",Vec(-p, 0,+q)),
		SymElem("C5",Vec( 0,+p, 1)),
		SymElem("C5",Vec( 0,-p, 1)),
		SymElem("C5",Vec(+p, 1, 0)),
		SymElem("C5",Vec(-p, 1, 0)),
		SymElem("C5",Vec( 1, 0, +p)),
		SymElem("C5",Vec( 1, 0, -p)),
		# tet
		SymElem("C3",Vec(1,1,1),cen=cell*Vec(1,1,1)),
		SymElem("C3",v33a,cen=cell*Vec(1,1,1)),
		SymElem("C3",v33b,cen=cell*Vec(1,1,1)),
		SymElem("C3",v33c,cen=cell*Vec(1,1,1)),
		SymElem("C2",v33a+v33b,cen=cell*Vec(1,1,1)),
		SymElem("C2",v33b+v33c,cen=cell*Vec(1,1,1)),
		SymElem("C2",v33c+v33a,cen=cell*Vec(1,1,1)),

	]
	symtrie = generate_sym_trie(G,depth=depth)
	# symtrie.visit(print_node)
	nodes = [ ]
	buildcgo = BuildCGO( nodes=nodes, origin=cell*Vec(0.5,0.5,0.5), showelems=True, **kwargs )		
	symtrie.visit(buildcgo)
	buildcgo.show()

########### Una's parsed xtals_from_point commands ####################

######### EXAMPLE ############
# def test_spacegroup_type_type(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_spacegroup_type_type(cell=100, depth=2)
# 	G = [ SymElem( 'type', cen=cell*( Vec ( origin,origin,origin ) - Vec ( axis_1,axis_1,axis_1 ) *0.5 ), axis=Vec(axis_1,axis_1,axis_1), #axis2=Vec(axis_2 (D only),axis_2 (D only),axis_2 (D only)) 
# 		),
# 	      SymElem( 'type', cen=cell*Vec(origin,origin,origin), axis=Vec(axis_1,axis_1,axis_1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_spacegroup_type_type',**kwargs)
######### END EXAMPLE ###########




# def test_F222_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen.py; test_F222_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,0.25,0.25 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,0,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F222_D2_D2',**kwargs)
	

# def test_F23_C2_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen.py; test_F23_C2_T(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0.25,-0.25,0 ) - Vec ( 0,0,1 ) *0.5), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F23_C2_T',**kwargs)
	

# def test_F23_C2_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F23_C2_T(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0.25,-0.25,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F23_C2_T',**kwargs)
	

# def test_F23_C3_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen.py; test_F23_C3_T(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0.166667,-0.166667,0.333333 ) - Vec ( -0.57735,0.57735,0.57735 ) *0 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F23_C3_T',**kwargs)
	

# def test_F23_C3_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F23_C3_T(cell=100, depth=2)
# 	G = [ SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,)
# 		),
	      
# 	      SymElem( 'C3', cen=cell*( Vec ( 0.166667,-0.166667,0.333333 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.25 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F23_C3_T',**kwargs)
	

# def test_F23_C3_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F23_C3_T(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0.166667,-0.166667,0.333333 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F23_C3_T',**kwargs)
	

def test_F23_C3_T(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_F23_C3_T(cell=100, depth=2)
	G = [ SymElem( 'C3', cen=cell*( Vec ( 0.333333,-0.166667,-0.166667 ) - Vec ( 0.57735,0.57735,0.57735 ) *0 ), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
		),
	      SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
	    ), ]
	test_xtal(G,cell,tag='test_F23_C3_T',**kwargs)
	

# def test_F23_C3_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F23_C3_T(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F23_C3_T',**kwargs)
	

# def test_F23_C3_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F23_C3_T(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0.166667,0.333333,0.166667 ) - Vec ( 0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F23_C3_T',**kwargs)
	

# def test_F23_C3_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F23_C3_T(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.5,0,0.5 ) - Vec ( 0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F23_C3_T',**kwargs)
	

# def test_F23_D2_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen.py; test_F23_D2_T(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.25,0.25 ) - Vec ( 0,0,1 ) *0.25 ), axis=Vec(0,0,1), #axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F23_D2_T',**kwargs)
	

# def test_F23_D2_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F23_D2_T(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.25,0.25 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F23_D2_T',**kwargs)
	

# def test_F23_T_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F23_T_D2(cell=100, depth=2)
# 	G = [ SymElem( 'T', cen=cell*( Vec ( 0,-0.5,-0.5 ) - Vec ( 0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.25,-0.25,-0.25), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F23_T_D2',**kwargs)
	

# def test_F23_T_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F23_T_D2(cell=100, depth=2)
# 	G = [ SymElem( 'T', cen=cell*( Vec ( 0,-0.5,-0.5 ) - Vec ( 0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.25,-0.25,-0.25), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F23_T_D2',**kwargs)
	

# def test_F23_T_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F23_T_T(cell=100, depth=2)
# 	G = [ SymElem( 'T', cen=cell*( Vec ( 0,-0.5,-0.5 ) - Vec ( 0.57735,-0.57735,0.57735 ) *0.25 ), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F23_T_T',**kwargs)
	

# def test_F23_T_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F23_T_T(cell=100, depth=2)
# 	G = [ SymElem( 'T', cen=cell*( Vec ( 0,-0.5,-0.5 ) - Vec ( 0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F23_T_T',**kwargs)
	

# def test_F23_T_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen.py; test_F23_T_T(cell=100, depth=2)
# 	G = [ SymElem( 'T', cen=cell*( Vec ( -0.5,0,-0.5 ) - (Vec ( -0.57735,0.57735,0.57735 ) *0) ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F23_T_T',**kwargs)
	

# def test_F4132_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,0.25,-0.25 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.375,0.125,-0.375), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0,0,1) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_C2_D3',**kwargs)


##### in progress #####
def test_F4132_C2_D3(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_C2_D3(cell=100, depth=2)
	G = [ SymElem( 'D3', cen=cell*Vec( 0.5 , 0.5 , 0 ), axis=Vec( -0.707107,0.707107,0 ), axis2=Vec( 0, 0, 1  ) 
	    ),
	    SymElem( 'C2', cen=cell*( Vec ( 0,0,0 )  ), axis=Vec( 0, 0 , 1 ), #axis2=Vec(-,-,-) 
		), ]
	test_xtal(G,cell,tag='test_F4132_C2_D3',**kwargs)
##### in progress #####	

# def test_F4132_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,0.25,-0.25 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.125,0.375,-0.375), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_C2_D3',**kwargs)
	

def test_F4132_C2_T(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_C2_T(cell=100, depth=2)
	G = [ SymElem( 'C2', cen=cell*( Vec ( 0.375,0.125,-0.125 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(-,-,-) 
		),
	      SymElem( 'T', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(,,) 
	    ), ]
	test_xtal(G,cell,tag='test_F4132_C2_T',**kwargs)
	

# def test_F4132_C2_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_C2_T(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0.375,0.125,-0.125 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_C2_T',**kwargs)
	

# def test_F4132_C2_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_C2_T(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0.375,-0.375,0.375 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_C2_T',**kwargs)
	

# def test_F4132_C2_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_C2_T(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.375,-0.375,-0.375 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_C2_T',**kwargs)
	

# def test_F4132_C2_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_C2_T(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0.375,-0.125,0.125 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_C2_T',**kwargs)
	

# def test_F4132_C2_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_C2_T(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0.375,0.375,-0.375 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_C2_T',**kwargs)
	

# def test_F4132_C2_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_C2_T(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0.375,0.375,-0.375 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_C2_T',**kwargs)
	

# def test_F4132_C2_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_C2_T(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0.125,0.375,0.375 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_C2_T',**kwargs)
	

# def test_F4132_C2_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_C2_T(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0.375,0.125,0.375 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_C2_T',**kwargs)
	

# def test_F4132_C3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_C3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0.166667,0.333333,-0.166667 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.125,0.375,0.125), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_C3_D3',**kwargs)
	

# def test_F4132_C3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_C3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0.166667,0.333333,-0.166667 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,-0.125,-0.375), axis=Vec(0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_C3_D3',**kwargs)
	

# def test_F4132_C3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_C3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.5,0.5,0 ) - Vec ( -0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,-0.125,0.375), axis=Vec(0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_C3_D3',**kwargs)
	

def test_F4132_D2_D3(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_D2_D3(cell=100, depth=2)
	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.25,0.25 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), axis2=Vec(0,1,0) 
		),
	      SymElem( 'D3', cen=cell*Vec(0.125,0.125,0.125), axis=Vec(-1,0,1),
	    ), ]
	test_xtal(G,cell,tag='test_F4132_D2_D3',**kwargs)
	

# def test_F4132_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,0.375,0.125), axis=Vec(1,0,1) #,axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_D2_D3',**kwargs)
	

# def test_F4132_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.125,-0.125,0.125), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_D2_D3',**kwargs)
	

# def test_F4132_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,0.375,0.125), axis=Vec(0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_D2_D3',**kwargs)
	

# def test_F4132_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.125,-0.125,0.125), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_D2_D3',**kwargs)
	

# def test_F4132_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.375,-0.125,0.375 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.25,-0.25,-0.25), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_D3_D2',**kwargs)
	

# def test_F4132_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.375,-0.125,0.375 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_D3_D2',**kwargs)
	

# def test_F4132_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.375,-0.125,0.375 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.125,-0.375,0.375), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_D3_D3',**kwargs)
	

# def test_F4132_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.375,-0.125,0.375 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,-0.375,0.125), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_D3_D3',**kwargs)
	

# def test_F4132_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.375,-0.125,0.375 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.375,-0.375,0.125), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_D3_D3',**kwargs)
	

# def test_F4132_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.125,0.375,-0.125 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,0.125,-0.125), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_D3_D3',**kwargs)
	

# def test_F4132_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.375,-0.375,0.375 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,0.125,0.125), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_D3_D3',**kwargs)
	

# def test_F4132_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.125,-0.375,-0.125 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,0.375,0.125), axis=Vec(0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_D3_D3',**kwargs)
	

# def test_F4132_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.125,-0.375,-0.125 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,0.125,0.125), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_D3_D3',**kwargs)
	

# def test_F4132_D3_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_D3_T(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*(Vec(-0.375,-0.125,0.375)-Vec(1,0,1)*0.5), axis=Vec(1,0,1), axis2=Vec(-1,1,1) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(-1,1,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_D3_T',**kwargs)
	

# def test_F4132_D3_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_D3_T(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.375,-0.125,0.375 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_D3_T',**kwargs)
	

# def test_F4132_D3_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_D3_T(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.125,0.375,-0.125 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_D3_T',**kwargs)
	

# def test_F4132_D3_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_D3_T(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.375,0.375,-0.125 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_D3_T',**kwargs)
	

# def test_F4132_D3_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_D3_T(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.375,0.375,-0.125 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_D3_T',**kwargs)
	

# def test_F4132_D3_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_D3_T(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.375,-0.375,0.375 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_D3_T',**kwargs)
	

# def test_F4132_D3_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_D3_T(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.375,0.375,-0.375 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_D3_T',**kwargs)
	

# def test_F4132_T_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_T_D3(cell=100, depth=2)
# 	G = [ SymElem( 'T', cen=cell*( Vec ( -0.5,0,-0.5 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,-0.125,-0.125), axis=Vec(0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_T_D3',**kwargs)
	

# def test_F4132_T_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_T_D3(cell=100, depth=2)
# 	G = [ SymElem( 'T', cen=cell*( Vec ( -0.5,0,-0.5 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.125,0.375,0.125), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_T_D3',**kwargs)
	

# def test_F4132_T_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F4132_T_D3(cell=100, depth=2)
# 	G = [ SymElem( 'T', cen=cell*( Vec ( 0,-0.5,-0.5 ) - Vec ( 0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,0.125,-0.125), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F4132_T_D3',**kwargs)
	

def test_F432_C2_O(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C2_O(cell=100, depth=2)
	G = [ SymElem( 'C2', cen=cell*( Vec ( 0.25,0,0.25 ) - Vec ( -0.707107,0,0.707107 ) *0 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(-,-,-) 
		),
	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
	    ), ]
	test_xtal(G,cell,tag='test_F432_C2_O',**kwargs)
	

# def test_F432_C2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C2_O(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.5,-0.25,0.25 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C2_O',**kwargs)
	

# def test_F432_C2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C2_O(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0.25,0.25,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C2_O',**kwargs)
	

# def test_F432_C2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C2_O(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0.25,0.25,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C2_O',**kwargs)
	

# def test_F432_C2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C2_O(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.25,-0.25,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C2_O',**kwargs)
	

# def test_F432_C2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C2_O(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.25,-0.5,0.25 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C2_O',**kwargs)
	

# def test_F432_C2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C2_O(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.5,0,0.5 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C2_O',**kwargs)
	

# def test_F432_C3_C4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C3_C4(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0,-0.5,0.5 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'C4', cen=cell*Vec(0,0,0), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C3_C4',**kwargs)
	

# def test_F432_C3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0,-0.5,0.5 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,0.5), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C3_D2',**kwargs)
	

# def test_F432_C3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0,-0.5,0.5 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,0.25,0.25), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C3_D2',**kwargs)
	

# def test_F432_C3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0,-0.5,0.5 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0.25,-0.5,0.25), axis=Vec(0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C3_D2',**kwargs)
	

# def test_F432_C3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0,-0.5,0.5 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.25,0.75), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C3_D2',**kwargs)
	

# def test_F432_C3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.333333,-0.333333,0.666667 ) - Vec ( 0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.25,-0.25), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C3_D2',**kwargs)
	

# def test_F432_C3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0,-0.5,0.5 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,-0.5,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C3_D3',**kwargs)
	

# def test_F432_C3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0,-0.5,0.5 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C3_D3',**kwargs)
	

# def test_F432_C3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.666667,-0.333333,-0.333333 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,-0.5,0.5), axis=Vec(0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C3_D3',**kwargs)
	

# def test_F432_C3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0,-0.5,0.5 ) - Vec ( 0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C3_D3',**kwargs)
	

# def test_F432_C3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.5,0.5,0 ) - Vec ( 0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,0,0.5), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C3_D3',**kwargs)
	

# def test_F432_C3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0,-0.5,0.5 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,0), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C3_D4',**kwargs)
	

# def test_F432_C3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0,-0.5,0.5 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,0,0.5), axis=Vec(0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C3_D4',**kwargs)
	

# def test_F432_C3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0.166667,0.333333,0.166667 ) - Vec ( 0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C3_D4',**kwargs)
	

def test_F432_C3_O(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C3_O(cell=100, depth=2)
	G = [ SymElem( 'C3', cen=cell*( Vec ( 0,-0.5,0.5 ) - Vec ( -0.57735,0.57735,0.57735 ) *0 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
		),
	      SymElem( 'O', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(,,) 
	    ), ]
	test_xtal(G,cell,tag='test_F432_C3_O',**kwargs)
	

# def test_F432_C3_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C3_O(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0,-0.5,0.5 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C3_O',**kwargs)
	

# def test_F432_C3_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C3_O(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.666667,-0.333333,-0.333333 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C3_O',**kwargs)
	

# def test_F432_C3_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C3_O(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.666667,-0.333333,-0.333333 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C3_O',**kwargs)
	

# def test_F432_C3_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C3_O(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0.166667,0.333333,0.166667 ) - Vec ( 0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C3_O',**kwargs)
	

# def test_F432_C3_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C3_O(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0.166667,0.333333,0.166667 ) - Vec ( 0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C3_O',**kwargs)
	

# def test_F432_C3_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C3_O(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0.166667,0.333333,0.166667 ) - Vec ( 0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C3_O',**kwargs)
	

# def test_F432_C4_C3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C4_C3(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,-0.5,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'C3', cen=cell*Vec(-0.166667,0.166667,-0.333333), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C4_C3',**kwargs)
	

# def test_F432_C4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,-0.5,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.75,-0.25), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C4_D2',**kwargs)
	

# def test_F432_C4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,-0.5,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.25,-0.25), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C4_D2',**kwargs)
	

# def test_F432_C4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,-0.5,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.25,-0.5,-0.25), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C4_D2',**kwargs)
	

# def test_F432_C4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,-0.5,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C4_D3',**kwargs)
	

# def test_F432_C4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,-0.5,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,0.5,0), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C4_D3',**kwargs)
	

# def test_F432_C4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,-0.5,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,-0.5,-0.5), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_C4_D3',**kwargs)
	

def test_F432_C4_O(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_C4_O(cell=100, depth=2)
	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,-0.5,0 ) - Vec ( 0,0,1 ) *0 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
		),
	      SymElem( 'O', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(,,) 
	    ), ]
	test_xtal(G,cell,tag='test_F432_C4_O',**kwargs)
	

# def test_F432_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0.25,-0.25 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(0,-0.707107,0.707107) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,0.5,-0.5), axis=Vec(0.707107,0.707107,0), axis2=Vec(0,0,1)
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D2',**kwargs)

def test_F222_D2_D2(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_F222_D2_D2(cell=100, depth=2)
	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,0.25,0.25 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(1,0,0) 
		),
	      SymElem( 'D2', cen=cell*Vec(0,0,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
	    ), ]
	test_xtal(G,cell,tag='test_F222_D2_D2',**kwargs)
	

# def test_F432_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0.25,-0.25 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*( Vec ( 0 , 0.5 , -0.5 )), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D2',**kwargs)
	

# def test_F432_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0.25,-0.25 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0.5,-0.5), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D2',**kwargs)
	

# def test_F432_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.75,-0.25,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.5,-0.5), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D2',**kwargs)
	

# def test_F432_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.25,-0.25 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.5,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D2',**kwargs)
	

def test_F432_D2_D2(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D2(cell=100, depth=2)
	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.25,0.25 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(1,0,0) 
		),
	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), axis2=Vec(0,0,1) 
	    ), ]
	test_xtal(G,cell,tag='test_F432_D2_D2',**kwargs)
	

# def test_F432_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( 0,-0.25,0.75 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(0,-0.707107,0.707107) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0.5,0,0), axis=Vec(0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D2',**kwargs)
	

# def test_F432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0.25,-0.25 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(0,-0.707107,0.707107) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D3',**kwargs)
	

# def test_F432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0.25,-0.25 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D3',**kwargs)
	

# def test_F432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -1,0,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,-0.5,0.5), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D3',**kwargs)
	

# def test_F432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -1,0,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D3',**kwargs)
	

# def test_F432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.75,-0.25,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D3',**kwargs)
	

# def test_F432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,0,-0.25 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(0.707107,0,0.707107) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D3',**kwargs)
	

# def test_F432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.25,-0.25 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,0.5,0), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D3',**kwargs)
	

# def test_F432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.25,-0.25 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D3',**kwargs)
	

# def test_F432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.25,-0.25 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,0,0), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D3',**kwargs)
	

# def test_F432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.25,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,0,0), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D3',**kwargs)
	

# def test_F432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.75,-0.25,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D3',**kwargs)
	

# def test_F432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,0.5 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(0,-0.707107,0.707107) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,-0.5), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D3',**kwargs)
	

# def test_F432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(0.707107,0,0.707107) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,-0.5), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D3',**kwargs)
	

# def test_F432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.25,0.75 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(0,-0.707107,0.707107) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,-0.5), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D3',**kwargs)
	

# def test_F432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0.25,-0.25 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(0,-0.707107,0.707107) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,0,0), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D4',**kwargs)
	

# def test_F432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0.25,-0.25 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,0,0), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D4',**kwargs)
	

# def test_F432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.25,-0.25 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,0,0.5), axis=Vec(0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D4',**kwargs)
	

# def test_F432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.5,0.25 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(-0.707107,0,0.707107) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_D4',**kwargs)
	

# def test_F432_D2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_O(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0.25,-0.25 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), axis2=Vec(0,-0.707107,0.707107) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_O',**kwargs)
	

# def test_F432_D2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_O(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0.25,-0.25 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_O',**kwargs)
	

# def test_F432_D2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_O(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.25,-0.25 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_O',**kwargs)
	

# def test_F432_D2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_O(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( 0.25,0.25,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_O',**kwargs)
	

# def test_F432_D2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_O(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.75,0,0.25 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), axis2=Vec(0.707107,0,0.707107) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_O',**kwargs)
	

# def test_F432_D2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_O(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,0,-0.25 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), axis2=Vec(0.707107,0,0.707107) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_O',**kwargs)
	

# def test_F432_D2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_O(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0.25,0.25 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_O',**kwargs)
	

# def test_F432_D2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_O(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_O',**kwargs)
	

# def test_F432_D2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D2_O(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,0,0.25 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), axis2=Vec(0.707107,0,0.707107) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D2_O',**kwargs)
	

# def test_F432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,0,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.75,-0.5,-0.25), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_D2',**kwargs)
	

# def test_F432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,0,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-1,-0.5,0), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_D2',**kwargs)
	

# def test_F432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,0,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.25,-0.25), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_D2',**kwargs)
	

# def test_F432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,0,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.75,-0.25,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_D2',**kwargs)
	

# def test_F432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,0,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.25,0.25,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_D2',**kwargs)
	

# def test_F432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,0,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.25,0.25,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_D2',**kwargs)
	

# def test_F432_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,0,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,-0.5,0), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_D3',**kwargs)
	

# def test_F432_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,0,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_D3',**kwargs)
	

# def test_F432_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,0,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_D3',**kwargs)
	

# def test_F432_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,0,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_D3',**kwargs)
	

# def test_F432_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_D3',**kwargs)
	

# def test_F432_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,-0.5,0.5), axis=Vec(0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_D3',**kwargs)
	

# def test_F432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,0,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,0), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_D4',**kwargs)
	

# def test_F432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,0,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_D4',**kwargs)
	

# def test_F432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,0,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,0), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_D4',**kwargs)
	

# def test_F432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,0,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_D4',**kwargs)
	

# def test_F432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_D4',**kwargs)
	

# def test_F432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_D4',**kwargs)
	

# def test_F432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,0,0.5 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_D4',**kwargs)
	

# def test_F432_D3_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_O(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,0,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_O',**kwargs)
	

# def test_F432_D3_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_O(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,0,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_O',**kwargs)
	

# def test_F432_D3_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_O(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_O',**kwargs)
	

# def test_F432_D3_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_O(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,0,0.5 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_O',**kwargs)
	

# def test_F432_D3_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_O(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,0,0.5 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_O',**kwargs)
	

# def test_F432_D3_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_O(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,0,-0.5 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_O',**kwargs)
	

# def test_F432_D3_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D3_O(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,0.5,0 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D3_O',**kwargs)
	

# def test_F432_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0,-1,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.25,0.25,-0.5), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D4_D2',**kwargs)
	

# def test_F432_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0,-1,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.25,0.25,-0.5), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D4_D2',**kwargs)
	

# def test_F432_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,0,0.5 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.25,0.25,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D4_D2',**kwargs)
	

# def test_F432_D4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,0,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D4_D3',**kwargs)
	

# def test_F432_D4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,0,0.5), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D4_D3',**kwargs)
	

# def test_F432_D4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,-0.5,0 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D4_D3',**kwargs)
	

# def test_F432_D4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-1,0,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,0,0), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D4_D3',**kwargs)
	

# def test_F432_D4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,0.5,0), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D4_D3',**kwargs)
	

# def test_F432_D4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,0,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,-1) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D4_D3',**kwargs)
	

# def test_F432_D4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,0.5 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D4_D3',**kwargs)
	

# def test_F432_D4_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D4_O(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0,-1,0) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D4_O',**kwargs)
	

# def test_F432_D4_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_D4_O(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_D4_O',**kwargs)
	

# def test_F432_O_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_O_D2(cell=100, depth=2)
# 	G = [ SymElem( 'O', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0.25,0.25,0), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_O_D2',**kwargs)
	

# def test_F432_O_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_O_D2(cell=100, depth=2)
# 	G = [ SymElem( 'O', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0.25,0.25,0), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_O_D2',**kwargs)
	

# def test_F432_O_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_O_D2(cell=100, depth=2)
# 	G = [ SymElem( 'O', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,0.25,0.25), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_O_D2',**kwargs)
	

# def test_F432_O_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_O_D2(cell=100, depth=2)
# 	G = [ SymElem( 'O', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.25,-0.25,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_O_D2',**kwargs)
	

# def test_F432_O_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_O_D2(cell=100, depth=2)
# 	G = [ SymElem( 'O', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.25,-0.25,-0.5), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_O_D2',**kwargs)
	

# def test_F432_O_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_O_D3(cell=100, depth=2)
# 	G = [ SymElem( 'O', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,0,0), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_O_D3',**kwargs)
	

# def test_F432_O_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_O_D3(cell=100, depth=2)
# 	G = [ SymElem( 'O', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_O_D3',**kwargs)
	

# def test_F432_O_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_O_D3(cell=100, depth=2)
# 	G = [ SymElem( 'O', cen=cell*( Vec ( 0,-0.5,-0.5 ) - Vec ( 0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,-0.5,0), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_O_D3',**kwargs)
	

# def test_F432_O_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_O_D4(cell=100, depth=2)
# 	G = [ SymElem( 'O', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_O_D4',**kwargs)
	

# def test_F432_O_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_O_D4(cell=100, depth=2)
# 	G = [ SymElem( 'O', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,-0.5,0.5), axis=Vec(0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_O_D4',**kwargs)
	

# def test_F432_O_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_O_O(cell=100, depth=2)
# 	G = [ SymElem( 'O', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_O_O',**kwargs)
	

# def test_F432_O_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_O_O(cell=100, depth=2)
# 	G = [ SymElem( 'O', cen=cell*( Vec ( -0.5,0,-0.5 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_O_O',**kwargs)
	

# def test_F432_O_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_F432_O_O(cell=100, depth=2)
# 	G = [ SymElem( 'O', cen=cell*( Vec ( -0.5,0,-0.5 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_F432_O_O',**kwargs)
	

# def test_H32_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_H32_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.166667,-0.333333,0.166667 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(0.5,0.866025,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_H32_C2_D3',**kwargs)
	

# def test_H32_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_H32_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.166667,0.166667,0.166667 ) - Vec ( 0.5,0.866025,0 ) *0.5 ), axis=Vec(0.5,0.866025,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(0.5,0.866025,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_H32_C2_D3',**kwargs)
	

# def test_H32_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_H32_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,0,0 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.333333,-0.333333,0.166667), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_H32_C2_D3',**kwargs)
	

# def test_H32_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_H32_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,0,0 ) - Vec ( -0.5,0.866025,0 ) *0.5 ), axis=Vec(-0.5,0.866025,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.333333,0.333333,-0.166667), axis=Vec(-0.5,0.866025,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_H32_C2_D3',**kwargs)
	

# def test_H32_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_H32_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.333333,-0.333333,0.166667 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(0.5,0.866025,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_H32_D3_D3',**kwargs)
	
#### NOT WORKING ####
def test_I213_C2_C3(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_I213_C2_C3(cell=100, depth=2)
	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,-0.25,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
		),
	      SymElem( 'C3', cen=cell*Vec(0.166667,-0.166667,0.333333), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(,,) 
	    ), ]
	test_xtal(G,cell,tag='test_I213_C2_C3',**kwargs)
	

def test_I213_C3_C2(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_I213_C3_C2(cell=100, depth=2)
	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.333333,-0.333333,0.666667 ) - Vec ( 0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
		),
	      SymElem( 'C2', cen=cell*Vec(0,-0.5,0.25), axis=Vec(1,0,0), #axis2=Vec(,,) 
	    ), ]
	test_xtal(G,cell,tag='test_I213_C3_C2',**kwargs)
	

# def test_I4122_C2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4122_C2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,-0.25,-0.375 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.5,-0.5), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4122_C2_D2',**kwargs)
	

# def test_I4122_C2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4122_C2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,-0.25,-0.375 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-1,0,-0.5), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4122_C2_D2',**kwargs)
	

# def test_I4132_C2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_C2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.375,0.125,0.125 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.25,0.375,0), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_C2_D2',**kwargs)
	

# def test_I4132_C2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_C2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.375,0.125,0.125 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.25,-0.375), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_C2_D2',**kwargs)
	

# def test_I4132_C2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_C2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.125,0.375,0.375 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0.25,0.375), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_C2_D2',**kwargs)
	

# def test_I4132_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.375,0.125,0.125 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,-0.375,-0.125), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_C2_D3',**kwargs)
	

# def test_I4132_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.375,0.125,0.125 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.375,0.125,0.375), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_C2_D3',**kwargs)
	

# def test_I4132_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.125,0.375,0.125 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.375,-0.125,0.125), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_C2_D3',**kwargs)
	

# def test_I4132_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.125,0.375,0.375 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,0.125,-0.125), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_C2_D3',**kwargs)
	

# def test_I4132_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.25,0,0 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.375,0.125,0.375), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_C2_D3',**kwargs)
	

# def test_I4132_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,-0.5,-0.25 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.125,-0.375,0.375), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_C2_D3',**kwargs)
	

# def test_I4132_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.375,-0.375,-0.375 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.375,-0.125,0.125), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_C2_D3',**kwargs)
	

# def test_I4132_C3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_C3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.333333,-0.333333,0.666667 ) - Vec ( 0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.25,-0.125), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_C3_D2',**kwargs)
	

# def test_I4132_C3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_C3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.333333,-0.333333,0.666667 ) - Vec ( 0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.75,-0.375,0), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_C3_D2',**kwargs)
	

# def test_I4132_C3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_C3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.333333,-0.333333,0.666667 ) - Vec ( 0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.25,0.125), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_C3_D2',**kwargs)
	

# def test_I4132_C3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_C3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.166667,0.333333,0.166667 ) - Vec ( -0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.375,0,0.25), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_C3_D2',**kwargs)
	

# def test_I4132_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( 0,0.75,-0.125 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), axis2=Vec(-0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.125,0,-0.25), axis=Vec(0,0.707107,0.707107), axis2=Vec(1,0,0) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D2',**kwargs)
	

# def test_I4132_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( 0,0.75,-0.125 ) ), axis=Vec(0.707107,0.707107,0), axis2=Vec(-0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.375,0.5,-0.25), axis=Vec(0,0.707107,0.707107), axis2=Vec(0,-0.707107,0.707107) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D2',**kwargs)
	

# def test_I4132_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.375,-0.5 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), axis2=Vec(0.707107,0,0.707107) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,0.25,0.125), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0,0,1) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D2',**kwargs)
	

# def test_I4132_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,0.125,-0.5 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), axis2=Vec(-0.707107,0,0.707107) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.125,0,-0.25), axis=Vec(0,0.707107,0.707107), axis2=Vec(1,0,0) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D2',**kwargs)
	

# def test_I4132_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( 0.125,0.5,-0.25 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), axis2=Vec(0,-0.707107,0.707107) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0.25,0.125,0), axis=Vec(0.707107,0,0.707107), axis2=Vec(0,1,0) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D2',**kwargs)
	

# def test_I4132_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( 0.375,0,0.75 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), axis2=Vec(0,-0.707107,0.707107) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0.25,0.125,0), axis=Vec(0.707107,0,0.707107), axis2=Vec(-0.707107,0,0.707107) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D2',**kwargs)
	

# def test_I4132_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( 0.125,0,0.25 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), axis2=Vec(0,-0.707107,0.707107) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0.25,0.125,0), axis=Vec(0,1,0), axis2=Vec(-0.707107,0,0.707107) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D2',**kwargs)
	

def test_I4132_D2_D3(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D3(cell=100, depth=2)
	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.375,0,-0.75 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), axis2=Vec(0,0.707107,0.707107) 
		),
	      SymElem( 'D3', cen=cell*Vec(0.125,-0.125,0.375), axis=Vec(0.707107,0,0.707107), axis2=Vec(-0.57735,0.57735,0.57735) 
	    ), ]
	test_xtal(G,cell,tag='test_I4132_D2_D3',**kwargs)
	

# def test_I4132_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.375,0,-0.75 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), axis2=Vec(0,0.707107,0.707107) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.125,0.375,0.125), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D3',**kwargs)
	

# def test_I4132_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.375,-0.5,-0.25 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,-0.125,0.375), axis=Vec(0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D3',**kwargs)
	

# def test_I4132_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.375,-0.5,-0.25 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.125,0.375,0.125), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D3',**kwargs)
	

# def test_I4132_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.375,-0.5,-0.25 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.125,0.125,-0.375), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D3',**kwargs)
	

# def test_I4132_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.25,-0.375 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.375,-0.375,-0.375), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D3',**kwargs)
	

# def test_I4132_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.125,0,-0.25 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), axis2=Vec(0,0.707107,0.707107) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,0.125,0.125), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D3',**kwargs)
	

# def test_I4132_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.375,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.125,-0.125,-0.125), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D3',**kwargs)
	

# def test_I4132_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.125,-0.5,0.25 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,0.125,0.125), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D3',**kwargs)
	

# def test_I4132_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.125,0 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,0.125,0.125), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D3',**kwargs)
	

# def test_I4132_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( 0,-0.75,0.125 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,0.375,0.375), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D3',**kwargs)
	

# def test_I4132_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0.25,0.375 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,0.375,0.375), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D3',**kwargs)
	

# def test_I4132_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.125,0 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,0.375,0.375), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D3',**kwargs)
	

# def test_I4132_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( 0.25,-0.125,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), axis2=Vec(0.707107,0,0.707107) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,0.125,0.125), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D3',**kwargs)
	

# def test_I4132_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.375,-0.5,-0.25 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,0.375,0.375), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D3',**kwargs)
	

# def test_I4132_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.25,-0.375 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,0.375,0.375), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D3',**kwargs)
	

# def test_I4132_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.375,0,0.25 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,0.375,0.375), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D3',**kwargs)
	

# def test_I4132_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.25,0.125 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,0.375,0.375), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D2_D3',**kwargs)
	

# def test_I4132_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.375,-0.375,-0.375 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.375,-0.5,-0.25), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D3_D2',**kwargs)
	

# def test_I4132_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.375,-0.375,-0.375 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.375,-0.5,-0.25), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D3_D2',**kwargs)
	

# def test_I4132_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.375,-0.375,-0.375 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.25,0.125), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D3_D2',**kwargs)
	

# def test_I4132_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.375,-0.375,-0.375 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.25,-0.375), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D3_D2',**kwargs)
	

# def test_I4132_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.375,0.125,-0.125 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), axis2=Vec(0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,0.25,-0.375), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D3_D2',**kwargs)
	

# def test_I4132_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.375,-0.375,-0.375 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,-0.375,-0.125), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D3_D3',**kwargs)
	

# def test_I4132_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.375,-0.375,-0.375 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.375,0.125,0.375), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D3_D3',**kwargs)
	

# def test_I4132_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.375,-0.375,-0.375 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,0.375,-0.375), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D3_D3',**kwargs)
	

# def test_I4132_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.375,0.375,-0.125 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.375,0.125,0.375), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D3_D3',**kwargs)
	

# def test_I4132_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I4132_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.375,0.375,-0.125 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,0.375,0.375), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I4132_D3_D3',**kwargs)
	

# def test_I422_C2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I422_C2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0.25,-0.25,-0.25 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,-0.5,-0.5), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I422_C2_D4',**kwargs)
	

# def test_I422_C2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I422_C2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0.25,-0.25,-0.25 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I422_C2_D4',**kwargs)
	

# def test_I422_C2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I422_C2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.25,-0.25,0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I422_C2_D4',**kwargs)
	

# def test_I422_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I422_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I422_D2_D4',**kwargs)
	

# def test_I422_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I422_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I422_D2_D4',**kwargs)
	

# def test_I422_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I422_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( 0,-0.5,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I422_D2_D4',**kwargs)
	

# def test_I422_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I422_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( 0,-0.5,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I422_D2_D4',**kwargs)
	

# def test_I422_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I422_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.25), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I422_D4_D2',**kwargs)
	

# def test_I422_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I422_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.25), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I422_D4_D2',**kwargs)
	

# def test_I422_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I422_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,0 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,0.25), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I422_D4_D2',**kwargs)
	

# def test_I422_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I422_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,0 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,0.25), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I422_D4_D2',**kwargs)
	

# def test_I422_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I422_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,0 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.5,0.25), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I422_D4_D2',**kwargs)
	

# def test_I432_C2_C4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C2_C4(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.25,-0.25,-0.25 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'C4', cen=cell*Vec(0,0,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C2_C4',**kwargs)
	

# def test_I432_C2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.25,-0.25,-0.25 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-1,0,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C2_D2',**kwargs)
	

# def test_I432_C2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.25,-0.25,-0.25 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C2_D2',**kwargs)
	

# def test_I432_C2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.25), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C2_D2',**kwargs)
	

# def test_I432_C2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.25,-0.5,0), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C2_D2',**kwargs)
	

def test_I432_C2_D3(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C2_D3(cell=100, depth=2)
	G = [ SymElem( 'D3', cen=cell*Vec(0.25, 0.25, 0.25), axis=Vec(0.707107,0.707107,0), axis2=Vec(0,0,1) 
	    ),
	    SymElem( 'C2', cen=cell*( Vec ( 0,0,0 ) ), axis=Vec(1,0,0), #axis2=Vec(-,-,-) 
		), ]
	test_xtal(G,cell,tag='test_I432_C2_D3',**kwargs)

# def test_I432_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.25,-0.25,-0.25 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C2_D3',**kwargs)
	

# def test_I432_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.25,-0.25,0.25 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,-0.5,-0.5), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C2_D3',**kwargs)
	

# def test_I432_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.25,-0.25,-0.25), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C2_D3',**kwargs)
	

# def test_I432_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.25,-0.25,0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,-0.5,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C2_D3',**kwargs)
	

# def test_I432_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.25,0.25,0.25 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,-0.5,-0.5), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C2_D3',**kwargs)
	

# def test_I432_C2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.25,-0.25,-0.25 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,0), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C2_D4',**kwargs)
	

# def test_I432_C2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.25,-0.25,-0.25 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C2_D4',**kwargs)
	

# def test_I432_C2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.25,-0.25,-0.25 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C2_D4',**kwargs)
	

# def test_I432_C2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.25,-0.25,0.25 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C2_D4',**kwargs)
	

# def test_I432_C2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.25,0.25,-0.25 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,-0.5,-0.5), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C2_D4',**kwargs)
	

def test_I432_C2_O(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C2_O(cell=100, depth=2)
	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.25,-0.25,-0.25 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(-,-,-) 
		),
	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
	    ), ]
	test_xtal(G,cell,tag='test_I432_C2_O',**kwargs)
	

# def test_I432_C2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C2_O(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.25,-0.25,0.25 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C2_O',**kwargs)
	

# def test_I432_C2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C2_O(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.25,-0.25,0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C2_O',**kwargs)
	

# def test_I432_C4_C2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C4_C2(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'C2', cen=cell*Vec(-0.25,-0.25,0.25), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C4_C2',**kwargs)
	

# def test_I432_C4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.25,-0.5,0), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C4_D2',**kwargs)
	

# def test_I432_C4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.25,0,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C4_D2',**kwargs)
	

# def test_I432_C4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.25,-0.5,0), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C4_D2',**kwargs)
	

# def test_I432_C4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.25,0.25,-0.25), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C4_D3',**kwargs)
	

# def test_I432_C4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_C4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( -0.5,0,0.5 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.25,0.25,0.25), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_C4_D3',**kwargs)
	

# def test_I432_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-1,0,0), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D2',**kwargs)
	

# def test_I432_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D2',**kwargs)
	

# def test_I432_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.5,0 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(0,0.707107,0.707107) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-1,0,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D2',**kwargs)
	

# def test_I432_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.5,0 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(0,0.707107,0.707107) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D2',**kwargs)
	

# def test_I432_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.5,0 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(0,0.707107,0.707107) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.5,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D2',**kwargs)
	

# def test_I432_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.5,0 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(0,0.707107,0.707107) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-1,0,0), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D2',**kwargs)
	

# def test_I432_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( 0,-0.5,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D2',**kwargs)
	

# def test_I432_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( 0,0.5,-0.25 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(-0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.5,0.5), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D2',**kwargs)
	

# def test_I432_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( 0,-0.5,0.5 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(0,-0.707107,0.707107) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,0.25,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D2',**kwargs)
	

# def test_I432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D3',**kwargs)
	

# def test_I432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D3',**kwargs)
	

# def test_I432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.5,0 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(0,0.707107,0.707107) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D3',**kwargs)
	

# def test_I432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D3',**kwargs)
	

# def test_I432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -1,-0.5,0 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0.707107,0,0.707107) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.25,0.25,-0.25), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D3',**kwargs)
	

# def test_I432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.25,-0.25,-0.25), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D3',**kwargs)
	

# def test_I432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,0,-0.5 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(0,0.707107,0.707107) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D3',**kwargs)
	

# def test_I432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,-0.5,0.5), axis=Vec(0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D4',**kwargs)
	

# def test_I432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D4',**kwargs)
	

# def test_I432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,0,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D4',**kwargs)
	

# def test_I432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.5,0 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(0,0.707107,0.707107) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D4',**kwargs)
	

# def test_I432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.5,0 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(0,0.707107,0.707107) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,0), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D4',**kwargs)
	

# def test_I432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.5,0 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(0,0.707107,0.707107) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,0), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D4',**kwargs)
	

# def test_I432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.5,0 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(0,0.707107,0.707107) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,0,0.5), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D4',**kwargs)
	

# def test_I432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,0,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D4',**kwargs)
	

# def test_I432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.25,0 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D4',**kwargs)
	

# def test_I432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,0,-0.5 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,0), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_D4',**kwargs)
	

# def test_I432_D2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_O(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_O',**kwargs)
	

# def test_I432_D2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_O(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.5,0 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), axis2=Vec(0,0.707107,0.707107) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_O',**kwargs)
	

# def test_I432_D2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D2_O(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.5,0 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D2_O',**kwargs)
	


# def test_I432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.25,0.25,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0.5,-0.5), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D2',**kwargs)
	

# def test_I432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.25,0.25,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D2',**kwargs)
	

# def test_I432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.25,0.25,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-1,0,0), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D2',**kwargs)
	

# def test_I432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.25), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D2',**kwargs)
	

# def test_I432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,0.25), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D2',**kwargs)
	

# def test_I432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.5,-0.25), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D2',**kwargs)
	

# def test_I432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.25,0), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D2',**kwargs)
	

# def test_I432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.25,0), axis=Vec(0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D2',**kwargs)
	

# def test_I432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.25,-0.25,0.25 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-1,0,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D2',**kwargs)
	

# def test_I432_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.25,0.25,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D3',**kwargs)
	

# def test_I432_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.25,0.25,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D3',**kwargs)
	

# def test_I432_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.25,0.25,0.25), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D3',**kwargs)
	

# def test_I432_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.25,-0.25,0.25), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D3',**kwargs)
	

# def test_I432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.25,0.25,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(1,0,0), axis2=Vec(0,1,0) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D4',**kwargs)
	

# def test_I432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.25,0.25,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(-0.57735,-0.57735,0.57735), 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,0), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D4',**kwargs)
	

# def test_I432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.25,0.25,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D4',**kwargs)
	

# def test_I432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.25,0.25,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,0), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D4',**kwargs)
	

# def test_I432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.25,-0.25,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D4',**kwargs)
	

# def test_I432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.25,-0.25,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D4',**kwargs)
	

# def test_I432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.25,-0.25,0.25 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), axis2=Vec(0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D4',**kwargs)
	

# def test_I432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.25,-0.25,0.25 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), axis2=Vec(0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D4',**kwargs)
	

# def test_I432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.25,0.25,0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_D4',**kwargs)



# def test_I432_D3_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_O(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.25,0.25,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_O',**kwargs)
	

# def test_I432_D3_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_O(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.25,-0.25,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_O',**kwargs)
	

# def test_I432_D3_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D3_O(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.25,-0.25,0.25 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D3_O',**kwargs)
	

# def test_I432_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.25), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D4_D2',**kwargs)
	

# def test_I432_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.25,-0.5), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D4_D2',**kwargs)
	

# def test_I432_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.5,-0.25), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D4_D2',**kwargs)
	

# def test_I432_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.25,0.5,0), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D4_D2',**kwargs)
	

# def test_I432_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.25,-0.5,0), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D4_D2',**kwargs)
	

# def test_I432_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.25,0), axis=Vec(0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D4_D2',**kwargs)
	

# def test_I432_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0.25,0,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D4_D2',**kwargs)
	

# def test_I432_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,0.5 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,0.25), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D4_D2',**kwargs)
	

# def test_I432_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,0,0.5 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0.25,-0.5,0), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D4_D2',**kwargs)
	

# def test_I432_D4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.25,-0.25,0.25), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D4_D3',**kwargs)
	

# def test_I432_D4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.25,-0.25,-0.25), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D4_D3',**kwargs)
	

# def test_I432_D4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.25,0.25,0.25), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D4_D3',**kwargs)
	

# def test_I432_D4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_I432_D4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.25,-0.25,-0.25), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_I432_D4_D3',**kwargs)
	

# def test_P213_C3_C3(cell=100,**kwargs): #### doesn't look correct
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P213_C3_C3(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.333333,-0.166667,0.166667 ) - Vec ( 0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'C3', cen=cell*Vec(-0.166667,0.166667,-0.333333), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P213_C3_C3',**kwargs)
	

def test_P23_C2_T(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_P23_C2_T(cell=100, depth=2)
	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.5,0,0 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(-,-,-) 
		),
	      SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
	    ), ]
	test_xtal(G,cell,tag='test_P23_C2_T',**kwargs)
	

# def test_P23_C3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P23_C3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.333333,-0.333333,0.666667 ) - Vec ( 0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P23_C3_D2',**kwargs)
	

# def test_P23_C3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P23_C3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.333333,-0.333333,0.666667 ) - Vec ( 0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P23_C3_D2',**kwargs)
	

# def test_P23_D2_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P23_D2_T(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.5 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P23_D2_T',**kwargs)
	

# def test_P23_D2_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P23_D2_T(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P23_D2_T',**kwargs)
	

# def test_P23_D2_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P23_D2_T(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( 0,-0.5,-0.5 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P23_D2_T',**kwargs)
	

def test_P312_D3_D3(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_P312_D3_D3(cell=100, depth=2)
	G = [ SymElem( 'D3', cen=cell*( Vec ( 0,0,0 ) ), axis=Vec(0,0,1), axis2=Vec(0.866025,0.5,0) 
		),
	      SymElem( 'D3', cen=cell*Vec(-0.333333,0.333333,-0.5), axis=Vec(0,0,1), axis2=Vec(0.866025,-0.5,0) 
	    ), ]
	test_xtal(G,cell,tag='test_P312_D3_D3',**kwargs)

# def test_P312_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P312_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.866025,0.5,0 ) *0.5 ), axis=Vec(0.866025,0.5,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.333333,0.333333,-0.5), axis=Vec(0.866025,-0.5,0), axis2=Vec(0,0,1) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P312_D3_D3',**kwargs)
	

def test_P4132_test2(cell=100,**kwargs):
 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4132_C2_C3(cell=100, depth=2)
 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.125,-0.125,-0.125 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-,-,-) 
		),
	      SymElem( 'C3', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(-0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
 	    ), ]
 	test_xtal(G,cell,tag='test_P4132_C2_C3',**kwargs)
	

# def test_P4132_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4132_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.125,-0.125,-0.125 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,-0.375,-0.125), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4132_C2_D3',**kwargs)
	

# def test_P4132_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4132_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.125,-0.125,-0.125 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,0.375,-0.375), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4132_C2_D3',**kwargs)
	

# def test_P4132_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4132_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.375,-0.375,0.375 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.125,-0.125,-0.125), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4132_C2_D3',**kwargs)
	

# def test_P4132_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4132_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.375,0.125,0.375 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.125,-0.125,-0.125), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4132_C2_D3',**kwargs)
	

# def test_P4132_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4132_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0.375,0.375,0.375 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,0.375,-0.375), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4132_C2_D3',**kwargs)
	

# def test_P4132_C3_C2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4132_C3_C2(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'C2', cen=cell*Vec(-0.375,-0.125,0.125), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4132_C3_C2',**kwargs)
	

# def test_P4132_C3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4132_C3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.375,-0.125,0.125), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4132_C3_D3',**kwargs)
	

# def test_P4132_C3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4132_C3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,0.375,-0.375), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4132_C3_D3',**kwargs)
	

# def test_P4132_C3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4132_C3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0.166667,-0.333333,-0.166667 ) - Vec ( -0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.125,-0.125,-0.125), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4132_C3_D3',**kwargs)
	

# def test_P4132_C3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4132_C3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0.166667,-0.166667,0.333333 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,0.375,-0.375), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4132_C3_D3',**kwargs)
	

# def test_P4132_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4132_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.375,-0.375,0.125 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.375,-0.125,0.125), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4132_D3_D3',**kwargs)
	

# def test_P4132_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4132_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.375,-0.125,0.125 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,0.375,0.375), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4132_D3_D3',**kwargs)
	

# def test_P4132_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4132_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.125,0.375,-0.375 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,0.375,0.375), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4132_D3_D3',**kwargs)
	

# def test_P4132_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4132_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.125,-0.125,-0.125 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.375,-0.125,0.125), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4132_D3_D3',**kwargs)
	

# def test_P4132_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4132_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.125,-0.125,-0.125 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.375,0.125,0.375), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4132_D3_D3',**kwargs)
	

# def test_P4132_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4132_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.125,-0.125,-0.125 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,0.375,-0.375), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4132_D3_D3',**kwargs)
	

# def test_P4132_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4132_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.375,0.125,0.375 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,0.375,0.375), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4132_D3_D3',**kwargs)
	

# def test_P4132_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4132_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.125,-0.375,-0.125 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.125,-0.125,-0.125), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4132_D3_D3',**kwargs)
	
### WORKS AS 2D ARRAY ###
def test_P422_D4_D2(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_P422_D4_D2(cell=100, depth=2)
	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,0 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), axis2=Vec(0,0,1) 
		),
	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
	    ), ]
	test_xtal(G,cell,tag='test_P422_D4_D2',**kwargs)
	

# def test_P422_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P422_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,0 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P422_D4_D2',**kwargs)
	

# def test_P422_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P422_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,0 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P422_D4_D2',**kwargs)
	

# def test_P422_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P422_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P422_D4_D2',**kwargs)
	

# def test_P422_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P422_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P422_D4_D2',**kwargs)
	

# def test_P422_D4_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P422_D4_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec( , , ) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P422_D4_D4',**kwargs)

### Stacked 2D layers ### Isn't going into third dimension...basically just creating fibers in 3rd dimension though, can I model it all? ###
def test_P422_D4_D4(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_P422_D4_D4(cell=100, depth=2)
	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,0 ) ), axis=Vec(0,0,1), axis2=Vec(1,0,0) 
		),
	      SymElem( 'D4', cen=cell*Vec(0.5,0.5,0), axis=Vec(0,0,1), axis2=Vec(1,0,0) 
	    ), ]
	test_xtal(G,cell,tag='test_P422_D4_D4',**kwargs)
	

########## fails at higher symmetries, need to move to origin #######
# def test_P4222_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4222_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.75,0,0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,0,0), axis=Vec(0,1,0), axis2=Vec(0,0,1) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4222_D2_D2',**kwargs)
########## fails at higher symmetries #######

# def test_P4222_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4222_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell* Vec ( -1,0,-0.25 ) , axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), axis2=Vec(0,0,1) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4222_D2_D2',**kwargs)
	

###getting closer....
# def test_P4222_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4222_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -1,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), axis2=Vec(1,0,0) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4222_D2_D2',**kwargs)
	
# def test_P4222_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4222_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -1,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,0,1), axis2=Vec(1,0,0) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4222_D2_D2',**kwargs)


# def test_P4222_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4222_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), axis2=Vec(0,0,1) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4222_D2_D2',**kwargs)
	
###close...
# def test_P4222_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4222_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(1,0,0), axis2=Vec(0,1,0) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4222_D2_D2',**kwargs)


# def test_P4222_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4222_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0.5,-0.25 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), axis2=Vec(-0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(1,0,0), axis2=Vec(0,1,0) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4222_D2_D2',**kwargs)
	

# def test_P4232_C3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_C3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.5,-0.25), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_C3_D2',**kwargs)
	

# def test_P4232_C3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_C3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.5,-0.25), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_C3_D2',**kwargs)
	

# def test_P4232_C3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_C3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.25,0), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_C3_D2',**kwargs)
	

def test_P4232_D2_D2(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D2_D2(cell=100, depth=2)
	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.707107,0.707107,0) 
		),
	      SymElem( 'D2', cen=cell*Vec(-0.25,0,-0.5), axis=Vec(0,-0.707107,0.707107), axis2=Vec(0,0.707107,0.707107) 
	    ), ]
	test_xtal(G,cell,tag='test_P4232_D2_D2',**kwargs)
	

# def test_P4232_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.25,0,-0.5), axis=Vec(0,-0.707107,0.707107), axis2=Vec(1,0,0) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D2_D2',**kwargs)
	

# def test_P4232_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0.5,-0.25,0), axis=Vec(0.707107,0,0.707107), axis2=Vec(-0.707107,0,0.707107) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D2_D2',**kwargs)
	

# def test_P4232_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.25,0,-0.5), axis=Vec(0,-0.707107,0.707107), axis2=Vec(1,0,0) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D2_D2',**kwargs)
	

# def test_P4232_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.25,0 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.25,-0.5,0), axis=Vec(0,0.707107,0.707107), axis2=Vec(1,0,0) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D2_D2',**kwargs)
	

# def test_P4232_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.25,0.25,0.25), axis=Vec(0.707107,0.707107,0), axis2=Vec(-0.57735,0.57735,0.57735) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D2_D3',**kwargs)
	

# def test_P4232_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.25,0.25,0.25), axis=Vec(0.707107,0.707107,0), axis2=Vec(-0.57735,0.57735,0.57735) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D2_D3',**kwargs)
	

# def test_P4232_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.25,-0.25,0.25), axis=Vec(-0.707107,0.707107,0), axis2=Vec(-0.57735,-0.57735,0.57735) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D2_D3',**kwargs)
	

# def test_P4232_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.25,0 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), axis2=Vec(0.707107,0,0.707107) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.25,0.25,-0.25), axis=Vec(0.707107,0.707107,0), axis2=Vec(0.57735,-0.57735,0.57735) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D2_D3',**kwargs)
	

# def test_P4232_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.25,0 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.25,0.25,-0.25), axis=Vec(0.707107,0.707107,0), axis2=Vec(0.57735,-0.57735,0.57735) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D2_D3',**kwargs)
	

# def test_P4232_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,0,-0.5 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.25,-0.25,0.25), axis=Vec(-0.707107,0.707107,0), axis2=Vec(-0.57735,-0.57735,0.57735) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D2_D3',**kwargs)
	

# def test_P4232_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.25,-0.5,0 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.25,-0.25,-0.25), axis=Vec(0.707107,0.707107,0), axis2=Vec(-0.57735,0.57735,0.57735) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D2_D3',**kwargs)
	

# def test_P4232_D2_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D2_T(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D2_T',**kwargs)
	

# def test_P4232_D2_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D2_T(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D2_T',**kwargs)
	

# def test_P4232_D2_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D2_T(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D2_T',**kwargs)
	

# def test_P4232_D2_T(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D2_T(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( 0,-0.5,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'T', cen=cell*Vec(0,0,0), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D2_T',**kwargs)
	

# def test_P4232_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.25,0.25,0.25 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.25,0), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D3_D2',**kwargs)
	

# def test_P4232_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.25,0.25,0.25 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.25,0), axis=Vec(0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D3_D2',**kwargs)
	

# def test_P4232_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.25,0.25,0.25 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.5,0.25), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D3_D2',**kwargs)
	

# def test_P4232_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.25,0.25,0.25 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,0.5,-0.25), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D3_D2',**kwargs)
	

# def test_P4232_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.25,0.25,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0.25,-0.5,0), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D3_D2',**kwargs)
	

# def test_P4232_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.25,-0.25,-0.25 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,0.25), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D3_D2',**kwargs)
	

# def test_P4232_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.25,0.25,0.25 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.25,0.25,0.25), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0.57735,0.57735,0.57735) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D3_D3',**kwargs)
	

# def test_P4232_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4232_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.25,0.25,0.25 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.25,0.25,-0.25), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4232_D3_D3',**kwargs)
	

# def test_P432_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,-0.5,-0.5), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C2_D3',**kwargs)
	

# def test_P432_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,-0.5,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C2_D3',**kwargs)
	

# def test_P432_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.5,-0.5,-0.5), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C2_D3',**kwargs)
	

# def test_P432_C2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C2_D4',**kwargs)
	

# def test_P432_C2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C2_D4',**kwargs)
	

# def test_P432_C2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,-0.5,0 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C2_D4',**kwargs)
	

# def test_P432_C2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,-0.5,0 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C2_D4',**kwargs)
	

# def test_P432_C2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C2_D4',**kwargs)
	

# def test_P432_C2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,-0.5,0.5 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C2_D4',**kwargs)
	

# def test_P432_C2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.5,-0.5,0.5 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C2_D4',**kwargs)
	

# def test_P432_C2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.5,0,0.5 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C2_D4',**kwargs)
	

def test_P432_C2_O(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C2_O(cell=100, depth=2)
	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(-,-,-) 
		),
	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
	    ), ]
	test_xtal(G,cell,tag='test_P432_C2_O',**kwargs)
	

# def test_P432_C2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C2_O(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,-0.5,0 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C2_O',**kwargs)
	

# def test_P432_C2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C2_O(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C2_O',**kwargs)
	

# def test_P432_C3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*Vec(0,0,0), axis=Vec(0,0,1), axis2=Vec(1,0,0) 
# 	    ), 
# 	      SymElem( 'C3', cen=cell*( Vec ( 0.5,0.5,0 ) ), axis=Vec(-1,1,2), #axis2=Vec(-,-,-) 
# 		),]
# 	test_xtal(G,cell,tag='test_P432_C3_D4',**kwargs)




# def test_P432_C3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(1,0,0), axis2=Vec(0,0,1) 
# 	    ), 
# 	      SymElem( 'C3', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),]
# 	test_xtal(G,cell,tag='test_P432_C3_D4',**kwargs)
	

# def test_P432_C3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C3_D4',**kwargs)
	

# def test_P432_C3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C3_D4',**kwargs)
	

# def test_P432_C3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.666667,-0.333333,0.333333 ) - Vec ( 0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C3_D4',**kwargs)
	

# def test_P432_C3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.333333,-0.666667,0.333333 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C3_D4',**kwargs)
	


	

# def test_P432_C4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,-0.5,-0.5 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-1,0,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C4_D2',**kwargs)
	

# def test_P432_C4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.5,-0.5), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C4_D2',**kwargs)
	

# def test_P432_C4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,-0.5,-0.5 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C4_D3',**kwargs)
	

# def test_P432_C4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C4_D3',**kwargs)
	

# def test_P432_C4_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C4_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,-0.5,-0.5 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C4_D4',**kwargs)
	

# def test_P432_C4_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C4_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,-0.5,-0.5 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,0), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C4_D4',**kwargs)
	

# def test_P432_C4_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C4_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,-0.5,-0.5 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C4_D4',**kwargs)
	

# def test_P432_C4_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C4_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,-0.5,-0.5 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,0,0.5), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C4_D4',**kwargs)
	

# def test_P432_C4_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C4_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C4_D4',**kwargs)
	

# def test_P432_C4_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C4_D4(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( -0.5,0,0.5 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C4_D4',**kwargs)
	

def test_P432_C4_O(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C4_O(cell=100, depth=2)
	G = [ SymElem( 'C4', cen=cell*( Vec ( 0,-0.5,-0.5 ) - Vec ( 1,0,0 ) *0.25 ), axis=Vec(1,0,0), #axis2=Vec(-,-,-) 
		),
	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
	    ), ]
	test_xtal(G,cell,tag='test_P432_C4_O',**kwargs)
	

# def test_P432_C4_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_C4_O(cell=100, depth=2)
# 	G = [ SymElem( 'C4', cen=cell*( Vec ( -0.5,0,0.5 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_C4_O',**kwargs)
	

# def test_P432_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-1,0,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_D2',**kwargs)
	

# def test_P432_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -1,-0.5,0 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0.707107,0,0.707107) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0.5,0), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_D2',**kwargs)
	

# def test_P432_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -1,0,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_D2',**kwargs)
	

# def test_P432_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-1,0 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(0,0.707107,0.707107) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_D2',**kwargs)
	

# def test_P432_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0.5,-0.5 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(-0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-1,0), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_D2',**kwargs)
	

# def test_P432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_D3',**kwargs)
	

# def test_P432_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0.707107,0,0.707107) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_D3',**kwargs)
	

# def test_P432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_D4',**kwargs)
	

# def test_P432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_D4',**kwargs)
	

# def test_P432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -1,-0.5,0 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0.707107,0,0.707107) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_D4',**kwargs)
	

# def test_P432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -1,-0.5,0 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0.707107,0,0.707107) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_D4',**kwargs)
	

# def test_P432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -1,-0.5,0 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0.707107,0,0.707107) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_D4',**kwargs)
	

# def test_P432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -1,0,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.707107,0.707107,0) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,0,0.5), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_D4',**kwargs)
	

# def test_P432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-1,0 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(0,0.707107,0.707107) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_D4',**kwargs)
	

# def test_P432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0.707107,0,0.707107) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_D4',**kwargs)
	

# def test_P432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.5 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(-0.707107,0,0.707107) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_D4',**kwargs)
	

# def test_P432_D2_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.5 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(0.707107,0,0.707107) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_D4',**kwargs)
	

# def test_P432_D2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_O(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_O',**kwargs)
	

# def test_P432_D2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_O(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0.707107,0,0.707107) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_O',**kwargs)
	

# def test_P432_D2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_O(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,0.5 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(0,-0.707107,0.707107) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_O',**kwargs)
	

# def test_P432_D2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_O(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(0.707107,0,0.707107) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_O',**kwargs)
	

# def test_P432_D2_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D2_O(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.5 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D2_O',**kwargs)
	

# def test_P432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-1,0,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D3_D2',**kwargs)
	

# def test_P432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D3_D2',**kwargs)
	

# def test_P432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D3_D2',**kwargs)
	

# def test_P432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D3_D2',**kwargs)
	

# def test_P432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D3_D2',**kwargs)
	

# def test_P432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0,0,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.5,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D3_D2',**kwargs)
	

# def test_P432_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D3_D2',**kwargs)
	

# def test_P432_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D3_D3',**kwargs)
	

# def test_P432_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D3_D3',**kwargs)
	

# def test_P432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,-0.5), axis=Vec(1,0,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D3_D4',**kwargs)
	

# def test_P432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D3_D4',**kwargs)
	

# def test_P432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,0,0.5), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D3_D4',**kwargs)
	

# def test_P432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,0), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D3_D4',**kwargs)
	

# def test_P432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0,0,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D3_D4',**kwargs)
	

# def test_P432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D3_D4',**kwargs)
	

# def test_P432_D3_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D3_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0,0,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,-0.5,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D3_D4',**kwargs)
	

# def test_P432_D3_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D3_O(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D3_O',**kwargs)
	

# def test_P432_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-1,0,0), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D2',**kwargs)
	

# def test_P432_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.5,0.5), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D2',**kwargs)
	

# def test_P432_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D2',**kwargs)
	

# def test_P432_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-1,0,0), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D2',**kwargs)
	

# def test_P432_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D2',**kwargs)
	

# def test_P432_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D2',**kwargs)
	

# def test_P432_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.5,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D2',**kwargs)
	

# def test_P432_D4_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,0,0.5 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0.5,-0.5), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D2',**kwargs)
	

# def test_P432_D4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D3',**kwargs)
	

# def test_P432_D4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D3',**kwargs)
	

# def test_P432_D4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D3',**kwargs)
	

# def test_P432_D4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D3',**kwargs)
	

# def test_P432_D4_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D3',**kwargs)
	

# def test_P432_D4_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,0,0.5), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D4',**kwargs)

def test_P432_D4_D4(cell=100,**kwargs):
	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D4(cell=100, depth=2)
	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,0 )  ), axis=Vec(0,0,1), axis2=Vec(1,0,0) 
		),
	      SymElem( 'D4', cen=cell*Vec(0,0.5,0), axis=Vec(1,0,0), axis2=Vec(0,0,1)  
	    ), ]
	test_xtal(G,cell,tag='test_P432_D4_D4',**kwargs)
	

# def test_P432_D4_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,0,0), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D4',**kwargs)
	

# def test_P432_D4_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D4',**kwargs)
	

# def test_P432_D4_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(1,0,0) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,0,0.5), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D4',**kwargs)
	

# def test_P432_D4_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,0,0.5), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D4',**kwargs)
	

# def test_P432_D4_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D4',**kwargs)
	

# def test_P432_D4_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,0.5 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D4',**kwargs)
	

# def test_P432_D4_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,-0.5,0 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,0,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D4',**kwargs)
	

# def test_P432_D4_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,0,0.5 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(-0.5,0,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D4',**kwargs)
	

# def test_P432_D4_D4(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_D4(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,0 ) - Vec ( -0.707107,0,0.707107 ) *0.5 ), axis=Vec(-0.707107,0,0.707107), #axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'D4', cen=cell*Vec(0,-0.5,-0.5), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_D4',**kwargs)
	

# def test_P432_D4_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_O(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_O',**kwargs)
	

# def test_P432_D4_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_O(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( 1,0,0 ) *0.5 ), axis=Vec(1,0,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_O',**kwargs)
	

# def test_P432_D4_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_O(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_O',**kwargs)
	

# def test_P432_D4_O(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P432_D4_O(cell=100, depth=2)
# 	G = [ SymElem( 'D4', cen=cell*( Vec ( -0.5,-0.5,0.5 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(0,1,0) 
# 		),
# 	      SymElem( 'O', cen=cell*Vec(0,0,0), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P432_D4_O',**kwargs)
	

# def test_P4332_C2_C3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4332_C2_C3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.375,0.125,0.125 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'C3', cen=cell*Vec(0.333333,0.166667,-0.166667), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4332_C2_C3',**kwargs)
	

# def test_P4332_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4332_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.375,0.125,0.125 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.125,0.375,0.125), axis=Vec(0,0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4332_C2_D3',**kwargs)
	

# def test_P4332_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4332_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.375,0.125,0.125 ) - Vec ( 0,-0.707107,0.707107 ) *0.5 ), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,0.125,-0.125), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4332_C2_D3',**kwargs)
	

# def test_P4332_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4332_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.125,0.375,0.125 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,0.125,0.125), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4332_C2_D3',**kwargs)
	

# def test_P4332_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4332_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0.125,-0.125,-0.125 ) - Vec ( 0.707107,0.707107,0 ) *0.5 ), axis=Vec(0.707107,0.707107,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,-0.125,-0.375), axis=Vec(0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4332_C2_D3',**kwargs)
	

# def test_P4332_C3_C2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4332_C3_C2(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.166667,0.333333,0.166667 ) - Vec ( -0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'C2', cen=cell*Vec(0.125,0.125,0.125), axis=Vec(0,-0.707107,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4332_C3_C2',**kwargs)
	

# def test_P4332_C3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4332_C3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.166667,0.333333,0.166667 ) - Vec ( -0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,0.125,0.125), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4332_C3_D3',**kwargs)
	

# def test_P4332_C3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4332_C3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( -0.166667,0.333333,0.166667 ) - Vec ( -0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.375,0.375,-0.125), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4332_C3_D3',**kwargs)
	

# def test_P4332_C3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4332_C3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0.166667,-0.166667,0.333333 ) - Vec ( -0.57735,0.57735,0.57735 ) *0.5 ), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,0.125,-0.125), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4332_C3_D3',**kwargs)
	

# def test_P4332_C3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4332_C3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C3', cen=cell*( Vec ( 0,-0.5,-0.5 ) - Vec ( 0.57735,-0.57735,0.57735 ) *0.5 ), axis=Vec(0.57735,-0.57735,0.57735), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.375,0.375,-0.125), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4332_C3_D3',**kwargs)
	

# def test_P4332_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4332_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.375,-0.125,-0.375 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.375,0.125,-0.125), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4332_D3_D3',**kwargs)
	

# def test_P4332_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4332_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.375,-0.125,-0.375 ) - Vec ( 0.707107,0,0.707107 ) *0.5 ), axis=Vec(0.707107,0,0.707107), #axis2=Vec(-0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,-0.125,0.375), axis=Vec(0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4332_D3_D3',**kwargs)
	

# def test_P4332_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4332_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.375,-0.375,-0.375 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.375,0.375,-0.125), axis=Vec(0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4332_D3_D3',**kwargs)
	

# def test_P4332_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4332_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.375,-0.375,-0.375 ) - Vec ( -0.707107,0.707107,0 ) *0.5 ), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(0.57735,0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,-0.125,0.375), axis=Vec(0.707107,0,0.707107), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4332_D3_D3',**kwargs)
	

# def test_P4332_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P4332_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.125,-0.375,0.375 ) - Vec ( 0,0.707107,0.707107 ) *0.5 ), axis=Vec(0,0.707107,0.707107), #axis2=Vec(0.57735,-0.57735,0.57735) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.125,0.125,0.125), axis=Vec(-0.707107,0.707107,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P4332_D3_D3',**kwargs)
	

# def test_P622_C2_D6(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P622_C2_D6(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.5,-0.5,0 ) - Vec ( 0.866025,-0.5,0 ) *0.5 ), axis=Vec(0.866025,-0.5,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D6', cen=cell*Vec(0,0,-0.5), axis=Vec(0.866025,-0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P622_C2_D6',**kwargs)
	

# def test_P622_C2_D6(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P622_C2_D6(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.5,0,-0.5 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D6', cen=cell*Vec(0,0,0), axis=Vec(0.866025,-0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P622_C2_D6',**kwargs)
	

# def test_P622_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P622_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) ), axis=Vec(0.866025,-0.5,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.333333,0.333333,0), axis=Vec(0,1,0), axis2=Vec(0,0,1) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P622_D2_D3',**kwargs)
	

# def test_P622_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P622_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -1,0,-0.5 )), axis=Vec(0.866025,-0.5,0), axis2=Vec(0.5,0.866025,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.333333,0.333333,0), axis=Vec(0,1,0), axis2=Vec(0,0,1) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P622_D2_D3',**kwargs)
	

# def test_P622_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P622_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) ), axis=Vec(0.866025,-0.5,0), axis2=Vec(0.5,0.866025,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.333333,0.333333,0), axis=Vec(0,1,0), axis2=Vec(0,0,1) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P622_D2_D3',**kwargs)
	

# def test_P622_D2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P622_D2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,0 ) ), axis=Vec(0,0,1), axis2=Vec(0.5,0.866025,0) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.333333,-0.333333,-0.5), axis=Vec(0.866025,0.5,0), axis2=Vec(0,0,1) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P622_D2_D3',**kwargs)
	

# def test_P622_D2_D6(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P622_D2_D6(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( 0.866025,-0.5,0 ) *0.5 ), axis=Vec(0.866025,-0.5,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D6', cen=cell*Vec(0,0,0), axis=Vec(0.866025,-0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P622_D2_D6',**kwargs)
	

# def test_P622_D2_D6(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P622_D2_D6(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.5 ) - Vec ( 0.866025,-0.5,0 ) *0.5 ), axis=Vec(0.866025,-0.5,0), #axis2=Vec(0.5,0.866025,0) 
# 		),
# 	      SymElem( 'D6', cen=cell*Vec(0,0,0), axis=Vec(0.866025,-0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P622_D2_D6',**kwargs)
	

# def test_P622_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P622_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.333333,-0.333333,-0.5 ) - Vec ( 0.866025,0.5,0 ) *0.5 ), axis=Vec(0.866025,0.5,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.5,0), axis=Vec(0.866025,0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P622_D3_D2',**kwargs)
	

# def test_P622_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P622_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.333333,-0.333333,-0.5 ) - Vec ( 0.866025,0.5,0 ) *0.5 ), axis=Vec(0.866025,0.5,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P622_D3_D2',**kwargs)
	

# def test_P622_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P622_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.333333,-0.333333,-0.5 ) - Vec ( 0.866025,0.5,0 ) *0.5 ), axis=Vec(0.866025,0.5,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P622_D3_D2',**kwargs)
	

# def test_P622_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P622_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.333333,-0.333333,-0.5 ) - Vec ( 0.866025,0.5,0 ) *0.5 ), axis=Vec(0.866025,0.5,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.5,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P622_D3_D2',**kwargs)
	

# def test_P622_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P622_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.333333,0.333333,0 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P622_D3_D2',**kwargs)
	

# def test_P622_D3_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P622_D3_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.333333,0.333333,0 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P622_D3_D2',**kwargs)
	

# def test_P622_D6_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P622_D6_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D6', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.866025,-0.5,0 ) *0.5 ), axis=Vec(0.866025,-0.5,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.5,-0.5), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P622_D6_D2',**kwargs)
	

# def test_P622_D6_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P622_D6_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D6', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.866025,-0.5,0 ) *0.5 ), axis=Vec(0.866025,-0.5,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P622_D6_D2',**kwargs)
	

# def test_P622_D6_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P622_D6_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D6', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.866025,-0.5,0 ) *0.5 ), axis=Vec(0.866025,-0.5,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P622_D6_D2',**kwargs)
	

# def test_P622_D6_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P622_D6_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D6', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.866025,-0.5,0 ) *0.5 ), axis=Vec(0.866025,-0.5,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P622_D6_D2',**kwargs)
	

# def test_P622_D6_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P622_D6_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D6', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0.866025,-0.5,0 ) *0.5 ), axis=Vec(0.866025,-0.5,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.333333,0.333333,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P622_D6_D3',**kwargs)
	

# def test_P6222_C2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6222_C2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,-0.5,-0.333333 ) - Vec ( 0.866025,0.5,0 ) *0.5 ), axis=Vec(0.866025,0.5,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.5,-0.166667), axis=Vec(0.866025,-0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6222_C2_D2',**kwargs)
	

# def test_P6222_C2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6222_C2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,-0.5,-0.333333 ) - Vec ( 0.866025,0.5,0 ) *0.5 ), axis=Vec(0.866025,0.5,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.5,-0.166667), axis=Vec(0.866025,-0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6222_C2_D2',**kwargs)
	








# def test_P6222_C2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6222_C2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.5,0,0 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.5,-0.166667), axis=Vec(0.866025,-0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6222_C2_D2',**kwargs)
	

# def test_P6222_C2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6222_C2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,0,0 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.5,-0.166667), axis=Vec(0.866025,-0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6222_C2_D2',**kwargs)
	

# def test_P6222_C2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6222_C2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,0,0.166667 ) - Vec ( 0.866025,0.5,0 ) *0.5 ), axis=Vec(0.866025,0.5,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.5,0.333333), axis=Vec(0.866025,-0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6222_C2_D2',**kwargs)
	

# def test_P6222_C2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6222_C2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,0,0.333333 ) - Vec ( 0.866025,-0.5,0 ) *0.5 ), axis=Vec(0.866025,-0.5,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.5,0.166667), axis=Vec(0.866025,0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6222_C2_D2',**kwargs)
	
#### looks 2D, because axis2 is commented out ####
# def test_P6222_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6222_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.166667 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(0.5,0.866025,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6222_D2_D2',**kwargs)
	


# def test_P6222_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6222_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.166667 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), axis2=Vec(0.5,0.866025,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.5,-0.333333), axis=Vec(0.866025,0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6222_D2_D2',**kwargs)
	

# def test_P6222_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6222_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -1,0,0.333333 ) - Vec ( 0.866025,-0.5,0 ) *0.5 ), axis=Vec(0.866025,-0.5,0), #axis2=Vec(0.5,0.866025,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.5,0.166667), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6222_D2_D2',**kwargs)
	

# def test_P6222_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6222_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -1,0,0.333333 ) - Vec ( 0.866025,-0.5,0 ) *0.5 ), axis=Vec(0.866025,-0.5,0), #axis2=Vec(0.5,0.866025,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.5,0.166667), axis=Vec(0.866025,0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6222_D2_D2',**kwargs)
	

# def test_P6222_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6222_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0,-0.5 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,0,-0.333333), axis=Vec(0.866025,0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6222_D2_D2',**kwargs)
	

# def test_P6222_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6222_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -1,0,-0.166667 ) - Vec ( 0.866025,-0.5,0 ) *0.5 ), axis=Vec(0.866025,-0.5,0), #axis2=Vec(0.5,0.866025,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6222_D2_D2',**kwargs)
	

# def test_P6222_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6222_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -1,0,-0.166667 ) - Vec ( 0.866025,-0.5,0 ) *0.5 ), axis=Vec(0.866025,-0.5,0), #axis2=Vec(0.5,0.866025,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,0), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6222_D2_D2',**kwargs)
	

# def test_P6222_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6222_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,0.333333 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(0.866025,-0.5,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,0,0.166667), axis=Vec(0.866025,0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6222_D2_D2',**kwargs)
	

# def test_P6222_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6222_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( 0,-0.5,-0.333333 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-0.5,0.866025,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,0,-0.166667), axis=Vec(0.866025,-0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6222_D2_D2',**kwargs)
	

# def test_P6222_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6222_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0.5,0.333333 ) - Vec ( 0.5,0.866025,0 ) *0.5 ), axis=Vec(0.5,0.866025,0), #axis2=Vec(0.866025,-0.5,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.5,0.166667), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6222_D2_D2',**kwargs)
	

# def test_P6322_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6322_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.5,0.5,0 ) - Vec ( 0.5,0.866025,0 ) *0.5 ), axis=Vec(0.5,0.866025,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(-0.333333,0.333333,-0.25), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6322_C2_D3',**kwargs)
	

# def test_P6322_C2_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6322_C2_D3(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,0,0 ) - Vec ( -0.5,0.866025,0 ) *0.5 ), axis=Vec(-0.5,0.866025,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0.333333,-0.333333,-0.25), axis=Vec(0.866025,0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6322_C2_D3',**kwargs)
	

# def test_P6322_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6322_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( 0.333333,-0.333333,0.25 ) - Vec ( 0.866025,0.5,0 ) *0.5 ), axis=Vec(0.866025,0.5,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,0), axis=Vec(1,0,0), #axis2=Vec(0,1,0) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6322_D3_D3',**kwargs)
	

# def test_P6322_D3_D3(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6322_D3_D3(cell=100, depth=2)
# 	G = [ SymElem( 'D3', cen=cell*( Vec ( -0.333333,0.333333,-0.25 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), axis2=Vec(0,0,1) 
# 		),
# 	      SymElem( 'D3', cen=cell*Vec(0,0,-0.5), axis=Vec(1,0,0), axis2=Vec(0,1,0) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6322_D3_D3',**kwargs)
	

# def test_P6422_C2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6422_C2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.5,-0.5,0.166667 ) - Vec ( 0.866025,-0.5,0 ) *0.5 ), axis=Vec(0.866025,-0.5,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6422_C2_D2',**kwargs)
	

# def test_P6422_C2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6422_C2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.5,-0.5,0.166667 ) - Vec ( 0.866025,-0.5,0 ) *0.5 ), axis=Vec(0.866025,-0.5,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6422_C2_D2',**kwargs)
	

# def test_P6422_C2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6422_C2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.5,-0.5,0.166667 ) - Vec ( 0.866025,-0.5,0 ) *0.5 ), axis=Vec(0.866025,-0.5,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.5,0.333333), axis=Vec(0.866025,0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6422_C2_D2',**kwargs)
	

# def test_P6422_C2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6422_C2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( -0.5,0,-0.5 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.5,-0.333333), axis=Vec(0.866025,-0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6422_C2_D2',**kwargs)
	

# def test_P6422_C2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6422_C2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,0,-0.5 ) - Vec ( 0,1,0 ) *0.5 ), axis=Vec(0,1,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.5,-0.333333), axis=Vec(0.866025,-0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6422_C2_D2',**kwargs)
	

# def test_P6422_C2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6422_C2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'C2', cen=cell*( Vec ( 0,0,-0.166667 ) - Vec ( 0.866025,0.5,0 ) *0.5 ), axis=Vec(0.866025,0.5,0), #axis2=Vec(-,-,-) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,-0.5,-0.333333), axis=Vec(0.866025,-0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6422_C2_D2',**kwargs)
	

# def test_P6422_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6422_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -1,0,-0.333333 ) - Vec ( 0.866025,-0.5,0 ) *0.5 ), axis=Vec(0.866025,-0.5,0), #axis2=Vec(0.5,0.866025,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6422_D2_D2',**kwargs)
	

# def test_P6422_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6422_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -1,0,-0.333333 ) - Vec ( 0.866025,-0.5,0 ) *0.5 ), axis=Vec(0.866025,-0.5,0), #axis2=Vec(0.5,0.866025,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,1,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6422_D2_D2',**kwargs)
	

# def test_P6422_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6422_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -1,0,-0.333333 ) - Vec ( 0.866025,-0.5,0 ) *0.5 ), axis=Vec(0.866025,-0.5,0), #axis2=Vec(0.5,0.866025,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,-0.5), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6422_D2_D2',**kwargs)
	

# def test_P6422_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6422_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,0.166667 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(0.866025,-0.5,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6422_D2_D2',**kwargs)
	

# def test_P6422_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6422_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,0.166667 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(0.866025,-0.5,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(-0.5,0,0), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6422_D2_D2',**kwargs)
	

# def test_P6422_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6422_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,0.166667 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(0.866025,-0.5,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,0,0.333333), axis=Vec(0.866025,0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6422_D2_D2',**kwargs)
	

# def test_P6422_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6422_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,-0.5,-0.333333 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(0.5,0.866025,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.5,-0.166667), axis=Vec(0.866025,0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6422_D2_D2',**kwargs)
	

# def test_P6422_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6422_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( 0,-0.5,0.333333 ) - Vec ( 0,0,1 ) *0.5 ), axis=Vec(0,0,1), #axis2=Vec(-0.5,0.866025,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,0,0.166667), axis=Vec(0.866025,-0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6422_D2_D2',**kwargs)
	

# def test_P6422_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6422_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0.5,0.166667 ) - Vec ( 0.5,0.866025,0 ) *0.5 ), axis=Vec(0.5,0.866025,0), #axis2=Vec(0.866025,-0.5,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.5,0.333333), axis=Vec(0,0,1), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6422_D2_D2',**kwargs)
	

# def test_P6422_D2_D2(cell=100,**kwargs):
# 	#delete all ; run ~/pymolscripts/symgen2.py; test_P6422_D2_D2(cell=100, depth=2)
# 	G = [ SymElem( 'D2', cen=cell*( Vec ( -0.5,0.5,0.166667 ) - Vec ( 0.5,0.866025,0 ) *0.5 ), axis=Vec(0.5,0.866025,0), #axis2=Vec(0.866025,-0.5,0) 
# 		),
# 	      SymElem( 'D2', cen=cell*Vec(0,-0.5,0.333333), axis=Vec(0.866025,0.5,0), #axis2=Vec(,,) 
# 	    ), ]
# 	test_xtal(G,cell,tag='test_P6422_D2_D2',**kwargs)
	
################ End Una's parsed xtals_from_point ####################


def test_H32_D3(cell=80,**kwargs):
	G = [ SymElem( "D3", cen=cell*Vec(1,0,0), axis=Vec(0,0,1), axis2=Vec(1,0,0)
		),
		  SymElem( "D3", cen=cell*Vec(1.66667,0.333333,0.333333), axis=Vec(0,0,-1), axis2=Vec(1,0,0)
		),
		]
	test_xtal(G,cell,tag='test_H32_D3',**kwargs)

#spacegroup	type	axis_1	axis_2 (D only)	origin	axis_1	axis_2 (D only)	origin	angle	offset	shift (angle=0 only)
#H32	D3	0,0,1	1,0,0	1,0,0	0,0,-1	1,0,0	1.66667,0.333333,0.333333	0	0.745356	0.333333
#H32	D3	0,0,1	0.5,0.866025,0	0.333333,0.666667,0.166667	0,0,-1	0.5,0.866025,0	0.666667,0.333333,-0.166667	0	0.471405	-0.333333

#F4132	T	0.57735,0.57735,0.57735	-	-0.5,0,0.5	-0.57735,-0.57735,-0.57735	-	-0.25,0.25,0.75	0	9.61E-17	0.433013

# def test_F4132_T(cell=80,**kwargs):
# 	G = [ SymElem( 'T', cen=cell*(Vec ( -0.5,0,0.5 )), axis=Vec(0.57735,0.57735,0.57735), #axis2=Vec(0.866025,-0.5,0) 
#  		),
# 		  SymElem( 'T', cen=cell*(Vec ( -0.25,0.25,0.75 )), axis=Vec(-0.57735,-0.57735,-0.57735), #axis2=Vec(0.866025,-0.5,0) 
#  		),
#  	    ]
#  	test_xtal(G,cell,tag='test_F4132_T',**kwargs)

# def test_F23_T(cell=80,**kwargs):
# 	G = [ SymElem( 'T', cen=cell*(Vec ( -0.5,-0.5,0 )), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(0.866025,-0.5,0) 
#  		),
# 		  SymElem( 'T', cen=cell*(Vec ( -0.5,0,0.5 )), axis=Vec(-0.57735,0.57735,0.57735), #axis2=Vec(0.866025,-0.5,0) 
#  		),
#  	    ]
#  	test_xtal(G,cell,tag='test_F23_T',**kwargs)






































