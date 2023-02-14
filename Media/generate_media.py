from matplotlib import pyplot as plt
from matplotlib import ticker
import numpy as np

def load_curve_representation(x, load, winding, oil, file):
    ''' A simple curve illustrating electricity demand '''
    
    plt.tick_params(
    axis='x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom=False,      # ticks along the bottom edge are off
    top=False,         # ticks along the top edge are off
    labelbottom=False)

    plt.tick_params(
    axis='y',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    left=False,      # ticks along the bottom edge are off
    top=False,         # ticks along the top edge are off
    labelleft=False)



    plt.plot(x,load, label="Load Demand",color="red",linewidth=3)
    plt.plot(x,winding,label="Winding Condition",color="black")
    plt.plot(x,oil,label="Oil Condition",color="green")
    plt.xlim(left=0, right=24)
    plt.ylim(bottom = 0, top = 3.3)
    #plt.legend(loc="upper left")
    plt.savefig(file,bbox_inches='tight')
    return plt

def run_load_curve_representation():
    
    x = [i/1000 for i in range(0,24000)]
    load = [0.5*np.sin(0.3*i)+1-0.3*np.cos(i) if i > 14 else 0.3*np.sin(0.3*i)+0.8 for i in x]
    winding = [4 - np.exp(0.04*i) for i in x]
    oil = [3-np.exp(0.05*i) if i <= 15.76 else 3-np.exp(0.05*i) + 1.2 if i <= 21.4 else 3-np.exp(0.05*i) + 1.91 for i in x]

    fig = load_curve_representation(x,load,winding,oil,"/home/dionisio/Desktop/Doutoramento/Trabalho/Media/PT1_example.png")
    #plt.savefig("/home/dionisio/Desktop/Doutoramento/Trabalho/Media/PT1_example.png",bbox_inches='tight')
    plt.show()

    load = [0.5*np.sin(0.28*i)+0.8-0.1*np.cos(i) if i > 14 else 0.3*np.sin(0.4*i)+0.62 for i in x]
    winding = [4 - np.exp(0.04*i) for i in x]
    oil = [3-np.exp(0.05*i) if i <= 19.5 else 3-np.exp(0.05*i) + 1.65 for i in x]
    fig = load_curve_representation(x,load,winding,oil,"/home/dionisio/Desktop/Doutoramento/Trabalho/Media/PT2_example.png")
    plt.show()
    #plt.savefig("/home/dionisio/Desktop/Doutoramento/Trabalho/Media/PT2_example.png",bbox_inches='tight')
    
    load = [0.5*np.sin(0.6*i)+1.1-0.1*np.cos(i) if i > 11 else 0.5*np.sin(0.2*i)+0.86 for i in x]
    winding = [4 - np.exp(0.04*i) if i <= 22.3 else 4-np.exp(0.04*i)+1.43 for i in x]
    oil = [3-np.exp(0.05*i) if i <= 11 else 3-np.exp(0.05*i) + 0.73 if i <= 20.4 else 3-np.exp(0.05*i) + 1.77 if i <= 22.9 else 3- np.exp(0.05*i) + 2.14 for i in x]
    fig = load_curve_representation(x,load,winding,oil,"/home/dionisio/Desktop/Doutoramento/Trabalho/Media/PT3_example.png")
    #plt.savefig("/home/dionisio/Desktop/Doutoramento/Trabalho/Media/PT3_example.png",bbox_inches='tight')
    plt.show()



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
    
    #############################
    #############################
    #############################
    #############################
    #############################
    plot_new_line([0,5,10,15,20], 0, maintenance=[10])
    plot_new_line([0,5,7,10,12,15,20], 1, maintenance=[7,12])
    plot_new_line([0,2,5,6,7,8,10,11,12,13,15,20], 2, maintenance=[6,11])
    #############################
    #############################
    #############################
    #############################

    #plot_new_line([0,10,20], 0, maintenance=[10])
    #plot_new_line([0,5,10,15,20], 1, maintenance=[15])
    #plot_new_line([0,5,10,12,15,17,20], 2, maintenance=[5,17])
    #plot_new_line([0, 1, 2, 3, 4, 5], ['0', '1', '2', '3', '4', '5'], 0)
    #plot_new_line([0, 1, 2, 3, 4, 5], ['0', '1', '2', '3', '4', '5'], 1)


    fig1.tight_layout()
    plt.savefig("/home/dionisio/Desktop/Doutoramento/Trabalho/Media/iterative_refinement_example.png",bbox_inches='tight')
    plt.show()

    return 


if __name__ == "__main__":
    iterative_refinement_example()
#run_load_curve_representation()