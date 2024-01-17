from collections import namedtuple
from .algorithms.mono_window import MonoWindowLST
from .algorithms.split_window.algorithms import (
    SplitWindowJiminezMunozLST,
    SplitWindowKerrLST,
    SplitWindowMcMillinLST,
    SplitWindowPriceLST,
    SplitWindowSobrino1993LST,
)

# Define namedtuples to organize available algorithms
SingleWindowAlgorithms = {
    "mono-window": MonoWindowLST # Algorithm for single window method
}

SplitWindowAlgorithms = {
    "jiminez-munoz": SplitWindowJiminezMunozLST,
    "kerr": SplitWindowKerrLST,
    "mc-millin": SplitWindowMcMillinLST,
    "price": SplitWindowPriceLST,
    "sobrino-1993": SplitWindowSobrino1993LST
}

# Organize algorithms using a namedtuple for clarity
Algorithms = namedtuple("Algorithms", ("single_window", "split_window"))
default_algorithms = Algorithms(SingleWindowAlgorithms, SplitWindowAlgorithms)

# 'default_algorithms' contains available algorithms for both single and split window methods
# Access them using 'default_algorithms.single_window' and 'default_algorithms.split_window'
