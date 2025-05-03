#!/usr/bin/env python3

import argparse
import datetime
import hashlib
import boto3

S3_DEFAULT_REGION_NAME = "us-east-1"

BOLD        = '\033[1;32m'
GREEN       = '\033[0;32m'
GREEN_BOLD  = '\033[1;32m'
RED         = '\033[0;31m'
RED_BOLD    = '\033[1;31m'
YELLOW      = '\033[0;33m'
YELLOW_BOLD = '\033[1;33m'
BLUE        = '\033[0;34m'
BLUE_BOLD   = '\033[1;34m'
RESET       = '\033[0m'
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


###########
## now() ##
###########
# helper function for pre 3.12 #
# not needed for 3.12 or later #
def now(dt=datetime.datetime.now(datetime.UTC)):
    debug = 0
    s = f'{dt.astimezone():%Y-%m-%d %H:%M:%S%z}'
    #s = f'{datetime.datetime.now().astimezone():%Y-%m-%d %H:%M:%S%z}'
    if debug > 0: print(f"datetime string: {s}")
    return s[:-2] + ':' + s[-2:]


#################
## create_note ##
#################
def create_note():

  # Generate timestamped log filename
  #timestamp = datetime.now().strftime("%Y_%m_%d_%H%M")
  # utcnow() is deprecated leaving here for now for reference
  # old_date      = datetime.datetime.utcnow()
  #n_date    = datetime.datetime.now(datetime.UTC)
  #n_name = f'''note-{n_date}'''
  #n_desc = f'''note-{n_date}'''
  #print(now(n_date))

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
  ###
  ###############
  ## Finish Up ##
  ###############
  ########################################################################
  #                                                                      #
  # because note can take a while to compose                             #
  # or be aborted or left dangling...                                    #
  # lets wait until completion to set meta data (name, desc, timestampt) #
  #                                                                      #
  ########################################################################
  n_date    = datetime.datetime.now(datetime.UTC)
  n_name = f'''note-{n_date}'''
  n_desc = f'''note-{n_date}'''

  ####################################
  ## return note text and meta data ##
  ####################################
  return n_data, n_date, n_name, n_desc

  '''
  # Check if input was entered and print the result
  if n_data.strip():  # Check for non-empty input
      if debug > 0: print(f">>>\nname: {n_name}\ndate: {n_date}\ndesc: {n_desc}\n{n_data}\n<<<")
      timestamp = n_date.strftime("%Y_%m_%d_%H%M")
      print()
      print(f"md5 hash is: {get_hash(n_data)}")
  else:
      print("No input was entered.")
  '''


############
# generate_hash #
############
# if testing with echo, don't forget the -n to prevent new line
# $: echo -n "just a test" | md5sum
# 25c674ceb1d7e145c01011d697c6e52f  -
#
def generate_hash(note):
    """Compute MD5 hash of a note."""
    md5_hash = hashlib.md5()
    md5_hash.update(note.encode('utf-8'))
    return md5_hash.hexdigest()


######################
## put_note_to_s3() ##
######################
def put_note_to_s3(s3client, bucket, note_name, prefix="/", region="us-east-1"):
  print(f"putting note {GREEN}{note_name}{RESET} to bucket {GREEN}{bucket}{RESET} with prefix {GREEN}{prefix}{RESET} in region {GREEN}{region}{RESET}")


def main():
  ##################################
  ## parse command line arguments ##
  ##################################
  parser = argparse.ArgumentParser(description="create note and write to s3 with a specified prefix")
  parser.add_argument("--bucket_name", required=True, help="Name of S3 bucket.")
  parser.add_argument("--prefix", required=True, help="S3 prefix to organizes notes.")
  parser.add_argument("--region", required=False, default="us-east-1", help="AWS region to use, default is us-east-1")
  args = parser.parse_args()

  ###############
  ## s3 client ##
  ###############
  #s3_region_name = S3_DEFAULT_REGION_NAME
  s3_region_name = args.region
  desclen = 25
  s3 = boto3.client("s3", region_name=s3_region_name)

  ###################
  ## create a note ##
  ###################
  # create note, do not generate name or timestamp until returned
  n_data, n_date, n_name, n_desc = create_note()

  ########################
  ## if empty note exit ##
  ########################
  if not n_data.strip():  # Check for empty input
      print("No input was entered.")
      exit(-1)

  #timestamp = n_date.strftime("%Y_%m_%d_%H%M")
  #dt_string = now()
  #print(dt_string)

  ###############
  ## Naming ?? ##
  ###############
  ###################################################################
  # not sure yet how im doing this                                  #
  # create note will default name and desc note as <note-timestamp> #
  # desc is changed here to be first desclen chars of the note      #
  ###################################################################

  datalen = len(n_data)
  print(f"datalen: {datalen}")
  if datalen < desclen:
    desclen = datalen
      
  n_desc = n_data[0:desclen] + "-" + str(n_date)

  #####################################
  ## generate the hash for this note ##
  #####################################
  n_hash = generate_hash(n_data)


  print(f"ndate: {n_date}")
  print(f"nname: {n_name}")
  print(f"ndesc: {n_desc}")
  print(n_data)
  print(f"nhash: {n_hash}")

  put_note_to_s3(s3, args.bucket_name, n_name, prefix=args.prefix, region=args.region)


if __name__ == '__main__':
  main()



