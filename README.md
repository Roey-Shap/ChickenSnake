ChickenSnake
=
ChickenSnake is a scrappy script to convert **spreadsheets** of custom MtG cards into images and metadata for **[Cockatrice](https://cockatrice.github.io/)** and **[Draftmancer](https://draftmancer.com/)** to use.

Usage
=
The only thing you'll need is a spreadsheet of custom card data.
For specifics of using ChickenSnake, refer to the manual:

For Windows users, simply download the BUILD folder and place your spreadsheet in the Inputs folder. Put its name in the JSON file, give it an output path, and watch it go. 

For non-Windows users, you'll need Python installed. Then you can download the SRC folder and run *python ChickenSnake.py* from the console after configuring the JSON file as mentioned above.
<br>
You can see an example of a spreadsheet by finding the spreadsheet for a set I made in the *DoD3* folder.

Opening *metadata.py* will allow you to configure ChickenSnake's behavior. 
For more details, do visit the instruction document.

Credits
=
Built for **[Cockatrice](https://cockatrice.github.io/)** and **[Draftmancer](https://draftmancer.com/)**. Continued effort here was facilited by their existances!
<br>None of the fonts are mine. 
<br>Used PIL and some built-in Python modules. 
<br>Built for Windows-Ease with PyInstaller!