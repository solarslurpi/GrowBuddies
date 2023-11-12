COMPARISON_FUNCTIONS = {
    "greater_than": lambda x, max_val: x > max_val,
    "less_than": lambda x, max_val: x < max_val,
    "within_range": lambda x, min_val, max_val: min_val <= x <= max_val,
}
