from langchain.prompts import PromptTemplate
from langchain.schema import SystemMessage, HumanMessage, AIMessage

def create_variable_template():
    template = """As a program analysis expert, you possess excellent program analysis skills. Below are the variable dependencies extracted from decompiled code. During the decompilation process, new variables are defined due to register usage, which leads to a large number of redundant variables compared to the source code. Redundant variables refer to those that are temporary, intermediate, or represent the same data. These variables are often generated during the decompilation process due to register operations or temporary storage needs. Considering temporary or intermediate calculation results, these variables are only used for intermediate steps in computations or operations and are not utilized multiple times or have no significant independent meaning. Repetitively, these variables store the same or similar information and can logically be merged with other statements. The task is to directly output potentially redundant variables without any explanation. The output format is as follows: **Potential redundant variable: {all variable names}.
    Question: {question}      
    Helpful Answer:
    """
    return PromptTemplate.from_template(template)
def create_prompt_template():
    template = """As an experienced reverse engineering expert, I possess advanced skills in using reverse engineering tools (such as IDA Pro, Ghidra) to analyze program code. 
I have extensive expertise in decompiled code analysis, but the readability of decompiled code is often poor, so I must carefully check and verify each line of the decompiled code. Below is the input question:
Question: {question}      
The task is to improve the readability of the decompiled code by performing the following operations: 1. Restore meaningful variable names; 2. Restore the original code as much as possible without changing the semantics.           
Output all lines of the Question code and add “//fixed” after the corrected lines, without providing any further explanation.
Helpful Answer:
    """
    return PromptTemplate.from_template(template)
def create_zero_shot_prompt_template():
    template = """As an experienced reverse engineering expert, I possess advanced skills in using reverse analysis tools (e.g., IDA Pro, Ghidra) to analyze program code. I have extensive expertise in analyzing decompiled code and am capable of accurately identifying false positives and false negatives. It is worth noting that these reverse engineering tools often generate significant code semantic distortions during decompilation due to factors such as the compiler, architecture, and optimization level. Therefore, I must carefully review and verify each line of decompiled code.
I have pre-defined the following types of distortions (i.e., semantic differences between source code and decompiled code):
I1: Non-inertial dereferencing: When accessing structure members using pointers and arrays or accessing array members using pointers, I check whether the source code accesses structure members while the corresponding decompiled code uses pointers and arrays to access the structure members, which often includes forced type casts such as _DWORD, _BYTE, etc., or if the source code accesses arrays while the corresponding decompiled code uses pointers to access array members.
I2: Character and string literal representation issues: String literals are replaced by references or represented as integers. I check if the source code uses characters or strings, and in the corresponding decompiled code with the same semantics, the characters or string literals are replaced by references or integers.
I3: Obfuscated control flow reconstruction: While and for loops are interchanged, inline functions, or ternary operators are deconstructed. I check whether the control flow in the decompiled code has been changed compared to the source code, such as possible interchanges between while, for, and if, inline functions, or ternary operators replaced with if statements.
I4: Redundant code: Code that performs the same function without needing new variable declarations, assigning parameters to variables without meaning, assigning values to variables from function calls that do not return a value, redundant variables introduced by non-inertial dereferencing, or variables introduced by the compiler or user macros. This type of distortion often results in many false negatives and must be thoroughly checked.
I5: Return anomalies: The structure or return value of the function does not meet expectations.
I6: Use of non-type symbols: In the decompiled code, symbols and macros are used that do not conform to the expected types. In decompiled code with the same semantics, non-type symbols, user macros, or specific compiler functions are used.
Please analyze the following decompiled code line by line and consider the potential distortion issues in each line of code.
Input question:
Question: {question}
Output format:
Output: Output all the decompiled code from the problem and append the distortion type number after each line where a distortion is found, without explanation.
Helpful Answer:
    """
    return PromptTemplate.from_template(template)
