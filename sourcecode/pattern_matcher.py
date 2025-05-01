import re
import random
import os
import sys

def calculate_semantic_intensity(line, feature_weights):
    """
    Calculate the semantic intensity for a line based on feature weights.
    Returns a dictionary of features detected and the total intensity.
    """
    features = {}
    total_intensity = 0

    # Check for various syntax constructs
    if '=' in line and not any(keyword in line for keyword in ['for', 'while']):  # Assignment
        features['assignment'] = feature_weights.get('assignment', 20)
        total_intensity += features['assignment']
    
    if '+' in line:  # Addition
        features['addition'] = feature_weights.get('addition', 25)
        total_intensity += features['addition']
    
    if re.search(r'\bint\b|\blong\b|\bchar\b|\bWORD\b|\bBYTE\b|\bvoid\b', line):  # Variable definitions
        features['variable'] = feature_weights.get('variable', 26)
        total_intensity += features['variable']
    
    if 'return' in line:  # return
        features['return'] = feature_weights.get('return', 25)
        total_intensity += features['return']
    
    if 'for' in line or 'while' in line:  # Loops
        features['loop'] = feature_weights.get('loop', 25)
        total_intensity += features['loop']
    
    if 'if' in line or 'else' in line:  # Conditional statements
        features['conditional'] = feature_weights.get('conditional', 25)
        total_intensity += features['conditional']
    
    if re.search(r'\w+\s*\(.*\)', line):  # Function calls
        features['function'] = feature_weights.get('function', 20)
        total_intensity += features['function']

    # Keywords
    if re.search(r'\(_DWORD\b|\(_BYTE\b|\(_QWORD\b', line):  # _DWORD, _BYTE or _QWORD keyword
        features['_TYPE'] = feature_weights.get('_TYPE', 26)
        total_intensity += features['_TYPE']

    return features, total_intensity

