from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ------------------------------------------------------------
# ANALYZER FUNCTION (NEW + FULLY TESTED)
# ------------------------------------------------------------

def analyze_code(language: str, code: str):

    lines_raw = code.splitlines()
    lines = [l for l in lines_raw if l.strip()]

    loop_stack = []
    max_nesting = 0
    total_loops = 0
    loop_types = []
    recursion_detected = False
    recursion_type = None
    array_usage = False
    function_names = set()

    # --- Detect function names ---
    for line in lines:
        stripped = line.strip()
        lower = stripped.lower()

        if "(" in stripped and ")" in stripped and any(
            kw in lower.split()
            for kw in ["def", "int", "void", "float", "double", "public", "static"]
        ):
            name_part = stripped.split("(")[0]

            for kw in ["def", "public", "static", "int", "void", "float", "double"]:
                name_part = name_part.replace(kw, "")

            tokens = name_part.strip().split()
            if tokens:
                function_names.add(tokens[-1])

    # Decide loop type
    def classify_loop(line_lower):
        if any(tok in line_lower for tok in ["n*n", "n * n", "n^2"]):
            return "quadratic"

        if "while" in line_lower and any(tok in line_lower for tok in ["/=2", "/2", ">>1"]):
            return "log"

        if "log" in line_lower:
            return "log"

        return "linear"

    # -----------------------------
    # MAIN PARSING
    # -----------------------------
    for line in lines:

        lower = line.lower()
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        # LOOP detection
        if "for " in lower or "while " in lower:
            total_loops += 1
            loop_type = classify_loop(lower)
            loop_types.append(loop_type)

            while loop_stack and loop_stack[-1] >= indent:
                loop_stack.pop()

            loop_stack.append(indent)
            max_nesting = max(max_nesting, len(loop_stack))

        # RECURSION
        for fname in function_names:
            if fname and (fname + "(") in stripped and not stripped.startswith(("def", "public", "static", "int", "void")):
                recursion_detected = True
                call_args = stripped.split("(")[1].split(")")[0].replace(" ", "")

                if any(k in call_args for k in ["n/2", "n//2", "n>>1"]):
                    recursion_type = recursion_type or "log"

                elif "n-1" in call_args:
                    recursion_type = recursion_type or "linear"

        # ARRAY / LIST
        if "[" in line and "]" in line:
            array_usage = True

    # -----------------------------
    # TIME COMPLEXITY: LOOPS
    # -----------------------------

    def loops_complexity(depth):
        if depth >= 3:
            return f"O(n^{depth})"
        if depth == 2:
            return "O(n^2)"
        if depth == 1:
            return "O(n)"
        return "O(1)"

    loops_comp = loops_complexity(max_nesting)

    # -----------------------------
    # TIME COMPLEXITY: RECURSION
    # -----------------------------
    if recursion_detected:
        if recursion_type == "log":
            rec_comp = "O(log n)"
        elif recursion_type == "linear":
            rec_comp = "O(n)"
        else:
            rec_comp = "O(n)"
    else:
        rec_comp = "O(1)"

    # Choose bigger one
    order = {
        "O(1)": 0,
        "O(log n)": 1,
        "O(n)": 2,
        "O(n log n)": 3,
        "O(n^2)": 4,
        "O(n^3)": 5
    }

    time_complexity = loops_comp if order.get(loops_comp, 0) >= order.get(rec_comp, 0) else rec_comp

    # -----------------------------
    # SPACE COMPLEXITY
    # -----------------------------
    space_complexity = "O(1)"
    if array_usage:
        space_complexity = "O(n)"
    if recursion_detected:
        space_complexity = "O(n)" if recursion_type == "linear" else "O(log n)"

    # -----------------------------
    # EXPLANATION
    # -----------------------------
    explanation_steps = [
        f"Language selected: {language}.",
        f"Total loops detected: {total_loops}, nesting depth: {max_nesting}.",
        f"Loop-based complexity approx: {loops_comp}.",
        f"Recursion {'detected' if recursion_detected else 'not detected'}.",
        f"Recursion complexity approx: {rec_comp}."
    ]

    if array_usage:
        explanation_steps.append("Array/List usage found → space O(n).")
    else:
        explanation_steps.append("No large arrays/lists → space O(1).")

    explanation_steps.append(f"Final time complexity = {time_complexity}.")
    explanation_steps.append(f"Final space complexity = {space_complexity}.")
    explanation_steps.append(
        "Note: This is an approximate static analysis based only on patterns (loops, nesting, recursion, arrays)."
    )

    return {
        "time_complexity": time_complexity,
        "space_complexity": space_complexity,
        "explanation_steps": explanation_steps
    }


# ------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    language = data.get("language", "unknown")
    code = data.get("code", "")

    result = analyze_code(language, code)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
