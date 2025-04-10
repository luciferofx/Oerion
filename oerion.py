import re

variables = {}
functions = {}

def evaluate_expr(expr):
    try:
        return eval(expr, {}, variables)
    except Exception as e:
        print("Evaluation Error:", e)
        return None

def interpret_line(line):
    line = line.strip()

    # Return from function
    if line.startswith("return "):
        value = evaluate_expr(line[7:].strip())
        return ("RETURN", value)

    # Print multiple values
    elif line.startswith("print "):
        content = line[6:].strip()
        if "," in content:
            parts = content.split(",")
            output = [str(evaluate_expr(part.strip())) for part in parts]
            print(" ".join(output))
        elif content.startswith('"') and content.endswith('"'):
            print(content[1:-1])
        elif content in variables:
            print(variables[content])
        else:
            val = evaluate_expr(content)
            if val is not None:
                print(val)
            else:
                print("Syntax Error: Unknown print content")

    # Variable assignment
    elif line.startswith("let "):
        match = re.match(r"let (\w+) = (.+)", line)
        if match:
            var, value = match.groups()
            try:
                variables[var] = evaluate_expr(value)
            except:
                print("Syntax Error: Invalid expression")
        else:
            print("Syntax Error in variable assignment")

    # If condition
    elif line.startswith("if "):
        condition = line[3:].strip(":\n")
        try:
            return "IF_TRUE" if eval(condition, {}, variables) else "IF_FALSE"
        except:
            print("Syntax Error in if condition")

    elif line.startswith("elif "):
        condition = line[5:].strip(":\n")
        try:
            return "ELIF_TRUE" if eval(condition, {}, variables) else "ELIF_FALSE"
        except:
            print("Syntax Error in elif condition")

    elif line == "else:":
        return "ELSE"

    # Function-like operations
    elif match := re.match(r"to_(int|str|float)\((.+)\)", line):
        conv, val = match.groups()
        val = evaluate_expr(val.strip())
        result = {"int": int(val), "str": str(val), "float": float(val)}[conv]
        print(result)

    elif match := re.match(r"(\w+)\.append\((.+)\)", line):
        list_name, val = match.groups()
        if list_name in variables and isinstance(variables[list_name], list):
            variables[list_name].append(evaluate_expr(val))
        else:
            print("Error: Not a list")

    elif match := re.match(r"(\w+)\.remove\((.+)\)", line):
        list_name, val = match.groups()
        if list_name in variables and isinstance(variables[list_name], list):
            try:
                variables[list_name].remove(evaluate_expr(val))
            except ValueError:
                print("Value not in list")
        else:
            print("Error: Not a list")

    elif line.startswith("type "):
        var = line[5:].strip()
        if var in variables:
            print(type(variables[var]).__name__)
        else:
            print("Variable not found")

    elif line == "break":
        return "BREAK"

    elif line == "continue":
        return "CONTINUE"

    elif line.startswith("import "):
        file_to_import = line.split("import")[1].strip().replace('"', "")
        try:
            with open(file_to_import, 'r') as f:
                imported_code = f.read()
                run_code(imported_code)
        except FileNotFoundError:
            print(f"ImportError: File {file_to_import} not found")

    elif line.startswith("    "):
        return "INDENT:" + line.strip()

    elif line.startswith("try:"):
        return "TRY"

    elif line.startswith("except:"):
        return "EXCEPT"

    else:
        print("Unknown syntax:", line)

def run_code(code):
    global variables
    lines = code.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        # While loop
        if line.startswith("while "):
            condition = line[6:].strip(":\n")
            loop_block = []
            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                loop_block.append(lines[i].strip())
                i += 1
            while eval(condition, {}, variables):
                for stmt in loop_block:
                    result = interpret_line(stmt)
                    if result == "BREAK":
                        break
                    elif result == "CONTINUE":
                        continue
            continue

        # For loop
        elif line.startswith("for "):
            match = re.match(r"for (\w+) in range\((\d+)\):", line)
            if match:
                var, count = match.groups()
                count = int(count)
                loop_block = []
                i += 1
                while i < len(lines) and lines[i].startswith("    "):
                    loop_block.append(lines[i].strip())
                    i += 1
                for val in range(count):
                    variables[var] = val
                    for stmt in loop_block:
                        result = interpret_line(stmt)
                        if result == "BREAK":
                            break
                        elif result == "CONTINUE":
                            continue
                continue

        # Try-Except block
        elif line.startswith("try:"):
            try_block, except_block = [], []
            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                try_block.append(lines[i].strip())
                i += 1
            if i < len(lines) and lines[i].strip() == "except:":
                i += 1
                while i < len(lines) and lines[i].startswith("    "):
                    except_block.append(lines[i].strip())
                    i += 1
            try:
                for stmt in try_block:
                    interpret_line(stmt)
            except:
                for stmt in except_block:
                    interpret_line(stmt)
            continue

        interpret_line(lines[i])
        i += 1

# Entry point
if __name__ == "__main__":
    with open("example.oer", "r") as f:
        code = f.read()
        run_code(code)
