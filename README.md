ChickenSnake
=
ChickenSnake is a scrappy script to convert **spreadsheets** of custom MtG cards into semi-pretty images and metadata for **[Cockatrice](https://cockatrice.github.io/)** and **[Draftmancer](https://draftmancer.com/)** to use.

Usage
=
The main thing you need to do is put your spreadsheet (.csv) in the same folder as *ChickenSnake.py*. Then you'll simply need to run it in the terminal from the folder containing it like so:
<br>
>python ChickenSnake.py

You can see an example of a spreadsheet by finding the spreadsheet for a set I made in the *DoD3* folder.

Opening *metadata.py* will allow you to configure ChickenSnake's behavior. The main things to control are:
1. Where your input is taken
    1. Name of spreadsheet CSV file with card data
    1. Playtest card image "base images" (borders, etc.)
1. Where the output will be saved
    1. Playtest card image output folder
    1. XML file (for Cockatrice's use)
    1. TXT file (for Draftmancer's use)
    1. Log file (warnings, errors, etc.)

Some other settings include:
1. Cockatrice Set settings
    1. Set name/code, release date/version number, etc.
1. Draftmancer Draft settings
    1. For now just pack distribution. Digging into [Draftmancer's drafting syntax](https://draftmancer.com/cubeformat.html) isn't too hard if you wanna do something else entirely
1. Card rendering settings
1. Program execution settings

Credits
=
Built for **[Cockatrice](https://cockatrice.github.io/)** and **[Draftmancer](https://draftmancer.com/)**. Continued effort here was facilited by their existances!
<br>None of the fonts are mine. 
<br>Used PIL and some built-in Python modules. 