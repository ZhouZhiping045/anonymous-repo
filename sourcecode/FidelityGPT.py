import os
import sys
import configparser
from typing import List
from document_processor import (
    load_document,
    split_document,
    read_queries,
    write_output
)
from pattern_matcher import match_patterns
from embedding_retriever import (
    create_embedding,
    create_vectorstore,
    create_retriever,
    retrieve_documents,
)
from prompt_templates import (
    create_RAG_prompt_template,
    create_RAG_promptwithvariable_template
)
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import variabledependency

# 获取当前目录和配置文件路径
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(CUR_DIR, "config.ini")

def load_config(field: str, value: str) -> str:
    """加载配置文件中的参数"""
    config = configparser.ConfigParser()
    try:
        config.read(CONFIG)
        return config[field][value]
    except KeyError:
        sys.exit(1)

# 设置 OpenAI 的环境变量
os.environ["OPENAI_API_BASE"] = load_config("LLM", "api_base")
os.environ["OPENAI_API_KEY"] = load_config("LLM", "api_key")

def format_docs(docs: List[str]) -> str:
    """格式化文档列表为字符串"""
    return "\n\n".join(docs)

def append_to_retrieve_log(file_path: str, sub_query: str, context: str):
    """将检索日志追加到文件中"""
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"Sub-query:\n{sub_query}\n")
            f.write(f"Formatted context:\n{context}\n")
            f.write("/////\n")
    except IOError:
        pass

def split_into_blocks(lines: List[str], block_size: int = 50, overlap: int = 5) -> List[List[str]]:
    """将长文本分割为块，支持重叠"""
    blocks = []
    total_lines = len(lines)

    start = 0
    while start < total_lines:
        end = min(start + block_size, total_lines)
        block = lines[start:end]
        blocks.append(block)
        start += block_size - overlap

    return blocks

def process_queries(
    file_path: str,
    output_dir: str,
    retriever,
    llm,
    RAG_prompt,
    RAG_prompt_with_variable,
):
    """处理文件中的所有查询"""
    try:
        queries = read_queries(file_path)
    except Exception:
        return

    RAG_results = []

    for query_index, query in enumerate(queries):
        sub_queries = query.strip().split("\n")
        query_line_count = len(sub_queries)

        # 根据查询的行数决定处理方式
        if query_line_count > 50:
            # 超过50行，执行变量名提取和分块处理
            try:
                variable_names = variabledependency.generate_and_query_llm("\n".join(sub_queries))
            except Exception:
                variable_names = ""

            # 分块处理查询
            blocks = split_into_blocks(sub_queries)

            for block_index, block in enumerate(blocks):
                # 模式匹配
                try:
                    matched_lines = match_patterns(block)
                except Exception:
                    continue

                # 检索相关文档
                try:
                    retrieved_docs = retrieve_documents(retriever, matched_lines)
                except Exception:
                    continue

                # 去除重复文档
                unique_retrieved_docs = list(dict.fromkeys(retrieved_docs))

                context = format_docs(unique_retrieved_docs)

                # 记录检索日志
                append_to_retrieve_log("retrieve-new.txt", "\n".join(block), context)

                # 构建变量字典
                variables = {
                    "Variable_names": variable_names,
                    "context": context,
                    "question": "\n".join(block),
                }

                # 构建 RAG 链
                RAG_chain = (
                    {
                        "Variable_names": RunnablePassthrough(),
                        "context": RunnablePassthrough(),
                        "question": RunnablePassthrough(),
                    }
                    | RAG_prompt_with_variable
                    | llm
                    | StrOutputParser()
                )

                # 生成完整的Prompt并输出
                full_prompt = RAG_prompt_with_variable.format(**variables)
                print(f"\n[Prompt for Query {query_index + 1}, Block {block_index + 1}]:\n{full_prompt}\n")

                # 调用模型生成结果
                try:
                    RAG_result = RAG_chain.invoke(variables).strip()
                    RAG_results.append(
                        f"Query {query_index + 1}, Block {block_index + 1}:\n{RAG_result}\n"
                    )
                except Exception:
                    continue
        else:
            # 不超过50行，直接处理
            # 模式匹配
            try:
                matched_lines = match_patterns(sub_queries)
            except Exception:
                continue

            # 检索相关文档
            try:
                retrieved_docs = retrieve_documents(retriever, matched_lines)
            except Exception:
                continue

            # 去除重复文档
            unique_retrieved_docs = list(dict.fromkeys(retrieved_docs))

            context = format_docs(unique_retrieved_docs)

            # 记录检索日志
            append_to_retrieve_log("retrieve-new.txt", "\n".join(matched_lines), context)

            # 构建变量字典
            variables = {
                "context": context,
                "question": query,
            }

            # 构建 RAG 链
            RAG_chain = (
                {
                    "context": RunnablePassthrough(),
                    "question": RunnablePassthrough()
                }
                | RAG_prompt
                | llm
                | StrOutputParser()
            )

            # 生成完整的Prompt并输出
            full_prompt = RAG_prompt.format(**variables)
            print(f"\n[Prompt for Query {query_index + 1}]:\n{full_prompt}\n")

            # 调用模型生成结果
            try:
                RAG_result = RAG_chain.invoke(variables).strip()
                RAG_results.append(f"Query {query_index + 1}:\n{RAG_result}\n")
            except Exception:
                continue

    # 写入结果到输出文件
    base_filename = os.path.basename(file_path).split('.')[0]
    RAG_output_path = os.path.join(output_dir, f"{base_filename}_RAG_answer.txt")
    try:
        write_output(RAG_output_path, "\n/////\n".join(RAG_results))
    except Exception:
        pass

def main():
    """主函数，初始化环境并处理文件"""
    current_dir = os.getcwd()
    testdata_dir = os.path.join(current_dir, "testdata")
    output_dir = os.path.join(current_dir, "output")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 加载知识库
    fidelity_file = os.path.join(current_dir, "fidelity_new.c")
    try:
        fidelity_content = load_document(fidelity_file)
        fidelity_documents = split_document(fidelity_content)
        fidelity_texts = [doc.page_content for doc in fidelity_documents]
    except Exception:
        sys.exit(1)

    # 创建嵌入和检索器
    try:
        embeddings = create_embedding(fidelity_texts)
        db = create_vectorstore(fidelity_texts, embeddings)
        retriever = create_retriever(db)
    except Exception:
        sys.exit(1)

    # 初始化语言模型和提示模板
    try:
        llm = ChatOpenAI(model="gpt-4o-2024-08-06", temperature=0.5)
        RAG_prompt = create_RAG_prompt_template()
        RAG_prompt_with_variable = create_RAG_promptwithvariable_template()
    except Exception:
        sys.exit(1)

    # 处理测试数据
    for root, dirs, files in os.walk(testdata_dir):
        for file in files:
            file_path = os.path.join(root, file)
            process_queries(file_path, output_dir, retriever, llm, RAG_prompt, RAG_prompt_with_variable)

if __name__ == "__main__":
    main()
