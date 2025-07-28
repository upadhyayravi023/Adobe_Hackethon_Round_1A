import os
import json

def normalize(text):
    return text.strip().lower().replace("–", "-").replace("—", "-")

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def match_heading(pred, truth, tolerance=0):
    return (
        pred["level"] == truth["level"] and
        abs(pred["page"] - truth["page"]) <= tolerance and
        normalize(pred["text"]) == normalize(truth["text"])
    )

def evaluate(pred_dir, gt_dir, tolerance=0):
    total_correct = 0
    total_predicted = 0
    total_ground_truth = 0

    for fname in os.listdir(pred_dir):
        if not fname.endswith(".json"):
            continue
        pred_path = os.path.join(pred_dir, fname)
        gt_path = os.path.join(gt_dir, fname)
        if not os.path.exists(gt_path):
            continue

        pred_data = load_json(pred_path)
        gt_data = load_json(gt_path)

        pred_headings = pred_data.get("outline", [])
        gt_headings = gt_data.get("outline", [])

        matched = set()
        correct = 0

        for pred in pred_headings:
            for i, truth in enumerate(gt_headings):
                if i in matched:
                    continue
                if match_heading(pred, truth, tolerance):
                    correct += 1
                    matched.add(i)
                    break

        total_correct += correct
        total_predicted += len(pred_headings)
        total_ground_truth += len(gt_headings)

    precision = total_correct / total_predicted if total_predicted else 0
    recall = total_correct / total_ground_truth if total_ground_truth else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
    accuracy = total_correct / total_ground_truth if total_ground_truth else 0

    return round(accuracy, 3), round(precision, 3), round(recall, 3), round(f1, 3)

if __name__ == "__main__":
    acc, prec, recall, f1 = evaluate("output", "ground_truth", tolerance=0)
    print(f"Accuracy: {acc}")
    print(f"Precision: {prec}")
    print(f"Recall: {recall}")
    print(f"F1-score: {f1}")
