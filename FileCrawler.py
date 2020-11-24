import os

__all__ = ["FileCrawler"]


class FileCrawler:

    def __init__(self, link=None):
        self.folder_list = []
        if link is None:
            directory = os.getcwd()
        else:
            directory = link
        self.folder_names = {}
        self.dir_tree = {}

        for root, dirs, files in os.walk(directory, followlinks=False):
            dir_list = []
            for folder in dirs:
                dir_list.append(folder)
            self.dir_tree[root] = dir_list

            sub_file_list = []
            for file in files:
                if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg") or file.endswith(".gif") \
                        or file.endswith(".tiff") or file.endswith(".bmp") or file.endswith(".tif"):
                    sub_file_list.append(os.path.join(root, file))
            if len(sub_file_list) != 0:
                self.folder_names.update({root: sub_file_list})
            else:
                continue

    def pull_folders(self, root):
        self.folder_list.clear()
        for key in self.dir_tree[root]:
            self.folder_list.append(key)
        if len(self.folder_list) > 0:
            return self.folder_list
        else:
            return -1

    def file_list(self, folder):
        try:
            return self.folder_names[folder]
        except KeyError:
            return -1