def create_RAG_prompt_template():
    template = """As an experienced reverse engineering expert, I possess advanced skills in analyzing program code using reverse engineering tools such as IDA Pro and Ghidra. I have extensive expertise in analyzing decompiled code and can accurately identify both false positives and false negatives. It is important to note that these reverse engineering tools often produce significant code semantic distortions during the decompilation process due to factors like the compiler, architecture, and optimization levels. Therefore, I must carefully review and verify every line of decompiled code. I have pre-defined the following types of distortions (i.e., semantic discrepancies between the source code and decompiled code):
- **I1: Non-inertial dereferencing**: This involves the use of pointers and arrays to access structure members or the use of pointers to access array members. I check if the source code accesses structure members, but the corresponding decompiled code semantics involve pointer and array access to structure members, including forced type conversions like `_DWORD`, `_BYTE`, etc., or if the source code accesses arrays, but the decompiled code semantics involve pointer access to array members.
  - **I2: Character and string literal representation issues**: This distortion occurs when string literals are replaced by references or represented as integers. I check if the source code uses characters or strings, but the corresponding decompiled code with the same semantics replaces these with references or integers.
- **I3: Obfuscated control flow reconstruction**: This distortion involves changes in control flow, such as while and for loops being interchanged, inline functions, or ternary operators being deconstructed. I verify if the control flow in the source code has changed in the decompiled code, with possible interchanges between while, for, and if statements, inline functions, and ternary operators being replaced by if statements.
- **I4: Redundant code**: This distortion involves declaring new variables unnecessarily for the same functionality, assigning parameters to variables meaninglessly, assigning function calls without return values to variables, redundant variables introduced by non-inertial dereferencing, or variable assignments introduced by the compiler or user macros. This type of distortion often results in more false negatives and requires careful examination.
- **I5: Return exceptions**: The structure or return value of a function does not meet expectations.
- **I6: Usage of non-typed symbols**: This occurs when non-typed symbols and macros are used in the decompiled code. I check if the same semantics in the decompiled code involve the use of non-typed symbols, user macros, function calls, or compiler-specific functions.
    {context}
Consider the retrieval results from the distorted code database. These retrieval results indicate code lines with high similarity to distortion issues. My responsibility is to analyze the following decompiled code line by line, considering the potential distortion issues in the code. The retrieval results are only for contextual reference and are not to be outputted.
Below is the question input:  
Question: {question}  
**Requirements**: Only label, do not fix.  
**Output format**: Output all decompiled code in the question, and for each identified distorted code line, append the distortion type number with “//Distortion type number” without explanation.  
Helpful Answer:
    """
    return PromptTemplate.from_template(template)
def create_RAG_promptwithvariable_template():
    template = """As an experienced reverse engineering expert, I possess advanced skills in analyzing program code using reverse engineering tools such as IDA Pro and Ghidra. I have extensive expertise in analyzing decompiled code and can accurately identify both false positives and false negatives. It is important to note that these reverse engineering tools often produce significant code semantic distortions during the decompilation process due to factors like the compiler, architecture, and optimization levels. Therefore, I must carefully review and verify every line of decompiled code. I have pre-defined the following types of distortions (i.e., semantic discrepancies between the source code and decompiled code):
- **I1: Non-inertial dereferencing**: This involves the use of pointers and arrays to access structure members or the use of pointers to access array members. I check if the source code accesses structure members, but the corresponding decompiled code semantics involve pointer and array access to structure members, including forced type conversions like `_DWORD`, `_BYTE`, etc., or if the source code accesses arrays, but the decompiled code semantics involve pointer access to array members.
  - **I2: Character and string literal representation issues**: This distortion occurs when string literals are replaced by references or represented as integers. I check if the source code uses characters or strings, but the corresponding decompiled code with the same semantics replaces these with references or integers.
- **I3: Obfuscated control flow reconstruction**: This distortion involves changes in control flow, such as while and for loops being interchanged, inline functions, or ternary operators being deconstructed. I verify if the control flow in the source code has changed in the decompiled code, with possible interchanges between while, for, and if statements, inline functions, and ternary operators being replaced by if statements.
- **I4: Redundant code**: This distortion involves declaring new variables unnecessarily for the same functionality, assigning parameters to variables meaninglessly, assigning function calls without return values to variables, redundant variables introduced by non-inertial dereferencing, or variable assignments introduced by the compiler or user macros. This type of distortion often results in more false negatives and requires careful examination.
- **I5: Return exceptions**: The structure or return value of a function does not meet expectations.
- **I6: Usage of non-typed symbols**: This occurs when non-typed symbols and macros are used in the decompiled code. I check if the same semantics in the decompiled code involve the use of non-typed symbols, user macros, function calls, or compiler-specific functions.
    {Variable_names}
First, consider the above potentially redundant variables and recheck them to avoid false positives and false negatives.
    {context}
Next, consider the retrieval results from the distorted code database. These retrieval results indicate code lines with high similarity to distortion issues. My responsibility is to analyze the following decompiled code line by line, considering the potential distortion issues in the code. The retrieval results are only for contextual reference and are not to be outputted.
Below is the question input:  
Question: {question}  
**Requirements**: Only label, do not fix.  
**Output format**: Output all decompiled code in the question, and for each identified distorted code line, append the distortion type number with “//Distortion type number” without explanation.  
Helpful Answer:
    """
    return PromptTemplate.from_template(template)
