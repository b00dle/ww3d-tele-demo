#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script

class Text(avango.script.Script):
    ''' Text styled environment prop. '''

    tex_paths = {
        'A' : 'data/textures/char/A.png',
        'B' : 'data/textures/char/B.png',
        'C' : 'data/textures/char/C.png',
        'D' : 'data/textures/char/D.png',
        'E' : 'data/textures/char/E.png',
        'F' : 'data/textures/char/F.png',
        'G' : 'data/textures/char/G.png',
        'H' : 'data/textures/char/H.png',
        'I' : 'data/textures/char/I.png',
        'J' : 'data/textures/char/J.png',
        'K' : 'data/textures/char/K.png',
        'L' : 'data/textures/char/L.png',
        'M' : 'data/textures/char/M.png',
        'N' : 'data/textures/char/N.png',
        'O' : 'data/textures/char/O.png',
        'P' : 'data/textures/char/P.png',
        'Q' : 'data/textures/char/Q.png',
        'R' : 'data/textures/char/R.png',
        'S' : 'data/textures/char/S.png',
        'T' : 'data/textures/char/T.png',
        'U' : 'data/textures/char/U.png',
        'V' : 'data/textures/char/V.png',
        'W' : 'data/textures/char/W.png',
        'X' : 'data/textures/char/X.png',
        'Y' : 'data/textures/char/Y.png',
        'Z' : 'data/textures/char/Z.png',
        '0' : 'data/textures/char/0.png',
        '1' : 'data/textures/char/1.png',
        '2' : 'data/textures/char/2.png',
        '3' : 'data/textures/char/3.png',
        '4' : 'data/textures/char/4.png',
        '5' : 'data/textures/char/5.png',
        '6' : 'data/textures/char/6.png',
        '7' : 'data/textures/char/7.png',
        '8' : 'data/textures/char/8.png',
        '9' : 'data/textures/char/9.png',
        ' ' : 'data/textures/char/Space.png',
        '?' : 'data/textures/char/QMark.png',
        '!' : 'data/textures/char/!.png',
        '.' : 'data/textures/char/Period.png',
        ',' : 'data/textures/char/comma.png',
        ';' : 'data/textures/char/semi.png',
        '(' : 'data/textures/char/brack_left.png',
        ')' : 'data/textures/char/brack_right.png',
        '{' : 'data/textures/char/curv_brack_left.png',
        '}' : 'data/textures/char/curv_brack_right.png',
        '[' : 'data/textures/char/rect_brack_left.png',
        ']' : 'data/textures/char/rect_brack_right.png'
    }

    def __init__(self):
        self.super(Text).__init__()

        # stores root node
        self.node = None

    def my_constructor(self, PARENT_NODE, TEXT, SCALE=0.3):
        self._scale = SCALE

        self.node = avango.gua.nodes.TransformNode(Name = "text_base")
        PARENT_NODE.Children.value.append(self.node)

        self.set_text(TEXT)

    def set_text(self, TEXT):
        ''' clears previous text and sets new char geometry. '''
        self.clear()
        _loader = avango.gua.nodes.TriMeshLoader() # get trimesh loader to load external meshes

        t_upper = TEXT.upper()
        x_offset = self._scale * 2.0
        start_x = -1 * (len(t_upper)/2.0*x_offset)
        i = 0
        for c in t_upper:
            if c not in self.tex_paths:
                c = ' '
            c_obj = _loader.create_geometry_from_file(
                "text_"+str(i)+"_geometry",
                "data/objects/plane.obj",
                avango.gua.LoaderFlags.DEFAULTS
            )
            c_obj.Material.value.set_uniform("ColorMap", self.tex_paths[c])
            c_obj.Transform.value = avango.gua.make_trans_mat(start_x+i*x_offset,0,0) *\
                avango.gua.make_scale_mat(self._scale, self._scale, self._scale)
            self.node.Children.value.append(c_obj)
            i += 1

    def clear(self):
        ''' removes all character geometries. '''
        while len(self.node.Children.value) > 0:
            self.node.Children.value.remove(self.node.Children.value[0])
