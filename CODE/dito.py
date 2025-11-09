# -- IMPORTS

import json
import os
from pathlib import Path
from PIL import Image
import time
from transformers import ( BlipProcessor, BlipForConditionalGeneration )
from typing import Dict, List
import sys

# -- CONSTANTS

IMAGE_EXTENSION_SET = { ".avif", ".jpg", ".jpeg", ".png", ".webp" }

# -- FUNCTIONS

def find_image_files(
    image_folder_path: str
    ) -> List[ str ]:

    image_file_array = []
    absolute_image_folder_path = Path( image_folder_path ).resolve()

    for absolute_image_file_path in absolute_image_folder_path.rglob( "*" ):

        if absolute_image_file_path.is_file() and absolute_image_file_path.suffix.lower() in IMAGE_EXTENSION_SET:

            image_file_path = absolute_image_file_path.relative_to( absolute_image_folder_path ).as_posix()
            image_file_array.append( image_file_path )

    return image_file_array

#

def read_image_description_data_file(
    image_description_data_file_path: str
    ) -> Dict[ str, Dict[ str, str ] ]:

    if os.path.exists( image_description_data_file_path ):

        try:

            with open( image_description_data_file_path, "r", encoding = "utf-8" ) as image_description_data_file:

                return json.load( image_description_data_file )

        except ( json.JSONDecodeError, OSError ) as exception_error:

            print( f"Warning: Failed to read image description data file {image_description_data_file_path}: {exception_error}", file=sys.stderr )

            return {}

    return {}

#

def get_image_label_from_path(
    image_path: str
    ) -> str:

    image_filename = Path( image_path ).name
    dot_character_index = image_filename.find( "." )

    if dot_character_index == -1:

        return image_filename

    return image_filename[ : dot_character_index ]

#

def resize_image_for_model(
    image: Image.Image,
    maximum_size: int = 512
    ) -> Image.Image:

    if max( image.width, image.height ) <= maximum_size:

        return image

    image.thumbnail( ( maximum_size, maximum_size ), Image.Resampling.LANCZOS )

    return image

#

def generate_image_description(
    image_path: str,
    model,
    processor
    ) -> str:

    try:

        image = Image.open( image_path ).convert( "RGB" )
        image = resize_image_for_model( image, maximum_size = 384 )

        processor_input_map = processor( images = image, return_tensors = "pt" )

        generated_id_array = (
            model.generate(
                **processor_input_map,
                max_length = 50,
                num_beams = 5
                )
            )

        generated_text = processor.decode( generated_id_array[ 0 ], skip_special_tokens=True )

        image_description = generated_text.strip()

        if image_description.endswith( "." ):

            image_description = image_description[ : -1 ]

        return image_description

    except Exception as exception_error:

        print( f"Error generating image_description for {image_path}: {exception_error}", file=sys.stderr )

        return "No description available."

#

def update_image_description_data(
    image_file_path_array: List[ str ],
    image_description_data: Dict[ str, Dict[ str, str ] ],
    old_image_description_data: Dict[ str, Dict[ str, str ] ],
    image_folder_path: str,
    model,
    processor
    ) -> Dict[ str, Dict[ str, str ] ]:

    absolute_image_folder_path = Path( image_folder_path ).resolve()

    for image_file_path in image_file_path_array:

        image_file_parent_path = Path( image_file_path ).parent

        if image_file_parent_path == Path( "." ):

            folder_path = ""

        else:

            folder_path = image_file_parent_path.as_posix() + "/"

        image_label = get_image_label_from_path( image_file_path )
        absolute_image_path = absolute_image_folder_path / image_file_path

        if folder_path not in image_description_data:

            image_description_data[ folder_path ] = {}

        if image_label in image_description_data[ folder_path ]:

            continue

        if folder_path in old_image_description_data:

            if image_label in old_image_description_data[ folder_path ]:

                image_description = old_image_description_data[ folder_path ][ image_label ]

                print( f"Keeping image_description : {image_file_path}" )
                image_description_data[ folder_path ][ image_label ] = image_description

                continue

        print( f"Generating image_description : {image_file_path}" )
        image_description = generate_image_description( str( absolute_image_path ), model, processor )

        image_description_data[ folder_path ][ image_label ] = image_description

    return image_description_data

#

def write_image_description_data_file(
    image_description_data_file_path: str,
    image_description_data: Dict[ str, Dict[ str, str ] ]
    ) -> None:

    image_description_path = Path( image_description_data_file_path )
    image_description_path.parent.mkdir( parents=True, exist_ok=True )

    with open( image_description_data_file_path, "w", encoding="utf-8" ) as image_description_data_file:

        json.dump( image_description_data, image_description_data_file, indent = 2, ensure_ascii = False )

#

def main(
    ):

    if len( sys.argv ) != 3:

        print( "Usage: dito.py <image_folder_path> <image_description_data_file_path>", file=sys.stderr )
        sys.exit(1)

    image_folder_path = sys.argv[ 1 ]
    image_description_data_file_path = sys.argv[ 2 ]

    if not os.path.isdir( image_folder_path ):

        print( f"Error: Invalid image folder path : {image_folder_path}", file=sys.stderr )
        sys.exit(1)

    print( "Reading image folder..." )
    image_file_path_array = find_image_files( image_folder_path )

    print( "Reading image description data file..." )
    old_image_description_data = read_image_description_data_file( image_description_data_file_path )

    image_description_data = {}

    print( "Reading AI model..." )
    model_path = "Salesforce/blip-image-captioning-base"
    processor = BlipProcessor.from_pretrained( model_path, use_fast=False )
    model = BlipForConditionalGeneration.from_pretrained( model_path )

    print( "Updating image description data..." )
    updated_image_description_data = (
        update_image_description_data(
            image_file_path_array,
            image_description_data,
            old_image_description_data,
            image_folder_path,
            model,
            processor
            )
        )

    print( "Writing image description data file..." )
    write_image_description_data_file( image_description_data_file_path, updated_image_description_data )

    print( "Done!" )

# -- STATEMENTS

if __name__ == "__main__":
    main()
