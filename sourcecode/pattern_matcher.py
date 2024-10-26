import re
import random
def calculate_max_semantic_strength(line):
    strengths = []

    # Heuristics based on specific code features
    if '=' in line and not any(keyword in line for keyword in ['for', 'while']):  # Assignment
        strengths.append(('assignment', 20))
    if '+' in line:  # Addition
        strengths.append(('addition', 25))
    if re.search(r'\bint\b|\blong\b|\bchar\b|\bWORD\b|\bBYTE\b|\bvoid\b', line):  # Variable definitions
        strengths.append(('variable', 26))
    if 'return' in line:  # return
        strengths.append(('return', 25))
    if 'for' in line or 'while' in line:  # Loops
        strengths.append(('loop', 25))
    if 'if' in line or 'else' in line:  # Conditional statements
        strengths.append(('conditional', 25))
    if re.search(r'\w+\s*\(.*\)', line):  # Function calls
        strengths.append(('function', 20))

    # Keywords
    keywords = [r'\(_DWORD\b', r'\(_BYTE\b', r'\(_QWORD\b']
    if any(re.search(keyword, line) for keyword in keywords):  # _DWORD, _BYTE or _QWORD keyword
        strengths.append(('_TYPE', 26))

    return max(strengths, key=lambda x: x[1]) if strengths else (None, 0)

def match_patterns(query_lines):
    # Remove the first line (line number definition) and empty lines and braces
    relevant_lines = [line for line in query_lines[1:] if line.strip() and line.strip() not in ['{', '}']]

    # Calculate semantic strength for each line
    line_strengths = [(line, *calculate_max_semantic_strength(line)) for line in relevant_lines]

    # Debugging output for each line's semantic value and strength
    # print("\nDebugging output for semantic values and strengths:")
    # for line, line_type, strength in line_strengths:
    #     print(f"Line: {line}\nType: {line_type}\nStrength: {strength}\n")

    # Sort lines by semantic strength
    line_strengths.sort(key=lambda x: x[2], reverse=True)

    # Determine the number of lines to output
    total_lines = len(relevant_lines)
    if total_lines <= 5:
        output_lines = total_lines
    else:
        output_lines = min(5 + (total_lines - 5) // 9, 10)

    # Debugging output for total lines and output lines
    print(f"Total lines: {total_lines}")
    print(f"Output lines: {output_lines}")

    # Select top line for each type
    selected_lines = []
    seen_types = set()

    # First pass: ensure each type has at most one line
    for line, line_type, strength in line_strengths:
        if line_type and line_type not in seen_types:
            selected_lines.append(line)
            seen_types.add(line_type)
        if len(selected_lines) == output_lines:
            break

    # Second pass: add more lines to reach the required number of output lines
    if len(selected_lines) < output_lines:
        for line, line_type, strength in line_strengths:
            if line not in selected_lines:
                selected_lines.append(line)
            if len(selected_lines) == output_lines:
                break

    # Ensure all types are represented
    remaining_types = {'assignment', 'addition', 'variable', 'return', 'loop', 'conditional', 'function', '_TYPE'} - seen_types
    if remaining_types:
        for line, line_type, strength in line_strengths:
            if line_type in remaining_types:
                selected_lines.append(line)
                remaining_types.remove(line_type)
            if not remaining_types:
                break

    return selected_lines

def select_random_lines(query_lines):
    """
    Selects 6 random lines from the code to use as a reference group.
    """
    # Remove the first line and any empty lines or braces
    relevant_lines = [line for line in query_lines[1:] if line.strip() and line.strip() not in ['{', '}']]

    # Ensure there are enough lines to select from
    if len(relevant_lines) < 6:
        return relevant_lines  # Return all lines if less than 6 are available

    # Randomly select 6 unique lines
    random_lines = random.sample(relevant_lines, 6)
    return random_lines

# # Example usage
# code_input = """
# __fastcall binarySearch(__int64 a1, unsigned int a2, unsigned int a3, unsigned int a4)
# {
#   __int64 result;
#   unsigned int v5; // I4
#   if ( (int)a3 < (int)a4 )
#   {
#     v5 = (int)(a4 - 1) / 2 + a3; // I3
#     if ( a2 == *(_DWORD *)(4LL * (int)v5 + a1) ) // I1
#     {
#       result = v5 + 1; // I3
#     }
#     else if ( (signed int)a2 >= *(_DWORD *)(4LL * (int)v5 + a1) ) // I1
#     {
#       result = binarySearch(a1, a2, v5 + 1, a4);
#     }
#     else
#     {
#       result = binarySearch(a1, a2, a3, v5 - 1);
#     }
#   }
#   else if ( (signed int)a2 <= *(_DWORD *)(4LL * (int)a3 + a1) ) // I1
#   {
#     result = a3;
#   }
#   else
#   {
#     result = a3 + 1; // I3
#   }
#   return result;
# }
#
# """
#
# # Split the input into lines
# query_lines = code_input.strip().split('\n')
#
# # Call the function with the split lines
# selected_lines = match_patterns(query_lines)
#
# # Check if output is as expected
# print("\nSelected lines:")
# for line in selected_lines:
#     print(line)