def generate_semantic_intensity_lines(lines, min_lines=5, base_lines=5, threshold=5, step=9, max_lines=10, feature_weights=None):
    """
    Implements the Dynamic Semantic Intensity Retrieval Algorithm.
    
    Args:
        lines: List of code lines to analyze
        min_lines: Minimum number of lines to select
        base_lines: Base number of lines to select
        threshold: Threshold for total lines to adjust selection
        step: Step size for dynamic line selection
        max_lines: Maximum number of lines to select
        feature_weights: Dictionary with weights for each feature type
    
    Returns:
        List of selected lines based on semantic intensity
    """
    # Remove the first line (line number definition) and empty lines and braces
    relevant_lines = [line for line in lines[1:] if line.strip() and line.strip() not in ['{', '}']]
    
    # Use default weights if not provided
    if feature_weights is None:
        feature_weights = {
            'assignment': 20,
            'addition': 25,
            'variable': 26,
            'return': 25,
            'loop': 25,
            'conditional': 25,
            'function': 20,
            '_TYPE': 26
        }
    
    # Calculate semantic intensity for each line
    line_intensities = []
    for line in relevant_lines:
        features, total_intensity = calculate_semantic_intensity(line, feature_weights)
        line_intensities.append((line, features, total_intensity))
    
    # Sort lines by semantic intensity
    line_intensities.sort(key=lambda x: x[2], reverse=True)
    
    # Determine the number of lines to output dynamically
    total_lines = len(relevant_lines)
    if total_lines <= min_lines:
        k = total_lines
    else:
        k = min(base_lines + (total_lines - threshold) // step, max_lines)
    
    # Debug information
    print(f"Total lines: {total_lines}")
    print(f"Output lines: {k}")
    
    # Select top lines prioritizing diverse construct types
    selected_lines = []
    seen_types = set()
    
    # First pass: ensure each type has at least one representation if possible
    for line, features, _ in line_intensities:
        # Get the most significant feature for this line
        if features:
            most_significant = max(features.items(), key=lambda x: x[1])
            feature_type = most_significant[0]
            
            if feature_type not in seen_types:
                selected_lines.append(line)
                seen_types.add(feature_type)
        
        if len(selected_lines) >= k:
            break
    
    # Second pass: add more lines to reach the required number
    if len(selected_lines) < k:
        for line, _, _ in line_intensities:
            if line not in selected_lines:
                selected_lines.append(line)
            if len(selected_lines) >= k:
                break
    
    return selected_lines

def load_feature_weights_from_statistics(filename):
    """
    Generate feature weights by analyzing the frequency of different syntax constructs 
    in the provided file (fidelity_new.c)
    
    Args:
        filename: Path to the fidelity_new.c file
    
    Returns:
        Dictionary with feature weights based on frequency analysis
    """
    if not filename or not os.path.exists(filename):
        print(f"Error: File {filename} not found. Please provide a valid path to the fidelity_new.c file.")
        sys.exit(1)
    
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        
        # Count occurrences of each syntax construct
        counts = {
            'assignment': len(re.findall(r'[^=!<>]=[^=]', content)),  # Assignment but not ==, >=, etc.
            'addition': len(re.findall(r'[+]', content)),  # Addition operations
            'variable': len(re.findall(r'\b(int|long|char|WORD|BYTE|void)\b', content)),  # Variable definitions
            'return': len(re.findall(r'\breturn\b', content)),  # Return statements
            'loop': len(re.findall(r'\b(for|while)\b', content)),  # Loops
            'conditional': len(re.findall(r'\b(if|else)\b', content)),  # Conditionals
            'function': len(re.findall(r'\w+\s*\([^)]*\)\s*{', content)),  # Function definitions
            '_TYPE': len(re.findall(r'\(_DWORD\b|\(_BYTE\b|\(_QWORD\b', content))  # Type keywords
        }
        
        # Make sure we found at least some constructs
        total_constructs = sum(counts.values())
        if total_constructs == 0:
            print("Error: No syntax constructs found in the file. Please check if the file format is correct.")
            sys.exit(1)
        
        weights = {}
        min_weight = 20
        max_weight = 30
        weight_range = max_weight - min_weight
        
        # Calculate percentage distribution of each construct type
        print(f"\nConstruct distribution in {filename}:")
        for construct, count in counts.items():
            percentage = (count / total_constructs) * 100
            print(f"  {construct}: {count} occurrences ({percentage:.2f}%)")
            
            # Calculate weight based on frequency
            weight = min_weight + int((count / total_constructs) * 100) % weight_range
            weights[construct] = weight
            
        print(f"\nGenerated weights from {filename}:")
        for construct, weight in weights.items():
            print(f"  {construct}: {weight}")
            
        return weights
        
    except Exception as e:
        print(f"Error analyzing file {filename}: {str(e)}")
        sys.exit(1)

# Example usage
if __name__ == "__main__":
    import sys
    
    # Check if fidelity_new.c file path is provided as an argument
    fidelity_file = "fidelity_new.c"
    if len(sys.argv) > 1:
        fidelity_file = sys.argv[1]
    
    # Check if code file is provided as an argument
    code_file = None
    if len(sys.argv) > 2:
        code_file = sys.argv[2]
    
    # Either use provided code file or example code
    if code_file:
        try:
            with open(code_file, 'r', encoding='utf-8', errors='ignore') as f:
                code_input = f.read()
        except Exception as e:
            print(f"Error reading code file {code_file}: {str(e)}")
            sys.exit(1)
    else:
        # Example code
        code_input = '''
__fastcall binarySearch(__int64 a1, unsigned int a2, unsigned int a3, unsigned int a4)
{
  __int64 result;
  unsigned int v5; // I4
  if ( (int)a3 < (int)a4 )
  {
    v5 = (int)(a4 - 1) / 2 + a3; // I3
    if ( a2 == *(_DWORD *)(4LL * (int)v5 + a1) ) // I1
    {
      result = v5 + 1; // I3
    }
    else if ( (signed int)a2 >= *(_DWORD *)(4LL * (int)v5 + a1) ) // I1
    {
      result = binarySearch(a1, a2, v5 + 1, a4);
    }
    else
    {
      result = binarySearch(a1, a2, a3, v5 - 1);
    }
  }
  else if ( (signed int)a2 <= *(_DWORD *)(4LL * (int)a3 + a1) ) // I1
  {
    result = a3;
  }
  else
  {
    result = a3 + 1; // I3
  }
  return result;
}
'''
    
    # Load feature weights by analyzing fidelity_new.c
    feature_weights = load_feature_weights_from_statistics(fidelity_file)
    
    # Split the input into lines
    query_lines = code_input.strip().split('\n')
    
    # Call the function with the split lines
    selected_lines = generate_semantic_intensity_lines(
        query_lines, 
        min_lines=5, 
        base_lines=5, 
        threshold=5, 
        step=9, 
        max_lines=10,
        feature_weights=feature_weights
    )
    
    # Print selected lines
    print("\nSelected lines:")
    for line in selected_lines:
        print(line)