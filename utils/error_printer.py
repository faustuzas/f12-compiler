from utils import printer

def line_number_prefix(number):
    return f'{number}. '

def print_error(self, type, cause, text, line_number, offset_in_line, file_name):
    all_lines = text.split('\n')
    lines_to_show = []
    line_in_array = line_number - 1
    if line_number - 1 >= 1 and len(all_lines[line_in_array - 1].strip()) > 0:
        lines_to_show.append(f'{line_number_prefix(line_number - 1)}{all_lines[line_in_array - 1]}')

    lines_to_show.append(f'{line_number_prefix(line_number)}{all_lines[line_in_array]}')
    lines_to_show.append(' ' * (offset_in_line + len(line_number_prefix(line_number)) - 1) + '^')

    if line_number + 1 <= len(all_lines) and len(all_lines[line_in_array + 1].strip()) > 0:
        lines_to_show.append(f'{line_number_prefix(line_number + 1)}{all_lines[line_in_array + 1]}')

    printer.error('\n'.join(lines_to_show), f'{type} error [{file_name}:{line_number}:{offset_in_line}] : {cause}')