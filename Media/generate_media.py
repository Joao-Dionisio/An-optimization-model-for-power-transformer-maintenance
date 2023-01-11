from matplotlib import pyplot as plt
from matplotlib import ticker

def iterative_refinement_example():
    """
    Creates a simple example of the iterative refinement heuristic, as shown in the paper "An optimization model for power transformer maintenance"
    """

    def setup(ax, title):
        """Set up common parameters for the Axes in the example."""
    
        # only show the bottom spine
        ax.yaxis.set_major_locator(ticker.NullLocator())
        ax.spines.right.set_color('none')
        ax.spines.left.set_color('none')
        ax.spines.top.set_color('none')

        # define tick positions
        ax.xaxis.set_major_locator(ticker.MultipleLocator(1.00))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.25))

        ax.xaxis.set_ticks_position('bottom')
        ax.tick_params(which='major', width=1.00, length=5)
        ax.tick_params(which='minor', width=0.75, length=2.5, labelsize=10)
        ax.set_xlim(0, 20)
        ax.set_ylim(0, 1)
        ax.text(0.0, 0.2, title, transform=ax.transAxes,
                fontsize=14, fontname='Monospace', color='tab:blue')

    fig1, axs1 = plt.subplots(3, 1, figsize=(8, 3))
    plt.subplots_adjust(top=0.1,bottom=0,hspace=0.001)
    fig1.suptitle('')#Formatter Object Formatting')

    # FuncFormatter can be used as a decorator
    @ticker.FuncFormatter
    def major_formatter(x, pos):
        return f'[{x:.2f}]'

    def plot_new_line(positions, index, maintenance=None):
        # Fixed formatter
        labels = [str(i) for i in positions]
        setup(axs1[index], title="")#"FixedFormatter(['A', 'B', 'C', ...])")
        axs1[index].xaxis.set_major_locator(ticker.FixedLocator(positions))
        axs1[index].xaxis.set_major_formatter(ticker.FixedFormatter(labels))
        
        for year in maintenance:
            axs1[index].scatter(year,0.1,color="red", marker="^", s=100)
    
    plot_new_line([0,10,20], 0, maintenance=[10])
    plot_new_line([0,5,10,15,20], 1, maintenance=[15])
    plot_new_line([0,5,10,12,15,17,20], 2, maintenance=[5,17])

    fig1.tight_layout()
    plt.savefig("/home/dionisio/Desktop/Doutoramento/Trabalho/Media/iterative_refinement_example.png",bbox_inches='tight')
    plt.show()

    return 


if __name__ == "__main__":
    iterative_refinement_example()
