import json
import argparse

def json_to_twee(data, passage_name="Start", depth=1):
    twee_code = f':: {passage_name}\n{data["description"]}\n\n'
    
    for option in data.get("options", []):
        next_passage_name = f"{passage_name}.{option['option']}"
        twee_code += f'[[{option["text"]}->{next_passage_name}]]\n'
    
    twee_code += "\n"
    
    for option in data.get("options", []):
        if option.get("response") is not None:
            twee_code += json_to_twee(option["response"], f"{passage_name}.{option['option']}", depth + 1)
    
    return twee_code

def main():
    parser = argparse.ArgumentParser(description="Convert JSON to Twee code.")
    parser.add_argument("input_file", help="Path to the input JSON file.")
    parser.add_argument("--output", default="output.twee", help="Path to the output Twee file (default: output.twee).")
    args = parser.parse_args()
    
    with open(args.input_file, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    
    twee_code = json_to_twee(json_data)
    
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(twee_code)
    
    print(f"Conversion completed. Twee file saved as {args.output}")

if __name__ == "__main__":
    main()