def create_RAG_correction_template():
    template = """As an experienced reverse engineering expert, I possess advanced skills in analyzing program code using reverse engineering tools such as IDA Pro and Ghidra. I have extensive expertise in decompiled code analysis, enabling me to accurately identify false positives and false negatives. It is noteworthy that these reverse engineering tools often generate significant code semantic distortions during the decompilation process due to compiler settings, architecture differences, and optimization levels. Therefore, I must carefully verify every line of the decompiled code. 

I have pre-defined the following types of distortions (i.e., semantic discrepancies between source code and decompiled code):

- **I1: Non-inertial Dereferencing**: This involves using pointers and arrays to access structure members or accessing array members with pointers. When the source code accesses structure members, but the decompiled code uses pointers or arrays to access structure members (or vice versa for arrays), you need to review and correct the dereferencing method.
- **I2: Character and String Literal Representation Issues**: This occurs when string literals are replaced with references or represented as integers. If the source code uses characters or strings but the decompiled code represents them as references or integers, review and correct the numeric values.
- **I3: Obfuscated Control Flow Reconstruction**: This involves swapping `while` and `for` loops, inline functions, or deconstructing ternary operators. If the control flow in the source code changes in the decompiled code, it needs to be reviewed.
- **I4: Redundant Code**: This includes declaring unnecessary new variables to perform the same function, assigning parameters to variables unnecessarily, assigning variables from function calls without return values, introducing redundant variables due to non-inertial dereferencing, and introducing variables through compiler or user macros. These issues need to be fixed.
- **I5: Return Anomalies**: If the structure or return value of a function is unexpected, it should be corrected.
- **I6: Usage of Non-Type Symbols**: This occurs when the decompiled code uses symbols or macros that do not conform to types. If the same semantic decompiled code uses symbols, user macros, function calls, or compiler-specific functions that are type-inconsistent, corrections are required.
Considering the above, I initially review the retrieval results from the distorted code repository. However, these results represent code lines with a high similarity in distortion issues. Therefore, my responsibility is to analyze each line of the decompiled code individually, taking into account the potential distortion issues in the code. The retrieved results serve only as contextual references but are not to be output.
Here is the problem input:
Question: {question}
You are required to perform the following tasks from the perspective of improving code readability and simplifying the code: 
1. Fix the distortion issues listed above. 
2. Restore meaningful variable names. 
3. Reconstruct the source code.
Output format:
Output: Fix the distortion issues + “//fixed” without further explanation. 
Helpful Answer: 
    """
    return PromptTemplate.from_template(template)
