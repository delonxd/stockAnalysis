import re


if __name__ == '__main__':
    with open("F:\\Backups\\价值投资0406.txt", "r", encoding="utf-8", errors="ignore") as f:
        txt = f.read()
        print(txt)

        list1 = re.findall(r'([0-9]{6})', txt)

        print(list1)