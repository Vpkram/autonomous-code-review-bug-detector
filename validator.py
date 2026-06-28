import ast
import difflib

# Validates a Python fix against the original code
def validate_fix(original: str, fix: str) -> dict:
    """
    Validates the fix for syntactic correctness, computes a unified diff,
    calculates the difference in line count, and assigns a quality score.
    """
    try:
        # Check syntax
        try:
            ast.parse(fix)
            is_valid = True
        except Exception:
            return {
                "is_valid": False,
                "diff": "",
                "lines_changed": 0,
                "score": 0.0
            }

        orig_lines = original.splitlines()
        fix_lines = fix.splitlines()

        orig_line_count = len(orig_lines)
        fix_line_count = len(fix_lines)

        # Generate unified diff
        diff_lines = list(difflib.unified_diff(
            orig_lines,
            fix_lines,
            fromfile="original",
            tofile="fix",
            lineterm=""
        ))
        diff_str = "\n".join(diff_lines)

        # Calculate lines_changed as absolute difference in line count
        lines_changed = abs(orig_line_count - fix_line_count)

        # Score logic
        score = 0.5
        if fix_line_count <= orig_line_count:
            score = 0.8
        if len(fix) < len(original):
            score = 1.0

        return {
            "is_valid": is_valid,
            "diff": diff_str,
            "lines_changed": lines_changed,
            "score": score
        }

    except Exception:
        return {
            "is_valid": False,
            "diff": "",
            "lines_changed": 0,
            "score": 0.0
        }
