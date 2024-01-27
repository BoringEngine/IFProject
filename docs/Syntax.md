- [Outer Layers](#outer-layers)
- [Story Content](#story-content)
  - [Choices](#choices)
  - [Subroutines](#subroutines)
  - [Goto](#goto)
  - [If](#if)
  - [Modify](#modify)
  - [Switch](#switch)
  - [Print](#print)
  - [Wait](#wait)
- [Special Terminal Types](#special-terminal-types)


Outer Layers
======

The document contains an element of type BLOCKS. There is only one document. (No load functionality yet).

[VARS] --> List of [VAR]

[VAR] --> Set with
    + name: [ID]
    + type: [DATA_TYPE]
    ? value: [VALUE]

[BLOCKS] --> List of [BLOCK]

[BLOCK] --> Set with
    + name: [ID]
    ? start: Bool
    ? img: [FILE_PATH]
    At least one of
        content: [CONTENT]
        blocks: [BLOCKS]


Story Content
======

[CONTENT] --> List of [STORY_COMMAND]

[STORY_COMMAND] --> One of
    [CHOICE]
    [GOSUB]
    [GOTO]
    [IF]
    [IF_LIST]
    [MODIFY]
    [SWITCH]
    [PRINT]
    [WAIT]


Choices
------

[CHOICE] --> Set with
    + choice: [ID]
    ? text: [SHORT_TEXT]
    ? reusable: Bool
    ? shown_effects: [SHOWN_EFFECTS]
    + effects: [CONTENT]

[SHOWN_EFFECTS] --> List of [SHOWN_EFFECT]

[SHOWN_EFFECT] --> One of
    [GAIN_EFFECT]
    [PAY_EFFECT]

[GAIN_EFFECT] --> Set with
    + gain: [ID]
    + amount: Unsigned Int

[PAYMENT_CHOICE_COST] --> Set with
    + pay: [ID]
    + amount: Unsigned Int


Subroutines
------

[GOSUB] --> Set with
    + gosub: [ADDRESS]


Goto
------

[GOTO] --> Set with
    + goto: [ADDRESS]


If
------

[IF] --> Set with
  + if: [EXPRESSION]
  + then: [CONTENT]
  ? else: [CONTENT]

[EXPRESSION] --> Valid python expression to be used with eval()

[IF_LIST] --> List of [IF]


Modify
------

[MODIFY] --> Set with
    + modify: [ID]
    One of
        add: [ID_OR_VALUE]
        multiply: [ID_OR_VALUE]
        set: [ID_OR_VALUE]


Switch
------

[SWITCH] --> Set with
    + switch: [ID]
    + cases: [CASES]

[CASES] --> List of [CASE]

[CASE] --> Set with
    + case: [VALUE]
    + then: [CONTENT]


Print
------

[PRINT] --> Set with
    + print: [LONG_TEXT]


Wait
------

[WAIT] --> Set with
    + wait: Null


Special Terminal Types
======

[SHORT_TEXT] --> Anything recognized as a single valid text string in YAML, fitting on one line

[LONG_TEXT] --> Text in YAML, but split across multiple lines in the file with the usage of the symbol |

[DATA_TYPE] --> A valid data type (uint, string, etc.)

[VALUE] --> An instance of a valid data type (for example, a string literal, or a number)

[ID] --> (a..zA..Z1..90_)*

[ID_OR_VALUE] --> One of
    [ID]
    [VALUE]

[FILE_PATH] --> ? [FILE_PATH] .. "/" [FILE_NAME]

[FILE_NAME] --> [ID] .. "." .. [ID]

[RETURN] --> Set with
  return: Null