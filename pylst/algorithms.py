# pylst/algorithm_runner.py
"""
Core runner / dispatcher for different LST (Land Surface Temperature) computation methods.

This module provides the LSTAlgorithmRunner class, which allows registering
and executing various LST algorithms in a uniform way.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional


class LSTAlgorithmRunner:
    """
    Dispatcher for Land Surface Temperature (LST) computation methods.

    It maps short, user-friendly method names to concrete functions or callable
    classes that perform LST retrieval.

    Typical usage (after instantiation in __init__.py):
        from pylst import runner

        # Using explicit method name
        lst = runner.run("split-window", tir1=..., tir2=..., emissivity=...)

        # Using default method (if configured)
        lst = runner.run(emissivity=0.97, ndvi=..., ...)
    """

    def __init__(
        self,
        algorithms: Dict[str, Callable[..., Any]],
        default_method: Optional[str] = None,
    ) -> None:
        """
        Parameters
        ----------
        algorithms : dict[str, callable]
            Mapping of method names → computation functions or classes
        default_method : str, optional
            Name of the algorithm to use when no method is explicitly provided
        """
        self.algorithms: Dict[str, Callable[..., Any]] = algorithms.copy()
        self.default_method = default_method

    def run(
        self,
        method: Optional[str] = None,
        /,                      # method is positional-only
        **kwargs: Any,
    ) -> Any:
        """
        Run the requested (or default) LST algorithm with the given arguments.

        Parameters
        ----------
        method : str, optional
            Name of the algorithm to execute. If omitted and a default is set,
            the default method is used.
        **kwargs
            Arguments forwarded directly to the selected algorithm.

        Returns
        -------
        Any
            The result of the algorithm (typically ndarray, dict, or custom object)

        Raises
        ------
        ValueError
            If no valid method is provided or the requested method doesn't exist
        TypeError
            If the registered algorithm cannot be called properly
        """
        selected_method = method or self.default_method

        if selected_method is None:
            raise ValueError(
                "No method specified and no default_method is configured.\n"
                f"Available methods: {', '.join(sorted(self.algorithms.keys()))}"
            )

        if selected_method not in self.algorithms:
            raise ValueError(
                f"Unknown LST method: '{selected_method}'\n"
                f"Available methods: {', '.join(sorted(self.algorithms.keys()))}"
            )

        algorithm = self.algorithms[selected_method]

        # ─── Execute the algorithm ───────────────────────────────────────
        try:
            if callable(algorithm):
                return algorithm(**kwargs)

            # Fallback: treat as class → instantiate and call
            instance = algorithm()
            if hasattr(instance, "run") and callable(instance.run):
                return instance.run(**kwargs)
            if callable(instance):
                return instance(**kwargs)

            raise TypeError(
                f"Algorithm '{selected_method}' is neither directly callable "
                "nor provides a .run() method after instantiation."
            )

        except TypeError as exc:
            raise TypeError(
                f"Failed to call algorithm '{selected_method}' — likely missing "
                f"or incorrect arguments.\nOriginal error: {exc}"
            ) from exc

    def available_methods(self) -> list[str]:
        """Return a sorted list of all registered algorithm names."""
        return sorted(self.algorithms.keys())

    def __repr__(self) -> str:
        methods_str = ", ".join(f"'{m}'" for m in self.available_methods())
        default_part = (
            f" (default: '{self.default_method}')" if self.default_method else ""
        )
        return f"LSTAlgorithmRunner[{methods_str}]{default_part}"


# For convenience during development/testing (can be removed or commented out)
if __name__ == "__main__":
    # Quick smoke test
    def dummy_algo(**kwargs):
        return {"result": "dummy", "kwargs_received": kwargs}

    runner = LSTAlgorithmRunner(
        {"test": dummy_algo},
        default_method="test"
    )
    print(runner)
    print(runner.run(a=1, b=2))