#### Date: 22nd of October, 2025

Implementation of a html+css+js rendering widget using Ultralight and Kivy. The main widget class, Websurface, can be easily used like any other widget in Kivy, although many features are still experiemental as of writing this message.
Please see the README.md for documentation on how to use this code.

#### Date: 23rd of October, 2025

Worked on translating most events from Kivy to the Ultralight renderer backend

#### Date: 24th of October, 2025

Worked largely on translating keyboard presses from Kivy to Ultralight. Got stuck at interpreting events having modifiers too, like Caps Lock and shift

#### Date: 3rd of November, 2025

- Still wworked on properly translating keyboard inputs. Also worked on extending the WebSurface widget to allow multiple independent instances, just like other all other widgets.
- Finished working on translating the keyboard input for now. Work still needs be done with respect to accounting for all input method.
- Work remains to be done for translating game pad input