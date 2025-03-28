from unittest import TestCase

from models import OrganizeResponse, Rename, GroupedItems


class TestOrganizeResponse(TestCase):
    def test_new_folders_renamed(self):
        organizer_response = OrganizeResponse(renames=[
            Rename(from_name="test1", to_name="test2"),
            Rename(from_name="test11", to_name="test22"),
            Rename(from_name="test4", to_name="test3"),
            Rename(from_name="not existing", to_name="another not existing"),
        ],
        grouped_items=[
            GroupedItems(name="test folder", files = ["test1", "not renamed"]),
            GroupedItems(name="test folder 2", files=['test4', 'test11', 'not renamed 2'])
        ])

        new_folders_renamed = organizer_response.new_folders_renamed()
        self.assertEqual(new_folders_renamed, [
            GroupedItems(name="test folder", files = ["test2", "not renamed"]),
            GroupedItems(name="test folder 2", files=['test3', 'test22', 'not renamed 2'])
        ])
