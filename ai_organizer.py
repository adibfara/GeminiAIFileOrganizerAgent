from typing import List

import litellm
from litellm import completion

from models import OrganizeResponse


class AIOrganizer:

    def organize(self, files: List[str], folders: List[str]) -> OrganizeResponse:
        prompt = self.prompt(files, folders)
        messages = [
            prompt
        ]
        litellm.enable_json_schema_validation = True
        response = completion(model="gemini/gemini-2.0-flash-exp", messages=messages, response_format=OrganizeResponse)
        content = response.choices[0].message.content
        organize_response = OrganizeResponse.model_validate_json(content)
        return organize_response

    def prompt(self, files: List[str], folders: List[str]):
        prompt_message = f"""You are a folder organizer agent. Your job is to analyze the current items (files/folders) given to you
                          and suggest how to organize the files by: 
                          1. Renaming files/folders. 
                          2. Creating new folders to group similar files/folders.
                          
                          <Items>
                          Input Files:
                          {files}
                          Folders:
                          {folders}
                          </Items>
                          
                          You can use `grouped_items` to group similar files/folders into a new/existing folder.
                          Each grouped item contains a name (the folder to be used/created), and a list of files which can be regular files or directories that need to be moved to that folder.
                          
                          You can also rename files so they have a better structurally name (using the rules below).
                          use `renames` to rename an item (file/folder) to a new name.
                          
                          <Rules>
                          - Only create folders to group multiple and similar items. 
                          - Do not create folders for a single item.
                          - You don't need to rename or move all files/folders. Just the ones that are better moved to a folder, or are enhanced by a better name.
                          - In new folder creation, use files' original name, as all the renames will be done after creating the folders.
                          - You can rename both files and folders.
                          - Remove underlines from movie and media names.
                          - If the file/folder is a movie name, always add a movie's year to the beginning and use the movie's complete name (whether it's a folder or a file). For example, if the name of the file is 'matrix', you should rename it to '(1999) The Matrix'. You don't need to do this for series or shows or personal movies.
                          - Do not create multiple folders with the same name, just use the same folder.
                          - If a folder exist, you can use its name to move files into it.
                          - New folders cannot be self referential.
                          </Rules>
                          
                          <Examples>
                          - two folders and 1 file (lost season 1, lost s2, lost s03e02_great_encode.mkv, lost s3e2.srt, Lost Season 3 Episode 1.mkv):
                            * A folder called Lost will be created and all items are moved to it
                            * Rename lost season 1 to `Season 1`
                            * Rename lost s2 to `Season 2`
                            * Rename lost s03e02.mkv to Lost Season 3 Episode 2.mkv
                            * Rename lost s3e2.srt to Lost Season 3 Episode 2.srt (to match the file name)
                            * The file Lost Season 3 Episode 1.mkv is not touched since it has a good name.
                          - these files and folders exist: /good fellas, the matrix.mp4,  dream theater - night terror.mp3, /radihead - ok computer, spider man 1.mp4, spiderman 2.mp4
                            * folder good fellas is renamed to (1990) Good Fellas
                            * the matrix.mp4 is renamed to (1999) The Matrix.mp4
                            * dream theater - night terror.mp3 is renamed to Dream Theater - Night Terror.mp3
                            * folder /radihead - ok computer is renamed to /Radiohead - (1997) Ok Computer
                            * A folder called `Spiderman Collection` is created for spiderman 1 and 2.
                            * spiderman 1 is renamed to (2002) Spider-Man
                            * spiderman 2 is renamed to (2004) Spider-Man 2
                          - two folders "in rainbows" and "the bends"
                            * A folder called Radiohead is created and "in rainbows" and "the bends" are moved to it
                            * in rainbows is renamed to (2007) In Rainbows
                            * the bends is renamed to (1995) The Bends
                          </Examples>
                          """

        prompt = {
            "role": "user",
            "content": prompt_message
        }
        return prompt


if __name__ == '__main__':
    AIOrganizer()
