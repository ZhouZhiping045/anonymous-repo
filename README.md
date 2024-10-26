<div align=center><img src="doc/fidelitygpt-workflow.pdf" width="80%"></div>

> *FidelityGPT: Correcting Decompilation Distortions with Retrieval Augmented Generation.*
> ## Source Code Structure
The following is a brief introduction to the directory structure of this artifact:
```
- sourcecode/          ; main source code directory
    - Evaluation/      ; folder for evaluation-related scripts and data
        - Evaluation.py          ; main evaluation script
        - ground_truth.txt       ; ground truth data for evaluation
        - model_output.txt       ; model output for comparison
    - output/           ; folder for outputs
        - Evaluation2.py         ; additional evaluation script
        - ground_truth.txt       ; ground truth data for outputs
        - model_output.txt       ; output from the model
        - test_RAG_answer.txt    ; test results from RAG evaluation
    - testdata/         ; test data and supporting files
        - test.txt                ; test data file
        - FidelityGPT.py          ; main FidelityGPT script
        - document_processor.py   ; document processing utility
        - embedding_retriever.py  ; script for retrieving embeddings
        - fidelity_new.c          ; RAG distortion database
        - pattern_matcher.py      ; Dynamic Semantic Intensity algorithm
        - prompt_templates.py     ; prompt templates for testing       
        - variabledependency.py   ;Variable Dependency Algorithm

```
