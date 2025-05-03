#!/usr/bin/env python3

import datetime

BOLD        = '\033[1;32m'
GREEN       = '\033[0;32m'
GREEN_BOLD  = '\033[1;32m'
RED_BOLD    = '\033[1;31m'
YELLOW_BOLD = '\033[1;33m'
BLUE_BOLD = '\033[1;34m'
UNBOLD      = '\033[0m'

# from prompt_toolkit
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout import Layout
from prompt_toolkit import Application

debug = 1

'''
  create a text note
  allow for editing across multiple lines
  ctrl-d completes the note

  required:
    import datetime
    from prompt_toolkit.styles import Style
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.widgets import TextArea
    from prompt_toolkit.layout import Layout
    from prompt_toolkit import Application
'''


#################
## create_note ##
#################
def create_note():

  n_date      = datetime.datetime.utcnow()
  n_name = f'''note-{n_date}'''
  n_desc = f'''note-{n_date}'''

  # Define custom style (optional)
  custom_style = Style.from_dict({
      '': '#00ff00',  # Default style (for all text)
      'fg': 'fg:#00ff00',  # Foreground color green (example)
  })

  # Create key bindings for handling Ctrl-D
  kb = KeyBindings()

  @kb.add('c-d')
  def _(event):
      "Pressing Ctrl-D will terminate input."
      event.app.exit()

  def get_multiline_input():
      print("Enter multiple lines. Press Ctrl-D to finish.")

      # Create a TextArea widget for displaying the input field
      text_area = TextArea(
          height=10,  # The height of the input area (10 lines tall)
          prompt='',  # The prompt that appears at the beginning of each line
          multiline=True,  # Allow multiline input
          wrap_lines=True  # Wrap text in the TextArea
      )

      # Create the layout for the application
      layout = Layout(text_area)

      # Create the application with the layout, key bindings, and style
      app = Application(
          layout=layout,
          key_bindings=kb,
          style=custom_style,
          full_screen=False  # This ensures it uses the entire terminal screen
      )

      # Run the app to capture the input
      app.run()

      # After Ctrl-D is pressed, explicitly capture the content from the TextArea
      return text_area.text  # Return the text inside the TextArea

  # Capture the user input from the multiline prompt
  #user_input = get_multiline_input()
  n_data = get_multiline_input()

  # Check if input was entered and print the result
  if n_data.strip():  # Check for non-empty input
      if debug > 0: print(f">>>\n{n_data}\n<<<\n")
      print()
  else:
      print("No input was entered.")

def main():
  create_note()


if __name__ == '__main__':
  main()

