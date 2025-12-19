import os
import json

root_data_dir = "../../data/final_json"

folder_item_counts = {}
total_items = 0

for folder in os.listdir(root_data_dir):
    folder_path = os.path.join(root_data_dir, folder)

    if not os.path.isdir(folder_path):
        continue

    item_count = 0

    for file in os.listdir(folder_path):
        if not file.endswith(".json"):
            continue

        file_path = os.path.join(folder_path, file)

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

                if isinstance(data, list):
                    item_count += len(data)
                else:
                    item_count += 1

        except Exception as e:
            print("Error reading:", file_path, e)

    folder_item_counts[folder] = item_count
    total_items += item_count

print("\n--- JSON ITEM COUNT PER FOLDER ---")
for folder, count in folder_item_counts.items():
    print(f"{folder}: {count}")

print("\nTotal items across all folders:", total_items)
