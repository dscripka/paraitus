import re

def format_code_blocks(text, text_widget):
    # Define the regular expression pattern for code blocks
    code_block_pattern = r"```(.*?)```"
    inline_code_pattern = r"[^`]`{1}([^`].*?)`{1}[^`]"

    # Find all code blocks in the text
    code_blocks = list(re.finditer(code_block_pattern, text, re.DOTALL))
    inline_code_blocks = list(re.finditer(inline_code_pattern, text, re.DOTALL))

    # Configure the "code_block" tag with red monospace font
    text_widget.tag_configure("code_block", font=("Courier", 12))
    text_widget.tag_configure("inline_code", font=("Courier", 12), foreground='green', background='lightgrey')

    for block in code_blocks:
        # Get the code block text and its start and end positions
        block_text = block.group(1)
        start_char = block.start()
        end_char = block.end()

        # Determine which lines the code block spans
        start_line = text.count("\n", 0, block.start())
        end_line = text.count("\n", 0, block.end())

        # Add the "code_block" tag to the code block text
        text_widget.tag_add("code_block", f"{start_line}.{start_char}", f"{end_line}.{end_char}")

    for block in inline_code_blocks:
        # Get the code block text and its start and end positions (relative to the start of the line)
        block_text = block.group(1)
        start_char = block.start() - text.rfind("\n", 0, block.start())
        end_char = block.end() - text.rfind("\n", 0, block.end())-2

        # Determine which lines the code block spans
        start_line = text.count("\n", 0, block.start())+1
        end_line = text.count("\n", 0, block.end())+1

        # Add the "code_block" tag to the code block text
        text_widget.tag_add("inline_code", f"{start_line}.{start_char}", f"{end_line}.{end_char}")

    # Update the GUI to reflect the changes
    text_widget.update_idletasks()