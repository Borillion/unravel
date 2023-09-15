import json
import zipfile
import argparse

def read_project_settings_from_3mf(zip_path, config_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        with zip_ref.open(config_path) as file:
            file_content = file.read().decode('utf-8')
    return file_content

def extract_project_settings(file_content, field_sets):
    json_blocks = []
    try:
        project_settings_json = json.loads(file_content)
    except json.JSONDecodeError as e:
        return {"error": f"Could not parse the file as JSON. Error message: {str(e)}"}

    for fields in field_sets:
        json_block = {}
        for field in fields:
            json_block[field] = project_settings_json.get(field, "Not Found")
        json_blocks.append(json_block)
    return json_blocks

def write_info_file(json_block):
    info_content = [
        "sync_info = ",
        f"user_id = {json_block.get('user_id', 'Not Found')}",
        f"setting_id = {json_block.get('setting_id', 'Not Found')}",
        f"base_id = {json_block.get('base_id', 'Not Found')}",
        f"updated_time = {json_block.get('updated_time', 'Not Found')}"
    ]
    info_filename = f"{json_block.get('name', 'Unnamed')}.info"
    with open(info_filename, 'w') as info_file:
        info_file.write('\n'.join(info_content))

def write_json_file(json_block):
    json_filename = f"{json_block.get('name', 'Unnamed')}.json"
    with open(json_filename, 'w') as json_file:
        json.dump(json_block, json_file, indent=4)

def print_json_blocks(json_blocks):
    for json_block in json_blocks:
        print(f"JSON block for {json_block.get('name', 'Unnamed')}:")
        print(json.dumps(json_block, indent=4))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process project settings.')
    parser.add_argument('filepath', type=str, help='Path to the 3MF file')
    parser.add_argument('-w', '--write', action='store_true', help='Write files to disk')
    args = parser.parse_args()

    zip_path = args.filepath
    config_path = 'Metadata/project_settings.config'
    field_sets = [
        ['type', 'filament_id', 'name', 'from', 'instantiation', 'inherits', 'filament_vendor', 'filament_cost', 'filament_flow_ratio', 'filament_density', 'filament_start_gcode'],
        ['type', 'setting_id', 'name', 'from', 'instantiation', 'inherits', 'filament_max_volumetric_speed', 'compatible_printers', 'version'],
        ['filament_settings_id', 'from', 'inherits', 'is_custom_defined', 'name', 'nozzle_temperature', 'nozzle_temperature_initial_layer', 'version', 'user_id', 'setting_id', 'base_id', 'updated_time']
    ]

    file_content = read_project_settings_from_3mf(zip_path, config_path)
    json_blocks = extract_project_settings(file_content, field_sets)

    print_json_blocks(json_blocks)

    if args.write:
        for json_block in json_blocks:
            write_json_file(json_block)
        write_info_file(json_blocks[-1])  # Write .info file based on the last JSON block
