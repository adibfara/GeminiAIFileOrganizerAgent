from os import renames
from typing import Optional, List

from pydantic import BaseModel


class Rename(BaseModel):
    from_name: str
    to_name: str

    def formatted(self):
        return f"{self.from_name}\n\t↪{self.to_name}"


class GroupedItems(BaseModel):
    name: str
    files: List[str]

    def formatted(self):
        return f"📁 {self.name}\n\t" + "\n\t".join(self.files)


class OrganizeResponse(BaseModel):
    renames: List[Rename]
    grouped_items: List[GroupedItems]

    def new_folders_renamed(self)->List[GroupedItems]:
        result_folders = []
        for folder in self.grouped_items:
            folder_items = []
            for file in folder.files:
                rename_found = False
                for rename in self.renames:
                    if rename.from_name == file:
                        folder_items.append(rename.to_name)
                        rename_found = True
                if not rename_found:
                    folder_items.append(file)

            new_folder = GroupedItems(name=folder.name, files = folder_items)
            result_folders.append(new_folder)

        return result_folders
