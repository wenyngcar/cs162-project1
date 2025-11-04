from filters.smoothing_filters import apply_average_filter, apply_median_filter
from filters.sharpening_filters import (
    highpass_filtering_with_laplacian_operator,
    unsharp_masking,
    highboost_filtering,
)
from filters.gradient import gradient_sobel

FILTERS = {
    "Averaging": {
        "fn": apply_average_filter,
        "params": [("kernel_size", "int", 3, {"min": 3, "odd": True})],
    },
    "Median": {
        "fn": apply_median_filter,
        "params": [("kernel_size", "int", 3, {"min": 3, "odd": True})],
    },
    "Laplacian (Highpass)": {
        "fn": highpass_filtering_with_laplacian_operator,
        "params": [],
    },
    "Unsharp Masking": {
        "fn": unsharp_masking,
        "params": [("kernel_size", "int", 3, {"min": 3, "odd": True})],
    },
    "Highboost": {
        "fn": highboost_filtering,
        "params": [
            ("boost_factor", "float", 2.0, {"min": 1.0, "max": 3}),
            ("kernel_size", "int", 3, {"min": 3, "odd": True}),
        ],
    },
    "Gradient (Sobel)": {"fn": gradient_sobel, "params": []},
}

