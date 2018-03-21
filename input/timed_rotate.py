import avango
import avango.script
import avango.gua

class TimedRotate(avango.script.Script):
    TimeIn = avango.SFFloat()
    MatrixOut = avango.gua.SFMatrix4()

    def evaluate(self):
        self.MatrixOut.value = avango.gua.make_trans_mat(
            0.0, -1.0, -2.0) * avango.gua.make_rot_mat(10 * self.TimeIn.value *
                                                       2.0, 0.0, 1.0, 0.0)