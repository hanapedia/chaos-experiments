import matplotlib.font_manager as fm
from pprint import pprint
def main():
    fm.fontManager.addfont('/Users/hirokihanada/Downloads/MS Mincho.ttf')
    font_list = [f.name for f in fm.fontManager.ttflist]

    pprint(font_list)

if __name__ == "__main__":
    main()
