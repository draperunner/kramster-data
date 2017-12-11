# Kramster Data

Welcome to the Kramster Data repository! Here you'll find the exam insertion tool if you want to add custom exams to your Kramster clone. You'll find instructions on how to contribute to Kramster.it. And of course, you'll find the PDFs and produced txt files that make up Kramster.it.

You have two choices if you want to add an exam to Kramster:
1) Email the PDF to matsbyr@gmail.com (easy!)
2) Follow the instructions in the workflow station below to do it yourself (slightly less easy!)

If your choice is 1), I don't think you need many more instructions. Just google how to send and email. If your choice is 2), on the other hand: Thanks, and please continue reading.

If you'd rather contribute to the code of `inserter.py`, please do! Pull requests are welcome! :)

If you were looking for the Kramster repository, you'll find it here: https://github.com/draperunner/kramster.git

## Procedure
Because no PDFs are similar, adding exams to Kramster includes a manual process. This process consists of
translating the exam to the structured file format explained below, and then inserting it into the database using the
`inserter.py` script.

The file structure of this repo is as follows:

* New exams (PDFs) that have not been processed are put in the `todo` folder.
* Exams that are being processed, that is, being written on the specified file format, are put in the `doing` folder.
* When an exam is done, the PDF and the produced .txt file are put in the `done` folder.

It doesn't get much simpler than that, huh?

If you want to just add an exam to this repo, make a pull request with your exam in the `todo` folder. You don't have to do the whole procedure. :)

If you want to process an exam that is in `todo`, move it to `doing` and create a .txt file with the same name, and start writing. If you are a hero and finishes the exam, please don't put in `done`, but create a pull request. I will put in the `done` folder after it has been published to kramster.it.

## The File Format
In this section, the format of the exam file format is explained. Some examples are provided. For complete examples, check the `done/txts` folder. It's full of examples!

PS! Some txts are written on another, older, legacy format. Those have each question defined on a single line. That was too hard to work with. The `old_inserter.py` is still around in case some of the old exams need to be edited and reinserted.

### Meta
The first line is the _school_ name, which is the full name followed by the abbreviation in parenthesis. Example: `Norges Teknisk-Naturvitenskaplige Universitet (NTNU)`.

The second line is the _course_ name, which is the full name of the course, beginning with its code. Example: `TTM4137 Wireless Security`.

The third line is the _exam_ name. Usually, the exam name starts with the year it was held. Exams are sorted by their names. Therefore, starting
with the year, then the semester or quarter it was held, will lead to correct order.

The fourth line is the _mode_ of the exam, and can be either `TF` for true/false or `MC` for multiple choice. If all questions in the exam have only the possible answers "True" and "False", this line should be `TF`, otherwise `MC`.

Example of start of file:
```
Norges Teknisk-Naturvitenskaplige Universitet (NTNU)
TTM4137 Wireless Security
2015 Fall
MC
```

### Questions
The rest of the file will consist of a series of _questions_. Each question starts with a line consisting of a single `Q`. The following line is the _index of the correct answer_. All questions will have a number of possible alternatives. The first alternative will have index 0, the second 1, and so on.

After the index of the correct answer, we write the actual question. It can go over as many lines as you want. See the next subsection for instructions on how to add images and math equations.

Then it's time for the alternatives. An alternative (or _option_) will start with a line consisting of a lonely `O`. Whatever comes after it is the alternative. As for the question, alternatives can contain images and equations.

After all the alternatives have been written, you can add an explanation, which will be shown after the user has answered. The explanation starts after a line saying `EXPLANATION`.

Example of a valid true/false question:
```
Q
0
Is 2 + 2 = 4?
O
True
O
False
```
2 + 2 is of course 4, and the index of "True" is 0, so 0 comes right after the Q.


Example of a valid multiple choice question:
```
Q
3
What is 2 + 2?
O
1
O
2
O
3
O
4
O
It's an unsolved problem.
EXPLANATION
Of course 2 + 2 = 4. It's basic math.
```
Note that 4 is the correct answer to this question, and that the _index_ of 4 is 3, so the 3 comes on line two.

### Images and Math Equations and Stuff
Questions and alternatives accept safe HTML. This includes the `<img>` tag. We'll use that to add images.
To add an image, you need cut it out of your PDF and Base64 encode it. You can use the `base64` unix tool, or an online tool like https://www.base64-image.de/. Then put the resulting string `MYIMAGE` into an img element like this: `<img class="img-responsive" alt="Figure 1" src="data:image/png;base64,MYIMAGE" />`. Your MYIMAGE string will be very long and random-looking. The img element can be included in the question or alternative. I recommend putting it and the end of the text, if it's not very important to have it in the middle of the text.

Kramster uses Katex (https://github.com/Khan/KaTeX) for rendering math equations. This lets us write equations using LaTeX. For inline equations, or math style font on words, variables or function names, wrap them in `\(` and `\)`. For bigger or more important equations that deserve their own lines, wrap them in `$$` and `$$`.

Example of inline equation: `The function \(f(x) = x \) is continuous`.

Example of block style equation: `The following equation will be on its own line $$ F = ma $$`.

## Using the Inserter
The Python 3 CLI script `inserter.py` has the following usage:
```
python3 inserter.py --help
```
```
usage: inserter.py [-h] [-d] [-r] [-e] [--db DB] file [file ...]

Kramster inserter

positional arguments:
  file               files to insert or remove

optional arguments:
  -h, --help         show this help message and exit
  -d, --delete       delete exam
  -r, --reinsert     delete and insert exam
  -e, --explanation  add explanation to existing questions
  --db DB            database to use (default: kramster)
```

When you have written a .txt file on the format described above, you can add it to your database using this script. The default database name is `kramster`, running on your local MongoDB instance.

Example usage: `python3 inserter.py doing/tdt4100-2014h.txt`

If everything goes well, you'll see the exam in your browser. If the program crashes, you likely have an error in your txt file.

After testing your freshly produced exam, you might have found a typo or some other error. You will then fix this in your txt file. To reinsert the exam into your database, you can use the `--reinsert` or `-r` option of the script. Like this: `python3 inserter.py doing/tdt4100-2014h.txt -r`. Then go test your changes!
