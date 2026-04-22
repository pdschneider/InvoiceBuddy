import sys
import os

print("frozen:", getattr(sys, 'frozen', False))
print("_MEIPASS:", getattr(sys, '_MEIPASS', 'NOT PRESENT'))
print("__file__:", __file__)
print("Project root guess:", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
