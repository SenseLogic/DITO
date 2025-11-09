![](https://github.com/senselogic/DITO/blob/master/LOGO/dito.png)

# Dito

Structured image description generator.

## Description

Dito uses a pre-trained vision-language model to automatically generate concise, human-readable captions for images. It processes all images in a given folder and outputs structured JSON grouped by subfolder which can be used for dataset annotation, content indexing, or training data preparation.

## Installation

```bash
pip install torch torchvision transformers pillow
```

## Usage

```bash
python dito.py {image folder path} {image description data file path}
```

Example:
```bash
python dito.py IMAGE_FOLDER/ image_description_data.json
```

## Format

The output is a JSON object where:
- **Keys** are relative subfolder paths (or `""` for the root folder).
- **Values** are objects mapping image file labels to their generated captions.

```json
{
  "": {
    "forest": "a person walking down a snowy path in the woods",
    "plane": "a blue and white plane",
    "ship": "two large ships in the water",
    "train": "snow on the ground"
  },
  "animal/": {
    "cow": "a brown cow standing on top of a grass covered hill",
    "robin": "a small bird sitting on a branch in the snow",
    "weaver": "a red bird sitting on a branch"
  },
  "landscape/": {
    "mountains": "a body of water",
    "mountains_2": "a clear blue sky"
  }
}
```

## Limitations

- Only image files with the following extensions are processed : `.avif`, `.jpg`, `.jpeg`, `.png`, `.webp`.

## Version

0.1

## Author

Eric Pelzer (ecstatic.coder@gmail.com).

## License

This project is licensed under the GNU General Public License version 3.

See the [LICENSE.md](LICENSE.md) file for details.
