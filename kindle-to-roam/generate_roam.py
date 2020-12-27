import argparse
import json
import os
import re
from collections import defaultdict


class RoamGenerator:

    def __init__(self, markdown_path, clippings_path):
        """
        :param markdown_path: str
        """
        self.clippings = ""
        self.page_header = ""
        self.clippings_list = list()
        self.diff = defaultdict(list)
        self.markdown_path = markdown_path
        self.existing_database = self.load_database()
        self.clippings_path = clippings_path

    def read_header(self):
        """
        Reads header template for the page.
        """
        with open("header.txt", 'r') as f:
            self.page_header = f.read()

    def load_database(self, database_path="database.json"):
        """
        Loads the database with existing notes.
        :param database_path: str
        :return: dict
        """
        if os.path.isfile(database_path):
            with open(database_path, 'r') as f:
                database = json.load(f)
        else:
            database = defaultdict(list)
        return self.deserialize_tuples(database)

    # @staticmethod
    def dump_database(self, db, database_path="database.json"):
        """
        Dumps database to json file.
        :param db: dict
        :param database_path: str
        """
        serialized_db = self.serialize_tuples(db)
        with open(database_path, 'w') as f:
            json.dump(serialized_db, f)

    def read_clippings(self):
        """
        Reads clippings directly from Kindle.
        """
        with open(self.clippings_path, 'r', encoding='utf-8') as f:
            self.clippings = f.read()

    def clear_clippings(self):
        """
        Gets rid of rubbish in clippings.
        """
        self.clippings_list = [s.strip('\n').strip('\ufeff') for s in self.clippings.split('==========')]

    def process_clippings(self):
        """
        Populates diff and database dictionaries with new data.
        """
        for note in self.clippings_list:
            header = note.split('\n')[0]
            title = header.split(" (")[0]
            r = re.search(r'(?<=\()[^.]*', header[:-1])
            author = r.group() if r else ''

            page_name = (title, author)
            if ("Ваш выделенный отрывок в месте" or "Your Highlight at location") in note:
                text = note.split('\n\n')[-1]

                self.existing_database = self.update_db(self.existing_database, page_name, text)

                if page_name not in self.diff:
                    self.diff = self.update_db(self.diff, page_name, text)

                elif text not in self.diff[page_name]:
                    self.diff[page_name].append(f"- {text}\n")
    #         if 'Ваш выделенный отрывок в месте' in note:
        #         text = note.split('\n\n')[-1]
        #         previous_chunk = result[head][-1].strip("\n") if result[head] else None
        #         if result[head] and previous_chunk and text.startswith(previous_chunk.strip("- ")):
        #             del result[head][-1]
        #         if result[head] and previous_chunk.endswith(text): continue
        #         result[head].append(f"- {text}\n")

    @staticmethod
    def update_db(db, page_name, text):
        """
        Adds a note to database.
        :param db: dict
        :param page_name: str
        :param text: str
        :return:
        """
        previous_chunk = db[page_name][-1].strip("\n") if db[page_name] else ""

        if previous_chunk.endswith(text):
            return db
        elif previous_chunk and text.startswith(previous_chunk.strip("- ")):
            del db[page_name][-1]
        db[page_name].append(f"- {text}\n")
        return db

    @staticmethod
    def deserialize_tuples(parsed_json):
        """
        Makes strings in json keys tuples.
        :param parsed_json:
        :return: dict
        """
        dict_json = defaultdict(list)
        for key, value in parsed_json.items():
            key = eval(key)
            dict_json[key] = value
        return dict_json

    @staticmethod
    def serialize_tuples(dictionary):
        """
        Makes tuples in json keys strings.
        :param dictionary:
        :return: dumpable json
        """
        str_json = defaultdict(list)
        for key, value in dictionary.items():
            key = str(key)
            str_json[key] = value
        return str_json

    def diff_to_markdown(self, markdown_path):
        """
        Dumps difference to markdown files.
        :param markdown_path: str
        """
        if not os.path.exists(markdown_path):
            os.makedirs(markdown_path)
        for book, note in self.diff.items():
            page_title = book[0]
            author = book[1]
            note = ''.join(note)
            content = self.page_header.format(author=author, note=note)
            page_title = re.sub("[<>’‘]", "'", page_title)
            page_title = re.sub("[|#?]", "", page_title)
            with open(os.path.join(markdown_path, f"{page_title}.md"), 'w', encoding='utf-8') as f:
                f.write(content)
        print("Diff dumped to Markdown.")
        # self.dump_database(self.diff)

    def run(self):
        """
        Runs the whole pipeline.
        """
        print("Start running...")
        self.read_header()
        self.read_clippings()
        self.clear_clippings()
        self.process_clippings()
        self.diff_to_markdown(self.markdown_path)
        self.dump_database(self.existing_database)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--clippings_path', type=str, nargs='?',
                        default="/Volumes/Kindle/documents/My Clippings.txt",
                        help='clippings path')
    parser.add_argument('--markdown_path', type=str, nargs='?', default="markdown",
                        help='path for saving markdown files')
    args = parser.parse_args()
    generator = RoamGenerator(args.markdown_path, args.clippings_path)
    generator.run()
