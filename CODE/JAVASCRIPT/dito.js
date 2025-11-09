// -- VARIABLES

export let imageDescriptionData = {};

// -- FUNCTIONS

export function setImageDescriptionData(
    imageDescriptionData_
    )
{
    imageDescriptionData = imageDescriptionData_;
}

// ~~

export function getImageDescription(
    imageFilePath
    )
{
    let imageFolderPath;
    let imageFileName;
    let lastSlashCharacterIndex = imageFilePath.lastIndexOf( '/' );

    if ( lastSlashCharacterIndex >= 0 )
    {
        imageFolderPath = imageFilePath.substring( 0, lastSlashCharacterIndex + 1 );
        imageFileName = imageFilePath.substring( lastSlashCharacterIndex + 1 );
    }
    else
    {
        imageFolderPath = '';
        imageFileName = imageFilePath;
    }

    let imageFileLabel;
    let firstDotCharacterIndex = imageFileName.indexOf( '.' );

    if ( firstDotCharacterIndex >= 0 )
    {
        imageFileLabel = imageFileName.substring(0, firstDotCharacterIndex);
    }
    else
    {
        imageFileLabel = imageFileName;
    }

    if ( imageDescriptionData[ imageFolderPath ]
         && imageDescriptionData[ imageFolderPath ][ imageFileLabel ] )
    {
        return imageDescriptionData[ imageFolderPath ][ imageFileLabel ];
    }
    else
    {
        return imageFileLabel.replaceAll( '_', ' ' ).replaceAll( '-', ' ' );
    }
}
