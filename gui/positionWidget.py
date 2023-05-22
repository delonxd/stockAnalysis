from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from method.fileMethod import *
import sys


class PositionWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('QTreeModifyDemo ')
        self.resize(800, 800)

        self.tree = QTreeWidget()

        self.tree.setColumnCount(8)
        self.tree.setColumnWidth(0, 200)
        self.tree.setColumnWidth(1, 50)
        self.tree.setColumnWidth(2, 70)
        self.tree.setColumnWidth(3, 100)
        self.tree.setColumnWidth(4, 100)
        self.tree.setColumnWidth(5, 70)
        self.tree.setColumnWidth(6, 100)
        self.tree.setColumnWidth(7, 100)

        self.tree.setHeaderLabels([
            'key',
            'rate',
            'm-value',
            'm-position',
            'm-rate',
            'i-value',
            'i-position',
            'i-rate'
        ])

        self.root = QTreeWidgetItem(self.tree)
        self.root.setText(0, 'root')

        self.tree.expandAll()

        self.tree.doubleClicked.connect(self.double_clicked)

        self.button1 = QPushButton('添加')
        self.button2 = QPushButton('删除')
        self.button3 = QPushButton('保存')
        self.button4 = QPushButton('加载')
        self.button5 = QPushButton('+')
        self.button6 = QPushButton('-')
        self.button7 = QPushButton('计算')
        self.button8 = QPushButton('展开')

        self.button1.clicked.connect(self.add_node)
        self.button2.clicked.connect(self.delete_node)
        self.button3.clicked.connect(self.save)
        self.button4.clicked.connect(self.load)
        self.button5.clicked.connect(self.up)
        self.button6.clicked.connect(self.down)
        self.button7.clicked.connect(self.calculate)
        self.button8.clicked.connect(self.depth_expand)

        layout1 = QHBoxLayout()
        layout1.addWidget(self.button1)
        layout1.addWidget(self.button2)
        layout1.addWidget(self.button5)
        layout1.addWidget(self.button6)

        layout2 = QHBoxLayout()
        layout2.addWidget(self.button3)
        layout2.addWidget(self.button4)
        layout2.addWidget(self.button7)
        layout2.addWidget(self.button8)

        layout = QVBoxLayout()
        layout.addLayout(layout1)
        layout.addWidget(self.tree)
        layout.addLayout(layout2)

        self.setLayout(layout)
        self.src_value = dict()
        self.total1 = 0
        self.total2 = 0
        self.cash = 6443

        self.load()
        self.calculate()
        self.depth_expand()

    def double_clicked(self, index):
        item = self.tree.currentItem()
        column = index.column()
        ini = item.text(column)
        txt, _ = QInputDialog.getText(self, '', '请输入:', text=ini)
        item.setText(column, txt)
        item.setExpanded(not(item.isExpanded()))

    def add_node(self):
        item = self.tree.currentItem()
        node = QTreeWidgetItem(item)
        txt, _ = QInputDialog.getText(self, '', '请输入:', text='默认')
        node.setText(0, txt)
        node.setText(1, '')

    def delete_node(self):
        for item in self.tree.selectedItems():
            parent = item.parent()
            if parent is not None:
                parent.removeChild(item)

    def generate_dict(self, root):
        res = dict()
        for index in range(root.childCount()):
            child = root.child(index)
            if child.childCount() == 0:
                key = child.text(0)
                value = child.text(1)
            else:
                key, value = self.generate_dict(child)
            res[key] = value

        name = root.text(0)
        return name, res

    def show_dict(self, item, src):
        for key, value in src.items():
            child = QTreeWidgetItem(item)
            child.setText(0, key)

            if isinstance(value, dict):
                self.show_dict(child, value)
            else:
                child.setText(1, value)

    def save(self):
        root = self.tree.topLevelItem(0)
        data = self.generate_dict(root)
        path = "..\\basicData\\position.txt"
        write_json_txt(path, data)

    def load(self):
        path = "..\\basicData\\position.txt"
        key, value = load_json_txt(path)
        self.tree.clear()
        self.root = QTreeWidgetItem(self.tree)
        self.root.setText(0, key)
        self.show_dict(self.root, value)
        self.tree.expandAll()

    def up(self):
        if self.tree.selectedItems():
            item = self.tree.currentItem()
            root = item.parent()

            if root is None:
                return

            status = item.isExpanded()
            index = root.indexOfChild(item)
            root.takeChild(index)

            index2 = max(0, index-1)

            root.insertChild(index2, item)
            item.setExpanded(status)

            self.tree.setCurrentItem(item)

    def down(self):
        if self.tree.selectedItems():
            item = self.tree.currentItem()

            root = item.parent()

            if root is None:
                return

            status = item.isExpanded()
            index = root.indexOfChild(item)
            root.takeChild(index)

            index2 = min(root.childCount(), index+1)

            root.insertChild(index2, item)
            item.setExpanded(status)
            self.tree.setCurrentItem(item)

    @staticmethod
    def get_hold_info():
        ret1 = dict()
        ret2 = dict()
        path = '..\\basicData\\self_selected\\gui_hold.txt'

        for val in load_json_txt(path):
            key = val[1]
            value1 = val[3]
            value2 = val[4]
            if value1 != 0:
                ret1[key] = value1
                ret2[key] = value2 * 2
        return ret1, ret2

    @staticmethod
    def get_inner_value():
        ret = dict()
        path = '..\\basicData\\self_selected\\gui_assessment.txt'
        src = load_json_txt(path)
        return ret

    def calculate(self):
        src1, src2 = self.get_hold_info()

        self.total1 = sum(src1.values()) + self.cash
        self.total2 = sum(src2.values()) + self.cash

        root = self.tree.invisibleRootItem()
        self.cal_recursion(root, src1, src2)
        self.tree.expandAll()

        self.sum_recursion(root)
        self.sort_recursion(root)
        self.tree.expandAll()

    def cal_recursion(self, root, src1, src2):
        for index in range(root.childCount()):
            child = root.child(index)
            if child.childCount() == 0:
                self.cal_item(child, src1, src2)
            else:
                self.cal_recursion(child, src1, src2)

    def cal_item(self, item, src1, src2):
        key = item.text(0)
        value = src1.get(key)
        value = 0 if value is None else int(value)
        item.setText(2, '%.0f' % value)

        position = value * self.get_fraction(item.text(1))
        item.setData(3, 1, position)
        item.setText(3, '%.0f' % position)

        total_rate = position / self.total1 * 100
        item.setData(4, 1, total_rate)
        item.setText(4, '%.2f%%' % total_rate)

        value = src2.get(key)
        value = 0 if value is None else int(value)
        item.setText(5, '%.0f' % value)

        position = value * self.get_fraction(item.text(1))
        item.setData(6, 1, position)
        item.setText(6, '%.0f' % position)

        total_rate = position / self.total2 * 100
        item.setData(7, 1, total_rate)
        item.setText(7, '%.2f%%' % total_rate)

    @staticmethod
    def get_fraction(txt: str):
        try:
            a, b = txt.split('/')
            return int(a) / int(b)
        except Exception as e:
            print(e)
            return 0

    def sum_recursion(self, root):
        sum1 = 0
        sum2 = 0
        sum3 = 0
        sum4 = 0
        for index in range(root.childCount()):
            child = root.child(index)
            if child.childCount() == 0:
                val1 = child.data(3, 1)
                val2 = child.data(4, 1)
                val3 = child.data(6, 1)
                val4 = child.data(7, 1)
            else:
                val1, val2, val3, val4 = self.sum_recursion(child)
            sum1 += val1
            sum2 += val2
            sum3 += val3
            sum4 += val4

        root.setData(3, 1, sum1)
        root.setData(4, 1, sum2)
        root.setData(6, 1, sum3)
        root.setData(7, 1, sum4)

        root.setText(3, '%.0f' % sum1)
        root.setText(4, '%.2f%%' % sum2)
        root.setText(6, '%.0f' % sum3)
        root.setText(7, '%.2f%%' % sum4)
        return sum1, sum2, sum3, sum4

    def sort_recursion(self, root):
        sort_list = []
        for index in range(root.childCount()):
            child = root.child(index)
            if child.childCount() != 0:
                self.sort_recursion(child)
            sort_list.append((child.data(3, 1), child))

        sort_list.sort()
        sort_list.reverse()

        root.takeChildren()
        for _, item in sort_list:
            root.addChild(item)

    def depth_expand(self):
        if self.tree.selectedItems():
            item = self.tree.currentItem()
        else:
            item = self.root

        depth_expanded = self.depth_expanded_recursion(item)
        depth_max = self.depth_max_recursion(item)

        res = (depth_expanded + 1) % (depth_max + 1)
        self.expand_recursion(item, res)
        self.show_position_recursion(item)

    def expand_recursion(self, root, depth):
        if depth == 0:
            root.setExpanded(False)
        else:
            root.setExpanded(True)

            for index in range(root.childCount()):
                child = root.child(index)
                self.expand_recursion(child, depth-1)

    def depth_expanded_recursion(self, root):
        depth = 0
        for index in range(root.childCount()):
            child = root.child(index)
            if child.childCount() != 0:
                tmp = self.depth_expanded_recursion(child)
                depth = max(depth, tmp)
        if root.childCount() == 0:
            depth = 0
        elif root.isExpanded():
            depth += 1
        else:
            depth = 0
        return depth

    def depth_max_recursion(self, root):
        depth = 0
        for index in range(root.childCount()):
            child = root.child(index)
            if child.childCount() != 0:
                tmp = self.depth_max_recursion(child)
                depth = max(depth, tmp)
        if root.childCount() == 0:
            depth = 0
        else:
            depth += 1
        return depth

    def show_position_recursion(self, root):
        if (not root.isExpanded()) or root.childCount() == 0:
            try:
                root.setText(3, '%.0f' % root.data(3, 1))
                root.setText(4, '%.2f%%' % root.data(4, 1))
                root.setText(6, '%.0f' % root.data(6, 1))
                root.setText(7, '%.2f%%' % root.data(7, 1))
            except Exception as e:
                print(e)
        else:
            root.setText(3, '')
            root.setText(4, '')
            root.setText(6, '')
            root.setText(7, '')

        for index in range(root.childCount()):
            child = root.child(index)
            self.show_position_recursion(child)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = PositionWidget()
    main.show()
    sys.exit(app.exec_())
