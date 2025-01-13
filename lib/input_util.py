from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit import PromptSession


def get_multiline_input(prompt):
  # Create custom key bindings
  bindings = KeyBindings()

  # Define behavior for Enter
  @bindings.add("enter")
  def _(event):
      buffer = event.app.current_buffer
      if event.key_sequence[0].data == '\n' and event.key_sequence[0].key.name == "Enter" and buffer.is_multiline():  # Check for multiline buffer
          buffer.insert_text("\n")  # Shift+Enter inserts a newline
      else:  # Regular Enter
          if buffer.document.text.strip():  # Submit if there is content
              buffer.validate_and_handle()
          else:  # Insert newline if empty
              buffer.insert_text("\n")

  # Create the prompt session with the custom key bindings
  session = PromptSession(multiline=True, key_bindings=bindings)

  # Prompt user for input
  multiline_input = session.prompt(prompt)
  return multiline_input
