import tkinter as tk
from tkinter import ttk
import sv_ttk
import os
import argparse
from pynput import mouse, keyboard
import signal
import time
import logging
logging.basicConfig(level=logging.INFO)
import threading
import paraitus
from paraitus import utils

# Parse command-line arguments for cache directory location (default is ~/.paraitus)
parser = argparse.ArgumentParser(description="Paraitus: A simple LLM API interface.")
parser.add_argument("--cache-dir", type=str, default=os.path.join(os.path.expanduser("~"), ".paraitus"),
                    help="Directory to store config files and custom authentication classes")

parser = parser.parse_args()

# Load the configuration file
paraitus.load_config(parser.cache_dir)

def main():
    # Create the main window
    logging.info("Preparing interface...")
    root = tk.Tk()
    sv_ttk.set_theme("dark")
    root.withdraw()  # Hide the main window

    # Make global object to store active windows
    global windows
    windows = []

    def on_key_press():
        open_text_input_window()

    def open_text_input_window():
        global window, windows
        window_name = f"Paraitus {len(windows) + 1}"
        window = tk.Toplevel(class_=window_name)
        window.title(window_name)
        # window.attributes('-fullscreen', True)
        windows.append(window)

        # Set the window height to the screen height
        screen_height = window.winfo_screenheight()
        window.geometry(f"1000x{int(screen_height*0.95)}+0+0")

        # Create a style object to modify the appearance of widgets
        style = ttk.Style()
        style.configure('Custom.TText', font=('Calibri', 12), foreground='black', background='gray')

        # Create a combobox and label for models
        model_names = [i["name"] for i in paraitus.MODELS]
        label = ttk.Label(window, text="Select a Model:")
        label.grid(row=1, column=0, sticky='w', padx=10, pady=10)
        combo = ttk.Combobox(window, values=model_names)
        combo.current(model_names.index([i['name'] for i in paraitus.MODELS if i["default"] == True][0]))
        combo.grid(row=2, column=0, sticky='nw', padx=10, pady=10)

        # Creat text input fields for temperature and top-p
        temperature_label = ttk.Label(window, text="Temperature:")
        temperature_label.grid(row=2, column=0, sticky='ws', padx=10, pady=90)
        temperature_input = ttk.Entry(window)
        temperature_input.insert(0, "0.0") 
        temperature_input.grid(row=2, column=0, sticky='ws', padx=10, pady=60)
        top_p_label = ttk.Label(window, text="Top-p:")
        top_p_label.grid(row=2, column=0, sticky='ws', padx=10, pady=40)
        top_p_input = ttk.Entry(window)
        top_p_input.insert(0, "1.0")
        top_p_input.grid(row=2, column=0, sticky='ws', padx=10, pady=10)

        # Load the default model based on the provider type
        global llm_provider
        llm_provider = [i["provider"] for i in paraitus.MODELS if i["default"] == True][0]

        # Create non-editable text box to list keyboard shorcuts
        keyboard_shortcuts = """
Ctrl+Enter: Submit Prompt
Ctrl+m: Focus Model Dropdown
Ctrl+u: Focus User Input
Ctrl+s: Focus System Prompt
Ctrl+o: Focus Output Text
Escape: Close Window
        """.strip()
        shortcuts_text = ttk.Label(window, text=keyboard_shortcuts)
        shortcuts_text.grid(row=6, column=0, sticky='sw', padx=10, pady=10)

        # Create a label for the first textbox (system prompt)
        label1 = ttk.Label(window, text="System Prompt:")
        label1.grid(row=1, column=1, sticky='w', padx=10, pady=10)

        # Create label estimated number of tokens in system prompt input
        token_counter_system_prompt = ttk.Label(window, text="Estimated Tokens: 0")
        token_counter_system_prompt.grid(row=1, column=1, sticky='e', padx=10, pady=10)

        # Create the first textbox with scrollbar
        system_prompt = tk.Text(window, wrap=tk.WORD, font=('Calibri', 12), padx=10, pady=10)
        system_prompt_starting_height = system_prompt.winfo_reqheight()/20
        scrollbar1 = ttk.Scrollbar(window, orient='vertical', command=system_prompt.yview)
        system_prompt.configure(yscrollcommand=scrollbar1.set)
        system_prompt.grid(row=2, column=1, sticky='nsew', padx=10, pady=10)
        scrollbar1.grid(row=2, column=2, sticky='ns')

        # Bind right click on the sytem prompt Text widget to a callback to expand the window
        def on_right_click(event):
            if system_prompt.winfo_reqheight()/20 > system_prompt_starting_height:
                system_prompt.configure(height=system_prompt_starting_height)
            else:
                system_prompt.configure(height=150)
        system_prompt.bind("<Button-3>", on_right_click)

        # Create a label for the second textbox (user input)
        label2 = ttk.Label(window, text="User Input (control+enter to submit):")
        label2.grid(row=3, column=1, sticky='w', padx=10, pady=10)

        # Create label for token count in user input window
        token_counter_user_input = ttk.Label(window, text="Estimated Tokens: 0")
        token_counter_user_input.grid(row=3, column=1, sticky='e', padx=10, pady=10)

        # Create the second textbox with scrollbar
        text_input = tk.Text(window, wrap=tk.WORD, font=('Calibri', 12), padx=10, pady=10)
        text_input_starting_height = text_input.winfo_reqheight()/20
        scrollbar2 = ttk.Scrollbar(window, orient='vertical', command=text_input.yview)
        text_input.configure(yscrollcommand=scrollbar2.set)
        text_input.grid(row=4, column=1, sticky='nsew', padx=10, pady=10)
        scrollbar2.grid(row=4, column=2, sticky='ns')

        # Bind right click on the sytem prompt Text widget to a callback to expand the window
        def on_right_click(event):
            if text_input.winfo_reqheight()/20 > text_input_starting_height:
                text_input.configure(height=text_input_starting_height)
            else:
                text_input.configure(height=150)
        text_input.bind("<Button-3>", on_right_click)

        # Create a label for the third textbox (LLM response)
        label3 = ttk.Label(window, text="LLM Response:")
        label3.grid(row=5, column=1, sticky='w', padx=10, pady=10)

        # Create timer for generation
        generation_timer = ttk.Label(window, text="")
        generation_timer.grid(row=5, column=1, sticky='e', padx=10, pady=10)

        # Create the third textbox with scrollbar
        text_output = tk.Text(window, wrap=tk.WORD, font=('Calibri', 12), padx=10, pady=10)
        text_output_starting_height = text_output.winfo_reqheight()/20
        scrollbar3 = ttk.Scrollbar(window, orient='vertical', command=text_output.yview)
        text_output.configure(yscrollcommand=scrollbar3.set)
        text_output.grid(row=6, column=1, sticky='nsew', padx=10, pady=10)
        scrollbar3.grid(row=6, column=2, sticky='ns')

        # Bind right click on the sytem prompt Text widget to a callback to expand the window
        def on_right_click(event):
            if text_output.winfo_reqheight()/20 > text_output_starting_height:
                text_output.configure(height=text_output_starting_height)
            else:
                text_output.configure(height=150)
        text_output.bind("<Button-3>", on_right_click)

        # Configure the textboxes to dynamically resize
        window.grid_rowconfigure(2, weight=4)  # First textbox (system prompt) takes less vertical space
        window.grid_rowconfigure(4, weight=1)
        window.grid_rowconfigure(6, weight=1)
        window.grid_columnconfigure(1, weight=1)

        # Define callback for model selection
        def on_model_select(event):
            global llm_provider
            model_name = combo.get()
            llm_provider = [i["provider"] for i in paraitus.MODELS if i["name"] == model_name][0]

        combo.bind("<<ComboboxSelected>>", on_model_select)

        # Define some callbacks for certain keyboard events
        def on_submit(event):
            # Get the text from the input field
            text_content = text_input.get('1.0', 'end')
            print(f"Text entered: {text_content}")

            # Get the text from the system prompt field
            system_prompt_content = system_prompt.get('1.0', 'end')
            print(f"System prompt: {system_prompt_content}")

            # Get the temperature and top-p values
            temperature = float(temperature_input.get())
            top_p = float(top_p_input.get())

            # Delete the newline character added to the input field
            text_input.delete('end-1c linestart', 'end')

            # Clear the output field
            text_output.delete('1.0', 'end')

            # Create a new thread for updating the output field
            update_thread = threading.Thread(target=update_output,
                                             args=(text_content, system_prompt_content, temperature, top_p))
            update_thread.start()

        def update_output(text_content, system_prompt, temperature, top_p):
            # Get response from the LLM provider
            start_time = time.time()
            
            global llm_provider
            if llm_provider.streaming is True:
                response_gen = llm_provider.generate_stream(
                    prompt=text_content,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    top_p=top_p
                )
            else:
                generation_timer.config(text=f"Generating response...")
                start_time = time.time()
                response_gen = [llm_provider.generate(prompt=text_content, system_prompt=system_prompt, temperature=temperature, top_p=top_p)]
                generation_timer.config(text=f"Generation time: {int(time.time() - start_time)}s")

            # Enter the response into the output field (either streaming or all at once)
            last_update_time = 0
            for i in response_gen:
                if len(i) > 0:
                    # Add text to output window as it is generated
                    text_output.insert('end', i)

                    # Update generation timer (every second) if streaming
                    if llm_provider.streaming is True:
                        if time.time() - last_update_time > 1:
                            generation_timer.config(text=f"Generating: {int(time.time() - start_time) + 1}s")
                            last_update_time = time.time()

                    # Update the GUI to reflect the changes
                    text_output.update_idletasks()

            # format the output text for code blocks
            utils.format_code_blocks(text_output.get('1.0', 'end'), text_output)

        def select_all(event):
            event.widget.tag_add("sel", "1.0", "end")
            return "break"  # https://stackoverflow.com/a/5871414

        def on_typing(event):
            # Get the text box associated with the event
            text_box = event.widget

            # Get the token label associated with the text box
            token_label = token_counter_system_prompt if text_box == system_prompt else token_counter_user_input

            # Get the text from the input field
            text_content = text_box.get('1.0', 'end')

            # Update the token counter for the user input field, using the estimate of ~4 characters per token (for english!)
            token_label.config(text=f"Estimated Tokens: {len(text_content)//4}")

        def on_paste(event):
            # Get the text that was pasted
            clipboard_content = root.clipboard_get()

            # Get the type of the pasted content
            if os.path.sep in clipboard_content:
                if os.path.exists(clipboard_content):
                    # Check the filetype
                    ftype = paraitus.utils.check_filetype(clipboard_content)

                    if ftype == "text":
                        # If the clipboard content is a text file, read its contents
                        with open(clipboard_content, "r") as file:
                            file_content = file.read()

                        # Replace the clipboard contents with the loaded file
                        root.clipboard_clear()
                        root.clipboard_append(file_content)
                    else:
                        pass # TODO: add handling of other filetypes like images, PDFs, etc.

        # Bind the typing event to the on_typing function for the text input widgets
        system_prompt.bind("<Key>", on_typing)
        text_input.bind("<Key>", on_typing)

        # Bind the <<Paste>> event to the on_paste function
        system_prompt.bind("<<Paste>>", on_paste)
        text_input.bind("<<Paste>>", on_paste)

        # Select all text in text input fields with Ctrl+A
        text_input.bind("<Control-a>", select_all)
        text_output.bind("<Control-a>", select_all)
        system_prompt.bind("<Control-a>", select_all)

        # Submit with Enter key
        window.bind("<Control-Return>", on_submit)

        # Select model dropdown
        window.bind("<Control-m>", lambda event: combo.focus_set())

        # Select user input
        window.bind("<Control-u>", lambda event: text_input.focus_set())

        # Select system prompt
        window.bind("<Control-s>", lambda event: system_prompt.focus_set())

        # Select output text
        window.bind("<Control-o>", lambda event: text_output.focus_set())

        # Close the window with Escape key, only if it has focus
        def close_window(event):
            global windows
            active_window = event.widget.winfo_toplevel()
            if active_window in windows:
                active_window.destroy()
                windows.remove(active_window)

        window.bind("<Escape>", close_window)

        # Force Tkinter to update the GUI and create the window
        time.sleep(0.1)
        window.update_idletasks()

        # Focus the first text field
        window.after(100, lambda: text_input.focus_set())

    # Set up the OS-wide keyboard listener to open the window
    listener = keyboard.GlobalHotKeys({'<ctrl>+<alt>+p': on_key_press})
    listener.start()

    def handle_sigint(signal, frame):
        listener.stop()
        os._exit(0)

    # Register the signal handler
    signal.signal(signal.SIGINT, handle_sigint)

    # Start the main loop
    logging.info("Ready to listen for hotkey!")
    root.mainloop()

if __name__ == "__main__":
    # Run main function
    main()