import re
import filetype

def format_code_blocks(text, text_widget):
    # Define the regular expression pattern for code blocks
    code_block_pattern = r"```(.*?)```"
    inline_code_pattern = r"[^`]`{1}([^`].*?)`{1}[^`]"

    # Find all code blocks in the text
    code_blocks = list(re.finditer(code_block_pattern, text, re.DOTALL))
    inline_code_blocks = list(re.finditer(inline_code_pattern, text, re.DOTALL))

    # Configure the "code_block" tag with red monospace font
    text_widget.tag_configure("code_block", font=("Courier", 12))
    text_widget.tag_configure("inline_code", font=("Courier", 12), foreground='green')

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

def check_filetype(path):
    """Predicts the type of a file based on heuristics and/or magic bytes
    
    Args:
        path (str): The path to the file to be checked

    Returns:
        str: The predicted file type
    """
    # Check using filetype library
    ftype = filetype.guess(path)
    if ftype is not None:
        return ftype
    else:
        # Check for common text file extensions
        if re.search("\.(txt|text|md|markdown|log|ini|conf|cfg|config|rc|properties|env|env\.[^.]+|json|xml|yml|yaml|csv|tsv|tab|html|htm|xhtml|asp|aspx|php|jsp|js|css|less|sass|scss|py|rb|pl|pm|sh|bat|cmd|ps1|vbs|asm|c|cpp|h|hpp|java|go|rs|swift|sql|r|m|f|f90|f95|f03|f08|ad[bs]|ada)$", path):
            return "text"
