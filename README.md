# mark2epub

mark2epub is a simple Python script for converting Markdown files, images, and
css files to a single ePub book.

## Installation and use

### Dependencies

mark2epub requires:

- Python (>= 3.4)
- markdown (>= 3.1)

### Running mark2epub

The syntax for mark2epub is the following:

    $ python md2epub.py <markdown_directory> <output_file.epub>

The directory `epub_md` is a sample markdown directory for mark2epub.

Note that the directory `markdown_directory` **must** contain

* Markdown `.md` files. Each file represent a chapter in the resulting ePub.
They are processed by name order, and will appear correspondingly in the e-book.

* An `images` folder, containing the images to be included. Only GIF (`.gif`
  extension), JPEG (`.jpg` or `.jpeg` extensions), and PNG (`.png` extension)
  files are currently supported. This folder is *not* processed recursively, so
  all images should be placed at the root of this folder.

* A `css` folder, containing the CSS files. This folder is *not* processed
   recursively, so all css files should be placed at the root of this folder.

* A `description.json` containing meta-information about the e-book. The key
  `cover_image` should indicate the name of the cover image.
  The key `default_css` is a list of css file names that are applied by default
  on all chapters.
  The key `chapters` is a list of dictionaries, each one containing a key `markdown`
  indicating the name of the corresponding markdown file, and a key `css` indicating
  the name of the css file that should be applied specifically to this chapter.
  See the example in the repository for a typical `description.json` file.

## Limitations/Features to be addressed

* Robustness checks in the `mark2epub.py` script
* Recursive processing of the `images` and `css` folders
* Support for additional fonts
* Support for mathematical notation
