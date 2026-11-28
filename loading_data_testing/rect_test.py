import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.widgets import RectangleSelector

plt.ylabel('height')
plt.xlabel('width')
plt.title('Test')
plt.plot(4.0,4.0)
plt.show()

def mark(ax, row, col, height, width):
    return ax.add_patch(
        Rectangle((col, row), width, height, fill=False, edgecolor="red", linewidth=2)
    )