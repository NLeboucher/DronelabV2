class Helpers:
    def _math_proportionnal(value, out="reel"):
            match out:
                case "pyg":
                    in_min=0 
                    in_max=20 
                    out_min=0 
                    out_max=1000
                case "reel":
                    in_min=0 
                    in_max=1000 
                    out_min=0 
                    out_max=20
            return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def set_reel_position(position):
        realPosition = pg.Vector2(_math_proportionnal(value=position.x,out="reel"),Vehicle._math_proportionnal(value=position.y,out="reel"))
        return realPosition
    def set_pyg_position(realPosition):
        position = pg.Vector2(_math_proportionnal(value=realPosition.x,out="pyg"),Vehicle._math_proportionnal(value=realPosition.y,out="pyg"))
        return position