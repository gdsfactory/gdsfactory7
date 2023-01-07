from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel


class LayerLevel(BaseModel):
    """Level for 3D LayerStack.

    Parameters:
        layer: (GDSII Layer number, GDSII datatype).
        thickness: layer thickness in um.
        thickness_tolerance: layer thickness tolerance in um.
        zmin: height position where material starts in um.
        material: material name.
        sidewall_angle: in degrees with respect to normal.
        width_to_z: if sidewall_angle, relative z-position
            (0 --> zmin, 1 --> zmin + thickness).
        z_to_bias: parametrizes shrinking/expansion of the design GDS layer
            when extruding from zmin (0) to zmin + thickness (1).
            Defaults no buffering [[0, 1], [0, 0]].
        info: simulation_info and other types of metadata.
            mesh_order: lower mesh order (1) will have priority over higher
                mesh order (2) in the regions where materials overlap.
            refractive_index: refractive_index
                can be int, complex or function that depends on wavelength (um).
            type: grow, etch, implant, or background.
            mode: octagon, taper, round.
                https://gdsfactory.github.io/klayout_pyxs/DocGrow.html
            into: etch into another layer.
                https://gdsfactory.github.io/klayout_pyxs/DocGrow.html
            doping_concentration: for implants.
            resistivity: for metals.
            bias: in um for the etch.
    """

    layer: Optional[Tuple[int, int]]
    thickness: float
    thickness_tolerance: Optional[float] = None
    zmin: float
    material: Optional[str] = None
    sidewall_angle: float = 0.0
    width_to_z: float = 0.0
    z_to_bias: Optional[Tuple[List[float], List[float]]] = None
    info: Dict[str, Any] = {}


class LayerStack(BaseModel):
    """For simulation and 3D rendering.

    Parameters:
        layers: dict of layer_levels.
    """

    layers: Dict[str, LayerLevel]

    def get_layer_to_thickness(self) -> Dict[Tuple[int, int], float]:
        """Returns layer tuple to thickness (um)."""
        return {
            level.layer: level.thickness
            for level in self.layers.values()
            if level.thickness
        }

    def get_layer_to_zmin(self) -> Dict[Tuple[int, int], float]:
        """Returns layer tuple to z min position (um)."""
        return {
            level.layer: level.zmin for level in self.layers.values() if level.thickness
        }

    def get_layer_to_material(self) -> Dict[Tuple[int, int], str]:
        """Returns layer tuple to material name."""
        return {
            level.layer: level.material
            for level in self.layers.values()
            if level.thickness
        }

    def get_layer_to_sidewall_angle(self) -> Dict[Tuple[int, int], str]:
        """Returns layer tuple to material name."""
        return {
            level.layer: level.sidewall_angle
            for level in self.layers.values()
            if level.thickness
        }

    def get_layer_to_info(self) -> Dict[Tuple[int, int], Dict]:
        """Returns layer tuple to info dict."""
        return {level.layer: level.info for level in self.layers.values()}

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        return {level_name: dict(level) for level_name, level in self.layers.items()}

    def get_klayout_3d_script(
        self,
        klayout28: bool = True,
        print_to_console: bool = True,
        layer_display_properties=None,
        dbu: Optional[float] = 0.001,
    ) -> str:
        """Prints script for 2.5 view KLayout information.

        You can add this information in your tech.lyt take a look at
        gdsfactory/klayout/tech/tech.lyt
        """
        out = ""
        for layer_name, level in self.layers.items():
            layer = level.layer
            zmin = level.zmin
            zmax = zmin + level.thickness

            if layer is None:
                continue

            if dbu:
                rnd_pl = len(str(dbu).split(".")[-1])
                zmin = round(zmin, rnd_pl)
                zmax = round(zmax, rnd_pl)

            if klayout28:
                txt = (
                    f"z("
                    f"input({layer[0]}, {layer[1]}), "
                    f"zstart: {zmin}, "
                    f"zstop: {zmax}, "
                    f"name: '{layer_name}: {level.material} {layer[0]}/{layer[1]}'"
                )
                if layer_display_properties:
                    txt += ", "
                    props = layer_display_properties.get_from_tuple(layer)
                    if props.fill_color == props.frame_color:
                        txt += f"color: {props.frame_color}"
                    else:
                        txt += (
                            f"fill: {props.fill_color}, " f"frame: {props.frame_color}"
                        )

                txt += ")"

            else:
                txt = f"{layer[0]}/{layer[1]}: {zmin} {zmax}"
            out += f"{txt}\n"

            if print_to_console:
                print(txt)
        if klayout28:
            out += "\nend\n"
        return out


if __name__ == "__main__":
    import pickle

    from gdsfactory.generic_tech import LAYER_STACK

    ls = LAYER_STACK
    data = pickle.dumps(ls)
    ls2 = pickle.loads(data)

    # ls_json = ls.json()
    # d = json.loads(ls.json())
    # ls2 = LayerStack.from_dict(d)
    # ls2 = LayerStack.parse_raw(ls_json)