def create_few_shot_prompt_template():
    uva_position_prompt = """As an experienced reverse engineering expert, I possess advanced skills in using reverse analysis tools (e.g., IDA Pro, Ghidra) to analyze program code. I have extensive expertise in analyzing decompiled code and am capable of accurately identifying false positives and false negatives. It is worth noting that these reverse engineering tools often generate significant code semantic distortions during decompilation due to factors such as the compiler, architecture, and optimization level. Therefore, I must carefully review and verify each line of decompiled code.
I have pre-defined the following types of distortions (i.e., semantic differences between source code and decompiled code):
I1: Non-inertial dereferencing: When accessing structure members using pointers and arrays or accessing array members using pointers, I check whether the source code accesses structure members while the corresponding decompiled code uses pointers and arrays to access the structure members, which often includes forced type casts such as _DWORD, _BYTE, etc., or if the source code accesses arrays while the corresponding decompiled code uses pointers to access array members.
I2: Character and string literal representation issues: String literals are replaced by references or represented as integers. I check if the source code uses characters or strings, and in the corresponding decompiled code with the same semantics, the characters or string literals are replaced by references or integers.
I3: Obfuscated control flow reconstruction: While and for loops are interchanged, inline functions, or ternary operators are deconstructed. I check whether the control flow in the decompiled code has been changed compared to the source code, such as possible interchanges between while, for, and if, inline functions, or ternary operators replaced with if statements.
I4: Redundant code: Code that performs the same function without needing new variable declarations, assigning parameters to variables without meaning, assigning values to variables from function calls that do not return a value, redundant variables introduced by non-inertial dereferencing, or variables introduced by the compiler or user macros. This type of distortion often results in many false negatives and must be thoroughly checked.
I5: Return anomalies: The structure or return value of the function does not meet expectations.
I6: Use of non-type symbols: In the decompiled code, symbols and macros are used that do not conform to the expected types. In decompiled code with the same semantics, non-type symbols, user macros, or specific compiler functions are used."""

    uva_example_q1 = """example 1:
void *__cdecl AES_cbc_encrypt(int a1, int a2, int a3, int a4, void *dest, int a6)
{
  void *result; 
  if ( a6 )
    result = CRYPTO_cbc128_encrypt(a1, a2, a3, a4, dest, (int)AES_encrypt);
  else
    result = (void *)CRYPTO_cbc128_decrypt(
                       (int *)a1, 
                       (int *)a2, 
                       a3,
                       a4,
                       dest,
                       (void (__cdecl *)(_DWORD *, int *, int))AES_decrypt); 
  return result; 
}
}"""

    uva_example_a1 = """
void *__cdecl AES_cbc_encrypt(int a1, int a2, int a3, int a4, void *dest, int a6)
{
  void *result; // I4
  if ( a6 )
    result = CRYPTO_cbc128_encrypt(a1, a2, a3, a4, dest, (int)AES_encrypt);
  else
    result = (void *)CRYPTO_cbc128_decrypt(
                       (int *)a1, // I1
                       (int *)a2, // I1
                       a3,
                       a4,
                       dest,
                       (void (__cdecl *)(_DWORD *, int *, int))AES_decrypt); // I1
  return result; // I5
}
"""

    uva_example_q2 = """example 2:
__fastcall SetStreamBuffering(int a1, int a2)
{
  int v2;
  unsigned int n;
  const char *v6;
  n = 0x4000;
  v6 = (const char *)j_GetImageOption(a1, (unsigned int)"stream:buffer-size"); 
  if ( v6 )
    n = StringToUnsignedLong(v6);
  if ( n ) 
    v2 = 0;
  else
    v2 = 2;
  return setvbuf(*(FILE **)(*(_DWORD *)(a2 + 13128) + 68), 0, v2, n) == 0; 
}
"""

    uva_example_a2 = """
__fastcall SetStreamBuffering(int a1, int a2)
{
  int v2;
  unsigned int n;
  const char *v6;
  n = 0x4000;
  v6 = (const char *)j_GetImageOption(a1, (unsigned int)"stream:buffer-size"); // I6
  if ( v6 )
    n = StringToUnsignedLong(v6);
  if ( n ) // I3
    v2 = 0;
  else
    v2 = 2;
  return setvbuf(*(FILE **)(*(_DWORD *)(a2 + 13128) + 68), 0, v2, n) == 0; // I1
}
"""

    uva_example_q3 = """example 3:
__fastcall ReadBlobString(int a1, int a2)
{
  int i;
  int v7;
  if ( !a1 )
    _assert_fail("image != (Image *) NULL", "MagickCore/blob.c", 0x12E7u, "ReadBlobString"); 
  for ( i = 0; i <= 4094; ++i )
  {
    *(_BYTE *)(a2 + i) = v7; 
    if ( v7 == 10 )
    {
      if ( i > 0 && *(_BYTE *)(a2 + i - 1) == 13 )
        --i;
      break;
    }
  }
  *(_BYTE *)(a2 + i) = 0; 
  return a2;
}
"""

    uva_example_a3 = """
__fastcall ReadBlobString(int a1, int a2)
{
  int i;
  int v7;
  if ( !a1 )
    _assert_fail("image != (Image *) NULL", "MagickCore/blob.c", 0x12E7u, "ReadBlobString"); // I6
  for ( i = 0; i <= 4094; ++i )
  {
    *(_BYTE *)(a2 + i) = v7; // I1
    if ( v7 == 10 ) // I2
    {
      if ( i > 0 && *(_BYTE *)(a2 + i - 1) == 13 ) // I2
        --i;
      break;
    }
  }
  *(_BYTE *)(a2 + i) = 0; // I1
  return a2;
}}"""

    sys_prompt = uva_position_prompt
    prompt_list = [
        SystemMessage(content=sys_prompt),
        HumanMessage(content=uva_example_q1),
        AIMessage(content=uva_example_a1),
        HumanMessage(content=uva_example_q2),
        AIMessage(content=uva_example_a2),
        HumanMessage(content=uva_example_q3),
        AIMessage(content=uva_example_a3),
    ]

    template = """
The above are examples of distortion detection. Please refer to the examples and analyze the following decompiled code line by line, considering possible distortion issues in the code. 
Please analyze the following decompiled code line by line and consider the potential distortion issues in each line of code.
Input question:
Question: {question}
Output format:
Output: Output all the decompiled code from the problem and append the distortion type number after each line where a distortion is found, without explanation.
Helpful Answer:
    """
    prompt_list.append(HumanMessage(content=template))

    return prompt_list
