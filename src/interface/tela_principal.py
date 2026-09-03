import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from interface.app import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
