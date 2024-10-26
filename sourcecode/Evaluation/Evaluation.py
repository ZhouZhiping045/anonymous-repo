import re
import os
from collections import defaultdict

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_lines_with_annotations(file_content):
    pattern = re.compile(r'(.*?)(//\s*I\d)')
    lines_with_annotations = []
    for line_number, line in enumerate(file_content.split('\n'), start=1):
        match = pattern.search(line)
        if match:
            code_line = match.group(1).strip()
            annotation = match.group(2).replace(" ", "")  # 移除注释标签中的空格
            lines_with_annotations.append((line_number, code_line, annotation))
        else:
            lines_with_annotations.append((line_number, line.strip(), None))
    return lines_with_annotations

def normalize_code_line(line):
    line = line.replace("\\\\", "\\").replace("\\t", "\t").replace("\\n", "\n")
    return line

def compare_annotations(gt_lines, model_lines):
    tp = 0
    tn = 0
    fp = 0
    fn = 0

    gt_dict = {normalize_code_line(code): (line_number, annotation) for line_number, code, annotation in gt_lines if annotation}
    model_dict = {normalize_code_line(code): (line_number, annotation) for line_number, code, annotation in model_lines if annotation}

    fp_lines = []

    for code in gt_dict:
        if code in model_dict:
            if gt_dict[code][1] == model_dict[code][1]:
                tp += 1
            else:
                fn += 1
                fp += 1
                fp_lines.append((model_dict[code][0], code, model_dict[code][1]))
        else:
            fn += 1

    for code in model_dict:
        if code not in gt_dict:
            fp += 1
            fp_lines.append((model_dict[code][0], code, model_dict[code][1]))

    tn = len(gt_lines) - tp - fn  # TN calculation adjusted

    return tp, tn, fp, fn, fp_lines

def compare_annotations_by_label(gt_lines, model_lines):
    results = defaultdict(lambda: {'tp': 0, 'tn': 0, 'fp': 0, 'fn': 0})

    gt_dict = {normalize_code_line(code): (line_number, annotation) for line_number, code, annotation in gt_lines if annotation}
    model_dict = {normalize_code_line(code): (line_number, annotation) for line_number, code, annotation in model_lines if annotation}

    all_labels = set(['//I1', '//I2', '//I3', '//I4', '//I5', '//I6'])

    for code in gt_dict:
        gt_annotation = gt_dict[code][1]
        if code in model_dict:
            model_annotation = model_dict[code][1]
            if gt_annotation == model_annotation:
                results[gt_annotation]['tp'] += 1
            else:
                results[gt_annotation]['fn'] += 1
                results[model_annotation]['fp'] += 1
        else:
            results[gt_annotation]['fn'] += 1

    for code in model_dict:
        if code not in gt_dict:
            model_annotation = model_dict[code][1]
            results[model_annotation]['fp'] += 1

    for label in all_labels:
        total_lines = len(gt_lines)
        results[label]['tn'] = total_lines - results[label]['tp'] - results[label]['fn']

    return results

def calculate_metrics(tp, tn, fp, fn):
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

    return accuracy, precision, recall, f1_score, specificity

def main():
    ground_truth_file = 'ground_truth.txt'
    model_output_file = 'model_output.txt'

    ground_truth_content = read_file(ground_truth_file)
    model_output_content = read_file(model_output_file)

    ground_truth_annotations = extract_lines_with_annotations(ground_truth_content)
    model_output_annotations = extract_lines_with_annotations(model_output_content)

    tp, tn, fp, fn, fp_lines = compare_annotations(ground_truth_annotations, model_output_annotations)

    overall_accuracy, overall_precision, overall_recall, overall_f1_score, overall_specificity = calculate_metrics(tp, tn, fp, fn)

    print("Overall Metrics:")
    print(f"  True Positives (TP): {tp}")
    print(f"  True Negatives (TN): {tn}")
    print(f"  False Positives (FP): {fp}")
    print(f"  False Negatives (FN): {fn}")
    print(f"  Accuracy: {overall_accuracy:.2f}")
    print(f"  Precision: {overall_precision:.2f}")
    print(f"  Recall: {overall_recall:.2f}")
    print(f"  F1 Score: {overall_f1_score:.2f}")
    print(f"  Specificity: {overall_specificity:.2f}")

    results = compare_annotations_by_label(ground_truth_annotations, model_output_annotations)

    for label, metrics in results.items():
        tp = metrics['tp']
        tn = metrics['tn']
        fp = metrics['fp']
        fn = metrics['fn']
        accuracy, precision, recall, f1_score, specificity = calculate_metrics(tp, tn, fp, fn)

        print(f"\nMetrics for {label}:")
        print(f"  True Positives (TP): {tp}")
        print(f"  True Negatives (TN): {tn}")
        print(f"  False Positives (FP): {fp}")
        print(f"  False Negatives (FN): {fn}")
        print(f"  Accuracy: {accuracy:.2f}")
        print(f"  Precision: {precision:.2f}")
        print(f"  Recall: {recall:.2f}")
        print(f"  F1 Score: {f1_score:.2f}")
        print(f"  Specificity: {specificity:.2f}")

    print("\nFalse Positives Details:")
    for line_number, code, annotation in fp_lines:
        print(f"Line {line_number}: {code} {annotation}")

if __name__ == "__main__":
    main()
