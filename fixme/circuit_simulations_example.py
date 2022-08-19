"""Demo of non-hierarchical circuit simulations."""
import jax.numpy as jnp
import sax
import gdsfactory as gf


def straight(wl=1.5, length=10.0, neff=2.4) -> sax.SDict:
    """Straight model."""
    return sax.reciprocal({("o1", "o2"): jnp.exp(2j * jnp.pi * neff * length / wl)})


def mmi1x2():
    """Assumes a perfect 1x2 splitter."""
    return sax.reciprocal(
        {
            ("o1", "o2"): 0.5**0.5,
            ("o1", "o3"): 0.5**0.5,
        }
    )


def bend_euler(wl=1.5, length=20.0):
    """Assumes reduced transmission for the euler bend compared to a straight."""
    return {k: 0.99 * v for k, v in straight(wl=wl, length=length).items()}


models = {
    "bend_euler": bend_euler,
    "mmi1x2": mmi1x2,
    "straight": straight,
}

if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt

    c = gf.components.mzi()
    c.show(show_ports=True)
    netlist = c.get_netlist_dict()
    circuit = sax.circuit_from_netlist(netlist=netlist, models=models)
    wl = np.linspace(1.5, 1.6)
    S = circuit(wl=wl)

    plt.figure(figsize=(14, 4))
    plt.title("MZI")
    plt.plot(1e3 * wl, jnp.abs(S["o1", "o2"]) ** 2)
    plt.xlabel("λ [nm]")
    plt.ylabel("T")
    plt.grid(True)
    plt.show()