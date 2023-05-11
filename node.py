import re


class Node:
    def __init__(self, name, text):
        self.sheet_name = name
        self.item_list = []
        self.child_node_dict = {}
        self.child_node_list = []
        self.with_node_dict = {}
        self.raw_text = text
        self.text = self.del_comment_text(text)
        self.raw_code_text = self.split_with_code_text(self.text)
        self.code_text = self.merger_with_code_text(self.raw_code_text)
        return

    def split_with_code_text(self, text):
        start = self.find_string(r'\bwith\b', text)
        if start == -1:
            return text
        text = text[start+4:]
        while True:
            name = re.search(r'\b\w*\b', text).group()
            start, end = self.find_parentheses(text)
            self.with_node_dict[name] = text[start:end+1]
            text = text[end+1:]
            if not re.match(r'\s*,', text):
                break
        # self.merger_with_code_text(text)
        return text

    def merger_with_code_text(self, text):
        key_set = ('where', 'limit', 'group', 'union', 'left', 'right', 'full', 'inner', 'join')
        code_text = ''.join([(c) for c in text]).lower()
        for key, value in self.with_node_dict.items():
            find_pos = re.search(r'\b'+key+r'\b', code_text)
            if find_pos is None:
                continue
            start_pos = find_pos.span(0)[0]
            end_pos = find_pos.span(0)[1]
            next_word = re.search(r'\b\w*\b', code_text[find_pos.span(0)[1]+1:])
            if next_word is None or next_word.group() in key_set:
                end_pos = find_pos.span(0)[1]
                value += ' as ' + key + ' '
            code_text = code_text[:start_pos] + value + code_text[end_pos:]
        return code_text

    @staticmethod
    def del_comment_text(text):
        ret_list = ''
        while True:
            start = text.find('--')
            if start == -1:
                break
            ret_list += text[:start]
            text = text[start:]
            start = text.find('\n')
            if start == -1:
                return ret_list
            text = text[start:]
        ret_list += text
        # print(ret_list)
        return ret_list

    @staticmethod
    def del_comment(word_list):
        ret_word = None
        for word in reversed(word_list):
            if word.find('--') == -1 and ret_word is None:
                ret_word = word
            if word.find('--') == 0:
                ret_word = None
            if word.find('--') > 0:
                ret_word = word.split('--')[0]
        return ret_word

    @staticmethod
    def split_comma(text):
        count = 0
        start = -1
        ret_list = []
        for index, char in enumerate(text):
            if char == ',' and count == 0:
                ret_list.append(text[start+1:index])
                start = index
            if char == '(':
                count += 1
            if char == ')':
                count -= 1
        ret_list.append(text[start+1:])
        return ret_list

    @staticmethod
    def find_string(pattern, string):
        ret = re.search(pattern, string.lower())
        if ret is None:
            return -1
        return ret.span(0)[0]

    def get_item(self):
        start = self.find_string(r'\bselect\b', self.code_text)
        end = self.find_string(r'\bfrom\b', self.code_text)
        if start == -1 or end == -1:
            return -1
        start += 6
        start_distinct = self.code_text[start:].lower().lstrip().find('distinct')
        if start_distinct == 0:
            start = self.code_text.lower().find('distinct') + 8
        word_list = list(map(lambda x: x.strip(), self.split_comma(self.code_text[start:end])))

        for word in word_list:
            append_list = list((None, None))
            word = self.del_comment(word.split()).split('.')
            if len(word) == 1:
                append_list[0] = word[0].strip()
            else:
                append_list[0] = word[1].strip()
                append_list[1] = word[0].strip()
            self.item_list.append(append_list)
        return end

    def get_analyse_child_list(self):
        ret_list = []
        for item in self.item_list:
            if item[0] == '*':
                if item[1] is None:
                    return []
                else:
                    ret_list.append(item[1])
        return ret_list if ret_list else None

    def find_child_node(self, text):
        start_from = self.find_string(r'\bfrom\b', text)
        start_join = self.find_string(r'\bjoin\b', text)
        if start_from == -1 and start_join == -1:
            return None
        if start_from == -1 or (start_join != -1 and start_join < start_from):
            return start_join
        if start_join == -1 or (start_from != -1 and start_from < start_join):
            return start_from
        return None

    def find_parentheses(self, text):
        count = 0
        start = text.find('(')
        end = self.find_child_node(text)
        if start == -1 or (end != -1 and end < start):
            return -1, -1
        for index, char in enumerate(text[start:]):
            if char == '(':
                count += 1
            if char == ')':
                count -= 1
            if count == 0:
                return start, start+index
        return -1, -1

    @staticmethod
    def find_node_name(text):
        tmp_list = text.split()
        if tmp_list[0] == 'as':
            return tmp_list[1]
        return tmp_list[0]

    def analyse_child_node(self, text, analyse_child_list):
        while True:
            start = self.find_child_node(text)
            if start is None:
                break
            text = text[start+4:]
            start, end = self.find_parentheses(text)
            if end == -1:
                continue
            name = self.find_node_name(text[end+1:])
            if analyse_child_list == [] or name in analyse_child_list:
                self.child_node_dict[name] = Node(name, text[start+1: end])
                self.child_node_dict[name].analyse_text()
                self.child_node_list.append(name)
            name_index = text[end+1].find(name)
            end += 1 + name_index + len(name)
            text = text[end:]
        return

    def analyse_text(self):
        end = self.get_item()
        analyse_child_list = self.get_analyse_child_list()
        if analyse_child_list is None:
            return
        self.analyse_child_node(self.code_text[end:], analyse_child_list)
        return

    def get_word(self):
        ret_list = []
        for item in self.item_list:
            if item[0] != '*':
                ret_list.append(item[0])
            elif not self.child_node_list:
                ret_list.append('*')
            elif item[1] is not None:
                ret_list.extend(self.child_node_dict[item[1]].get_word())
            else:
                for child_node in self.child_node_list:
                    ret_list.extend(self.child_node_dict[child_node].get_word())
        return ret_list
