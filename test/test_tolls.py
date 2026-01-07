import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.tolls_file import Tolls

tolls = Tolls()

start = (46.4833, 3.9833)   # Buchelay FL
end   = (46.3167, 2.9500)   # Montesson FL


print("Has toll:", tolls.has_toll_on_route(start, end))
print("Toll count:", tolls.count_tolls_on_route(start, end))
